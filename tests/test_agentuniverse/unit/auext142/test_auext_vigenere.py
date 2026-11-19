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
    (("kitten142", "key"), "umrdil142"),
    (("kitten142", "lemon"), "vmfhry142"),
    (("kitten142", "a"), "kitten142"),
    (("kitten142", "zz"), "jhssdm142"),
    (("kitten142", "AgentU"), "koxgxh142"),
    (("kitten142", "keyboard"), "umrusn142"),
    (("kitten142", "AA"), "kitten142"),
    (("sitting142", "key"), "cmrdmlq142"),
    (("sitting142", "lemon"), "dmfhvyk142"),
    (("sitting142", "a"), "sitting142"),
    (("sitting142", "zz"), "rhsshmf142"),
    (("sitting142", "AgentU"), "soxgbhg142"),
    (("sitting142", "keyboard"), "cmruwnx142"),
    (("sitting142", "AA"), "sitting142"),
    (("agent142", "key"), "kkcxx142"),
    (("agent142", "lemon"), "lkqbg142"),
    (("agent142", "a"), "agent142"),
    (("agent142", "zz"), "zfdms142"),
    (("agent142", "AgentU"), "amiam142"),
    (("agent142", "keyboard"), "kkcoh142"),
    (("agent142", "AA"), "agent142"),
    (("angle142", "key"), "krevi142"),
    (("angle142", "lemon"), "lrszr142"),
    (("angle142", "a"), "angle142"),
    (("angle142", "zz"), "zmfkd142"),
    (("angle142", "AgentU"), "atkyx142"),
    (("angle142", "keyboard"), "krems142"),
    (("angle142", "AA"), "angle142"),
    (("universe142", "key"), "ergfipci142"),
    (("universe142", "lemon"), "frujrcwq142"),
    (("universe142", "a"), "universe142"),
    (("universe142", "zz"), "tmhudqrd142"),
    (("universe142", "AgentU"), "utmixlsk142"),
    (("universe142", "keyboard"), "ergwsrjh142"),
    (("universe142", "AA"), "universe142"),
    (("memory142", "key"), "wikyvw142"),
    (("memory142", "lemon"), "xiycej142"),
    (("memory142", "a"), "memory142"),
    (("memory142", "zz"), "ldlnqx142"),
    (("memory142", "AgentU"), "mkqbks142"),
    (("memory142", "keyboard"), "wikpfy142"),
    (("memory142", "AA"), "memory142"),
    (("stream142", "key"), "cxpoek142"),
    (("stream142", "lemon"), "dxdsnx142"),
    (("stream142", "a"), "stream142"),
    (("stream142", "zz"), "rsqdzl142"),
    (("stream142", "AgentU"), "szvrtg142"),
    (("stream142", "keyboard"), "cxpfom142"),
    (("stream142", "AA"), "stream142"),
    (("context142", "key"), "msldivd142"),
    (("context142", "lemon"), "nszhrix142"),
    (("context142", "a"), "context142"),
    (("context142", "zz"), "bnmsdws142"),
    (("context142", "AgentU"), "curgxrt142"),
    (("context142", "keyboard"), "mslusxk142"),
    (("context142", "AA"), "context142"),
    (("knowledge142", "key"), "urmgpcnkc142"),
    (("knowledge142", "lemon"), "vrakyphss142"),
    (("knowledge142", "a"), "knowledge142"),
    (("knowledge142", "zz"), "jmnvkdcfd142"),
    (("knowledge142", "AgentU"), "ktsjeydmi142"),
    (("knowledge142", "keyboard"), "urmxzeujo142"),
    (("knowledge142", "AA"), "knowledge142"),
    (("vector142", "key"), "fiadsp142"),
    (("vector142", "lemon"), "giohbc142"),
    (("vector142", "a"), "vector142"),
    (("vector142", "zz"), "udbsnq142"),
    (("vector142", "AgentU"), "vkgghl142"),
    (("vector142", "keyboard"), "fiaucr142"),
    (("vector142", "AA"), "vector142"),
    (("processor142", "key"), "zvmmiqcsp142"),
    (("processor142", "lemon"), "avaqrdwaf142"),
    (("processor142", "a"), "processor142"),
    (("processor142", "zz"), "oqnbdrrnq142"),
    (("processor142", "AgentU"), "pxspxmsuv142"),
    (("processor142", "keyboard"), "zvmdssjrb142"),
    (("processor142", "AA"), "processor142"),
    (("reasoning142", "key"), "biycslsre142"),
    (("reasoning142", "lemon"), "cimgbymzu142"),
    (("reasoning142", "a"), "reasoning142"),
    (("reasoning142", "zz"), "qdzrnmhmf142"),
    (("reasoning142", "AgentU"), "rkefhhitk142"),
    (("reasoning142", "keyboard"), "biytcnzqq142"),
    (("reasoning142", "AA"), "reasoning142"),
    (("machine142", "key"), "wearmlo142"),
    (("machine142", "lemon"), "xeovvyi142"),
    (("machine142", "a"), "machine142"),
    (("machine142", "zz"), "lzbghmd142"),
    (("machine142", "AgentU"), "mggubhe142"),
    (("machine142", "keyboard"), "weaiwnv142"),
    (("machine142", "AA"), "machine142"),
    (("learning142", "key"), "viybrgxk142"),
    (("learning142", "lemon"), "wimfatrs142"),
    (("learning142", "a"), "learning142"),
    (("learning142", "zz"), "kdzqmhmf142"),
    (("learning142", "AgentU"), "lkeegcnm142"),
    (("learning142", "keyboard"), "viysbiej142"),
    (("learning142", "AA"), "learning142"),
    (("model142", "key"), "wsbop142"),
    (("model142", "lemon"), "xspsy142"),
    (("model142", "a"), "model142"),
    (("model142", "zz"), "lncdk142"),
    (("model142", "AgentU"), "muhre142"),
    (("model142", "keyboard"), "wsbfz142"),
    (("model142", "AA"), "model142"),
    (("token142", "key"), "dsior142"),
    (("token142", "lemon"), "eswsa142"),
    (("token142", "a"), "token142"),
    (("token142", "zz"), "snjdm142"),
    (("token142", "AgentU"), "tuorg142"),
    (("token142", "keyboard"), "dsifb142"),
    (("token142", "AA"), "token142"),
    (("prompt142", "key"), "zvmwtr142"),
    (("prompt142", "lemon"), "avaace142"),
    (("prompt142", "a"), "prompt142"),
    (("prompt142", "zz"), "oqnlos142"),
    (("prompt142", "AgentU"), "pxszin142"),
    (("prompt142", "keyboard"), "zvmndt142"),
    (("prompt142", "AA"), "prompt142"),
    (("session142", "key"), "ciqcmmx142"),
    (("session142", "lemon"), "diegvzr142"),
    (("session142", "a"), "session142"),
    (("session142", "zz"), "rdrrhnm142"),
    (("session142", "AgentU"), "skwfbin142"),
    (("session142", "keyboard"), "ciqtwoe142"),
    (("session142", "AA"), "session142"),
    (("library142", "key"), "vmzbepi142"),
    (("library142", "lemon"), "wmnfncc142"),
    (("library142", "a"), "library142"),
    (("library142", "zz"), "khaqzqx142"),
    (("library142", "AgentU"), "lofetly142"),
    (("library142", "keyboard"), "vmzsorp142"),
    (("library142", "AA"), "library142"),
    (("service142", "key"), "cipfmao142"),
    (("service142", "lemon"), "didjvni142"),
    (("service142", "a"), "service142"),
    (("service142", "zz"), "rdquhbd142"),
    (("service142", "AgentU"), "skvibwe142"),
    (("service142", "keyboard"), "cipwwcv142"),
    (("service142", "AA"), "service142"),
    (("gateway142", "key"), "qeroayi142"),
    (("gateway142", "lemon"), "refsjlc142"),
    (("gateway142", "a"), "gateway142"),
    (("gateway142", "zz"), "fzsdvzx142"),
    (("gateway142", "AgentU"), "ggxrpuy142"),
    (("gateway142", "keyboard"), "qerfkap142"),
    (("gateway142", "AA"), "gateway142"),
    (("storage142", "key"), "cxmbeeo142"),
    (("storage142", "lemon"), "dxafnri142"),
    (("storage142", "a"), "storage142"),
    (("storage142", "zz"), "rsnqzfd142"),
    (("storage142", "AgentU"), "szsetae142"),
    (("storage142", "keyboard"), "cxmsogv142"),
    (("storage142", "AA"), "storage142"),
    (("network142", "key"), "xirgspu142"),
    (("network142", "lemon"), "yifkbco142"),
    (("network142", "a"), "network142"),
    (("network142", "zz"), "mdsvnqj142"),
    (("network142", "AgentU"), "nkxjhlk142"),
    (("network142", "keyboard"), "xirxcrb142"),
    (("network142", "AA"), "network142"),
    (("latency142", "key"), "verorai142"),
    (("latency142", "lemon"), "wefsanc142"),
    (("latency142", "a"), "latency142"),
    (("latency142", "zz"), "kzsdmbx142"),
    (("latency142", "AgentU"), "lgxrgwy142"),
    (("latency142", "keyboard"), "verfbcp142"),
    (("latency142", "AA"), "latency142"),
    (("buffer142", "key"), "lydpip142"),
    (("buffer142", "lemon"), "myrtrc142"),
    (("buffer142", "a"), "buffer142"),
    (("buffer142", "zz"), "ateedq142"),
    (("buffer142", "AgentU"), "bajsxl142"),
    (("buffer142", "keyboard"), "lydgsr142"),
    (("buffer142", "AA"), "buffer142"),
    (("queue142", "key"), "aycei142"),
    (("queue142", "lemon"), "byqir142"),
    (("queue142", "a"), "queue142"),
    (("queue142", "zz"), "ptdtd142"),
    (("queue142", "AgentU"), "qaihx142"),
    (("queue142", "keyboard"), "aycvs142"),
    (("queue142", "AA"), "queue142"),
    (("worker142", "key"), "gspuip142"),
    (("worker142", "lemon"), "hsdyrc142"),
    (("worker142", "a"), "worker142"),
    (("worker142", "zz"), "vnqjdq142"),
    (("worker142", "AgentU"), "wuvxxl142"),
    (("worker142", "keyboard"), "gsplsr142"),
    (("worker142", "AA"), "worker142"),
    (("kernel142", "key"), "uipxij142"),
    (("kernel142", "lemon"), "vidbrw142"),
    (("kernel142", "a"), "kernel142"),
    (("kernel142", "zz"), "jdqmdk142"),
    (("kernel142", "AgentU"), "kkvaxf142"),
    (("kernel142", "keyboard"), "uiposl142"),
    (("kernel142", "AA"), "kernel142"),
    (("signal142", "key"), "cmexej142"),
    (("signal142", "lemon"), "dmsbnw142"),
    (("signal142", "a"), "signal142"),
    (("signal142", "zz"), "rhfmzk142"),
    (("signal142", "AgentU"), "sokatf142"),
    (("signal142", "keyboard"), "cmeool142"),
    (("signal142", "AA"), "signal142"),
    (("packet142", "key"), "zeauir142"),
    (("packet142", "lemon"), "aeoyre142"),
    (("packet142", "a"), "packet142"),
    (("packet142", "zz"), "ozbjds142"),
    (("packet142", "AgentU"), "pggxxn142"),
    (("packet142", "keyboard"), "zealst142"),
    (("packet142", "AA"), "packet142"),
    (("router142", "key"), "bssdip142"),
    (("router142", "lemon"), "csghrc142"),
    (("router142", "a"), "router142"),
    (("router142", "zz"), "qntsdq142"),
    (("router142", "AgentU"), "ruygxl142"),
    (("router142", "keyboard"), "bssusr142"),
    (("router142", "AA"), "router142"),
    (("cluster142", "key"), "mpscxcb142"),
    (("cluster142", "lemon"), "npgggpv142"),
    (("cluster142", "a"), "cluster142"),
    (("cluster142", "zz"), "bktrsdq142"),
    (("cluster142", "AgentU"), "cryfmyr142"),
    (("cluster142", "keyboard"), "mpsthei142"),
    (("cluster142", "AA"), "cluster142"),
    (("mirror142", "key"), "wmpbsp142"),
    (("mirror142", "lemon"), "xmdfbc142"),
    (("mirror142", "a"), "mirror142"),
    (("mirror142", "zz"), "lhqqnq142"),
    (("mirror142", "AgentU"), "movehl142"),
    (("mirror142", "keyboard"), "wmpscr142"),
    (("mirror142", "AA"), "mirror142"),
    (("filter142", "key"), "pmjdip142"),
    (("filter142", "lemon"), "qmxhrc142"),
    (("filter142", "a"), "filter142"),
    (("filter142", "zz"), "ehksdq142"),
    (("filter142", "AgentU"), "fopgxl142"),
    (("filter142", "keyboard"), "pmjusr142"),
    (("filter142", "AA"), "filter142"),
    (("ranking142", "key"), "belumlq142"),
    (("ranking142", "lemon"), "cezyvyk142"),
    (("ranking142", "a"), "ranking142"),
    (("ranking142", "zz"), "qzmjhmf142"),
    (("ranking142", "AgentU"), "rgrxbhg142"),
    (("ranking142", "keyboard"), "bellwnx142"),
    (("ranking142", "AA"), "ranking142"),
    (("encoding142", "key"), "orayhgxk142"),
    (("encoding142", "lemon"), "procqtrs142"),
    (("encoding142", "a"), "encoding142"),
    (("encoding142", "zz"), "dmbnchmf142"),
    (("encoding142", "AgentU"), "etgbwcnm142"),
    (("encoding142", "keyboard"), "orapriej142"),
    (("encoding142", "AA"), "encoding142"),
    (("mapping142", "key"), "wenzmlq142"),
    (("mapping142", "lemon"), "xebdvyk142"),
    (("mapping142", "a"), "mapping142"),
    (("mapping142", "zz"), "lzoohmf142"),
    (("mapping142", "AgentU"), "mgtcbhg142"),
    (("mapping142", "keyboard"), "wenqwnx142"),
    (("mapping142", "AA"), "mapping142"),
    (("record142", "key"), "biayvb142"),
    (("record142", "lemon"), "cioceo142"),
    (("record142", "a"), "record142"),
    (("record142", "zz"), "qdbnqc142"),
    (("record142", "AgentU"), "rkgbkx142"),
    (("record142", "keyboard"), "biapfd142"),
    (("record142", "AA"), "record142"),
    (("candle142", "key"), "melnpc142"),
    (("candle142", "lemon"), "nezryp142"),
    (("candle142", "a"), "candle142"),
    (("candle142", "zz"), "bzmckd142"),
    (("candle142", "AgentU"), "cgrqey142"),
    (("candle142", "keyboard"), "meleze142"),
    (("candle142", "AA"), "candle142"),
    (("thread142", "key"), "dlpoeb142"),
    (("thread142", "lemon"), "eldsno142"),
    (("thread142", "a"), "thread142"),
    (("thread142", "zz"), "sgqdzc142"),
    (("thread142", "AgentU"), "tnvrtx142"),
    (("thread142", "keyboard"), "dlpfod142"),
    (("thread142", "AA"), "thread142"),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 142: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 142: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "a"),
        "round 142: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 142: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 142: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 142: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", "AA"),
        "round 142: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "key"),
        "bssxh 142: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 142: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "a"),
        "round 142: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 142: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 142: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 142: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", "AA"),
        "round 142: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 142: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 142: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "a"),
        "round 142: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 142: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 142: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 142: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", "AA"),
        "round 142: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 142: the processor reads the record then stops", "key"),
        "bssxh 142: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 142: the processor reads the record then stops", "lemon"),
        "csgbq 142: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 142: the processor reads the record then stops", "a"),
        "round 142: the processor reads the record then stops",
    ),
    (
        ("round 142: the processor reads the record then stops", "zz"),
        "qntmc 142: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 142: the processor reads the record then stops", "AgentU"),
        "ruyaw 142: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 142: the processor reads the record then stops", "keyboard"),
        "bssor 142: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 142: the processor reads the record then stops", "AA"),
        "round 142: the processor reads the record then stops",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "key"),
        "bssxh 142: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "lemon"),
        "csgbq 142: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "a"),
        "round 142: a worker pulls the next task from the queue",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "zz"),
        "qntmc 142: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 142: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "keyboard"),
        "bssor 142: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 142: a worker pulls the next task from the queue", "AA"),
        "round 142: a worker pulls the next task from the queue",
    ),
    (
        ("round 142: signals travel through the network layer", "key"),
        "bssxh 142: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 142: signals travel through the network layer", "lemon"),
        "csgbq 142: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 142: signals travel through the network layer", "a"),
        "round 142: signals travel through the network layer",
    ),
    (
        ("round 142: signals travel through the network layer", "zz"),
        "qntmc 142: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 142: signals travel through the network layer", "AgentU"),
        "ruyaw 142: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 142: signals travel through the network layer", "keyboard"),
        "bssor 142: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 142: signals travel through the network layer", "AA"),
        "round 142: signals travel through the network layer",
    ),
    (
        ("round 142: the gateway routes each request by policy", "key"),
        "bssxh 142: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 142: the gateway routes each request by policy", "lemon"),
        "csgbq 142: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 142: the gateway routes each request by policy", "a"),
        "round 142: the gateway routes each request by policy",
    ),
    (
        ("round 142: the gateway routes each request by policy", "zz"),
        "qntmc 142: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 142: the gateway routes each request by policy", "AgentU"),
        "ruyaw 142: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 142: the gateway routes each request by policy", "keyboard"),
        "bssor 142: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 142: the gateway routes each request by policy", "AA"),
        "round 142: the gateway routes each request by policy",
    ),
    (("round 142: memory grows until the buffer is full", "key"), "bssxh 142: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 142: memory grows until the buffer is full", "lemon"), "csgbq 142: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 142: memory grows until the buffer is full", "a"), "round 142: memory grows until the buffer is full"),
    (("round 142: memory grows until the buffer is full", "zz"), "qntmc 142: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 142: memory grows until the buffer is full", "AgentU"),
        "ruyaw 142: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 142: memory grows until the buffer is full", "keyboard"),
        "bssor 142: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 142: memory grows until the buffer is full", "AA"), "round 142: memory grows until the buffer is full"),
    (("round 142: the cluster mirrors every packet twice", "key"), "bssxh 142: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 142: the cluster mirrors every packet twice", "lemon"),
        "csgbq 142: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 142: the cluster mirrors every packet twice", "a"), "round 142: the cluster mirrors every packet twice"),
    (("round 142: the cluster mirrors every packet twice", "zz"), "qntmc 142: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 142: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 142: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 142: the cluster mirrors every packet twice", "keyboard"),
        "bssor 142: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 142: the cluster mirrors every packet twice", "AA"), "round 142: the cluster mirrors every packet twice"),
    (
        ("round 142: ranking uses tokens learned from the corpus", "key"),
        "bssxh 142: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 142: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", "a"),
        "round 142: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 142: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 142: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 142: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", "AA"),
        "round 142: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 142: a long session ends when the candle dies", "key"),
        "bssxh 142: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 142: a long session ends when the candle dies", "lemon"),
        "csgbq 142: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 142: a long session ends when the candle dies", "a"),
        "round 142: a long session ends when the candle dies",
    ),
    (
        ("round 142: a long session ends when the candle dies", "zz"),
        "qntmc 142: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 142: a long session ends when the candle dies", "AgentU"),
        "ruyaw 142: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 142: a long session ends when the candle dies", "keyboard"),
        "bssor 142: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 142: a long session ends when the candle dies", "AA"),
        "round 142: a long session ends when the candle dies",
    ),
    (("round 142: encode the prompt then map the result", "key"), "bssxh 142: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 142: encode the prompt then map the result", "lemon"), "csgbq 142: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 142: encode the prompt then map the result", "a"), "round 142: encode the prompt then map the result"),
    (("round 142: encode the prompt then map the result", "zz"), "qntmc 142: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 142: encode the prompt then map the result", "AgentU"),
        "ruyaw 142: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 142: encode the prompt then map the result", "keyboard"),
        "bssor 142: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 142: encode the prompt then map the result", "AA"), "round 142: encode the prompt then map the result"),
    (("round 142: the kernel wakes the worker at dawn", "key"), "bssxh 142: rri iovlop ukocc xfo ambocb er neux"),
    (("round 142: the kernel wakes the worker at dawn", "lemon"), "csgbq 142: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 142: the kernel wakes the worker at dawn", "a"), "round 142: the kernel wakes the worker at dawn"),
    (("round 142: the kernel wakes the worker at dawn", "zz"), "qntmc 142: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 142: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 142: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 142: the kernel wakes the worker at dawn", "keyboard"), "bssor 142: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 142: the kernel wakes the worker at dawn", "AA"), "round 142: the kernel wakes the worker at dawn"),
    (("round 142: service latency drops after the patch", "key"), "bssxh 142: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 142: service latency drops after the patch", "lemon"), "csgbq 142: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 142: service latency drops after the patch", "a"), "round 142: service latency drops after the patch"),
    (("round 142: service latency drops after the patch", "zz"), "qntmc 142: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 142: service latency drops after the patch", "AgentU"),
        "ruyaw 142: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 142: service latency drops after the patch", "keyboard"),
        "bssor 142: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 142: service latency drops after the patch", "AA"), "round 142: service latency drops after the patch"),
    (
        ("round 142: the library caches every vector it sees", "key"),
        "bssxh 142: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 142: the library caches every vector it sees", "lemon"),
        "csgbq 142: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 142: the library caches every vector it sees", "a"), "round 142: the library caches every vector it sees"),
    (
        ("round 142: the library caches every vector it sees", "zz"),
        "qntmc 142: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 142: the library caches every vector it sees", "AgentU"),
        "ruyaw 142: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 142: the library caches every vector it sees", "keyboard"),
        "bssor 142: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 142: the library caches every vector it sees", "AA"),
        "round 142: the library caches every vector it sees",
    ),
    (("round 142: agents argue then the debate resolves", "key"), "bssxh 142: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 142: agents argue then the debate resolves", "lemon"), "csgbq 142: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 142: agents argue then the debate resolves", "a"), "round 142: agents argue then the debate resolves"),
    (("round 142: agents argue then the debate resolves", "zz"), "qntmc 142: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 142: agents argue then the debate resolves", "AgentU"),
        "ruyaw 142: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 142: agents argue then the debate resolves", "keyboard"),
        "bssor 142: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 142: agents argue then the debate resolves", "AA"), "round 142: agents argue then the debate resolves"),
    (("round 142: the filter keeps only strong matches", "key"), "bssxh 142: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 142: the filter keeps only strong matches", "lemon"), "csgbq 142: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 142: the filter keeps only strong matches", "a"), "round 142: the filter keeps only strong matches"),
    (("round 142: the filter keeps only strong matches", "zz"), "qntmc 142: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 142: the filter keeps only strong matches", "AgentU"), "ruyaw 142: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 142: the filter keeps only strong matches", "keyboard"),
        "bssor 142: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 142: the filter keeps only strong matches", "AA"), "round 142: the filter keeps only strong matches"),
    (("round 142: the model answers with a short reply", "key"), "bssxh 142: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 142: the model answers with a short reply", "lemon"), "csgbq 142: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 142: the model answers with a short reply", "a"), "round 142: the model answers with a short reply"),
    (("round 142: the model answers with a short reply", "zz"), "qntmc 142: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 142: the model answers with a short reply", "AgentU"), "ruyaw 142: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 142: the model answers with a short reply", "keyboard"),
        "bssor 142: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 142: the model answers with a short reply", "AA"), "round 142: the model answers with a short reply"),
    (
        ("round 142: the recorder stores the reasoning trace", "key"),
        "bssxh 142: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 142: the recorder stores the reasoning trace", "lemon"),
        "csgbq 142: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 142: the recorder stores the reasoning trace", "a"), "round 142: the recorder stores the reasoning trace"),
    (
        ("round 142: the recorder stores the reasoning trace", "zz"),
        "qntmc 142: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 142: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 142: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 142: the recorder stores the reasoning trace", "keyboard"),
        "bssor 142: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 142: the recorder stores the reasoning trace", "AA"),
        "round 142: the recorder stores the reasoning trace",
    ),
    (("round 142: the angel watches the processor run", "key"), "bssxh 142: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 142: the angel watches the processor run", "lemon"), "csgbq 142: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 142: the angel watches the processor run", "a"), "round 142: the angel watches the processor run"),
    (("round 142: the angel watches the processor run", "zz"), "qntmc 142: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 142: the angel watches the processor run", "AgentU"), "ruyaw 142: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 142: the angel watches the processor run", "keyboard"), "bssor 142: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 142: the angel watches the processor run", "AA"), "round 142: the angel watches the processor run"),
    (("round 142: angle of the vector decides the match", "key"), "bssxh 142: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 142: angle of the vector decides the match", "lemon"), "csgbq 142: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 142: angle of the vector decides the match", "a"), "round 142: angle of the vector decides the match"),
    (("round 142: angle of the vector decides the match", "zz"), "qntmc 142: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 142: angle of the vector decides the match", "AgentU"),
        "ruyaw 142: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 142: angle of the vector decides the match", "keyboard"),
        "bssor 142: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 142: angle of the vector decides the match", "AA"), "round 142: angle of the vector decides the match"),
    (
        ("round 142: the candle burns twice as long at night", "key"),
        "bssxh 142: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 142: the candle burns twice as long at night", "lemon"),
        "csgbq 142: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 142: the candle burns twice as long at night", "a"), "round 142: the candle burns twice as long at night"),
    (
        ("round 142: the candle burns twice as long at night", "zz"),
        "qntmc 142: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 142: the candle burns twice as long at night", "AgentU"),
        "ruyaw 142: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 142: the candle burns twice as long at night", "keyboard"),
        "bssor 142: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 142: the candle burns twice as long at night", "AA"),
        "round 142: the candle burns twice as long at night",
    ),
    (("round 142: a mirror of the universe in one line", "key"), "bssxh 142: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 142: a mirror of the universe in one line", "lemon"), "csgbq 142: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 142: a mirror of the universe in one line", "a"), "round 142: a mirror of the universe in one line"),
    (("round 142: a mirror of the universe in one line", "zz"), "qntmc 142: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 142: a mirror of the universe in one line", "AgentU"), "ruyaw 142: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 142: a mirror of the universe in one line", "keyboard"),
        "bssor 142: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 142: a mirror of the universe in one line", "AA"), "round 142: a mirror of the universe in one line"),
    (("round 142: the queue drains before the storm", "key"), "bssxh 142: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 142: the queue drains before the storm", "lemon"), "csgbq 142: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 142: the queue drains before the storm", "a"), "round 142: the queue drains before the storm"),
    (("round 142: the queue drains before the storm", "zz"), "qntmc 142: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 142: the queue drains before the storm", "AgentU"), "ruyaw 142: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 142: the queue drains before the storm", "keyboard"), "bssor 142: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 142: the queue drains before the storm", "AA"), "round 142: the queue drains before the storm"),
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
