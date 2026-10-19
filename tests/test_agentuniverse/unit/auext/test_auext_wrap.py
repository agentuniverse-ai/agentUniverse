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
        ("the quick brown fox jumps over the lazy dog", 4),
        ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("the quick brown fox jumps over the lazy dog", 8),
        ["the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (("the quick brown fox jumps over the lazy dog", 12), ["the quick", "brown fox", "jumps over", "the lazy dog"]),
    (("the quick brown fox jumps over the lazy dog", 16), ["the quick brown", "fox jumps over", "the lazy dog"]),
    (("the quick brown fox jumps over the lazy dog", 24), ["the quick brown fox", "jumps over the lazy dog"]),
    (("the quick brown fox jumps over the lazy dog", 32), ["the quick brown fox jumps over", "the lazy dog"]),
    (
        ("agentuniverse is a framework for multi agents", 4),
        ["agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("agentuniverse is a framework for multi agents", 8),
        ["agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("agentuniverse is a framework for multi agents", 12),
        ["agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (("agentuniverse is a framework for multi agents", 16), ["agentuniverse is", "a framework for", "multi agents"]),
    (("agentuniverse is a framework for multi agents", 24), ["agentuniverse is a", "framework for multi", "agents"]),
    (("agentuniverse is a framework for multi agents", 32), ["agentuniverse is a framework for", "multi agents"]),
    (
        ("knowledge stored as vectors enables retrieval", 4),
        ["knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("knowledge stored as vectors enables retrieval", 8),
        ["knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("knowledge stored as vectors enables retrieval", 12),
        ["knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (("knowledge stored as vectors enables retrieval", 16), ["knowledge stored", "as vectors", "enables", "retrieval"]),
    (("knowledge stored as vectors enables retrieval", 24), ["knowledge stored as", "vectors enables", "retrieval"]),
    (("knowledge stored as vectors enables retrieval", 32), ["knowledge stored as vectors", "enables retrieval"]),
    (("the processor reads the record then stops", 4), ["the", "processor", "reads", "the", "record", "then", "stops"]),
    (("the processor reads the record then stops", 8), ["the", "processor", "reads", "the", "record", "then", "stops"]),
    (("the processor reads the record then stops", 12), ["the", "processor", "reads the", "record then", "stops"]),
    (("the processor reads the record then stops", 16), ["the processor", "reads the record", "then stops"]),
    (("the processor reads the record then stops", 24), ["the processor reads the", "record then stops"]),
    (("the processor reads the record then stops", 32), ["the processor reads the record", "then stops"]),
    (
        ("a worker pulls the next task from the queue", 4),
        ["a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("a worker pulls the next task from the queue", 8),
        ["a worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (("a worker pulls the next task from the queue", 12), ["a worker", "pulls the", "next task", "from the", "queue"]),
    (("a worker pulls the next task from the queue", 16), ["a worker pulls", "the next task", "from the queue"]),
    (("a worker pulls the next task from the queue", 24), ["a worker pulls the next", "task from the queue"]),
    (("a worker pulls the next task from the queue", 32), ["a worker pulls the next task", "from the queue"]),
    (("signals travel through the network layer", 4), ["signals", "travel", "through", "the", "network", "layer"]),
    (("signals travel through the network layer", 8), ["signals", "travel", "through", "the", "network", "layer"]),
    (("signals travel through the network layer", 12), ["signals", "travel", "through the", "network", "layer"]),
    (("signals travel through the network layer", 16), ["signals travel", "through the", "network layer"]),
    (("signals travel through the network layer", 24), ["signals travel through", "the network layer"]),
    (("signals travel through the network layer", 32), ["signals travel through the", "network layer"]),
    (("the gateway routes each request by policy", 4), ["the", "gateway", "routes", "each", "request", "by", "policy"]),
    (("the gateway routes each request by policy", 8), ["the", "gateway", "routes", "each", "request", "by", "policy"]),
    (("the gateway routes each request by policy", 12), ["the gateway", "routes each", "request by", "policy"]),
    (("the gateway routes each request by policy", 16), ["the gateway", "routes each", "request by", "policy"]),
    (("the gateway routes each request by policy", 24), ["the gateway routes each", "request by policy"]),
    (("the gateway routes each request by policy", 32), ["the gateway routes each request", "by policy"]),
    (("memory grows until the buffer is full", 4), ["memory", "grows", "until", "the", "buffer", "is", "full"]),
    (("memory grows until the buffer is full", 8), ["memory", "grows", "until", "the", "buffer", "is full"]),
    (("memory grows until the buffer is full", 12), ["memory grows", "until the", "buffer is", "full"]),
    (("memory grows until the buffer is full", 16), ["memory grows", "until the buffer", "is full"]),
    (("memory grows until the buffer is full", 24), ["memory grows until the", "buffer is full"]),
    (("memory grows until the buffer is full", 32), ["memory grows until the buffer is", "full"]),
    (("the cluster mirrors every packet twice", 4), ["the", "cluster", "mirrors", "every", "packet", "twice"]),
    (("the cluster mirrors every packet twice", 8), ["the", "cluster", "mirrors", "every", "packet", "twice"]),
    (("the cluster mirrors every packet twice", 12), ["the cluster", "mirrors", "every packet", "twice"]),
    (("the cluster mirrors every packet twice", 16), ["the cluster", "mirrors every", "packet twice"]),
    (("the cluster mirrors every packet twice", 24), ["the cluster mirrors", "every packet twice"]),
    (("the cluster mirrors every packet twice", 32), ["the cluster mirrors every packet", "twice"]),
    (
        ("ranking uses tokens learned from the corpus", 4),
        ["ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("ranking uses tokens learned from the corpus", 8),
        ["ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (("ranking uses tokens learned from the corpus", 12), ["ranking uses", "tokens", "learned from", "the corpus"]),
    (("ranking uses tokens learned from the corpus", 16), ["ranking uses", "tokens learned", "from the corpus"]),
    (("ranking uses tokens learned from the corpus", 24), ["ranking uses tokens", "learned from the corpus"]),
    (("ranking uses tokens learned from the corpus", 32), ["ranking uses tokens learned from", "the corpus"]),
    (
        ("a long session ends when the candle dies", 4),
        ["a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (("a long session ends when the candle dies", 8), ["a long", "session", "ends", "when the", "candle", "dies"]),
    (("a long session ends when the candle dies", 12), ["a long", "session ends", "when the", "candle dies"]),
    (("a long session ends when the candle dies", 16), ["a long session", "ends when the", "candle dies"]),
    (("a long session ends when the candle dies", 24), ["a long session ends when", "the candle dies"]),
    (("a long session ends when the candle dies", 32), ["a long session ends when the", "candle dies"]),
    (("encode the prompt then map the result", 4), ["encode", "the", "prompt", "then", "map", "the", "result"]),
    (("encode the prompt then map the result", 8), ["encode", "the", "prompt", "then map", "the", "result"]),
    (("encode the prompt then map the result", 12), ["encode the", "prompt then", "map the", "result"]),
    (("encode the prompt then map the result", 16), ["encode the", "prompt then map", "the result"]),
    (("encode the prompt then map the result", 24), ["encode the prompt then", "map the result"]),
    (("encode the prompt then map the result", 32), ["encode the prompt then map the", "result"]),
    (("the kernel wakes the worker at dawn", 4), ["the", "kernel", "wakes", "the", "worker", "at", "dawn"]),
    (("the kernel wakes the worker at dawn", 8), ["the", "kernel", "wakes", "the", "worker", "at dawn"]),
    (("the kernel wakes the worker at dawn", 12), ["the kernel", "wakes the", "worker at", "dawn"]),
    (("the kernel wakes the worker at dawn", 16), ["the kernel wakes", "the worker at", "dawn"]),
    (("the kernel wakes the worker at dawn", 24), ["the kernel wakes the", "worker at dawn"]),
    (("the kernel wakes the worker at dawn", 32), ["the kernel wakes the worker at", "dawn"]),
    (("service latency drops after the patch", 4), ["service", "latency", "drops", "after", "the", "patch"]),
    (("service latency drops after the patch", 8), ["service", "latency", "drops", "after", "the", "patch"]),
    (("service latency drops after the patch", 12), ["service", "latency", "drops after", "the patch"]),
    (("service latency drops after the patch", 16), ["service latency", "drops after the", "patch"]),
    (("service latency drops after the patch", 24), ["service latency drops", "after the patch"]),
    (("service latency drops after the patch", 32), ["service latency drops after the", "patch"]),
    (("the library caches every vector it sees", 4), ["the", "library", "caches", "every", "vector", "it", "sees"]),
    (("the library caches every vector it sees", 8), ["the", "library", "caches", "every", "vector", "it sees"]),
    (("the library caches every vector it sees", 12), ["the library", "caches every", "vector it", "sees"]),
    (("the library caches every vector it sees", 16), ["the library", "caches every", "vector it sees"]),
    (("the library caches every vector it sees", 24), ["the library caches every", "vector it sees"]),
    (("the library caches every vector it sees", 32), ["the library caches every vector", "it sees"]),
    (("agents argue then the debate resolves", 4), ["agents", "argue", "then", "the", "debate", "resolves"]),
    (("agents argue then the debate resolves", 8), ["agents", "argue", "then the", "debate", "resolves"]),
    (("agents argue then the debate resolves", 12), ["agents argue", "then the", "debate", "resolves"]),
    (("agents argue then the debate resolves", 16), ["agents argue", "then the debate", "resolves"]),
    (("agents argue then the debate resolves", 24), ["agents argue then the", "debate resolves"]),
    (("agents argue then the debate resolves", 32), ["agents argue then the debate", "resolves"]),
    (("the filter keeps only strong matches", 4), ["the", "filter", "keeps", "only", "strong", "matches"]),
    (("the filter keeps only strong matches", 8), ["the", "filter", "keeps", "only", "strong", "matches"]),
    (("the filter keeps only strong matches", 12), ["the filter", "keeps only", "strong", "matches"]),
    (("the filter keeps only strong matches", 16), ["the filter keeps", "only strong", "matches"]),
    (("the filter keeps only strong matches", 24), ["the filter keeps only", "strong matches"]),
    (("the filter keeps only strong matches", 32), ["the filter keeps only strong", "matches"]),
    (("the model answers with a short reply", 4), ["the", "model", "answers", "with", "a", "short", "reply"]),
    (("the model answers with a short reply", 8), ["the", "model", "answers", "with a", "short", "reply"]),
    (("the model answers with a short reply", 12), ["the model", "answers with", "a short", "reply"]),
    (("the model answers with a short reply", 16), ["the model", "answers with a", "short reply"]),
    (("the model answers with a short reply", 24), ["the model answers with a", "short reply"]),
    (("the model answers with a short reply", 32), ["the model answers with a short", "reply"]),
    (("the recorder stores the reasoning trace", 4), ["the", "recorder", "stores", "the", "reasoning", "trace"]),
    (("the recorder stores the reasoning trace", 8), ["the", "recorder", "stores", "the", "reasoning", "trace"]),
    (("the recorder stores the reasoning trace", 12), ["the recorder", "stores the", "reasoning", "trace"]),
    (("the recorder stores the reasoning trace", 16), ["the recorder", "stores the", "reasoning trace"]),
    (("the recorder stores the reasoning trace", 24), ["the recorder stores the", "reasoning trace"]),
    (("the recorder stores the reasoning trace", 32), ["the recorder stores the", "reasoning trace"]),
    (("the angel watches the processor run", 4), ["the", "angel", "watches", "the", "processor", "run"]),
    (("the angel watches the processor run", 8), ["the", "angel", "watches", "the", "processor", "run"]),
    (("the angel watches the processor run", 12), ["the angel", "watches the", "processor", "run"]),
    (("the angel watches the processor run", 16), ["the angel", "watches the", "processor run"]),
    (("the angel watches the processor run", 24), ["the angel watches the", "processor run"]),
    (("the angel watches the processor run", 32), ["the angel watches the processor", "run"]),
    (("angle of the vector decides the match", 4), ["angle", "of", "the", "vector", "decides", "the", "match"]),
    (("angle of the vector decides the match", 8), ["angle of", "the", "vector", "decides", "the", "match"]),
    (("angle of the vector decides the match", 12), ["angle of the", "vector", "decides the", "match"]),
    (("angle of the vector decides the match", 16), ["angle of the", "vector decides", "the match"]),
    (("angle of the vector decides the match", 24), ["angle of the vector", "decides the match"]),
    (("angle of the vector decides the match", 32), ["angle of the vector decides the", "match"]),
    (("the candle burns twice as long at night", 4), ["the", "candle", "burns", "twice", "as", "long", "at", "night"]),
    (("the candle burns twice as long at night", 8), ["the", "candle", "burns", "twice as", "long at", "night"]),
    (("the candle burns twice as long at night", 12), ["the candle", "burns twice", "as long at", "night"]),
    (("the candle burns twice as long at night", 16), ["the candle burns", "twice as long at", "night"]),
    (("the candle burns twice as long at night", 24), ["the candle burns twice", "as long at night"]),
    (("the candle burns twice as long at night", 32), ["the candle burns twice as long", "at night"]),
    (("a mirror of the universe in one line", 4), ["a", "mirror", "of", "the", "universe", "in", "one", "line"]),
    (("a mirror of the universe in one line", 8), ["a mirror", "of the", "universe", "in one", "line"]),
    (("a mirror of the universe in one line", 12), ["a mirror of", "the universe", "in one line"]),
    (("a mirror of the universe in one line", 16), ["a mirror of the", "universe in one", "line"]),
    (("a mirror of the universe in one line", 24), ["a mirror of the universe", "in one line"]),
    (("a mirror of the universe in one line", 32), ["a mirror of the universe in one", "line"]),
    (("the queue drains before the storm", 4), ["the", "queue", "drains", "before", "the", "storm"]),
    (("the queue drains before the storm", 8), ["the", "queue", "drains", "before", "the", "storm"]),
    (("the queue drains before the storm", 12), ["the queue", "drains", "before the", "storm"]),
    (("the queue drains before the storm", 16), ["the queue drains", "before the storm"]),
    (("the queue drains before the storm", 24), ["the queue drains before", "the storm"]),
    (("the queue drains before the storm", 32), ["the queue drains before the", "storm"]),
    (("kitten sitting agent angle universe memory", 6), ["kitten", "sitting", "agent", "angle", "universe", "memory"]),
    (("kitten sitting agent angle universe memory", 10), ["kitten", "sitting", "agent", "angle", "universe", "memory"]),
    (("kitten sitting agent angle universe memory", 18), ["kitten sitting", "agent angle", "universe memory"]),
    (("kitten sitting agent angle universe memory", 28), ["kitten sitting agent angle", "universe memory"]),
    (("sitting agent angle universe memory stream", 6), ["sitting", "agent", "angle", "universe", "memory", "stream"]),
    (("sitting agent angle universe memory stream", 10), ["sitting", "agent", "angle", "universe", "memory", "stream"]),
    (("sitting agent angle universe memory stream", 18), ["sitting agent", "angle universe", "memory stream"]),
    (("sitting agent angle universe memory stream", 28), ["sitting agent angle universe", "memory stream"]),
    (("agent angle universe memory stream context", 6), ["agent", "angle", "universe", "memory", "stream", "context"]),
    (("agent angle universe memory stream context", 10), ["agent", "angle", "universe", "memory", "stream", "context"]),
    (("agent angle universe memory stream context", 18), ["agent angle", "universe memory", "stream context"]),
    (("agent angle universe memory stream context", 28), ["agent angle universe memory", "stream context"]),
    (
        ("angle universe memory stream context knowledge", 6),
        ["angle", "universe", "memory", "stream", "context", "knowledge"],
    ),
    (
        ("angle universe memory stream context knowledge", 10),
        ["angle", "universe", "memory", "stream", "context", "knowledge"],
    ),
    (("angle universe memory stream context knowledge", 18), ["angle universe", "memory stream", "context knowledge"]),
    (("angle universe memory stream context knowledge", 28), ["angle universe memory stream", "context knowledge"]),
    (
        ("universe memory stream context knowledge vector", 6),
        ["universe", "memory", "stream", "context", "knowledge", "vector"],
    ),
    (
        ("universe memory stream context knowledge vector", 10),
        ["universe", "memory", "stream", "context", "knowledge", "vector"],
    ),
    (
        ("universe memory stream context knowledge vector", 18),
        ["universe memory", "stream context", "knowledge vector"],
    ),
    (("universe memory stream context knowledge vector", 28), ["universe memory stream", "context knowledge vector"]),
    (
        ("memory stream context knowledge vector processor", 6),
        ["memory", "stream", "context", "knowledge", "vector", "processor"],
    ),
    (
        ("memory stream context knowledge vector processor", 10),
        ["memory", "stream", "context", "knowledge", "vector", "processor"],
    ),
    (
        ("memory stream context knowledge vector processor", 18),
        ["memory stream", "context knowledge", "vector processor"],
    ),
    (("memory stream context knowledge vector processor", 28), ["memory stream context", "knowledge vector processor"]),
    (
        ("stream context knowledge vector processor reasoning", 6),
        ["stream", "context", "knowledge", "vector", "processor", "reasoning"],
    ),
    (
        ("stream context knowledge vector processor reasoning", 10),
        ["stream", "context", "knowledge", "vector", "processor", "reasoning"],
    ),
    (
        ("stream context knowledge vector processor reasoning", 18),
        ["stream context", "knowledge vector", "processor", "reasoning"],
    ),
    (
        ("stream context knowledge vector processor reasoning", 28),
        ["stream context knowledge", "vector processor reasoning"],
    ),
    (
        ("context knowledge vector processor reasoning machine", 6),
        ["context", "knowledge", "vector", "processor", "reasoning", "machine"],
    ),
    (
        ("context knowledge vector processor reasoning machine", 10),
        ["context", "knowledge", "vector", "processor", "reasoning", "machine"],
    ),
    (
        ("context knowledge vector processor reasoning machine", 18),
        ["context knowledge", "vector processor", "reasoning machine"],
    ),
    (
        ("context knowledge vector processor reasoning machine", 28),
        ["context knowledge vector", "processor reasoning machine"],
    ),
    (
        ("knowledge vector processor reasoning machine learning", 6),
        ["knowledge", "vector", "processor", "reasoning", "machine", "learning"],
    ),
    (
        ("knowledge vector processor reasoning machine learning", 10),
        ["knowledge", "vector", "processor", "reasoning", "machine", "learning"],
    ),
    (
        ("knowledge vector processor reasoning machine learning", 18),
        ["knowledge vector", "processor", "reasoning machine", "learning"],
    ),
    (
        ("knowledge vector processor reasoning machine learning", 28),
        ["knowledge vector processor", "reasoning machine learning"],
    ),
    (
        ("vector processor reasoning machine learning model", 6),
        ["vector", "processor", "reasoning", "machine", "learning", "model"],
    ),
    (
        ("vector processor reasoning machine learning model", 10),
        ["vector", "processor", "reasoning", "machine", "learning", "model"],
    ),
    (
        ("vector processor reasoning machine learning model", 18),
        ["vector processor", "reasoning machine", "learning model"],
    ),
    (
        ("vector processor reasoning machine learning model", 28),
        ["vector processor reasoning", "machine learning model"],
    ),
    (
        ("processor reasoning machine learning model token", 6),
        ["processor", "reasoning", "machine", "learning", "model", "token"],
    ),
    (
        ("processor reasoning machine learning model token", 10),
        ["processor", "reasoning", "machine", "learning", "model", "token"],
    ),
    (
        ("processor reasoning machine learning model token", 18),
        ["processor", "reasoning machine", "learning model", "token"],
    ),
    (("processor reasoning machine learning model token", 28), ["processor reasoning machine", "learning model token"]),
    (
        ("reasoning machine learning model token prompt", 6),
        ["reasoning", "machine", "learning", "model", "token", "prompt"],
    ),
    (
        ("reasoning machine learning model token prompt", 10),
        ["reasoning", "machine", "learning", "model", "token", "prompt"],
    ),
    (("reasoning machine learning model token prompt", 18), ["reasoning machine", "learning model", "token prompt"]),
    (("reasoning machine learning model token prompt", 28), ["reasoning machine learning", "model token prompt"]),
    (
        ("machine learning model token prompt session", 6),
        ["machine", "learning", "model", "token", "prompt", "session"],
    ),
    (
        ("machine learning model token prompt session", 10),
        ["machine", "learning", "model", "token", "prompt", "session"],
    ),
    (("machine learning model token prompt session", 18), ["machine learning", "model token prompt", "session"]),
    (("machine learning model token prompt session", 28), ["machine learning model token", "prompt session"]),
    (
        ("learning model token prompt session library", 6),
        ["learning", "model", "token", "prompt", "session", "library"],
    ),
    (
        ("learning model token prompt session library", 10),
        ["learning", "model", "token", "prompt", "session", "library"],
    ),
    (("learning model token prompt session library", 18), ["learning model", "token prompt", "session library"]),
    (("learning model token prompt session library", 28), ["learning model token prompt", "session library"]),
    (("model token prompt session library service", 6), ["model", "token", "prompt", "session", "library", "service"]),
    (("model token prompt session library service", 10), ["model", "token", "prompt", "session", "library", "service"]),
    (("model token prompt session library service", 18), ["model token prompt", "session library", "service"]),
    (("model token prompt session library service", 28), ["model token prompt session", "library service"]),
    (
        ("token prompt session library service gateway", 6),
        ["token", "prompt", "session", "library", "service", "gateway"],
    ),
    (
        ("token prompt session library service gateway", 10),
        ["token", "prompt", "session", "library", "service", "gateway"],
    ),
    (("token prompt session library service gateway", 18), ["token prompt", "session library", "service gateway"]),
    (("token prompt session library service gateway", 28), ["token prompt session library", "service gateway"]),
    (
        ("prompt session library service gateway storage", 6),
        ["prompt", "session", "library", "service", "gateway", "storage"],
    ),
    (
        ("prompt session library service gateway storage", 10),
        ["prompt", "session", "library", "service", "gateway", "storage"],
    ),
    (("prompt session library service gateway storage", 18), ["prompt session", "library service", "gateway storage"]),
    (("prompt session library service gateway storage", 28), ["prompt session library", "service gateway storage"]),
    (
        ("session library service gateway storage network", 6),
        ["session", "library", "service", "gateway", "storage", "network"],
    ),
    (
        ("session library service gateway storage network", 10),
        ["session", "library", "service", "gateway", "storage", "network"],
    ),
    (
        ("session library service gateway storage network", 18),
        ["session library", "service gateway", "storage network"],
    ),
    (("session library service gateway storage network", 28), ["session library service", "gateway storage network"]),
    (
        ("library service gateway storage network latency", 6),
        ["library", "service", "gateway", "storage", "network", "latency"],
    ),
    (
        ("library service gateway storage network latency", 10),
        ["library", "service", "gateway", "storage", "network", "latency"],
    ),
    (
        ("library service gateway storage network latency", 18),
        ["library service", "gateway storage", "network latency"],
    ),
    (("library service gateway storage network latency", 28), ["library service gateway", "storage network latency"]),
    (
        ("service gateway storage network latency buffer", 6),
        ["service", "gateway", "storage", "network", "latency", "buffer"],
    ),
    (
        ("service gateway storage network latency buffer", 10),
        ["service", "gateway", "storage", "network", "latency", "buffer"],
    ),
    (("service gateway storage network latency buffer", 18), ["service gateway", "storage network", "latency buffer"]),
    (("service gateway storage network latency buffer", 28), ["service gateway storage", "network latency buffer"]),
    (
        ("gateway storage network latency buffer queue", 6),
        ["gateway", "storage", "network", "latency", "buffer", "queue"],
    ),
    (
        ("gateway storage network latency buffer queue", 10),
        ["gateway", "storage", "network", "latency", "buffer", "queue"],
    ),
    (("gateway storage network latency buffer queue", 18), ["gateway storage", "network latency", "buffer queue"]),
    (("gateway storage network latency buffer queue", 28), ["gateway storage network", "latency buffer queue"]),
    (
        ("storage network latency buffer queue worker", 6),
        ["storage", "network", "latency", "buffer", "queue", "worker"],
    ),
    (
        ("storage network latency buffer queue worker", 10),
        ["storage", "network", "latency", "buffer", "queue", "worker"],
    ),
    (("storage network latency buffer queue worker", 18), ["storage network", "latency buffer", "queue worker"]),
    (("storage network latency buffer queue worker", 28), ["storage network latency", "buffer queue worker"]),
    (("network latency buffer queue worker kernel", 6), ["network", "latency", "buffer", "queue", "worker", "kernel"]),
    (("network latency buffer queue worker kernel", 10), ["network", "latency", "buffer", "queue", "worker", "kernel"]),
    (("network latency buffer queue worker kernel", 18), ["network latency", "buffer queue", "worker kernel"]),
    (("network latency buffer queue worker kernel", 28), ["network latency buffer queue", "worker kernel"]),
    (("latency buffer queue worker kernel signal", 6), ["latency", "buffer", "queue", "worker", "kernel", "signal"]),
    (("latency buffer queue worker kernel signal", 10), ["latency", "buffer", "queue", "worker", "kernel", "signal"]),
    (("latency buffer queue worker kernel signal", 18), ["latency buffer", "queue worker", "kernel signal"]),
    (("latency buffer queue worker kernel signal", 28), ["latency buffer queue worker", "kernel signal"]),
    (("buffer queue worker kernel signal packet", 6), ["buffer", "queue", "worker", "kernel", "signal", "packet"]),
    (("buffer queue worker kernel signal packet", 10), ["buffer", "queue", "worker", "kernel", "signal", "packet"]),
    (("buffer queue worker kernel signal packet", 18), ["buffer queue", "worker kernel", "signal packet"]),
    (("buffer queue worker kernel signal packet", 28), ["buffer queue worker kernel", "signal packet"]),
    (("queue worker kernel signal packet router", 6), ["queue", "worker", "kernel", "signal", "packet", "router"]),
    (("queue worker kernel signal packet router", 10), ["queue", "worker", "kernel", "signal", "packet", "router"]),
    (("queue worker kernel signal packet router", 18), ["queue worker", "kernel signal", "packet router"]),
    (("queue worker kernel signal packet router", 28), ["queue worker kernel signal", "packet router"]),
    (("worker kernel signal packet router cluster", 6), ["worker", "kernel", "signal", "packet", "router", "cluster"]),
    (("worker kernel signal packet router cluster", 10), ["worker", "kernel", "signal", "packet", "router", "cluster"]),
    (("worker kernel signal packet router cluster", 18), ["worker kernel", "signal packet", "router cluster"]),
    (("worker kernel signal packet router cluster", 28), ["worker kernel signal packet", "router cluster"]),
    (("kernel signal packet router cluster mirror", 6), ["kernel", "signal", "packet", "router", "cluster", "mirror"]),
    (("kernel signal packet router cluster mirror", 10), ["kernel", "signal", "packet", "router", "cluster", "mirror"]),
    (("kernel signal packet router cluster mirror", 18), ["kernel signal", "packet router", "cluster mirror"]),
    (("kernel signal packet router cluster mirror", 28), ["kernel signal packet router", "cluster mirror"]),
    (("signal packet router cluster mirror filter", 6), ["signal", "packet", "router", "cluster", "mirror", "filter"]),
    (("signal packet router cluster mirror filter", 10), ["signal", "packet", "router", "cluster", "mirror", "filter"]),
    (("signal packet router cluster mirror filter", 18), ["signal packet", "router cluster", "mirror filter"]),
    (("signal packet router cluster mirror filter", 28), ["signal packet router cluster", "mirror filter"]),
    (
        ("packet router cluster mirror filter ranking", 6),
        ["packet", "router", "cluster", "mirror", "filter", "ranking"],
    ),
    (
        ("packet router cluster mirror filter ranking", 10),
        ["packet", "router", "cluster", "mirror", "filter", "ranking"],
    ),
    (("packet router cluster mirror filter ranking", 18), ["packet router", "cluster mirror", "filter ranking"]),
    (("packet router cluster mirror filter ranking", 28), ["packet router cluster mirror", "filter ranking"]),
    (
        ("router cluster mirror filter ranking encoding", 6),
        ["router", "cluster", "mirror", "filter", "ranking", "encoding"],
    ),
    (
        ("router cluster mirror filter ranking encoding", 10),
        ["router", "cluster", "mirror", "filter", "ranking", "encoding"],
    ),
    (("router cluster mirror filter ranking encoding", 18), ["router cluster", "mirror filter", "ranking encoding"]),
    (("router cluster mirror filter ranking encoding", 28), ["router cluster mirror filter", "ranking encoding"]),
    (
        ("cluster mirror filter ranking encoding mapping", 6),
        ["cluster", "mirror", "filter", "ranking", "encoding", "mapping"],
    ),
    (
        ("cluster mirror filter ranking encoding mapping", 10),
        ["cluster", "mirror", "filter", "ranking", "encoding", "mapping"],
    ),
    (("cluster mirror filter ranking encoding mapping", 18), ["cluster mirror", "filter ranking", "encoding mapping"]),
    (("cluster mirror filter ranking encoding mapping", 28), ["cluster mirror filter", "ranking encoding mapping"]),
    (
        ("mirror filter ranking encoding mapping record", 6),
        ["mirror", "filter", "ranking", "encoding", "mapping", "record"],
    ),
    (
        ("mirror filter ranking encoding mapping record", 10),
        ["mirror", "filter", "ranking", "encoding", "mapping", "record"],
    ),
    (("mirror filter ranking encoding mapping record", 18), ["mirror filter", "ranking encoding", "mapping record"]),
    (("mirror filter ranking encoding mapping record", 28), ["mirror filter ranking", "encoding mapping record"]),
    (
        ("filter ranking encoding mapping record candle", 6),
        ["filter", "ranking", "encoding", "mapping", "record", "candle"],
    ),
    (
        ("filter ranking encoding mapping record candle", 10),
        ["filter", "ranking", "encoding", "mapping", "record", "candle"],
    ),
    (("filter ranking encoding mapping record candle", 18), ["filter ranking", "encoding mapping", "record candle"]),
    (("filter ranking encoding mapping record candle", 28), ["filter ranking encoding", "mapping record candle"]),
    (
        ("ranking encoding mapping record candle thread", 6),
        ["ranking", "encoding", "mapping", "record", "candle", "thread"],
    ),
    (
        ("ranking encoding mapping record candle thread", 10),
        ["ranking", "encoding", "mapping", "record", "candle", "thread"],
    ),
    (("ranking encoding mapping record candle thread", 18), ["ranking encoding", "mapping record", "candle thread"]),
    (("ranking encoding mapping record candle thread", 28), ["ranking encoding mapping", "record candle thread"]),
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
