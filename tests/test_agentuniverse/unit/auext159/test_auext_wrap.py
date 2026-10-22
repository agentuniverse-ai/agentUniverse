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
        ("round 159: the quick brown fox jumps over the lazy dog", 4),
        ["round", "159:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", 8),
        ["round", "159: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", 12),
        ["round 159:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", 16),
        ["round 159: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", 24),
        ["round 159: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", 32),
        ["round 159: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", 4),
        ["round", "159:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", 8),
        ["round", "159:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", 12),
        ["round 159:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", 16),
        ["round 159:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", 24),
        ["round 159: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", 32),
        ["round 159: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", 4),
        ["round", "159:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", 8),
        ["round", "159:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", 12),
        ["round 159:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", 16),
        ["round 159:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", 24),
        ["round 159: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", 32),
        ["round 159: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 159: the processor reads the record then stops", 4),
        ["round", "159:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 159: the processor reads the record then stops", 8),
        ["round", "159: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 159: the processor reads the record then stops", 12),
        ["round 159:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 159: the processor reads the record then stops", 16),
        ["round 159: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 159: the processor reads the record then stops", 24),
        ["round 159: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 159: the processor reads the record then stops", 32),
        ["round 159: the processor reads", "the record then stops"],
    ),
    (
        ("round 159: a worker pulls the next task from the queue", 4),
        ["round", "159:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 159: a worker pulls the next task from the queue", 8),
        ["round", "159: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 159: a worker pulls the next task from the queue", 12),
        ["round 159: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 159: a worker pulls the next task from the queue", 16),
        ["round 159: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 159: a worker pulls the next task from the queue", 24),
        ["round 159: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 159: a worker pulls the next task from the queue", 32),
        ["round 159: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 159: signals travel through the network layer", 4),
        ["round", "159:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 159: signals travel through the network layer", 8),
        ["round", "159:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 159: signals travel through the network layer", 12),
        ["round 159:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 159: signals travel through the network layer", 16),
        ["round 159:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 159: signals travel through the network layer", 24),
        ["round 159: signals", "travel through the", "network layer"],
    ),
    (
        ("round 159: signals travel through the network layer", 32),
        ["round 159: signals travel", "through the network layer"],
    ),
    (
        ("round 159: the gateway routes each request by policy", 4),
        ["round", "159:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 159: the gateway routes each request by policy", 8),
        ["round", "159: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 159: the gateway routes each request by policy", 12),
        ["round 159:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 159: the gateway routes each request by policy", 16),
        ["round 159: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 159: the gateway routes each request by policy", 24),
        ["round 159: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 159: the gateway routes each request by policy", 32),
        ["round 159: the gateway routes", "each request by policy"],
    ),
    (
        ("round 159: memory grows until the buffer is full", 4),
        ["round", "159:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 159: memory grows until the buffer is full", 8),
        ["round", "159:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 159: memory grows until the buffer is full", 12),
        ["round 159:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 159: memory grows until the buffer is full", 16),
        ["round 159:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 159: memory grows until the buffer is full", 24), ["round 159: memory grows", "until the buffer is full"]),
    (("round 159: memory grows until the buffer is full", 32), ["round 159: memory grows until", "the buffer is full"]),
    (
        ("round 159: the cluster mirrors every packet twice", 4),
        ["round", "159:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 159: the cluster mirrors every packet twice", 8),
        ["round", "159: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 159: the cluster mirrors every packet twice", 12),
        ["round 159:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 159: the cluster mirrors every packet twice", 16),
        ["round 159: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 159: the cluster mirrors every packet twice", 24),
        ["round 159: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 159: the cluster mirrors every packet twice", 32),
        ["round 159: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", 4),
        ["round", "159:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", 8),
        ["round", "159:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", 12),
        ["round 159:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", 16),
        ["round 159:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", 24),
        ["round 159: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", 32),
        ["round 159: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 159: a long session ends when the candle dies", 4),
        ["round", "159:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 159: a long session ends when the candle dies", 8),
        ["round", "159: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 159: a long session ends when the candle dies", 12),
        ["round 159: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 159: a long session ends when the candle dies", 16),
        ["round 159: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 159: a long session ends when the candle dies", 24),
        ["round 159: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 159: a long session ends when the candle dies", 32),
        ["round 159: a long session ends", "when the candle dies"],
    ),
    (
        ("round 159: encode the prompt then map the result", 4),
        ["round", "159:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 159: encode the prompt then map the result", 8),
        ["round", "159:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 159: encode the prompt then map the result", 12),
        ["round 159:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 159: encode the prompt then map the result", 16),
        ["round 159:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 159: encode the prompt then map the result", 24),
        ["round 159: encode the", "prompt then map the", "result"],
    ),
    (("round 159: encode the prompt then map the result", 32), ["round 159: encode the prompt", "then map the result"]),
    (
        ("round 159: the kernel wakes the worker at dawn", 4),
        ["round", "159:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 159: the kernel wakes the worker at dawn", 8),
        ["round", "159: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 159: the kernel wakes the worker at dawn", 12),
        ["round 159:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 159: the kernel wakes the worker at dawn", 16), ["round 159: the", "kernel wakes the", "worker at dawn"]),
    (("round 159: the kernel wakes the worker at dawn", 24), ["round 159: the kernel", "wakes the worker at dawn"]),
    (("round 159: the kernel wakes the worker at dawn", 32), ["round 159: the kernel wakes the", "worker at dawn"]),
    (
        ("round 159: service latency drops after the patch", 4),
        ["round", "159:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 159: service latency drops after the patch", 8),
        ["round", "159:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 159: service latency drops after the patch", 12),
        ["round 159:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 159: service latency drops after the patch", 16),
        ["round 159:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 159: service latency drops after the patch", 24),
        ["round 159: service", "latency drops after the", "patch"],
    ),
    (("round 159: service latency drops after the patch", 32), ["round 159: service latency drops", "after the patch"]),
    (
        ("round 159: the library caches every vector it sees", 4),
        ["round", "159:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 159: the library caches every vector it sees", 8),
        ["round", "159: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 159: the library caches every vector it sees", 12),
        ["round 159:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 159: the library caches every vector it sees", 16),
        ["round 159: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 159: the library caches every vector it sees", 24),
        ["round 159: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 159: the library caches every vector it sees", 32),
        ["round 159: the library caches", "every vector it sees"],
    ),
    (
        ("round 159: agents argue then the debate resolves", 4),
        ["round", "159:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 159: agents argue then the debate resolves", 8),
        ["round", "159:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 159: agents argue then the debate resolves", 12),
        ["round 159:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 159: agents argue then the debate resolves", 16),
        ["round 159:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 159: agents argue then the debate resolves", 24), ["round 159: agents argue", "then the debate resolves"]),
    (("round 159: agents argue then the debate resolves", 32), ["round 159: agents argue then the", "debate resolves"]),
    (
        ("round 159: the filter keeps only strong matches", 4),
        ["round", "159:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 159: the filter keeps only strong matches", 8),
        ["round", "159: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 159: the filter keeps only strong matches", 12),
        ["round 159:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 159: the filter keeps only strong matches", 16),
        ["round 159: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 159: the filter keeps only strong matches", 24),
        ["round 159: the filter", "keeps only strong", "matches"],
    ),
    (("round 159: the filter keeps only strong matches", 32), ["round 159: the filter keeps only", "strong matches"]),
    (
        ("round 159: the model answers with a short reply", 4),
        ["round", "159:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 159: the model answers with a short reply", 8),
        ["round", "159: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 159: the model answers with a short reply", 12),
        ["round 159:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 159: the model answers with a short reply", 16),
        ["round 159: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 159: the model answers with a short reply", 24),
        ["round 159: the model", "answers with a short", "reply"],
    ),
    (("round 159: the model answers with a short reply", 32), ["round 159: the model answers", "with a short reply"]),
    (
        ("round 159: the recorder stores the reasoning trace", 4),
        ["round", "159:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 159: the recorder stores the reasoning trace", 8),
        ["round", "159: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 159: the recorder stores the reasoning trace", 12),
        ["round 159:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 159: the recorder stores the reasoning trace", 16),
        ["round 159: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 159: the recorder stores the reasoning trace", 24),
        ["round 159: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 159: the recorder stores the reasoning trace", 32),
        ["round 159: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 159: the angel watches the processor run", 4),
        ["round", "159:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 159: the angel watches the processor run", 8),
        ["round", "159: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 159: the angel watches the processor run", 12),
        ["round 159:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 159: the angel watches the processor run", 16),
        ["round 159: the", "angel watches", "the processor", "run"],
    ),
    (("round 159: the angel watches the processor run", 24), ["round 159: the angel", "watches the processor", "run"]),
    (("round 159: the angel watches the processor run", 32), ["round 159: the angel watches the", "processor run"]),
    (
        ("round 159: angle of the vector decides the match", 4),
        ["round", "159:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 159: angle of the vector decides the match", 8),
        ["round", "159:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 159: angle of the vector decides the match", 12),
        ["round 159:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 159: angle of the vector decides the match", 16),
        ["round 159: angle", "of the vector", "decides the", "match"],
    ),
    (("round 159: angle of the vector decides the match", 24), ["round 159: angle of the", "vector decides the match"]),
    (("round 159: angle of the vector decides the match", 32), ["round 159: angle of the vector", "decides the match"]),
    (
        ("round 159: the candle burns twice as long at night", 4),
        ["round", "159:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 159: the candle burns twice as long at night", 8),
        ["round", "159: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 159: the candle burns twice as long at night", 12),
        ["round 159:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 159: the candle burns twice as long at night", 16),
        ["round 159: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 159: the candle burns twice as long at night", 24),
        ["round 159: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 159: the candle burns twice as long at night", 32),
        ["round 159: the candle burns", "twice as long at night"],
    ),
    (
        ("round 159: a mirror of the universe in one line", 4),
        ["round", "159:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 159: a mirror of the universe in one line", 8),
        ["round", "159: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 159: a mirror of the universe in one line", 12),
        ["round 159: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 159: a mirror of the universe in one line", 16),
        ["round 159: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 159: a mirror of the universe in one line", 24), ["round 159: a mirror of", "the universe in one line"]),
    (("round 159: a mirror of the universe in one line", 32), ["round 159: a mirror of the", "universe in one line"]),
    (
        ("round 159: the queue drains before the storm", 4),
        ["round", "159:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 159: the queue drains before the storm", 8),
        ["round", "159: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 159: the queue drains before the storm", 12),
        ["round 159:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 159: the queue drains before the storm", 16), ["round 159: the", "queue drains", "before the storm"]),
    (("round 159: the queue drains before the storm", 24), ["round 159: the queue", "drains before the storm"]),
    (("round 159: the queue drains before the storm", 32), ["round 159: the queue drains", "before the storm"]),
    (
        ("kitten159 sitting159 agent159 angle159 universe159 memory159", 6),
        ["kitten159", "sitting159", "agent159", "angle159", "universe159", "memory159"],
    ),
    (
        ("kitten159 sitting159 agent159 angle159 universe159 memory159", 10),
        ["kitten159", "sitting159", "agent159", "angle159", "universe159", "memory159"],
    ),
    (
        ("kitten159 sitting159 agent159 angle159 universe159 memory159", 18),
        ["kitten159", "sitting159", "agent159 angle159", "universe159", "memory159"],
    ),
    (
        ("kitten159 sitting159 agent159 angle159 universe159 memory159", 28),
        ["kitten159 sitting159", "agent159 angle159", "universe159 memory159"],
    ),
    (
        ("sitting159 agent159 angle159 universe159 memory159 stream159", 6),
        ["sitting159", "agent159", "angle159", "universe159", "memory159", "stream159"],
    ),
    (
        ("sitting159 agent159 angle159 universe159 memory159 stream159", 10),
        ["sitting159", "agent159", "angle159", "universe159", "memory159", "stream159"],
    ),
    (
        ("sitting159 agent159 angle159 universe159 memory159 stream159", 18),
        ["sitting159", "agent159 angle159", "universe159", "memory159", "stream159"],
    ),
    (
        ("sitting159 agent159 angle159 universe159 memory159 stream159", 28),
        ["sitting159 agent159 angle159", "universe159 memory159", "stream159"],
    ),
    (
        ("agent159 angle159 universe159 memory159 stream159 context159", 6),
        ["agent159", "angle159", "universe159", "memory159", "stream159", "context159"],
    ),
    (
        ("agent159 angle159 universe159 memory159 stream159 context159", 10),
        ["agent159", "angle159", "universe159", "memory159", "stream159", "context159"],
    ),
    (
        ("agent159 angle159 universe159 memory159 stream159 context159", 18),
        ["agent159 angle159", "universe159", "memory159", "stream159", "context159"],
    ),
    (
        ("agent159 angle159 universe159 memory159 stream159 context159", 28),
        ["agent159 angle159", "universe159 memory159", "stream159 context159"],
    ),
    (
        ("angle159 universe159 memory159 stream159 context159 knowledge159", 6),
        ["angle159", "universe159", "memory159", "stream159", "context159", "knowledge159"],
    ),
    (
        ("angle159 universe159 memory159 stream159 context159 knowledge159", 10),
        ["angle159", "universe159", "memory159", "stream159", "context159", "knowledge159"],
    ),
    (
        ("angle159 universe159 memory159 stream159 context159 knowledge159", 18),
        ["angle159", "universe159", "memory159", "stream159", "context159", "knowledge159"],
    ),
    (
        ("angle159 universe159 memory159 stream159 context159 knowledge159", 28),
        ["angle159 universe159", "memory159 stream159", "context159 knowledge159"],
    ),
    (
        ("universe159 memory159 stream159 context159 knowledge159 vector159", 6),
        ["universe159", "memory159", "stream159", "context159", "knowledge159", "vector159"],
    ),
    (
        ("universe159 memory159 stream159 context159 knowledge159 vector159", 10),
        ["universe159", "memory159", "stream159", "context159", "knowledge159", "vector159"],
    ),
    (
        ("universe159 memory159 stream159 context159 knowledge159 vector159", 18),
        ["universe159", "memory159", "stream159", "context159", "knowledge159", "vector159"],
    ),
    (
        ("universe159 memory159 stream159 context159 knowledge159 vector159", 28),
        ["universe159 memory159", "stream159 context159", "knowledge159 vector159"],
    ),
    (
        ("memory159 stream159 context159 knowledge159 vector159 processor159", 6),
        ["memory159", "stream159", "context159", "knowledge159", "vector159", "processor159"],
    ),
    (
        ("memory159 stream159 context159 knowledge159 vector159 processor159", 10),
        ["memory159", "stream159", "context159", "knowledge159", "vector159", "processor159"],
    ),
    (
        ("memory159 stream159 context159 knowledge159 vector159 processor159", 18),
        ["memory159", "stream159", "context159", "knowledge159", "vector159", "processor159"],
    ),
    (
        ("memory159 stream159 context159 knowledge159 vector159 processor159", 28),
        ["memory159 stream159", "context159 knowledge159", "vector159 processor159"],
    ),
    (
        ("stream159 context159 knowledge159 vector159 processor159 reasoning159", 6),
        ["stream159", "context159", "knowledge159", "vector159", "processor159", "reasoning159"],
    ),
    (
        ("stream159 context159 knowledge159 vector159 processor159 reasoning159", 10),
        ["stream159", "context159", "knowledge159", "vector159", "processor159", "reasoning159"],
    ),
    (
        ("stream159 context159 knowledge159 vector159 processor159 reasoning159", 18),
        ["stream159", "context159", "knowledge159", "vector159", "processor159", "reasoning159"],
    ),
    (
        ("stream159 context159 knowledge159 vector159 processor159 reasoning159", 28),
        ["stream159 context159", "knowledge159 vector159", "processor159 reasoning159"],
    ),
    (
        ("context159 knowledge159 vector159 processor159 reasoning159 machine159", 6),
        ["context159", "knowledge159", "vector159", "processor159", "reasoning159", "machine159"],
    ),
    (
        ("context159 knowledge159 vector159 processor159 reasoning159 machine159", 10),
        ["context159", "knowledge159", "vector159", "processor159", "reasoning159", "machine159"],
    ),
    (
        ("context159 knowledge159 vector159 processor159 reasoning159 machine159", 18),
        ["context159", "knowledge159", "vector159", "processor159", "reasoning159", "machine159"],
    ),
    (
        ("context159 knowledge159 vector159 processor159 reasoning159 machine159", 28),
        ["context159 knowledge159", "vector159 processor159", "reasoning159 machine159"],
    ),
    (
        ("knowledge159 vector159 processor159 reasoning159 machine159 learning159", 6),
        ["knowledge159", "vector159", "processor159", "reasoning159", "machine159", "learning159"],
    ),
    (
        ("knowledge159 vector159 processor159 reasoning159 machine159 learning159", 10),
        ["knowledge159", "vector159", "processor159", "reasoning159", "machine159", "learning159"],
    ),
    (
        ("knowledge159 vector159 processor159 reasoning159 machine159 learning159", 18),
        ["knowledge159", "vector159", "processor159", "reasoning159", "machine159", "learning159"],
    ),
    (
        ("knowledge159 vector159 processor159 reasoning159 machine159 learning159", 28),
        ["knowledge159 vector159", "processor159 reasoning159", "machine159 learning159"],
    ),
    (
        ("vector159 processor159 reasoning159 machine159 learning159 model159", 6),
        ["vector159", "processor159", "reasoning159", "machine159", "learning159", "model159"],
    ),
    (
        ("vector159 processor159 reasoning159 machine159 learning159 model159", 10),
        ["vector159", "processor159", "reasoning159", "machine159", "learning159", "model159"],
    ),
    (
        ("vector159 processor159 reasoning159 machine159 learning159 model159", 18),
        ["vector159", "processor159", "reasoning159", "machine159", "learning159", "model159"],
    ),
    (
        ("vector159 processor159 reasoning159 machine159 learning159 model159", 28),
        ["vector159 processor159", "reasoning159 machine159", "learning159 model159"],
    ),
    (
        ("processor159 reasoning159 machine159 learning159 model159 token159", 6),
        ["processor159", "reasoning159", "machine159", "learning159", "model159", "token159"],
    ),
    (
        ("processor159 reasoning159 machine159 learning159 model159 token159", 10),
        ["processor159", "reasoning159", "machine159", "learning159", "model159", "token159"],
    ),
    (
        ("processor159 reasoning159 machine159 learning159 model159 token159", 18),
        ["processor159", "reasoning159", "machine159", "learning159", "model159 token159"],
    ),
    (
        ("processor159 reasoning159 machine159 learning159 model159 token159", 28),
        ["processor159 reasoning159", "machine159 learning159", "model159 token159"],
    ),
    (
        ("reasoning159 machine159 learning159 model159 token159 prompt159", 6),
        ["reasoning159", "machine159", "learning159", "model159", "token159", "prompt159"],
    ),
    (
        ("reasoning159 machine159 learning159 model159 token159 prompt159", 10),
        ["reasoning159", "machine159", "learning159", "model159", "token159", "prompt159"],
    ),
    (
        ("reasoning159 machine159 learning159 model159 token159 prompt159", 18),
        ["reasoning159", "machine159", "learning159", "model159 token159", "prompt159"],
    ),
    (
        ("reasoning159 machine159 learning159 model159 token159 prompt159", 28),
        ["reasoning159 machine159", "learning159 model159", "token159 prompt159"],
    ),
    (
        ("machine159 learning159 model159 token159 prompt159 session159", 6),
        ["machine159", "learning159", "model159", "token159", "prompt159", "session159"],
    ),
    (
        ("machine159 learning159 model159 token159 prompt159 session159", 10),
        ["machine159", "learning159", "model159", "token159", "prompt159", "session159"],
    ),
    (
        ("machine159 learning159 model159 token159 prompt159 session159", 18),
        ["machine159", "learning159", "model159 token159", "prompt159", "session159"],
    ),
    (
        ("machine159 learning159 model159 token159 prompt159 session159", 28),
        ["machine159 learning159", "model159 token159 prompt159", "session159"],
    ),
    (
        ("learning159 model159 token159 prompt159 session159 library159", 6),
        ["learning159", "model159", "token159", "prompt159", "session159", "library159"],
    ),
    (
        ("learning159 model159 token159 prompt159 session159 library159", 10),
        ["learning159", "model159", "token159", "prompt159", "session159", "library159"],
    ),
    (
        ("learning159 model159 token159 prompt159 session159 library159", 18),
        ["learning159", "model159 token159", "prompt159", "session159", "library159"],
    ),
    (
        ("learning159 model159 token159 prompt159 session159 library159", 28),
        ["learning159 model159", "token159 prompt159", "session159 library159"],
    ),
    (
        ("model159 token159 prompt159 session159 library159 service159", 6),
        ["model159", "token159", "prompt159", "session159", "library159", "service159"],
    ),
    (
        ("model159 token159 prompt159 session159 library159 service159", 10),
        ["model159", "token159", "prompt159", "session159", "library159", "service159"],
    ),
    (
        ("model159 token159 prompt159 session159 library159 service159", 18),
        ["model159 token159", "prompt159", "session159", "library159", "service159"],
    ),
    (
        ("model159 token159 prompt159 session159 library159 service159", 28),
        ["model159 token159 prompt159", "session159 library159", "service159"],
    ),
    (
        ("token159 prompt159 session159 library159 service159 gateway159", 6),
        ["token159", "prompt159", "session159", "library159", "service159", "gateway159"],
    ),
    (
        ("token159 prompt159 session159 library159 service159 gateway159", 10),
        ["token159", "prompt159", "session159", "library159", "service159", "gateway159"],
    ),
    (
        ("token159 prompt159 session159 library159 service159 gateway159", 18),
        ["token159 prompt159", "session159", "library159", "service159", "gateway159"],
    ),
    (
        ("token159 prompt159 session159 library159 service159 gateway159", 28),
        ["token159 prompt159", "session159 library159", "service159 gateway159"],
    ),
    (
        ("prompt159 session159 library159 service159 gateway159 storage159", 6),
        ["prompt159", "session159", "library159", "service159", "gateway159", "storage159"],
    ),
    (
        ("prompt159 session159 library159 service159 gateway159 storage159", 10),
        ["prompt159", "session159", "library159", "service159", "gateway159", "storage159"],
    ),
    (
        ("prompt159 session159 library159 service159 gateway159 storage159", 18),
        ["prompt159", "session159", "library159", "service159", "gateway159", "storage159"],
    ),
    (
        ("prompt159 session159 library159 service159 gateway159 storage159", 28),
        ["prompt159 session159", "library159 service159", "gateway159 storage159"],
    ),
    (
        ("session159 library159 service159 gateway159 storage159 network159", 6),
        ["session159", "library159", "service159", "gateway159", "storage159", "network159"],
    ),
    (
        ("session159 library159 service159 gateway159 storage159 network159", 10),
        ["session159", "library159", "service159", "gateway159", "storage159", "network159"],
    ),
    (
        ("session159 library159 service159 gateway159 storage159 network159", 18),
        ["session159", "library159", "service159", "gateway159", "storage159", "network159"],
    ),
    (
        ("session159 library159 service159 gateway159 storage159 network159", 28),
        ["session159 library159", "service159 gateway159", "storage159 network159"],
    ),
    (
        ("library159 service159 gateway159 storage159 network159 latency159", 6),
        ["library159", "service159", "gateway159", "storage159", "network159", "latency159"],
    ),
    (
        ("library159 service159 gateway159 storage159 network159 latency159", 10),
        ["library159", "service159", "gateway159", "storage159", "network159", "latency159"],
    ),
    (
        ("library159 service159 gateway159 storage159 network159 latency159", 18),
        ["library159", "service159", "gateway159", "storage159", "network159", "latency159"],
    ),
    (
        ("library159 service159 gateway159 storage159 network159 latency159", 28),
        ["library159 service159", "gateway159 storage159", "network159 latency159"],
    ),
    (
        ("service159 gateway159 storage159 network159 latency159 buffer159", 6),
        ["service159", "gateway159", "storage159", "network159", "latency159", "buffer159"],
    ),
    (
        ("service159 gateway159 storage159 network159 latency159 buffer159", 10),
        ["service159", "gateway159", "storage159", "network159", "latency159", "buffer159"],
    ),
    (
        ("service159 gateway159 storage159 network159 latency159 buffer159", 18),
        ["service159", "gateway159", "storage159", "network159", "latency159", "buffer159"],
    ),
    (
        ("service159 gateway159 storage159 network159 latency159 buffer159", 28),
        ["service159 gateway159", "storage159 network159", "latency159 buffer159"],
    ),
    (
        ("gateway159 storage159 network159 latency159 buffer159 queue159", 6),
        ["gateway159", "storage159", "network159", "latency159", "buffer159", "queue159"],
    ),
    (
        ("gateway159 storage159 network159 latency159 buffer159 queue159", 10),
        ["gateway159", "storage159", "network159", "latency159", "buffer159", "queue159"],
    ),
    (
        ("gateway159 storage159 network159 latency159 buffer159 queue159", 18),
        ["gateway159", "storage159", "network159", "latency159", "buffer159 queue159"],
    ),
    (
        ("gateway159 storage159 network159 latency159 buffer159 queue159", 28),
        ["gateway159 storage159", "network159 latency159", "buffer159 queue159"],
    ),
    (
        ("storage159 network159 latency159 buffer159 queue159 worker159", 6),
        ["storage159", "network159", "latency159", "buffer159", "queue159", "worker159"],
    ),
    (
        ("storage159 network159 latency159 buffer159 queue159 worker159", 10),
        ["storage159", "network159", "latency159", "buffer159", "queue159", "worker159"],
    ),
    (
        ("storage159 network159 latency159 buffer159 queue159 worker159", 18),
        ["storage159", "network159", "latency159", "buffer159 queue159", "worker159"],
    ),
    (
        ("storage159 network159 latency159 buffer159 queue159 worker159", 28),
        ["storage159 network159", "latency159 buffer159", "queue159 worker159"],
    ),
    (
        ("network159 latency159 buffer159 queue159 worker159 kernel159", 6),
        ["network159", "latency159", "buffer159", "queue159", "worker159", "kernel159"],
    ),
    (
        ("network159 latency159 buffer159 queue159 worker159 kernel159", 10),
        ["network159", "latency159", "buffer159", "queue159", "worker159", "kernel159"],
    ),
    (
        ("network159 latency159 buffer159 queue159 worker159 kernel159", 18),
        ["network159", "latency159", "buffer159 queue159", "worker159", "kernel159"],
    ),
    (
        ("network159 latency159 buffer159 queue159 worker159 kernel159", 28),
        ["network159 latency159", "buffer159 queue159 worker159", "kernel159"],
    ),
    (
        ("latency159 buffer159 queue159 worker159 kernel159 signal159", 6),
        ["latency159", "buffer159", "queue159", "worker159", "kernel159", "signal159"],
    ),
    (
        ("latency159 buffer159 queue159 worker159 kernel159 signal159", 10),
        ["latency159", "buffer159", "queue159", "worker159", "kernel159", "signal159"],
    ),
    (
        ("latency159 buffer159 queue159 worker159 kernel159 signal159", 18),
        ["latency159", "buffer159 queue159", "worker159", "kernel159", "signal159"],
    ),
    (
        ("latency159 buffer159 queue159 worker159 kernel159 signal159", 28),
        ["latency159 buffer159", "queue159 worker159 kernel159", "signal159"],
    ),
    (
        ("buffer159 queue159 worker159 kernel159 signal159 packet159", 6),
        ["buffer159", "queue159", "worker159", "kernel159", "signal159", "packet159"],
    ),
    (
        ("buffer159 queue159 worker159 kernel159 signal159 packet159", 10),
        ["buffer159", "queue159", "worker159", "kernel159", "signal159", "packet159"],
    ),
    (
        ("buffer159 queue159 worker159 kernel159 signal159 packet159", 18),
        ["buffer159 queue159", "worker159", "kernel159", "signal159", "packet159"],
    ),
    (
        ("buffer159 queue159 worker159 kernel159 signal159 packet159", 28),
        ["buffer159 queue159 worker159", "kernel159 signal159", "packet159"],
    ),
    (
        ("queue159 worker159 kernel159 signal159 packet159 router159", 6),
        ["queue159", "worker159", "kernel159", "signal159", "packet159", "router159"],
    ),
    (
        ("queue159 worker159 kernel159 signal159 packet159 router159", 10),
        ["queue159", "worker159", "kernel159", "signal159", "packet159", "router159"],
    ),
    (
        ("queue159 worker159 kernel159 signal159 packet159 router159", 18),
        ["queue159 worker159", "kernel159", "signal159", "packet159", "router159"],
    ),
    (
        ("queue159 worker159 kernel159 signal159 packet159 router159", 28),
        ["queue159 worker159 kernel159", "signal159 packet159", "router159"],
    ),
    (
        ("worker159 kernel159 signal159 packet159 router159 cluster159", 6),
        ["worker159", "kernel159", "signal159", "packet159", "router159", "cluster159"],
    ),
    (
        ("worker159 kernel159 signal159 packet159 router159 cluster159", 10),
        ["worker159", "kernel159", "signal159", "packet159", "router159", "cluster159"],
    ),
    (
        ("worker159 kernel159 signal159 packet159 router159 cluster159", 18),
        ["worker159", "kernel159", "signal159", "packet159", "router159", "cluster159"],
    ),
    (
        ("worker159 kernel159 signal159 packet159 router159 cluster159", 28),
        ["worker159 kernel159", "signal159 packet159", "router159 cluster159"],
    ),
    (
        ("kernel159 signal159 packet159 router159 cluster159 mirror159", 6),
        ["kernel159", "signal159", "packet159", "router159", "cluster159", "mirror159"],
    ),
    (
        ("kernel159 signal159 packet159 router159 cluster159 mirror159", 10),
        ["kernel159", "signal159", "packet159", "router159", "cluster159", "mirror159"],
    ),
    (
        ("kernel159 signal159 packet159 router159 cluster159 mirror159", 18),
        ["kernel159", "signal159", "packet159", "router159", "cluster159", "mirror159"],
    ),
    (
        ("kernel159 signal159 packet159 router159 cluster159 mirror159", 28),
        ["kernel159 signal159", "packet159 router159", "cluster159 mirror159"],
    ),
    (
        ("signal159 packet159 router159 cluster159 mirror159 filter159", 6),
        ["signal159", "packet159", "router159", "cluster159", "mirror159", "filter159"],
    ),
    (
        ("signal159 packet159 router159 cluster159 mirror159 filter159", 10),
        ["signal159", "packet159", "router159", "cluster159", "mirror159", "filter159"],
    ),
    (
        ("signal159 packet159 router159 cluster159 mirror159 filter159", 18),
        ["signal159", "packet159", "router159", "cluster159", "mirror159", "filter159"],
    ),
    (
        ("signal159 packet159 router159 cluster159 mirror159 filter159", 28),
        ["signal159 packet159", "router159 cluster159", "mirror159 filter159"],
    ),
    (
        ("packet159 router159 cluster159 mirror159 filter159 ranking159", 6),
        ["packet159", "router159", "cluster159", "mirror159", "filter159", "ranking159"],
    ),
    (
        ("packet159 router159 cluster159 mirror159 filter159 ranking159", 10),
        ["packet159", "router159", "cluster159", "mirror159", "filter159", "ranking159"],
    ),
    (
        ("packet159 router159 cluster159 mirror159 filter159 ranking159", 18),
        ["packet159", "router159", "cluster159", "mirror159", "filter159", "ranking159"],
    ),
    (
        ("packet159 router159 cluster159 mirror159 filter159 ranking159", 28),
        ["packet159 router159", "cluster159 mirror159", "filter159 ranking159"],
    ),
    (
        ("router159 cluster159 mirror159 filter159 ranking159 encoding159", 6),
        ["router159", "cluster159", "mirror159", "filter159", "ranking159", "encoding159"],
    ),
    (
        ("router159 cluster159 mirror159 filter159 ranking159 encoding159", 10),
        ["router159", "cluster159", "mirror159", "filter159", "ranking159", "encoding159"],
    ),
    (
        ("router159 cluster159 mirror159 filter159 ranking159 encoding159", 18),
        ["router159", "cluster159", "mirror159", "filter159", "ranking159", "encoding159"],
    ),
    (
        ("router159 cluster159 mirror159 filter159 ranking159 encoding159", 28),
        ["router159 cluster159", "mirror159 filter159", "ranking159 encoding159"],
    ),
    (
        ("cluster159 mirror159 filter159 ranking159 encoding159 mapping159", 6),
        ["cluster159", "mirror159", "filter159", "ranking159", "encoding159", "mapping159"],
    ),
    (
        ("cluster159 mirror159 filter159 ranking159 encoding159 mapping159", 10),
        ["cluster159", "mirror159", "filter159", "ranking159", "encoding159", "mapping159"],
    ),
    (
        ("cluster159 mirror159 filter159 ranking159 encoding159 mapping159", 18),
        ["cluster159", "mirror159", "filter159", "ranking159", "encoding159", "mapping159"],
    ),
    (
        ("cluster159 mirror159 filter159 ranking159 encoding159 mapping159", 28),
        ["cluster159 mirror159", "filter159 ranking159", "encoding159 mapping159"],
    ),
    (
        ("mirror159 filter159 ranking159 encoding159 mapping159 record159", 6),
        ["mirror159", "filter159", "ranking159", "encoding159", "mapping159", "record159"],
    ),
    (
        ("mirror159 filter159 ranking159 encoding159 mapping159 record159", 10),
        ["mirror159", "filter159", "ranking159", "encoding159", "mapping159", "record159"],
    ),
    (
        ("mirror159 filter159 ranking159 encoding159 mapping159 record159", 18),
        ["mirror159", "filter159", "ranking159", "encoding159", "mapping159", "record159"],
    ),
    (
        ("mirror159 filter159 ranking159 encoding159 mapping159 record159", 28),
        ["mirror159 filter159", "ranking159 encoding159", "mapping159 record159"],
    ),
    (
        ("filter159 ranking159 encoding159 mapping159 record159 candle159", 6),
        ["filter159", "ranking159", "encoding159", "mapping159", "record159", "candle159"],
    ),
    (
        ("filter159 ranking159 encoding159 mapping159 record159 candle159", 10),
        ["filter159", "ranking159", "encoding159", "mapping159", "record159", "candle159"],
    ),
    (
        ("filter159 ranking159 encoding159 mapping159 record159 candle159", 18),
        ["filter159", "ranking159", "encoding159", "mapping159", "record159", "candle159"],
    ),
    (
        ("filter159 ranking159 encoding159 mapping159 record159 candle159", 28),
        ["filter159 ranking159", "encoding159 mapping159", "record159 candle159"],
    ),
    (
        ("ranking159 encoding159 mapping159 record159 candle159 thread159", 6),
        ["ranking159", "encoding159", "mapping159", "record159", "candle159", "thread159"],
    ),
    (
        ("ranking159 encoding159 mapping159 record159 candle159 thread159", 10),
        ["ranking159", "encoding159", "mapping159", "record159", "candle159", "thread159"],
    ),
    (
        ("ranking159 encoding159 mapping159 record159 candle159 thread159", 18),
        ["ranking159", "encoding159", "mapping159", "record159", "candle159", "thread159"],
    ),
    (
        ("ranking159 encoding159 mapping159 record159 candle159 thread159", 28),
        ["ranking159 encoding159", "mapping159 record159", "candle159 thread159"],
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
