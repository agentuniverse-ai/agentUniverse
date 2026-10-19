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
    (("kitten120", "key"), "umrdil120"),
    (("kitten120", "lemon"), "vmfhry120"),
    (("kitten120", "a"), "kitten120"),
    (("kitten120", "zz"), "jhssdm120"),
    (("kitten120", "AgentU"), "koxgxh120"),
    (("kitten120", "keyboard"), "umrusn120"),
    (("kitten120", "AA"), "kitten120"),
    (("sitting120", "key"), "cmrdmlq120"),
    (("sitting120", "lemon"), "dmfhvyk120"),
    (("sitting120", "a"), "sitting120"),
    (("sitting120", "zz"), "rhsshmf120"),
    (("sitting120", "AgentU"), "soxgbhg120"),
    (("sitting120", "keyboard"), "cmruwnx120"),
    (("sitting120", "AA"), "sitting120"),
    (("agent120", "key"), "kkcxx120"),
    (("agent120", "lemon"), "lkqbg120"),
    (("agent120", "a"), "agent120"),
    (("agent120", "zz"), "zfdms120"),
    (("agent120", "AgentU"), "amiam120"),
    (("agent120", "keyboard"), "kkcoh120"),
    (("agent120", "AA"), "agent120"),
    (("angle120", "key"), "krevi120"),
    (("angle120", "lemon"), "lrszr120"),
    (("angle120", "a"), "angle120"),
    (("angle120", "zz"), "zmfkd120"),
    (("angle120", "AgentU"), "atkyx120"),
    (("angle120", "keyboard"), "krems120"),
    (("angle120", "AA"), "angle120"),
    (("universe120", "key"), "ergfipci120"),
    (("universe120", "lemon"), "frujrcwq120"),
    (("universe120", "a"), "universe120"),
    (("universe120", "zz"), "tmhudqrd120"),
    (("universe120", "AgentU"), "utmixlsk120"),
    (("universe120", "keyboard"), "ergwsrjh120"),
    (("universe120", "AA"), "universe120"),
    (("memory120", "key"), "wikyvw120"),
    (("memory120", "lemon"), "xiycej120"),
    (("memory120", "a"), "memory120"),
    (("memory120", "zz"), "ldlnqx120"),
    (("memory120", "AgentU"), "mkqbks120"),
    (("memory120", "keyboard"), "wikpfy120"),
    (("memory120", "AA"), "memory120"),
    (("stream120", "key"), "cxpoek120"),
    (("stream120", "lemon"), "dxdsnx120"),
    (("stream120", "a"), "stream120"),
    (("stream120", "zz"), "rsqdzl120"),
    (("stream120", "AgentU"), "szvrtg120"),
    (("stream120", "keyboard"), "cxpfom120"),
    (("stream120", "AA"), "stream120"),
    (("context120", "key"), "msldivd120"),
    (("context120", "lemon"), "nszhrix120"),
    (("context120", "a"), "context120"),
    (("context120", "zz"), "bnmsdws120"),
    (("context120", "AgentU"), "curgxrt120"),
    (("context120", "keyboard"), "mslusxk120"),
    (("context120", "AA"), "context120"),
    (("knowledge120", "key"), "urmgpcnkc120"),
    (("knowledge120", "lemon"), "vrakyphss120"),
    (("knowledge120", "a"), "knowledge120"),
    (("knowledge120", "zz"), "jmnvkdcfd120"),
    (("knowledge120", "AgentU"), "ktsjeydmi120"),
    (("knowledge120", "keyboard"), "urmxzeujo120"),
    (("knowledge120", "AA"), "knowledge120"),
    (("vector120", "key"), "fiadsp120"),
    (("vector120", "lemon"), "giohbc120"),
    (("vector120", "a"), "vector120"),
    (("vector120", "zz"), "udbsnq120"),
    (("vector120", "AgentU"), "vkgghl120"),
    (("vector120", "keyboard"), "fiaucr120"),
    (("vector120", "AA"), "vector120"),
    (("processor120", "key"), "zvmmiqcsp120"),
    (("processor120", "lemon"), "avaqrdwaf120"),
    (("processor120", "a"), "processor120"),
    (("processor120", "zz"), "oqnbdrrnq120"),
    (("processor120", "AgentU"), "pxspxmsuv120"),
    (("processor120", "keyboard"), "zvmdssjrb120"),
    (("processor120", "AA"), "processor120"),
    (("reasoning120", "key"), "biycslsre120"),
    (("reasoning120", "lemon"), "cimgbymzu120"),
    (("reasoning120", "a"), "reasoning120"),
    (("reasoning120", "zz"), "qdzrnmhmf120"),
    (("reasoning120", "AgentU"), "rkefhhitk120"),
    (("reasoning120", "keyboard"), "biytcnzqq120"),
    (("reasoning120", "AA"), "reasoning120"),
    (("machine120", "key"), "wearmlo120"),
    (("machine120", "lemon"), "xeovvyi120"),
    (("machine120", "a"), "machine120"),
    (("machine120", "zz"), "lzbghmd120"),
    (("machine120", "AgentU"), "mggubhe120"),
    (("machine120", "keyboard"), "weaiwnv120"),
    (("machine120", "AA"), "machine120"),
    (("learning120", "key"), "viybrgxk120"),
    (("learning120", "lemon"), "wimfatrs120"),
    (("learning120", "a"), "learning120"),
    (("learning120", "zz"), "kdzqmhmf120"),
    (("learning120", "AgentU"), "lkeegcnm120"),
    (("learning120", "keyboard"), "viysbiej120"),
    (("learning120", "AA"), "learning120"),
    (("model120", "key"), "wsbop120"),
    (("model120", "lemon"), "xspsy120"),
    (("model120", "a"), "model120"),
    (("model120", "zz"), "lncdk120"),
    (("model120", "AgentU"), "muhre120"),
    (("model120", "keyboard"), "wsbfz120"),
    (("model120", "AA"), "model120"),
    (("token120", "key"), "dsior120"),
    (("token120", "lemon"), "eswsa120"),
    (("token120", "a"), "token120"),
    (("token120", "zz"), "snjdm120"),
    (("token120", "AgentU"), "tuorg120"),
    (("token120", "keyboard"), "dsifb120"),
    (("token120", "AA"), "token120"),
    (("prompt120", "key"), "zvmwtr120"),
    (("prompt120", "lemon"), "avaace120"),
    (("prompt120", "a"), "prompt120"),
    (("prompt120", "zz"), "oqnlos120"),
    (("prompt120", "AgentU"), "pxszin120"),
    (("prompt120", "keyboard"), "zvmndt120"),
    (("prompt120", "AA"), "prompt120"),
    (("session120", "key"), "ciqcmmx120"),
    (("session120", "lemon"), "diegvzr120"),
    (("session120", "a"), "session120"),
    (("session120", "zz"), "rdrrhnm120"),
    (("session120", "AgentU"), "skwfbin120"),
    (("session120", "keyboard"), "ciqtwoe120"),
    (("session120", "AA"), "session120"),
    (("library120", "key"), "vmzbepi120"),
    (("library120", "lemon"), "wmnfncc120"),
    (("library120", "a"), "library120"),
    (("library120", "zz"), "khaqzqx120"),
    (("library120", "AgentU"), "lofetly120"),
    (("library120", "keyboard"), "vmzsorp120"),
    (("library120", "AA"), "library120"),
    (("service120", "key"), "cipfmao120"),
    (("service120", "lemon"), "didjvni120"),
    (("service120", "a"), "service120"),
    (("service120", "zz"), "rdquhbd120"),
    (("service120", "AgentU"), "skvibwe120"),
    (("service120", "keyboard"), "cipwwcv120"),
    (("service120", "AA"), "service120"),
    (("gateway120", "key"), "qeroayi120"),
    (("gateway120", "lemon"), "refsjlc120"),
    (("gateway120", "a"), "gateway120"),
    (("gateway120", "zz"), "fzsdvzx120"),
    (("gateway120", "AgentU"), "ggxrpuy120"),
    (("gateway120", "keyboard"), "qerfkap120"),
    (("gateway120", "AA"), "gateway120"),
    (("storage120", "key"), "cxmbeeo120"),
    (("storage120", "lemon"), "dxafnri120"),
    (("storage120", "a"), "storage120"),
    (("storage120", "zz"), "rsnqzfd120"),
    (("storage120", "AgentU"), "szsetae120"),
    (("storage120", "keyboard"), "cxmsogv120"),
    (("storage120", "AA"), "storage120"),
    (("network120", "key"), "xirgspu120"),
    (("network120", "lemon"), "yifkbco120"),
    (("network120", "a"), "network120"),
    (("network120", "zz"), "mdsvnqj120"),
    (("network120", "AgentU"), "nkxjhlk120"),
    (("network120", "keyboard"), "xirxcrb120"),
    (("network120", "AA"), "network120"),
    (("latency120", "key"), "verorai120"),
    (("latency120", "lemon"), "wefsanc120"),
    (("latency120", "a"), "latency120"),
    (("latency120", "zz"), "kzsdmbx120"),
    (("latency120", "AgentU"), "lgxrgwy120"),
    (("latency120", "keyboard"), "verfbcp120"),
    (("latency120", "AA"), "latency120"),
    (("buffer120", "key"), "lydpip120"),
    (("buffer120", "lemon"), "myrtrc120"),
    (("buffer120", "a"), "buffer120"),
    (("buffer120", "zz"), "ateedq120"),
    (("buffer120", "AgentU"), "bajsxl120"),
    (("buffer120", "keyboard"), "lydgsr120"),
    (("buffer120", "AA"), "buffer120"),
    (("queue120", "key"), "aycei120"),
    (("queue120", "lemon"), "byqir120"),
    (("queue120", "a"), "queue120"),
    (("queue120", "zz"), "ptdtd120"),
    (("queue120", "AgentU"), "qaihx120"),
    (("queue120", "keyboard"), "aycvs120"),
    (("queue120", "AA"), "queue120"),
    (("worker120", "key"), "gspuip120"),
    (("worker120", "lemon"), "hsdyrc120"),
    (("worker120", "a"), "worker120"),
    (("worker120", "zz"), "vnqjdq120"),
    (("worker120", "AgentU"), "wuvxxl120"),
    (("worker120", "keyboard"), "gsplsr120"),
    (("worker120", "AA"), "worker120"),
    (("kernel120", "key"), "uipxij120"),
    (("kernel120", "lemon"), "vidbrw120"),
    (("kernel120", "a"), "kernel120"),
    (("kernel120", "zz"), "jdqmdk120"),
    (("kernel120", "AgentU"), "kkvaxf120"),
    (("kernel120", "keyboard"), "uiposl120"),
    (("kernel120", "AA"), "kernel120"),
    (("signal120", "key"), "cmexej120"),
    (("signal120", "lemon"), "dmsbnw120"),
    (("signal120", "a"), "signal120"),
    (("signal120", "zz"), "rhfmzk120"),
    (("signal120", "AgentU"), "sokatf120"),
    (("signal120", "keyboard"), "cmeool120"),
    (("signal120", "AA"), "signal120"),
    (("packet120", "key"), "zeauir120"),
    (("packet120", "lemon"), "aeoyre120"),
    (("packet120", "a"), "packet120"),
    (("packet120", "zz"), "ozbjds120"),
    (("packet120", "AgentU"), "pggxxn120"),
    (("packet120", "keyboard"), "zealst120"),
    (("packet120", "AA"), "packet120"),
    (("router120", "key"), "bssdip120"),
    (("router120", "lemon"), "csghrc120"),
    (("router120", "a"), "router120"),
    (("router120", "zz"), "qntsdq120"),
    (("router120", "AgentU"), "ruygxl120"),
    (("router120", "keyboard"), "bssusr120"),
    (("router120", "AA"), "router120"),
    (("cluster120", "key"), "mpscxcb120"),
    (("cluster120", "lemon"), "npgggpv120"),
    (("cluster120", "a"), "cluster120"),
    (("cluster120", "zz"), "bktrsdq120"),
    (("cluster120", "AgentU"), "cryfmyr120"),
    (("cluster120", "keyboard"), "mpsthei120"),
    (("cluster120", "AA"), "cluster120"),
    (("mirror120", "key"), "wmpbsp120"),
    (("mirror120", "lemon"), "xmdfbc120"),
    (("mirror120", "a"), "mirror120"),
    (("mirror120", "zz"), "lhqqnq120"),
    (("mirror120", "AgentU"), "movehl120"),
    (("mirror120", "keyboard"), "wmpscr120"),
    (("mirror120", "AA"), "mirror120"),
    (("filter120", "key"), "pmjdip120"),
    (("filter120", "lemon"), "qmxhrc120"),
    (("filter120", "a"), "filter120"),
    (("filter120", "zz"), "ehksdq120"),
    (("filter120", "AgentU"), "fopgxl120"),
    (("filter120", "keyboard"), "pmjusr120"),
    (("filter120", "AA"), "filter120"),
    (("ranking120", "key"), "belumlq120"),
    (("ranking120", "lemon"), "cezyvyk120"),
    (("ranking120", "a"), "ranking120"),
    (("ranking120", "zz"), "qzmjhmf120"),
    (("ranking120", "AgentU"), "rgrxbhg120"),
    (("ranking120", "keyboard"), "bellwnx120"),
    (("ranking120", "AA"), "ranking120"),
    (("encoding120", "key"), "orayhgxk120"),
    (("encoding120", "lemon"), "procqtrs120"),
    (("encoding120", "a"), "encoding120"),
    (("encoding120", "zz"), "dmbnchmf120"),
    (("encoding120", "AgentU"), "etgbwcnm120"),
    (("encoding120", "keyboard"), "orapriej120"),
    (("encoding120", "AA"), "encoding120"),
    (("mapping120", "key"), "wenzmlq120"),
    (("mapping120", "lemon"), "xebdvyk120"),
    (("mapping120", "a"), "mapping120"),
    (("mapping120", "zz"), "lzoohmf120"),
    (("mapping120", "AgentU"), "mgtcbhg120"),
    (("mapping120", "keyboard"), "wenqwnx120"),
    (("mapping120", "AA"), "mapping120"),
    (("record120", "key"), "biayvb120"),
    (("record120", "lemon"), "cioceo120"),
    (("record120", "a"), "record120"),
    (("record120", "zz"), "qdbnqc120"),
    (("record120", "AgentU"), "rkgbkx120"),
    (("record120", "keyboard"), "biapfd120"),
    (("record120", "AA"), "record120"),
    (("candle120", "key"), "melnpc120"),
    (("candle120", "lemon"), "nezryp120"),
    (("candle120", "a"), "candle120"),
    (("candle120", "zz"), "bzmckd120"),
    (("candle120", "AgentU"), "cgrqey120"),
    (("candle120", "keyboard"), "meleze120"),
    (("candle120", "AA"), "candle120"),
    (("thread120", "key"), "dlpoeb120"),
    (("thread120", "lemon"), "eldsno120"),
    (("thread120", "a"), "thread120"),
    (("thread120", "zz"), "sgqdzc120"),
    (("thread120", "AgentU"), "tnvrtx120"),
    (("thread120", "keyboard"), "dlpfod120"),
    (("thread120", "AA"), "thread120"),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 120: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 120: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "a"),
        "round 120: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 120: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 120: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 120: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", "AA"),
        "round 120: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "key"),
        "bssxh 120: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 120: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "a"),
        "round 120: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 120: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 120: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 120: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", "AA"),
        "round 120: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 120: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 120: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "a"),
        "round 120: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 120: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 120: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 120: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", "AA"),
        "round 120: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 120: the processor reads the record then stops", "key"),
        "bssxh 120: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 120: the processor reads the record then stops", "lemon"),
        "csgbq 120: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 120: the processor reads the record then stops", "a"),
        "round 120: the processor reads the record then stops",
    ),
    (
        ("round 120: the processor reads the record then stops", "zz"),
        "qntmc 120: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 120: the processor reads the record then stops", "AgentU"),
        "ruyaw 120: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 120: the processor reads the record then stops", "keyboard"),
        "bssor 120: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 120: the processor reads the record then stops", "AA"),
        "round 120: the processor reads the record then stops",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "key"),
        "bssxh 120: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "lemon"),
        "csgbq 120: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "a"),
        "round 120: a worker pulls the next task from the queue",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "zz"),
        "qntmc 120: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 120: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "keyboard"),
        "bssor 120: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 120: a worker pulls the next task from the queue", "AA"),
        "round 120: a worker pulls the next task from the queue",
    ),
    (
        ("round 120: signals travel through the network layer", "key"),
        "bssxh 120: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 120: signals travel through the network layer", "lemon"),
        "csgbq 120: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 120: signals travel through the network layer", "a"),
        "round 120: signals travel through the network layer",
    ),
    (
        ("round 120: signals travel through the network layer", "zz"),
        "qntmc 120: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 120: signals travel through the network layer", "AgentU"),
        "ruyaw 120: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 120: signals travel through the network layer", "keyboard"),
        "bssor 120: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 120: signals travel through the network layer", "AA"),
        "round 120: signals travel through the network layer",
    ),
    (
        ("round 120: the gateway routes each request by policy", "key"),
        "bssxh 120: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 120: the gateway routes each request by policy", "lemon"),
        "csgbq 120: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 120: the gateway routes each request by policy", "a"),
        "round 120: the gateway routes each request by policy",
    ),
    (
        ("round 120: the gateway routes each request by policy", "zz"),
        "qntmc 120: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 120: the gateway routes each request by policy", "AgentU"),
        "ruyaw 120: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 120: the gateway routes each request by policy", "keyboard"),
        "bssor 120: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 120: the gateway routes each request by policy", "AA"),
        "round 120: the gateway routes each request by policy",
    ),
    (("round 120: memory grows until the buffer is full", "key"), "bssxh 120: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 120: memory grows until the buffer is full", "lemon"), "csgbq 120: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 120: memory grows until the buffer is full", "a"), "round 120: memory grows until the buffer is full"),
    (("round 120: memory grows until the buffer is full", "zz"), "qntmc 120: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 120: memory grows until the buffer is full", "AgentU"),
        "ruyaw 120: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 120: memory grows until the buffer is full", "keyboard"),
        "bssor 120: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 120: memory grows until the buffer is full", "AA"), "round 120: memory grows until the buffer is full"),
    (("round 120: the cluster mirrors every packet twice", "key"), "bssxh 120: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 120: the cluster mirrors every packet twice", "lemon"),
        "csgbq 120: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 120: the cluster mirrors every packet twice", "a"), "round 120: the cluster mirrors every packet twice"),
    (("round 120: the cluster mirrors every packet twice", "zz"), "qntmc 120: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 120: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 120: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 120: the cluster mirrors every packet twice", "keyboard"),
        "bssor 120: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 120: the cluster mirrors every packet twice", "AA"), "round 120: the cluster mirrors every packet twice"),
    (
        ("round 120: ranking uses tokens learned from the corpus", "key"),
        "bssxh 120: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 120: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", "a"),
        "round 120: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 120: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 120: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 120: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", "AA"),
        "round 120: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 120: a long session ends when the candle dies", "key"),
        "bssxh 120: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 120: a long session ends when the candle dies", "lemon"),
        "csgbq 120: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 120: a long session ends when the candle dies", "a"),
        "round 120: a long session ends when the candle dies",
    ),
    (
        ("round 120: a long session ends when the candle dies", "zz"),
        "qntmc 120: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 120: a long session ends when the candle dies", "AgentU"),
        "ruyaw 120: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 120: a long session ends when the candle dies", "keyboard"),
        "bssor 120: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 120: a long session ends when the candle dies", "AA"),
        "round 120: a long session ends when the candle dies",
    ),
    (("round 120: encode the prompt then map the result", "key"), "bssxh 120: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 120: encode the prompt then map the result", "lemon"), "csgbq 120: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 120: encode the prompt then map the result", "a"), "round 120: encode the prompt then map the result"),
    (("round 120: encode the prompt then map the result", "zz"), "qntmc 120: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 120: encode the prompt then map the result", "AgentU"),
        "ruyaw 120: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 120: encode the prompt then map the result", "keyboard"),
        "bssor 120: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 120: encode the prompt then map the result", "AA"), "round 120: encode the prompt then map the result"),
    (("round 120: the kernel wakes the worker at dawn", "key"), "bssxh 120: rri iovlop ukocc xfo ambocb er neux"),
    (("round 120: the kernel wakes the worker at dawn", "lemon"), "csgbq 120: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 120: the kernel wakes the worker at dawn", "a"), "round 120: the kernel wakes the worker at dawn"),
    (("round 120: the kernel wakes the worker at dawn", "zz"), "qntmc 120: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 120: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 120: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 120: the kernel wakes the worker at dawn", "keyboard"), "bssor 120: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 120: the kernel wakes the worker at dawn", "AA"), "round 120: the kernel wakes the worker at dawn"),
    (("round 120: service latency drops after the patch", "key"), "bssxh 120: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 120: service latency drops after the patch", "lemon"), "csgbq 120: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 120: service latency drops after the patch", "a"), "round 120: service latency drops after the patch"),
    (("round 120: service latency drops after the patch", "zz"), "qntmc 120: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 120: service latency drops after the patch", "AgentU"),
        "ruyaw 120: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 120: service latency drops after the patch", "keyboard"),
        "bssor 120: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 120: service latency drops after the patch", "AA"), "round 120: service latency drops after the patch"),
    (
        ("round 120: the library caches every vector it sees", "key"),
        "bssxh 120: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 120: the library caches every vector it sees", "lemon"),
        "csgbq 120: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 120: the library caches every vector it sees", "a"), "round 120: the library caches every vector it sees"),
    (
        ("round 120: the library caches every vector it sees", "zz"),
        "qntmc 120: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 120: the library caches every vector it sees", "AgentU"),
        "ruyaw 120: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 120: the library caches every vector it sees", "keyboard"),
        "bssor 120: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 120: the library caches every vector it sees", "AA"),
        "round 120: the library caches every vector it sees",
    ),
    (("round 120: agents argue then the debate resolves", "key"), "bssxh 120: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 120: agents argue then the debate resolves", "lemon"), "csgbq 120: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 120: agents argue then the debate resolves", "a"), "round 120: agents argue then the debate resolves"),
    (("round 120: agents argue then the debate resolves", "zz"), "qntmc 120: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 120: agents argue then the debate resolves", "AgentU"),
        "ruyaw 120: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 120: agents argue then the debate resolves", "keyboard"),
        "bssor 120: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 120: agents argue then the debate resolves", "AA"), "round 120: agents argue then the debate resolves"),
    (("round 120: the filter keeps only strong matches", "key"), "bssxh 120: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 120: the filter keeps only strong matches", "lemon"), "csgbq 120: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 120: the filter keeps only strong matches", "a"), "round 120: the filter keeps only strong matches"),
    (("round 120: the filter keeps only strong matches", "zz"), "qntmc 120: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 120: the filter keeps only strong matches", "AgentU"), "ruyaw 120: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 120: the filter keeps only strong matches", "keyboard"),
        "bssor 120: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 120: the filter keeps only strong matches", "AA"), "round 120: the filter keeps only strong matches"),
    (("round 120: the model answers with a short reply", "key"), "bssxh 120: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 120: the model answers with a short reply", "lemon"), "csgbq 120: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 120: the model answers with a short reply", "a"), "round 120: the model answers with a short reply"),
    (("round 120: the model answers with a short reply", "zz"), "qntmc 120: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 120: the model answers with a short reply", "AgentU"), "ruyaw 120: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 120: the model answers with a short reply", "keyboard"),
        "bssor 120: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 120: the model answers with a short reply", "AA"), "round 120: the model answers with a short reply"),
    (
        ("round 120: the recorder stores the reasoning trace", "key"),
        "bssxh 120: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 120: the recorder stores the reasoning trace", "lemon"),
        "csgbq 120: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 120: the recorder stores the reasoning trace", "a"), "round 120: the recorder stores the reasoning trace"),
    (
        ("round 120: the recorder stores the reasoning trace", "zz"),
        "qntmc 120: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 120: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 120: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 120: the recorder stores the reasoning trace", "keyboard"),
        "bssor 120: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 120: the recorder stores the reasoning trace", "AA"),
        "round 120: the recorder stores the reasoning trace",
    ),
    (("round 120: the angel watches the processor run", "key"), "bssxh 120: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 120: the angel watches the processor run", "lemon"), "csgbq 120: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 120: the angel watches the processor run", "a"), "round 120: the angel watches the processor run"),
    (("round 120: the angel watches the processor run", "zz"), "qntmc 120: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 120: the angel watches the processor run", "AgentU"), "ruyaw 120: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 120: the angel watches the processor run", "keyboard"), "bssor 120: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 120: the angel watches the processor run", "AA"), "round 120: the angel watches the processor run"),
    (("round 120: angle of the vector decides the match", "key"), "bssxh 120: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 120: angle of the vector decides the match", "lemon"), "csgbq 120: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 120: angle of the vector decides the match", "a"), "round 120: angle of the vector decides the match"),
    (("round 120: angle of the vector decides the match", "zz"), "qntmc 120: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 120: angle of the vector decides the match", "AgentU"),
        "ruyaw 120: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 120: angle of the vector decides the match", "keyboard"),
        "bssor 120: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 120: angle of the vector decides the match", "AA"), "round 120: angle of the vector decides the match"),
    (
        ("round 120: the candle burns twice as long at night", "key"),
        "bssxh 120: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 120: the candle burns twice as long at night", "lemon"),
        "csgbq 120: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 120: the candle burns twice as long at night", "a"), "round 120: the candle burns twice as long at night"),
    (
        ("round 120: the candle burns twice as long at night", "zz"),
        "qntmc 120: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 120: the candle burns twice as long at night", "AgentU"),
        "ruyaw 120: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 120: the candle burns twice as long at night", "keyboard"),
        "bssor 120: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 120: the candle burns twice as long at night", "AA"),
        "round 120: the candle burns twice as long at night",
    ),
    (("round 120: a mirror of the universe in one line", "key"), "bssxh 120: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 120: a mirror of the universe in one line", "lemon"), "csgbq 120: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 120: a mirror of the universe in one line", "a"), "round 120: a mirror of the universe in one line"),
    (("round 120: a mirror of the universe in one line", "zz"), "qntmc 120: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 120: a mirror of the universe in one line", "AgentU"), "ruyaw 120: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 120: a mirror of the universe in one line", "keyboard"),
        "bssor 120: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 120: a mirror of the universe in one line", "AA"), "round 120: a mirror of the universe in one line"),
    (("round 120: the queue drains before the storm", "key"), "bssxh 120: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 120: the queue drains before the storm", "lemon"), "csgbq 120: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 120: the queue drains before the storm", "a"), "round 120: the queue drains before the storm"),
    (("round 120: the queue drains before the storm", "zz"), "qntmc 120: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 120: the queue drains before the storm", "AgentU"), "ruyaw 120: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 120: the queue drains before the storm", "keyboard"), "bssor 120: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 120: the queue drains before the storm", "AA"), "round 120: the queue drains before the storm"),
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
