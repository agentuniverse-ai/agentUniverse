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
    (("kitten187", "key"), "umrdil187"),
    (("kitten187", "lemon"), "vmfhry187"),
    (("kitten187", "a"), "kitten187"),
    (("kitten187", "zz"), "jhssdm187"),
    (("kitten187", "AgentU"), "koxgxh187"),
    (("kitten187", "keyboard"), "umrusn187"),
    (("kitten187", "AA"), "kitten187"),
    (("sitting187", "key"), "cmrdmlq187"),
    (("sitting187", "lemon"), "dmfhvyk187"),
    (("sitting187", "a"), "sitting187"),
    (("sitting187", "zz"), "rhsshmf187"),
    (("sitting187", "AgentU"), "soxgbhg187"),
    (("sitting187", "keyboard"), "cmruwnx187"),
    (("sitting187", "AA"), "sitting187"),
    (("agent187", "key"), "kkcxx187"),
    (("agent187", "lemon"), "lkqbg187"),
    (("agent187", "a"), "agent187"),
    (("agent187", "zz"), "zfdms187"),
    (("agent187", "AgentU"), "amiam187"),
    (("agent187", "keyboard"), "kkcoh187"),
    (("agent187", "AA"), "agent187"),
    (("angle187", "key"), "krevi187"),
    (("angle187", "lemon"), "lrszr187"),
    (("angle187", "a"), "angle187"),
    (("angle187", "zz"), "zmfkd187"),
    (("angle187", "AgentU"), "atkyx187"),
    (("angle187", "keyboard"), "krems187"),
    (("angle187", "AA"), "angle187"),
    (("universe187", "key"), "ergfipci187"),
    (("universe187", "lemon"), "frujrcwq187"),
    (("universe187", "a"), "universe187"),
    (("universe187", "zz"), "tmhudqrd187"),
    (("universe187", "AgentU"), "utmixlsk187"),
    (("universe187", "keyboard"), "ergwsrjh187"),
    (("universe187", "AA"), "universe187"),
    (("memory187", "key"), "wikyvw187"),
    (("memory187", "lemon"), "xiycej187"),
    (("memory187", "a"), "memory187"),
    (("memory187", "zz"), "ldlnqx187"),
    (("memory187", "AgentU"), "mkqbks187"),
    (("memory187", "keyboard"), "wikpfy187"),
    (("memory187", "AA"), "memory187"),
    (("stream187", "key"), "cxpoek187"),
    (("stream187", "lemon"), "dxdsnx187"),
    (("stream187", "a"), "stream187"),
    (("stream187", "zz"), "rsqdzl187"),
    (("stream187", "AgentU"), "szvrtg187"),
    (("stream187", "keyboard"), "cxpfom187"),
    (("stream187", "AA"), "stream187"),
    (("context187", "key"), "msldivd187"),
    (("context187", "lemon"), "nszhrix187"),
    (("context187", "a"), "context187"),
    (("context187", "zz"), "bnmsdws187"),
    (("context187", "AgentU"), "curgxrt187"),
    (("context187", "keyboard"), "mslusxk187"),
    (("context187", "AA"), "context187"),
    (("knowledge187", "key"), "urmgpcnkc187"),
    (("knowledge187", "lemon"), "vrakyphss187"),
    (("knowledge187", "a"), "knowledge187"),
    (("knowledge187", "zz"), "jmnvkdcfd187"),
    (("knowledge187", "AgentU"), "ktsjeydmi187"),
    (("knowledge187", "keyboard"), "urmxzeujo187"),
    (("knowledge187", "AA"), "knowledge187"),
    (("vector187", "key"), "fiadsp187"),
    (("vector187", "lemon"), "giohbc187"),
    (("vector187", "a"), "vector187"),
    (("vector187", "zz"), "udbsnq187"),
    (("vector187", "AgentU"), "vkgghl187"),
    (("vector187", "keyboard"), "fiaucr187"),
    (("vector187", "AA"), "vector187"),
    (("processor187", "key"), "zvmmiqcsp187"),
    (("processor187", "lemon"), "avaqrdwaf187"),
    (("processor187", "a"), "processor187"),
    (("processor187", "zz"), "oqnbdrrnq187"),
    (("processor187", "AgentU"), "pxspxmsuv187"),
    (("processor187", "keyboard"), "zvmdssjrb187"),
    (("processor187", "AA"), "processor187"),
    (("reasoning187", "key"), "biycslsre187"),
    (("reasoning187", "lemon"), "cimgbymzu187"),
    (("reasoning187", "a"), "reasoning187"),
    (("reasoning187", "zz"), "qdzrnmhmf187"),
    (("reasoning187", "AgentU"), "rkefhhitk187"),
    (("reasoning187", "keyboard"), "biytcnzqq187"),
    (("reasoning187", "AA"), "reasoning187"),
    (("machine187", "key"), "wearmlo187"),
    (("machine187", "lemon"), "xeovvyi187"),
    (("machine187", "a"), "machine187"),
    (("machine187", "zz"), "lzbghmd187"),
    (("machine187", "AgentU"), "mggubhe187"),
    (("machine187", "keyboard"), "weaiwnv187"),
    (("machine187", "AA"), "machine187"),
    (("learning187", "key"), "viybrgxk187"),
    (("learning187", "lemon"), "wimfatrs187"),
    (("learning187", "a"), "learning187"),
    (("learning187", "zz"), "kdzqmhmf187"),
    (("learning187", "AgentU"), "lkeegcnm187"),
    (("learning187", "keyboard"), "viysbiej187"),
    (("learning187", "AA"), "learning187"),
    (("model187", "key"), "wsbop187"),
    (("model187", "lemon"), "xspsy187"),
    (("model187", "a"), "model187"),
    (("model187", "zz"), "lncdk187"),
    (("model187", "AgentU"), "muhre187"),
    (("model187", "keyboard"), "wsbfz187"),
    (("model187", "AA"), "model187"),
    (("token187", "key"), "dsior187"),
    (("token187", "lemon"), "eswsa187"),
    (("token187", "a"), "token187"),
    (("token187", "zz"), "snjdm187"),
    (("token187", "AgentU"), "tuorg187"),
    (("token187", "keyboard"), "dsifb187"),
    (("token187", "AA"), "token187"),
    (("prompt187", "key"), "zvmwtr187"),
    (("prompt187", "lemon"), "avaace187"),
    (("prompt187", "a"), "prompt187"),
    (("prompt187", "zz"), "oqnlos187"),
    (("prompt187", "AgentU"), "pxszin187"),
    (("prompt187", "keyboard"), "zvmndt187"),
    (("prompt187", "AA"), "prompt187"),
    (("session187", "key"), "ciqcmmx187"),
    (("session187", "lemon"), "diegvzr187"),
    (("session187", "a"), "session187"),
    (("session187", "zz"), "rdrrhnm187"),
    (("session187", "AgentU"), "skwfbin187"),
    (("session187", "keyboard"), "ciqtwoe187"),
    (("session187", "AA"), "session187"),
    (("library187", "key"), "vmzbepi187"),
    (("library187", "lemon"), "wmnfncc187"),
    (("library187", "a"), "library187"),
    (("library187", "zz"), "khaqzqx187"),
    (("library187", "AgentU"), "lofetly187"),
    (("library187", "keyboard"), "vmzsorp187"),
    (("library187", "AA"), "library187"),
    (("service187", "key"), "cipfmao187"),
    (("service187", "lemon"), "didjvni187"),
    (("service187", "a"), "service187"),
    (("service187", "zz"), "rdquhbd187"),
    (("service187", "AgentU"), "skvibwe187"),
    (("service187", "keyboard"), "cipwwcv187"),
    (("service187", "AA"), "service187"),
    (("gateway187", "key"), "qeroayi187"),
    (("gateway187", "lemon"), "refsjlc187"),
    (("gateway187", "a"), "gateway187"),
    (("gateway187", "zz"), "fzsdvzx187"),
    (("gateway187", "AgentU"), "ggxrpuy187"),
    (("gateway187", "keyboard"), "qerfkap187"),
    (("gateway187", "AA"), "gateway187"),
    (("storage187", "key"), "cxmbeeo187"),
    (("storage187", "lemon"), "dxafnri187"),
    (("storage187", "a"), "storage187"),
    (("storage187", "zz"), "rsnqzfd187"),
    (("storage187", "AgentU"), "szsetae187"),
    (("storage187", "keyboard"), "cxmsogv187"),
    (("storage187", "AA"), "storage187"),
    (("network187", "key"), "xirgspu187"),
    (("network187", "lemon"), "yifkbco187"),
    (("network187", "a"), "network187"),
    (("network187", "zz"), "mdsvnqj187"),
    (("network187", "AgentU"), "nkxjhlk187"),
    (("network187", "keyboard"), "xirxcrb187"),
    (("network187", "AA"), "network187"),
    (("latency187", "key"), "verorai187"),
    (("latency187", "lemon"), "wefsanc187"),
    (("latency187", "a"), "latency187"),
    (("latency187", "zz"), "kzsdmbx187"),
    (("latency187", "AgentU"), "lgxrgwy187"),
    (("latency187", "keyboard"), "verfbcp187"),
    (("latency187", "AA"), "latency187"),
    (("buffer187", "key"), "lydpip187"),
    (("buffer187", "lemon"), "myrtrc187"),
    (("buffer187", "a"), "buffer187"),
    (("buffer187", "zz"), "ateedq187"),
    (("buffer187", "AgentU"), "bajsxl187"),
    (("buffer187", "keyboard"), "lydgsr187"),
    (("buffer187", "AA"), "buffer187"),
    (("queue187", "key"), "aycei187"),
    (("queue187", "lemon"), "byqir187"),
    (("queue187", "a"), "queue187"),
    (("queue187", "zz"), "ptdtd187"),
    (("queue187", "AgentU"), "qaihx187"),
    (("queue187", "keyboard"), "aycvs187"),
    (("queue187", "AA"), "queue187"),
    (("worker187", "key"), "gspuip187"),
    (("worker187", "lemon"), "hsdyrc187"),
    (("worker187", "a"), "worker187"),
    (("worker187", "zz"), "vnqjdq187"),
    (("worker187", "AgentU"), "wuvxxl187"),
    (("worker187", "keyboard"), "gsplsr187"),
    (("worker187", "AA"), "worker187"),
    (("kernel187", "key"), "uipxij187"),
    (("kernel187", "lemon"), "vidbrw187"),
    (("kernel187", "a"), "kernel187"),
    (("kernel187", "zz"), "jdqmdk187"),
    (("kernel187", "AgentU"), "kkvaxf187"),
    (("kernel187", "keyboard"), "uiposl187"),
    (("kernel187", "AA"), "kernel187"),
    (("signal187", "key"), "cmexej187"),
    (("signal187", "lemon"), "dmsbnw187"),
    (("signal187", "a"), "signal187"),
    (("signal187", "zz"), "rhfmzk187"),
    (("signal187", "AgentU"), "sokatf187"),
    (("signal187", "keyboard"), "cmeool187"),
    (("signal187", "AA"), "signal187"),
    (("packet187", "key"), "zeauir187"),
    (("packet187", "lemon"), "aeoyre187"),
    (("packet187", "a"), "packet187"),
    (("packet187", "zz"), "ozbjds187"),
    (("packet187", "AgentU"), "pggxxn187"),
    (("packet187", "keyboard"), "zealst187"),
    (("packet187", "AA"), "packet187"),
    (("router187", "key"), "bssdip187"),
    (("router187", "lemon"), "csghrc187"),
    (("router187", "a"), "router187"),
    (("router187", "zz"), "qntsdq187"),
    (("router187", "AgentU"), "ruygxl187"),
    (("router187", "keyboard"), "bssusr187"),
    (("router187", "AA"), "router187"),
    (("cluster187", "key"), "mpscxcb187"),
    (("cluster187", "lemon"), "npgggpv187"),
    (("cluster187", "a"), "cluster187"),
    (("cluster187", "zz"), "bktrsdq187"),
    (("cluster187", "AgentU"), "cryfmyr187"),
    (("cluster187", "keyboard"), "mpsthei187"),
    (("cluster187", "AA"), "cluster187"),
    (("mirror187", "key"), "wmpbsp187"),
    (("mirror187", "lemon"), "xmdfbc187"),
    (("mirror187", "a"), "mirror187"),
    (("mirror187", "zz"), "lhqqnq187"),
    (("mirror187", "AgentU"), "movehl187"),
    (("mirror187", "keyboard"), "wmpscr187"),
    (("mirror187", "AA"), "mirror187"),
    (("filter187", "key"), "pmjdip187"),
    (("filter187", "lemon"), "qmxhrc187"),
    (("filter187", "a"), "filter187"),
    (("filter187", "zz"), "ehksdq187"),
    (("filter187", "AgentU"), "fopgxl187"),
    (("filter187", "keyboard"), "pmjusr187"),
    (("filter187", "AA"), "filter187"),
    (("ranking187", "key"), "belumlq187"),
    (("ranking187", "lemon"), "cezyvyk187"),
    (("ranking187", "a"), "ranking187"),
    (("ranking187", "zz"), "qzmjhmf187"),
    (("ranking187", "AgentU"), "rgrxbhg187"),
    (("ranking187", "keyboard"), "bellwnx187"),
    (("ranking187", "AA"), "ranking187"),
    (("encoding187", "key"), "orayhgxk187"),
    (("encoding187", "lemon"), "procqtrs187"),
    (("encoding187", "a"), "encoding187"),
    (("encoding187", "zz"), "dmbnchmf187"),
    (("encoding187", "AgentU"), "etgbwcnm187"),
    (("encoding187", "keyboard"), "orapriej187"),
    (("encoding187", "AA"), "encoding187"),
    (("mapping187", "key"), "wenzmlq187"),
    (("mapping187", "lemon"), "xebdvyk187"),
    (("mapping187", "a"), "mapping187"),
    (("mapping187", "zz"), "lzoohmf187"),
    (("mapping187", "AgentU"), "mgtcbhg187"),
    (("mapping187", "keyboard"), "wenqwnx187"),
    (("mapping187", "AA"), "mapping187"),
    (("record187", "key"), "biayvb187"),
    (("record187", "lemon"), "cioceo187"),
    (("record187", "a"), "record187"),
    (("record187", "zz"), "qdbnqc187"),
    (("record187", "AgentU"), "rkgbkx187"),
    (("record187", "keyboard"), "biapfd187"),
    (("record187", "AA"), "record187"),
    (("candle187", "key"), "melnpc187"),
    (("candle187", "lemon"), "nezryp187"),
    (("candle187", "a"), "candle187"),
    (("candle187", "zz"), "bzmckd187"),
    (("candle187", "AgentU"), "cgrqey187"),
    (("candle187", "keyboard"), "meleze187"),
    (("candle187", "AA"), "candle187"),
    (("thread187", "key"), "dlpoeb187"),
    (("thread187", "lemon"), "eldsno187"),
    (("thread187", "a"), "thread187"),
    (("thread187", "zz"), "sgqdzc187"),
    (("thread187", "AgentU"), "tnvrtx187"),
    (("thread187", "keyboard"), "dlpfod187"),
    (("thread187", "AA"), "thread187"),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 187: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 187: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "a"),
        "round 187: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 187: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 187: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 187: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", "AA"),
        "round 187: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "key"),
        "bssxh 187: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 187: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "a"),
        "round 187: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 187: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 187: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 187: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", "AA"),
        "round 187: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 187: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 187: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "a"),
        "round 187: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 187: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 187: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 187: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", "AA"),
        "round 187: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 187: the processor reads the record then stops", "key"),
        "bssxh 187: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 187: the processor reads the record then stops", "lemon"),
        "csgbq 187: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 187: the processor reads the record then stops", "a"),
        "round 187: the processor reads the record then stops",
    ),
    (
        ("round 187: the processor reads the record then stops", "zz"),
        "qntmc 187: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 187: the processor reads the record then stops", "AgentU"),
        "ruyaw 187: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 187: the processor reads the record then stops", "keyboard"),
        "bssor 187: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 187: the processor reads the record then stops", "AA"),
        "round 187: the processor reads the record then stops",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "key"),
        "bssxh 187: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "lemon"),
        "csgbq 187: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "a"),
        "round 187: a worker pulls the next task from the queue",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "zz"),
        "qntmc 187: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 187: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "keyboard"),
        "bssor 187: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 187: a worker pulls the next task from the queue", "AA"),
        "round 187: a worker pulls the next task from the queue",
    ),
    (
        ("round 187: signals travel through the network layer", "key"),
        "bssxh 187: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 187: signals travel through the network layer", "lemon"),
        "csgbq 187: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 187: signals travel through the network layer", "a"),
        "round 187: signals travel through the network layer",
    ),
    (
        ("round 187: signals travel through the network layer", "zz"),
        "qntmc 187: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 187: signals travel through the network layer", "AgentU"),
        "ruyaw 187: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 187: signals travel through the network layer", "keyboard"),
        "bssor 187: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 187: signals travel through the network layer", "AA"),
        "round 187: signals travel through the network layer",
    ),
    (
        ("round 187: the gateway routes each request by policy", "key"),
        "bssxh 187: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 187: the gateway routes each request by policy", "lemon"),
        "csgbq 187: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 187: the gateway routes each request by policy", "a"),
        "round 187: the gateway routes each request by policy",
    ),
    (
        ("round 187: the gateway routes each request by policy", "zz"),
        "qntmc 187: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 187: the gateway routes each request by policy", "AgentU"),
        "ruyaw 187: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 187: the gateway routes each request by policy", "keyboard"),
        "bssor 187: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 187: the gateway routes each request by policy", "AA"),
        "round 187: the gateway routes each request by policy",
    ),
    (("round 187: memory grows until the buffer is full", "key"), "bssxh 187: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 187: memory grows until the buffer is full", "lemon"), "csgbq 187: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 187: memory grows until the buffer is full", "a"), "round 187: memory grows until the buffer is full"),
    (("round 187: memory grows until the buffer is full", "zz"), "qntmc 187: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 187: memory grows until the buffer is full", "AgentU"),
        "ruyaw 187: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 187: memory grows until the buffer is full", "keyboard"),
        "bssor 187: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 187: memory grows until the buffer is full", "AA"), "round 187: memory grows until the buffer is full"),
    (("round 187: the cluster mirrors every packet twice", "key"), "bssxh 187: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 187: the cluster mirrors every packet twice", "lemon"),
        "csgbq 187: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 187: the cluster mirrors every packet twice", "a"), "round 187: the cluster mirrors every packet twice"),
    (("round 187: the cluster mirrors every packet twice", "zz"), "qntmc 187: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 187: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 187: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 187: the cluster mirrors every packet twice", "keyboard"),
        "bssor 187: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 187: the cluster mirrors every packet twice", "AA"), "round 187: the cluster mirrors every packet twice"),
    (
        ("round 187: ranking uses tokens learned from the corpus", "key"),
        "bssxh 187: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 187: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", "a"),
        "round 187: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 187: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 187: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 187: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", "AA"),
        "round 187: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 187: a long session ends when the candle dies", "key"),
        "bssxh 187: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 187: a long session ends when the candle dies", "lemon"),
        "csgbq 187: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 187: a long session ends when the candle dies", "a"),
        "round 187: a long session ends when the candle dies",
    ),
    (
        ("round 187: a long session ends when the candle dies", "zz"),
        "qntmc 187: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 187: a long session ends when the candle dies", "AgentU"),
        "ruyaw 187: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 187: a long session ends when the candle dies", "keyboard"),
        "bssor 187: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 187: a long session ends when the candle dies", "AA"),
        "round 187: a long session ends when the candle dies",
    ),
    (("round 187: encode the prompt then map the result", "key"), "bssxh 187: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 187: encode the prompt then map the result", "lemon"), "csgbq 187: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 187: encode the prompt then map the result", "a"), "round 187: encode the prompt then map the result"),
    (("round 187: encode the prompt then map the result", "zz"), "qntmc 187: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 187: encode the prompt then map the result", "AgentU"),
        "ruyaw 187: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 187: encode the prompt then map the result", "keyboard"),
        "bssor 187: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 187: encode the prompt then map the result", "AA"), "round 187: encode the prompt then map the result"),
    (("round 187: the kernel wakes the worker at dawn", "key"), "bssxh 187: rri iovlop ukocc xfo ambocb er neux"),
    (("round 187: the kernel wakes the worker at dawn", "lemon"), "csgbq 187: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 187: the kernel wakes the worker at dawn", "a"), "round 187: the kernel wakes the worker at dawn"),
    (("round 187: the kernel wakes the worker at dawn", "zz"), "qntmc 187: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 187: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 187: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 187: the kernel wakes the worker at dawn", "keyboard"), "bssor 187: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 187: the kernel wakes the worker at dawn", "AA"), "round 187: the kernel wakes the worker at dawn"),
    (("round 187: service latency drops after the patch", "key"), "bssxh 187: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 187: service latency drops after the patch", "lemon"), "csgbq 187: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 187: service latency drops after the patch", "a"), "round 187: service latency drops after the patch"),
    (("round 187: service latency drops after the patch", "zz"), "qntmc 187: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 187: service latency drops after the patch", "AgentU"),
        "ruyaw 187: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 187: service latency drops after the patch", "keyboard"),
        "bssor 187: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 187: service latency drops after the patch", "AA"), "round 187: service latency drops after the patch"),
    (
        ("round 187: the library caches every vector it sees", "key"),
        "bssxh 187: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 187: the library caches every vector it sees", "lemon"),
        "csgbq 187: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 187: the library caches every vector it sees", "a"), "round 187: the library caches every vector it sees"),
    (
        ("round 187: the library caches every vector it sees", "zz"),
        "qntmc 187: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 187: the library caches every vector it sees", "AgentU"),
        "ruyaw 187: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 187: the library caches every vector it sees", "keyboard"),
        "bssor 187: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 187: the library caches every vector it sees", "AA"),
        "round 187: the library caches every vector it sees",
    ),
    (("round 187: agents argue then the debate resolves", "key"), "bssxh 187: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 187: agents argue then the debate resolves", "lemon"), "csgbq 187: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 187: agents argue then the debate resolves", "a"), "round 187: agents argue then the debate resolves"),
    (("round 187: agents argue then the debate resolves", "zz"), "qntmc 187: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 187: agents argue then the debate resolves", "AgentU"),
        "ruyaw 187: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 187: agents argue then the debate resolves", "keyboard"),
        "bssor 187: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 187: agents argue then the debate resolves", "AA"), "round 187: agents argue then the debate resolves"),
    (("round 187: the filter keeps only strong matches", "key"), "bssxh 187: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 187: the filter keeps only strong matches", "lemon"), "csgbq 187: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 187: the filter keeps only strong matches", "a"), "round 187: the filter keeps only strong matches"),
    (("round 187: the filter keeps only strong matches", "zz"), "qntmc 187: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 187: the filter keeps only strong matches", "AgentU"), "ruyaw 187: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 187: the filter keeps only strong matches", "keyboard"),
        "bssor 187: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 187: the filter keeps only strong matches", "AA"), "round 187: the filter keeps only strong matches"),
    (("round 187: the model answers with a short reply", "key"), "bssxh 187: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 187: the model answers with a short reply", "lemon"), "csgbq 187: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 187: the model answers with a short reply", "a"), "round 187: the model answers with a short reply"),
    (("round 187: the model answers with a short reply", "zz"), "qntmc 187: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 187: the model answers with a short reply", "AgentU"), "ruyaw 187: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 187: the model answers with a short reply", "keyboard"),
        "bssor 187: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 187: the model answers with a short reply", "AA"), "round 187: the model answers with a short reply"),
    (
        ("round 187: the recorder stores the reasoning trace", "key"),
        "bssxh 187: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 187: the recorder stores the reasoning trace", "lemon"),
        "csgbq 187: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 187: the recorder stores the reasoning trace", "a"), "round 187: the recorder stores the reasoning trace"),
    (
        ("round 187: the recorder stores the reasoning trace", "zz"),
        "qntmc 187: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 187: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 187: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 187: the recorder stores the reasoning trace", "keyboard"),
        "bssor 187: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 187: the recorder stores the reasoning trace", "AA"),
        "round 187: the recorder stores the reasoning trace",
    ),
    (("round 187: the angel watches the processor run", "key"), "bssxh 187: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 187: the angel watches the processor run", "lemon"), "csgbq 187: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 187: the angel watches the processor run", "a"), "round 187: the angel watches the processor run"),
    (("round 187: the angel watches the processor run", "zz"), "qntmc 187: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 187: the angel watches the processor run", "AgentU"), "ruyaw 187: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 187: the angel watches the processor run", "keyboard"), "bssor 187: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 187: the angel watches the processor run", "AA"), "round 187: the angel watches the processor run"),
    (("round 187: angle of the vector decides the match", "key"), "bssxh 187: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 187: angle of the vector decides the match", "lemon"), "csgbq 187: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 187: angle of the vector decides the match", "a"), "round 187: angle of the vector decides the match"),
    (("round 187: angle of the vector decides the match", "zz"), "qntmc 187: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 187: angle of the vector decides the match", "AgentU"),
        "ruyaw 187: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 187: angle of the vector decides the match", "keyboard"),
        "bssor 187: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 187: angle of the vector decides the match", "AA"), "round 187: angle of the vector decides the match"),
    (
        ("round 187: the candle burns twice as long at night", "key"),
        "bssxh 187: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 187: the candle burns twice as long at night", "lemon"),
        "csgbq 187: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 187: the candle burns twice as long at night", "a"), "round 187: the candle burns twice as long at night"),
    (
        ("round 187: the candle burns twice as long at night", "zz"),
        "qntmc 187: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 187: the candle burns twice as long at night", "AgentU"),
        "ruyaw 187: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 187: the candle burns twice as long at night", "keyboard"),
        "bssor 187: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 187: the candle burns twice as long at night", "AA"),
        "round 187: the candle burns twice as long at night",
    ),
    (("round 187: a mirror of the universe in one line", "key"), "bssxh 187: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 187: a mirror of the universe in one line", "lemon"), "csgbq 187: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 187: a mirror of the universe in one line", "a"), "round 187: a mirror of the universe in one line"),
    (("round 187: a mirror of the universe in one line", "zz"), "qntmc 187: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 187: a mirror of the universe in one line", "AgentU"), "ruyaw 187: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 187: a mirror of the universe in one line", "keyboard"),
        "bssor 187: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 187: a mirror of the universe in one line", "AA"), "round 187: a mirror of the universe in one line"),
    (("round 187: the queue drains before the storm", "key"), "bssxh 187: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 187: the queue drains before the storm", "lemon"), "csgbq 187: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 187: the queue drains before the storm", "a"), "round 187: the queue drains before the storm"),
    (("round 187: the queue drains before the storm", "zz"), "qntmc 187: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 187: the queue drains before the storm", "AgentU"), "ruyaw 187: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 187: the queue drains before the storm", "keyboard"), "bssor 187: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 187: the queue drains before the storm", "AA"), "round 187: the queue drains before the storm"),
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
