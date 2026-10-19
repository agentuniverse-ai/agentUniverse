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
    (("kitten103", "key"), "umrdil103"),
    (("kitten103", "lemon"), "vmfhry103"),
    (("kitten103", "a"), "kitten103"),
    (("kitten103", "zz"), "jhssdm103"),
    (("kitten103", "AgentU"), "koxgxh103"),
    (("kitten103", "keyboard"), "umrusn103"),
    (("kitten103", "AA"), "kitten103"),
    (("sitting103", "key"), "cmrdmlq103"),
    (("sitting103", "lemon"), "dmfhvyk103"),
    (("sitting103", "a"), "sitting103"),
    (("sitting103", "zz"), "rhsshmf103"),
    (("sitting103", "AgentU"), "soxgbhg103"),
    (("sitting103", "keyboard"), "cmruwnx103"),
    (("sitting103", "AA"), "sitting103"),
    (("agent103", "key"), "kkcxx103"),
    (("agent103", "lemon"), "lkqbg103"),
    (("agent103", "a"), "agent103"),
    (("agent103", "zz"), "zfdms103"),
    (("agent103", "AgentU"), "amiam103"),
    (("agent103", "keyboard"), "kkcoh103"),
    (("agent103", "AA"), "agent103"),
    (("angle103", "key"), "krevi103"),
    (("angle103", "lemon"), "lrszr103"),
    (("angle103", "a"), "angle103"),
    (("angle103", "zz"), "zmfkd103"),
    (("angle103", "AgentU"), "atkyx103"),
    (("angle103", "keyboard"), "krems103"),
    (("angle103", "AA"), "angle103"),
    (("universe103", "key"), "ergfipci103"),
    (("universe103", "lemon"), "frujrcwq103"),
    (("universe103", "a"), "universe103"),
    (("universe103", "zz"), "tmhudqrd103"),
    (("universe103", "AgentU"), "utmixlsk103"),
    (("universe103", "keyboard"), "ergwsrjh103"),
    (("universe103", "AA"), "universe103"),
    (("memory103", "key"), "wikyvw103"),
    (("memory103", "lemon"), "xiycej103"),
    (("memory103", "a"), "memory103"),
    (("memory103", "zz"), "ldlnqx103"),
    (("memory103", "AgentU"), "mkqbks103"),
    (("memory103", "keyboard"), "wikpfy103"),
    (("memory103", "AA"), "memory103"),
    (("stream103", "key"), "cxpoek103"),
    (("stream103", "lemon"), "dxdsnx103"),
    (("stream103", "a"), "stream103"),
    (("stream103", "zz"), "rsqdzl103"),
    (("stream103", "AgentU"), "szvrtg103"),
    (("stream103", "keyboard"), "cxpfom103"),
    (("stream103", "AA"), "stream103"),
    (("context103", "key"), "msldivd103"),
    (("context103", "lemon"), "nszhrix103"),
    (("context103", "a"), "context103"),
    (("context103", "zz"), "bnmsdws103"),
    (("context103", "AgentU"), "curgxrt103"),
    (("context103", "keyboard"), "mslusxk103"),
    (("context103", "AA"), "context103"),
    (("knowledge103", "key"), "urmgpcnkc103"),
    (("knowledge103", "lemon"), "vrakyphss103"),
    (("knowledge103", "a"), "knowledge103"),
    (("knowledge103", "zz"), "jmnvkdcfd103"),
    (("knowledge103", "AgentU"), "ktsjeydmi103"),
    (("knowledge103", "keyboard"), "urmxzeujo103"),
    (("knowledge103", "AA"), "knowledge103"),
    (("vector103", "key"), "fiadsp103"),
    (("vector103", "lemon"), "giohbc103"),
    (("vector103", "a"), "vector103"),
    (("vector103", "zz"), "udbsnq103"),
    (("vector103", "AgentU"), "vkgghl103"),
    (("vector103", "keyboard"), "fiaucr103"),
    (("vector103", "AA"), "vector103"),
    (("processor103", "key"), "zvmmiqcsp103"),
    (("processor103", "lemon"), "avaqrdwaf103"),
    (("processor103", "a"), "processor103"),
    (("processor103", "zz"), "oqnbdrrnq103"),
    (("processor103", "AgentU"), "pxspxmsuv103"),
    (("processor103", "keyboard"), "zvmdssjrb103"),
    (("processor103", "AA"), "processor103"),
    (("reasoning103", "key"), "biycslsre103"),
    (("reasoning103", "lemon"), "cimgbymzu103"),
    (("reasoning103", "a"), "reasoning103"),
    (("reasoning103", "zz"), "qdzrnmhmf103"),
    (("reasoning103", "AgentU"), "rkefhhitk103"),
    (("reasoning103", "keyboard"), "biytcnzqq103"),
    (("reasoning103", "AA"), "reasoning103"),
    (("machine103", "key"), "wearmlo103"),
    (("machine103", "lemon"), "xeovvyi103"),
    (("machine103", "a"), "machine103"),
    (("machine103", "zz"), "lzbghmd103"),
    (("machine103", "AgentU"), "mggubhe103"),
    (("machine103", "keyboard"), "weaiwnv103"),
    (("machine103", "AA"), "machine103"),
    (("learning103", "key"), "viybrgxk103"),
    (("learning103", "lemon"), "wimfatrs103"),
    (("learning103", "a"), "learning103"),
    (("learning103", "zz"), "kdzqmhmf103"),
    (("learning103", "AgentU"), "lkeegcnm103"),
    (("learning103", "keyboard"), "viysbiej103"),
    (("learning103", "AA"), "learning103"),
    (("model103", "key"), "wsbop103"),
    (("model103", "lemon"), "xspsy103"),
    (("model103", "a"), "model103"),
    (("model103", "zz"), "lncdk103"),
    (("model103", "AgentU"), "muhre103"),
    (("model103", "keyboard"), "wsbfz103"),
    (("model103", "AA"), "model103"),
    (("token103", "key"), "dsior103"),
    (("token103", "lemon"), "eswsa103"),
    (("token103", "a"), "token103"),
    (("token103", "zz"), "snjdm103"),
    (("token103", "AgentU"), "tuorg103"),
    (("token103", "keyboard"), "dsifb103"),
    (("token103", "AA"), "token103"),
    (("prompt103", "key"), "zvmwtr103"),
    (("prompt103", "lemon"), "avaace103"),
    (("prompt103", "a"), "prompt103"),
    (("prompt103", "zz"), "oqnlos103"),
    (("prompt103", "AgentU"), "pxszin103"),
    (("prompt103", "keyboard"), "zvmndt103"),
    (("prompt103", "AA"), "prompt103"),
    (("session103", "key"), "ciqcmmx103"),
    (("session103", "lemon"), "diegvzr103"),
    (("session103", "a"), "session103"),
    (("session103", "zz"), "rdrrhnm103"),
    (("session103", "AgentU"), "skwfbin103"),
    (("session103", "keyboard"), "ciqtwoe103"),
    (("session103", "AA"), "session103"),
    (("library103", "key"), "vmzbepi103"),
    (("library103", "lemon"), "wmnfncc103"),
    (("library103", "a"), "library103"),
    (("library103", "zz"), "khaqzqx103"),
    (("library103", "AgentU"), "lofetly103"),
    (("library103", "keyboard"), "vmzsorp103"),
    (("library103", "AA"), "library103"),
    (("service103", "key"), "cipfmao103"),
    (("service103", "lemon"), "didjvni103"),
    (("service103", "a"), "service103"),
    (("service103", "zz"), "rdquhbd103"),
    (("service103", "AgentU"), "skvibwe103"),
    (("service103", "keyboard"), "cipwwcv103"),
    (("service103", "AA"), "service103"),
    (("gateway103", "key"), "qeroayi103"),
    (("gateway103", "lemon"), "refsjlc103"),
    (("gateway103", "a"), "gateway103"),
    (("gateway103", "zz"), "fzsdvzx103"),
    (("gateway103", "AgentU"), "ggxrpuy103"),
    (("gateway103", "keyboard"), "qerfkap103"),
    (("gateway103", "AA"), "gateway103"),
    (("storage103", "key"), "cxmbeeo103"),
    (("storage103", "lemon"), "dxafnri103"),
    (("storage103", "a"), "storage103"),
    (("storage103", "zz"), "rsnqzfd103"),
    (("storage103", "AgentU"), "szsetae103"),
    (("storage103", "keyboard"), "cxmsogv103"),
    (("storage103", "AA"), "storage103"),
    (("network103", "key"), "xirgspu103"),
    (("network103", "lemon"), "yifkbco103"),
    (("network103", "a"), "network103"),
    (("network103", "zz"), "mdsvnqj103"),
    (("network103", "AgentU"), "nkxjhlk103"),
    (("network103", "keyboard"), "xirxcrb103"),
    (("network103", "AA"), "network103"),
    (("latency103", "key"), "verorai103"),
    (("latency103", "lemon"), "wefsanc103"),
    (("latency103", "a"), "latency103"),
    (("latency103", "zz"), "kzsdmbx103"),
    (("latency103", "AgentU"), "lgxrgwy103"),
    (("latency103", "keyboard"), "verfbcp103"),
    (("latency103", "AA"), "latency103"),
    (("buffer103", "key"), "lydpip103"),
    (("buffer103", "lemon"), "myrtrc103"),
    (("buffer103", "a"), "buffer103"),
    (("buffer103", "zz"), "ateedq103"),
    (("buffer103", "AgentU"), "bajsxl103"),
    (("buffer103", "keyboard"), "lydgsr103"),
    (("buffer103", "AA"), "buffer103"),
    (("queue103", "key"), "aycei103"),
    (("queue103", "lemon"), "byqir103"),
    (("queue103", "a"), "queue103"),
    (("queue103", "zz"), "ptdtd103"),
    (("queue103", "AgentU"), "qaihx103"),
    (("queue103", "keyboard"), "aycvs103"),
    (("queue103", "AA"), "queue103"),
    (("worker103", "key"), "gspuip103"),
    (("worker103", "lemon"), "hsdyrc103"),
    (("worker103", "a"), "worker103"),
    (("worker103", "zz"), "vnqjdq103"),
    (("worker103", "AgentU"), "wuvxxl103"),
    (("worker103", "keyboard"), "gsplsr103"),
    (("worker103", "AA"), "worker103"),
    (("kernel103", "key"), "uipxij103"),
    (("kernel103", "lemon"), "vidbrw103"),
    (("kernel103", "a"), "kernel103"),
    (("kernel103", "zz"), "jdqmdk103"),
    (("kernel103", "AgentU"), "kkvaxf103"),
    (("kernel103", "keyboard"), "uiposl103"),
    (("kernel103", "AA"), "kernel103"),
    (("signal103", "key"), "cmexej103"),
    (("signal103", "lemon"), "dmsbnw103"),
    (("signal103", "a"), "signal103"),
    (("signal103", "zz"), "rhfmzk103"),
    (("signal103", "AgentU"), "sokatf103"),
    (("signal103", "keyboard"), "cmeool103"),
    (("signal103", "AA"), "signal103"),
    (("packet103", "key"), "zeauir103"),
    (("packet103", "lemon"), "aeoyre103"),
    (("packet103", "a"), "packet103"),
    (("packet103", "zz"), "ozbjds103"),
    (("packet103", "AgentU"), "pggxxn103"),
    (("packet103", "keyboard"), "zealst103"),
    (("packet103", "AA"), "packet103"),
    (("router103", "key"), "bssdip103"),
    (("router103", "lemon"), "csghrc103"),
    (("router103", "a"), "router103"),
    (("router103", "zz"), "qntsdq103"),
    (("router103", "AgentU"), "ruygxl103"),
    (("router103", "keyboard"), "bssusr103"),
    (("router103", "AA"), "router103"),
    (("cluster103", "key"), "mpscxcb103"),
    (("cluster103", "lemon"), "npgggpv103"),
    (("cluster103", "a"), "cluster103"),
    (("cluster103", "zz"), "bktrsdq103"),
    (("cluster103", "AgentU"), "cryfmyr103"),
    (("cluster103", "keyboard"), "mpsthei103"),
    (("cluster103", "AA"), "cluster103"),
    (("mirror103", "key"), "wmpbsp103"),
    (("mirror103", "lemon"), "xmdfbc103"),
    (("mirror103", "a"), "mirror103"),
    (("mirror103", "zz"), "lhqqnq103"),
    (("mirror103", "AgentU"), "movehl103"),
    (("mirror103", "keyboard"), "wmpscr103"),
    (("mirror103", "AA"), "mirror103"),
    (("filter103", "key"), "pmjdip103"),
    (("filter103", "lemon"), "qmxhrc103"),
    (("filter103", "a"), "filter103"),
    (("filter103", "zz"), "ehksdq103"),
    (("filter103", "AgentU"), "fopgxl103"),
    (("filter103", "keyboard"), "pmjusr103"),
    (("filter103", "AA"), "filter103"),
    (("ranking103", "key"), "belumlq103"),
    (("ranking103", "lemon"), "cezyvyk103"),
    (("ranking103", "a"), "ranking103"),
    (("ranking103", "zz"), "qzmjhmf103"),
    (("ranking103", "AgentU"), "rgrxbhg103"),
    (("ranking103", "keyboard"), "bellwnx103"),
    (("ranking103", "AA"), "ranking103"),
    (("encoding103", "key"), "orayhgxk103"),
    (("encoding103", "lemon"), "procqtrs103"),
    (("encoding103", "a"), "encoding103"),
    (("encoding103", "zz"), "dmbnchmf103"),
    (("encoding103", "AgentU"), "etgbwcnm103"),
    (("encoding103", "keyboard"), "orapriej103"),
    (("encoding103", "AA"), "encoding103"),
    (("mapping103", "key"), "wenzmlq103"),
    (("mapping103", "lemon"), "xebdvyk103"),
    (("mapping103", "a"), "mapping103"),
    (("mapping103", "zz"), "lzoohmf103"),
    (("mapping103", "AgentU"), "mgtcbhg103"),
    (("mapping103", "keyboard"), "wenqwnx103"),
    (("mapping103", "AA"), "mapping103"),
    (("record103", "key"), "biayvb103"),
    (("record103", "lemon"), "cioceo103"),
    (("record103", "a"), "record103"),
    (("record103", "zz"), "qdbnqc103"),
    (("record103", "AgentU"), "rkgbkx103"),
    (("record103", "keyboard"), "biapfd103"),
    (("record103", "AA"), "record103"),
    (("candle103", "key"), "melnpc103"),
    (("candle103", "lemon"), "nezryp103"),
    (("candle103", "a"), "candle103"),
    (("candle103", "zz"), "bzmckd103"),
    (("candle103", "AgentU"), "cgrqey103"),
    (("candle103", "keyboard"), "meleze103"),
    (("candle103", "AA"), "candle103"),
    (("thread103", "key"), "dlpoeb103"),
    (("thread103", "lemon"), "eldsno103"),
    (("thread103", "a"), "thread103"),
    (("thread103", "zz"), "sgqdzc103"),
    (("thread103", "AgentU"), "tnvrtx103"),
    (("thread103", "keyboard"), "dlpfod103"),
    (("thread103", "AA"), "thread103"),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 103: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 103: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "a"),
        "round 103: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 103: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 103: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 103: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", "AA"),
        "round 103: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "key"),
        "bssxh 103: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 103: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "a"),
        "round 103: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 103: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 103: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 103: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", "AA"),
        "round 103: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 103: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 103: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "a"),
        "round 103: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 103: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 103: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 103: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", "AA"),
        "round 103: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 103: the processor reads the record then stops", "key"),
        "bssxh 103: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 103: the processor reads the record then stops", "lemon"),
        "csgbq 103: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 103: the processor reads the record then stops", "a"),
        "round 103: the processor reads the record then stops",
    ),
    (
        ("round 103: the processor reads the record then stops", "zz"),
        "qntmc 103: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 103: the processor reads the record then stops", "AgentU"),
        "ruyaw 103: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 103: the processor reads the record then stops", "keyboard"),
        "bssor 103: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 103: the processor reads the record then stops", "AA"),
        "round 103: the processor reads the record then stops",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "key"),
        "bssxh 103: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "lemon"),
        "csgbq 103: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "a"),
        "round 103: a worker pulls the next task from the queue",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "zz"),
        "qntmc 103: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 103: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "keyboard"),
        "bssor 103: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 103: a worker pulls the next task from the queue", "AA"),
        "round 103: a worker pulls the next task from the queue",
    ),
    (
        ("round 103: signals travel through the network layer", "key"),
        "bssxh 103: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 103: signals travel through the network layer", "lemon"),
        "csgbq 103: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 103: signals travel through the network layer", "a"),
        "round 103: signals travel through the network layer",
    ),
    (
        ("round 103: signals travel through the network layer", "zz"),
        "qntmc 103: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 103: signals travel through the network layer", "AgentU"),
        "ruyaw 103: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 103: signals travel through the network layer", "keyboard"),
        "bssor 103: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 103: signals travel through the network layer", "AA"),
        "round 103: signals travel through the network layer",
    ),
    (
        ("round 103: the gateway routes each request by policy", "key"),
        "bssxh 103: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 103: the gateway routes each request by policy", "lemon"),
        "csgbq 103: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 103: the gateway routes each request by policy", "a"),
        "round 103: the gateway routes each request by policy",
    ),
    (
        ("round 103: the gateway routes each request by policy", "zz"),
        "qntmc 103: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 103: the gateway routes each request by policy", "AgentU"),
        "ruyaw 103: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 103: the gateway routes each request by policy", "keyboard"),
        "bssor 103: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 103: the gateway routes each request by policy", "AA"),
        "round 103: the gateway routes each request by policy",
    ),
    (("round 103: memory grows until the buffer is full", "key"), "bssxh 103: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 103: memory grows until the buffer is full", "lemon"), "csgbq 103: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 103: memory grows until the buffer is full", "a"), "round 103: memory grows until the buffer is full"),
    (("round 103: memory grows until the buffer is full", "zz"), "qntmc 103: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 103: memory grows until the buffer is full", "AgentU"),
        "ruyaw 103: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 103: memory grows until the buffer is full", "keyboard"),
        "bssor 103: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 103: memory grows until the buffer is full", "AA"), "round 103: memory grows until the buffer is full"),
    (("round 103: the cluster mirrors every packet twice", "key"), "bssxh 103: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 103: the cluster mirrors every packet twice", "lemon"),
        "csgbq 103: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 103: the cluster mirrors every packet twice", "a"), "round 103: the cluster mirrors every packet twice"),
    (("round 103: the cluster mirrors every packet twice", "zz"), "qntmc 103: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 103: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 103: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 103: the cluster mirrors every packet twice", "keyboard"),
        "bssor 103: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 103: the cluster mirrors every packet twice", "AA"), "round 103: the cluster mirrors every packet twice"),
    (
        ("round 103: ranking uses tokens learned from the corpus", "key"),
        "bssxh 103: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 103: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", "a"),
        "round 103: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 103: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 103: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 103: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", "AA"),
        "round 103: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 103: a long session ends when the candle dies", "key"),
        "bssxh 103: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 103: a long session ends when the candle dies", "lemon"),
        "csgbq 103: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 103: a long session ends when the candle dies", "a"),
        "round 103: a long session ends when the candle dies",
    ),
    (
        ("round 103: a long session ends when the candle dies", "zz"),
        "qntmc 103: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 103: a long session ends when the candle dies", "AgentU"),
        "ruyaw 103: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 103: a long session ends when the candle dies", "keyboard"),
        "bssor 103: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 103: a long session ends when the candle dies", "AA"),
        "round 103: a long session ends when the candle dies",
    ),
    (("round 103: encode the prompt then map the result", "key"), "bssxh 103: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 103: encode the prompt then map the result", "lemon"), "csgbq 103: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 103: encode the prompt then map the result", "a"), "round 103: encode the prompt then map the result"),
    (("round 103: encode the prompt then map the result", "zz"), "qntmc 103: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 103: encode the prompt then map the result", "AgentU"),
        "ruyaw 103: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 103: encode the prompt then map the result", "keyboard"),
        "bssor 103: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 103: encode the prompt then map the result", "AA"), "round 103: encode the prompt then map the result"),
    (("round 103: the kernel wakes the worker at dawn", "key"), "bssxh 103: rri iovlop ukocc xfo ambocb er neux"),
    (("round 103: the kernel wakes the worker at dawn", "lemon"), "csgbq 103: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 103: the kernel wakes the worker at dawn", "a"), "round 103: the kernel wakes the worker at dawn"),
    (("round 103: the kernel wakes the worker at dawn", "zz"), "qntmc 103: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 103: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 103: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 103: the kernel wakes the worker at dawn", "keyboard"), "bssor 103: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 103: the kernel wakes the worker at dawn", "AA"), "round 103: the kernel wakes the worker at dawn"),
    (("round 103: service latency drops after the patch", "key"), "bssxh 103: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 103: service latency drops after the patch", "lemon"), "csgbq 103: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 103: service latency drops after the patch", "a"), "round 103: service latency drops after the patch"),
    (("round 103: service latency drops after the patch", "zz"), "qntmc 103: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 103: service latency drops after the patch", "AgentU"),
        "ruyaw 103: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 103: service latency drops after the patch", "keyboard"),
        "bssor 103: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 103: service latency drops after the patch", "AA"), "round 103: service latency drops after the patch"),
    (
        ("round 103: the library caches every vector it sees", "key"),
        "bssxh 103: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 103: the library caches every vector it sees", "lemon"),
        "csgbq 103: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 103: the library caches every vector it sees", "a"), "round 103: the library caches every vector it sees"),
    (
        ("round 103: the library caches every vector it sees", "zz"),
        "qntmc 103: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 103: the library caches every vector it sees", "AgentU"),
        "ruyaw 103: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 103: the library caches every vector it sees", "keyboard"),
        "bssor 103: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 103: the library caches every vector it sees", "AA"),
        "round 103: the library caches every vector it sees",
    ),
    (("round 103: agents argue then the debate resolves", "key"), "bssxh 103: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 103: agents argue then the debate resolves", "lemon"), "csgbq 103: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 103: agents argue then the debate resolves", "a"), "round 103: agents argue then the debate resolves"),
    (("round 103: agents argue then the debate resolves", "zz"), "qntmc 103: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 103: agents argue then the debate resolves", "AgentU"),
        "ruyaw 103: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 103: agents argue then the debate resolves", "keyboard"),
        "bssor 103: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 103: agents argue then the debate resolves", "AA"), "round 103: agents argue then the debate resolves"),
    (("round 103: the filter keeps only strong matches", "key"), "bssxh 103: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 103: the filter keeps only strong matches", "lemon"), "csgbq 103: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 103: the filter keeps only strong matches", "a"), "round 103: the filter keeps only strong matches"),
    (("round 103: the filter keeps only strong matches", "zz"), "qntmc 103: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 103: the filter keeps only strong matches", "AgentU"), "ruyaw 103: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 103: the filter keeps only strong matches", "keyboard"),
        "bssor 103: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 103: the filter keeps only strong matches", "AA"), "round 103: the filter keeps only strong matches"),
    (("round 103: the model answers with a short reply", "key"), "bssxh 103: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 103: the model answers with a short reply", "lemon"), "csgbq 103: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 103: the model answers with a short reply", "a"), "round 103: the model answers with a short reply"),
    (("round 103: the model answers with a short reply", "zz"), "qntmc 103: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 103: the model answers with a short reply", "AgentU"), "ruyaw 103: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 103: the model answers with a short reply", "keyboard"),
        "bssor 103: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 103: the model answers with a short reply", "AA"), "round 103: the model answers with a short reply"),
    (
        ("round 103: the recorder stores the reasoning trace", "key"),
        "bssxh 103: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 103: the recorder stores the reasoning trace", "lemon"),
        "csgbq 103: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 103: the recorder stores the reasoning trace", "a"), "round 103: the recorder stores the reasoning trace"),
    (
        ("round 103: the recorder stores the reasoning trace", "zz"),
        "qntmc 103: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 103: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 103: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 103: the recorder stores the reasoning trace", "keyboard"),
        "bssor 103: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 103: the recorder stores the reasoning trace", "AA"),
        "round 103: the recorder stores the reasoning trace",
    ),
    (("round 103: the angel watches the processor run", "key"), "bssxh 103: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 103: the angel watches the processor run", "lemon"), "csgbq 103: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 103: the angel watches the processor run", "a"), "round 103: the angel watches the processor run"),
    (("round 103: the angel watches the processor run", "zz"), "qntmc 103: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 103: the angel watches the processor run", "AgentU"), "ruyaw 103: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 103: the angel watches the processor run", "keyboard"), "bssor 103: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 103: the angel watches the processor run", "AA"), "round 103: the angel watches the processor run"),
    (("round 103: angle of the vector decides the match", "key"), "bssxh 103: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 103: angle of the vector decides the match", "lemon"), "csgbq 103: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 103: angle of the vector decides the match", "a"), "round 103: angle of the vector decides the match"),
    (("round 103: angle of the vector decides the match", "zz"), "qntmc 103: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 103: angle of the vector decides the match", "AgentU"),
        "ruyaw 103: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 103: angle of the vector decides the match", "keyboard"),
        "bssor 103: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 103: angle of the vector decides the match", "AA"), "round 103: angle of the vector decides the match"),
    (
        ("round 103: the candle burns twice as long at night", "key"),
        "bssxh 103: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 103: the candle burns twice as long at night", "lemon"),
        "csgbq 103: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 103: the candle burns twice as long at night", "a"), "round 103: the candle burns twice as long at night"),
    (
        ("round 103: the candle burns twice as long at night", "zz"),
        "qntmc 103: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 103: the candle burns twice as long at night", "AgentU"),
        "ruyaw 103: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 103: the candle burns twice as long at night", "keyboard"),
        "bssor 103: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 103: the candle burns twice as long at night", "AA"),
        "round 103: the candle burns twice as long at night",
    ),
    (("round 103: a mirror of the universe in one line", "key"), "bssxh 103: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 103: a mirror of the universe in one line", "lemon"), "csgbq 103: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 103: a mirror of the universe in one line", "a"), "round 103: a mirror of the universe in one line"),
    (("round 103: a mirror of the universe in one line", "zz"), "qntmc 103: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 103: a mirror of the universe in one line", "AgentU"), "ruyaw 103: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 103: a mirror of the universe in one line", "keyboard"),
        "bssor 103: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 103: a mirror of the universe in one line", "AA"), "round 103: a mirror of the universe in one line"),
    (("round 103: the queue drains before the storm", "key"), "bssxh 103: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 103: the queue drains before the storm", "lemon"), "csgbq 103: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 103: the queue drains before the storm", "a"), "round 103: the queue drains before the storm"),
    (("round 103: the queue drains before the storm", "zz"), "qntmc 103: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 103: the queue drains before the storm", "AgentU"), "ruyaw 103: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 103: the queue drains before the storm", "keyboard"), "bssor 103: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 103: the queue drains before the storm", "AA"), "round 103: the queue drains before the storm"),
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
