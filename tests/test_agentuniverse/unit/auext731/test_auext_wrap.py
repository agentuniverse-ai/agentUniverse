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
        ("round 731: the quick brown fox jumps over the lazy dog", 4),
        ["round", "731:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", 8),
        ["round", "731: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", 12),
        ["round 731:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", 16),
        ["round 731: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", 24),
        ["round 731: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", 32),
        ["round 731: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", 4),
        ["round", "731:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", 8),
        ["round", "731:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", 12),
        ["round 731:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", 16),
        ["round 731:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", 24),
        ["round 731: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", 32),
        ["round 731: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", 4),
        ["round", "731:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", 8),
        ["round", "731:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", 12),
        ["round 731:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", 16),
        ["round 731:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", 24),
        ["round 731: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", 32),
        ["round 731: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 731: the processor reads the record then stops", 4),
        ["round", "731:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 731: the processor reads the record then stops", 8),
        ["round", "731: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 731: the processor reads the record then stops", 12),
        ["round 731:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 731: the processor reads the record then stops", 16),
        ["round 731: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 731: the processor reads the record then stops", 24),
        ["round 731: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 731: the processor reads the record then stops", 32),
        ["round 731: the processor reads", "the record then stops"],
    ),
    (
        ("round 731: a worker pulls the next task from the queue", 4),
        ["round", "731:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 731: a worker pulls the next task from the queue", 8),
        ["round", "731: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 731: a worker pulls the next task from the queue", 12),
        ["round 731: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 731: a worker pulls the next task from the queue", 16),
        ["round 731: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 731: a worker pulls the next task from the queue", 24),
        ["round 731: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 731: a worker pulls the next task from the queue", 32),
        ["round 731: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 731: signals travel through the network layer", 4),
        ["round", "731:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 731: signals travel through the network layer", 8),
        ["round", "731:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 731: signals travel through the network layer", 12),
        ["round 731:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 731: signals travel through the network layer", 16),
        ["round 731:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 731: signals travel through the network layer", 24),
        ["round 731: signals", "travel through the", "network layer"],
    ),
    (
        ("round 731: signals travel through the network layer", 32),
        ["round 731: signals travel", "through the network layer"],
    ),
    (
        ("round 731: the gateway routes each request by policy", 4),
        ["round", "731:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 731: the gateway routes each request by policy", 8),
        ["round", "731: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 731: the gateway routes each request by policy", 12),
        ["round 731:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 731: the gateway routes each request by policy", 16),
        ["round 731: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 731: the gateway routes each request by policy", 24),
        ["round 731: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 731: the gateway routes each request by policy", 32),
        ["round 731: the gateway routes", "each request by policy"],
    ),
    (
        ("round 731: memory grows until the buffer is full", 4),
        ["round", "731:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 731: memory grows until the buffer is full", 8),
        ["round", "731:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 731: memory grows until the buffer is full", 12),
        ["round 731:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 731: memory grows until the buffer is full", 16),
        ["round 731:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 731: memory grows until the buffer is full", 24), ["round 731: memory grows", "until the buffer is full"]),
    (("round 731: memory grows until the buffer is full", 32), ["round 731: memory grows until", "the buffer is full"]),
    (
        ("round 731: the cluster mirrors every packet twice", 4),
        ["round", "731:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 731: the cluster mirrors every packet twice", 8),
        ["round", "731: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 731: the cluster mirrors every packet twice", 12),
        ["round 731:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 731: the cluster mirrors every packet twice", 16),
        ["round 731: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 731: the cluster mirrors every packet twice", 24),
        ["round 731: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 731: the cluster mirrors every packet twice", 32),
        ["round 731: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", 4),
        ["round", "731:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", 8),
        ["round", "731:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", 12),
        ["round 731:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", 16),
        ["round 731:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", 24),
        ["round 731: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", 32),
        ["round 731: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 731: a long session ends when the candle dies", 4),
        ["round", "731:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 731: a long session ends when the candle dies", 8),
        ["round", "731: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 731: a long session ends when the candle dies", 12),
        ["round 731: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 731: a long session ends when the candle dies", 16),
        ["round 731: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 731: a long session ends when the candle dies", 24),
        ["round 731: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 731: a long session ends when the candle dies", 32),
        ["round 731: a long session ends", "when the candle dies"],
    ),
    (
        ("round 731: encode the prompt then map the result", 4),
        ["round", "731:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 731: encode the prompt then map the result", 8),
        ["round", "731:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 731: encode the prompt then map the result", 12),
        ["round 731:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 731: encode the prompt then map the result", 16),
        ["round 731:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 731: encode the prompt then map the result", 24),
        ["round 731: encode the", "prompt then map the", "result"],
    ),
    (("round 731: encode the prompt then map the result", 32), ["round 731: encode the prompt", "then map the result"]),
    (
        ("round 731: the kernel wakes the worker at dawn", 4),
        ["round", "731:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 731: the kernel wakes the worker at dawn", 8),
        ["round", "731: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 731: the kernel wakes the worker at dawn", 12),
        ["round 731:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 731: the kernel wakes the worker at dawn", 16), ["round 731: the", "kernel wakes the", "worker at dawn"]),
    (("round 731: the kernel wakes the worker at dawn", 24), ["round 731: the kernel", "wakes the worker at dawn"]),
    (("round 731: the kernel wakes the worker at dawn", 32), ["round 731: the kernel wakes the", "worker at dawn"]),
    (
        ("round 731: service latency drops after the patch", 4),
        ["round", "731:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 731: service latency drops after the patch", 8),
        ["round", "731:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 731: service latency drops after the patch", 12),
        ["round 731:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 731: service latency drops after the patch", 16),
        ["round 731:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 731: service latency drops after the patch", 24),
        ["round 731: service", "latency drops after the", "patch"],
    ),
    (("round 731: service latency drops after the patch", 32), ["round 731: service latency drops", "after the patch"]),
    (
        ("round 731: the library caches every vector it sees", 4),
        ["round", "731:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 731: the library caches every vector it sees", 8),
        ["round", "731: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 731: the library caches every vector it sees", 12),
        ["round 731:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 731: the library caches every vector it sees", 16),
        ["round 731: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 731: the library caches every vector it sees", 24),
        ["round 731: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 731: the library caches every vector it sees", 32),
        ["round 731: the library caches", "every vector it sees"],
    ),
    (
        ("round 731: agents argue then the debate resolves", 4),
        ["round", "731:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 731: agents argue then the debate resolves", 8),
        ["round", "731:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 731: agents argue then the debate resolves", 12),
        ["round 731:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 731: agents argue then the debate resolves", 16),
        ["round 731:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 731: agents argue then the debate resolves", 24), ["round 731: agents argue", "then the debate resolves"]),
    (("round 731: agents argue then the debate resolves", 32), ["round 731: agents argue then the", "debate resolves"]),
    (
        ("round 731: the filter keeps only strong matches", 4),
        ["round", "731:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 731: the filter keeps only strong matches", 8),
        ["round", "731: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 731: the filter keeps only strong matches", 12),
        ["round 731:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 731: the filter keeps only strong matches", 16),
        ["round 731: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 731: the filter keeps only strong matches", 24),
        ["round 731: the filter", "keeps only strong", "matches"],
    ),
    (("round 731: the filter keeps only strong matches", 32), ["round 731: the filter keeps only", "strong matches"]),
    (
        ("round 731: the model answers with a short reply", 4),
        ["round", "731:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 731: the model answers with a short reply", 8),
        ["round", "731: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 731: the model answers with a short reply", 12),
        ["round 731:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 731: the model answers with a short reply", 16),
        ["round 731: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 731: the model answers with a short reply", 24),
        ["round 731: the model", "answers with a short", "reply"],
    ),
    (("round 731: the model answers with a short reply", 32), ["round 731: the model answers", "with a short reply"]),
    (
        ("round 731: the recorder stores the reasoning trace", 4),
        ["round", "731:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 731: the recorder stores the reasoning trace", 8),
        ["round", "731: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 731: the recorder stores the reasoning trace", 12),
        ["round 731:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 731: the recorder stores the reasoning trace", 16),
        ["round 731: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 731: the recorder stores the reasoning trace", 24),
        ["round 731: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 731: the recorder stores the reasoning trace", 32),
        ["round 731: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 731: the angel watches the processor run", 4),
        ["round", "731:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 731: the angel watches the processor run", 8),
        ["round", "731: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 731: the angel watches the processor run", 12),
        ["round 731:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 731: the angel watches the processor run", 16),
        ["round 731: the", "angel watches", "the processor", "run"],
    ),
    (("round 731: the angel watches the processor run", 24), ["round 731: the angel", "watches the processor", "run"]),
    (("round 731: the angel watches the processor run", 32), ["round 731: the angel watches the", "processor run"]),
    (
        ("round 731: angle of the vector decides the match", 4),
        ["round", "731:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 731: angle of the vector decides the match", 8),
        ["round", "731:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 731: angle of the vector decides the match", 12),
        ["round 731:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 731: angle of the vector decides the match", 16),
        ["round 731: angle", "of the vector", "decides the", "match"],
    ),
    (("round 731: angle of the vector decides the match", 24), ["round 731: angle of the", "vector decides the match"]),
    (("round 731: angle of the vector decides the match", 32), ["round 731: angle of the vector", "decides the match"]),
    (
        ("round 731: the candle burns twice as long at night", 4),
        ["round", "731:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 731: the candle burns twice as long at night", 8),
        ["round", "731: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 731: the candle burns twice as long at night", 12),
        ["round 731:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 731: the candle burns twice as long at night", 16),
        ["round 731: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 731: the candle burns twice as long at night", 24),
        ["round 731: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 731: the candle burns twice as long at night", 32),
        ["round 731: the candle burns", "twice as long at night"],
    ),
    (
        ("round 731: a mirror of the universe in one line", 4),
        ["round", "731:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 731: a mirror of the universe in one line", 8),
        ["round", "731: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 731: a mirror of the universe in one line", 12),
        ["round 731: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 731: a mirror of the universe in one line", 16),
        ["round 731: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 731: a mirror of the universe in one line", 24), ["round 731: a mirror of", "the universe in one line"]),
    (("round 731: a mirror of the universe in one line", 32), ["round 731: a mirror of the", "universe in one line"]),
    (
        ("round 731: the queue drains before the storm", 4),
        ["round", "731:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 731: the queue drains before the storm", 8),
        ["round", "731: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 731: the queue drains before the storm", 12),
        ["round 731:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 731: the queue drains before the storm", 16), ["round 731: the", "queue drains", "before the storm"]),
    (("round 731: the queue drains before the storm", 24), ["round 731: the queue", "drains before the storm"]),
    (("round 731: the queue drains before the storm", 32), ["round 731: the queue drains", "before the storm"]),
    (
        ("kitten731 sitting731 agent731 angle731 universe731 memory731", 6),
        ["kitten731", "sitting731", "agent731", "angle731", "universe731", "memory731"],
    ),
    (
        ("kitten731 sitting731 agent731 angle731 universe731 memory731", 10),
        ["kitten731", "sitting731", "agent731", "angle731", "universe731", "memory731"],
    ),
    (
        ("kitten731 sitting731 agent731 angle731 universe731 memory731", 18),
        ["kitten731", "sitting731", "agent731 angle731", "universe731", "memory731"],
    ),
    (
        ("kitten731 sitting731 agent731 angle731 universe731 memory731", 28),
        ["kitten731 sitting731", "agent731 angle731", "universe731 memory731"],
    ),
    (
        ("sitting731 agent731 angle731 universe731 memory731 stream731", 6),
        ["sitting731", "agent731", "angle731", "universe731", "memory731", "stream731"],
    ),
    (
        ("sitting731 agent731 angle731 universe731 memory731 stream731", 10),
        ["sitting731", "agent731", "angle731", "universe731", "memory731", "stream731"],
    ),
    (
        ("sitting731 agent731 angle731 universe731 memory731 stream731", 18),
        ["sitting731", "agent731 angle731", "universe731", "memory731", "stream731"],
    ),
    (
        ("sitting731 agent731 angle731 universe731 memory731 stream731", 28),
        ["sitting731 agent731 angle731", "universe731 memory731", "stream731"],
    ),
    (
        ("agent731 angle731 universe731 memory731 stream731 context731", 6),
        ["agent731", "angle731", "universe731", "memory731", "stream731", "context731"],
    ),
    (
        ("agent731 angle731 universe731 memory731 stream731 context731", 10),
        ["agent731", "angle731", "universe731", "memory731", "stream731", "context731"],
    ),
    (
        ("agent731 angle731 universe731 memory731 stream731 context731", 18),
        ["agent731 angle731", "universe731", "memory731", "stream731", "context731"],
    ),
    (
        ("agent731 angle731 universe731 memory731 stream731 context731", 28),
        ["agent731 angle731", "universe731 memory731", "stream731 context731"],
    ),
    (
        ("angle731 universe731 memory731 stream731 context731 knowledge731", 6),
        ["angle731", "universe731", "memory731", "stream731", "context731", "knowledge731"],
    ),
    (
        ("angle731 universe731 memory731 stream731 context731 knowledge731", 10),
        ["angle731", "universe731", "memory731", "stream731", "context731", "knowledge731"],
    ),
    (
        ("angle731 universe731 memory731 stream731 context731 knowledge731", 18),
        ["angle731", "universe731", "memory731", "stream731", "context731", "knowledge731"],
    ),
    (
        ("angle731 universe731 memory731 stream731 context731 knowledge731", 28),
        ["angle731 universe731", "memory731 stream731", "context731 knowledge731"],
    ),
    (
        ("universe731 memory731 stream731 context731 knowledge731 vector731", 6),
        ["universe731", "memory731", "stream731", "context731", "knowledge731", "vector731"],
    ),
    (
        ("universe731 memory731 stream731 context731 knowledge731 vector731", 10),
        ["universe731", "memory731", "stream731", "context731", "knowledge731", "vector731"],
    ),
    (
        ("universe731 memory731 stream731 context731 knowledge731 vector731", 18),
        ["universe731", "memory731", "stream731", "context731", "knowledge731", "vector731"],
    ),
    (
        ("universe731 memory731 stream731 context731 knowledge731 vector731", 28),
        ["universe731 memory731", "stream731 context731", "knowledge731 vector731"],
    ),
    (
        ("memory731 stream731 context731 knowledge731 vector731 processor731", 6),
        ["memory731", "stream731", "context731", "knowledge731", "vector731", "processor731"],
    ),
    (
        ("memory731 stream731 context731 knowledge731 vector731 processor731", 10),
        ["memory731", "stream731", "context731", "knowledge731", "vector731", "processor731"],
    ),
    (
        ("memory731 stream731 context731 knowledge731 vector731 processor731", 18),
        ["memory731", "stream731", "context731", "knowledge731", "vector731", "processor731"],
    ),
    (
        ("memory731 stream731 context731 knowledge731 vector731 processor731", 28),
        ["memory731 stream731", "context731 knowledge731", "vector731 processor731"],
    ),
    (
        ("stream731 context731 knowledge731 vector731 processor731 reasoning731", 6),
        ["stream731", "context731", "knowledge731", "vector731", "processor731", "reasoning731"],
    ),
    (
        ("stream731 context731 knowledge731 vector731 processor731 reasoning731", 10),
        ["stream731", "context731", "knowledge731", "vector731", "processor731", "reasoning731"],
    ),
    (
        ("stream731 context731 knowledge731 vector731 processor731 reasoning731", 18),
        ["stream731", "context731", "knowledge731", "vector731", "processor731", "reasoning731"],
    ),
    (
        ("stream731 context731 knowledge731 vector731 processor731 reasoning731", 28),
        ["stream731 context731", "knowledge731 vector731", "processor731 reasoning731"],
    ),
    (
        ("context731 knowledge731 vector731 processor731 reasoning731 machine731", 6),
        ["context731", "knowledge731", "vector731", "processor731", "reasoning731", "machine731"],
    ),
    (
        ("context731 knowledge731 vector731 processor731 reasoning731 machine731", 10),
        ["context731", "knowledge731", "vector731", "processor731", "reasoning731", "machine731"],
    ),
    (
        ("context731 knowledge731 vector731 processor731 reasoning731 machine731", 18),
        ["context731", "knowledge731", "vector731", "processor731", "reasoning731", "machine731"],
    ),
    (
        ("context731 knowledge731 vector731 processor731 reasoning731 machine731", 28),
        ["context731 knowledge731", "vector731 processor731", "reasoning731 machine731"],
    ),
    (
        ("knowledge731 vector731 processor731 reasoning731 machine731 learning731", 6),
        ["knowledge731", "vector731", "processor731", "reasoning731", "machine731", "learning731"],
    ),
    (
        ("knowledge731 vector731 processor731 reasoning731 machine731 learning731", 10),
        ["knowledge731", "vector731", "processor731", "reasoning731", "machine731", "learning731"],
    ),
    (
        ("knowledge731 vector731 processor731 reasoning731 machine731 learning731", 18),
        ["knowledge731", "vector731", "processor731", "reasoning731", "machine731", "learning731"],
    ),
    (
        ("knowledge731 vector731 processor731 reasoning731 machine731 learning731", 28),
        ["knowledge731 vector731", "processor731 reasoning731", "machine731 learning731"],
    ),
    (
        ("vector731 processor731 reasoning731 machine731 learning731 model731", 6),
        ["vector731", "processor731", "reasoning731", "machine731", "learning731", "model731"],
    ),
    (
        ("vector731 processor731 reasoning731 machine731 learning731 model731", 10),
        ["vector731", "processor731", "reasoning731", "machine731", "learning731", "model731"],
    ),
    (
        ("vector731 processor731 reasoning731 machine731 learning731 model731", 18),
        ["vector731", "processor731", "reasoning731", "machine731", "learning731", "model731"],
    ),
    (
        ("vector731 processor731 reasoning731 machine731 learning731 model731", 28),
        ["vector731 processor731", "reasoning731 machine731", "learning731 model731"],
    ),
    (
        ("processor731 reasoning731 machine731 learning731 model731 token731", 6),
        ["processor731", "reasoning731", "machine731", "learning731", "model731", "token731"],
    ),
    (
        ("processor731 reasoning731 machine731 learning731 model731 token731", 10),
        ["processor731", "reasoning731", "machine731", "learning731", "model731", "token731"],
    ),
    (
        ("processor731 reasoning731 machine731 learning731 model731 token731", 18),
        ["processor731", "reasoning731", "machine731", "learning731", "model731 token731"],
    ),
    (
        ("processor731 reasoning731 machine731 learning731 model731 token731", 28),
        ["processor731 reasoning731", "machine731 learning731", "model731 token731"],
    ),
    (
        ("reasoning731 machine731 learning731 model731 token731 prompt731", 6),
        ["reasoning731", "machine731", "learning731", "model731", "token731", "prompt731"],
    ),
    (
        ("reasoning731 machine731 learning731 model731 token731 prompt731", 10),
        ["reasoning731", "machine731", "learning731", "model731", "token731", "prompt731"],
    ),
    (
        ("reasoning731 machine731 learning731 model731 token731 prompt731", 18),
        ["reasoning731", "machine731", "learning731", "model731 token731", "prompt731"],
    ),
    (
        ("reasoning731 machine731 learning731 model731 token731 prompt731", 28),
        ["reasoning731 machine731", "learning731 model731", "token731 prompt731"],
    ),
    (
        ("machine731 learning731 model731 token731 prompt731 session731", 6),
        ["machine731", "learning731", "model731", "token731", "prompt731", "session731"],
    ),
    (
        ("machine731 learning731 model731 token731 prompt731 session731", 10),
        ["machine731", "learning731", "model731", "token731", "prompt731", "session731"],
    ),
    (
        ("machine731 learning731 model731 token731 prompt731 session731", 18),
        ["machine731", "learning731", "model731 token731", "prompt731", "session731"],
    ),
    (
        ("machine731 learning731 model731 token731 prompt731 session731", 28),
        ["machine731 learning731", "model731 token731 prompt731", "session731"],
    ),
    (
        ("learning731 model731 token731 prompt731 session731 library731", 6),
        ["learning731", "model731", "token731", "prompt731", "session731", "library731"],
    ),
    (
        ("learning731 model731 token731 prompt731 session731 library731", 10),
        ["learning731", "model731", "token731", "prompt731", "session731", "library731"],
    ),
    (
        ("learning731 model731 token731 prompt731 session731 library731", 18),
        ["learning731", "model731 token731", "prompt731", "session731", "library731"],
    ),
    (
        ("learning731 model731 token731 prompt731 session731 library731", 28),
        ["learning731 model731", "token731 prompt731", "session731 library731"],
    ),
    (
        ("model731 token731 prompt731 session731 library731 service731", 6),
        ["model731", "token731", "prompt731", "session731", "library731", "service731"],
    ),
    (
        ("model731 token731 prompt731 session731 library731 service731", 10),
        ["model731", "token731", "prompt731", "session731", "library731", "service731"],
    ),
    (
        ("model731 token731 prompt731 session731 library731 service731", 18),
        ["model731 token731", "prompt731", "session731", "library731", "service731"],
    ),
    (
        ("model731 token731 prompt731 session731 library731 service731", 28),
        ["model731 token731 prompt731", "session731 library731", "service731"],
    ),
    (
        ("token731 prompt731 session731 library731 service731 gateway731", 6),
        ["token731", "prompt731", "session731", "library731", "service731", "gateway731"],
    ),
    (
        ("token731 prompt731 session731 library731 service731 gateway731", 10),
        ["token731", "prompt731", "session731", "library731", "service731", "gateway731"],
    ),
    (
        ("token731 prompt731 session731 library731 service731 gateway731", 18),
        ["token731 prompt731", "session731", "library731", "service731", "gateway731"],
    ),
    (
        ("token731 prompt731 session731 library731 service731 gateway731", 28),
        ["token731 prompt731", "session731 library731", "service731 gateway731"],
    ),
    (
        ("prompt731 session731 library731 service731 gateway731 storage731", 6),
        ["prompt731", "session731", "library731", "service731", "gateway731", "storage731"],
    ),
    (
        ("prompt731 session731 library731 service731 gateway731 storage731", 10),
        ["prompt731", "session731", "library731", "service731", "gateway731", "storage731"],
    ),
    (
        ("prompt731 session731 library731 service731 gateway731 storage731", 18),
        ["prompt731", "session731", "library731", "service731", "gateway731", "storage731"],
    ),
    (
        ("prompt731 session731 library731 service731 gateway731 storage731", 28),
        ["prompt731 session731", "library731 service731", "gateway731 storage731"],
    ),
    (
        ("session731 library731 service731 gateway731 storage731 network731", 6),
        ["session731", "library731", "service731", "gateway731", "storage731", "network731"],
    ),
    (
        ("session731 library731 service731 gateway731 storage731 network731", 10),
        ["session731", "library731", "service731", "gateway731", "storage731", "network731"],
    ),
    (
        ("session731 library731 service731 gateway731 storage731 network731", 18),
        ["session731", "library731", "service731", "gateway731", "storage731", "network731"],
    ),
    (
        ("session731 library731 service731 gateway731 storage731 network731", 28),
        ["session731 library731", "service731 gateway731", "storage731 network731"],
    ),
    (
        ("library731 service731 gateway731 storage731 network731 latency731", 6),
        ["library731", "service731", "gateway731", "storage731", "network731", "latency731"],
    ),
    (
        ("library731 service731 gateway731 storage731 network731 latency731", 10),
        ["library731", "service731", "gateway731", "storage731", "network731", "latency731"],
    ),
    (
        ("library731 service731 gateway731 storage731 network731 latency731", 18),
        ["library731", "service731", "gateway731", "storage731", "network731", "latency731"],
    ),
    (
        ("library731 service731 gateway731 storage731 network731 latency731", 28),
        ["library731 service731", "gateway731 storage731", "network731 latency731"],
    ),
    (
        ("service731 gateway731 storage731 network731 latency731 buffer731", 6),
        ["service731", "gateway731", "storage731", "network731", "latency731", "buffer731"],
    ),
    (
        ("service731 gateway731 storage731 network731 latency731 buffer731", 10),
        ["service731", "gateway731", "storage731", "network731", "latency731", "buffer731"],
    ),
    (
        ("service731 gateway731 storage731 network731 latency731 buffer731", 18),
        ["service731", "gateway731", "storage731", "network731", "latency731", "buffer731"],
    ),
    (
        ("service731 gateway731 storage731 network731 latency731 buffer731", 28),
        ["service731 gateway731", "storage731 network731", "latency731 buffer731"],
    ),
    (
        ("gateway731 storage731 network731 latency731 buffer731 queue731", 6),
        ["gateway731", "storage731", "network731", "latency731", "buffer731", "queue731"],
    ),
    (
        ("gateway731 storage731 network731 latency731 buffer731 queue731", 10),
        ["gateway731", "storage731", "network731", "latency731", "buffer731", "queue731"],
    ),
    (
        ("gateway731 storage731 network731 latency731 buffer731 queue731", 18),
        ["gateway731", "storage731", "network731", "latency731", "buffer731 queue731"],
    ),
    (
        ("gateway731 storage731 network731 latency731 buffer731 queue731", 28),
        ["gateway731 storage731", "network731 latency731", "buffer731 queue731"],
    ),
    (
        ("storage731 network731 latency731 buffer731 queue731 worker731", 6),
        ["storage731", "network731", "latency731", "buffer731", "queue731", "worker731"],
    ),
    (
        ("storage731 network731 latency731 buffer731 queue731 worker731", 10),
        ["storage731", "network731", "latency731", "buffer731", "queue731", "worker731"],
    ),
    (
        ("storage731 network731 latency731 buffer731 queue731 worker731", 18),
        ["storage731", "network731", "latency731", "buffer731 queue731", "worker731"],
    ),
    (
        ("storage731 network731 latency731 buffer731 queue731 worker731", 28),
        ["storage731 network731", "latency731 buffer731", "queue731 worker731"],
    ),
    (
        ("network731 latency731 buffer731 queue731 worker731 kernel731", 6),
        ["network731", "latency731", "buffer731", "queue731", "worker731", "kernel731"],
    ),
    (
        ("network731 latency731 buffer731 queue731 worker731 kernel731", 10),
        ["network731", "latency731", "buffer731", "queue731", "worker731", "kernel731"],
    ),
    (
        ("network731 latency731 buffer731 queue731 worker731 kernel731", 18),
        ["network731", "latency731", "buffer731 queue731", "worker731", "kernel731"],
    ),
    (
        ("network731 latency731 buffer731 queue731 worker731 kernel731", 28),
        ["network731 latency731", "buffer731 queue731 worker731", "kernel731"],
    ),
    (
        ("latency731 buffer731 queue731 worker731 kernel731 signal731", 6),
        ["latency731", "buffer731", "queue731", "worker731", "kernel731", "signal731"],
    ),
    (
        ("latency731 buffer731 queue731 worker731 kernel731 signal731", 10),
        ["latency731", "buffer731", "queue731", "worker731", "kernel731", "signal731"],
    ),
    (
        ("latency731 buffer731 queue731 worker731 kernel731 signal731", 18),
        ["latency731", "buffer731 queue731", "worker731", "kernel731", "signal731"],
    ),
    (
        ("latency731 buffer731 queue731 worker731 kernel731 signal731", 28),
        ["latency731 buffer731", "queue731 worker731 kernel731", "signal731"],
    ),
    (
        ("buffer731 queue731 worker731 kernel731 signal731 packet731", 6),
        ["buffer731", "queue731", "worker731", "kernel731", "signal731", "packet731"],
    ),
    (
        ("buffer731 queue731 worker731 kernel731 signal731 packet731", 10),
        ["buffer731", "queue731", "worker731", "kernel731", "signal731", "packet731"],
    ),
    (
        ("buffer731 queue731 worker731 kernel731 signal731 packet731", 18),
        ["buffer731 queue731", "worker731", "kernel731", "signal731", "packet731"],
    ),
    (
        ("buffer731 queue731 worker731 kernel731 signal731 packet731", 28),
        ["buffer731 queue731 worker731", "kernel731 signal731", "packet731"],
    ),
    (
        ("queue731 worker731 kernel731 signal731 packet731 router731", 6),
        ["queue731", "worker731", "kernel731", "signal731", "packet731", "router731"],
    ),
    (
        ("queue731 worker731 kernel731 signal731 packet731 router731", 10),
        ["queue731", "worker731", "kernel731", "signal731", "packet731", "router731"],
    ),
    (
        ("queue731 worker731 kernel731 signal731 packet731 router731", 18),
        ["queue731 worker731", "kernel731", "signal731", "packet731", "router731"],
    ),
    (
        ("queue731 worker731 kernel731 signal731 packet731 router731", 28),
        ["queue731 worker731 kernel731", "signal731 packet731", "router731"],
    ),
    (
        ("worker731 kernel731 signal731 packet731 router731 cluster731", 6),
        ["worker731", "kernel731", "signal731", "packet731", "router731", "cluster731"],
    ),
    (
        ("worker731 kernel731 signal731 packet731 router731 cluster731", 10),
        ["worker731", "kernel731", "signal731", "packet731", "router731", "cluster731"],
    ),
    (
        ("worker731 kernel731 signal731 packet731 router731 cluster731", 18),
        ["worker731", "kernel731", "signal731", "packet731", "router731", "cluster731"],
    ),
    (
        ("worker731 kernel731 signal731 packet731 router731 cluster731", 28),
        ["worker731 kernel731", "signal731 packet731", "router731 cluster731"],
    ),
    (
        ("kernel731 signal731 packet731 router731 cluster731 mirror731", 6),
        ["kernel731", "signal731", "packet731", "router731", "cluster731", "mirror731"],
    ),
    (
        ("kernel731 signal731 packet731 router731 cluster731 mirror731", 10),
        ["kernel731", "signal731", "packet731", "router731", "cluster731", "mirror731"],
    ),
    (
        ("kernel731 signal731 packet731 router731 cluster731 mirror731", 18),
        ["kernel731", "signal731", "packet731", "router731", "cluster731", "mirror731"],
    ),
    (
        ("kernel731 signal731 packet731 router731 cluster731 mirror731", 28),
        ["kernel731 signal731", "packet731 router731", "cluster731 mirror731"],
    ),
    (
        ("signal731 packet731 router731 cluster731 mirror731 filter731", 6),
        ["signal731", "packet731", "router731", "cluster731", "mirror731", "filter731"],
    ),
    (
        ("signal731 packet731 router731 cluster731 mirror731 filter731", 10),
        ["signal731", "packet731", "router731", "cluster731", "mirror731", "filter731"],
    ),
    (
        ("signal731 packet731 router731 cluster731 mirror731 filter731", 18),
        ["signal731", "packet731", "router731", "cluster731", "mirror731", "filter731"],
    ),
    (
        ("signal731 packet731 router731 cluster731 mirror731 filter731", 28),
        ["signal731 packet731", "router731 cluster731", "mirror731 filter731"],
    ),
    (
        ("packet731 router731 cluster731 mirror731 filter731 ranking731", 6),
        ["packet731", "router731", "cluster731", "mirror731", "filter731", "ranking731"],
    ),
    (
        ("packet731 router731 cluster731 mirror731 filter731 ranking731", 10),
        ["packet731", "router731", "cluster731", "mirror731", "filter731", "ranking731"],
    ),
    (
        ("packet731 router731 cluster731 mirror731 filter731 ranking731", 18),
        ["packet731", "router731", "cluster731", "mirror731", "filter731", "ranking731"],
    ),
    (
        ("packet731 router731 cluster731 mirror731 filter731 ranking731", 28),
        ["packet731 router731", "cluster731 mirror731", "filter731 ranking731"],
    ),
    (
        ("router731 cluster731 mirror731 filter731 ranking731 encoding731", 6),
        ["router731", "cluster731", "mirror731", "filter731", "ranking731", "encoding731"],
    ),
    (
        ("router731 cluster731 mirror731 filter731 ranking731 encoding731", 10),
        ["router731", "cluster731", "mirror731", "filter731", "ranking731", "encoding731"],
    ),
    (
        ("router731 cluster731 mirror731 filter731 ranking731 encoding731", 18),
        ["router731", "cluster731", "mirror731", "filter731", "ranking731", "encoding731"],
    ),
    (
        ("router731 cluster731 mirror731 filter731 ranking731 encoding731", 28),
        ["router731 cluster731", "mirror731 filter731", "ranking731 encoding731"],
    ),
    (
        ("cluster731 mirror731 filter731 ranking731 encoding731 mapping731", 6),
        ["cluster731", "mirror731", "filter731", "ranking731", "encoding731", "mapping731"],
    ),
    (
        ("cluster731 mirror731 filter731 ranking731 encoding731 mapping731", 10),
        ["cluster731", "mirror731", "filter731", "ranking731", "encoding731", "mapping731"],
    ),
    (
        ("cluster731 mirror731 filter731 ranking731 encoding731 mapping731", 18),
        ["cluster731", "mirror731", "filter731", "ranking731", "encoding731", "mapping731"],
    ),
    (
        ("cluster731 mirror731 filter731 ranking731 encoding731 mapping731", 28),
        ["cluster731 mirror731", "filter731 ranking731", "encoding731 mapping731"],
    ),
    (
        ("mirror731 filter731 ranking731 encoding731 mapping731 record731", 6),
        ["mirror731", "filter731", "ranking731", "encoding731", "mapping731", "record731"],
    ),
    (
        ("mirror731 filter731 ranking731 encoding731 mapping731 record731", 10),
        ["mirror731", "filter731", "ranking731", "encoding731", "mapping731", "record731"],
    ),
    (
        ("mirror731 filter731 ranking731 encoding731 mapping731 record731", 18),
        ["mirror731", "filter731", "ranking731", "encoding731", "mapping731", "record731"],
    ),
    (
        ("mirror731 filter731 ranking731 encoding731 mapping731 record731", 28),
        ["mirror731 filter731", "ranking731 encoding731", "mapping731 record731"],
    ),
    (
        ("filter731 ranking731 encoding731 mapping731 record731 candle731", 6),
        ["filter731", "ranking731", "encoding731", "mapping731", "record731", "candle731"],
    ),
    (
        ("filter731 ranking731 encoding731 mapping731 record731 candle731", 10),
        ["filter731", "ranking731", "encoding731", "mapping731", "record731", "candle731"],
    ),
    (
        ("filter731 ranking731 encoding731 mapping731 record731 candle731", 18),
        ["filter731", "ranking731", "encoding731", "mapping731", "record731", "candle731"],
    ),
    (
        ("filter731 ranking731 encoding731 mapping731 record731 candle731", 28),
        ["filter731 ranking731", "encoding731 mapping731", "record731 candle731"],
    ),
    (
        ("ranking731 encoding731 mapping731 record731 candle731 thread731", 6),
        ["ranking731", "encoding731", "mapping731", "record731", "candle731", "thread731"],
    ),
    (
        ("ranking731 encoding731 mapping731 record731 candle731 thread731", 10),
        ["ranking731", "encoding731", "mapping731", "record731", "candle731", "thread731"],
    ),
    (
        ("ranking731 encoding731 mapping731 record731 candle731 thread731", 18),
        ["ranking731", "encoding731", "mapping731", "record731", "candle731", "thread731"],
    ),
    (
        ("ranking731 encoding731 mapping731 record731 candle731 thread731", 28),
        ["ranking731 encoding731", "mapping731 record731", "candle731 thread731"],
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
