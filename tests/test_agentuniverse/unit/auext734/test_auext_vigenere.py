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
    (("kitten734", "key"), "umrdil734"),
    (("kitten734", "lemon"), "vmfhry734"),
    (("kitten734", "a"), "kitten734"),
    (("kitten734", "zz"), "jhssdm734"),
    (("kitten734", "AgentU"), "koxgxh734"),
    (("kitten734", "keyboard"), "umrusn734"),
    (("kitten734", "AA"), "kitten734"),
    (("sitting734", "key"), "cmrdmlq734"),
    (("sitting734", "lemon"), "dmfhvyk734"),
    (("sitting734", "a"), "sitting734"),
    (("sitting734", "zz"), "rhsshmf734"),
    (("sitting734", "AgentU"), "soxgbhg734"),
    (("sitting734", "keyboard"), "cmruwnx734"),
    (("sitting734", "AA"), "sitting734"),
    (("agent734", "key"), "kkcxx734"),
    (("agent734", "lemon"), "lkqbg734"),
    (("agent734", "a"), "agent734"),
    (("agent734", "zz"), "zfdms734"),
    (("agent734", "AgentU"), "amiam734"),
    (("agent734", "keyboard"), "kkcoh734"),
    (("agent734", "AA"), "agent734"),
    (("angle734", "key"), "krevi734"),
    (("angle734", "lemon"), "lrszr734"),
    (("angle734", "a"), "angle734"),
    (("angle734", "zz"), "zmfkd734"),
    (("angle734", "AgentU"), "atkyx734"),
    (("angle734", "keyboard"), "krems734"),
    (("angle734", "AA"), "angle734"),
    (("universe734", "key"), "ergfipci734"),
    (("universe734", "lemon"), "frujrcwq734"),
    (("universe734", "a"), "universe734"),
    (("universe734", "zz"), "tmhudqrd734"),
    (("universe734", "AgentU"), "utmixlsk734"),
    (("universe734", "keyboard"), "ergwsrjh734"),
    (("universe734", "AA"), "universe734"),
    (("memory734", "key"), "wikyvw734"),
    (("memory734", "lemon"), "xiycej734"),
    (("memory734", "a"), "memory734"),
    (("memory734", "zz"), "ldlnqx734"),
    (("memory734", "AgentU"), "mkqbks734"),
    (("memory734", "keyboard"), "wikpfy734"),
    (("memory734", "AA"), "memory734"),
    (("stream734", "key"), "cxpoek734"),
    (("stream734", "lemon"), "dxdsnx734"),
    (("stream734", "a"), "stream734"),
    (("stream734", "zz"), "rsqdzl734"),
    (("stream734", "AgentU"), "szvrtg734"),
    (("stream734", "keyboard"), "cxpfom734"),
    (("stream734", "AA"), "stream734"),
    (("context734", "key"), "msldivd734"),
    (("context734", "lemon"), "nszhrix734"),
    (("context734", "a"), "context734"),
    (("context734", "zz"), "bnmsdws734"),
    (("context734", "AgentU"), "curgxrt734"),
    (("context734", "keyboard"), "mslusxk734"),
    (("context734", "AA"), "context734"),
    (("knowledge734", "key"), "urmgpcnkc734"),
    (("knowledge734", "lemon"), "vrakyphss734"),
    (("knowledge734", "a"), "knowledge734"),
    (("knowledge734", "zz"), "jmnvkdcfd734"),
    (("knowledge734", "AgentU"), "ktsjeydmi734"),
    (("knowledge734", "keyboard"), "urmxzeujo734"),
    (("knowledge734", "AA"), "knowledge734"),
    (("vector734", "key"), "fiadsp734"),
    (("vector734", "lemon"), "giohbc734"),
    (("vector734", "a"), "vector734"),
    (("vector734", "zz"), "udbsnq734"),
    (("vector734", "AgentU"), "vkgghl734"),
    (("vector734", "keyboard"), "fiaucr734"),
    (("vector734", "AA"), "vector734"),
    (("processor734", "key"), "zvmmiqcsp734"),
    (("processor734", "lemon"), "avaqrdwaf734"),
    (("processor734", "a"), "processor734"),
    (("processor734", "zz"), "oqnbdrrnq734"),
    (("processor734", "AgentU"), "pxspxmsuv734"),
    (("processor734", "keyboard"), "zvmdssjrb734"),
    (("processor734", "AA"), "processor734"),
    (("reasoning734", "key"), "biycslsre734"),
    (("reasoning734", "lemon"), "cimgbymzu734"),
    (("reasoning734", "a"), "reasoning734"),
    (("reasoning734", "zz"), "qdzrnmhmf734"),
    (("reasoning734", "AgentU"), "rkefhhitk734"),
    (("reasoning734", "keyboard"), "biytcnzqq734"),
    (("reasoning734", "AA"), "reasoning734"),
    (("machine734", "key"), "wearmlo734"),
    (("machine734", "lemon"), "xeovvyi734"),
    (("machine734", "a"), "machine734"),
    (("machine734", "zz"), "lzbghmd734"),
    (("machine734", "AgentU"), "mggubhe734"),
    (("machine734", "keyboard"), "weaiwnv734"),
    (("machine734", "AA"), "machine734"),
    (("learning734", "key"), "viybrgxk734"),
    (("learning734", "lemon"), "wimfatrs734"),
    (("learning734", "a"), "learning734"),
    (("learning734", "zz"), "kdzqmhmf734"),
    (("learning734", "AgentU"), "lkeegcnm734"),
    (("learning734", "keyboard"), "viysbiej734"),
    (("learning734", "AA"), "learning734"),
    (("model734", "key"), "wsbop734"),
    (("model734", "lemon"), "xspsy734"),
    (("model734", "a"), "model734"),
    (("model734", "zz"), "lncdk734"),
    (("model734", "AgentU"), "muhre734"),
    (("model734", "keyboard"), "wsbfz734"),
    (("model734", "AA"), "model734"),
    (("token734", "key"), "dsior734"),
    (("token734", "lemon"), "eswsa734"),
    (("token734", "a"), "token734"),
    (("token734", "zz"), "snjdm734"),
    (("token734", "AgentU"), "tuorg734"),
    (("token734", "keyboard"), "dsifb734"),
    (("token734", "AA"), "token734"),
    (("prompt734", "key"), "zvmwtr734"),
    (("prompt734", "lemon"), "avaace734"),
    (("prompt734", "a"), "prompt734"),
    (("prompt734", "zz"), "oqnlos734"),
    (("prompt734", "AgentU"), "pxszin734"),
    (("prompt734", "keyboard"), "zvmndt734"),
    (("prompt734", "AA"), "prompt734"),
    (("session734", "key"), "ciqcmmx734"),
    (("session734", "lemon"), "diegvzr734"),
    (("session734", "a"), "session734"),
    (("session734", "zz"), "rdrrhnm734"),
    (("session734", "AgentU"), "skwfbin734"),
    (("session734", "keyboard"), "ciqtwoe734"),
    (("session734", "AA"), "session734"),
    (("library734", "key"), "vmzbepi734"),
    (("library734", "lemon"), "wmnfncc734"),
    (("library734", "a"), "library734"),
    (("library734", "zz"), "khaqzqx734"),
    (("library734", "AgentU"), "lofetly734"),
    (("library734", "keyboard"), "vmzsorp734"),
    (("library734", "AA"), "library734"),
    (("service734", "key"), "cipfmao734"),
    (("service734", "lemon"), "didjvni734"),
    (("service734", "a"), "service734"),
    (("service734", "zz"), "rdquhbd734"),
    (("service734", "AgentU"), "skvibwe734"),
    (("service734", "keyboard"), "cipwwcv734"),
    (("service734", "AA"), "service734"),
    (("gateway734", "key"), "qeroayi734"),
    (("gateway734", "lemon"), "refsjlc734"),
    (("gateway734", "a"), "gateway734"),
    (("gateway734", "zz"), "fzsdvzx734"),
    (("gateway734", "AgentU"), "ggxrpuy734"),
    (("gateway734", "keyboard"), "qerfkap734"),
    (("gateway734", "AA"), "gateway734"),
    (("storage734", "key"), "cxmbeeo734"),
    (("storage734", "lemon"), "dxafnri734"),
    (("storage734", "a"), "storage734"),
    (("storage734", "zz"), "rsnqzfd734"),
    (("storage734", "AgentU"), "szsetae734"),
    (("storage734", "keyboard"), "cxmsogv734"),
    (("storage734", "AA"), "storage734"),
    (("network734", "key"), "xirgspu734"),
    (("network734", "lemon"), "yifkbco734"),
    (("network734", "a"), "network734"),
    (("network734", "zz"), "mdsvnqj734"),
    (("network734", "AgentU"), "nkxjhlk734"),
    (("network734", "keyboard"), "xirxcrb734"),
    (("network734", "AA"), "network734"),
    (("latency734", "key"), "verorai734"),
    (("latency734", "lemon"), "wefsanc734"),
    (("latency734", "a"), "latency734"),
    (("latency734", "zz"), "kzsdmbx734"),
    (("latency734", "AgentU"), "lgxrgwy734"),
    (("latency734", "keyboard"), "verfbcp734"),
    (("latency734", "AA"), "latency734"),
    (("buffer734", "key"), "lydpip734"),
    (("buffer734", "lemon"), "myrtrc734"),
    (("buffer734", "a"), "buffer734"),
    (("buffer734", "zz"), "ateedq734"),
    (("buffer734", "AgentU"), "bajsxl734"),
    (("buffer734", "keyboard"), "lydgsr734"),
    (("buffer734", "AA"), "buffer734"),
    (("queue734", "key"), "aycei734"),
    (("queue734", "lemon"), "byqir734"),
    (("queue734", "a"), "queue734"),
    (("queue734", "zz"), "ptdtd734"),
    (("queue734", "AgentU"), "qaihx734"),
    (("queue734", "keyboard"), "aycvs734"),
    (("queue734", "AA"), "queue734"),
    (("worker734", "key"), "gspuip734"),
    (("worker734", "lemon"), "hsdyrc734"),
    (("worker734", "a"), "worker734"),
    (("worker734", "zz"), "vnqjdq734"),
    (("worker734", "AgentU"), "wuvxxl734"),
    (("worker734", "keyboard"), "gsplsr734"),
    (("worker734", "AA"), "worker734"),
    (("kernel734", "key"), "uipxij734"),
    (("kernel734", "lemon"), "vidbrw734"),
    (("kernel734", "a"), "kernel734"),
    (("kernel734", "zz"), "jdqmdk734"),
    (("kernel734", "AgentU"), "kkvaxf734"),
    (("kernel734", "keyboard"), "uiposl734"),
    (("kernel734", "AA"), "kernel734"),
    (("signal734", "key"), "cmexej734"),
    (("signal734", "lemon"), "dmsbnw734"),
    (("signal734", "a"), "signal734"),
    (("signal734", "zz"), "rhfmzk734"),
    (("signal734", "AgentU"), "sokatf734"),
    (("signal734", "keyboard"), "cmeool734"),
    (("signal734", "AA"), "signal734"),
    (("packet734", "key"), "zeauir734"),
    (("packet734", "lemon"), "aeoyre734"),
    (("packet734", "a"), "packet734"),
    (("packet734", "zz"), "ozbjds734"),
    (("packet734", "AgentU"), "pggxxn734"),
    (("packet734", "keyboard"), "zealst734"),
    (("packet734", "AA"), "packet734"),
    (("router734", "key"), "bssdip734"),
    (("router734", "lemon"), "csghrc734"),
    (("router734", "a"), "router734"),
    (("router734", "zz"), "qntsdq734"),
    (("router734", "AgentU"), "ruygxl734"),
    (("router734", "keyboard"), "bssusr734"),
    (("router734", "AA"), "router734"),
    (("cluster734", "key"), "mpscxcb734"),
    (("cluster734", "lemon"), "npgggpv734"),
    (("cluster734", "a"), "cluster734"),
    (("cluster734", "zz"), "bktrsdq734"),
    (("cluster734", "AgentU"), "cryfmyr734"),
    (("cluster734", "keyboard"), "mpsthei734"),
    (("cluster734", "AA"), "cluster734"),
    (("mirror734", "key"), "wmpbsp734"),
    (("mirror734", "lemon"), "xmdfbc734"),
    (("mirror734", "a"), "mirror734"),
    (("mirror734", "zz"), "lhqqnq734"),
    (("mirror734", "AgentU"), "movehl734"),
    (("mirror734", "keyboard"), "wmpscr734"),
    (("mirror734", "AA"), "mirror734"),
    (("filter734", "key"), "pmjdip734"),
    (("filter734", "lemon"), "qmxhrc734"),
    (("filter734", "a"), "filter734"),
    (("filter734", "zz"), "ehksdq734"),
    (("filter734", "AgentU"), "fopgxl734"),
    (("filter734", "keyboard"), "pmjusr734"),
    (("filter734", "AA"), "filter734"),
    (("ranking734", "key"), "belumlq734"),
    (("ranking734", "lemon"), "cezyvyk734"),
    (("ranking734", "a"), "ranking734"),
    (("ranking734", "zz"), "qzmjhmf734"),
    (("ranking734", "AgentU"), "rgrxbhg734"),
    (("ranking734", "keyboard"), "bellwnx734"),
    (("ranking734", "AA"), "ranking734"),
    (("encoding734", "key"), "orayhgxk734"),
    (("encoding734", "lemon"), "procqtrs734"),
    (("encoding734", "a"), "encoding734"),
    (("encoding734", "zz"), "dmbnchmf734"),
    (("encoding734", "AgentU"), "etgbwcnm734"),
    (("encoding734", "keyboard"), "orapriej734"),
    (("encoding734", "AA"), "encoding734"),
    (("mapping734", "key"), "wenzmlq734"),
    (("mapping734", "lemon"), "xebdvyk734"),
    (("mapping734", "a"), "mapping734"),
    (("mapping734", "zz"), "lzoohmf734"),
    (("mapping734", "AgentU"), "mgtcbhg734"),
    (("mapping734", "keyboard"), "wenqwnx734"),
    (("mapping734", "AA"), "mapping734"),
    (("record734", "key"), "biayvb734"),
    (("record734", "lemon"), "cioceo734"),
    (("record734", "a"), "record734"),
    (("record734", "zz"), "qdbnqc734"),
    (("record734", "AgentU"), "rkgbkx734"),
    (("record734", "keyboard"), "biapfd734"),
    (("record734", "AA"), "record734"),
    (("candle734", "key"), "melnpc734"),
    (("candle734", "lemon"), "nezryp734"),
    (("candle734", "a"), "candle734"),
    (("candle734", "zz"), "bzmckd734"),
    (("candle734", "AgentU"), "cgrqey734"),
    (("candle734", "keyboard"), "meleze734"),
    (("candle734", "AA"), "candle734"),
    (("thread734", "key"), "dlpoeb734"),
    (("thread734", "lemon"), "eldsno734"),
    (("thread734", "a"), "thread734"),
    (("thread734", "zz"), "sgqdzc734"),
    (("thread734", "AgentU"), "tnvrtx734"),
    (("thread734", "keyboard"), "dlpfod734"),
    (("thread734", "AA"), "thread734"),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 734: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 734: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "a"),
        "round 734: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 734: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 734: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 734: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", "AA"),
        "round 734: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "key"),
        "bssxh 734: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 734: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "a"),
        "round 734: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 734: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 734: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 734: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", "AA"),
        "round 734: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 734: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 734: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "a"),
        "round 734: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 734: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 734: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 734: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", "AA"),
        "round 734: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 734: the processor reads the record then stops", "key"),
        "bssxh 734: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 734: the processor reads the record then stops", "lemon"),
        "csgbq 734: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 734: the processor reads the record then stops", "a"),
        "round 734: the processor reads the record then stops",
    ),
    (
        ("round 734: the processor reads the record then stops", "zz"),
        "qntmc 734: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 734: the processor reads the record then stops", "AgentU"),
        "ruyaw 734: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 734: the processor reads the record then stops", "keyboard"),
        "bssor 734: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 734: the processor reads the record then stops", "AA"),
        "round 734: the processor reads the record then stops",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "key"),
        "bssxh 734: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "lemon"),
        "csgbq 734: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "a"),
        "round 734: a worker pulls the next task from the queue",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "zz"),
        "qntmc 734: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 734: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "keyboard"),
        "bssor 734: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 734: a worker pulls the next task from the queue", "AA"),
        "round 734: a worker pulls the next task from the queue",
    ),
    (
        ("round 734: signals travel through the network layer", "key"),
        "bssxh 734: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 734: signals travel through the network layer", "lemon"),
        "csgbq 734: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 734: signals travel through the network layer", "a"),
        "round 734: signals travel through the network layer",
    ),
    (
        ("round 734: signals travel through the network layer", "zz"),
        "qntmc 734: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 734: signals travel through the network layer", "AgentU"),
        "ruyaw 734: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 734: signals travel through the network layer", "keyboard"),
        "bssor 734: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 734: signals travel through the network layer", "AA"),
        "round 734: signals travel through the network layer",
    ),
    (
        ("round 734: the gateway routes each request by policy", "key"),
        "bssxh 734: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 734: the gateway routes each request by policy", "lemon"),
        "csgbq 734: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 734: the gateway routes each request by policy", "a"),
        "round 734: the gateway routes each request by policy",
    ),
    (
        ("round 734: the gateway routes each request by policy", "zz"),
        "qntmc 734: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 734: the gateway routes each request by policy", "AgentU"),
        "ruyaw 734: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 734: the gateway routes each request by policy", "keyboard"),
        "bssor 734: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 734: the gateway routes each request by policy", "AA"),
        "round 734: the gateway routes each request by policy",
    ),
    (("round 734: memory grows until the buffer is full", "key"), "bssxh 734: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 734: memory grows until the buffer is full", "lemon"), "csgbq 734: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 734: memory grows until the buffer is full", "a"), "round 734: memory grows until the buffer is full"),
    (("round 734: memory grows until the buffer is full", "zz"), "qntmc 734: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 734: memory grows until the buffer is full", "AgentU"),
        "ruyaw 734: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 734: memory grows until the buffer is full", "keyboard"),
        "bssor 734: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 734: memory grows until the buffer is full", "AA"), "round 734: memory grows until the buffer is full"),
    (("round 734: the cluster mirrors every packet twice", "key"), "bssxh 734: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 734: the cluster mirrors every packet twice", "lemon"),
        "csgbq 734: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 734: the cluster mirrors every packet twice", "a"), "round 734: the cluster mirrors every packet twice"),
    (("round 734: the cluster mirrors every packet twice", "zz"), "qntmc 734: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 734: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 734: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 734: the cluster mirrors every packet twice", "keyboard"),
        "bssor 734: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 734: the cluster mirrors every packet twice", "AA"), "round 734: the cluster mirrors every packet twice"),
    (
        ("round 734: ranking uses tokens learned from the corpus", "key"),
        "bssxh 734: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 734: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", "a"),
        "round 734: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 734: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 734: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 734: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", "AA"),
        "round 734: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 734: a long session ends when the candle dies", "key"),
        "bssxh 734: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 734: a long session ends when the candle dies", "lemon"),
        "csgbq 734: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 734: a long session ends when the candle dies", "a"),
        "round 734: a long session ends when the candle dies",
    ),
    (
        ("round 734: a long session ends when the candle dies", "zz"),
        "qntmc 734: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 734: a long session ends when the candle dies", "AgentU"),
        "ruyaw 734: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 734: a long session ends when the candle dies", "keyboard"),
        "bssor 734: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 734: a long session ends when the candle dies", "AA"),
        "round 734: a long session ends when the candle dies",
    ),
    (("round 734: encode the prompt then map the result", "key"), "bssxh 734: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 734: encode the prompt then map the result", "lemon"), "csgbq 734: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 734: encode the prompt then map the result", "a"), "round 734: encode the prompt then map the result"),
    (("round 734: encode the prompt then map the result", "zz"), "qntmc 734: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 734: encode the prompt then map the result", "AgentU"),
        "ruyaw 734: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 734: encode the prompt then map the result", "keyboard"),
        "bssor 734: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 734: encode the prompt then map the result", "AA"), "round 734: encode the prompt then map the result"),
    (("round 734: the kernel wakes the worker at dawn", "key"), "bssxh 734: rri iovlop ukocc xfo ambocb er neux"),
    (("round 734: the kernel wakes the worker at dawn", "lemon"), "csgbq 734: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 734: the kernel wakes the worker at dawn", "a"), "round 734: the kernel wakes the worker at dawn"),
    (("round 734: the kernel wakes the worker at dawn", "zz"), "qntmc 734: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 734: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 734: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 734: the kernel wakes the worker at dawn", "keyboard"), "bssor 734: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 734: the kernel wakes the worker at dawn", "AA"), "round 734: the kernel wakes the worker at dawn"),
    (("round 734: service latency drops after the patch", "key"), "bssxh 734: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 734: service latency drops after the patch", "lemon"), "csgbq 734: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 734: service latency drops after the patch", "a"), "round 734: service latency drops after the patch"),
    (("round 734: service latency drops after the patch", "zz"), "qntmc 734: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 734: service latency drops after the patch", "AgentU"),
        "ruyaw 734: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 734: service latency drops after the patch", "keyboard"),
        "bssor 734: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 734: service latency drops after the patch", "AA"), "round 734: service latency drops after the patch"),
    (
        ("round 734: the library caches every vector it sees", "key"),
        "bssxh 734: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 734: the library caches every vector it sees", "lemon"),
        "csgbq 734: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 734: the library caches every vector it sees", "a"), "round 734: the library caches every vector it sees"),
    (
        ("round 734: the library caches every vector it sees", "zz"),
        "qntmc 734: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 734: the library caches every vector it sees", "AgentU"),
        "ruyaw 734: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 734: the library caches every vector it sees", "keyboard"),
        "bssor 734: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 734: the library caches every vector it sees", "AA"),
        "round 734: the library caches every vector it sees",
    ),
    (("round 734: agents argue then the debate resolves", "key"), "bssxh 734: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 734: agents argue then the debate resolves", "lemon"), "csgbq 734: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 734: agents argue then the debate resolves", "a"), "round 734: agents argue then the debate resolves"),
    (("round 734: agents argue then the debate resolves", "zz"), "qntmc 734: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 734: agents argue then the debate resolves", "AgentU"),
        "ruyaw 734: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 734: agents argue then the debate resolves", "keyboard"),
        "bssor 734: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 734: agents argue then the debate resolves", "AA"), "round 734: agents argue then the debate resolves"),
    (("round 734: the filter keeps only strong matches", "key"), "bssxh 734: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 734: the filter keeps only strong matches", "lemon"), "csgbq 734: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 734: the filter keeps only strong matches", "a"), "round 734: the filter keeps only strong matches"),
    (("round 734: the filter keeps only strong matches", "zz"), "qntmc 734: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 734: the filter keeps only strong matches", "AgentU"), "ruyaw 734: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 734: the filter keeps only strong matches", "keyboard"),
        "bssor 734: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 734: the filter keeps only strong matches", "AA"), "round 734: the filter keeps only strong matches"),
    (("round 734: the model answers with a short reply", "key"), "bssxh 734: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 734: the model answers with a short reply", "lemon"), "csgbq 734: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 734: the model answers with a short reply", "a"), "round 734: the model answers with a short reply"),
    (("round 734: the model answers with a short reply", "zz"), "qntmc 734: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 734: the model answers with a short reply", "AgentU"), "ruyaw 734: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 734: the model answers with a short reply", "keyboard"),
        "bssor 734: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 734: the model answers with a short reply", "AA"), "round 734: the model answers with a short reply"),
    (
        ("round 734: the recorder stores the reasoning trace", "key"),
        "bssxh 734: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 734: the recorder stores the reasoning trace", "lemon"),
        "csgbq 734: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 734: the recorder stores the reasoning trace", "a"), "round 734: the recorder stores the reasoning trace"),
    (
        ("round 734: the recorder stores the reasoning trace", "zz"),
        "qntmc 734: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 734: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 734: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 734: the recorder stores the reasoning trace", "keyboard"),
        "bssor 734: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 734: the recorder stores the reasoning trace", "AA"),
        "round 734: the recorder stores the reasoning trace",
    ),
    (("round 734: the angel watches the processor run", "key"), "bssxh 734: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 734: the angel watches the processor run", "lemon"), "csgbq 734: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 734: the angel watches the processor run", "a"), "round 734: the angel watches the processor run"),
    (("round 734: the angel watches the processor run", "zz"), "qntmc 734: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 734: the angel watches the processor run", "AgentU"), "ruyaw 734: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 734: the angel watches the processor run", "keyboard"), "bssor 734: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 734: the angel watches the processor run", "AA"), "round 734: the angel watches the processor run"),
    (("round 734: angle of the vector decides the match", "key"), "bssxh 734: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 734: angle of the vector decides the match", "lemon"), "csgbq 734: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 734: angle of the vector decides the match", "a"), "round 734: angle of the vector decides the match"),
    (("round 734: angle of the vector decides the match", "zz"), "qntmc 734: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 734: angle of the vector decides the match", "AgentU"),
        "ruyaw 734: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 734: angle of the vector decides the match", "keyboard"),
        "bssor 734: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 734: angle of the vector decides the match", "AA"), "round 734: angle of the vector decides the match"),
    (
        ("round 734: the candle burns twice as long at night", "key"),
        "bssxh 734: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 734: the candle burns twice as long at night", "lemon"),
        "csgbq 734: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 734: the candle burns twice as long at night", "a"), "round 734: the candle burns twice as long at night"),
    (
        ("round 734: the candle burns twice as long at night", "zz"),
        "qntmc 734: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 734: the candle burns twice as long at night", "AgentU"),
        "ruyaw 734: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 734: the candle burns twice as long at night", "keyboard"),
        "bssor 734: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 734: the candle burns twice as long at night", "AA"),
        "round 734: the candle burns twice as long at night",
    ),
    (("round 734: a mirror of the universe in one line", "key"), "bssxh 734: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 734: a mirror of the universe in one line", "lemon"), "csgbq 734: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 734: a mirror of the universe in one line", "a"), "round 734: a mirror of the universe in one line"),
    (("round 734: a mirror of the universe in one line", "zz"), "qntmc 734: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 734: a mirror of the universe in one line", "AgentU"), "ruyaw 734: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 734: a mirror of the universe in one line", "keyboard"),
        "bssor 734: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 734: a mirror of the universe in one line", "AA"), "round 734: a mirror of the universe in one line"),
    (("round 734: the queue drains before the storm", "key"), "bssxh 734: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 734: the queue drains before the storm", "lemon"), "csgbq 734: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 734: the queue drains before the storm", "a"), "round 734: the queue drains before the storm"),
    (("round 734: the queue drains before the storm", "zz"), "qntmc 734: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 734: the queue drains before the storm", "AgentU"), "ruyaw 734: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 734: the queue drains before the storm", "keyboard"), "bssor 734: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 734: the queue drains before the storm", "AA"), "round 734: the queue drains before the storm"),
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
