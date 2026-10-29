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
    (("kitten106", "key"), "umrdil106"),
    (("kitten106", "lemon"), "vmfhry106"),
    (("kitten106", "a"), "kitten106"),
    (("kitten106", "zz"), "jhssdm106"),
    (("kitten106", "AgentU"), "koxgxh106"),
    (("kitten106", "keyboard"), "umrusn106"),
    (("kitten106", "AA"), "kitten106"),
    (("sitting106", "key"), "cmrdmlq106"),
    (("sitting106", "lemon"), "dmfhvyk106"),
    (("sitting106", "a"), "sitting106"),
    (("sitting106", "zz"), "rhsshmf106"),
    (("sitting106", "AgentU"), "soxgbhg106"),
    (("sitting106", "keyboard"), "cmruwnx106"),
    (("sitting106", "AA"), "sitting106"),
    (("agent106", "key"), "kkcxx106"),
    (("agent106", "lemon"), "lkqbg106"),
    (("agent106", "a"), "agent106"),
    (("agent106", "zz"), "zfdms106"),
    (("agent106", "AgentU"), "amiam106"),
    (("agent106", "keyboard"), "kkcoh106"),
    (("agent106", "AA"), "agent106"),
    (("angle106", "key"), "krevi106"),
    (("angle106", "lemon"), "lrszr106"),
    (("angle106", "a"), "angle106"),
    (("angle106", "zz"), "zmfkd106"),
    (("angle106", "AgentU"), "atkyx106"),
    (("angle106", "keyboard"), "krems106"),
    (("angle106", "AA"), "angle106"),
    (("universe106", "key"), "ergfipci106"),
    (("universe106", "lemon"), "frujrcwq106"),
    (("universe106", "a"), "universe106"),
    (("universe106", "zz"), "tmhudqrd106"),
    (("universe106", "AgentU"), "utmixlsk106"),
    (("universe106", "keyboard"), "ergwsrjh106"),
    (("universe106", "AA"), "universe106"),
    (("memory106", "key"), "wikyvw106"),
    (("memory106", "lemon"), "xiycej106"),
    (("memory106", "a"), "memory106"),
    (("memory106", "zz"), "ldlnqx106"),
    (("memory106", "AgentU"), "mkqbks106"),
    (("memory106", "keyboard"), "wikpfy106"),
    (("memory106", "AA"), "memory106"),
    (("stream106", "key"), "cxpoek106"),
    (("stream106", "lemon"), "dxdsnx106"),
    (("stream106", "a"), "stream106"),
    (("stream106", "zz"), "rsqdzl106"),
    (("stream106", "AgentU"), "szvrtg106"),
    (("stream106", "keyboard"), "cxpfom106"),
    (("stream106", "AA"), "stream106"),
    (("context106", "key"), "msldivd106"),
    (("context106", "lemon"), "nszhrix106"),
    (("context106", "a"), "context106"),
    (("context106", "zz"), "bnmsdws106"),
    (("context106", "AgentU"), "curgxrt106"),
    (("context106", "keyboard"), "mslusxk106"),
    (("context106", "AA"), "context106"),
    (("knowledge106", "key"), "urmgpcnkc106"),
    (("knowledge106", "lemon"), "vrakyphss106"),
    (("knowledge106", "a"), "knowledge106"),
    (("knowledge106", "zz"), "jmnvkdcfd106"),
    (("knowledge106", "AgentU"), "ktsjeydmi106"),
    (("knowledge106", "keyboard"), "urmxzeujo106"),
    (("knowledge106", "AA"), "knowledge106"),
    (("vector106", "key"), "fiadsp106"),
    (("vector106", "lemon"), "giohbc106"),
    (("vector106", "a"), "vector106"),
    (("vector106", "zz"), "udbsnq106"),
    (("vector106", "AgentU"), "vkgghl106"),
    (("vector106", "keyboard"), "fiaucr106"),
    (("vector106", "AA"), "vector106"),
    (("processor106", "key"), "zvmmiqcsp106"),
    (("processor106", "lemon"), "avaqrdwaf106"),
    (("processor106", "a"), "processor106"),
    (("processor106", "zz"), "oqnbdrrnq106"),
    (("processor106", "AgentU"), "pxspxmsuv106"),
    (("processor106", "keyboard"), "zvmdssjrb106"),
    (("processor106", "AA"), "processor106"),
    (("reasoning106", "key"), "biycslsre106"),
    (("reasoning106", "lemon"), "cimgbymzu106"),
    (("reasoning106", "a"), "reasoning106"),
    (("reasoning106", "zz"), "qdzrnmhmf106"),
    (("reasoning106", "AgentU"), "rkefhhitk106"),
    (("reasoning106", "keyboard"), "biytcnzqq106"),
    (("reasoning106", "AA"), "reasoning106"),
    (("machine106", "key"), "wearmlo106"),
    (("machine106", "lemon"), "xeovvyi106"),
    (("machine106", "a"), "machine106"),
    (("machine106", "zz"), "lzbghmd106"),
    (("machine106", "AgentU"), "mggubhe106"),
    (("machine106", "keyboard"), "weaiwnv106"),
    (("machine106", "AA"), "machine106"),
    (("learning106", "key"), "viybrgxk106"),
    (("learning106", "lemon"), "wimfatrs106"),
    (("learning106", "a"), "learning106"),
    (("learning106", "zz"), "kdzqmhmf106"),
    (("learning106", "AgentU"), "lkeegcnm106"),
    (("learning106", "keyboard"), "viysbiej106"),
    (("learning106", "AA"), "learning106"),
    (("model106", "key"), "wsbop106"),
    (("model106", "lemon"), "xspsy106"),
    (("model106", "a"), "model106"),
    (("model106", "zz"), "lncdk106"),
    (("model106", "AgentU"), "muhre106"),
    (("model106", "keyboard"), "wsbfz106"),
    (("model106", "AA"), "model106"),
    (("token106", "key"), "dsior106"),
    (("token106", "lemon"), "eswsa106"),
    (("token106", "a"), "token106"),
    (("token106", "zz"), "snjdm106"),
    (("token106", "AgentU"), "tuorg106"),
    (("token106", "keyboard"), "dsifb106"),
    (("token106", "AA"), "token106"),
    (("prompt106", "key"), "zvmwtr106"),
    (("prompt106", "lemon"), "avaace106"),
    (("prompt106", "a"), "prompt106"),
    (("prompt106", "zz"), "oqnlos106"),
    (("prompt106", "AgentU"), "pxszin106"),
    (("prompt106", "keyboard"), "zvmndt106"),
    (("prompt106", "AA"), "prompt106"),
    (("session106", "key"), "ciqcmmx106"),
    (("session106", "lemon"), "diegvzr106"),
    (("session106", "a"), "session106"),
    (("session106", "zz"), "rdrrhnm106"),
    (("session106", "AgentU"), "skwfbin106"),
    (("session106", "keyboard"), "ciqtwoe106"),
    (("session106", "AA"), "session106"),
    (("library106", "key"), "vmzbepi106"),
    (("library106", "lemon"), "wmnfncc106"),
    (("library106", "a"), "library106"),
    (("library106", "zz"), "khaqzqx106"),
    (("library106", "AgentU"), "lofetly106"),
    (("library106", "keyboard"), "vmzsorp106"),
    (("library106", "AA"), "library106"),
    (("service106", "key"), "cipfmao106"),
    (("service106", "lemon"), "didjvni106"),
    (("service106", "a"), "service106"),
    (("service106", "zz"), "rdquhbd106"),
    (("service106", "AgentU"), "skvibwe106"),
    (("service106", "keyboard"), "cipwwcv106"),
    (("service106", "AA"), "service106"),
    (("gateway106", "key"), "qeroayi106"),
    (("gateway106", "lemon"), "refsjlc106"),
    (("gateway106", "a"), "gateway106"),
    (("gateway106", "zz"), "fzsdvzx106"),
    (("gateway106", "AgentU"), "ggxrpuy106"),
    (("gateway106", "keyboard"), "qerfkap106"),
    (("gateway106", "AA"), "gateway106"),
    (("storage106", "key"), "cxmbeeo106"),
    (("storage106", "lemon"), "dxafnri106"),
    (("storage106", "a"), "storage106"),
    (("storage106", "zz"), "rsnqzfd106"),
    (("storage106", "AgentU"), "szsetae106"),
    (("storage106", "keyboard"), "cxmsogv106"),
    (("storage106", "AA"), "storage106"),
    (("network106", "key"), "xirgspu106"),
    (("network106", "lemon"), "yifkbco106"),
    (("network106", "a"), "network106"),
    (("network106", "zz"), "mdsvnqj106"),
    (("network106", "AgentU"), "nkxjhlk106"),
    (("network106", "keyboard"), "xirxcrb106"),
    (("network106", "AA"), "network106"),
    (("latency106", "key"), "verorai106"),
    (("latency106", "lemon"), "wefsanc106"),
    (("latency106", "a"), "latency106"),
    (("latency106", "zz"), "kzsdmbx106"),
    (("latency106", "AgentU"), "lgxrgwy106"),
    (("latency106", "keyboard"), "verfbcp106"),
    (("latency106", "AA"), "latency106"),
    (("buffer106", "key"), "lydpip106"),
    (("buffer106", "lemon"), "myrtrc106"),
    (("buffer106", "a"), "buffer106"),
    (("buffer106", "zz"), "ateedq106"),
    (("buffer106", "AgentU"), "bajsxl106"),
    (("buffer106", "keyboard"), "lydgsr106"),
    (("buffer106", "AA"), "buffer106"),
    (("queue106", "key"), "aycei106"),
    (("queue106", "lemon"), "byqir106"),
    (("queue106", "a"), "queue106"),
    (("queue106", "zz"), "ptdtd106"),
    (("queue106", "AgentU"), "qaihx106"),
    (("queue106", "keyboard"), "aycvs106"),
    (("queue106", "AA"), "queue106"),
    (("worker106", "key"), "gspuip106"),
    (("worker106", "lemon"), "hsdyrc106"),
    (("worker106", "a"), "worker106"),
    (("worker106", "zz"), "vnqjdq106"),
    (("worker106", "AgentU"), "wuvxxl106"),
    (("worker106", "keyboard"), "gsplsr106"),
    (("worker106", "AA"), "worker106"),
    (("kernel106", "key"), "uipxij106"),
    (("kernel106", "lemon"), "vidbrw106"),
    (("kernel106", "a"), "kernel106"),
    (("kernel106", "zz"), "jdqmdk106"),
    (("kernel106", "AgentU"), "kkvaxf106"),
    (("kernel106", "keyboard"), "uiposl106"),
    (("kernel106", "AA"), "kernel106"),
    (("signal106", "key"), "cmexej106"),
    (("signal106", "lemon"), "dmsbnw106"),
    (("signal106", "a"), "signal106"),
    (("signal106", "zz"), "rhfmzk106"),
    (("signal106", "AgentU"), "sokatf106"),
    (("signal106", "keyboard"), "cmeool106"),
    (("signal106", "AA"), "signal106"),
    (("packet106", "key"), "zeauir106"),
    (("packet106", "lemon"), "aeoyre106"),
    (("packet106", "a"), "packet106"),
    (("packet106", "zz"), "ozbjds106"),
    (("packet106", "AgentU"), "pggxxn106"),
    (("packet106", "keyboard"), "zealst106"),
    (("packet106", "AA"), "packet106"),
    (("router106", "key"), "bssdip106"),
    (("router106", "lemon"), "csghrc106"),
    (("router106", "a"), "router106"),
    (("router106", "zz"), "qntsdq106"),
    (("router106", "AgentU"), "ruygxl106"),
    (("router106", "keyboard"), "bssusr106"),
    (("router106", "AA"), "router106"),
    (("cluster106", "key"), "mpscxcb106"),
    (("cluster106", "lemon"), "npgggpv106"),
    (("cluster106", "a"), "cluster106"),
    (("cluster106", "zz"), "bktrsdq106"),
    (("cluster106", "AgentU"), "cryfmyr106"),
    (("cluster106", "keyboard"), "mpsthei106"),
    (("cluster106", "AA"), "cluster106"),
    (("mirror106", "key"), "wmpbsp106"),
    (("mirror106", "lemon"), "xmdfbc106"),
    (("mirror106", "a"), "mirror106"),
    (("mirror106", "zz"), "lhqqnq106"),
    (("mirror106", "AgentU"), "movehl106"),
    (("mirror106", "keyboard"), "wmpscr106"),
    (("mirror106", "AA"), "mirror106"),
    (("filter106", "key"), "pmjdip106"),
    (("filter106", "lemon"), "qmxhrc106"),
    (("filter106", "a"), "filter106"),
    (("filter106", "zz"), "ehksdq106"),
    (("filter106", "AgentU"), "fopgxl106"),
    (("filter106", "keyboard"), "pmjusr106"),
    (("filter106", "AA"), "filter106"),
    (("ranking106", "key"), "belumlq106"),
    (("ranking106", "lemon"), "cezyvyk106"),
    (("ranking106", "a"), "ranking106"),
    (("ranking106", "zz"), "qzmjhmf106"),
    (("ranking106", "AgentU"), "rgrxbhg106"),
    (("ranking106", "keyboard"), "bellwnx106"),
    (("ranking106", "AA"), "ranking106"),
    (("encoding106", "key"), "orayhgxk106"),
    (("encoding106", "lemon"), "procqtrs106"),
    (("encoding106", "a"), "encoding106"),
    (("encoding106", "zz"), "dmbnchmf106"),
    (("encoding106", "AgentU"), "etgbwcnm106"),
    (("encoding106", "keyboard"), "orapriej106"),
    (("encoding106", "AA"), "encoding106"),
    (("mapping106", "key"), "wenzmlq106"),
    (("mapping106", "lemon"), "xebdvyk106"),
    (("mapping106", "a"), "mapping106"),
    (("mapping106", "zz"), "lzoohmf106"),
    (("mapping106", "AgentU"), "mgtcbhg106"),
    (("mapping106", "keyboard"), "wenqwnx106"),
    (("mapping106", "AA"), "mapping106"),
    (("record106", "key"), "biayvb106"),
    (("record106", "lemon"), "cioceo106"),
    (("record106", "a"), "record106"),
    (("record106", "zz"), "qdbnqc106"),
    (("record106", "AgentU"), "rkgbkx106"),
    (("record106", "keyboard"), "biapfd106"),
    (("record106", "AA"), "record106"),
    (("candle106", "key"), "melnpc106"),
    (("candle106", "lemon"), "nezryp106"),
    (("candle106", "a"), "candle106"),
    (("candle106", "zz"), "bzmckd106"),
    (("candle106", "AgentU"), "cgrqey106"),
    (("candle106", "keyboard"), "meleze106"),
    (("candle106", "AA"), "candle106"),
    (("thread106", "key"), "dlpoeb106"),
    (("thread106", "lemon"), "eldsno106"),
    (("thread106", "a"), "thread106"),
    (("thread106", "zz"), "sgqdzc106"),
    (("thread106", "AgentU"), "tnvrtx106"),
    (("thread106", "keyboard"), "dlpfod106"),
    (("thread106", "AA"), "thread106"),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 106: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 106: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "a"),
        "round 106: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 106: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 106: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 106: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", "AA"),
        "round 106: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "key"),
        "bssxh 106: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 106: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "a"),
        "round 106: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 106: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 106: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 106: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", "AA"),
        "round 106: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 106: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 106: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "a"),
        "round 106: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 106: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 106: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 106: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", "AA"),
        "round 106: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 106: the processor reads the record then stops", "key"),
        "bssxh 106: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 106: the processor reads the record then stops", "lemon"),
        "csgbq 106: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 106: the processor reads the record then stops", "a"),
        "round 106: the processor reads the record then stops",
    ),
    (
        ("round 106: the processor reads the record then stops", "zz"),
        "qntmc 106: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 106: the processor reads the record then stops", "AgentU"),
        "ruyaw 106: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 106: the processor reads the record then stops", "keyboard"),
        "bssor 106: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 106: the processor reads the record then stops", "AA"),
        "round 106: the processor reads the record then stops",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "key"),
        "bssxh 106: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "lemon"),
        "csgbq 106: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "a"),
        "round 106: a worker pulls the next task from the queue",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "zz"),
        "qntmc 106: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 106: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "keyboard"),
        "bssor 106: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 106: a worker pulls the next task from the queue", "AA"),
        "round 106: a worker pulls the next task from the queue",
    ),
    (
        ("round 106: signals travel through the network layer", "key"),
        "bssxh 106: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 106: signals travel through the network layer", "lemon"),
        "csgbq 106: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 106: signals travel through the network layer", "a"),
        "round 106: signals travel through the network layer",
    ),
    (
        ("round 106: signals travel through the network layer", "zz"),
        "qntmc 106: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 106: signals travel through the network layer", "AgentU"),
        "ruyaw 106: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 106: signals travel through the network layer", "keyboard"),
        "bssor 106: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 106: signals travel through the network layer", "AA"),
        "round 106: signals travel through the network layer",
    ),
    (
        ("round 106: the gateway routes each request by policy", "key"),
        "bssxh 106: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 106: the gateway routes each request by policy", "lemon"),
        "csgbq 106: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 106: the gateway routes each request by policy", "a"),
        "round 106: the gateway routes each request by policy",
    ),
    (
        ("round 106: the gateway routes each request by policy", "zz"),
        "qntmc 106: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 106: the gateway routes each request by policy", "AgentU"),
        "ruyaw 106: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 106: the gateway routes each request by policy", "keyboard"),
        "bssor 106: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 106: the gateway routes each request by policy", "AA"),
        "round 106: the gateway routes each request by policy",
    ),
    (("round 106: memory grows until the buffer is full", "key"), "bssxh 106: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 106: memory grows until the buffer is full", "lemon"), "csgbq 106: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 106: memory grows until the buffer is full", "a"), "round 106: memory grows until the buffer is full"),
    (("round 106: memory grows until the buffer is full", "zz"), "qntmc 106: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 106: memory grows until the buffer is full", "AgentU"),
        "ruyaw 106: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 106: memory grows until the buffer is full", "keyboard"),
        "bssor 106: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 106: memory grows until the buffer is full", "AA"), "round 106: memory grows until the buffer is full"),
    (("round 106: the cluster mirrors every packet twice", "key"), "bssxh 106: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 106: the cluster mirrors every packet twice", "lemon"),
        "csgbq 106: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 106: the cluster mirrors every packet twice", "a"), "round 106: the cluster mirrors every packet twice"),
    (("round 106: the cluster mirrors every packet twice", "zz"), "qntmc 106: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 106: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 106: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 106: the cluster mirrors every packet twice", "keyboard"),
        "bssor 106: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 106: the cluster mirrors every packet twice", "AA"), "round 106: the cluster mirrors every packet twice"),
    (
        ("round 106: ranking uses tokens learned from the corpus", "key"),
        "bssxh 106: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 106: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", "a"),
        "round 106: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 106: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 106: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 106: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", "AA"),
        "round 106: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 106: a long session ends when the candle dies", "key"),
        "bssxh 106: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 106: a long session ends when the candle dies", "lemon"),
        "csgbq 106: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 106: a long session ends when the candle dies", "a"),
        "round 106: a long session ends when the candle dies",
    ),
    (
        ("round 106: a long session ends when the candle dies", "zz"),
        "qntmc 106: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 106: a long session ends when the candle dies", "AgentU"),
        "ruyaw 106: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 106: a long session ends when the candle dies", "keyboard"),
        "bssor 106: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 106: a long session ends when the candle dies", "AA"),
        "round 106: a long session ends when the candle dies",
    ),
    (("round 106: encode the prompt then map the result", "key"), "bssxh 106: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 106: encode the prompt then map the result", "lemon"), "csgbq 106: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 106: encode the prompt then map the result", "a"), "round 106: encode the prompt then map the result"),
    (("round 106: encode the prompt then map the result", "zz"), "qntmc 106: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 106: encode the prompt then map the result", "AgentU"),
        "ruyaw 106: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 106: encode the prompt then map the result", "keyboard"),
        "bssor 106: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 106: encode the prompt then map the result", "AA"), "round 106: encode the prompt then map the result"),
    (("round 106: the kernel wakes the worker at dawn", "key"), "bssxh 106: rri iovlop ukocc xfo ambocb er neux"),
    (("round 106: the kernel wakes the worker at dawn", "lemon"), "csgbq 106: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 106: the kernel wakes the worker at dawn", "a"), "round 106: the kernel wakes the worker at dawn"),
    (("round 106: the kernel wakes the worker at dawn", "zz"), "qntmc 106: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 106: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 106: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 106: the kernel wakes the worker at dawn", "keyboard"), "bssor 106: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 106: the kernel wakes the worker at dawn", "AA"), "round 106: the kernel wakes the worker at dawn"),
    (("round 106: service latency drops after the patch", "key"), "bssxh 106: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 106: service latency drops after the patch", "lemon"), "csgbq 106: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 106: service latency drops after the patch", "a"), "round 106: service latency drops after the patch"),
    (("round 106: service latency drops after the patch", "zz"), "qntmc 106: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 106: service latency drops after the patch", "AgentU"),
        "ruyaw 106: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 106: service latency drops after the patch", "keyboard"),
        "bssor 106: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 106: service latency drops after the patch", "AA"), "round 106: service latency drops after the patch"),
    (
        ("round 106: the library caches every vector it sees", "key"),
        "bssxh 106: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 106: the library caches every vector it sees", "lemon"),
        "csgbq 106: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 106: the library caches every vector it sees", "a"), "round 106: the library caches every vector it sees"),
    (
        ("round 106: the library caches every vector it sees", "zz"),
        "qntmc 106: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 106: the library caches every vector it sees", "AgentU"),
        "ruyaw 106: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 106: the library caches every vector it sees", "keyboard"),
        "bssor 106: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 106: the library caches every vector it sees", "AA"),
        "round 106: the library caches every vector it sees",
    ),
    (("round 106: agents argue then the debate resolves", "key"), "bssxh 106: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 106: agents argue then the debate resolves", "lemon"), "csgbq 106: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 106: agents argue then the debate resolves", "a"), "round 106: agents argue then the debate resolves"),
    (("round 106: agents argue then the debate resolves", "zz"), "qntmc 106: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 106: agents argue then the debate resolves", "AgentU"),
        "ruyaw 106: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 106: agents argue then the debate resolves", "keyboard"),
        "bssor 106: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 106: agents argue then the debate resolves", "AA"), "round 106: agents argue then the debate resolves"),
    (("round 106: the filter keeps only strong matches", "key"), "bssxh 106: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 106: the filter keeps only strong matches", "lemon"), "csgbq 106: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 106: the filter keeps only strong matches", "a"), "round 106: the filter keeps only strong matches"),
    (("round 106: the filter keeps only strong matches", "zz"), "qntmc 106: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 106: the filter keeps only strong matches", "AgentU"), "ruyaw 106: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 106: the filter keeps only strong matches", "keyboard"),
        "bssor 106: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 106: the filter keeps only strong matches", "AA"), "round 106: the filter keeps only strong matches"),
    (("round 106: the model answers with a short reply", "key"), "bssxh 106: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 106: the model answers with a short reply", "lemon"), "csgbq 106: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 106: the model answers with a short reply", "a"), "round 106: the model answers with a short reply"),
    (("round 106: the model answers with a short reply", "zz"), "qntmc 106: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 106: the model answers with a short reply", "AgentU"), "ruyaw 106: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 106: the model answers with a short reply", "keyboard"),
        "bssor 106: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 106: the model answers with a short reply", "AA"), "round 106: the model answers with a short reply"),
    (
        ("round 106: the recorder stores the reasoning trace", "key"),
        "bssxh 106: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 106: the recorder stores the reasoning trace", "lemon"),
        "csgbq 106: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 106: the recorder stores the reasoning trace", "a"), "round 106: the recorder stores the reasoning trace"),
    (
        ("round 106: the recorder stores the reasoning trace", "zz"),
        "qntmc 106: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 106: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 106: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 106: the recorder stores the reasoning trace", "keyboard"),
        "bssor 106: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 106: the recorder stores the reasoning trace", "AA"),
        "round 106: the recorder stores the reasoning trace",
    ),
    (("round 106: the angel watches the processor run", "key"), "bssxh 106: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 106: the angel watches the processor run", "lemon"), "csgbq 106: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 106: the angel watches the processor run", "a"), "round 106: the angel watches the processor run"),
    (("round 106: the angel watches the processor run", "zz"), "qntmc 106: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 106: the angel watches the processor run", "AgentU"), "ruyaw 106: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 106: the angel watches the processor run", "keyboard"), "bssor 106: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 106: the angel watches the processor run", "AA"), "round 106: the angel watches the processor run"),
    (("round 106: angle of the vector decides the match", "key"), "bssxh 106: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 106: angle of the vector decides the match", "lemon"), "csgbq 106: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 106: angle of the vector decides the match", "a"), "round 106: angle of the vector decides the match"),
    (("round 106: angle of the vector decides the match", "zz"), "qntmc 106: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 106: angle of the vector decides the match", "AgentU"),
        "ruyaw 106: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 106: angle of the vector decides the match", "keyboard"),
        "bssor 106: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 106: angle of the vector decides the match", "AA"), "round 106: angle of the vector decides the match"),
    (
        ("round 106: the candle burns twice as long at night", "key"),
        "bssxh 106: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 106: the candle burns twice as long at night", "lemon"),
        "csgbq 106: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 106: the candle burns twice as long at night", "a"), "round 106: the candle burns twice as long at night"),
    (
        ("round 106: the candle burns twice as long at night", "zz"),
        "qntmc 106: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 106: the candle burns twice as long at night", "AgentU"),
        "ruyaw 106: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 106: the candle burns twice as long at night", "keyboard"),
        "bssor 106: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 106: the candle burns twice as long at night", "AA"),
        "round 106: the candle burns twice as long at night",
    ),
    (("round 106: a mirror of the universe in one line", "key"), "bssxh 106: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 106: a mirror of the universe in one line", "lemon"), "csgbq 106: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 106: a mirror of the universe in one line", "a"), "round 106: a mirror of the universe in one line"),
    (("round 106: a mirror of the universe in one line", "zz"), "qntmc 106: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 106: a mirror of the universe in one line", "AgentU"), "ruyaw 106: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 106: a mirror of the universe in one line", "keyboard"),
        "bssor 106: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 106: a mirror of the universe in one line", "AA"), "round 106: a mirror of the universe in one line"),
    (("round 106: the queue drains before the storm", "key"), "bssxh 106: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 106: the queue drains before the storm", "lemon"), "csgbq 106: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 106: the queue drains before the storm", "a"), "round 106: the queue drains before the storm"),
    (("round 106: the queue drains before the storm", "zz"), "qntmc 106: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 106: the queue drains before the storm", "AgentU"), "ruyaw 106: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 106: the queue drains before the storm", "keyboard"), "bssor 106: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 106: the queue drains before the storm", "AA"), "round 106: the queue drains before the storm"),
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
