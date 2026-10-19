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
    (("kitten115", "key"), "umrdil115"),
    (("kitten115", "lemon"), "vmfhry115"),
    (("kitten115", "a"), "kitten115"),
    (("kitten115", "zz"), "jhssdm115"),
    (("kitten115", "AgentU"), "koxgxh115"),
    (("kitten115", "keyboard"), "umrusn115"),
    (("kitten115", "AA"), "kitten115"),
    (("sitting115", "key"), "cmrdmlq115"),
    (("sitting115", "lemon"), "dmfhvyk115"),
    (("sitting115", "a"), "sitting115"),
    (("sitting115", "zz"), "rhsshmf115"),
    (("sitting115", "AgentU"), "soxgbhg115"),
    (("sitting115", "keyboard"), "cmruwnx115"),
    (("sitting115", "AA"), "sitting115"),
    (("agent115", "key"), "kkcxx115"),
    (("agent115", "lemon"), "lkqbg115"),
    (("agent115", "a"), "agent115"),
    (("agent115", "zz"), "zfdms115"),
    (("agent115", "AgentU"), "amiam115"),
    (("agent115", "keyboard"), "kkcoh115"),
    (("agent115", "AA"), "agent115"),
    (("angle115", "key"), "krevi115"),
    (("angle115", "lemon"), "lrszr115"),
    (("angle115", "a"), "angle115"),
    (("angle115", "zz"), "zmfkd115"),
    (("angle115", "AgentU"), "atkyx115"),
    (("angle115", "keyboard"), "krems115"),
    (("angle115", "AA"), "angle115"),
    (("universe115", "key"), "ergfipci115"),
    (("universe115", "lemon"), "frujrcwq115"),
    (("universe115", "a"), "universe115"),
    (("universe115", "zz"), "tmhudqrd115"),
    (("universe115", "AgentU"), "utmixlsk115"),
    (("universe115", "keyboard"), "ergwsrjh115"),
    (("universe115", "AA"), "universe115"),
    (("memory115", "key"), "wikyvw115"),
    (("memory115", "lemon"), "xiycej115"),
    (("memory115", "a"), "memory115"),
    (("memory115", "zz"), "ldlnqx115"),
    (("memory115", "AgentU"), "mkqbks115"),
    (("memory115", "keyboard"), "wikpfy115"),
    (("memory115", "AA"), "memory115"),
    (("stream115", "key"), "cxpoek115"),
    (("stream115", "lemon"), "dxdsnx115"),
    (("stream115", "a"), "stream115"),
    (("stream115", "zz"), "rsqdzl115"),
    (("stream115", "AgentU"), "szvrtg115"),
    (("stream115", "keyboard"), "cxpfom115"),
    (("stream115", "AA"), "stream115"),
    (("context115", "key"), "msldivd115"),
    (("context115", "lemon"), "nszhrix115"),
    (("context115", "a"), "context115"),
    (("context115", "zz"), "bnmsdws115"),
    (("context115", "AgentU"), "curgxrt115"),
    (("context115", "keyboard"), "mslusxk115"),
    (("context115", "AA"), "context115"),
    (("knowledge115", "key"), "urmgpcnkc115"),
    (("knowledge115", "lemon"), "vrakyphss115"),
    (("knowledge115", "a"), "knowledge115"),
    (("knowledge115", "zz"), "jmnvkdcfd115"),
    (("knowledge115", "AgentU"), "ktsjeydmi115"),
    (("knowledge115", "keyboard"), "urmxzeujo115"),
    (("knowledge115", "AA"), "knowledge115"),
    (("vector115", "key"), "fiadsp115"),
    (("vector115", "lemon"), "giohbc115"),
    (("vector115", "a"), "vector115"),
    (("vector115", "zz"), "udbsnq115"),
    (("vector115", "AgentU"), "vkgghl115"),
    (("vector115", "keyboard"), "fiaucr115"),
    (("vector115", "AA"), "vector115"),
    (("processor115", "key"), "zvmmiqcsp115"),
    (("processor115", "lemon"), "avaqrdwaf115"),
    (("processor115", "a"), "processor115"),
    (("processor115", "zz"), "oqnbdrrnq115"),
    (("processor115", "AgentU"), "pxspxmsuv115"),
    (("processor115", "keyboard"), "zvmdssjrb115"),
    (("processor115", "AA"), "processor115"),
    (("reasoning115", "key"), "biycslsre115"),
    (("reasoning115", "lemon"), "cimgbymzu115"),
    (("reasoning115", "a"), "reasoning115"),
    (("reasoning115", "zz"), "qdzrnmhmf115"),
    (("reasoning115", "AgentU"), "rkefhhitk115"),
    (("reasoning115", "keyboard"), "biytcnzqq115"),
    (("reasoning115", "AA"), "reasoning115"),
    (("machine115", "key"), "wearmlo115"),
    (("machine115", "lemon"), "xeovvyi115"),
    (("machine115", "a"), "machine115"),
    (("machine115", "zz"), "lzbghmd115"),
    (("machine115", "AgentU"), "mggubhe115"),
    (("machine115", "keyboard"), "weaiwnv115"),
    (("machine115", "AA"), "machine115"),
    (("learning115", "key"), "viybrgxk115"),
    (("learning115", "lemon"), "wimfatrs115"),
    (("learning115", "a"), "learning115"),
    (("learning115", "zz"), "kdzqmhmf115"),
    (("learning115", "AgentU"), "lkeegcnm115"),
    (("learning115", "keyboard"), "viysbiej115"),
    (("learning115", "AA"), "learning115"),
    (("model115", "key"), "wsbop115"),
    (("model115", "lemon"), "xspsy115"),
    (("model115", "a"), "model115"),
    (("model115", "zz"), "lncdk115"),
    (("model115", "AgentU"), "muhre115"),
    (("model115", "keyboard"), "wsbfz115"),
    (("model115", "AA"), "model115"),
    (("token115", "key"), "dsior115"),
    (("token115", "lemon"), "eswsa115"),
    (("token115", "a"), "token115"),
    (("token115", "zz"), "snjdm115"),
    (("token115", "AgentU"), "tuorg115"),
    (("token115", "keyboard"), "dsifb115"),
    (("token115", "AA"), "token115"),
    (("prompt115", "key"), "zvmwtr115"),
    (("prompt115", "lemon"), "avaace115"),
    (("prompt115", "a"), "prompt115"),
    (("prompt115", "zz"), "oqnlos115"),
    (("prompt115", "AgentU"), "pxszin115"),
    (("prompt115", "keyboard"), "zvmndt115"),
    (("prompt115", "AA"), "prompt115"),
    (("session115", "key"), "ciqcmmx115"),
    (("session115", "lemon"), "diegvzr115"),
    (("session115", "a"), "session115"),
    (("session115", "zz"), "rdrrhnm115"),
    (("session115", "AgentU"), "skwfbin115"),
    (("session115", "keyboard"), "ciqtwoe115"),
    (("session115", "AA"), "session115"),
    (("library115", "key"), "vmzbepi115"),
    (("library115", "lemon"), "wmnfncc115"),
    (("library115", "a"), "library115"),
    (("library115", "zz"), "khaqzqx115"),
    (("library115", "AgentU"), "lofetly115"),
    (("library115", "keyboard"), "vmzsorp115"),
    (("library115", "AA"), "library115"),
    (("service115", "key"), "cipfmao115"),
    (("service115", "lemon"), "didjvni115"),
    (("service115", "a"), "service115"),
    (("service115", "zz"), "rdquhbd115"),
    (("service115", "AgentU"), "skvibwe115"),
    (("service115", "keyboard"), "cipwwcv115"),
    (("service115", "AA"), "service115"),
    (("gateway115", "key"), "qeroayi115"),
    (("gateway115", "lemon"), "refsjlc115"),
    (("gateway115", "a"), "gateway115"),
    (("gateway115", "zz"), "fzsdvzx115"),
    (("gateway115", "AgentU"), "ggxrpuy115"),
    (("gateway115", "keyboard"), "qerfkap115"),
    (("gateway115", "AA"), "gateway115"),
    (("storage115", "key"), "cxmbeeo115"),
    (("storage115", "lemon"), "dxafnri115"),
    (("storage115", "a"), "storage115"),
    (("storage115", "zz"), "rsnqzfd115"),
    (("storage115", "AgentU"), "szsetae115"),
    (("storage115", "keyboard"), "cxmsogv115"),
    (("storage115", "AA"), "storage115"),
    (("network115", "key"), "xirgspu115"),
    (("network115", "lemon"), "yifkbco115"),
    (("network115", "a"), "network115"),
    (("network115", "zz"), "mdsvnqj115"),
    (("network115", "AgentU"), "nkxjhlk115"),
    (("network115", "keyboard"), "xirxcrb115"),
    (("network115", "AA"), "network115"),
    (("latency115", "key"), "verorai115"),
    (("latency115", "lemon"), "wefsanc115"),
    (("latency115", "a"), "latency115"),
    (("latency115", "zz"), "kzsdmbx115"),
    (("latency115", "AgentU"), "lgxrgwy115"),
    (("latency115", "keyboard"), "verfbcp115"),
    (("latency115", "AA"), "latency115"),
    (("buffer115", "key"), "lydpip115"),
    (("buffer115", "lemon"), "myrtrc115"),
    (("buffer115", "a"), "buffer115"),
    (("buffer115", "zz"), "ateedq115"),
    (("buffer115", "AgentU"), "bajsxl115"),
    (("buffer115", "keyboard"), "lydgsr115"),
    (("buffer115", "AA"), "buffer115"),
    (("queue115", "key"), "aycei115"),
    (("queue115", "lemon"), "byqir115"),
    (("queue115", "a"), "queue115"),
    (("queue115", "zz"), "ptdtd115"),
    (("queue115", "AgentU"), "qaihx115"),
    (("queue115", "keyboard"), "aycvs115"),
    (("queue115", "AA"), "queue115"),
    (("worker115", "key"), "gspuip115"),
    (("worker115", "lemon"), "hsdyrc115"),
    (("worker115", "a"), "worker115"),
    (("worker115", "zz"), "vnqjdq115"),
    (("worker115", "AgentU"), "wuvxxl115"),
    (("worker115", "keyboard"), "gsplsr115"),
    (("worker115", "AA"), "worker115"),
    (("kernel115", "key"), "uipxij115"),
    (("kernel115", "lemon"), "vidbrw115"),
    (("kernel115", "a"), "kernel115"),
    (("kernel115", "zz"), "jdqmdk115"),
    (("kernel115", "AgentU"), "kkvaxf115"),
    (("kernel115", "keyboard"), "uiposl115"),
    (("kernel115", "AA"), "kernel115"),
    (("signal115", "key"), "cmexej115"),
    (("signal115", "lemon"), "dmsbnw115"),
    (("signal115", "a"), "signal115"),
    (("signal115", "zz"), "rhfmzk115"),
    (("signal115", "AgentU"), "sokatf115"),
    (("signal115", "keyboard"), "cmeool115"),
    (("signal115", "AA"), "signal115"),
    (("packet115", "key"), "zeauir115"),
    (("packet115", "lemon"), "aeoyre115"),
    (("packet115", "a"), "packet115"),
    (("packet115", "zz"), "ozbjds115"),
    (("packet115", "AgentU"), "pggxxn115"),
    (("packet115", "keyboard"), "zealst115"),
    (("packet115", "AA"), "packet115"),
    (("router115", "key"), "bssdip115"),
    (("router115", "lemon"), "csghrc115"),
    (("router115", "a"), "router115"),
    (("router115", "zz"), "qntsdq115"),
    (("router115", "AgentU"), "ruygxl115"),
    (("router115", "keyboard"), "bssusr115"),
    (("router115", "AA"), "router115"),
    (("cluster115", "key"), "mpscxcb115"),
    (("cluster115", "lemon"), "npgggpv115"),
    (("cluster115", "a"), "cluster115"),
    (("cluster115", "zz"), "bktrsdq115"),
    (("cluster115", "AgentU"), "cryfmyr115"),
    (("cluster115", "keyboard"), "mpsthei115"),
    (("cluster115", "AA"), "cluster115"),
    (("mirror115", "key"), "wmpbsp115"),
    (("mirror115", "lemon"), "xmdfbc115"),
    (("mirror115", "a"), "mirror115"),
    (("mirror115", "zz"), "lhqqnq115"),
    (("mirror115", "AgentU"), "movehl115"),
    (("mirror115", "keyboard"), "wmpscr115"),
    (("mirror115", "AA"), "mirror115"),
    (("filter115", "key"), "pmjdip115"),
    (("filter115", "lemon"), "qmxhrc115"),
    (("filter115", "a"), "filter115"),
    (("filter115", "zz"), "ehksdq115"),
    (("filter115", "AgentU"), "fopgxl115"),
    (("filter115", "keyboard"), "pmjusr115"),
    (("filter115", "AA"), "filter115"),
    (("ranking115", "key"), "belumlq115"),
    (("ranking115", "lemon"), "cezyvyk115"),
    (("ranking115", "a"), "ranking115"),
    (("ranking115", "zz"), "qzmjhmf115"),
    (("ranking115", "AgentU"), "rgrxbhg115"),
    (("ranking115", "keyboard"), "bellwnx115"),
    (("ranking115", "AA"), "ranking115"),
    (("encoding115", "key"), "orayhgxk115"),
    (("encoding115", "lemon"), "procqtrs115"),
    (("encoding115", "a"), "encoding115"),
    (("encoding115", "zz"), "dmbnchmf115"),
    (("encoding115", "AgentU"), "etgbwcnm115"),
    (("encoding115", "keyboard"), "orapriej115"),
    (("encoding115", "AA"), "encoding115"),
    (("mapping115", "key"), "wenzmlq115"),
    (("mapping115", "lemon"), "xebdvyk115"),
    (("mapping115", "a"), "mapping115"),
    (("mapping115", "zz"), "lzoohmf115"),
    (("mapping115", "AgentU"), "mgtcbhg115"),
    (("mapping115", "keyboard"), "wenqwnx115"),
    (("mapping115", "AA"), "mapping115"),
    (("record115", "key"), "biayvb115"),
    (("record115", "lemon"), "cioceo115"),
    (("record115", "a"), "record115"),
    (("record115", "zz"), "qdbnqc115"),
    (("record115", "AgentU"), "rkgbkx115"),
    (("record115", "keyboard"), "biapfd115"),
    (("record115", "AA"), "record115"),
    (("candle115", "key"), "melnpc115"),
    (("candle115", "lemon"), "nezryp115"),
    (("candle115", "a"), "candle115"),
    (("candle115", "zz"), "bzmckd115"),
    (("candle115", "AgentU"), "cgrqey115"),
    (("candle115", "keyboard"), "meleze115"),
    (("candle115", "AA"), "candle115"),
    (("thread115", "key"), "dlpoeb115"),
    (("thread115", "lemon"), "eldsno115"),
    (("thread115", "a"), "thread115"),
    (("thread115", "zz"), "sgqdzc115"),
    (("thread115", "AgentU"), "tnvrtx115"),
    (("thread115", "keyboard"), "dlpfod115"),
    (("thread115", "AA"), "thread115"),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 115: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 115: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "a"),
        "round 115: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 115: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 115: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 115: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", "AA"),
        "round 115: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "key"),
        "bssxh 115: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 115: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "a"),
        "round 115: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 115: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 115: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 115: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", "AA"),
        "round 115: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 115: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 115: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "a"),
        "round 115: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 115: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 115: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 115: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", "AA"),
        "round 115: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 115: the processor reads the record then stops", "key"),
        "bssxh 115: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 115: the processor reads the record then stops", "lemon"),
        "csgbq 115: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 115: the processor reads the record then stops", "a"),
        "round 115: the processor reads the record then stops",
    ),
    (
        ("round 115: the processor reads the record then stops", "zz"),
        "qntmc 115: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 115: the processor reads the record then stops", "AgentU"),
        "ruyaw 115: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 115: the processor reads the record then stops", "keyboard"),
        "bssor 115: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 115: the processor reads the record then stops", "AA"),
        "round 115: the processor reads the record then stops",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "key"),
        "bssxh 115: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "lemon"),
        "csgbq 115: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "a"),
        "round 115: a worker pulls the next task from the queue",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "zz"),
        "qntmc 115: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 115: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "keyboard"),
        "bssor 115: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 115: a worker pulls the next task from the queue", "AA"),
        "round 115: a worker pulls the next task from the queue",
    ),
    (
        ("round 115: signals travel through the network layer", "key"),
        "bssxh 115: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 115: signals travel through the network layer", "lemon"),
        "csgbq 115: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 115: signals travel through the network layer", "a"),
        "round 115: signals travel through the network layer",
    ),
    (
        ("round 115: signals travel through the network layer", "zz"),
        "qntmc 115: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 115: signals travel through the network layer", "AgentU"),
        "ruyaw 115: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 115: signals travel through the network layer", "keyboard"),
        "bssor 115: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 115: signals travel through the network layer", "AA"),
        "round 115: signals travel through the network layer",
    ),
    (
        ("round 115: the gateway routes each request by policy", "key"),
        "bssxh 115: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 115: the gateway routes each request by policy", "lemon"),
        "csgbq 115: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 115: the gateway routes each request by policy", "a"),
        "round 115: the gateway routes each request by policy",
    ),
    (
        ("round 115: the gateway routes each request by policy", "zz"),
        "qntmc 115: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 115: the gateway routes each request by policy", "AgentU"),
        "ruyaw 115: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 115: the gateway routes each request by policy", "keyboard"),
        "bssor 115: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 115: the gateway routes each request by policy", "AA"),
        "round 115: the gateway routes each request by policy",
    ),
    (("round 115: memory grows until the buffer is full", "key"), "bssxh 115: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 115: memory grows until the buffer is full", "lemon"), "csgbq 115: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 115: memory grows until the buffer is full", "a"), "round 115: memory grows until the buffer is full"),
    (("round 115: memory grows until the buffer is full", "zz"), "qntmc 115: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 115: memory grows until the buffer is full", "AgentU"),
        "ruyaw 115: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 115: memory grows until the buffer is full", "keyboard"),
        "bssor 115: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 115: memory grows until the buffer is full", "AA"), "round 115: memory grows until the buffer is full"),
    (("round 115: the cluster mirrors every packet twice", "key"), "bssxh 115: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 115: the cluster mirrors every packet twice", "lemon"),
        "csgbq 115: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 115: the cluster mirrors every packet twice", "a"), "round 115: the cluster mirrors every packet twice"),
    (("round 115: the cluster mirrors every packet twice", "zz"), "qntmc 115: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 115: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 115: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 115: the cluster mirrors every packet twice", "keyboard"),
        "bssor 115: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 115: the cluster mirrors every packet twice", "AA"), "round 115: the cluster mirrors every packet twice"),
    (
        ("round 115: ranking uses tokens learned from the corpus", "key"),
        "bssxh 115: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 115: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", "a"),
        "round 115: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 115: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 115: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 115: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", "AA"),
        "round 115: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 115: a long session ends when the candle dies", "key"),
        "bssxh 115: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 115: a long session ends when the candle dies", "lemon"),
        "csgbq 115: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 115: a long session ends when the candle dies", "a"),
        "round 115: a long session ends when the candle dies",
    ),
    (
        ("round 115: a long session ends when the candle dies", "zz"),
        "qntmc 115: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 115: a long session ends when the candle dies", "AgentU"),
        "ruyaw 115: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 115: a long session ends when the candle dies", "keyboard"),
        "bssor 115: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 115: a long session ends when the candle dies", "AA"),
        "round 115: a long session ends when the candle dies",
    ),
    (("round 115: encode the prompt then map the result", "key"), "bssxh 115: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 115: encode the prompt then map the result", "lemon"), "csgbq 115: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 115: encode the prompt then map the result", "a"), "round 115: encode the prompt then map the result"),
    (("round 115: encode the prompt then map the result", "zz"), "qntmc 115: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 115: encode the prompt then map the result", "AgentU"),
        "ruyaw 115: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 115: encode the prompt then map the result", "keyboard"),
        "bssor 115: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 115: encode the prompt then map the result", "AA"), "round 115: encode the prompt then map the result"),
    (("round 115: the kernel wakes the worker at dawn", "key"), "bssxh 115: rri iovlop ukocc xfo ambocb er neux"),
    (("round 115: the kernel wakes the worker at dawn", "lemon"), "csgbq 115: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 115: the kernel wakes the worker at dawn", "a"), "round 115: the kernel wakes the worker at dawn"),
    (("round 115: the kernel wakes the worker at dawn", "zz"), "qntmc 115: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 115: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 115: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 115: the kernel wakes the worker at dawn", "keyboard"), "bssor 115: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 115: the kernel wakes the worker at dawn", "AA"), "round 115: the kernel wakes the worker at dawn"),
    (("round 115: service latency drops after the patch", "key"), "bssxh 115: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 115: service latency drops after the patch", "lemon"), "csgbq 115: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 115: service latency drops after the patch", "a"), "round 115: service latency drops after the patch"),
    (("round 115: service latency drops after the patch", "zz"), "qntmc 115: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 115: service latency drops after the patch", "AgentU"),
        "ruyaw 115: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 115: service latency drops after the patch", "keyboard"),
        "bssor 115: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 115: service latency drops after the patch", "AA"), "round 115: service latency drops after the patch"),
    (
        ("round 115: the library caches every vector it sees", "key"),
        "bssxh 115: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 115: the library caches every vector it sees", "lemon"),
        "csgbq 115: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 115: the library caches every vector it sees", "a"), "round 115: the library caches every vector it sees"),
    (
        ("round 115: the library caches every vector it sees", "zz"),
        "qntmc 115: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 115: the library caches every vector it sees", "AgentU"),
        "ruyaw 115: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 115: the library caches every vector it sees", "keyboard"),
        "bssor 115: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 115: the library caches every vector it sees", "AA"),
        "round 115: the library caches every vector it sees",
    ),
    (("round 115: agents argue then the debate resolves", "key"), "bssxh 115: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 115: agents argue then the debate resolves", "lemon"), "csgbq 115: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 115: agents argue then the debate resolves", "a"), "round 115: agents argue then the debate resolves"),
    (("round 115: agents argue then the debate resolves", "zz"), "qntmc 115: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 115: agents argue then the debate resolves", "AgentU"),
        "ruyaw 115: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 115: agents argue then the debate resolves", "keyboard"),
        "bssor 115: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 115: agents argue then the debate resolves", "AA"), "round 115: agents argue then the debate resolves"),
    (("round 115: the filter keeps only strong matches", "key"), "bssxh 115: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 115: the filter keeps only strong matches", "lemon"), "csgbq 115: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 115: the filter keeps only strong matches", "a"), "round 115: the filter keeps only strong matches"),
    (("round 115: the filter keeps only strong matches", "zz"), "qntmc 115: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 115: the filter keeps only strong matches", "AgentU"), "ruyaw 115: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 115: the filter keeps only strong matches", "keyboard"),
        "bssor 115: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 115: the filter keeps only strong matches", "AA"), "round 115: the filter keeps only strong matches"),
    (("round 115: the model answers with a short reply", "key"), "bssxh 115: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 115: the model answers with a short reply", "lemon"), "csgbq 115: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 115: the model answers with a short reply", "a"), "round 115: the model answers with a short reply"),
    (("round 115: the model answers with a short reply", "zz"), "qntmc 115: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 115: the model answers with a short reply", "AgentU"), "ruyaw 115: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 115: the model answers with a short reply", "keyboard"),
        "bssor 115: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 115: the model answers with a short reply", "AA"), "round 115: the model answers with a short reply"),
    (
        ("round 115: the recorder stores the reasoning trace", "key"),
        "bssxh 115: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 115: the recorder stores the reasoning trace", "lemon"),
        "csgbq 115: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 115: the recorder stores the reasoning trace", "a"), "round 115: the recorder stores the reasoning trace"),
    (
        ("round 115: the recorder stores the reasoning trace", "zz"),
        "qntmc 115: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 115: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 115: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 115: the recorder stores the reasoning trace", "keyboard"),
        "bssor 115: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 115: the recorder stores the reasoning trace", "AA"),
        "round 115: the recorder stores the reasoning trace",
    ),
    (("round 115: the angel watches the processor run", "key"), "bssxh 115: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 115: the angel watches the processor run", "lemon"), "csgbq 115: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 115: the angel watches the processor run", "a"), "round 115: the angel watches the processor run"),
    (("round 115: the angel watches the processor run", "zz"), "qntmc 115: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 115: the angel watches the processor run", "AgentU"), "ruyaw 115: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 115: the angel watches the processor run", "keyboard"), "bssor 115: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 115: the angel watches the processor run", "AA"), "round 115: the angel watches the processor run"),
    (("round 115: angle of the vector decides the match", "key"), "bssxh 115: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 115: angle of the vector decides the match", "lemon"), "csgbq 115: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 115: angle of the vector decides the match", "a"), "round 115: angle of the vector decides the match"),
    (("round 115: angle of the vector decides the match", "zz"), "qntmc 115: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 115: angle of the vector decides the match", "AgentU"),
        "ruyaw 115: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 115: angle of the vector decides the match", "keyboard"),
        "bssor 115: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 115: angle of the vector decides the match", "AA"), "round 115: angle of the vector decides the match"),
    (
        ("round 115: the candle burns twice as long at night", "key"),
        "bssxh 115: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 115: the candle burns twice as long at night", "lemon"),
        "csgbq 115: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 115: the candle burns twice as long at night", "a"), "round 115: the candle burns twice as long at night"),
    (
        ("round 115: the candle burns twice as long at night", "zz"),
        "qntmc 115: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 115: the candle burns twice as long at night", "AgentU"),
        "ruyaw 115: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 115: the candle burns twice as long at night", "keyboard"),
        "bssor 115: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 115: the candle burns twice as long at night", "AA"),
        "round 115: the candle burns twice as long at night",
    ),
    (("round 115: a mirror of the universe in one line", "key"), "bssxh 115: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 115: a mirror of the universe in one line", "lemon"), "csgbq 115: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 115: a mirror of the universe in one line", "a"), "round 115: a mirror of the universe in one line"),
    (("round 115: a mirror of the universe in one line", "zz"), "qntmc 115: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 115: a mirror of the universe in one line", "AgentU"), "ruyaw 115: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 115: a mirror of the universe in one line", "keyboard"),
        "bssor 115: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 115: a mirror of the universe in one line", "AA"), "round 115: a mirror of the universe in one line"),
    (("round 115: the queue drains before the storm", "key"), "bssxh 115: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 115: the queue drains before the storm", "lemon"), "csgbq 115: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 115: the queue drains before the storm", "a"), "round 115: the queue drains before the storm"),
    (("round 115: the queue drains before the storm", "zz"), "qntmc 115: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 115: the queue drains before the storm", "AgentU"), "ruyaw 115: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 115: the queue drains before the storm", "keyboard"), "bssor 115: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 115: the queue drains before the storm", "AA"), "round 115: the queue drains before the storm"),
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
