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
    (("kitten117", "key"), "umrdil117"),
    (("kitten117", "lemon"), "vmfhry117"),
    (("kitten117", "a"), "kitten117"),
    (("kitten117", "zz"), "jhssdm117"),
    (("kitten117", "AgentU"), "koxgxh117"),
    (("kitten117", "keyboard"), "umrusn117"),
    (("kitten117", "AA"), "kitten117"),
    (("sitting117", "key"), "cmrdmlq117"),
    (("sitting117", "lemon"), "dmfhvyk117"),
    (("sitting117", "a"), "sitting117"),
    (("sitting117", "zz"), "rhsshmf117"),
    (("sitting117", "AgentU"), "soxgbhg117"),
    (("sitting117", "keyboard"), "cmruwnx117"),
    (("sitting117", "AA"), "sitting117"),
    (("agent117", "key"), "kkcxx117"),
    (("agent117", "lemon"), "lkqbg117"),
    (("agent117", "a"), "agent117"),
    (("agent117", "zz"), "zfdms117"),
    (("agent117", "AgentU"), "amiam117"),
    (("agent117", "keyboard"), "kkcoh117"),
    (("agent117", "AA"), "agent117"),
    (("angle117", "key"), "krevi117"),
    (("angle117", "lemon"), "lrszr117"),
    (("angle117", "a"), "angle117"),
    (("angle117", "zz"), "zmfkd117"),
    (("angle117", "AgentU"), "atkyx117"),
    (("angle117", "keyboard"), "krems117"),
    (("angle117", "AA"), "angle117"),
    (("universe117", "key"), "ergfipci117"),
    (("universe117", "lemon"), "frujrcwq117"),
    (("universe117", "a"), "universe117"),
    (("universe117", "zz"), "tmhudqrd117"),
    (("universe117", "AgentU"), "utmixlsk117"),
    (("universe117", "keyboard"), "ergwsrjh117"),
    (("universe117", "AA"), "universe117"),
    (("memory117", "key"), "wikyvw117"),
    (("memory117", "lemon"), "xiycej117"),
    (("memory117", "a"), "memory117"),
    (("memory117", "zz"), "ldlnqx117"),
    (("memory117", "AgentU"), "mkqbks117"),
    (("memory117", "keyboard"), "wikpfy117"),
    (("memory117", "AA"), "memory117"),
    (("stream117", "key"), "cxpoek117"),
    (("stream117", "lemon"), "dxdsnx117"),
    (("stream117", "a"), "stream117"),
    (("stream117", "zz"), "rsqdzl117"),
    (("stream117", "AgentU"), "szvrtg117"),
    (("stream117", "keyboard"), "cxpfom117"),
    (("stream117", "AA"), "stream117"),
    (("context117", "key"), "msldivd117"),
    (("context117", "lemon"), "nszhrix117"),
    (("context117", "a"), "context117"),
    (("context117", "zz"), "bnmsdws117"),
    (("context117", "AgentU"), "curgxrt117"),
    (("context117", "keyboard"), "mslusxk117"),
    (("context117", "AA"), "context117"),
    (("knowledge117", "key"), "urmgpcnkc117"),
    (("knowledge117", "lemon"), "vrakyphss117"),
    (("knowledge117", "a"), "knowledge117"),
    (("knowledge117", "zz"), "jmnvkdcfd117"),
    (("knowledge117", "AgentU"), "ktsjeydmi117"),
    (("knowledge117", "keyboard"), "urmxzeujo117"),
    (("knowledge117", "AA"), "knowledge117"),
    (("vector117", "key"), "fiadsp117"),
    (("vector117", "lemon"), "giohbc117"),
    (("vector117", "a"), "vector117"),
    (("vector117", "zz"), "udbsnq117"),
    (("vector117", "AgentU"), "vkgghl117"),
    (("vector117", "keyboard"), "fiaucr117"),
    (("vector117", "AA"), "vector117"),
    (("processor117", "key"), "zvmmiqcsp117"),
    (("processor117", "lemon"), "avaqrdwaf117"),
    (("processor117", "a"), "processor117"),
    (("processor117", "zz"), "oqnbdrrnq117"),
    (("processor117", "AgentU"), "pxspxmsuv117"),
    (("processor117", "keyboard"), "zvmdssjrb117"),
    (("processor117", "AA"), "processor117"),
    (("reasoning117", "key"), "biycslsre117"),
    (("reasoning117", "lemon"), "cimgbymzu117"),
    (("reasoning117", "a"), "reasoning117"),
    (("reasoning117", "zz"), "qdzrnmhmf117"),
    (("reasoning117", "AgentU"), "rkefhhitk117"),
    (("reasoning117", "keyboard"), "biytcnzqq117"),
    (("reasoning117", "AA"), "reasoning117"),
    (("machine117", "key"), "wearmlo117"),
    (("machine117", "lemon"), "xeovvyi117"),
    (("machine117", "a"), "machine117"),
    (("machine117", "zz"), "lzbghmd117"),
    (("machine117", "AgentU"), "mggubhe117"),
    (("machine117", "keyboard"), "weaiwnv117"),
    (("machine117", "AA"), "machine117"),
    (("learning117", "key"), "viybrgxk117"),
    (("learning117", "lemon"), "wimfatrs117"),
    (("learning117", "a"), "learning117"),
    (("learning117", "zz"), "kdzqmhmf117"),
    (("learning117", "AgentU"), "lkeegcnm117"),
    (("learning117", "keyboard"), "viysbiej117"),
    (("learning117", "AA"), "learning117"),
    (("model117", "key"), "wsbop117"),
    (("model117", "lemon"), "xspsy117"),
    (("model117", "a"), "model117"),
    (("model117", "zz"), "lncdk117"),
    (("model117", "AgentU"), "muhre117"),
    (("model117", "keyboard"), "wsbfz117"),
    (("model117", "AA"), "model117"),
    (("token117", "key"), "dsior117"),
    (("token117", "lemon"), "eswsa117"),
    (("token117", "a"), "token117"),
    (("token117", "zz"), "snjdm117"),
    (("token117", "AgentU"), "tuorg117"),
    (("token117", "keyboard"), "dsifb117"),
    (("token117", "AA"), "token117"),
    (("prompt117", "key"), "zvmwtr117"),
    (("prompt117", "lemon"), "avaace117"),
    (("prompt117", "a"), "prompt117"),
    (("prompt117", "zz"), "oqnlos117"),
    (("prompt117", "AgentU"), "pxszin117"),
    (("prompt117", "keyboard"), "zvmndt117"),
    (("prompt117", "AA"), "prompt117"),
    (("session117", "key"), "ciqcmmx117"),
    (("session117", "lemon"), "diegvzr117"),
    (("session117", "a"), "session117"),
    (("session117", "zz"), "rdrrhnm117"),
    (("session117", "AgentU"), "skwfbin117"),
    (("session117", "keyboard"), "ciqtwoe117"),
    (("session117", "AA"), "session117"),
    (("library117", "key"), "vmzbepi117"),
    (("library117", "lemon"), "wmnfncc117"),
    (("library117", "a"), "library117"),
    (("library117", "zz"), "khaqzqx117"),
    (("library117", "AgentU"), "lofetly117"),
    (("library117", "keyboard"), "vmzsorp117"),
    (("library117", "AA"), "library117"),
    (("service117", "key"), "cipfmao117"),
    (("service117", "lemon"), "didjvni117"),
    (("service117", "a"), "service117"),
    (("service117", "zz"), "rdquhbd117"),
    (("service117", "AgentU"), "skvibwe117"),
    (("service117", "keyboard"), "cipwwcv117"),
    (("service117", "AA"), "service117"),
    (("gateway117", "key"), "qeroayi117"),
    (("gateway117", "lemon"), "refsjlc117"),
    (("gateway117", "a"), "gateway117"),
    (("gateway117", "zz"), "fzsdvzx117"),
    (("gateway117", "AgentU"), "ggxrpuy117"),
    (("gateway117", "keyboard"), "qerfkap117"),
    (("gateway117", "AA"), "gateway117"),
    (("storage117", "key"), "cxmbeeo117"),
    (("storage117", "lemon"), "dxafnri117"),
    (("storage117", "a"), "storage117"),
    (("storage117", "zz"), "rsnqzfd117"),
    (("storage117", "AgentU"), "szsetae117"),
    (("storage117", "keyboard"), "cxmsogv117"),
    (("storage117", "AA"), "storage117"),
    (("network117", "key"), "xirgspu117"),
    (("network117", "lemon"), "yifkbco117"),
    (("network117", "a"), "network117"),
    (("network117", "zz"), "mdsvnqj117"),
    (("network117", "AgentU"), "nkxjhlk117"),
    (("network117", "keyboard"), "xirxcrb117"),
    (("network117", "AA"), "network117"),
    (("latency117", "key"), "verorai117"),
    (("latency117", "lemon"), "wefsanc117"),
    (("latency117", "a"), "latency117"),
    (("latency117", "zz"), "kzsdmbx117"),
    (("latency117", "AgentU"), "lgxrgwy117"),
    (("latency117", "keyboard"), "verfbcp117"),
    (("latency117", "AA"), "latency117"),
    (("buffer117", "key"), "lydpip117"),
    (("buffer117", "lemon"), "myrtrc117"),
    (("buffer117", "a"), "buffer117"),
    (("buffer117", "zz"), "ateedq117"),
    (("buffer117", "AgentU"), "bajsxl117"),
    (("buffer117", "keyboard"), "lydgsr117"),
    (("buffer117", "AA"), "buffer117"),
    (("queue117", "key"), "aycei117"),
    (("queue117", "lemon"), "byqir117"),
    (("queue117", "a"), "queue117"),
    (("queue117", "zz"), "ptdtd117"),
    (("queue117", "AgentU"), "qaihx117"),
    (("queue117", "keyboard"), "aycvs117"),
    (("queue117", "AA"), "queue117"),
    (("worker117", "key"), "gspuip117"),
    (("worker117", "lemon"), "hsdyrc117"),
    (("worker117", "a"), "worker117"),
    (("worker117", "zz"), "vnqjdq117"),
    (("worker117", "AgentU"), "wuvxxl117"),
    (("worker117", "keyboard"), "gsplsr117"),
    (("worker117", "AA"), "worker117"),
    (("kernel117", "key"), "uipxij117"),
    (("kernel117", "lemon"), "vidbrw117"),
    (("kernel117", "a"), "kernel117"),
    (("kernel117", "zz"), "jdqmdk117"),
    (("kernel117", "AgentU"), "kkvaxf117"),
    (("kernel117", "keyboard"), "uiposl117"),
    (("kernel117", "AA"), "kernel117"),
    (("signal117", "key"), "cmexej117"),
    (("signal117", "lemon"), "dmsbnw117"),
    (("signal117", "a"), "signal117"),
    (("signal117", "zz"), "rhfmzk117"),
    (("signal117", "AgentU"), "sokatf117"),
    (("signal117", "keyboard"), "cmeool117"),
    (("signal117", "AA"), "signal117"),
    (("packet117", "key"), "zeauir117"),
    (("packet117", "lemon"), "aeoyre117"),
    (("packet117", "a"), "packet117"),
    (("packet117", "zz"), "ozbjds117"),
    (("packet117", "AgentU"), "pggxxn117"),
    (("packet117", "keyboard"), "zealst117"),
    (("packet117", "AA"), "packet117"),
    (("router117", "key"), "bssdip117"),
    (("router117", "lemon"), "csghrc117"),
    (("router117", "a"), "router117"),
    (("router117", "zz"), "qntsdq117"),
    (("router117", "AgentU"), "ruygxl117"),
    (("router117", "keyboard"), "bssusr117"),
    (("router117", "AA"), "router117"),
    (("cluster117", "key"), "mpscxcb117"),
    (("cluster117", "lemon"), "npgggpv117"),
    (("cluster117", "a"), "cluster117"),
    (("cluster117", "zz"), "bktrsdq117"),
    (("cluster117", "AgentU"), "cryfmyr117"),
    (("cluster117", "keyboard"), "mpsthei117"),
    (("cluster117", "AA"), "cluster117"),
    (("mirror117", "key"), "wmpbsp117"),
    (("mirror117", "lemon"), "xmdfbc117"),
    (("mirror117", "a"), "mirror117"),
    (("mirror117", "zz"), "lhqqnq117"),
    (("mirror117", "AgentU"), "movehl117"),
    (("mirror117", "keyboard"), "wmpscr117"),
    (("mirror117", "AA"), "mirror117"),
    (("filter117", "key"), "pmjdip117"),
    (("filter117", "lemon"), "qmxhrc117"),
    (("filter117", "a"), "filter117"),
    (("filter117", "zz"), "ehksdq117"),
    (("filter117", "AgentU"), "fopgxl117"),
    (("filter117", "keyboard"), "pmjusr117"),
    (("filter117", "AA"), "filter117"),
    (("ranking117", "key"), "belumlq117"),
    (("ranking117", "lemon"), "cezyvyk117"),
    (("ranking117", "a"), "ranking117"),
    (("ranking117", "zz"), "qzmjhmf117"),
    (("ranking117", "AgentU"), "rgrxbhg117"),
    (("ranking117", "keyboard"), "bellwnx117"),
    (("ranking117", "AA"), "ranking117"),
    (("encoding117", "key"), "orayhgxk117"),
    (("encoding117", "lemon"), "procqtrs117"),
    (("encoding117", "a"), "encoding117"),
    (("encoding117", "zz"), "dmbnchmf117"),
    (("encoding117", "AgentU"), "etgbwcnm117"),
    (("encoding117", "keyboard"), "orapriej117"),
    (("encoding117", "AA"), "encoding117"),
    (("mapping117", "key"), "wenzmlq117"),
    (("mapping117", "lemon"), "xebdvyk117"),
    (("mapping117", "a"), "mapping117"),
    (("mapping117", "zz"), "lzoohmf117"),
    (("mapping117", "AgentU"), "mgtcbhg117"),
    (("mapping117", "keyboard"), "wenqwnx117"),
    (("mapping117", "AA"), "mapping117"),
    (("record117", "key"), "biayvb117"),
    (("record117", "lemon"), "cioceo117"),
    (("record117", "a"), "record117"),
    (("record117", "zz"), "qdbnqc117"),
    (("record117", "AgentU"), "rkgbkx117"),
    (("record117", "keyboard"), "biapfd117"),
    (("record117", "AA"), "record117"),
    (("candle117", "key"), "melnpc117"),
    (("candle117", "lemon"), "nezryp117"),
    (("candle117", "a"), "candle117"),
    (("candle117", "zz"), "bzmckd117"),
    (("candle117", "AgentU"), "cgrqey117"),
    (("candle117", "keyboard"), "meleze117"),
    (("candle117", "AA"), "candle117"),
    (("thread117", "key"), "dlpoeb117"),
    (("thread117", "lemon"), "eldsno117"),
    (("thread117", "a"), "thread117"),
    (("thread117", "zz"), "sgqdzc117"),
    (("thread117", "AgentU"), "tnvrtx117"),
    (("thread117", "keyboard"), "dlpfod117"),
    (("thread117", "AA"), "thread117"),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 117: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 117: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "a"),
        "round 117: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 117: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 117: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 117: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", "AA"),
        "round 117: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "key"),
        "bssxh 117: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 117: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "a"),
        "round 117: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 117: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 117: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 117: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", "AA"),
        "round 117: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 117: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 117: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "a"),
        "round 117: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 117: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 117: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 117: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", "AA"),
        "round 117: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 117: the processor reads the record then stops", "key"),
        "bssxh 117: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 117: the processor reads the record then stops", "lemon"),
        "csgbq 117: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 117: the processor reads the record then stops", "a"),
        "round 117: the processor reads the record then stops",
    ),
    (
        ("round 117: the processor reads the record then stops", "zz"),
        "qntmc 117: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 117: the processor reads the record then stops", "AgentU"),
        "ruyaw 117: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 117: the processor reads the record then stops", "keyboard"),
        "bssor 117: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 117: the processor reads the record then stops", "AA"),
        "round 117: the processor reads the record then stops",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "key"),
        "bssxh 117: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "lemon"),
        "csgbq 117: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "a"),
        "round 117: a worker pulls the next task from the queue",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "zz"),
        "qntmc 117: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 117: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "keyboard"),
        "bssor 117: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 117: a worker pulls the next task from the queue", "AA"),
        "round 117: a worker pulls the next task from the queue",
    ),
    (
        ("round 117: signals travel through the network layer", "key"),
        "bssxh 117: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 117: signals travel through the network layer", "lemon"),
        "csgbq 117: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 117: signals travel through the network layer", "a"),
        "round 117: signals travel through the network layer",
    ),
    (
        ("round 117: signals travel through the network layer", "zz"),
        "qntmc 117: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 117: signals travel through the network layer", "AgentU"),
        "ruyaw 117: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 117: signals travel through the network layer", "keyboard"),
        "bssor 117: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 117: signals travel through the network layer", "AA"),
        "round 117: signals travel through the network layer",
    ),
    (
        ("round 117: the gateway routes each request by policy", "key"),
        "bssxh 117: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 117: the gateway routes each request by policy", "lemon"),
        "csgbq 117: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 117: the gateway routes each request by policy", "a"),
        "round 117: the gateway routes each request by policy",
    ),
    (
        ("round 117: the gateway routes each request by policy", "zz"),
        "qntmc 117: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 117: the gateway routes each request by policy", "AgentU"),
        "ruyaw 117: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 117: the gateway routes each request by policy", "keyboard"),
        "bssor 117: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 117: the gateway routes each request by policy", "AA"),
        "round 117: the gateway routes each request by policy",
    ),
    (("round 117: memory grows until the buffer is full", "key"), "bssxh 117: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 117: memory grows until the buffer is full", "lemon"), "csgbq 117: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 117: memory grows until the buffer is full", "a"), "round 117: memory grows until the buffer is full"),
    (("round 117: memory grows until the buffer is full", "zz"), "qntmc 117: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 117: memory grows until the buffer is full", "AgentU"),
        "ruyaw 117: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 117: memory grows until the buffer is full", "keyboard"),
        "bssor 117: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 117: memory grows until the buffer is full", "AA"), "round 117: memory grows until the buffer is full"),
    (("round 117: the cluster mirrors every packet twice", "key"), "bssxh 117: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 117: the cluster mirrors every packet twice", "lemon"),
        "csgbq 117: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 117: the cluster mirrors every packet twice", "a"), "round 117: the cluster mirrors every packet twice"),
    (("round 117: the cluster mirrors every packet twice", "zz"), "qntmc 117: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 117: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 117: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 117: the cluster mirrors every packet twice", "keyboard"),
        "bssor 117: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 117: the cluster mirrors every packet twice", "AA"), "round 117: the cluster mirrors every packet twice"),
    (
        ("round 117: ranking uses tokens learned from the corpus", "key"),
        "bssxh 117: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 117: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", "a"),
        "round 117: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 117: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 117: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 117: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", "AA"),
        "round 117: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 117: a long session ends when the candle dies", "key"),
        "bssxh 117: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 117: a long session ends when the candle dies", "lemon"),
        "csgbq 117: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 117: a long session ends when the candle dies", "a"),
        "round 117: a long session ends when the candle dies",
    ),
    (
        ("round 117: a long session ends when the candle dies", "zz"),
        "qntmc 117: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 117: a long session ends when the candle dies", "AgentU"),
        "ruyaw 117: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 117: a long session ends when the candle dies", "keyboard"),
        "bssor 117: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 117: a long session ends when the candle dies", "AA"),
        "round 117: a long session ends when the candle dies",
    ),
    (("round 117: encode the prompt then map the result", "key"), "bssxh 117: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 117: encode the prompt then map the result", "lemon"), "csgbq 117: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 117: encode the prompt then map the result", "a"), "round 117: encode the prompt then map the result"),
    (("round 117: encode the prompt then map the result", "zz"), "qntmc 117: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 117: encode the prompt then map the result", "AgentU"),
        "ruyaw 117: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 117: encode the prompt then map the result", "keyboard"),
        "bssor 117: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 117: encode the prompt then map the result", "AA"), "round 117: encode the prompt then map the result"),
    (("round 117: the kernel wakes the worker at dawn", "key"), "bssxh 117: rri iovlop ukocc xfo ambocb er neux"),
    (("round 117: the kernel wakes the worker at dawn", "lemon"), "csgbq 117: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 117: the kernel wakes the worker at dawn", "a"), "round 117: the kernel wakes the worker at dawn"),
    (("round 117: the kernel wakes the worker at dawn", "zz"), "qntmc 117: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 117: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 117: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 117: the kernel wakes the worker at dawn", "keyboard"), "bssor 117: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 117: the kernel wakes the worker at dawn", "AA"), "round 117: the kernel wakes the worker at dawn"),
    (("round 117: service latency drops after the patch", "key"), "bssxh 117: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 117: service latency drops after the patch", "lemon"), "csgbq 117: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 117: service latency drops after the patch", "a"), "round 117: service latency drops after the patch"),
    (("round 117: service latency drops after the patch", "zz"), "qntmc 117: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 117: service latency drops after the patch", "AgentU"),
        "ruyaw 117: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 117: service latency drops after the patch", "keyboard"),
        "bssor 117: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 117: service latency drops after the patch", "AA"), "round 117: service latency drops after the patch"),
    (
        ("round 117: the library caches every vector it sees", "key"),
        "bssxh 117: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 117: the library caches every vector it sees", "lemon"),
        "csgbq 117: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 117: the library caches every vector it sees", "a"), "round 117: the library caches every vector it sees"),
    (
        ("round 117: the library caches every vector it sees", "zz"),
        "qntmc 117: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 117: the library caches every vector it sees", "AgentU"),
        "ruyaw 117: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 117: the library caches every vector it sees", "keyboard"),
        "bssor 117: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 117: the library caches every vector it sees", "AA"),
        "round 117: the library caches every vector it sees",
    ),
    (("round 117: agents argue then the debate resolves", "key"), "bssxh 117: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 117: agents argue then the debate resolves", "lemon"), "csgbq 117: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 117: agents argue then the debate resolves", "a"), "round 117: agents argue then the debate resolves"),
    (("round 117: agents argue then the debate resolves", "zz"), "qntmc 117: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 117: agents argue then the debate resolves", "AgentU"),
        "ruyaw 117: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 117: agents argue then the debate resolves", "keyboard"),
        "bssor 117: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 117: agents argue then the debate resolves", "AA"), "round 117: agents argue then the debate resolves"),
    (("round 117: the filter keeps only strong matches", "key"), "bssxh 117: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 117: the filter keeps only strong matches", "lemon"), "csgbq 117: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 117: the filter keeps only strong matches", "a"), "round 117: the filter keeps only strong matches"),
    (("round 117: the filter keeps only strong matches", "zz"), "qntmc 117: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 117: the filter keeps only strong matches", "AgentU"), "ruyaw 117: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 117: the filter keeps only strong matches", "keyboard"),
        "bssor 117: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 117: the filter keeps only strong matches", "AA"), "round 117: the filter keeps only strong matches"),
    (("round 117: the model answers with a short reply", "key"), "bssxh 117: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 117: the model answers with a short reply", "lemon"), "csgbq 117: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 117: the model answers with a short reply", "a"), "round 117: the model answers with a short reply"),
    (("round 117: the model answers with a short reply", "zz"), "qntmc 117: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 117: the model answers with a short reply", "AgentU"), "ruyaw 117: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 117: the model answers with a short reply", "keyboard"),
        "bssor 117: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 117: the model answers with a short reply", "AA"), "round 117: the model answers with a short reply"),
    (
        ("round 117: the recorder stores the reasoning trace", "key"),
        "bssxh 117: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 117: the recorder stores the reasoning trace", "lemon"),
        "csgbq 117: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 117: the recorder stores the reasoning trace", "a"), "round 117: the recorder stores the reasoning trace"),
    (
        ("round 117: the recorder stores the reasoning trace", "zz"),
        "qntmc 117: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 117: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 117: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 117: the recorder stores the reasoning trace", "keyboard"),
        "bssor 117: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 117: the recorder stores the reasoning trace", "AA"),
        "round 117: the recorder stores the reasoning trace",
    ),
    (("round 117: the angel watches the processor run", "key"), "bssxh 117: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 117: the angel watches the processor run", "lemon"), "csgbq 117: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 117: the angel watches the processor run", "a"), "round 117: the angel watches the processor run"),
    (("round 117: the angel watches the processor run", "zz"), "qntmc 117: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 117: the angel watches the processor run", "AgentU"), "ruyaw 117: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 117: the angel watches the processor run", "keyboard"), "bssor 117: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 117: the angel watches the processor run", "AA"), "round 117: the angel watches the processor run"),
    (("round 117: angle of the vector decides the match", "key"), "bssxh 117: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 117: angle of the vector decides the match", "lemon"), "csgbq 117: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 117: angle of the vector decides the match", "a"), "round 117: angle of the vector decides the match"),
    (("round 117: angle of the vector decides the match", "zz"), "qntmc 117: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 117: angle of the vector decides the match", "AgentU"),
        "ruyaw 117: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 117: angle of the vector decides the match", "keyboard"),
        "bssor 117: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 117: angle of the vector decides the match", "AA"), "round 117: angle of the vector decides the match"),
    (
        ("round 117: the candle burns twice as long at night", "key"),
        "bssxh 117: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 117: the candle burns twice as long at night", "lemon"),
        "csgbq 117: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 117: the candle burns twice as long at night", "a"), "round 117: the candle burns twice as long at night"),
    (
        ("round 117: the candle burns twice as long at night", "zz"),
        "qntmc 117: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 117: the candle burns twice as long at night", "AgentU"),
        "ruyaw 117: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 117: the candle burns twice as long at night", "keyboard"),
        "bssor 117: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 117: the candle burns twice as long at night", "AA"),
        "round 117: the candle burns twice as long at night",
    ),
    (("round 117: a mirror of the universe in one line", "key"), "bssxh 117: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 117: a mirror of the universe in one line", "lemon"), "csgbq 117: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 117: a mirror of the universe in one line", "a"), "round 117: a mirror of the universe in one line"),
    (("round 117: a mirror of the universe in one line", "zz"), "qntmc 117: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 117: a mirror of the universe in one line", "AgentU"), "ruyaw 117: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 117: a mirror of the universe in one line", "keyboard"),
        "bssor 117: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 117: a mirror of the universe in one line", "AA"), "round 117: a mirror of the universe in one line"),
    (("round 117: the queue drains before the storm", "key"), "bssxh 117: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 117: the queue drains before the storm", "lemon"), "csgbq 117: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 117: the queue drains before the storm", "a"), "round 117: the queue drains before the storm"),
    (("round 117: the queue drains before the storm", "zz"), "qntmc 117: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 117: the queue drains before the storm", "AgentU"), "ruyaw 117: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 117: the queue drains before the storm", "keyboard"), "bssor 117: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 117: the queue drains before the storm", "AA"), "round 117: the queue drains before the storm"),
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
