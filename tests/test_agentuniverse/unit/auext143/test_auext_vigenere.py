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
    (("kitten143", "key"), "umrdil143"),
    (("kitten143", "lemon"), "vmfhry143"),
    (("kitten143", "a"), "kitten143"),
    (("kitten143", "zz"), "jhssdm143"),
    (("kitten143", "AgentU"), "koxgxh143"),
    (("kitten143", "keyboard"), "umrusn143"),
    (("kitten143", "AA"), "kitten143"),
    (("sitting143", "key"), "cmrdmlq143"),
    (("sitting143", "lemon"), "dmfhvyk143"),
    (("sitting143", "a"), "sitting143"),
    (("sitting143", "zz"), "rhsshmf143"),
    (("sitting143", "AgentU"), "soxgbhg143"),
    (("sitting143", "keyboard"), "cmruwnx143"),
    (("sitting143", "AA"), "sitting143"),
    (("agent143", "key"), "kkcxx143"),
    (("agent143", "lemon"), "lkqbg143"),
    (("agent143", "a"), "agent143"),
    (("agent143", "zz"), "zfdms143"),
    (("agent143", "AgentU"), "amiam143"),
    (("agent143", "keyboard"), "kkcoh143"),
    (("agent143", "AA"), "agent143"),
    (("angle143", "key"), "krevi143"),
    (("angle143", "lemon"), "lrszr143"),
    (("angle143", "a"), "angle143"),
    (("angle143", "zz"), "zmfkd143"),
    (("angle143", "AgentU"), "atkyx143"),
    (("angle143", "keyboard"), "krems143"),
    (("angle143", "AA"), "angle143"),
    (("universe143", "key"), "ergfipci143"),
    (("universe143", "lemon"), "frujrcwq143"),
    (("universe143", "a"), "universe143"),
    (("universe143", "zz"), "tmhudqrd143"),
    (("universe143", "AgentU"), "utmixlsk143"),
    (("universe143", "keyboard"), "ergwsrjh143"),
    (("universe143", "AA"), "universe143"),
    (("memory143", "key"), "wikyvw143"),
    (("memory143", "lemon"), "xiycej143"),
    (("memory143", "a"), "memory143"),
    (("memory143", "zz"), "ldlnqx143"),
    (("memory143", "AgentU"), "mkqbks143"),
    (("memory143", "keyboard"), "wikpfy143"),
    (("memory143", "AA"), "memory143"),
    (("stream143", "key"), "cxpoek143"),
    (("stream143", "lemon"), "dxdsnx143"),
    (("stream143", "a"), "stream143"),
    (("stream143", "zz"), "rsqdzl143"),
    (("stream143", "AgentU"), "szvrtg143"),
    (("stream143", "keyboard"), "cxpfom143"),
    (("stream143", "AA"), "stream143"),
    (("context143", "key"), "msldivd143"),
    (("context143", "lemon"), "nszhrix143"),
    (("context143", "a"), "context143"),
    (("context143", "zz"), "bnmsdws143"),
    (("context143", "AgentU"), "curgxrt143"),
    (("context143", "keyboard"), "mslusxk143"),
    (("context143", "AA"), "context143"),
    (("knowledge143", "key"), "urmgpcnkc143"),
    (("knowledge143", "lemon"), "vrakyphss143"),
    (("knowledge143", "a"), "knowledge143"),
    (("knowledge143", "zz"), "jmnvkdcfd143"),
    (("knowledge143", "AgentU"), "ktsjeydmi143"),
    (("knowledge143", "keyboard"), "urmxzeujo143"),
    (("knowledge143", "AA"), "knowledge143"),
    (("vector143", "key"), "fiadsp143"),
    (("vector143", "lemon"), "giohbc143"),
    (("vector143", "a"), "vector143"),
    (("vector143", "zz"), "udbsnq143"),
    (("vector143", "AgentU"), "vkgghl143"),
    (("vector143", "keyboard"), "fiaucr143"),
    (("vector143", "AA"), "vector143"),
    (("processor143", "key"), "zvmmiqcsp143"),
    (("processor143", "lemon"), "avaqrdwaf143"),
    (("processor143", "a"), "processor143"),
    (("processor143", "zz"), "oqnbdrrnq143"),
    (("processor143", "AgentU"), "pxspxmsuv143"),
    (("processor143", "keyboard"), "zvmdssjrb143"),
    (("processor143", "AA"), "processor143"),
    (("reasoning143", "key"), "biycslsre143"),
    (("reasoning143", "lemon"), "cimgbymzu143"),
    (("reasoning143", "a"), "reasoning143"),
    (("reasoning143", "zz"), "qdzrnmhmf143"),
    (("reasoning143", "AgentU"), "rkefhhitk143"),
    (("reasoning143", "keyboard"), "biytcnzqq143"),
    (("reasoning143", "AA"), "reasoning143"),
    (("machine143", "key"), "wearmlo143"),
    (("machine143", "lemon"), "xeovvyi143"),
    (("machine143", "a"), "machine143"),
    (("machine143", "zz"), "lzbghmd143"),
    (("machine143", "AgentU"), "mggubhe143"),
    (("machine143", "keyboard"), "weaiwnv143"),
    (("machine143", "AA"), "machine143"),
    (("learning143", "key"), "viybrgxk143"),
    (("learning143", "lemon"), "wimfatrs143"),
    (("learning143", "a"), "learning143"),
    (("learning143", "zz"), "kdzqmhmf143"),
    (("learning143", "AgentU"), "lkeegcnm143"),
    (("learning143", "keyboard"), "viysbiej143"),
    (("learning143", "AA"), "learning143"),
    (("model143", "key"), "wsbop143"),
    (("model143", "lemon"), "xspsy143"),
    (("model143", "a"), "model143"),
    (("model143", "zz"), "lncdk143"),
    (("model143", "AgentU"), "muhre143"),
    (("model143", "keyboard"), "wsbfz143"),
    (("model143", "AA"), "model143"),
    (("token143", "key"), "dsior143"),
    (("token143", "lemon"), "eswsa143"),
    (("token143", "a"), "token143"),
    (("token143", "zz"), "snjdm143"),
    (("token143", "AgentU"), "tuorg143"),
    (("token143", "keyboard"), "dsifb143"),
    (("token143", "AA"), "token143"),
    (("prompt143", "key"), "zvmwtr143"),
    (("prompt143", "lemon"), "avaace143"),
    (("prompt143", "a"), "prompt143"),
    (("prompt143", "zz"), "oqnlos143"),
    (("prompt143", "AgentU"), "pxszin143"),
    (("prompt143", "keyboard"), "zvmndt143"),
    (("prompt143", "AA"), "prompt143"),
    (("session143", "key"), "ciqcmmx143"),
    (("session143", "lemon"), "diegvzr143"),
    (("session143", "a"), "session143"),
    (("session143", "zz"), "rdrrhnm143"),
    (("session143", "AgentU"), "skwfbin143"),
    (("session143", "keyboard"), "ciqtwoe143"),
    (("session143", "AA"), "session143"),
    (("library143", "key"), "vmzbepi143"),
    (("library143", "lemon"), "wmnfncc143"),
    (("library143", "a"), "library143"),
    (("library143", "zz"), "khaqzqx143"),
    (("library143", "AgentU"), "lofetly143"),
    (("library143", "keyboard"), "vmzsorp143"),
    (("library143", "AA"), "library143"),
    (("service143", "key"), "cipfmao143"),
    (("service143", "lemon"), "didjvni143"),
    (("service143", "a"), "service143"),
    (("service143", "zz"), "rdquhbd143"),
    (("service143", "AgentU"), "skvibwe143"),
    (("service143", "keyboard"), "cipwwcv143"),
    (("service143", "AA"), "service143"),
    (("gateway143", "key"), "qeroayi143"),
    (("gateway143", "lemon"), "refsjlc143"),
    (("gateway143", "a"), "gateway143"),
    (("gateway143", "zz"), "fzsdvzx143"),
    (("gateway143", "AgentU"), "ggxrpuy143"),
    (("gateway143", "keyboard"), "qerfkap143"),
    (("gateway143", "AA"), "gateway143"),
    (("storage143", "key"), "cxmbeeo143"),
    (("storage143", "lemon"), "dxafnri143"),
    (("storage143", "a"), "storage143"),
    (("storage143", "zz"), "rsnqzfd143"),
    (("storage143", "AgentU"), "szsetae143"),
    (("storage143", "keyboard"), "cxmsogv143"),
    (("storage143", "AA"), "storage143"),
    (("network143", "key"), "xirgspu143"),
    (("network143", "lemon"), "yifkbco143"),
    (("network143", "a"), "network143"),
    (("network143", "zz"), "mdsvnqj143"),
    (("network143", "AgentU"), "nkxjhlk143"),
    (("network143", "keyboard"), "xirxcrb143"),
    (("network143", "AA"), "network143"),
    (("latency143", "key"), "verorai143"),
    (("latency143", "lemon"), "wefsanc143"),
    (("latency143", "a"), "latency143"),
    (("latency143", "zz"), "kzsdmbx143"),
    (("latency143", "AgentU"), "lgxrgwy143"),
    (("latency143", "keyboard"), "verfbcp143"),
    (("latency143", "AA"), "latency143"),
    (("buffer143", "key"), "lydpip143"),
    (("buffer143", "lemon"), "myrtrc143"),
    (("buffer143", "a"), "buffer143"),
    (("buffer143", "zz"), "ateedq143"),
    (("buffer143", "AgentU"), "bajsxl143"),
    (("buffer143", "keyboard"), "lydgsr143"),
    (("buffer143", "AA"), "buffer143"),
    (("queue143", "key"), "aycei143"),
    (("queue143", "lemon"), "byqir143"),
    (("queue143", "a"), "queue143"),
    (("queue143", "zz"), "ptdtd143"),
    (("queue143", "AgentU"), "qaihx143"),
    (("queue143", "keyboard"), "aycvs143"),
    (("queue143", "AA"), "queue143"),
    (("worker143", "key"), "gspuip143"),
    (("worker143", "lemon"), "hsdyrc143"),
    (("worker143", "a"), "worker143"),
    (("worker143", "zz"), "vnqjdq143"),
    (("worker143", "AgentU"), "wuvxxl143"),
    (("worker143", "keyboard"), "gsplsr143"),
    (("worker143", "AA"), "worker143"),
    (("kernel143", "key"), "uipxij143"),
    (("kernel143", "lemon"), "vidbrw143"),
    (("kernel143", "a"), "kernel143"),
    (("kernel143", "zz"), "jdqmdk143"),
    (("kernel143", "AgentU"), "kkvaxf143"),
    (("kernel143", "keyboard"), "uiposl143"),
    (("kernel143", "AA"), "kernel143"),
    (("signal143", "key"), "cmexej143"),
    (("signal143", "lemon"), "dmsbnw143"),
    (("signal143", "a"), "signal143"),
    (("signal143", "zz"), "rhfmzk143"),
    (("signal143", "AgentU"), "sokatf143"),
    (("signal143", "keyboard"), "cmeool143"),
    (("signal143", "AA"), "signal143"),
    (("packet143", "key"), "zeauir143"),
    (("packet143", "lemon"), "aeoyre143"),
    (("packet143", "a"), "packet143"),
    (("packet143", "zz"), "ozbjds143"),
    (("packet143", "AgentU"), "pggxxn143"),
    (("packet143", "keyboard"), "zealst143"),
    (("packet143", "AA"), "packet143"),
    (("router143", "key"), "bssdip143"),
    (("router143", "lemon"), "csghrc143"),
    (("router143", "a"), "router143"),
    (("router143", "zz"), "qntsdq143"),
    (("router143", "AgentU"), "ruygxl143"),
    (("router143", "keyboard"), "bssusr143"),
    (("router143", "AA"), "router143"),
    (("cluster143", "key"), "mpscxcb143"),
    (("cluster143", "lemon"), "npgggpv143"),
    (("cluster143", "a"), "cluster143"),
    (("cluster143", "zz"), "bktrsdq143"),
    (("cluster143", "AgentU"), "cryfmyr143"),
    (("cluster143", "keyboard"), "mpsthei143"),
    (("cluster143", "AA"), "cluster143"),
    (("mirror143", "key"), "wmpbsp143"),
    (("mirror143", "lemon"), "xmdfbc143"),
    (("mirror143", "a"), "mirror143"),
    (("mirror143", "zz"), "lhqqnq143"),
    (("mirror143", "AgentU"), "movehl143"),
    (("mirror143", "keyboard"), "wmpscr143"),
    (("mirror143", "AA"), "mirror143"),
    (("filter143", "key"), "pmjdip143"),
    (("filter143", "lemon"), "qmxhrc143"),
    (("filter143", "a"), "filter143"),
    (("filter143", "zz"), "ehksdq143"),
    (("filter143", "AgentU"), "fopgxl143"),
    (("filter143", "keyboard"), "pmjusr143"),
    (("filter143", "AA"), "filter143"),
    (("ranking143", "key"), "belumlq143"),
    (("ranking143", "lemon"), "cezyvyk143"),
    (("ranking143", "a"), "ranking143"),
    (("ranking143", "zz"), "qzmjhmf143"),
    (("ranking143", "AgentU"), "rgrxbhg143"),
    (("ranking143", "keyboard"), "bellwnx143"),
    (("ranking143", "AA"), "ranking143"),
    (("encoding143", "key"), "orayhgxk143"),
    (("encoding143", "lemon"), "procqtrs143"),
    (("encoding143", "a"), "encoding143"),
    (("encoding143", "zz"), "dmbnchmf143"),
    (("encoding143", "AgentU"), "etgbwcnm143"),
    (("encoding143", "keyboard"), "orapriej143"),
    (("encoding143", "AA"), "encoding143"),
    (("mapping143", "key"), "wenzmlq143"),
    (("mapping143", "lemon"), "xebdvyk143"),
    (("mapping143", "a"), "mapping143"),
    (("mapping143", "zz"), "lzoohmf143"),
    (("mapping143", "AgentU"), "mgtcbhg143"),
    (("mapping143", "keyboard"), "wenqwnx143"),
    (("mapping143", "AA"), "mapping143"),
    (("record143", "key"), "biayvb143"),
    (("record143", "lemon"), "cioceo143"),
    (("record143", "a"), "record143"),
    (("record143", "zz"), "qdbnqc143"),
    (("record143", "AgentU"), "rkgbkx143"),
    (("record143", "keyboard"), "biapfd143"),
    (("record143", "AA"), "record143"),
    (("candle143", "key"), "melnpc143"),
    (("candle143", "lemon"), "nezryp143"),
    (("candle143", "a"), "candle143"),
    (("candle143", "zz"), "bzmckd143"),
    (("candle143", "AgentU"), "cgrqey143"),
    (("candle143", "keyboard"), "meleze143"),
    (("candle143", "AA"), "candle143"),
    (("thread143", "key"), "dlpoeb143"),
    (("thread143", "lemon"), "eldsno143"),
    (("thread143", "a"), "thread143"),
    (("thread143", "zz"), "sgqdzc143"),
    (("thread143", "AgentU"), "tnvrtx143"),
    (("thread143", "keyboard"), "dlpfod143"),
    (("thread143", "AA"), "thread143"),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 143: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 143: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "a"),
        "round 143: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 143: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 143: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 143: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", "AA"),
        "round 143: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "key"),
        "bssxh 143: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 143: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "a"),
        "round 143: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 143: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 143: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 143: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", "AA"),
        "round 143: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 143: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 143: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "a"),
        "round 143: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 143: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 143: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 143: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", "AA"),
        "round 143: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 143: the processor reads the record then stops", "key"),
        "bssxh 143: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 143: the processor reads the record then stops", "lemon"),
        "csgbq 143: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 143: the processor reads the record then stops", "a"),
        "round 143: the processor reads the record then stops",
    ),
    (
        ("round 143: the processor reads the record then stops", "zz"),
        "qntmc 143: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 143: the processor reads the record then stops", "AgentU"),
        "ruyaw 143: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 143: the processor reads the record then stops", "keyboard"),
        "bssor 143: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 143: the processor reads the record then stops", "AA"),
        "round 143: the processor reads the record then stops",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "key"),
        "bssxh 143: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "lemon"),
        "csgbq 143: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "a"),
        "round 143: a worker pulls the next task from the queue",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "zz"),
        "qntmc 143: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 143: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "keyboard"),
        "bssor 143: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 143: a worker pulls the next task from the queue", "AA"),
        "round 143: a worker pulls the next task from the queue",
    ),
    (
        ("round 143: signals travel through the network layer", "key"),
        "bssxh 143: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 143: signals travel through the network layer", "lemon"),
        "csgbq 143: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 143: signals travel through the network layer", "a"),
        "round 143: signals travel through the network layer",
    ),
    (
        ("round 143: signals travel through the network layer", "zz"),
        "qntmc 143: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 143: signals travel through the network layer", "AgentU"),
        "ruyaw 143: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 143: signals travel through the network layer", "keyboard"),
        "bssor 143: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 143: signals travel through the network layer", "AA"),
        "round 143: signals travel through the network layer",
    ),
    (
        ("round 143: the gateway routes each request by policy", "key"),
        "bssxh 143: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 143: the gateway routes each request by policy", "lemon"),
        "csgbq 143: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 143: the gateway routes each request by policy", "a"),
        "round 143: the gateway routes each request by policy",
    ),
    (
        ("round 143: the gateway routes each request by policy", "zz"),
        "qntmc 143: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 143: the gateway routes each request by policy", "AgentU"),
        "ruyaw 143: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 143: the gateway routes each request by policy", "keyboard"),
        "bssor 143: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 143: the gateway routes each request by policy", "AA"),
        "round 143: the gateway routes each request by policy",
    ),
    (("round 143: memory grows until the buffer is full", "key"), "bssxh 143: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 143: memory grows until the buffer is full", "lemon"), "csgbq 143: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 143: memory grows until the buffer is full", "a"), "round 143: memory grows until the buffer is full"),
    (("round 143: memory grows until the buffer is full", "zz"), "qntmc 143: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 143: memory grows until the buffer is full", "AgentU"),
        "ruyaw 143: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 143: memory grows until the buffer is full", "keyboard"),
        "bssor 143: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 143: memory grows until the buffer is full", "AA"), "round 143: memory grows until the buffer is full"),
    (("round 143: the cluster mirrors every packet twice", "key"), "bssxh 143: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 143: the cluster mirrors every packet twice", "lemon"),
        "csgbq 143: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 143: the cluster mirrors every packet twice", "a"), "round 143: the cluster mirrors every packet twice"),
    (("round 143: the cluster mirrors every packet twice", "zz"), "qntmc 143: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 143: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 143: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 143: the cluster mirrors every packet twice", "keyboard"),
        "bssor 143: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 143: the cluster mirrors every packet twice", "AA"), "round 143: the cluster mirrors every packet twice"),
    (
        ("round 143: ranking uses tokens learned from the corpus", "key"),
        "bssxh 143: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 143: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", "a"),
        "round 143: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 143: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 143: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 143: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", "AA"),
        "round 143: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 143: a long session ends when the candle dies", "key"),
        "bssxh 143: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 143: a long session ends when the candle dies", "lemon"),
        "csgbq 143: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 143: a long session ends when the candle dies", "a"),
        "round 143: a long session ends when the candle dies",
    ),
    (
        ("round 143: a long session ends when the candle dies", "zz"),
        "qntmc 143: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 143: a long session ends when the candle dies", "AgentU"),
        "ruyaw 143: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 143: a long session ends when the candle dies", "keyboard"),
        "bssor 143: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 143: a long session ends when the candle dies", "AA"),
        "round 143: a long session ends when the candle dies",
    ),
    (("round 143: encode the prompt then map the result", "key"), "bssxh 143: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 143: encode the prompt then map the result", "lemon"), "csgbq 143: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 143: encode the prompt then map the result", "a"), "round 143: encode the prompt then map the result"),
    (("round 143: encode the prompt then map the result", "zz"), "qntmc 143: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 143: encode the prompt then map the result", "AgentU"),
        "ruyaw 143: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 143: encode the prompt then map the result", "keyboard"),
        "bssor 143: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 143: encode the prompt then map the result", "AA"), "round 143: encode the prompt then map the result"),
    (("round 143: the kernel wakes the worker at dawn", "key"), "bssxh 143: rri iovlop ukocc xfo ambocb er neux"),
    (("round 143: the kernel wakes the worker at dawn", "lemon"), "csgbq 143: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 143: the kernel wakes the worker at dawn", "a"), "round 143: the kernel wakes the worker at dawn"),
    (("round 143: the kernel wakes the worker at dawn", "zz"), "qntmc 143: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 143: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 143: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 143: the kernel wakes the worker at dawn", "keyboard"), "bssor 143: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 143: the kernel wakes the worker at dawn", "AA"), "round 143: the kernel wakes the worker at dawn"),
    (("round 143: service latency drops after the patch", "key"), "bssxh 143: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 143: service latency drops after the patch", "lemon"), "csgbq 143: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 143: service latency drops after the patch", "a"), "round 143: service latency drops after the patch"),
    (("round 143: service latency drops after the patch", "zz"), "qntmc 143: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 143: service latency drops after the patch", "AgentU"),
        "ruyaw 143: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 143: service latency drops after the patch", "keyboard"),
        "bssor 143: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 143: service latency drops after the patch", "AA"), "round 143: service latency drops after the patch"),
    (
        ("round 143: the library caches every vector it sees", "key"),
        "bssxh 143: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 143: the library caches every vector it sees", "lemon"),
        "csgbq 143: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 143: the library caches every vector it sees", "a"), "round 143: the library caches every vector it sees"),
    (
        ("round 143: the library caches every vector it sees", "zz"),
        "qntmc 143: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 143: the library caches every vector it sees", "AgentU"),
        "ruyaw 143: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 143: the library caches every vector it sees", "keyboard"),
        "bssor 143: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 143: the library caches every vector it sees", "AA"),
        "round 143: the library caches every vector it sees",
    ),
    (("round 143: agents argue then the debate resolves", "key"), "bssxh 143: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 143: agents argue then the debate resolves", "lemon"), "csgbq 143: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 143: agents argue then the debate resolves", "a"), "round 143: agents argue then the debate resolves"),
    (("round 143: agents argue then the debate resolves", "zz"), "qntmc 143: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 143: agents argue then the debate resolves", "AgentU"),
        "ruyaw 143: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 143: agents argue then the debate resolves", "keyboard"),
        "bssor 143: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 143: agents argue then the debate resolves", "AA"), "round 143: agents argue then the debate resolves"),
    (("round 143: the filter keeps only strong matches", "key"), "bssxh 143: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 143: the filter keeps only strong matches", "lemon"), "csgbq 143: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 143: the filter keeps only strong matches", "a"), "round 143: the filter keeps only strong matches"),
    (("round 143: the filter keeps only strong matches", "zz"), "qntmc 143: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 143: the filter keeps only strong matches", "AgentU"), "ruyaw 143: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 143: the filter keeps only strong matches", "keyboard"),
        "bssor 143: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 143: the filter keeps only strong matches", "AA"), "round 143: the filter keeps only strong matches"),
    (("round 143: the model answers with a short reply", "key"), "bssxh 143: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 143: the model answers with a short reply", "lemon"), "csgbq 143: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 143: the model answers with a short reply", "a"), "round 143: the model answers with a short reply"),
    (("round 143: the model answers with a short reply", "zz"), "qntmc 143: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 143: the model answers with a short reply", "AgentU"), "ruyaw 143: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 143: the model answers with a short reply", "keyboard"),
        "bssor 143: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 143: the model answers with a short reply", "AA"), "round 143: the model answers with a short reply"),
    (
        ("round 143: the recorder stores the reasoning trace", "key"),
        "bssxh 143: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 143: the recorder stores the reasoning trace", "lemon"),
        "csgbq 143: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 143: the recorder stores the reasoning trace", "a"), "round 143: the recorder stores the reasoning trace"),
    (
        ("round 143: the recorder stores the reasoning trace", "zz"),
        "qntmc 143: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 143: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 143: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 143: the recorder stores the reasoning trace", "keyboard"),
        "bssor 143: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 143: the recorder stores the reasoning trace", "AA"),
        "round 143: the recorder stores the reasoning trace",
    ),
    (("round 143: the angel watches the processor run", "key"), "bssxh 143: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 143: the angel watches the processor run", "lemon"), "csgbq 143: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 143: the angel watches the processor run", "a"), "round 143: the angel watches the processor run"),
    (("round 143: the angel watches the processor run", "zz"), "qntmc 143: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 143: the angel watches the processor run", "AgentU"), "ruyaw 143: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 143: the angel watches the processor run", "keyboard"), "bssor 143: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 143: the angel watches the processor run", "AA"), "round 143: the angel watches the processor run"),
    (("round 143: angle of the vector decides the match", "key"), "bssxh 143: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 143: angle of the vector decides the match", "lemon"), "csgbq 143: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 143: angle of the vector decides the match", "a"), "round 143: angle of the vector decides the match"),
    (("round 143: angle of the vector decides the match", "zz"), "qntmc 143: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 143: angle of the vector decides the match", "AgentU"),
        "ruyaw 143: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 143: angle of the vector decides the match", "keyboard"),
        "bssor 143: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 143: angle of the vector decides the match", "AA"), "round 143: angle of the vector decides the match"),
    (
        ("round 143: the candle burns twice as long at night", "key"),
        "bssxh 143: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 143: the candle burns twice as long at night", "lemon"),
        "csgbq 143: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 143: the candle burns twice as long at night", "a"), "round 143: the candle burns twice as long at night"),
    (
        ("round 143: the candle burns twice as long at night", "zz"),
        "qntmc 143: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 143: the candle burns twice as long at night", "AgentU"),
        "ruyaw 143: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 143: the candle burns twice as long at night", "keyboard"),
        "bssor 143: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 143: the candle burns twice as long at night", "AA"),
        "round 143: the candle burns twice as long at night",
    ),
    (("round 143: a mirror of the universe in one line", "key"), "bssxh 143: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 143: a mirror of the universe in one line", "lemon"), "csgbq 143: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 143: a mirror of the universe in one line", "a"), "round 143: a mirror of the universe in one line"),
    (("round 143: a mirror of the universe in one line", "zz"), "qntmc 143: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 143: a mirror of the universe in one line", "AgentU"), "ruyaw 143: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 143: a mirror of the universe in one line", "keyboard"),
        "bssor 143: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 143: a mirror of the universe in one line", "AA"), "round 143: a mirror of the universe in one line"),
    (("round 143: the queue drains before the storm", "key"), "bssxh 143: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 143: the queue drains before the storm", "lemon"), "csgbq 143: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 143: the queue drains before the storm", "a"), "round 143: the queue drains before the storm"),
    (("round 143: the queue drains before the storm", "zz"), "qntmc 143: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 143: the queue drains before the storm", "AgentU"), "ruyaw 143: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 143: the queue drains before the storm", "keyboard"), "bssor 143: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 143: the queue drains before the storm", "AA"), "round 143: the queue drains before the storm"),
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
