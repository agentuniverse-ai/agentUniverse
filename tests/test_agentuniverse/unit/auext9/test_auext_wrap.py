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
        ("round 9: the quick brown fox jumps over the lazy dog", 4),
        ["round", "9:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 9: the quick brown fox jumps over the lazy dog", 8),
        ["round 9:", "the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 9: the quick brown fox jumps over the lazy dog", 12),
        ["round 9: the", "quick brown", "fox jumps", "over the", "lazy dog"],
    ),
    (
        ("round 9: the quick brown fox jumps over the lazy dog", 16),
        ["round 9: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 9: the quick brown fox jumps over the lazy dog", 24),
        ["round 9: the quick brown", "fox jumps over the lazy", "dog"],
    ),
    (
        ("round 9: the quick brown fox jumps over the lazy dog", 32),
        ["round 9: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 9: agentuniverse is a framework for multi agents", 4),
        ["round", "9:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 9: agentuniverse is a framework for multi agents", 8),
        ["round 9:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 9: agentuniverse is a framework for multi agents", 12),
        ["round 9:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 9: agentuniverse is a framework for multi agents", 16),
        ["round 9:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 9: agentuniverse is a framework for multi agents", 24),
        ["round 9: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 9: agentuniverse is a framework for multi agents", 32),
        ["round 9: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 9: knowledge stored as vectors enables retrieval", 4),
        ["round", "9:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 9: knowledge stored as vectors enables retrieval", 8),
        ["round 9:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 9: knowledge stored as vectors enables retrieval", 12),
        ["round 9:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 9: knowledge stored as vectors enables retrieval", 16),
        ["round 9:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 9: knowledge stored as vectors enables retrieval", 24),
        ["round 9: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 9: knowledge stored as vectors enables retrieval", 32),
        ["round 9: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 9: the processor reads the record then stops", 4),
        ["round", "9:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 9: the processor reads the record then stops", 8),
        ["round 9:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 9: the processor reads the record then stops", 12),
        ["round 9: the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 9: the processor reads the record then stops", 16),
        ["round 9: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 9: the processor reads the record then stops", 24),
        ["round 9: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 9: the processor reads the record then stops", 32),
        ["round 9: the processor reads the", "record then stops"],
    ),
    (
        ("round 9: a worker pulls the next task from the queue", 4),
        ["round", "9: a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 9: a worker pulls the next task from the queue", 8),
        ["round 9:", "a worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 9: a worker pulls the next task from the queue", 12),
        ["round 9: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 9: a worker pulls the next task from the queue", 16),
        ["round 9: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 9: a worker pulls the next task from the queue", 24),
        ["round 9: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 9: a worker pulls the next task from the queue", 32),
        ["round 9: a worker pulls the next", "task from the queue"],
    ),
    (
        ("round 9: signals travel through the network layer", 4),
        ["round", "9:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 9: signals travel through the network layer", 8),
        ["round 9:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 9: signals travel through the network layer", 12),
        ["round 9:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 9: signals travel through the network layer", 16),
        ["round 9: signals", "travel through", "the network", "layer"],
    ),
    (
        ("round 9: signals travel through the network layer", 24),
        ["round 9: signals travel", "through the network", "layer"],
    ),
    (
        ("round 9: signals travel through the network layer", 32),
        ["round 9: signals travel through", "the network layer"],
    ),
    (
        ("round 9: the gateway routes each request by policy", 4),
        ["round", "9:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 9: the gateway routes each request by policy", 8),
        ["round 9:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 9: the gateway routes each request by policy", 12),
        ["round 9: the", "gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 9: the gateway routes each request by policy", 16),
        ["round 9: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 9: the gateway routes each request by policy", 24),
        ["round 9: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 9: the gateway routes each request by policy", 32),
        ["round 9: the gateway routes each", "request by policy"],
    ),
    (
        ("round 9: memory grows until the buffer is full", 4),
        ["round", "9:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 9: memory grows until the buffer is full", 8),
        ["round 9:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 9: memory grows until the buffer is full", 12),
        ["round 9:", "memory grows", "until the", "buffer is", "full"],
    ),
    (("round 9: memory grows until the buffer is full", 16), ["round 9: memory", "grows until the", "buffer is full"]),
    (("round 9: memory grows until the buffer is full", 24), ["round 9: memory grows", "until the buffer is full"]),
    (("round 9: memory grows until the buffer is full", 32), ["round 9: memory grows until the", "buffer is full"]),
    (
        ("round 9: the cluster mirrors every packet twice", 4),
        ["round", "9:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 9: the cluster mirrors every packet twice", 8),
        ["round 9:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 9: the cluster mirrors every packet twice", 12),
        ["round 9: the", "cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 9: the cluster mirrors every packet twice", 16),
        ["round 9: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 9: the cluster mirrors every packet twice", 24),
        ["round 9: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 9: the cluster mirrors every packet twice", 32), ["round 9: the cluster mirrors", "every packet twice"]),
    (
        ("round 9: ranking uses tokens learned from the corpus", 4),
        ["round", "9:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 9: ranking uses tokens learned from the corpus", 8),
        ["round 9:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 9: ranking uses tokens learned from the corpus", 12),
        ["round 9:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 9: ranking uses tokens learned from the corpus", 16),
        ["round 9: ranking", "uses tokens", "learned from the", "corpus"],
    ),
    (
        ("round 9: ranking uses tokens learned from the corpus", 24),
        ["round 9: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 9: ranking uses tokens learned from the corpus", 32),
        ["round 9: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 9: a long session ends when the candle dies", 4),
        ["round", "9: a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 9: a long session ends when the candle dies", 8),
        ["round 9:", "a long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 9: a long session ends when the candle dies", 12),
        ["round 9: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 9: a long session ends when the candle dies", 16),
        ["round 9: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 9: a long session ends when the candle dies", 24),
        ["round 9: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 9: a long session ends when the candle dies", 32),
        ["round 9: a long session ends", "when the candle dies"],
    ),
    (
        ("round 9: encode the prompt then map the result", 4),
        ["round", "9:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 9: encode the prompt then map the result", 8),
        ["round 9:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 9: encode the prompt then map the result", 12),
        ["round 9:", "encode the", "prompt then", "map the", "result"],
    ),
    (("round 9: encode the prompt then map the result", 16), ["round 9: encode", "the prompt then", "map the result"]),
    (("round 9: encode the prompt then map the result", 24), ["round 9: encode the", "prompt then map the", "result"]),
    (("round 9: encode the prompt then map the result", 32), ["round 9: encode the prompt then", "map the result"]),
    (
        ("round 9: the kernel wakes the worker at dawn", 4),
        ["round", "9:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 9: the kernel wakes the worker at dawn", 8),
        ["round 9:", "the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (("round 9: the kernel wakes the worker at dawn", 12), ["round 9: the", "kernel wakes", "the worker", "at dawn"]),
    (("round 9: the kernel wakes the worker at dawn", 16), ["round 9: the", "kernel wakes the", "worker at dawn"]),
    (("round 9: the kernel wakes the worker at dawn", 24), ["round 9: the kernel", "wakes the worker at dawn"]),
    (("round 9: the kernel wakes the worker at dawn", 32), ["round 9: the kernel wakes the", "worker at dawn"]),
    (
        ("round 9: service latency drops after the patch", 4),
        ["round", "9:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 9: service latency drops after the patch", 8),
        ["round 9:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 9: service latency drops after the patch", 12),
        ["round 9:", "service", "latency", "drops after", "the patch"],
    ),
    (("round 9: service latency drops after the patch", 16), ["round 9: service", "latency drops", "after the patch"]),
    (("round 9: service latency drops after the patch", 24), ["round 9: service latency", "drops after the patch"]),
    (("round 9: service latency drops after the patch", 32), ["round 9: service latency drops", "after the patch"]),
    (
        ("round 9: the library caches every vector it sees", 4),
        ["round", "9:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 9: the library caches every vector it sees", 8),
        ["round 9:", "the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 9: the library caches every vector it sees", 12),
        ["round 9: the", "library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 9: the library caches every vector it sees", 16),
        ["round 9: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 9: the library caches every vector it sees", 24),
        ["round 9: the library", "caches every vector it", "sees"],
    ),
    (("round 9: the library caches every vector it sees", 32), ["round 9: the library caches", "every vector it sees"]),
    (
        ("round 9: agents argue then the debate resolves", 4),
        ["round", "9:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 9: agents argue then the debate resolves", 8),
        ["round 9:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 9: agents argue then the debate resolves", 12),
        ["round 9:", "agents argue", "then the", "debate", "resolves"],
    ),
    (("round 9: agents argue then the debate resolves", 16), ["round 9: agents", "argue then the", "debate resolves"]),
    (("round 9: agents argue then the debate resolves", 24), ["round 9: agents argue", "then the debate resolves"]),
    (("round 9: agents argue then the debate resolves", 32), ["round 9: agents argue then the", "debate resolves"]),
    (
        ("round 9: the filter keeps only strong matches", 4),
        ["round", "9:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 9: the filter keeps only strong matches", 8),
        ["round 9:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (("round 9: the filter keeps only strong matches", 12), ["round 9: the", "filter keeps", "only strong", "matches"]),
    (("round 9: the filter keeps only strong matches", 16), ["round 9: the", "filter keeps", "only strong", "matches"]),
    (("round 9: the filter keeps only strong matches", 24), ["round 9: the filter", "keeps only strong", "matches"]),
    (("round 9: the filter keeps only strong matches", 32), ["round 9: the filter keeps only", "strong matches"]),
    (
        ("round 9: the model answers with a short reply", 4),
        ["round", "9:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 9: the model answers with a short reply", 8),
        ["round 9:", "the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 9: the model answers with a short reply", 12),
        ["round 9: the", "model", "answers with", "a short", "reply"],
    ),
    (("round 9: the model answers with a short reply", 16), ["round 9: the", "model answers", "with a short", "reply"]),
    (("round 9: the model answers with a short reply", 24), ["round 9: the model", "answers with a short", "reply"]),
    (("round 9: the model answers with a short reply", 32), ["round 9: the model answers with", "a short reply"]),
    (
        ("round 9: the recorder stores the reasoning trace", 4),
        ["round", "9:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 9: the recorder stores the reasoning trace", 8),
        ["round 9:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 9: the recorder stores the reasoning trace", 12),
        ["round 9: the", "recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 9: the recorder stores the reasoning trace", 16),
        ["round 9: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 9: the recorder stores the reasoning trace", 24),
        ["round 9: the recorder", "stores the reasoning", "trace"],
    ),
    (("round 9: the recorder stores the reasoning trace", 32), ["round 9: the recorder stores the", "reasoning trace"]),
    (
        ("round 9: the angel watches the processor run", 4),
        ["round", "9:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 9: the angel watches the processor run", 8),
        ["round 9:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 9: the angel watches the processor run", 12),
        ["round 9: the", "angel", "watches the", "processor", "run"],
    ),
    (("round 9: the angel watches the processor run", 16), ["round 9: the", "angel watches", "the processor", "run"]),
    (("round 9: the angel watches the processor run", 24), ["round 9: the angel", "watches the processor", "run"]),
    (("round 9: the angel watches the processor run", 32), ["round 9: the angel watches the", "processor run"]),
    (
        ("round 9: angle of the vector decides the match", 4),
        ["round", "9:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 9: angle of the vector decides the match", 8),
        ["round 9:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 9: angle of the vector decides the match", 12),
        ["round 9:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 9: angle of the vector decides the match", 16),
        ["round 9: angle", "of the vector", "decides the", "match"],
    ),
    (("round 9: angle of the vector decides the match", 24), ["round 9: angle of the", "vector decides the match"]),
    (("round 9: angle of the vector decides the match", 32), ["round 9: angle of the vector", "decides the match"]),
    (
        ("round 9: the candle burns twice as long at night", 4),
        ["round", "9:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 9: the candle burns twice as long at night", 8),
        ["round 9:", "the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 9: the candle burns twice as long at night", 12),
        ["round 9: the", "candle burns", "twice as", "long at", "night"],
    ),
    (
        ("round 9: the candle burns twice as long at night", 16),
        ["round 9: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 9: the candle burns twice as long at night", 24),
        ["round 9: the candle", "burns twice as long at", "night"],
    ),
    (("round 9: the candle burns twice as long at night", 32), ["round 9: the candle burns twice", "as long at night"]),
    (
        ("round 9: a mirror of the universe in one line", 4),
        ["round", "9: a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 9: a mirror of the universe in one line", 8),
        ["round 9:", "a mirror", "of the", "universe", "in one", "line"],
    ),
    (("round 9: a mirror of the universe in one line", 12), ["round 9: a", "mirror of", "the universe", "in one line"]),
    (("round 9: a mirror of the universe in one line", 16), ["round 9: a", "mirror of the", "universe in one", "line"]),
    (("round 9: a mirror of the universe in one line", 24), ["round 9: a mirror of the", "universe in one line"]),
    (("round 9: a mirror of the universe in one line", 32), ["round 9: a mirror of the", "universe in one line"]),
    (
        ("round 9: the queue drains before the storm", 4),
        ["round", "9:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 9: the queue drains before the storm", 8),
        ["round 9:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 9: the queue drains before the storm", 12), ["round 9: the", "queue drains", "before the", "storm"]),
    (("round 9: the queue drains before the storm", 16), ["round 9: the", "queue drains", "before the storm"]),
    (("round 9: the queue drains before the storm", 24), ["round 9: the queue", "drains before the storm"]),
    (("round 9: the queue drains before the storm", 32), ["round 9: the queue drains before", "the storm"]),
    (
        ("kitten9 sitting9 agent9 angle9 universe9 memory9", 6),
        ["kitten9", "sitting9", "agent9", "angle9", "universe9", "memory9"],
    ),
    (
        ("kitten9 sitting9 agent9 angle9 universe9 memory9", 10),
        ["kitten9", "sitting9", "agent9", "angle9", "universe9", "memory9"],
    ),
    (
        ("kitten9 sitting9 agent9 angle9 universe9 memory9", 18),
        ["kitten9 sitting9", "agent9 angle9", "universe9 memory9"],
    ),
    (("kitten9 sitting9 agent9 angle9 universe9 memory9", 28), ["kitten9 sitting9 agent9", "angle9 universe9 memory9"]),
    (
        ("sitting9 agent9 angle9 universe9 memory9 stream9", 6),
        ["sitting9", "agent9", "angle9", "universe9", "memory9", "stream9"],
    ),
    (
        ("sitting9 agent9 angle9 universe9 memory9 stream9", 10),
        ["sitting9", "agent9", "angle9", "universe9", "memory9", "stream9"],
    ),
    (
        ("sitting9 agent9 angle9 universe9 memory9 stream9", 18),
        ["sitting9 agent9", "angle9 universe9", "memory9 stream9"],
    ),
    (("sitting9 agent9 angle9 universe9 memory9 stream9", 28), ["sitting9 agent9 angle9", "universe9 memory9 stream9"]),
    (
        ("agent9 angle9 universe9 memory9 stream9 context9", 6),
        ["agent9", "angle9", "universe9", "memory9", "stream9", "context9"],
    ),
    (
        ("agent9 angle9 universe9 memory9 stream9 context9", 10),
        ["agent9", "angle9", "universe9", "memory9", "stream9", "context9"],
    ),
    (
        ("agent9 angle9 universe9 memory9 stream9 context9", 18),
        ["agent9 angle9", "universe9 memory9", "stream9 context9"],
    ),
    (("agent9 angle9 universe9 memory9 stream9 context9", 28), ["agent9 angle9 universe9", "memory9 stream9 context9"]),
    (
        ("angle9 universe9 memory9 stream9 context9 knowledge9", 6),
        ["angle9", "universe9", "memory9", "stream9", "context9", "knowledge9"],
    ),
    (
        ("angle9 universe9 memory9 stream9 context9 knowledge9", 10),
        ["angle9", "universe9", "memory9", "stream9", "context9", "knowledge9"],
    ),
    (
        ("angle9 universe9 memory9 stream9 context9 knowledge9", 18),
        ["angle9 universe9", "memory9 stream9", "context9", "knowledge9"],
    ),
    (
        ("angle9 universe9 memory9 stream9 context9 knowledge9", 28),
        ["angle9 universe9 memory9", "stream9 context9 knowledge9"],
    ),
    (
        ("universe9 memory9 stream9 context9 knowledge9 vector9", 6),
        ["universe9", "memory9", "stream9", "context9", "knowledge9", "vector9"],
    ),
    (
        ("universe9 memory9 stream9 context9 knowledge9 vector9", 10),
        ["universe9", "memory9", "stream9", "context9", "knowledge9", "vector9"],
    ),
    (
        ("universe9 memory9 stream9 context9 knowledge9 vector9", 18),
        ["universe9 memory9", "stream9 context9", "knowledge9 vector9"],
    ),
    (
        ("universe9 memory9 stream9 context9 knowledge9 vector9", 28),
        ["universe9 memory9 stream9", "context9 knowledge9 vector9"],
    ),
    (
        ("memory9 stream9 context9 knowledge9 vector9 processor9", 6),
        ["memory9", "stream9", "context9", "knowledge9", "vector9", "processor9"],
    ),
    (
        ("memory9 stream9 context9 knowledge9 vector9 processor9", 10),
        ["memory9", "stream9", "context9", "knowledge9", "vector9", "processor9"],
    ),
    (
        ("memory9 stream9 context9 knowledge9 vector9 processor9", 18),
        ["memory9 stream9", "context9", "knowledge9 vector9", "processor9"],
    ),
    (
        ("memory9 stream9 context9 knowledge9 vector9 processor9", 28),
        ["memory9 stream9 context9", "knowledge9 vector9", "processor9"],
    ),
    (
        ("stream9 context9 knowledge9 vector9 processor9 reasoning9", 6),
        ["stream9", "context9", "knowledge9", "vector9", "processor9", "reasoning9"],
    ),
    (
        ("stream9 context9 knowledge9 vector9 processor9 reasoning9", 10),
        ["stream9", "context9", "knowledge9", "vector9", "processor9", "reasoning9"],
    ),
    (
        ("stream9 context9 knowledge9 vector9 processor9 reasoning9", 18),
        ["stream9 context9", "knowledge9 vector9", "processor9", "reasoning9"],
    ),
    (
        ("stream9 context9 knowledge9 vector9 processor9 reasoning9", 28),
        ["stream9 context9 knowledge9", "vector9 processor9", "reasoning9"],
    ),
    (
        ("context9 knowledge9 vector9 processor9 reasoning9 machine9", 6),
        ["context9", "knowledge9", "vector9", "processor9", "reasoning9", "machine9"],
    ),
    (
        ("context9 knowledge9 vector9 processor9 reasoning9 machine9", 10),
        ["context9", "knowledge9", "vector9", "processor9", "reasoning9", "machine9"],
    ),
    (
        ("context9 knowledge9 vector9 processor9 reasoning9 machine9", 18),
        ["context9", "knowledge9 vector9", "processor9", "reasoning9", "machine9"],
    ),
    (
        ("context9 knowledge9 vector9 processor9 reasoning9 machine9", 28),
        ["context9 knowledge9 vector9", "processor9 reasoning9", "machine9"],
    ),
    (
        ("knowledge9 vector9 processor9 reasoning9 machine9 learning9", 6),
        ["knowledge9", "vector9", "processor9", "reasoning9", "machine9", "learning9"],
    ),
    (
        ("knowledge9 vector9 processor9 reasoning9 machine9 learning9", 10),
        ["knowledge9", "vector9", "processor9", "reasoning9", "machine9", "learning9"],
    ),
    (
        ("knowledge9 vector9 processor9 reasoning9 machine9 learning9", 18),
        ["knowledge9 vector9", "processor9", "reasoning9", "machine9 learning9"],
    ),
    (
        ("knowledge9 vector9 processor9 reasoning9 machine9 learning9", 28),
        ["knowledge9 vector9", "processor9 reasoning9", "machine9 learning9"],
    ),
    (
        ("vector9 processor9 reasoning9 machine9 learning9 model9", 6),
        ["vector9", "processor9", "reasoning9", "machine9", "learning9", "model9"],
    ),
    (
        ("vector9 processor9 reasoning9 machine9 learning9 model9", 10),
        ["vector9", "processor9", "reasoning9", "machine9", "learning9", "model9"],
    ),
    (
        ("vector9 processor9 reasoning9 machine9 learning9 model9", 18),
        ["vector9 processor9", "reasoning9", "machine9 learning9", "model9"],
    ),
    (
        ("vector9 processor9 reasoning9 machine9 learning9 model9", 28),
        ["vector9 processor9", "reasoning9 machine9", "learning9 model9"],
    ),
    (
        ("processor9 reasoning9 machine9 learning9 model9 token9", 6),
        ["processor9", "reasoning9", "machine9", "learning9", "model9", "token9"],
    ),
    (
        ("processor9 reasoning9 machine9 learning9 model9 token9", 10),
        ["processor9", "reasoning9", "machine9", "learning9", "model9", "token9"],
    ),
    (
        ("processor9 reasoning9 machine9 learning9 model9 token9", 18),
        ["processor9", "reasoning9", "machine9 learning9", "model9 token9"],
    ),
    (
        ("processor9 reasoning9 machine9 learning9 model9 token9", 28),
        ["processor9 reasoning9", "machine9 learning9 model9", "token9"],
    ),
    (
        ("reasoning9 machine9 learning9 model9 token9 prompt9", 6),
        ["reasoning9", "machine9", "learning9", "model9", "token9", "prompt9"],
    ),
    (
        ("reasoning9 machine9 learning9 model9 token9 prompt9", 10),
        ["reasoning9", "machine9", "learning9", "model9", "token9", "prompt9"],
    ),
    (
        ("reasoning9 machine9 learning9 model9 token9 prompt9", 18),
        ["reasoning9", "machine9 learning9", "model9 token9", "prompt9"],
    ),
    (
        ("reasoning9 machine9 learning9 model9 token9 prompt9", 28),
        ["reasoning9 machine9", "learning9 model9 token9", "prompt9"],
    ),
    (
        ("machine9 learning9 model9 token9 prompt9 session9", 6),
        ["machine9", "learning9", "model9", "token9", "prompt9", "session9"],
    ),
    (
        ("machine9 learning9 model9 token9 prompt9 session9", 10),
        ["machine9", "learning9", "model9", "token9", "prompt9", "session9"],
    ),
    (
        ("machine9 learning9 model9 token9 prompt9 session9", 18),
        ["machine9 learning9", "model9 token9", "prompt9 session9"],
    ),
    (
        ("machine9 learning9 model9 token9 prompt9 session9", 28),
        ["machine9 learning9 model9", "token9 prompt9 session9"],
    ),
    (
        ("learning9 model9 token9 prompt9 session9 library9", 6),
        ["learning9", "model9", "token9", "prompt9", "session9", "library9"],
    ),
    (
        ("learning9 model9 token9 prompt9 session9 library9", 10),
        ["learning9", "model9", "token9", "prompt9", "session9", "library9"],
    ),
    (
        ("learning9 model9 token9 prompt9 session9 library9", 18),
        ["learning9 model9", "token9 prompt9", "session9 library9"],
    ),
    (
        ("learning9 model9 token9 prompt9 session9 library9", 28),
        ["learning9 model9 token9", "prompt9 session9 library9"],
    ),
    (
        ("model9 token9 prompt9 session9 library9 service9", 6),
        ["model9", "token9", "prompt9", "session9", "library9", "service9"],
    ),
    (
        ("model9 token9 prompt9 session9 library9 service9", 10),
        ["model9", "token9", "prompt9", "session9", "library9", "service9"],
    ),
    (
        ("model9 token9 prompt9 session9 library9 service9", 18),
        ["model9 token9", "prompt9 session9", "library9 service9"],
    ),
    (("model9 token9 prompt9 session9 library9 service9", 28), ["model9 token9 prompt9", "session9 library9 service9"]),
    (
        ("token9 prompt9 session9 library9 service9 gateway9", 6),
        ["token9", "prompt9", "session9", "library9", "service9", "gateway9"],
    ),
    (
        ("token9 prompt9 session9 library9 service9 gateway9", 10),
        ["token9", "prompt9", "session9", "library9", "service9", "gateway9"],
    ),
    (
        ("token9 prompt9 session9 library9 service9 gateway9", 18),
        ["token9 prompt9", "session9 library9", "service9 gateway9"],
    ),
    (
        ("token9 prompt9 session9 library9 service9 gateway9", 28),
        ["token9 prompt9 session9", "library9 service9 gateway9"],
    ),
    (
        ("prompt9 session9 library9 service9 gateway9 storage9", 6),
        ["prompt9", "session9", "library9", "service9", "gateway9", "storage9"],
    ),
    (
        ("prompt9 session9 library9 service9 gateway9 storage9", 10),
        ["prompt9", "session9", "library9", "service9", "gateway9", "storage9"],
    ),
    (
        ("prompt9 session9 library9 service9 gateway9 storage9", 18),
        ["prompt9 session9", "library9 service9", "gateway9 storage9"],
    ),
    (
        ("prompt9 session9 library9 service9 gateway9 storage9", 28),
        ["prompt9 session9 library9", "service9 gateway9 storage9"],
    ),
    (
        ("session9 library9 service9 gateway9 storage9 network9", 6),
        ["session9", "library9", "service9", "gateway9", "storage9", "network9"],
    ),
    (
        ("session9 library9 service9 gateway9 storage9 network9", 10),
        ["session9", "library9", "service9", "gateway9", "storage9", "network9"],
    ),
    (
        ("session9 library9 service9 gateway9 storage9 network9", 18),
        ["session9 library9", "service9 gateway9", "storage9 network9"],
    ),
    (
        ("session9 library9 service9 gateway9 storage9 network9", 28),
        ["session9 library9 service9", "gateway9 storage9 network9"],
    ),
    (
        ("library9 service9 gateway9 storage9 network9 latency9", 6),
        ["library9", "service9", "gateway9", "storage9", "network9", "latency9"],
    ),
    (
        ("library9 service9 gateway9 storage9 network9 latency9", 10),
        ["library9", "service9", "gateway9", "storage9", "network9", "latency9"],
    ),
    (
        ("library9 service9 gateway9 storage9 network9 latency9", 18),
        ["library9 service9", "gateway9 storage9", "network9 latency9"],
    ),
    (
        ("library9 service9 gateway9 storage9 network9 latency9", 28),
        ["library9 service9 gateway9", "storage9 network9 latency9"],
    ),
    (
        ("service9 gateway9 storage9 network9 latency9 buffer9", 6),
        ["service9", "gateway9", "storage9", "network9", "latency9", "buffer9"],
    ),
    (
        ("service9 gateway9 storage9 network9 latency9 buffer9", 10),
        ["service9", "gateway9", "storage9", "network9", "latency9", "buffer9"],
    ),
    (
        ("service9 gateway9 storage9 network9 latency9 buffer9", 18),
        ["service9 gateway9", "storage9 network9", "latency9 buffer9"],
    ),
    (
        ("service9 gateway9 storage9 network9 latency9 buffer9", 28),
        ["service9 gateway9 storage9", "network9 latency9 buffer9"],
    ),
    (
        ("gateway9 storage9 network9 latency9 buffer9 queue9", 6),
        ["gateway9", "storage9", "network9", "latency9", "buffer9", "queue9"],
    ),
    (
        ("gateway9 storage9 network9 latency9 buffer9 queue9", 10),
        ["gateway9", "storage9", "network9", "latency9", "buffer9", "queue9"],
    ),
    (
        ("gateway9 storage9 network9 latency9 buffer9 queue9", 18),
        ["gateway9 storage9", "network9 latency9", "buffer9 queue9"],
    ),
    (
        ("gateway9 storage9 network9 latency9 buffer9 queue9", 28),
        ["gateway9 storage9 network9", "latency9 buffer9 queue9"],
    ),
    (
        ("storage9 network9 latency9 buffer9 queue9 worker9", 6),
        ["storage9", "network9", "latency9", "buffer9", "queue9", "worker9"],
    ),
    (
        ("storage9 network9 latency9 buffer9 queue9 worker9", 10),
        ["storage9", "network9", "latency9", "buffer9", "queue9", "worker9"],
    ),
    (
        ("storage9 network9 latency9 buffer9 queue9 worker9", 18),
        ["storage9 network9", "latency9 buffer9", "queue9 worker9"],
    ),
    (
        ("storage9 network9 latency9 buffer9 queue9 worker9", 28),
        ["storage9 network9 latency9", "buffer9 queue9 worker9"],
    ),
    (
        ("network9 latency9 buffer9 queue9 worker9 kernel9", 6),
        ["network9", "latency9", "buffer9", "queue9", "worker9", "kernel9"],
    ),
    (
        ("network9 latency9 buffer9 queue9 worker9 kernel9", 10),
        ["network9", "latency9", "buffer9", "queue9", "worker9", "kernel9"],
    ),
    (
        ("network9 latency9 buffer9 queue9 worker9 kernel9", 18),
        ["network9 latency9", "buffer9 queue9", "worker9 kernel9"],
    ),
    (("network9 latency9 buffer9 queue9 worker9 kernel9", 28), ["network9 latency9 buffer9", "queue9 worker9 kernel9"]),
    (
        ("latency9 buffer9 queue9 worker9 kernel9 signal9", 6),
        ["latency9", "buffer9", "queue9", "worker9", "kernel9", "signal9"],
    ),
    (
        ("latency9 buffer9 queue9 worker9 kernel9 signal9", 10),
        ["latency9", "buffer9", "queue9", "worker9", "kernel9", "signal9"],
    ),
    (
        ("latency9 buffer9 queue9 worker9 kernel9 signal9", 18),
        ["latency9 buffer9", "queue9 worker9", "kernel9 signal9"],
    ),
    (("latency9 buffer9 queue9 worker9 kernel9 signal9", 28), ["latency9 buffer9 queue9", "worker9 kernel9 signal9"]),
    (
        ("buffer9 queue9 worker9 kernel9 signal9 packet9", 6),
        ["buffer9", "queue9", "worker9", "kernel9", "signal9", "packet9"],
    ),
    (
        ("buffer9 queue9 worker9 kernel9 signal9 packet9", 10),
        ["buffer9", "queue9", "worker9", "kernel9", "signal9", "packet9"],
    ),
    (("buffer9 queue9 worker9 kernel9 signal9 packet9", 18), ["buffer9 queue9", "worker9 kernel9", "signal9 packet9"]),
    (("buffer9 queue9 worker9 kernel9 signal9 packet9", 28), ["buffer9 queue9 worker9", "kernel9 signal9 packet9"]),
    (
        ("queue9 worker9 kernel9 signal9 packet9 router9", 6),
        ["queue9", "worker9", "kernel9", "signal9", "packet9", "router9"],
    ),
    (
        ("queue9 worker9 kernel9 signal9 packet9 router9", 10),
        ["queue9", "worker9", "kernel9", "signal9", "packet9", "router9"],
    ),
    (("queue9 worker9 kernel9 signal9 packet9 router9", 18), ["queue9 worker9", "kernel9 signal9", "packet9 router9"]),
    (("queue9 worker9 kernel9 signal9 packet9 router9", 28), ["queue9 worker9 kernel9", "signal9 packet9 router9"]),
    (
        ("worker9 kernel9 signal9 packet9 router9 cluster9", 6),
        ["worker9", "kernel9", "signal9", "packet9", "router9", "cluster9"],
    ),
    (
        ("worker9 kernel9 signal9 packet9 router9 cluster9", 10),
        ["worker9", "kernel9", "signal9", "packet9", "router9", "cluster9"],
    ),
    (
        ("worker9 kernel9 signal9 packet9 router9 cluster9", 18),
        ["worker9 kernel9", "signal9 packet9", "router9 cluster9"],
    ),
    (("worker9 kernel9 signal9 packet9 router9 cluster9", 28), ["worker9 kernel9 signal9", "packet9 router9 cluster9"]),
    (
        ("kernel9 signal9 packet9 router9 cluster9 mirror9", 6),
        ["kernel9", "signal9", "packet9", "router9", "cluster9", "mirror9"],
    ),
    (
        ("kernel9 signal9 packet9 router9 cluster9 mirror9", 10),
        ["kernel9", "signal9", "packet9", "router9", "cluster9", "mirror9"],
    ),
    (
        ("kernel9 signal9 packet9 router9 cluster9 mirror9", 18),
        ["kernel9 signal9", "packet9 router9", "cluster9 mirror9"],
    ),
    (("kernel9 signal9 packet9 router9 cluster9 mirror9", 28), ["kernel9 signal9 packet9", "router9 cluster9 mirror9"]),
    (
        ("signal9 packet9 router9 cluster9 mirror9 filter9", 6),
        ["signal9", "packet9", "router9", "cluster9", "mirror9", "filter9"],
    ),
    (
        ("signal9 packet9 router9 cluster9 mirror9 filter9", 10),
        ["signal9", "packet9", "router9", "cluster9", "mirror9", "filter9"],
    ),
    (
        ("signal9 packet9 router9 cluster9 mirror9 filter9", 18),
        ["signal9 packet9", "router9 cluster9", "mirror9 filter9"],
    ),
    (("signal9 packet9 router9 cluster9 mirror9 filter9", 28), ["signal9 packet9 router9", "cluster9 mirror9 filter9"]),
    (
        ("packet9 router9 cluster9 mirror9 filter9 ranking9", 6),
        ["packet9", "router9", "cluster9", "mirror9", "filter9", "ranking9"],
    ),
    (
        ("packet9 router9 cluster9 mirror9 filter9 ranking9", 10),
        ["packet9", "router9", "cluster9", "mirror9", "filter9", "ranking9"],
    ),
    (
        ("packet9 router9 cluster9 mirror9 filter9 ranking9", 18),
        ["packet9 router9", "cluster9 mirror9", "filter9 ranking9"],
    ),
    (
        ("packet9 router9 cluster9 mirror9 filter9 ranking9", 28),
        ["packet9 router9 cluster9", "mirror9 filter9 ranking9"],
    ),
    (
        ("router9 cluster9 mirror9 filter9 ranking9 encoding9", 6),
        ["router9", "cluster9", "mirror9", "filter9", "ranking9", "encoding9"],
    ),
    (
        ("router9 cluster9 mirror9 filter9 ranking9 encoding9", 10),
        ["router9", "cluster9", "mirror9", "filter9", "ranking9", "encoding9"],
    ),
    (
        ("router9 cluster9 mirror9 filter9 ranking9 encoding9", 18),
        ["router9 cluster9", "mirror9 filter9", "ranking9 encoding9"],
    ),
    (
        ("router9 cluster9 mirror9 filter9 ranking9 encoding9", 28),
        ["router9 cluster9 mirror9", "filter9 ranking9 encoding9"],
    ),
    (
        ("cluster9 mirror9 filter9 ranking9 encoding9 mapping9", 6),
        ["cluster9", "mirror9", "filter9", "ranking9", "encoding9", "mapping9"],
    ),
    (
        ("cluster9 mirror9 filter9 ranking9 encoding9 mapping9", 10),
        ["cluster9", "mirror9", "filter9", "ranking9", "encoding9", "mapping9"],
    ),
    (
        ("cluster9 mirror9 filter9 ranking9 encoding9 mapping9", 18),
        ["cluster9 mirror9", "filter9 ranking9", "encoding9 mapping9"],
    ),
    (
        ("cluster9 mirror9 filter9 ranking9 encoding9 mapping9", 28),
        ["cluster9 mirror9 filter9", "ranking9 encoding9 mapping9"],
    ),
    (
        ("mirror9 filter9 ranking9 encoding9 mapping9 record9", 6),
        ["mirror9", "filter9", "ranking9", "encoding9", "mapping9", "record9"],
    ),
    (
        ("mirror9 filter9 ranking9 encoding9 mapping9 record9", 10),
        ["mirror9", "filter9", "ranking9", "encoding9", "mapping9", "record9"],
    ),
    (
        ("mirror9 filter9 ranking9 encoding9 mapping9 record9", 18),
        ["mirror9 filter9", "ranking9 encoding9", "mapping9 record9"],
    ),
    (
        ("mirror9 filter9 ranking9 encoding9 mapping9 record9", 28),
        ["mirror9 filter9 ranking9", "encoding9 mapping9 record9"],
    ),
    (
        ("filter9 ranking9 encoding9 mapping9 record9 candle9", 6),
        ["filter9", "ranking9", "encoding9", "mapping9", "record9", "candle9"],
    ),
    (
        ("filter9 ranking9 encoding9 mapping9 record9 candle9", 10),
        ["filter9", "ranking9", "encoding9", "mapping9", "record9", "candle9"],
    ),
    (
        ("filter9 ranking9 encoding9 mapping9 record9 candle9", 18),
        ["filter9 ranking9", "encoding9 mapping9", "record9 candle9"],
    ),
    (
        ("filter9 ranking9 encoding9 mapping9 record9 candle9", 28),
        ["filter9 ranking9 encoding9", "mapping9 record9 candle9"],
    ),
    (
        ("ranking9 encoding9 mapping9 record9 candle9 thread9", 6),
        ["ranking9", "encoding9", "mapping9", "record9", "candle9", "thread9"],
    ),
    (
        ("ranking9 encoding9 mapping9 record9 candle9 thread9", 10),
        ["ranking9", "encoding9", "mapping9", "record9", "candle9", "thread9"],
    ),
    (
        ("ranking9 encoding9 mapping9 record9 candle9 thread9", 18),
        ["ranking9 encoding9", "mapping9 record9", "candle9 thread9"],
    ),
    (
        ("ranking9 encoding9 mapping9 record9 candle9 thread9", 28),
        ["ranking9 encoding9 mapping9", "record9 candle9 thread9"],
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
