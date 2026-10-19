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
    (("kitten736", "key"), "umrdil736"),
    (("kitten736", "lemon"), "vmfhry736"),
    (("kitten736", "a"), "kitten736"),
    (("kitten736", "zz"), "jhssdm736"),
    (("kitten736", "AgentU"), "koxgxh736"),
    (("kitten736", "keyboard"), "umrusn736"),
    (("kitten736", "AA"), "kitten736"),
    (("sitting736", "key"), "cmrdmlq736"),
    (("sitting736", "lemon"), "dmfhvyk736"),
    (("sitting736", "a"), "sitting736"),
    (("sitting736", "zz"), "rhsshmf736"),
    (("sitting736", "AgentU"), "soxgbhg736"),
    (("sitting736", "keyboard"), "cmruwnx736"),
    (("sitting736", "AA"), "sitting736"),
    (("agent736", "key"), "kkcxx736"),
    (("agent736", "lemon"), "lkqbg736"),
    (("agent736", "a"), "agent736"),
    (("agent736", "zz"), "zfdms736"),
    (("agent736", "AgentU"), "amiam736"),
    (("agent736", "keyboard"), "kkcoh736"),
    (("agent736", "AA"), "agent736"),
    (("angle736", "key"), "krevi736"),
    (("angle736", "lemon"), "lrszr736"),
    (("angle736", "a"), "angle736"),
    (("angle736", "zz"), "zmfkd736"),
    (("angle736", "AgentU"), "atkyx736"),
    (("angle736", "keyboard"), "krems736"),
    (("angle736", "AA"), "angle736"),
    (("universe736", "key"), "ergfipci736"),
    (("universe736", "lemon"), "frujrcwq736"),
    (("universe736", "a"), "universe736"),
    (("universe736", "zz"), "tmhudqrd736"),
    (("universe736", "AgentU"), "utmixlsk736"),
    (("universe736", "keyboard"), "ergwsrjh736"),
    (("universe736", "AA"), "universe736"),
    (("memory736", "key"), "wikyvw736"),
    (("memory736", "lemon"), "xiycej736"),
    (("memory736", "a"), "memory736"),
    (("memory736", "zz"), "ldlnqx736"),
    (("memory736", "AgentU"), "mkqbks736"),
    (("memory736", "keyboard"), "wikpfy736"),
    (("memory736", "AA"), "memory736"),
    (("stream736", "key"), "cxpoek736"),
    (("stream736", "lemon"), "dxdsnx736"),
    (("stream736", "a"), "stream736"),
    (("stream736", "zz"), "rsqdzl736"),
    (("stream736", "AgentU"), "szvrtg736"),
    (("stream736", "keyboard"), "cxpfom736"),
    (("stream736", "AA"), "stream736"),
    (("context736", "key"), "msldivd736"),
    (("context736", "lemon"), "nszhrix736"),
    (("context736", "a"), "context736"),
    (("context736", "zz"), "bnmsdws736"),
    (("context736", "AgentU"), "curgxrt736"),
    (("context736", "keyboard"), "mslusxk736"),
    (("context736", "AA"), "context736"),
    (("knowledge736", "key"), "urmgpcnkc736"),
    (("knowledge736", "lemon"), "vrakyphss736"),
    (("knowledge736", "a"), "knowledge736"),
    (("knowledge736", "zz"), "jmnvkdcfd736"),
    (("knowledge736", "AgentU"), "ktsjeydmi736"),
    (("knowledge736", "keyboard"), "urmxzeujo736"),
    (("knowledge736", "AA"), "knowledge736"),
    (("vector736", "key"), "fiadsp736"),
    (("vector736", "lemon"), "giohbc736"),
    (("vector736", "a"), "vector736"),
    (("vector736", "zz"), "udbsnq736"),
    (("vector736", "AgentU"), "vkgghl736"),
    (("vector736", "keyboard"), "fiaucr736"),
    (("vector736", "AA"), "vector736"),
    (("processor736", "key"), "zvmmiqcsp736"),
    (("processor736", "lemon"), "avaqrdwaf736"),
    (("processor736", "a"), "processor736"),
    (("processor736", "zz"), "oqnbdrrnq736"),
    (("processor736", "AgentU"), "pxspxmsuv736"),
    (("processor736", "keyboard"), "zvmdssjrb736"),
    (("processor736", "AA"), "processor736"),
    (("reasoning736", "key"), "biycslsre736"),
    (("reasoning736", "lemon"), "cimgbymzu736"),
    (("reasoning736", "a"), "reasoning736"),
    (("reasoning736", "zz"), "qdzrnmhmf736"),
    (("reasoning736", "AgentU"), "rkefhhitk736"),
    (("reasoning736", "keyboard"), "biytcnzqq736"),
    (("reasoning736", "AA"), "reasoning736"),
    (("machine736", "key"), "wearmlo736"),
    (("machine736", "lemon"), "xeovvyi736"),
    (("machine736", "a"), "machine736"),
    (("machine736", "zz"), "lzbghmd736"),
    (("machine736", "AgentU"), "mggubhe736"),
    (("machine736", "keyboard"), "weaiwnv736"),
    (("machine736", "AA"), "machine736"),
    (("learning736", "key"), "viybrgxk736"),
    (("learning736", "lemon"), "wimfatrs736"),
    (("learning736", "a"), "learning736"),
    (("learning736", "zz"), "kdzqmhmf736"),
    (("learning736", "AgentU"), "lkeegcnm736"),
    (("learning736", "keyboard"), "viysbiej736"),
    (("learning736", "AA"), "learning736"),
    (("model736", "key"), "wsbop736"),
    (("model736", "lemon"), "xspsy736"),
    (("model736", "a"), "model736"),
    (("model736", "zz"), "lncdk736"),
    (("model736", "AgentU"), "muhre736"),
    (("model736", "keyboard"), "wsbfz736"),
    (("model736", "AA"), "model736"),
    (("token736", "key"), "dsior736"),
    (("token736", "lemon"), "eswsa736"),
    (("token736", "a"), "token736"),
    (("token736", "zz"), "snjdm736"),
    (("token736", "AgentU"), "tuorg736"),
    (("token736", "keyboard"), "dsifb736"),
    (("token736", "AA"), "token736"),
    (("prompt736", "key"), "zvmwtr736"),
    (("prompt736", "lemon"), "avaace736"),
    (("prompt736", "a"), "prompt736"),
    (("prompt736", "zz"), "oqnlos736"),
    (("prompt736", "AgentU"), "pxszin736"),
    (("prompt736", "keyboard"), "zvmndt736"),
    (("prompt736", "AA"), "prompt736"),
    (("session736", "key"), "ciqcmmx736"),
    (("session736", "lemon"), "diegvzr736"),
    (("session736", "a"), "session736"),
    (("session736", "zz"), "rdrrhnm736"),
    (("session736", "AgentU"), "skwfbin736"),
    (("session736", "keyboard"), "ciqtwoe736"),
    (("session736", "AA"), "session736"),
    (("library736", "key"), "vmzbepi736"),
    (("library736", "lemon"), "wmnfncc736"),
    (("library736", "a"), "library736"),
    (("library736", "zz"), "khaqzqx736"),
    (("library736", "AgentU"), "lofetly736"),
    (("library736", "keyboard"), "vmzsorp736"),
    (("library736", "AA"), "library736"),
    (("service736", "key"), "cipfmao736"),
    (("service736", "lemon"), "didjvni736"),
    (("service736", "a"), "service736"),
    (("service736", "zz"), "rdquhbd736"),
    (("service736", "AgentU"), "skvibwe736"),
    (("service736", "keyboard"), "cipwwcv736"),
    (("service736", "AA"), "service736"),
    (("gateway736", "key"), "qeroayi736"),
    (("gateway736", "lemon"), "refsjlc736"),
    (("gateway736", "a"), "gateway736"),
    (("gateway736", "zz"), "fzsdvzx736"),
    (("gateway736", "AgentU"), "ggxrpuy736"),
    (("gateway736", "keyboard"), "qerfkap736"),
    (("gateway736", "AA"), "gateway736"),
    (("storage736", "key"), "cxmbeeo736"),
    (("storage736", "lemon"), "dxafnri736"),
    (("storage736", "a"), "storage736"),
    (("storage736", "zz"), "rsnqzfd736"),
    (("storage736", "AgentU"), "szsetae736"),
    (("storage736", "keyboard"), "cxmsogv736"),
    (("storage736", "AA"), "storage736"),
    (("network736", "key"), "xirgspu736"),
    (("network736", "lemon"), "yifkbco736"),
    (("network736", "a"), "network736"),
    (("network736", "zz"), "mdsvnqj736"),
    (("network736", "AgentU"), "nkxjhlk736"),
    (("network736", "keyboard"), "xirxcrb736"),
    (("network736", "AA"), "network736"),
    (("latency736", "key"), "verorai736"),
    (("latency736", "lemon"), "wefsanc736"),
    (("latency736", "a"), "latency736"),
    (("latency736", "zz"), "kzsdmbx736"),
    (("latency736", "AgentU"), "lgxrgwy736"),
    (("latency736", "keyboard"), "verfbcp736"),
    (("latency736", "AA"), "latency736"),
    (("buffer736", "key"), "lydpip736"),
    (("buffer736", "lemon"), "myrtrc736"),
    (("buffer736", "a"), "buffer736"),
    (("buffer736", "zz"), "ateedq736"),
    (("buffer736", "AgentU"), "bajsxl736"),
    (("buffer736", "keyboard"), "lydgsr736"),
    (("buffer736", "AA"), "buffer736"),
    (("queue736", "key"), "aycei736"),
    (("queue736", "lemon"), "byqir736"),
    (("queue736", "a"), "queue736"),
    (("queue736", "zz"), "ptdtd736"),
    (("queue736", "AgentU"), "qaihx736"),
    (("queue736", "keyboard"), "aycvs736"),
    (("queue736", "AA"), "queue736"),
    (("worker736", "key"), "gspuip736"),
    (("worker736", "lemon"), "hsdyrc736"),
    (("worker736", "a"), "worker736"),
    (("worker736", "zz"), "vnqjdq736"),
    (("worker736", "AgentU"), "wuvxxl736"),
    (("worker736", "keyboard"), "gsplsr736"),
    (("worker736", "AA"), "worker736"),
    (("kernel736", "key"), "uipxij736"),
    (("kernel736", "lemon"), "vidbrw736"),
    (("kernel736", "a"), "kernel736"),
    (("kernel736", "zz"), "jdqmdk736"),
    (("kernel736", "AgentU"), "kkvaxf736"),
    (("kernel736", "keyboard"), "uiposl736"),
    (("kernel736", "AA"), "kernel736"),
    (("signal736", "key"), "cmexej736"),
    (("signal736", "lemon"), "dmsbnw736"),
    (("signal736", "a"), "signal736"),
    (("signal736", "zz"), "rhfmzk736"),
    (("signal736", "AgentU"), "sokatf736"),
    (("signal736", "keyboard"), "cmeool736"),
    (("signal736", "AA"), "signal736"),
    (("packet736", "key"), "zeauir736"),
    (("packet736", "lemon"), "aeoyre736"),
    (("packet736", "a"), "packet736"),
    (("packet736", "zz"), "ozbjds736"),
    (("packet736", "AgentU"), "pggxxn736"),
    (("packet736", "keyboard"), "zealst736"),
    (("packet736", "AA"), "packet736"),
    (("router736", "key"), "bssdip736"),
    (("router736", "lemon"), "csghrc736"),
    (("router736", "a"), "router736"),
    (("router736", "zz"), "qntsdq736"),
    (("router736", "AgentU"), "ruygxl736"),
    (("router736", "keyboard"), "bssusr736"),
    (("router736", "AA"), "router736"),
    (("cluster736", "key"), "mpscxcb736"),
    (("cluster736", "lemon"), "npgggpv736"),
    (("cluster736", "a"), "cluster736"),
    (("cluster736", "zz"), "bktrsdq736"),
    (("cluster736", "AgentU"), "cryfmyr736"),
    (("cluster736", "keyboard"), "mpsthei736"),
    (("cluster736", "AA"), "cluster736"),
    (("mirror736", "key"), "wmpbsp736"),
    (("mirror736", "lemon"), "xmdfbc736"),
    (("mirror736", "a"), "mirror736"),
    (("mirror736", "zz"), "lhqqnq736"),
    (("mirror736", "AgentU"), "movehl736"),
    (("mirror736", "keyboard"), "wmpscr736"),
    (("mirror736", "AA"), "mirror736"),
    (("filter736", "key"), "pmjdip736"),
    (("filter736", "lemon"), "qmxhrc736"),
    (("filter736", "a"), "filter736"),
    (("filter736", "zz"), "ehksdq736"),
    (("filter736", "AgentU"), "fopgxl736"),
    (("filter736", "keyboard"), "pmjusr736"),
    (("filter736", "AA"), "filter736"),
    (("ranking736", "key"), "belumlq736"),
    (("ranking736", "lemon"), "cezyvyk736"),
    (("ranking736", "a"), "ranking736"),
    (("ranking736", "zz"), "qzmjhmf736"),
    (("ranking736", "AgentU"), "rgrxbhg736"),
    (("ranking736", "keyboard"), "bellwnx736"),
    (("ranking736", "AA"), "ranking736"),
    (("encoding736", "key"), "orayhgxk736"),
    (("encoding736", "lemon"), "procqtrs736"),
    (("encoding736", "a"), "encoding736"),
    (("encoding736", "zz"), "dmbnchmf736"),
    (("encoding736", "AgentU"), "etgbwcnm736"),
    (("encoding736", "keyboard"), "orapriej736"),
    (("encoding736", "AA"), "encoding736"),
    (("mapping736", "key"), "wenzmlq736"),
    (("mapping736", "lemon"), "xebdvyk736"),
    (("mapping736", "a"), "mapping736"),
    (("mapping736", "zz"), "lzoohmf736"),
    (("mapping736", "AgentU"), "mgtcbhg736"),
    (("mapping736", "keyboard"), "wenqwnx736"),
    (("mapping736", "AA"), "mapping736"),
    (("record736", "key"), "biayvb736"),
    (("record736", "lemon"), "cioceo736"),
    (("record736", "a"), "record736"),
    (("record736", "zz"), "qdbnqc736"),
    (("record736", "AgentU"), "rkgbkx736"),
    (("record736", "keyboard"), "biapfd736"),
    (("record736", "AA"), "record736"),
    (("candle736", "key"), "melnpc736"),
    (("candle736", "lemon"), "nezryp736"),
    (("candle736", "a"), "candle736"),
    (("candle736", "zz"), "bzmckd736"),
    (("candle736", "AgentU"), "cgrqey736"),
    (("candle736", "keyboard"), "meleze736"),
    (("candle736", "AA"), "candle736"),
    (("thread736", "key"), "dlpoeb736"),
    (("thread736", "lemon"), "eldsno736"),
    (("thread736", "a"), "thread736"),
    (("thread736", "zz"), "sgqdzc736"),
    (("thread736", "AgentU"), "tnvrtx736"),
    (("thread736", "keyboard"), "dlpfod736"),
    (("thread736", "AA"), "thread736"),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 736: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 736: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "a"),
        "round 736: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 736: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 736: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 736: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", "AA"),
        "round 736: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "key"),
        "bssxh 736: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 736: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "a"),
        "round 736: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 736: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 736: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 736: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", "AA"),
        "round 736: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 736: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 736: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "a"),
        "round 736: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 736: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 736: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 736: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", "AA"),
        "round 736: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 736: the processor reads the record then stops", "key"),
        "bssxh 736: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 736: the processor reads the record then stops", "lemon"),
        "csgbq 736: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 736: the processor reads the record then stops", "a"),
        "round 736: the processor reads the record then stops",
    ),
    (
        ("round 736: the processor reads the record then stops", "zz"),
        "qntmc 736: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 736: the processor reads the record then stops", "AgentU"),
        "ruyaw 736: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 736: the processor reads the record then stops", "keyboard"),
        "bssor 736: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 736: the processor reads the record then stops", "AA"),
        "round 736: the processor reads the record then stops",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "key"),
        "bssxh 736: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "lemon"),
        "csgbq 736: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "a"),
        "round 736: a worker pulls the next task from the queue",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "zz"),
        "qntmc 736: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 736: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "keyboard"),
        "bssor 736: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 736: a worker pulls the next task from the queue", "AA"),
        "round 736: a worker pulls the next task from the queue",
    ),
    (
        ("round 736: signals travel through the network layer", "key"),
        "bssxh 736: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 736: signals travel through the network layer", "lemon"),
        "csgbq 736: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 736: signals travel through the network layer", "a"),
        "round 736: signals travel through the network layer",
    ),
    (
        ("round 736: signals travel through the network layer", "zz"),
        "qntmc 736: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 736: signals travel through the network layer", "AgentU"),
        "ruyaw 736: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 736: signals travel through the network layer", "keyboard"),
        "bssor 736: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 736: signals travel through the network layer", "AA"),
        "round 736: signals travel through the network layer",
    ),
    (
        ("round 736: the gateway routes each request by policy", "key"),
        "bssxh 736: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 736: the gateway routes each request by policy", "lemon"),
        "csgbq 736: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 736: the gateway routes each request by policy", "a"),
        "round 736: the gateway routes each request by policy",
    ),
    (
        ("round 736: the gateway routes each request by policy", "zz"),
        "qntmc 736: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 736: the gateway routes each request by policy", "AgentU"),
        "ruyaw 736: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 736: the gateway routes each request by policy", "keyboard"),
        "bssor 736: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 736: the gateway routes each request by policy", "AA"),
        "round 736: the gateway routes each request by policy",
    ),
    (("round 736: memory grows until the buffer is full", "key"), "bssxh 736: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 736: memory grows until the buffer is full", "lemon"), "csgbq 736: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 736: memory grows until the buffer is full", "a"), "round 736: memory grows until the buffer is full"),
    (("round 736: memory grows until the buffer is full", "zz"), "qntmc 736: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 736: memory grows until the buffer is full", "AgentU"),
        "ruyaw 736: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 736: memory grows until the buffer is full", "keyboard"),
        "bssor 736: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 736: memory grows until the buffer is full", "AA"), "round 736: memory grows until the buffer is full"),
    (("round 736: the cluster mirrors every packet twice", "key"), "bssxh 736: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 736: the cluster mirrors every packet twice", "lemon"),
        "csgbq 736: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 736: the cluster mirrors every packet twice", "a"), "round 736: the cluster mirrors every packet twice"),
    (("round 736: the cluster mirrors every packet twice", "zz"), "qntmc 736: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 736: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 736: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 736: the cluster mirrors every packet twice", "keyboard"),
        "bssor 736: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 736: the cluster mirrors every packet twice", "AA"), "round 736: the cluster mirrors every packet twice"),
    (
        ("round 736: ranking uses tokens learned from the corpus", "key"),
        "bssxh 736: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 736: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", "a"),
        "round 736: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 736: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 736: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 736: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", "AA"),
        "round 736: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 736: a long session ends when the candle dies", "key"),
        "bssxh 736: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 736: a long session ends when the candle dies", "lemon"),
        "csgbq 736: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 736: a long session ends when the candle dies", "a"),
        "round 736: a long session ends when the candle dies",
    ),
    (
        ("round 736: a long session ends when the candle dies", "zz"),
        "qntmc 736: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 736: a long session ends when the candle dies", "AgentU"),
        "ruyaw 736: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 736: a long session ends when the candle dies", "keyboard"),
        "bssor 736: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 736: a long session ends when the candle dies", "AA"),
        "round 736: a long session ends when the candle dies",
    ),
    (("round 736: encode the prompt then map the result", "key"), "bssxh 736: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 736: encode the prompt then map the result", "lemon"), "csgbq 736: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 736: encode the prompt then map the result", "a"), "round 736: encode the prompt then map the result"),
    (("round 736: encode the prompt then map the result", "zz"), "qntmc 736: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 736: encode the prompt then map the result", "AgentU"),
        "ruyaw 736: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 736: encode the prompt then map the result", "keyboard"),
        "bssor 736: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 736: encode the prompt then map the result", "AA"), "round 736: encode the prompt then map the result"),
    (("round 736: the kernel wakes the worker at dawn", "key"), "bssxh 736: rri iovlop ukocc xfo ambocb er neux"),
    (("round 736: the kernel wakes the worker at dawn", "lemon"), "csgbq 736: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 736: the kernel wakes the worker at dawn", "a"), "round 736: the kernel wakes the worker at dawn"),
    (("round 736: the kernel wakes the worker at dawn", "zz"), "qntmc 736: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 736: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 736: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 736: the kernel wakes the worker at dawn", "keyboard"), "bssor 736: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 736: the kernel wakes the worker at dawn", "AA"), "round 736: the kernel wakes the worker at dawn"),
    (("round 736: service latency drops after the patch", "key"), "bssxh 736: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 736: service latency drops after the patch", "lemon"), "csgbq 736: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 736: service latency drops after the patch", "a"), "round 736: service latency drops after the patch"),
    (("round 736: service latency drops after the patch", "zz"), "qntmc 736: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 736: service latency drops after the patch", "AgentU"),
        "ruyaw 736: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 736: service latency drops after the patch", "keyboard"),
        "bssor 736: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 736: service latency drops after the patch", "AA"), "round 736: service latency drops after the patch"),
    (
        ("round 736: the library caches every vector it sees", "key"),
        "bssxh 736: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 736: the library caches every vector it sees", "lemon"),
        "csgbq 736: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 736: the library caches every vector it sees", "a"), "round 736: the library caches every vector it sees"),
    (
        ("round 736: the library caches every vector it sees", "zz"),
        "qntmc 736: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 736: the library caches every vector it sees", "AgentU"),
        "ruyaw 736: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 736: the library caches every vector it sees", "keyboard"),
        "bssor 736: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 736: the library caches every vector it sees", "AA"),
        "round 736: the library caches every vector it sees",
    ),
    (("round 736: agents argue then the debate resolves", "key"), "bssxh 736: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 736: agents argue then the debate resolves", "lemon"), "csgbq 736: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 736: agents argue then the debate resolves", "a"), "round 736: agents argue then the debate resolves"),
    (("round 736: agents argue then the debate resolves", "zz"), "qntmc 736: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 736: agents argue then the debate resolves", "AgentU"),
        "ruyaw 736: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 736: agents argue then the debate resolves", "keyboard"),
        "bssor 736: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 736: agents argue then the debate resolves", "AA"), "round 736: agents argue then the debate resolves"),
    (("round 736: the filter keeps only strong matches", "key"), "bssxh 736: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 736: the filter keeps only strong matches", "lemon"), "csgbq 736: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 736: the filter keeps only strong matches", "a"), "round 736: the filter keeps only strong matches"),
    (("round 736: the filter keeps only strong matches", "zz"), "qntmc 736: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 736: the filter keeps only strong matches", "AgentU"), "ruyaw 736: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 736: the filter keeps only strong matches", "keyboard"),
        "bssor 736: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 736: the filter keeps only strong matches", "AA"), "round 736: the filter keeps only strong matches"),
    (("round 736: the model answers with a short reply", "key"), "bssxh 736: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 736: the model answers with a short reply", "lemon"), "csgbq 736: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 736: the model answers with a short reply", "a"), "round 736: the model answers with a short reply"),
    (("round 736: the model answers with a short reply", "zz"), "qntmc 736: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 736: the model answers with a short reply", "AgentU"), "ruyaw 736: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 736: the model answers with a short reply", "keyboard"),
        "bssor 736: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 736: the model answers with a short reply", "AA"), "round 736: the model answers with a short reply"),
    (
        ("round 736: the recorder stores the reasoning trace", "key"),
        "bssxh 736: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 736: the recorder stores the reasoning trace", "lemon"),
        "csgbq 736: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 736: the recorder stores the reasoning trace", "a"), "round 736: the recorder stores the reasoning trace"),
    (
        ("round 736: the recorder stores the reasoning trace", "zz"),
        "qntmc 736: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 736: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 736: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 736: the recorder stores the reasoning trace", "keyboard"),
        "bssor 736: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 736: the recorder stores the reasoning trace", "AA"),
        "round 736: the recorder stores the reasoning trace",
    ),
    (("round 736: the angel watches the processor run", "key"), "bssxh 736: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 736: the angel watches the processor run", "lemon"), "csgbq 736: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 736: the angel watches the processor run", "a"), "round 736: the angel watches the processor run"),
    (("round 736: the angel watches the processor run", "zz"), "qntmc 736: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 736: the angel watches the processor run", "AgentU"), "ruyaw 736: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 736: the angel watches the processor run", "keyboard"), "bssor 736: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 736: the angel watches the processor run", "AA"), "round 736: the angel watches the processor run"),
    (("round 736: angle of the vector decides the match", "key"), "bssxh 736: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 736: angle of the vector decides the match", "lemon"), "csgbq 736: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 736: angle of the vector decides the match", "a"), "round 736: angle of the vector decides the match"),
    (("round 736: angle of the vector decides the match", "zz"), "qntmc 736: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 736: angle of the vector decides the match", "AgentU"),
        "ruyaw 736: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 736: angle of the vector decides the match", "keyboard"),
        "bssor 736: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 736: angle of the vector decides the match", "AA"), "round 736: angle of the vector decides the match"),
    (
        ("round 736: the candle burns twice as long at night", "key"),
        "bssxh 736: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 736: the candle burns twice as long at night", "lemon"),
        "csgbq 736: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 736: the candle burns twice as long at night", "a"), "round 736: the candle burns twice as long at night"),
    (
        ("round 736: the candle burns twice as long at night", "zz"),
        "qntmc 736: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 736: the candle burns twice as long at night", "AgentU"),
        "ruyaw 736: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 736: the candle burns twice as long at night", "keyboard"),
        "bssor 736: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 736: the candle burns twice as long at night", "AA"),
        "round 736: the candle burns twice as long at night",
    ),
    (("round 736: a mirror of the universe in one line", "key"), "bssxh 736: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 736: a mirror of the universe in one line", "lemon"), "csgbq 736: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 736: a mirror of the universe in one line", "a"), "round 736: a mirror of the universe in one line"),
    (("round 736: a mirror of the universe in one line", "zz"), "qntmc 736: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 736: a mirror of the universe in one line", "AgentU"), "ruyaw 736: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 736: a mirror of the universe in one line", "keyboard"),
        "bssor 736: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 736: a mirror of the universe in one line", "AA"), "round 736: a mirror of the universe in one line"),
    (("round 736: the queue drains before the storm", "key"), "bssxh 736: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 736: the queue drains before the storm", "lemon"), "csgbq 736: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 736: the queue drains before the storm", "a"), "round 736: the queue drains before the storm"),
    (("round 736: the queue drains before the storm", "zz"), "qntmc 736: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 736: the queue drains before the storm", "AgentU"), "ruyaw 736: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 736: the queue drains before the storm", "keyboard"), "bssor 736: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 736: the queue drains before the storm", "AA"), "round 736: the queue drains before the storm"),
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
