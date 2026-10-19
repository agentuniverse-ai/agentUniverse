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
    (("kitten140", "key"), "umrdil140"),
    (("kitten140", "lemon"), "vmfhry140"),
    (("kitten140", "a"), "kitten140"),
    (("kitten140", "zz"), "jhssdm140"),
    (("kitten140", "AgentU"), "koxgxh140"),
    (("kitten140", "keyboard"), "umrusn140"),
    (("kitten140", "AA"), "kitten140"),
    (("sitting140", "key"), "cmrdmlq140"),
    (("sitting140", "lemon"), "dmfhvyk140"),
    (("sitting140", "a"), "sitting140"),
    (("sitting140", "zz"), "rhsshmf140"),
    (("sitting140", "AgentU"), "soxgbhg140"),
    (("sitting140", "keyboard"), "cmruwnx140"),
    (("sitting140", "AA"), "sitting140"),
    (("agent140", "key"), "kkcxx140"),
    (("agent140", "lemon"), "lkqbg140"),
    (("agent140", "a"), "agent140"),
    (("agent140", "zz"), "zfdms140"),
    (("agent140", "AgentU"), "amiam140"),
    (("agent140", "keyboard"), "kkcoh140"),
    (("agent140", "AA"), "agent140"),
    (("angle140", "key"), "krevi140"),
    (("angle140", "lemon"), "lrszr140"),
    (("angle140", "a"), "angle140"),
    (("angle140", "zz"), "zmfkd140"),
    (("angle140", "AgentU"), "atkyx140"),
    (("angle140", "keyboard"), "krems140"),
    (("angle140", "AA"), "angle140"),
    (("universe140", "key"), "ergfipci140"),
    (("universe140", "lemon"), "frujrcwq140"),
    (("universe140", "a"), "universe140"),
    (("universe140", "zz"), "tmhudqrd140"),
    (("universe140", "AgentU"), "utmixlsk140"),
    (("universe140", "keyboard"), "ergwsrjh140"),
    (("universe140", "AA"), "universe140"),
    (("memory140", "key"), "wikyvw140"),
    (("memory140", "lemon"), "xiycej140"),
    (("memory140", "a"), "memory140"),
    (("memory140", "zz"), "ldlnqx140"),
    (("memory140", "AgentU"), "mkqbks140"),
    (("memory140", "keyboard"), "wikpfy140"),
    (("memory140", "AA"), "memory140"),
    (("stream140", "key"), "cxpoek140"),
    (("stream140", "lemon"), "dxdsnx140"),
    (("stream140", "a"), "stream140"),
    (("stream140", "zz"), "rsqdzl140"),
    (("stream140", "AgentU"), "szvrtg140"),
    (("stream140", "keyboard"), "cxpfom140"),
    (("stream140", "AA"), "stream140"),
    (("context140", "key"), "msldivd140"),
    (("context140", "lemon"), "nszhrix140"),
    (("context140", "a"), "context140"),
    (("context140", "zz"), "bnmsdws140"),
    (("context140", "AgentU"), "curgxrt140"),
    (("context140", "keyboard"), "mslusxk140"),
    (("context140", "AA"), "context140"),
    (("knowledge140", "key"), "urmgpcnkc140"),
    (("knowledge140", "lemon"), "vrakyphss140"),
    (("knowledge140", "a"), "knowledge140"),
    (("knowledge140", "zz"), "jmnvkdcfd140"),
    (("knowledge140", "AgentU"), "ktsjeydmi140"),
    (("knowledge140", "keyboard"), "urmxzeujo140"),
    (("knowledge140", "AA"), "knowledge140"),
    (("vector140", "key"), "fiadsp140"),
    (("vector140", "lemon"), "giohbc140"),
    (("vector140", "a"), "vector140"),
    (("vector140", "zz"), "udbsnq140"),
    (("vector140", "AgentU"), "vkgghl140"),
    (("vector140", "keyboard"), "fiaucr140"),
    (("vector140", "AA"), "vector140"),
    (("processor140", "key"), "zvmmiqcsp140"),
    (("processor140", "lemon"), "avaqrdwaf140"),
    (("processor140", "a"), "processor140"),
    (("processor140", "zz"), "oqnbdrrnq140"),
    (("processor140", "AgentU"), "pxspxmsuv140"),
    (("processor140", "keyboard"), "zvmdssjrb140"),
    (("processor140", "AA"), "processor140"),
    (("reasoning140", "key"), "biycslsre140"),
    (("reasoning140", "lemon"), "cimgbymzu140"),
    (("reasoning140", "a"), "reasoning140"),
    (("reasoning140", "zz"), "qdzrnmhmf140"),
    (("reasoning140", "AgentU"), "rkefhhitk140"),
    (("reasoning140", "keyboard"), "biytcnzqq140"),
    (("reasoning140", "AA"), "reasoning140"),
    (("machine140", "key"), "wearmlo140"),
    (("machine140", "lemon"), "xeovvyi140"),
    (("machine140", "a"), "machine140"),
    (("machine140", "zz"), "lzbghmd140"),
    (("machine140", "AgentU"), "mggubhe140"),
    (("machine140", "keyboard"), "weaiwnv140"),
    (("machine140", "AA"), "machine140"),
    (("learning140", "key"), "viybrgxk140"),
    (("learning140", "lemon"), "wimfatrs140"),
    (("learning140", "a"), "learning140"),
    (("learning140", "zz"), "kdzqmhmf140"),
    (("learning140", "AgentU"), "lkeegcnm140"),
    (("learning140", "keyboard"), "viysbiej140"),
    (("learning140", "AA"), "learning140"),
    (("model140", "key"), "wsbop140"),
    (("model140", "lemon"), "xspsy140"),
    (("model140", "a"), "model140"),
    (("model140", "zz"), "lncdk140"),
    (("model140", "AgentU"), "muhre140"),
    (("model140", "keyboard"), "wsbfz140"),
    (("model140", "AA"), "model140"),
    (("token140", "key"), "dsior140"),
    (("token140", "lemon"), "eswsa140"),
    (("token140", "a"), "token140"),
    (("token140", "zz"), "snjdm140"),
    (("token140", "AgentU"), "tuorg140"),
    (("token140", "keyboard"), "dsifb140"),
    (("token140", "AA"), "token140"),
    (("prompt140", "key"), "zvmwtr140"),
    (("prompt140", "lemon"), "avaace140"),
    (("prompt140", "a"), "prompt140"),
    (("prompt140", "zz"), "oqnlos140"),
    (("prompt140", "AgentU"), "pxszin140"),
    (("prompt140", "keyboard"), "zvmndt140"),
    (("prompt140", "AA"), "prompt140"),
    (("session140", "key"), "ciqcmmx140"),
    (("session140", "lemon"), "diegvzr140"),
    (("session140", "a"), "session140"),
    (("session140", "zz"), "rdrrhnm140"),
    (("session140", "AgentU"), "skwfbin140"),
    (("session140", "keyboard"), "ciqtwoe140"),
    (("session140", "AA"), "session140"),
    (("library140", "key"), "vmzbepi140"),
    (("library140", "lemon"), "wmnfncc140"),
    (("library140", "a"), "library140"),
    (("library140", "zz"), "khaqzqx140"),
    (("library140", "AgentU"), "lofetly140"),
    (("library140", "keyboard"), "vmzsorp140"),
    (("library140", "AA"), "library140"),
    (("service140", "key"), "cipfmao140"),
    (("service140", "lemon"), "didjvni140"),
    (("service140", "a"), "service140"),
    (("service140", "zz"), "rdquhbd140"),
    (("service140", "AgentU"), "skvibwe140"),
    (("service140", "keyboard"), "cipwwcv140"),
    (("service140", "AA"), "service140"),
    (("gateway140", "key"), "qeroayi140"),
    (("gateway140", "lemon"), "refsjlc140"),
    (("gateway140", "a"), "gateway140"),
    (("gateway140", "zz"), "fzsdvzx140"),
    (("gateway140", "AgentU"), "ggxrpuy140"),
    (("gateway140", "keyboard"), "qerfkap140"),
    (("gateway140", "AA"), "gateway140"),
    (("storage140", "key"), "cxmbeeo140"),
    (("storage140", "lemon"), "dxafnri140"),
    (("storage140", "a"), "storage140"),
    (("storage140", "zz"), "rsnqzfd140"),
    (("storage140", "AgentU"), "szsetae140"),
    (("storage140", "keyboard"), "cxmsogv140"),
    (("storage140", "AA"), "storage140"),
    (("network140", "key"), "xirgspu140"),
    (("network140", "lemon"), "yifkbco140"),
    (("network140", "a"), "network140"),
    (("network140", "zz"), "mdsvnqj140"),
    (("network140", "AgentU"), "nkxjhlk140"),
    (("network140", "keyboard"), "xirxcrb140"),
    (("network140", "AA"), "network140"),
    (("latency140", "key"), "verorai140"),
    (("latency140", "lemon"), "wefsanc140"),
    (("latency140", "a"), "latency140"),
    (("latency140", "zz"), "kzsdmbx140"),
    (("latency140", "AgentU"), "lgxrgwy140"),
    (("latency140", "keyboard"), "verfbcp140"),
    (("latency140", "AA"), "latency140"),
    (("buffer140", "key"), "lydpip140"),
    (("buffer140", "lemon"), "myrtrc140"),
    (("buffer140", "a"), "buffer140"),
    (("buffer140", "zz"), "ateedq140"),
    (("buffer140", "AgentU"), "bajsxl140"),
    (("buffer140", "keyboard"), "lydgsr140"),
    (("buffer140", "AA"), "buffer140"),
    (("queue140", "key"), "aycei140"),
    (("queue140", "lemon"), "byqir140"),
    (("queue140", "a"), "queue140"),
    (("queue140", "zz"), "ptdtd140"),
    (("queue140", "AgentU"), "qaihx140"),
    (("queue140", "keyboard"), "aycvs140"),
    (("queue140", "AA"), "queue140"),
    (("worker140", "key"), "gspuip140"),
    (("worker140", "lemon"), "hsdyrc140"),
    (("worker140", "a"), "worker140"),
    (("worker140", "zz"), "vnqjdq140"),
    (("worker140", "AgentU"), "wuvxxl140"),
    (("worker140", "keyboard"), "gsplsr140"),
    (("worker140", "AA"), "worker140"),
    (("kernel140", "key"), "uipxij140"),
    (("kernel140", "lemon"), "vidbrw140"),
    (("kernel140", "a"), "kernel140"),
    (("kernel140", "zz"), "jdqmdk140"),
    (("kernel140", "AgentU"), "kkvaxf140"),
    (("kernel140", "keyboard"), "uiposl140"),
    (("kernel140", "AA"), "kernel140"),
    (("signal140", "key"), "cmexej140"),
    (("signal140", "lemon"), "dmsbnw140"),
    (("signal140", "a"), "signal140"),
    (("signal140", "zz"), "rhfmzk140"),
    (("signal140", "AgentU"), "sokatf140"),
    (("signal140", "keyboard"), "cmeool140"),
    (("signal140", "AA"), "signal140"),
    (("packet140", "key"), "zeauir140"),
    (("packet140", "lemon"), "aeoyre140"),
    (("packet140", "a"), "packet140"),
    (("packet140", "zz"), "ozbjds140"),
    (("packet140", "AgentU"), "pggxxn140"),
    (("packet140", "keyboard"), "zealst140"),
    (("packet140", "AA"), "packet140"),
    (("router140", "key"), "bssdip140"),
    (("router140", "lemon"), "csghrc140"),
    (("router140", "a"), "router140"),
    (("router140", "zz"), "qntsdq140"),
    (("router140", "AgentU"), "ruygxl140"),
    (("router140", "keyboard"), "bssusr140"),
    (("router140", "AA"), "router140"),
    (("cluster140", "key"), "mpscxcb140"),
    (("cluster140", "lemon"), "npgggpv140"),
    (("cluster140", "a"), "cluster140"),
    (("cluster140", "zz"), "bktrsdq140"),
    (("cluster140", "AgentU"), "cryfmyr140"),
    (("cluster140", "keyboard"), "mpsthei140"),
    (("cluster140", "AA"), "cluster140"),
    (("mirror140", "key"), "wmpbsp140"),
    (("mirror140", "lemon"), "xmdfbc140"),
    (("mirror140", "a"), "mirror140"),
    (("mirror140", "zz"), "lhqqnq140"),
    (("mirror140", "AgentU"), "movehl140"),
    (("mirror140", "keyboard"), "wmpscr140"),
    (("mirror140", "AA"), "mirror140"),
    (("filter140", "key"), "pmjdip140"),
    (("filter140", "lemon"), "qmxhrc140"),
    (("filter140", "a"), "filter140"),
    (("filter140", "zz"), "ehksdq140"),
    (("filter140", "AgentU"), "fopgxl140"),
    (("filter140", "keyboard"), "pmjusr140"),
    (("filter140", "AA"), "filter140"),
    (("ranking140", "key"), "belumlq140"),
    (("ranking140", "lemon"), "cezyvyk140"),
    (("ranking140", "a"), "ranking140"),
    (("ranking140", "zz"), "qzmjhmf140"),
    (("ranking140", "AgentU"), "rgrxbhg140"),
    (("ranking140", "keyboard"), "bellwnx140"),
    (("ranking140", "AA"), "ranking140"),
    (("encoding140", "key"), "orayhgxk140"),
    (("encoding140", "lemon"), "procqtrs140"),
    (("encoding140", "a"), "encoding140"),
    (("encoding140", "zz"), "dmbnchmf140"),
    (("encoding140", "AgentU"), "etgbwcnm140"),
    (("encoding140", "keyboard"), "orapriej140"),
    (("encoding140", "AA"), "encoding140"),
    (("mapping140", "key"), "wenzmlq140"),
    (("mapping140", "lemon"), "xebdvyk140"),
    (("mapping140", "a"), "mapping140"),
    (("mapping140", "zz"), "lzoohmf140"),
    (("mapping140", "AgentU"), "mgtcbhg140"),
    (("mapping140", "keyboard"), "wenqwnx140"),
    (("mapping140", "AA"), "mapping140"),
    (("record140", "key"), "biayvb140"),
    (("record140", "lemon"), "cioceo140"),
    (("record140", "a"), "record140"),
    (("record140", "zz"), "qdbnqc140"),
    (("record140", "AgentU"), "rkgbkx140"),
    (("record140", "keyboard"), "biapfd140"),
    (("record140", "AA"), "record140"),
    (("candle140", "key"), "melnpc140"),
    (("candle140", "lemon"), "nezryp140"),
    (("candle140", "a"), "candle140"),
    (("candle140", "zz"), "bzmckd140"),
    (("candle140", "AgentU"), "cgrqey140"),
    (("candle140", "keyboard"), "meleze140"),
    (("candle140", "AA"), "candle140"),
    (("thread140", "key"), "dlpoeb140"),
    (("thread140", "lemon"), "eldsno140"),
    (("thread140", "a"), "thread140"),
    (("thread140", "zz"), "sgqdzc140"),
    (("thread140", "AgentU"), "tnvrtx140"),
    (("thread140", "keyboard"), "dlpfod140"),
    (("thread140", "AA"), "thread140"),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 140: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 140: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "a"),
        "round 140: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 140: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 140: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 140: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", "AA"),
        "round 140: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "key"),
        "bssxh 140: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 140: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "a"),
        "round 140: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 140: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 140: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 140: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", "AA"),
        "round 140: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 140: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 140: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "a"),
        "round 140: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 140: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 140: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 140: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", "AA"),
        "round 140: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 140: the processor reads the record then stops", "key"),
        "bssxh 140: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 140: the processor reads the record then stops", "lemon"),
        "csgbq 140: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 140: the processor reads the record then stops", "a"),
        "round 140: the processor reads the record then stops",
    ),
    (
        ("round 140: the processor reads the record then stops", "zz"),
        "qntmc 140: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 140: the processor reads the record then stops", "AgentU"),
        "ruyaw 140: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 140: the processor reads the record then stops", "keyboard"),
        "bssor 140: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 140: the processor reads the record then stops", "AA"),
        "round 140: the processor reads the record then stops",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "key"),
        "bssxh 140: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "lemon"),
        "csgbq 140: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "a"),
        "round 140: a worker pulls the next task from the queue",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "zz"),
        "qntmc 140: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 140: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "keyboard"),
        "bssor 140: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 140: a worker pulls the next task from the queue", "AA"),
        "round 140: a worker pulls the next task from the queue",
    ),
    (
        ("round 140: signals travel through the network layer", "key"),
        "bssxh 140: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 140: signals travel through the network layer", "lemon"),
        "csgbq 140: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 140: signals travel through the network layer", "a"),
        "round 140: signals travel through the network layer",
    ),
    (
        ("round 140: signals travel through the network layer", "zz"),
        "qntmc 140: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 140: signals travel through the network layer", "AgentU"),
        "ruyaw 140: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 140: signals travel through the network layer", "keyboard"),
        "bssor 140: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 140: signals travel through the network layer", "AA"),
        "round 140: signals travel through the network layer",
    ),
    (
        ("round 140: the gateway routes each request by policy", "key"),
        "bssxh 140: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 140: the gateway routes each request by policy", "lemon"),
        "csgbq 140: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 140: the gateway routes each request by policy", "a"),
        "round 140: the gateway routes each request by policy",
    ),
    (
        ("round 140: the gateway routes each request by policy", "zz"),
        "qntmc 140: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 140: the gateway routes each request by policy", "AgentU"),
        "ruyaw 140: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 140: the gateway routes each request by policy", "keyboard"),
        "bssor 140: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 140: the gateway routes each request by policy", "AA"),
        "round 140: the gateway routes each request by policy",
    ),
    (("round 140: memory grows until the buffer is full", "key"), "bssxh 140: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 140: memory grows until the buffer is full", "lemon"), "csgbq 140: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 140: memory grows until the buffer is full", "a"), "round 140: memory grows until the buffer is full"),
    (("round 140: memory grows until the buffer is full", "zz"), "qntmc 140: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 140: memory grows until the buffer is full", "AgentU"),
        "ruyaw 140: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 140: memory grows until the buffer is full", "keyboard"),
        "bssor 140: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 140: memory grows until the buffer is full", "AA"), "round 140: memory grows until the buffer is full"),
    (("round 140: the cluster mirrors every packet twice", "key"), "bssxh 140: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 140: the cluster mirrors every packet twice", "lemon"),
        "csgbq 140: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 140: the cluster mirrors every packet twice", "a"), "round 140: the cluster mirrors every packet twice"),
    (("round 140: the cluster mirrors every packet twice", "zz"), "qntmc 140: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 140: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 140: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 140: the cluster mirrors every packet twice", "keyboard"),
        "bssor 140: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 140: the cluster mirrors every packet twice", "AA"), "round 140: the cluster mirrors every packet twice"),
    (
        ("round 140: ranking uses tokens learned from the corpus", "key"),
        "bssxh 140: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 140: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", "a"),
        "round 140: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 140: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 140: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 140: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", "AA"),
        "round 140: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 140: a long session ends when the candle dies", "key"),
        "bssxh 140: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 140: a long session ends when the candle dies", "lemon"),
        "csgbq 140: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 140: a long session ends when the candle dies", "a"),
        "round 140: a long session ends when the candle dies",
    ),
    (
        ("round 140: a long session ends when the candle dies", "zz"),
        "qntmc 140: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 140: a long session ends when the candle dies", "AgentU"),
        "ruyaw 140: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 140: a long session ends when the candle dies", "keyboard"),
        "bssor 140: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 140: a long session ends when the candle dies", "AA"),
        "round 140: a long session ends when the candle dies",
    ),
    (("round 140: encode the prompt then map the result", "key"), "bssxh 140: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 140: encode the prompt then map the result", "lemon"), "csgbq 140: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 140: encode the prompt then map the result", "a"), "round 140: encode the prompt then map the result"),
    (("round 140: encode the prompt then map the result", "zz"), "qntmc 140: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 140: encode the prompt then map the result", "AgentU"),
        "ruyaw 140: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 140: encode the prompt then map the result", "keyboard"),
        "bssor 140: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 140: encode the prompt then map the result", "AA"), "round 140: encode the prompt then map the result"),
    (("round 140: the kernel wakes the worker at dawn", "key"), "bssxh 140: rri iovlop ukocc xfo ambocb er neux"),
    (("round 140: the kernel wakes the worker at dawn", "lemon"), "csgbq 140: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 140: the kernel wakes the worker at dawn", "a"), "round 140: the kernel wakes the worker at dawn"),
    (("round 140: the kernel wakes the worker at dawn", "zz"), "qntmc 140: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 140: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 140: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 140: the kernel wakes the worker at dawn", "keyboard"), "bssor 140: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 140: the kernel wakes the worker at dawn", "AA"), "round 140: the kernel wakes the worker at dawn"),
    (("round 140: service latency drops after the patch", "key"), "bssxh 140: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 140: service latency drops after the patch", "lemon"), "csgbq 140: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 140: service latency drops after the patch", "a"), "round 140: service latency drops after the patch"),
    (("round 140: service latency drops after the patch", "zz"), "qntmc 140: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 140: service latency drops after the patch", "AgentU"),
        "ruyaw 140: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 140: service latency drops after the patch", "keyboard"),
        "bssor 140: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 140: service latency drops after the patch", "AA"), "round 140: service latency drops after the patch"),
    (
        ("round 140: the library caches every vector it sees", "key"),
        "bssxh 140: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 140: the library caches every vector it sees", "lemon"),
        "csgbq 140: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 140: the library caches every vector it sees", "a"), "round 140: the library caches every vector it sees"),
    (
        ("round 140: the library caches every vector it sees", "zz"),
        "qntmc 140: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 140: the library caches every vector it sees", "AgentU"),
        "ruyaw 140: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 140: the library caches every vector it sees", "keyboard"),
        "bssor 140: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 140: the library caches every vector it sees", "AA"),
        "round 140: the library caches every vector it sees",
    ),
    (("round 140: agents argue then the debate resolves", "key"), "bssxh 140: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 140: agents argue then the debate resolves", "lemon"), "csgbq 140: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 140: agents argue then the debate resolves", "a"), "round 140: agents argue then the debate resolves"),
    (("round 140: agents argue then the debate resolves", "zz"), "qntmc 140: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 140: agents argue then the debate resolves", "AgentU"),
        "ruyaw 140: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 140: agents argue then the debate resolves", "keyboard"),
        "bssor 140: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 140: agents argue then the debate resolves", "AA"), "round 140: agents argue then the debate resolves"),
    (("round 140: the filter keeps only strong matches", "key"), "bssxh 140: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 140: the filter keeps only strong matches", "lemon"), "csgbq 140: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 140: the filter keeps only strong matches", "a"), "round 140: the filter keeps only strong matches"),
    (("round 140: the filter keeps only strong matches", "zz"), "qntmc 140: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 140: the filter keeps only strong matches", "AgentU"), "ruyaw 140: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 140: the filter keeps only strong matches", "keyboard"),
        "bssor 140: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 140: the filter keeps only strong matches", "AA"), "round 140: the filter keeps only strong matches"),
    (("round 140: the model answers with a short reply", "key"), "bssxh 140: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 140: the model answers with a short reply", "lemon"), "csgbq 140: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 140: the model answers with a short reply", "a"), "round 140: the model answers with a short reply"),
    (("round 140: the model answers with a short reply", "zz"), "qntmc 140: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 140: the model answers with a short reply", "AgentU"), "ruyaw 140: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 140: the model answers with a short reply", "keyboard"),
        "bssor 140: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 140: the model answers with a short reply", "AA"), "round 140: the model answers with a short reply"),
    (
        ("round 140: the recorder stores the reasoning trace", "key"),
        "bssxh 140: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 140: the recorder stores the reasoning trace", "lemon"),
        "csgbq 140: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 140: the recorder stores the reasoning trace", "a"), "round 140: the recorder stores the reasoning trace"),
    (
        ("round 140: the recorder stores the reasoning trace", "zz"),
        "qntmc 140: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 140: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 140: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 140: the recorder stores the reasoning trace", "keyboard"),
        "bssor 140: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 140: the recorder stores the reasoning trace", "AA"),
        "round 140: the recorder stores the reasoning trace",
    ),
    (("round 140: the angel watches the processor run", "key"), "bssxh 140: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 140: the angel watches the processor run", "lemon"), "csgbq 140: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 140: the angel watches the processor run", "a"), "round 140: the angel watches the processor run"),
    (("round 140: the angel watches the processor run", "zz"), "qntmc 140: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 140: the angel watches the processor run", "AgentU"), "ruyaw 140: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 140: the angel watches the processor run", "keyboard"), "bssor 140: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 140: the angel watches the processor run", "AA"), "round 140: the angel watches the processor run"),
    (("round 140: angle of the vector decides the match", "key"), "bssxh 140: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 140: angle of the vector decides the match", "lemon"), "csgbq 140: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 140: angle of the vector decides the match", "a"), "round 140: angle of the vector decides the match"),
    (("round 140: angle of the vector decides the match", "zz"), "qntmc 140: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 140: angle of the vector decides the match", "AgentU"),
        "ruyaw 140: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 140: angle of the vector decides the match", "keyboard"),
        "bssor 140: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 140: angle of the vector decides the match", "AA"), "round 140: angle of the vector decides the match"),
    (
        ("round 140: the candle burns twice as long at night", "key"),
        "bssxh 140: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 140: the candle burns twice as long at night", "lemon"),
        "csgbq 140: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 140: the candle burns twice as long at night", "a"), "round 140: the candle burns twice as long at night"),
    (
        ("round 140: the candle burns twice as long at night", "zz"),
        "qntmc 140: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 140: the candle burns twice as long at night", "AgentU"),
        "ruyaw 140: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 140: the candle burns twice as long at night", "keyboard"),
        "bssor 140: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 140: the candle burns twice as long at night", "AA"),
        "round 140: the candle burns twice as long at night",
    ),
    (("round 140: a mirror of the universe in one line", "key"), "bssxh 140: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 140: a mirror of the universe in one line", "lemon"), "csgbq 140: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 140: a mirror of the universe in one line", "a"), "round 140: a mirror of the universe in one line"),
    (("round 140: a mirror of the universe in one line", "zz"), "qntmc 140: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 140: a mirror of the universe in one line", "AgentU"), "ruyaw 140: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 140: a mirror of the universe in one line", "keyboard"),
        "bssor 140: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 140: a mirror of the universe in one line", "AA"), "round 140: a mirror of the universe in one line"),
    (("round 140: the queue drains before the storm", "key"), "bssxh 140: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 140: the queue drains before the storm", "lemon"), "csgbq 140: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 140: the queue drains before the storm", "a"), "round 140: the queue drains before the storm"),
    (("round 140: the queue drains before the storm", "zz"), "qntmc 140: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 140: the queue drains before the storm", "AgentU"), "ruyaw 140: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 140: the queue drains before the storm", "keyboard"), "bssor 140: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 140: the queue drains before the storm", "AA"), "round 140: the queue drains before the storm"),
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
