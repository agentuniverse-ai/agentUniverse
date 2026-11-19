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
        ("round 197: the quick brown fox jumps over the lazy dog", 4),
        ["round", "197:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", 8),
        ["round", "197: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", 12),
        ["round 197:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", 16),
        ["round 197: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", 24),
        ["round 197: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", 32),
        ["round 197: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", 4),
        ["round", "197:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", 8),
        ["round", "197:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", 12),
        ["round 197:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", 16),
        ["round 197:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", 24),
        ["round 197: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", 32),
        ["round 197: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", 4),
        ["round", "197:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", 8),
        ["round", "197:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", 12),
        ["round 197:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", 16),
        ["round 197:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", 24),
        ["round 197: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", 32),
        ["round 197: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 197: the processor reads the record then stops", 4),
        ["round", "197:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 197: the processor reads the record then stops", 8),
        ["round", "197: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 197: the processor reads the record then stops", 12),
        ["round 197:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 197: the processor reads the record then stops", 16),
        ["round 197: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 197: the processor reads the record then stops", 24),
        ["round 197: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 197: the processor reads the record then stops", 32),
        ["round 197: the processor reads", "the record then stops"],
    ),
    (
        ("round 197: a worker pulls the next task from the queue", 4),
        ["round", "197:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 197: a worker pulls the next task from the queue", 8),
        ["round", "197: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 197: a worker pulls the next task from the queue", 12),
        ["round 197: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 197: a worker pulls the next task from the queue", 16),
        ["round 197: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 197: a worker pulls the next task from the queue", 24),
        ["round 197: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 197: a worker pulls the next task from the queue", 32),
        ["round 197: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 197: signals travel through the network layer", 4),
        ["round", "197:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 197: signals travel through the network layer", 8),
        ["round", "197:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 197: signals travel through the network layer", 12),
        ["round 197:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 197: signals travel through the network layer", 16),
        ["round 197:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 197: signals travel through the network layer", 24),
        ["round 197: signals", "travel through the", "network layer"],
    ),
    (
        ("round 197: signals travel through the network layer", 32),
        ["round 197: signals travel", "through the network layer"],
    ),
    (
        ("round 197: the gateway routes each request by policy", 4),
        ["round", "197:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 197: the gateway routes each request by policy", 8),
        ["round", "197: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 197: the gateway routes each request by policy", 12),
        ["round 197:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 197: the gateway routes each request by policy", 16),
        ["round 197: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 197: the gateway routes each request by policy", 24),
        ["round 197: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 197: the gateway routes each request by policy", 32),
        ["round 197: the gateway routes", "each request by policy"],
    ),
    (
        ("round 197: memory grows until the buffer is full", 4),
        ["round", "197:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 197: memory grows until the buffer is full", 8),
        ["round", "197:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 197: memory grows until the buffer is full", 12),
        ["round 197:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 197: memory grows until the buffer is full", 16),
        ["round 197:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 197: memory grows until the buffer is full", 24), ["round 197: memory grows", "until the buffer is full"]),
    (("round 197: memory grows until the buffer is full", 32), ["round 197: memory grows until", "the buffer is full"]),
    (
        ("round 197: the cluster mirrors every packet twice", 4),
        ["round", "197:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 197: the cluster mirrors every packet twice", 8),
        ["round", "197: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 197: the cluster mirrors every packet twice", 12),
        ["round 197:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 197: the cluster mirrors every packet twice", 16),
        ["round 197: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 197: the cluster mirrors every packet twice", 24),
        ["round 197: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 197: the cluster mirrors every packet twice", 32),
        ["round 197: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", 4),
        ["round", "197:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", 8),
        ["round", "197:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", 12),
        ["round 197:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", 16),
        ["round 197:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", 24),
        ["round 197: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", 32),
        ["round 197: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 197: a long session ends when the candle dies", 4),
        ["round", "197:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 197: a long session ends when the candle dies", 8),
        ["round", "197: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 197: a long session ends when the candle dies", 12),
        ["round 197: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 197: a long session ends when the candle dies", 16),
        ["round 197: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 197: a long session ends when the candle dies", 24),
        ["round 197: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 197: a long session ends when the candle dies", 32),
        ["round 197: a long session ends", "when the candle dies"],
    ),
    (
        ("round 197: encode the prompt then map the result", 4),
        ["round", "197:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 197: encode the prompt then map the result", 8),
        ["round", "197:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 197: encode the prompt then map the result", 12),
        ["round 197:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 197: encode the prompt then map the result", 16),
        ["round 197:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 197: encode the prompt then map the result", 24),
        ["round 197: encode the", "prompt then map the", "result"],
    ),
    (("round 197: encode the prompt then map the result", 32), ["round 197: encode the prompt", "then map the result"]),
    (
        ("round 197: the kernel wakes the worker at dawn", 4),
        ["round", "197:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 197: the kernel wakes the worker at dawn", 8),
        ["round", "197: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 197: the kernel wakes the worker at dawn", 12),
        ["round 197:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 197: the kernel wakes the worker at dawn", 16), ["round 197: the", "kernel wakes the", "worker at dawn"]),
    (("round 197: the kernel wakes the worker at dawn", 24), ["round 197: the kernel", "wakes the worker at dawn"]),
    (("round 197: the kernel wakes the worker at dawn", 32), ["round 197: the kernel wakes the", "worker at dawn"]),
    (
        ("round 197: service latency drops after the patch", 4),
        ["round", "197:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 197: service latency drops after the patch", 8),
        ["round", "197:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 197: service latency drops after the patch", 12),
        ["round 197:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 197: service latency drops after the patch", 16),
        ["round 197:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 197: service latency drops after the patch", 24),
        ["round 197: service", "latency drops after the", "patch"],
    ),
    (("round 197: service latency drops after the patch", 32), ["round 197: service latency drops", "after the patch"]),
    (
        ("round 197: the library caches every vector it sees", 4),
        ["round", "197:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 197: the library caches every vector it sees", 8),
        ["round", "197: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 197: the library caches every vector it sees", 12),
        ["round 197:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 197: the library caches every vector it sees", 16),
        ["round 197: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 197: the library caches every vector it sees", 24),
        ["round 197: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 197: the library caches every vector it sees", 32),
        ["round 197: the library caches", "every vector it sees"],
    ),
    (
        ("round 197: agents argue then the debate resolves", 4),
        ["round", "197:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 197: agents argue then the debate resolves", 8),
        ["round", "197:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 197: agents argue then the debate resolves", 12),
        ["round 197:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 197: agents argue then the debate resolves", 16),
        ["round 197:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 197: agents argue then the debate resolves", 24), ["round 197: agents argue", "then the debate resolves"]),
    (("round 197: agents argue then the debate resolves", 32), ["round 197: agents argue then the", "debate resolves"]),
    (
        ("round 197: the filter keeps only strong matches", 4),
        ["round", "197:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 197: the filter keeps only strong matches", 8),
        ["round", "197: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 197: the filter keeps only strong matches", 12),
        ["round 197:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 197: the filter keeps only strong matches", 16),
        ["round 197: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 197: the filter keeps only strong matches", 24),
        ["round 197: the filter", "keeps only strong", "matches"],
    ),
    (("round 197: the filter keeps only strong matches", 32), ["round 197: the filter keeps only", "strong matches"]),
    (
        ("round 197: the model answers with a short reply", 4),
        ["round", "197:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 197: the model answers with a short reply", 8),
        ["round", "197: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 197: the model answers with a short reply", 12),
        ["round 197:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 197: the model answers with a short reply", 16),
        ["round 197: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 197: the model answers with a short reply", 24),
        ["round 197: the model", "answers with a short", "reply"],
    ),
    (("round 197: the model answers with a short reply", 32), ["round 197: the model answers", "with a short reply"]),
    (
        ("round 197: the recorder stores the reasoning trace", 4),
        ["round", "197:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 197: the recorder stores the reasoning trace", 8),
        ["round", "197: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 197: the recorder stores the reasoning trace", 12),
        ["round 197:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 197: the recorder stores the reasoning trace", 16),
        ["round 197: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 197: the recorder stores the reasoning trace", 24),
        ["round 197: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 197: the recorder stores the reasoning trace", 32),
        ["round 197: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 197: the angel watches the processor run", 4),
        ["round", "197:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 197: the angel watches the processor run", 8),
        ["round", "197: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 197: the angel watches the processor run", 12),
        ["round 197:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 197: the angel watches the processor run", 16),
        ["round 197: the", "angel watches", "the processor", "run"],
    ),
    (("round 197: the angel watches the processor run", 24), ["round 197: the angel", "watches the processor", "run"]),
    (("round 197: the angel watches the processor run", 32), ["round 197: the angel watches the", "processor run"]),
    (
        ("round 197: angle of the vector decides the match", 4),
        ["round", "197:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 197: angle of the vector decides the match", 8),
        ["round", "197:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 197: angle of the vector decides the match", 12),
        ["round 197:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 197: angle of the vector decides the match", 16),
        ["round 197: angle", "of the vector", "decides the", "match"],
    ),
    (("round 197: angle of the vector decides the match", 24), ["round 197: angle of the", "vector decides the match"]),
    (("round 197: angle of the vector decides the match", 32), ["round 197: angle of the vector", "decides the match"]),
    (
        ("round 197: the candle burns twice as long at night", 4),
        ["round", "197:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 197: the candle burns twice as long at night", 8),
        ["round", "197: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 197: the candle burns twice as long at night", 12),
        ["round 197:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 197: the candle burns twice as long at night", 16),
        ["round 197: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 197: the candle burns twice as long at night", 24),
        ["round 197: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 197: the candle burns twice as long at night", 32),
        ["round 197: the candle burns", "twice as long at night"],
    ),
    (
        ("round 197: a mirror of the universe in one line", 4),
        ["round", "197:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 197: a mirror of the universe in one line", 8),
        ["round", "197: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 197: a mirror of the universe in one line", 12),
        ["round 197: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 197: a mirror of the universe in one line", 16),
        ["round 197: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 197: a mirror of the universe in one line", 24), ["round 197: a mirror of", "the universe in one line"]),
    (("round 197: a mirror of the universe in one line", 32), ["round 197: a mirror of the", "universe in one line"]),
    (
        ("round 197: the queue drains before the storm", 4),
        ["round", "197:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 197: the queue drains before the storm", 8),
        ["round", "197: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 197: the queue drains before the storm", 12),
        ["round 197:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 197: the queue drains before the storm", 16), ["round 197: the", "queue drains", "before the storm"]),
    (("round 197: the queue drains before the storm", 24), ["round 197: the queue", "drains before the storm"]),
    (("round 197: the queue drains before the storm", 32), ["round 197: the queue drains", "before the storm"]),
    (
        ("kitten197 sitting197 agent197 angle197 universe197 memory197", 6),
        ["kitten197", "sitting197", "agent197", "angle197", "universe197", "memory197"],
    ),
    (
        ("kitten197 sitting197 agent197 angle197 universe197 memory197", 10),
        ["kitten197", "sitting197", "agent197", "angle197", "universe197", "memory197"],
    ),
    (
        ("kitten197 sitting197 agent197 angle197 universe197 memory197", 18),
        ["kitten197", "sitting197", "agent197 angle197", "universe197", "memory197"],
    ),
    (
        ("kitten197 sitting197 agent197 angle197 universe197 memory197", 28),
        ["kitten197 sitting197", "agent197 angle197", "universe197 memory197"],
    ),
    (
        ("sitting197 agent197 angle197 universe197 memory197 stream197", 6),
        ["sitting197", "agent197", "angle197", "universe197", "memory197", "stream197"],
    ),
    (
        ("sitting197 agent197 angle197 universe197 memory197 stream197", 10),
        ["sitting197", "agent197", "angle197", "universe197", "memory197", "stream197"],
    ),
    (
        ("sitting197 agent197 angle197 universe197 memory197 stream197", 18),
        ["sitting197", "agent197 angle197", "universe197", "memory197", "stream197"],
    ),
    (
        ("sitting197 agent197 angle197 universe197 memory197 stream197", 28),
        ["sitting197 agent197 angle197", "universe197 memory197", "stream197"],
    ),
    (
        ("agent197 angle197 universe197 memory197 stream197 context197", 6),
        ["agent197", "angle197", "universe197", "memory197", "stream197", "context197"],
    ),
    (
        ("agent197 angle197 universe197 memory197 stream197 context197", 10),
        ["agent197", "angle197", "universe197", "memory197", "stream197", "context197"],
    ),
    (
        ("agent197 angle197 universe197 memory197 stream197 context197", 18),
        ["agent197 angle197", "universe197", "memory197", "stream197", "context197"],
    ),
    (
        ("agent197 angle197 universe197 memory197 stream197 context197", 28),
        ["agent197 angle197", "universe197 memory197", "stream197 context197"],
    ),
    (
        ("angle197 universe197 memory197 stream197 context197 knowledge197", 6),
        ["angle197", "universe197", "memory197", "stream197", "context197", "knowledge197"],
    ),
    (
        ("angle197 universe197 memory197 stream197 context197 knowledge197", 10),
        ["angle197", "universe197", "memory197", "stream197", "context197", "knowledge197"],
    ),
    (
        ("angle197 universe197 memory197 stream197 context197 knowledge197", 18),
        ["angle197", "universe197", "memory197", "stream197", "context197", "knowledge197"],
    ),
    (
        ("angle197 universe197 memory197 stream197 context197 knowledge197", 28),
        ["angle197 universe197", "memory197 stream197", "context197 knowledge197"],
    ),
    (
        ("universe197 memory197 stream197 context197 knowledge197 vector197", 6),
        ["universe197", "memory197", "stream197", "context197", "knowledge197", "vector197"],
    ),
    (
        ("universe197 memory197 stream197 context197 knowledge197 vector197", 10),
        ["universe197", "memory197", "stream197", "context197", "knowledge197", "vector197"],
    ),
    (
        ("universe197 memory197 stream197 context197 knowledge197 vector197", 18),
        ["universe197", "memory197", "stream197", "context197", "knowledge197", "vector197"],
    ),
    (
        ("universe197 memory197 stream197 context197 knowledge197 vector197", 28),
        ["universe197 memory197", "stream197 context197", "knowledge197 vector197"],
    ),
    (
        ("memory197 stream197 context197 knowledge197 vector197 processor197", 6),
        ["memory197", "stream197", "context197", "knowledge197", "vector197", "processor197"],
    ),
    (
        ("memory197 stream197 context197 knowledge197 vector197 processor197", 10),
        ["memory197", "stream197", "context197", "knowledge197", "vector197", "processor197"],
    ),
    (
        ("memory197 stream197 context197 knowledge197 vector197 processor197", 18),
        ["memory197", "stream197", "context197", "knowledge197", "vector197", "processor197"],
    ),
    (
        ("memory197 stream197 context197 knowledge197 vector197 processor197", 28),
        ["memory197 stream197", "context197 knowledge197", "vector197 processor197"],
    ),
    (
        ("stream197 context197 knowledge197 vector197 processor197 reasoning197", 6),
        ["stream197", "context197", "knowledge197", "vector197", "processor197", "reasoning197"],
    ),
    (
        ("stream197 context197 knowledge197 vector197 processor197 reasoning197", 10),
        ["stream197", "context197", "knowledge197", "vector197", "processor197", "reasoning197"],
    ),
    (
        ("stream197 context197 knowledge197 vector197 processor197 reasoning197", 18),
        ["stream197", "context197", "knowledge197", "vector197", "processor197", "reasoning197"],
    ),
    (
        ("stream197 context197 knowledge197 vector197 processor197 reasoning197", 28),
        ["stream197 context197", "knowledge197 vector197", "processor197 reasoning197"],
    ),
    (
        ("context197 knowledge197 vector197 processor197 reasoning197 machine197", 6),
        ["context197", "knowledge197", "vector197", "processor197", "reasoning197", "machine197"],
    ),
    (
        ("context197 knowledge197 vector197 processor197 reasoning197 machine197", 10),
        ["context197", "knowledge197", "vector197", "processor197", "reasoning197", "machine197"],
    ),
    (
        ("context197 knowledge197 vector197 processor197 reasoning197 machine197", 18),
        ["context197", "knowledge197", "vector197", "processor197", "reasoning197", "machine197"],
    ),
    (
        ("context197 knowledge197 vector197 processor197 reasoning197 machine197", 28),
        ["context197 knowledge197", "vector197 processor197", "reasoning197 machine197"],
    ),
    (
        ("knowledge197 vector197 processor197 reasoning197 machine197 learning197", 6),
        ["knowledge197", "vector197", "processor197", "reasoning197", "machine197", "learning197"],
    ),
    (
        ("knowledge197 vector197 processor197 reasoning197 machine197 learning197", 10),
        ["knowledge197", "vector197", "processor197", "reasoning197", "machine197", "learning197"],
    ),
    (
        ("knowledge197 vector197 processor197 reasoning197 machine197 learning197", 18),
        ["knowledge197", "vector197", "processor197", "reasoning197", "machine197", "learning197"],
    ),
    (
        ("knowledge197 vector197 processor197 reasoning197 machine197 learning197", 28),
        ["knowledge197 vector197", "processor197 reasoning197", "machine197 learning197"],
    ),
    (
        ("vector197 processor197 reasoning197 machine197 learning197 model197", 6),
        ["vector197", "processor197", "reasoning197", "machine197", "learning197", "model197"],
    ),
    (
        ("vector197 processor197 reasoning197 machine197 learning197 model197", 10),
        ["vector197", "processor197", "reasoning197", "machine197", "learning197", "model197"],
    ),
    (
        ("vector197 processor197 reasoning197 machine197 learning197 model197", 18),
        ["vector197", "processor197", "reasoning197", "machine197", "learning197", "model197"],
    ),
    (
        ("vector197 processor197 reasoning197 machine197 learning197 model197", 28),
        ["vector197 processor197", "reasoning197 machine197", "learning197 model197"],
    ),
    (
        ("processor197 reasoning197 machine197 learning197 model197 token197", 6),
        ["processor197", "reasoning197", "machine197", "learning197", "model197", "token197"],
    ),
    (
        ("processor197 reasoning197 machine197 learning197 model197 token197", 10),
        ["processor197", "reasoning197", "machine197", "learning197", "model197", "token197"],
    ),
    (
        ("processor197 reasoning197 machine197 learning197 model197 token197", 18),
        ["processor197", "reasoning197", "machine197", "learning197", "model197 token197"],
    ),
    (
        ("processor197 reasoning197 machine197 learning197 model197 token197", 28),
        ["processor197 reasoning197", "machine197 learning197", "model197 token197"],
    ),
    (
        ("reasoning197 machine197 learning197 model197 token197 prompt197", 6),
        ["reasoning197", "machine197", "learning197", "model197", "token197", "prompt197"],
    ),
    (
        ("reasoning197 machine197 learning197 model197 token197 prompt197", 10),
        ["reasoning197", "machine197", "learning197", "model197", "token197", "prompt197"],
    ),
    (
        ("reasoning197 machine197 learning197 model197 token197 prompt197", 18),
        ["reasoning197", "machine197", "learning197", "model197 token197", "prompt197"],
    ),
    (
        ("reasoning197 machine197 learning197 model197 token197 prompt197", 28),
        ["reasoning197 machine197", "learning197 model197", "token197 prompt197"],
    ),
    (
        ("machine197 learning197 model197 token197 prompt197 session197", 6),
        ["machine197", "learning197", "model197", "token197", "prompt197", "session197"],
    ),
    (
        ("machine197 learning197 model197 token197 prompt197 session197", 10),
        ["machine197", "learning197", "model197", "token197", "prompt197", "session197"],
    ),
    (
        ("machine197 learning197 model197 token197 prompt197 session197", 18),
        ["machine197", "learning197", "model197 token197", "prompt197", "session197"],
    ),
    (
        ("machine197 learning197 model197 token197 prompt197 session197", 28),
        ["machine197 learning197", "model197 token197 prompt197", "session197"],
    ),
    (
        ("learning197 model197 token197 prompt197 session197 library197", 6),
        ["learning197", "model197", "token197", "prompt197", "session197", "library197"],
    ),
    (
        ("learning197 model197 token197 prompt197 session197 library197", 10),
        ["learning197", "model197", "token197", "prompt197", "session197", "library197"],
    ),
    (
        ("learning197 model197 token197 prompt197 session197 library197", 18),
        ["learning197", "model197 token197", "prompt197", "session197", "library197"],
    ),
    (
        ("learning197 model197 token197 prompt197 session197 library197", 28),
        ["learning197 model197", "token197 prompt197", "session197 library197"],
    ),
    (
        ("model197 token197 prompt197 session197 library197 service197", 6),
        ["model197", "token197", "prompt197", "session197", "library197", "service197"],
    ),
    (
        ("model197 token197 prompt197 session197 library197 service197", 10),
        ["model197", "token197", "prompt197", "session197", "library197", "service197"],
    ),
    (
        ("model197 token197 prompt197 session197 library197 service197", 18),
        ["model197 token197", "prompt197", "session197", "library197", "service197"],
    ),
    (
        ("model197 token197 prompt197 session197 library197 service197", 28),
        ["model197 token197 prompt197", "session197 library197", "service197"],
    ),
    (
        ("token197 prompt197 session197 library197 service197 gateway197", 6),
        ["token197", "prompt197", "session197", "library197", "service197", "gateway197"],
    ),
    (
        ("token197 prompt197 session197 library197 service197 gateway197", 10),
        ["token197", "prompt197", "session197", "library197", "service197", "gateway197"],
    ),
    (
        ("token197 prompt197 session197 library197 service197 gateway197", 18),
        ["token197 prompt197", "session197", "library197", "service197", "gateway197"],
    ),
    (
        ("token197 prompt197 session197 library197 service197 gateway197", 28),
        ["token197 prompt197", "session197 library197", "service197 gateway197"],
    ),
    (
        ("prompt197 session197 library197 service197 gateway197 storage197", 6),
        ["prompt197", "session197", "library197", "service197", "gateway197", "storage197"],
    ),
    (
        ("prompt197 session197 library197 service197 gateway197 storage197", 10),
        ["prompt197", "session197", "library197", "service197", "gateway197", "storage197"],
    ),
    (
        ("prompt197 session197 library197 service197 gateway197 storage197", 18),
        ["prompt197", "session197", "library197", "service197", "gateway197", "storage197"],
    ),
    (
        ("prompt197 session197 library197 service197 gateway197 storage197", 28),
        ["prompt197 session197", "library197 service197", "gateway197 storage197"],
    ),
    (
        ("session197 library197 service197 gateway197 storage197 network197", 6),
        ["session197", "library197", "service197", "gateway197", "storage197", "network197"],
    ),
    (
        ("session197 library197 service197 gateway197 storage197 network197", 10),
        ["session197", "library197", "service197", "gateway197", "storage197", "network197"],
    ),
    (
        ("session197 library197 service197 gateway197 storage197 network197", 18),
        ["session197", "library197", "service197", "gateway197", "storage197", "network197"],
    ),
    (
        ("session197 library197 service197 gateway197 storage197 network197", 28),
        ["session197 library197", "service197 gateway197", "storage197 network197"],
    ),
    (
        ("library197 service197 gateway197 storage197 network197 latency197", 6),
        ["library197", "service197", "gateway197", "storage197", "network197", "latency197"],
    ),
    (
        ("library197 service197 gateway197 storage197 network197 latency197", 10),
        ["library197", "service197", "gateway197", "storage197", "network197", "latency197"],
    ),
    (
        ("library197 service197 gateway197 storage197 network197 latency197", 18),
        ["library197", "service197", "gateway197", "storage197", "network197", "latency197"],
    ),
    (
        ("library197 service197 gateway197 storage197 network197 latency197", 28),
        ["library197 service197", "gateway197 storage197", "network197 latency197"],
    ),
    (
        ("service197 gateway197 storage197 network197 latency197 buffer197", 6),
        ["service197", "gateway197", "storage197", "network197", "latency197", "buffer197"],
    ),
    (
        ("service197 gateway197 storage197 network197 latency197 buffer197", 10),
        ["service197", "gateway197", "storage197", "network197", "latency197", "buffer197"],
    ),
    (
        ("service197 gateway197 storage197 network197 latency197 buffer197", 18),
        ["service197", "gateway197", "storage197", "network197", "latency197", "buffer197"],
    ),
    (
        ("service197 gateway197 storage197 network197 latency197 buffer197", 28),
        ["service197 gateway197", "storage197 network197", "latency197 buffer197"],
    ),
    (
        ("gateway197 storage197 network197 latency197 buffer197 queue197", 6),
        ["gateway197", "storage197", "network197", "latency197", "buffer197", "queue197"],
    ),
    (
        ("gateway197 storage197 network197 latency197 buffer197 queue197", 10),
        ["gateway197", "storage197", "network197", "latency197", "buffer197", "queue197"],
    ),
    (
        ("gateway197 storage197 network197 latency197 buffer197 queue197", 18),
        ["gateway197", "storage197", "network197", "latency197", "buffer197 queue197"],
    ),
    (
        ("gateway197 storage197 network197 latency197 buffer197 queue197", 28),
        ["gateway197 storage197", "network197 latency197", "buffer197 queue197"],
    ),
    (
        ("storage197 network197 latency197 buffer197 queue197 worker197", 6),
        ["storage197", "network197", "latency197", "buffer197", "queue197", "worker197"],
    ),
    (
        ("storage197 network197 latency197 buffer197 queue197 worker197", 10),
        ["storage197", "network197", "latency197", "buffer197", "queue197", "worker197"],
    ),
    (
        ("storage197 network197 latency197 buffer197 queue197 worker197", 18),
        ["storage197", "network197", "latency197", "buffer197 queue197", "worker197"],
    ),
    (
        ("storage197 network197 latency197 buffer197 queue197 worker197", 28),
        ["storage197 network197", "latency197 buffer197", "queue197 worker197"],
    ),
    (
        ("network197 latency197 buffer197 queue197 worker197 kernel197", 6),
        ["network197", "latency197", "buffer197", "queue197", "worker197", "kernel197"],
    ),
    (
        ("network197 latency197 buffer197 queue197 worker197 kernel197", 10),
        ["network197", "latency197", "buffer197", "queue197", "worker197", "kernel197"],
    ),
    (
        ("network197 latency197 buffer197 queue197 worker197 kernel197", 18),
        ["network197", "latency197", "buffer197 queue197", "worker197", "kernel197"],
    ),
    (
        ("network197 latency197 buffer197 queue197 worker197 kernel197", 28),
        ["network197 latency197", "buffer197 queue197 worker197", "kernel197"],
    ),
    (
        ("latency197 buffer197 queue197 worker197 kernel197 signal197", 6),
        ["latency197", "buffer197", "queue197", "worker197", "kernel197", "signal197"],
    ),
    (
        ("latency197 buffer197 queue197 worker197 kernel197 signal197", 10),
        ["latency197", "buffer197", "queue197", "worker197", "kernel197", "signal197"],
    ),
    (
        ("latency197 buffer197 queue197 worker197 kernel197 signal197", 18),
        ["latency197", "buffer197 queue197", "worker197", "kernel197", "signal197"],
    ),
    (
        ("latency197 buffer197 queue197 worker197 kernel197 signal197", 28),
        ["latency197 buffer197", "queue197 worker197 kernel197", "signal197"],
    ),
    (
        ("buffer197 queue197 worker197 kernel197 signal197 packet197", 6),
        ["buffer197", "queue197", "worker197", "kernel197", "signal197", "packet197"],
    ),
    (
        ("buffer197 queue197 worker197 kernel197 signal197 packet197", 10),
        ["buffer197", "queue197", "worker197", "kernel197", "signal197", "packet197"],
    ),
    (
        ("buffer197 queue197 worker197 kernel197 signal197 packet197", 18),
        ["buffer197 queue197", "worker197", "kernel197", "signal197", "packet197"],
    ),
    (
        ("buffer197 queue197 worker197 kernel197 signal197 packet197", 28),
        ["buffer197 queue197 worker197", "kernel197 signal197", "packet197"],
    ),
    (
        ("queue197 worker197 kernel197 signal197 packet197 router197", 6),
        ["queue197", "worker197", "kernel197", "signal197", "packet197", "router197"],
    ),
    (
        ("queue197 worker197 kernel197 signal197 packet197 router197", 10),
        ["queue197", "worker197", "kernel197", "signal197", "packet197", "router197"],
    ),
    (
        ("queue197 worker197 kernel197 signal197 packet197 router197", 18),
        ["queue197 worker197", "kernel197", "signal197", "packet197", "router197"],
    ),
    (
        ("queue197 worker197 kernel197 signal197 packet197 router197", 28),
        ["queue197 worker197 kernel197", "signal197 packet197", "router197"],
    ),
    (
        ("worker197 kernel197 signal197 packet197 router197 cluster197", 6),
        ["worker197", "kernel197", "signal197", "packet197", "router197", "cluster197"],
    ),
    (
        ("worker197 kernel197 signal197 packet197 router197 cluster197", 10),
        ["worker197", "kernel197", "signal197", "packet197", "router197", "cluster197"],
    ),
    (
        ("worker197 kernel197 signal197 packet197 router197 cluster197", 18),
        ["worker197", "kernel197", "signal197", "packet197", "router197", "cluster197"],
    ),
    (
        ("worker197 kernel197 signal197 packet197 router197 cluster197", 28),
        ["worker197 kernel197", "signal197 packet197", "router197 cluster197"],
    ),
    (
        ("kernel197 signal197 packet197 router197 cluster197 mirror197", 6),
        ["kernel197", "signal197", "packet197", "router197", "cluster197", "mirror197"],
    ),
    (
        ("kernel197 signal197 packet197 router197 cluster197 mirror197", 10),
        ["kernel197", "signal197", "packet197", "router197", "cluster197", "mirror197"],
    ),
    (
        ("kernel197 signal197 packet197 router197 cluster197 mirror197", 18),
        ["kernel197", "signal197", "packet197", "router197", "cluster197", "mirror197"],
    ),
    (
        ("kernel197 signal197 packet197 router197 cluster197 mirror197", 28),
        ["kernel197 signal197", "packet197 router197", "cluster197 mirror197"],
    ),
    (
        ("signal197 packet197 router197 cluster197 mirror197 filter197", 6),
        ["signal197", "packet197", "router197", "cluster197", "mirror197", "filter197"],
    ),
    (
        ("signal197 packet197 router197 cluster197 mirror197 filter197", 10),
        ["signal197", "packet197", "router197", "cluster197", "mirror197", "filter197"],
    ),
    (
        ("signal197 packet197 router197 cluster197 mirror197 filter197", 18),
        ["signal197", "packet197", "router197", "cluster197", "mirror197", "filter197"],
    ),
    (
        ("signal197 packet197 router197 cluster197 mirror197 filter197", 28),
        ["signal197 packet197", "router197 cluster197", "mirror197 filter197"],
    ),
    (
        ("packet197 router197 cluster197 mirror197 filter197 ranking197", 6),
        ["packet197", "router197", "cluster197", "mirror197", "filter197", "ranking197"],
    ),
    (
        ("packet197 router197 cluster197 mirror197 filter197 ranking197", 10),
        ["packet197", "router197", "cluster197", "mirror197", "filter197", "ranking197"],
    ),
    (
        ("packet197 router197 cluster197 mirror197 filter197 ranking197", 18),
        ["packet197", "router197", "cluster197", "mirror197", "filter197", "ranking197"],
    ),
    (
        ("packet197 router197 cluster197 mirror197 filter197 ranking197", 28),
        ["packet197 router197", "cluster197 mirror197", "filter197 ranking197"],
    ),
    (
        ("router197 cluster197 mirror197 filter197 ranking197 encoding197", 6),
        ["router197", "cluster197", "mirror197", "filter197", "ranking197", "encoding197"],
    ),
    (
        ("router197 cluster197 mirror197 filter197 ranking197 encoding197", 10),
        ["router197", "cluster197", "mirror197", "filter197", "ranking197", "encoding197"],
    ),
    (
        ("router197 cluster197 mirror197 filter197 ranking197 encoding197", 18),
        ["router197", "cluster197", "mirror197", "filter197", "ranking197", "encoding197"],
    ),
    (
        ("router197 cluster197 mirror197 filter197 ranking197 encoding197", 28),
        ["router197 cluster197", "mirror197 filter197", "ranking197 encoding197"],
    ),
    (
        ("cluster197 mirror197 filter197 ranking197 encoding197 mapping197", 6),
        ["cluster197", "mirror197", "filter197", "ranking197", "encoding197", "mapping197"],
    ),
    (
        ("cluster197 mirror197 filter197 ranking197 encoding197 mapping197", 10),
        ["cluster197", "mirror197", "filter197", "ranking197", "encoding197", "mapping197"],
    ),
    (
        ("cluster197 mirror197 filter197 ranking197 encoding197 mapping197", 18),
        ["cluster197", "mirror197", "filter197", "ranking197", "encoding197", "mapping197"],
    ),
    (
        ("cluster197 mirror197 filter197 ranking197 encoding197 mapping197", 28),
        ["cluster197 mirror197", "filter197 ranking197", "encoding197 mapping197"],
    ),
    (
        ("mirror197 filter197 ranking197 encoding197 mapping197 record197", 6),
        ["mirror197", "filter197", "ranking197", "encoding197", "mapping197", "record197"],
    ),
    (
        ("mirror197 filter197 ranking197 encoding197 mapping197 record197", 10),
        ["mirror197", "filter197", "ranking197", "encoding197", "mapping197", "record197"],
    ),
    (
        ("mirror197 filter197 ranking197 encoding197 mapping197 record197", 18),
        ["mirror197", "filter197", "ranking197", "encoding197", "mapping197", "record197"],
    ),
    (
        ("mirror197 filter197 ranking197 encoding197 mapping197 record197", 28),
        ["mirror197 filter197", "ranking197 encoding197", "mapping197 record197"],
    ),
    (
        ("filter197 ranking197 encoding197 mapping197 record197 candle197", 6),
        ["filter197", "ranking197", "encoding197", "mapping197", "record197", "candle197"],
    ),
    (
        ("filter197 ranking197 encoding197 mapping197 record197 candle197", 10),
        ["filter197", "ranking197", "encoding197", "mapping197", "record197", "candle197"],
    ),
    (
        ("filter197 ranking197 encoding197 mapping197 record197 candle197", 18),
        ["filter197", "ranking197", "encoding197", "mapping197", "record197", "candle197"],
    ),
    (
        ("filter197 ranking197 encoding197 mapping197 record197 candle197", 28),
        ["filter197 ranking197", "encoding197 mapping197", "record197 candle197"],
    ),
    (
        ("ranking197 encoding197 mapping197 record197 candle197 thread197", 6),
        ["ranking197", "encoding197", "mapping197", "record197", "candle197", "thread197"],
    ),
    (
        ("ranking197 encoding197 mapping197 record197 candle197 thread197", 10),
        ["ranking197", "encoding197", "mapping197", "record197", "candle197", "thread197"],
    ),
    (
        ("ranking197 encoding197 mapping197 record197 candle197 thread197", 18),
        ["ranking197", "encoding197", "mapping197", "record197", "candle197", "thread197"],
    ),
    (
        ("ranking197 encoding197 mapping197 record197 candle197 thread197", 28),
        ["ranking197 encoding197", "mapping197 record197", "candle197 thread197"],
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
