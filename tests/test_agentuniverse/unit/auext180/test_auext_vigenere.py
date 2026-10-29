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
    (("kitten180", "key"), "umrdil180"),
    (("kitten180", "lemon"), "vmfhry180"),
    (("kitten180", "a"), "kitten180"),
    (("kitten180", "zz"), "jhssdm180"),
    (("kitten180", "AgentU"), "koxgxh180"),
    (("kitten180", "keyboard"), "umrusn180"),
    (("kitten180", "AA"), "kitten180"),
    (("sitting180", "key"), "cmrdmlq180"),
    (("sitting180", "lemon"), "dmfhvyk180"),
    (("sitting180", "a"), "sitting180"),
    (("sitting180", "zz"), "rhsshmf180"),
    (("sitting180", "AgentU"), "soxgbhg180"),
    (("sitting180", "keyboard"), "cmruwnx180"),
    (("sitting180", "AA"), "sitting180"),
    (("agent180", "key"), "kkcxx180"),
    (("agent180", "lemon"), "lkqbg180"),
    (("agent180", "a"), "agent180"),
    (("agent180", "zz"), "zfdms180"),
    (("agent180", "AgentU"), "amiam180"),
    (("agent180", "keyboard"), "kkcoh180"),
    (("agent180", "AA"), "agent180"),
    (("angle180", "key"), "krevi180"),
    (("angle180", "lemon"), "lrszr180"),
    (("angle180", "a"), "angle180"),
    (("angle180", "zz"), "zmfkd180"),
    (("angle180", "AgentU"), "atkyx180"),
    (("angle180", "keyboard"), "krems180"),
    (("angle180", "AA"), "angle180"),
    (("universe180", "key"), "ergfipci180"),
    (("universe180", "lemon"), "frujrcwq180"),
    (("universe180", "a"), "universe180"),
    (("universe180", "zz"), "tmhudqrd180"),
    (("universe180", "AgentU"), "utmixlsk180"),
    (("universe180", "keyboard"), "ergwsrjh180"),
    (("universe180", "AA"), "universe180"),
    (("memory180", "key"), "wikyvw180"),
    (("memory180", "lemon"), "xiycej180"),
    (("memory180", "a"), "memory180"),
    (("memory180", "zz"), "ldlnqx180"),
    (("memory180", "AgentU"), "mkqbks180"),
    (("memory180", "keyboard"), "wikpfy180"),
    (("memory180", "AA"), "memory180"),
    (("stream180", "key"), "cxpoek180"),
    (("stream180", "lemon"), "dxdsnx180"),
    (("stream180", "a"), "stream180"),
    (("stream180", "zz"), "rsqdzl180"),
    (("stream180", "AgentU"), "szvrtg180"),
    (("stream180", "keyboard"), "cxpfom180"),
    (("stream180", "AA"), "stream180"),
    (("context180", "key"), "msldivd180"),
    (("context180", "lemon"), "nszhrix180"),
    (("context180", "a"), "context180"),
    (("context180", "zz"), "bnmsdws180"),
    (("context180", "AgentU"), "curgxrt180"),
    (("context180", "keyboard"), "mslusxk180"),
    (("context180", "AA"), "context180"),
    (("knowledge180", "key"), "urmgpcnkc180"),
    (("knowledge180", "lemon"), "vrakyphss180"),
    (("knowledge180", "a"), "knowledge180"),
    (("knowledge180", "zz"), "jmnvkdcfd180"),
    (("knowledge180", "AgentU"), "ktsjeydmi180"),
    (("knowledge180", "keyboard"), "urmxzeujo180"),
    (("knowledge180", "AA"), "knowledge180"),
    (("vector180", "key"), "fiadsp180"),
    (("vector180", "lemon"), "giohbc180"),
    (("vector180", "a"), "vector180"),
    (("vector180", "zz"), "udbsnq180"),
    (("vector180", "AgentU"), "vkgghl180"),
    (("vector180", "keyboard"), "fiaucr180"),
    (("vector180", "AA"), "vector180"),
    (("processor180", "key"), "zvmmiqcsp180"),
    (("processor180", "lemon"), "avaqrdwaf180"),
    (("processor180", "a"), "processor180"),
    (("processor180", "zz"), "oqnbdrrnq180"),
    (("processor180", "AgentU"), "pxspxmsuv180"),
    (("processor180", "keyboard"), "zvmdssjrb180"),
    (("processor180", "AA"), "processor180"),
    (("reasoning180", "key"), "biycslsre180"),
    (("reasoning180", "lemon"), "cimgbymzu180"),
    (("reasoning180", "a"), "reasoning180"),
    (("reasoning180", "zz"), "qdzrnmhmf180"),
    (("reasoning180", "AgentU"), "rkefhhitk180"),
    (("reasoning180", "keyboard"), "biytcnzqq180"),
    (("reasoning180", "AA"), "reasoning180"),
    (("machine180", "key"), "wearmlo180"),
    (("machine180", "lemon"), "xeovvyi180"),
    (("machine180", "a"), "machine180"),
    (("machine180", "zz"), "lzbghmd180"),
    (("machine180", "AgentU"), "mggubhe180"),
    (("machine180", "keyboard"), "weaiwnv180"),
    (("machine180", "AA"), "machine180"),
    (("learning180", "key"), "viybrgxk180"),
    (("learning180", "lemon"), "wimfatrs180"),
    (("learning180", "a"), "learning180"),
    (("learning180", "zz"), "kdzqmhmf180"),
    (("learning180", "AgentU"), "lkeegcnm180"),
    (("learning180", "keyboard"), "viysbiej180"),
    (("learning180", "AA"), "learning180"),
    (("model180", "key"), "wsbop180"),
    (("model180", "lemon"), "xspsy180"),
    (("model180", "a"), "model180"),
    (("model180", "zz"), "lncdk180"),
    (("model180", "AgentU"), "muhre180"),
    (("model180", "keyboard"), "wsbfz180"),
    (("model180", "AA"), "model180"),
    (("token180", "key"), "dsior180"),
    (("token180", "lemon"), "eswsa180"),
    (("token180", "a"), "token180"),
    (("token180", "zz"), "snjdm180"),
    (("token180", "AgentU"), "tuorg180"),
    (("token180", "keyboard"), "dsifb180"),
    (("token180", "AA"), "token180"),
    (("prompt180", "key"), "zvmwtr180"),
    (("prompt180", "lemon"), "avaace180"),
    (("prompt180", "a"), "prompt180"),
    (("prompt180", "zz"), "oqnlos180"),
    (("prompt180", "AgentU"), "pxszin180"),
    (("prompt180", "keyboard"), "zvmndt180"),
    (("prompt180", "AA"), "prompt180"),
    (("session180", "key"), "ciqcmmx180"),
    (("session180", "lemon"), "diegvzr180"),
    (("session180", "a"), "session180"),
    (("session180", "zz"), "rdrrhnm180"),
    (("session180", "AgentU"), "skwfbin180"),
    (("session180", "keyboard"), "ciqtwoe180"),
    (("session180", "AA"), "session180"),
    (("library180", "key"), "vmzbepi180"),
    (("library180", "lemon"), "wmnfncc180"),
    (("library180", "a"), "library180"),
    (("library180", "zz"), "khaqzqx180"),
    (("library180", "AgentU"), "lofetly180"),
    (("library180", "keyboard"), "vmzsorp180"),
    (("library180", "AA"), "library180"),
    (("service180", "key"), "cipfmao180"),
    (("service180", "lemon"), "didjvni180"),
    (("service180", "a"), "service180"),
    (("service180", "zz"), "rdquhbd180"),
    (("service180", "AgentU"), "skvibwe180"),
    (("service180", "keyboard"), "cipwwcv180"),
    (("service180", "AA"), "service180"),
    (("gateway180", "key"), "qeroayi180"),
    (("gateway180", "lemon"), "refsjlc180"),
    (("gateway180", "a"), "gateway180"),
    (("gateway180", "zz"), "fzsdvzx180"),
    (("gateway180", "AgentU"), "ggxrpuy180"),
    (("gateway180", "keyboard"), "qerfkap180"),
    (("gateway180", "AA"), "gateway180"),
    (("storage180", "key"), "cxmbeeo180"),
    (("storage180", "lemon"), "dxafnri180"),
    (("storage180", "a"), "storage180"),
    (("storage180", "zz"), "rsnqzfd180"),
    (("storage180", "AgentU"), "szsetae180"),
    (("storage180", "keyboard"), "cxmsogv180"),
    (("storage180", "AA"), "storage180"),
    (("network180", "key"), "xirgspu180"),
    (("network180", "lemon"), "yifkbco180"),
    (("network180", "a"), "network180"),
    (("network180", "zz"), "mdsvnqj180"),
    (("network180", "AgentU"), "nkxjhlk180"),
    (("network180", "keyboard"), "xirxcrb180"),
    (("network180", "AA"), "network180"),
    (("latency180", "key"), "verorai180"),
    (("latency180", "lemon"), "wefsanc180"),
    (("latency180", "a"), "latency180"),
    (("latency180", "zz"), "kzsdmbx180"),
    (("latency180", "AgentU"), "lgxrgwy180"),
    (("latency180", "keyboard"), "verfbcp180"),
    (("latency180", "AA"), "latency180"),
    (("buffer180", "key"), "lydpip180"),
    (("buffer180", "lemon"), "myrtrc180"),
    (("buffer180", "a"), "buffer180"),
    (("buffer180", "zz"), "ateedq180"),
    (("buffer180", "AgentU"), "bajsxl180"),
    (("buffer180", "keyboard"), "lydgsr180"),
    (("buffer180", "AA"), "buffer180"),
    (("queue180", "key"), "aycei180"),
    (("queue180", "lemon"), "byqir180"),
    (("queue180", "a"), "queue180"),
    (("queue180", "zz"), "ptdtd180"),
    (("queue180", "AgentU"), "qaihx180"),
    (("queue180", "keyboard"), "aycvs180"),
    (("queue180", "AA"), "queue180"),
    (("worker180", "key"), "gspuip180"),
    (("worker180", "lemon"), "hsdyrc180"),
    (("worker180", "a"), "worker180"),
    (("worker180", "zz"), "vnqjdq180"),
    (("worker180", "AgentU"), "wuvxxl180"),
    (("worker180", "keyboard"), "gsplsr180"),
    (("worker180", "AA"), "worker180"),
    (("kernel180", "key"), "uipxij180"),
    (("kernel180", "lemon"), "vidbrw180"),
    (("kernel180", "a"), "kernel180"),
    (("kernel180", "zz"), "jdqmdk180"),
    (("kernel180", "AgentU"), "kkvaxf180"),
    (("kernel180", "keyboard"), "uiposl180"),
    (("kernel180", "AA"), "kernel180"),
    (("signal180", "key"), "cmexej180"),
    (("signal180", "lemon"), "dmsbnw180"),
    (("signal180", "a"), "signal180"),
    (("signal180", "zz"), "rhfmzk180"),
    (("signal180", "AgentU"), "sokatf180"),
    (("signal180", "keyboard"), "cmeool180"),
    (("signal180", "AA"), "signal180"),
    (("packet180", "key"), "zeauir180"),
    (("packet180", "lemon"), "aeoyre180"),
    (("packet180", "a"), "packet180"),
    (("packet180", "zz"), "ozbjds180"),
    (("packet180", "AgentU"), "pggxxn180"),
    (("packet180", "keyboard"), "zealst180"),
    (("packet180", "AA"), "packet180"),
    (("router180", "key"), "bssdip180"),
    (("router180", "lemon"), "csghrc180"),
    (("router180", "a"), "router180"),
    (("router180", "zz"), "qntsdq180"),
    (("router180", "AgentU"), "ruygxl180"),
    (("router180", "keyboard"), "bssusr180"),
    (("router180", "AA"), "router180"),
    (("cluster180", "key"), "mpscxcb180"),
    (("cluster180", "lemon"), "npgggpv180"),
    (("cluster180", "a"), "cluster180"),
    (("cluster180", "zz"), "bktrsdq180"),
    (("cluster180", "AgentU"), "cryfmyr180"),
    (("cluster180", "keyboard"), "mpsthei180"),
    (("cluster180", "AA"), "cluster180"),
    (("mirror180", "key"), "wmpbsp180"),
    (("mirror180", "lemon"), "xmdfbc180"),
    (("mirror180", "a"), "mirror180"),
    (("mirror180", "zz"), "lhqqnq180"),
    (("mirror180", "AgentU"), "movehl180"),
    (("mirror180", "keyboard"), "wmpscr180"),
    (("mirror180", "AA"), "mirror180"),
    (("filter180", "key"), "pmjdip180"),
    (("filter180", "lemon"), "qmxhrc180"),
    (("filter180", "a"), "filter180"),
    (("filter180", "zz"), "ehksdq180"),
    (("filter180", "AgentU"), "fopgxl180"),
    (("filter180", "keyboard"), "pmjusr180"),
    (("filter180", "AA"), "filter180"),
    (("ranking180", "key"), "belumlq180"),
    (("ranking180", "lemon"), "cezyvyk180"),
    (("ranking180", "a"), "ranking180"),
    (("ranking180", "zz"), "qzmjhmf180"),
    (("ranking180", "AgentU"), "rgrxbhg180"),
    (("ranking180", "keyboard"), "bellwnx180"),
    (("ranking180", "AA"), "ranking180"),
    (("encoding180", "key"), "orayhgxk180"),
    (("encoding180", "lemon"), "procqtrs180"),
    (("encoding180", "a"), "encoding180"),
    (("encoding180", "zz"), "dmbnchmf180"),
    (("encoding180", "AgentU"), "etgbwcnm180"),
    (("encoding180", "keyboard"), "orapriej180"),
    (("encoding180", "AA"), "encoding180"),
    (("mapping180", "key"), "wenzmlq180"),
    (("mapping180", "lemon"), "xebdvyk180"),
    (("mapping180", "a"), "mapping180"),
    (("mapping180", "zz"), "lzoohmf180"),
    (("mapping180", "AgentU"), "mgtcbhg180"),
    (("mapping180", "keyboard"), "wenqwnx180"),
    (("mapping180", "AA"), "mapping180"),
    (("record180", "key"), "biayvb180"),
    (("record180", "lemon"), "cioceo180"),
    (("record180", "a"), "record180"),
    (("record180", "zz"), "qdbnqc180"),
    (("record180", "AgentU"), "rkgbkx180"),
    (("record180", "keyboard"), "biapfd180"),
    (("record180", "AA"), "record180"),
    (("candle180", "key"), "melnpc180"),
    (("candle180", "lemon"), "nezryp180"),
    (("candle180", "a"), "candle180"),
    (("candle180", "zz"), "bzmckd180"),
    (("candle180", "AgentU"), "cgrqey180"),
    (("candle180", "keyboard"), "meleze180"),
    (("candle180", "AA"), "candle180"),
    (("thread180", "key"), "dlpoeb180"),
    (("thread180", "lemon"), "eldsno180"),
    (("thread180", "a"), "thread180"),
    (("thread180", "zz"), "sgqdzc180"),
    (("thread180", "AgentU"), "tnvrtx180"),
    (("thread180", "keyboard"), "dlpfod180"),
    (("thread180", "AA"), "thread180"),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 180: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 180: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "a"),
        "round 180: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 180: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 180: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 180: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", "AA"),
        "round 180: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "key"),
        "bssxh 180: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 180: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "a"),
        "round 180: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 180: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 180: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 180: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", "AA"),
        "round 180: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 180: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 180: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "a"),
        "round 180: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 180: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 180: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 180: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", "AA"),
        "round 180: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 180: the processor reads the record then stops", "key"),
        "bssxh 180: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 180: the processor reads the record then stops", "lemon"),
        "csgbq 180: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 180: the processor reads the record then stops", "a"),
        "round 180: the processor reads the record then stops",
    ),
    (
        ("round 180: the processor reads the record then stops", "zz"),
        "qntmc 180: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 180: the processor reads the record then stops", "AgentU"),
        "ruyaw 180: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 180: the processor reads the record then stops", "keyboard"),
        "bssor 180: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 180: the processor reads the record then stops", "AA"),
        "round 180: the processor reads the record then stops",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "key"),
        "bssxh 180: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "lemon"),
        "csgbq 180: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "a"),
        "round 180: a worker pulls the next task from the queue",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "zz"),
        "qntmc 180: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 180: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "keyboard"),
        "bssor 180: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 180: a worker pulls the next task from the queue", "AA"),
        "round 180: a worker pulls the next task from the queue",
    ),
    (
        ("round 180: signals travel through the network layer", "key"),
        "bssxh 180: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 180: signals travel through the network layer", "lemon"),
        "csgbq 180: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 180: signals travel through the network layer", "a"),
        "round 180: signals travel through the network layer",
    ),
    (
        ("round 180: signals travel through the network layer", "zz"),
        "qntmc 180: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 180: signals travel through the network layer", "AgentU"),
        "ruyaw 180: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 180: signals travel through the network layer", "keyboard"),
        "bssor 180: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 180: signals travel through the network layer", "AA"),
        "round 180: signals travel through the network layer",
    ),
    (
        ("round 180: the gateway routes each request by policy", "key"),
        "bssxh 180: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 180: the gateway routes each request by policy", "lemon"),
        "csgbq 180: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 180: the gateway routes each request by policy", "a"),
        "round 180: the gateway routes each request by policy",
    ),
    (
        ("round 180: the gateway routes each request by policy", "zz"),
        "qntmc 180: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 180: the gateway routes each request by policy", "AgentU"),
        "ruyaw 180: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 180: the gateway routes each request by policy", "keyboard"),
        "bssor 180: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 180: the gateway routes each request by policy", "AA"),
        "round 180: the gateway routes each request by policy",
    ),
    (("round 180: memory grows until the buffer is full", "key"), "bssxh 180: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 180: memory grows until the buffer is full", "lemon"), "csgbq 180: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 180: memory grows until the buffer is full", "a"), "round 180: memory grows until the buffer is full"),
    (("round 180: memory grows until the buffer is full", "zz"), "qntmc 180: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 180: memory grows until the buffer is full", "AgentU"),
        "ruyaw 180: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 180: memory grows until the buffer is full", "keyboard"),
        "bssor 180: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 180: memory grows until the buffer is full", "AA"), "round 180: memory grows until the buffer is full"),
    (("round 180: the cluster mirrors every packet twice", "key"), "bssxh 180: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 180: the cluster mirrors every packet twice", "lemon"),
        "csgbq 180: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 180: the cluster mirrors every packet twice", "a"), "round 180: the cluster mirrors every packet twice"),
    (("round 180: the cluster mirrors every packet twice", "zz"), "qntmc 180: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 180: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 180: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 180: the cluster mirrors every packet twice", "keyboard"),
        "bssor 180: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 180: the cluster mirrors every packet twice", "AA"), "round 180: the cluster mirrors every packet twice"),
    (
        ("round 180: ranking uses tokens learned from the corpus", "key"),
        "bssxh 180: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 180: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", "a"),
        "round 180: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 180: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 180: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 180: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", "AA"),
        "round 180: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 180: a long session ends when the candle dies", "key"),
        "bssxh 180: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 180: a long session ends when the candle dies", "lemon"),
        "csgbq 180: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 180: a long session ends when the candle dies", "a"),
        "round 180: a long session ends when the candle dies",
    ),
    (
        ("round 180: a long session ends when the candle dies", "zz"),
        "qntmc 180: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 180: a long session ends when the candle dies", "AgentU"),
        "ruyaw 180: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 180: a long session ends when the candle dies", "keyboard"),
        "bssor 180: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 180: a long session ends when the candle dies", "AA"),
        "round 180: a long session ends when the candle dies",
    ),
    (("round 180: encode the prompt then map the result", "key"), "bssxh 180: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 180: encode the prompt then map the result", "lemon"), "csgbq 180: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 180: encode the prompt then map the result", "a"), "round 180: encode the prompt then map the result"),
    (("round 180: encode the prompt then map the result", "zz"), "qntmc 180: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 180: encode the prompt then map the result", "AgentU"),
        "ruyaw 180: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 180: encode the prompt then map the result", "keyboard"),
        "bssor 180: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 180: encode the prompt then map the result", "AA"), "round 180: encode the prompt then map the result"),
    (("round 180: the kernel wakes the worker at dawn", "key"), "bssxh 180: rri iovlop ukocc xfo ambocb er neux"),
    (("round 180: the kernel wakes the worker at dawn", "lemon"), "csgbq 180: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 180: the kernel wakes the worker at dawn", "a"), "round 180: the kernel wakes the worker at dawn"),
    (("round 180: the kernel wakes the worker at dawn", "zz"), "qntmc 180: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 180: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 180: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 180: the kernel wakes the worker at dawn", "keyboard"), "bssor 180: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 180: the kernel wakes the worker at dawn", "AA"), "round 180: the kernel wakes the worker at dawn"),
    (("round 180: service latency drops after the patch", "key"), "bssxh 180: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 180: service latency drops after the patch", "lemon"), "csgbq 180: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 180: service latency drops after the patch", "a"), "round 180: service latency drops after the patch"),
    (("round 180: service latency drops after the patch", "zz"), "qntmc 180: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 180: service latency drops after the patch", "AgentU"),
        "ruyaw 180: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 180: service latency drops after the patch", "keyboard"),
        "bssor 180: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 180: service latency drops after the patch", "AA"), "round 180: service latency drops after the patch"),
    (
        ("round 180: the library caches every vector it sees", "key"),
        "bssxh 180: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 180: the library caches every vector it sees", "lemon"),
        "csgbq 180: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 180: the library caches every vector it sees", "a"), "round 180: the library caches every vector it sees"),
    (
        ("round 180: the library caches every vector it sees", "zz"),
        "qntmc 180: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 180: the library caches every vector it sees", "AgentU"),
        "ruyaw 180: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 180: the library caches every vector it sees", "keyboard"),
        "bssor 180: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 180: the library caches every vector it sees", "AA"),
        "round 180: the library caches every vector it sees",
    ),
    (("round 180: agents argue then the debate resolves", "key"), "bssxh 180: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 180: agents argue then the debate resolves", "lemon"), "csgbq 180: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 180: agents argue then the debate resolves", "a"), "round 180: agents argue then the debate resolves"),
    (("round 180: agents argue then the debate resolves", "zz"), "qntmc 180: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 180: agents argue then the debate resolves", "AgentU"),
        "ruyaw 180: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 180: agents argue then the debate resolves", "keyboard"),
        "bssor 180: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 180: agents argue then the debate resolves", "AA"), "round 180: agents argue then the debate resolves"),
    (("round 180: the filter keeps only strong matches", "key"), "bssxh 180: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 180: the filter keeps only strong matches", "lemon"), "csgbq 180: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 180: the filter keeps only strong matches", "a"), "round 180: the filter keeps only strong matches"),
    (("round 180: the filter keeps only strong matches", "zz"), "qntmc 180: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 180: the filter keeps only strong matches", "AgentU"), "ruyaw 180: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 180: the filter keeps only strong matches", "keyboard"),
        "bssor 180: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 180: the filter keeps only strong matches", "AA"), "round 180: the filter keeps only strong matches"),
    (("round 180: the model answers with a short reply", "key"), "bssxh 180: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 180: the model answers with a short reply", "lemon"), "csgbq 180: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 180: the model answers with a short reply", "a"), "round 180: the model answers with a short reply"),
    (("round 180: the model answers with a short reply", "zz"), "qntmc 180: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 180: the model answers with a short reply", "AgentU"), "ruyaw 180: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 180: the model answers with a short reply", "keyboard"),
        "bssor 180: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 180: the model answers with a short reply", "AA"), "round 180: the model answers with a short reply"),
    (
        ("round 180: the recorder stores the reasoning trace", "key"),
        "bssxh 180: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 180: the recorder stores the reasoning trace", "lemon"),
        "csgbq 180: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 180: the recorder stores the reasoning trace", "a"), "round 180: the recorder stores the reasoning trace"),
    (
        ("round 180: the recorder stores the reasoning trace", "zz"),
        "qntmc 180: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 180: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 180: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 180: the recorder stores the reasoning trace", "keyboard"),
        "bssor 180: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 180: the recorder stores the reasoning trace", "AA"),
        "round 180: the recorder stores the reasoning trace",
    ),
    (("round 180: the angel watches the processor run", "key"), "bssxh 180: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 180: the angel watches the processor run", "lemon"), "csgbq 180: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 180: the angel watches the processor run", "a"), "round 180: the angel watches the processor run"),
    (("round 180: the angel watches the processor run", "zz"), "qntmc 180: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 180: the angel watches the processor run", "AgentU"), "ruyaw 180: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 180: the angel watches the processor run", "keyboard"), "bssor 180: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 180: the angel watches the processor run", "AA"), "round 180: the angel watches the processor run"),
    (("round 180: angle of the vector decides the match", "key"), "bssxh 180: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 180: angle of the vector decides the match", "lemon"), "csgbq 180: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 180: angle of the vector decides the match", "a"), "round 180: angle of the vector decides the match"),
    (("round 180: angle of the vector decides the match", "zz"), "qntmc 180: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 180: angle of the vector decides the match", "AgentU"),
        "ruyaw 180: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 180: angle of the vector decides the match", "keyboard"),
        "bssor 180: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 180: angle of the vector decides the match", "AA"), "round 180: angle of the vector decides the match"),
    (
        ("round 180: the candle burns twice as long at night", "key"),
        "bssxh 180: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 180: the candle burns twice as long at night", "lemon"),
        "csgbq 180: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 180: the candle burns twice as long at night", "a"), "round 180: the candle burns twice as long at night"),
    (
        ("round 180: the candle burns twice as long at night", "zz"),
        "qntmc 180: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 180: the candle burns twice as long at night", "AgentU"),
        "ruyaw 180: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 180: the candle burns twice as long at night", "keyboard"),
        "bssor 180: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 180: the candle burns twice as long at night", "AA"),
        "round 180: the candle burns twice as long at night",
    ),
    (("round 180: a mirror of the universe in one line", "key"), "bssxh 180: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 180: a mirror of the universe in one line", "lemon"), "csgbq 180: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 180: a mirror of the universe in one line", "a"), "round 180: a mirror of the universe in one line"),
    (("round 180: a mirror of the universe in one line", "zz"), "qntmc 180: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 180: a mirror of the universe in one line", "AgentU"), "ruyaw 180: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 180: a mirror of the universe in one line", "keyboard"),
        "bssor 180: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 180: a mirror of the universe in one line", "AA"), "round 180: a mirror of the universe in one line"),
    (("round 180: the queue drains before the storm", "key"), "bssxh 180: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 180: the queue drains before the storm", "lemon"), "csgbq 180: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 180: the queue drains before the storm", "a"), "round 180: the queue drains before the storm"),
    (("round 180: the queue drains before the storm", "zz"), "qntmc 180: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 180: the queue drains before the storm", "AgentU"), "ruyaw 180: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 180: the queue drains before the storm", "keyboard"), "bssor 180: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 180: the queue drains before the storm", "AA"), "round 180: the queue drains before the storm"),
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
