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
    (("kitten173", "key"), "umrdil173"),
    (("kitten173", "lemon"), "vmfhry173"),
    (("kitten173", "a"), "kitten173"),
    (("kitten173", "zz"), "jhssdm173"),
    (("kitten173", "AgentU"), "koxgxh173"),
    (("kitten173", "keyboard"), "umrusn173"),
    (("kitten173", "AA"), "kitten173"),
    (("sitting173", "key"), "cmrdmlq173"),
    (("sitting173", "lemon"), "dmfhvyk173"),
    (("sitting173", "a"), "sitting173"),
    (("sitting173", "zz"), "rhsshmf173"),
    (("sitting173", "AgentU"), "soxgbhg173"),
    (("sitting173", "keyboard"), "cmruwnx173"),
    (("sitting173", "AA"), "sitting173"),
    (("agent173", "key"), "kkcxx173"),
    (("agent173", "lemon"), "lkqbg173"),
    (("agent173", "a"), "agent173"),
    (("agent173", "zz"), "zfdms173"),
    (("agent173", "AgentU"), "amiam173"),
    (("agent173", "keyboard"), "kkcoh173"),
    (("agent173", "AA"), "agent173"),
    (("angle173", "key"), "krevi173"),
    (("angle173", "lemon"), "lrszr173"),
    (("angle173", "a"), "angle173"),
    (("angle173", "zz"), "zmfkd173"),
    (("angle173", "AgentU"), "atkyx173"),
    (("angle173", "keyboard"), "krems173"),
    (("angle173", "AA"), "angle173"),
    (("universe173", "key"), "ergfipci173"),
    (("universe173", "lemon"), "frujrcwq173"),
    (("universe173", "a"), "universe173"),
    (("universe173", "zz"), "tmhudqrd173"),
    (("universe173", "AgentU"), "utmixlsk173"),
    (("universe173", "keyboard"), "ergwsrjh173"),
    (("universe173", "AA"), "universe173"),
    (("memory173", "key"), "wikyvw173"),
    (("memory173", "lemon"), "xiycej173"),
    (("memory173", "a"), "memory173"),
    (("memory173", "zz"), "ldlnqx173"),
    (("memory173", "AgentU"), "mkqbks173"),
    (("memory173", "keyboard"), "wikpfy173"),
    (("memory173", "AA"), "memory173"),
    (("stream173", "key"), "cxpoek173"),
    (("stream173", "lemon"), "dxdsnx173"),
    (("stream173", "a"), "stream173"),
    (("stream173", "zz"), "rsqdzl173"),
    (("stream173", "AgentU"), "szvrtg173"),
    (("stream173", "keyboard"), "cxpfom173"),
    (("stream173", "AA"), "stream173"),
    (("context173", "key"), "msldivd173"),
    (("context173", "lemon"), "nszhrix173"),
    (("context173", "a"), "context173"),
    (("context173", "zz"), "bnmsdws173"),
    (("context173", "AgentU"), "curgxrt173"),
    (("context173", "keyboard"), "mslusxk173"),
    (("context173", "AA"), "context173"),
    (("knowledge173", "key"), "urmgpcnkc173"),
    (("knowledge173", "lemon"), "vrakyphss173"),
    (("knowledge173", "a"), "knowledge173"),
    (("knowledge173", "zz"), "jmnvkdcfd173"),
    (("knowledge173", "AgentU"), "ktsjeydmi173"),
    (("knowledge173", "keyboard"), "urmxzeujo173"),
    (("knowledge173", "AA"), "knowledge173"),
    (("vector173", "key"), "fiadsp173"),
    (("vector173", "lemon"), "giohbc173"),
    (("vector173", "a"), "vector173"),
    (("vector173", "zz"), "udbsnq173"),
    (("vector173", "AgentU"), "vkgghl173"),
    (("vector173", "keyboard"), "fiaucr173"),
    (("vector173", "AA"), "vector173"),
    (("processor173", "key"), "zvmmiqcsp173"),
    (("processor173", "lemon"), "avaqrdwaf173"),
    (("processor173", "a"), "processor173"),
    (("processor173", "zz"), "oqnbdrrnq173"),
    (("processor173", "AgentU"), "pxspxmsuv173"),
    (("processor173", "keyboard"), "zvmdssjrb173"),
    (("processor173", "AA"), "processor173"),
    (("reasoning173", "key"), "biycslsre173"),
    (("reasoning173", "lemon"), "cimgbymzu173"),
    (("reasoning173", "a"), "reasoning173"),
    (("reasoning173", "zz"), "qdzrnmhmf173"),
    (("reasoning173", "AgentU"), "rkefhhitk173"),
    (("reasoning173", "keyboard"), "biytcnzqq173"),
    (("reasoning173", "AA"), "reasoning173"),
    (("machine173", "key"), "wearmlo173"),
    (("machine173", "lemon"), "xeovvyi173"),
    (("machine173", "a"), "machine173"),
    (("machine173", "zz"), "lzbghmd173"),
    (("machine173", "AgentU"), "mggubhe173"),
    (("machine173", "keyboard"), "weaiwnv173"),
    (("machine173", "AA"), "machine173"),
    (("learning173", "key"), "viybrgxk173"),
    (("learning173", "lemon"), "wimfatrs173"),
    (("learning173", "a"), "learning173"),
    (("learning173", "zz"), "kdzqmhmf173"),
    (("learning173", "AgentU"), "lkeegcnm173"),
    (("learning173", "keyboard"), "viysbiej173"),
    (("learning173", "AA"), "learning173"),
    (("model173", "key"), "wsbop173"),
    (("model173", "lemon"), "xspsy173"),
    (("model173", "a"), "model173"),
    (("model173", "zz"), "lncdk173"),
    (("model173", "AgentU"), "muhre173"),
    (("model173", "keyboard"), "wsbfz173"),
    (("model173", "AA"), "model173"),
    (("token173", "key"), "dsior173"),
    (("token173", "lemon"), "eswsa173"),
    (("token173", "a"), "token173"),
    (("token173", "zz"), "snjdm173"),
    (("token173", "AgentU"), "tuorg173"),
    (("token173", "keyboard"), "dsifb173"),
    (("token173", "AA"), "token173"),
    (("prompt173", "key"), "zvmwtr173"),
    (("prompt173", "lemon"), "avaace173"),
    (("prompt173", "a"), "prompt173"),
    (("prompt173", "zz"), "oqnlos173"),
    (("prompt173", "AgentU"), "pxszin173"),
    (("prompt173", "keyboard"), "zvmndt173"),
    (("prompt173", "AA"), "prompt173"),
    (("session173", "key"), "ciqcmmx173"),
    (("session173", "lemon"), "diegvzr173"),
    (("session173", "a"), "session173"),
    (("session173", "zz"), "rdrrhnm173"),
    (("session173", "AgentU"), "skwfbin173"),
    (("session173", "keyboard"), "ciqtwoe173"),
    (("session173", "AA"), "session173"),
    (("library173", "key"), "vmzbepi173"),
    (("library173", "lemon"), "wmnfncc173"),
    (("library173", "a"), "library173"),
    (("library173", "zz"), "khaqzqx173"),
    (("library173", "AgentU"), "lofetly173"),
    (("library173", "keyboard"), "vmzsorp173"),
    (("library173", "AA"), "library173"),
    (("service173", "key"), "cipfmao173"),
    (("service173", "lemon"), "didjvni173"),
    (("service173", "a"), "service173"),
    (("service173", "zz"), "rdquhbd173"),
    (("service173", "AgentU"), "skvibwe173"),
    (("service173", "keyboard"), "cipwwcv173"),
    (("service173", "AA"), "service173"),
    (("gateway173", "key"), "qeroayi173"),
    (("gateway173", "lemon"), "refsjlc173"),
    (("gateway173", "a"), "gateway173"),
    (("gateway173", "zz"), "fzsdvzx173"),
    (("gateway173", "AgentU"), "ggxrpuy173"),
    (("gateway173", "keyboard"), "qerfkap173"),
    (("gateway173", "AA"), "gateway173"),
    (("storage173", "key"), "cxmbeeo173"),
    (("storage173", "lemon"), "dxafnri173"),
    (("storage173", "a"), "storage173"),
    (("storage173", "zz"), "rsnqzfd173"),
    (("storage173", "AgentU"), "szsetae173"),
    (("storage173", "keyboard"), "cxmsogv173"),
    (("storage173", "AA"), "storage173"),
    (("network173", "key"), "xirgspu173"),
    (("network173", "lemon"), "yifkbco173"),
    (("network173", "a"), "network173"),
    (("network173", "zz"), "mdsvnqj173"),
    (("network173", "AgentU"), "nkxjhlk173"),
    (("network173", "keyboard"), "xirxcrb173"),
    (("network173", "AA"), "network173"),
    (("latency173", "key"), "verorai173"),
    (("latency173", "lemon"), "wefsanc173"),
    (("latency173", "a"), "latency173"),
    (("latency173", "zz"), "kzsdmbx173"),
    (("latency173", "AgentU"), "lgxrgwy173"),
    (("latency173", "keyboard"), "verfbcp173"),
    (("latency173", "AA"), "latency173"),
    (("buffer173", "key"), "lydpip173"),
    (("buffer173", "lemon"), "myrtrc173"),
    (("buffer173", "a"), "buffer173"),
    (("buffer173", "zz"), "ateedq173"),
    (("buffer173", "AgentU"), "bajsxl173"),
    (("buffer173", "keyboard"), "lydgsr173"),
    (("buffer173", "AA"), "buffer173"),
    (("queue173", "key"), "aycei173"),
    (("queue173", "lemon"), "byqir173"),
    (("queue173", "a"), "queue173"),
    (("queue173", "zz"), "ptdtd173"),
    (("queue173", "AgentU"), "qaihx173"),
    (("queue173", "keyboard"), "aycvs173"),
    (("queue173", "AA"), "queue173"),
    (("worker173", "key"), "gspuip173"),
    (("worker173", "lemon"), "hsdyrc173"),
    (("worker173", "a"), "worker173"),
    (("worker173", "zz"), "vnqjdq173"),
    (("worker173", "AgentU"), "wuvxxl173"),
    (("worker173", "keyboard"), "gsplsr173"),
    (("worker173", "AA"), "worker173"),
    (("kernel173", "key"), "uipxij173"),
    (("kernel173", "lemon"), "vidbrw173"),
    (("kernel173", "a"), "kernel173"),
    (("kernel173", "zz"), "jdqmdk173"),
    (("kernel173", "AgentU"), "kkvaxf173"),
    (("kernel173", "keyboard"), "uiposl173"),
    (("kernel173", "AA"), "kernel173"),
    (("signal173", "key"), "cmexej173"),
    (("signal173", "lemon"), "dmsbnw173"),
    (("signal173", "a"), "signal173"),
    (("signal173", "zz"), "rhfmzk173"),
    (("signal173", "AgentU"), "sokatf173"),
    (("signal173", "keyboard"), "cmeool173"),
    (("signal173", "AA"), "signal173"),
    (("packet173", "key"), "zeauir173"),
    (("packet173", "lemon"), "aeoyre173"),
    (("packet173", "a"), "packet173"),
    (("packet173", "zz"), "ozbjds173"),
    (("packet173", "AgentU"), "pggxxn173"),
    (("packet173", "keyboard"), "zealst173"),
    (("packet173", "AA"), "packet173"),
    (("router173", "key"), "bssdip173"),
    (("router173", "lemon"), "csghrc173"),
    (("router173", "a"), "router173"),
    (("router173", "zz"), "qntsdq173"),
    (("router173", "AgentU"), "ruygxl173"),
    (("router173", "keyboard"), "bssusr173"),
    (("router173", "AA"), "router173"),
    (("cluster173", "key"), "mpscxcb173"),
    (("cluster173", "lemon"), "npgggpv173"),
    (("cluster173", "a"), "cluster173"),
    (("cluster173", "zz"), "bktrsdq173"),
    (("cluster173", "AgentU"), "cryfmyr173"),
    (("cluster173", "keyboard"), "mpsthei173"),
    (("cluster173", "AA"), "cluster173"),
    (("mirror173", "key"), "wmpbsp173"),
    (("mirror173", "lemon"), "xmdfbc173"),
    (("mirror173", "a"), "mirror173"),
    (("mirror173", "zz"), "lhqqnq173"),
    (("mirror173", "AgentU"), "movehl173"),
    (("mirror173", "keyboard"), "wmpscr173"),
    (("mirror173", "AA"), "mirror173"),
    (("filter173", "key"), "pmjdip173"),
    (("filter173", "lemon"), "qmxhrc173"),
    (("filter173", "a"), "filter173"),
    (("filter173", "zz"), "ehksdq173"),
    (("filter173", "AgentU"), "fopgxl173"),
    (("filter173", "keyboard"), "pmjusr173"),
    (("filter173", "AA"), "filter173"),
    (("ranking173", "key"), "belumlq173"),
    (("ranking173", "lemon"), "cezyvyk173"),
    (("ranking173", "a"), "ranking173"),
    (("ranking173", "zz"), "qzmjhmf173"),
    (("ranking173", "AgentU"), "rgrxbhg173"),
    (("ranking173", "keyboard"), "bellwnx173"),
    (("ranking173", "AA"), "ranking173"),
    (("encoding173", "key"), "orayhgxk173"),
    (("encoding173", "lemon"), "procqtrs173"),
    (("encoding173", "a"), "encoding173"),
    (("encoding173", "zz"), "dmbnchmf173"),
    (("encoding173", "AgentU"), "etgbwcnm173"),
    (("encoding173", "keyboard"), "orapriej173"),
    (("encoding173", "AA"), "encoding173"),
    (("mapping173", "key"), "wenzmlq173"),
    (("mapping173", "lemon"), "xebdvyk173"),
    (("mapping173", "a"), "mapping173"),
    (("mapping173", "zz"), "lzoohmf173"),
    (("mapping173", "AgentU"), "mgtcbhg173"),
    (("mapping173", "keyboard"), "wenqwnx173"),
    (("mapping173", "AA"), "mapping173"),
    (("record173", "key"), "biayvb173"),
    (("record173", "lemon"), "cioceo173"),
    (("record173", "a"), "record173"),
    (("record173", "zz"), "qdbnqc173"),
    (("record173", "AgentU"), "rkgbkx173"),
    (("record173", "keyboard"), "biapfd173"),
    (("record173", "AA"), "record173"),
    (("candle173", "key"), "melnpc173"),
    (("candle173", "lemon"), "nezryp173"),
    (("candle173", "a"), "candle173"),
    (("candle173", "zz"), "bzmckd173"),
    (("candle173", "AgentU"), "cgrqey173"),
    (("candle173", "keyboard"), "meleze173"),
    (("candle173", "AA"), "candle173"),
    (("thread173", "key"), "dlpoeb173"),
    (("thread173", "lemon"), "eldsno173"),
    (("thread173", "a"), "thread173"),
    (("thread173", "zz"), "sgqdzc173"),
    (("thread173", "AgentU"), "tnvrtx173"),
    (("thread173", "keyboard"), "dlpfod173"),
    (("thread173", "AA"), "thread173"),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 173: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 173: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "a"),
        "round 173: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 173: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 173: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 173: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", "AA"),
        "round 173: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "key"),
        "bssxh 173: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 173: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "a"),
        "round 173: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 173: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 173: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 173: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", "AA"),
        "round 173: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 173: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 173: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "a"),
        "round 173: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 173: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 173: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 173: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", "AA"),
        "round 173: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 173: the processor reads the record then stops", "key"),
        "bssxh 173: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 173: the processor reads the record then stops", "lemon"),
        "csgbq 173: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 173: the processor reads the record then stops", "a"),
        "round 173: the processor reads the record then stops",
    ),
    (
        ("round 173: the processor reads the record then stops", "zz"),
        "qntmc 173: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 173: the processor reads the record then stops", "AgentU"),
        "ruyaw 173: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 173: the processor reads the record then stops", "keyboard"),
        "bssor 173: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 173: the processor reads the record then stops", "AA"),
        "round 173: the processor reads the record then stops",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "key"),
        "bssxh 173: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "lemon"),
        "csgbq 173: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "a"),
        "round 173: a worker pulls the next task from the queue",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "zz"),
        "qntmc 173: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 173: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "keyboard"),
        "bssor 173: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 173: a worker pulls the next task from the queue", "AA"),
        "round 173: a worker pulls the next task from the queue",
    ),
    (
        ("round 173: signals travel through the network layer", "key"),
        "bssxh 173: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 173: signals travel through the network layer", "lemon"),
        "csgbq 173: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 173: signals travel through the network layer", "a"),
        "round 173: signals travel through the network layer",
    ),
    (
        ("round 173: signals travel through the network layer", "zz"),
        "qntmc 173: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 173: signals travel through the network layer", "AgentU"),
        "ruyaw 173: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 173: signals travel through the network layer", "keyboard"),
        "bssor 173: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 173: signals travel through the network layer", "AA"),
        "round 173: signals travel through the network layer",
    ),
    (
        ("round 173: the gateway routes each request by policy", "key"),
        "bssxh 173: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 173: the gateway routes each request by policy", "lemon"),
        "csgbq 173: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 173: the gateway routes each request by policy", "a"),
        "round 173: the gateway routes each request by policy",
    ),
    (
        ("round 173: the gateway routes each request by policy", "zz"),
        "qntmc 173: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 173: the gateway routes each request by policy", "AgentU"),
        "ruyaw 173: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 173: the gateway routes each request by policy", "keyboard"),
        "bssor 173: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 173: the gateway routes each request by policy", "AA"),
        "round 173: the gateway routes each request by policy",
    ),
    (("round 173: memory grows until the buffer is full", "key"), "bssxh 173: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 173: memory grows until the buffer is full", "lemon"), "csgbq 173: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 173: memory grows until the buffer is full", "a"), "round 173: memory grows until the buffer is full"),
    (("round 173: memory grows until the buffer is full", "zz"), "qntmc 173: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 173: memory grows until the buffer is full", "AgentU"),
        "ruyaw 173: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 173: memory grows until the buffer is full", "keyboard"),
        "bssor 173: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 173: memory grows until the buffer is full", "AA"), "round 173: memory grows until the buffer is full"),
    (("round 173: the cluster mirrors every packet twice", "key"), "bssxh 173: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 173: the cluster mirrors every packet twice", "lemon"),
        "csgbq 173: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 173: the cluster mirrors every packet twice", "a"), "round 173: the cluster mirrors every packet twice"),
    (("round 173: the cluster mirrors every packet twice", "zz"), "qntmc 173: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 173: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 173: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 173: the cluster mirrors every packet twice", "keyboard"),
        "bssor 173: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 173: the cluster mirrors every packet twice", "AA"), "round 173: the cluster mirrors every packet twice"),
    (
        ("round 173: ranking uses tokens learned from the corpus", "key"),
        "bssxh 173: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 173: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", "a"),
        "round 173: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 173: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 173: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 173: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", "AA"),
        "round 173: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 173: a long session ends when the candle dies", "key"),
        "bssxh 173: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 173: a long session ends when the candle dies", "lemon"),
        "csgbq 173: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 173: a long session ends when the candle dies", "a"),
        "round 173: a long session ends when the candle dies",
    ),
    (
        ("round 173: a long session ends when the candle dies", "zz"),
        "qntmc 173: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 173: a long session ends when the candle dies", "AgentU"),
        "ruyaw 173: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 173: a long session ends when the candle dies", "keyboard"),
        "bssor 173: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 173: a long session ends when the candle dies", "AA"),
        "round 173: a long session ends when the candle dies",
    ),
    (("round 173: encode the prompt then map the result", "key"), "bssxh 173: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 173: encode the prompt then map the result", "lemon"), "csgbq 173: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 173: encode the prompt then map the result", "a"), "round 173: encode the prompt then map the result"),
    (("round 173: encode the prompt then map the result", "zz"), "qntmc 173: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 173: encode the prompt then map the result", "AgentU"),
        "ruyaw 173: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 173: encode the prompt then map the result", "keyboard"),
        "bssor 173: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 173: encode the prompt then map the result", "AA"), "round 173: encode the prompt then map the result"),
    (("round 173: the kernel wakes the worker at dawn", "key"), "bssxh 173: rri iovlop ukocc xfo ambocb er neux"),
    (("round 173: the kernel wakes the worker at dawn", "lemon"), "csgbq 173: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 173: the kernel wakes the worker at dawn", "a"), "round 173: the kernel wakes the worker at dawn"),
    (("round 173: the kernel wakes the worker at dawn", "zz"), "qntmc 173: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 173: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 173: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 173: the kernel wakes the worker at dawn", "keyboard"), "bssor 173: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 173: the kernel wakes the worker at dawn", "AA"), "round 173: the kernel wakes the worker at dawn"),
    (("round 173: service latency drops after the patch", "key"), "bssxh 173: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 173: service latency drops after the patch", "lemon"), "csgbq 173: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 173: service latency drops after the patch", "a"), "round 173: service latency drops after the patch"),
    (("round 173: service latency drops after the patch", "zz"), "qntmc 173: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 173: service latency drops after the patch", "AgentU"),
        "ruyaw 173: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 173: service latency drops after the patch", "keyboard"),
        "bssor 173: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 173: service latency drops after the patch", "AA"), "round 173: service latency drops after the patch"),
    (
        ("round 173: the library caches every vector it sees", "key"),
        "bssxh 173: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 173: the library caches every vector it sees", "lemon"),
        "csgbq 173: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 173: the library caches every vector it sees", "a"), "round 173: the library caches every vector it sees"),
    (
        ("round 173: the library caches every vector it sees", "zz"),
        "qntmc 173: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 173: the library caches every vector it sees", "AgentU"),
        "ruyaw 173: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 173: the library caches every vector it sees", "keyboard"),
        "bssor 173: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 173: the library caches every vector it sees", "AA"),
        "round 173: the library caches every vector it sees",
    ),
    (("round 173: agents argue then the debate resolves", "key"), "bssxh 173: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 173: agents argue then the debate resolves", "lemon"), "csgbq 173: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 173: agents argue then the debate resolves", "a"), "round 173: agents argue then the debate resolves"),
    (("round 173: agents argue then the debate resolves", "zz"), "qntmc 173: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 173: agents argue then the debate resolves", "AgentU"),
        "ruyaw 173: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 173: agents argue then the debate resolves", "keyboard"),
        "bssor 173: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 173: agents argue then the debate resolves", "AA"), "round 173: agents argue then the debate resolves"),
    (("round 173: the filter keeps only strong matches", "key"), "bssxh 173: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 173: the filter keeps only strong matches", "lemon"), "csgbq 173: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 173: the filter keeps only strong matches", "a"), "round 173: the filter keeps only strong matches"),
    (("round 173: the filter keeps only strong matches", "zz"), "qntmc 173: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 173: the filter keeps only strong matches", "AgentU"), "ruyaw 173: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 173: the filter keeps only strong matches", "keyboard"),
        "bssor 173: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 173: the filter keeps only strong matches", "AA"), "round 173: the filter keeps only strong matches"),
    (("round 173: the model answers with a short reply", "key"), "bssxh 173: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 173: the model answers with a short reply", "lemon"), "csgbq 173: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 173: the model answers with a short reply", "a"), "round 173: the model answers with a short reply"),
    (("round 173: the model answers with a short reply", "zz"), "qntmc 173: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 173: the model answers with a short reply", "AgentU"), "ruyaw 173: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 173: the model answers with a short reply", "keyboard"),
        "bssor 173: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 173: the model answers with a short reply", "AA"), "round 173: the model answers with a short reply"),
    (
        ("round 173: the recorder stores the reasoning trace", "key"),
        "bssxh 173: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 173: the recorder stores the reasoning trace", "lemon"),
        "csgbq 173: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 173: the recorder stores the reasoning trace", "a"), "round 173: the recorder stores the reasoning trace"),
    (
        ("round 173: the recorder stores the reasoning trace", "zz"),
        "qntmc 173: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 173: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 173: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 173: the recorder stores the reasoning trace", "keyboard"),
        "bssor 173: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 173: the recorder stores the reasoning trace", "AA"),
        "round 173: the recorder stores the reasoning trace",
    ),
    (("round 173: the angel watches the processor run", "key"), "bssxh 173: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 173: the angel watches the processor run", "lemon"), "csgbq 173: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 173: the angel watches the processor run", "a"), "round 173: the angel watches the processor run"),
    (("round 173: the angel watches the processor run", "zz"), "qntmc 173: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 173: the angel watches the processor run", "AgentU"), "ruyaw 173: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 173: the angel watches the processor run", "keyboard"), "bssor 173: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 173: the angel watches the processor run", "AA"), "round 173: the angel watches the processor run"),
    (("round 173: angle of the vector decides the match", "key"), "bssxh 173: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 173: angle of the vector decides the match", "lemon"), "csgbq 173: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 173: angle of the vector decides the match", "a"), "round 173: angle of the vector decides the match"),
    (("round 173: angle of the vector decides the match", "zz"), "qntmc 173: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 173: angle of the vector decides the match", "AgentU"),
        "ruyaw 173: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 173: angle of the vector decides the match", "keyboard"),
        "bssor 173: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 173: angle of the vector decides the match", "AA"), "round 173: angle of the vector decides the match"),
    (
        ("round 173: the candle burns twice as long at night", "key"),
        "bssxh 173: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 173: the candle burns twice as long at night", "lemon"),
        "csgbq 173: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 173: the candle burns twice as long at night", "a"), "round 173: the candle burns twice as long at night"),
    (
        ("round 173: the candle burns twice as long at night", "zz"),
        "qntmc 173: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 173: the candle burns twice as long at night", "AgentU"),
        "ruyaw 173: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 173: the candle burns twice as long at night", "keyboard"),
        "bssor 173: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 173: the candle burns twice as long at night", "AA"),
        "round 173: the candle burns twice as long at night",
    ),
    (("round 173: a mirror of the universe in one line", "key"), "bssxh 173: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 173: a mirror of the universe in one line", "lemon"), "csgbq 173: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 173: a mirror of the universe in one line", "a"), "round 173: a mirror of the universe in one line"),
    (("round 173: a mirror of the universe in one line", "zz"), "qntmc 173: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 173: a mirror of the universe in one line", "AgentU"), "ruyaw 173: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 173: a mirror of the universe in one line", "keyboard"),
        "bssor 173: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 173: a mirror of the universe in one line", "AA"), "round 173: a mirror of the universe in one line"),
    (("round 173: the queue drains before the storm", "key"), "bssxh 173: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 173: the queue drains before the storm", "lemon"), "csgbq 173: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 173: the queue drains before the storm", "a"), "round 173: the queue drains before the storm"),
    (("round 173: the queue drains before the storm", "zz"), "qntmc 173: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 173: the queue drains before the storm", "AgentU"), "ruyaw 173: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 173: the queue drains before the storm", "keyboard"), "bssor 173: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 173: the queue drains before the storm", "AA"), "round 173: the queue drains before the storm"),
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
