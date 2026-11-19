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
    (("kitten164", "key"), "umrdil164"),
    (("kitten164", "lemon"), "vmfhry164"),
    (("kitten164", "a"), "kitten164"),
    (("kitten164", "zz"), "jhssdm164"),
    (("kitten164", "AgentU"), "koxgxh164"),
    (("kitten164", "keyboard"), "umrusn164"),
    (("kitten164", "AA"), "kitten164"),
    (("sitting164", "key"), "cmrdmlq164"),
    (("sitting164", "lemon"), "dmfhvyk164"),
    (("sitting164", "a"), "sitting164"),
    (("sitting164", "zz"), "rhsshmf164"),
    (("sitting164", "AgentU"), "soxgbhg164"),
    (("sitting164", "keyboard"), "cmruwnx164"),
    (("sitting164", "AA"), "sitting164"),
    (("agent164", "key"), "kkcxx164"),
    (("agent164", "lemon"), "lkqbg164"),
    (("agent164", "a"), "agent164"),
    (("agent164", "zz"), "zfdms164"),
    (("agent164", "AgentU"), "amiam164"),
    (("agent164", "keyboard"), "kkcoh164"),
    (("agent164", "AA"), "agent164"),
    (("angle164", "key"), "krevi164"),
    (("angle164", "lemon"), "lrszr164"),
    (("angle164", "a"), "angle164"),
    (("angle164", "zz"), "zmfkd164"),
    (("angle164", "AgentU"), "atkyx164"),
    (("angle164", "keyboard"), "krems164"),
    (("angle164", "AA"), "angle164"),
    (("universe164", "key"), "ergfipci164"),
    (("universe164", "lemon"), "frujrcwq164"),
    (("universe164", "a"), "universe164"),
    (("universe164", "zz"), "tmhudqrd164"),
    (("universe164", "AgentU"), "utmixlsk164"),
    (("universe164", "keyboard"), "ergwsrjh164"),
    (("universe164", "AA"), "universe164"),
    (("memory164", "key"), "wikyvw164"),
    (("memory164", "lemon"), "xiycej164"),
    (("memory164", "a"), "memory164"),
    (("memory164", "zz"), "ldlnqx164"),
    (("memory164", "AgentU"), "mkqbks164"),
    (("memory164", "keyboard"), "wikpfy164"),
    (("memory164", "AA"), "memory164"),
    (("stream164", "key"), "cxpoek164"),
    (("stream164", "lemon"), "dxdsnx164"),
    (("stream164", "a"), "stream164"),
    (("stream164", "zz"), "rsqdzl164"),
    (("stream164", "AgentU"), "szvrtg164"),
    (("stream164", "keyboard"), "cxpfom164"),
    (("stream164", "AA"), "stream164"),
    (("context164", "key"), "msldivd164"),
    (("context164", "lemon"), "nszhrix164"),
    (("context164", "a"), "context164"),
    (("context164", "zz"), "bnmsdws164"),
    (("context164", "AgentU"), "curgxrt164"),
    (("context164", "keyboard"), "mslusxk164"),
    (("context164", "AA"), "context164"),
    (("knowledge164", "key"), "urmgpcnkc164"),
    (("knowledge164", "lemon"), "vrakyphss164"),
    (("knowledge164", "a"), "knowledge164"),
    (("knowledge164", "zz"), "jmnvkdcfd164"),
    (("knowledge164", "AgentU"), "ktsjeydmi164"),
    (("knowledge164", "keyboard"), "urmxzeujo164"),
    (("knowledge164", "AA"), "knowledge164"),
    (("vector164", "key"), "fiadsp164"),
    (("vector164", "lemon"), "giohbc164"),
    (("vector164", "a"), "vector164"),
    (("vector164", "zz"), "udbsnq164"),
    (("vector164", "AgentU"), "vkgghl164"),
    (("vector164", "keyboard"), "fiaucr164"),
    (("vector164", "AA"), "vector164"),
    (("processor164", "key"), "zvmmiqcsp164"),
    (("processor164", "lemon"), "avaqrdwaf164"),
    (("processor164", "a"), "processor164"),
    (("processor164", "zz"), "oqnbdrrnq164"),
    (("processor164", "AgentU"), "pxspxmsuv164"),
    (("processor164", "keyboard"), "zvmdssjrb164"),
    (("processor164", "AA"), "processor164"),
    (("reasoning164", "key"), "biycslsre164"),
    (("reasoning164", "lemon"), "cimgbymzu164"),
    (("reasoning164", "a"), "reasoning164"),
    (("reasoning164", "zz"), "qdzrnmhmf164"),
    (("reasoning164", "AgentU"), "rkefhhitk164"),
    (("reasoning164", "keyboard"), "biytcnzqq164"),
    (("reasoning164", "AA"), "reasoning164"),
    (("machine164", "key"), "wearmlo164"),
    (("machine164", "lemon"), "xeovvyi164"),
    (("machine164", "a"), "machine164"),
    (("machine164", "zz"), "lzbghmd164"),
    (("machine164", "AgentU"), "mggubhe164"),
    (("machine164", "keyboard"), "weaiwnv164"),
    (("machine164", "AA"), "machine164"),
    (("learning164", "key"), "viybrgxk164"),
    (("learning164", "lemon"), "wimfatrs164"),
    (("learning164", "a"), "learning164"),
    (("learning164", "zz"), "kdzqmhmf164"),
    (("learning164", "AgentU"), "lkeegcnm164"),
    (("learning164", "keyboard"), "viysbiej164"),
    (("learning164", "AA"), "learning164"),
    (("model164", "key"), "wsbop164"),
    (("model164", "lemon"), "xspsy164"),
    (("model164", "a"), "model164"),
    (("model164", "zz"), "lncdk164"),
    (("model164", "AgentU"), "muhre164"),
    (("model164", "keyboard"), "wsbfz164"),
    (("model164", "AA"), "model164"),
    (("token164", "key"), "dsior164"),
    (("token164", "lemon"), "eswsa164"),
    (("token164", "a"), "token164"),
    (("token164", "zz"), "snjdm164"),
    (("token164", "AgentU"), "tuorg164"),
    (("token164", "keyboard"), "dsifb164"),
    (("token164", "AA"), "token164"),
    (("prompt164", "key"), "zvmwtr164"),
    (("prompt164", "lemon"), "avaace164"),
    (("prompt164", "a"), "prompt164"),
    (("prompt164", "zz"), "oqnlos164"),
    (("prompt164", "AgentU"), "pxszin164"),
    (("prompt164", "keyboard"), "zvmndt164"),
    (("prompt164", "AA"), "prompt164"),
    (("session164", "key"), "ciqcmmx164"),
    (("session164", "lemon"), "diegvzr164"),
    (("session164", "a"), "session164"),
    (("session164", "zz"), "rdrrhnm164"),
    (("session164", "AgentU"), "skwfbin164"),
    (("session164", "keyboard"), "ciqtwoe164"),
    (("session164", "AA"), "session164"),
    (("library164", "key"), "vmzbepi164"),
    (("library164", "lemon"), "wmnfncc164"),
    (("library164", "a"), "library164"),
    (("library164", "zz"), "khaqzqx164"),
    (("library164", "AgentU"), "lofetly164"),
    (("library164", "keyboard"), "vmzsorp164"),
    (("library164", "AA"), "library164"),
    (("service164", "key"), "cipfmao164"),
    (("service164", "lemon"), "didjvni164"),
    (("service164", "a"), "service164"),
    (("service164", "zz"), "rdquhbd164"),
    (("service164", "AgentU"), "skvibwe164"),
    (("service164", "keyboard"), "cipwwcv164"),
    (("service164", "AA"), "service164"),
    (("gateway164", "key"), "qeroayi164"),
    (("gateway164", "lemon"), "refsjlc164"),
    (("gateway164", "a"), "gateway164"),
    (("gateway164", "zz"), "fzsdvzx164"),
    (("gateway164", "AgentU"), "ggxrpuy164"),
    (("gateway164", "keyboard"), "qerfkap164"),
    (("gateway164", "AA"), "gateway164"),
    (("storage164", "key"), "cxmbeeo164"),
    (("storage164", "lemon"), "dxafnri164"),
    (("storage164", "a"), "storage164"),
    (("storage164", "zz"), "rsnqzfd164"),
    (("storage164", "AgentU"), "szsetae164"),
    (("storage164", "keyboard"), "cxmsogv164"),
    (("storage164", "AA"), "storage164"),
    (("network164", "key"), "xirgspu164"),
    (("network164", "lemon"), "yifkbco164"),
    (("network164", "a"), "network164"),
    (("network164", "zz"), "mdsvnqj164"),
    (("network164", "AgentU"), "nkxjhlk164"),
    (("network164", "keyboard"), "xirxcrb164"),
    (("network164", "AA"), "network164"),
    (("latency164", "key"), "verorai164"),
    (("latency164", "lemon"), "wefsanc164"),
    (("latency164", "a"), "latency164"),
    (("latency164", "zz"), "kzsdmbx164"),
    (("latency164", "AgentU"), "lgxrgwy164"),
    (("latency164", "keyboard"), "verfbcp164"),
    (("latency164", "AA"), "latency164"),
    (("buffer164", "key"), "lydpip164"),
    (("buffer164", "lemon"), "myrtrc164"),
    (("buffer164", "a"), "buffer164"),
    (("buffer164", "zz"), "ateedq164"),
    (("buffer164", "AgentU"), "bajsxl164"),
    (("buffer164", "keyboard"), "lydgsr164"),
    (("buffer164", "AA"), "buffer164"),
    (("queue164", "key"), "aycei164"),
    (("queue164", "lemon"), "byqir164"),
    (("queue164", "a"), "queue164"),
    (("queue164", "zz"), "ptdtd164"),
    (("queue164", "AgentU"), "qaihx164"),
    (("queue164", "keyboard"), "aycvs164"),
    (("queue164", "AA"), "queue164"),
    (("worker164", "key"), "gspuip164"),
    (("worker164", "lemon"), "hsdyrc164"),
    (("worker164", "a"), "worker164"),
    (("worker164", "zz"), "vnqjdq164"),
    (("worker164", "AgentU"), "wuvxxl164"),
    (("worker164", "keyboard"), "gsplsr164"),
    (("worker164", "AA"), "worker164"),
    (("kernel164", "key"), "uipxij164"),
    (("kernel164", "lemon"), "vidbrw164"),
    (("kernel164", "a"), "kernel164"),
    (("kernel164", "zz"), "jdqmdk164"),
    (("kernel164", "AgentU"), "kkvaxf164"),
    (("kernel164", "keyboard"), "uiposl164"),
    (("kernel164", "AA"), "kernel164"),
    (("signal164", "key"), "cmexej164"),
    (("signal164", "lemon"), "dmsbnw164"),
    (("signal164", "a"), "signal164"),
    (("signal164", "zz"), "rhfmzk164"),
    (("signal164", "AgentU"), "sokatf164"),
    (("signal164", "keyboard"), "cmeool164"),
    (("signal164", "AA"), "signal164"),
    (("packet164", "key"), "zeauir164"),
    (("packet164", "lemon"), "aeoyre164"),
    (("packet164", "a"), "packet164"),
    (("packet164", "zz"), "ozbjds164"),
    (("packet164", "AgentU"), "pggxxn164"),
    (("packet164", "keyboard"), "zealst164"),
    (("packet164", "AA"), "packet164"),
    (("router164", "key"), "bssdip164"),
    (("router164", "lemon"), "csghrc164"),
    (("router164", "a"), "router164"),
    (("router164", "zz"), "qntsdq164"),
    (("router164", "AgentU"), "ruygxl164"),
    (("router164", "keyboard"), "bssusr164"),
    (("router164", "AA"), "router164"),
    (("cluster164", "key"), "mpscxcb164"),
    (("cluster164", "lemon"), "npgggpv164"),
    (("cluster164", "a"), "cluster164"),
    (("cluster164", "zz"), "bktrsdq164"),
    (("cluster164", "AgentU"), "cryfmyr164"),
    (("cluster164", "keyboard"), "mpsthei164"),
    (("cluster164", "AA"), "cluster164"),
    (("mirror164", "key"), "wmpbsp164"),
    (("mirror164", "lemon"), "xmdfbc164"),
    (("mirror164", "a"), "mirror164"),
    (("mirror164", "zz"), "lhqqnq164"),
    (("mirror164", "AgentU"), "movehl164"),
    (("mirror164", "keyboard"), "wmpscr164"),
    (("mirror164", "AA"), "mirror164"),
    (("filter164", "key"), "pmjdip164"),
    (("filter164", "lemon"), "qmxhrc164"),
    (("filter164", "a"), "filter164"),
    (("filter164", "zz"), "ehksdq164"),
    (("filter164", "AgentU"), "fopgxl164"),
    (("filter164", "keyboard"), "pmjusr164"),
    (("filter164", "AA"), "filter164"),
    (("ranking164", "key"), "belumlq164"),
    (("ranking164", "lemon"), "cezyvyk164"),
    (("ranking164", "a"), "ranking164"),
    (("ranking164", "zz"), "qzmjhmf164"),
    (("ranking164", "AgentU"), "rgrxbhg164"),
    (("ranking164", "keyboard"), "bellwnx164"),
    (("ranking164", "AA"), "ranking164"),
    (("encoding164", "key"), "orayhgxk164"),
    (("encoding164", "lemon"), "procqtrs164"),
    (("encoding164", "a"), "encoding164"),
    (("encoding164", "zz"), "dmbnchmf164"),
    (("encoding164", "AgentU"), "etgbwcnm164"),
    (("encoding164", "keyboard"), "orapriej164"),
    (("encoding164", "AA"), "encoding164"),
    (("mapping164", "key"), "wenzmlq164"),
    (("mapping164", "lemon"), "xebdvyk164"),
    (("mapping164", "a"), "mapping164"),
    (("mapping164", "zz"), "lzoohmf164"),
    (("mapping164", "AgentU"), "mgtcbhg164"),
    (("mapping164", "keyboard"), "wenqwnx164"),
    (("mapping164", "AA"), "mapping164"),
    (("record164", "key"), "biayvb164"),
    (("record164", "lemon"), "cioceo164"),
    (("record164", "a"), "record164"),
    (("record164", "zz"), "qdbnqc164"),
    (("record164", "AgentU"), "rkgbkx164"),
    (("record164", "keyboard"), "biapfd164"),
    (("record164", "AA"), "record164"),
    (("candle164", "key"), "melnpc164"),
    (("candle164", "lemon"), "nezryp164"),
    (("candle164", "a"), "candle164"),
    (("candle164", "zz"), "bzmckd164"),
    (("candle164", "AgentU"), "cgrqey164"),
    (("candle164", "keyboard"), "meleze164"),
    (("candle164", "AA"), "candle164"),
    (("thread164", "key"), "dlpoeb164"),
    (("thread164", "lemon"), "eldsno164"),
    (("thread164", "a"), "thread164"),
    (("thread164", "zz"), "sgqdzc164"),
    (("thread164", "AgentU"), "tnvrtx164"),
    (("thread164", "keyboard"), "dlpfod164"),
    (("thread164", "AA"), "thread164"),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 164: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 164: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "a"),
        "round 164: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 164: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 164: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 164: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", "AA"),
        "round 164: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "key"),
        "bssxh 164: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 164: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "a"),
        "round 164: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 164: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 164: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 164: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", "AA"),
        "round 164: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 164: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 164: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "a"),
        "round 164: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 164: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 164: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 164: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", "AA"),
        "round 164: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 164: the processor reads the record then stops", "key"),
        "bssxh 164: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 164: the processor reads the record then stops", "lemon"),
        "csgbq 164: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 164: the processor reads the record then stops", "a"),
        "round 164: the processor reads the record then stops",
    ),
    (
        ("round 164: the processor reads the record then stops", "zz"),
        "qntmc 164: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 164: the processor reads the record then stops", "AgentU"),
        "ruyaw 164: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 164: the processor reads the record then stops", "keyboard"),
        "bssor 164: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 164: the processor reads the record then stops", "AA"),
        "round 164: the processor reads the record then stops",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "key"),
        "bssxh 164: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "lemon"),
        "csgbq 164: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "a"),
        "round 164: a worker pulls the next task from the queue",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "zz"),
        "qntmc 164: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 164: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "keyboard"),
        "bssor 164: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 164: a worker pulls the next task from the queue", "AA"),
        "round 164: a worker pulls the next task from the queue",
    ),
    (
        ("round 164: signals travel through the network layer", "key"),
        "bssxh 164: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 164: signals travel through the network layer", "lemon"),
        "csgbq 164: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 164: signals travel through the network layer", "a"),
        "round 164: signals travel through the network layer",
    ),
    (
        ("round 164: signals travel through the network layer", "zz"),
        "qntmc 164: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 164: signals travel through the network layer", "AgentU"),
        "ruyaw 164: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 164: signals travel through the network layer", "keyboard"),
        "bssor 164: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 164: signals travel through the network layer", "AA"),
        "round 164: signals travel through the network layer",
    ),
    (
        ("round 164: the gateway routes each request by policy", "key"),
        "bssxh 164: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 164: the gateway routes each request by policy", "lemon"),
        "csgbq 164: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 164: the gateway routes each request by policy", "a"),
        "round 164: the gateway routes each request by policy",
    ),
    (
        ("round 164: the gateway routes each request by policy", "zz"),
        "qntmc 164: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 164: the gateway routes each request by policy", "AgentU"),
        "ruyaw 164: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 164: the gateway routes each request by policy", "keyboard"),
        "bssor 164: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 164: the gateway routes each request by policy", "AA"),
        "round 164: the gateway routes each request by policy",
    ),
    (("round 164: memory grows until the buffer is full", "key"), "bssxh 164: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 164: memory grows until the buffer is full", "lemon"), "csgbq 164: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 164: memory grows until the buffer is full", "a"), "round 164: memory grows until the buffer is full"),
    (("round 164: memory grows until the buffer is full", "zz"), "qntmc 164: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 164: memory grows until the buffer is full", "AgentU"),
        "ruyaw 164: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 164: memory grows until the buffer is full", "keyboard"),
        "bssor 164: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 164: memory grows until the buffer is full", "AA"), "round 164: memory grows until the buffer is full"),
    (("round 164: the cluster mirrors every packet twice", "key"), "bssxh 164: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 164: the cluster mirrors every packet twice", "lemon"),
        "csgbq 164: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 164: the cluster mirrors every packet twice", "a"), "round 164: the cluster mirrors every packet twice"),
    (("round 164: the cluster mirrors every packet twice", "zz"), "qntmc 164: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 164: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 164: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 164: the cluster mirrors every packet twice", "keyboard"),
        "bssor 164: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 164: the cluster mirrors every packet twice", "AA"), "round 164: the cluster mirrors every packet twice"),
    (
        ("round 164: ranking uses tokens learned from the corpus", "key"),
        "bssxh 164: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 164: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", "a"),
        "round 164: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 164: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 164: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 164: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", "AA"),
        "round 164: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 164: a long session ends when the candle dies", "key"),
        "bssxh 164: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 164: a long session ends when the candle dies", "lemon"),
        "csgbq 164: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 164: a long session ends when the candle dies", "a"),
        "round 164: a long session ends when the candle dies",
    ),
    (
        ("round 164: a long session ends when the candle dies", "zz"),
        "qntmc 164: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 164: a long session ends when the candle dies", "AgentU"),
        "ruyaw 164: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 164: a long session ends when the candle dies", "keyboard"),
        "bssor 164: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 164: a long session ends when the candle dies", "AA"),
        "round 164: a long session ends when the candle dies",
    ),
    (("round 164: encode the prompt then map the result", "key"), "bssxh 164: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 164: encode the prompt then map the result", "lemon"), "csgbq 164: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 164: encode the prompt then map the result", "a"), "round 164: encode the prompt then map the result"),
    (("round 164: encode the prompt then map the result", "zz"), "qntmc 164: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 164: encode the prompt then map the result", "AgentU"),
        "ruyaw 164: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 164: encode the prompt then map the result", "keyboard"),
        "bssor 164: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 164: encode the prompt then map the result", "AA"), "round 164: encode the prompt then map the result"),
    (("round 164: the kernel wakes the worker at dawn", "key"), "bssxh 164: rri iovlop ukocc xfo ambocb er neux"),
    (("round 164: the kernel wakes the worker at dawn", "lemon"), "csgbq 164: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 164: the kernel wakes the worker at dawn", "a"), "round 164: the kernel wakes the worker at dawn"),
    (("round 164: the kernel wakes the worker at dawn", "zz"), "qntmc 164: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 164: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 164: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 164: the kernel wakes the worker at dawn", "keyboard"), "bssor 164: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 164: the kernel wakes the worker at dawn", "AA"), "round 164: the kernel wakes the worker at dawn"),
    (("round 164: service latency drops after the patch", "key"), "bssxh 164: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 164: service latency drops after the patch", "lemon"), "csgbq 164: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 164: service latency drops after the patch", "a"), "round 164: service latency drops after the patch"),
    (("round 164: service latency drops after the patch", "zz"), "qntmc 164: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 164: service latency drops after the patch", "AgentU"),
        "ruyaw 164: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 164: service latency drops after the patch", "keyboard"),
        "bssor 164: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 164: service latency drops after the patch", "AA"), "round 164: service latency drops after the patch"),
    (
        ("round 164: the library caches every vector it sees", "key"),
        "bssxh 164: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 164: the library caches every vector it sees", "lemon"),
        "csgbq 164: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 164: the library caches every vector it sees", "a"), "round 164: the library caches every vector it sees"),
    (
        ("round 164: the library caches every vector it sees", "zz"),
        "qntmc 164: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 164: the library caches every vector it sees", "AgentU"),
        "ruyaw 164: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 164: the library caches every vector it sees", "keyboard"),
        "bssor 164: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 164: the library caches every vector it sees", "AA"),
        "round 164: the library caches every vector it sees",
    ),
    (("round 164: agents argue then the debate resolves", "key"), "bssxh 164: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 164: agents argue then the debate resolves", "lemon"), "csgbq 164: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 164: agents argue then the debate resolves", "a"), "round 164: agents argue then the debate resolves"),
    (("round 164: agents argue then the debate resolves", "zz"), "qntmc 164: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 164: agents argue then the debate resolves", "AgentU"),
        "ruyaw 164: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 164: agents argue then the debate resolves", "keyboard"),
        "bssor 164: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 164: agents argue then the debate resolves", "AA"), "round 164: agents argue then the debate resolves"),
    (("round 164: the filter keeps only strong matches", "key"), "bssxh 164: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 164: the filter keeps only strong matches", "lemon"), "csgbq 164: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 164: the filter keeps only strong matches", "a"), "round 164: the filter keeps only strong matches"),
    (("round 164: the filter keeps only strong matches", "zz"), "qntmc 164: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 164: the filter keeps only strong matches", "AgentU"), "ruyaw 164: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 164: the filter keeps only strong matches", "keyboard"),
        "bssor 164: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 164: the filter keeps only strong matches", "AA"), "round 164: the filter keeps only strong matches"),
    (("round 164: the model answers with a short reply", "key"), "bssxh 164: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 164: the model answers with a short reply", "lemon"), "csgbq 164: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 164: the model answers with a short reply", "a"), "round 164: the model answers with a short reply"),
    (("round 164: the model answers with a short reply", "zz"), "qntmc 164: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 164: the model answers with a short reply", "AgentU"), "ruyaw 164: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 164: the model answers with a short reply", "keyboard"),
        "bssor 164: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 164: the model answers with a short reply", "AA"), "round 164: the model answers with a short reply"),
    (
        ("round 164: the recorder stores the reasoning trace", "key"),
        "bssxh 164: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 164: the recorder stores the reasoning trace", "lemon"),
        "csgbq 164: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 164: the recorder stores the reasoning trace", "a"), "round 164: the recorder stores the reasoning trace"),
    (
        ("round 164: the recorder stores the reasoning trace", "zz"),
        "qntmc 164: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 164: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 164: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 164: the recorder stores the reasoning trace", "keyboard"),
        "bssor 164: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 164: the recorder stores the reasoning trace", "AA"),
        "round 164: the recorder stores the reasoning trace",
    ),
    (("round 164: the angel watches the processor run", "key"), "bssxh 164: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 164: the angel watches the processor run", "lemon"), "csgbq 164: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 164: the angel watches the processor run", "a"), "round 164: the angel watches the processor run"),
    (("round 164: the angel watches the processor run", "zz"), "qntmc 164: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 164: the angel watches the processor run", "AgentU"), "ruyaw 164: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 164: the angel watches the processor run", "keyboard"), "bssor 164: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 164: the angel watches the processor run", "AA"), "round 164: the angel watches the processor run"),
    (("round 164: angle of the vector decides the match", "key"), "bssxh 164: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 164: angle of the vector decides the match", "lemon"), "csgbq 164: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 164: angle of the vector decides the match", "a"), "round 164: angle of the vector decides the match"),
    (("round 164: angle of the vector decides the match", "zz"), "qntmc 164: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 164: angle of the vector decides the match", "AgentU"),
        "ruyaw 164: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 164: angle of the vector decides the match", "keyboard"),
        "bssor 164: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 164: angle of the vector decides the match", "AA"), "round 164: angle of the vector decides the match"),
    (
        ("round 164: the candle burns twice as long at night", "key"),
        "bssxh 164: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 164: the candle burns twice as long at night", "lemon"),
        "csgbq 164: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 164: the candle burns twice as long at night", "a"), "round 164: the candle burns twice as long at night"),
    (
        ("round 164: the candle burns twice as long at night", "zz"),
        "qntmc 164: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 164: the candle burns twice as long at night", "AgentU"),
        "ruyaw 164: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 164: the candle burns twice as long at night", "keyboard"),
        "bssor 164: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 164: the candle burns twice as long at night", "AA"),
        "round 164: the candle burns twice as long at night",
    ),
    (("round 164: a mirror of the universe in one line", "key"), "bssxh 164: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 164: a mirror of the universe in one line", "lemon"), "csgbq 164: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 164: a mirror of the universe in one line", "a"), "round 164: a mirror of the universe in one line"),
    (("round 164: a mirror of the universe in one line", "zz"), "qntmc 164: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 164: a mirror of the universe in one line", "AgentU"), "ruyaw 164: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 164: a mirror of the universe in one line", "keyboard"),
        "bssor 164: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 164: a mirror of the universe in one line", "AA"), "round 164: a mirror of the universe in one line"),
    (("round 164: the queue drains before the storm", "key"), "bssxh 164: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 164: the queue drains before the storm", "lemon"), "csgbq 164: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 164: the queue drains before the storm", "a"), "round 164: the queue drains before the storm"),
    (("round 164: the queue drains before the storm", "zz"), "qntmc 164: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 164: the queue drains before the storm", "AgentU"), "ruyaw 164: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 164: the queue drains before the storm", "keyboard"), "bssor 164: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 164: the queue drains before the storm", "AA"), "round 164: the queue drains before the storm"),
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
