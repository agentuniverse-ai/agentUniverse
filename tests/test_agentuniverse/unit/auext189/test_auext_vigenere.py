"""Vigenere cipher: deterministic known-answer vectors (auext)."""

def _ref_vigenere(case):
    """Vigenere cipher: shift each letter by the next key letter (A=0).

    Only letters advance the key; case is preserved; other characters pass
    through. A key without letters returns the input unchanged.
    """
    s, key = case
    key = "".join(ch for ch in key.upper() if "A" <= ch <= "Z")
    if not key:
        return s
    out = []
    i = 0
    for ch in s:
        if "A" <= ch <= "Z":
            k = ord(key[i % len(key)]) - 65
            out.append(chr((ord(ch) - 65 + k) % 26 + 65))
            i += 1
        elif "a" <= ch <= "z":
            k = ord(key[i % len(key)]) - 65
            out.append(chr((ord(ch) - 97 + k) % 26 + 97))
            i += 1
        else:
            out.append(ch)
    return "".join(out)

_CASES = [
    (("kitten189", "key"), "umrdil189"),
    (("kitten189", "lemon"), "vmfhry189"),
    (("kitten189", "a"), "kitten189"),
    (("kitten189", "zz"), "jhssdm189"),
    (("kitten189", "AgentU"), "koxgxh189"),
    (("kitten189", "keyboard"), "umrusn189"),
    (("kitten189", "AA"), "kitten189"),
    (("sitting189", "key"), "cmrdmlq189"),
    (("sitting189", "lemon"), "dmfhvyk189"),
    (("sitting189", "a"), "sitting189"),
    (("sitting189", "zz"), "rhsshmf189"),
    (("sitting189", "AgentU"), "soxgbhg189"),
    (("sitting189", "keyboard"), "cmruwnx189"),
    (("sitting189", "AA"), "sitting189"),
    (("agent189", "key"), "kkcxx189"),
    (("agent189", "lemon"), "lkqbg189"),
    (("agent189", "a"), "agent189"),
    (("agent189", "zz"), "zfdms189"),
    (("agent189", "AgentU"), "amiam189"),
    (("agent189", "keyboard"), "kkcoh189"),
    (("agent189", "AA"), "agent189"),
    (("angle189", "key"), "krevi189"),
    (("angle189", "lemon"), "lrszr189"),
    (("angle189", "a"), "angle189"),
    (("angle189", "zz"), "zmfkd189"),
    (("angle189", "AgentU"), "atkyx189"),
    (("angle189", "keyboard"), "krems189"),
    (("angle189", "AA"), "angle189"),
    (("universe189", "key"), "ergfipci189"),
    (("universe189", "lemon"), "frujrcwq189"),
    (("universe189", "a"), "universe189"),
    (("universe189", "zz"), "tmhudqrd189"),
    (("universe189", "AgentU"), "utmixlsk189"),
    (("universe189", "keyboard"), "ergwsrjh189"),
    (("universe189", "AA"), "universe189"),
    (("memory189", "key"), "wikyvw189"),
    (("memory189", "lemon"), "xiycej189"),
    (("memory189", "a"), "memory189"),
    (("memory189", "zz"), "ldlnqx189"),
    (("memory189", "AgentU"), "mkqbks189"),
    (("memory189", "keyboard"), "wikpfy189"),
    (("memory189", "AA"), "memory189"),
    (("stream189", "key"), "cxpoek189"),
    (("stream189", "lemon"), "dxdsnx189"),
    (("stream189", "a"), "stream189"),
    (("stream189", "zz"), "rsqdzl189"),
    (("stream189", "AgentU"), "szvrtg189"),
    (("stream189", "keyboard"), "cxpfom189"),
    (("stream189", "AA"), "stream189"),
    (("context189", "key"), "msldivd189"),
    (("context189", "lemon"), "nszhrix189"),
    (("context189", "a"), "context189"),
    (("context189", "zz"), "bnmsdws189"),
    (("context189", "AgentU"), "curgxrt189"),
    (("context189", "keyboard"), "mslusxk189"),
    (("context189", "AA"), "context189"),
    (("knowledge189", "key"), "urmgpcnkc189"),
    (("knowledge189", "lemon"), "vrakyphss189"),
    (("knowledge189", "a"), "knowledge189"),
    (("knowledge189", "zz"), "jmnvkdcfd189"),
    (("knowledge189", "AgentU"), "ktsjeydmi189"),
    (("knowledge189", "keyboard"), "urmxzeujo189"),
    (("knowledge189", "AA"), "knowledge189"),
    (("vector189", "key"), "fiadsp189"),
    (("vector189", "lemon"), "giohbc189"),
    (("vector189", "a"), "vector189"),
    (("vector189", "zz"), "udbsnq189"),
    (("vector189", "AgentU"), "vkgghl189"),
    (("vector189", "keyboard"), "fiaucr189"),
    (("vector189", "AA"), "vector189"),
    (("processor189", "key"), "zvmmiqcsp189"),
    (("processor189", "lemon"), "avaqrdwaf189"),
    (("processor189", "a"), "processor189"),
    (("processor189", "zz"), "oqnbdrrnq189"),
    (("processor189", "AgentU"), "pxspxmsuv189"),
    (("processor189", "keyboard"), "zvmdssjrb189"),
    (("processor189", "AA"), "processor189"),
    (("reasoning189", "key"), "biycslsre189"),
    (("reasoning189", "lemon"), "cimgbymzu189"),
    (("reasoning189", "a"), "reasoning189"),
    (("reasoning189", "zz"), "qdzrnmhmf189"),
    (("reasoning189", "AgentU"), "rkefhhitk189"),
    (("reasoning189", "keyboard"), "biytcnzqq189"),
    (("reasoning189", "AA"), "reasoning189"),
    (("machine189", "key"), "wearmlo189"),
    (("machine189", "lemon"), "xeovvyi189"),
    (("machine189", "a"), "machine189"),
    (("machine189", "zz"), "lzbghmd189"),
    (("machine189", "AgentU"), "mggubhe189"),
    (("machine189", "keyboard"), "weaiwnv189"),
    (("machine189", "AA"), "machine189"),
    (("learning189", "key"), "viybrgxk189"),
    (("learning189", "lemon"), "wimfatrs189"),
    (("learning189", "a"), "learning189"),
    (("learning189", "zz"), "kdzqmhmf189"),
    (("learning189", "AgentU"), "lkeegcnm189"),
    (("learning189", "keyboard"), "viysbiej189"),
    (("learning189", "AA"), "learning189"),
    (("model189", "key"), "wsbop189"),
    (("model189", "lemon"), "xspsy189"),
    (("model189", "a"), "model189"),
    (("model189", "zz"), "lncdk189"),
    (("model189", "AgentU"), "muhre189"),
    (("model189", "keyboard"), "wsbfz189"),
    (("model189", "AA"), "model189"),
    (("token189", "key"), "dsior189"),
    (("token189", "lemon"), "eswsa189"),
    (("token189", "a"), "token189"),
    (("token189", "zz"), "snjdm189"),
    (("token189", "AgentU"), "tuorg189"),
    (("token189", "keyboard"), "dsifb189"),
    (("token189", "AA"), "token189"),
    (("prompt189", "key"), "zvmwtr189"),
    (("prompt189", "lemon"), "avaace189"),
    (("prompt189", "a"), "prompt189"),
    (("prompt189", "zz"), "oqnlos189"),
    (("prompt189", "AgentU"), "pxszin189"),
    (("prompt189", "keyboard"), "zvmndt189"),
    (("prompt189", "AA"), "prompt189"),
    (("session189", "key"), "ciqcmmx189"),
    (("session189", "lemon"), "diegvzr189"),
    (("session189", "a"), "session189"),
    (("session189", "zz"), "rdrrhnm189"),
    (("session189", "AgentU"), "skwfbin189"),
    (("session189", "keyboard"), "ciqtwoe189"),
    (("session189", "AA"), "session189"),
    (("library189", "key"), "vmzbepi189"),
    (("library189", "lemon"), "wmnfncc189"),
    (("library189", "a"), "library189"),
    (("library189", "zz"), "khaqzqx189"),
    (("library189", "AgentU"), "lofetly189"),
    (("library189", "keyboard"), "vmzsorp189"),
    (("library189", "AA"), "library189"),
    (("service189", "key"), "cipfmao189"),
    (("service189", "lemon"), "didjvni189"),
    (("service189", "a"), "service189"),
    (("service189", "zz"), "rdquhbd189"),
    (("service189", "AgentU"), "skvibwe189"),
    (("service189", "keyboard"), "cipwwcv189"),
    (("service189", "AA"), "service189"),
    (("gateway189", "key"), "qeroayi189"),
    (("gateway189", "lemon"), "refsjlc189"),
    (("gateway189", "a"), "gateway189"),
    (("gateway189", "zz"), "fzsdvzx189"),
    (("gateway189", "AgentU"), "ggxrpuy189"),
    (("gateway189", "keyboard"), "qerfkap189"),
    (("gateway189", "AA"), "gateway189"),
    (("storage189", "key"), "cxmbeeo189"),
    (("storage189", "lemon"), "dxafnri189"),
    (("storage189", "a"), "storage189"),
    (("storage189", "zz"), "rsnqzfd189"),
    (("storage189", "AgentU"), "szsetae189"),
    (("storage189", "keyboard"), "cxmsogv189"),
    (("storage189", "AA"), "storage189"),
    (("network189", "key"), "xirgspu189"),
    (("network189", "lemon"), "yifkbco189"),
    (("network189", "a"), "network189"),
    (("network189", "zz"), "mdsvnqj189"),
    (("network189", "AgentU"), "nkxjhlk189"),
    (("network189", "keyboard"), "xirxcrb189"),
    (("network189", "AA"), "network189"),
    (("latency189", "key"), "verorai189"),
    (("latency189", "lemon"), "wefsanc189"),
    (("latency189", "a"), "latency189"),
    (("latency189", "zz"), "kzsdmbx189"),
    (("latency189", "AgentU"), "lgxrgwy189"),
    (("latency189", "keyboard"), "verfbcp189"),
    (("latency189", "AA"), "latency189"),
    (("buffer189", "key"), "lydpip189"),
    (("buffer189", "lemon"), "myrtrc189"),
    (("buffer189", "a"), "buffer189"),
    (("buffer189", "zz"), "ateedq189"),
    (("buffer189", "AgentU"), "bajsxl189"),
    (("buffer189", "keyboard"), "lydgsr189"),
    (("buffer189", "AA"), "buffer189"),
    (("queue189", "key"), "aycei189"),
    (("queue189", "lemon"), "byqir189"),
    (("queue189", "a"), "queue189"),
    (("queue189", "zz"), "ptdtd189"),
    (("queue189", "AgentU"), "qaihx189"),
    (("queue189", "keyboard"), "aycvs189"),
    (("queue189", "AA"), "queue189"),
    (("worker189", "key"), "gspuip189"),
    (("worker189", "lemon"), "hsdyrc189"),
    (("worker189", "a"), "worker189"),
    (("worker189", "zz"), "vnqjdq189"),
    (("worker189", "AgentU"), "wuvxxl189"),
    (("worker189", "keyboard"), "gsplsr189"),
    (("worker189", "AA"), "worker189"),
    (("kernel189", "key"), "uipxij189"),
    (("kernel189", "lemon"), "vidbrw189"),
    (("kernel189", "a"), "kernel189"),
    (("kernel189", "zz"), "jdqmdk189"),
    (("kernel189", "AgentU"), "kkvaxf189"),
    (("kernel189", "keyboard"), "uiposl189"),
    (("kernel189", "AA"), "kernel189"),
    (("signal189", "key"), "cmexej189"),
    (("signal189", "lemon"), "dmsbnw189"),
    (("signal189", "a"), "signal189"),
    (("signal189", "zz"), "rhfmzk189"),
    (("signal189", "AgentU"), "sokatf189"),
    (("signal189", "keyboard"), "cmeool189"),
    (("signal189", "AA"), "signal189"),
    (("packet189", "key"), "zeauir189"),
    (("packet189", "lemon"), "aeoyre189"),
    (("packet189", "a"), "packet189"),
    (("packet189", "zz"), "ozbjds189"),
    (("packet189", "AgentU"), "pggxxn189"),
    (("packet189", "keyboard"), "zealst189"),
    (("packet189", "AA"), "packet189"),
    (("router189", "key"), "bssdip189"),
    (("router189", "lemon"), "csghrc189"),
    (("router189", "a"), "router189"),
    (("router189", "zz"), "qntsdq189"),
    (("router189", "AgentU"), "ruygxl189"),
    (("router189", "keyboard"), "bssusr189"),
    (("router189", "AA"), "router189"),
    (("cluster189", "key"), "mpscxcb189"),
    (("cluster189", "lemon"), "npgggpv189"),
    (("cluster189", "a"), "cluster189"),
    (("cluster189", "zz"), "bktrsdq189"),
    (("cluster189", "AgentU"), "cryfmyr189"),
    (("cluster189", "keyboard"), "mpsthei189"),
    (("cluster189", "AA"), "cluster189"),
    (("mirror189", "key"), "wmpbsp189"),
    (("mirror189", "lemon"), "xmdfbc189"),
    (("mirror189", "a"), "mirror189"),
    (("mirror189", "zz"), "lhqqnq189"),
    (("mirror189", "AgentU"), "movehl189"),
    (("mirror189", "keyboard"), "wmpscr189"),
    (("mirror189", "AA"), "mirror189"),
    (("filter189", "key"), "pmjdip189"),
    (("filter189", "lemon"), "qmxhrc189"),
    (("filter189", "a"), "filter189"),
    (("filter189", "zz"), "ehksdq189"),
    (("filter189", "AgentU"), "fopgxl189"),
    (("filter189", "keyboard"), "pmjusr189"),
    (("filter189", "AA"), "filter189"),
    (("ranking189", "key"), "belumlq189"),
    (("ranking189", "lemon"), "cezyvyk189"),
    (("ranking189", "a"), "ranking189"),
    (("ranking189", "zz"), "qzmjhmf189"),
    (("ranking189", "AgentU"), "rgrxbhg189"),
    (("ranking189", "keyboard"), "bellwnx189"),
    (("ranking189", "AA"), "ranking189"),
    (("encoding189", "key"), "orayhgxk189"),
    (("encoding189", "lemon"), "procqtrs189"),
    (("encoding189", "a"), "encoding189"),
    (("encoding189", "zz"), "dmbnchmf189"),
    (("encoding189", "AgentU"), "etgbwcnm189"),
    (("encoding189", "keyboard"), "orapriej189"),
    (("encoding189", "AA"), "encoding189"),
    (("mapping189", "key"), "wenzmlq189"),
    (("mapping189", "lemon"), "xebdvyk189"),
    (("mapping189", "a"), "mapping189"),
    (("mapping189", "zz"), "lzoohmf189"),
    (("mapping189", "AgentU"), "mgtcbhg189"),
    (("mapping189", "keyboard"), "wenqwnx189"),
    (("mapping189", "AA"), "mapping189"),
    (("record189", "key"), "biayvb189"),
    (("record189", "lemon"), "cioceo189"),
    (("record189", "a"), "record189"),
    (("record189", "zz"), "qdbnqc189"),
    (("record189", "AgentU"), "rkgbkx189"),
    (("record189", "keyboard"), "biapfd189"),
    (("record189", "AA"), "record189"),
    (("candle189", "key"), "melnpc189"),
    (("candle189", "lemon"), "nezryp189"),
    (("candle189", "a"), "candle189"),
    (("candle189", "zz"), "bzmckd189"),
    (("candle189", "AgentU"), "cgrqey189"),
    (("candle189", "keyboard"), "meleze189"),
    (("candle189", "AA"), "candle189"),
    (("thread189", "key"), "dlpoeb189"),
    (("thread189", "lemon"), "eldsno189"),
    (("thread189", "a"), "thread189"),
    (("thread189", "zz"), "sgqdzc189"),
    (("thread189", "AgentU"), "tnvrtx189"),
    (("thread189", "keyboard"), "dlpfod189"),
    (("thread189", "AA"), "thread189"),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 189: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 189: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "a"),
        "round 189: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 189: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 189: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 189: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", "AA"),
        "round 189: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "key"),
        "bssxh 189: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 189: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "a"),
        "round 189: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 189: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 189: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 189: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", "AA"),
        "round 189: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 189: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 189: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "a"),
        "round 189: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 189: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 189: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 189: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", "AA"),
        "round 189: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 189: the processor reads the record then stops", "key"),
        "bssxh 189: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 189: the processor reads the record then stops", "lemon"),
        "csgbq 189: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 189: the processor reads the record then stops", "a"),
        "round 189: the processor reads the record then stops",
    ),
    (
        ("round 189: the processor reads the record then stops", "zz"),
        "qntmc 189: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 189: the processor reads the record then stops", "AgentU"),
        "ruyaw 189: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 189: the processor reads the record then stops", "keyboard"),
        "bssor 189: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 189: the processor reads the record then stops", "AA"),
        "round 189: the processor reads the record then stops",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "key"),
        "bssxh 189: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "lemon"),
        "csgbq 189: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "a"),
        "round 189: a worker pulls the next task from the queue",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "zz"),
        "qntmc 189: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 189: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "keyboard"),
        "bssor 189: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 189: a worker pulls the next task from the queue", "AA"),
        "round 189: a worker pulls the next task from the queue",
    ),
    (
        ("round 189: signals travel through the network layer", "key"),
        "bssxh 189: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 189: signals travel through the network layer", "lemon"),
        "csgbq 189: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 189: signals travel through the network layer", "a"),
        "round 189: signals travel through the network layer",
    ),
    (
        ("round 189: signals travel through the network layer", "zz"),
        "qntmc 189: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 189: signals travel through the network layer", "AgentU"),
        "ruyaw 189: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 189: signals travel through the network layer", "keyboard"),
        "bssor 189: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 189: signals travel through the network layer", "AA"),
        "round 189: signals travel through the network layer",
    ),
    (
        ("round 189: the gateway routes each request by policy", "key"),
        "bssxh 189: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 189: the gateway routes each request by policy", "lemon"),
        "csgbq 189: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 189: the gateway routes each request by policy", "a"),
        "round 189: the gateway routes each request by policy",
    ),
    (
        ("round 189: the gateway routes each request by policy", "zz"),
        "qntmc 189: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 189: the gateway routes each request by policy", "AgentU"),
        "ruyaw 189: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 189: the gateway routes each request by policy", "keyboard"),
        "bssor 189: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 189: the gateway routes each request by policy", "AA"),
        "round 189: the gateway routes each request by policy",
    ),
    (("round 189: memory grows until the buffer is full", "key"), "bssxh 189: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 189: memory grows until the buffer is full", "lemon"), "csgbq 189: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 189: memory grows until the buffer is full", "a"), "round 189: memory grows until the buffer is full"),
    (("round 189: memory grows until the buffer is full", "zz"), "qntmc 189: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 189: memory grows until the buffer is full", "AgentU"),
        "ruyaw 189: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 189: memory grows until the buffer is full", "keyboard"),
        "bssor 189: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 189: memory grows until the buffer is full", "AA"), "round 189: memory grows until the buffer is full"),
    (("round 189: the cluster mirrors every packet twice", "key"), "bssxh 189: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 189: the cluster mirrors every packet twice", "lemon"),
        "csgbq 189: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 189: the cluster mirrors every packet twice", "a"), "round 189: the cluster mirrors every packet twice"),
    (("round 189: the cluster mirrors every packet twice", "zz"), "qntmc 189: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 189: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 189: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 189: the cluster mirrors every packet twice", "keyboard"),
        "bssor 189: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 189: the cluster mirrors every packet twice", "AA"), "round 189: the cluster mirrors every packet twice"),
    (
        ("round 189: ranking uses tokens learned from the corpus", "key"),
        "bssxh 189: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 189: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", "a"),
        "round 189: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 189: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 189: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 189: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", "AA"),
        "round 189: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 189: a long session ends when the candle dies", "key"),
        "bssxh 189: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 189: a long session ends when the candle dies", "lemon"),
        "csgbq 189: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 189: a long session ends when the candle dies", "a"),
        "round 189: a long session ends when the candle dies",
    ),
    (
        ("round 189: a long session ends when the candle dies", "zz"),
        "qntmc 189: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 189: a long session ends when the candle dies", "AgentU"),
        "ruyaw 189: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 189: a long session ends when the candle dies", "keyboard"),
        "bssor 189: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 189: a long session ends when the candle dies", "AA"),
        "round 189: a long session ends when the candle dies",
    ),
    (("round 189: encode the prompt then map the result", "key"), "bssxh 189: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 189: encode the prompt then map the result", "lemon"), "csgbq 189: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 189: encode the prompt then map the result", "a"), "round 189: encode the prompt then map the result"),
    (("round 189: encode the prompt then map the result", "zz"), "qntmc 189: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 189: encode the prompt then map the result", "AgentU"),
        "ruyaw 189: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 189: encode the prompt then map the result", "keyboard"),
        "bssor 189: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 189: encode the prompt then map the result", "AA"), "round 189: encode the prompt then map the result"),
    (("round 189: the kernel wakes the worker at dawn", "key"), "bssxh 189: rri iovlop ukocc xfo ambocb er neux"),
    (("round 189: the kernel wakes the worker at dawn", "lemon"), "csgbq 189: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 189: the kernel wakes the worker at dawn", "a"), "round 189: the kernel wakes the worker at dawn"),
    (("round 189: the kernel wakes the worker at dawn", "zz"), "qntmc 189: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 189: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 189: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 189: the kernel wakes the worker at dawn", "keyboard"), "bssor 189: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 189: the kernel wakes the worker at dawn", "AA"), "round 189: the kernel wakes the worker at dawn"),
    (("round 189: service latency drops after the patch", "key"), "bssxh 189: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 189: service latency drops after the patch", "lemon"), "csgbq 189: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 189: service latency drops after the patch", "a"), "round 189: service latency drops after the patch"),
    (("round 189: service latency drops after the patch", "zz"), "qntmc 189: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 189: service latency drops after the patch", "AgentU"),
        "ruyaw 189: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 189: service latency drops after the patch", "keyboard"),
        "bssor 189: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 189: service latency drops after the patch", "AA"), "round 189: service latency drops after the patch"),
    (
        ("round 189: the library caches every vector it sees", "key"),
        "bssxh 189: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 189: the library caches every vector it sees", "lemon"),
        "csgbq 189: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 189: the library caches every vector it sees", "a"), "round 189: the library caches every vector it sees"),
    (
        ("round 189: the library caches every vector it sees", "zz"),
        "qntmc 189: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 189: the library caches every vector it sees", "AgentU"),
        "ruyaw 189: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 189: the library caches every vector it sees", "keyboard"),
        "bssor 189: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 189: the library caches every vector it sees", "AA"),
        "round 189: the library caches every vector it sees",
    ),
    (("round 189: agents argue then the debate resolves", "key"), "bssxh 189: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 189: agents argue then the debate resolves", "lemon"), "csgbq 189: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 189: agents argue then the debate resolves", "a"), "round 189: agents argue then the debate resolves"),
    (("round 189: agents argue then the debate resolves", "zz"), "qntmc 189: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 189: agents argue then the debate resolves", "AgentU"),
        "ruyaw 189: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 189: agents argue then the debate resolves", "keyboard"),
        "bssor 189: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 189: agents argue then the debate resolves", "AA"), "round 189: agents argue then the debate resolves"),
    (("round 189: the filter keeps only strong matches", "key"), "bssxh 189: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 189: the filter keeps only strong matches", "lemon"), "csgbq 189: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 189: the filter keeps only strong matches", "a"), "round 189: the filter keeps only strong matches"),
    (("round 189: the filter keeps only strong matches", "zz"), "qntmc 189: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 189: the filter keeps only strong matches", "AgentU"), "ruyaw 189: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 189: the filter keeps only strong matches", "keyboard"),
        "bssor 189: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 189: the filter keeps only strong matches", "AA"), "round 189: the filter keeps only strong matches"),
    (("round 189: the model answers with a short reply", "key"), "bssxh 189: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 189: the model answers with a short reply", "lemon"), "csgbq 189: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 189: the model answers with a short reply", "a"), "round 189: the model answers with a short reply"),
    (("round 189: the model answers with a short reply", "zz"), "qntmc 189: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 189: the model answers with a short reply", "AgentU"), "ruyaw 189: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 189: the model answers with a short reply", "keyboard"),
        "bssor 189: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 189: the model answers with a short reply", "AA"), "round 189: the model answers with a short reply"),
    (
        ("round 189: the recorder stores the reasoning trace", "key"),
        "bssxh 189: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 189: the recorder stores the reasoning trace", "lemon"),
        "csgbq 189: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 189: the recorder stores the reasoning trace", "a"), "round 189: the recorder stores the reasoning trace"),
    (
        ("round 189: the recorder stores the reasoning trace", "zz"),
        "qntmc 189: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 189: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 189: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 189: the recorder stores the reasoning trace", "keyboard"),
        "bssor 189: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 189: the recorder stores the reasoning trace", "AA"),
        "round 189: the recorder stores the reasoning trace",
    ),
    (("round 189: the angel watches the processor run", "key"), "bssxh 189: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 189: the angel watches the processor run", "lemon"), "csgbq 189: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 189: the angel watches the processor run", "a"), "round 189: the angel watches the processor run"),
    (("round 189: the angel watches the processor run", "zz"), "qntmc 189: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 189: the angel watches the processor run", "AgentU"), "ruyaw 189: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 189: the angel watches the processor run", "keyboard"), "bssor 189: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 189: the angel watches the processor run", "AA"), "round 189: the angel watches the processor run"),
    (("round 189: angle of the vector decides the match", "key"), "bssxh 189: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 189: angle of the vector decides the match", "lemon"), "csgbq 189: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 189: angle of the vector decides the match", "a"), "round 189: angle of the vector decides the match"),
    (("round 189: angle of the vector decides the match", "zz"), "qntmc 189: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 189: angle of the vector decides the match", "AgentU"),
        "ruyaw 189: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 189: angle of the vector decides the match", "keyboard"),
        "bssor 189: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 189: angle of the vector decides the match", "AA"), "round 189: angle of the vector decides the match"),
    (
        ("round 189: the candle burns twice as long at night", "key"),
        "bssxh 189: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 189: the candle burns twice as long at night", "lemon"),
        "csgbq 189: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 189: the candle burns twice as long at night", "a"), "round 189: the candle burns twice as long at night"),
    (
        ("round 189: the candle burns twice as long at night", "zz"),
        "qntmc 189: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 189: the candle burns twice as long at night", "AgentU"),
        "ruyaw 189: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 189: the candle burns twice as long at night", "keyboard"),
        "bssor 189: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 189: the candle burns twice as long at night", "AA"),
        "round 189: the candle burns twice as long at night",
    ),
    (("round 189: a mirror of the universe in one line", "key"), "bssxh 189: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 189: a mirror of the universe in one line", "lemon"), "csgbq 189: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 189: a mirror of the universe in one line", "a"), "round 189: a mirror of the universe in one line"),
    (("round 189: a mirror of the universe in one line", "zz"), "qntmc 189: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 189: a mirror of the universe in one line", "AgentU"), "ruyaw 189: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 189: a mirror of the universe in one line", "keyboard"),
        "bssor 189: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 189: a mirror of the universe in one line", "AA"), "round 189: a mirror of the universe in one line"),
    (("round 189: the queue drains before the storm", "key"), "bssxh 189: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 189: the queue drains before the storm", "lemon"), "csgbq 189: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 189: the queue drains before the storm", "a"), "round 189: the queue drains before the storm"),
    (("round 189: the queue drains before the storm", "zz"), "qntmc 189: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 189: the queue drains before the storm", "AgentU"), "ruyaw 189: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 189: the queue drains before the storm", "keyboard"), "bssor 189: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 189: the queue drains before the storm", "AA"), "round 189: the queue drains before the storm"),
    ((" Attack! 2026.", "lemon"), " Lxfopv! 2026."),
    (("THE---QUICK", "a"), "THE---QUICK"),
    (("", "key"), ""),
    (("no-caps-here", "K"), "xy-mkzc-robo"),
    (("MixedCase123", "PassWord"), "BipwzQrvt123"),
]

_EXPECTED_COUNT = 453

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_vigenere(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..239."""
    for case, expected in _CASES[120:240]:
        assert _ref_vigenere(case) == expected

def test_vectors_240():
    """Known-answer vectors 240..359."""
    for case, expected in _CASES[240:360]:
        assert _ref_vigenere(case) == expected

def test_vectors_360():
    """Known-answer vectors 360..452."""
    for case, expected in _CASES[360:453]:
        assert _ref_vigenere(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_vigenere(case) == expected
        assert _ref_vigenere(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_vigenere(case) == expected
        assert _ref_vigenere(case) == expected
