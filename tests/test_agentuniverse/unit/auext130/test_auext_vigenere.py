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
    (("kitten130", "key"), "umrdil130"),
    (("kitten130", "lemon"), "vmfhry130"),
    (("kitten130", "a"), "kitten130"),
    (("kitten130", "zz"), "jhssdm130"),
    (("kitten130", "AgentU"), "koxgxh130"),
    (("kitten130", "keyboard"), "umrusn130"),
    (("kitten130", "AA"), "kitten130"),
    (("sitting130", "key"), "cmrdmlq130"),
    (("sitting130", "lemon"), "dmfhvyk130"),
    (("sitting130", "a"), "sitting130"),
    (("sitting130", "zz"), "rhsshmf130"),
    (("sitting130", "AgentU"), "soxgbhg130"),
    (("sitting130", "keyboard"), "cmruwnx130"),
    (("sitting130", "AA"), "sitting130"),
    (("agent130", "key"), "kkcxx130"),
    (("agent130", "lemon"), "lkqbg130"),
    (("agent130", "a"), "agent130"),
    (("agent130", "zz"), "zfdms130"),
    (("agent130", "AgentU"), "amiam130"),
    (("agent130", "keyboard"), "kkcoh130"),
    (("agent130", "AA"), "agent130"),
    (("angle130", "key"), "krevi130"),
    (("angle130", "lemon"), "lrszr130"),
    (("angle130", "a"), "angle130"),
    (("angle130", "zz"), "zmfkd130"),
    (("angle130", "AgentU"), "atkyx130"),
    (("angle130", "keyboard"), "krems130"),
    (("angle130", "AA"), "angle130"),
    (("universe130", "key"), "ergfipci130"),
    (("universe130", "lemon"), "frujrcwq130"),
    (("universe130", "a"), "universe130"),
    (("universe130", "zz"), "tmhudqrd130"),
    (("universe130", "AgentU"), "utmixlsk130"),
    (("universe130", "keyboard"), "ergwsrjh130"),
    (("universe130", "AA"), "universe130"),
    (("memory130", "key"), "wikyvw130"),
    (("memory130", "lemon"), "xiycej130"),
    (("memory130", "a"), "memory130"),
    (("memory130", "zz"), "ldlnqx130"),
    (("memory130", "AgentU"), "mkqbks130"),
    (("memory130", "keyboard"), "wikpfy130"),
    (("memory130", "AA"), "memory130"),
    (("stream130", "key"), "cxpoek130"),
    (("stream130", "lemon"), "dxdsnx130"),
    (("stream130", "a"), "stream130"),
    (("stream130", "zz"), "rsqdzl130"),
    (("stream130", "AgentU"), "szvrtg130"),
    (("stream130", "keyboard"), "cxpfom130"),
    (("stream130", "AA"), "stream130"),
    (("context130", "key"), "msldivd130"),
    (("context130", "lemon"), "nszhrix130"),
    (("context130", "a"), "context130"),
    (("context130", "zz"), "bnmsdws130"),
    (("context130", "AgentU"), "curgxrt130"),
    (("context130", "keyboard"), "mslusxk130"),
    (("context130", "AA"), "context130"),
    (("knowledge130", "key"), "urmgpcnkc130"),
    (("knowledge130", "lemon"), "vrakyphss130"),
    (("knowledge130", "a"), "knowledge130"),
    (("knowledge130", "zz"), "jmnvkdcfd130"),
    (("knowledge130", "AgentU"), "ktsjeydmi130"),
    (("knowledge130", "keyboard"), "urmxzeujo130"),
    (("knowledge130", "AA"), "knowledge130"),
    (("vector130", "key"), "fiadsp130"),
    (("vector130", "lemon"), "giohbc130"),
    (("vector130", "a"), "vector130"),
    (("vector130", "zz"), "udbsnq130"),
    (("vector130", "AgentU"), "vkgghl130"),
    (("vector130", "keyboard"), "fiaucr130"),
    (("vector130", "AA"), "vector130"),
    (("processor130", "key"), "zvmmiqcsp130"),
    (("processor130", "lemon"), "avaqrdwaf130"),
    (("processor130", "a"), "processor130"),
    (("processor130", "zz"), "oqnbdrrnq130"),
    (("processor130", "AgentU"), "pxspxmsuv130"),
    (("processor130", "keyboard"), "zvmdssjrb130"),
    (("processor130", "AA"), "processor130"),
    (("reasoning130", "key"), "biycslsre130"),
    (("reasoning130", "lemon"), "cimgbymzu130"),
    (("reasoning130", "a"), "reasoning130"),
    (("reasoning130", "zz"), "qdzrnmhmf130"),
    (("reasoning130", "AgentU"), "rkefhhitk130"),
    (("reasoning130", "keyboard"), "biytcnzqq130"),
    (("reasoning130", "AA"), "reasoning130"),
    (("machine130", "key"), "wearmlo130"),
    (("machine130", "lemon"), "xeovvyi130"),
    (("machine130", "a"), "machine130"),
    (("machine130", "zz"), "lzbghmd130"),
    (("machine130", "AgentU"), "mggubhe130"),
    (("machine130", "keyboard"), "weaiwnv130"),
    (("machine130", "AA"), "machine130"),
    (("learning130", "key"), "viybrgxk130"),
    (("learning130", "lemon"), "wimfatrs130"),
    (("learning130", "a"), "learning130"),
    (("learning130", "zz"), "kdzqmhmf130"),
    (("learning130", "AgentU"), "lkeegcnm130"),
    (("learning130", "keyboard"), "viysbiej130"),
    (("learning130", "AA"), "learning130"),
    (("model130", "key"), "wsbop130"),
    (("model130", "lemon"), "xspsy130"),
    (("model130", "a"), "model130"),
    (("model130", "zz"), "lncdk130"),
    (("model130", "AgentU"), "muhre130"),
    (("model130", "keyboard"), "wsbfz130"),
    (("model130", "AA"), "model130"),
    (("token130", "key"), "dsior130"),
    (("token130", "lemon"), "eswsa130"),
    (("token130", "a"), "token130"),
    (("token130", "zz"), "snjdm130"),
    (("token130", "AgentU"), "tuorg130"),
    (("token130", "keyboard"), "dsifb130"),
    (("token130", "AA"), "token130"),
    (("prompt130", "key"), "zvmwtr130"),
    (("prompt130", "lemon"), "avaace130"),
    (("prompt130", "a"), "prompt130"),
    (("prompt130", "zz"), "oqnlos130"),
    (("prompt130", "AgentU"), "pxszin130"),
    (("prompt130", "keyboard"), "zvmndt130"),
    (("prompt130", "AA"), "prompt130"),
    (("session130", "key"), "ciqcmmx130"),
    (("session130", "lemon"), "diegvzr130"),
    (("session130", "a"), "session130"),
    (("session130", "zz"), "rdrrhnm130"),
    (("session130", "AgentU"), "skwfbin130"),
    (("session130", "keyboard"), "ciqtwoe130"),
    (("session130", "AA"), "session130"),
    (("library130", "key"), "vmzbepi130"),
    (("library130", "lemon"), "wmnfncc130"),
    (("library130", "a"), "library130"),
    (("library130", "zz"), "khaqzqx130"),
    (("library130", "AgentU"), "lofetly130"),
    (("library130", "keyboard"), "vmzsorp130"),
    (("library130", "AA"), "library130"),
    (("service130", "key"), "cipfmao130"),
    (("service130", "lemon"), "didjvni130"),
    (("service130", "a"), "service130"),
    (("service130", "zz"), "rdquhbd130"),
    (("service130", "AgentU"), "skvibwe130"),
    (("service130", "keyboard"), "cipwwcv130"),
    (("service130", "AA"), "service130"),
    (("gateway130", "key"), "qeroayi130"),
    (("gateway130", "lemon"), "refsjlc130"),
    (("gateway130", "a"), "gateway130"),
    (("gateway130", "zz"), "fzsdvzx130"),
    (("gateway130", "AgentU"), "ggxrpuy130"),
    (("gateway130", "keyboard"), "qerfkap130"),
    (("gateway130", "AA"), "gateway130"),
    (("storage130", "key"), "cxmbeeo130"),
    (("storage130", "lemon"), "dxafnri130"),
    (("storage130", "a"), "storage130"),
    (("storage130", "zz"), "rsnqzfd130"),
    (("storage130", "AgentU"), "szsetae130"),
    (("storage130", "keyboard"), "cxmsogv130"),
    (("storage130", "AA"), "storage130"),
    (("network130", "key"), "xirgspu130"),
    (("network130", "lemon"), "yifkbco130"),
    (("network130", "a"), "network130"),
    (("network130", "zz"), "mdsvnqj130"),
    (("network130", "AgentU"), "nkxjhlk130"),
    (("network130", "keyboard"), "xirxcrb130"),
    (("network130", "AA"), "network130"),
    (("latency130", "key"), "verorai130"),
    (("latency130", "lemon"), "wefsanc130"),
    (("latency130", "a"), "latency130"),
    (("latency130", "zz"), "kzsdmbx130"),
    (("latency130", "AgentU"), "lgxrgwy130"),
    (("latency130", "keyboard"), "verfbcp130"),
    (("latency130", "AA"), "latency130"),
    (("buffer130", "key"), "lydpip130"),
    (("buffer130", "lemon"), "myrtrc130"),
    (("buffer130", "a"), "buffer130"),
    (("buffer130", "zz"), "ateedq130"),
    (("buffer130", "AgentU"), "bajsxl130"),
    (("buffer130", "keyboard"), "lydgsr130"),
    (("buffer130", "AA"), "buffer130"),
    (("queue130", "key"), "aycei130"),
    (("queue130", "lemon"), "byqir130"),
    (("queue130", "a"), "queue130"),
    (("queue130", "zz"), "ptdtd130"),
    (("queue130", "AgentU"), "qaihx130"),
    (("queue130", "keyboard"), "aycvs130"),
    (("queue130", "AA"), "queue130"),
    (("worker130", "key"), "gspuip130"),
    (("worker130", "lemon"), "hsdyrc130"),
    (("worker130", "a"), "worker130"),
    (("worker130", "zz"), "vnqjdq130"),
    (("worker130", "AgentU"), "wuvxxl130"),
    (("worker130", "keyboard"), "gsplsr130"),
    (("worker130", "AA"), "worker130"),
    (("kernel130", "key"), "uipxij130"),
    (("kernel130", "lemon"), "vidbrw130"),
    (("kernel130", "a"), "kernel130"),
    (("kernel130", "zz"), "jdqmdk130"),
    (("kernel130", "AgentU"), "kkvaxf130"),
    (("kernel130", "keyboard"), "uiposl130"),
    (("kernel130", "AA"), "kernel130"),
    (("signal130", "key"), "cmexej130"),
    (("signal130", "lemon"), "dmsbnw130"),
    (("signal130", "a"), "signal130"),
    (("signal130", "zz"), "rhfmzk130"),
    (("signal130", "AgentU"), "sokatf130"),
    (("signal130", "keyboard"), "cmeool130"),
    (("signal130", "AA"), "signal130"),
    (("packet130", "key"), "zeauir130"),
    (("packet130", "lemon"), "aeoyre130"),
    (("packet130", "a"), "packet130"),
    (("packet130", "zz"), "ozbjds130"),
    (("packet130", "AgentU"), "pggxxn130"),
    (("packet130", "keyboard"), "zealst130"),
    (("packet130", "AA"), "packet130"),
    (("router130", "key"), "bssdip130"),
    (("router130", "lemon"), "csghrc130"),
    (("router130", "a"), "router130"),
    (("router130", "zz"), "qntsdq130"),
    (("router130", "AgentU"), "ruygxl130"),
    (("router130", "keyboard"), "bssusr130"),
    (("router130", "AA"), "router130"),
    (("cluster130", "key"), "mpscxcb130"),
    (("cluster130", "lemon"), "npgggpv130"),
    (("cluster130", "a"), "cluster130"),
    (("cluster130", "zz"), "bktrsdq130"),
    (("cluster130", "AgentU"), "cryfmyr130"),
    (("cluster130", "keyboard"), "mpsthei130"),
    (("cluster130", "AA"), "cluster130"),
    (("mirror130", "key"), "wmpbsp130"),
    (("mirror130", "lemon"), "xmdfbc130"),
    (("mirror130", "a"), "mirror130"),
    (("mirror130", "zz"), "lhqqnq130"),
    (("mirror130", "AgentU"), "movehl130"),
    (("mirror130", "keyboard"), "wmpscr130"),
    (("mirror130", "AA"), "mirror130"),
    (("filter130", "key"), "pmjdip130"),
    (("filter130", "lemon"), "qmxhrc130"),
    (("filter130", "a"), "filter130"),
    (("filter130", "zz"), "ehksdq130"),
    (("filter130", "AgentU"), "fopgxl130"),
    (("filter130", "keyboard"), "pmjusr130"),
    (("filter130", "AA"), "filter130"),
    (("ranking130", "key"), "belumlq130"),
    (("ranking130", "lemon"), "cezyvyk130"),
    (("ranking130", "a"), "ranking130"),
    (("ranking130", "zz"), "qzmjhmf130"),
    (("ranking130", "AgentU"), "rgrxbhg130"),
    (("ranking130", "keyboard"), "bellwnx130"),
    (("ranking130", "AA"), "ranking130"),
    (("encoding130", "key"), "orayhgxk130"),
    (("encoding130", "lemon"), "procqtrs130"),
    (("encoding130", "a"), "encoding130"),
    (("encoding130", "zz"), "dmbnchmf130"),
    (("encoding130", "AgentU"), "etgbwcnm130"),
    (("encoding130", "keyboard"), "orapriej130"),
    (("encoding130", "AA"), "encoding130"),
    (("mapping130", "key"), "wenzmlq130"),
    (("mapping130", "lemon"), "xebdvyk130"),
    (("mapping130", "a"), "mapping130"),
    (("mapping130", "zz"), "lzoohmf130"),
    (("mapping130", "AgentU"), "mgtcbhg130"),
    (("mapping130", "keyboard"), "wenqwnx130"),
    (("mapping130", "AA"), "mapping130"),
    (("record130", "key"), "biayvb130"),
    (("record130", "lemon"), "cioceo130"),
    (("record130", "a"), "record130"),
    (("record130", "zz"), "qdbnqc130"),
    (("record130", "AgentU"), "rkgbkx130"),
    (("record130", "keyboard"), "biapfd130"),
    (("record130", "AA"), "record130"),
    (("candle130", "key"), "melnpc130"),
    (("candle130", "lemon"), "nezryp130"),
    (("candle130", "a"), "candle130"),
    (("candle130", "zz"), "bzmckd130"),
    (("candle130", "AgentU"), "cgrqey130"),
    (("candle130", "keyboard"), "meleze130"),
    (("candle130", "AA"), "candle130"),
    (("thread130", "key"), "dlpoeb130"),
    (("thread130", "lemon"), "eldsno130"),
    (("thread130", "a"), "thread130"),
    (("thread130", "zz"), "sgqdzc130"),
    (("thread130", "AgentU"), "tnvrtx130"),
    (("thread130", "keyboard"), "dlpfod130"),
    (("thread130", "AA"), "thread130"),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 130: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 130: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "a"),
        "round 130: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 130: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 130: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 130: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", "AA"),
        "round 130: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "key"),
        "bssxh 130: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 130: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "a"),
        "round 130: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 130: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 130: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 130: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", "AA"),
        "round 130: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 130: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 130: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "a"),
        "round 130: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 130: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 130: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 130: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", "AA"),
        "round 130: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 130: the processor reads the record then stops", "key"),
        "bssxh 130: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 130: the processor reads the record then stops", "lemon"),
        "csgbq 130: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 130: the processor reads the record then stops", "a"),
        "round 130: the processor reads the record then stops",
    ),
    (
        ("round 130: the processor reads the record then stops", "zz"),
        "qntmc 130: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 130: the processor reads the record then stops", "AgentU"),
        "ruyaw 130: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 130: the processor reads the record then stops", "keyboard"),
        "bssor 130: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 130: the processor reads the record then stops", "AA"),
        "round 130: the processor reads the record then stops",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "key"),
        "bssxh 130: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "lemon"),
        "csgbq 130: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "a"),
        "round 130: a worker pulls the next task from the queue",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "zz"),
        "qntmc 130: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 130: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "keyboard"),
        "bssor 130: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 130: a worker pulls the next task from the queue", "AA"),
        "round 130: a worker pulls the next task from the queue",
    ),
    (
        ("round 130: signals travel through the network layer", "key"),
        "bssxh 130: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 130: signals travel through the network layer", "lemon"),
        "csgbq 130: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 130: signals travel through the network layer", "a"),
        "round 130: signals travel through the network layer",
    ),
    (
        ("round 130: signals travel through the network layer", "zz"),
        "qntmc 130: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 130: signals travel through the network layer", "AgentU"),
        "ruyaw 130: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 130: signals travel through the network layer", "keyboard"),
        "bssor 130: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 130: signals travel through the network layer", "AA"),
        "round 130: signals travel through the network layer",
    ),
    (
        ("round 130: the gateway routes each request by policy", "key"),
        "bssxh 130: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 130: the gateway routes each request by policy", "lemon"),
        "csgbq 130: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 130: the gateway routes each request by policy", "a"),
        "round 130: the gateway routes each request by policy",
    ),
    (
        ("round 130: the gateway routes each request by policy", "zz"),
        "qntmc 130: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 130: the gateway routes each request by policy", "AgentU"),
        "ruyaw 130: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 130: the gateway routes each request by policy", "keyboard"),
        "bssor 130: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 130: the gateway routes each request by policy", "AA"),
        "round 130: the gateway routes each request by policy",
    ),
    (("round 130: memory grows until the buffer is full", "key"), "bssxh 130: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 130: memory grows until the buffer is full", "lemon"), "csgbq 130: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 130: memory grows until the buffer is full", "a"), "round 130: memory grows until the buffer is full"),
    (("round 130: memory grows until the buffer is full", "zz"), "qntmc 130: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 130: memory grows until the buffer is full", "AgentU"),
        "ruyaw 130: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 130: memory grows until the buffer is full", "keyboard"),
        "bssor 130: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 130: memory grows until the buffer is full", "AA"), "round 130: memory grows until the buffer is full"),
    (("round 130: the cluster mirrors every packet twice", "key"), "bssxh 130: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 130: the cluster mirrors every packet twice", "lemon"),
        "csgbq 130: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 130: the cluster mirrors every packet twice", "a"), "round 130: the cluster mirrors every packet twice"),
    (("round 130: the cluster mirrors every packet twice", "zz"), "qntmc 130: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 130: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 130: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 130: the cluster mirrors every packet twice", "keyboard"),
        "bssor 130: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 130: the cluster mirrors every packet twice", "AA"), "round 130: the cluster mirrors every packet twice"),
    (
        ("round 130: ranking uses tokens learned from the corpus", "key"),
        "bssxh 130: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 130: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", "a"),
        "round 130: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 130: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 130: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 130: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", "AA"),
        "round 130: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 130: a long session ends when the candle dies", "key"),
        "bssxh 130: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 130: a long session ends when the candle dies", "lemon"),
        "csgbq 130: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 130: a long session ends when the candle dies", "a"),
        "round 130: a long session ends when the candle dies",
    ),
    (
        ("round 130: a long session ends when the candle dies", "zz"),
        "qntmc 130: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 130: a long session ends when the candle dies", "AgentU"),
        "ruyaw 130: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 130: a long session ends when the candle dies", "keyboard"),
        "bssor 130: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 130: a long session ends when the candle dies", "AA"),
        "round 130: a long session ends when the candle dies",
    ),
    (("round 130: encode the prompt then map the result", "key"), "bssxh 130: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 130: encode the prompt then map the result", "lemon"), "csgbq 130: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 130: encode the prompt then map the result", "a"), "round 130: encode the prompt then map the result"),
    (("round 130: encode the prompt then map the result", "zz"), "qntmc 130: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 130: encode the prompt then map the result", "AgentU"),
        "ruyaw 130: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 130: encode the prompt then map the result", "keyboard"),
        "bssor 130: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 130: encode the prompt then map the result", "AA"), "round 130: encode the prompt then map the result"),
    (("round 130: the kernel wakes the worker at dawn", "key"), "bssxh 130: rri iovlop ukocc xfo ambocb er neux"),
    (("round 130: the kernel wakes the worker at dawn", "lemon"), "csgbq 130: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 130: the kernel wakes the worker at dawn", "a"), "round 130: the kernel wakes the worker at dawn"),
    (("round 130: the kernel wakes the worker at dawn", "zz"), "qntmc 130: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 130: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 130: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 130: the kernel wakes the worker at dawn", "keyboard"), "bssor 130: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 130: the kernel wakes the worker at dawn", "AA"), "round 130: the kernel wakes the worker at dawn"),
    (("round 130: service latency drops after the patch", "key"), "bssxh 130: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 130: service latency drops after the patch", "lemon"), "csgbq 130: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 130: service latency drops after the patch", "a"), "round 130: service latency drops after the patch"),
    (("round 130: service latency drops after the patch", "zz"), "qntmc 130: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 130: service latency drops after the patch", "AgentU"),
        "ruyaw 130: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 130: service latency drops after the patch", "keyboard"),
        "bssor 130: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 130: service latency drops after the patch", "AA"), "round 130: service latency drops after the patch"),
    (
        ("round 130: the library caches every vector it sees", "key"),
        "bssxh 130: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 130: the library caches every vector it sees", "lemon"),
        "csgbq 130: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 130: the library caches every vector it sees", "a"), "round 130: the library caches every vector it sees"),
    (
        ("round 130: the library caches every vector it sees", "zz"),
        "qntmc 130: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 130: the library caches every vector it sees", "AgentU"),
        "ruyaw 130: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 130: the library caches every vector it sees", "keyboard"),
        "bssor 130: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 130: the library caches every vector it sees", "AA"),
        "round 130: the library caches every vector it sees",
    ),
    (("round 130: agents argue then the debate resolves", "key"), "bssxh 130: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 130: agents argue then the debate resolves", "lemon"), "csgbq 130: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 130: agents argue then the debate resolves", "a"), "round 130: agents argue then the debate resolves"),
    (("round 130: agents argue then the debate resolves", "zz"), "qntmc 130: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 130: agents argue then the debate resolves", "AgentU"),
        "ruyaw 130: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 130: agents argue then the debate resolves", "keyboard"),
        "bssor 130: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 130: agents argue then the debate resolves", "AA"), "round 130: agents argue then the debate resolves"),
    (("round 130: the filter keeps only strong matches", "key"), "bssxh 130: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 130: the filter keeps only strong matches", "lemon"), "csgbq 130: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 130: the filter keeps only strong matches", "a"), "round 130: the filter keeps only strong matches"),
    (("round 130: the filter keeps only strong matches", "zz"), "qntmc 130: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 130: the filter keeps only strong matches", "AgentU"), "ruyaw 130: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 130: the filter keeps only strong matches", "keyboard"),
        "bssor 130: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 130: the filter keeps only strong matches", "AA"), "round 130: the filter keeps only strong matches"),
    (("round 130: the model answers with a short reply", "key"), "bssxh 130: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 130: the model answers with a short reply", "lemon"), "csgbq 130: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 130: the model answers with a short reply", "a"), "round 130: the model answers with a short reply"),
    (("round 130: the model answers with a short reply", "zz"), "qntmc 130: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 130: the model answers with a short reply", "AgentU"), "ruyaw 130: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 130: the model answers with a short reply", "keyboard"),
        "bssor 130: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 130: the model answers with a short reply", "AA"), "round 130: the model answers with a short reply"),
    (
        ("round 130: the recorder stores the reasoning trace", "key"),
        "bssxh 130: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 130: the recorder stores the reasoning trace", "lemon"),
        "csgbq 130: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 130: the recorder stores the reasoning trace", "a"), "round 130: the recorder stores the reasoning trace"),
    (
        ("round 130: the recorder stores the reasoning trace", "zz"),
        "qntmc 130: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 130: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 130: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 130: the recorder stores the reasoning trace", "keyboard"),
        "bssor 130: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 130: the recorder stores the reasoning trace", "AA"),
        "round 130: the recorder stores the reasoning trace",
    ),
    (("round 130: the angel watches the processor run", "key"), "bssxh 130: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 130: the angel watches the processor run", "lemon"), "csgbq 130: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 130: the angel watches the processor run", "a"), "round 130: the angel watches the processor run"),
    (("round 130: the angel watches the processor run", "zz"), "qntmc 130: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 130: the angel watches the processor run", "AgentU"), "ruyaw 130: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 130: the angel watches the processor run", "keyboard"), "bssor 130: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 130: the angel watches the processor run", "AA"), "round 130: the angel watches the processor run"),
    (("round 130: angle of the vector decides the match", "key"), "bssxh 130: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 130: angle of the vector decides the match", "lemon"), "csgbq 130: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 130: angle of the vector decides the match", "a"), "round 130: angle of the vector decides the match"),
    (("round 130: angle of the vector decides the match", "zz"), "qntmc 130: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 130: angle of the vector decides the match", "AgentU"),
        "ruyaw 130: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 130: angle of the vector decides the match", "keyboard"),
        "bssor 130: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 130: angle of the vector decides the match", "AA"), "round 130: angle of the vector decides the match"),
    (
        ("round 130: the candle burns twice as long at night", "key"),
        "bssxh 130: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 130: the candle burns twice as long at night", "lemon"),
        "csgbq 130: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 130: the candle burns twice as long at night", "a"), "round 130: the candle burns twice as long at night"),
    (
        ("round 130: the candle burns twice as long at night", "zz"),
        "qntmc 130: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 130: the candle burns twice as long at night", "AgentU"),
        "ruyaw 130: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 130: the candle burns twice as long at night", "keyboard"),
        "bssor 130: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 130: the candle burns twice as long at night", "AA"),
        "round 130: the candle burns twice as long at night",
    ),
    (("round 130: a mirror of the universe in one line", "key"), "bssxh 130: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 130: a mirror of the universe in one line", "lemon"), "csgbq 130: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 130: a mirror of the universe in one line", "a"), "round 130: a mirror of the universe in one line"),
    (("round 130: a mirror of the universe in one line", "zz"), "qntmc 130: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 130: a mirror of the universe in one line", "AgentU"), "ruyaw 130: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 130: a mirror of the universe in one line", "keyboard"),
        "bssor 130: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 130: a mirror of the universe in one line", "AA"), "round 130: a mirror of the universe in one line"),
    (("round 130: the queue drains before the storm", "key"), "bssxh 130: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 130: the queue drains before the storm", "lemon"), "csgbq 130: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 130: the queue drains before the storm", "a"), "round 130: the queue drains before the storm"),
    (("round 130: the queue drains before the storm", "zz"), "qntmc 130: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 130: the queue drains before the storm", "AgentU"), "ruyaw 130: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 130: the queue drains before the storm", "keyboard"), "bssor 130: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 130: the queue drains before the storm", "AA"), "round 130: the queue drains before the storm"),
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
