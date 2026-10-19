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
    (("kitten134", "key"), "umrdil134"),
    (("kitten134", "lemon"), "vmfhry134"),
    (("kitten134", "a"), "kitten134"),
    (("kitten134", "zz"), "jhssdm134"),
    (("kitten134", "AgentU"), "koxgxh134"),
    (("kitten134", "keyboard"), "umrusn134"),
    (("kitten134", "AA"), "kitten134"),
    (("sitting134", "key"), "cmrdmlq134"),
    (("sitting134", "lemon"), "dmfhvyk134"),
    (("sitting134", "a"), "sitting134"),
    (("sitting134", "zz"), "rhsshmf134"),
    (("sitting134", "AgentU"), "soxgbhg134"),
    (("sitting134", "keyboard"), "cmruwnx134"),
    (("sitting134", "AA"), "sitting134"),
    (("agent134", "key"), "kkcxx134"),
    (("agent134", "lemon"), "lkqbg134"),
    (("agent134", "a"), "agent134"),
    (("agent134", "zz"), "zfdms134"),
    (("agent134", "AgentU"), "amiam134"),
    (("agent134", "keyboard"), "kkcoh134"),
    (("agent134", "AA"), "agent134"),
    (("angle134", "key"), "krevi134"),
    (("angle134", "lemon"), "lrszr134"),
    (("angle134", "a"), "angle134"),
    (("angle134", "zz"), "zmfkd134"),
    (("angle134", "AgentU"), "atkyx134"),
    (("angle134", "keyboard"), "krems134"),
    (("angle134", "AA"), "angle134"),
    (("universe134", "key"), "ergfipci134"),
    (("universe134", "lemon"), "frujrcwq134"),
    (("universe134", "a"), "universe134"),
    (("universe134", "zz"), "tmhudqrd134"),
    (("universe134", "AgentU"), "utmixlsk134"),
    (("universe134", "keyboard"), "ergwsrjh134"),
    (("universe134", "AA"), "universe134"),
    (("memory134", "key"), "wikyvw134"),
    (("memory134", "lemon"), "xiycej134"),
    (("memory134", "a"), "memory134"),
    (("memory134", "zz"), "ldlnqx134"),
    (("memory134", "AgentU"), "mkqbks134"),
    (("memory134", "keyboard"), "wikpfy134"),
    (("memory134", "AA"), "memory134"),
    (("stream134", "key"), "cxpoek134"),
    (("stream134", "lemon"), "dxdsnx134"),
    (("stream134", "a"), "stream134"),
    (("stream134", "zz"), "rsqdzl134"),
    (("stream134", "AgentU"), "szvrtg134"),
    (("stream134", "keyboard"), "cxpfom134"),
    (("stream134", "AA"), "stream134"),
    (("context134", "key"), "msldivd134"),
    (("context134", "lemon"), "nszhrix134"),
    (("context134", "a"), "context134"),
    (("context134", "zz"), "bnmsdws134"),
    (("context134", "AgentU"), "curgxrt134"),
    (("context134", "keyboard"), "mslusxk134"),
    (("context134", "AA"), "context134"),
    (("knowledge134", "key"), "urmgpcnkc134"),
    (("knowledge134", "lemon"), "vrakyphss134"),
    (("knowledge134", "a"), "knowledge134"),
    (("knowledge134", "zz"), "jmnvkdcfd134"),
    (("knowledge134", "AgentU"), "ktsjeydmi134"),
    (("knowledge134", "keyboard"), "urmxzeujo134"),
    (("knowledge134", "AA"), "knowledge134"),
    (("vector134", "key"), "fiadsp134"),
    (("vector134", "lemon"), "giohbc134"),
    (("vector134", "a"), "vector134"),
    (("vector134", "zz"), "udbsnq134"),
    (("vector134", "AgentU"), "vkgghl134"),
    (("vector134", "keyboard"), "fiaucr134"),
    (("vector134", "AA"), "vector134"),
    (("processor134", "key"), "zvmmiqcsp134"),
    (("processor134", "lemon"), "avaqrdwaf134"),
    (("processor134", "a"), "processor134"),
    (("processor134", "zz"), "oqnbdrrnq134"),
    (("processor134", "AgentU"), "pxspxmsuv134"),
    (("processor134", "keyboard"), "zvmdssjrb134"),
    (("processor134", "AA"), "processor134"),
    (("reasoning134", "key"), "biycslsre134"),
    (("reasoning134", "lemon"), "cimgbymzu134"),
    (("reasoning134", "a"), "reasoning134"),
    (("reasoning134", "zz"), "qdzrnmhmf134"),
    (("reasoning134", "AgentU"), "rkefhhitk134"),
    (("reasoning134", "keyboard"), "biytcnzqq134"),
    (("reasoning134", "AA"), "reasoning134"),
    (("machine134", "key"), "wearmlo134"),
    (("machine134", "lemon"), "xeovvyi134"),
    (("machine134", "a"), "machine134"),
    (("machine134", "zz"), "lzbghmd134"),
    (("machine134", "AgentU"), "mggubhe134"),
    (("machine134", "keyboard"), "weaiwnv134"),
    (("machine134", "AA"), "machine134"),
    (("learning134", "key"), "viybrgxk134"),
    (("learning134", "lemon"), "wimfatrs134"),
    (("learning134", "a"), "learning134"),
    (("learning134", "zz"), "kdzqmhmf134"),
    (("learning134", "AgentU"), "lkeegcnm134"),
    (("learning134", "keyboard"), "viysbiej134"),
    (("learning134", "AA"), "learning134"),
    (("model134", "key"), "wsbop134"),
    (("model134", "lemon"), "xspsy134"),
    (("model134", "a"), "model134"),
    (("model134", "zz"), "lncdk134"),
    (("model134", "AgentU"), "muhre134"),
    (("model134", "keyboard"), "wsbfz134"),
    (("model134", "AA"), "model134"),
    (("token134", "key"), "dsior134"),
    (("token134", "lemon"), "eswsa134"),
    (("token134", "a"), "token134"),
    (("token134", "zz"), "snjdm134"),
    (("token134", "AgentU"), "tuorg134"),
    (("token134", "keyboard"), "dsifb134"),
    (("token134", "AA"), "token134"),
    (("prompt134", "key"), "zvmwtr134"),
    (("prompt134", "lemon"), "avaace134"),
    (("prompt134", "a"), "prompt134"),
    (("prompt134", "zz"), "oqnlos134"),
    (("prompt134", "AgentU"), "pxszin134"),
    (("prompt134", "keyboard"), "zvmndt134"),
    (("prompt134", "AA"), "prompt134"),
    (("session134", "key"), "ciqcmmx134"),
    (("session134", "lemon"), "diegvzr134"),
    (("session134", "a"), "session134"),
    (("session134", "zz"), "rdrrhnm134"),
    (("session134", "AgentU"), "skwfbin134"),
    (("session134", "keyboard"), "ciqtwoe134"),
    (("session134", "AA"), "session134"),
    (("library134", "key"), "vmzbepi134"),
    (("library134", "lemon"), "wmnfncc134"),
    (("library134", "a"), "library134"),
    (("library134", "zz"), "khaqzqx134"),
    (("library134", "AgentU"), "lofetly134"),
    (("library134", "keyboard"), "vmzsorp134"),
    (("library134", "AA"), "library134"),
    (("service134", "key"), "cipfmao134"),
    (("service134", "lemon"), "didjvni134"),
    (("service134", "a"), "service134"),
    (("service134", "zz"), "rdquhbd134"),
    (("service134", "AgentU"), "skvibwe134"),
    (("service134", "keyboard"), "cipwwcv134"),
    (("service134", "AA"), "service134"),
    (("gateway134", "key"), "qeroayi134"),
    (("gateway134", "lemon"), "refsjlc134"),
    (("gateway134", "a"), "gateway134"),
    (("gateway134", "zz"), "fzsdvzx134"),
    (("gateway134", "AgentU"), "ggxrpuy134"),
    (("gateway134", "keyboard"), "qerfkap134"),
    (("gateway134", "AA"), "gateway134"),
    (("storage134", "key"), "cxmbeeo134"),
    (("storage134", "lemon"), "dxafnri134"),
    (("storage134", "a"), "storage134"),
    (("storage134", "zz"), "rsnqzfd134"),
    (("storage134", "AgentU"), "szsetae134"),
    (("storage134", "keyboard"), "cxmsogv134"),
    (("storage134", "AA"), "storage134"),
    (("network134", "key"), "xirgspu134"),
    (("network134", "lemon"), "yifkbco134"),
    (("network134", "a"), "network134"),
    (("network134", "zz"), "mdsvnqj134"),
    (("network134", "AgentU"), "nkxjhlk134"),
    (("network134", "keyboard"), "xirxcrb134"),
    (("network134", "AA"), "network134"),
    (("latency134", "key"), "verorai134"),
    (("latency134", "lemon"), "wefsanc134"),
    (("latency134", "a"), "latency134"),
    (("latency134", "zz"), "kzsdmbx134"),
    (("latency134", "AgentU"), "lgxrgwy134"),
    (("latency134", "keyboard"), "verfbcp134"),
    (("latency134", "AA"), "latency134"),
    (("buffer134", "key"), "lydpip134"),
    (("buffer134", "lemon"), "myrtrc134"),
    (("buffer134", "a"), "buffer134"),
    (("buffer134", "zz"), "ateedq134"),
    (("buffer134", "AgentU"), "bajsxl134"),
    (("buffer134", "keyboard"), "lydgsr134"),
    (("buffer134", "AA"), "buffer134"),
    (("queue134", "key"), "aycei134"),
    (("queue134", "lemon"), "byqir134"),
    (("queue134", "a"), "queue134"),
    (("queue134", "zz"), "ptdtd134"),
    (("queue134", "AgentU"), "qaihx134"),
    (("queue134", "keyboard"), "aycvs134"),
    (("queue134", "AA"), "queue134"),
    (("worker134", "key"), "gspuip134"),
    (("worker134", "lemon"), "hsdyrc134"),
    (("worker134", "a"), "worker134"),
    (("worker134", "zz"), "vnqjdq134"),
    (("worker134", "AgentU"), "wuvxxl134"),
    (("worker134", "keyboard"), "gsplsr134"),
    (("worker134", "AA"), "worker134"),
    (("kernel134", "key"), "uipxij134"),
    (("kernel134", "lemon"), "vidbrw134"),
    (("kernel134", "a"), "kernel134"),
    (("kernel134", "zz"), "jdqmdk134"),
    (("kernel134", "AgentU"), "kkvaxf134"),
    (("kernel134", "keyboard"), "uiposl134"),
    (("kernel134", "AA"), "kernel134"),
    (("signal134", "key"), "cmexej134"),
    (("signal134", "lemon"), "dmsbnw134"),
    (("signal134", "a"), "signal134"),
    (("signal134", "zz"), "rhfmzk134"),
    (("signal134", "AgentU"), "sokatf134"),
    (("signal134", "keyboard"), "cmeool134"),
    (("signal134", "AA"), "signal134"),
    (("packet134", "key"), "zeauir134"),
    (("packet134", "lemon"), "aeoyre134"),
    (("packet134", "a"), "packet134"),
    (("packet134", "zz"), "ozbjds134"),
    (("packet134", "AgentU"), "pggxxn134"),
    (("packet134", "keyboard"), "zealst134"),
    (("packet134", "AA"), "packet134"),
    (("router134", "key"), "bssdip134"),
    (("router134", "lemon"), "csghrc134"),
    (("router134", "a"), "router134"),
    (("router134", "zz"), "qntsdq134"),
    (("router134", "AgentU"), "ruygxl134"),
    (("router134", "keyboard"), "bssusr134"),
    (("router134", "AA"), "router134"),
    (("cluster134", "key"), "mpscxcb134"),
    (("cluster134", "lemon"), "npgggpv134"),
    (("cluster134", "a"), "cluster134"),
    (("cluster134", "zz"), "bktrsdq134"),
    (("cluster134", "AgentU"), "cryfmyr134"),
    (("cluster134", "keyboard"), "mpsthei134"),
    (("cluster134", "AA"), "cluster134"),
    (("mirror134", "key"), "wmpbsp134"),
    (("mirror134", "lemon"), "xmdfbc134"),
    (("mirror134", "a"), "mirror134"),
    (("mirror134", "zz"), "lhqqnq134"),
    (("mirror134", "AgentU"), "movehl134"),
    (("mirror134", "keyboard"), "wmpscr134"),
    (("mirror134", "AA"), "mirror134"),
    (("filter134", "key"), "pmjdip134"),
    (("filter134", "lemon"), "qmxhrc134"),
    (("filter134", "a"), "filter134"),
    (("filter134", "zz"), "ehksdq134"),
    (("filter134", "AgentU"), "fopgxl134"),
    (("filter134", "keyboard"), "pmjusr134"),
    (("filter134", "AA"), "filter134"),
    (("ranking134", "key"), "belumlq134"),
    (("ranking134", "lemon"), "cezyvyk134"),
    (("ranking134", "a"), "ranking134"),
    (("ranking134", "zz"), "qzmjhmf134"),
    (("ranking134", "AgentU"), "rgrxbhg134"),
    (("ranking134", "keyboard"), "bellwnx134"),
    (("ranking134", "AA"), "ranking134"),
    (("encoding134", "key"), "orayhgxk134"),
    (("encoding134", "lemon"), "procqtrs134"),
    (("encoding134", "a"), "encoding134"),
    (("encoding134", "zz"), "dmbnchmf134"),
    (("encoding134", "AgentU"), "etgbwcnm134"),
    (("encoding134", "keyboard"), "orapriej134"),
    (("encoding134", "AA"), "encoding134"),
    (("mapping134", "key"), "wenzmlq134"),
    (("mapping134", "lemon"), "xebdvyk134"),
    (("mapping134", "a"), "mapping134"),
    (("mapping134", "zz"), "lzoohmf134"),
    (("mapping134", "AgentU"), "mgtcbhg134"),
    (("mapping134", "keyboard"), "wenqwnx134"),
    (("mapping134", "AA"), "mapping134"),
    (("record134", "key"), "biayvb134"),
    (("record134", "lemon"), "cioceo134"),
    (("record134", "a"), "record134"),
    (("record134", "zz"), "qdbnqc134"),
    (("record134", "AgentU"), "rkgbkx134"),
    (("record134", "keyboard"), "biapfd134"),
    (("record134", "AA"), "record134"),
    (("candle134", "key"), "melnpc134"),
    (("candle134", "lemon"), "nezryp134"),
    (("candle134", "a"), "candle134"),
    (("candle134", "zz"), "bzmckd134"),
    (("candle134", "AgentU"), "cgrqey134"),
    (("candle134", "keyboard"), "meleze134"),
    (("candle134", "AA"), "candle134"),
    (("thread134", "key"), "dlpoeb134"),
    (("thread134", "lemon"), "eldsno134"),
    (("thread134", "a"), "thread134"),
    (("thread134", "zz"), "sgqdzc134"),
    (("thread134", "AgentU"), "tnvrtx134"),
    (("thread134", "keyboard"), "dlpfod134"),
    (("thread134", "AA"), "thread134"),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 134: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 134: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "a"),
        "round 134: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 134: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 134: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 134: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", "AA"),
        "round 134: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "key"),
        "bssxh 134: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 134: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "a"),
        "round 134: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 134: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 134: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 134: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", "AA"),
        "round 134: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 134: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 134: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "a"),
        "round 134: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 134: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 134: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 134: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", "AA"),
        "round 134: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 134: the processor reads the record then stops", "key"),
        "bssxh 134: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 134: the processor reads the record then stops", "lemon"),
        "csgbq 134: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 134: the processor reads the record then stops", "a"),
        "round 134: the processor reads the record then stops",
    ),
    (
        ("round 134: the processor reads the record then stops", "zz"),
        "qntmc 134: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 134: the processor reads the record then stops", "AgentU"),
        "ruyaw 134: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 134: the processor reads the record then stops", "keyboard"),
        "bssor 134: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 134: the processor reads the record then stops", "AA"),
        "round 134: the processor reads the record then stops",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "key"),
        "bssxh 134: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "lemon"),
        "csgbq 134: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "a"),
        "round 134: a worker pulls the next task from the queue",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "zz"),
        "qntmc 134: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 134: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "keyboard"),
        "bssor 134: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 134: a worker pulls the next task from the queue", "AA"),
        "round 134: a worker pulls the next task from the queue",
    ),
    (
        ("round 134: signals travel through the network layer", "key"),
        "bssxh 134: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 134: signals travel through the network layer", "lemon"),
        "csgbq 134: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 134: signals travel through the network layer", "a"),
        "round 134: signals travel through the network layer",
    ),
    (
        ("round 134: signals travel through the network layer", "zz"),
        "qntmc 134: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 134: signals travel through the network layer", "AgentU"),
        "ruyaw 134: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 134: signals travel through the network layer", "keyboard"),
        "bssor 134: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 134: signals travel through the network layer", "AA"),
        "round 134: signals travel through the network layer",
    ),
    (
        ("round 134: the gateway routes each request by policy", "key"),
        "bssxh 134: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 134: the gateway routes each request by policy", "lemon"),
        "csgbq 134: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 134: the gateway routes each request by policy", "a"),
        "round 134: the gateway routes each request by policy",
    ),
    (
        ("round 134: the gateway routes each request by policy", "zz"),
        "qntmc 134: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 134: the gateway routes each request by policy", "AgentU"),
        "ruyaw 134: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 134: the gateway routes each request by policy", "keyboard"),
        "bssor 134: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 134: the gateway routes each request by policy", "AA"),
        "round 134: the gateway routes each request by policy",
    ),
    (("round 134: memory grows until the buffer is full", "key"), "bssxh 134: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 134: memory grows until the buffer is full", "lemon"), "csgbq 134: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 134: memory grows until the buffer is full", "a"), "round 134: memory grows until the buffer is full"),
    (("round 134: memory grows until the buffer is full", "zz"), "qntmc 134: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 134: memory grows until the buffer is full", "AgentU"),
        "ruyaw 134: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 134: memory grows until the buffer is full", "keyboard"),
        "bssor 134: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 134: memory grows until the buffer is full", "AA"), "round 134: memory grows until the buffer is full"),
    (("round 134: the cluster mirrors every packet twice", "key"), "bssxh 134: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 134: the cluster mirrors every packet twice", "lemon"),
        "csgbq 134: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 134: the cluster mirrors every packet twice", "a"), "round 134: the cluster mirrors every packet twice"),
    (("round 134: the cluster mirrors every packet twice", "zz"), "qntmc 134: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 134: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 134: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 134: the cluster mirrors every packet twice", "keyboard"),
        "bssor 134: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 134: the cluster mirrors every packet twice", "AA"), "round 134: the cluster mirrors every packet twice"),
    (
        ("round 134: ranking uses tokens learned from the corpus", "key"),
        "bssxh 134: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 134: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", "a"),
        "round 134: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 134: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 134: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 134: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", "AA"),
        "round 134: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 134: a long session ends when the candle dies", "key"),
        "bssxh 134: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 134: a long session ends when the candle dies", "lemon"),
        "csgbq 134: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 134: a long session ends when the candle dies", "a"),
        "round 134: a long session ends when the candle dies",
    ),
    (
        ("round 134: a long session ends when the candle dies", "zz"),
        "qntmc 134: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 134: a long session ends when the candle dies", "AgentU"),
        "ruyaw 134: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 134: a long session ends when the candle dies", "keyboard"),
        "bssor 134: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 134: a long session ends when the candle dies", "AA"),
        "round 134: a long session ends when the candle dies",
    ),
    (("round 134: encode the prompt then map the result", "key"), "bssxh 134: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 134: encode the prompt then map the result", "lemon"), "csgbq 134: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 134: encode the prompt then map the result", "a"), "round 134: encode the prompt then map the result"),
    (("round 134: encode the prompt then map the result", "zz"), "qntmc 134: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 134: encode the prompt then map the result", "AgentU"),
        "ruyaw 134: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 134: encode the prompt then map the result", "keyboard"),
        "bssor 134: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 134: encode the prompt then map the result", "AA"), "round 134: encode the prompt then map the result"),
    (("round 134: the kernel wakes the worker at dawn", "key"), "bssxh 134: rri iovlop ukocc xfo ambocb er neux"),
    (("round 134: the kernel wakes the worker at dawn", "lemon"), "csgbq 134: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 134: the kernel wakes the worker at dawn", "a"), "round 134: the kernel wakes the worker at dawn"),
    (("round 134: the kernel wakes the worker at dawn", "zz"), "qntmc 134: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 134: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 134: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 134: the kernel wakes the worker at dawn", "keyboard"), "bssor 134: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 134: the kernel wakes the worker at dawn", "AA"), "round 134: the kernel wakes the worker at dawn"),
    (("round 134: service latency drops after the patch", "key"), "bssxh 134: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 134: service latency drops after the patch", "lemon"), "csgbq 134: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 134: service latency drops after the patch", "a"), "round 134: service latency drops after the patch"),
    (("round 134: service latency drops after the patch", "zz"), "qntmc 134: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 134: service latency drops after the patch", "AgentU"),
        "ruyaw 134: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 134: service latency drops after the patch", "keyboard"),
        "bssor 134: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 134: service latency drops after the patch", "AA"), "round 134: service latency drops after the patch"),
    (
        ("round 134: the library caches every vector it sees", "key"),
        "bssxh 134: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 134: the library caches every vector it sees", "lemon"),
        "csgbq 134: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 134: the library caches every vector it sees", "a"), "round 134: the library caches every vector it sees"),
    (
        ("round 134: the library caches every vector it sees", "zz"),
        "qntmc 134: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 134: the library caches every vector it sees", "AgentU"),
        "ruyaw 134: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 134: the library caches every vector it sees", "keyboard"),
        "bssor 134: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 134: the library caches every vector it sees", "AA"),
        "round 134: the library caches every vector it sees",
    ),
    (("round 134: agents argue then the debate resolves", "key"), "bssxh 134: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 134: agents argue then the debate resolves", "lemon"), "csgbq 134: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 134: agents argue then the debate resolves", "a"), "round 134: agents argue then the debate resolves"),
    (("round 134: agents argue then the debate resolves", "zz"), "qntmc 134: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 134: agents argue then the debate resolves", "AgentU"),
        "ruyaw 134: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 134: agents argue then the debate resolves", "keyboard"),
        "bssor 134: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 134: agents argue then the debate resolves", "AA"), "round 134: agents argue then the debate resolves"),
    (("round 134: the filter keeps only strong matches", "key"), "bssxh 134: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 134: the filter keeps only strong matches", "lemon"), "csgbq 134: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 134: the filter keeps only strong matches", "a"), "round 134: the filter keeps only strong matches"),
    (("round 134: the filter keeps only strong matches", "zz"), "qntmc 134: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 134: the filter keeps only strong matches", "AgentU"), "ruyaw 134: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 134: the filter keeps only strong matches", "keyboard"),
        "bssor 134: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 134: the filter keeps only strong matches", "AA"), "round 134: the filter keeps only strong matches"),
    (("round 134: the model answers with a short reply", "key"), "bssxh 134: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 134: the model answers with a short reply", "lemon"), "csgbq 134: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 134: the model answers with a short reply", "a"), "round 134: the model answers with a short reply"),
    (("round 134: the model answers with a short reply", "zz"), "qntmc 134: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 134: the model answers with a short reply", "AgentU"), "ruyaw 134: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 134: the model answers with a short reply", "keyboard"),
        "bssor 134: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 134: the model answers with a short reply", "AA"), "round 134: the model answers with a short reply"),
    (
        ("round 134: the recorder stores the reasoning trace", "key"),
        "bssxh 134: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 134: the recorder stores the reasoning trace", "lemon"),
        "csgbq 134: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 134: the recorder stores the reasoning trace", "a"), "round 134: the recorder stores the reasoning trace"),
    (
        ("round 134: the recorder stores the reasoning trace", "zz"),
        "qntmc 134: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 134: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 134: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 134: the recorder stores the reasoning trace", "keyboard"),
        "bssor 134: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 134: the recorder stores the reasoning trace", "AA"),
        "round 134: the recorder stores the reasoning trace",
    ),
    (("round 134: the angel watches the processor run", "key"), "bssxh 134: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 134: the angel watches the processor run", "lemon"), "csgbq 134: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 134: the angel watches the processor run", "a"), "round 134: the angel watches the processor run"),
    (("round 134: the angel watches the processor run", "zz"), "qntmc 134: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 134: the angel watches the processor run", "AgentU"), "ruyaw 134: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 134: the angel watches the processor run", "keyboard"), "bssor 134: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 134: the angel watches the processor run", "AA"), "round 134: the angel watches the processor run"),
    (("round 134: angle of the vector decides the match", "key"), "bssxh 134: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 134: angle of the vector decides the match", "lemon"), "csgbq 134: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 134: angle of the vector decides the match", "a"), "round 134: angle of the vector decides the match"),
    (("round 134: angle of the vector decides the match", "zz"), "qntmc 134: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 134: angle of the vector decides the match", "AgentU"),
        "ruyaw 134: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 134: angle of the vector decides the match", "keyboard"),
        "bssor 134: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 134: angle of the vector decides the match", "AA"), "round 134: angle of the vector decides the match"),
    (
        ("round 134: the candle burns twice as long at night", "key"),
        "bssxh 134: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 134: the candle burns twice as long at night", "lemon"),
        "csgbq 134: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 134: the candle burns twice as long at night", "a"), "round 134: the candle burns twice as long at night"),
    (
        ("round 134: the candle burns twice as long at night", "zz"),
        "qntmc 134: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 134: the candle burns twice as long at night", "AgentU"),
        "ruyaw 134: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 134: the candle burns twice as long at night", "keyboard"),
        "bssor 134: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 134: the candle burns twice as long at night", "AA"),
        "round 134: the candle burns twice as long at night",
    ),
    (("round 134: a mirror of the universe in one line", "key"), "bssxh 134: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 134: a mirror of the universe in one line", "lemon"), "csgbq 134: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 134: a mirror of the universe in one line", "a"), "round 134: a mirror of the universe in one line"),
    (("round 134: a mirror of the universe in one line", "zz"), "qntmc 134: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 134: a mirror of the universe in one line", "AgentU"), "ruyaw 134: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 134: a mirror of the universe in one line", "keyboard"),
        "bssor 134: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 134: a mirror of the universe in one line", "AA"), "round 134: a mirror of the universe in one line"),
    (("round 134: the queue drains before the storm", "key"), "bssxh 134: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 134: the queue drains before the storm", "lemon"), "csgbq 134: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 134: the queue drains before the storm", "a"), "round 134: the queue drains before the storm"),
    (("round 134: the queue drains before the storm", "zz"), "qntmc 134: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 134: the queue drains before the storm", "AgentU"), "ruyaw 134: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 134: the queue drains before the storm", "keyboard"), "bssor 134: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 134: the queue drains before the storm", "AA"), "round 134: the queue drains before the storm"),
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
