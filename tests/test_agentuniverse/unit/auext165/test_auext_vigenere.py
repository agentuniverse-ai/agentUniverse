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
    (("kitten165", "key"), "umrdil165"),
    (("kitten165", "lemon"), "vmfhry165"),
    (("kitten165", "a"), "kitten165"),
    (("kitten165", "zz"), "jhssdm165"),
    (("kitten165", "AgentU"), "koxgxh165"),
    (("kitten165", "keyboard"), "umrusn165"),
    (("kitten165", "AA"), "kitten165"),
    (("sitting165", "key"), "cmrdmlq165"),
    (("sitting165", "lemon"), "dmfhvyk165"),
    (("sitting165", "a"), "sitting165"),
    (("sitting165", "zz"), "rhsshmf165"),
    (("sitting165", "AgentU"), "soxgbhg165"),
    (("sitting165", "keyboard"), "cmruwnx165"),
    (("sitting165", "AA"), "sitting165"),
    (("agent165", "key"), "kkcxx165"),
    (("agent165", "lemon"), "lkqbg165"),
    (("agent165", "a"), "agent165"),
    (("agent165", "zz"), "zfdms165"),
    (("agent165", "AgentU"), "amiam165"),
    (("agent165", "keyboard"), "kkcoh165"),
    (("agent165", "AA"), "agent165"),
    (("angle165", "key"), "krevi165"),
    (("angle165", "lemon"), "lrszr165"),
    (("angle165", "a"), "angle165"),
    (("angle165", "zz"), "zmfkd165"),
    (("angle165", "AgentU"), "atkyx165"),
    (("angle165", "keyboard"), "krems165"),
    (("angle165", "AA"), "angle165"),
    (("universe165", "key"), "ergfipci165"),
    (("universe165", "lemon"), "frujrcwq165"),
    (("universe165", "a"), "universe165"),
    (("universe165", "zz"), "tmhudqrd165"),
    (("universe165", "AgentU"), "utmixlsk165"),
    (("universe165", "keyboard"), "ergwsrjh165"),
    (("universe165", "AA"), "universe165"),
    (("memory165", "key"), "wikyvw165"),
    (("memory165", "lemon"), "xiycej165"),
    (("memory165", "a"), "memory165"),
    (("memory165", "zz"), "ldlnqx165"),
    (("memory165", "AgentU"), "mkqbks165"),
    (("memory165", "keyboard"), "wikpfy165"),
    (("memory165", "AA"), "memory165"),
    (("stream165", "key"), "cxpoek165"),
    (("stream165", "lemon"), "dxdsnx165"),
    (("stream165", "a"), "stream165"),
    (("stream165", "zz"), "rsqdzl165"),
    (("stream165", "AgentU"), "szvrtg165"),
    (("stream165", "keyboard"), "cxpfom165"),
    (("stream165", "AA"), "stream165"),
    (("context165", "key"), "msldivd165"),
    (("context165", "lemon"), "nszhrix165"),
    (("context165", "a"), "context165"),
    (("context165", "zz"), "bnmsdws165"),
    (("context165", "AgentU"), "curgxrt165"),
    (("context165", "keyboard"), "mslusxk165"),
    (("context165", "AA"), "context165"),
    (("knowledge165", "key"), "urmgpcnkc165"),
    (("knowledge165", "lemon"), "vrakyphss165"),
    (("knowledge165", "a"), "knowledge165"),
    (("knowledge165", "zz"), "jmnvkdcfd165"),
    (("knowledge165", "AgentU"), "ktsjeydmi165"),
    (("knowledge165", "keyboard"), "urmxzeujo165"),
    (("knowledge165", "AA"), "knowledge165"),
    (("vector165", "key"), "fiadsp165"),
    (("vector165", "lemon"), "giohbc165"),
    (("vector165", "a"), "vector165"),
    (("vector165", "zz"), "udbsnq165"),
    (("vector165", "AgentU"), "vkgghl165"),
    (("vector165", "keyboard"), "fiaucr165"),
    (("vector165", "AA"), "vector165"),
    (("processor165", "key"), "zvmmiqcsp165"),
    (("processor165", "lemon"), "avaqrdwaf165"),
    (("processor165", "a"), "processor165"),
    (("processor165", "zz"), "oqnbdrrnq165"),
    (("processor165", "AgentU"), "pxspxmsuv165"),
    (("processor165", "keyboard"), "zvmdssjrb165"),
    (("processor165", "AA"), "processor165"),
    (("reasoning165", "key"), "biycslsre165"),
    (("reasoning165", "lemon"), "cimgbymzu165"),
    (("reasoning165", "a"), "reasoning165"),
    (("reasoning165", "zz"), "qdzrnmhmf165"),
    (("reasoning165", "AgentU"), "rkefhhitk165"),
    (("reasoning165", "keyboard"), "biytcnzqq165"),
    (("reasoning165", "AA"), "reasoning165"),
    (("machine165", "key"), "wearmlo165"),
    (("machine165", "lemon"), "xeovvyi165"),
    (("machine165", "a"), "machine165"),
    (("machine165", "zz"), "lzbghmd165"),
    (("machine165", "AgentU"), "mggubhe165"),
    (("machine165", "keyboard"), "weaiwnv165"),
    (("machine165", "AA"), "machine165"),
    (("learning165", "key"), "viybrgxk165"),
    (("learning165", "lemon"), "wimfatrs165"),
    (("learning165", "a"), "learning165"),
    (("learning165", "zz"), "kdzqmhmf165"),
    (("learning165", "AgentU"), "lkeegcnm165"),
    (("learning165", "keyboard"), "viysbiej165"),
    (("learning165", "AA"), "learning165"),
    (("model165", "key"), "wsbop165"),
    (("model165", "lemon"), "xspsy165"),
    (("model165", "a"), "model165"),
    (("model165", "zz"), "lncdk165"),
    (("model165", "AgentU"), "muhre165"),
    (("model165", "keyboard"), "wsbfz165"),
    (("model165", "AA"), "model165"),
    (("token165", "key"), "dsior165"),
    (("token165", "lemon"), "eswsa165"),
    (("token165", "a"), "token165"),
    (("token165", "zz"), "snjdm165"),
    (("token165", "AgentU"), "tuorg165"),
    (("token165", "keyboard"), "dsifb165"),
    (("token165", "AA"), "token165"),
    (("prompt165", "key"), "zvmwtr165"),
    (("prompt165", "lemon"), "avaace165"),
    (("prompt165", "a"), "prompt165"),
    (("prompt165", "zz"), "oqnlos165"),
    (("prompt165", "AgentU"), "pxszin165"),
    (("prompt165", "keyboard"), "zvmndt165"),
    (("prompt165", "AA"), "prompt165"),
    (("session165", "key"), "ciqcmmx165"),
    (("session165", "lemon"), "diegvzr165"),
    (("session165", "a"), "session165"),
    (("session165", "zz"), "rdrrhnm165"),
    (("session165", "AgentU"), "skwfbin165"),
    (("session165", "keyboard"), "ciqtwoe165"),
    (("session165", "AA"), "session165"),
    (("library165", "key"), "vmzbepi165"),
    (("library165", "lemon"), "wmnfncc165"),
    (("library165", "a"), "library165"),
    (("library165", "zz"), "khaqzqx165"),
    (("library165", "AgentU"), "lofetly165"),
    (("library165", "keyboard"), "vmzsorp165"),
    (("library165", "AA"), "library165"),
    (("service165", "key"), "cipfmao165"),
    (("service165", "lemon"), "didjvni165"),
    (("service165", "a"), "service165"),
    (("service165", "zz"), "rdquhbd165"),
    (("service165", "AgentU"), "skvibwe165"),
    (("service165", "keyboard"), "cipwwcv165"),
    (("service165", "AA"), "service165"),
    (("gateway165", "key"), "qeroayi165"),
    (("gateway165", "lemon"), "refsjlc165"),
    (("gateway165", "a"), "gateway165"),
    (("gateway165", "zz"), "fzsdvzx165"),
    (("gateway165", "AgentU"), "ggxrpuy165"),
    (("gateway165", "keyboard"), "qerfkap165"),
    (("gateway165", "AA"), "gateway165"),
    (("storage165", "key"), "cxmbeeo165"),
    (("storage165", "lemon"), "dxafnri165"),
    (("storage165", "a"), "storage165"),
    (("storage165", "zz"), "rsnqzfd165"),
    (("storage165", "AgentU"), "szsetae165"),
    (("storage165", "keyboard"), "cxmsogv165"),
    (("storage165", "AA"), "storage165"),
    (("network165", "key"), "xirgspu165"),
    (("network165", "lemon"), "yifkbco165"),
    (("network165", "a"), "network165"),
    (("network165", "zz"), "mdsvnqj165"),
    (("network165", "AgentU"), "nkxjhlk165"),
    (("network165", "keyboard"), "xirxcrb165"),
    (("network165", "AA"), "network165"),
    (("latency165", "key"), "verorai165"),
    (("latency165", "lemon"), "wefsanc165"),
    (("latency165", "a"), "latency165"),
    (("latency165", "zz"), "kzsdmbx165"),
    (("latency165", "AgentU"), "lgxrgwy165"),
    (("latency165", "keyboard"), "verfbcp165"),
    (("latency165", "AA"), "latency165"),
    (("buffer165", "key"), "lydpip165"),
    (("buffer165", "lemon"), "myrtrc165"),
    (("buffer165", "a"), "buffer165"),
    (("buffer165", "zz"), "ateedq165"),
    (("buffer165", "AgentU"), "bajsxl165"),
    (("buffer165", "keyboard"), "lydgsr165"),
    (("buffer165", "AA"), "buffer165"),
    (("queue165", "key"), "aycei165"),
    (("queue165", "lemon"), "byqir165"),
    (("queue165", "a"), "queue165"),
    (("queue165", "zz"), "ptdtd165"),
    (("queue165", "AgentU"), "qaihx165"),
    (("queue165", "keyboard"), "aycvs165"),
    (("queue165", "AA"), "queue165"),
    (("worker165", "key"), "gspuip165"),
    (("worker165", "lemon"), "hsdyrc165"),
    (("worker165", "a"), "worker165"),
    (("worker165", "zz"), "vnqjdq165"),
    (("worker165", "AgentU"), "wuvxxl165"),
    (("worker165", "keyboard"), "gsplsr165"),
    (("worker165", "AA"), "worker165"),
    (("kernel165", "key"), "uipxij165"),
    (("kernel165", "lemon"), "vidbrw165"),
    (("kernel165", "a"), "kernel165"),
    (("kernel165", "zz"), "jdqmdk165"),
    (("kernel165", "AgentU"), "kkvaxf165"),
    (("kernel165", "keyboard"), "uiposl165"),
    (("kernel165", "AA"), "kernel165"),
    (("signal165", "key"), "cmexej165"),
    (("signal165", "lemon"), "dmsbnw165"),
    (("signal165", "a"), "signal165"),
    (("signal165", "zz"), "rhfmzk165"),
    (("signal165", "AgentU"), "sokatf165"),
    (("signal165", "keyboard"), "cmeool165"),
    (("signal165", "AA"), "signal165"),
    (("packet165", "key"), "zeauir165"),
    (("packet165", "lemon"), "aeoyre165"),
    (("packet165", "a"), "packet165"),
    (("packet165", "zz"), "ozbjds165"),
    (("packet165", "AgentU"), "pggxxn165"),
    (("packet165", "keyboard"), "zealst165"),
    (("packet165", "AA"), "packet165"),
    (("router165", "key"), "bssdip165"),
    (("router165", "lemon"), "csghrc165"),
    (("router165", "a"), "router165"),
    (("router165", "zz"), "qntsdq165"),
    (("router165", "AgentU"), "ruygxl165"),
    (("router165", "keyboard"), "bssusr165"),
    (("router165", "AA"), "router165"),
    (("cluster165", "key"), "mpscxcb165"),
    (("cluster165", "lemon"), "npgggpv165"),
    (("cluster165", "a"), "cluster165"),
    (("cluster165", "zz"), "bktrsdq165"),
    (("cluster165", "AgentU"), "cryfmyr165"),
    (("cluster165", "keyboard"), "mpsthei165"),
    (("cluster165", "AA"), "cluster165"),
    (("mirror165", "key"), "wmpbsp165"),
    (("mirror165", "lemon"), "xmdfbc165"),
    (("mirror165", "a"), "mirror165"),
    (("mirror165", "zz"), "lhqqnq165"),
    (("mirror165", "AgentU"), "movehl165"),
    (("mirror165", "keyboard"), "wmpscr165"),
    (("mirror165", "AA"), "mirror165"),
    (("filter165", "key"), "pmjdip165"),
    (("filter165", "lemon"), "qmxhrc165"),
    (("filter165", "a"), "filter165"),
    (("filter165", "zz"), "ehksdq165"),
    (("filter165", "AgentU"), "fopgxl165"),
    (("filter165", "keyboard"), "pmjusr165"),
    (("filter165", "AA"), "filter165"),
    (("ranking165", "key"), "belumlq165"),
    (("ranking165", "lemon"), "cezyvyk165"),
    (("ranking165", "a"), "ranking165"),
    (("ranking165", "zz"), "qzmjhmf165"),
    (("ranking165", "AgentU"), "rgrxbhg165"),
    (("ranking165", "keyboard"), "bellwnx165"),
    (("ranking165", "AA"), "ranking165"),
    (("encoding165", "key"), "orayhgxk165"),
    (("encoding165", "lemon"), "procqtrs165"),
    (("encoding165", "a"), "encoding165"),
    (("encoding165", "zz"), "dmbnchmf165"),
    (("encoding165", "AgentU"), "etgbwcnm165"),
    (("encoding165", "keyboard"), "orapriej165"),
    (("encoding165", "AA"), "encoding165"),
    (("mapping165", "key"), "wenzmlq165"),
    (("mapping165", "lemon"), "xebdvyk165"),
    (("mapping165", "a"), "mapping165"),
    (("mapping165", "zz"), "lzoohmf165"),
    (("mapping165", "AgentU"), "mgtcbhg165"),
    (("mapping165", "keyboard"), "wenqwnx165"),
    (("mapping165", "AA"), "mapping165"),
    (("record165", "key"), "biayvb165"),
    (("record165", "lemon"), "cioceo165"),
    (("record165", "a"), "record165"),
    (("record165", "zz"), "qdbnqc165"),
    (("record165", "AgentU"), "rkgbkx165"),
    (("record165", "keyboard"), "biapfd165"),
    (("record165", "AA"), "record165"),
    (("candle165", "key"), "melnpc165"),
    (("candle165", "lemon"), "nezryp165"),
    (("candle165", "a"), "candle165"),
    (("candle165", "zz"), "bzmckd165"),
    (("candle165", "AgentU"), "cgrqey165"),
    (("candle165", "keyboard"), "meleze165"),
    (("candle165", "AA"), "candle165"),
    (("thread165", "key"), "dlpoeb165"),
    (("thread165", "lemon"), "eldsno165"),
    (("thread165", "a"), "thread165"),
    (("thread165", "zz"), "sgqdzc165"),
    (("thread165", "AgentU"), "tnvrtx165"),
    (("thread165", "keyboard"), "dlpfod165"),
    (("thread165", "AA"), "thread165"),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 165: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 165: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "a"),
        "round 165: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 165: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 165: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 165: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", "AA"),
        "round 165: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "key"),
        "bssxh 165: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 165: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "a"),
        "round 165: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 165: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 165: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 165: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", "AA"),
        "round 165: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 165: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 165: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "a"),
        "round 165: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 165: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 165: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 165: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", "AA"),
        "round 165: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 165: the processor reads the record then stops", "key"),
        "bssxh 165: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 165: the processor reads the record then stops", "lemon"),
        "csgbq 165: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 165: the processor reads the record then stops", "a"),
        "round 165: the processor reads the record then stops",
    ),
    (
        ("round 165: the processor reads the record then stops", "zz"),
        "qntmc 165: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 165: the processor reads the record then stops", "AgentU"),
        "ruyaw 165: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 165: the processor reads the record then stops", "keyboard"),
        "bssor 165: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 165: the processor reads the record then stops", "AA"),
        "round 165: the processor reads the record then stops",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "key"),
        "bssxh 165: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "lemon"),
        "csgbq 165: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "a"),
        "round 165: a worker pulls the next task from the queue",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "zz"),
        "qntmc 165: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 165: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "keyboard"),
        "bssor 165: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 165: a worker pulls the next task from the queue", "AA"),
        "round 165: a worker pulls the next task from the queue",
    ),
    (
        ("round 165: signals travel through the network layer", "key"),
        "bssxh 165: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 165: signals travel through the network layer", "lemon"),
        "csgbq 165: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 165: signals travel through the network layer", "a"),
        "round 165: signals travel through the network layer",
    ),
    (
        ("round 165: signals travel through the network layer", "zz"),
        "qntmc 165: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 165: signals travel through the network layer", "AgentU"),
        "ruyaw 165: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 165: signals travel through the network layer", "keyboard"),
        "bssor 165: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 165: signals travel through the network layer", "AA"),
        "round 165: signals travel through the network layer",
    ),
    (
        ("round 165: the gateway routes each request by policy", "key"),
        "bssxh 165: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 165: the gateway routes each request by policy", "lemon"),
        "csgbq 165: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 165: the gateway routes each request by policy", "a"),
        "round 165: the gateway routes each request by policy",
    ),
    (
        ("round 165: the gateway routes each request by policy", "zz"),
        "qntmc 165: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 165: the gateway routes each request by policy", "AgentU"),
        "ruyaw 165: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 165: the gateway routes each request by policy", "keyboard"),
        "bssor 165: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 165: the gateway routes each request by policy", "AA"),
        "round 165: the gateway routes each request by policy",
    ),
    (("round 165: memory grows until the buffer is full", "key"), "bssxh 165: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 165: memory grows until the buffer is full", "lemon"), "csgbq 165: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 165: memory grows until the buffer is full", "a"), "round 165: memory grows until the buffer is full"),
    (("round 165: memory grows until the buffer is full", "zz"), "qntmc 165: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 165: memory grows until the buffer is full", "AgentU"),
        "ruyaw 165: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 165: memory grows until the buffer is full", "keyboard"),
        "bssor 165: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 165: memory grows until the buffer is full", "AA"), "round 165: memory grows until the buffer is full"),
    (("round 165: the cluster mirrors every packet twice", "key"), "bssxh 165: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 165: the cluster mirrors every packet twice", "lemon"),
        "csgbq 165: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 165: the cluster mirrors every packet twice", "a"), "round 165: the cluster mirrors every packet twice"),
    (("round 165: the cluster mirrors every packet twice", "zz"), "qntmc 165: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 165: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 165: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 165: the cluster mirrors every packet twice", "keyboard"),
        "bssor 165: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 165: the cluster mirrors every packet twice", "AA"), "round 165: the cluster mirrors every packet twice"),
    (
        ("round 165: ranking uses tokens learned from the corpus", "key"),
        "bssxh 165: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 165: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", "a"),
        "round 165: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 165: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 165: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 165: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", "AA"),
        "round 165: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 165: a long session ends when the candle dies", "key"),
        "bssxh 165: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 165: a long session ends when the candle dies", "lemon"),
        "csgbq 165: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 165: a long session ends when the candle dies", "a"),
        "round 165: a long session ends when the candle dies",
    ),
    (
        ("round 165: a long session ends when the candle dies", "zz"),
        "qntmc 165: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 165: a long session ends when the candle dies", "AgentU"),
        "ruyaw 165: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 165: a long session ends when the candle dies", "keyboard"),
        "bssor 165: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 165: a long session ends when the candle dies", "AA"),
        "round 165: a long session ends when the candle dies",
    ),
    (("round 165: encode the prompt then map the result", "key"), "bssxh 165: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 165: encode the prompt then map the result", "lemon"), "csgbq 165: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 165: encode the prompt then map the result", "a"), "round 165: encode the prompt then map the result"),
    (("round 165: encode the prompt then map the result", "zz"), "qntmc 165: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 165: encode the prompt then map the result", "AgentU"),
        "ruyaw 165: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 165: encode the prompt then map the result", "keyboard"),
        "bssor 165: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 165: encode the prompt then map the result", "AA"), "round 165: encode the prompt then map the result"),
    (("round 165: the kernel wakes the worker at dawn", "key"), "bssxh 165: rri iovlop ukocc xfo ambocb er neux"),
    (("round 165: the kernel wakes the worker at dawn", "lemon"), "csgbq 165: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 165: the kernel wakes the worker at dawn", "a"), "round 165: the kernel wakes the worker at dawn"),
    (("round 165: the kernel wakes the worker at dawn", "zz"), "qntmc 165: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 165: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 165: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 165: the kernel wakes the worker at dawn", "keyboard"), "bssor 165: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 165: the kernel wakes the worker at dawn", "AA"), "round 165: the kernel wakes the worker at dawn"),
    (("round 165: service latency drops after the patch", "key"), "bssxh 165: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 165: service latency drops after the patch", "lemon"), "csgbq 165: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 165: service latency drops after the patch", "a"), "round 165: service latency drops after the patch"),
    (("round 165: service latency drops after the patch", "zz"), "qntmc 165: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 165: service latency drops after the patch", "AgentU"),
        "ruyaw 165: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 165: service latency drops after the patch", "keyboard"),
        "bssor 165: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 165: service latency drops after the patch", "AA"), "round 165: service latency drops after the patch"),
    (
        ("round 165: the library caches every vector it sees", "key"),
        "bssxh 165: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 165: the library caches every vector it sees", "lemon"),
        "csgbq 165: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 165: the library caches every vector it sees", "a"), "round 165: the library caches every vector it sees"),
    (
        ("round 165: the library caches every vector it sees", "zz"),
        "qntmc 165: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 165: the library caches every vector it sees", "AgentU"),
        "ruyaw 165: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 165: the library caches every vector it sees", "keyboard"),
        "bssor 165: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 165: the library caches every vector it sees", "AA"),
        "round 165: the library caches every vector it sees",
    ),
    (("round 165: agents argue then the debate resolves", "key"), "bssxh 165: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 165: agents argue then the debate resolves", "lemon"), "csgbq 165: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 165: agents argue then the debate resolves", "a"), "round 165: agents argue then the debate resolves"),
    (("round 165: agents argue then the debate resolves", "zz"), "qntmc 165: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 165: agents argue then the debate resolves", "AgentU"),
        "ruyaw 165: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 165: agents argue then the debate resolves", "keyboard"),
        "bssor 165: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 165: agents argue then the debate resolves", "AA"), "round 165: agents argue then the debate resolves"),
    (("round 165: the filter keeps only strong matches", "key"), "bssxh 165: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 165: the filter keeps only strong matches", "lemon"), "csgbq 165: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 165: the filter keeps only strong matches", "a"), "round 165: the filter keeps only strong matches"),
    (("round 165: the filter keeps only strong matches", "zz"), "qntmc 165: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 165: the filter keeps only strong matches", "AgentU"), "ruyaw 165: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 165: the filter keeps only strong matches", "keyboard"),
        "bssor 165: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 165: the filter keeps only strong matches", "AA"), "round 165: the filter keeps only strong matches"),
    (("round 165: the model answers with a short reply", "key"), "bssxh 165: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 165: the model answers with a short reply", "lemon"), "csgbq 165: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 165: the model answers with a short reply", "a"), "round 165: the model answers with a short reply"),
    (("round 165: the model answers with a short reply", "zz"), "qntmc 165: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 165: the model answers with a short reply", "AgentU"), "ruyaw 165: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 165: the model answers with a short reply", "keyboard"),
        "bssor 165: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 165: the model answers with a short reply", "AA"), "round 165: the model answers with a short reply"),
    (
        ("round 165: the recorder stores the reasoning trace", "key"),
        "bssxh 165: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 165: the recorder stores the reasoning trace", "lemon"),
        "csgbq 165: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 165: the recorder stores the reasoning trace", "a"), "round 165: the recorder stores the reasoning trace"),
    (
        ("round 165: the recorder stores the reasoning trace", "zz"),
        "qntmc 165: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 165: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 165: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 165: the recorder stores the reasoning trace", "keyboard"),
        "bssor 165: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 165: the recorder stores the reasoning trace", "AA"),
        "round 165: the recorder stores the reasoning trace",
    ),
    (("round 165: the angel watches the processor run", "key"), "bssxh 165: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 165: the angel watches the processor run", "lemon"), "csgbq 165: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 165: the angel watches the processor run", "a"), "round 165: the angel watches the processor run"),
    (("round 165: the angel watches the processor run", "zz"), "qntmc 165: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 165: the angel watches the processor run", "AgentU"), "ruyaw 165: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 165: the angel watches the processor run", "keyboard"), "bssor 165: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 165: the angel watches the processor run", "AA"), "round 165: the angel watches the processor run"),
    (("round 165: angle of the vector decides the match", "key"), "bssxh 165: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 165: angle of the vector decides the match", "lemon"), "csgbq 165: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 165: angle of the vector decides the match", "a"), "round 165: angle of the vector decides the match"),
    (("round 165: angle of the vector decides the match", "zz"), "qntmc 165: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 165: angle of the vector decides the match", "AgentU"),
        "ruyaw 165: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 165: angle of the vector decides the match", "keyboard"),
        "bssor 165: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 165: angle of the vector decides the match", "AA"), "round 165: angle of the vector decides the match"),
    (
        ("round 165: the candle burns twice as long at night", "key"),
        "bssxh 165: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 165: the candle burns twice as long at night", "lemon"),
        "csgbq 165: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 165: the candle burns twice as long at night", "a"), "round 165: the candle burns twice as long at night"),
    (
        ("round 165: the candle burns twice as long at night", "zz"),
        "qntmc 165: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 165: the candle burns twice as long at night", "AgentU"),
        "ruyaw 165: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 165: the candle burns twice as long at night", "keyboard"),
        "bssor 165: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 165: the candle burns twice as long at night", "AA"),
        "round 165: the candle burns twice as long at night",
    ),
    (("round 165: a mirror of the universe in one line", "key"), "bssxh 165: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 165: a mirror of the universe in one line", "lemon"), "csgbq 165: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 165: a mirror of the universe in one line", "a"), "round 165: a mirror of the universe in one line"),
    (("round 165: a mirror of the universe in one line", "zz"), "qntmc 165: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 165: a mirror of the universe in one line", "AgentU"), "ruyaw 165: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 165: a mirror of the universe in one line", "keyboard"),
        "bssor 165: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 165: a mirror of the universe in one line", "AA"), "round 165: a mirror of the universe in one line"),
    (("round 165: the queue drains before the storm", "key"), "bssxh 165: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 165: the queue drains before the storm", "lemon"), "csgbq 165: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 165: the queue drains before the storm", "a"), "round 165: the queue drains before the storm"),
    (("round 165: the queue drains before the storm", "zz"), "qntmc 165: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 165: the queue drains before the storm", "AgentU"), "ruyaw 165: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 165: the queue drains before the storm", "keyboard"), "bssor 165: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 165: the queue drains before the storm", "AA"), "round 165: the queue drains before the storm"),
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
