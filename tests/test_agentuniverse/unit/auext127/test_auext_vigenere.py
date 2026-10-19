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
    (("kitten127", "key"), "umrdil127"),
    (("kitten127", "lemon"), "vmfhry127"),
    (("kitten127", "a"), "kitten127"),
    (("kitten127", "zz"), "jhssdm127"),
    (("kitten127", "AgentU"), "koxgxh127"),
    (("kitten127", "keyboard"), "umrusn127"),
    (("kitten127", "AA"), "kitten127"),
    (("sitting127", "key"), "cmrdmlq127"),
    (("sitting127", "lemon"), "dmfhvyk127"),
    (("sitting127", "a"), "sitting127"),
    (("sitting127", "zz"), "rhsshmf127"),
    (("sitting127", "AgentU"), "soxgbhg127"),
    (("sitting127", "keyboard"), "cmruwnx127"),
    (("sitting127", "AA"), "sitting127"),
    (("agent127", "key"), "kkcxx127"),
    (("agent127", "lemon"), "lkqbg127"),
    (("agent127", "a"), "agent127"),
    (("agent127", "zz"), "zfdms127"),
    (("agent127", "AgentU"), "amiam127"),
    (("agent127", "keyboard"), "kkcoh127"),
    (("agent127", "AA"), "agent127"),
    (("angle127", "key"), "krevi127"),
    (("angle127", "lemon"), "lrszr127"),
    (("angle127", "a"), "angle127"),
    (("angle127", "zz"), "zmfkd127"),
    (("angle127", "AgentU"), "atkyx127"),
    (("angle127", "keyboard"), "krems127"),
    (("angle127", "AA"), "angle127"),
    (("universe127", "key"), "ergfipci127"),
    (("universe127", "lemon"), "frujrcwq127"),
    (("universe127", "a"), "universe127"),
    (("universe127", "zz"), "tmhudqrd127"),
    (("universe127", "AgentU"), "utmixlsk127"),
    (("universe127", "keyboard"), "ergwsrjh127"),
    (("universe127", "AA"), "universe127"),
    (("memory127", "key"), "wikyvw127"),
    (("memory127", "lemon"), "xiycej127"),
    (("memory127", "a"), "memory127"),
    (("memory127", "zz"), "ldlnqx127"),
    (("memory127", "AgentU"), "mkqbks127"),
    (("memory127", "keyboard"), "wikpfy127"),
    (("memory127", "AA"), "memory127"),
    (("stream127", "key"), "cxpoek127"),
    (("stream127", "lemon"), "dxdsnx127"),
    (("stream127", "a"), "stream127"),
    (("stream127", "zz"), "rsqdzl127"),
    (("stream127", "AgentU"), "szvrtg127"),
    (("stream127", "keyboard"), "cxpfom127"),
    (("stream127", "AA"), "stream127"),
    (("context127", "key"), "msldivd127"),
    (("context127", "lemon"), "nszhrix127"),
    (("context127", "a"), "context127"),
    (("context127", "zz"), "bnmsdws127"),
    (("context127", "AgentU"), "curgxrt127"),
    (("context127", "keyboard"), "mslusxk127"),
    (("context127", "AA"), "context127"),
    (("knowledge127", "key"), "urmgpcnkc127"),
    (("knowledge127", "lemon"), "vrakyphss127"),
    (("knowledge127", "a"), "knowledge127"),
    (("knowledge127", "zz"), "jmnvkdcfd127"),
    (("knowledge127", "AgentU"), "ktsjeydmi127"),
    (("knowledge127", "keyboard"), "urmxzeujo127"),
    (("knowledge127", "AA"), "knowledge127"),
    (("vector127", "key"), "fiadsp127"),
    (("vector127", "lemon"), "giohbc127"),
    (("vector127", "a"), "vector127"),
    (("vector127", "zz"), "udbsnq127"),
    (("vector127", "AgentU"), "vkgghl127"),
    (("vector127", "keyboard"), "fiaucr127"),
    (("vector127", "AA"), "vector127"),
    (("processor127", "key"), "zvmmiqcsp127"),
    (("processor127", "lemon"), "avaqrdwaf127"),
    (("processor127", "a"), "processor127"),
    (("processor127", "zz"), "oqnbdrrnq127"),
    (("processor127", "AgentU"), "pxspxmsuv127"),
    (("processor127", "keyboard"), "zvmdssjrb127"),
    (("processor127", "AA"), "processor127"),
    (("reasoning127", "key"), "biycslsre127"),
    (("reasoning127", "lemon"), "cimgbymzu127"),
    (("reasoning127", "a"), "reasoning127"),
    (("reasoning127", "zz"), "qdzrnmhmf127"),
    (("reasoning127", "AgentU"), "rkefhhitk127"),
    (("reasoning127", "keyboard"), "biytcnzqq127"),
    (("reasoning127", "AA"), "reasoning127"),
    (("machine127", "key"), "wearmlo127"),
    (("machine127", "lemon"), "xeovvyi127"),
    (("machine127", "a"), "machine127"),
    (("machine127", "zz"), "lzbghmd127"),
    (("machine127", "AgentU"), "mggubhe127"),
    (("machine127", "keyboard"), "weaiwnv127"),
    (("machine127", "AA"), "machine127"),
    (("learning127", "key"), "viybrgxk127"),
    (("learning127", "lemon"), "wimfatrs127"),
    (("learning127", "a"), "learning127"),
    (("learning127", "zz"), "kdzqmhmf127"),
    (("learning127", "AgentU"), "lkeegcnm127"),
    (("learning127", "keyboard"), "viysbiej127"),
    (("learning127", "AA"), "learning127"),
    (("model127", "key"), "wsbop127"),
    (("model127", "lemon"), "xspsy127"),
    (("model127", "a"), "model127"),
    (("model127", "zz"), "lncdk127"),
    (("model127", "AgentU"), "muhre127"),
    (("model127", "keyboard"), "wsbfz127"),
    (("model127", "AA"), "model127"),
    (("token127", "key"), "dsior127"),
    (("token127", "lemon"), "eswsa127"),
    (("token127", "a"), "token127"),
    (("token127", "zz"), "snjdm127"),
    (("token127", "AgentU"), "tuorg127"),
    (("token127", "keyboard"), "dsifb127"),
    (("token127", "AA"), "token127"),
    (("prompt127", "key"), "zvmwtr127"),
    (("prompt127", "lemon"), "avaace127"),
    (("prompt127", "a"), "prompt127"),
    (("prompt127", "zz"), "oqnlos127"),
    (("prompt127", "AgentU"), "pxszin127"),
    (("prompt127", "keyboard"), "zvmndt127"),
    (("prompt127", "AA"), "prompt127"),
    (("session127", "key"), "ciqcmmx127"),
    (("session127", "lemon"), "diegvzr127"),
    (("session127", "a"), "session127"),
    (("session127", "zz"), "rdrrhnm127"),
    (("session127", "AgentU"), "skwfbin127"),
    (("session127", "keyboard"), "ciqtwoe127"),
    (("session127", "AA"), "session127"),
    (("library127", "key"), "vmzbepi127"),
    (("library127", "lemon"), "wmnfncc127"),
    (("library127", "a"), "library127"),
    (("library127", "zz"), "khaqzqx127"),
    (("library127", "AgentU"), "lofetly127"),
    (("library127", "keyboard"), "vmzsorp127"),
    (("library127", "AA"), "library127"),
    (("service127", "key"), "cipfmao127"),
    (("service127", "lemon"), "didjvni127"),
    (("service127", "a"), "service127"),
    (("service127", "zz"), "rdquhbd127"),
    (("service127", "AgentU"), "skvibwe127"),
    (("service127", "keyboard"), "cipwwcv127"),
    (("service127", "AA"), "service127"),
    (("gateway127", "key"), "qeroayi127"),
    (("gateway127", "lemon"), "refsjlc127"),
    (("gateway127", "a"), "gateway127"),
    (("gateway127", "zz"), "fzsdvzx127"),
    (("gateway127", "AgentU"), "ggxrpuy127"),
    (("gateway127", "keyboard"), "qerfkap127"),
    (("gateway127", "AA"), "gateway127"),
    (("storage127", "key"), "cxmbeeo127"),
    (("storage127", "lemon"), "dxafnri127"),
    (("storage127", "a"), "storage127"),
    (("storage127", "zz"), "rsnqzfd127"),
    (("storage127", "AgentU"), "szsetae127"),
    (("storage127", "keyboard"), "cxmsogv127"),
    (("storage127", "AA"), "storage127"),
    (("network127", "key"), "xirgspu127"),
    (("network127", "lemon"), "yifkbco127"),
    (("network127", "a"), "network127"),
    (("network127", "zz"), "mdsvnqj127"),
    (("network127", "AgentU"), "nkxjhlk127"),
    (("network127", "keyboard"), "xirxcrb127"),
    (("network127", "AA"), "network127"),
    (("latency127", "key"), "verorai127"),
    (("latency127", "lemon"), "wefsanc127"),
    (("latency127", "a"), "latency127"),
    (("latency127", "zz"), "kzsdmbx127"),
    (("latency127", "AgentU"), "lgxrgwy127"),
    (("latency127", "keyboard"), "verfbcp127"),
    (("latency127", "AA"), "latency127"),
    (("buffer127", "key"), "lydpip127"),
    (("buffer127", "lemon"), "myrtrc127"),
    (("buffer127", "a"), "buffer127"),
    (("buffer127", "zz"), "ateedq127"),
    (("buffer127", "AgentU"), "bajsxl127"),
    (("buffer127", "keyboard"), "lydgsr127"),
    (("buffer127", "AA"), "buffer127"),
    (("queue127", "key"), "aycei127"),
    (("queue127", "lemon"), "byqir127"),
    (("queue127", "a"), "queue127"),
    (("queue127", "zz"), "ptdtd127"),
    (("queue127", "AgentU"), "qaihx127"),
    (("queue127", "keyboard"), "aycvs127"),
    (("queue127", "AA"), "queue127"),
    (("worker127", "key"), "gspuip127"),
    (("worker127", "lemon"), "hsdyrc127"),
    (("worker127", "a"), "worker127"),
    (("worker127", "zz"), "vnqjdq127"),
    (("worker127", "AgentU"), "wuvxxl127"),
    (("worker127", "keyboard"), "gsplsr127"),
    (("worker127", "AA"), "worker127"),
    (("kernel127", "key"), "uipxij127"),
    (("kernel127", "lemon"), "vidbrw127"),
    (("kernel127", "a"), "kernel127"),
    (("kernel127", "zz"), "jdqmdk127"),
    (("kernel127", "AgentU"), "kkvaxf127"),
    (("kernel127", "keyboard"), "uiposl127"),
    (("kernel127", "AA"), "kernel127"),
    (("signal127", "key"), "cmexej127"),
    (("signal127", "lemon"), "dmsbnw127"),
    (("signal127", "a"), "signal127"),
    (("signal127", "zz"), "rhfmzk127"),
    (("signal127", "AgentU"), "sokatf127"),
    (("signal127", "keyboard"), "cmeool127"),
    (("signal127", "AA"), "signal127"),
    (("packet127", "key"), "zeauir127"),
    (("packet127", "lemon"), "aeoyre127"),
    (("packet127", "a"), "packet127"),
    (("packet127", "zz"), "ozbjds127"),
    (("packet127", "AgentU"), "pggxxn127"),
    (("packet127", "keyboard"), "zealst127"),
    (("packet127", "AA"), "packet127"),
    (("router127", "key"), "bssdip127"),
    (("router127", "lemon"), "csghrc127"),
    (("router127", "a"), "router127"),
    (("router127", "zz"), "qntsdq127"),
    (("router127", "AgentU"), "ruygxl127"),
    (("router127", "keyboard"), "bssusr127"),
    (("router127", "AA"), "router127"),
    (("cluster127", "key"), "mpscxcb127"),
    (("cluster127", "lemon"), "npgggpv127"),
    (("cluster127", "a"), "cluster127"),
    (("cluster127", "zz"), "bktrsdq127"),
    (("cluster127", "AgentU"), "cryfmyr127"),
    (("cluster127", "keyboard"), "mpsthei127"),
    (("cluster127", "AA"), "cluster127"),
    (("mirror127", "key"), "wmpbsp127"),
    (("mirror127", "lemon"), "xmdfbc127"),
    (("mirror127", "a"), "mirror127"),
    (("mirror127", "zz"), "lhqqnq127"),
    (("mirror127", "AgentU"), "movehl127"),
    (("mirror127", "keyboard"), "wmpscr127"),
    (("mirror127", "AA"), "mirror127"),
    (("filter127", "key"), "pmjdip127"),
    (("filter127", "lemon"), "qmxhrc127"),
    (("filter127", "a"), "filter127"),
    (("filter127", "zz"), "ehksdq127"),
    (("filter127", "AgentU"), "fopgxl127"),
    (("filter127", "keyboard"), "pmjusr127"),
    (("filter127", "AA"), "filter127"),
    (("ranking127", "key"), "belumlq127"),
    (("ranking127", "lemon"), "cezyvyk127"),
    (("ranking127", "a"), "ranking127"),
    (("ranking127", "zz"), "qzmjhmf127"),
    (("ranking127", "AgentU"), "rgrxbhg127"),
    (("ranking127", "keyboard"), "bellwnx127"),
    (("ranking127", "AA"), "ranking127"),
    (("encoding127", "key"), "orayhgxk127"),
    (("encoding127", "lemon"), "procqtrs127"),
    (("encoding127", "a"), "encoding127"),
    (("encoding127", "zz"), "dmbnchmf127"),
    (("encoding127", "AgentU"), "etgbwcnm127"),
    (("encoding127", "keyboard"), "orapriej127"),
    (("encoding127", "AA"), "encoding127"),
    (("mapping127", "key"), "wenzmlq127"),
    (("mapping127", "lemon"), "xebdvyk127"),
    (("mapping127", "a"), "mapping127"),
    (("mapping127", "zz"), "lzoohmf127"),
    (("mapping127", "AgentU"), "mgtcbhg127"),
    (("mapping127", "keyboard"), "wenqwnx127"),
    (("mapping127", "AA"), "mapping127"),
    (("record127", "key"), "biayvb127"),
    (("record127", "lemon"), "cioceo127"),
    (("record127", "a"), "record127"),
    (("record127", "zz"), "qdbnqc127"),
    (("record127", "AgentU"), "rkgbkx127"),
    (("record127", "keyboard"), "biapfd127"),
    (("record127", "AA"), "record127"),
    (("candle127", "key"), "melnpc127"),
    (("candle127", "lemon"), "nezryp127"),
    (("candle127", "a"), "candle127"),
    (("candle127", "zz"), "bzmckd127"),
    (("candle127", "AgentU"), "cgrqey127"),
    (("candle127", "keyboard"), "meleze127"),
    (("candle127", "AA"), "candle127"),
    (("thread127", "key"), "dlpoeb127"),
    (("thread127", "lemon"), "eldsno127"),
    (("thread127", "a"), "thread127"),
    (("thread127", "zz"), "sgqdzc127"),
    (("thread127", "AgentU"), "tnvrtx127"),
    (("thread127", "keyboard"), "dlpfod127"),
    (("thread127", "AA"), "thread127"),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 127: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 127: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "a"),
        "round 127: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 127: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 127: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 127: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", "AA"),
        "round 127: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "key"),
        "bssxh 127: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 127: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "a"),
        "round 127: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 127: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 127: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 127: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", "AA"),
        "round 127: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 127: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 127: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "a"),
        "round 127: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 127: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 127: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 127: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", "AA"),
        "round 127: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 127: the processor reads the record then stops", "key"),
        "bssxh 127: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 127: the processor reads the record then stops", "lemon"),
        "csgbq 127: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 127: the processor reads the record then stops", "a"),
        "round 127: the processor reads the record then stops",
    ),
    (
        ("round 127: the processor reads the record then stops", "zz"),
        "qntmc 127: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 127: the processor reads the record then stops", "AgentU"),
        "ruyaw 127: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 127: the processor reads the record then stops", "keyboard"),
        "bssor 127: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 127: the processor reads the record then stops", "AA"),
        "round 127: the processor reads the record then stops",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "key"),
        "bssxh 127: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "lemon"),
        "csgbq 127: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "a"),
        "round 127: a worker pulls the next task from the queue",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "zz"),
        "qntmc 127: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 127: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "keyboard"),
        "bssor 127: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 127: a worker pulls the next task from the queue", "AA"),
        "round 127: a worker pulls the next task from the queue",
    ),
    (
        ("round 127: signals travel through the network layer", "key"),
        "bssxh 127: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 127: signals travel through the network layer", "lemon"),
        "csgbq 127: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 127: signals travel through the network layer", "a"),
        "round 127: signals travel through the network layer",
    ),
    (
        ("round 127: signals travel through the network layer", "zz"),
        "qntmc 127: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 127: signals travel through the network layer", "AgentU"),
        "ruyaw 127: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 127: signals travel through the network layer", "keyboard"),
        "bssor 127: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 127: signals travel through the network layer", "AA"),
        "round 127: signals travel through the network layer",
    ),
    (
        ("round 127: the gateway routes each request by policy", "key"),
        "bssxh 127: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 127: the gateway routes each request by policy", "lemon"),
        "csgbq 127: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 127: the gateway routes each request by policy", "a"),
        "round 127: the gateway routes each request by policy",
    ),
    (
        ("round 127: the gateway routes each request by policy", "zz"),
        "qntmc 127: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 127: the gateway routes each request by policy", "AgentU"),
        "ruyaw 127: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 127: the gateway routes each request by policy", "keyboard"),
        "bssor 127: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 127: the gateway routes each request by policy", "AA"),
        "round 127: the gateway routes each request by policy",
    ),
    (("round 127: memory grows until the buffer is full", "key"), "bssxh 127: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 127: memory grows until the buffer is full", "lemon"), "csgbq 127: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 127: memory grows until the buffer is full", "a"), "round 127: memory grows until the buffer is full"),
    (("round 127: memory grows until the buffer is full", "zz"), "qntmc 127: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 127: memory grows until the buffer is full", "AgentU"),
        "ruyaw 127: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 127: memory grows until the buffer is full", "keyboard"),
        "bssor 127: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 127: memory grows until the buffer is full", "AA"), "round 127: memory grows until the buffer is full"),
    (("round 127: the cluster mirrors every packet twice", "key"), "bssxh 127: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 127: the cluster mirrors every packet twice", "lemon"),
        "csgbq 127: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 127: the cluster mirrors every packet twice", "a"), "round 127: the cluster mirrors every packet twice"),
    (("round 127: the cluster mirrors every packet twice", "zz"), "qntmc 127: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 127: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 127: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 127: the cluster mirrors every packet twice", "keyboard"),
        "bssor 127: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 127: the cluster mirrors every packet twice", "AA"), "round 127: the cluster mirrors every packet twice"),
    (
        ("round 127: ranking uses tokens learned from the corpus", "key"),
        "bssxh 127: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 127: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", "a"),
        "round 127: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 127: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 127: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 127: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", "AA"),
        "round 127: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 127: a long session ends when the candle dies", "key"),
        "bssxh 127: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 127: a long session ends when the candle dies", "lemon"),
        "csgbq 127: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 127: a long session ends when the candle dies", "a"),
        "round 127: a long session ends when the candle dies",
    ),
    (
        ("round 127: a long session ends when the candle dies", "zz"),
        "qntmc 127: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 127: a long session ends when the candle dies", "AgentU"),
        "ruyaw 127: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 127: a long session ends when the candle dies", "keyboard"),
        "bssor 127: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 127: a long session ends when the candle dies", "AA"),
        "round 127: a long session ends when the candle dies",
    ),
    (("round 127: encode the prompt then map the result", "key"), "bssxh 127: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 127: encode the prompt then map the result", "lemon"), "csgbq 127: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 127: encode the prompt then map the result", "a"), "round 127: encode the prompt then map the result"),
    (("round 127: encode the prompt then map the result", "zz"), "qntmc 127: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 127: encode the prompt then map the result", "AgentU"),
        "ruyaw 127: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 127: encode the prompt then map the result", "keyboard"),
        "bssor 127: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 127: encode the prompt then map the result", "AA"), "round 127: encode the prompt then map the result"),
    (("round 127: the kernel wakes the worker at dawn", "key"), "bssxh 127: rri iovlop ukocc xfo ambocb er neux"),
    (("round 127: the kernel wakes the worker at dawn", "lemon"), "csgbq 127: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 127: the kernel wakes the worker at dawn", "a"), "round 127: the kernel wakes the worker at dawn"),
    (("round 127: the kernel wakes the worker at dawn", "zz"), "qntmc 127: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 127: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 127: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 127: the kernel wakes the worker at dawn", "keyboard"), "bssor 127: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 127: the kernel wakes the worker at dawn", "AA"), "round 127: the kernel wakes the worker at dawn"),
    (("round 127: service latency drops after the patch", "key"), "bssxh 127: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 127: service latency drops after the patch", "lemon"), "csgbq 127: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 127: service latency drops after the patch", "a"), "round 127: service latency drops after the patch"),
    (("round 127: service latency drops after the patch", "zz"), "qntmc 127: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 127: service latency drops after the patch", "AgentU"),
        "ruyaw 127: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 127: service latency drops after the patch", "keyboard"),
        "bssor 127: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 127: service latency drops after the patch", "AA"), "round 127: service latency drops after the patch"),
    (
        ("round 127: the library caches every vector it sees", "key"),
        "bssxh 127: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 127: the library caches every vector it sees", "lemon"),
        "csgbq 127: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 127: the library caches every vector it sees", "a"), "round 127: the library caches every vector it sees"),
    (
        ("round 127: the library caches every vector it sees", "zz"),
        "qntmc 127: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 127: the library caches every vector it sees", "AgentU"),
        "ruyaw 127: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 127: the library caches every vector it sees", "keyboard"),
        "bssor 127: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 127: the library caches every vector it sees", "AA"),
        "round 127: the library caches every vector it sees",
    ),
    (("round 127: agents argue then the debate resolves", "key"), "bssxh 127: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 127: agents argue then the debate resolves", "lemon"), "csgbq 127: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 127: agents argue then the debate resolves", "a"), "round 127: agents argue then the debate resolves"),
    (("round 127: agents argue then the debate resolves", "zz"), "qntmc 127: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 127: agents argue then the debate resolves", "AgentU"),
        "ruyaw 127: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 127: agents argue then the debate resolves", "keyboard"),
        "bssor 127: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 127: agents argue then the debate resolves", "AA"), "round 127: agents argue then the debate resolves"),
    (("round 127: the filter keeps only strong matches", "key"), "bssxh 127: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 127: the filter keeps only strong matches", "lemon"), "csgbq 127: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 127: the filter keeps only strong matches", "a"), "round 127: the filter keeps only strong matches"),
    (("round 127: the filter keeps only strong matches", "zz"), "qntmc 127: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 127: the filter keeps only strong matches", "AgentU"), "ruyaw 127: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 127: the filter keeps only strong matches", "keyboard"),
        "bssor 127: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 127: the filter keeps only strong matches", "AA"), "round 127: the filter keeps only strong matches"),
    (("round 127: the model answers with a short reply", "key"), "bssxh 127: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 127: the model answers with a short reply", "lemon"), "csgbq 127: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 127: the model answers with a short reply", "a"), "round 127: the model answers with a short reply"),
    (("round 127: the model answers with a short reply", "zz"), "qntmc 127: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 127: the model answers with a short reply", "AgentU"), "ruyaw 127: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 127: the model answers with a short reply", "keyboard"),
        "bssor 127: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 127: the model answers with a short reply", "AA"), "round 127: the model answers with a short reply"),
    (
        ("round 127: the recorder stores the reasoning trace", "key"),
        "bssxh 127: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 127: the recorder stores the reasoning trace", "lemon"),
        "csgbq 127: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 127: the recorder stores the reasoning trace", "a"), "round 127: the recorder stores the reasoning trace"),
    (
        ("round 127: the recorder stores the reasoning trace", "zz"),
        "qntmc 127: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 127: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 127: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 127: the recorder stores the reasoning trace", "keyboard"),
        "bssor 127: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 127: the recorder stores the reasoning trace", "AA"),
        "round 127: the recorder stores the reasoning trace",
    ),
    (("round 127: the angel watches the processor run", "key"), "bssxh 127: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 127: the angel watches the processor run", "lemon"), "csgbq 127: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 127: the angel watches the processor run", "a"), "round 127: the angel watches the processor run"),
    (("round 127: the angel watches the processor run", "zz"), "qntmc 127: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 127: the angel watches the processor run", "AgentU"), "ruyaw 127: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 127: the angel watches the processor run", "keyboard"), "bssor 127: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 127: the angel watches the processor run", "AA"), "round 127: the angel watches the processor run"),
    (("round 127: angle of the vector decides the match", "key"), "bssxh 127: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 127: angle of the vector decides the match", "lemon"), "csgbq 127: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 127: angle of the vector decides the match", "a"), "round 127: angle of the vector decides the match"),
    (("round 127: angle of the vector decides the match", "zz"), "qntmc 127: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 127: angle of the vector decides the match", "AgentU"),
        "ruyaw 127: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 127: angle of the vector decides the match", "keyboard"),
        "bssor 127: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 127: angle of the vector decides the match", "AA"), "round 127: angle of the vector decides the match"),
    (
        ("round 127: the candle burns twice as long at night", "key"),
        "bssxh 127: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 127: the candle burns twice as long at night", "lemon"),
        "csgbq 127: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 127: the candle burns twice as long at night", "a"), "round 127: the candle burns twice as long at night"),
    (
        ("round 127: the candle burns twice as long at night", "zz"),
        "qntmc 127: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 127: the candle burns twice as long at night", "AgentU"),
        "ruyaw 127: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 127: the candle burns twice as long at night", "keyboard"),
        "bssor 127: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 127: the candle burns twice as long at night", "AA"),
        "round 127: the candle burns twice as long at night",
    ),
    (("round 127: a mirror of the universe in one line", "key"), "bssxh 127: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 127: a mirror of the universe in one line", "lemon"), "csgbq 127: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 127: a mirror of the universe in one line", "a"), "round 127: a mirror of the universe in one line"),
    (("round 127: a mirror of the universe in one line", "zz"), "qntmc 127: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 127: a mirror of the universe in one line", "AgentU"), "ruyaw 127: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 127: a mirror of the universe in one line", "keyboard"),
        "bssor 127: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 127: a mirror of the universe in one line", "AA"), "round 127: a mirror of the universe in one line"),
    (("round 127: the queue drains before the storm", "key"), "bssxh 127: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 127: the queue drains before the storm", "lemon"), "csgbq 127: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 127: the queue drains before the storm", "a"), "round 127: the queue drains before the storm"),
    (("round 127: the queue drains before the storm", "zz"), "qntmc 127: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 127: the queue drains before the storm", "AgentU"), "ruyaw 127: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 127: the queue drains before the storm", "keyboard"), "bssor 127: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 127: the queue drains before the storm", "AA"), "round 127: the queue drains before the storm"),
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
