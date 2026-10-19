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
    (("kitten742", "key"), "umrdil742"),
    (("kitten742", "lemon"), "vmfhry742"),
    (("kitten742", "a"), "kitten742"),
    (("kitten742", "zz"), "jhssdm742"),
    (("kitten742", "AgentU"), "koxgxh742"),
    (("kitten742", "keyboard"), "umrusn742"),
    (("kitten742", "AA"), "kitten742"),
    (("sitting742", "key"), "cmrdmlq742"),
    (("sitting742", "lemon"), "dmfhvyk742"),
    (("sitting742", "a"), "sitting742"),
    (("sitting742", "zz"), "rhsshmf742"),
    (("sitting742", "AgentU"), "soxgbhg742"),
    (("sitting742", "keyboard"), "cmruwnx742"),
    (("sitting742", "AA"), "sitting742"),
    (("agent742", "key"), "kkcxx742"),
    (("agent742", "lemon"), "lkqbg742"),
    (("agent742", "a"), "agent742"),
    (("agent742", "zz"), "zfdms742"),
    (("agent742", "AgentU"), "amiam742"),
    (("agent742", "keyboard"), "kkcoh742"),
    (("agent742", "AA"), "agent742"),
    (("angle742", "key"), "krevi742"),
    (("angle742", "lemon"), "lrszr742"),
    (("angle742", "a"), "angle742"),
    (("angle742", "zz"), "zmfkd742"),
    (("angle742", "AgentU"), "atkyx742"),
    (("angle742", "keyboard"), "krems742"),
    (("angle742", "AA"), "angle742"),
    (("universe742", "key"), "ergfipci742"),
    (("universe742", "lemon"), "frujrcwq742"),
    (("universe742", "a"), "universe742"),
    (("universe742", "zz"), "tmhudqrd742"),
    (("universe742", "AgentU"), "utmixlsk742"),
    (("universe742", "keyboard"), "ergwsrjh742"),
    (("universe742", "AA"), "universe742"),
    (("memory742", "key"), "wikyvw742"),
    (("memory742", "lemon"), "xiycej742"),
    (("memory742", "a"), "memory742"),
    (("memory742", "zz"), "ldlnqx742"),
    (("memory742", "AgentU"), "mkqbks742"),
    (("memory742", "keyboard"), "wikpfy742"),
    (("memory742", "AA"), "memory742"),
    (("stream742", "key"), "cxpoek742"),
    (("stream742", "lemon"), "dxdsnx742"),
    (("stream742", "a"), "stream742"),
    (("stream742", "zz"), "rsqdzl742"),
    (("stream742", "AgentU"), "szvrtg742"),
    (("stream742", "keyboard"), "cxpfom742"),
    (("stream742", "AA"), "stream742"),
    (("context742", "key"), "msldivd742"),
    (("context742", "lemon"), "nszhrix742"),
    (("context742", "a"), "context742"),
    (("context742", "zz"), "bnmsdws742"),
    (("context742", "AgentU"), "curgxrt742"),
    (("context742", "keyboard"), "mslusxk742"),
    (("context742", "AA"), "context742"),
    (("knowledge742", "key"), "urmgpcnkc742"),
    (("knowledge742", "lemon"), "vrakyphss742"),
    (("knowledge742", "a"), "knowledge742"),
    (("knowledge742", "zz"), "jmnvkdcfd742"),
    (("knowledge742", "AgentU"), "ktsjeydmi742"),
    (("knowledge742", "keyboard"), "urmxzeujo742"),
    (("knowledge742", "AA"), "knowledge742"),
    (("vector742", "key"), "fiadsp742"),
    (("vector742", "lemon"), "giohbc742"),
    (("vector742", "a"), "vector742"),
    (("vector742", "zz"), "udbsnq742"),
    (("vector742", "AgentU"), "vkgghl742"),
    (("vector742", "keyboard"), "fiaucr742"),
    (("vector742", "AA"), "vector742"),
    (("processor742", "key"), "zvmmiqcsp742"),
    (("processor742", "lemon"), "avaqrdwaf742"),
    (("processor742", "a"), "processor742"),
    (("processor742", "zz"), "oqnbdrrnq742"),
    (("processor742", "AgentU"), "pxspxmsuv742"),
    (("processor742", "keyboard"), "zvmdssjrb742"),
    (("processor742", "AA"), "processor742"),
    (("reasoning742", "key"), "biycslsre742"),
    (("reasoning742", "lemon"), "cimgbymzu742"),
    (("reasoning742", "a"), "reasoning742"),
    (("reasoning742", "zz"), "qdzrnmhmf742"),
    (("reasoning742", "AgentU"), "rkefhhitk742"),
    (("reasoning742", "keyboard"), "biytcnzqq742"),
    (("reasoning742", "AA"), "reasoning742"),
    (("machine742", "key"), "wearmlo742"),
    (("machine742", "lemon"), "xeovvyi742"),
    (("machine742", "a"), "machine742"),
    (("machine742", "zz"), "lzbghmd742"),
    (("machine742", "AgentU"), "mggubhe742"),
    (("machine742", "keyboard"), "weaiwnv742"),
    (("machine742", "AA"), "machine742"),
    (("learning742", "key"), "viybrgxk742"),
    (("learning742", "lemon"), "wimfatrs742"),
    (("learning742", "a"), "learning742"),
    (("learning742", "zz"), "kdzqmhmf742"),
    (("learning742", "AgentU"), "lkeegcnm742"),
    (("learning742", "keyboard"), "viysbiej742"),
    (("learning742", "AA"), "learning742"),
    (("model742", "key"), "wsbop742"),
    (("model742", "lemon"), "xspsy742"),
    (("model742", "a"), "model742"),
    (("model742", "zz"), "lncdk742"),
    (("model742", "AgentU"), "muhre742"),
    (("model742", "keyboard"), "wsbfz742"),
    (("model742", "AA"), "model742"),
    (("token742", "key"), "dsior742"),
    (("token742", "lemon"), "eswsa742"),
    (("token742", "a"), "token742"),
    (("token742", "zz"), "snjdm742"),
    (("token742", "AgentU"), "tuorg742"),
    (("token742", "keyboard"), "dsifb742"),
    (("token742", "AA"), "token742"),
    (("prompt742", "key"), "zvmwtr742"),
    (("prompt742", "lemon"), "avaace742"),
    (("prompt742", "a"), "prompt742"),
    (("prompt742", "zz"), "oqnlos742"),
    (("prompt742", "AgentU"), "pxszin742"),
    (("prompt742", "keyboard"), "zvmndt742"),
    (("prompt742", "AA"), "prompt742"),
    (("session742", "key"), "ciqcmmx742"),
    (("session742", "lemon"), "diegvzr742"),
    (("session742", "a"), "session742"),
    (("session742", "zz"), "rdrrhnm742"),
    (("session742", "AgentU"), "skwfbin742"),
    (("session742", "keyboard"), "ciqtwoe742"),
    (("session742", "AA"), "session742"),
    (("library742", "key"), "vmzbepi742"),
    (("library742", "lemon"), "wmnfncc742"),
    (("library742", "a"), "library742"),
    (("library742", "zz"), "khaqzqx742"),
    (("library742", "AgentU"), "lofetly742"),
    (("library742", "keyboard"), "vmzsorp742"),
    (("library742", "AA"), "library742"),
    (("service742", "key"), "cipfmao742"),
    (("service742", "lemon"), "didjvni742"),
    (("service742", "a"), "service742"),
    (("service742", "zz"), "rdquhbd742"),
    (("service742", "AgentU"), "skvibwe742"),
    (("service742", "keyboard"), "cipwwcv742"),
    (("service742", "AA"), "service742"),
    (("gateway742", "key"), "qeroayi742"),
    (("gateway742", "lemon"), "refsjlc742"),
    (("gateway742", "a"), "gateway742"),
    (("gateway742", "zz"), "fzsdvzx742"),
    (("gateway742", "AgentU"), "ggxrpuy742"),
    (("gateway742", "keyboard"), "qerfkap742"),
    (("gateway742", "AA"), "gateway742"),
    (("storage742", "key"), "cxmbeeo742"),
    (("storage742", "lemon"), "dxafnri742"),
    (("storage742", "a"), "storage742"),
    (("storage742", "zz"), "rsnqzfd742"),
    (("storage742", "AgentU"), "szsetae742"),
    (("storage742", "keyboard"), "cxmsogv742"),
    (("storage742", "AA"), "storage742"),
    (("network742", "key"), "xirgspu742"),
    (("network742", "lemon"), "yifkbco742"),
    (("network742", "a"), "network742"),
    (("network742", "zz"), "mdsvnqj742"),
    (("network742", "AgentU"), "nkxjhlk742"),
    (("network742", "keyboard"), "xirxcrb742"),
    (("network742", "AA"), "network742"),
    (("latency742", "key"), "verorai742"),
    (("latency742", "lemon"), "wefsanc742"),
    (("latency742", "a"), "latency742"),
    (("latency742", "zz"), "kzsdmbx742"),
    (("latency742", "AgentU"), "lgxrgwy742"),
    (("latency742", "keyboard"), "verfbcp742"),
    (("latency742", "AA"), "latency742"),
    (("buffer742", "key"), "lydpip742"),
    (("buffer742", "lemon"), "myrtrc742"),
    (("buffer742", "a"), "buffer742"),
    (("buffer742", "zz"), "ateedq742"),
    (("buffer742", "AgentU"), "bajsxl742"),
    (("buffer742", "keyboard"), "lydgsr742"),
    (("buffer742", "AA"), "buffer742"),
    (("queue742", "key"), "aycei742"),
    (("queue742", "lemon"), "byqir742"),
    (("queue742", "a"), "queue742"),
    (("queue742", "zz"), "ptdtd742"),
    (("queue742", "AgentU"), "qaihx742"),
    (("queue742", "keyboard"), "aycvs742"),
    (("queue742", "AA"), "queue742"),
    (("worker742", "key"), "gspuip742"),
    (("worker742", "lemon"), "hsdyrc742"),
    (("worker742", "a"), "worker742"),
    (("worker742", "zz"), "vnqjdq742"),
    (("worker742", "AgentU"), "wuvxxl742"),
    (("worker742", "keyboard"), "gsplsr742"),
    (("worker742", "AA"), "worker742"),
    (("kernel742", "key"), "uipxij742"),
    (("kernel742", "lemon"), "vidbrw742"),
    (("kernel742", "a"), "kernel742"),
    (("kernel742", "zz"), "jdqmdk742"),
    (("kernel742", "AgentU"), "kkvaxf742"),
    (("kernel742", "keyboard"), "uiposl742"),
    (("kernel742", "AA"), "kernel742"),
    (("signal742", "key"), "cmexej742"),
    (("signal742", "lemon"), "dmsbnw742"),
    (("signal742", "a"), "signal742"),
    (("signal742", "zz"), "rhfmzk742"),
    (("signal742", "AgentU"), "sokatf742"),
    (("signal742", "keyboard"), "cmeool742"),
    (("signal742", "AA"), "signal742"),
    (("packet742", "key"), "zeauir742"),
    (("packet742", "lemon"), "aeoyre742"),
    (("packet742", "a"), "packet742"),
    (("packet742", "zz"), "ozbjds742"),
    (("packet742", "AgentU"), "pggxxn742"),
    (("packet742", "keyboard"), "zealst742"),
    (("packet742", "AA"), "packet742"),
    (("router742", "key"), "bssdip742"),
    (("router742", "lemon"), "csghrc742"),
    (("router742", "a"), "router742"),
    (("router742", "zz"), "qntsdq742"),
    (("router742", "AgentU"), "ruygxl742"),
    (("router742", "keyboard"), "bssusr742"),
    (("router742", "AA"), "router742"),
    (("cluster742", "key"), "mpscxcb742"),
    (("cluster742", "lemon"), "npgggpv742"),
    (("cluster742", "a"), "cluster742"),
    (("cluster742", "zz"), "bktrsdq742"),
    (("cluster742", "AgentU"), "cryfmyr742"),
    (("cluster742", "keyboard"), "mpsthei742"),
    (("cluster742", "AA"), "cluster742"),
    (("mirror742", "key"), "wmpbsp742"),
    (("mirror742", "lemon"), "xmdfbc742"),
    (("mirror742", "a"), "mirror742"),
    (("mirror742", "zz"), "lhqqnq742"),
    (("mirror742", "AgentU"), "movehl742"),
    (("mirror742", "keyboard"), "wmpscr742"),
    (("mirror742", "AA"), "mirror742"),
    (("filter742", "key"), "pmjdip742"),
    (("filter742", "lemon"), "qmxhrc742"),
    (("filter742", "a"), "filter742"),
    (("filter742", "zz"), "ehksdq742"),
    (("filter742", "AgentU"), "fopgxl742"),
    (("filter742", "keyboard"), "pmjusr742"),
    (("filter742", "AA"), "filter742"),
    (("ranking742", "key"), "belumlq742"),
    (("ranking742", "lemon"), "cezyvyk742"),
    (("ranking742", "a"), "ranking742"),
    (("ranking742", "zz"), "qzmjhmf742"),
    (("ranking742", "AgentU"), "rgrxbhg742"),
    (("ranking742", "keyboard"), "bellwnx742"),
    (("ranking742", "AA"), "ranking742"),
    (("encoding742", "key"), "orayhgxk742"),
    (("encoding742", "lemon"), "procqtrs742"),
    (("encoding742", "a"), "encoding742"),
    (("encoding742", "zz"), "dmbnchmf742"),
    (("encoding742", "AgentU"), "etgbwcnm742"),
    (("encoding742", "keyboard"), "orapriej742"),
    (("encoding742", "AA"), "encoding742"),
    (("mapping742", "key"), "wenzmlq742"),
    (("mapping742", "lemon"), "xebdvyk742"),
    (("mapping742", "a"), "mapping742"),
    (("mapping742", "zz"), "lzoohmf742"),
    (("mapping742", "AgentU"), "mgtcbhg742"),
    (("mapping742", "keyboard"), "wenqwnx742"),
    (("mapping742", "AA"), "mapping742"),
    (("record742", "key"), "biayvb742"),
    (("record742", "lemon"), "cioceo742"),
    (("record742", "a"), "record742"),
    (("record742", "zz"), "qdbnqc742"),
    (("record742", "AgentU"), "rkgbkx742"),
    (("record742", "keyboard"), "biapfd742"),
    (("record742", "AA"), "record742"),
    (("candle742", "key"), "melnpc742"),
    (("candle742", "lemon"), "nezryp742"),
    (("candle742", "a"), "candle742"),
    (("candle742", "zz"), "bzmckd742"),
    (("candle742", "AgentU"), "cgrqey742"),
    (("candle742", "keyboard"), "meleze742"),
    (("candle742", "AA"), "candle742"),
    (("thread742", "key"), "dlpoeb742"),
    (("thread742", "lemon"), "eldsno742"),
    (("thread742", "a"), "thread742"),
    (("thread742", "zz"), "sgqdzc742"),
    (("thread742", "AgentU"), "tnvrtx742"),
    (("thread742", "keyboard"), "dlpfod742"),
    (("thread742", "AA"), "thread742"),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 742: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 742: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "a"),
        "round 742: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 742: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 742: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 742: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", "AA"),
        "round 742: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "key"),
        "bssxh 742: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 742: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "a"),
        "round 742: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 742: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 742: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 742: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", "AA"),
        "round 742: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 742: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 742: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "a"),
        "round 742: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 742: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 742: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 742: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", "AA"),
        "round 742: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 742: the processor reads the record then stops", "key"),
        "bssxh 742: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 742: the processor reads the record then stops", "lemon"),
        "csgbq 742: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 742: the processor reads the record then stops", "a"),
        "round 742: the processor reads the record then stops",
    ),
    (
        ("round 742: the processor reads the record then stops", "zz"),
        "qntmc 742: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 742: the processor reads the record then stops", "AgentU"),
        "ruyaw 742: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 742: the processor reads the record then stops", "keyboard"),
        "bssor 742: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 742: the processor reads the record then stops", "AA"),
        "round 742: the processor reads the record then stops",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "key"),
        "bssxh 742: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "lemon"),
        "csgbq 742: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "a"),
        "round 742: a worker pulls the next task from the queue",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "zz"),
        "qntmc 742: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 742: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "keyboard"),
        "bssor 742: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 742: a worker pulls the next task from the queue", "AA"),
        "round 742: a worker pulls the next task from the queue",
    ),
    (
        ("round 742: signals travel through the network layer", "key"),
        "bssxh 742: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 742: signals travel through the network layer", "lemon"),
        "csgbq 742: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 742: signals travel through the network layer", "a"),
        "round 742: signals travel through the network layer",
    ),
    (
        ("round 742: signals travel through the network layer", "zz"),
        "qntmc 742: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 742: signals travel through the network layer", "AgentU"),
        "ruyaw 742: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 742: signals travel through the network layer", "keyboard"),
        "bssor 742: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 742: signals travel through the network layer", "AA"),
        "round 742: signals travel through the network layer",
    ),
    (
        ("round 742: the gateway routes each request by policy", "key"),
        "bssxh 742: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 742: the gateway routes each request by policy", "lemon"),
        "csgbq 742: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 742: the gateway routes each request by policy", "a"),
        "round 742: the gateway routes each request by policy",
    ),
    (
        ("round 742: the gateway routes each request by policy", "zz"),
        "qntmc 742: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 742: the gateway routes each request by policy", "AgentU"),
        "ruyaw 742: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 742: the gateway routes each request by policy", "keyboard"),
        "bssor 742: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 742: the gateway routes each request by policy", "AA"),
        "round 742: the gateway routes each request by policy",
    ),
    (("round 742: memory grows until the buffer is full", "key"), "bssxh 742: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 742: memory grows until the buffer is full", "lemon"), "csgbq 742: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 742: memory grows until the buffer is full", "a"), "round 742: memory grows until the buffer is full"),
    (("round 742: memory grows until the buffer is full", "zz"), "qntmc 742: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 742: memory grows until the buffer is full", "AgentU"),
        "ruyaw 742: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 742: memory grows until the buffer is full", "keyboard"),
        "bssor 742: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 742: memory grows until the buffer is full", "AA"), "round 742: memory grows until the buffer is full"),
    (("round 742: the cluster mirrors every packet twice", "key"), "bssxh 742: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 742: the cluster mirrors every packet twice", "lemon"),
        "csgbq 742: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 742: the cluster mirrors every packet twice", "a"), "round 742: the cluster mirrors every packet twice"),
    (("round 742: the cluster mirrors every packet twice", "zz"), "qntmc 742: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 742: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 742: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 742: the cluster mirrors every packet twice", "keyboard"),
        "bssor 742: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 742: the cluster mirrors every packet twice", "AA"), "round 742: the cluster mirrors every packet twice"),
    (
        ("round 742: ranking uses tokens learned from the corpus", "key"),
        "bssxh 742: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 742: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", "a"),
        "round 742: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 742: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 742: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 742: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", "AA"),
        "round 742: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 742: a long session ends when the candle dies", "key"),
        "bssxh 742: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 742: a long session ends when the candle dies", "lemon"),
        "csgbq 742: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 742: a long session ends when the candle dies", "a"),
        "round 742: a long session ends when the candle dies",
    ),
    (
        ("round 742: a long session ends when the candle dies", "zz"),
        "qntmc 742: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 742: a long session ends when the candle dies", "AgentU"),
        "ruyaw 742: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 742: a long session ends when the candle dies", "keyboard"),
        "bssor 742: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 742: a long session ends when the candle dies", "AA"),
        "round 742: a long session ends when the candle dies",
    ),
    (("round 742: encode the prompt then map the result", "key"), "bssxh 742: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 742: encode the prompt then map the result", "lemon"), "csgbq 742: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 742: encode the prompt then map the result", "a"), "round 742: encode the prompt then map the result"),
    (("round 742: encode the prompt then map the result", "zz"), "qntmc 742: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 742: encode the prompt then map the result", "AgentU"),
        "ruyaw 742: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 742: encode the prompt then map the result", "keyboard"),
        "bssor 742: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 742: encode the prompt then map the result", "AA"), "round 742: encode the prompt then map the result"),
    (("round 742: the kernel wakes the worker at dawn", "key"), "bssxh 742: rri iovlop ukocc xfo ambocb er neux"),
    (("round 742: the kernel wakes the worker at dawn", "lemon"), "csgbq 742: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 742: the kernel wakes the worker at dawn", "a"), "round 742: the kernel wakes the worker at dawn"),
    (("round 742: the kernel wakes the worker at dawn", "zz"), "qntmc 742: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 742: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 742: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 742: the kernel wakes the worker at dawn", "keyboard"), "bssor 742: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 742: the kernel wakes the worker at dawn", "AA"), "round 742: the kernel wakes the worker at dawn"),
    (("round 742: service latency drops after the patch", "key"), "bssxh 742: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 742: service latency drops after the patch", "lemon"), "csgbq 742: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 742: service latency drops after the patch", "a"), "round 742: service latency drops after the patch"),
    (("round 742: service latency drops after the patch", "zz"), "qntmc 742: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 742: service latency drops after the patch", "AgentU"),
        "ruyaw 742: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 742: service latency drops after the patch", "keyboard"),
        "bssor 742: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 742: service latency drops after the patch", "AA"), "round 742: service latency drops after the patch"),
    (
        ("round 742: the library caches every vector it sees", "key"),
        "bssxh 742: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 742: the library caches every vector it sees", "lemon"),
        "csgbq 742: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 742: the library caches every vector it sees", "a"), "round 742: the library caches every vector it sees"),
    (
        ("round 742: the library caches every vector it sees", "zz"),
        "qntmc 742: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 742: the library caches every vector it sees", "AgentU"),
        "ruyaw 742: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 742: the library caches every vector it sees", "keyboard"),
        "bssor 742: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 742: the library caches every vector it sees", "AA"),
        "round 742: the library caches every vector it sees",
    ),
    (("round 742: agents argue then the debate resolves", "key"), "bssxh 742: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 742: agents argue then the debate resolves", "lemon"), "csgbq 742: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 742: agents argue then the debate resolves", "a"), "round 742: agents argue then the debate resolves"),
    (("round 742: agents argue then the debate resolves", "zz"), "qntmc 742: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 742: agents argue then the debate resolves", "AgentU"),
        "ruyaw 742: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 742: agents argue then the debate resolves", "keyboard"),
        "bssor 742: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 742: agents argue then the debate resolves", "AA"), "round 742: agents argue then the debate resolves"),
    (("round 742: the filter keeps only strong matches", "key"), "bssxh 742: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 742: the filter keeps only strong matches", "lemon"), "csgbq 742: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 742: the filter keeps only strong matches", "a"), "round 742: the filter keeps only strong matches"),
    (("round 742: the filter keeps only strong matches", "zz"), "qntmc 742: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 742: the filter keeps only strong matches", "AgentU"), "ruyaw 742: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 742: the filter keeps only strong matches", "keyboard"),
        "bssor 742: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 742: the filter keeps only strong matches", "AA"), "round 742: the filter keeps only strong matches"),
    (("round 742: the model answers with a short reply", "key"), "bssxh 742: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 742: the model answers with a short reply", "lemon"), "csgbq 742: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 742: the model answers with a short reply", "a"), "round 742: the model answers with a short reply"),
    (("round 742: the model answers with a short reply", "zz"), "qntmc 742: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 742: the model answers with a short reply", "AgentU"), "ruyaw 742: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 742: the model answers with a short reply", "keyboard"),
        "bssor 742: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 742: the model answers with a short reply", "AA"), "round 742: the model answers with a short reply"),
    (
        ("round 742: the recorder stores the reasoning trace", "key"),
        "bssxh 742: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 742: the recorder stores the reasoning trace", "lemon"),
        "csgbq 742: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 742: the recorder stores the reasoning trace", "a"), "round 742: the recorder stores the reasoning trace"),
    (
        ("round 742: the recorder stores the reasoning trace", "zz"),
        "qntmc 742: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 742: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 742: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 742: the recorder stores the reasoning trace", "keyboard"),
        "bssor 742: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 742: the recorder stores the reasoning trace", "AA"),
        "round 742: the recorder stores the reasoning trace",
    ),
    (("round 742: the angel watches the processor run", "key"), "bssxh 742: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 742: the angel watches the processor run", "lemon"), "csgbq 742: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 742: the angel watches the processor run", "a"), "round 742: the angel watches the processor run"),
    (("round 742: the angel watches the processor run", "zz"), "qntmc 742: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 742: the angel watches the processor run", "AgentU"), "ruyaw 742: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 742: the angel watches the processor run", "keyboard"), "bssor 742: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 742: the angel watches the processor run", "AA"), "round 742: the angel watches the processor run"),
    (("round 742: angle of the vector decides the match", "key"), "bssxh 742: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 742: angle of the vector decides the match", "lemon"), "csgbq 742: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 742: angle of the vector decides the match", "a"), "round 742: angle of the vector decides the match"),
    (("round 742: angle of the vector decides the match", "zz"), "qntmc 742: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 742: angle of the vector decides the match", "AgentU"),
        "ruyaw 742: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 742: angle of the vector decides the match", "keyboard"),
        "bssor 742: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 742: angle of the vector decides the match", "AA"), "round 742: angle of the vector decides the match"),
    (
        ("round 742: the candle burns twice as long at night", "key"),
        "bssxh 742: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 742: the candle burns twice as long at night", "lemon"),
        "csgbq 742: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 742: the candle burns twice as long at night", "a"), "round 742: the candle burns twice as long at night"),
    (
        ("round 742: the candle burns twice as long at night", "zz"),
        "qntmc 742: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 742: the candle burns twice as long at night", "AgentU"),
        "ruyaw 742: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 742: the candle burns twice as long at night", "keyboard"),
        "bssor 742: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 742: the candle burns twice as long at night", "AA"),
        "round 742: the candle burns twice as long at night",
    ),
    (("round 742: a mirror of the universe in one line", "key"), "bssxh 742: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 742: a mirror of the universe in one line", "lemon"), "csgbq 742: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 742: a mirror of the universe in one line", "a"), "round 742: a mirror of the universe in one line"),
    (("round 742: a mirror of the universe in one line", "zz"), "qntmc 742: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 742: a mirror of the universe in one line", "AgentU"), "ruyaw 742: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 742: a mirror of the universe in one line", "keyboard"),
        "bssor 742: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 742: a mirror of the universe in one line", "AA"), "round 742: a mirror of the universe in one line"),
    (("round 742: the queue drains before the storm", "key"), "bssxh 742: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 742: the queue drains before the storm", "lemon"), "csgbq 742: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 742: the queue drains before the storm", "a"), "round 742: the queue drains before the storm"),
    (("round 742: the queue drains before the storm", "zz"), "qntmc 742: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 742: the queue drains before the storm", "AgentU"), "ruyaw 742: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 742: the queue drains before the storm", "keyboard"), "bssor 742: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 742: the queue drains before the storm", "AA"), "round 742: the queue drains before the storm"),
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
