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
    (("kitten733", "key"), "umrdil733"),
    (("kitten733", "lemon"), "vmfhry733"),
    (("kitten733", "a"), "kitten733"),
    (("kitten733", "zz"), "jhssdm733"),
    (("kitten733", "AgentU"), "koxgxh733"),
    (("kitten733", "keyboard"), "umrusn733"),
    (("kitten733", "AA"), "kitten733"),
    (("sitting733", "key"), "cmrdmlq733"),
    (("sitting733", "lemon"), "dmfhvyk733"),
    (("sitting733", "a"), "sitting733"),
    (("sitting733", "zz"), "rhsshmf733"),
    (("sitting733", "AgentU"), "soxgbhg733"),
    (("sitting733", "keyboard"), "cmruwnx733"),
    (("sitting733", "AA"), "sitting733"),
    (("agent733", "key"), "kkcxx733"),
    (("agent733", "lemon"), "lkqbg733"),
    (("agent733", "a"), "agent733"),
    (("agent733", "zz"), "zfdms733"),
    (("agent733", "AgentU"), "amiam733"),
    (("agent733", "keyboard"), "kkcoh733"),
    (("agent733", "AA"), "agent733"),
    (("angle733", "key"), "krevi733"),
    (("angle733", "lemon"), "lrszr733"),
    (("angle733", "a"), "angle733"),
    (("angle733", "zz"), "zmfkd733"),
    (("angle733", "AgentU"), "atkyx733"),
    (("angle733", "keyboard"), "krems733"),
    (("angle733", "AA"), "angle733"),
    (("universe733", "key"), "ergfipci733"),
    (("universe733", "lemon"), "frujrcwq733"),
    (("universe733", "a"), "universe733"),
    (("universe733", "zz"), "tmhudqrd733"),
    (("universe733", "AgentU"), "utmixlsk733"),
    (("universe733", "keyboard"), "ergwsrjh733"),
    (("universe733", "AA"), "universe733"),
    (("memory733", "key"), "wikyvw733"),
    (("memory733", "lemon"), "xiycej733"),
    (("memory733", "a"), "memory733"),
    (("memory733", "zz"), "ldlnqx733"),
    (("memory733", "AgentU"), "mkqbks733"),
    (("memory733", "keyboard"), "wikpfy733"),
    (("memory733", "AA"), "memory733"),
    (("stream733", "key"), "cxpoek733"),
    (("stream733", "lemon"), "dxdsnx733"),
    (("stream733", "a"), "stream733"),
    (("stream733", "zz"), "rsqdzl733"),
    (("stream733", "AgentU"), "szvrtg733"),
    (("stream733", "keyboard"), "cxpfom733"),
    (("stream733", "AA"), "stream733"),
    (("context733", "key"), "msldivd733"),
    (("context733", "lemon"), "nszhrix733"),
    (("context733", "a"), "context733"),
    (("context733", "zz"), "bnmsdws733"),
    (("context733", "AgentU"), "curgxrt733"),
    (("context733", "keyboard"), "mslusxk733"),
    (("context733", "AA"), "context733"),
    (("knowledge733", "key"), "urmgpcnkc733"),
    (("knowledge733", "lemon"), "vrakyphss733"),
    (("knowledge733", "a"), "knowledge733"),
    (("knowledge733", "zz"), "jmnvkdcfd733"),
    (("knowledge733", "AgentU"), "ktsjeydmi733"),
    (("knowledge733", "keyboard"), "urmxzeujo733"),
    (("knowledge733", "AA"), "knowledge733"),
    (("vector733", "key"), "fiadsp733"),
    (("vector733", "lemon"), "giohbc733"),
    (("vector733", "a"), "vector733"),
    (("vector733", "zz"), "udbsnq733"),
    (("vector733", "AgentU"), "vkgghl733"),
    (("vector733", "keyboard"), "fiaucr733"),
    (("vector733", "AA"), "vector733"),
    (("processor733", "key"), "zvmmiqcsp733"),
    (("processor733", "lemon"), "avaqrdwaf733"),
    (("processor733", "a"), "processor733"),
    (("processor733", "zz"), "oqnbdrrnq733"),
    (("processor733", "AgentU"), "pxspxmsuv733"),
    (("processor733", "keyboard"), "zvmdssjrb733"),
    (("processor733", "AA"), "processor733"),
    (("reasoning733", "key"), "biycslsre733"),
    (("reasoning733", "lemon"), "cimgbymzu733"),
    (("reasoning733", "a"), "reasoning733"),
    (("reasoning733", "zz"), "qdzrnmhmf733"),
    (("reasoning733", "AgentU"), "rkefhhitk733"),
    (("reasoning733", "keyboard"), "biytcnzqq733"),
    (("reasoning733", "AA"), "reasoning733"),
    (("machine733", "key"), "wearmlo733"),
    (("machine733", "lemon"), "xeovvyi733"),
    (("machine733", "a"), "machine733"),
    (("machine733", "zz"), "lzbghmd733"),
    (("machine733", "AgentU"), "mggubhe733"),
    (("machine733", "keyboard"), "weaiwnv733"),
    (("machine733", "AA"), "machine733"),
    (("learning733", "key"), "viybrgxk733"),
    (("learning733", "lemon"), "wimfatrs733"),
    (("learning733", "a"), "learning733"),
    (("learning733", "zz"), "kdzqmhmf733"),
    (("learning733", "AgentU"), "lkeegcnm733"),
    (("learning733", "keyboard"), "viysbiej733"),
    (("learning733", "AA"), "learning733"),
    (("model733", "key"), "wsbop733"),
    (("model733", "lemon"), "xspsy733"),
    (("model733", "a"), "model733"),
    (("model733", "zz"), "lncdk733"),
    (("model733", "AgentU"), "muhre733"),
    (("model733", "keyboard"), "wsbfz733"),
    (("model733", "AA"), "model733"),
    (("token733", "key"), "dsior733"),
    (("token733", "lemon"), "eswsa733"),
    (("token733", "a"), "token733"),
    (("token733", "zz"), "snjdm733"),
    (("token733", "AgentU"), "tuorg733"),
    (("token733", "keyboard"), "dsifb733"),
    (("token733", "AA"), "token733"),
    (("prompt733", "key"), "zvmwtr733"),
    (("prompt733", "lemon"), "avaace733"),
    (("prompt733", "a"), "prompt733"),
    (("prompt733", "zz"), "oqnlos733"),
    (("prompt733", "AgentU"), "pxszin733"),
    (("prompt733", "keyboard"), "zvmndt733"),
    (("prompt733", "AA"), "prompt733"),
    (("session733", "key"), "ciqcmmx733"),
    (("session733", "lemon"), "diegvzr733"),
    (("session733", "a"), "session733"),
    (("session733", "zz"), "rdrrhnm733"),
    (("session733", "AgentU"), "skwfbin733"),
    (("session733", "keyboard"), "ciqtwoe733"),
    (("session733", "AA"), "session733"),
    (("library733", "key"), "vmzbepi733"),
    (("library733", "lemon"), "wmnfncc733"),
    (("library733", "a"), "library733"),
    (("library733", "zz"), "khaqzqx733"),
    (("library733", "AgentU"), "lofetly733"),
    (("library733", "keyboard"), "vmzsorp733"),
    (("library733", "AA"), "library733"),
    (("service733", "key"), "cipfmao733"),
    (("service733", "lemon"), "didjvni733"),
    (("service733", "a"), "service733"),
    (("service733", "zz"), "rdquhbd733"),
    (("service733", "AgentU"), "skvibwe733"),
    (("service733", "keyboard"), "cipwwcv733"),
    (("service733", "AA"), "service733"),
    (("gateway733", "key"), "qeroayi733"),
    (("gateway733", "lemon"), "refsjlc733"),
    (("gateway733", "a"), "gateway733"),
    (("gateway733", "zz"), "fzsdvzx733"),
    (("gateway733", "AgentU"), "ggxrpuy733"),
    (("gateway733", "keyboard"), "qerfkap733"),
    (("gateway733", "AA"), "gateway733"),
    (("storage733", "key"), "cxmbeeo733"),
    (("storage733", "lemon"), "dxafnri733"),
    (("storage733", "a"), "storage733"),
    (("storage733", "zz"), "rsnqzfd733"),
    (("storage733", "AgentU"), "szsetae733"),
    (("storage733", "keyboard"), "cxmsogv733"),
    (("storage733", "AA"), "storage733"),
    (("network733", "key"), "xirgspu733"),
    (("network733", "lemon"), "yifkbco733"),
    (("network733", "a"), "network733"),
    (("network733", "zz"), "mdsvnqj733"),
    (("network733", "AgentU"), "nkxjhlk733"),
    (("network733", "keyboard"), "xirxcrb733"),
    (("network733", "AA"), "network733"),
    (("latency733", "key"), "verorai733"),
    (("latency733", "lemon"), "wefsanc733"),
    (("latency733", "a"), "latency733"),
    (("latency733", "zz"), "kzsdmbx733"),
    (("latency733", "AgentU"), "lgxrgwy733"),
    (("latency733", "keyboard"), "verfbcp733"),
    (("latency733", "AA"), "latency733"),
    (("buffer733", "key"), "lydpip733"),
    (("buffer733", "lemon"), "myrtrc733"),
    (("buffer733", "a"), "buffer733"),
    (("buffer733", "zz"), "ateedq733"),
    (("buffer733", "AgentU"), "bajsxl733"),
    (("buffer733", "keyboard"), "lydgsr733"),
    (("buffer733", "AA"), "buffer733"),
    (("queue733", "key"), "aycei733"),
    (("queue733", "lemon"), "byqir733"),
    (("queue733", "a"), "queue733"),
    (("queue733", "zz"), "ptdtd733"),
    (("queue733", "AgentU"), "qaihx733"),
    (("queue733", "keyboard"), "aycvs733"),
    (("queue733", "AA"), "queue733"),
    (("worker733", "key"), "gspuip733"),
    (("worker733", "lemon"), "hsdyrc733"),
    (("worker733", "a"), "worker733"),
    (("worker733", "zz"), "vnqjdq733"),
    (("worker733", "AgentU"), "wuvxxl733"),
    (("worker733", "keyboard"), "gsplsr733"),
    (("worker733", "AA"), "worker733"),
    (("kernel733", "key"), "uipxij733"),
    (("kernel733", "lemon"), "vidbrw733"),
    (("kernel733", "a"), "kernel733"),
    (("kernel733", "zz"), "jdqmdk733"),
    (("kernel733", "AgentU"), "kkvaxf733"),
    (("kernel733", "keyboard"), "uiposl733"),
    (("kernel733", "AA"), "kernel733"),
    (("signal733", "key"), "cmexej733"),
    (("signal733", "lemon"), "dmsbnw733"),
    (("signal733", "a"), "signal733"),
    (("signal733", "zz"), "rhfmzk733"),
    (("signal733", "AgentU"), "sokatf733"),
    (("signal733", "keyboard"), "cmeool733"),
    (("signal733", "AA"), "signal733"),
    (("packet733", "key"), "zeauir733"),
    (("packet733", "lemon"), "aeoyre733"),
    (("packet733", "a"), "packet733"),
    (("packet733", "zz"), "ozbjds733"),
    (("packet733", "AgentU"), "pggxxn733"),
    (("packet733", "keyboard"), "zealst733"),
    (("packet733", "AA"), "packet733"),
    (("router733", "key"), "bssdip733"),
    (("router733", "lemon"), "csghrc733"),
    (("router733", "a"), "router733"),
    (("router733", "zz"), "qntsdq733"),
    (("router733", "AgentU"), "ruygxl733"),
    (("router733", "keyboard"), "bssusr733"),
    (("router733", "AA"), "router733"),
    (("cluster733", "key"), "mpscxcb733"),
    (("cluster733", "lemon"), "npgggpv733"),
    (("cluster733", "a"), "cluster733"),
    (("cluster733", "zz"), "bktrsdq733"),
    (("cluster733", "AgentU"), "cryfmyr733"),
    (("cluster733", "keyboard"), "mpsthei733"),
    (("cluster733", "AA"), "cluster733"),
    (("mirror733", "key"), "wmpbsp733"),
    (("mirror733", "lemon"), "xmdfbc733"),
    (("mirror733", "a"), "mirror733"),
    (("mirror733", "zz"), "lhqqnq733"),
    (("mirror733", "AgentU"), "movehl733"),
    (("mirror733", "keyboard"), "wmpscr733"),
    (("mirror733", "AA"), "mirror733"),
    (("filter733", "key"), "pmjdip733"),
    (("filter733", "lemon"), "qmxhrc733"),
    (("filter733", "a"), "filter733"),
    (("filter733", "zz"), "ehksdq733"),
    (("filter733", "AgentU"), "fopgxl733"),
    (("filter733", "keyboard"), "pmjusr733"),
    (("filter733", "AA"), "filter733"),
    (("ranking733", "key"), "belumlq733"),
    (("ranking733", "lemon"), "cezyvyk733"),
    (("ranking733", "a"), "ranking733"),
    (("ranking733", "zz"), "qzmjhmf733"),
    (("ranking733", "AgentU"), "rgrxbhg733"),
    (("ranking733", "keyboard"), "bellwnx733"),
    (("ranking733", "AA"), "ranking733"),
    (("encoding733", "key"), "orayhgxk733"),
    (("encoding733", "lemon"), "procqtrs733"),
    (("encoding733", "a"), "encoding733"),
    (("encoding733", "zz"), "dmbnchmf733"),
    (("encoding733", "AgentU"), "etgbwcnm733"),
    (("encoding733", "keyboard"), "orapriej733"),
    (("encoding733", "AA"), "encoding733"),
    (("mapping733", "key"), "wenzmlq733"),
    (("mapping733", "lemon"), "xebdvyk733"),
    (("mapping733", "a"), "mapping733"),
    (("mapping733", "zz"), "lzoohmf733"),
    (("mapping733", "AgentU"), "mgtcbhg733"),
    (("mapping733", "keyboard"), "wenqwnx733"),
    (("mapping733", "AA"), "mapping733"),
    (("record733", "key"), "biayvb733"),
    (("record733", "lemon"), "cioceo733"),
    (("record733", "a"), "record733"),
    (("record733", "zz"), "qdbnqc733"),
    (("record733", "AgentU"), "rkgbkx733"),
    (("record733", "keyboard"), "biapfd733"),
    (("record733", "AA"), "record733"),
    (("candle733", "key"), "melnpc733"),
    (("candle733", "lemon"), "nezryp733"),
    (("candle733", "a"), "candle733"),
    (("candle733", "zz"), "bzmckd733"),
    (("candle733", "AgentU"), "cgrqey733"),
    (("candle733", "keyboard"), "meleze733"),
    (("candle733", "AA"), "candle733"),
    (("thread733", "key"), "dlpoeb733"),
    (("thread733", "lemon"), "eldsno733"),
    (("thread733", "a"), "thread733"),
    (("thread733", "zz"), "sgqdzc733"),
    (("thread733", "AgentU"), "tnvrtx733"),
    (("thread733", "keyboard"), "dlpfod733"),
    (("thread733", "AA"), "thread733"),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 733: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 733: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "a"),
        "round 733: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 733: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 733: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 733: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", "AA"),
        "round 733: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "key"),
        "bssxh 733: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 733: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "a"),
        "round 733: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 733: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 733: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 733: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", "AA"),
        "round 733: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 733: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 733: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "a"),
        "round 733: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 733: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 733: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 733: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", "AA"),
        "round 733: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 733: the processor reads the record then stops", "key"),
        "bssxh 733: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 733: the processor reads the record then stops", "lemon"),
        "csgbq 733: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 733: the processor reads the record then stops", "a"),
        "round 733: the processor reads the record then stops",
    ),
    (
        ("round 733: the processor reads the record then stops", "zz"),
        "qntmc 733: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 733: the processor reads the record then stops", "AgentU"),
        "ruyaw 733: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 733: the processor reads the record then stops", "keyboard"),
        "bssor 733: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 733: the processor reads the record then stops", "AA"),
        "round 733: the processor reads the record then stops",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "key"),
        "bssxh 733: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "lemon"),
        "csgbq 733: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "a"),
        "round 733: a worker pulls the next task from the queue",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "zz"),
        "qntmc 733: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 733: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "keyboard"),
        "bssor 733: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 733: a worker pulls the next task from the queue", "AA"),
        "round 733: a worker pulls the next task from the queue",
    ),
    (
        ("round 733: signals travel through the network layer", "key"),
        "bssxh 733: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 733: signals travel through the network layer", "lemon"),
        "csgbq 733: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 733: signals travel through the network layer", "a"),
        "round 733: signals travel through the network layer",
    ),
    (
        ("round 733: signals travel through the network layer", "zz"),
        "qntmc 733: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 733: signals travel through the network layer", "AgentU"),
        "ruyaw 733: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 733: signals travel through the network layer", "keyboard"),
        "bssor 733: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 733: signals travel through the network layer", "AA"),
        "round 733: signals travel through the network layer",
    ),
    (
        ("round 733: the gateway routes each request by policy", "key"),
        "bssxh 733: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 733: the gateway routes each request by policy", "lemon"),
        "csgbq 733: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 733: the gateway routes each request by policy", "a"),
        "round 733: the gateway routes each request by policy",
    ),
    (
        ("round 733: the gateway routes each request by policy", "zz"),
        "qntmc 733: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 733: the gateway routes each request by policy", "AgentU"),
        "ruyaw 733: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 733: the gateway routes each request by policy", "keyboard"),
        "bssor 733: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 733: the gateway routes each request by policy", "AA"),
        "round 733: the gateway routes each request by policy",
    ),
    (("round 733: memory grows until the buffer is full", "key"), "bssxh 733: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 733: memory grows until the buffer is full", "lemon"), "csgbq 733: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 733: memory grows until the buffer is full", "a"), "round 733: memory grows until the buffer is full"),
    (("round 733: memory grows until the buffer is full", "zz"), "qntmc 733: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 733: memory grows until the buffer is full", "AgentU"),
        "ruyaw 733: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 733: memory grows until the buffer is full", "keyboard"),
        "bssor 733: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 733: memory grows until the buffer is full", "AA"), "round 733: memory grows until the buffer is full"),
    (("round 733: the cluster mirrors every packet twice", "key"), "bssxh 733: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 733: the cluster mirrors every packet twice", "lemon"),
        "csgbq 733: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 733: the cluster mirrors every packet twice", "a"), "round 733: the cluster mirrors every packet twice"),
    (("round 733: the cluster mirrors every packet twice", "zz"), "qntmc 733: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 733: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 733: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 733: the cluster mirrors every packet twice", "keyboard"),
        "bssor 733: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 733: the cluster mirrors every packet twice", "AA"), "round 733: the cluster mirrors every packet twice"),
    (
        ("round 733: ranking uses tokens learned from the corpus", "key"),
        "bssxh 733: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 733: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", "a"),
        "round 733: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 733: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 733: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 733: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", "AA"),
        "round 733: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 733: a long session ends when the candle dies", "key"),
        "bssxh 733: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 733: a long session ends when the candle dies", "lemon"),
        "csgbq 733: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 733: a long session ends when the candle dies", "a"),
        "round 733: a long session ends when the candle dies",
    ),
    (
        ("round 733: a long session ends when the candle dies", "zz"),
        "qntmc 733: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 733: a long session ends when the candle dies", "AgentU"),
        "ruyaw 733: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 733: a long session ends when the candle dies", "keyboard"),
        "bssor 733: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 733: a long session ends when the candle dies", "AA"),
        "round 733: a long session ends when the candle dies",
    ),
    (("round 733: encode the prompt then map the result", "key"), "bssxh 733: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 733: encode the prompt then map the result", "lemon"), "csgbq 733: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 733: encode the prompt then map the result", "a"), "round 733: encode the prompt then map the result"),
    (("round 733: encode the prompt then map the result", "zz"), "qntmc 733: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 733: encode the prompt then map the result", "AgentU"),
        "ruyaw 733: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 733: encode the prompt then map the result", "keyboard"),
        "bssor 733: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 733: encode the prompt then map the result", "AA"), "round 733: encode the prompt then map the result"),
    (("round 733: the kernel wakes the worker at dawn", "key"), "bssxh 733: rri iovlop ukocc xfo ambocb er neux"),
    (("round 733: the kernel wakes the worker at dawn", "lemon"), "csgbq 733: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 733: the kernel wakes the worker at dawn", "a"), "round 733: the kernel wakes the worker at dawn"),
    (("round 733: the kernel wakes the worker at dawn", "zz"), "qntmc 733: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 733: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 733: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 733: the kernel wakes the worker at dawn", "keyboard"), "bssor 733: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 733: the kernel wakes the worker at dawn", "AA"), "round 733: the kernel wakes the worker at dawn"),
    (("round 733: service latency drops after the patch", "key"), "bssxh 733: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 733: service latency drops after the patch", "lemon"), "csgbq 733: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 733: service latency drops after the patch", "a"), "round 733: service latency drops after the patch"),
    (("round 733: service latency drops after the patch", "zz"), "qntmc 733: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 733: service latency drops after the patch", "AgentU"),
        "ruyaw 733: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 733: service latency drops after the patch", "keyboard"),
        "bssor 733: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 733: service latency drops after the patch", "AA"), "round 733: service latency drops after the patch"),
    (
        ("round 733: the library caches every vector it sees", "key"),
        "bssxh 733: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 733: the library caches every vector it sees", "lemon"),
        "csgbq 733: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 733: the library caches every vector it sees", "a"), "round 733: the library caches every vector it sees"),
    (
        ("round 733: the library caches every vector it sees", "zz"),
        "qntmc 733: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 733: the library caches every vector it sees", "AgentU"),
        "ruyaw 733: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 733: the library caches every vector it sees", "keyboard"),
        "bssor 733: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 733: the library caches every vector it sees", "AA"),
        "round 733: the library caches every vector it sees",
    ),
    (("round 733: agents argue then the debate resolves", "key"), "bssxh 733: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 733: agents argue then the debate resolves", "lemon"), "csgbq 733: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 733: agents argue then the debate resolves", "a"), "round 733: agents argue then the debate resolves"),
    (("round 733: agents argue then the debate resolves", "zz"), "qntmc 733: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 733: agents argue then the debate resolves", "AgentU"),
        "ruyaw 733: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 733: agents argue then the debate resolves", "keyboard"),
        "bssor 733: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 733: agents argue then the debate resolves", "AA"), "round 733: agents argue then the debate resolves"),
    (("round 733: the filter keeps only strong matches", "key"), "bssxh 733: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 733: the filter keeps only strong matches", "lemon"), "csgbq 733: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 733: the filter keeps only strong matches", "a"), "round 733: the filter keeps only strong matches"),
    (("round 733: the filter keeps only strong matches", "zz"), "qntmc 733: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 733: the filter keeps only strong matches", "AgentU"), "ruyaw 733: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 733: the filter keeps only strong matches", "keyboard"),
        "bssor 733: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 733: the filter keeps only strong matches", "AA"), "round 733: the filter keeps only strong matches"),
    (("round 733: the model answers with a short reply", "key"), "bssxh 733: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 733: the model answers with a short reply", "lemon"), "csgbq 733: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 733: the model answers with a short reply", "a"), "round 733: the model answers with a short reply"),
    (("round 733: the model answers with a short reply", "zz"), "qntmc 733: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 733: the model answers with a short reply", "AgentU"), "ruyaw 733: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 733: the model answers with a short reply", "keyboard"),
        "bssor 733: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 733: the model answers with a short reply", "AA"), "round 733: the model answers with a short reply"),
    (
        ("round 733: the recorder stores the reasoning trace", "key"),
        "bssxh 733: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 733: the recorder stores the reasoning trace", "lemon"),
        "csgbq 733: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 733: the recorder stores the reasoning trace", "a"), "round 733: the recorder stores the reasoning trace"),
    (
        ("round 733: the recorder stores the reasoning trace", "zz"),
        "qntmc 733: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 733: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 733: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 733: the recorder stores the reasoning trace", "keyboard"),
        "bssor 733: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 733: the recorder stores the reasoning trace", "AA"),
        "round 733: the recorder stores the reasoning trace",
    ),
    (("round 733: the angel watches the processor run", "key"), "bssxh 733: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 733: the angel watches the processor run", "lemon"), "csgbq 733: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 733: the angel watches the processor run", "a"), "round 733: the angel watches the processor run"),
    (("round 733: the angel watches the processor run", "zz"), "qntmc 733: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 733: the angel watches the processor run", "AgentU"), "ruyaw 733: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 733: the angel watches the processor run", "keyboard"), "bssor 733: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 733: the angel watches the processor run", "AA"), "round 733: the angel watches the processor run"),
    (("round 733: angle of the vector decides the match", "key"), "bssxh 733: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 733: angle of the vector decides the match", "lemon"), "csgbq 733: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 733: angle of the vector decides the match", "a"), "round 733: angle of the vector decides the match"),
    (("round 733: angle of the vector decides the match", "zz"), "qntmc 733: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 733: angle of the vector decides the match", "AgentU"),
        "ruyaw 733: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 733: angle of the vector decides the match", "keyboard"),
        "bssor 733: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 733: angle of the vector decides the match", "AA"), "round 733: angle of the vector decides the match"),
    (
        ("round 733: the candle burns twice as long at night", "key"),
        "bssxh 733: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 733: the candle burns twice as long at night", "lemon"),
        "csgbq 733: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 733: the candle burns twice as long at night", "a"), "round 733: the candle burns twice as long at night"),
    (
        ("round 733: the candle burns twice as long at night", "zz"),
        "qntmc 733: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 733: the candle burns twice as long at night", "AgentU"),
        "ruyaw 733: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 733: the candle burns twice as long at night", "keyboard"),
        "bssor 733: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 733: the candle burns twice as long at night", "AA"),
        "round 733: the candle burns twice as long at night",
    ),
    (("round 733: a mirror of the universe in one line", "key"), "bssxh 733: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 733: a mirror of the universe in one line", "lemon"), "csgbq 733: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 733: a mirror of the universe in one line", "a"), "round 733: a mirror of the universe in one line"),
    (("round 733: a mirror of the universe in one line", "zz"), "qntmc 733: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 733: a mirror of the universe in one line", "AgentU"), "ruyaw 733: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 733: a mirror of the universe in one line", "keyboard"),
        "bssor 733: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 733: a mirror of the universe in one line", "AA"), "round 733: a mirror of the universe in one line"),
    (("round 733: the queue drains before the storm", "key"), "bssxh 733: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 733: the queue drains before the storm", "lemon"), "csgbq 733: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 733: the queue drains before the storm", "a"), "round 733: the queue drains before the storm"),
    (("round 733: the queue drains before the storm", "zz"), "qntmc 733: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 733: the queue drains before the storm", "AgentU"), "ruyaw 733: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 733: the queue drains before the storm", "keyboard"), "bssor 733: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 733: the queue drains before the storm", "AA"), "round 733: the queue drains before the storm"),
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
