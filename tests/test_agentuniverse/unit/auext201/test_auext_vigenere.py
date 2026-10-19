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
    (("kitten201", "key"), "umrdil201"),
    (("kitten201", "lemon"), "vmfhry201"),
    (("kitten201", "a"), "kitten201"),
    (("kitten201", "zz"), "jhssdm201"),
    (("kitten201", "AgentU"), "koxgxh201"),
    (("kitten201", "keyboard"), "umrusn201"),
    (("kitten201", "AA"), "kitten201"),
    (("sitting201", "key"), "cmrdmlq201"),
    (("sitting201", "lemon"), "dmfhvyk201"),
    (("sitting201", "a"), "sitting201"),
    (("sitting201", "zz"), "rhsshmf201"),
    (("sitting201", "AgentU"), "soxgbhg201"),
    (("sitting201", "keyboard"), "cmruwnx201"),
    (("sitting201", "AA"), "sitting201"),
    (("agent201", "key"), "kkcxx201"),
    (("agent201", "lemon"), "lkqbg201"),
    (("agent201", "a"), "agent201"),
    (("agent201", "zz"), "zfdms201"),
    (("agent201", "AgentU"), "amiam201"),
    (("agent201", "keyboard"), "kkcoh201"),
    (("agent201", "AA"), "agent201"),
    (("angle201", "key"), "krevi201"),
    (("angle201", "lemon"), "lrszr201"),
    (("angle201", "a"), "angle201"),
    (("angle201", "zz"), "zmfkd201"),
    (("angle201", "AgentU"), "atkyx201"),
    (("angle201", "keyboard"), "krems201"),
    (("angle201", "AA"), "angle201"),
    (("universe201", "key"), "ergfipci201"),
    (("universe201", "lemon"), "frujrcwq201"),
    (("universe201", "a"), "universe201"),
    (("universe201", "zz"), "tmhudqrd201"),
    (("universe201", "AgentU"), "utmixlsk201"),
    (("universe201", "keyboard"), "ergwsrjh201"),
    (("universe201", "AA"), "universe201"),
    (("memory201", "key"), "wikyvw201"),
    (("memory201", "lemon"), "xiycej201"),
    (("memory201", "a"), "memory201"),
    (("memory201", "zz"), "ldlnqx201"),
    (("memory201", "AgentU"), "mkqbks201"),
    (("memory201", "keyboard"), "wikpfy201"),
    (("memory201", "AA"), "memory201"),
    (("stream201", "key"), "cxpoek201"),
    (("stream201", "lemon"), "dxdsnx201"),
    (("stream201", "a"), "stream201"),
    (("stream201", "zz"), "rsqdzl201"),
    (("stream201", "AgentU"), "szvrtg201"),
    (("stream201", "keyboard"), "cxpfom201"),
    (("stream201", "AA"), "stream201"),
    (("context201", "key"), "msldivd201"),
    (("context201", "lemon"), "nszhrix201"),
    (("context201", "a"), "context201"),
    (("context201", "zz"), "bnmsdws201"),
    (("context201", "AgentU"), "curgxrt201"),
    (("context201", "keyboard"), "mslusxk201"),
    (("context201", "AA"), "context201"),
    (("knowledge201", "key"), "urmgpcnkc201"),
    (("knowledge201", "lemon"), "vrakyphss201"),
    (("knowledge201", "a"), "knowledge201"),
    (("knowledge201", "zz"), "jmnvkdcfd201"),
    (("knowledge201", "AgentU"), "ktsjeydmi201"),
    (("knowledge201", "keyboard"), "urmxzeujo201"),
    (("knowledge201", "AA"), "knowledge201"),
    (("vector201", "key"), "fiadsp201"),
    (("vector201", "lemon"), "giohbc201"),
    (("vector201", "a"), "vector201"),
    (("vector201", "zz"), "udbsnq201"),
    (("vector201", "AgentU"), "vkgghl201"),
    (("vector201", "keyboard"), "fiaucr201"),
    (("vector201", "AA"), "vector201"),
    (("processor201", "key"), "zvmmiqcsp201"),
    (("processor201", "lemon"), "avaqrdwaf201"),
    (("processor201", "a"), "processor201"),
    (("processor201", "zz"), "oqnbdrrnq201"),
    (("processor201", "AgentU"), "pxspxmsuv201"),
    (("processor201", "keyboard"), "zvmdssjrb201"),
    (("processor201", "AA"), "processor201"),
    (("reasoning201", "key"), "biycslsre201"),
    (("reasoning201", "lemon"), "cimgbymzu201"),
    (("reasoning201", "a"), "reasoning201"),
    (("reasoning201", "zz"), "qdzrnmhmf201"),
    (("reasoning201", "AgentU"), "rkefhhitk201"),
    (("reasoning201", "keyboard"), "biytcnzqq201"),
    (("reasoning201", "AA"), "reasoning201"),
    (("machine201", "key"), "wearmlo201"),
    (("machine201", "lemon"), "xeovvyi201"),
    (("machine201", "a"), "machine201"),
    (("machine201", "zz"), "lzbghmd201"),
    (("machine201", "AgentU"), "mggubhe201"),
    (("machine201", "keyboard"), "weaiwnv201"),
    (("machine201", "AA"), "machine201"),
    (("learning201", "key"), "viybrgxk201"),
    (("learning201", "lemon"), "wimfatrs201"),
    (("learning201", "a"), "learning201"),
    (("learning201", "zz"), "kdzqmhmf201"),
    (("learning201", "AgentU"), "lkeegcnm201"),
    (("learning201", "keyboard"), "viysbiej201"),
    (("learning201", "AA"), "learning201"),
    (("model201", "key"), "wsbop201"),
    (("model201", "lemon"), "xspsy201"),
    (("model201", "a"), "model201"),
    (("model201", "zz"), "lncdk201"),
    (("model201", "AgentU"), "muhre201"),
    (("model201", "keyboard"), "wsbfz201"),
    (("model201", "AA"), "model201"),
    (("token201", "key"), "dsior201"),
    (("token201", "lemon"), "eswsa201"),
    (("token201", "a"), "token201"),
    (("token201", "zz"), "snjdm201"),
    (("token201", "AgentU"), "tuorg201"),
    (("token201", "keyboard"), "dsifb201"),
    (("token201", "AA"), "token201"),
    (("prompt201", "key"), "zvmwtr201"),
    (("prompt201", "lemon"), "avaace201"),
    (("prompt201", "a"), "prompt201"),
    (("prompt201", "zz"), "oqnlos201"),
    (("prompt201", "AgentU"), "pxszin201"),
    (("prompt201", "keyboard"), "zvmndt201"),
    (("prompt201", "AA"), "prompt201"),
    (("session201", "key"), "ciqcmmx201"),
    (("session201", "lemon"), "diegvzr201"),
    (("session201", "a"), "session201"),
    (("session201", "zz"), "rdrrhnm201"),
    (("session201", "AgentU"), "skwfbin201"),
    (("session201", "keyboard"), "ciqtwoe201"),
    (("session201", "AA"), "session201"),
    (("library201", "key"), "vmzbepi201"),
    (("library201", "lemon"), "wmnfncc201"),
    (("library201", "a"), "library201"),
    (("library201", "zz"), "khaqzqx201"),
    (("library201", "AgentU"), "lofetly201"),
    (("library201", "keyboard"), "vmzsorp201"),
    (("library201", "AA"), "library201"),
    (("service201", "key"), "cipfmao201"),
    (("service201", "lemon"), "didjvni201"),
    (("service201", "a"), "service201"),
    (("service201", "zz"), "rdquhbd201"),
    (("service201", "AgentU"), "skvibwe201"),
    (("service201", "keyboard"), "cipwwcv201"),
    (("service201", "AA"), "service201"),
    (("gateway201", "key"), "qeroayi201"),
    (("gateway201", "lemon"), "refsjlc201"),
    (("gateway201", "a"), "gateway201"),
    (("gateway201", "zz"), "fzsdvzx201"),
    (("gateway201", "AgentU"), "ggxrpuy201"),
    (("gateway201", "keyboard"), "qerfkap201"),
    (("gateway201", "AA"), "gateway201"),
    (("storage201", "key"), "cxmbeeo201"),
    (("storage201", "lemon"), "dxafnri201"),
    (("storage201", "a"), "storage201"),
    (("storage201", "zz"), "rsnqzfd201"),
    (("storage201", "AgentU"), "szsetae201"),
    (("storage201", "keyboard"), "cxmsogv201"),
    (("storage201", "AA"), "storage201"),
    (("network201", "key"), "xirgspu201"),
    (("network201", "lemon"), "yifkbco201"),
    (("network201", "a"), "network201"),
    (("network201", "zz"), "mdsvnqj201"),
    (("network201", "AgentU"), "nkxjhlk201"),
    (("network201", "keyboard"), "xirxcrb201"),
    (("network201", "AA"), "network201"),
    (("latency201", "key"), "verorai201"),
    (("latency201", "lemon"), "wefsanc201"),
    (("latency201", "a"), "latency201"),
    (("latency201", "zz"), "kzsdmbx201"),
    (("latency201", "AgentU"), "lgxrgwy201"),
    (("latency201", "keyboard"), "verfbcp201"),
    (("latency201", "AA"), "latency201"),
    (("buffer201", "key"), "lydpip201"),
    (("buffer201", "lemon"), "myrtrc201"),
    (("buffer201", "a"), "buffer201"),
    (("buffer201", "zz"), "ateedq201"),
    (("buffer201", "AgentU"), "bajsxl201"),
    (("buffer201", "keyboard"), "lydgsr201"),
    (("buffer201", "AA"), "buffer201"),
    (("queue201", "key"), "aycei201"),
    (("queue201", "lemon"), "byqir201"),
    (("queue201", "a"), "queue201"),
    (("queue201", "zz"), "ptdtd201"),
    (("queue201", "AgentU"), "qaihx201"),
    (("queue201", "keyboard"), "aycvs201"),
    (("queue201", "AA"), "queue201"),
    (("worker201", "key"), "gspuip201"),
    (("worker201", "lemon"), "hsdyrc201"),
    (("worker201", "a"), "worker201"),
    (("worker201", "zz"), "vnqjdq201"),
    (("worker201", "AgentU"), "wuvxxl201"),
    (("worker201", "keyboard"), "gsplsr201"),
    (("worker201", "AA"), "worker201"),
    (("kernel201", "key"), "uipxij201"),
    (("kernel201", "lemon"), "vidbrw201"),
    (("kernel201", "a"), "kernel201"),
    (("kernel201", "zz"), "jdqmdk201"),
    (("kernel201", "AgentU"), "kkvaxf201"),
    (("kernel201", "keyboard"), "uiposl201"),
    (("kernel201", "AA"), "kernel201"),
    (("signal201", "key"), "cmexej201"),
    (("signal201", "lemon"), "dmsbnw201"),
    (("signal201", "a"), "signal201"),
    (("signal201", "zz"), "rhfmzk201"),
    (("signal201", "AgentU"), "sokatf201"),
    (("signal201", "keyboard"), "cmeool201"),
    (("signal201", "AA"), "signal201"),
    (("packet201", "key"), "zeauir201"),
    (("packet201", "lemon"), "aeoyre201"),
    (("packet201", "a"), "packet201"),
    (("packet201", "zz"), "ozbjds201"),
    (("packet201", "AgentU"), "pggxxn201"),
    (("packet201", "keyboard"), "zealst201"),
    (("packet201", "AA"), "packet201"),
    (("router201", "key"), "bssdip201"),
    (("router201", "lemon"), "csghrc201"),
    (("router201", "a"), "router201"),
    (("router201", "zz"), "qntsdq201"),
    (("router201", "AgentU"), "ruygxl201"),
    (("router201", "keyboard"), "bssusr201"),
    (("router201", "AA"), "router201"),
    (("cluster201", "key"), "mpscxcb201"),
    (("cluster201", "lemon"), "npgggpv201"),
    (("cluster201", "a"), "cluster201"),
    (("cluster201", "zz"), "bktrsdq201"),
    (("cluster201", "AgentU"), "cryfmyr201"),
    (("cluster201", "keyboard"), "mpsthei201"),
    (("cluster201", "AA"), "cluster201"),
    (("mirror201", "key"), "wmpbsp201"),
    (("mirror201", "lemon"), "xmdfbc201"),
    (("mirror201", "a"), "mirror201"),
    (("mirror201", "zz"), "lhqqnq201"),
    (("mirror201", "AgentU"), "movehl201"),
    (("mirror201", "keyboard"), "wmpscr201"),
    (("mirror201", "AA"), "mirror201"),
    (("filter201", "key"), "pmjdip201"),
    (("filter201", "lemon"), "qmxhrc201"),
    (("filter201", "a"), "filter201"),
    (("filter201", "zz"), "ehksdq201"),
    (("filter201", "AgentU"), "fopgxl201"),
    (("filter201", "keyboard"), "pmjusr201"),
    (("filter201", "AA"), "filter201"),
    (("ranking201", "key"), "belumlq201"),
    (("ranking201", "lemon"), "cezyvyk201"),
    (("ranking201", "a"), "ranking201"),
    (("ranking201", "zz"), "qzmjhmf201"),
    (("ranking201", "AgentU"), "rgrxbhg201"),
    (("ranking201", "keyboard"), "bellwnx201"),
    (("ranking201", "AA"), "ranking201"),
    (("encoding201", "key"), "orayhgxk201"),
    (("encoding201", "lemon"), "procqtrs201"),
    (("encoding201", "a"), "encoding201"),
    (("encoding201", "zz"), "dmbnchmf201"),
    (("encoding201", "AgentU"), "etgbwcnm201"),
    (("encoding201", "keyboard"), "orapriej201"),
    (("encoding201", "AA"), "encoding201"),
    (("mapping201", "key"), "wenzmlq201"),
    (("mapping201", "lemon"), "xebdvyk201"),
    (("mapping201", "a"), "mapping201"),
    (("mapping201", "zz"), "lzoohmf201"),
    (("mapping201", "AgentU"), "mgtcbhg201"),
    (("mapping201", "keyboard"), "wenqwnx201"),
    (("mapping201", "AA"), "mapping201"),
    (("record201", "key"), "biayvb201"),
    (("record201", "lemon"), "cioceo201"),
    (("record201", "a"), "record201"),
    (("record201", "zz"), "qdbnqc201"),
    (("record201", "AgentU"), "rkgbkx201"),
    (("record201", "keyboard"), "biapfd201"),
    (("record201", "AA"), "record201"),
    (("candle201", "key"), "melnpc201"),
    (("candle201", "lemon"), "nezryp201"),
    (("candle201", "a"), "candle201"),
    (("candle201", "zz"), "bzmckd201"),
    (("candle201", "AgentU"), "cgrqey201"),
    (("candle201", "keyboard"), "meleze201"),
    (("candle201", "AA"), "candle201"),
    (("thread201", "key"), "dlpoeb201"),
    (("thread201", "lemon"), "eldsno201"),
    (("thread201", "a"), "thread201"),
    (("thread201", "zz"), "sgqdzc201"),
    (("thread201", "AgentU"), "tnvrtx201"),
    (("thread201", "keyboard"), "dlpfod201"),
    (("thread201", "AA"), "thread201"),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 201: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 201: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "a"),
        "round 201: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 201: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 201: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 201: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", "AA"),
        "round 201: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "key"),
        "bssxh 201: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 201: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "a"),
        "round 201: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 201: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 201: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 201: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", "AA"),
        "round 201: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 201: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 201: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "a"),
        "round 201: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 201: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 201: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 201: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", "AA"),
        "round 201: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 201: the processor reads the record then stops", "key"),
        "bssxh 201: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 201: the processor reads the record then stops", "lemon"),
        "csgbq 201: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 201: the processor reads the record then stops", "a"),
        "round 201: the processor reads the record then stops",
    ),
    (
        ("round 201: the processor reads the record then stops", "zz"),
        "qntmc 201: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 201: the processor reads the record then stops", "AgentU"),
        "ruyaw 201: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 201: the processor reads the record then stops", "keyboard"),
        "bssor 201: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 201: the processor reads the record then stops", "AA"),
        "round 201: the processor reads the record then stops",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "key"),
        "bssxh 201: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "lemon"),
        "csgbq 201: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "a"),
        "round 201: a worker pulls the next task from the queue",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "zz"),
        "qntmc 201: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 201: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "keyboard"),
        "bssor 201: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 201: a worker pulls the next task from the queue", "AA"),
        "round 201: a worker pulls the next task from the queue",
    ),
    (
        ("round 201: signals travel through the network layer", "key"),
        "bssxh 201: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 201: signals travel through the network layer", "lemon"),
        "csgbq 201: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 201: signals travel through the network layer", "a"),
        "round 201: signals travel through the network layer",
    ),
    (
        ("round 201: signals travel through the network layer", "zz"),
        "qntmc 201: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 201: signals travel through the network layer", "AgentU"),
        "ruyaw 201: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 201: signals travel through the network layer", "keyboard"),
        "bssor 201: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 201: signals travel through the network layer", "AA"),
        "round 201: signals travel through the network layer",
    ),
    (
        ("round 201: the gateway routes each request by policy", "key"),
        "bssxh 201: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 201: the gateway routes each request by policy", "lemon"),
        "csgbq 201: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 201: the gateway routes each request by policy", "a"),
        "round 201: the gateway routes each request by policy",
    ),
    (
        ("round 201: the gateway routes each request by policy", "zz"),
        "qntmc 201: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 201: the gateway routes each request by policy", "AgentU"),
        "ruyaw 201: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 201: the gateway routes each request by policy", "keyboard"),
        "bssor 201: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 201: the gateway routes each request by policy", "AA"),
        "round 201: the gateway routes each request by policy",
    ),
    (("round 201: memory grows until the buffer is full", "key"), "bssxh 201: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 201: memory grows until the buffer is full", "lemon"), "csgbq 201: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 201: memory grows until the buffer is full", "a"), "round 201: memory grows until the buffer is full"),
    (("round 201: memory grows until the buffer is full", "zz"), "qntmc 201: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 201: memory grows until the buffer is full", "AgentU"),
        "ruyaw 201: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 201: memory grows until the buffer is full", "keyboard"),
        "bssor 201: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 201: memory grows until the buffer is full", "AA"), "round 201: memory grows until the buffer is full"),
    (("round 201: the cluster mirrors every packet twice", "key"), "bssxh 201: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 201: the cluster mirrors every packet twice", "lemon"),
        "csgbq 201: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 201: the cluster mirrors every packet twice", "a"), "round 201: the cluster mirrors every packet twice"),
    (("round 201: the cluster mirrors every packet twice", "zz"), "qntmc 201: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 201: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 201: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 201: the cluster mirrors every packet twice", "keyboard"),
        "bssor 201: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 201: the cluster mirrors every packet twice", "AA"), "round 201: the cluster mirrors every packet twice"),
    (
        ("round 201: ranking uses tokens learned from the corpus", "key"),
        "bssxh 201: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 201: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", "a"),
        "round 201: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 201: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 201: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 201: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", "AA"),
        "round 201: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 201: a long session ends when the candle dies", "key"),
        "bssxh 201: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 201: a long session ends when the candle dies", "lemon"),
        "csgbq 201: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 201: a long session ends when the candle dies", "a"),
        "round 201: a long session ends when the candle dies",
    ),
    (
        ("round 201: a long session ends when the candle dies", "zz"),
        "qntmc 201: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 201: a long session ends when the candle dies", "AgentU"),
        "ruyaw 201: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 201: a long session ends when the candle dies", "keyboard"),
        "bssor 201: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 201: a long session ends when the candle dies", "AA"),
        "round 201: a long session ends when the candle dies",
    ),
    (("round 201: encode the prompt then map the result", "key"), "bssxh 201: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 201: encode the prompt then map the result", "lemon"), "csgbq 201: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 201: encode the prompt then map the result", "a"), "round 201: encode the prompt then map the result"),
    (("round 201: encode the prompt then map the result", "zz"), "qntmc 201: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 201: encode the prompt then map the result", "AgentU"),
        "ruyaw 201: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 201: encode the prompt then map the result", "keyboard"),
        "bssor 201: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 201: encode the prompt then map the result", "AA"), "round 201: encode the prompt then map the result"),
    (("round 201: the kernel wakes the worker at dawn", "key"), "bssxh 201: rri iovlop ukocc xfo ambocb er neux"),
    (("round 201: the kernel wakes the worker at dawn", "lemon"), "csgbq 201: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 201: the kernel wakes the worker at dawn", "a"), "round 201: the kernel wakes the worker at dawn"),
    (("round 201: the kernel wakes the worker at dawn", "zz"), "qntmc 201: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 201: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 201: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 201: the kernel wakes the worker at dawn", "keyboard"), "bssor 201: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 201: the kernel wakes the worker at dawn", "AA"), "round 201: the kernel wakes the worker at dawn"),
    (("round 201: service latency drops after the patch", "key"), "bssxh 201: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 201: service latency drops after the patch", "lemon"), "csgbq 201: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 201: service latency drops after the patch", "a"), "round 201: service latency drops after the patch"),
    (("round 201: service latency drops after the patch", "zz"), "qntmc 201: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 201: service latency drops after the patch", "AgentU"),
        "ruyaw 201: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 201: service latency drops after the patch", "keyboard"),
        "bssor 201: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 201: service latency drops after the patch", "AA"), "round 201: service latency drops after the patch"),
    (
        ("round 201: the library caches every vector it sees", "key"),
        "bssxh 201: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 201: the library caches every vector it sees", "lemon"),
        "csgbq 201: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 201: the library caches every vector it sees", "a"), "round 201: the library caches every vector it sees"),
    (
        ("round 201: the library caches every vector it sees", "zz"),
        "qntmc 201: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 201: the library caches every vector it sees", "AgentU"),
        "ruyaw 201: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 201: the library caches every vector it sees", "keyboard"),
        "bssor 201: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 201: the library caches every vector it sees", "AA"),
        "round 201: the library caches every vector it sees",
    ),
    (("round 201: agents argue then the debate resolves", "key"), "bssxh 201: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 201: agents argue then the debate resolves", "lemon"), "csgbq 201: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 201: agents argue then the debate resolves", "a"), "round 201: agents argue then the debate resolves"),
    (("round 201: agents argue then the debate resolves", "zz"), "qntmc 201: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 201: agents argue then the debate resolves", "AgentU"),
        "ruyaw 201: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 201: agents argue then the debate resolves", "keyboard"),
        "bssor 201: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 201: agents argue then the debate resolves", "AA"), "round 201: agents argue then the debate resolves"),
    (("round 201: the filter keeps only strong matches", "key"), "bssxh 201: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 201: the filter keeps only strong matches", "lemon"), "csgbq 201: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 201: the filter keeps only strong matches", "a"), "round 201: the filter keeps only strong matches"),
    (("round 201: the filter keeps only strong matches", "zz"), "qntmc 201: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 201: the filter keeps only strong matches", "AgentU"), "ruyaw 201: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 201: the filter keeps only strong matches", "keyboard"),
        "bssor 201: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 201: the filter keeps only strong matches", "AA"), "round 201: the filter keeps only strong matches"),
    (("round 201: the model answers with a short reply", "key"), "bssxh 201: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 201: the model answers with a short reply", "lemon"), "csgbq 201: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 201: the model answers with a short reply", "a"), "round 201: the model answers with a short reply"),
    (("round 201: the model answers with a short reply", "zz"), "qntmc 201: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 201: the model answers with a short reply", "AgentU"), "ruyaw 201: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 201: the model answers with a short reply", "keyboard"),
        "bssor 201: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 201: the model answers with a short reply", "AA"), "round 201: the model answers with a short reply"),
    (
        ("round 201: the recorder stores the reasoning trace", "key"),
        "bssxh 201: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 201: the recorder stores the reasoning trace", "lemon"),
        "csgbq 201: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 201: the recorder stores the reasoning trace", "a"), "round 201: the recorder stores the reasoning trace"),
    (
        ("round 201: the recorder stores the reasoning trace", "zz"),
        "qntmc 201: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 201: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 201: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 201: the recorder stores the reasoning trace", "keyboard"),
        "bssor 201: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 201: the recorder stores the reasoning trace", "AA"),
        "round 201: the recorder stores the reasoning trace",
    ),
    (("round 201: the angel watches the processor run", "key"), "bssxh 201: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 201: the angel watches the processor run", "lemon"), "csgbq 201: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 201: the angel watches the processor run", "a"), "round 201: the angel watches the processor run"),
    (("round 201: the angel watches the processor run", "zz"), "qntmc 201: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 201: the angel watches the processor run", "AgentU"), "ruyaw 201: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 201: the angel watches the processor run", "keyboard"), "bssor 201: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 201: the angel watches the processor run", "AA"), "round 201: the angel watches the processor run"),
    (("round 201: angle of the vector decides the match", "key"), "bssxh 201: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 201: angle of the vector decides the match", "lemon"), "csgbq 201: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 201: angle of the vector decides the match", "a"), "round 201: angle of the vector decides the match"),
    (("round 201: angle of the vector decides the match", "zz"), "qntmc 201: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 201: angle of the vector decides the match", "AgentU"),
        "ruyaw 201: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 201: angle of the vector decides the match", "keyboard"),
        "bssor 201: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 201: angle of the vector decides the match", "AA"), "round 201: angle of the vector decides the match"),
    (
        ("round 201: the candle burns twice as long at night", "key"),
        "bssxh 201: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 201: the candle burns twice as long at night", "lemon"),
        "csgbq 201: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 201: the candle burns twice as long at night", "a"), "round 201: the candle burns twice as long at night"),
    (
        ("round 201: the candle burns twice as long at night", "zz"),
        "qntmc 201: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 201: the candle burns twice as long at night", "AgentU"),
        "ruyaw 201: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 201: the candle burns twice as long at night", "keyboard"),
        "bssor 201: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 201: the candle burns twice as long at night", "AA"),
        "round 201: the candle burns twice as long at night",
    ),
    (("round 201: a mirror of the universe in one line", "key"), "bssxh 201: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 201: a mirror of the universe in one line", "lemon"), "csgbq 201: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 201: a mirror of the universe in one line", "a"), "round 201: a mirror of the universe in one line"),
    (("round 201: a mirror of the universe in one line", "zz"), "qntmc 201: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 201: a mirror of the universe in one line", "AgentU"), "ruyaw 201: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 201: a mirror of the universe in one line", "keyboard"),
        "bssor 201: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 201: a mirror of the universe in one line", "AA"), "round 201: a mirror of the universe in one line"),
    (("round 201: the queue drains before the storm", "key"), "bssxh 201: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 201: the queue drains before the storm", "lemon"), "csgbq 201: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 201: the queue drains before the storm", "a"), "round 201: the queue drains before the storm"),
    (("round 201: the queue drains before the storm", "zz"), "qntmc 201: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 201: the queue drains before the storm", "AgentU"), "ruyaw 201: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 201: the queue drains before the storm", "keyboard"), "bssor 201: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 201: the queue drains before the storm", "AA"), "round 201: the queue drains before the storm"),
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
