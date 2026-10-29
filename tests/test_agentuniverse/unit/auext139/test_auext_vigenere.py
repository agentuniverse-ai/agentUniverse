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
    (("kitten139", "key"), "umrdil139"),
    (("kitten139", "lemon"), "vmfhry139"),
    (("kitten139", "a"), "kitten139"),
    (("kitten139", "zz"), "jhssdm139"),
    (("kitten139", "AgentU"), "koxgxh139"),
    (("kitten139", "keyboard"), "umrusn139"),
    (("kitten139", "AA"), "kitten139"),
    (("sitting139", "key"), "cmrdmlq139"),
    (("sitting139", "lemon"), "dmfhvyk139"),
    (("sitting139", "a"), "sitting139"),
    (("sitting139", "zz"), "rhsshmf139"),
    (("sitting139", "AgentU"), "soxgbhg139"),
    (("sitting139", "keyboard"), "cmruwnx139"),
    (("sitting139", "AA"), "sitting139"),
    (("agent139", "key"), "kkcxx139"),
    (("agent139", "lemon"), "lkqbg139"),
    (("agent139", "a"), "agent139"),
    (("agent139", "zz"), "zfdms139"),
    (("agent139", "AgentU"), "amiam139"),
    (("agent139", "keyboard"), "kkcoh139"),
    (("agent139", "AA"), "agent139"),
    (("angle139", "key"), "krevi139"),
    (("angle139", "lemon"), "lrszr139"),
    (("angle139", "a"), "angle139"),
    (("angle139", "zz"), "zmfkd139"),
    (("angle139", "AgentU"), "atkyx139"),
    (("angle139", "keyboard"), "krems139"),
    (("angle139", "AA"), "angle139"),
    (("universe139", "key"), "ergfipci139"),
    (("universe139", "lemon"), "frujrcwq139"),
    (("universe139", "a"), "universe139"),
    (("universe139", "zz"), "tmhudqrd139"),
    (("universe139", "AgentU"), "utmixlsk139"),
    (("universe139", "keyboard"), "ergwsrjh139"),
    (("universe139", "AA"), "universe139"),
    (("memory139", "key"), "wikyvw139"),
    (("memory139", "lemon"), "xiycej139"),
    (("memory139", "a"), "memory139"),
    (("memory139", "zz"), "ldlnqx139"),
    (("memory139", "AgentU"), "mkqbks139"),
    (("memory139", "keyboard"), "wikpfy139"),
    (("memory139", "AA"), "memory139"),
    (("stream139", "key"), "cxpoek139"),
    (("stream139", "lemon"), "dxdsnx139"),
    (("stream139", "a"), "stream139"),
    (("stream139", "zz"), "rsqdzl139"),
    (("stream139", "AgentU"), "szvrtg139"),
    (("stream139", "keyboard"), "cxpfom139"),
    (("stream139", "AA"), "stream139"),
    (("context139", "key"), "msldivd139"),
    (("context139", "lemon"), "nszhrix139"),
    (("context139", "a"), "context139"),
    (("context139", "zz"), "bnmsdws139"),
    (("context139", "AgentU"), "curgxrt139"),
    (("context139", "keyboard"), "mslusxk139"),
    (("context139", "AA"), "context139"),
    (("knowledge139", "key"), "urmgpcnkc139"),
    (("knowledge139", "lemon"), "vrakyphss139"),
    (("knowledge139", "a"), "knowledge139"),
    (("knowledge139", "zz"), "jmnvkdcfd139"),
    (("knowledge139", "AgentU"), "ktsjeydmi139"),
    (("knowledge139", "keyboard"), "urmxzeujo139"),
    (("knowledge139", "AA"), "knowledge139"),
    (("vector139", "key"), "fiadsp139"),
    (("vector139", "lemon"), "giohbc139"),
    (("vector139", "a"), "vector139"),
    (("vector139", "zz"), "udbsnq139"),
    (("vector139", "AgentU"), "vkgghl139"),
    (("vector139", "keyboard"), "fiaucr139"),
    (("vector139", "AA"), "vector139"),
    (("processor139", "key"), "zvmmiqcsp139"),
    (("processor139", "lemon"), "avaqrdwaf139"),
    (("processor139", "a"), "processor139"),
    (("processor139", "zz"), "oqnbdrrnq139"),
    (("processor139", "AgentU"), "pxspxmsuv139"),
    (("processor139", "keyboard"), "zvmdssjrb139"),
    (("processor139", "AA"), "processor139"),
    (("reasoning139", "key"), "biycslsre139"),
    (("reasoning139", "lemon"), "cimgbymzu139"),
    (("reasoning139", "a"), "reasoning139"),
    (("reasoning139", "zz"), "qdzrnmhmf139"),
    (("reasoning139", "AgentU"), "rkefhhitk139"),
    (("reasoning139", "keyboard"), "biytcnzqq139"),
    (("reasoning139", "AA"), "reasoning139"),
    (("machine139", "key"), "wearmlo139"),
    (("machine139", "lemon"), "xeovvyi139"),
    (("machine139", "a"), "machine139"),
    (("machine139", "zz"), "lzbghmd139"),
    (("machine139", "AgentU"), "mggubhe139"),
    (("machine139", "keyboard"), "weaiwnv139"),
    (("machine139", "AA"), "machine139"),
    (("learning139", "key"), "viybrgxk139"),
    (("learning139", "lemon"), "wimfatrs139"),
    (("learning139", "a"), "learning139"),
    (("learning139", "zz"), "kdzqmhmf139"),
    (("learning139", "AgentU"), "lkeegcnm139"),
    (("learning139", "keyboard"), "viysbiej139"),
    (("learning139", "AA"), "learning139"),
    (("model139", "key"), "wsbop139"),
    (("model139", "lemon"), "xspsy139"),
    (("model139", "a"), "model139"),
    (("model139", "zz"), "lncdk139"),
    (("model139", "AgentU"), "muhre139"),
    (("model139", "keyboard"), "wsbfz139"),
    (("model139", "AA"), "model139"),
    (("token139", "key"), "dsior139"),
    (("token139", "lemon"), "eswsa139"),
    (("token139", "a"), "token139"),
    (("token139", "zz"), "snjdm139"),
    (("token139", "AgentU"), "tuorg139"),
    (("token139", "keyboard"), "dsifb139"),
    (("token139", "AA"), "token139"),
    (("prompt139", "key"), "zvmwtr139"),
    (("prompt139", "lemon"), "avaace139"),
    (("prompt139", "a"), "prompt139"),
    (("prompt139", "zz"), "oqnlos139"),
    (("prompt139", "AgentU"), "pxszin139"),
    (("prompt139", "keyboard"), "zvmndt139"),
    (("prompt139", "AA"), "prompt139"),
    (("session139", "key"), "ciqcmmx139"),
    (("session139", "lemon"), "diegvzr139"),
    (("session139", "a"), "session139"),
    (("session139", "zz"), "rdrrhnm139"),
    (("session139", "AgentU"), "skwfbin139"),
    (("session139", "keyboard"), "ciqtwoe139"),
    (("session139", "AA"), "session139"),
    (("library139", "key"), "vmzbepi139"),
    (("library139", "lemon"), "wmnfncc139"),
    (("library139", "a"), "library139"),
    (("library139", "zz"), "khaqzqx139"),
    (("library139", "AgentU"), "lofetly139"),
    (("library139", "keyboard"), "vmzsorp139"),
    (("library139", "AA"), "library139"),
    (("service139", "key"), "cipfmao139"),
    (("service139", "lemon"), "didjvni139"),
    (("service139", "a"), "service139"),
    (("service139", "zz"), "rdquhbd139"),
    (("service139", "AgentU"), "skvibwe139"),
    (("service139", "keyboard"), "cipwwcv139"),
    (("service139", "AA"), "service139"),
    (("gateway139", "key"), "qeroayi139"),
    (("gateway139", "lemon"), "refsjlc139"),
    (("gateway139", "a"), "gateway139"),
    (("gateway139", "zz"), "fzsdvzx139"),
    (("gateway139", "AgentU"), "ggxrpuy139"),
    (("gateway139", "keyboard"), "qerfkap139"),
    (("gateway139", "AA"), "gateway139"),
    (("storage139", "key"), "cxmbeeo139"),
    (("storage139", "lemon"), "dxafnri139"),
    (("storage139", "a"), "storage139"),
    (("storage139", "zz"), "rsnqzfd139"),
    (("storage139", "AgentU"), "szsetae139"),
    (("storage139", "keyboard"), "cxmsogv139"),
    (("storage139", "AA"), "storage139"),
    (("network139", "key"), "xirgspu139"),
    (("network139", "lemon"), "yifkbco139"),
    (("network139", "a"), "network139"),
    (("network139", "zz"), "mdsvnqj139"),
    (("network139", "AgentU"), "nkxjhlk139"),
    (("network139", "keyboard"), "xirxcrb139"),
    (("network139", "AA"), "network139"),
    (("latency139", "key"), "verorai139"),
    (("latency139", "lemon"), "wefsanc139"),
    (("latency139", "a"), "latency139"),
    (("latency139", "zz"), "kzsdmbx139"),
    (("latency139", "AgentU"), "lgxrgwy139"),
    (("latency139", "keyboard"), "verfbcp139"),
    (("latency139", "AA"), "latency139"),
    (("buffer139", "key"), "lydpip139"),
    (("buffer139", "lemon"), "myrtrc139"),
    (("buffer139", "a"), "buffer139"),
    (("buffer139", "zz"), "ateedq139"),
    (("buffer139", "AgentU"), "bajsxl139"),
    (("buffer139", "keyboard"), "lydgsr139"),
    (("buffer139", "AA"), "buffer139"),
    (("queue139", "key"), "aycei139"),
    (("queue139", "lemon"), "byqir139"),
    (("queue139", "a"), "queue139"),
    (("queue139", "zz"), "ptdtd139"),
    (("queue139", "AgentU"), "qaihx139"),
    (("queue139", "keyboard"), "aycvs139"),
    (("queue139", "AA"), "queue139"),
    (("worker139", "key"), "gspuip139"),
    (("worker139", "lemon"), "hsdyrc139"),
    (("worker139", "a"), "worker139"),
    (("worker139", "zz"), "vnqjdq139"),
    (("worker139", "AgentU"), "wuvxxl139"),
    (("worker139", "keyboard"), "gsplsr139"),
    (("worker139", "AA"), "worker139"),
    (("kernel139", "key"), "uipxij139"),
    (("kernel139", "lemon"), "vidbrw139"),
    (("kernel139", "a"), "kernel139"),
    (("kernel139", "zz"), "jdqmdk139"),
    (("kernel139", "AgentU"), "kkvaxf139"),
    (("kernel139", "keyboard"), "uiposl139"),
    (("kernel139", "AA"), "kernel139"),
    (("signal139", "key"), "cmexej139"),
    (("signal139", "lemon"), "dmsbnw139"),
    (("signal139", "a"), "signal139"),
    (("signal139", "zz"), "rhfmzk139"),
    (("signal139", "AgentU"), "sokatf139"),
    (("signal139", "keyboard"), "cmeool139"),
    (("signal139", "AA"), "signal139"),
    (("packet139", "key"), "zeauir139"),
    (("packet139", "lemon"), "aeoyre139"),
    (("packet139", "a"), "packet139"),
    (("packet139", "zz"), "ozbjds139"),
    (("packet139", "AgentU"), "pggxxn139"),
    (("packet139", "keyboard"), "zealst139"),
    (("packet139", "AA"), "packet139"),
    (("router139", "key"), "bssdip139"),
    (("router139", "lemon"), "csghrc139"),
    (("router139", "a"), "router139"),
    (("router139", "zz"), "qntsdq139"),
    (("router139", "AgentU"), "ruygxl139"),
    (("router139", "keyboard"), "bssusr139"),
    (("router139", "AA"), "router139"),
    (("cluster139", "key"), "mpscxcb139"),
    (("cluster139", "lemon"), "npgggpv139"),
    (("cluster139", "a"), "cluster139"),
    (("cluster139", "zz"), "bktrsdq139"),
    (("cluster139", "AgentU"), "cryfmyr139"),
    (("cluster139", "keyboard"), "mpsthei139"),
    (("cluster139", "AA"), "cluster139"),
    (("mirror139", "key"), "wmpbsp139"),
    (("mirror139", "lemon"), "xmdfbc139"),
    (("mirror139", "a"), "mirror139"),
    (("mirror139", "zz"), "lhqqnq139"),
    (("mirror139", "AgentU"), "movehl139"),
    (("mirror139", "keyboard"), "wmpscr139"),
    (("mirror139", "AA"), "mirror139"),
    (("filter139", "key"), "pmjdip139"),
    (("filter139", "lemon"), "qmxhrc139"),
    (("filter139", "a"), "filter139"),
    (("filter139", "zz"), "ehksdq139"),
    (("filter139", "AgentU"), "fopgxl139"),
    (("filter139", "keyboard"), "pmjusr139"),
    (("filter139", "AA"), "filter139"),
    (("ranking139", "key"), "belumlq139"),
    (("ranking139", "lemon"), "cezyvyk139"),
    (("ranking139", "a"), "ranking139"),
    (("ranking139", "zz"), "qzmjhmf139"),
    (("ranking139", "AgentU"), "rgrxbhg139"),
    (("ranking139", "keyboard"), "bellwnx139"),
    (("ranking139", "AA"), "ranking139"),
    (("encoding139", "key"), "orayhgxk139"),
    (("encoding139", "lemon"), "procqtrs139"),
    (("encoding139", "a"), "encoding139"),
    (("encoding139", "zz"), "dmbnchmf139"),
    (("encoding139", "AgentU"), "etgbwcnm139"),
    (("encoding139", "keyboard"), "orapriej139"),
    (("encoding139", "AA"), "encoding139"),
    (("mapping139", "key"), "wenzmlq139"),
    (("mapping139", "lemon"), "xebdvyk139"),
    (("mapping139", "a"), "mapping139"),
    (("mapping139", "zz"), "lzoohmf139"),
    (("mapping139", "AgentU"), "mgtcbhg139"),
    (("mapping139", "keyboard"), "wenqwnx139"),
    (("mapping139", "AA"), "mapping139"),
    (("record139", "key"), "biayvb139"),
    (("record139", "lemon"), "cioceo139"),
    (("record139", "a"), "record139"),
    (("record139", "zz"), "qdbnqc139"),
    (("record139", "AgentU"), "rkgbkx139"),
    (("record139", "keyboard"), "biapfd139"),
    (("record139", "AA"), "record139"),
    (("candle139", "key"), "melnpc139"),
    (("candle139", "lemon"), "nezryp139"),
    (("candle139", "a"), "candle139"),
    (("candle139", "zz"), "bzmckd139"),
    (("candle139", "AgentU"), "cgrqey139"),
    (("candle139", "keyboard"), "meleze139"),
    (("candle139", "AA"), "candle139"),
    (("thread139", "key"), "dlpoeb139"),
    (("thread139", "lemon"), "eldsno139"),
    (("thread139", "a"), "thread139"),
    (("thread139", "zz"), "sgqdzc139"),
    (("thread139", "AgentU"), "tnvrtx139"),
    (("thread139", "keyboard"), "dlpfod139"),
    (("thread139", "AA"), "thread139"),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 139: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 139: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "a"),
        "round 139: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 139: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 139: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 139: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", "AA"),
        "round 139: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "key"),
        "bssxh 139: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 139: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "a"),
        "round 139: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 139: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 139: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 139: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", "AA"),
        "round 139: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 139: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 139: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "a"),
        "round 139: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 139: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 139: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 139: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", "AA"),
        "round 139: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 139: the processor reads the record then stops", "key"),
        "bssxh 139: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 139: the processor reads the record then stops", "lemon"),
        "csgbq 139: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 139: the processor reads the record then stops", "a"),
        "round 139: the processor reads the record then stops",
    ),
    (
        ("round 139: the processor reads the record then stops", "zz"),
        "qntmc 139: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 139: the processor reads the record then stops", "AgentU"),
        "ruyaw 139: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 139: the processor reads the record then stops", "keyboard"),
        "bssor 139: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 139: the processor reads the record then stops", "AA"),
        "round 139: the processor reads the record then stops",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "key"),
        "bssxh 139: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "lemon"),
        "csgbq 139: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "a"),
        "round 139: a worker pulls the next task from the queue",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "zz"),
        "qntmc 139: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 139: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "keyboard"),
        "bssor 139: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 139: a worker pulls the next task from the queue", "AA"),
        "round 139: a worker pulls the next task from the queue",
    ),
    (
        ("round 139: signals travel through the network layer", "key"),
        "bssxh 139: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 139: signals travel through the network layer", "lemon"),
        "csgbq 139: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 139: signals travel through the network layer", "a"),
        "round 139: signals travel through the network layer",
    ),
    (
        ("round 139: signals travel through the network layer", "zz"),
        "qntmc 139: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 139: signals travel through the network layer", "AgentU"),
        "ruyaw 139: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 139: signals travel through the network layer", "keyboard"),
        "bssor 139: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 139: signals travel through the network layer", "AA"),
        "round 139: signals travel through the network layer",
    ),
    (
        ("round 139: the gateway routes each request by policy", "key"),
        "bssxh 139: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 139: the gateway routes each request by policy", "lemon"),
        "csgbq 139: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 139: the gateway routes each request by policy", "a"),
        "round 139: the gateway routes each request by policy",
    ),
    (
        ("round 139: the gateway routes each request by policy", "zz"),
        "qntmc 139: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 139: the gateway routes each request by policy", "AgentU"),
        "ruyaw 139: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 139: the gateway routes each request by policy", "keyboard"),
        "bssor 139: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 139: the gateway routes each request by policy", "AA"),
        "round 139: the gateway routes each request by policy",
    ),
    (("round 139: memory grows until the buffer is full", "key"), "bssxh 139: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 139: memory grows until the buffer is full", "lemon"), "csgbq 139: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 139: memory grows until the buffer is full", "a"), "round 139: memory grows until the buffer is full"),
    (("round 139: memory grows until the buffer is full", "zz"), "qntmc 139: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 139: memory grows until the buffer is full", "AgentU"),
        "ruyaw 139: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 139: memory grows until the buffer is full", "keyboard"),
        "bssor 139: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 139: memory grows until the buffer is full", "AA"), "round 139: memory grows until the buffer is full"),
    (("round 139: the cluster mirrors every packet twice", "key"), "bssxh 139: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 139: the cluster mirrors every packet twice", "lemon"),
        "csgbq 139: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 139: the cluster mirrors every packet twice", "a"), "round 139: the cluster mirrors every packet twice"),
    (("round 139: the cluster mirrors every packet twice", "zz"), "qntmc 139: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 139: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 139: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 139: the cluster mirrors every packet twice", "keyboard"),
        "bssor 139: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 139: the cluster mirrors every packet twice", "AA"), "round 139: the cluster mirrors every packet twice"),
    (
        ("round 139: ranking uses tokens learned from the corpus", "key"),
        "bssxh 139: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 139: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", "a"),
        "round 139: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 139: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 139: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 139: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", "AA"),
        "round 139: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 139: a long session ends when the candle dies", "key"),
        "bssxh 139: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 139: a long session ends when the candle dies", "lemon"),
        "csgbq 139: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 139: a long session ends when the candle dies", "a"),
        "round 139: a long session ends when the candle dies",
    ),
    (
        ("round 139: a long session ends when the candle dies", "zz"),
        "qntmc 139: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 139: a long session ends when the candle dies", "AgentU"),
        "ruyaw 139: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 139: a long session ends when the candle dies", "keyboard"),
        "bssor 139: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 139: a long session ends when the candle dies", "AA"),
        "round 139: a long session ends when the candle dies",
    ),
    (("round 139: encode the prompt then map the result", "key"), "bssxh 139: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 139: encode the prompt then map the result", "lemon"), "csgbq 139: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 139: encode the prompt then map the result", "a"), "round 139: encode the prompt then map the result"),
    (("round 139: encode the prompt then map the result", "zz"), "qntmc 139: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 139: encode the prompt then map the result", "AgentU"),
        "ruyaw 139: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 139: encode the prompt then map the result", "keyboard"),
        "bssor 139: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 139: encode the prompt then map the result", "AA"), "round 139: encode the prompt then map the result"),
    (("round 139: the kernel wakes the worker at dawn", "key"), "bssxh 139: rri iovlop ukocc xfo ambocb er neux"),
    (("round 139: the kernel wakes the worker at dawn", "lemon"), "csgbq 139: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 139: the kernel wakes the worker at dawn", "a"), "round 139: the kernel wakes the worker at dawn"),
    (("round 139: the kernel wakes the worker at dawn", "zz"), "qntmc 139: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 139: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 139: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 139: the kernel wakes the worker at dawn", "keyboard"), "bssor 139: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 139: the kernel wakes the worker at dawn", "AA"), "round 139: the kernel wakes the worker at dawn"),
    (("round 139: service latency drops after the patch", "key"), "bssxh 139: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 139: service latency drops after the patch", "lemon"), "csgbq 139: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 139: service latency drops after the patch", "a"), "round 139: service latency drops after the patch"),
    (("round 139: service latency drops after the patch", "zz"), "qntmc 139: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 139: service latency drops after the patch", "AgentU"),
        "ruyaw 139: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 139: service latency drops after the patch", "keyboard"),
        "bssor 139: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 139: service latency drops after the patch", "AA"), "round 139: service latency drops after the patch"),
    (
        ("round 139: the library caches every vector it sees", "key"),
        "bssxh 139: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 139: the library caches every vector it sees", "lemon"),
        "csgbq 139: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 139: the library caches every vector it sees", "a"), "round 139: the library caches every vector it sees"),
    (
        ("round 139: the library caches every vector it sees", "zz"),
        "qntmc 139: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 139: the library caches every vector it sees", "AgentU"),
        "ruyaw 139: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 139: the library caches every vector it sees", "keyboard"),
        "bssor 139: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 139: the library caches every vector it sees", "AA"),
        "round 139: the library caches every vector it sees",
    ),
    (("round 139: agents argue then the debate resolves", "key"), "bssxh 139: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 139: agents argue then the debate resolves", "lemon"), "csgbq 139: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 139: agents argue then the debate resolves", "a"), "round 139: agents argue then the debate resolves"),
    (("round 139: agents argue then the debate resolves", "zz"), "qntmc 139: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 139: agents argue then the debate resolves", "AgentU"),
        "ruyaw 139: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 139: agents argue then the debate resolves", "keyboard"),
        "bssor 139: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 139: agents argue then the debate resolves", "AA"), "round 139: agents argue then the debate resolves"),
    (("round 139: the filter keeps only strong matches", "key"), "bssxh 139: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 139: the filter keeps only strong matches", "lemon"), "csgbq 139: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 139: the filter keeps only strong matches", "a"), "round 139: the filter keeps only strong matches"),
    (("round 139: the filter keeps only strong matches", "zz"), "qntmc 139: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 139: the filter keeps only strong matches", "AgentU"), "ruyaw 139: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 139: the filter keeps only strong matches", "keyboard"),
        "bssor 139: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 139: the filter keeps only strong matches", "AA"), "round 139: the filter keeps only strong matches"),
    (("round 139: the model answers with a short reply", "key"), "bssxh 139: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 139: the model answers with a short reply", "lemon"), "csgbq 139: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 139: the model answers with a short reply", "a"), "round 139: the model answers with a short reply"),
    (("round 139: the model answers with a short reply", "zz"), "qntmc 139: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 139: the model answers with a short reply", "AgentU"), "ruyaw 139: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 139: the model answers with a short reply", "keyboard"),
        "bssor 139: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 139: the model answers with a short reply", "AA"), "round 139: the model answers with a short reply"),
    (
        ("round 139: the recorder stores the reasoning trace", "key"),
        "bssxh 139: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 139: the recorder stores the reasoning trace", "lemon"),
        "csgbq 139: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 139: the recorder stores the reasoning trace", "a"), "round 139: the recorder stores the reasoning trace"),
    (
        ("round 139: the recorder stores the reasoning trace", "zz"),
        "qntmc 139: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 139: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 139: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 139: the recorder stores the reasoning trace", "keyboard"),
        "bssor 139: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 139: the recorder stores the reasoning trace", "AA"),
        "round 139: the recorder stores the reasoning trace",
    ),
    (("round 139: the angel watches the processor run", "key"), "bssxh 139: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 139: the angel watches the processor run", "lemon"), "csgbq 139: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 139: the angel watches the processor run", "a"), "round 139: the angel watches the processor run"),
    (("round 139: the angel watches the processor run", "zz"), "qntmc 139: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 139: the angel watches the processor run", "AgentU"), "ruyaw 139: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 139: the angel watches the processor run", "keyboard"), "bssor 139: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 139: the angel watches the processor run", "AA"), "round 139: the angel watches the processor run"),
    (("round 139: angle of the vector decides the match", "key"), "bssxh 139: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 139: angle of the vector decides the match", "lemon"), "csgbq 139: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 139: angle of the vector decides the match", "a"), "round 139: angle of the vector decides the match"),
    (("round 139: angle of the vector decides the match", "zz"), "qntmc 139: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 139: angle of the vector decides the match", "AgentU"),
        "ruyaw 139: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 139: angle of the vector decides the match", "keyboard"),
        "bssor 139: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 139: angle of the vector decides the match", "AA"), "round 139: angle of the vector decides the match"),
    (
        ("round 139: the candle burns twice as long at night", "key"),
        "bssxh 139: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 139: the candle burns twice as long at night", "lemon"),
        "csgbq 139: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 139: the candle burns twice as long at night", "a"), "round 139: the candle burns twice as long at night"),
    (
        ("round 139: the candle burns twice as long at night", "zz"),
        "qntmc 139: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 139: the candle burns twice as long at night", "AgentU"),
        "ruyaw 139: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 139: the candle burns twice as long at night", "keyboard"),
        "bssor 139: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 139: the candle burns twice as long at night", "AA"),
        "round 139: the candle burns twice as long at night",
    ),
    (("round 139: a mirror of the universe in one line", "key"), "bssxh 139: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 139: a mirror of the universe in one line", "lemon"), "csgbq 139: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 139: a mirror of the universe in one line", "a"), "round 139: a mirror of the universe in one line"),
    (("round 139: a mirror of the universe in one line", "zz"), "qntmc 139: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 139: a mirror of the universe in one line", "AgentU"), "ruyaw 139: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 139: a mirror of the universe in one line", "keyboard"),
        "bssor 139: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 139: a mirror of the universe in one line", "AA"), "round 139: a mirror of the universe in one line"),
    (("round 139: the queue drains before the storm", "key"), "bssxh 139: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 139: the queue drains before the storm", "lemon"), "csgbq 139: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 139: the queue drains before the storm", "a"), "round 139: the queue drains before the storm"),
    (("round 139: the queue drains before the storm", "zz"), "qntmc 139: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 139: the queue drains before the storm", "AgentU"), "ruyaw 139: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 139: the queue drains before the storm", "keyboard"), "bssor 139: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 139: the queue drains before the storm", "AA"), "round 139: the queue drains before the storm"),
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
