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
        ("round 62: the quick brown fox jumps over the lazy dog", 4),
        ["round", "62:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 62: the quick brown fox jumps over the lazy dog", 8),
        ["round", "62: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 62: the quick brown fox jumps over the lazy dog", 12),
        ["round 62:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 62: the quick brown fox jumps over the lazy dog", 16),
        ["round 62: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 62: the quick brown fox jumps over the lazy dog", 24),
        ["round 62: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 62: the quick brown fox jumps over the lazy dog", 32),
        ["round 62: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 62: agentuniverse is a framework for multi agents", 4),
        ["round", "62:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 62: agentuniverse is a framework for multi agents", 8),
        ["round", "62:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 62: agentuniverse is a framework for multi agents", 12),
        ["round 62:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 62: agentuniverse is a framework for multi agents", 16),
        ["round 62:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 62: agentuniverse is a framework for multi agents", 24),
        ["round 62: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 62: agentuniverse is a framework for multi agents", 32),
        ["round 62: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 62: knowledge stored as vectors enables retrieval", 4),
        ["round", "62:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 62: knowledge stored as vectors enables retrieval", 8),
        ["round", "62:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 62: knowledge stored as vectors enables retrieval", 12),
        ["round 62:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 62: knowledge stored as vectors enables retrieval", 16),
        ["round 62:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 62: knowledge stored as vectors enables retrieval", 24),
        ["round 62: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 62: knowledge stored as vectors enables retrieval", 32),
        ["round 62: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 62: the processor reads the record then stops", 4),
        ["round", "62:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 62: the processor reads the record then stops", 8),
        ["round", "62: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 62: the processor reads the record then stops", 12),
        ["round 62:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 62: the processor reads the record then stops", 16),
        ["round 62: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 62: the processor reads the record then stops", 24),
        ["round 62: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 62: the processor reads the record then stops", 32),
        ["round 62: the processor reads", "the record then stops"],
    ),
    (
        ("round 62: a worker pulls the next task from the queue", 4),
        ["round", "62:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 62: a worker pulls the next task from the queue", 8),
        ["round", "62: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 62: a worker pulls the next task from the queue", 12),
        ["round 62: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 62: a worker pulls the next task from the queue", 16),
        ["round 62: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 62: a worker pulls the next task from the queue", 24),
        ["round 62: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 62: a worker pulls the next task from the queue", 32),
        ["round 62: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 62: signals travel through the network layer", 4),
        ["round", "62:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 62: signals travel through the network layer", 8),
        ["round", "62:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 62: signals travel through the network layer", 12),
        ["round 62:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 62: signals travel through the network layer", 16),
        ["round 62:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 62: signals travel through the network layer", 24),
        ["round 62: signals travel", "through the network", "layer"],
    ),
    (
        ("round 62: signals travel through the network layer", 32),
        ["round 62: signals travel through", "the network layer"],
    ),
    (
        ("round 62: the gateway routes each request by policy", 4),
        ["round", "62:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 62: the gateway routes each request by policy", 8),
        ["round", "62: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 62: the gateway routes each request by policy", 12),
        ["round 62:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 62: the gateway routes each request by policy", 16),
        ["round 62: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 62: the gateway routes each request by policy", 24),
        ["round 62: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 62: the gateway routes each request by policy", 32),
        ["round 62: the gateway routes", "each request by policy"],
    ),
    (
        ("round 62: memory grows until the buffer is full", 4),
        ["round", "62:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 62: memory grows until the buffer is full", 8),
        ["round", "62:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 62: memory grows until the buffer is full", 12),
        ["round 62:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 62: memory grows until the buffer is full", 16),
        ["round 62: memory", "grows until the", "buffer is full"],
    ),
    (("round 62: memory grows until the buffer is full", 24), ["round 62: memory grows", "until the buffer is full"]),
    (("round 62: memory grows until the buffer is full", 32), ["round 62: memory grows until the", "buffer is full"]),
    (
        ("round 62: the cluster mirrors every packet twice", 4),
        ["round", "62:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 62: the cluster mirrors every packet twice", 8),
        ["round", "62: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 62: the cluster mirrors every packet twice", 12),
        ["round 62:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 62: the cluster mirrors every packet twice", 16),
        ["round 62: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 62: the cluster mirrors every packet twice", 24),
        ["round 62: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 62: the cluster mirrors every packet twice", 32), ["round 62: the cluster mirrors", "every packet twice"]),
    (
        ("round 62: ranking uses tokens learned from the corpus", 4),
        ["round", "62:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 62: ranking uses tokens learned from the corpus", 8),
        ["round", "62:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 62: ranking uses tokens learned from the corpus", 12),
        ["round 62:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 62: ranking uses tokens learned from the corpus", 16),
        ["round 62:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 62: ranking uses tokens learned from the corpus", 24),
        ["round 62: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 62: ranking uses tokens learned from the corpus", 32),
        ["round 62: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 62: a long session ends when the candle dies", 4),
        ["round", "62:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 62: a long session ends when the candle dies", 8),
        ["round", "62: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 62: a long session ends when the candle dies", 12),
        ["round 62: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 62: a long session ends when the candle dies", 16),
        ["round 62: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 62: a long session ends when the candle dies", 24),
        ["round 62: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 62: a long session ends when the candle dies", 32),
        ["round 62: a long session ends", "when the candle dies"],
    ),
    (
        ("round 62: encode the prompt then map the result", 4),
        ["round", "62:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 62: encode the prompt then map the result", 8),
        ["round", "62:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 62: encode the prompt then map the result", 12),
        ["round 62:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 62: encode the prompt then map the result", 16),
        ["round 62: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 62: encode the prompt then map the result", 24),
        ["round 62: encode the", "prompt then map the", "result"],
    ),
    (("round 62: encode the prompt then map the result", 32), ["round 62: encode the prompt then", "map the result"]),
    (
        ("round 62: the kernel wakes the worker at dawn", 4),
        ["round", "62:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 62: the kernel wakes the worker at dawn", 8),
        ["round", "62: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 62: the kernel wakes the worker at dawn", 12),
        ["round 62:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 62: the kernel wakes the worker at dawn", 16), ["round 62: the", "kernel wakes the", "worker at dawn"]),
    (("round 62: the kernel wakes the worker at dawn", 24), ["round 62: the kernel", "wakes the worker at dawn"]),
    (("round 62: the kernel wakes the worker at dawn", 32), ["round 62: the kernel wakes the", "worker at dawn"]),
    (
        ("round 62: service latency drops after the patch", 4),
        ["round", "62:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 62: service latency drops after the patch", 8),
        ["round", "62:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 62: service latency drops after the patch", 12),
        ["round 62:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 62: service latency drops after the patch", 16),
        ["round 62:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 62: service latency drops after the patch", 24),
        ["round 62: service", "latency drops after the", "patch"],
    ),
    (("round 62: service latency drops after the patch", 32), ["round 62: service latency drops", "after the patch"]),
    (
        ("round 62: the library caches every vector it sees", 4),
        ["round", "62:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 62: the library caches every vector it sees", 8),
        ["round", "62: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 62: the library caches every vector it sees", 12),
        ["round 62:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 62: the library caches every vector it sees", 16),
        ["round 62: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 62: the library caches every vector it sees", 24),
        ["round 62: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 62: the library caches every vector it sees", 32),
        ["round 62: the library caches", "every vector it sees"],
    ),
    (
        ("round 62: agents argue then the debate resolves", 4),
        ["round", "62:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 62: agents argue then the debate resolves", 8),
        ["round", "62:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 62: agents argue then the debate resolves", 12),
        ["round 62:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 62: agents argue then the debate resolves", 16),
        ["round 62: agents", "argue then the", "debate resolves"],
    ),
    (("round 62: agents argue then the debate resolves", 24), ["round 62: agents argue", "then the debate resolves"]),
    (("round 62: agents argue then the debate resolves", 32), ["round 62: agents argue then the", "debate resolves"]),
    (
        ("round 62: the filter keeps only strong matches", 4),
        ["round", "62:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 62: the filter keeps only strong matches", 8),
        ["round", "62: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 62: the filter keeps only strong matches", 12),
        ["round 62:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 62: the filter keeps only strong matches", 16),
        ["round 62: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 62: the filter keeps only strong matches", 24), ["round 62: the filter", "keeps only strong", "matches"]),
    (("round 62: the filter keeps only strong matches", 32), ["round 62: the filter keeps only", "strong matches"]),
    (
        ("round 62: the model answers with a short reply", 4),
        ["round", "62:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 62: the model answers with a short reply", 8),
        ["round", "62: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 62: the model answers with a short reply", 12),
        ["round 62:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 62: the model answers with a short reply", 16),
        ["round 62: the", "model answers", "with a short", "reply"],
    ),
    (("round 62: the model answers with a short reply", 24), ["round 62: the model", "answers with a short", "reply"]),
    (("round 62: the model answers with a short reply", 32), ["round 62: the model answers with", "a short reply"]),
    (
        ("round 62: the recorder stores the reasoning trace", 4),
        ["round", "62:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 62: the recorder stores the reasoning trace", 8),
        ["round", "62: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 62: the recorder stores the reasoning trace", 12),
        ["round 62:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 62: the recorder stores the reasoning trace", 16),
        ["round 62: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 62: the recorder stores the reasoning trace", 24),
        ["round 62: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 62: the recorder stores the reasoning trace", 32),
        ["round 62: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 62: the angel watches the processor run", 4),
        ["round", "62:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 62: the angel watches the processor run", 8),
        ["round", "62: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 62: the angel watches the processor run", 12),
        ["round 62:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 62: the angel watches the processor run", 16), ["round 62: the", "angel watches", "the processor", "run"]),
    (("round 62: the angel watches the processor run", 24), ["round 62: the angel", "watches the processor", "run"]),
    (("round 62: the angel watches the processor run", 32), ["round 62: the angel watches the", "processor run"]),
    (
        ("round 62: angle of the vector decides the match", 4),
        ["round", "62:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 62: angle of the vector decides the match", 8),
        ["round", "62:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 62: angle of the vector decides the match", 12),
        ["round 62:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 62: angle of the vector decides the match", 16),
        ["round 62: angle", "of the vector", "decides the", "match"],
    ),
    (("round 62: angle of the vector decides the match", 24), ["round 62: angle of the", "vector decides the match"]),
    (("round 62: angle of the vector decides the match", 32), ["round 62: angle of the vector", "decides the match"]),
    (
        ("round 62: the candle burns twice as long at night", 4),
        ["round", "62:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 62: the candle burns twice as long at night", 8),
        ["round", "62: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 62: the candle burns twice as long at night", 12),
        ["round 62:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 62: the candle burns twice as long at night", 16),
        ["round 62: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 62: the candle burns twice as long at night", 24),
        ["round 62: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 62: the candle burns twice as long at night", 32),
        ["round 62: the candle burns twice", "as long at night"],
    ),
    (
        ("round 62: a mirror of the universe in one line", 4),
        ["round", "62:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 62: a mirror of the universe in one line", 8),
        ["round", "62: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 62: a mirror of the universe in one line", 12),
        ["round 62: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 62: a mirror of the universe in one line", 16),
        ["round 62: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 62: a mirror of the universe in one line", 24), ["round 62: a mirror of", "the universe in one line"]),
    (("round 62: a mirror of the universe in one line", 32), ["round 62: a mirror of the", "universe in one line"]),
    (
        ("round 62: the queue drains before the storm", 4),
        ["round", "62:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 62: the queue drains before the storm", 8),
        ["round", "62: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 62: the queue drains before the storm", 12), ["round 62:", "the queue", "drains", "before the", "storm"]),
    (("round 62: the queue drains before the storm", 16), ["round 62: the", "queue drains", "before the storm"]),
    (("round 62: the queue drains before the storm", 24), ["round 62: the queue", "drains before the storm"]),
    (("round 62: the queue drains before the storm", 32), ["round 62: the queue drains", "before the storm"]),
    (
        ("kitten62 sitting62 agent62 angle62 universe62 memory62", 6),
        ["kitten62", "sitting62", "agent62", "angle62", "universe62", "memory62"],
    ),
    (
        ("kitten62 sitting62 agent62 angle62 universe62 memory62", 10),
        ["kitten62", "sitting62", "agent62", "angle62", "universe62", "memory62"],
    ),
    (
        ("kitten62 sitting62 agent62 angle62 universe62 memory62", 18),
        ["kitten62 sitting62", "agent62 angle62", "universe62", "memory62"],
    ),
    (
        ("kitten62 sitting62 agent62 angle62 universe62 memory62", 28),
        ["kitten62 sitting62 agent62", "angle62 universe62 memory62"],
    ),
    (
        ("sitting62 agent62 angle62 universe62 memory62 stream62", 6),
        ["sitting62", "agent62", "angle62", "universe62", "memory62", "stream62"],
    ),
    (
        ("sitting62 agent62 angle62 universe62 memory62 stream62", 10),
        ["sitting62", "agent62", "angle62", "universe62", "memory62", "stream62"],
    ),
    (
        ("sitting62 agent62 angle62 universe62 memory62 stream62", 18),
        ["sitting62 agent62", "angle62 universe62", "memory62 stream62"],
    ),
    (
        ("sitting62 agent62 angle62 universe62 memory62 stream62", 28),
        ["sitting62 agent62 angle62", "universe62 memory62 stream62"],
    ),
    (
        ("agent62 angle62 universe62 memory62 stream62 context62", 6),
        ["agent62", "angle62", "universe62", "memory62", "stream62", "context62"],
    ),
    (
        ("agent62 angle62 universe62 memory62 stream62 context62", 10),
        ["agent62", "angle62", "universe62", "memory62", "stream62", "context62"],
    ),
    (
        ("agent62 angle62 universe62 memory62 stream62 context62", 18),
        ["agent62 angle62", "universe62", "memory62 stream62", "context62"],
    ),
    (
        ("agent62 angle62 universe62 memory62 stream62 context62", 28),
        ["agent62 angle62 universe62", "memory62 stream62 context62"],
    ),
    (
        ("angle62 universe62 memory62 stream62 context62 knowledge62", 6),
        ["angle62", "universe62", "memory62", "stream62", "context62", "knowledge62"],
    ),
    (
        ("angle62 universe62 memory62 stream62 context62 knowledge62", 10),
        ["angle62", "universe62", "memory62", "stream62", "context62", "knowledge62"],
    ),
    (
        ("angle62 universe62 memory62 stream62 context62 knowledge62", 18),
        ["angle62 universe62", "memory62 stream62", "context62", "knowledge62"],
    ),
    (
        ("angle62 universe62 memory62 stream62 context62 knowledge62", 28),
        ["angle62 universe62 memory62", "stream62 context62", "knowledge62"],
    ),
    (
        ("universe62 memory62 stream62 context62 knowledge62 vector62", 6),
        ["universe62", "memory62", "stream62", "context62", "knowledge62", "vector62"],
    ),
    (
        ("universe62 memory62 stream62 context62 knowledge62 vector62", 10),
        ["universe62", "memory62", "stream62", "context62", "knowledge62", "vector62"],
    ),
    (
        ("universe62 memory62 stream62 context62 knowledge62 vector62", 18),
        ["universe62", "memory62 stream62", "context62", "knowledge62", "vector62"],
    ),
    (
        ("universe62 memory62 stream62 context62 knowledge62 vector62", 28),
        ["universe62 memory62 stream62", "context62 knowledge62", "vector62"],
    ),
    (
        ("memory62 stream62 context62 knowledge62 vector62 processor62", 6),
        ["memory62", "stream62", "context62", "knowledge62", "vector62", "processor62"],
    ),
    (
        ("memory62 stream62 context62 knowledge62 vector62 processor62", 10),
        ["memory62", "stream62", "context62", "knowledge62", "vector62", "processor62"],
    ),
    (
        ("memory62 stream62 context62 knowledge62 vector62 processor62", 18),
        ["memory62 stream62", "context62", "knowledge62", "vector62", "processor62"],
    ),
    (
        ("memory62 stream62 context62 knowledge62 vector62 processor62", 28),
        ["memory62 stream62 context62", "knowledge62 vector62", "processor62"],
    ),
    (
        ("stream62 context62 knowledge62 vector62 processor62 reasoning62", 6),
        ["stream62", "context62", "knowledge62", "vector62", "processor62", "reasoning62"],
    ),
    (
        ("stream62 context62 knowledge62 vector62 processor62 reasoning62", 10),
        ["stream62", "context62", "knowledge62", "vector62", "processor62", "reasoning62"],
    ),
    (
        ("stream62 context62 knowledge62 vector62 processor62 reasoning62", 18),
        ["stream62 context62", "knowledge62", "vector62", "processor62", "reasoning62"],
    ),
    (
        ("stream62 context62 knowledge62 vector62 processor62 reasoning62", 28),
        ["stream62 context62", "knowledge62 vector62", "processor62 reasoning62"],
    ),
    (
        ("context62 knowledge62 vector62 processor62 reasoning62 machine62", 6),
        ["context62", "knowledge62", "vector62", "processor62", "reasoning62", "machine62"],
    ),
    (
        ("context62 knowledge62 vector62 processor62 reasoning62 machine62", 10),
        ["context62", "knowledge62", "vector62", "processor62", "reasoning62", "machine62"],
    ),
    (
        ("context62 knowledge62 vector62 processor62 reasoning62 machine62", 18),
        ["context62", "knowledge62", "vector62", "processor62", "reasoning62", "machine62"],
    ),
    (
        ("context62 knowledge62 vector62 processor62 reasoning62 machine62", 28),
        ["context62 knowledge62", "vector62 processor62", "reasoning62 machine62"],
    ),
    (
        ("knowledge62 vector62 processor62 reasoning62 machine62 learning62", 6),
        ["knowledge62", "vector62", "processor62", "reasoning62", "machine62", "learning62"],
    ),
    (
        ("knowledge62 vector62 processor62 reasoning62 machine62 learning62", 10),
        ["knowledge62", "vector62", "processor62", "reasoning62", "machine62", "learning62"],
    ),
    (
        ("knowledge62 vector62 processor62 reasoning62 machine62 learning62", 18),
        ["knowledge62", "vector62", "processor62", "reasoning62", "machine62", "learning62"],
    ),
    (
        ("knowledge62 vector62 processor62 reasoning62 machine62 learning62", 28),
        ["knowledge62 vector62", "processor62 reasoning62", "machine62 learning62"],
    ),
    (
        ("vector62 processor62 reasoning62 machine62 learning62 model62", 6),
        ["vector62", "processor62", "reasoning62", "machine62", "learning62", "model62"],
    ),
    (
        ("vector62 processor62 reasoning62 machine62 learning62 model62", 10),
        ["vector62", "processor62", "reasoning62", "machine62", "learning62", "model62"],
    ),
    (
        ("vector62 processor62 reasoning62 machine62 learning62 model62", 18),
        ["vector62", "processor62", "reasoning62", "machine62", "learning62 model62"],
    ),
    (
        ("vector62 processor62 reasoning62 machine62 learning62 model62", 28),
        ["vector62 processor62", "reasoning62 machine62", "learning62 model62"],
    ),
    (
        ("processor62 reasoning62 machine62 learning62 model62 token62", 6),
        ["processor62", "reasoning62", "machine62", "learning62", "model62", "token62"],
    ),
    (
        ("processor62 reasoning62 machine62 learning62 model62 token62", 10),
        ["processor62", "reasoning62", "machine62", "learning62", "model62", "token62"],
    ),
    (
        ("processor62 reasoning62 machine62 learning62 model62 token62", 18),
        ["processor62", "reasoning62", "machine62", "learning62 model62", "token62"],
    ),
    (
        ("processor62 reasoning62 machine62 learning62 model62 token62", 28),
        ["processor62 reasoning62", "machine62 learning62 model62", "token62"],
    ),
    (
        ("reasoning62 machine62 learning62 model62 token62 prompt62", 6),
        ["reasoning62", "machine62", "learning62", "model62", "token62", "prompt62"],
    ),
    (
        ("reasoning62 machine62 learning62 model62 token62 prompt62", 10),
        ["reasoning62", "machine62", "learning62", "model62", "token62", "prompt62"],
    ),
    (
        ("reasoning62 machine62 learning62 model62 token62 prompt62", 18),
        ["reasoning62", "machine62", "learning62 model62", "token62 prompt62"],
    ),
    (
        ("reasoning62 machine62 learning62 model62 token62 prompt62", 28),
        ["reasoning62 machine62", "learning62 model62 token62", "prompt62"],
    ),
    (
        ("machine62 learning62 model62 token62 prompt62 session62", 6),
        ["machine62", "learning62", "model62", "token62", "prompt62", "session62"],
    ),
    (
        ("machine62 learning62 model62 token62 prompt62 session62", 10),
        ["machine62", "learning62", "model62", "token62", "prompt62", "session62"],
    ),
    (
        ("machine62 learning62 model62 token62 prompt62 session62", 18),
        ["machine62", "learning62 model62", "token62 prompt62", "session62"],
    ),
    (
        ("machine62 learning62 model62 token62 prompt62 session62", 28),
        ["machine62 learning62 model62", "token62 prompt62 session62"],
    ),
    (
        ("learning62 model62 token62 prompt62 session62 library62", 6),
        ["learning62", "model62", "token62", "prompt62", "session62", "library62"],
    ),
    (
        ("learning62 model62 token62 prompt62 session62 library62", 10),
        ["learning62", "model62", "token62", "prompt62", "session62", "library62"],
    ),
    (
        ("learning62 model62 token62 prompt62 session62 library62", 18),
        ["learning62 model62", "token62 prompt62", "session62", "library62"],
    ),
    (
        ("learning62 model62 token62 prompt62 session62 library62", 28),
        ["learning62 model62 token62", "prompt62 session62 library62"],
    ),
    (
        ("model62 token62 prompt62 session62 library62 service62", 6),
        ["model62", "token62", "prompt62", "session62", "library62", "service62"],
    ),
    (
        ("model62 token62 prompt62 session62 library62 service62", 10),
        ["model62", "token62", "prompt62", "session62", "library62", "service62"],
    ),
    (
        ("model62 token62 prompt62 session62 library62 service62", 18),
        ["model62 token62", "prompt62 session62", "library62", "service62"],
    ),
    (
        ("model62 token62 prompt62 session62 library62 service62", 28),
        ["model62 token62 prompt62", "session62 library62", "service62"],
    ),
    (
        ("token62 prompt62 session62 library62 service62 gateway62", 6),
        ["token62", "prompt62", "session62", "library62", "service62", "gateway62"],
    ),
    (
        ("token62 prompt62 session62 library62 service62 gateway62", 10),
        ["token62", "prompt62", "session62", "library62", "service62", "gateway62"],
    ),
    (
        ("token62 prompt62 session62 library62 service62 gateway62", 18),
        ["token62 prompt62", "session62", "library62", "service62", "gateway62"],
    ),
    (
        ("token62 prompt62 session62 library62 service62 gateway62", 28),
        ["token62 prompt62 session62", "library62 service62", "gateway62"],
    ),
    (
        ("prompt62 session62 library62 service62 gateway62 storage62", 6),
        ["prompt62", "session62", "library62", "service62", "gateway62", "storage62"],
    ),
    (
        ("prompt62 session62 library62 service62 gateway62 storage62", 10),
        ["prompt62", "session62", "library62", "service62", "gateway62", "storage62"],
    ),
    (
        ("prompt62 session62 library62 service62 gateway62 storage62", 18),
        ["prompt62 session62", "library62", "service62", "gateway62", "storage62"],
    ),
    (
        ("prompt62 session62 library62 service62 gateway62 storage62", 28),
        ["prompt62 session62 library62", "service62 gateway62", "storage62"],
    ),
    (
        ("session62 library62 service62 gateway62 storage62 network62", 6),
        ["session62", "library62", "service62", "gateway62", "storage62", "network62"],
    ),
    (
        ("session62 library62 service62 gateway62 storage62 network62", 10),
        ["session62", "library62", "service62", "gateway62", "storage62", "network62"],
    ),
    (
        ("session62 library62 service62 gateway62 storage62 network62", 18),
        ["session62", "library62", "service62", "gateway62", "storage62", "network62"],
    ),
    (
        ("session62 library62 service62 gateway62 storage62 network62", 28),
        ["session62 library62", "service62 gateway62", "storage62 network62"],
    ),
    (
        ("library62 service62 gateway62 storage62 network62 latency62", 6),
        ["library62", "service62", "gateway62", "storage62", "network62", "latency62"],
    ),
    (
        ("library62 service62 gateway62 storage62 network62 latency62", 10),
        ["library62", "service62", "gateway62", "storage62", "network62", "latency62"],
    ),
    (
        ("library62 service62 gateway62 storage62 network62 latency62", 18),
        ["library62", "service62", "gateway62", "storage62", "network62", "latency62"],
    ),
    (
        ("library62 service62 gateway62 storage62 network62 latency62", 28),
        ["library62 service62", "gateway62 storage62", "network62 latency62"],
    ),
    (
        ("service62 gateway62 storage62 network62 latency62 buffer62", 6),
        ["service62", "gateway62", "storage62", "network62", "latency62", "buffer62"],
    ),
    (
        ("service62 gateway62 storage62 network62 latency62 buffer62", 10),
        ["service62", "gateway62", "storage62", "network62", "latency62", "buffer62"],
    ),
    (
        ("service62 gateway62 storage62 network62 latency62 buffer62", 18),
        ["service62", "gateway62", "storage62", "network62", "latency62 buffer62"],
    ),
    (
        ("service62 gateway62 storage62 network62 latency62 buffer62", 28),
        ["service62 gateway62", "storage62 network62", "latency62 buffer62"],
    ),
    (
        ("gateway62 storage62 network62 latency62 buffer62 queue62", 6),
        ["gateway62", "storage62", "network62", "latency62", "buffer62", "queue62"],
    ),
    (
        ("gateway62 storage62 network62 latency62 buffer62 queue62", 10),
        ["gateway62", "storage62", "network62", "latency62", "buffer62", "queue62"],
    ),
    (
        ("gateway62 storage62 network62 latency62 buffer62 queue62", 18),
        ["gateway62", "storage62", "network62", "latency62 buffer62", "queue62"],
    ),
    (
        ("gateway62 storage62 network62 latency62 buffer62 queue62", 28),
        ["gateway62 storage62", "network62 latency62 buffer62", "queue62"],
    ),
    (
        ("storage62 network62 latency62 buffer62 queue62 worker62", 6),
        ["storage62", "network62", "latency62", "buffer62", "queue62", "worker62"],
    ),
    (
        ("storage62 network62 latency62 buffer62 queue62 worker62", 10),
        ["storage62", "network62", "latency62", "buffer62", "queue62", "worker62"],
    ),
    (
        ("storage62 network62 latency62 buffer62 queue62 worker62", 18),
        ["storage62", "network62", "latency62 buffer62", "queue62 worker62"],
    ),
    (
        ("storage62 network62 latency62 buffer62 queue62 worker62", 28),
        ["storage62 network62", "latency62 buffer62 queue62", "worker62"],
    ),
    (
        ("network62 latency62 buffer62 queue62 worker62 kernel62", 6),
        ["network62", "latency62", "buffer62", "queue62", "worker62", "kernel62"],
    ),
    (
        ("network62 latency62 buffer62 queue62 worker62 kernel62", 10),
        ["network62", "latency62", "buffer62", "queue62", "worker62", "kernel62"],
    ),
    (
        ("network62 latency62 buffer62 queue62 worker62 kernel62", 18),
        ["network62", "latency62 buffer62", "queue62 worker62", "kernel62"],
    ),
    (
        ("network62 latency62 buffer62 queue62 worker62 kernel62", 28),
        ["network62 latency62 buffer62", "queue62 worker62 kernel62"],
    ),
    (
        ("latency62 buffer62 queue62 worker62 kernel62 signal62", 6),
        ["latency62", "buffer62", "queue62", "worker62", "kernel62", "signal62"],
    ),
    (
        ("latency62 buffer62 queue62 worker62 kernel62 signal62", 10),
        ["latency62", "buffer62", "queue62", "worker62", "kernel62", "signal62"],
    ),
    (
        ("latency62 buffer62 queue62 worker62 kernel62 signal62", 18),
        ["latency62 buffer62", "queue62 worker62", "kernel62 signal62"],
    ),
    (
        ("latency62 buffer62 queue62 worker62 kernel62 signal62", 28),
        ["latency62 buffer62 queue62", "worker62 kernel62 signal62"],
    ),
    (
        ("buffer62 queue62 worker62 kernel62 signal62 packet62", 6),
        ["buffer62", "queue62", "worker62", "kernel62", "signal62", "packet62"],
    ),
    (
        ("buffer62 queue62 worker62 kernel62 signal62 packet62", 10),
        ["buffer62", "queue62", "worker62", "kernel62", "signal62", "packet62"],
    ),
    (
        ("buffer62 queue62 worker62 kernel62 signal62 packet62", 18),
        ["buffer62 queue62", "worker62 kernel62", "signal62 packet62"],
    ),
    (
        ("buffer62 queue62 worker62 kernel62 signal62 packet62", 28),
        ["buffer62 queue62 worker62", "kernel62 signal62 packet62"],
    ),
    (
        ("queue62 worker62 kernel62 signal62 packet62 router62", 6),
        ["queue62", "worker62", "kernel62", "signal62", "packet62", "router62"],
    ),
    (
        ("queue62 worker62 kernel62 signal62 packet62 router62", 10),
        ["queue62", "worker62", "kernel62", "signal62", "packet62", "router62"],
    ),
    (
        ("queue62 worker62 kernel62 signal62 packet62 router62", 18),
        ["queue62 worker62", "kernel62 signal62", "packet62 router62"],
    ),
    (
        ("queue62 worker62 kernel62 signal62 packet62 router62", 28),
        ["queue62 worker62 kernel62", "signal62 packet62 router62"],
    ),
    (
        ("worker62 kernel62 signal62 packet62 router62 cluster62", 6),
        ["worker62", "kernel62", "signal62", "packet62", "router62", "cluster62"],
    ),
    (
        ("worker62 kernel62 signal62 packet62 router62 cluster62", 10),
        ["worker62", "kernel62", "signal62", "packet62", "router62", "cluster62"],
    ),
    (
        ("worker62 kernel62 signal62 packet62 router62 cluster62", 18),
        ["worker62 kernel62", "signal62 packet62", "router62 cluster62"],
    ),
    (
        ("worker62 kernel62 signal62 packet62 router62 cluster62", 28),
        ["worker62 kernel62 signal62", "packet62 router62 cluster62"],
    ),
    (
        ("kernel62 signal62 packet62 router62 cluster62 mirror62", 6),
        ["kernel62", "signal62", "packet62", "router62", "cluster62", "mirror62"],
    ),
    (
        ("kernel62 signal62 packet62 router62 cluster62 mirror62", 10),
        ["kernel62", "signal62", "packet62", "router62", "cluster62", "mirror62"],
    ),
    (
        ("kernel62 signal62 packet62 router62 cluster62 mirror62", 18),
        ["kernel62 signal62", "packet62 router62", "cluster62 mirror62"],
    ),
    (
        ("kernel62 signal62 packet62 router62 cluster62 mirror62", 28),
        ["kernel62 signal62 packet62", "router62 cluster62 mirror62"],
    ),
    (
        ("signal62 packet62 router62 cluster62 mirror62 filter62", 6),
        ["signal62", "packet62", "router62", "cluster62", "mirror62", "filter62"],
    ),
    (
        ("signal62 packet62 router62 cluster62 mirror62 filter62", 10),
        ["signal62", "packet62", "router62", "cluster62", "mirror62", "filter62"],
    ),
    (
        ("signal62 packet62 router62 cluster62 mirror62 filter62", 18),
        ["signal62 packet62", "router62 cluster62", "mirror62 filter62"],
    ),
    (
        ("signal62 packet62 router62 cluster62 mirror62 filter62", 28),
        ["signal62 packet62 router62", "cluster62 mirror62 filter62"],
    ),
    (
        ("packet62 router62 cluster62 mirror62 filter62 ranking62", 6),
        ["packet62", "router62", "cluster62", "mirror62", "filter62", "ranking62"],
    ),
    (
        ("packet62 router62 cluster62 mirror62 filter62 ranking62", 10),
        ["packet62", "router62", "cluster62", "mirror62", "filter62", "ranking62"],
    ),
    (
        ("packet62 router62 cluster62 mirror62 filter62 ranking62", 18),
        ["packet62 router62", "cluster62 mirror62", "filter62 ranking62"],
    ),
    (
        ("packet62 router62 cluster62 mirror62 filter62 ranking62", 28),
        ["packet62 router62 cluster62", "mirror62 filter62 ranking62"],
    ),
    (
        ("router62 cluster62 mirror62 filter62 ranking62 encoding62", 6),
        ["router62", "cluster62", "mirror62", "filter62", "ranking62", "encoding62"],
    ),
    (
        ("router62 cluster62 mirror62 filter62 ranking62 encoding62", 10),
        ["router62", "cluster62", "mirror62", "filter62", "ranking62", "encoding62"],
    ),
    (
        ("router62 cluster62 mirror62 filter62 ranking62 encoding62", 18),
        ["router62 cluster62", "mirror62 filter62", "ranking62", "encoding62"],
    ),
    (
        ("router62 cluster62 mirror62 filter62 ranking62 encoding62", 28),
        ["router62 cluster62 mirror62", "filter62 ranking62", "encoding62"],
    ),
    (
        ("cluster62 mirror62 filter62 ranking62 encoding62 mapping62", 6),
        ["cluster62", "mirror62", "filter62", "ranking62", "encoding62", "mapping62"],
    ),
    (
        ("cluster62 mirror62 filter62 ranking62 encoding62 mapping62", 10),
        ["cluster62", "mirror62", "filter62", "ranking62", "encoding62", "mapping62"],
    ),
    (
        ("cluster62 mirror62 filter62 ranking62 encoding62 mapping62", 18),
        ["cluster62 mirror62", "filter62 ranking62", "encoding62", "mapping62"],
    ),
    (
        ("cluster62 mirror62 filter62 ranking62 encoding62 mapping62", 28),
        ["cluster62 mirror62 filter62", "ranking62 encoding62", "mapping62"],
    ),
    (
        ("mirror62 filter62 ranking62 encoding62 mapping62 record62", 6),
        ["mirror62", "filter62", "ranking62", "encoding62", "mapping62", "record62"],
    ),
    (
        ("mirror62 filter62 ranking62 encoding62 mapping62 record62", 10),
        ["mirror62", "filter62", "ranking62", "encoding62", "mapping62", "record62"],
    ),
    (
        ("mirror62 filter62 ranking62 encoding62 mapping62 record62", 18),
        ["mirror62 filter62", "ranking62", "encoding62", "mapping62 record62"],
    ),
    (
        ("mirror62 filter62 ranking62 encoding62 mapping62 record62", 28),
        ["mirror62 filter62 ranking62", "encoding62 mapping62", "record62"],
    ),
    (
        ("filter62 ranking62 encoding62 mapping62 record62 candle62", 6),
        ["filter62", "ranking62", "encoding62", "mapping62", "record62", "candle62"],
    ),
    (
        ("filter62 ranking62 encoding62 mapping62 record62 candle62", 10),
        ["filter62", "ranking62", "encoding62", "mapping62", "record62", "candle62"],
    ),
    (
        ("filter62 ranking62 encoding62 mapping62 record62 candle62", 18),
        ["filter62 ranking62", "encoding62", "mapping62 record62", "candle62"],
    ),
    (
        ("filter62 ranking62 encoding62 mapping62 record62 candle62", 28),
        ["filter62 ranking62", "encoding62 mapping62", "record62 candle62"],
    ),
    (
        ("ranking62 encoding62 mapping62 record62 candle62 thread62", 6),
        ["ranking62", "encoding62", "mapping62", "record62", "candle62", "thread62"],
    ),
    (
        ("ranking62 encoding62 mapping62 record62 candle62 thread62", 10),
        ["ranking62", "encoding62", "mapping62", "record62", "candle62", "thread62"],
    ),
    (
        ("ranking62 encoding62 mapping62 record62 candle62 thread62", 18),
        ["ranking62", "encoding62", "mapping62 record62", "candle62 thread62"],
    ),
    (
        ("ranking62 encoding62 mapping62 record62 candle62 thread62", 28),
        ["ranking62 encoding62", "mapping62 record62 candle62", "thread62"],
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
