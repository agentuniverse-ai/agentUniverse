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
    (("kitten747", "key"), "umrdil747"),
    (("kitten747", "lemon"), "vmfhry747"),
    (("kitten747", "a"), "kitten747"),
    (("kitten747", "zz"), "jhssdm747"),
    (("kitten747", "AgentU"), "koxgxh747"),
    (("kitten747", "keyboard"), "umrusn747"),
    (("kitten747", "AA"), "kitten747"),
    (("sitting747", "key"), "cmrdmlq747"),
    (("sitting747", "lemon"), "dmfhvyk747"),
    (("sitting747", "a"), "sitting747"),
    (("sitting747", "zz"), "rhsshmf747"),
    (("sitting747", "AgentU"), "soxgbhg747"),
    (("sitting747", "keyboard"), "cmruwnx747"),
    (("sitting747", "AA"), "sitting747"),
    (("agent747", "key"), "kkcxx747"),
    (("agent747", "lemon"), "lkqbg747"),
    (("agent747", "a"), "agent747"),
    (("agent747", "zz"), "zfdms747"),
    (("agent747", "AgentU"), "amiam747"),
    (("agent747", "keyboard"), "kkcoh747"),
    (("agent747", "AA"), "agent747"),
    (("angle747", "key"), "krevi747"),
    (("angle747", "lemon"), "lrszr747"),
    (("angle747", "a"), "angle747"),
    (("angle747", "zz"), "zmfkd747"),
    (("angle747", "AgentU"), "atkyx747"),
    (("angle747", "keyboard"), "krems747"),
    (("angle747", "AA"), "angle747"),
    (("universe747", "key"), "ergfipci747"),
    (("universe747", "lemon"), "frujrcwq747"),
    (("universe747", "a"), "universe747"),
    (("universe747", "zz"), "tmhudqrd747"),
    (("universe747", "AgentU"), "utmixlsk747"),
    (("universe747", "keyboard"), "ergwsrjh747"),
    (("universe747", "AA"), "universe747"),
    (("memory747", "key"), "wikyvw747"),
    (("memory747", "lemon"), "xiycej747"),
    (("memory747", "a"), "memory747"),
    (("memory747", "zz"), "ldlnqx747"),
    (("memory747", "AgentU"), "mkqbks747"),
    (("memory747", "keyboard"), "wikpfy747"),
    (("memory747", "AA"), "memory747"),
    (("stream747", "key"), "cxpoek747"),
    (("stream747", "lemon"), "dxdsnx747"),
    (("stream747", "a"), "stream747"),
    (("stream747", "zz"), "rsqdzl747"),
    (("stream747", "AgentU"), "szvrtg747"),
    (("stream747", "keyboard"), "cxpfom747"),
    (("stream747", "AA"), "stream747"),
    (("context747", "key"), "msldivd747"),
    (("context747", "lemon"), "nszhrix747"),
    (("context747", "a"), "context747"),
    (("context747", "zz"), "bnmsdws747"),
    (("context747", "AgentU"), "curgxrt747"),
    (("context747", "keyboard"), "mslusxk747"),
    (("context747", "AA"), "context747"),
    (("knowledge747", "key"), "urmgpcnkc747"),
    (("knowledge747", "lemon"), "vrakyphss747"),
    (("knowledge747", "a"), "knowledge747"),
    (("knowledge747", "zz"), "jmnvkdcfd747"),
    (("knowledge747", "AgentU"), "ktsjeydmi747"),
    (("knowledge747", "keyboard"), "urmxzeujo747"),
    (("knowledge747", "AA"), "knowledge747"),
    (("vector747", "key"), "fiadsp747"),
    (("vector747", "lemon"), "giohbc747"),
    (("vector747", "a"), "vector747"),
    (("vector747", "zz"), "udbsnq747"),
    (("vector747", "AgentU"), "vkgghl747"),
    (("vector747", "keyboard"), "fiaucr747"),
    (("vector747", "AA"), "vector747"),
    (("processor747", "key"), "zvmmiqcsp747"),
    (("processor747", "lemon"), "avaqrdwaf747"),
    (("processor747", "a"), "processor747"),
    (("processor747", "zz"), "oqnbdrrnq747"),
    (("processor747", "AgentU"), "pxspxmsuv747"),
    (("processor747", "keyboard"), "zvmdssjrb747"),
    (("processor747", "AA"), "processor747"),
    (("reasoning747", "key"), "biycslsre747"),
    (("reasoning747", "lemon"), "cimgbymzu747"),
    (("reasoning747", "a"), "reasoning747"),
    (("reasoning747", "zz"), "qdzrnmhmf747"),
    (("reasoning747", "AgentU"), "rkefhhitk747"),
    (("reasoning747", "keyboard"), "biytcnzqq747"),
    (("reasoning747", "AA"), "reasoning747"),
    (("machine747", "key"), "wearmlo747"),
    (("machine747", "lemon"), "xeovvyi747"),
    (("machine747", "a"), "machine747"),
    (("machine747", "zz"), "lzbghmd747"),
    (("machine747", "AgentU"), "mggubhe747"),
    (("machine747", "keyboard"), "weaiwnv747"),
    (("machine747", "AA"), "machine747"),
    (("learning747", "key"), "viybrgxk747"),
    (("learning747", "lemon"), "wimfatrs747"),
    (("learning747", "a"), "learning747"),
    (("learning747", "zz"), "kdzqmhmf747"),
    (("learning747", "AgentU"), "lkeegcnm747"),
    (("learning747", "keyboard"), "viysbiej747"),
    (("learning747", "AA"), "learning747"),
    (("model747", "key"), "wsbop747"),
    (("model747", "lemon"), "xspsy747"),
    (("model747", "a"), "model747"),
    (("model747", "zz"), "lncdk747"),
    (("model747", "AgentU"), "muhre747"),
    (("model747", "keyboard"), "wsbfz747"),
    (("model747", "AA"), "model747"),
    (("token747", "key"), "dsior747"),
    (("token747", "lemon"), "eswsa747"),
    (("token747", "a"), "token747"),
    (("token747", "zz"), "snjdm747"),
    (("token747", "AgentU"), "tuorg747"),
    (("token747", "keyboard"), "dsifb747"),
    (("token747", "AA"), "token747"),
    (("prompt747", "key"), "zvmwtr747"),
    (("prompt747", "lemon"), "avaace747"),
    (("prompt747", "a"), "prompt747"),
    (("prompt747", "zz"), "oqnlos747"),
    (("prompt747", "AgentU"), "pxszin747"),
    (("prompt747", "keyboard"), "zvmndt747"),
    (("prompt747", "AA"), "prompt747"),
    (("session747", "key"), "ciqcmmx747"),
    (("session747", "lemon"), "diegvzr747"),
    (("session747", "a"), "session747"),
    (("session747", "zz"), "rdrrhnm747"),
    (("session747", "AgentU"), "skwfbin747"),
    (("session747", "keyboard"), "ciqtwoe747"),
    (("session747", "AA"), "session747"),
    (("library747", "key"), "vmzbepi747"),
    (("library747", "lemon"), "wmnfncc747"),
    (("library747", "a"), "library747"),
    (("library747", "zz"), "khaqzqx747"),
    (("library747", "AgentU"), "lofetly747"),
    (("library747", "keyboard"), "vmzsorp747"),
    (("library747", "AA"), "library747"),
    (("service747", "key"), "cipfmao747"),
    (("service747", "lemon"), "didjvni747"),
    (("service747", "a"), "service747"),
    (("service747", "zz"), "rdquhbd747"),
    (("service747", "AgentU"), "skvibwe747"),
    (("service747", "keyboard"), "cipwwcv747"),
    (("service747", "AA"), "service747"),
    (("gateway747", "key"), "qeroayi747"),
    (("gateway747", "lemon"), "refsjlc747"),
    (("gateway747", "a"), "gateway747"),
    (("gateway747", "zz"), "fzsdvzx747"),
    (("gateway747", "AgentU"), "ggxrpuy747"),
    (("gateway747", "keyboard"), "qerfkap747"),
    (("gateway747", "AA"), "gateway747"),
    (("storage747", "key"), "cxmbeeo747"),
    (("storage747", "lemon"), "dxafnri747"),
    (("storage747", "a"), "storage747"),
    (("storage747", "zz"), "rsnqzfd747"),
    (("storage747", "AgentU"), "szsetae747"),
    (("storage747", "keyboard"), "cxmsogv747"),
    (("storage747", "AA"), "storage747"),
    (("network747", "key"), "xirgspu747"),
    (("network747", "lemon"), "yifkbco747"),
    (("network747", "a"), "network747"),
    (("network747", "zz"), "mdsvnqj747"),
    (("network747", "AgentU"), "nkxjhlk747"),
    (("network747", "keyboard"), "xirxcrb747"),
    (("network747", "AA"), "network747"),
    (("latency747", "key"), "verorai747"),
    (("latency747", "lemon"), "wefsanc747"),
    (("latency747", "a"), "latency747"),
    (("latency747", "zz"), "kzsdmbx747"),
    (("latency747", "AgentU"), "lgxrgwy747"),
    (("latency747", "keyboard"), "verfbcp747"),
    (("latency747", "AA"), "latency747"),
    (("buffer747", "key"), "lydpip747"),
    (("buffer747", "lemon"), "myrtrc747"),
    (("buffer747", "a"), "buffer747"),
    (("buffer747", "zz"), "ateedq747"),
    (("buffer747", "AgentU"), "bajsxl747"),
    (("buffer747", "keyboard"), "lydgsr747"),
    (("buffer747", "AA"), "buffer747"),
    (("queue747", "key"), "aycei747"),
    (("queue747", "lemon"), "byqir747"),
    (("queue747", "a"), "queue747"),
    (("queue747", "zz"), "ptdtd747"),
    (("queue747", "AgentU"), "qaihx747"),
    (("queue747", "keyboard"), "aycvs747"),
    (("queue747", "AA"), "queue747"),
    (("worker747", "key"), "gspuip747"),
    (("worker747", "lemon"), "hsdyrc747"),
    (("worker747", "a"), "worker747"),
    (("worker747", "zz"), "vnqjdq747"),
    (("worker747", "AgentU"), "wuvxxl747"),
    (("worker747", "keyboard"), "gsplsr747"),
    (("worker747", "AA"), "worker747"),
    (("kernel747", "key"), "uipxij747"),
    (("kernel747", "lemon"), "vidbrw747"),
    (("kernel747", "a"), "kernel747"),
    (("kernel747", "zz"), "jdqmdk747"),
    (("kernel747", "AgentU"), "kkvaxf747"),
    (("kernel747", "keyboard"), "uiposl747"),
    (("kernel747", "AA"), "kernel747"),
    (("signal747", "key"), "cmexej747"),
    (("signal747", "lemon"), "dmsbnw747"),
    (("signal747", "a"), "signal747"),
    (("signal747", "zz"), "rhfmzk747"),
    (("signal747", "AgentU"), "sokatf747"),
    (("signal747", "keyboard"), "cmeool747"),
    (("signal747", "AA"), "signal747"),
    (("packet747", "key"), "zeauir747"),
    (("packet747", "lemon"), "aeoyre747"),
    (("packet747", "a"), "packet747"),
    (("packet747", "zz"), "ozbjds747"),
    (("packet747", "AgentU"), "pggxxn747"),
    (("packet747", "keyboard"), "zealst747"),
    (("packet747", "AA"), "packet747"),
    (("router747", "key"), "bssdip747"),
    (("router747", "lemon"), "csghrc747"),
    (("router747", "a"), "router747"),
    (("router747", "zz"), "qntsdq747"),
    (("router747", "AgentU"), "ruygxl747"),
    (("router747", "keyboard"), "bssusr747"),
    (("router747", "AA"), "router747"),
    (("cluster747", "key"), "mpscxcb747"),
    (("cluster747", "lemon"), "npgggpv747"),
    (("cluster747", "a"), "cluster747"),
    (("cluster747", "zz"), "bktrsdq747"),
    (("cluster747", "AgentU"), "cryfmyr747"),
    (("cluster747", "keyboard"), "mpsthei747"),
    (("cluster747", "AA"), "cluster747"),
    (("mirror747", "key"), "wmpbsp747"),
    (("mirror747", "lemon"), "xmdfbc747"),
    (("mirror747", "a"), "mirror747"),
    (("mirror747", "zz"), "lhqqnq747"),
    (("mirror747", "AgentU"), "movehl747"),
    (("mirror747", "keyboard"), "wmpscr747"),
    (("mirror747", "AA"), "mirror747"),
    (("filter747", "key"), "pmjdip747"),
    (("filter747", "lemon"), "qmxhrc747"),
    (("filter747", "a"), "filter747"),
    (("filter747", "zz"), "ehksdq747"),
    (("filter747", "AgentU"), "fopgxl747"),
    (("filter747", "keyboard"), "pmjusr747"),
    (("filter747", "AA"), "filter747"),
    (("ranking747", "key"), "belumlq747"),
    (("ranking747", "lemon"), "cezyvyk747"),
    (("ranking747", "a"), "ranking747"),
    (("ranking747", "zz"), "qzmjhmf747"),
    (("ranking747", "AgentU"), "rgrxbhg747"),
    (("ranking747", "keyboard"), "bellwnx747"),
    (("ranking747", "AA"), "ranking747"),
    (("encoding747", "key"), "orayhgxk747"),
    (("encoding747", "lemon"), "procqtrs747"),
    (("encoding747", "a"), "encoding747"),
    (("encoding747", "zz"), "dmbnchmf747"),
    (("encoding747", "AgentU"), "etgbwcnm747"),
    (("encoding747", "keyboard"), "orapriej747"),
    (("encoding747", "AA"), "encoding747"),
    (("mapping747", "key"), "wenzmlq747"),
    (("mapping747", "lemon"), "xebdvyk747"),
    (("mapping747", "a"), "mapping747"),
    (("mapping747", "zz"), "lzoohmf747"),
    (("mapping747", "AgentU"), "mgtcbhg747"),
    (("mapping747", "keyboard"), "wenqwnx747"),
    (("mapping747", "AA"), "mapping747"),
    (("record747", "key"), "biayvb747"),
    (("record747", "lemon"), "cioceo747"),
    (("record747", "a"), "record747"),
    (("record747", "zz"), "qdbnqc747"),
    (("record747", "AgentU"), "rkgbkx747"),
    (("record747", "keyboard"), "biapfd747"),
    (("record747", "AA"), "record747"),
    (("candle747", "key"), "melnpc747"),
    (("candle747", "lemon"), "nezryp747"),
    (("candle747", "a"), "candle747"),
    (("candle747", "zz"), "bzmckd747"),
    (("candle747", "AgentU"), "cgrqey747"),
    (("candle747", "keyboard"), "meleze747"),
    (("candle747", "AA"), "candle747"),
    (("thread747", "key"), "dlpoeb747"),
    (("thread747", "lemon"), "eldsno747"),
    (("thread747", "a"), "thread747"),
    (("thread747", "zz"), "sgqdzc747"),
    (("thread747", "AgentU"), "tnvrtx747"),
    (("thread747", "keyboard"), "dlpfod747"),
    (("thread747", "AA"), "thread747"),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 747: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 747: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "a"),
        "round 747: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 747: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 747: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 747: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", "AA"),
        "round 747: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "key"),
        "bssxh 747: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 747: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "a"),
        "round 747: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 747: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 747: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 747: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", "AA"),
        "round 747: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 747: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 747: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "a"),
        "round 747: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 747: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 747: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 747: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", "AA"),
        "round 747: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 747: the processor reads the record then stops", "key"),
        "bssxh 747: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 747: the processor reads the record then stops", "lemon"),
        "csgbq 747: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 747: the processor reads the record then stops", "a"),
        "round 747: the processor reads the record then stops",
    ),
    (
        ("round 747: the processor reads the record then stops", "zz"),
        "qntmc 747: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 747: the processor reads the record then stops", "AgentU"),
        "ruyaw 747: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 747: the processor reads the record then stops", "keyboard"),
        "bssor 747: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 747: the processor reads the record then stops", "AA"),
        "round 747: the processor reads the record then stops",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "key"),
        "bssxh 747: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "lemon"),
        "csgbq 747: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "a"),
        "round 747: a worker pulls the next task from the queue",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "zz"),
        "qntmc 747: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 747: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "keyboard"),
        "bssor 747: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 747: a worker pulls the next task from the queue", "AA"),
        "round 747: a worker pulls the next task from the queue",
    ),
    (
        ("round 747: signals travel through the network layer", "key"),
        "bssxh 747: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 747: signals travel through the network layer", "lemon"),
        "csgbq 747: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 747: signals travel through the network layer", "a"),
        "round 747: signals travel through the network layer",
    ),
    (
        ("round 747: signals travel through the network layer", "zz"),
        "qntmc 747: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 747: signals travel through the network layer", "AgentU"),
        "ruyaw 747: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 747: signals travel through the network layer", "keyboard"),
        "bssor 747: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 747: signals travel through the network layer", "AA"),
        "round 747: signals travel through the network layer",
    ),
    (
        ("round 747: the gateway routes each request by policy", "key"),
        "bssxh 747: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 747: the gateway routes each request by policy", "lemon"),
        "csgbq 747: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 747: the gateway routes each request by policy", "a"),
        "round 747: the gateway routes each request by policy",
    ),
    (
        ("round 747: the gateway routes each request by policy", "zz"),
        "qntmc 747: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 747: the gateway routes each request by policy", "AgentU"),
        "ruyaw 747: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 747: the gateway routes each request by policy", "keyboard"),
        "bssor 747: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 747: the gateway routes each request by policy", "AA"),
        "round 747: the gateway routes each request by policy",
    ),
    (("round 747: memory grows until the buffer is full", "key"), "bssxh 747: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 747: memory grows until the buffer is full", "lemon"), "csgbq 747: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 747: memory grows until the buffer is full", "a"), "round 747: memory grows until the buffer is full"),
    (("round 747: memory grows until the buffer is full", "zz"), "qntmc 747: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 747: memory grows until the buffer is full", "AgentU"),
        "ruyaw 747: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 747: memory grows until the buffer is full", "keyboard"),
        "bssor 747: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 747: memory grows until the buffer is full", "AA"), "round 747: memory grows until the buffer is full"),
    (("round 747: the cluster mirrors every packet twice", "key"), "bssxh 747: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 747: the cluster mirrors every packet twice", "lemon"),
        "csgbq 747: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 747: the cluster mirrors every packet twice", "a"), "round 747: the cluster mirrors every packet twice"),
    (("round 747: the cluster mirrors every packet twice", "zz"), "qntmc 747: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 747: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 747: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 747: the cluster mirrors every packet twice", "keyboard"),
        "bssor 747: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 747: the cluster mirrors every packet twice", "AA"), "round 747: the cluster mirrors every packet twice"),
    (
        ("round 747: ranking uses tokens learned from the corpus", "key"),
        "bssxh 747: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 747: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", "a"),
        "round 747: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 747: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 747: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 747: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", "AA"),
        "round 747: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 747: a long session ends when the candle dies", "key"),
        "bssxh 747: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 747: a long session ends when the candle dies", "lemon"),
        "csgbq 747: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 747: a long session ends when the candle dies", "a"),
        "round 747: a long session ends when the candle dies",
    ),
    (
        ("round 747: a long session ends when the candle dies", "zz"),
        "qntmc 747: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 747: a long session ends when the candle dies", "AgentU"),
        "ruyaw 747: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 747: a long session ends when the candle dies", "keyboard"),
        "bssor 747: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 747: a long session ends when the candle dies", "AA"),
        "round 747: a long session ends when the candle dies",
    ),
    (("round 747: encode the prompt then map the result", "key"), "bssxh 747: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 747: encode the prompt then map the result", "lemon"), "csgbq 747: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 747: encode the prompt then map the result", "a"), "round 747: encode the prompt then map the result"),
    (("round 747: encode the prompt then map the result", "zz"), "qntmc 747: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 747: encode the prompt then map the result", "AgentU"),
        "ruyaw 747: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 747: encode the prompt then map the result", "keyboard"),
        "bssor 747: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 747: encode the prompt then map the result", "AA"), "round 747: encode the prompt then map the result"),
    (("round 747: the kernel wakes the worker at dawn", "key"), "bssxh 747: rri iovlop ukocc xfo ambocb er neux"),
    (("round 747: the kernel wakes the worker at dawn", "lemon"), "csgbq 747: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 747: the kernel wakes the worker at dawn", "a"), "round 747: the kernel wakes the worker at dawn"),
    (("round 747: the kernel wakes the worker at dawn", "zz"), "qntmc 747: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 747: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 747: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 747: the kernel wakes the worker at dawn", "keyboard"), "bssor 747: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 747: the kernel wakes the worker at dawn", "AA"), "round 747: the kernel wakes the worker at dawn"),
    (("round 747: service latency drops after the patch", "key"), "bssxh 747: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 747: service latency drops after the patch", "lemon"), "csgbq 747: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 747: service latency drops after the patch", "a"), "round 747: service latency drops after the patch"),
    (("round 747: service latency drops after the patch", "zz"), "qntmc 747: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 747: service latency drops after the patch", "AgentU"),
        "ruyaw 747: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 747: service latency drops after the patch", "keyboard"),
        "bssor 747: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 747: service latency drops after the patch", "AA"), "round 747: service latency drops after the patch"),
    (
        ("round 747: the library caches every vector it sees", "key"),
        "bssxh 747: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 747: the library caches every vector it sees", "lemon"),
        "csgbq 747: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 747: the library caches every vector it sees", "a"), "round 747: the library caches every vector it sees"),
    (
        ("round 747: the library caches every vector it sees", "zz"),
        "qntmc 747: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 747: the library caches every vector it sees", "AgentU"),
        "ruyaw 747: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 747: the library caches every vector it sees", "keyboard"),
        "bssor 747: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 747: the library caches every vector it sees", "AA"),
        "round 747: the library caches every vector it sees",
    ),
    (("round 747: agents argue then the debate resolves", "key"), "bssxh 747: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 747: agents argue then the debate resolves", "lemon"), "csgbq 747: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 747: agents argue then the debate resolves", "a"), "round 747: agents argue then the debate resolves"),
    (("round 747: agents argue then the debate resolves", "zz"), "qntmc 747: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 747: agents argue then the debate resolves", "AgentU"),
        "ruyaw 747: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 747: agents argue then the debate resolves", "keyboard"),
        "bssor 747: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 747: agents argue then the debate resolves", "AA"), "round 747: agents argue then the debate resolves"),
    (("round 747: the filter keeps only strong matches", "key"), "bssxh 747: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 747: the filter keeps only strong matches", "lemon"), "csgbq 747: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 747: the filter keeps only strong matches", "a"), "round 747: the filter keeps only strong matches"),
    (("round 747: the filter keeps only strong matches", "zz"), "qntmc 747: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 747: the filter keeps only strong matches", "AgentU"), "ruyaw 747: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 747: the filter keeps only strong matches", "keyboard"),
        "bssor 747: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 747: the filter keeps only strong matches", "AA"), "round 747: the filter keeps only strong matches"),
    (("round 747: the model answers with a short reply", "key"), "bssxh 747: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 747: the model answers with a short reply", "lemon"), "csgbq 747: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 747: the model answers with a short reply", "a"), "round 747: the model answers with a short reply"),
    (("round 747: the model answers with a short reply", "zz"), "qntmc 747: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 747: the model answers with a short reply", "AgentU"), "ruyaw 747: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 747: the model answers with a short reply", "keyboard"),
        "bssor 747: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 747: the model answers with a short reply", "AA"), "round 747: the model answers with a short reply"),
    (
        ("round 747: the recorder stores the reasoning trace", "key"),
        "bssxh 747: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 747: the recorder stores the reasoning trace", "lemon"),
        "csgbq 747: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 747: the recorder stores the reasoning trace", "a"), "round 747: the recorder stores the reasoning trace"),
    (
        ("round 747: the recorder stores the reasoning trace", "zz"),
        "qntmc 747: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 747: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 747: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 747: the recorder stores the reasoning trace", "keyboard"),
        "bssor 747: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 747: the recorder stores the reasoning trace", "AA"),
        "round 747: the recorder stores the reasoning trace",
    ),
    (("round 747: the angel watches the processor run", "key"), "bssxh 747: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 747: the angel watches the processor run", "lemon"), "csgbq 747: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 747: the angel watches the processor run", "a"), "round 747: the angel watches the processor run"),
    (("round 747: the angel watches the processor run", "zz"), "qntmc 747: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 747: the angel watches the processor run", "AgentU"), "ruyaw 747: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 747: the angel watches the processor run", "keyboard"), "bssor 747: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 747: the angel watches the processor run", "AA"), "round 747: the angel watches the processor run"),
    (("round 747: angle of the vector decides the match", "key"), "bssxh 747: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 747: angle of the vector decides the match", "lemon"), "csgbq 747: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 747: angle of the vector decides the match", "a"), "round 747: angle of the vector decides the match"),
    (("round 747: angle of the vector decides the match", "zz"), "qntmc 747: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 747: angle of the vector decides the match", "AgentU"),
        "ruyaw 747: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 747: angle of the vector decides the match", "keyboard"),
        "bssor 747: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 747: angle of the vector decides the match", "AA"), "round 747: angle of the vector decides the match"),
    (
        ("round 747: the candle burns twice as long at night", "key"),
        "bssxh 747: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 747: the candle burns twice as long at night", "lemon"),
        "csgbq 747: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 747: the candle burns twice as long at night", "a"), "round 747: the candle burns twice as long at night"),
    (
        ("round 747: the candle burns twice as long at night", "zz"),
        "qntmc 747: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 747: the candle burns twice as long at night", "AgentU"),
        "ruyaw 747: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 747: the candle burns twice as long at night", "keyboard"),
        "bssor 747: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 747: the candle burns twice as long at night", "AA"),
        "round 747: the candle burns twice as long at night",
    ),
    (("round 747: a mirror of the universe in one line", "key"), "bssxh 747: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 747: a mirror of the universe in one line", "lemon"), "csgbq 747: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 747: a mirror of the universe in one line", "a"), "round 747: a mirror of the universe in one line"),
    (("round 747: a mirror of the universe in one line", "zz"), "qntmc 747: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 747: a mirror of the universe in one line", "AgentU"), "ruyaw 747: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 747: a mirror of the universe in one line", "keyboard"),
        "bssor 747: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 747: a mirror of the universe in one line", "AA"), "round 747: a mirror of the universe in one line"),
    (("round 747: the queue drains before the storm", "key"), "bssxh 747: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 747: the queue drains before the storm", "lemon"), "csgbq 747: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 747: the queue drains before the storm", "a"), "round 747: the queue drains before the storm"),
    (("round 747: the queue drains before the storm", "zz"), "qntmc 747: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 747: the queue drains before the storm", "AgentU"), "ruyaw 747: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 747: the queue drains before the storm", "keyboard"), "bssor 747: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 747: the queue drains before the storm", "AA"), "round 747: the queue drains before the storm"),
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
