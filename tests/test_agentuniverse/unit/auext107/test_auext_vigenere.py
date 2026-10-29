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
    (("kitten107", "key"), "umrdil107"),
    (("kitten107", "lemon"), "vmfhry107"),
    (("kitten107", "a"), "kitten107"),
    (("kitten107", "zz"), "jhssdm107"),
    (("kitten107", "AgentU"), "koxgxh107"),
    (("kitten107", "keyboard"), "umrusn107"),
    (("kitten107", "AA"), "kitten107"),
    (("sitting107", "key"), "cmrdmlq107"),
    (("sitting107", "lemon"), "dmfhvyk107"),
    (("sitting107", "a"), "sitting107"),
    (("sitting107", "zz"), "rhsshmf107"),
    (("sitting107", "AgentU"), "soxgbhg107"),
    (("sitting107", "keyboard"), "cmruwnx107"),
    (("sitting107", "AA"), "sitting107"),
    (("agent107", "key"), "kkcxx107"),
    (("agent107", "lemon"), "lkqbg107"),
    (("agent107", "a"), "agent107"),
    (("agent107", "zz"), "zfdms107"),
    (("agent107", "AgentU"), "amiam107"),
    (("agent107", "keyboard"), "kkcoh107"),
    (("agent107", "AA"), "agent107"),
    (("angle107", "key"), "krevi107"),
    (("angle107", "lemon"), "lrszr107"),
    (("angle107", "a"), "angle107"),
    (("angle107", "zz"), "zmfkd107"),
    (("angle107", "AgentU"), "atkyx107"),
    (("angle107", "keyboard"), "krems107"),
    (("angle107", "AA"), "angle107"),
    (("universe107", "key"), "ergfipci107"),
    (("universe107", "lemon"), "frujrcwq107"),
    (("universe107", "a"), "universe107"),
    (("universe107", "zz"), "tmhudqrd107"),
    (("universe107", "AgentU"), "utmixlsk107"),
    (("universe107", "keyboard"), "ergwsrjh107"),
    (("universe107", "AA"), "universe107"),
    (("memory107", "key"), "wikyvw107"),
    (("memory107", "lemon"), "xiycej107"),
    (("memory107", "a"), "memory107"),
    (("memory107", "zz"), "ldlnqx107"),
    (("memory107", "AgentU"), "mkqbks107"),
    (("memory107", "keyboard"), "wikpfy107"),
    (("memory107", "AA"), "memory107"),
    (("stream107", "key"), "cxpoek107"),
    (("stream107", "lemon"), "dxdsnx107"),
    (("stream107", "a"), "stream107"),
    (("stream107", "zz"), "rsqdzl107"),
    (("stream107", "AgentU"), "szvrtg107"),
    (("stream107", "keyboard"), "cxpfom107"),
    (("stream107", "AA"), "stream107"),
    (("context107", "key"), "msldivd107"),
    (("context107", "lemon"), "nszhrix107"),
    (("context107", "a"), "context107"),
    (("context107", "zz"), "bnmsdws107"),
    (("context107", "AgentU"), "curgxrt107"),
    (("context107", "keyboard"), "mslusxk107"),
    (("context107", "AA"), "context107"),
    (("knowledge107", "key"), "urmgpcnkc107"),
    (("knowledge107", "lemon"), "vrakyphss107"),
    (("knowledge107", "a"), "knowledge107"),
    (("knowledge107", "zz"), "jmnvkdcfd107"),
    (("knowledge107", "AgentU"), "ktsjeydmi107"),
    (("knowledge107", "keyboard"), "urmxzeujo107"),
    (("knowledge107", "AA"), "knowledge107"),
    (("vector107", "key"), "fiadsp107"),
    (("vector107", "lemon"), "giohbc107"),
    (("vector107", "a"), "vector107"),
    (("vector107", "zz"), "udbsnq107"),
    (("vector107", "AgentU"), "vkgghl107"),
    (("vector107", "keyboard"), "fiaucr107"),
    (("vector107", "AA"), "vector107"),
    (("processor107", "key"), "zvmmiqcsp107"),
    (("processor107", "lemon"), "avaqrdwaf107"),
    (("processor107", "a"), "processor107"),
    (("processor107", "zz"), "oqnbdrrnq107"),
    (("processor107", "AgentU"), "pxspxmsuv107"),
    (("processor107", "keyboard"), "zvmdssjrb107"),
    (("processor107", "AA"), "processor107"),
    (("reasoning107", "key"), "biycslsre107"),
    (("reasoning107", "lemon"), "cimgbymzu107"),
    (("reasoning107", "a"), "reasoning107"),
    (("reasoning107", "zz"), "qdzrnmhmf107"),
    (("reasoning107", "AgentU"), "rkefhhitk107"),
    (("reasoning107", "keyboard"), "biytcnzqq107"),
    (("reasoning107", "AA"), "reasoning107"),
    (("machine107", "key"), "wearmlo107"),
    (("machine107", "lemon"), "xeovvyi107"),
    (("machine107", "a"), "machine107"),
    (("machine107", "zz"), "lzbghmd107"),
    (("machine107", "AgentU"), "mggubhe107"),
    (("machine107", "keyboard"), "weaiwnv107"),
    (("machine107", "AA"), "machine107"),
    (("learning107", "key"), "viybrgxk107"),
    (("learning107", "lemon"), "wimfatrs107"),
    (("learning107", "a"), "learning107"),
    (("learning107", "zz"), "kdzqmhmf107"),
    (("learning107", "AgentU"), "lkeegcnm107"),
    (("learning107", "keyboard"), "viysbiej107"),
    (("learning107", "AA"), "learning107"),
    (("model107", "key"), "wsbop107"),
    (("model107", "lemon"), "xspsy107"),
    (("model107", "a"), "model107"),
    (("model107", "zz"), "lncdk107"),
    (("model107", "AgentU"), "muhre107"),
    (("model107", "keyboard"), "wsbfz107"),
    (("model107", "AA"), "model107"),
    (("token107", "key"), "dsior107"),
    (("token107", "lemon"), "eswsa107"),
    (("token107", "a"), "token107"),
    (("token107", "zz"), "snjdm107"),
    (("token107", "AgentU"), "tuorg107"),
    (("token107", "keyboard"), "dsifb107"),
    (("token107", "AA"), "token107"),
    (("prompt107", "key"), "zvmwtr107"),
    (("prompt107", "lemon"), "avaace107"),
    (("prompt107", "a"), "prompt107"),
    (("prompt107", "zz"), "oqnlos107"),
    (("prompt107", "AgentU"), "pxszin107"),
    (("prompt107", "keyboard"), "zvmndt107"),
    (("prompt107", "AA"), "prompt107"),
    (("session107", "key"), "ciqcmmx107"),
    (("session107", "lemon"), "diegvzr107"),
    (("session107", "a"), "session107"),
    (("session107", "zz"), "rdrrhnm107"),
    (("session107", "AgentU"), "skwfbin107"),
    (("session107", "keyboard"), "ciqtwoe107"),
    (("session107", "AA"), "session107"),
    (("library107", "key"), "vmzbepi107"),
    (("library107", "lemon"), "wmnfncc107"),
    (("library107", "a"), "library107"),
    (("library107", "zz"), "khaqzqx107"),
    (("library107", "AgentU"), "lofetly107"),
    (("library107", "keyboard"), "vmzsorp107"),
    (("library107", "AA"), "library107"),
    (("service107", "key"), "cipfmao107"),
    (("service107", "lemon"), "didjvni107"),
    (("service107", "a"), "service107"),
    (("service107", "zz"), "rdquhbd107"),
    (("service107", "AgentU"), "skvibwe107"),
    (("service107", "keyboard"), "cipwwcv107"),
    (("service107", "AA"), "service107"),
    (("gateway107", "key"), "qeroayi107"),
    (("gateway107", "lemon"), "refsjlc107"),
    (("gateway107", "a"), "gateway107"),
    (("gateway107", "zz"), "fzsdvzx107"),
    (("gateway107", "AgentU"), "ggxrpuy107"),
    (("gateway107", "keyboard"), "qerfkap107"),
    (("gateway107", "AA"), "gateway107"),
    (("storage107", "key"), "cxmbeeo107"),
    (("storage107", "lemon"), "dxafnri107"),
    (("storage107", "a"), "storage107"),
    (("storage107", "zz"), "rsnqzfd107"),
    (("storage107", "AgentU"), "szsetae107"),
    (("storage107", "keyboard"), "cxmsogv107"),
    (("storage107", "AA"), "storage107"),
    (("network107", "key"), "xirgspu107"),
    (("network107", "lemon"), "yifkbco107"),
    (("network107", "a"), "network107"),
    (("network107", "zz"), "mdsvnqj107"),
    (("network107", "AgentU"), "nkxjhlk107"),
    (("network107", "keyboard"), "xirxcrb107"),
    (("network107", "AA"), "network107"),
    (("latency107", "key"), "verorai107"),
    (("latency107", "lemon"), "wefsanc107"),
    (("latency107", "a"), "latency107"),
    (("latency107", "zz"), "kzsdmbx107"),
    (("latency107", "AgentU"), "lgxrgwy107"),
    (("latency107", "keyboard"), "verfbcp107"),
    (("latency107", "AA"), "latency107"),
    (("buffer107", "key"), "lydpip107"),
    (("buffer107", "lemon"), "myrtrc107"),
    (("buffer107", "a"), "buffer107"),
    (("buffer107", "zz"), "ateedq107"),
    (("buffer107", "AgentU"), "bajsxl107"),
    (("buffer107", "keyboard"), "lydgsr107"),
    (("buffer107", "AA"), "buffer107"),
    (("queue107", "key"), "aycei107"),
    (("queue107", "lemon"), "byqir107"),
    (("queue107", "a"), "queue107"),
    (("queue107", "zz"), "ptdtd107"),
    (("queue107", "AgentU"), "qaihx107"),
    (("queue107", "keyboard"), "aycvs107"),
    (("queue107", "AA"), "queue107"),
    (("worker107", "key"), "gspuip107"),
    (("worker107", "lemon"), "hsdyrc107"),
    (("worker107", "a"), "worker107"),
    (("worker107", "zz"), "vnqjdq107"),
    (("worker107", "AgentU"), "wuvxxl107"),
    (("worker107", "keyboard"), "gsplsr107"),
    (("worker107", "AA"), "worker107"),
    (("kernel107", "key"), "uipxij107"),
    (("kernel107", "lemon"), "vidbrw107"),
    (("kernel107", "a"), "kernel107"),
    (("kernel107", "zz"), "jdqmdk107"),
    (("kernel107", "AgentU"), "kkvaxf107"),
    (("kernel107", "keyboard"), "uiposl107"),
    (("kernel107", "AA"), "kernel107"),
    (("signal107", "key"), "cmexej107"),
    (("signal107", "lemon"), "dmsbnw107"),
    (("signal107", "a"), "signal107"),
    (("signal107", "zz"), "rhfmzk107"),
    (("signal107", "AgentU"), "sokatf107"),
    (("signal107", "keyboard"), "cmeool107"),
    (("signal107", "AA"), "signal107"),
    (("packet107", "key"), "zeauir107"),
    (("packet107", "lemon"), "aeoyre107"),
    (("packet107", "a"), "packet107"),
    (("packet107", "zz"), "ozbjds107"),
    (("packet107", "AgentU"), "pggxxn107"),
    (("packet107", "keyboard"), "zealst107"),
    (("packet107", "AA"), "packet107"),
    (("router107", "key"), "bssdip107"),
    (("router107", "lemon"), "csghrc107"),
    (("router107", "a"), "router107"),
    (("router107", "zz"), "qntsdq107"),
    (("router107", "AgentU"), "ruygxl107"),
    (("router107", "keyboard"), "bssusr107"),
    (("router107", "AA"), "router107"),
    (("cluster107", "key"), "mpscxcb107"),
    (("cluster107", "lemon"), "npgggpv107"),
    (("cluster107", "a"), "cluster107"),
    (("cluster107", "zz"), "bktrsdq107"),
    (("cluster107", "AgentU"), "cryfmyr107"),
    (("cluster107", "keyboard"), "mpsthei107"),
    (("cluster107", "AA"), "cluster107"),
    (("mirror107", "key"), "wmpbsp107"),
    (("mirror107", "lemon"), "xmdfbc107"),
    (("mirror107", "a"), "mirror107"),
    (("mirror107", "zz"), "lhqqnq107"),
    (("mirror107", "AgentU"), "movehl107"),
    (("mirror107", "keyboard"), "wmpscr107"),
    (("mirror107", "AA"), "mirror107"),
    (("filter107", "key"), "pmjdip107"),
    (("filter107", "lemon"), "qmxhrc107"),
    (("filter107", "a"), "filter107"),
    (("filter107", "zz"), "ehksdq107"),
    (("filter107", "AgentU"), "fopgxl107"),
    (("filter107", "keyboard"), "pmjusr107"),
    (("filter107", "AA"), "filter107"),
    (("ranking107", "key"), "belumlq107"),
    (("ranking107", "lemon"), "cezyvyk107"),
    (("ranking107", "a"), "ranking107"),
    (("ranking107", "zz"), "qzmjhmf107"),
    (("ranking107", "AgentU"), "rgrxbhg107"),
    (("ranking107", "keyboard"), "bellwnx107"),
    (("ranking107", "AA"), "ranking107"),
    (("encoding107", "key"), "orayhgxk107"),
    (("encoding107", "lemon"), "procqtrs107"),
    (("encoding107", "a"), "encoding107"),
    (("encoding107", "zz"), "dmbnchmf107"),
    (("encoding107", "AgentU"), "etgbwcnm107"),
    (("encoding107", "keyboard"), "orapriej107"),
    (("encoding107", "AA"), "encoding107"),
    (("mapping107", "key"), "wenzmlq107"),
    (("mapping107", "lemon"), "xebdvyk107"),
    (("mapping107", "a"), "mapping107"),
    (("mapping107", "zz"), "lzoohmf107"),
    (("mapping107", "AgentU"), "mgtcbhg107"),
    (("mapping107", "keyboard"), "wenqwnx107"),
    (("mapping107", "AA"), "mapping107"),
    (("record107", "key"), "biayvb107"),
    (("record107", "lemon"), "cioceo107"),
    (("record107", "a"), "record107"),
    (("record107", "zz"), "qdbnqc107"),
    (("record107", "AgentU"), "rkgbkx107"),
    (("record107", "keyboard"), "biapfd107"),
    (("record107", "AA"), "record107"),
    (("candle107", "key"), "melnpc107"),
    (("candle107", "lemon"), "nezryp107"),
    (("candle107", "a"), "candle107"),
    (("candle107", "zz"), "bzmckd107"),
    (("candle107", "AgentU"), "cgrqey107"),
    (("candle107", "keyboard"), "meleze107"),
    (("candle107", "AA"), "candle107"),
    (("thread107", "key"), "dlpoeb107"),
    (("thread107", "lemon"), "eldsno107"),
    (("thread107", "a"), "thread107"),
    (("thread107", "zz"), "sgqdzc107"),
    (("thread107", "AgentU"), "tnvrtx107"),
    (("thread107", "keyboard"), "dlpfod107"),
    (("thread107", "AA"), "thread107"),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 107: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 107: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "a"),
        "round 107: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 107: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 107: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 107: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", "AA"),
        "round 107: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "key"),
        "bssxh 107: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 107: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "a"),
        "round 107: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 107: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 107: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 107: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", "AA"),
        "round 107: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 107: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 107: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "a"),
        "round 107: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 107: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 107: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 107: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", "AA"),
        "round 107: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 107: the processor reads the record then stops", "key"),
        "bssxh 107: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 107: the processor reads the record then stops", "lemon"),
        "csgbq 107: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 107: the processor reads the record then stops", "a"),
        "round 107: the processor reads the record then stops",
    ),
    (
        ("round 107: the processor reads the record then stops", "zz"),
        "qntmc 107: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 107: the processor reads the record then stops", "AgentU"),
        "ruyaw 107: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 107: the processor reads the record then stops", "keyboard"),
        "bssor 107: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 107: the processor reads the record then stops", "AA"),
        "round 107: the processor reads the record then stops",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "key"),
        "bssxh 107: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "lemon"),
        "csgbq 107: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "a"),
        "round 107: a worker pulls the next task from the queue",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "zz"),
        "qntmc 107: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 107: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "keyboard"),
        "bssor 107: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 107: a worker pulls the next task from the queue", "AA"),
        "round 107: a worker pulls the next task from the queue",
    ),
    (
        ("round 107: signals travel through the network layer", "key"),
        "bssxh 107: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 107: signals travel through the network layer", "lemon"),
        "csgbq 107: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 107: signals travel through the network layer", "a"),
        "round 107: signals travel through the network layer",
    ),
    (
        ("round 107: signals travel through the network layer", "zz"),
        "qntmc 107: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 107: signals travel through the network layer", "AgentU"),
        "ruyaw 107: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 107: signals travel through the network layer", "keyboard"),
        "bssor 107: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 107: signals travel through the network layer", "AA"),
        "round 107: signals travel through the network layer",
    ),
    (
        ("round 107: the gateway routes each request by policy", "key"),
        "bssxh 107: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 107: the gateway routes each request by policy", "lemon"),
        "csgbq 107: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 107: the gateway routes each request by policy", "a"),
        "round 107: the gateway routes each request by policy",
    ),
    (
        ("round 107: the gateway routes each request by policy", "zz"),
        "qntmc 107: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 107: the gateway routes each request by policy", "AgentU"),
        "ruyaw 107: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 107: the gateway routes each request by policy", "keyboard"),
        "bssor 107: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 107: the gateway routes each request by policy", "AA"),
        "round 107: the gateway routes each request by policy",
    ),
    (("round 107: memory grows until the buffer is full", "key"), "bssxh 107: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 107: memory grows until the buffer is full", "lemon"), "csgbq 107: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 107: memory grows until the buffer is full", "a"), "round 107: memory grows until the buffer is full"),
    (("round 107: memory grows until the buffer is full", "zz"), "qntmc 107: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 107: memory grows until the buffer is full", "AgentU"),
        "ruyaw 107: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 107: memory grows until the buffer is full", "keyboard"),
        "bssor 107: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 107: memory grows until the buffer is full", "AA"), "round 107: memory grows until the buffer is full"),
    (("round 107: the cluster mirrors every packet twice", "key"), "bssxh 107: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 107: the cluster mirrors every packet twice", "lemon"),
        "csgbq 107: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 107: the cluster mirrors every packet twice", "a"), "round 107: the cluster mirrors every packet twice"),
    (("round 107: the cluster mirrors every packet twice", "zz"), "qntmc 107: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 107: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 107: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 107: the cluster mirrors every packet twice", "keyboard"),
        "bssor 107: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 107: the cluster mirrors every packet twice", "AA"), "round 107: the cluster mirrors every packet twice"),
    (
        ("round 107: ranking uses tokens learned from the corpus", "key"),
        "bssxh 107: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 107: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", "a"),
        "round 107: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 107: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 107: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 107: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", "AA"),
        "round 107: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 107: a long session ends when the candle dies", "key"),
        "bssxh 107: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 107: a long session ends when the candle dies", "lemon"),
        "csgbq 107: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 107: a long session ends when the candle dies", "a"),
        "round 107: a long session ends when the candle dies",
    ),
    (
        ("round 107: a long session ends when the candle dies", "zz"),
        "qntmc 107: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 107: a long session ends when the candle dies", "AgentU"),
        "ruyaw 107: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 107: a long session ends when the candle dies", "keyboard"),
        "bssor 107: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 107: a long session ends when the candle dies", "AA"),
        "round 107: a long session ends when the candle dies",
    ),
    (("round 107: encode the prompt then map the result", "key"), "bssxh 107: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 107: encode the prompt then map the result", "lemon"), "csgbq 107: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 107: encode the prompt then map the result", "a"), "round 107: encode the prompt then map the result"),
    (("round 107: encode the prompt then map the result", "zz"), "qntmc 107: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 107: encode the prompt then map the result", "AgentU"),
        "ruyaw 107: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 107: encode the prompt then map the result", "keyboard"),
        "bssor 107: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 107: encode the prompt then map the result", "AA"), "round 107: encode the prompt then map the result"),
    (("round 107: the kernel wakes the worker at dawn", "key"), "bssxh 107: rri iovlop ukocc xfo ambocb er neux"),
    (("round 107: the kernel wakes the worker at dawn", "lemon"), "csgbq 107: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 107: the kernel wakes the worker at dawn", "a"), "round 107: the kernel wakes the worker at dawn"),
    (("round 107: the kernel wakes the worker at dawn", "zz"), "qntmc 107: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 107: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 107: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 107: the kernel wakes the worker at dawn", "keyboard"), "bssor 107: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 107: the kernel wakes the worker at dawn", "AA"), "round 107: the kernel wakes the worker at dawn"),
    (("round 107: service latency drops after the patch", "key"), "bssxh 107: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 107: service latency drops after the patch", "lemon"), "csgbq 107: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 107: service latency drops after the patch", "a"), "round 107: service latency drops after the patch"),
    (("round 107: service latency drops after the patch", "zz"), "qntmc 107: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 107: service latency drops after the patch", "AgentU"),
        "ruyaw 107: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 107: service latency drops after the patch", "keyboard"),
        "bssor 107: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 107: service latency drops after the patch", "AA"), "round 107: service latency drops after the patch"),
    (
        ("round 107: the library caches every vector it sees", "key"),
        "bssxh 107: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 107: the library caches every vector it sees", "lemon"),
        "csgbq 107: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 107: the library caches every vector it sees", "a"), "round 107: the library caches every vector it sees"),
    (
        ("round 107: the library caches every vector it sees", "zz"),
        "qntmc 107: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 107: the library caches every vector it sees", "AgentU"),
        "ruyaw 107: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 107: the library caches every vector it sees", "keyboard"),
        "bssor 107: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 107: the library caches every vector it sees", "AA"),
        "round 107: the library caches every vector it sees",
    ),
    (("round 107: agents argue then the debate resolves", "key"), "bssxh 107: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 107: agents argue then the debate resolves", "lemon"), "csgbq 107: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 107: agents argue then the debate resolves", "a"), "round 107: agents argue then the debate resolves"),
    (("round 107: agents argue then the debate resolves", "zz"), "qntmc 107: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 107: agents argue then the debate resolves", "AgentU"),
        "ruyaw 107: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 107: agents argue then the debate resolves", "keyboard"),
        "bssor 107: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 107: agents argue then the debate resolves", "AA"), "round 107: agents argue then the debate resolves"),
    (("round 107: the filter keeps only strong matches", "key"), "bssxh 107: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 107: the filter keeps only strong matches", "lemon"), "csgbq 107: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 107: the filter keeps only strong matches", "a"), "round 107: the filter keeps only strong matches"),
    (("round 107: the filter keeps only strong matches", "zz"), "qntmc 107: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 107: the filter keeps only strong matches", "AgentU"), "ruyaw 107: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 107: the filter keeps only strong matches", "keyboard"),
        "bssor 107: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 107: the filter keeps only strong matches", "AA"), "round 107: the filter keeps only strong matches"),
    (("round 107: the model answers with a short reply", "key"), "bssxh 107: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 107: the model answers with a short reply", "lemon"), "csgbq 107: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 107: the model answers with a short reply", "a"), "round 107: the model answers with a short reply"),
    (("round 107: the model answers with a short reply", "zz"), "qntmc 107: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 107: the model answers with a short reply", "AgentU"), "ruyaw 107: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 107: the model answers with a short reply", "keyboard"),
        "bssor 107: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 107: the model answers with a short reply", "AA"), "round 107: the model answers with a short reply"),
    (
        ("round 107: the recorder stores the reasoning trace", "key"),
        "bssxh 107: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 107: the recorder stores the reasoning trace", "lemon"),
        "csgbq 107: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 107: the recorder stores the reasoning trace", "a"), "round 107: the recorder stores the reasoning trace"),
    (
        ("round 107: the recorder stores the reasoning trace", "zz"),
        "qntmc 107: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 107: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 107: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 107: the recorder stores the reasoning trace", "keyboard"),
        "bssor 107: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 107: the recorder stores the reasoning trace", "AA"),
        "round 107: the recorder stores the reasoning trace",
    ),
    (("round 107: the angel watches the processor run", "key"), "bssxh 107: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 107: the angel watches the processor run", "lemon"), "csgbq 107: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 107: the angel watches the processor run", "a"), "round 107: the angel watches the processor run"),
    (("round 107: the angel watches the processor run", "zz"), "qntmc 107: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 107: the angel watches the processor run", "AgentU"), "ruyaw 107: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 107: the angel watches the processor run", "keyboard"), "bssor 107: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 107: the angel watches the processor run", "AA"), "round 107: the angel watches the processor run"),
    (("round 107: angle of the vector decides the match", "key"), "bssxh 107: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 107: angle of the vector decides the match", "lemon"), "csgbq 107: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 107: angle of the vector decides the match", "a"), "round 107: angle of the vector decides the match"),
    (("round 107: angle of the vector decides the match", "zz"), "qntmc 107: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 107: angle of the vector decides the match", "AgentU"),
        "ruyaw 107: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 107: angle of the vector decides the match", "keyboard"),
        "bssor 107: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 107: angle of the vector decides the match", "AA"), "round 107: angle of the vector decides the match"),
    (
        ("round 107: the candle burns twice as long at night", "key"),
        "bssxh 107: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 107: the candle burns twice as long at night", "lemon"),
        "csgbq 107: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 107: the candle burns twice as long at night", "a"), "round 107: the candle burns twice as long at night"),
    (
        ("round 107: the candle burns twice as long at night", "zz"),
        "qntmc 107: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 107: the candle burns twice as long at night", "AgentU"),
        "ruyaw 107: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 107: the candle burns twice as long at night", "keyboard"),
        "bssor 107: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 107: the candle burns twice as long at night", "AA"),
        "round 107: the candle burns twice as long at night",
    ),
    (("round 107: a mirror of the universe in one line", "key"), "bssxh 107: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 107: a mirror of the universe in one line", "lemon"), "csgbq 107: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 107: a mirror of the universe in one line", "a"), "round 107: a mirror of the universe in one line"),
    (("round 107: a mirror of the universe in one line", "zz"), "qntmc 107: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 107: a mirror of the universe in one line", "AgentU"), "ruyaw 107: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 107: a mirror of the universe in one line", "keyboard"),
        "bssor 107: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 107: a mirror of the universe in one line", "AA"), "round 107: a mirror of the universe in one line"),
    (("round 107: the queue drains before the storm", "key"), "bssxh 107: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 107: the queue drains before the storm", "lemon"), "csgbq 107: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 107: the queue drains before the storm", "a"), "round 107: the queue drains before the storm"),
    (("round 107: the queue drains before the storm", "zz"), "qntmc 107: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 107: the queue drains before the storm", "AgentU"), "ruyaw 107: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 107: the queue drains before the storm", "keyboard"), "bssor 107: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 107: the queue drains before the storm", "AA"), "round 107: the queue drains before the storm"),
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
