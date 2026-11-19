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
    (("kitten153", "key"), "umrdil153"),
    (("kitten153", "lemon"), "vmfhry153"),
    (("kitten153", "a"), "kitten153"),
    (("kitten153", "zz"), "jhssdm153"),
    (("kitten153", "AgentU"), "koxgxh153"),
    (("kitten153", "keyboard"), "umrusn153"),
    (("kitten153", "AA"), "kitten153"),
    (("sitting153", "key"), "cmrdmlq153"),
    (("sitting153", "lemon"), "dmfhvyk153"),
    (("sitting153", "a"), "sitting153"),
    (("sitting153", "zz"), "rhsshmf153"),
    (("sitting153", "AgentU"), "soxgbhg153"),
    (("sitting153", "keyboard"), "cmruwnx153"),
    (("sitting153", "AA"), "sitting153"),
    (("agent153", "key"), "kkcxx153"),
    (("agent153", "lemon"), "lkqbg153"),
    (("agent153", "a"), "agent153"),
    (("agent153", "zz"), "zfdms153"),
    (("agent153", "AgentU"), "amiam153"),
    (("agent153", "keyboard"), "kkcoh153"),
    (("agent153", "AA"), "agent153"),
    (("angle153", "key"), "krevi153"),
    (("angle153", "lemon"), "lrszr153"),
    (("angle153", "a"), "angle153"),
    (("angle153", "zz"), "zmfkd153"),
    (("angle153", "AgentU"), "atkyx153"),
    (("angle153", "keyboard"), "krems153"),
    (("angle153", "AA"), "angle153"),
    (("universe153", "key"), "ergfipci153"),
    (("universe153", "lemon"), "frujrcwq153"),
    (("universe153", "a"), "universe153"),
    (("universe153", "zz"), "tmhudqrd153"),
    (("universe153", "AgentU"), "utmixlsk153"),
    (("universe153", "keyboard"), "ergwsrjh153"),
    (("universe153", "AA"), "universe153"),
    (("memory153", "key"), "wikyvw153"),
    (("memory153", "lemon"), "xiycej153"),
    (("memory153", "a"), "memory153"),
    (("memory153", "zz"), "ldlnqx153"),
    (("memory153", "AgentU"), "mkqbks153"),
    (("memory153", "keyboard"), "wikpfy153"),
    (("memory153", "AA"), "memory153"),
    (("stream153", "key"), "cxpoek153"),
    (("stream153", "lemon"), "dxdsnx153"),
    (("stream153", "a"), "stream153"),
    (("stream153", "zz"), "rsqdzl153"),
    (("stream153", "AgentU"), "szvrtg153"),
    (("stream153", "keyboard"), "cxpfom153"),
    (("stream153", "AA"), "stream153"),
    (("context153", "key"), "msldivd153"),
    (("context153", "lemon"), "nszhrix153"),
    (("context153", "a"), "context153"),
    (("context153", "zz"), "bnmsdws153"),
    (("context153", "AgentU"), "curgxrt153"),
    (("context153", "keyboard"), "mslusxk153"),
    (("context153", "AA"), "context153"),
    (("knowledge153", "key"), "urmgpcnkc153"),
    (("knowledge153", "lemon"), "vrakyphss153"),
    (("knowledge153", "a"), "knowledge153"),
    (("knowledge153", "zz"), "jmnvkdcfd153"),
    (("knowledge153", "AgentU"), "ktsjeydmi153"),
    (("knowledge153", "keyboard"), "urmxzeujo153"),
    (("knowledge153", "AA"), "knowledge153"),
    (("vector153", "key"), "fiadsp153"),
    (("vector153", "lemon"), "giohbc153"),
    (("vector153", "a"), "vector153"),
    (("vector153", "zz"), "udbsnq153"),
    (("vector153", "AgentU"), "vkgghl153"),
    (("vector153", "keyboard"), "fiaucr153"),
    (("vector153", "AA"), "vector153"),
    (("processor153", "key"), "zvmmiqcsp153"),
    (("processor153", "lemon"), "avaqrdwaf153"),
    (("processor153", "a"), "processor153"),
    (("processor153", "zz"), "oqnbdrrnq153"),
    (("processor153", "AgentU"), "pxspxmsuv153"),
    (("processor153", "keyboard"), "zvmdssjrb153"),
    (("processor153", "AA"), "processor153"),
    (("reasoning153", "key"), "biycslsre153"),
    (("reasoning153", "lemon"), "cimgbymzu153"),
    (("reasoning153", "a"), "reasoning153"),
    (("reasoning153", "zz"), "qdzrnmhmf153"),
    (("reasoning153", "AgentU"), "rkefhhitk153"),
    (("reasoning153", "keyboard"), "biytcnzqq153"),
    (("reasoning153", "AA"), "reasoning153"),
    (("machine153", "key"), "wearmlo153"),
    (("machine153", "lemon"), "xeovvyi153"),
    (("machine153", "a"), "machine153"),
    (("machine153", "zz"), "lzbghmd153"),
    (("machine153", "AgentU"), "mggubhe153"),
    (("machine153", "keyboard"), "weaiwnv153"),
    (("machine153", "AA"), "machine153"),
    (("learning153", "key"), "viybrgxk153"),
    (("learning153", "lemon"), "wimfatrs153"),
    (("learning153", "a"), "learning153"),
    (("learning153", "zz"), "kdzqmhmf153"),
    (("learning153", "AgentU"), "lkeegcnm153"),
    (("learning153", "keyboard"), "viysbiej153"),
    (("learning153", "AA"), "learning153"),
    (("model153", "key"), "wsbop153"),
    (("model153", "lemon"), "xspsy153"),
    (("model153", "a"), "model153"),
    (("model153", "zz"), "lncdk153"),
    (("model153", "AgentU"), "muhre153"),
    (("model153", "keyboard"), "wsbfz153"),
    (("model153", "AA"), "model153"),
    (("token153", "key"), "dsior153"),
    (("token153", "lemon"), "eswsa153"),
    (("token153", "a"), "token153"),
    (("token153", "zz"), "snjdm153"),
    (("token153", "AgentU"), "tuorg153"),
    (("token153", "keyboard"), "dsifb153"),
    (("token153", "AA"), "token153"),
    (("prompt153", "key"), "zvmwtr153"),
    (("prompt153", "lemon"), "avaace153"),
    (("prompt153", "a"), "prompt153"),
    (("prompt153", "zz"), "oqnlos153"),
    (("prompt153", "AgentU"), "pxszin153"),
    (("prompt153", "keyboard"), "zvmndt153"),
    (("prompt153", "AA"), "prompt153"),
    (("session153", "key"), "ciqcmmx153"),
    (("session153", "lemon"), "diegvzr153"),
    (("session153", "a"), "session153"),
    (("session153", "zz"), "rdrrhnm153"),
    (("session153", "AgentU"), "skwfbin153"),
    (("session153", "keyboard"), "ciqtwoe153"),
    (("session153", "AA"), "session153"),
    (("library153", "key"), "vmzbepi153"),
    (("library153", "lemon"), "wmnfncc153"),
    (("library153", "a"), "library153"),
    (("library153", "zz"), "khaqzqx153"),
    (("library153", "AgentU"), "lofetly153"),
    (("library153", "keyboard"), "vmzsorp153"),
    (("library153", "AA"), "library153"),
    (("service153", "key"), "cipfmao153"),
    (("service153", "lemon"), "didjvni153"),
    (("service153", "a"), "service153"),
    (("service153", "zz"), "rdquhbd153"),
    (("service153", "AgentU"), "skvibwe153"),
    (("service153", "keyboard"), "cipwwcv153"),
    (("service153", "AA"), "service153"),
    (("gateway153", "key"), "qeroayi153"),
    (("gateway153", "lemon"), "refsjlc153"),
    (("gateway153", "a"), "gateway153"),
    (("gateway153", "zz"), "fzsdvzx153"),
    (("gateway153", "AgentU"), "ggxrpuy153"),
    (("gateway153", "keyboard"), "qerfkap153"),
    (("gateway153", "AA"), "gateway153"),
    (("storage153", "key"), "cxmbeeo153"),
    (("storage153", "lemon"), "dxafnri153"),
    (("storage153", "a"), "storage153"),
    (("storage153", "zz"), "rsnqzfd153"),
    (("storage153", "AgentU"), "szsetae153"),
    (("storage153", "keyboard"), "cxmsogv153"),
    (("storage153", "AA"), "storage153"),
    (("network153", "key"), "xirgspu153"),
    (("network153", "lemon"), "yifkbco153"),
    (("network153", "a"), "network153"),
    (("network153", "zz"), "mdsvnqj153"),
    (("network153", "AgentU"), "nkxjhlk153"),
    (("network153", "keyboard"), "xirxcrb153"),
    (("network153", "AA"), "network153"),
    (("latency153", "key"), "verorai153"),
    (("latency153", "lemon"), "wefsanc153"),
    (("latency153", "a"), "latency153"),
    (("latency153", "zz"), "kzsdmbx153"),
    (("latency153", "AgentU"), "lgxrgwy153"),
    (("latency153", "keyboard"), "verfbcp153"),
    (("latency153", "AA"), "latency153"),
    (("buffer153", "key"), "lydpip153"),
    (("buffer153", "lemon"), "myrtrc153"),
    (("buffer153", "a"), "buffer153"),
    (("buffer153", "zz"), "ateedq153"),
    (("buffer153", "AgentU"), "bajsxl153"),
    (("buffer153", "keyboard"), "lydgsr153"),
    (("buffer153", "AA"), "buffer153"),
    (("queue153", "key"), "aycei153"),
    (("queue153", "lemon"), "byqir153"),
    (("queue153", "a"), "queue153"),
    (("queue153", "zz"), "ptdtd153"),
    (("queue153", "AgentU"), "qaihx153"),
    (("queue153", "keyboard"), "aycvs153"),
    (("queue153", "AA"), "queue153"),
    (("worker153", "key"), "gspuip153"),
    (("worker153", "lemon"), "hsdyrc153"),
    (("worker153", "a"), "worker153"),
    (("worker153", "zz"), "vnqjdq153"),
    (("worker153", "AgentU"), "wuvxxl153"),
    (("worker153", "keyboard"), "gsplsr153"),
    (("worker153", "AA"), "worker153"),
    (("kernel153", "key"), "uipxij153"),
    (("kernel153", "lemon"), "vidbrw153"),
    (("kernel153", "a"), "kernel153"),
    (("kernel153", "zz"), "jdqmdk153"),
    (("kernel153", "AgentU"), "kkvaxf153"),
    (("kernel153", "keyboard"), "uiposl153"),
    (("kernel153", "AA"), "kernel153"),
    (("signal153", "key"), "cmexej153"),
    (("signal153", "lemon"), "dmsbnw153"),
    (("signal153", "a"), "signal153"),
    (("signal153", "zz"), "rhfmzk153"),
    (("signal153", "AgentU"), "sokatf153"),
    (("signal153", "keyboard"), "cmeool153"),
    (("signal153", "AA"), "signal153"),
    (("packet153", "key"), "zeauir153"),
    (("packet153", "lemon"), "aeoyre153"),
    (("packet153", "a"), "packet153"),
    (("packet153", "zz"), "ozbjds153"),
    (("packet153", "AgentU"), "pggxxn153"),
    (("packet153", "keyboard"), "zealst153"),
    (("packet153", "AA"), "packet153"),
    (("router153", "key"), "bssdip153"),
    (("router153", "lemon"), "csghrc153"),
    (("router153", "a"), "router153"),
    (("router153", "zz"), "qntsdq153"),
    (("router153", "AgentU"), "ruygxl153"),
    (("router153", "keyboard"), "bssusr153"),
    (("router153", "AA"), "router153"),
    (("cluster153", "key"), "mpscxcb153"),
    (("cluster153", "lemon"), "npgggpv153"),
    (("cluster153", "a"), "cluster153"),
    (("cluster153", "zz"), "bktrsdq153"),
    (("cluster153", "AgentU"), "cryfmyr153"),
    (("cluster153", "keyboard"), "mpsthei153"),
    (("cluster153", "AA"), "cluster153"),
    (("mirror153", "key"), "wmpbsp153"),
    (("mirror153", "lemon"), "xmdfbc153"),
    (("mirror153", "a"), "mirror153"),
    (("mirror153", "zz"), "lhqqnq153"),
    (("mirror153", "AgentU"), "movehl153"),
    (("mirror153", "keyboard"), "wmpscr153"),
    (("mirror153", "AA"), "mirror153"),
    (("filter153", "key"), "pmjdip153"),
    (("filter153", "lemon"), "qmxhrc153"),
    (("filter153", "a"), "filter153"),
    (("filter153", "zz"), "ehksdq153"),
    (("filter153", "AgentU"), "fopgxl153"),
    (("filter153", "keyboard"), "pmjusr153"),
    (("filter153", "AA"), "filter153"),
    (("ranking153", "key"), "belumlq153"),
    (("ranking153", "lemon"), "cezyvyk153"),
    (("ranking153", "a"), "ranking153"),
    (("ranking153", "zz"), "qzmjhmf153"),
    (("ranking153", "AgentU"), "rgrxbhg153"),
    (("ranking153", "keyboard"), "bellwnx153"),
    (("ranking153", "AA"), "ranking153"),
    (("encoding153", "key"), "orayhgxk153"),
    (("encoding153", "lemon"), "procqtrs153"),
    (("encoding153", "a"), "encoding153"),
    (("encoding153", "zz"), "dmbnchmf153"),
    (("encoding153", "AgentU"), "etgbwcnm153"),
    (("encoding153", "keyboard"), "orapriej153"),
    (("encoding153", "AA"), "encoding153"),
    (("mapping153", "key"), "wenzmlq153"),
    (("mapping153", "lemon"), "xebdvyk153"),
    (("mapping153", "a"), "mapping153"),
    (("mapping153", "zz"), "lzoohmf153"),
    (("mapping153", "AgentU"), "mgtcbhg153"),
    (("mapping153", "keyboard"), "wenqwnx153"),
    (("mapping153", "AA"), "mapping153"),
    (("record153", "key"), "biayvb153"),
    (("record153", "lemon"), "cioceo153"),
    (("record153", "a"), "record153"),
    (("record153", "zz"), "qdbnqc153"),
    (("record153", "AgentU"), "rkgbkx153"),
    (("record153", "keyboard"), "biapfd153"),
    (("record153", "AA"), "record153"),
    (("candle153", "key"), "melnpc153"),
    (("candle153", "lemon"), "nezryp153"),
    (("candle153", "a"), "candle153"),
    (("candle153", "zz"), "bzmckd153"),
    (("candle153", "AgentU"), "cgrqey153"),
    (("candle153", "keyboard"), "meleze153"),
    (("candle153", "AA"), "candle153"),
    (("thread153", "key"), "dlpoeb153"),
    (("thread153", "lemon"), "eldsno153"),
    (("thread153", "a"), "thread153"),
    (("thread153", "zz"), "sgqdzc153"),
    (("thread153", "AgentU"), "tnvrtx153"),
    (("thread153", "keyboard"), "dlpfod153"),
    (("thread153", "AA"), "thread153"),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 153: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 153: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "a"),
        "round 153: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 153: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 153: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 153: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", "AA"),
        "round 153: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "key"),
        "bssxh 153: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 153: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "a"),
        "round 153: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 153: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 153: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 153: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", "AA"),
        "round 153: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 153: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 153: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "a"),
        "round 153: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 153: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 153: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 153: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", "AA"),
        "round 153: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 153: the processor reads the record then stops", "key"),
        "bssxh 153: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 153: the processor reads the record then stops", "lemon"),
        "csgbq 153: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 153: the processor reads the record then stops", "a"),
        "round 153: the processor reads the record then stops",
    ),
    (
        ("round 153: the processor reads the record then stops", "zz"),
        "qntmc 153: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 153: the processor reads the record then stops", "AgentU"),
        "ruyaw 153: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 153: the processor reads the record then stops", "keyboard"),
        "bssor 153: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 153: the processor reads the record then stops", "AA"),
        "round 153: the processor reads the record then stops",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "key"),
        "bssxh 153: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "lemon"),
        "csgbq 153: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "a"),
        "round 153: a worker pulls the next task from the queue",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "zz"),
        "qntmc 153: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 153: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "keyboard"),
        "bssor 153: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 153: a worker pulls the next task from the queue", "AA"),
        "round 153: a worker pulls the next task from the queue",
    ),
    (
        ("round 153: signals travel through the network layer", "key"),
        "bssxh 153: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 153: signals travel through the network layer", "lemon"),
        "csgbq 153: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 153: signals travel through the network layer", "a"),
        "round 153: signals travel through the network layer",
    ),
    (
        ("round 153: signals travel through the network layer", "zz"),
        "qntmc 153: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 153: signals travel through the network layer", "AgentU"),
        "ruyaw 153: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 153: signals travel through the network layer", "keyboard"),
        "bssor 153: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 153: signals travel through the network layer", "AA"),
        "round 153: signals travel through the network layer",
    ),
    (
        ("round 153: the gateway routes each request by policy", "key"),
        "bssxh 153: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 153: the gateway routes each request by policy", "lemon"),
        "csgbq 153: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 153: the gateway routes each request by policy", "a"),
        "round 153: the gateway routes each request by policy",
    ),
    (
        ("round 153: the gateway routes each request by policy", "zz"),
        "qntmc 153: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 153: the gateway routes each request by policy", "AgentU"),
        "ruyaw 153: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 153: the gateway routes each request by policy", "keyboard"),
        "bssor 153: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 153: the gateway routes each request by policy", "AA"),
        "round 153: the gateway routes each request by policy",
    ),
    (("round 153: memory grows until the buffer is full", "key"), "bssxh 153: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 153: memory grows until the buffer is full", "lemon"), "csgbq 153: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 153: memory grows until the buffer is full", "a"), "round 153: memory grows until the buffer is full"),
    (("round 153: memory grows until the buffer is full", "zz"), "qntmc 153: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 153: memory grows until the buffer is full", "AgentU"),
        "ruyaw 153: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 153: memory grows until the buffer is full", "keyboard"),
        "bssor 153: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 153: memory grows until the buffer is full", "AA"), "round 153: memory grows until the buffer is full"),
    (("round 153: the cluster mirrors every packet twice", "key"), "bssxh 153: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 153: the cluster mirrors every packet twice", "lemon"),
        "csgbq 153: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 153: the cluster mirrors every packet twice", "a"), "round 153: the cluster mirrors every packet twice"),
    (("round 153: the cluster mirrors every packet twice", "zz"), "qntmc 153: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 153: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 153: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 153: the cluster mirrors every packet twice", "keyboard"),
        "bssor 153: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 153: the cluster mirrors every packet twice", "AA"), "round 153: the cluster mirrors every packet twice"),
    (
        ("round 153: ranking uses tokens learned from the corpus", "key"),
        "bssxh 153: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 153: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", "a"),
        "round 153: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 153: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 153: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 153: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", "AA"),
        "round 153: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 153: a long session ends when the candle dies", "key"),
        "bssxh 153: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 153: a long session ends when the candle dies", "lemon"),
        "csgbq 153: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 153: a long session ends when the candle dies", "a"),
        "round 153: a long session ends when the candle dies",
    ),
    (
        ("round 153: a long session ends when the candle dies", "zz"),
        "qntmc 153: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 153: a long session ends when the candle dies", "AgentU"),
        "ruyaw 153: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 153: a long session ends when the candle dies", "keyboard"),
        "bssor 153: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 153: a long session ends when the candle dies", "AA"),
        "round 153: a long session ends when the candle dies",
    ),
    (("round 153: encode the prompt then map the result", "key"), "bssxh 153: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 153: encode the prompt then map the result", "lemon"), "csgbq 153: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 153: encode the prompt then map the result", "a"), "round 153: encode the prompt then map the result"),
    (("round 153: encode the prompt then map the result", "zz"), "qntmc 153: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 153: encode the prompt then map the result", "AgentU"),
        "ruyaw 153: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 153: encode the prompt then map the result", "keyboard"),
        "bssor 153: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 153: encode the prompt then map the result", "AA"), "round 153: encode the prompt then map the result"),
    (("round 153: the kernel wakes the worker at dawn", "key"), "bssxh 153: rri iovlop ukocc xfo ambocb er neux"),
    (("round 153: the kernel wakes the worker at dawn", "lemon"), "csgbq 153: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 153: the kernel wakes the worker at dawn", "a"), "round 153: the kernel wakes the worker at dawn"),
    (("round 153: the kernel wakes the worker at dawn", "zz"), "qntmc 153: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 153: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 153: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 153: the kernel wakes the worker at dawn", "keyboard"), "bssor 153: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 153: the kernel wakes the worker at dawn", "AA"), "round 153: the kernel wakes the worker at dawn"),
    (("round 153: service latency drops after the patch", "key"), "bssxh 153: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 153: service latency drops after the patch", "lemon"), "csgbq 153: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 153: service latency drops after the patch", "a"), "round 153: service latency drops after the patch"),
    (("round 153: service latency drops after the patch", "zz"), "qntmc 153: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 153: service latency drops after the patch", "AgentU"),
        "ruyaw 153: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 153: service latency drops after the patch", "keyboard"),
        "bssor 153: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 153: service latency drops after the patch", "AA"), "round 153: service latency drops after the patch"),
    (
        ("round 153: the library caches every vector it sees", "key"),
        "bssxh 153: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 153: the library caches every vector it sees", "lemon"),
        "csgbq 153: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 153: the library caches every vector it sees", "a"), "round 153: the library caches every vector it sees"),
    (
        ("round 153: the library caches every vector it sees", "zz"),
        "qntmc 153: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 153: the library caches every vector it sees", "AgentU"),
        "ruyaw 153: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 153: the library caches every vector it sees", "keyboard"),
        "bssor 153: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 153: the library caches every vector it sees", "AA"),
        "round 153: the library caches every vector it sees",
    ),
    (("round 153: agents argue then the debate resolves", "key"), "bssxh 153: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 153: agents argue then the debate resolves", "lemon"), "csgbq 153: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 153: agents argue then the debate resolves", "a"), "round 153: agents argue then the debate resolves"),
    (("round 153: agents argue then the debate resolves", "zz"), "qntmc 153: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 153: agents argue then the debate resolves", "AgentU"),
        "ruyaw 153: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 153: agents argue then the debate resolves", "keyboard"),
        "bssor 153: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 153: agents argue then the debate resolves", "AA"), "round 153: agents argue then the debate resolves"),
    (("round 153: the filter keeps only strong matches", "key"), "bssxh 153: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 153: the filter keeps only strong matches", "lemon"), "csgbq 153: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 153: the filter keeps only strong matches", "a"), "round 153: the filter keeps only strong matches"),
    (("round 153: the filter keeps only strong matches", "zz"), "qntmc 153: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 153: the filter keeps only strong matches", "AgentU"), "ruyaw 153: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 153: the filter keeps only strong matches", "keyboard"),
        "bssor 153: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 153: the filter keeps only strong matches", "AA"), "round 153: the filter keeps only strong matches"),
    (("round 153: the model answers with a short reply", "key"), "bssxh 153: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 153: the model answers with a short reply", "lemon"), "csgbq 153: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 153: the model answers with a short reply", "a"), "round 153: the model answers with a short reply"),
    (("round 153: the model answers with a short reply", "zz"), "qntmc 153: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 153: the model answers with a short reply", "AgentU"), "ruyaw 153: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 153: the model answers with a short reply", "keyboard"),
        "bssor 153: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 153: the model answers with a short reply", "AA"), "round 153: the model answers with a short reply"),
    (
        ("round 153: the recorder stores the reasoning trace", "key"),
        "bssxh 153: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 153: the recorder stores the reasoning trace", "lemon"),
        "csgbq 153: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 153: the recorder stores the reasoning trace", "a"), "round 153: the recorder stores the reasoning trace"),
    (
        ("round 153: the recorder stores the reasoning trace", "zz"),
        "qntmc 153: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 153: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 153: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 153: the recorder stores the reasoning trace", "keyboard"),
        "bssor 153: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 153: the recorder stores the reasoning trace", "AA"),
        "round 153: the recorder stores the reasoning trace",
    ),
    (("round 153: the angel watches the processor run", "key"), "bssxh 153: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 153: the angel watches the processor run", "lemon"), "csgbq 153: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 153: the angel watches the processor run", "a"), "round 153: the angel watches the processor run"),
    (("round 153: the angel watches the processor run", "zz"), "qntmc 153: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 153: the angel watches the processor run", "AgentU"), "ruyaw 153: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 153: the angel watches the processor run", "keyboard"), "bssor 153: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 153: the angel watches the processor run", "AA"), "round 153: the angel watches the processor run"),
    (("round 153: angle of the vector decides the match", "key"), "bssxh 153: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 153: angle of the vector decides the match", "lemon"), "csgbq 153: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 153: angle of the vector decides the match", "a"), "round 153: angle of the vector decides the match"),
    (("round 153: angle of the vector decides the match", "zz"), "qntmc 153: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 153: angle of the vector decides the match", "AgentU"),
        "ruyaw 153: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 153: angle of the vector decides the match", "keyboard"),
        "bssor 153: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 153: angle of the vector decides the match", "AA"), "round 153: angle of the vector decides the match"),
    (
        ("round 153: the candle burns twice as long at night", "key"),
        "bssxh 153: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 153: the candle burns twice as long at night", "lemon"),
        "csgbq 153: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 153: the candle burns twice as long at night", "a"), "round 153: the candle burns twice as long at night"),
    (
        ("round 153: the candle burns twice as long at night", "zz"),
        "qntmc 153: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 153: the candle burns twice as long at night", "AgentU"),
        "ruyaw 153: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 153: the candle burns twice as long at night", "keyboard"),
        "bssor 153: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 153: the candle burns twice as long at night", "AA"),
        "round 153: the candle burns twice as long at night",
    ),
    (("round 153: a mirror of the universe in one line", "key"), "bssxh 153: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 153: a mirror of the universe in one line", "lemon"), "csgbq 153: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 153: a mirror of the universe in one line", "a"), "round 153: a mirror of the universe in one line"),
    (("round 153: a mirror of the universe in one line", "zz"), "qntmc 153: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 153: a mirror of the universe in one line", "AgentU"), "ruyaw 153: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 153: a mirror of the universe in one line", "keyboard"),
        "bssor 153: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 153: a mirror of the universe in one line", "AA"), "round 153: a mirror of the universe in one line"),
    (("round 153: the queue drains before the storm", "key"), "bssxh 153: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 153: the queue drains before the storm", "lemon"), "csgbq 153: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 153: the queue drains before the storm", "a"), "round 153: the queue drains before the storm"),
    (("round 153: the queue drains before the storm", "zz"), "qntmc 153: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 153: the queue drains before the storm", "AgentU"), "ruyaw 153: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 153: the queue drains before the storm", "keyboard"), "bssor 153: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 153: the queue drains before the storm", "AA"), "round 153: the queue drains before the storm"),
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
