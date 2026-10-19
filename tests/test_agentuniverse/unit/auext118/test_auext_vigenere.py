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
    (("kitten118", "key"), "umrdil118"),
    (("kitten118", "lemon"), "vmfhry118"),
    (("kitten118", "a"), "kitten118"),
    (("kitten118", "zz"), "jhssdm118"),
    (("kitten118", "AgentU"), "koxgxh118"),
    (("kitten118", "keyboard"), "umrusn118"),
    (("kitten118", "AA"), "kitten118"),
    (("sitting118", "key"), "cmrdmlq118"),
    (("sitting118", "lemon"), "dmfhvyk118"),
    (("sitting118", "a"), "sitting118"),
    (("sitting118", "zz"), "rhsshmf118"),
    (("sitting118", "AgentU"), "soxgbhg118"),
    (("sitting118", "keyboard"), "cmruwnx118"),
    (("sitting118", "AA"), "sitting118"),
    (("agent118", "key"), "kkcxx118"),
    (("agent118", "lemon"), "lkqbg118"),
    (("agent118", "a"), "agent118"),
    (("agent118", "zz"), "zfdms118"),
    (("agent118", "AgentU"), "amiam118"),
    (("agent118", "keyboard"), "kkcoh118"),
    (("agent118", "AA"), "agent118"),
    (("angle118", "key"), "krevi118"),
    (("angle118", "lemon"), "lrszr118"),
    (("angle118", "a"), "angle118"),
    (("angle118", "zz"), "zmfkd118"),
    (("angle118", "AgentU"), "atkyx118"),
    (("angle118", "keyboard"), "krems118"),
    (("angle118", "AA"), "angle118"),
    (("universe118", "key"), "ergfipci118"),
    (("universe118", "lemon"), "frujrcwq118"),
    (("universe118", "a"), "universe118"),
    (("universe118", "zz"), "tmhudqrd118"),
    (("universe118", "AgentU"), "utmixlsk118"),
    (("universe118", "keyboard"), "ergwsrjh118"),
    (("universe118", "AA"), "universe118"),
    (("memory118", "key"), "wikyvw118"),
    (("memory118", "lemon"), "xiycej118"),
    (("memory118", "a"), "memory118"),
    (("memory118", "zz"), "ldlnqx118"),
    (("memory118", "AgentU"), "mkqbks118"),
    (("memory118", "keyboard"), "wikpfy118"),
    (("memory118", "AA"), "memory118"),
    (("stream118", "key"), "cxpoek118"),
    (("stream118", "lemon"), "dxdsnx118"),
    (("stream118", "a"), "stream118"),
    (("stream118", "zz"), "rsqdzl118"),
    (("stream118", "AgentU"), "szvrtg118"),
    (("stream118", "keyboard"), "cxpfom118"),
    (("stream118", "AA"), "stream118"),
    (("context118", "key"), "msldivd118"),
    (("context118", "lemon"), "nszhrix118"),
    (("context118", "a"), "context118"),
    (("context118", "zz"), "bnmsdws118"),
    (("context118", "AgentU"), "curgxrt118"),
    (("context118", "keyboard"), "mslusxk118"),
    (("context118", "AA"), "context118"),
    (("knowledge118", "key"), "urmgpcnkc118"),
    (("knowledge118", "lemon"), "vrakyphss118"),
    (("knowledge118", "a"), "knowledge118"),
    (("knowledge118", "zz"), "jmnvkdcfd118"),
    (("knowledge118", "AgentU"), "ktsjeydmi118"),
    (("knowledge118", "keyboard"), "urmxzeujo118"),
    (("knowledge118", "AA"), "knowledge118"),
    (("vector118", "key"), "fiadsp118"),
    (("vector118", "lemon"), "giohbc118"),
    (("vector118", "a"), "vector118"),
    (("vector118", "zz"), "udbsnq118"),
    (("vector118", "AgentU"), "vkgghl118"),
    (("vector118", "keyboard"), "fiaucr118"),
    (("vector118", "AA"), "vector118"),
    (("processor118", "key"), "zvmmiqcsp118"),
    (("processor118", "lemon"), "avaqrdwaf118"),
    (("processor118", "a"), "processor118"),
    (("processor118", "zz"), "oqnbdrrnq118"),
    (("processor118", "AgentU"), "pxspxmsuv118"),
    (("processor118", "keyboard"), "zvmdssjrb118"),
    (("processor118", "AA"), "processor118"),
    (("reasoning118", "key"), "biycslsre118"),
    (("reasoning118", "lemon"), "cimgbymzu118"),
    (("reasoning118", "a"), "reasoning118"),
    (("reasoning118", "zz"), "qdzrnmhmf118"),
    (("reasoning118", "AgentU"), "rkefhhitk118"),
    (("reasoning118", "keyboard"), "biytcnzqq118"),
    (("reasoning118", "AA"), "reasoning118"),
    (("machine118", "key"), "wearmlo118"),
    (("machine118", "lemon"), "xeovvyi118"),
    (("machine118", "a"), "machine118"),
    (("machine118", "zz"), "lzbghmd118"),
    (("machine118", "AgentU"), "mggubhe118"),
    (("machine118", "keyboard"), "weaiwnv118"),
    (("machine118", "AA"), "machine118"),
    (("learning118", "key"), "viybrgxk118"),
    (("learning118", "lemon"), "wimfatrs118"),
    (("learning118", "a"), "learning118"),
    (("learning118", "zz"), "kdzqmhmf118"),
    (("learning118", "AgentU"), "lkeegcnm118"),
    (("learning118", "keyboard"), "viysbiej118"),
    (("learning118", "AA"), "learning118"),
    (("model118", "key"), "wsbop118"),
    (("model118", "lemon"), "xspsy118"),
    (("model118", "a"), "model118"),
    (("model118", "zz"), "lncdk118"),
    (("model118", "AgentU"), "muhre118"),
    (("model118", "keyboard"), "wsbfz118"),
    (("model118", "AA"), "model118"),
    (("token118", "key"), "dsior118"),
    (("token118", "lemon"), "eswsa118"),
    (("token118", "a"), "token118"),
    (("token118", "zz"), "snjdm118"),
    (("token118", "AgentU"), "tuorg118"),
    (("token118", "keyboard"), "dsifb118"),
    (("token118", "AA"), "token118"),
    (("prompt118", "key"), "zvmwtr118"),
    (("prompt118", "lemon"), "avaace118"),
    (("prompt118", "a"), "prompt118"),
    (("prompt118", "zz"), "oqnlos118"),
    (("prompt118", "AgentU"), "pxszin118"),
    (("prompt118", "keyboard"), "zvmndt118"),
    (("prompt118", "AA"), "prompt118"),
    (("session118", "key"), "ciqcmmx118"),
    (("session118", "lemon"), "diegvzr118"),
    (("session118", "a"), "session118"),
    (("session118", "zz"), "rdrrhnm118"),
    (("session118", "AgentU"), "skwfbin118"),
    (("session118", "keyboard"), "ciqtwoe118"),
    (("session118", "AA"), "session118"),
    (("library118", "key"), "vmzbepi118"),
    (("library118", "lemon"), "wmnfncc118"),
    (("library118", "a"), "library118"),
    (("library118", "zz"), "khaqzqx118"),
    (("library118", "AgentU"), "lofetly118"),
    (("library118", "keyboard"), "vmzsorp118"),
    (("library118", "AA"), "library118"),
    (("service118", "key"), "cipfmao118"),
    (("service118", "lemon"), "didjvni118"),
    (("service118", "a"), "service118"),
    (("service118", "zz"), "rdquhbd118"),
    (("service118", "AgentU"), "skvibwe118"),
    (("service118", "keyboard"), "cipwwcv118"),
    (("service118", "AA"), "service118"),
    (("gateway118", "key"), "qeroayi118"),
    (("gateway118", "lemon"), "refsjlc118"),
    (("gateway118", "a"), "gateway118"),
    (("gateway118", "zz"), "fzsdvzx118"),
    (("gateway118", "AgentU"), "ggxrpuy118"),
    (("gateway118", "keyboard"), "qerfkap118"),
    (("gateway118", "AA"), "gateway118"),
    (("storage118", "key"), "cxmbeeo118"),
    (("storage118", "lemon"), "dxafnri118"),
    (("storage118", "a"), "storage118"),
    (("storage118", "zz"), "rsnqzfd118"),
    (("storage118", "AgentU"), "szsetae118"),
    (("storage118", "keyboard"), "cxmsogv118"),
    (("storage118", "AA"), "storage118"),
    (("network118", "key"), "xirgspu118"),
    (("network118", "lemon"), "yifkbco118"),
    (("network118", "a"), "network118"),
    (("network118", "zz"), "mdsvnqj118"),
    (("network118", "AgentU"), "nkxjhlk118"),
    (("network118", "keyboard"), "xirxcrb118"),
    (("network118", "AA"), "network118"),
    (("latency118", "key"), "verorai118"),
    (("latency118", "lemon"), "wefsanc118"),
    (("latency118", "a"), "latency118"),
    (("latency118", "zz"), "kzsdmbx118"),
    (("latency118", "AgentU"), "lgxrgwy118"),
    (("latency118", "keyboard"), "verfbcp118"),
    (("latency118", "AA"), "latency118"),
    (("buffer118", "key"), "lydpip118"),
    (("buffer118", "lemon"), "myrtrc118"),
    (("buffer118", "a"), "buffer118"),
    (("buffer118", "zz"), "ateedq118"),
    (("buffer118", "AgentU"), "bajsxl118"),
    (("buffer118", "keyboard"), "lydgsr118"),
    (("buffer118", "AA"), "buffer118"),
    (("queue118", "key"), "aycei118"),
    (("queue118", "lemon"), "byqir118"),
    (("queue118", "a"), "queue118"),
    (("queue118", "zz"), "ptdtd118"),
    (("queue118", "AgentU"), "qaihx118"),
    (("queue118", "keyboard"), "aycvs118"),
    (("queue118", "AA"), "queue118"),
    (("worker118", "key"), "gspuip118"),
    (("worker118", "lemon"), "hsdyrc118"),
    (("worker118", "a"), "worker118"),
    (("worker118", "zz"), "vnqjdq118"),
    (("worker118", "AgentU"), "wuvxxl118"),
    (("worker118", "keyboard"), "gsplsr118"),
    (("worker118", "AA"), "worker118"),
    (("kernel118", "key"), "uipxij118"),
    (("kernel118", "lemon"), "vidbrw118"),
    (("kernel118", "a"), "kernel118"),
    (("kernel118", "zz"), "jdqmdk118"),
    (("kernel118", "AgentU"), "kkvaxf118"),
    (("kernel118", "keyboard"), "uiposl118"),
    (("kernel118", "AA"), "kernel118"),
    (("signal118", "key"), "cmexej118"),
    (("signal118", "lemon"), "dmsbnw118"),
    (("signal118", "a"), "signal118"),
    (("signal118", "zz"), "rhfmzk118"),
    (("signal118", "AgentU"), "sokatf118"),
    (("signal118", "keyboard"), "cmeool118"),
    (("signal118", "AA"), "signal118"),
    (("packet118", "key"), "zeauir118"),
    (("packet118", "lemon"), "aeoyre118"),
    (("packet118", "a"), "packet118"),
    (("packet118", "zz"), "ozbjds118"),
    (("packet118", "AgentU"), "pggxxn118"),
    (("packet118", "keyboard"), "zealst118"),
    (("packet118", "AA"), "packet118"),
    (("router118", "key"), "bssdip118"),
    (("router118", "lemon"), "csghrc118"),
    (("router118", "a"), "router118"),
    (("router118", "zz"), "qntsdq118"),
    (("router118", "AgentU"), "ruygxl118"),
    (("router118", "keyboard"), "bssusr118"),
    (("router118", "AA"), "router118"),
    (("cluster118", "key"), "mpscxcb118"),
    (("cluster118", "lemon"), "npgggpv118"),
    (("cluster118", "a"), "cluster118"),
    (("cluster118", "zz"), "bktrsdq118"),
    (("cluster118", "AgentU"), "cryfmyr118"),
    (("cluster118", "keyboard"), "mpsthei118"),
    (("cluster118", "AA"), "cluster118"),
    (("mirror118", "key"), "wmpbsp118"),
    (("mirror118", "lemon"), "xmdfbc118"),
    (("mirror118", "a"), "mirror118"),
    (("mirror118", "zz"), "lhqqnq118"),
    (("mirror118", "AgentU"), "movehl118"),
    (("mirror118", "keyboard"), "wmpscr118"),
    (("mirror118", "AA"), "mirror118"),
    (("filter118", "key"), "pmjdip118"),
    (("filter118", "lemon"), "qmxhrc118"),
    (("filter118", "a"), "filter118"),
    (("filter118", "zz"), "ehksdq118"),
    (("filter118", "AgentU"), "fopgxl118"),
    (("filter118", "keyboard"), "pmjusr118"),
    (("filter118", "AA"), "filter118"),
    (("ranking118", "key"), "belumlq118"),
    (("ranking118", "lemon"), "cezyvyk118"),
    (("ranking118", "a"), "ranking118"),
    (("ranking118", "zz"), "qzmjhmf118"),
    (("ranking118", "AgentU"), "rgrxbhg118"),
    (("ranking118", "keyboard"), "bellwnx118"),
    (("ranking118", "AA"), "ranking118"),
    (("encoding118", "key"), "orayhgxk118"),
    (("encoding118", "lemon"), "procqtrs118"),
    (("encoding118", "a"), "encoding118"),
    (("encoding118", "zz"), "dmbnchmf118"),
    (("encoding118", "AgentU"), "etgbwcnm118"),
    (("encoding118", "keyboard"), "orapriej118"),
    (("encoding118", "AA"), "encoding118"),
    (("mapping118", "key"), "wenzmlq118"),
    (("mapping118", "lemon"), "xebdvyk118"),
    (("mapping118", "a"), "mapping118"),
    (("mapping118", "zz"), "lzoohmf118"),
    (("mapping118", "AgentU"), "mgtcbhg118"),
    (("mapping118", "keyboard"), "wenqwnx118"),
    (("mapping118", "AA"), "mapping118"),
    (("record118", "key"), "biayvb118"),
    (("record118", "lemon"), "cioceo118"),
    (("record118", "a"), "record118"),
    (("record118", "zz"), "qdbnqc118"),
    (("record118", "AgentU"), "rkgbkx118"),
    (("record118", "keyboard"), "biapfd118"),
    (("record118", "AA"), "record118"),
    (("candle118", "key"), "melnpc118"),
    (("candle118", "lemon"), "nezryp118"),
    (("candle118", "a"), "candle118"),
    (("candle118", "zz"), "bzmckd118"),
    (("candle118", "AgentU"), "cgrqey118"),
    (("candle118", "keyboard"), "meleze118"),
    (("candle118", "AA"), "candle118"),
    (("thread118", "key"), "dlpoeb118"),
    (("thread118", "lemon"), "eldsno118"),
    (("thread118", "a"), "thread118"),
    (("thread118", "zz"), "sgqdzc118"),
    (("thread118", "AgentU"), "tnvrtx118"),
    (("thread118", "keyboard"), "dlpfod118"),
    (("thread118", "AA"), "thread118"),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 118: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 118: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "a"),
        "round 118: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 118: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 118: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 118: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", "AA"),
        "round 118: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "key"),
        "bssxh 118: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 118: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "a"),
        "round 118: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 118: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 118: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 118: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", "AA"),
        "round 118: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 118: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 118: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "a"),
        "round 118: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 118: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 118: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 118: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", "AA"),
        "round 118: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 118: the processor reads the record then stops", "key"),
        "bssxh 118: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 118: the processor reads the record then stops", "lemon"),
        "csgbq 118: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 118: the processor reads the record then stops", "a"),
        "round 118: the processor reads the record then stops",
    ),
    (
        ("round 118: the processor reads the record then stops", "zz"),
        "qntmc 118: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 118: the processor reads the record then stops", "AgentU"),
        "ruyaw 118: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 118: the processor reads the record then stops", "keyboard"),
        "bssor 118: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 118: the processor reads the record then stops", "AA"),
        "round 118: the processor reads the record then stops",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "key"),
        "bssxh 118: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "lemon"),
        "csgbq 118: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "a"),
        "round 118: a worker pulls the next task from the queue",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "zz"),
        "qntmc 118: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 118: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "keyboard"),
        "bssor 118: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 118: a worker pulls the next task from the queue", "AA"),
        "round 118: a worker pulls the next task from the queue",
    ),
    (
        ("round 118: signals travel through the network layer", "key"),
        "bssxh 118: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 118: signals travel through the network layer", "lemon"),
        "csgbq 118: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 118: signals travel through the network layer", "a"),
        "round 118: signals travel through the network layer",
    ),
    (
        ("round 118: signals travel through the network layer", "zz"),
        "qntmc 118: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 118: signals travel through the network layer", "AgentU"),
        "ruyaw 118: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 118: signals travel through the network layer", "keyboard"),
        "bssor 118: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 118: signals travel through the network layer", "AA"),
        "round 118: signals travel through the network layer",
    ),
    (
        ("round 118: the gateway routes each request by policy", "key"),
        "bssxh 118: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 118: the gateway routes each request by policy", "lemon"),
        "csgbq 118: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 118: the gateway routes each request by policy", "a"),
        "round 118: the gateway routes each request by policy",
    ),
    (
        ("round 118: the gateway routes each request by policy", "zz"),
        "qntmc 118: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 118: the gateway routes each request by policy", "AgentU"),
        "ruyaw 118: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 118: the gateway routes each request by policy", "keyboard"),
        "bssor 118: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 118: the gateway routes each request by policy", "AA"),
        "round 118: the gateway routes each request by policy",
    ),
    (("round 118: memory grows until the buffer is full", "key"), "bssxh 118: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 118: memory grows until the buffer is full", "lemon"), "csgbq 118: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 118: memory grows until the buffer is full", "a"), "round 118: memory grows until the buffer is full"),
    (("round 118: memory grows until the buffer is full", "zz"), "qntmc 118: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 118: memory grows until the buffer is full", "AgentU"),
        "ruyaw 118: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 118: memory grows until the buffer is full", "keyboard"),
        "bssor 118: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 118: memory grows until the buffer is full", "AA"), "round 118: memory grows until the buffer is full"),
    (("round 118: the cluster mirrors every packet twice", "key"), "bssxh 118: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 118: the cluster mirrors every packet twice", "lemon"),
        "csgbq 118: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 118: the cluster mirrors every packet twice", "a"), "round 118: the cluster mirrors every packet twice"),
    (("round 118: the cluster mirrors every packet twice", "zz"), "qntmc 118: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 118: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 118: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 118: the cluster mirrors every packet twice", "keyboard"),
        "bssor 118: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 118: the cluster mirrors every packet twice", "AA"), "round 118: the cluster mirrors every packet twice"),
    (
        ("round 118: ranking uses tokens learned from the corpus", "key"),
        "bssxh 118: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 118: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", "a"),
        "round 118: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 118: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 118: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 118: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", "AA"),
        "round 118: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 118: a long session ends when the candle dies", "key"),
        "bssxh 118: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 118: a long session ends when the candle dies", "lemon"),
        "csgbq 118: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 118: a long session ends when the candle dies", "a"),
        "round 118: a long session ends when the candle dies",
    ),
    (
        ("round 118: a long session ends when the candle dies", "zz"),
        "qntmc 118: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 118: a long session ends when the candle dies", "AgentU"),
        "ruyaw 118: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 118: a long session ends when the candle dies", "keyboard"),
        "bssor 118: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 118: a long session ends when the candle dies", "AA"),
        "round 118: a long session ends when the candle dies",
    ),
    (("round 118: encode the prompt then map the result", "key"), "bssxh 118: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 118: encode the prompt then map the result", "lemon"), "csgbq 118: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 118: encode the prompt then map the result", "a"), "round 118: encode the prompt then map the result"),
    (("round 118: encode the prompt then map the result", "zz"), "qntmc 118: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 118: encode the prompt then map the result", "AgentU"),
        "ruyaw 118: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 118: encode the prompt then map the result", "keyboard"),
        "bssor 118: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 118: encode the prompt then map the result", "AA"), "round 118: encode the prompt then map the result"),
    (("round 118: the kernel wakes the worker at dawn", "key"), "bssxh 118: rri iovlop ukocc xfo ambocb er neux"),
    (("round 118: the kernel wakes the worker at dawn", "lemon"), "csgbq 118: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 118: the kernel wakes the worker at dawn", "a"), "round 118: the kernel wakes the worker at dawn"),
    (("round 118: the kernel wakes the worker at dawn", "zz"), "qntmc 118: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 118: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 118: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 118: the kernel wakes the worker at dawn", "keyboard"), "bssor 118: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 118: the kernel wakes the worker at dawn", "AA"), "round 118: the kernel wakes the worker at dawn"),
    (("round 118: service latency drops after the patch", "key"), "bssxh 118: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 118: service latency drops after the patch", "lemon"), "csgbq 118: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 118: service latency drops after the patch", "a"), "round 118: service latency drops after the patch"),
    (("round 118: service latency drops after the patch", "zz"), "qntmc 118: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 118: service latency drops after the patch", "AgentU"),
        "ruyaw 118: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 118: service latency drops after the patch", "keyboard"),
        "bssor 118: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 118: service latency drops after the patch", "AA"), "round 118: service latency drops after the patch"),
    (
        ("round 118: the library caches every vector it sees", "key"),
        "bssxh 118: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 118: the library caches every vector it sees", "lemon"),
        "csgbq 118: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 118: the library caches every vector it sees", "a"), "round 118: the library caches every vector it sees"),
    (
        ("round 118: the library caches every vector it sees", "zz"),
        "qntmc 118: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 118: the library caches every vector it sees", "AgentU"),
        "ruyaw 118: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 118: the library caches every vector it sees", "keyboard"),
        "bssor 118: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 118: the library caches every vector it sees", "AA"),
        "round 118: the library caches every vector it sees",
    ),
    (("round 118: agents argue then the debate resolves", "key"), "bssxh 118: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 118: agents argue then the debate resolves", "lemon"), "csgbq 118: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 118: agents argue then the debate resolves", "a"), "round 118: agents argue then the debate resolves"),
    (("round 118: agents argue then the debate resolves", "zz"), "qntmc 118: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 118: agents argue then the debate resolves", "AgentU"),
        "ruyaw 118: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 118: agents argue then the debate resolves", "keyboard"),
        "bssor 118: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 118: agents argue then the debate resolves", "AA"), "round 118: agents argue then the debate resolves"),
    (("round 118: the filter keeps only strong matches", "key"), "bssxh 118: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 118: the filter keeps only strong matches", "lemon"), "csgbq 118: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 118: the filter keeps only strong matches", "a"), "round 118: the filter keeps only strong matches"),
    (("round 118: the filter keeps only strong matches", "zz"), "qntmc 118: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 118: the filter keeps only strong matches", "AgentU"), "ruyaw 118: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 118: the filter keeps only strong matches", "keyboard"),
        "bssor 118: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 118: the filter keeps only strong matches", "AA"), "round 118: the filter keeps only strong matches"),
    (("round 118: the model answers with a short reply", "key"), "bssxh 118: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 118: the model answers with a short reply", "lemon"), "csgbq 118: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 118: the model answers with a short reply", "a"), "round 118: the model answers with a short reply"),
    (("round 118: the model answers with a short reply", "zz"), "qntmc 118: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 118: the model answers with a short reply", "AgentU"), "ruyaw 118: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 118: the model answers with a short reply", "keyboard"),
        "bssor 118: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 118: the model answers with a short reply", "AA"), "round 118: the model answers with a short reply"),
    (
        ("round 118: the recorder stores the reasoning trace", "key"),
        "bssxh 118: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 118: the recorder stores the reasoning trace", "lemon"),
        "csgbq 118: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 118: the recorder stores the reasoning trace", "a"), "round 118: the recorder stores the reasoning trace"),
    (
        ("round 118: the recorder stores the reasoning trace", "zz"),
        "qntmc 118: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 118: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 118: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 118: the recorder stores the reasoning trace", "keyboard"),
        "bssor 118: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 118: the recorder stores the reasoning trace", "AA"),
        "round 118: the recorder stores the reasoning trace",
    ),
    (("round 118: the angel watches the processor run", "key"), "bssxh 118: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 118: the angel watches the processor run", "lemon"), "csgbq 118: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 118: the angel watches the processor run", "a"), "round 118: the angel watches the processor run"),
    (("round 118: the angel watches the processor run", "zz"), "qntmc 118: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 118: the angel watches the processor run", "AgentU"), "ruyaw 118: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 118: the angel watches the processor run", "keyboard"), "bssor 118: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 118: the angel watches the processor run", "AA"), "round 118: the angel watches the processor run"),
    (("round 118: angle of the vector decides the match", "key"), "bssxh 118: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 118: angle of the vector decides the match", "lemon"), "csgbq 118: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 118: angle of the vector decides the match", "a"), "round 118: angle of the vector decides the match"),
    (("round 118: angle of the vector decides the match", "zz"), "qntmc 118: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 118: angle of the vector decides the match", "AgentU"),
        "ruyaw 118: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 118: angle of the vector decides the match", "keyboard"),
        "bssor 118: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 118: angle of the vector decides the match", "AA"), "round 118: angle of the vector decides the match"),
    (
        ("round 118: the candle burns twice as long at night", "key"),
        "bssxh 118: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 118: the candle burns twice as long at night", "lemon"),
        "csgbq 118: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 118: the candle burns twice as long at night", "a"), "round 118: the candle burns twice as long at night"),
    (
        ("round 118: the candle burns twice as long at night", "zz"),
        "qntmc 118: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 118: the candle burns twice as long at night", "AgentU"),
        "ruyaw 118: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 118: the candle burns twice as long at night", "keyboard"),
        "bssor 118: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 118: the candle burns twice as long at night", "AA"),
        "round 118: the candle burns twice as long at night",
    ),
    (("round 118: a mirror of the universe in one line", "key"), "bssxh 118: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 118: a mirror of the universe in one line", "lemon"), "csgbq 118: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 118: a mirror of the universe in one line", "a"), "round 118: a mirror of the universe in one line"),
    (("round 118: a mirror of the universe in one line", "zz"), "qntmc 118: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 118: a mirror of the universe in one line", "AgentU"), "ruyaw 118: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 118: a mirror of the universe in one line", "keyboard"),
        "bssor 118: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 118: a mirror of the universe in one line", "AA"), "round 118: a mirror of the universe in one line"),
    (("round 118: the queue drains before the storm", "key"), "bssxh 118: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 118: the queue drains before the storm", "lemon"), "csgbq 118: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 118: the queue drains before the storm", "a"), "round 118: the queue drains before the storm"),
    (("round 118: the queue drains before the storm", "zz"), "qntmc 118: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 118: the queue drains before the storm", "AgentU"), "ruyaw 118: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 118: the queue drains before the storm", "keyboard"), "bssor 118: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 118: the queue drains before the storm", "AA"), "round 118: the queue drains before the storm"),
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
