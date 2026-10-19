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
    (("kitten176", "key"), "umrdil176"),
    (("kitten176", "lemon"), "vmfhry176"),
    (("kitten176", "a"), "kitten176"),
    (("kitten176", "zz"), "jhssdm176"),
    (("kitten176", "AgentU"), "koxgxh176"),
    (("kitten176", "keyboard"), "umrusn176"),
    (("kitten176", "AA"), "kitten176"),
    (("sitting176", "key"), "cmrdmlq176"),
    (("sitting176", "lemon"), "dmfhvyk176"),
    (("sitting176", "a"), "sitting176"),
    (("sitting176", "zz"), "rhsshmf176"),
    (("sitting176", "AgentU"), "soxgbhg176"),
    (("sitting176", "keyboard"), "cmruwnx176"),
    (("sitting176", "AA"), "sitting176"),
    (("agent176", "key"), "kkcxx176"),
    (("agent176", "lemon"), "lkqbg176"),
    (("agent176", "a"), "agent176"),
    (("agent176", "zz"), "zfdms176"),
    (("agent176", "AgentU"), "amiam176"),
    (("agent176", "keyboard"), "kkcoh176"),
    (("agent176", "AA"), "agent176"),
    (("angle176", "key"), "krevi176"),
    (("angle176", "lemon"), "lrszr176"),
    (("angle176", "a"), "angle176"),
    (("angle176", "zz"), "zmfkd176"),
    (("angle176", "AgentU"), "atkyx176"),
    (("angle176", "keyboard"), "krems176"),
    (("angle176", "AA"), "angle176"),
    (("universe176", "key"), "ergfipci176"),
    (("universe176", "lemon"), "frujrcwq176"),
    (("universe176", "a"), "universe176"),
    (("universe176", "zz"), "tmhudqrd176"),
    (("universe176", "AgentU"), "utmixlsk176"),
    (("universe176", "keyboard"), "ergwsrjh176"),
    (("universe176", "AA"), "universe176"),
    (("memory176", "key"), "wikyvw176"),
    (("memory176", "lemon"), "xiycej176"),
    (("memory176", "a"), "memory176"),
    (("memory176", "zz"), "ldlnqx176"),
    (("memory176", "AgentU"), "mkqbks176"),
    (("memory176", "keyboard"), "wikpfy176"),
    (("memory176", "AA"), "memory176"),
    (("stream176", "key"), "cxpoek176"),
    (("stream176", "lemon"), "dxdsnx176"),
    (("stream176", "a"), "stream176"),
    (("stream176", "zz"), "rsqdzl176"),
    (("stream176", "AgentU"), "szvrtg176"),
    (("stream176", "keyboard"), "cxpfom176"),
    (("stream176", "AA"), "stream176"),
    (("context176", "key"), "msldivd176"),
    (("context176", "lemon"), "nszhrix176"),
    (("context176", "a"), "context176"),
    (("context176", "zz"), "bnmsdws176"),
    (("context176", "AgentU"), "curgxrt176"),
    (("context176", "keyboard"), "mslusxk176"),
    (("context176", "AA"), "context176"),
    (("knowledge176", "key"), "urmgpcnkc176"),
    (("knowledge176", "lemon"), "vrakyphss176"),
    (("knowledge176", "a"), "knowledge176"),
    (("knowledge176", "zz"), "jmnvkdcfd176"),
    (("knowledge176", "AgentU"), "ktsjeydmi176"),
    (("knowledge176", "keyboard"), "urmxzeujo176"),
    (("knowledge176", "AA"), "knowledge176"),
    (("vector176", "key"), "fiadsp176"),
    (("vector176", "lemon"), "giohbc176"),
    (("vector176", "a"), "vector176"),
    (("vector176", "zz"), "udbsnq176"),
    (("vector176", "AgentU"), "vkgghl176"),
    (("vector176", "keyboard"), "fiaucr176"),
    (("vector176", "AA"), "vector176"),
    (("processor176", "key"), "zvmmiqcsp176"),
    (("processor176", "lemon"), "avaqrdwaf176"),
    (("processor176", "a"), "processor176"),
    (("processor176", "zz"), "oqnbdrrnq176"),
    (("processor176", "AgentU"), "pxspxmsuv176"),
    (("processor176", "keyboard"), "zvmdssjrb176"),
    (("processor176", "AA"), "processor176"),
    (("reasoning176", "key"), "biycslsre176"),
    (("reasoning176", "lemon"), "cimgbymzu176"),
    (("reasoning176", "a"), "reasoning176"),
    (("reasoning176", "zz"), "qdzrnmhmf176"),
    (("reasoning176", "AgentU"), "rkefhhitk176"),
    (("reasoning176", "keyboard"), "biytcnzqq176"),
    (("reasoning176", "AA"), "reasoning176"),
    (("machine176", "key"), "wearmlo176"),
    (("machine176", "lemon"), "xeovvyi176"),
    (("machine176", "a"), "machine176"),
    (("machine176", "zz"), "lzbghmd176"),
    (("machine176", "AgentU"), "mggubhe176"),
    (("machine176", "keyboard"), "weaiwnv176"),
    (("machine176", "AA"), "machine176"),
    (("learning176", "key"), "viybrgxk176"),
    (("learning176", "lemon"), "wimfatrs176"),
    (("learning176", "a"), "learning176"),
    (("learning176", "zz"), "kdzqmhmf176"),
    (("learning176", "AgentU"), "lkeegcnm176"),
    (("learning176", "keyboard"), "viysbiej176"),
    (("learning176", "AA"), "learning176"),
    (("model176", "key"), "wsbop176"),
    (("model176", "lemon"), "xspsy176"),
    (("model176", "a"), "model176"),
    (("model176", "zz"), "lncdk176"),
    (("model176", "AgentU"), "muhre176"),
    (("model176", "keyboard"), "wsbfz176"),
    (("model176", "AA"), "model176"),
    (("token176", "key"), "dsior176"),
    (("token176", "lemon"), "eswsa176"),
    (("token176", "a"), "token176"),
    (("token176", "zz"), "snjdm176"),
    (("token176", "AgentU"), "tuorg176"),
    (("token176", "keyboard"), "dsifb176"),
    (("token176", "AA"), "token176"),
    (("prompt176", "key"), "zvmwtr176"),
    (("prompt176", "lemon"), "avaace176"),
    (("prompt176", "a"), "prompt176"),
    (("prompt176", "zz"), "oqnlos176"),
    (("prompt176", "AgentU"), "pxszin176"),
    (("prompt176", "keyboard"), "zvmndt176"),
    (("prompt176", "AA"), "prompt176"),
    (("session176", "key"), "ciqcmmx176"),
    (("session176", "lemon"), "diegvzr176"),
    (("session176", "a"), "session176"),
    (("session176", "zz"), "rdrrhnm176"),
    (("session176", "AgentU"), "skwfbin176"),
    (("session176", "keyboard"), "ciqtwoe176"),
    (("session176", "AA"), "session176"),
    (("library176", "key"), "vmzbepi176"),
    (("library176", "lemon"), "wmnfncc176"),
    (("library176", "a"), "library176"),
    (("library176", "zz"), "khaqzqx176"),
    (("library176", "AgentU"), "lofetly176"),
    (("library176", "keyboard"), "vmzsorp176"),
    (("library176", "AA"), "library176"),
    (("service176", "key"), "cipfmao176"),
    (("service176", "lemon"), "didjvni176"),
    (("service176", "a"), "service176"),
    (("service176", "zz"), "rdquhbd176"),
    (("service176", "AgentU"), "skvibwe176"),
    (("service176", "keyboard"), "cipwwcv176"),
    (("service176", "AA"), "service176"),
    (("gateway176", "key"), "qeroayi176"),
    (("gateway176", "lemon"), "refsjlc176"),
    (("gateway176", "a"), "gateway176"),
    (("gateway176", "zz"), "fzsdvzx176"),
    (("gateway176", "AgentU"), "ggxrpuy176"),
    (("gateway176", "keyboard"), "qerfkap176"),
    (("gateway176", "AA"), "gateway176"),
    (("storage176", "key"), "cxmbeeo176"),
    (("storage176", "lemon"), "dxafnri176"),
    (("storage176", "a"), "storage176"),
    (("storage176", "zz"), "rsnqzfd176"),
    (("storage176", "AgentU"), "szsetae176"),
    (("storage176", "keyboard"), "cxmsogv176"),
    (("storage176", "AA"), "storage176"),
    (("network176", "key"), "xirgspu176"),
    (("network176", "lemon"), "yifkbco176"),
    (("network176", "a"), "network176"),
    (("network176", "zz"), "mdsvnqj176"),
    (("network176", "AgentU"), "nkxjhlk176"),
    (("network176", "keyboard"), "xirxcrb176"),
    (("network176", "AA"), "network176"),
    (("latency176", "key"), "verorai176"),
    (("latency176", "lemon"), "wefsanc176"),
    (("latency176", "a"), "latency176"),
    (("latency176", "zz"), "kzsdmbx176"),
    (("latency176", "AgentU"), "lgxrgwy176"),
    (("latency176", "keyboard"), "verfbcp176"),
    (("latency176", "AA"), "latency176"),
    (("buffer176", "key"), "lydpip176"),
    (("buffer176", "lemon"), "myrtrc176"),
    (("buffer176", "a"), "buffer176"),
    (("buffer176", "zz"), "ateedq176"),
    (("buffer176", "AgentU"), "bajsxl176"),
    (("buffer176", "keyboard"), "lydgsr176"),
    (("buffer176", "AA"), "buffer176"),
    (("queue176", "key"), "aycei176"),
    (("queue176", "lemon"), "byqir176"),
    (("queue176", "a"), "queue176"),
    (("queue176", "zz"), "ptdtd176"),
    (("queue176", "AgentU"), "qaihx176"),
    (("queue176", "keyboard"), "aycvs176"),
    (("queue176", "AA"), "queue176"),
    (("worker176", "key"), "gspuip176"),
    (("worker176", "lemon"), "hsdyrc176"),
    (("worker176", "a"), "worker176"),
    (("worker176", "zz"), "vnqjdq176"),
    (("worker176", "AgentU"), "wuvxxl176"),
    (("worker176", "keyboard"), "gsplsr176"),
    (("worker176", "AA"), "worker176"),
    (("kernel176", "key"), "uipxij176"),
    (("kernel176", "lemon"), "vidbrw176"),
    (("kernel176", "a"), "kernel176"),
    (("kernel176", "zz"), "jdqmdk176"),
    (("kernel176", "AgentU"), "kkvaxf176"),
    (("kernel176", "keyboard"), "uiposl176"),
    (("kernel176", "AA"), "kernel176"),
    (("signal176", "key"), "cmexej176"),
    (("signal176", "lemon"), "dmsbnw176"),
    (("signal176", "a"), "signal176"),
    (("signal176", "zz"), "rhfmzk176"),
    (("signal176", "AgentU"), "sokatf176"),
    (("signal176", "keyboard"), "cmeool176"),
    (("signal176", "AA"), "signal176"),
    (("packet176", "key"), "zeauir176"),
    (("packet176", "lemon"), "aeoyre176"),
    (("packet176", "a"), "packet176"),
    (("packet176", "zz"), "ozbjds176"),
    (("packet176", "AgentU"), "pggxxn176"),
    (("packet176", "keyboard"), "zealst176"),
    (("packet176", "AA"), "packet176"),
    (("router176", "key"), "bssdip176"),
    (("router176", "lemon"), "csghrc176"),
    (("router176", "a"), "router176"),
    (("router176", "zz"), "qntsdq176"),
    (("router176", "AgentU"), "ruygxl176"),
    (("router176", "keyboard"), "bssusr176"),
    (("router176", "AA"), "router176"),
    (("cluster176", "key"), "mpscxcb176"),
    (("cluster176", "lemon"), "npgggpv176"),
    (("cluster176", "a"), "cluster176"),
    (("cluster176", "zz"), "bktrsdq176"),
    (("cluster176", "AgentU"), "cryfmyr176"),
    (("cluster176", "keyboard"), "mpsthei176"),
    (("cluster176", "AA"), "cluster176"),
    (("mirror176", "key"), "wmpbsp176"),
    (("mirror176", "lemon"), "xmdfbc176"),
    (("mirror176", "a"), "mirror176"),
    (("mirror176", "zz"), "lhqqnq176"),
    (("mirror176", "AgentU"), "movehl176"),
    (("mirror176", "keyboard"), "wmpscr176"),
    (("mirror176", "AA"), "mirror176"),
    (("filter176", "key"), "pmjdip176"),
    (("filter176", "lemon"), "qmxhrc176"),
    (("filter176", "a"), "filter176"),
    (("filter176", "zz"), "ehksdq176"),
    (("filter176", "AgentU"), "fopgxl176"),
    (("filter176", "keyboard"), "pmjusr176"),
    (("filter176", "AA"), "filter176"),
    (("ranking176", "key"), "belumlq176"),
    (("ranking176", "lemon"), "cezyvyk176"),
    (("ranking176", "a"), "ranking176"),
    (("ranking176", "zz"), "qzmjhmf176"),
    (("ranking176", "AgentU"), "rgrxbhg176"),
    (("ranking176", "keyboard"), "bellwnx176"),
    (("ranking176", "AA"), "ranking176"),
    (("encoding176", "key"), "orayhgxk176"),
    (("encoding176", "lemon"), "procqtrs176"),
    (("encoding176", "a"), "encoding176"),
    (("encoding176", "zz"), "dmbnchmf176"),
    (("encoding176", "AgentU"), "etgbwcnm176"),
    (("encoding176", "keyboard"), "orapriej176"),
    (("encoding176", "AA"), "encoding176"),
    (("mapping176", "key"), "wenzmlq176"),
    (("mapping176", "lemon"), "xebdvyk176"),
    (("mapping176", "a"), "mapping176"),
    (("mapping176", "zz"), "lzoohmf176"),
    (("mapping176", "AgentU"), "mgtcbhg176"),
    (("mapping176", "keyboard"), "wenqwnx176"),
    (("mapping176", "AA"), "mapping176"),
    (("record176", "key"), "biayvb176"),
    (("record176", "lemon"), "cioceo176"),
    (("record176", "a"), "record176"),
    (("record176", "zz"), "qdbnqc176"),
    (("record176", "AgentU"), "rkgbkx176"),
    (("record176", "keyboard"), "biapfd176"),
    (("record176", "AA"), "record176"),
    (("candle176", "key"), "melnpc176"),
    (("candle176", "lemon"), "nezryp176"),
    (("candle176", "a"), "candle176"),
    (("candle176", "zz"), "bzmckd176"),
    (("candle176", "AgentU"), "cgrqey176"),
    (("candle176", "keyboard"), "meleze176"),
    (("candle176", "AA"), "candle176"),
    (("thread176", "key"), "dlpoeb176"),
    (("thread176", "lemon"), "eldsno176"),
    (("thread176", "a"), "thread176"),
    (("thread176", "zz"), "sgqdzc176"),
    (("thread176", "AgentU"), "tnvrtx176"),
    (("thread176", "keyboard"), "dlpfod176"),
    (("thread176", "AA"), "thread176"),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 176: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 176: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "a"),
        "round 176: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 176: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 176: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 176: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", "AA"),
        "round 176: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "key"),
        "bssxh 176: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 176: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "a"),
        "round 176: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 176: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 176: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 176: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", "AA"),
        "round 176: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 176: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 176: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "a"),
        "round 176: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 176: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 176: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 176: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", "AA"),
        "round 176: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 176: the processor reads the record then stops", "key"),
        "bssxh 176: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 176: the processor reads the record then stops", "lemon"),
        "csgbq 176: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 176: the processor reads the record then stops", "a"),
        "round 176: the processor reads the record then stops",
    ),
    (
        ("round 176: the processor reads the record then stops", "zz"),
        "qntmc 176: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 176: the processor reads the record then stops", "AgentU"),
        "ruyaw 176: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 176: the processor reads the record then stops", "keyboard"),
        "bssor 176: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 176: the processor reads the record then stops", "AA"),
        "round 176: the processor reads the record then stops",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "key"),
        "bssxh 176: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "lemon"),
        "csgbq 176: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "a"),
        "round 176: a worker pulls the next task from the queue",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "zz"),
        "qntmc 176: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 176: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "keyboard"),
        "bssor 176: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 176: a worker pulls the next task from the queue", "AA"),
        "round 176: a worker pulls the next task from the queue",
    ),
    (
        ("round 176: signals travel through the network layer", "key"),
        "bssxh 176: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 176: signals travel through the network layer", "lemon"),
        "csgbq 176: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 176: signals travel through the network layer", "a"),
        "round 176: signals travel through the network layer",
    ),
    (
        ("round 176: signals travel through the network layer", "zz"),
        "qntmc 176: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 176: signals travel through the network layer", "AgentU"),
        "ruyaw 176: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 176: signals travel through the network layer", "keyboard"),
        "bssor 176: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 176: signals travel through the network layer", "AA"),
        "round 176: signals travel through the network layer",
    ),
    (
        ("round 176: the gateway routes each request by policy", "key"),
        "bssxh 176: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 176: the gateway routes each request by policy", "lemon"),
        "csgbq 176: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 176: the gateway routes each request by policy", "a"),
        "round 176: the gateway routes each request by policy",
    ),
    (
        ("round 176: the gateway routes each request by policy", "zz"),
        "qntmc 176: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 176: the gateway routes each request by policy", "AgentU"),
        "ruyaw 176: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 176: the gateway routes each request by policy", "keyboard"),
        "bssor 176: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 176: the gateway routes each request by policy", "AA"),
        "round 176: the gateway routes each request by policy",
    ),
    (("round 176: memory grows until the buffer is full", "key"), "bssxh 176: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 176: memory grows until the buffer is full", "lemon"), "csgbq 176: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 176: memory grows until the buffer is full", "a"), "round 176: memory grows until the buffer is full"),
    (("round 176: memory grows until the buffer is full", "zz"), "qntmc 176: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 176: memory grows until the buffer is full", "AgentU"),
        "ruyaw 176: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 176: memory grows until the buffer is full", "keyboard"),
        "bssor 176: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 176: memory grows until the buffer is full", "AA"), "round 176: memory grows until the buffer is full"),
    (("round 176: the cluster mirrors every packet twice", "key"), "bssxh 176: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 176: the cluster mirrors every packet twice", "lemon"),
        "csgbq 176: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 176: the cluster mirrors every packet twice", "a"), "round 176: the cluster mirrors every packet twice"),
    (("round 176: the cluster mirrors every packet twice", "zz"), "qntmc 176: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 176: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 176: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 176: the cluster mirrors every packet twice", "keyboard"),
        "bssor 176: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 176: the cluster mirrors every packet twice", "AA"), "round 176: the cluster mirrors every packet twice"),
    (
        ("round 176: ranking uses tokens learned from the corpus", "key"),
        "bssxh 176: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 176: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", "a"),
        "round 176: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 176: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 176: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 176: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", "AA"),
        "round 176: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 176: a long session ends when the candle dies", "key"),
        "bssxh 176: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 176: a long session ends when the candle dies", "lemon"),
        "csgbq 176: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 176: a long session ends when the candle dies", "a"),
        "round 176: a long session ends when the candle dies",
    ),
    (
        ("round 176: a long session ends when the candle dies", "zz"),
        "qntmc 176: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 176: a long session ends when the candle dies", "AgentU"),
        "ruyaw 176: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 176: a long session ends when the candle dies", "keyboard"),
        "bssor 176: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 176: a long session ends when the candle dies", "AA"),
        "round 176: a long session ends when the candle dies",
    ),
    (("round 176: encode the prompt then map the result", "key"), "bssxh 176: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 176: encode the prompt then map the result", "lemon"), "csgbq 176: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 176: encode the prompt then map the result", "a"), "round 176: encode the prompt then map the result"),
    (("round 176: encode the prompt then map the result", "zz"), "qntmc 176: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 176: encode the prompt then map the result", "AgentU"),
        "ruyaw 176: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 176: encode the prompt then map the result", "keyboard"),
        "bssor 176: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 176: encode the prompt then map the result", "AA"), "round 176: encode the prompt then map the result"),
    (("round 176: the kernel wakes the worker at dawn", "key"), "bssxh 176: rri iovlop ukocc xfo ambocb er neux"),
    (("round 176: the kernel wakes the worker at dawn", "lemon"), "csgbq 176: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 176: the kernel wakes the worker at dawn", "a"), "round 176: the kernel wakes the worker at dawn"),
    (("round 176: the kernel wakes the worker at dawn", "zz"), "qntmc 176: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 176: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 176: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 176: the kernel wakes the worker at dawn", "keyboard"), "bssor 176: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 176: the kernel wakes the worker at dawn", "AA"), "round 176: the kernel wakes the worker at dawn"),
    (("round 176: service latency drops after the patch", "key"), "bssxh 176: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 176: service latency drops after the patch", "lemon"), "csgbq 176: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 176: service latency drops after the patch", "a"), "round 176: service latency drops after the patch"),
    (("round 176: service latency drops after the patch", "zz"), "qntmc 176: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 176: service latency drops after the patch", "AgentU"),
        "ruyaw 176: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 176: service latency drops after the patch", "keyboard"),
        "bssor 176: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 176: service latency drops after the patch", "AA"), "round 176: service latency drops after the patch"),
    (
        ("round 176: the library caches every vector it sees", "key"),
        "bssxh 176: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 176: the library caches every vector it sees", "lemon"),
        "csgbq 176: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 176: the library caches every vector it sees", "a"), "round 176: the library caches every vector it sees"),
    (
        ("round 176: the library caches every vector it sees", "zz"),
        "qntmc 176: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 176: the library caches every vector it sees", "AgentU"),
        "ruyaw 176: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 176: the library caches every vector it sees", "keyboard"),
        "bssor 176: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 176: the library caches every vector it sees", "AA"),
        "round 176: the library caches every vector it sees",
    ),
    (("round 176: agents argue then the debate resolves", "key"), "bssxh 176: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 176: agents argue then the debate resolves", "lemon"), "csgbq 176: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 176: agents argue then the debate resolves", "a"), "round 176: agents argue then the debate resolves"),
    (("round 176: agents argue then the debate resolves", "zz"), "qntmc 176: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 176: agents argue then the debate resolves", "AgentU"),
        "ruyaw 176: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 176: agents argue then the debate resolves", "keyboard"),
        "bssor 176: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 176: agents argue then the debate resolves", "AA"), "round 176: agents argue then the debate resolves"),
    (("round 176: the filter keeps only strong matches", "key"), "bssxh 176: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 176: the filter keeps only strong matches", "lemon"), "csgbq 176: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 176: the filter keeps only strong matches", "a"), "round 176: the filter keeps only strong matches"),
    (("round 176: the filter keeps only strong matches", "zz"), "qntmc 176: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 176: the filter keeps only strong matches", "AgentU"), "ruyaw 176: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 176: the filter keeps only strong matches", "keyboard"),
        "bssor 176: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 176: the filter keeps only strong matches", "AA"), "round 176: the filter keeps only strong matches"),
    (("round 176: the model answers with a short reply", "key"), "bssxh 176: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 176: the model answers with a short reply", "lemon"), "csgbq 176: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 176: the model answers with a short reply", "a"), "round 176: the model answers with a short reply"),
    (("round 176: the model answers with a short reply", "zz"), "qntmc 176: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 176: the model answers with a short reply", "AgentU"), "ruyaw 176: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 176: the model answers with a short reply", "keyboard"),
        "bssor 176: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 176: the model answers with a short reply", "AA"), "round 176: the model answers with a short reply"),
    (
        ("round 176: the recorder stores the reasoning trace", "key"),
        "bssxh 176: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 176: the recorder stores the reasoning trace", "lemon"),
        "csgbq 176: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 176: the recorder stores the reasoning trace", "a"), "round 176: the recorder stores the reasoning trace"),
    (
        ("round 176: the recorder stores the reasoning trace", "zz"),
        "qntmc 176: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 176: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 176: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 176: the recorder stores the reasoning trace", "keyboard"),
        "bssor 176: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 176: the recorder stores the reasoning trace", "AA"),
        "round 176: the recorder stores the reasoning trace",
    ),
    (("round 176: the angel watches the processor run", "key"), "bssxh 176: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 176: the angel watches the processor run", "lemon"), "csgbq 176: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 176: the angel watches the processor run", "a"), "round 176: the angel watches the processor run"),
    (("round 176: the angel watches the processor run", "zz"), "qntmc 176: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 176: the angel watches the processor run", "AgentU"), "ruyaw 176: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 176: the angel watches the processor run", "keyboard"), "bssor 176: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 176: the angel watches the processor run", "AA"), "round 176: the angel watches the processor run"),
    (("round 176: angle of the vector decides the match", "key"), "bssxh 176: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 176: angle of the vector decides the match", "lemon"), "csgbq 176: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 176: angle of the vector decides the match", "a"), "round 176: angle of the vector decides the match"),
    (("round 176: angle of the vector decides the match", "zz"), "qntmc 176: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 176: angle of the vector decides the match", "AgentU"),
        "ruyaw 176: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 176: angle of the vector decides the match", "keyboard"),
        "bssor 176: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 176: angle of the vector decides the match", "AA"), "round 176: angle of the vector decides the match"),
    (
        ("round 176: the candle burns twice as long at night", "key"),
        "bssxh 176: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 176: the candle burns twice as long at night", "lemon"),
        "csgbq 176: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 176: the candle burns twice as long at night", "a"), "round 176: the candle burns twice as long at night"),
    (
        ("round 176: the candle burns twice as long at night", "zz"),
        "qntmc 176: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 176: the candle burns twice as long at night", "AgentU"),
        "ruyaw 176: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 176: the candle burns twice as long at night", "keyboard"),
        "bssor 176: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 176: the candle burns twice as long at night", "AA"),
        "round 176: the candle burns twice as long at night",
    ),
    (("round 176: a mirror of the universe in one line", "key"), "bssxh 176: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 176: a mirror of the universe in one line", "lemon"), "csgbq 176: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 176: a mirror of the universe in one line", "a"), "round 176: a mirror of the universe in one line"),
    (("round 176: a mirror of the universe in one line", "zz"), "qntmc 176: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 176: a mirror of the universe in one line", "AgentU"), "ruyaw 176: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 176: a mirror of the universe in one line", "keyboard"),
        "bssor 176: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 176: a mirror of the universe in one line", "AA"), "round 176: a mirror of the universe in one line"),
    (("round 176: the queue drains before the storm", "key"), "bssxh 176: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 176: the queue drains before the storm", "lemon"), "csgbq 176: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 176: the queue drains before the storm", "a"), "round 176: the queue drains before the storm"),
    (("round 176: the queue drains before the storm", "zz"), "qntmc 176: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 176: the queue drains before the storm", "AgentU"), "ruyaw 176: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 176: the queue drains before the storm", "keyboard"), "bssor 176: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 176: the queue drains before the storm", "AA"), "round 176: the queue drains before the storm"),
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
