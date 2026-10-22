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
    (("kitten114", "key"), "umrdil114"),
    (("kitten114", "lemon"), "vmfhry114"),
    (("kitten114", "a"), "kitten114"),
    (("kitten114", "zz"), "jhssdm114"),
    (("kitten114", "AgentU"), "koxgxh114"),
    (("kitten114", "keyboard"), "umrusn114"),
    (("kitten114", "AA"), "kitten114"),
    (("sitting114", "key"), "cmrdmlq114"),
    (("sitting114", "lemon"), "dmfhvyk114"),
    (("sitting114", "a"), "sitting114"),
    (("sitting114", "zz"), "rhsshmf114"),
    (("sitting114", "AgentU"), "soxgbhg114"),
    (("sitting114", "keyboard"), "cmruwnx114"),
    (("sitting114", "AA"), "sitting114"),
    (("agent114", "key"), "kkcxx114"),
    (("agent114", "lemon"), "lkqbg114"),
    (("agent114", "a"), "agent114"),
    (("agent114", "zz"), "zfdms114"),
    (("agent114", "AgentU"), "amiam114"),
    (("agent114", "keyboard"), "kkcoh114"),
    (("agent114", "AA"), "agent114"),
    (("angle114", "key"), "krevi114"),
    (("angle114", "lemon"), "lrszr114"),
    (("angle114", "a"), "angle114"),
    (("angle114", "zz"), "zmfkd114"),
    (("angle114", "AgentU"), "atkyx114"),
    (("angle114", "keyboard"), "krems114"),
    (("angle114", "AA"), "angle114"),
    (("universe114", "key"), "ergfipci114"),
    (("universe114", "lemon"), "frujrcwq114"),
    (("universe114", "a"), "universe114"),
    (("universe114", "zz"), "tmhudqrd114"),
    (("universe114", "AgentU"), "utmixlsk114"),
    (("universe114", "keyboard"), "ergwsrjh114"),
    (("universe114", "AA"), "universe114"),
    (("memory114", "key"), "wikyvw114"),
    (("memory114", "lemon"), "xiycej114"),
    (("memory114", "a"), "memory114"),
    (("memory114", "zz"), "ldlnqx114"),
    (("memory114", "AgentU"), "mkqbks114"),
    (("memory114", "keyboard"), "wikpfy114"),
    (("memory114", "AA"), "memory114"),
    (("stream114", "key"), "cxpoek114"),
    (("stream114", "lemon"), "dxdsnx114"),
    (("stream114", "a"), "stream114"),
    (("stream114", "zz"), "rsqdzl114"),
    (("stream114", "AgentU"), "szvrtg114"),
    (("stream114", "keyboard"), "cxpfom114"),
    (("stream114", "AA"), "stream114"),
    (("context114", "key"), "msldivd114"),
    (("context114", "lemon"), "nszhrix114"),
    (("context114", "a"), "context114"),
    (("context114", "zz"), "bnmsdws114"),
    (("context114", "AgentU"), "curgxrt114"),
    (("context114", "keyboard"), "mslusxk114"),
    (("context114", "AA"), "context114"),
    (("knowledge114", "key"), "urmgpcnkc114"),
    (("knowledge114", "lemon"), "vrakyphss114"),
    (("knowledge114", "a"), "knowledge114"),
    (("knowledge114", "zz"), "jmnvkdcfd114"),
    (("knowledge114", "AgentU"), "ktsjeydmi114"),
    (("knowledge114", "keyboard"), "urmxzeujo114"),
    (("knowledge114", "AA"), "knowledge114"),
    (("vector114", "key"), "fiadsp114"),
    (("vector114", "lemon"), "giohbc114"),
    (("vector114", "a"), "vector114"),
    (("vector114", "zz"), "udbsnq114"),
    (("vector114", "AgentU"), "vkgghl114"),
    (("vector114", "keyboard"), "fiaucr114"),
    (("vector114", "AA"), "vector114"),
    (("processor114", "key"), "zvmmiqcsp114"),
    (("processor114", "lemon"), "avaqrdwaf114"),
    (("processor114", "a"), "processor114"),
    (("processor114", "zz"), "oqnbdrrnq114"),
    (("processor114", "AgentU"), "pxspxmsuv114"),
    (("processor114", "keyboard"), "zvmdssjrb114"),
    (("processor114", "AA"), "processor114"),
    (("reasoning114", "key"), "biycslsre114"),
    (("reasoning114", "lemon"), "cimgbymzu114"),
    (("reasoning114", "a"), "reasoning114"),
    (("reasoning114", "zz"), "qdzrnmhmf114"),
    (("reasoning114", "AgentU"), "rkefhhitk114"),
    (("reasoning114", "keyboard"), "biytcnzqq114"),
    (("reasoning114", "AA"), "reasoning114"),
    (("machine114", "key"), "wearmlo114"),
    (("machine114", "lemon"), "xeovvyi114"),
    (("machine114", "a"), "machine114"),
    (("machine114", "zz"), "lzbghmd114"),
    (("machine114", "AgentU"), "mggubhe114"),
    (("machine114", "keyboard"), "weaiwnv114"),
    (("machine114", "AA"), "machine114"),
    (("learning114", "key"), "viybrgxk114"),
    (("learning114", "lemon"), "wimfatrs114"),
    (("learning114", "a"), "learning114"),
    (("learning114", "zz"), "kdzqmhmf114"),
    (("learning114", "AgentU"), "lkeegcnm114"),
    (("learning114", "keyboard"), "viysbiej114"),
    (("learning114", "AA"), "learning114"),
    (("model114", "key"), "wsbop114"),
    (("model114", "lemon"), "xspsy114"),
    (("model114", "a"), "model114"),
    (("model114", "zz"), "lncdk114"),
    (("model114", "AgentU"), "muhre114"),
    (("model114", "keyboard"), "wsbfz114"),
    (("model114", "AA"), "model114"),
    (("token114", "key"), "dsior114"),
    (("token114", "lemon"), "eswsa114"),
    (("token114", "a"), "token114"),
    (("token114", "zz"), "snjdm114"),
    (("token114", "AgentU"), "tuorg114"),
    (("token114", "keyboard"), "dsifb114"),
    (("token114", "AA"), "token114"),
    (("prompt114", "key"), "zvmwtr114"),
    (("prompt114", "lemon"), "avaace114"),
    (("prompt114", "a"), "prompt114"),
    (("prompt114", "zz"), "oqnlos114"),
    (("prompt114", "AgentU"), "pxszin114"),
    (("prompt114", "keyboard"), "zvmndt114"),
    (("prompt114", "AA"), "prompt114"),
    (("session114", "key"), "ciqcmmx114"),
    (("session114", "lemon"), "diegvzr114"),
    (("session114", "a"), "session114"),
    (("session114", "zz"), "rdrrhnm114"),
    (("session114", "AgentU"), "skwfbin114"),
    (("session114", "keyboard"), "ciqtwoe114"),
    (("session114", "AA"), "session114"),
    (("library114", "key"), "vmzbepi114"),
    (("library114", "lemon"), "wmnfncc114"),
    (("library114", "a"), "library114"),
    (("library114", "zz"), "khaqzqx114"),
    (("library114", "AgentU"), "lofetly114"),
    (("library114", "keyboard"), "vmzsorp114"),
    (("library114", "AA"), "library114"),
    (("service114", "key"), "cipfmao114"),
    (("service114", "lemon"), "didjvni114"),
    (("service114", "a"), "service114"),
    (("service114", "zz"), "rdquhbd114"),
    (("service114", "AgentU"), "skvibwe114"),
    (("service114", "keyboard"), "cipwwcv114"),
    (("service114", "AA"), "service114"),
    (("gateway114", "key"), "qeroayi114"),
    (("gateway114", "lemon"), "refsjlc114"),
    (("gateway114", "a"), "gateway114"),
    (("gateway114", "zz"), "fzsdvzx114"),
    (("gateway114", "AgentU"), "ggxrpuy114"),
    (("gateway114", "keyboard"), "qerfkap114"),
    (("gateway114", "AA"), "gateway114"),
    (("storage114", "key"), "cxmbeeo114"),
    (("storage114", "lemon"), "dxafnri114"),
    (("storage114", "a"), "storage114"),
    (("storage114", "zz"), "rsnqzfd114"),
    (("storage114", "AgentU"), "szsetae114"),
    (("storage114", "keyboard"), "cxmsogv114"),
    (("storage114", "AA"), "storage114"),
    (("network114", "key"), "xirgspu114"),
    (("network114", "lemon"), "yifkbco114"),
    (("network114", "a"), "network114"),
    (("network114", "zz"), "mdsvnqj114"),
    (("network114", "AgentU"), "nkxjhlk114"),
    (("network114", "keyboard"), "xirxcrb114"),
    (("network114", "AA"), "network114"),
    (("latency114", "key"), "verorai114"),
    (("latency114", "lemon"), "wefsanc114"),
    (("latency114", "a"), "latency114"),
    (("latency114", "zz"), "kzsdmbx114"),
    (("latency114", "AgentU"), "lgxrgwy114"),
    (("latency114", "keyboard"), "verfbcp114"),
    (("latency114", "AA"), "latency114"),
    (("buffer114", "key"), "lydpip114"),
    (("buffer114", "lemon"), "myrtrc114"),
    (("buffer114", "a"), "buffer114"),
    (("buffer114", "zz"), "ateedq114"),
    (("buffer114", "AgentU"), "bajsxl114"),
    (("buffer114", "keyboard"), "lydgsr114"),
    (("buffer114", "AA"), "buffer114"),
    (("queue114", "key"), "aycei114"),
    (("queue114", "lemon"), "byqir114"),
    (("queue114", "a"), "queue114"),
    (("queue114", "zz"), "ptdtd114"),
    (("queue114", "AgentU"), "qaihx114"),
    (("queue114", "keyboard"), "aycvs114"),
    (("queue114", "AA"), "queue114"),
    (("worker114", "key"), "gspuip114"),
    (("worker114", "lemon"), "hsdyrc114"),
    (("worker114", "a"), "worker114"),
    (("worker114", "zz"), "vnqjdq114"),
    (("worker114", "AgentU"), "wuvxxl114"),
    (("worker114", "keyboard"), "gsplsr114"),
    (("worker114", "AA"), "worker114"),
    (("kernel114", "key"), "uipxij114"),
    (("kernel114", "lemon"), "vidbrw114"),
    (("kernel114", "a"), "kernel114"),
    (("kernel114", "zz"), "jdqmdk114"),
    (("kernel114", "AgentU"), "kkvaxf114"),
    (("kernel114", "keyboard"), "uiposl114"),
    (("kernel114", "AA"), "kernel114"),
    (("signal114", "key"), "cmexej114"),
    (("signal114", "lemon"), "dmsbnw114"),
    (("signal114", "a"), "signal114"),
    (("signal114", "zz"), "rhfmzk114"),
    (("signal114", "AgentU"), "sokatf114"),
    (("signal114", "keyboard"), "cmeool114"),
    (("signal114", "AA"), "signal114"),
    (("packet114", "key"), "zeauir114"),
    (("packet114", "lemon"), "aeoyre114"),
    (("packet114", "a"), "packet114"),
    (("packet114", "zz"), "ozbjds114"),
    (("packet114", "AgentU"), "pggxxn114"),
    (("packet114", "keyboard"), "zealst114"),
    (("packet114", "AA"), "packet114"),
    (("router114", "key"), "bssdip114"),
    (("router114", "lemon"), "csghrc114"),
    (("router114", "a"), "router114"),
    (("router114", "zz"), "qntsdq114"),
    (("router114", "AgentU"), "ruygxl114"),
    (("router114", "keyboard"), "bssusr114"),
    (("router114", "AA"), "router114"),
    (("cluster114", "key"), "mpscxcb114"),
    (("cluster114", "lemon"), "npgggpv114"),
    (("cluster114", "a"), "cluster114"),
    (("cluster114", "zz"), "bktrsdq114"),
    (("cluster114", "AgentU"), "cryfmyr114"),
    (("cluster114", "keyboard"), "mpsthei114"),
    (("cluster114", "AA"), "cluster114"),
    (("mirror114", "key"), "wmpbsp114"),
    (("mirror114", "lemon"), "xmdfbc114"),
    (("mirror114", "a"), "mirror114"),
    (("mirror114", "zz"), "lhqqnq114"),
    (("mirror114", "AgentU"), "movehl114"),
    (("mirror114", "keyboard"), "wmpscr114"),
    (("mirror114", "AA"), "mirror114"),
    (("filter114", "key"), "pmjdip114"),
    (("filter114", "lemon"), "qmxhrc114"),
    (("filter114", "a"), "filter114"),
    (("filter114", "zz"), "ehksdq114"),
    (("filter114", "AgentU"), "fopgxl114"),
    (("filter114", "keyboard"), "pmjusr114"),
    (("filter114", "AA"), "filter114"),
    (("ranking114", "key"), "belumlq114"),
    (("ranking114", "lemon"), "cezyvyk114"),
    (("ranking114", "a"), "ranking114"),
    (("ranking114", "zz"), "qzmjhmf114"),
    (("ranking114", "AgentU"), "rgrxbhg114"),
    (("ranking114", "keyboard"), "bellwnx114"),
    (("ranking114", "AA"), "ranking114"),
    (("encoding114", "key"), "orayhgxk114"),
    (("encoding114", "lemon"), "procqtrs114"),
    (("encoding114", "a"), "encoding114"),
    (("encoding114", "zz"), "dmbnchmf114"),
    (("encoding114", "AgentU"), "etgbwcnm114"),
    (("encoding114", "keyboard"), "orapriej114"),
    (("encoding114", "AA"), "encoding114"),
    (("mapping114", "key"), "wenzmlq114"),
    (("mapping114", "lemon"), "xebdvyk114"),
    (("mapping114", "a"), "mapping114"),
    (("mapping114", "zz"), "lzoohmf114"),
    (("mapping114", "AgentU"), "mgtcbhg114"),
    (("mapping114", "keyboard"), "wenqwnx114"),
    (("mapping114", "AA"), "mapping114"),
    (("record114", "key"), "biayvb114"),
    (("record114", "lemon"), "cioceo114"),
    (("record114", "a"), "record114"),
    (("record114", "zz"), "qdbnqc114"),
    (("record114", "AgentU"), "rkgbkx114"),
    (("record114", "keyboard"), "biapfd114"),
    (("record114", "AA"), "record114"),
    (("candle114", "key"), "melnpc114"),
    (("candle114", "lemon"), "nezryp114"),
    (("candle114", "a"), "candle114"),
    (("candle114", "zz"), "bzmckd114"),
    (("candle114", "AgentU"), "cgrqey114"),
    (("candle114", "keyboard"), "meleze114"),
    (("candle114", "AA"), "candle114"),
    (("thread114", "key"), "dlpoeb114"),
    (("thread114", "lemon"), "eldsno114"),
    (("thread114", "a"), "thread114"),
    (("thread114", "zz"), "sgqdzc114"),
    (("thread114", "AgentU"), "tnvrtx114"),
    (("thread114", "keyboard"), "dlpfod114"),
    (("thread114", "AA"), "thread114"),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 114: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 114: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "a"),
        "round 114: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 114: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 114: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 114: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", "AA"),
        "round 114: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "key"),
        "bssxh 114: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 114: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "a"),
        "round 114: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 114: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 114: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 114: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", "AA"),
        "round 114: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 114: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 114: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "a"),
        "round 114: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 114: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 114: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 114: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", "AA"),
        "round 114: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 114: the processor reads the record then stops", "key"),
        "bssxh 114: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 114: the processor reads the record then stops", "lemon"),
        "csgbq 114: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 114: the processor reads the record then stops", "a"),
        "round 114: the processor reads the record then stops",
    ),
    (
        ("round 114: the processor reads the record then stops", "zz"),
        "qntmc 114: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 114: the processor reads the record then stops", "AgentU"),
        "ruyaw 114: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 114: the processor reads the record then stops", "keyboard"),
        "bssor 114: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 114: the processor reads the record then stops", "AA"),
        "round 114: the processor reads the record then stops",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "key"),
        "bssxh 114: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "lemon"),
        "csgbq 114: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "a"),
        "round 114: a worker pulls the next task from the queue",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "zz"),
        "qntmc 114: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 114: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "keyboard"),
        "bssor 114: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 114: a worker pulls the next task from the queue", "AA"),
        "round 114: a worker pulls the next task from the queue",
    ),
    (
        ("round 114: signals travel through the network layer", "key"),
        "bssxh 114: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 114: signals travel through the network layer", "lemon"),
        "csgbq 114: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 114: signals travel through the network layer", "a"),
        "round 114: signals travel through the network layer",
    ),
    (
        ("round 114: signals travel through the network layer", "zz"),
        "qntmc 114: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 114: signals travel through the network layer", "AgentU"),
        "ruyaw 114: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 114: signals travel through the network layer", "keyboard"),
        "bssor 114: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 114: signals travel through the network layer", "AA"),
        "round 114: signals travel through the network layer",
    ),
    (
        ("round 114: the gateway routes each request by policy", "key"),
        "bssxh 114: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 114: the gateway routes each request by policy", "lemon"),
        "csgbq 114: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 114: the gateway routes each request by policy", "a"),
        "round 114: the gateway routes each request by policy",
    ),
    (
        ("round 114: the gateway routes each request by policy", "zz"),
        "qntmc 114: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 114: the gateway routes each request by policy", "AgentU"),
        "ruyaw 114: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 114: the gateway routes each request by policy", "keyboard"),
        "bssor 114: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 114: the gateway routes each request by policy", "AA"),
        "round 114: the gateway routes each request by policy",
    ),
    (("round 114: memory grows until the buffer is full", "key"), "bssxh 114: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 114: memory grows until the buffer is full", "lemon"), "csgbq 114: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 114: memory grows until the buffer is full", "a"), "round 114: memory grows until the buffer is full"),
    (("round 114: memory grows until the buffer is full", "zz"), "qntmc 114: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 114: memory grows until the buffer is full", "AgentU"),
        "ruyaw 114: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 114: memory grows until the buffer is full", "keyboard"),
        "bssor 114: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 114: memory grows until the buffer is full", "AA"), "round 114: memory grows until the buffer is full"),
    (("round 114: the cluster mirrors every packet twice", "key"), "bssxh 114: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 114: the cluster mirrors every packet twice", "lemon"),
        "csgbq 114: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 114: the cluster mirrors every packet twice", "a"), "round 114: the cluster mirrors every packet twice"),
    (("round 114: the cluster mirrors every packet twice", "zz"), "qntmc 114: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 114: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 114: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 114: the cluster mirrors every packet twice", "keyboard"),
        "bssor 114: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 114: the cluster mirrors every packet twice", "AA"), "round 114: the cluster mirrors every packet twice"),
    (
        ("round 114: ranking uses tokens learned from the corpus", "key"),
        "bssxh 114: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 114: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", "a"),
        "round 114: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 114: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 114: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 114: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", "AA"),
        "round 114: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 114: a long session ends when the candle dies", "key"),
        "bssxh 114: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 114: a long session ends when the candle dies", "lemon"),
        "csgbq 114: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 114: a long session ends when the candle dies", "a"),
        "round 114: a long session ends when the candle dies",
    ),
    (
        ("round 114: a long session ends when the candle dies", "zz"),
        "qntmc 114: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 114: a long session ends when the candle dies", "AgentU"),
        "ruyaw 114: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 114: a long session ends when the candle dies", "keyboard"),
        "bssor 114: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 114: a long session ends when the candle dies", "AA"),
        "round 114: a long session ends when the candle dies",
    ),
    (("round 114: encode the prompt then map the result", "key"), "bssxh 114: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 114: encode the prompt then map the result", "lemon"), "csgbq 114: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 114: encode the prompt then map the result", "a"), "round 114: encode the prompt then map the result"),
    (("round 114: encode the prompt then map the result", "zz"), "qntmc 114: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 114: encode the prompt then map the result", "AgentU"),
        "ruyaw 114: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 114: encode the prompt then map the result", "keyboard"),
        "bssor 114: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 114: encode the prompt then map the result", "AA"), "round 114: encode the prompt then map the result"),
    (("round 114: the kernel wakes the worker at dawn", "key"), "bssxh 114: rri iovlop ukocc xfo ambocb er neux"),
    (("round 114: the kernel wakes the worker at dawn", "lemon"), "csgbq 114: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 114: the kernel wakes the worker at dawn", "a"), "round 114: the kernel wakes the worker at dawn"),
    (("round 114: the kernel wakes the worker at dawn", "zz"), "qntmc 114: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 114: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 114: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 114: the kernel wakes the worker at dawn", "keyboard"), "bssor 114: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 114: the kernel wakes the worker at dawn", "AA"), "round 114: the kernel wakes the worker at dawn"),
    (("round 114: service latency drops after the patch", "key"), "bssxh 114: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 114: service latency drops after the patch", "lemon"), "csgbq 114: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 114: service latency drops after the patch", "a"), "round 114: service latency drops after the patch"),
    (("round 114: service latency drops after the patch", "zz"), "qntmc 114: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 114: service latency drops after the patch", "AgentU"),
        "ruyaw 114: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 114: service latency drops after the patch", "keyboard"),
        "bssor 114: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 114: service latency drops after the patch", "AA"), "round 114: service latency drops after the patch"),
    (
        ("round 114: the library caches every vector it sees", "key"),
        "bssxh 114: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 114: the library caches every vector it sees", "lemon"),
        "csgbq 114: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 114: the library caches every vector it sees", "a"), "round 114: the library caches every vector it sees"),
    (
        ("round 114: the library caches every vector it sees", "zz"),
        "qntmc 114: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 114: the library caches every vector it sees", "AgentU"),
        "ruyaw 114: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 114: the library caches every vector it sees", "keyboard"),
        "bssor 114: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 114: the library caches every vector it sees", "AA"),
        "round 114: the library caches every vector it sees",
    ),
    (("round 114: agents argue then the debate resolves", "key"), "bssxh 114: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 114: agents argue then the debate resolves", "lemon"), "csgbq 114: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 114: agents argue then the debate resolves", "a"), "round 114: agents argue then the debate resolves"),
    (("round 114: agents argue then the debate resolves", "zz"), "qntmc 114: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 114: agents argue then the debate resolves", "AgentU"),
        "ruyaw 114: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 114: agents argue then the debate resolves", "keyboard"),
        "bssor 114: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 114: agents argue then the debate resolves", "AA"), "round 114: agents argue then the debate resolves"),
    (("round 114: the filter keeps only strong matches", "key"), "bssxh 114: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 114: the filter keeps only strong matches", "lemon"), "csgbq 114: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 114: the filter keeps only strong matches", "a"), "round 114: the filter keeps only strong matches"),
    (("round 114: the filter keeps only strong matches", "zz"), "qntmc 114: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 114: the filter keeps only strong matches", "AgentU"), "ruyaw 114: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 114: the filter keeps only strong matches", "keyboard"),
        "bssor 114: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 114: the filter keeps only strong matches", "AA"), "round 114: the filter keeps only strong matches"),
    (("round 114: the model answers with a short reply", "key"), "bssxh 114: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 114: the model answers with a short reply", "lemon"), "csgbq 114: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 114: the model answers with a short reply", "a"), "round 114: the model answers with a short reply"),
    (("round 114: the model answers with a short reply", "zz"), "qntmc 114: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 114: the model answers with a short reply", "AgentU"), "ruyaw 114: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 114: the model answers with a short reply", "keyboard"),
        "bssor 114: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 114: the model answers with a short reply", "AA"), "round 114: the model answers with a short reply"),
    (
        ("round 114: the recorder stores the reasoning trace", "key"),
        "bssxh 114: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 114: the recorder stores the reasoning trace", "lemon"),
        "csgbq 114: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 114: the recorder stores the reasoning trace", "a"), "round 114: the recorder stores the reasoning trace"),
    (
        ("round 114: the recorder stores the reasoning trace", "zz"),
        "qntmc 114: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 114: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 114: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 114: the recorder stores the reasoning trace", "keyboard"),
        "bssor 114: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 114: the recorder stores the reasoning trace", "AA"),
        "round 114: the recorder stores the reasoning trace",
    ),
    (("round 114: the angel watches the processor run", "key"), "bssxh 114: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 114: the angel watches the processor run", "lemon"), "csgbq 114: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 114: the angel watches the processor run", "a"), "round 114: the angel watches the processor run"),
    (("round 114: the angel watches the processor run", "zz"), "qntmc 114: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 114: the angel watches the processor run", "AgentU"), "ruyaw 114: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 114: the angel watches the processor run", "keyboard"), "bssor 114: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 114: the angel watches the processor run", "AA"), "round 114: the angel watches the processor run"),
    (("round 114: angle of the vector decides the match", "key"), "bssxh 114: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 114: angle of the vector decides the match", "lemon"), "csgbq 114: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 114: angle of the vector decides the match", "a"), "round 114: angle of the vector decides the match"),
    (("round 114: angle of the vector decides the match", "zz"), "qntmc 114: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 114: angle of the vector decides the match", "AgentU"),
        "ruyaw 114: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 114: angle of the vector decides the match", "keyboard"),
        "bssor 114: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 114: angle of the vector decides the match", "AA"), "round 114: angle of the vector decides the match"),
    (
        ("round 114: the candle burns twice as long at night", "key"),
        "bssxh 114: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 114: the candle burns twice as long at night", "lemon"),
        "csgbq 114: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 114: the candle burns twice as long at night", "a"), "round 114: the candle burns twice as long at night"),
    (
        ("round 114: the candle burns twice as long at night", "zz"),
        "qntmc 114: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 114: the candle burns twice as long at night", "AgentU"),
        "ruyaw 114: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 114: the candle burns twice as long at night", "keyboard"),
        "bssor 114: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 114: the candle burns twice as long at night", "AA"),
        "round 114: the candle burns twice as long at night",
    ),
    (("round 114: a mirror of the universe in one line", "key"), "bssxh 114: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 114: a mirror of the universe in one line", "lemon"), "csgbq 114: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 114: a mirror of the universe in one line", "a"), "round 114: a mirror of the universe in one line"),
    (("round 114: a mirror of the universe in one line", "zz"), "qntmc 114: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 114: a mirror of the universe in one line", "AgentU"), "ruyaw 114: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 114: a mirror of the universe in one line", "keyboard"),
        "bssor 114: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 114: a mirror of the universe in one line", "AA"), "round 114: a mirror of the universe in one line"),
    (("round 114: the queue drains before the storm", "key"), "bssxh 114: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 114: the queue drains before the storm", "lemon"), "csgbq 114: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 114: the queue drains before the storm", "a"), "round 114: the queue drains before the storm"),
    (("round 114: the queue drains before the storm", "zz"), "qntmc 114: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 114: the queue drains before the storm", "AgentU"), "ruyaw 114: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 114: the queue drains before the storm", "keyboard"), "bssor 114: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 114: the queue drains before the storm", "AA"), "round 114: the queue drains before the storm"),
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
