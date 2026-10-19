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
    (("kitten132", "key"), "umrdil132"),
    (("kitten132", "lemon"), "vmfhry132"),
    (("kitten132", "a"), "kitten132"),
    (("kitten132", "zz"), "jhssdm132"),
    (("kitten132", "AgentU"), "koxgxh132"),
    (("kitten132", "keyboard"), "umrusn132"),
    (("kitten132", "AA"), "kitten132"),
    (("sitting132", "key"), "cmrdmlq132"),
    (("sitting132", "lemon"), "dmfhvyk132"),
    (("sitting132", "a"), "sitting132"),
    (("sitting132", "zz"), "rhsshmf132"),
    (("sitting132", "AgentU"), "soxgbhg132"),
    (("sitting132", "keyboard"), "cmruwnx132"),
    (("sitting132", "AA"), "sitting132"),
    (("agent132", "key"), "kkcxx132"),
    (("agent132", "lemon"), "lkqbg132"),
    (("agent132", "a"), "agent132"),
    (("agent132", "zz"), "zfdms132"),
    (("agent132", "AgentU"), "amiam132"),
    (("agent132", "keyboard"), "kkcoh132"),
    (("agent132", "AA"), "agent132"),
    (("angle132", "key"), "krevi132"),
    (("angle132", "lemon"), "lrszr132"),
    (("angle132", "a"), "angle132"),
    (("angle132", "zz"), "zmfkd132"),
    (("angle132", "AgentU"), "atkyx132"),
    (("angle132", "keyboard"), "krems132"),
    (("angle132", "AA"), "angle132"),
    (("universe132", "key"), "ergfipci132"),
    (("universe132", "lemon"), "frujrcwq132"),
    (("universe132", "a"), "universe132"),
    (("universe132", "zz"), "tmhudqrd132"),
    (("universe132", "AgentU"), "utmixlsk132"),
    (("universe132", "keyboard"), "ergwsrjh132"),
    (("universe132", "AA"), "universe132"),
    (("memory132", "key"), "wikyvw132"),
    (("memory132", "lemon"), "xiycej132"),
    (("memory132", "a"), "memory132"),
    (("memory132", "zz"), "ldlnqx132"),
    (("memory132", "AgentU"), "mkqbks132"),
    (("memory132", "keyboard"), "wikpfy132"),
    (("memory132", "AA"), "memory132"),
    (("stream132", "key"), "cxpoek132"),
    (("stream132", "lemon"), "dxdsnx132"),
    (("stream132", "a"), "stream132"),
    (("stream132", "zz"), "rsqdzl132"),
    (("stream132", "AgentU"), "szvrtg132"),
    (("stream132", "keyboard"), "cxpfom132"),
    (("stream132", "AA"), "stream132"),
    (("context132", "key"), "msldivd132"),
    (("context132", "lemon"), "nszhrix132"),
    (("context132", "a"), "context132"),
    (("context132", "zz"), "bnmsdws132"),
    (("context132", "AgentU"), "curgxrt132"),
    (("context132", "keyboard"), "mslusxk132"),
    (("context132", "AA"), "context132"),
    (("knowledge132", "key"), "urmgpcnkc132"),
    (("knowledge132", "lemon"), "vrakyphss132"),
    (("knowledge132", "a"), "knowledge132"),
    (("knowledge132", "zz"), "jmnvkdcfd132"),
    (("knowledge132", "AgentU"), "ktsjeydmi132"),
    (("knowledge132", "keyboard"), "urmxzeujo132"),
    (("knowledge132", "AA"), "knowledge132"),
    (("vector132", "key"), "fiadsp132"),
    (("vector132", "lemon"), "giohbc132"),
    (("vector132", "a"), "vector132"),
    (("vector132", "zz"), "udbsnq132"),
    (("vector132", "AgentU"), "vkgghl132"),
    (("vector132", "keyboard"), "fiaucr132"),
    (("vector132", "AA"), "vector132"),
    (("processor132", "key"), "zvmmiqcsp132"),
    (("processor132", "lemon"), "avaqrdwaf132"),
    (("processor132", "a"), "processor132"),
    (("processor132", "zz"), "oqnbdrrnq132"),
    (("processor132", "AgentU"), "pxspxmsuv132"),
    (("processor132", "keyboard"), "zvmdssjrb132"),
    (("processor132", "AA"), "processor132"),
    (("reasoning132", "key"), "biycslsre132"),
    (("reasoning132", "lemon"), "cimgbymzu132"),
    (("reasoning132", "a"), "reasoning132"),
    (("reasoning132", "zz"), "qdzrnmhmf132"),
    (("reasoning132", "AgentU"), "rkefhhitk132"),
    (("reasoning132", "keyboard"), "biytcnzqq132"),
    (("reasoning132", "AA"), "reasoning132"),
    (("machine132", "key"), "wearmlo132"),
    (("machine132", "lemon"), "xeovvyi132"),
    (("machine132", "a"), "machine132"),
    (("machine132", "zz"), "lzbghmd132"),
    (("machine132", "AgentU"), "mggubhe132"),
    (("machine132", "keyboard"), "weaiwnv132"),
    (("machine132", "AA"), "machine132"),
    (("learning132", "key"), "viybrgxk132"),
    (("learning132", "lemon"), "wimfatrs132"),
    (("learning132", "a"), "learning132"),
    (("learning132", "zz"), "kdzqmhmf132"),
    (("learning132", "AgentU"), "lkeegcnm132"),
    (("learning132", "keyboard"), "viysbiej132"),
    (("learning132", "AA"), "learning132"),
    (("model132", "key"), "wsbop132"),
    (("model132", "lemon"), "xspsy132"),
    (("model132", "a"), "model132"),
    (("model132", "zz"), "lncdk132"),
    (("model132", "AgentU"), "muhre132"),
    (("model132", "keyboard"), "wsbfz132"),
    (("model132", "AA"), "model132"),
    (("token132", "key"), "dsior132"),
    (("token132", "lemon"), "eswsa132"),
    (("token132", "a"), "token132"),
    (("token132", "zz"), "snjdm132"),
    (("token132", "AgentU"), "tuorg132"),
    (("token132", "keyboard"), "dsifb132"),
    (("token132", "AA"), "token132"),
    (("prompt132", "key"), "zvmwtr132"),
    (("prompt132", "lemon"), "avaace132"),
    (("prompt132", "a"), "prompt132"),
    (("prompt132", "zz"), "oqnlos132"),
    (("prompt132", "AgentU"), "pxszin132"),
    (("prompt132", "keyboard"), "zvmndt132"),
    (("prompt132", "AA"), "prompt132"),
    (("session132", "key"), "ciqcmmx132"),
    (("session132", "lemon"), "diegvzr132"),
    (("session132", "a"), "session132"),
    (("session132", "zz"), "rdrrhnm132"),
    (("session132", "AgentU"), "skwfbin132"),
    (("session132", "keyboard"), "ciqtwoe132"),
    (("session132", "AA"), "session132"),
    (("library132", "key"), "vmzbepi132"),
    (("library132", "lemon"), "wmnfncc132"),
    (("library132", "a"), "library132"),
    (("library132", "zz"), "khaqzqx132"),
    (("library132", "AgentU"), "lofetly132"),
    (("library132", "keyboard"), "vmzsorp132"),
    (("library132", "AA"), "library132"),
    (("service132", "key"), "cipfmao132"),
    (("service132", "lemon"), "didjvni132"),
    (("service132", "a"), "service132"),
    (("service132", "zz"), "rdquhbd132"),
    (("service132", "AgentU"), "skvibwe132"),
    (("service132", "keyboard"), "cipwwcv132"),
    (("service132", "AA"), "service132"),
    (("gateway132", "key"), "qeroayi132"),
    (("gateway132", "lemon"), "refsjlc132"),
    (("gateway132", "a"), "gateway132"),
    (("gateway132", "zz"), "fzsdvzx132"),
    (("gateway132", "AgentU"), "ggxrpuy132"),
    (("gateway132", "keyboard"), "qerfkap132"),
    (("gateway132", "AA"), "gateway132"),
    (("storage132", "key"), "cxmbeeo132"),
    (("storage132", "lemon"), "dxafnri132"),
    (("storage132", "a"), "storage132"),
    (("storage132", "zz"), "rsnqzfd132"),
    (("storage132", "AgentU"), "szsetae132"),
    (("storage132", "keyboard"), "cxmsogv132"),
    (("storage132", "AA"), "storage132"),
    (("network132", "key"), "xirgspu132"),
    (("network132", "lemon"), "yifkbco132"),
    (("network132", "a"), "network132"),
    (("network132", "zz"), "mdsvnqj132"),
    (("network132", "AgentU"), "nkxjhlk132"),
    (("network132", "keyboard"), "xirxcrb132"),
    (("network132", "AA"), "network132"),
    (("latency132", "key"), "verorai132"),
    (("latency132", "lemon"), "wefsanc132"),
    (("latency132", "a"), "latency132"),
    (("latency132", "zz"), "kzsdmbx132"),
    (("latency132", "AgentU"), "lgxrgwy132"),
    (("latency132", "keyboard"), "verfbcp132"),
    (("latency132", "AA"), "latency132"),
    (("buffer132", "key"), "lydpip132"),
    (("buffer132", "lemon"), "myrtrc132"),
    (("buffer132", "a"), "buffer132"),
    (("buffer132", "zz"), "ateedq132"),
    (("buffer132", "AgentU"), "bajsxl132"),
    (("buffer132", "keyboard"), "lydgsr132"),
    (("buffer132", "AA"), "buffer132"),
    (("queue132", "key"), "aycei132"),
    (("queue132", "lemon"), "byqir132"),
    (("queue132", "a"), "queue132"),
    (("queue132", "zz"), "ptdtd132"),
    (("queue132", "AgentU"), "qaihx132"),
    (("queue132", "keyboard"), "aycvs132"),
    (("queue132", "AA"), "queue132"),
    (("worker132", "key"), "gspuip132"),
    (("worker132", "lemon"), "hsdyrc132"),
    (("worker132", "a"), "worker132"),
    (("worker132", "zz"), "vnqjdq132"),
    (("worker132", "AgentU"), "wuvxxl132"),
    (("worker132", "keyboard"), "gsplsr132"),
    (("worker132", "AA"), "worker132"),
    (("kernel132", "key"), "uipxij132"),
    (("kernel132", "lemon"), "vidbrw132"),
    (("kernel132", "a"), "kernel132"),
    (("kernel132", "zz"), "jdqmdk132"),
    (("kernel132", "AgentU"), "kkvaxf132"),
    (("kernel132", "keyboard"), "uiposl132"),
    (("kernel132", "AA"), "kernel132"),
    (("signal132", "key"), "cmexej132"),
    (("signal132", "lemon"), "dmsbnw132"),
    (("signal132", "a"), "signal132"),
    (("signal132", "zz"), "rhfmzk132"),
    (("signal132", "AgentU"), "sokatf132"),
    (("signal132", "keyboard"), "cmeool132"),
    (("signal132", "AA"), "signal132"),
    (("packet132", "key"), "zeauir132"),
    (("packet132", "lemon"), "aeoyre132"),
    (("packet132", "a"), "packet132"),
    (("packet132", "zz"), "ozbjds132"),
    (("packet132", "AgentU"), "pggxxn132"),
    (("packet132", "keyboard"), "zealst132"),
    (("packet132", "AA"), "packet132"),
    (("router132", "key"), "bssdip132"),
    (("router132", "lemon"), "csghrc132"),
    (("router132", "a"), "router132"),
    (("router132", "zz"), "qntsdq132"),
    (("router132", "AgentU"), "ruygxl132"),
    (("router132", "keyboard"), "bssusr132"),
    (("router132", "AA"), "router132"),
    (("cluster132", "key"), "mpscxcb132"),
    (("cluster132", "lemon"), "npgggpv132"),
    (("cluster132", "a"), "cluster132"),
    (("cluster132", "zz"), "bktrsdq132"),
    (("cluster132", "AgentU"), "cryfmyr132"),
    (("cluster132", "keyboard"), "mpsthei132"),
    (("cluster132", "AA"), "cluster132"),
    (("mirror132", "key"), "wmpbsp132"),
    (("mirror132", "lemon"), "xmdfbc132"),
    (("mirror132", "a"), "mirror132"),
    (("mirror132", "zz"), "lhqqnq132"),
    (("mirror132", "AgentU"), "movehl132"),
    (("mirror132", "keyboard"), "wmpscr132"),
    (("mirror132", "AA"), "mirror132"),
    (("filter132", "key"), "pmjdip132"),
    (("filter132", "lemon"), "qmxhrc132"),
    (("filter132", "a"), "filter132"),
    (("filter132", "zz"), "ehksdq132"),
    (("filter132", "AgentU"), "fopgxl132"),
    (("filter132", "keyboard"), "pmjusr132"),
    (("filter132", "AA"), "filter132"),
    (("ranking132", "key"), "belumlq132"),
    (("ranking132", "lemon"), "cezyvyk132"),
    (("ranking132", "a"), "ranking132"),
    (("ranking132", "zz"), "qzmjhmf132"),
    (("ranking132", "AgentU"), "rgrxbhg132"),
    (("ranking132", "keyboard"), "bellwnx132"),
    (("ranking132", "AA"), "ranking132"),
    (("encoding132", "key"), "orayhgxk132"),
    (("encoding132", "lemon"), "procqtrs132"),
    (("encoding132", "a"), "encoding132"),
    (("encoding132", "zz"), "dmbnchmf132"),
    (("encoding132", "AgentU"), "etgbwcnm132"),
    (("encoding132", "keyboard"), "orapriej132"),
    (("encoding132", "AA"), "encoding132"),
    (("mapping132", "key"), "wenzmlq132"),
    (("mapping132", "lemon"), "xebdvyk132"),
    (("mapping132", "a"), "mapping132"),
    (("mapping132", "zz"), "lzoohmf132"),
    (("mapping132", "AgentU"), "mgtcbhg132"),
    (("mapping132", "keyboard"), "wenqwnx132"),
    (("mapping132", "AA"), "mapping132"),
    (("record132", "key"), "biayvb132"),
    (("record132", "lemon"), "cioceo132"),
    (("record132", "a"), "record132"),
    (("record132", "zz"), "qdbnqc132"),
    (("record132", "AgentU"), "rkgbkx132"),
    (("record132", "keyboard"), "biapfd132"),
    (("record132", "AA"), "record132"),
    (("candle132", "key"), "melnpc132"),
    (("candle132", "lemon"), "nezryp132"),
    (("candle132", "a"), "candle132"),
    (("candle132", "zz"), "bzmckd132"),
    (("candle132", "AgentU"), "cgrqey132"),
    (("candle132", "keyboard"), "meleze132"),
    (("candle132", "AA"), "candle132"),
    (("thread132", "key"), "dlpoeb132"),
    (("thread132", "lemon"), "eldsno132"),
    (("thread132", "a"), "thread132"),
    (("thread132", "zz"), "sgqdzc132"),
    (("thread132", "AgentU"), "tnvrtx132"),
    (("thread132", "keyboard"), "dlpfod132"),
    (("thread132", "AA"), "thread132"),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 132: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 132: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "a"),
        "round 132: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 132: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 132: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 132: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", "AA"),
        "round 132: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "key"),
        "bssxh 132: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 132: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "a"),
        "round 132: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 132: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 132: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 132: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", "AA"),
        "round 132: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 132: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 132: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "a"),
        "round 132: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 132: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 132: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 132: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", "AA"),
        "round 132: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 132: the processor reads the record then stops", "key"),
        "bssxh 132: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 132: the processor reads the record then stops", "lemon"),
        "csgbq 132: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 132: the processor reads the record then stops", "a"),
        "round 132: the processor reads the record then stops",
    ),
    (
        ("round 132: the processor reads the record then stops", "zz"),
        "qntmc 132: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 132: the processor reads the record then stops", "AgentU"),
        "ruyaw 132: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 132: the processor reads the record then stops", "keyboard"),
        "bssor 132: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 132: the processor reads the record then stops", "AA"),
        "round 132: the processor reads the record then stops",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "key"),
        "bssxh 132: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "lemon"),
        "csgbq 132: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "a"),
        "round 132: a worker pulls the next task from the queue",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "zz"),
        "qntmc 132: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 132: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "keyboard"),
        "bssor 132: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 132: a worker pulls the next task from the queue", "AA"),
        "round 132: a worker pulls the next task from the queue",
    ),
    (
        ("round 132: signals travel through the network layer", "key"),
        "bssxh 132: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 132: signals travel through the network layer", "lemon"),
        "csgbq 132: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 132: signals travel through the network layer", "a"),
        "round 132: signals travel through the network layer",
    ),
    (
        ("round 132: signals travel through the network layer", "zz"),
        "qntmc 132: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 132: signals travel through the network layer", "AgentU"),
        "ruyaw 132: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 132: signals travel through the network layer", "keyboard"),
        "bssor 132: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 132: signals travel through the network layer", "AA"),
        "round 132: signals travel through the network layer",
    ),
    (
        ("round 132: the gateway routes each request by policy", "key"),
        "bssxh 132: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 132: the gateway routes each request by policy", "lemon"),
        "csgbq 132: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 132: the gateway routes each request by policy", "a"),
        "round 132: the gateway routes each request by policy",
    ),
    (
        ("round 132: the gateway routes each request by policy", "zz"),
        "qntmc 132: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 132: the gateway routes each request by policy", "AgentU"),
        "ruyaw 132: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 132: the gateway routes each request by policy", "keyboard"),
        "bssor 132: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 132: the gateway routes each request by policy", "AA"),
        "round 132: the gateway routes each request by policy",
    ),
    (("round 132: memory grows until the buffer is full", "key"), "bssxh 132: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 132: memory grows until the buffer is full", "lemon"), "csgbq 132: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 132: memory grows until the buffer is full", "a"), "round 132: memory grows until the buffer is full"),
    (("round 132: memory grows until the buffer is full", "zz"), "qntmc 132: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 132: memory grows until the buffer is full", "AgentU"),
        "ruyaw 132: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 132: memory grows until the buffer is full", "keyboard"),
        "bssor 132: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 132: memory grows until the buffer is full", "AA"), "round 132: memory grows until the buffer is full"),
    (("round 132: the cluster mirrors every packet twice", "key"), "bssxh 132: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 132: the cluster mirrors every packet twice", "lemon"),
        "csgbq 132: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 132: the cluster mirrors every packet twice", "a"), "round 132: the cluster mirrors every packet twice"),
    (("round 132: the cluster mirrors every packet twice", "zz"), "qntmc 132: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 132: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 132: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 132: the cluster mirrors every packet twice", "keyboard"),
        "bssor 132: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 132: the cluster mirrors every packet twice", "AA"), "round 132: the cluster mirrors every packet twice"),
    (
        ("round 132: ranking uses tokens learned from the corpus", "key"),
        "bssxh 132: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 132: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", "a"),
        "round 132: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 132: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 132: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 132: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", "AA"),
        "round 132: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 132: a long session ends when the candle dies", "key"),
        "bssxh 132: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 132: a long session ends when the candle dies", "lemon"),
        "csgbq 132: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 132: a long session ends when the candle dies", "a"),
        "round 132: a long session ends when the candle dies",
    ),
    (
        ("round 132: a long session ends when the candle dies", "zz"),
        "qntmc 132: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 132: a long session ends when the candle dies", "AgentU"),
        "ruyaw 132: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 132: a long session ends when the candle dies", "keyboard"),
        "bssor 132: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 132: a long session ends when the candle dies", "AA"),
        "round 132: a long session ends when the candle dies",
    ),
    (("round 132: encode the prompt then map the result", "key"), "bssxh 132: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 132: encode the prompt then map the result", "lemon"), "csgbq 132: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 132: encode the prompt then map the result", "a"), "round 132: encode the prompt then map the result"),
    (("round 132: encode the prompt then map the result", "zz"), "qntmc 132: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 132: encode the prompt then map the result", "AgentU"),
        "ruyaw 132: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 132: encode the prompt then map the result", "keyboard"),
        "bssor 132: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 132: encode the prompt then map the result", "AA"), "round 132: encode the prompt then map the result"),
    (("round 132: the kernel wakes the worker at dawn", "key"), "bssxh 132: rri iovlop ukocc xfo ambocb er neux"),
    (("round 132: the kernel wakes the worker at dawn", "lemon"), "csgbq 132: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 132: the kernel wakes the worker at dawn", "a"), "round 132: the kernel wakes the worker at dawn"),
    (("round 132: the kernel wakes the worker at dawn", "zz"), "qntmc 132: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 132: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 132: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 132: the kernel wakes the worker at dawn", "keyboard"), "bssor 132: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 132: the kernel wakes the worker at dawn", "AA"), "round 132: the kernel wakes the worker at dawn"),
    (("round 132: service latency drops after the patch", "key"), "bssxh 132: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 132: service latency drops after the patch", "lemon"), "csgbq 132: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 132: service latency drops after the patch", "a"), "round 132: service latency drops after the patch"),
    (("round 132: service latency drops after the patch", "zz"), "qntmc 132: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 132: service latency drops after the patch", "AgentU"),
        "ruyaw 132: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 132: service latency drops after the patch", "keyboard"),
        "bssor 132: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 132: service latency drops after the patch", "AA"), "round 132: service latency drops after the patch"),
    (
        ("round 132: the library caches every vector it sees", "key"),
        "bssxh 132: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 132: the library caches every vector it sees", "lemon"),
        "csgbq 132: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 132: the library caches every vector it sees", "a"), "round 132: the library caches every vector it sees"),
    (
        ("round 132: the library caches every vector it sees", "zz"),
        "qntmc 132: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 132: the library caches every vector it sees", "AgentU"),
        "ruyaw 132: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 132: the library caches every vector it sees", "keyboard"),
        "bssor 132: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 132: the library caches every vector it sees", "AA"),
        "round 132: the library caches every vector it sees",
    ),
    (("round 132: agents argue then the debate resolves", "key"), "bssxh 132: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 132: agents argue then the debate resolves", "lemon"), "csgbq 132: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 132: agents argue then the debate resolves", "a"), "round 132: agents argue then the debate resolves"),
    (("round 132: agents argue then the debate resolves", "zz"), "qntmc 132: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 132: agents argue then the debate resolves", "AgentU"),
        "ruyaw 132: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 132: agents argue then the debate resolves", "keyboard"),
        "bssor 132: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 132: agents argue then the debate resolves", "AA"), "round 132: agents argue then the debate resolves"),
    (("round 132: the filter keeps only strong matches", "key"), "bssxh 132: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 132: the filter keeps only strong matches", "lemon"), "csgbq 132: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 132: the filter keeps only strong matches", "a"), "round 132: the filter keeps only strong matches"),
    (("round 132: the filter keeps only strong matches", "zz"), "qntmc 132: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 132: the filter keeps only strong matches", "AgentU"), "ruyaw 132: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 132: the filter keeps only strong matches", "keyboard"),
        "bssor 132: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 132: the filter keeps only strong matches", "AA"), "round 132: the filter keeps only strong matches"),
    (("round 132: the model answers with a short reply", "key"), "bssxh 132: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 132: the model answers with a short reply", "lemon"), "csgbq 132: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 132: the model answers with a short reply", "a"), "round 132: the model answers with a short reply"),
    (("round 132: the model answers with a short reply", "zz"), "qntmc 132: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 132: the model answers with a short reply", "AgentU"), "ruyaw 132: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 132: the model answers with a short reply", "keyboard"),
        "bssor 132: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 132: the model answers with a short reply", "AA"), "round 132: the model answers with a short reply"),
    (
        ("round 132: the recorder stores the reasoning trace", "key"),
        "bssxh 132: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 132: the recorder stores the reasoning trace", "lemon"),
        "csgbq 132: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 132: the recorder stores the reasoning trace", "a"), "round 132: the recorder stores the reasoning trace"),
    (
        ("round 132: the recorder stores the reasoning trace", "zz"),
        "qntmc 132: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 132: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 132: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 132: the recorder stores the reasoning trace", "keyboard"),
        "bssor 132: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 132: the recorder stores the reasoning trace", "AA"),
        "round 132: the recorder stores the reasoning trace",
    ),
    (("round 132: the angel watches the processor run", "key"), "bssxh 132: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 132: the angel watches the processor run", "lemon"), "csgbq 132: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 132: the angel watches the processor run", "a"), "round 132: the angel watches the processor run"),
    (("round 132: the angel watches the processor run", "zz"), "qntmc 132: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 132: the angel watches the processor run", "AgentU"), "ruyaw 132: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 132: the angel watches the processor run", "keyboard"), "bssor 132: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 132: the angel watches the processor run", "AA"), "round 132: the angel watches the processor run"),
    (("round 132: angle of the vector decides the match", "key"), "bssxh 132: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 132: angle of the vector decides the match", "lemon"), "csgbq 132: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 132: angle of the vector decides the match", "a"), "round 132: angle of the vector decides the match"),
    (("round 132: angle of the vector decides the match", "zz"), "qntmc 132: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 132: angle of the vector decides the match", "AgentU"),
        "ruyaw 132: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 132: angle of the vector decides the match", "keyboard"),
        "bssor 132: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 132: angle of the vector decides the match", "AA"), "round 132: angle of the vector decides the match"),
    (
        ("round 132: the candle burns twice as long at night", "key"),
        "bssxh 132: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 132: the candle burns twice as long at night", "lemon"),
        "csgbq 132: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 132: the candle burns twice as long at night", "a"), "round 132: the candle burns twice as long at night"),
    (
        ("round 132: the candle burns twice as long at night", "zz"),
        "qntmc 132: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 132: the candle burns twice as long at night", "AgentU"),
        "ruyaw 132: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 132: the candle burns twice as long at night", "keyboard"),
        "bssor 132: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 132: the candle burns twice as long at night", "AA"),
        "round 132: the candle burns twice as long at night",
    ),
    (("round 132: a mirror of the universe in one line", "key"), "bssxh 132: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 132: a mirror of the universe in one line", "lemon"), "csgbq 132: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 132: a mirror of the universe in one line", "a"), "round 132: a mirror of the universe in one line"),
    (("round 132: a mirror of the universe in one line", "zz"), "qntmc 132: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 132: a mirror of the universe in one line", "AgentU"), "ruyaw 132: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 132: a mirror of the universe in one line", "keyboard"),
        "bssor 132: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 132: a mirror of the universe in one line", "AA"), "round 132: a mirror of the universe in one line"),
    (("round 132: the queue drains before the storm", "key"), "bssxh 132: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 132: the queue drains before the storm", "lemon"), "csgbq 132: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 132: the queue drains before the storm", "a"), "round 132: the queue drains before the storm"),
    (("round 132: the queue drains before the storm", "zz"), "qntmc 132: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 132: the queue drains before the storm", "AgentU"), "ruyaw 132: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 132: the queue drains before the storm", "keyboard"), "bssor 132: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 132: the queue drains before the storm", "AA"), "round 132: the queue drains before the storm"),
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
