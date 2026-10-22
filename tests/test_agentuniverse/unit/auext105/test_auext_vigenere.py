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
    (("kitten105", "key"), "umrdil105"),
    (("kitten105", "lemon"), "vmfhry105"),
    (("kitten105", "a"), "kitten105"),
    (("kitten105", "zz"), "jhssdm105"),
    (("kitten105", "AgentU"), "koxgxh105"),
    (("kitten105", "keyboard"), "umrusn105"),
    (("kitten105", "AA"), "kitten105"),
    (("sitting105", "key"), "cmrdmlq105"),
    (("sitting105", "lemon"), "dmfhvyk105"),
    (("sitting105", "a"), "sitting105"),
    (("sitting105", "zz"), "rhsshmf105"),
    (("sitting105", "AgentU"), "soxgbhg105"),
    (("sitting105", "keyboard"), "cmruwnx105"),
    (("sitting105", "AA"), "sitting105"),
    (("agent105", "key"), "kkcxx105"),
    (("agent105", "lemon"), "lkqbg105"),
    (("agent105", "a"), "agent105"),
    (("agent105", "zz"), "zfdms105"),
    (("agent105", "AgentU"), "amiam105"),
    (("agent105", "keyboard"), "kkcoh105"),
    (("agent105", "AA"), "agent105"),
    (("angle105", "key"), "krevi105"),
    (("angle105", "lemon"), "lrszr105"),
    (("angle105", "a"), "angle105"),
    (("angle105", "zz"), "zmfkd105"),
    (("angle105", "AgentU"), "atkyx105"),
    (("angle105", "keyboard"), "krems105"),
    (("angle105", "AA"), "angle105"),
    (("universe105", "key"), "ergfipci105"),
    (("universe105", "lemon"), "frujrcwq105"),
    (("universe105", "a"), "universe105"),
    (("universe105", "zz"), "tmhudqrd105"),
    (("universe105", "AgentU"), "utmixlsk105"),
    (("universe105", "keyboard"), "ergwsrjh105"),
    (("universe105", "AA"), "universe105"),
    (("memory105", "key"), "wikyvw105"),
    (("memory105", "lemon"), "xiycej105"),
    (("memory105", "a"), "memory105"),
    (("memory105", "zz"), "ldlnqx105"),
    (("memory105", "AgentU"), "mkqbks105"),
    (("memory105", "keyboard"), "wikpfy105"),
    (("memory105", "AA"), "memory105"),
    (("stream105", "key"), "cxpoek105"),
    (("stream105", "lemon"), "dxdsnx105"),
    (("stream105", "a"), "stream105"),
    (("stream105", "zz"), "rsqdzl105"),
    (("stream105", "AgentU"), "szvrtg105"),
    (("stream105", "keyboard"), "cxpfom105"),
    (("stream105", "AA"), "stream105"),
    (("context105", "key"), "msldivd105"),
    (("context105", "lemon"), "nszhrix105"),
    (("context105", "a"), "context105"),
    (("context105", "zz"), "bnmsdws105"),
    (("context105", "AgentU"), "curgxrt105"),
    (("context105", "keyboard"), "mslusxk105"),
    (("context105", "AA"), "context105"),
    (("knowledge105", "key"), "urmgpcnkc105"),
    (("knowledge105", "lemon"), "vrakyphss105"),
    (("knowledge105", "a"), "knowledge105"),
    (("knowledge105", "zz"), "jmnvkdcfd105"),
    (("knowledge105", "AgentU"), "ktsjeydmi105"),
    (("knowledge105", "keyboard"), "urmxzeujo105"),
    (("knowledge105", "AA"), "knowledge105"),
    (("vector105", "key"), "fiadsp105"),
    (("vector105", "lemon"), "giohbc105"),
    (("vector105", "a"), "vector105"),
    (("vector105", "zz"), "udbsnq105"),
    (("vector105", "AgentU"), "vkgghl105"),
    (("vector105", "keyboard"), "fiaucr105"),
    (("vector105", "AA"), "vector105"),
    (("processor105", "key"), "zvmmiqcsp105"),
    (("processor105", "lemon"), "avaqrdwaf105"),
    (("processor105", "a"), "processor105"),
    (("processor105", "zz"), "oqnbdrrnq105"),
    (("processor105", "AgentU"), "pxspxmsuv105"),
    (("processor105", "keyboard"), "zvmdssjrb105"),
    (("processor105", "AA"), "processor105"),
    (("reasoning105", "key"), "biycslsre105"),
    (("reasoning105", "lemon"), "cimgbymzu105"),
    (("reasoning105", "a"), "reasoning105"),
    (("reasoning105", "zz"), "qdzrnmhmf105"),
    (("reasoning105", "AgentU"), "rkefhhitk105"),
    (("reasoning105", "keyboard"), "biytcnzqq105"),
    (("reasoning105", "AA"), "reasoning105"),
    (("machine105", "key"), "wearmlo105"),
    (("machine105", "lemon"), "xeovvyi105"),
    (("machine105", "a"), "machine105"),
    (("machine105", "zz"), "lzbghmd105"),
    (("machine105", "AgentU"), "mggubhe105"),
    (("machine105", "keyboard"), "weaiwnv105"),
    (("machine105", "AA"), "machine105"),
    (("learning105", "key"), "viybrgxk105"),
    (("learning105", "lemon"), "wimfatrs105"),
    (("learning105", "a"), "learning105"),
    (("learning105", "zz"), "kdzqmhmf105"),
    (("learning105", "AgentU"), "lkeegcnm105"),
    (("learning105", "keyboard"), "viysbiej105"),
    (("learning105", "AA"), "learning105"),
    (("model105", "key"), "wsbop105"),
    (("model105", "lemon"), "xspsy105"),
    (("model105", "a"), "model105"),
    (("model105", "zz"), "lncdk105"),
    (("model105", "AgentU"), "muhre105"),
    (("model105", "keyboard"), "wsbfz105"),
    (("model105", "AA"), "model105"),
    (("token105", "key"), "dsior105"),
    (("token105", "lemon"), "eswsa105"),
    (("token105", "a"), "token105"),
    (("token105", "zz"), "snjdm105"),
    (("token105", "AgentU"), "tuorg105"),
    (("token105", "keyboard"), "dsifb105"),
    (("token105", "AA"), "token105"),
    (("prompt105", "key"), "zvmwtr105"),
    (("prompt105", "lemon"), "avaace105"),
    (("prompt105", "a"), "prompt105"),
    (("prompt105", "zz"), "oqnlos105"),
    (("prompt105", "AgentU"), "pxszin105"),
    (("prompt105", "keyboard"), "zvmndt105"),
    (("prompt105", "AA"), "prompt105"),
    (("session105", "key"), "ciqcmmx105"),
    (("session105", "lemon"), "diegvzr105"),
    (("session105", "a"), "session105"),
    (("session105", "zz"), "rdrrhnm105"),
    (("session105", "AgentU"), "skwfbin105"),
    (("session105", "keyboard"), "ciqtwoe105"),
    (("session105", "AA"), "session105"),
    (("library105", "key"), "vmzbepi105"),
    (("library105", "lemon"), "wmnfncc105"),
    (("library105", "a"), "library105"),
    (("library105", "zz"), "khaqzqx105"),
    (("library105", "AgentU"), "lofetly105"),
    (("library105", "keyboard"), "vmzsorp105"),
    (("library105", "AA"), "library105"),
    (("service105", "key"), "cipfmao105"),
    (("service105", "lemon"), "didjvni105"),
    (("service105", "a"), "service105"),
    (("service105", "zz"), "rdquhbd105"),
    (("service105", "AgentU"), "skvibwe105"),
    (("service105", "keyboard"), "cipwwcv105"),
    (("service105", "AA"), "service105"),
    (("gateway105", "key"), "qeroayi105"),
    (("gateway105", "lemon"), "refsjlc105"),
    (("gateway105", "a"), "gateway105"),
    (("gateway105", "zz"), "fzsdvzx105"),
    (("gateway105", "AgentU"), "ggxrpuy105"),
    (("gateway105", "keyboard"), "qerfkap105"),
    (("gateway105", "AA"), "gateway105"),
    (("storage105", "key"), "cxmbeeo105"),
    (("storage105", "lemon"), "dxafnri105"),
    (("storage105", "a"), "storage105"),
    (("storage105", "zz"), "rsnqzfd105"),
    (("storage105", "AgentU"), "szsetae105"),
    (("storage105", "keyboard"), "cxmsogv105"),
    (("storage105", "AA"), "storage105"),
    (("network105", "key"), "xirgspu105"),
    (("network105", "lemon"), "yifkbco105"),
    (("network105", "a"), "network105"),
    (("network105", "zz"), "mdsvnqj105"),
    (("network105", "AgentU"), "nkxjhlk105"),
    (("network105", "keyboard"), "xirxcrb105"),
    (("network105", "AA"), "network105"),
    (("latency105", "key"), "verorai105"),
    (("latency105", "lemon"), "wefsanc105"),
    (("latency105", "a"), "latency105"),
    (("latency105", "zz"), "kzsdmbx105"),
    (("latency105", "AgentU"), "lgxrgwy105"),
    (("latency105", "keyboard"), "verfbcp105"),
    (("latency105", "AA"), "latency105"),
    (("buffer105", "key"), "lydpip105"),
    (("buffer105", "lemon"), "myrtrc105"),
    (("buffer105", "a"), "buffer105"),
    (("buffer105", "zz"), "ateedq105"),
    (("buffer105", "AgentU"), "bajsxl105"),
    (("buffer105", "keyboard"), "lydgsr105"),
    (("buffer105", "AA"), "buffer105"),
    (("queue105", "key"), "aycei105"),
    (("queue105", "lemon"), "byqir105"),
    (("queue105", "a"), "queue105"),
    (("queue105", "zz"), "ptdtd105"),
    (("queue105", "AgentU"), "qaihx105"),
    (("queue105", "keyboard"), "aycvs105"),
    (("queue105", "AA"), "queue105"),
    (("worker105", "key"), "gspuip105"),
    (("worker105", "lemon"), "hsdyrc105"),
    (("worker105", "a"), "worker105"),
    (("worker105", "zz"), "vnqjdq105"),
    (("worker105", "AgentU"), "wuvxxl105"),
    (("worker105", "keyboard"), "gsplsr105"),
    (("worker105", "AA"), "worker105"),
    (("kernel105", "key"), "uipxij105"),
    (("kernel105", "lemon"), "vidbrw105"),
    (("kernel105", "a"), "kernel105"),
    (("kernel105", "zz"), "jdqmdk105"),
    (("kernel105", "AgentU"), "kkvaxf105"),
    (("kernel105", "keyboard"), "uiposl105"),
    (("kernel105", "AA"), "kernel105"),
    (("signal105", "key"), "cmexej105"),
    (("signal105", "lemon"), "dmsbnw105"),
    (("signal105", "a"), "signal105"),
    (("signal105", "zz"), "rhfmzk105"),
    (("signal105", "AgentU"), "sokatf105"),
    (("signal105", "keyboard"), "cmeool105"),
    (("signal105", "AA"), "signal105"),
    (("packet105", "key"), "zeauir105"),
    (("packet105", "lemon"), "aeoyre105"),
    (("packet105", "a"), "packet105"),
    (("packet105", "zz"), "ozbjds105"),
    (("packet105", "AgentU"), "pggxxn105"),
    (("packet105", "keyboard"), "zealst105"),
    (("packet105", "AA"), "packet105"),
    (("router105", "key"), "bssdip105"),
    (("router105", "lemon"), "csghrc105"),
    (("router105", "a"), "router105"),
    (("router105", "zz"), "qntsdq105"),
    (("router105", "AgentU"), "ruygxl105"),
    (("router105", "keyboard"), "bssusr105"),
    (("router105", "AA"), "router105"),
    (("cluster105", "key"), "mpscxcb105"),
    (("cluster105", "lemon"), "npgggpv105"),
    (("cluster105", "a"), "cluster105"),
    (("cluster105", "zz"), "bktrsdq105"),
    (("cluster105", "AgentU"), "cryfmyr105"),
    (("cluster105", "keyboard"), "mpsthei105"),
    (("cluster105", "AA"), "cluster105"),
    (("mirror105", "key"), "wmpbsp105"),
    (("mirror105", "lemon"), "xmdfbc105"),
    (("mirror105", "a"), "mirror105"),
    (("mirror105", "zz"), "lhqqnq105"),
    (("mirror105", "AgentU"), "movehl105"),
    (("mirror105", "keyboard"), "wmpscr105"),
    (("mirror105", "AA"), "mirror105"),
    (("filter105", "key"), "pmjdip105"),
    (("filter105", "lemon"), "qmxhrc105"),
    (("filter105", "a"), "filter105"),
    (("filter105", "zz"), "ehksdq105"),
    (("filter105", "AgentU"), "fopgxl105"),
    (("filter105", "keyboard"), "pmjusr105"),
    (("filter105", "AA"), "filter105"),
    (("ranking105", "key"), "belumlq105"),
    (("ranking105", "lemon"), "cezyvyk105"),
    (("ranking105", "a"), "ranking105"),
    (("ranking105", "zz"), "qzmjhmf105"),
    (("ranking105", "AgentU"), "rgrxbhg105"),
    (("ranking105", "keyboard"), "bellwnx105"),
    (("ranking105", "AA"), "ranking105"),
    (("encoding105", "key"), "orayhgxk105"),
    (("encoding105", "lemon"), "procqtrs105"),
    (("encoding105", "a"), "encoding105"),
    (("encoding105", "zz"), "dmbnchmf105"),
    (("encoding105", "AgentU"), "etgbwcnm105"),
    (("encoding105", "keyboard"), "orapriej105"),
    (("encoding105", "AA"), "encoding105"),
    (("mapping105", "key"), "wenzmlq105"),
    (("mapping105", "lemon"), "xebdvyk105"),
    (("mapping105", "a"), "mapping105"),
    (("mapping105", "zz"), "lzoohmf105"),
    (("mapping105", "AgentU"), "mgtcbhg105"),
    (("mapping105", "keyboard"), "wenqwnx105"),
    (("mapping105", "AA"), "mapping105"),
    (("record105", "key"), "biayvb105"),
    (("record105", "lemon"), "cioceo105"),
    (("record105", "a"), "record105"),
    (("record105", "zz"), "qdbnqc105"),
    (("record105", "AgentU"), "rkgbkx105"),
    (("record105", "keyboard"), "biapfd105"),
    (("record105", "AA"), "record105"),
    (("candle105", "key"), "melnpc105"),
    (("candle105", "lemon"), "nezryp105"),
    (("candle105", "a"), "candle105"),
    (("candle105", "zz"), "bzmckd105"),
    (("candle105", "AgentU"), "cgrqey105"),
    (("candle105", "keyboard"), "meleze105"),
    (("candle105", "AA"), "candle105"),
    (("thread105", "key"), "dlpoeb105"),
    (("thread105", "lemon"), "eldsno105"),
    (("thread105", "a"), "thread105"),
    (("thread105", "zz"), "sgqdzc105"),
    (("thread105", "AgentU"), "tnvrtx105"),
    (("thread105", "keyboard"), "dlpfod105"),
    (("thread105", "AA"), "thread105"),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 105: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 105: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "a"),
        "round 105: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 105: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 105: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 105: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", "AA"),
        "round 105: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "key"),
        "bssxh 105: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 105: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "a"),
        "round 105: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 105: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 105: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 105: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", "AA"),
        "round 105: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 105: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 105: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "a"),
        "round 105: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 105: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 105: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 105: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", "AA"),
        "round 105: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 105: the processor reads the record then stops", "key"),
        "bssxh 105: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 105: the processor reads the record then stops", "lemon"),
        "csgbq 105: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 105: the processor reads the record then stops", "a"),
        "round 105: the processor reads the record then stops",
    ),
    (
        ("round 105: the processor reads the record then stops", "zz"),
        "qntmc 105: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 105: the processor reads the record then stops", "AgentU"),
        "ruyaw 105: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 105: the processor reads the record then stops", "keyboard"),
        "bssor 105: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 105: the processor reads the record then stops", "AA"),
        "round 105: the processor reads the record then stops",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "key"),
        "bssxh 105: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "lemon"),
        "csgbq 105: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "a"),
        "round 105: a worker pulls the next task from the queue",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "zz"),
        "qntmc 105: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 105: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "keyboard"),
        "bssor 105: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 105: a worker pulls the next task from the queue", "AA"),
        "round 105: a worker pulls the next task from the queue",
    ),
    (
        ("round 105: signals travel through the network layer", "key"),
        "bssxh 105: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 105: signals travel through the network layer", "lemon"),
        "csgbq 105: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 105: signals travel through the network layer", "a"),
        "round 105: signals travel through the network layer",
    ),
    (
        ("round 105: signals travel through the network layer", "zz"),
        "qntmc 105: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 105: signals travel through the network layer", "AgentU"),
        "ruyaw 105: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 105: signals travel through the network layer", "keyboard"),
        "bssor 105: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 105: signals travel through the network layer", "AA"),
        "round 105: signals travel through the network layer",
    ),
    (
        ("round 105: the gateway routes each request by policy", "key"),
        "bssxh 105: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 105: the gateway routes each request by policy", "lemon"),
        "csgbq 105: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 105: the gateway routes each request by policy", "a"),
        "round 105: the gateway routes each request by policy",
    ),
    (
        ("round 105: the gateway routes each request by policy", "zz"),
        "qntmc 105: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 105: the gateway routes each request by policy", "AgentU"),
        "ruyaw 105: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 105: the gateway routes each request by policy", "keyboard"),
        "bssor 105: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 105: the gateway routes each request by policy", "AA"),
        "round 105: the gateway routes each request by policy",
    ),
    (("round 105: memory grows until the buffer is full", "key"), "bssxh 105: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 105: memory grows until the buffer is full", "lemon"), "csgbq 105: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 105: memory grows until the buffer is full", "a"), "round 105: memory grows until the buffer is full"),
    (("round 105: memory grows until the buffer is full", "zz"), "qntmc 105: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 105: memory grows until the buffer is full", "AgentU"),
        "ruyaw 105: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 105: memory grows until the buffer is full", "keyboard"),
        "bssor 105: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 105: memory grows until the buffer is full", "AA"), "round 105: memory grows until the buffer is full"),
    (("round 105: the cluster mirrors every packet twice", "key"), "bssxh 105: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 105: the cluster mirrors every packet twice", "lemon"),
        "csgbq 105: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 105: the cluster mirrors every packet twice", "a"), "round 105: the cluster mirrors every packet twice"),
    (("round 105: the cluster mirrors every packet twice", "zz"), "qntmc 105: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 105: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 105: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 105: the cluster mirrors every packet twice", "keyboard"),
        "bssor 105: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 105: the cluster mirrors every packet twice", "AA"), "round 105: the cluster mirrors every packet twice"),
    (
        ("round 105: ranking uses tokens learned from the corpus", "key"),
        "bssxh 105: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 105: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", "a"),
        "round 105: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 105: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 105: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 105: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", "AA"),
        "round 105: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 105: a long session ends when the candle dies", "key"),
        "bssxh 105: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 105: a long session ends when the candle dies", "lemon"),
        "csgbq 105: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 105: a long session ends when the candle dies", "a"),
        "round 105: a long session ends when the candle dies",
    ),
    (
        ("round 105: a long session ends when the candle dies", "zz"),
        "qntmc 105: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 105: a long session ends when the candle dies", "AgentU"),
        "ruyaw 105: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 105: a long session ends when the candle dies", "keyboard"),
        "bssor 105: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 105: a long session ends when the candle dies", "AA"),
        "round 105: a long session ends when the candle dies",
    ),
    (("round 105: encode the prompt then map the result", "key"), "bssxh 105: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 105: encode the prompt then map the result", "lemon"), "csgbq 105: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 105: encode the prompt then map the result", "a"), "round 105: encode the prompt then map the result"),
    (("round 105: encode the prompt then map the result", "zz"), "qntmc 105: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 105: encode the prompt then map the result", "AgentU"),
        "ruyaw 105: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 105: encode the prompt then map the result", "keyboard"),
        "bssor 105: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 105: encode the prompt then map the result", "AA"), "round 105: encode the prompt then map the result"),
    (("round 105: the kernel wakes the worker at dawn", "key"), "bssxh 105: rri iovlop ukocc xfo ambocb er neux"),
    (("round 105: the kernel wakes the worker at dawn", "lemon"), "csgbq 105: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 105: the kernel wakes the worker at dawn", "a"), "round 105: the kernel wakes the worker at dawn"),
    (("round 105: the kernel wakes the worker at dawn", "zz"), "qntmc 105: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 105: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 105: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 105: the kernel wakes the worker at dawn", "keyboard"), "bssor 105: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 105: the kernel wakes the worker at dawn", "AA"), "round 105: the kernel wakes the worker at dawn"),
    (("round 105: service latency drops after the patch", "key"), "bssxh 105: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 105: service latency drops after the patch", "lemon"), "csgbq 105: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 105: service latency drops after the patch", "a"), "round 105: service latency drops after the patch"),
    (("round 105: service latency drops after the patch", "zz"), "qntmc 105: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 105: service latency drops after the patch", "AgentU"),
        "ruyaw 105: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 105: service latency drops after the patch", "keyboard"),
        "bssor 105: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 105: service latency drops after the patch", "AA"), "round 105: service latency drops after the patch"),
    (
        ("round 105: the library caches every vector it sees", "key"),
        "bssxh 105: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 105: the library caches every vector it sees", "lemon"),
        "csgbq 105: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 105: the library caches every vector it sees", "a"), "round 105: the library caches every vector it sees"),
    (
        ("round 105: the library caches every vector it sees", "zz"),
        "qntmc 105: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 105: the library caches every vector it sees", "AgentU"),
        "ruyaw 105: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 105: the library caches every vector it sees", "keyboard"),
        "bssor 105: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 105: the library caches every vector it sees", "AA"),
        "round 105: the library caches every vector it sees",
    ),
    (("round 105: agents argue then the debate resolves", "key"), "bssxh 105: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 105: agents argue then the debate resolves", "lemon"), "csgbq 105: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 105: agents argue then the debate resolves", "a"), "round 105: agents argue then the debate resolves"),
    (("round 105: agents argue then the debate resolves", "zz"), "qntmc 105: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 105: agents argue then the debate resolves", "AgentU"),
        "ruyaw 105: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 105: agents argue then the debate resolves", "keyboard"),
        "bssor 105: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 105: agents argue then the debate resolves", "AA"), "round 105: agents argue then the debate resolves"),
    (("round 105: the filter keeps only strong matches", "key"), "bssxh 105: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 105: the filter keeps only strong matches", "lemon"), "csgbq 105: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 105: the filter keeps only strong matches", "a"), "round 105: the filter keeps only strong matches"),
    (("round 105: the filter keeps only strong matches", "zz"), "qntmc 105: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 105: the filter keeps only strong matches", "AgentU"), "ruyaw 105: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 105: the filter keeps only strong matches", "keyboard"),
        "bssor 105: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 105: the filter keeps only strong matches", "AA"), "round 105: the filter keeps only strong matches"),
    (("round 105: the model answers with a short reply", "key"), "bssxh 105: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 105: the model answers with a short reply", "lemon"), "csgbq 105: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 105: the model answers with a short reply", "a"), "round 105: the model answers with a short reply"),
    (("round 105: the model answers with a short reply", "zz"), "qntmc 105: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 105: the model answers with a short reply", "AgentU"), "ruyaw 105: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 105: the model answers with a short reply", "keyboard"),
        "bssor 105: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 105: the model answers with a short reply", "AA"), "round 105: the model answers with a short reply"),
    (
        ("round 105: the recorder stores the reasoning trace", "key"),
        "bssxh 105: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 105: the recorder stores the reasoning trace", "lemon"),
        "csgbq 105: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 105: the recorder stores the reasoning trace", "a"), "round 105: the recorder stores the reasoning trace"),
    (
        ("round 105: the recorder stores the reasoning trace", "zz"),
        "qntmc 105: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 105: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 105: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 105: the recorder stores the reasoning trace", "keyboard"),
        "bssor 105: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 105: the recorder stores the reasoning trace", "AA"),
        "round 105: the recorder stores the reasoning trace",
    ),
    (("round 105: the angel watches the processor run", "key"), "bssxh 105: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 105: the angel watches the processor run", "lemon"), "csgbq 105: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 105: the angel watches the processor run", "a"), "round 105: the angel watches the processor run"),
    (("round 105: the angel watches the processor run", "zz"), "qntmc 105: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 105: the angel watches the processor run", "AgentU"), "ruyaw 105: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 105: the angel watches the processor run", "keyboard"), "bssor 105: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 105: the angel watches the processor run", "AA"), "round 105: the angel watches the processor run"),
    (("round 105: angle of the vector decides the match", "key"), "bssxh 105: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 105: angle of the vector decides the match", "lemon"), "csgbq 105: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 105: angle of the vector decides the match", "a"), "round 105: angle of the vector decides the match"),
    (("round 105: angle of the vector decides the match", "zz"), "qntmc 105: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 105: angle of the vector decides the match", "AgentU"),
        "ruyaw 105: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 105: angle of the vector decides the match", "keyboard"),
        "bssor 105: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 105: angle of the vector decides the match", "AA"), "round 105: angle of the vector decides the match"),
    (
        ("round 105: the candle burns twice as long at night", "key"),
        "bssxh 105: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 105: the candle burns twice as long at night", "lemon"),
        "csgbq 105: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 105: the candle burns twice as long at night", "a"), "round 105: the candle burns twice as long at night"),
    (
        ("round 105: the candle burns twice as long at night", "zz"),
        "qntmc 105: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 105: the candle burns twice as long at night", "AgentU"),
        "ruyaw 105: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 105: the candle burns twice as long at night", "keyboard"),
        "bssor 105: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 105: the candle burns twice as long at night", "AA"),
        "round 105: the candle burns twice as long at night",
    ),
    (("round 105: a mirror of the universe in one line", "key"), "bssxh 105: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 105: a mirror of the universe in one line", "lemon"), "csgbq 105: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 105: a mirror of the universe in one line", "a"), "round 105: a mirror of the universe in one line"),
    (("round 105: a mirror of the universe in one line", "zz"), "qntmc 105: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 105: a mirror of the universe in one line", "AgentU"), "ruyaw 105: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 105: a mirror of the universe in one line", "keyboard"),
        "bssor 105: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 105: a mirror of the universe in one line", "AA"), "round 105: a mirror of the universe in one line"),
    (("round 105: the queue drains before the storm", "key"), "bssxh 105: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 105: the queue drains before the storm", "lemon"), "csgbq 105: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 105: the queue drains before the storm", "a"), "round 105: the queue drains before the storm"),
    (("round 105: the queue drains before the storm", "zz"), "qntmc 105: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 105: the queue drains before the storm", "AgentU"), "ruyaw 105: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 105: the queue drains before the storm", "keyboard"), "bssor 105: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 105: the queue drains before the storm", "AA"), "round 105: the queue drains before the storm"),
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
