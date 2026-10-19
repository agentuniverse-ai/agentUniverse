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
    (("kitten162", "key"), "umrdil162"),
    (("kitten162", "lemon"), "vmfhry162"),
    (("kitten162", "a"), "kitten162"),
    (("kitten162", "zz"), "jhssdm162"),
    (("kitten162", "AgentU"), "koxgxh162"),
    (("kitten162", "keyboard"), "umrusn162"),
    (("kitten162", "AA"), "kitten162"),
    (("sitting162", "key"), "cmrdmlq162"),
    (("sitting162", "lemon"), "dmfhvyk162"),
    (("sitting162", "a"), "sitting162"),
    (("sitting162", "zz"), "rhsshmf162"),
    (("sitting162", "AgentU"), "soxgbhg162"),
    (("sitting162", "keyboard"), "cmruwnx162"),
    (("sitting162", "AA"), "sitting162"),
    (("agent162", "key"), "kkcxx162"),
    (("agent162", "lemon"), "lkqbg162"),
    (("agent162", "a"), "agent162"),
    (("agent162", "zz"), "zfdms162"),
    (("agent162", "AgentU"), "amiam162"),
    (("agent162", "keyboard"), "kkcoh162"),
    (("agent162", "AA"), "agent162"),
    (("angle162", "key"), "krevi162"),
    (("angle162", "lemon"), "lrszr162"),
    (("angle162", "a"), "angle162"),
    (("angle162", "zz"), "zmfkd162"),
    (("angle162", "AgentU"), "atkyx162"),
    (("angle162", "keyboard"), "krems162"),
    (("angle162", "AA"), "angle162"),
    (("universe162", "key"), "ergfipci162"),
    (("universe162", "lemon"), "frujrcwq162"),
    (("universe162", "a"), "universe162"),
    (("universe162", "zz"), "tmhudqrd162"),
    (("universe162", "AgentU"), "utmixlsk162"),
    (("universe162", "keyboard"), "ergwsrjh162"),
    (("universe162", "AA"), "universe162"),
    (("memory162", "key"), "wikyvw162"),
    (("memory162", "lemon"), "xiycej162"),
    (("memory162", "a"), "memory162"),
    (("memory162", "zz"), "ldlnqx162"),
    (("memory162", "AgentU"), "mkqbks162"),
    (("memory162", "keyboard"), "wikpfy162"),
    (("memory162", "AA"), "memory162"),
    (("stream162", "key"), "cxpoek162"),
    (("stream162", "lemon"), "dxdsnx162"),
    (("stream162", "a"), "stream162"),
    (("stream162", "zz"), "rsqdzl162"),
    (("stream162", "AgentU"), "szvrtg162"),
    (("stream162", "keyboard"), "cxpfom162"),
    (("stream162", "AA"), "stream162"),
    (("context162", "key"), "msldivd162"),
    (("context162", "lemon"), "nszhrix162"),
    (("context162", "a"), "context162"),
    (("context162", "zz"), "bnmsdws162"),
    (("context162", "AgentU"), "curgxrt162"),
    (("context162", "keyboard"), "mslusxk162"),
    (("context162", "AA"), "context162"),
    (("knowledge162", "key"), "urmgpcnkc162"),
    (("knowledge162", "lemon"), "vrakyphss162"),
    (("knowledge162", "a"), "knowledge162"),
    (("knowledge162", "zz"), "jmnvkdcfd162"),
    (("knowledge162", "AgentU"), "ktsjeydmi162"),
    (("knowledge162", "keyboard"), "urmxzeujo162"),
    (("knowledge162", "AA"), "knowledge162"),
    (("vector162", "key"), "fiadsp162"),
    (("vector162", "lemon"), "giohbc162"),
    (("vector162", "a"), "vector162"),
    (("vector162", "zz"), "udbsnq162"),
    (("vector162", "AgentU"), "vkgghl162"),
    (("vector162", "keyboard"), "fiaucr162"),
    (("vector162", "AA"), "vector162"),
    (("processor162", "key"), "zvmmiqcsp162"),
    (("processor162", "lemon"), "avaqrdwaf162"),
    (("processor162", "a"), "processor162"),
    (("processor162", "zz"), "oqnbdrrnq162"),
    (("processor162", "AgentU"), "pxspxmsuv162"),
    (("processor162", "keyboard"), "zvmdssjrb162"),
    (("processor162", "AA"), "processor162"),
    (("reasoning162", "key"), "biycslsre162"),
    (("reasoning162", "lemon"), "cimgbymzu162"),
    (("reasoning162", "a"), "reasoning162"),
    (("reasoning162", "zz"), "qdzrnmhmf162"),
    (("reasoning162", "AgentU"), "rkefhhitk162"),
    (("reasoning162", "keyboard"), "biytcnzqq162"),
    (("reasoning162", "AA"), "reasoning162"),
    (("machine162", "key"), "wearmlo162"),
    (("machine162", "lemon"), "xeovvyi162"),
    (("machine162", "a"), "machine162"),
    (("machine162", "zz"), "lzbghmd162"),
    (("machine162", "AgentU"), "mggubhe162"),
    (("machine162", "keyboard"), "weaiwnv162"),
    (("machine162", "AA"), "machine162"),
    (("learning162", "key"), "viybrgxk162"),
    (("learning162", "lemon"), "wimfatrs162"),
    (("learning162", "a"), "learning162"),
    (("learning162", "zz"), "kdzqmhmf162"),
    (("learning162", "AgentU"), "lkeegcnm162"),
    (("learning162", "keyboard"), "viysbiej162"),
    (("learning162", "AA"), "learning162"),
    (("model162", "key"), "wsbop162"),
    (("model162", "lemon"), "xspsy162"),
    (("model162", "a"), "model162"),
    (("model162", "zz"), "lncdk162"),
    (("model162", "AgentU"), "muhre162"),
    (("model162", "keyboard"), "wsbfz162"),
    (("model162", "AA"), "model162"),
    (("token162", "key"), "dsior162"),
    (("token162", "lemon"), "eswsa162"),
    (("token162", "a"), "token162"),
    (("token162", "zz"), "snjdm162"),
    (("token162", "AgentU"), "tuorg162"),
    (("token162", "keyboard"), "dsifb162"),
    (("token162", "AA"), "token162"),
    (("prompt162", "key"), "zvmwtr162"),
    (("prompt162", "lemon"), "avaace162"),
    (("prompt162", "a"), "prompt162"),
    (("prompt162", "zz"), "oqnlos162"),
    (("prompt162", "AgentU"), "pxszin162"),
    (("prompt162", "keyboard"), "zvmndt162"),
    (("prompt162", "AA"), "prompt162"),
    (("session162", "key"), "ciqcmmx162"),
    (("session162", "lemon"), "diegvzr162"),
    (("session162", "a"), "session162"),
    (("session162", "zz"), "rdrrhnm162"),
    (("session162", "AgentU"), "skwfbin162"),
    (("session162", "keyboard"), "ciqtwoe162"),
    (("session162", "AA"), "session162"),
    (("library162", "key"), "vmzbepi162"),
    (("library162", "lemon"), "wmnfncc162"),
    (("library162", "a"), "library162"),
    (("library162", "zz"), "khaqzqx162"),
    (("library162", "AgentU"), "lofetly162"),
    (("library162", "keyboard"), "vmzsorp162"),
    (("library162", "AA"), "library162"),
    (("service162", "key"), "cipfmao162"),
    (("service162", "lemon"), "didjvni162"),
    (("service162", "a"), "service162"),
    (("service162", "zz"), "rdquhbd162"),
    (("service162", "AgentU"), "skvibwe162"),
    (("service162", "keyboard"), "cipwwcv162"),
    (("service162", "AA"), "service162"),
    (("gateway162", "key"), "qeroayi162"),
    (("gateway162", "lemon"), "refsjlc162"),
    (("gateway162", "a"), "gateway162"),
    (("gateway162", "zz"), "fzsdvzx162"),
    (("gateway162", "AgentU"), "ggxrpuy162"),
    (("gateway162", "keyboard"), "qerfkap162"),
    (("gateway162", "AA"), "gateway162"),
    (("storage162", "key"), "cxmbeeo162"),
    (("storage162", "lemon"), "dxafnri162"),
    (("storage162", "a"), "storage162"),
    (("storage162", "zz"), "rsnqzfd162"),
    (("storage162", "AgentU"), "szsetae162"),
    (("storage162", "keyboard"), "cxmsogv162"),
    (("storage162", "AA"), "storage162"),
    (("network162", "key"), "xirgspu162"),
    (("network162", "lemon"), "yifkbco162"),
    (("network162", "a"), "network162"),
    (("network162", "zz"), "mdsvnqj162"),
    (("network162", "AgentU"), "nkxjhlk162"),
    (("network162", "keyboard"), "xirxcrb162"),
    (("network162", "AA"), "network162"),
    (("latency162", "key"), "verorai162"),
    (("latency162", "lemon"), "wefsanc162"),
    (("latency162", "a"), "latency162"),
    (("latency162", "zz"), "kzsdmbx162"),
    (("latency162", "AgentU"), "lgxrgwy162"),
    (("latency162", "keyboard"), "verfbcp162"),
    (("latency162", "AA"), "latency162"),
    (("buffer162", "key"), "lydpip162"),
    (("buffer162", "lemon"), "myrtrc162"),
    (("buffer162", "a"), "buffer162"),
    (("buffer162", "zz"), "ateedq162"),
    (("buffer162", "AgentU"), "bajsxl162"),
    (("buffer162", "keyboard"), "lydgsr162"),
    (("buffer162", "AA"), "buffer162"),
    (("queue162", "key"), "aycei162"),
    (("queue162", "lemon"), "byqir162"),
    (("queue162", "a"), "queue162"),
    (("queue162", "zz"), "ptdtd162"),
    (("queue162", "AgentU"), "qaihx162"),
    (("queue162", "keyboard"), "aycvs162"),
    (("queue162", "AA"), "queue162"),
    (("worker162", "key"), "gspuip162"),
    (("worker162", "lemon"), "hsdyrc162"),
    (("worker162", "a"), "worker162"),
    (("worker162", "zz"), "vnqjdq162"),
    (("worker162", "AgentU"), "wuvxxl162"),
    (("worker162", "keyboard"), "gsplsr162"),
    (("worker162", "AA"), "worker162"),
    (("kernel162", "key"), "uipxij162"),
    (("kernel162", "lemon"), "vidbrw162"),
    (("kernel162", "a"), "kernel162"),
    (("kernel162", "zz"), "jdqmdk162"),
    (("kernel162", "AgentU"), "kkvaxf162"),
    (("kernel162", "keyboard"), "uiposl162"),
    (("kernel162", "AA"), "kernel162"),
    (("signal162", "key"), "cmexej162"),
    (("signal162", "lemon"), "dmsbnw162"),
    (("signal162", "a"), "signal162"),
    (("signal162", "zz"), "rhfmzk162"),
    (("signal162", "AgentU"), "sokatf162"),
    (("signal162", "keyboard"), "cmeool162"),
    (("signal162", "AA"), "signal162"),
    (("packet162", "key"), "zeauir162"),
    (("packet162", "lemon"), "aeoyre162"),
    (("packet162", "a"), "packet162"),
    (("packet162", "zz"), "ozbjds162"),
    (("packet162", "AgentU"), "pggxxn162"),
    (("packet162", "keyboard"), "zealst162"),
    (("packet162", "AA"), "packet162"),
    (("router162", "key"), "bssdip162"),
    (("router162", "lemon"), "csghrc162"),
    (("router162", "a"), "router162"),
    (("router162", "zz"), "qntsdq162"),
    (("router162", "AgentU"), "ruygxl162"),
    (("router162", "keyboard"), "bssusr162"),
    (("router162", "AA"), "router162"),
    (("cluster162", "key"), "mpscxcb162"),
    (("cluster162", "lemon"), "npgggpv162"),
    (("cluster162", "a"), "cluster162"),
    (("cluster162", "zz"), "bktrsdq162"),
    (("cluster162", "AgentU"), "cryfmyr162"),
    (("cluster162", "keyboard"), "mpsthei162"),
    (("cluster162", "AA"), "cluster162"),
    (("mirror162", "key"), "wmpbsp162"),
    (("mirror162", "lemon"), "xmdfbc162"),
    (("mirror162", "a"), "mirror162"),
    (("mirror162", "zz"), "lhqqnq162"),
    (("mirror162", "AgentU"), "movehl162"),
    (("mirror162", "keyboard"), "wmpscr162"),
    (("mirror162", "AA"), "mirror162"),
    (("filter162", "key"), "pmjdip162"),
    (("filter162", "lemon"), "qmxhrc162"),
    (("filter162", "a"), "filter162"),
    (("filter162", "zz"), "ehksdq162"),
    (("filter162", "AgentU"), "fopgxl162"),
    (("filter162", "keyboard"), "pmjusr162"),
    (("filter162", "AA"), "filter162"),
    (("ranking162", "key"), "belumlq162"),
    (("ranking162", "lemon"), "cezyvyk162"),
    (("ranking162", "a"), "ranking162"),
    (("ranking162", "zz"), "qzmjhmf162"),
    (("ranking162", "AgentU"), "rgrxbhg162"),
    (("ranking162", "keyboard"), "bellwnx162"),
    (("ranking162", "AA"), "ranking162"),
    (("encoding162", "key"), "orayhgxk162"),
    (("encoding162", "lemon"), "procqtrs162"),
    (("encoding162", "a"), "encoding162"),
    (("encoding162", "zz"), "dmbnchmf162"),
    (("encoding162", "AgentU"), "etgbwcnm162"),
    (("encoding162", "keyboard"), "orapriej162"),
    (("encoding162", "AA"), "encoding162"),
    (("mapping162", "key"), "wenzmlq162"),
    (("mapping162", "lemon"), "xebdvyk162"),
    (("mapping162", "a"), "mapping162"),
    (("mapping162", "zz"), "lzoohmf162"),
    (("mapping162", "AgentU"), "mgtcbhg162"),
    (("mapping162", "keyboard"), "wenqwnx162"),
    (("mapping162", "AA"), "mapping162"),
    (("record162", "key"), "biayvb162"),
    (("record162", "lemon"), "cioceo162"),
    (("record162", "a"), "record162"),
    (("record162", "zz"), "qdbnqc162"),
    (("record162", "AgentU"), "rkgbkx162"),
    (("record162", "keyboard"), "biapfd162"),
    (("record162", "AA"), "record162"),
    (("candle162", "key"), "melnpc162"),
    (("candle162", "lemon"), "nezryp162"),
    (("candle162", "a"), "candle162"),
    (("candle162", "zz"), "bzmckd162"),
    (("candle162", "AgentU"), "cgrqey162"),
    (("candle162", "keyboard"), "meleze162"),
    (("candle162", "AA"), "candle162"),
    (("thread162", "key"), "dlpoeb162"),
    (("thread162", "lemon"), "eldsno162"),
    (("thread162", "a"), "thread162"),
    (("thread162", "zz"), "sgqdzc162"),
    (("thread162", "AgentU"), "tnvrtx162"),
    (("thread162", "keyboard"), "dlpfod162"),
    (("thread162", "AA"), "thread162"),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 162: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 162: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "a"),
        "round 162: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 162: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 162: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 162: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", "AA"),
        "round 162: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "key"),
        "bssxh 162: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 162: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "a"),
        "round 162: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 162: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 162: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 162: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", "AA"),
        "round 162: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 162: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 162: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "a"),
        "round 162: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 162: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 162: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 162: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", "AA"),
        "round 162: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 162: the processor reads the record then stops", "key"),
        "bssxh 162: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 162: the processor reads the record then stops", "lemon"),
        "csgbq 162: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 162: the processor reads the record then stops", "a"),
        "round 162: the processor reads the record then stops",
    ),
    (
        ("round 162: the processor reads the record then stops", "zz"),
        "qntmc 162: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 162: the processor reads the record then stops", "AgentU"),
        "ruyaw 162: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 162: the processor reads the record then stops", "keyboard"),
        "bssor 162: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 162: the processor reads the record then stops", "AA"),
        "round 162: the processor reads the record then stops",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "key"),
        "bssxh 162: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "lemon"),
        "csgbq 162: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "a"),
        "round 162: a worker pulls the next task from the queue",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "zz"),
        "qntmc 162: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 162: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "keyboard"),
        "bssor 162: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 162: a worker pulls the next task from the queue", "AA"),
        "round 162: a worker pulls the next task from the queue",
    ),
    (
        ("round 162: signals travel through the network layer", "key"),
        "bssxh 162: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 162: signals travel through the network layer", "lemon"),
        "csgbq 162: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 162: signals travel through the network layer", "a"),
        "round 162: signals travel through the network layer",
    ),
    (
        ("round 162: signals travel through the network layer", "zz"),
        "qntmc 162: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 162: signals travel through the network layer", "AgentU"),
        "ruyaw 162: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 162: signals travel through the network layer", "keyboard"),
        "bssor 162: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 162: signals travel through the network layer", "AA"),
        "round 162: signals travel through the network layer",
    ),
    (
        ("round 162: the gateway routes each request by policy", "key"),
        "bssxh 162: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 162: the gateway routes each request by policy", "lemon"),
        "csgbq 162: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 162: the gateway routes each request by policy", "a"),
        "round 162: the gateway routes each request by policy",
    ),
    (
        ("round 162: the gateway routes each request by policy", "zz"),
        "qntmc 162: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 162: the gateway routes each request by policy", "AgentU"),
        "ruyaw 162: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 162: the gateway routes each request by policy", "keyboard"),
        "bssor 162: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 162: the gateway routes each request by policy", "AA"),
        "round 162: the gateway routes each request by policy",
    ),
    (("round 162: memory grows until the buffer is full", "key"), "bssxh 162: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 162: memory grows until the buffer is full", "lemon"), "csgbq 162: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 162: memory grows until the buffer is full", "a"), "round 162: memory grows until the buffer is full"),
    (("round 162: memory grows until the buffer is full", "zz"), "qntmc 162: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 162: memory grows until the buffer is full", "AgentU"),
        "ruyaw 162: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 162: memory grows until the buffer is full", "keyboard"),
        "bssor 162: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 162: memory grows until the buffer is full", "AA"), "round 162: memory grows until the buffer is full"),
    (("round 162: the cluster mirrors every packet twice", "key"), "bssxh 162: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 162: the cluster mirrors every packet twice", "lemon"),
        "csgbq 162: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 162: the cluster mirrors every packet twice", "a"), "round 162: the cluster mirrors every packet twice"),
    (("round 162: the cluster mirrors every packet twice", "zz"), "qntmc 162: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 162: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 162: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 162: the cluster mirrors every packet twice", "keyboard"),
        "bssor 162: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 162: the cluster mirrors every packet twice", "AA"), "round 162: the cluster mirrors every packet twice"),
    (
        ("round 162: ranking uses tokens learned from the corpus", "key"),
        "bssxh 162: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 162: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", "a"),
        "round 162: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 162: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 162: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 162: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", "AA"),
        "round 162: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 162: a long session ends when the candle dies", "key"),
        "bssxh 162: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 162: a long session ends when the candle dies", "lemon"),
        "csgbq 162: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 162: a long session ends when the candle dies", "a"),
        "round 162: a long session ends when the candle dies",
    ),
    (
        ("round 162: a long session ends when the candle dies", "zz"),
        "qntmc 162: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 162: a long session ends when the candle dies", "AgentU"),
        "ruyaw 162: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 162: a long session ends when the candle dies", "keyboard"),
        "bssor 162: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 162: a long session ends when the candle dies", "AA"),
        "round 162: a long session ends when the candle dies",
    ),
    (("round 162: encode the prompt then map the result", "key"), "bssxh 162: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 162: encode the prompt then map the result", "lemon"), "csgbq 162: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 162: encode the prompt then map the result", "a"), "round 162: encode the prompt then map the result"),
    (("round 162: encode the prompt then map the result", "zz"), "qntmc 162: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 162: encode the prompt then map the result", "AgentU"),
        "ruyaw 162: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 162: encode the prompt then map the result", "keyboard"),
        "bssor 162: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 162: encode the prompt then map the result", "AA"), "round 162: encode the prompt then map the result"),
    (("round 162: the kernel wakes the worker at dawn", "key"), "bssxh 162: rri iovlop ukocc xfo ambocb er neux"),
    (("round 162: the kernel wakes the worker at dawn", "lemon"), "csgbq 162: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 162: the kernel wakes the worker at dawn", "a"), "round 162: the kernel wakes the worker at dawn"),
    (("round 162: the kernel wakes the worker at dawn", "zz"), "qntmc 162: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 162: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 162: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 162: the kernel wakes the worker at dawn", "keyboard"), "bssor 162: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 162: the kernel wakes the worker at dawn", "AA"), "round 162: the kernel wakes the worker at dawn"),
    (("round 162: service latency drops after the patch", "key"), "bssxh 162: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 162: service latency drops after the patch", "lemon"), "csgbq 162: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 162: service latency drops after the patch", "a"), "round 162: service latency drops after the patch"),
    (("round 162: service latency drops after the patch", "zz"), "qntmc 162: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 162: service latency drops after the patch", "AgentU"),
        "ruyaw 162: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 162: service latency drops after the patch", "keyboard"),
        "bssor 162: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 162: service latency drops after the patch", "AA"), "round 162: service latency drops after the patch"),
    (
        ("round 162: the library caches every vector it sees", "key"),
        "bssxh 162: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 162: the library caches every vector it sees", "lemon"),
        "csgbq 162: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 162: the library caches every vector it sees", "a"), "round 162: the library caches every vector it sees"),
    (
        ("round 162: the library caches every vector it sees", "zz"),
        "qntmc 162: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 162: the library caches every vector it sees", "AgentU"),
        "ruyaw 162: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 162: the library caches every vector it sees", "keyboard"),
        "bssor 162: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 162: the library caches every vector it sees", "AA"),
        "round 162: the library caches every vector it sees",
    ),
    (("round 162: agents argue then the debate resolves", "key"), "bssxh 162: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 162: agents argue then the debate resolves", "lemon"), "csgbq 162: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 162: agents argue then the debate resolves", "a"), "round 162: agents argue then the debate resolves"),
    (("round 162: agents argue then the debate resolves", "zz"), "qntmc 162: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 162: agents argue then the debate resolves", "AgentU"),
        "ruyaw 162: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 162: agents argue then the debate resolves", "keyboard"),
        "bssor 162: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 162: agents argue then the debate resolves", "AA"), "round 162: agents argue then the debate resolves"),
    (("round 162: the filter keeps only strong matches", "key"), "bssxh 162: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 162: the filter keeps only strong matches", "lemon"), "csgbq 162: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 162: the filter keeps only strong matches", "a"), "round 162: the filter keeps only strong matches"),
    (("round 162: the filter keeps only strong matches", "zz"), "qntmc 162: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 162: the filter keeps only strong matches", "AgentU"), "ruyaw 162: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 162: the filter keeps only strong matches", "keyboard"),
        "bssor 162: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 162: the filter keeps only strong matches", "AA"), "round 162: the filter keeps only strong matches"),
    (("round 162: the model answers with a short reply", "key"), "bssxh 162: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 162: the model answers with a short reply", "lemon"), "csgbq 162: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 162: the model answers with a short reply", "a"), "round 162: the model answers with a short reply"),
    (("round 162: the model answers with a short reply", "zz"), "qntmc 162: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 162: the model answers with a short reply", "AgentU"), "ruyaw 162: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 162: the model answers with a short reply", "keyboard"),
        "bssor 162: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 162: the model answers with a short reply", "AA"), "round 162: the model answers with a short reply"),
    (
        ("round 162: the recorder stores the reasoning trace", "key"),
        "bssxh 162: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 162: the recorder stores the reasoning trace", "lemon"),
        "csgbq 162: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 162: the recorder stores the reasoning trace", "a"), "round 162: the recorder stores the reasoning trace"),
    (
        ("round 162: the recorder stores the reasoning trace", "zz"),
        "qntmc 162: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 162: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 162: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 162: the recorder stores the reasoning trace", "keyboard"),
        "bssor 162: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 162: the recorder stores the reasoning trace", "AA"),
        "round 162: the recorder stores the reasoning trace",
    ),
    (("round 162: the angel watches the processor run", "key"), "bssxh 162: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 162: the angel watches the processor run", "lemon"), "csgbq 162: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 162: the angel watches the processor run", "a"), "round 162: the angel watches the processor run"),
    (("round 162: the angel watches the processor run", "zz"), "qntmc 162: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 162: the angel watches the processor run", "AgentU"), "ruyaw 162: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 162: the angel watches the processor run", "keyboard"), "bssor 162: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 162: the angel watches the processor run", "AA"), "round 162: the angel watches the processor run"),
    (("round 162: angle of the vector decides the match", "key"), "bssxh 162: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 162: angle of the vector decides the match", "lemon"), "csgbq 162: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 162: angle of the vector decides the match", "a"), "round 162: angle of the vector decides the match"),
    (("round 162: angle of the vector decides the match", "zz"), "qntmc 162: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 162: angle of the vector decides the match", "AgentU"),
        "ruyaw 162: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 162: angle of the vector decides the match", "keyboard"),
        "bssor 162: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 162: angle of the vector decides the match", "AA"), "round 162: angle of the vector decides the match"),
    (
        ("round 162: the candle burns twice as long at night", "key"),
        "bssxh 162: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 162: the candle burns twice as long at night", "lemon"),
        "csgbq 162: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 162: the candle burns twice as long at night", "a"), "round 162: the candle burns twice as long at night"),
    (
        ("round 162: the candle burns twice as long at night", "zz"),
        "qntmc 162: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 162: the candle burns twice as long at night", "AgentU"),
        "ruyaw 162: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 162: the candle burns twice as long at night", "keyboard"),
        "bssor 162: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 162: the candle burns twice as long at night", "AA"),
        "round 162: the candle burns twice as long at night",
    ),
    (("round 162: a mirror of the universe in one line", "key"), "bssxh 162: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 162: a mirror of the universe in one line", "lemon"), "csgbq 162: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 162: a mirror of the universe in one line", "a"), "round 162: a mirror of the universe in one line"),
    (("round 162: a mirror of the universe in one line", "zz"), "qntmc 162: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 162: a mirror of the universe in one line", "AgentU"), "ruyaw 162: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 162: a mirror of the universe in one line", "keyboard"),
        "bssor 162: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 162: a mirror of the universe in one line", "AA"), "round 162: a mirror of the universe in one line"),
    (("round 162: the queue drains before the storm", "key"), "bssxh 162: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 162: the queue drains before the storm", "lemon"), "csgbq 162: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 162: the queue drains before the storm", "a"), "round 162: the queue drains before the storm"),
    (("round 162: the queue drains before the storm", "zz"), "qntmc 162: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 162: the queue drains before the storm", "AgentU"), "ruyaw 162: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 162: the queue drains before the storm", "keyboard"), "bssor 162: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 162: the queue drains before the storm", "AA"), "round 162: the queue drains before the storm"),
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
