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
    (("kitten738", "key"), "umrdil738"),
    (("kitten738", "lemon"), "vmfhry738"),
    (("kitten738", "a"), "kitten738"),
    (("kitten738", "zz"), "jhssdm738"),
    (("kitten738", "AgentU"), "koxgxh738"),
    (("kitten738", "keyboard"), "umrusn738"),
    (("kitten738", "AA"), "kitten738"),
    (("sitting738", "key"), "cmrdmlq738"),
    (("sitting738", "lemon"), "dmfhvyk738"),
    (("sitting738", "a"), "sitting738"),
    (("sitting738", "zz"), "rhsshmf738"),
    (("sitting738", "AgentU"), "soxgbhg738"),
    (("sitting738", "keyboard"), "cmruwnx738"),
    (("sitting738", "AA"), "sitting738"),
    (("agent738", "key"), "kkcxx738"),
    (("agent738", "lemon"), "lkqbg738"),
    (("agent738", "a"), "agent738"),
    (("agent738", "zz"), "zfdms738"),
    (("agent738", "AgentU"), "amiam738"),
    (("agent738", "keyboard"), "kkcoh738"),
    (("agent738", "AA"), "agent738"),
    (("angle738", "key"), "krevi738"),
    (("angle738", "lemon"), "lrszr738"),
    (("angle738", "a"), "angle738"),
    (("angle738", "zz"), "zmfkd738"),
    (("angle738", "AgentU"), "atkyx738"),
    (("angle738", "keyboard"), "krems738"),
    (("angle738", "AA"), "angle738"),
    (("universe738", "key"), "ergfipci738"),
    (("universe738", "lemon"), "frujrcwq738"),
    (("universe738", "a"), "universe738"),
    (("universe738", "zz"), "tmhudqrd738"),
    (("universe738", "AgentU"), "utmixlsk738"),
    (("universe738", "keyboard"), "ergwsrjh738"),
    (("universe738", "AA"), "universe738"),
    (("memory738", "key"), "wikyvw738"),
    (("memory738", "lemon"), "xiycej738"),
    (("memory738", "a"), "memory738"),
    (("memory738", "zz"), "ldlnqx738"),
    (("memory738", "AgentU"), "mkqbks738"),
    (("memory738", "keyboard"), "wikpfy738"),
    (("memory738", "AA"), "memory738"),
    (("stream738", "key"), "cxpoek738"),
    (("stream738", "lemon"), "dxdsnx738"),
    (("stream738", "a"), "stream738"),
    (("stream738", "zz"), "rsqdzl738"),
    (("stream738", "AgentU"), "szvrtg738"),
    (("stream738", "keyboard"), "cxpfom738"),
    (("stream738", "AA"), "stream738"),
    (("context738", "key"), "msldivd738"),
    (("context738", "lemon"), "nszhrix738"),
    (("context738", "a"), "context738"),
    (("context738", "zz"), "bnmsdws738"),
    (("context738", "AgentU"), "curgxrt738"),
    (("context738", "keyboard"), "mslusxk738"),
    (("context738", "AA"), "context738"),
    (("knowledge738", "key"), "urmgpcnkc738"),
    (("knowledge738", "lemon"), "vrakyphss738"),
    (("knowledge738", "a"), "knowledge738"),
    (("knowledge738", "zz"), "jmnvkdcfd738"),
    (("knowledge738", "AgentU"), "ktsjeydmi738"),
    (("knowledge738", "keyboard"), "urmxzeujo738"),
    (("knowledge738", "AA"), "knowledge738"),
    (("vector738", "key"), "fiadsp738"),
    (("vector738", "lemon"), "giohbc738"),
    (("vector738", "a"), "vector738"),
    (("vector738", "zz"), "udbsnq738"),
    (("vector738", "AgentU"), "vkgghl738"),
    (("vector738", "keyboard"), "fiaucr738"),
    (("vector738", "AA"), "vector738"),
    (("processor738", "key"), "zvmmiqcsp738"),
    (("processor738", "lemon"), "avaqrdwaf738"),
    (("processor738", "a"), "processor738"),
    (("processor738", "zz"), "oqnbdrrnq738"),
    (("processor738", "AgentU"), "pxspxmsuv738"),
    (("processor738", "keyboard"), "zvmdssjrb738"),
    (("processor738", "AA"), "processor738"),
    (("reasoning738", "key"), "biycslsre738"),
    (("reasoning738", "lemon"), "cimgbymzu738"),
    (("reasoning738", "a"), "reasoning738"),
    (("reasoning738", "zz"), "qdzrnmhmf738"),
    (("reasoning738", "AgentU"), "rkefhhitk738"),
    (("reasoning738", "keyboard"), "biytcnzqq738"),
    (("reasoning738", "AA"), "reasoning738"),
    (("machine738", "key"), "wearmlo738"),
    (("machine738", "lemon"), "xeovvyi738"),
    (("machine738", "a"), "machine738"),
    (("machine738", "zz"), "lzbghmd738"),
    (("machine738", "AgentU"), "mggubhe738"),
    (("machine738", "keyboard"), "weaiwnv738"),
    (("machine738", "AA"), "machine738"),
    (("learning738", "key"), "viybrgxk738"),
    (("learning738", "lemon"), "wimfatrs738"),
    (("learning738", "a"), "learning738"),
    (("learning738", "zz"), "kdzqmhmf738"),
    (("learning738", "AgentU"), "lkeegcnm738"),
    (("learning738", "keyboard"), "viysbiej738"),
    (("learning738", "AA"), "learning738"),
    (("model738", "key"), "wsbop738"),
    (("model738", "lemon"), "xspsy738"),
    (("model738", "a"), "model738"),
    (("model738", "zz"), "lncdk738"),
    (("model738", "AgentU"), "muhre738"),
    (("model738", "keyboard"), "wsbfz738"),
    (("model738", "AA"), "model738"),
    (("token738", "key"), "dsior738"),
    (("token738", "lemon"), "eswsa738"),
    (("token738", "a"), "token738"),
    (("token738", "zz"), "snjdm738"),
    (("token738", "AgentU"), "tuorg738"),
    (("token738", "keyboard"), "dsifb738"),
    (("token738", "AA"), "token738"),
    (("prompt738", "key"), "zvmwtr738"),
    (("prompt738", "lemon"), "avaace738"),
    (("prompt738", "a"), "prompt738"),
    (("prompt738", "zz"), "oqnlos738"),
    (("prompt738", "AgentU"), "pxszin738"),
    (("prompt738", "keyboard"), "zvmndt738"),
    (("prompt738", "AA"), "prompt738"),
    (("session738", "key"), "ciqcmmx738"),
    (("session738", "lemon"), "diegvzr738"),
    (("session738", "a"), "session738"),
    (("session738", "zz"), "rdrrhnm738"),
    (("session738", "AgentU"), "skwfbin738"),
    (("session738", "keyboard"), "ciqtwoe738"),
    (("session738", "AA"), "session738"),
    (("library738", "key"), "vmzbepi738"),
    (("library738", "lemon"), "wmnfncc738"),
    (("library738", "a"), "library738"),
    (("library738", "zz"), "khaqzqx738"),
    (("library738", "AgentU"), "lofetly738"),
    (("library738", "keyboard"), "vmzsorp738"),
    (("library738", "AA"), "library738"),
    (("service738", "key"), "cipfmao738"),
    (("service738", "lemon"), "didjvni738"),
    (("service738", "a"), "service738"),
    (("service738", "zz"), "rdquhbd738"),
    (("service738", "AgentU"), "skvibwe738"),
    (("service738", "keyboard"), "cipwwcv738"),
    (("service738", "AA"), "service738"),
    (("gateway738", "key"), "qeroayi738"),
    (("gateway738", "lemon"), "refsjlc738"),
    (("gateway738", "a"), "gateway738"),
    (("gateway738", "zz"), "fzsdvzx738"),
    (("gateway738", "AgentU"), "ggxrpuy738"),
    (("gateway738", "keyboard"), "qerfkap738"),
    (("gateway738", "AA"), "gateway738"),
    (("storage738", "key"), "cxmbeeo738"),
    (("storage738", "lemon"), "dxafnri738"),
    (("storage738", "a"), "storage738"),
    (("storage738", "zz"), "rsnqzfd738"),
    (("storage738", "AgentU"), "szsetae738"),
    (("storage738", "keyboard"), "cxmsogv738"),
    (("storage738", "AA"), "storage738"),
    (("network738", "key"), "xirgspu738"),
    (("network738", "lemon"), "yifkbco738"),
    (("network738", "a"), "network738"),
    (("network738", "zz"), "mdsvnqj738"),
    (("network738", "AgentU"), "nkxjhlk738"),
    (("network738", "keyboard"), "xirxcrb738"),
    (("network738", "AA"), "network738"),
    (("latency738", "key"), "verorai738"),
    (("latency738", "lemon"), "wefsanc738"),
    (("latency738", "a"), "latency738"),
    (("latency738", "zz"), "kzsdmbx738"),
    (("latency738", "AgentU"), "lgxrgwy738"),
    (("latency738", "keyboard"), "verfbcp738"),
    (("latency738", "AA"), "latency738"),
    (("buffer738", "key"), "lydpip738"),
    (("buffer738", "lemon"), "myrtrc738"),
    (("buffer738", "a"), "buffer738"),
    (("buffer738", "zz"), "ateedq738"),
    (("buffer738", "AgentU"), "bajsxl738"),
    (("buffer738", "keyboard"), "lydgsr738"),
    (("buffer738", "AA"), "buffer738"),
    (("queue738", "key"), "aycei738"),
    (("queue738", "lemon"), "byqir738"),
    (("queue738", "a"), "queue738"),
    (("queue738", "zz"), "ptdtd738"),
    (("queue738", "AgentU"), "qaihx738"),
    (("queue738", "keyboard"), "aycvs738"),
    (("queue738", "AA"), "queue738"),
    (("worker738", "key"), "gspuip738"),
    (("worker738", "lemon"), "hsdyrc738"),
    (("worker738", "a"), "worker738"),
    (("worker738", "zz"), "vnqjdq738"),
    (("worker738", "AgentU"), "wuvxxl738"),
    (("worker738", "keyboard"), "gsplsr738"),
    (("worker738", "AA"), "worker738"),
    (("kernel738", "key"), "uipxij738"),
    (("kernel738", "lemon"), "vidbrw738"),
    (("kernel738", "a"), "kernel738"),
    (("kernel738", "zz"), "jdqmdk738"),
    (("kernel738", "AgentU"), "kkvaxf738"),
    (("kernel738", "keyboard"), "uiposl738"),
    (("kernel738", "AA"), "kernel738"),
    (("signal738", "key"), "cmexej738"),
    (("signal738", "lemon"), "dmsbnw738"),
    (("signal738", "a"), "signal738"),
    (("signal738", "zz"), "rhfmzk738"),
    (("signal738", "AgentU"), "sokatf738"),
    (("signal738", "keyboard"), "cmeool738"),
    (("signal738", "AA"), "signal738"),
    (("packet738", "key"), "zeauir738"),
    (("packet738", "lemon"), "aeoyre738"),
    (("packet738", "a"), "packet738"),
    (("packet738", "zz"), "ozbjds738"),
    (("packet738", "AgentU"), "pggxxn738"),
    (("packet738", "keyboard"), "zealst738"),
    (("packet738", "AA"), "packet738"),
    (("router738", "key"), "bssdip738"),
    (("router738", "lemon"), "csghrc738"),
    (("router738", "a"), "router738"),
    (("router738", "zz"), "qntsdq738"),
    (("router738", "AgentU"), "ruygxl738"),
    (("router738", "keyboard"), "bssusr738"),
    (("router738", "AA"), "router738"),
    (("cluster738", "key"), "mpscxcb738"),
    (("cluster738", "lemon"), "npgggpv738"),
    (("cluster738", "a"), "cluster738"),
    (("cluster738", "zz"), "bktrsdq738"),
    (("cluster738", "AgentU"), "cryfmyr738"),
    (("cluster738", "keyboard"), "mpsthei738"),
    (("cluster738", "AA"), "cluster738"),
    (("mirror738", "key"), "wmpbsp738"),
    (("mirror738", "lemon"), "xmdfbc738"),
    (("mirror738", "a"), "mirror738"),
    (("mirror738", "zz"), "lhqqnq738"),
    (("mirror738", "AgentU"), "movehl738"),
    (("mirror738", "keyboard"), "wmpscr738"),
    (("mirror738", "AA"), "mirror738"),
    (("filter738", "key"), "pmjdip738"),
    (("filter738", "lemon"), "qmxhrc738"),
    (("filter738", "a"), "filter738"),
    (("filter738", "zz"), "ehksdq738"),
    (("filter738", "AgentU"), "fopgxl738"),
    (("filter738", "keyboard"), "pmjusr738"),
    (("filter738", "AA"), "filter738"),
    (("ranking738", "key"), "belumlq738"),
    (("ranking738", "lemon"), "cezyvyk738"),
    (("ranking738", "a"), "ranking738"),
    (("ranking738", "zz"), "qzmjhmf738"),
    (("ranking738", "AgentU"), "rgrxbhg738"),
    (("ranking738", "keyboard"), "bellwnx738"),
    (("ranking738", "AA"), "ranking738"),
    (("encoding738", "key"), "orayhgxk738"),
    (("encoding738", "lemon"), "procqtrs738"),
    (("encoding738", "a"), "encoding738"),
    (("encoding738", "zz"), "dmbnchmf738"),
    (("encoding738", "AgentU"), "etgbwcnm738"),
    (("encoding738", "keyboard"), "orapriej738"),
    (("encoding738", "AA"), "encoding738"),
    (("mapping738", "key"), "wenzmlq738"),
    (("mapping738", "lemon"), "xebdvyk738"),
    (("mapping738", "a"), "mapping738"),
    (("mapping738", "zz"), "lzoohmf738"),
    (("mapping738", "AgentU"), "mgtcbhg738"),
    (("mapping738", "keyboard"), "wenqwnx738"),
    (("mapping738", "AA"), "mapping738"),
    (("record738", "key"), "biayvb738"),
    (("record738", "lemon"), "cioceo738"),
    (("record738", "a"), "record738"),
    (("record738", "zz"), "qdbnqc738"),
    (("record738", "AgentU"), "rkgbkx738"),
    (("record738", "keyboard"), "biapfd738"),
    (("record738", "AA"), "record738"),
    (("candle738", "key"), "melnpc738"),
    (("candle738", "lemon"), "nezryp738"),
    (("candle738", "a"), "candle738"),
    (("candle738", "zz"), "bzmckd738"),
    (("candle738", "AgentU"), "cgrqey738"),
    (("candle738", "keyboard"), "meleze738"),
    (("candle738", "AA"), "candle738"),
    (("thread738", "key"), "dlpoeb738"),
    (("thread738", "lemon"), "eldsno738"),
    (("thread738", "a"), "thread738"),
    (("thread738", "zz"), "sgqdzc738"),
    (("thread738", "AgentU"), "tnvrtx738"),
    (("thread738", "keyboard"), "dlpfod738"),
    (("thread738", "AA"), "thread738"),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 738: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 738: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "a"),
        "round 738: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 738: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 738: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 738: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", "AA"),
        "round 738: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "key"),
        "bssxh 738: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 738: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "a"),
        "round 738: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 738: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 738: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 738: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", "AA"),
        "round 738: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 738: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 738: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "a"),
        "round 738: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 738: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 738: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 738: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", "AA"),
        "round 738: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 738: the processor reads the record then stops", "key"),
        "bssxh 738: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 738: the processor reads the record then stops", "lemon"),
        "csgbq 738: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 738: the processor reads the record then stops", "a"),
        "round 738: the processor reads the record then stops",
    ),
    (
        ("round 738: the processor reads the record then stops", "zz"),
        "qntmc 738: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 738: the processor reads the record then stops", "AgentU"),
        "ruyaw 738: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 738: the processor reads the record then stops", "keyboard"),
        "bssor 738: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 738: the processor reads the record then stops", "AA"),
        "round 738: the processor reads the record then stops",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "key"),
        "bssxh 738: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "lemon"),
        "csgbq 738: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "a"),
        "round 738: a worker pulls the next task from the queue",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "zz"),
        "qntmc 738: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 738: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "keyboard"),
        "bssor 738: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 738: a worker pulls the next task from the queue", "AA"),
        "round 738: a worker pulls the next task from the queue",
    ),
    (
        ("round 738: signals travel through the network layer", "key"),
        "bssxh 738: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 738: signals travel through the network layer", "lemon"),
        "csgbq 738: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 738: signals travel through the network layer", "a"),
        "round 738: signals travel through the network layer",
    ),
    (
        ("round 738: signals travel through the network layer", "zz"),
        "qntmc 738: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 738: signals travel through the network layer", "AgentU"),
        "ruyaw 738: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 738: signals travel through the network layer", "keyboard"),
        "bssor 738: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 738: signals travel through the network layer", "AA"),
        "round 738: signals travel through the network layer",
    ),
    (
        ("round 738: the gateway routes each request by policy", "key"),
        "bssxh 738: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 738: the gateway routes each request by policy", "lemon"),
        "csgbq 738: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 738: the gateway routes each request by policy", "a"),
        "round 738: the gateway routes each request by policy",
    ),
    (
        ("round 738: the gateway routes each request by policy", "zz"),
        "qntmc 738: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 738: the gateway routes each request by policy", "AgentU"),
        "ruyaw 738: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 738: the gateway routes each request by policy", "keyboard"),
        "bssor 738: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 738: the gateway routes each request by policy", "AA"),
        "round 738: the gateway routes each request by policy",
    ),
    (("round 738: memory grows until the buffer is full", "key"), "bssxh 738: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 738: memory grows until the buffer is full", "lemon"), "csgbq 738: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 738: memory grows until the buffer is full", "a"), "round 738: memory grows until the buffer is full"),
    (("round 738: memory grows until the buffer is full", "zz"), "qntmc 738: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 738: memory grows until the buffer is full", "AgentU"),
        "ruyaw 738: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 738: memory grows until the buffer is full", "keyboard"),
        "bssor 738: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 738: memory grows until the buffer is full", "AA"), "round 738: memory grows until the buffer is full"),
    (("round 738: the cluster mirrors every packet twice", "key"), "bssxh 738: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 738: the cluster mirrors every packet twice", "lemon"),
        "csgbq 738: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 738: the cluster mirrors every packet twice", "a"), "round 738: the cluster mirrors every packet twice"),
    (("round 738: the cluster mirrors every packet twice", "zz"), "qntmc 738: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 738: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 738: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 738: the cluster mirrors every packet twice", "keyboard"),
        "bssor 738: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 738: the cluster mirrors every packet twice", "AA"), "round 738: the cluster mirrors every packet twice"),
    (
        ("round 738: ranking uses tokens learned from the corpus", "key"),
        "bssxh 738: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 738: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", "a"),
        "round 738: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 738: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 738: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 738: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", "AA"),
        "round 738: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 738: a long session ends when the candle dies", "key"),
        "bssxh 738: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 738: a long session ends when the candle dies", "lemon"),
        "csgbq 738: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 738: a long session ends when the candle dies", "a"),
        "round 738: a long session ends when the candle dies",
    ),
    (
        ("round 738: a long session ends when the candle dies", "zz"),
        "qntmc 738: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 738: a long session ends when the candle dies", "AgentU"),
        "ruyaw 738: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 738: a long session ends when the candle dies", "keyboard"),
        "bssor 738: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 738: a long session ends when the candle dies", "AA"),
        "round 738: a long session ends when the candle dies",
    ),
    (("round 738: encode the prompt then map the result", "key"), "bssxh 738: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 738: encode the prompt then map the result", "lemon"), "csgbq 738: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 738: encode the prompt then map the result", "a"), "round 738: encode the prompt then map the result"),
    (("round 738: encode the prompt then map the result", "zz"), "qntmc 738: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 738: encode the prompt then map the result", "AgentU"),
        "ruyaw 738: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 738: encode the prompt then map the result", "keyboard"),
        "bssor 738: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 738: encode the prompt then map the result", "AA"), "round 738: encode the prompt then map the result"),
    (("round 738: the kernel wakes the worker at dawn", "key"), "bssxh 738: rri iovlop ukocc xfo ambocb er neux"),
    (("round 738: the kernel wakes the worker at dawn", "lemon"), "csgbq 738: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 738: the kernel wakes the worker at dawn", "a"), "round 738: the kernel wakes the worker at dawn"),
    (("round 738: the kernel wakes the worker at dawn", "zz"), "qntmc 738: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 738: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 738: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 738: the kernel wakes the worker at dawn", "keyboard"), "bssor 738: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 738: the kernel wakes the worker at dawn", "AA"), "round 738: the kernel wakes the worker at dawn"),
    (("round 738: service latency drops after the patch", "key"), "bssxh 738: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 738: service latency drops after the patch", "lemon"), "csgbq 738: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 738: service latency drops after the patch", "a"), "round 738: service latency drops after the patch"),
    (("round 738: service latency drops after the patch", "zz"), "qntmc 738: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 738: service latency drops after the patch", "AgentU"),
        "ruyaw 738: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 738: service latency drops after the patch", "keyboard"),
        "bssor 738: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 738: service latency drops after the patch", "AA"), "round 738: service latency drops after the patch"),
    (
        ("round 738: the library caches every vector it sees", "key"),
        "bssxh 738: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 738: the library caches every vector it sees", "lemon"),
        "csgbq 738: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 738: the library caches every vector it sees", "a"), "round 738: the library caches every vector it sees"),
    (
        ("round 738: the library caches every vector it sees", "zz"),
        "qntmc 738: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 738: the library caches every vector it sees", "AgentU"),
        "ruyaw 738: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 738: the library caches every vector it sees", "keyboard"),
        "bssor 738: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 738: the library caches every vector it sees", "AA"),
        "round 738: the library caches every vector it sees",
    ),
    (("round 738: agents argue then the debate resolves", "key"), "bssxh 738: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 738: agents argue then the debate resolves", "lemon"), "csgbq 738: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 738: agents argue then the debate resolves", "a"), "round 738: agents argue then the debate resolves"),
    (("round 738: agents argue then the debate resolves", "zz"), "qntmc 738: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 738: agents argue then the debate resolves", "AgentU"),
        "ruyaw 738: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 738: agents argue then the debate resolves", "keyboard"),
        "bssor 738: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 738: agents argue then the debate resolves", "AA"), "round 738: agents argue then the debate resolves"),
    (("round 738: the filter keeps only strong matches", "key"), "bssxh 738: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 738: the filter keeps only strong matches", "lemon"), "csgbq 738: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 738: the filter keeps only strong matches", "a"), "round 738: the filter keeps only strong matches"),
    (("round 738: the filter keeps only strong matches", "zz"), "qntmc 738: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 738: the filter keeps only strong matches", "AgentU"), "ruyaw 738: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 738: the filter keeps only strong matches", "keyboard"),
        "bssor 738: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 738: the filter keeps only strong matches", "AA"), "round 738: the filter keeps only strong matches"),
    (("round 738: the model answers with a short reply", "key"), "bssxh 738: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 738: the model answers with a short reply", "lemon"), "csgbq 738: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 738: the model answers with a short reply", "a"), "round 738: the model answers with a short reply"),
    (("round 738: the model answers with a short reply", "zz"), "qntmc 738: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 738: the model answers with a short reply", "AgentU"), "ruyaw 738: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 738: the model answers with a short reply", "keyboard"),
        "bssor 738: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 738: the model answers with a short reply", "AA"), "round 738: the model answers with a short reply"),
    (
        ("round 738: the recorder stores the reasoning trace", "key"),
        "bssxh 738: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 738: the recorder stores the reasoning trace", "lemon"),
        "csgbq 738: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 738: the recorder stores the reasoning trace", "a"), "round 738: the recorder stores the reasoning trace"),
    (
        ("round 738: the recorder stores the reasoning trace", "zz"),
        "qntmc 738: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 738: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 738: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 738: the recorder stores the reasoning trace", "keyboard"),
        "bssor 738: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 738: the recorder stores the reasoning trace", "AA"),
        "round 738: the recorder stores the reasoning trace",
    ),
    (("round 738: the angel watches the processor run", "key"), "bssxh 738: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 738: the angel watches the processor run", "lemon"), "csgbq 738: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 738: the angel watches the processor run", "a"), "round 738: the angel watches the processor run"),
    (("round 738: the angel watches the processor run", "zz"), "qntmc 738: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 738: the angel watches the processor run", "AgentU"), "ruyaw 738: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 738: the angel watches the processor run", "keyboard"), "bssor 738: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 738: the angel watches the processor run", "AA"), "round 738: the angel watches the processor run"),
    (("round 738: angle of the vector decides the match", "key"), "bssxh 738: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 738: angle of the vector decides the match", "lemon"), "csgbq 738: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 738: angle of the vector decides the match", "a"), "round 738: angle of the vector decides the match"),
    (("round 738: angle of the vector decides the match", "zz"), "qntmc 738: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 738: angle of the vector decides the match", "AgentU"),
        "ruyaw 738: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 738: angle of the vector decides the match", "keyboard"),
        "bssor 738: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 738: angle of the vector decides the match", "AA"), "round 738: angle of the vector decides the match"),
    (
        ("round 738: the candle burns twice as long at night", "key"),
        "bssxh 738: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 738: the candle burns twice as long at night", "lemon"),
        "csgbq 738: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 738: the candle burns twice as long at night", "a"), "round 738: the candle burns twice as long at night"),
    (
        ("round 738: the candle burns twice as long at night", "zz"),
        "qntmc 738: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 738: the candle burns twice as long at night", "AgentU"),
        "ruyaw 738: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 738: the candle burns twice as long at night", "keyboard"),
        "bssor 738: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 738: the candle burns twice as long at night", "AA"),
        "round 738: the candle burns twice as long at night",
    ),
    (("round 738: a mirror of the universe in one line", "key"), "bssxh 738: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 738: a mirror of the universe in one line", "lemon"), "csgbq 738: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 738: a mirror of the universe in one line", "a"), "round 738: a mirror of the universe in one line"),
    (("round 738: a mirror of the universe in one line", "zz"), "qntmc 738: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 738: a mirror of the universe in one line", "AgentU"), "ruyaw 738: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 738: a mirror of the universe in one line", "keyboard"),
        "bssor 738: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 738: a mirror of the universe in one line", "AA"), "round 738: a mirror of the universe in one line"),
    (("round 738: the queue drains before the storm", "key"), "bssxh 738: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 738: the queue drains before the storm", "lemon"), "csgbq 738: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 738: the queue drains before the storm", "a"), "round 738: the queue drains before the storm"),
    (("round 738: the queue drains before the storm", "zz"), "qntmc 738: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 738: the queue drains before the storm", "AgentU"), "ruyaw 738: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 738: the queue drains before the storm", "keyboard"), "bssor 738: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 738: the queue drains before the storm", "AA"), "round 738: the queue drains before the storm"),
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
