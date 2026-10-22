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
    (("kitten113", "key"), "umrdil113"),
    (("kitten113", "lemon"), "vmfhry113"),
    (("kitten113", "a"), "kitten113"),
    (("kitten113", "zz"), "jhssdm113"),
    (("kitten113", "AgentU"), "koxgxh113"),
    (("kitten113", "keyboard"), "umrusn113"),
    (("kitten113", "AA"), "kitten113"),
    (("sitting113", "key"), "cmrdmlq113"),
    (("sitting113", "lemon"), "dmfhvyk113"),
    (("sitting113", "a"), "sitting113"),
    (("sitting113", "zz"), "rhsshmf113"),
    (("sitting113", "AgentU"), "soxgbhg113"),
    (("sitting113", "keyboard"), "cmruwnx113"),
    (("sitting113", "AA"), "sitting113"),
    (("agent113", "key"), "kkcxx113"),
    (("agent113", "lemon"), "lkqbg113"),
    (("agent113", "a"), "agent113"),
    (("agent113", "zz"), "zfdms113"),
    (("agent113", "AgentU"), "amiam113"),
    (("agent113", "keyboard"), "kkcoh113"),
    (("agent113", "AA"), "agent113"),
    (("angle113", "key"), "krevi113"),
    (("angle113", "lemon"), "lrszr113"),
    (("angle113", "a"), "angle113"),
    (("angle113", "zz"), "zmfkd113"),
    (("angle113", "AgentU"), "atkyx113"),
    (("angle113", "keyboard"), "krems113"),
    (("angle113", "AA"), "angle113"),
    (("universe113", "key"), "ergfipci113"),
    (("universe113", "lemon"), "frujrcwq113"),
    (("universe113", "a"), "universe113"),
    (("universe113", "zz"), "tmhudqrd113"),
    (("universe113", "AgentU"), "utmixlsk113"),
    (("universe113", "keyboard"), "ergwsrjh113"),
    (("universe113", "AA"), "universe113"),
    (("memory113", "key"), "wikyvw113"),
    (("memory113", "lemon"), "xiycej113"),
    (("memory113", "a"), "memory113"),
    (("memory113", "zz"), "ldlnqx113"),
    (("memory113", "AgentU"), "mkqbks113"),
    (("memory113", "keyboard"), "wikpfy113"),
    (("memory113", "AA"), "memory113"),
    (("stream113", "key"), "cxpoek113"),
    (("stream113", "lemon"), "dxdsnx113"),
    (("stream113", "a"), "stream113"),
    (("stream113", "zz"), "rsqdzl113"),
    (("stream113", "AgentU"), "szvrtg113"),
    (("stream113", "keyboard"), "cxpfom113"),
    (("stream113", "AA"), "stream113"),
    (("context113", "key"), "msldivd113"),
    (("context113", "lemon"), "nszhrix113"),
    (("context113", "a"), "context113"),
    (("context113", "zz"), "bnmsdws113"),
    (("context113", "AgentU"), "curgxrt113"),
    (("context113", "keyboard"), "mslusxk113"),
    (("context113", "AA"), "context113"),
    (("knowledge113", "key"), "urmgpcnkc113"),
    (("knowledge113", "lemon"), "vrakyphss113"),
    (("knowledge113", "a"), "knowledge113"),
    (("knowledge113", "zz"), "jmnvkdcfd113"),
    (("knowledge113", "AgentU"), "ktsjeydmi113"),
    (("knowledge113", "keyboard"), "urmxzeujo113"),
    (("knowledge113", "AA"), "knowledge113"),
    (("vector113", "key"), "fiadsp113"),
    (("vector113", "lemon"), "giohbc113"),
    (("vector113", "a"), "vector113"),
    (("vector113", "zz"), "udbsnq113"),
    (("vector113", "AgentU"), "vkgghl113"),
    (("vector113", "keyboard"), "fiaucr113"),
    (("vector113", "AA"), "vector113"),
    (("processor113", "key"), "zvmmiqcsp113"),
    (("processor113", "lemon"), "avaqrdwaf113"),
    (("processor113", "a"), "processor113"),
    (("processor113", "zz"), "oqnbdrrnq113"),
    (("processor113", "AgentU"), "pxspxmsuv113"),
    (("processor113", "keyboard"), "zvmdssjrb113"),
    (("processor113", "AA"), "processor113"),
    (("reasoning113", "key"), "biycslsre113"),
    (("reasoning113", "lemon"), "cimgbymzu113"),
    (("reasoning113", "a"), "reasoning113"),
    (("reasoning113", "zz"), "qdzrnmhmf113"),
    (("reasoning113", "AgentU"), "rkefhhitk113"),
    (("reasoning113", "keyboard"), "biytcnzqq113"),
    (("reasoning113", "AA"), "reasoning113"),
    (("machine113", "key"), "wearmlo113"),
    (("machine113", "lemon"), "xeovvyi113"),
    (("machine113", "a"), "machine113"),
    (("machine113", "zz"), "lzbghmd113"),
    (("machine113", "AgentU"), "mggubhe113"),
    (("machine113", "keyboard"), "weaiwnv113"),
    (("machine113", "AA"), "machine113"),
    (("learning113", "key"), "viybrgxk113"),
    (("learning113", "lemon"), "wimfatrs113"),
    (("learning113", "a"), "learning113"),
    (("learning113", "zz"), "kdzqmhmf113"),
    (("learning113", "AgentU"), "lkeegcnm113"),
    (("learning113", "keyboard"), "viysbiej113"),
    (("learning113", "AA"), "learning113"),
    (("model113", "key"), "wsbop113"),
    (("model113", "lemon"), "xspsy113"),
    (("model113", "a"), "model113"),
    (("model113", "zz"), "lncdk113"),
    (("model113", "AgentU"), "muhre113"),
    (("model113", "keyboard"), "wsbfz113"),
    (("model113", "AA"), "model113"),
    (("token113", "key"), "dsior113"),
    (("token113", "lemon"), "eswsa113"),
    (("token113", "a"), "token113"),
    (("token113", "zz"), "snjdm113"),
    (("token113", "AgentU"), "tuorg113"),
    (("token113", "keyboard"), "dsifb113"),
    (("token113", "AA"), "token113"),
    (("prompt113", "key"), "zvmwtr113"),
    (("prompt113", "lemon"), "avaace113"),
    (("prompt113", "a"), "prompt113"),
    (("prompt113", "zz"), "oqnlos113"),
    (("prompt113", "AgentU"), "pxszin113"),
    (("prompt113", "keyboard"), "zvmndt113"),
    (("prompt113", "AA"), "prompt113"),
    (("session113", "key"), "ciqcmmx113"),
    (("session113", "lemon"), "diegvzr113"),
    (("session113", "a"), "session113"),
    (("session113", "zz"), "rdrrhnm113"),
    (("session113", "AgentU"), "skwfbin113"),
    (("session113", "keyboard"), "ciqtwoe113"),
    (("session113", "AA"), "session113"),
    (("library113", "key"), "vmzbepi113"),
    (("library113", "lemon"), "wmnfncc113"),
    (("library113", "a"), "library113"),
    (("library113", "zz"), "khaqzqx113"),
    (("library113", "AgentU"), "lofetly113"),
    (("library113", "keyboard"), "vmzsorp113"),
    (("library113", "AA"), "library113"),
    (("service113", "key"), "cipfmao113"),
    (("service113", "lemon"), "didjvni113"),
    (("service113", "a"), "service113"),
    (("service113", "zz"), "rdquhbd113"),
    (("service113", "AgentU"), "skvibwe113"),
    (("service113", "keyboard"), "cipwwcv113"),
    (("service113", "AA"), "service113"),
    (("gateway113", "key"), "qeroayi113"),
    (("gateway113", "lemon"), "refsjlc113"),
    (("gateway113", "a"), "gateway113"),
    (("gateway113", "zz"), "fzsdvzx113"),
    (("gateway113", "AgentU"), "ggxrpuy113"),
    (("gateway113", "keyboard"), "qerfkap113"),
    (("gateway113", "AA"), "gateway113"),
    (("storage113", "key"), "cxmbeeo113"),
    (("storage113", "lemon"), "dxafnri113"),
    (("storage113", "a"), "storage113"),
    (("storage113", "zz"), "rsnqzfd113"),
    (("storage113", "AgentU"), "szsetae113"),
    (("storage113", "keyboard"), "cxmsogv113"),
    (("storage113", "AA"), "storage113"),
    (("network113", "key"), "xirgspu113"),
    (("network113", "lemon"), "yifkbco113"),
    (("network113", "a"), "network113"),
    (("network113", "zz"), "mdsvnqj113"),
    (("network113", "AgentU"), "nkxjhlk113"),
    (("network113", "keyboard"), "xirxcrb113"),
    (("network113", "AA"), "network113"),
    (("latency113", "key"), "verorai113"),
    (("latency113", "lemon"), "wefsanc113"),
    (("latency113", "a"), "latency113"),
    (("latency113", "zz"), "kzsdmbx113"),
    (("latency113", "AgentU"), "lgxrgwy113"),
    (("latency113", "keyboard"), "verfbcp113"),
    (("latency113", "AA"), "latency113"),
    (("buffer113", "key"), "lydpip113"),
    (("buffer113", "lemon"), "myrtrc113"),
    (("buffer113", "a"), "buffer113"),
    (("buffer113", "zz"), "ateedq113"),
    (("buffer113", "AgentU"), "bajsxl113"),
    (("buffer113", "keyboard"), "lydgsr113"),
    (("buffer113", "AA"), "buffer113"),
    (("queue113", "key"), "aycei113"),
    (("queue113", "lemon"), "byqir113"),
    (("queue113", "a"), "queue113"),
    (("queue113", "zz"), "ptdtd113"),
    (("queue113", "AgentU"), "qaihx113"),
    (("queue113", "keyboard"), "aycvs113"),
    (("queue113", "AA"), "queue113"),
    (("worker113", "key"), "gspuip113"),
    (("worker113", "lemon"), "hsdyrc113"),
    (("worker113", "a"), "worker113"),
    (("worker113", "zz"), "vnqjdq113"),
    (("worker113", "AgentU"), "wuvxxl113"),
    (("worker113", "keyboard"), "gsplsr113"),
    (("worker113", "AA"), "worker113"),
    (("kernel113", "key"), "uipxij113"),
    (("kernel113", "lemon"), "vidbrw113"),
    (("kernel113", "a"), "kernel113"),
    (("kernel113", "zz"), "jdqmdk113"),
    (("kernel113", "AgentU"), "kkvaxf113"),
    (("kernel113", "keyboard"), "uiposl113"),
    (("kernel113", "AA"), "kernel113"),
    (("signal113", "key"), "cmexej113"),
    (("signal113", "lemon"), "dmsbnw113"),
    (("signal113", "a"), "signal113"),
    (("signal113", "zz"), "rhfmzk113"),
    (("signal113", "AgentU"), "sokatf113"),
    (("signal113", "keyboard"), "cmeool113"),
    (("signal113", "AA"), "signal113"),
    (("packet113", "key"), "zeauir113"),
    (("packet113", "lemon"), "aeoyre113"),
    (("packet113", "a"), "packet113"),
    (("packet113", "zz"), "ozbjds113"),
    (("packet113", "AgentU"), "pggxxn113"),
    (("packet113", "keyboard"), "zealst113"),
    (("packet113", "AA"), "packet113"),
    (("router113", "key"), "bssdip113"),
    (("router113", "lemon"), "csghrc113"),
    (("router113", "a"), "router113"),
    (("router113", "zz"), "qntsdq113"),
    (("router113", "AgentU"), "ruygxl113"),
    (("router113", "keyboard"), "bssusr113"),
    (("router113", "AA"), "router113"),
    (("cluster113", "key"), "mpscxcb113"),
    (("cluster113", "lemon"), "npgggpv113"),
    (("cluster113", "a"), "cluster113"),
    (("cluster113", "zz"), "bktrsdq113"),
    (("cluster113", "AgentU"), "cryfmyr113"),
    (("cluster113", "keyboard"), "mpsthei113"),
    (("cluster113", "AA"), "cluster113"),
    (("mirror113", "key"), "wmpbsp113"),
    (("mirror113", "lemon"), "xmdfbc113"),
    (("mirror113", "a"), "mirror113"),
    (("mirror113", "zz"), "lhqqnq113"),
    (("mirror113", "AgentU"), "movehl113"),
    (("mirror113", "keyboard"), "wmpscr113"),
    (("mirror113", "AA"), "mirror113"),
    (("filter113", "key"), "pmjdip113"),
    (("filter113", "lemon"), "qmxhrc113"),
    (("filter113", "a"), "filter113"),
    (("filter113", "zz"), "ehksdq113"),
    (("filter113", "AgentU"), "fopgxl113"),
    (("filter113", "keyboard"), "pmjusr113"),
    (("filter113", "AA"), "filter113"),
    (("ranking113", "key"), "belumlq113"),
    (("ranking113", "lemon"), "cezyvyk113"),
    (("ranking113", "a"), "ranking113"),
    (("ranking113", "zz"), "qzmjhmf113"),
    (("ranking113", "AgentU"), "rgrxbhg113"),
    (("ranking113", "keyboard"), "bellwnx113"),
    (("ranking113", "AA"), "ranking113"),
    (("encoding113", "key"), "orayhgxk113"),
    (("encoding113", "lemon"), "procqtrs113"),
    (("encoding113", "a"), "encoding113"),
    (("encoding113", "zz"), "dmbnchmf113"),
    (("encoding113", "AgentU"), "etgbwcnm113"),
    (("encoding113", "keyboard"), "orapriej113"),
    (("encoding113", "AA"), "encoding113"),
    (("mapping113", "key"), "wenzmlq113"),
    (("mapping113", "lemon"), "xebdvyk113"),
    (("mapping113", "a"), "mapping113"),
    (("mapping113", "zz"), "lzoohmf113"),
    (("mapping113", "AgentU"), "mgtcbhg113"),
    (("mapping113", "keyboard"), "wenqwnx113"),
    (("mapping113", "AA"), "mapping113"),
    (("record113", "key"), "biayvb113"),
    (("record113", "lemon"), "cioceo113"),
    (("record113", "a"), "record113"),
    (("record113", "zz"), "qdbnqc113"),
    (("record113", "AgentU"), "rkgbkx113"),
    (("record113", "keyboard"), "biapfd113"),
    (("record113", "AA"), "record113"),
    (("candle113", "key"), "melnpc113"),
    (("candle113", "lemon"), "nezryp113"),
    (("candle113", "a"), "candle113"),
    (("candle113", "zz"), "bzmckd113"),
    (("candle113", "AgentU"), "cgrqey113"),
    (("candle113", "keyboard"), "meleze113"),
    (("candle113", "AA"), "candle113"),
    (("thread113", "key"), "dlpoeb113"),
    (("thread113", "lemon"), "eldsno113"),
    (("thread113", "a"), "thread113"),
    (("thread113", "zz"), "sgqdzc113"),
    (("thread113", "AgentU"), "tnvrtx113"),
    (("thread113", "keyboard"), "dlpfod113"),
    (("thread113", "AA"), "thread113"),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 113: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 113: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "a"),
        "round 113: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 113: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 113: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 113: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", "AA"),
        "round 113: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "key"),
        "bssxh 113: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 113: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "a"),
        "round 113: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 113: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 113: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 113: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", "AA"),
        "round 113: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 113: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 113: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "a"),
        "round 113: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 113: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 113: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 113: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", "AA"),
        "round 113: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 113: the processor reads the record then stops", "key"),
        "bssxh 113: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 113: the processor reads the record then stops", "lemon"),
        "csgbq 113: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 113: the processor reads the record then stops", "a"),
        "round 113: the processor reads the record then stops",
    ),
    (
        ("round 113: the processor reads the record then stops", "zz"),
        "qntmc 113: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 113: the processor reads the record then stops", "AgentU"),
        "ruyaw 113: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 113: the processor reads the record then stops", "keyboard"),
        "bssor 113: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 113: the processor reads the record then stops", "AA"),
        "round 113: the processor reads the record then stops",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "key"),
        "bssxh 113: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "lemon"),
        "csgbq 113: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "a"),
        "round 113: a worker pulls the next task from the queue",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "zz"),
        "qntmc 113: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 113: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "keyboard"),
        "bssor 113: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 113: a worker pulls the next task from the queue", "AA"),
        "round 113: a worker pulls the next task from the queue",
    ),
    (
        ("round 113: signals travel through the network layer", "key"),
        "bssxh 113: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 113: signals travel through the network layer", "lemon"),
        "csgbq 113: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 113: signals travel through the network layer", "a"),
        "round 113: signals travel through the network layer",
    ),
    (
        ("round 113: signals travel through the network layer", "zz"),
        "qntmc 113: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 113: signals travel through the network layer", "AgentU"),
        "ruyaw 113: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 113: signals travel through the network layer", "keyboard"),
        "bssor 113: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 113: signals travel through the network layer", "AA"),
        "round 113: signals travel through the network layer",
    ),
    (
        ("round 113: the gateway routes each request by policy", "key"),
        "bssxh 113: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 113: the gateway routes each request by policy", "lemon"),
        "csgbq 113: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 113: the gateway routes each request by policy", "a"),
        "round 113: the gateway routes each request by policy",
    ),
    (
        ("round 113: the gateway routes each request by policy", "zz"),
        "qntmc 113: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 113: the gateway routes each request by policy", "AgentU"),
        "ruyaw 113: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 113: the gateway routes each request by policy", "keyboard"),
        "bssor 113: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 113: the gateway routes each request by policy", "AA"),
        "round 113: the gateway routes each request by policy",
    ),
    (("round 113: memory grows until the buffer is full", "key"), "bssxh 113: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 113: memory grows until the buffer is full", "lemon"), "csgbq 113: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 113: memory grows until the buffer is full", "a"), "round 113: memory grows until the buffer is full"),
    (("round 113: memory grows until the buffer is full", "zz"), "qntmc 113: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 113: memory grows until the buffer is full", "AgentU"),
        "ruyaw 113: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 113: memory grows until the buffer is full", "keyboard"),
        "bssor 113: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 113: memory grows until the buffer is full", "AA"), "round 113: memory grows until the buffer is full"),
    (("round 113: the cluster mirrors every packet twice", "key"), "bssxh 113: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 113: the cluster mirrors every packet twice", "lemon"),
        "csgbq 113: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 113: the cluster mirrors every packet twice", "a"), "round 113: the cluster mirrors every packet twice"),
    (("round 113: the cluster mirrors every packet twice", "zz"), "qntmc 113: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 113: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 113: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 113: the cluster mirrors every packet twice", "keyboard"),
        "bssor 113: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 113: the cluster mirrors every packet twice", "AA"), "round 113: the cluster mirrors every packet twice"),
    (
        ("round 113: ranking uses tokens learned from the corpus", "key"),
        "bssxh 113: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 113: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", "a"),
        "round 113: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 113: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 113: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 113: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", "AA"),
        "round 113: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 113: a long session ends when the candle dies", "key"),
        "bssxh 113: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 113: a long session ends when the candle dies", "lemon"),
        "csgbq 113: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 113: a long session ends when the candle dies", "a"),
        "round 113: a long session ends when the candle dies",
    ),
    (
        ("round 113: a long session ends when the candle dies", "zz"),
        "qntmc 113: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 113: a long session ends when the candle dies", "AgentU"),
        "ruyaw 113: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 113: a long session ends when the candle dies", "keyboard"),
        "bssor 113: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 113: a long session ends when the candle dies", "AA"),
        "round 113: a long session ends when the candle dies",
    ),
    (("round 113: encode the prompt then map the result", "key"), "bssxh 113: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 113: encode the prompt then map the result", "lemon"), "csgbq 113: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 113: encode the prompt then map the result", "a"), "round 113: encode the prompt then map the result"),
    (("round 113: encode the prompt then map the result", "zz"), "qntmc 113: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 113: encode the prompt then map the result", "AgentU"),
        "ruyaw 113: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 113: encode the prompt then map the result", "keyboard"),
        "bssor 113: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 113: encode the prompt then map the result", "AA"), "round 113: encode the prompt then map the result"),
    (("round 113: the kernel wakes the worker at dawn", "key"), "bssxh 113: rri iovlop ukocc xfo ambocb er neux"),
    (("round 113: the kernel wakes the worker at dawn", "lemon"), "csgbq 113: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 113: the kernel wakes the worker at dawn", "a"), "round 113: the kernel wakes the worker at dawn"),
    (("round 113: the kernel wakes the worker at dawn", "zz"), "qntmc 113: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 113: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 113: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 113: the kernel wakes the worker at dawn", "keyboard"), "bssor 113: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 113: the kernel wakes the worker at dawn", "AA"), "round 113: the kernel wakes the worker at dawn"),
    (("round 113: service latency drops after the patch", "key"), "bssxh 113: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 113: service latency drops after the patch", "lemon"), "csgbq 113: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 113: service latency drops after the patch", "a"), "round 113: service latency drops after the patch"),
    (("round 113: service latency drops after the patch", "zz"), "qntmc 113: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 113: service latency drops after the patch", "AgentU"),
        "ruyaw 113: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 113: service latency drops after the patch", "keyboard"),
        "bssor 113: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 113: service latency drops after the patch", "AA"), "round 113: service latency drops after the patch"),
    (
        ("round 113: the library caches every vector it sees", "key"),
        "bssxh 113: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 113: the library caches every vector it sees", "lemon"),
        "csgbq 113: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 113: the library caches every vector it sees", "a"), "round 113: the library caches every vector it sees"),
    (
        ("round 113: the library caches every vector it sees", "zz"),
        "qntmc 113: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 113: the library caches every vector it sees", "AgentU"),
        "ruyaw 113: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 113: the library caches every vector it sees", "keyboard"),
        "bssor 113: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 113: the library caches every vector it sees", "AA"),
        "round 113: the library caches every vector it sees",
    ),
    (("round 113: agents argue then the debate resolves", "key"), "bssxh 113: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 113: agents argue then the debate resolves", "lemon"), "csgbq 113: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 113: agents argue then the debate resolves", "a"), "round 113: agents argue then the debate resolves"),
    (("round 113: agents argue then the debate resolves", "zz"), "qntmc 113: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 113: agents argue then the debate resolves", "AgentU"),
        "ruyaw 113: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 113: agents argue then the debate resolves", "keyboard"),
        "bssor 113: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 113: agents argue then the debate resolves", "AA"), "round 113: agents argue then the debate resolves"),
    (("round 113: the filter keeps only strong matches", "key"), "bssxh 113: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 113: the filter keeps only strong matches", "lemon"), "csgbq 113: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 113: the filter keeps only strong matches", "a"), "round 113: the filter keeps only strong matches"),
    (("round 113: the filter keeps only strong matches", "zz"), "qntmc 113: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 113: the filter keeps only strong matches", "AgentU"), "ruyaw 113: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 113: the filter keeps only strong matches", "keyboard"),
        "bssor 113: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 113: the filter keeps only strong matches", "AA"), "round 113: the filter keeps only strong matches"),
    (("round 113: the model answers with a short reply", "key"), "bssxh 113: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 113: the model answers with a short reply", "lemon"), "csgbq 113: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 113: the model answers with a short reply", "a"), "round 113: the model answers with a short reply"),
    (("round 113: the model answers with a short reply", "zz"), "qntmc 113: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 113: the model answers with a short reply", "AgentU"), "ruyaw 113: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 113: the model answers with a short reply", "keyboard"),
        "bssor 113: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 113: the model answers with a short reply", "AA"), "round 113: the model answers with a short reply"),
    (
        ("round 113: the recorder stores the reasoning trace", "key"),
        "bssxh 113: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 113: the recorder stores the reasoning trace", "lemon"),
        "csgbq 113: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 113: the recorder stores the reasoning trace", "a"), "round 113: the recorder stores the reasoning trace"),
    (
        ("round 113: the recorder stores the reasoning trace", "zz"),
        "qntmc 113: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 113: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 113: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 113: the recorder stores the reasoning trace", "keyboard"),
        "bssor 113: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 113: the recorder stores the reasoning trace", "AA"),
        "round 113: the recorder stores the reasoning trace",
    ),
    (("round 113: the angel watches the processor run", "key"), "bssxh 113: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 113: the angel watches the processor run", "lemon"), "csgbq 113: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 113: the angel watches the processor run", "a"), "round 113: the angel watches the processor run"),
    (("round 113: the angel watches the processor run", "zz"), "qntmc 113: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 113: the angel watches the processor run", "AgentU"), "ruyaw 113: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 113: the angel watches the processor run", "keyboard"), "bssor 113: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 113: the angel watches the processor run", "AA"), "round 113: the angel watches the processor run"),
    (("round 113: angle of the vector decides the match", "key"), "bssxh 113: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 113: angle of the vector decides the match", "lemon"), "csgbq 113: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 113: angle of the vector decides the match", "a"), "round 113: angle of the vector decides the match"),
    (("round 113: angle of the vector decides the match", "zz"), "qntmc 113: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 113: angle of the vector decides the match", "AgentU"),
        "ruyaw 113: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 113: angle of the vector decides the match", "keyboard"),
        "bssor 113: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 113: angle of the vector decides the match", "AA"), "round 113: angle of the vector decides the match"),
    (
        ("round 113: the candle burns twice as long at night", "key"),
        "bssxh 113: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 113: the candle burns twice as long at night", "lemon"),
        "csgbq 113: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 113: the candle burns twice as long at night", "a"), "round 113: the candle burns twice as long at night"),
    (
        ("round 113: the candle burns twice as long at night", "zz"),
        "qntmc 113: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 113: the candle burns twice as long at night", "AgentU"),
        "ruyaw 113: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 113: the candle burns twice as long at night", "keyboard"),
        "bssor 113: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 113: the candle burns twice as long at night", "AA"),
        "round 113: the candle burns twice as long at night",
    ),
    (("round 113: a mirror of the universe in one line", "key"), "bssxh 113: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 113: a mirror of the universe in one line", "lemon"), "csgbq 113: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 113: a mirror of the universe in one line", "a"), "round 113: a mirror of the universe in one line"),
    (("round 113: a mirror of the universe in one line", "zz"), "qntmc 113: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 113: a mirror of the universe in one line", "AgentU"), "ruyaw 113: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 113: a mirror of the universe in one line", "keyboard"),
        "bssor 113: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 113: a mirror of the universe in one line", "AA"), "round 113: a mirror of the universe in one line"),
    (("round 113: the queue drains before the storm", "key"), "bssxh 113: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 113: the queue drains before the storm", "lemon"), "csgbq 113: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 113: the queue drains before the storm", "a"), "round 113: the queue drains before the storm"),
    (("round 113: the queue drains before the storm", "zz"), "qntmc 113: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 113: the queue drains before the storm", "AgentU"), "ruyaw 113: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 113: the queue drains before the storm", "keyboard"), "bssor 113: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 113: the queue drains before the storm", "AA"), "round 113: the queue drains before the storm"),
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
