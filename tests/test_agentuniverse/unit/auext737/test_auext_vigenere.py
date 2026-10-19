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
    (("kitten737", "key"), "umrdil737"),
    (("kitten737", "lemon"), "vmfhry737"),
    (("kitten737", "a"), "kitten737"),
    (("kitten737", "zz"), "jhssdm737"),
    (("kitten737", "AgentU"), "koxgxh737"),
    (("kitten737", "keyboard"), "umrusn737"),
    (("kitten737", "AA"), "kitten737"),
    (("sitting737", "key"), "cmrdmlq737"),
    (("sitting737", "lemon"), "dmfhvyk737"),
    (("sitting737", "a"), "sitting737"),
    (("sitting737", "zz"), "rhsshmf737"),
    (("sitting737", "AgentU"), "soxgbhg737"),
    (("sitting737", "keyboard"), "cmruwnx737"),
    (("sitting737", "AA"), "sitting737"),
    (("agent737", "key"), "kkcxx737"),
    (("agent737", "lemon"), "lkqbg737"),
    (("agent737", "a"), "agent737"),
    (("agent737", "zz"), "zfdms737"),
    (("agent737", "AgentU"), "amiam737"),
    (("agent737", "keyboard"), "kkcoh737"),
    (("agent737", "AA"), "agent737"),
    (("angle737", "key"), "krevi737"),
    (("angle737", "lemon"), "lrszr737"),
    (("angle737", "a"), "angle737"),
    (("angle737", "zz"), "zmfkd737"),
    (("angle737", "AgentU"), "atkyx737"),
    (("angle737", "keyboard"), "krems737"),
    (("angle737", "AA"), "angle737"),
    (("universe737", "key"), "ergfipci737"),
    (("universe737", "lemon"), "frujrcwq737"),
    (("universe737", "a"), "universe737"),
    (("universe737", "zz"), "tmhudqrd737"),
    (("universe737", "AgentU"), "utmixlsk737"),
    (("universe737", "keyboard"), "ergwsrjh737"),
    (("universe737", "AA"), "universe737"),
    (("memory737", "key"), "wikyvw737"),
    (("memory737", "lemon"), "xiycej737"),
    (("memory737", "a"), "memory737"),
    (("memory737", "zz"), "ldlnqx737"),
    (("memory737", "AgentU"), "mkqbks737"),
    (("memory737", "keyboard"), "wikpfy737"),
    (("memory737", "AA"), "memory737"),
    (("stream737", "key"), "cxpoek737"),
    (("stream737", "lemon"), "dxdsnx737"),
    (("stream737", "a"), "stream737"),
    (("stream737", "zz"), "rsqdzl737"),
    (("stream737", "AgentU"), "szvrtg737"),
    (("stream737", "keyboard"), "cxpfom737"),
    (("stream737", "AA"), "stream737"),
    (("context737", "key"), "msldivd737"),
    (("context737", "lemon"), "nszhrix737"),
    (("context737", "a"), "context737"),
    (("context737", "zz"), "bnmsdws737"),
    (("context737", "AgentU"), "curgxrt737"),
    (("context737", "keyboard"), "mslusxk737"),
    (("context737", "AA"), "context737"),
    (("knowledge737", "key"), "urmgpcnkc737"),
    (("knowledge737", "lemon"), "vrakyphss737"),
    (("knowledge737", "a"), "knowledge737"),
    (("knowledge737", "zz"), "jmnvkdcfd737"),
    (("knowledge737", "AgentU"), "ktsjeydmi737"),
    (("knowledge737", "keyboard"), "urmxzeujo737"),
    (("knowledge737", "AA"), "knowledge737"),
    (("vector737", "key"), "fiadsp737"),
    (("vector737", "lemon"), "giohbc737"),
    (("vector737", "a"), "vector737"),
    (("vector737", "zz"), "udbsnq737"),
    (("vector737", "AgentU"), "vkgghl737"),
    (("vector737", "keyboard"), "fiaucr737"),
    (("vector737", "AA"), "vector737"),
    (("processor737", "key"), "zvmmiqcsp737"),
    (("processor737", "lemon"), "avaqrdwaf737"),
    (("processor737", "a"), "processor737"),
    (("processor737", "zz"), "oqnbdrrnq737"),
    (("processor737", "AgentU"), "pxspxmsuv737"),
    (("processor737", "keyboard"), "zvmdssjrb737"),
    (("processor737", "AA"), "processor737"),
    (("reasoning737", "key"), "biycslsre737"),
    (("reasoning737", "lemon"), "cimgbymzu737"),
    (("reasoning737", "a"), "reasoning737"),
    (("reasoning737", "zz"), "qdzrnmhmf737"),
    (("reasoning737", "AgentU"), "rkefhhitk737"),
    (("reasoning737", "keyboard"), "biytcnzqq737"),
    (("reasoning737", "AA"), "reasoning737"),
    (("machine737", "key"), "wearmlo737"),
    (("machine737", "lemon"), "xeovvyi737"),
    (("machine737", "a"), "machine737"),
    (("machine737", "zz"), "lzbghmd737"),
    (("machine737", "AgentU"), "mggubhe737"),
    (("machine737", "keyboard"), "weaiwnv737"),
    (("machine737", "AA"), "machine737"),
    (("learning737", "key"), "viybrgxk737"),
    (("learning737", "lemon"), "wimfatrs737"),
    (("learning737", "a"), "learning737"),
    (("learning737", "zz"), "kdzqmhmf737"),
    (("learning737", "AgentU"), "lkeegcnm737"),
    (("learning737", "keyboard"), "viysbiej737"),
    (("learning737", "AA"), "learning737"),
    (("model737", "key"), "wsbop737"),
    (("model737", "lemon"), "xspsy737"),
    (("model737", "a"), "model737"),
    (("model737", "zz"), "lncdk737"),
    (("model737", "AgentU"), "muhre737"),
    (("model737", "keyboard"), "wsbfz737"),
    (("model737", "AA"), "model737"),
    (("token737", "key"), "dsior737"),
    (("token737", "lemon"), "eswsa737"),
    (("token737", "a"), "token737"),
    (("token737", "zz"), "snjdm737"),
    (("token737", "AgentU"), "tuorg737"),
    (("token737", "keyboard"), "dsifb737"),
    (("token737", "AA"), "token737"),
    (("prompt737", "key"), "zvmwtr737"),
    (("prompt737", "lemon"), "avaace737"),
    (("prompt737", "a"), "prompt737"),
    (("prompt737", "zz"), "oqnlos737"),
    (("prompt737", "AgentU"), "pxszin737"),
    (("prompt737", "keyboard"), "zvmndt737"),
    (("prompt737", "AA"), "prompt737"),
    (("session737", "key"), "ciqcmmx737"),
    (("session737", "lemon"), "diegvzr737"),
    (("session737", "a"), "session737"),
    (("session737", "zz"), "rdrrhnm737"),
    (("session737", "AgentU"), "skwfbin737"),
    (("session737", "keyboard"), "ciqtwoe737"),
    (("session737", "AA"), "session737"),
    (("library737", "key"), "vmzbepi737"),
    (("library737", "lemon"), "wmnfncc737"),
    (("library737", "a"), "library737"),
    (("library737", "zz"), "khaqzqx737"),
    (("library737", "AgentU"), "lofetly737"),
    (("library737", "keyboard"), "vmzsorp737"),
    (("library737", "AA"), "library737"),
    (("service737", "key"), "cipfmao737"),
    (("service737", "lemon"), "didjvni737"),
    (("service737", "a"), "service737"),
    (("service737", "zz"), "rdquhbd737"),
    (("service737", "AgentU"), "skvibwe737"),
    (("service737", "keyboard"), "cipwwcv737"),
    (("service737", "AA"), "service737"),
    (("gateway737", "key"), "qeroayi737"),
    (("gateway737", "lemon"), "refsjlc737"),
    (("gateway737", "a"), "gateway737"),
    (("gateway737", "zz"), "fzsdvzx737"),
    (("gateway737", "AgentU"), "ggxrpuy737"),
    (("gateway737", "keyboard"), "qerfkap737"),
    (("gateway737", "AA"), "gateway737"),
    (("storage737", "key"), "cxmbeeo737"),
    (("storage737", "lemon"), "dxafnri737"),
    (("storage737", "a"), "storage737"),
    (("storage737", "zz"), "rsnqzfd737"),
    (("storage737", "AgentU"), "szsetae737"),
    (("storage737", "keyboard"), "cxmsogv737"),
    (("storage737", "AA"), "storage737"),
    (("network737", "key"), "xirgspu737"),
    (("network737", "lemon"), "yifkbco737"),
    (("network737", "a"), "network737"),
    (("network737", "zz"), "mdsvnqj737"),
    (("network737", "AgentU"), "nkxjhlk737"),
    (("network737", "keyboard"), "xirxcrb737"),
    (("network737", "AA"), "network737"),
    (("latency737", "key"), "verorai737"),
    (("latency737", "lemon"), "wefsanc737"),
    (("latency737", "a"), "latency737"),
    (("latency737", "zz"), "kzsdmbx737"),
    (("latency737", "AgentU"), "lgxrgwy737"),
    (("latency737", "keyboard"), "verfbcp737"),
    (("latency737", "AA"), "latency737"),
    (("buffer737", "key"), "lydpip737"),
    (("buffer737", "lemon"), "myrtrc737"),
    (("buffer737", "a"), "buffer737"),
    (("buffer737", "zz"), "ateedq737"),
    (("buffer737", "AgentU"), "bajsxl737"),
    (("buffer737", "keyboard"), "lydgsr737"),
    (("buffer737", "AA"), "buffer737"),
    (("queue737", "key"), "aycei737"),
    (("queue737", "lemon"), "byqir737"),
    (("queue737", "a"), "queue737"),
    (("queue737", "zz"), "ptdtd737"),
    (("queue737", "AgentU"), "qaihx737"),
    (("queue737", "keyboard"), "aycvs737"),
    (("queue737", "AA"), "queue737"),
    (("worker737", "key"), "gspuip737"),
    (("worker737", "lemon"), "hsdyrc737"),
    (("worker737", "a"), "worker737"),
    (("worker737", "zz"), "vnqjdq737"),
    (("worker737", "AgentU"), "wuvxxl737"),
    (("worker737", "keyboard"), "gsplsr737"),
    (("worker737", "AA"), "worker737"),
    (("kernel737", "key"), "uipxij737"),
    (("kernel737", "lemon"), "vidbrw737"),
    (("kernel737", "a"), "kernel737"),
    (("kernel737", "zz"), "jdqmdk737"),
    (("kernel737", "AgentU"), "kkvaxf737"),
    (("kernel737", "keyboard"), "uiposl737"),
    (("kernel737", "AA"), "kernel737"),
    (("signal737", "key"), "cmexej737"),
    (("signal737", "lemon"), "dmsbnw737"),
    (("signal737", "a"), "signal737"),
    (("signal737", "zz"), "rhfmzk737"),
    (("signal737", "AgentU"), "sokatf737"),
    (("signal737", "keyboard"), "cmeool737"),
    (("signal737", "AA"), "signal737"),
    (("packet737", "key"), "zeauir737"),
    (("packet737", "lemon"), "aeoyre737"),
    (("packet737", "a"), "packet737"),
    (("packet737", "zz"), "ozbjds737"),
    (("packet737", "AgentU"), "pggxxn737"),
    (("packet737", "keyboard"), "zealst737"),
    (("packet737", "AA"), "packet737"),
    (("router737", "key"), "bssdip737"),
    (("router737", "lemon"), "csghrc737"),
    (("router737", "a"), "router737"),
    (("router737", "zz"), "qntsdq737"),
    (("router737", "AgentU"), "ruygxl737"),
    (("router737", "keyboard"), "bssusr737"),
    (("router737", "AA"), "router737"),
    (("cluster737", "key"), "mpscxcb737"),
    (("cluster737", "lemon"), "npgggpv737"),
    (("cluster737", "a"), "cluster737"),
    (("cluster737", "zz"), "bktrsdq737"),
    (("cluster737", "AgentU"), "cryfmyr737"),
    (("cluster737", "keyboard"), "mpsthei737"),
    (("cluster737", "AA"), "cluster737"),
    (("mirror737", "key"), "wmpbsp737"),
    (("mirror737", "lemon"), "xmdfbc737"),
    (("mirror737", "a"), "mirror737"),
    (("mirror737", "zz"), "lhqqnq737"),
    (("mirror737", "AgentU"), "movehl737"),
    (("mirror737", "keyboard"), "wmpscr737"),
    (("mirror737", "AA"), "mirror737"),
    (("filter737", "key"), "pmjdip737"),
    (("filter737", "lemon"), "qmxhrc737"),
    (("filter737", "a"), "filter737"),
    (("filter737", "zz"), "ehksdq737"),
    (("filter737", "AgentU"), "fopgxl737"),
    (("filter737", "keyboard"), "pmjusr737"),
    (("filter737", "AA"), "filter737"),
    (("ranking737", "key"), "belumlq737"),
    (("ranking737", "lemon"), "cezyvyk737"),
    (("ranking737", "a"), "ranking737"),
    (("ranking737", "zz"), "qzmjhmf737"),
    (("ranking737", "AgentU"), "rgrxbhg737"),
    (("ranking737", "keyboard"), "bellwnx737"),
    (("ranking737", "AA"), "ranking737"),
    (("encoding737", "key"), "orayhgxk737"),
    (("encoding737", "lemon"), "procqtrs737"),
    (("encoding737", "a"), "encoding737"),
    (("encoding737", "zz"), "dmbnchmf737"),
    (("encoding737", "AgentU"), "etgbwcnm737"),
    (("encoding737", "keyboard"), "orapriej737"),
    (("encoding737", "AA"), "encoding737"),
    (("mapping737", "key"), "wenzmlq737"),
    (("mapping737", "lemon"), "xebdvyk737"),
    (("mapping737", "a"), "mapping737"),
    (("mapping737", "zz"), "lzoohmf737"),
    (("mapping737", "AgentU"), "mgtcbhg737"),
    (("mapping737", "keyboard"), "wenqwnx737"),
    (("mapping737", "AA"), "mapping737"),
    (("record737", "key"), "biayvb737"),
    (("record737", "lemon"), "cioceo737"),
    (("record737", "a"), "record737"),
    (("record737", "zz"), "qdbnqc737"),
    (("record737", "AgentU"), "rkgbkx737"),
    (("record737", "keyboard"), "biapfd737"),
    (("record737", "AA"), "record737"),
    (("candle737", "key"), "melnpc737"),
    (("candle737", "lemon"), "nezryp737"),
    (("candle737", "a"), "candle737"),
    (("candle737", "zz"), "bzmckd737"),
    (("candle737", "AgentU"), "cgrqey737"),
    (("candle737", "keyboard"), "meleze737"),
    (("candle737", "AA"), "candle737"),
    (("thread737", "key"), "dlpoeb737"),
    (("thread737", "lemon"), "eldsno737"),
    (("thread737", "a"), "thread737"),
    (("thread737", "zz"), "sgqdzc737"),
    (("thread737", "AgentU"), "tnvrtx737"),
    (("thread737", "keyboard"), "dlpfod737"),
    (("thread737", "AA"), "thread737"),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 737: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 737: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "a"),
        "round 737: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 737: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 737: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 737: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", "AA"),
        "round 737: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "key"),
        "bssxh 737: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 737: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "a"),
        "round 737: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 737: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 737: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 737: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", "AA"),
        "round 737: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 737: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 737: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "a"),
        "round 737: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 737: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 737: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 737: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", "AA"),
        "round 737: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 737: the processor reads the record then stops", "key"),
        "bssxh 737: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 737: the processor reads the record then stops", "lemon"),
        "csgbq 737: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 737: the processor reads the record then stops", "a"),
        "round 737: the processor reads the record then stops",
    ),
    (
        ("round 737: the processor reads the record then stops", "zz"),
        "qntmc 737: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 737: the processor reads the record then stops", "AgentU"),
        "ruyaw 737: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 737: the processor reads the record then stops", "keyboard"),
        "bssor 737: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 737: the processor reads the record then stops", "AA"),
        "round 737: the processor reads the record then stops",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "key"),
        "bssxh 737: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "lemon"),
        "csgbq 737: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "a"),
        "round 737: a worker pulls the next task from the queue",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "zz"),
        "qntmc 737: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 737: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "keyboard"),
        "bssor 737: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 737: a worker pulls the next task from the queue", "AA"),
        "round 737: a worker pulls the next task from the queue",
    ),
    (
        ("round 737: signals travel through the network layer", "key"),
        "bssxh 737: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 737: signals travel through the network layer", "lemon"),
        "csgbq 737: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 737: signals travel through the network layer", "a"),
        "round 737: signals travel through the network layer",
    ),
    (
        ("round 737: signals travel through the network layer", "zz"),
        "qntmc 737: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 737: signals travel through the network layer", "AgentU"),
        "ruyaw 737: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 737: signals travel through the network layer", "keyboard"),
        "bssor 737: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 737: signals travel through the network layer", "AA"),
        "round 737: signals travel through the network layer",
    ),
    (
        ("round 737: the gateway routes each request by policy", "key"),
        "bssxh 737: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 737: the gateway routes each request by policy", "lemon"),
        "csgbq 737: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 737: the gateway routes each request by policy", "a"),
        "round 737: the gateway routes each request by policy",
    ),
    (
        ("round 737: the gateway routes each request by policy", "zz"),
        "qntmc 737: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 737: the gateway routes each request by policy", "AgentU"),
        "ruyaw 737: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 737: the gateway routes each request by policy", "keyboard"),
        "bssor 737: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 737: the gateway routes each request by policy", "AA"),
        "round 737: the gateway routes each request by policy",
    ),
    (("round 737: memory grows until the buffer is full", "key"), "bssxh 737: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 737: memory grows until the buffer is full", "lemon"), "csgbq 737: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 737: memory grows until the buffer is full", "a"), "round 737: memory grows until the buffer is full"),
    (("round 737: memory grows until the buffer is full", "zz"), "qntmc 737: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 737: memory grows until the buffer is full", "AgentU"),
        "ruyaw 737: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 737: memory grows until the buffer is full", "keyboard"),
        "bssor 737: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 737: memory grows until the buffer is full", "AA"), "round 737: memory grows until the buffer is full"),
    (("round 737: the cluster mirrors every packet twice", "key"), "bssxh 737: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 737: the cluster mirrors every packet twice", "lemon"),
        "csgbq 737: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 737: the cluster mirrors every packet twice", "a"), "round 737: the cluster mirrors every packet twice"),
    (("round 737: the cluster mirrors every packet twice", "zz"), "qntmc 737: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 737: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 737: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 737: the cluster mirrors every packet twice", "keyboard"),
        "bssor 737: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 737: the cluster mirrors every packet twice", "AA"), "round 737: the cluster mirrors every packet twice"),
    (
        ("round 737: ranking uses tokens learned from the corpus", "key"),
        "bssxh 737: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 737: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", "a"),
        "round 737: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 737: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 737: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 737: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", "AA"),
        "round 737: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 737: a long session ends when the candle dies", "key"),
        "bssxh 737: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 737: a long session ends when the candle dies", "lemon"),
        "csgbq 737: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 737: a long session ends when the candle dies", "a"),
        "round 737: a long session ends when the candle dies",
    ),
    (
        ("round 737: a long session ends when the candle dies", "zz"),
        "qntmc 737: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 737: a long session ends when the candle dies", "AgentU"),
        "ruyaw 737: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 737: a long session ends when the candle dies", "keyboard"),
        "bssor 737: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 737: a long session ends when the candle dies", "AA"),
        "round 737: a long session ends when the candle dies",
    ),
    (("round 737: encode the prompt then map the result", "key"), "bssxh 737: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 737: encode the prompt then map the result", "lemon"), "csgbq 737: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 737: encode the prompt then map the result", "a"), "round 737: encode the prompt then map the result"),
    (("round 737: encode the prompt then map the result", "zz"), "qntmc 737: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 737: encode the prompt then map the result", "AgentU"),
        "ruyaw 737: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 737: encode the prompt then map the result", "keyboard"),
        "bssor 737: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 737: encode the prompt then map the result", "AA"), "round 737: encode the prompt then map the result"),
    (("round 737: the kernel wakes the worker at dawn", "key"), "bssxh 737: rri iovlop ukocc xfo ambocb er neux"),
    (("round 737: the kernel wakes the worker at dawn", "lemon"), "csgbq 737: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 737: the kernel wakes the worker at dawn", "a"), "round 737: the kernel wakes the worker at dawn"),
    (("round 737: the kernel wakes the worker at dawn", "zz"), "qntmc 737: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 737: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 737: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 737: the kernel wakes the worker at dawn", "keyboard"), "bssor 737: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 737: the kernel wakes the worker at dawn", "AA"), "round 737: the kernel wakes the worker at dawn"),
    (("round 737: service latency drops after the patch", "key"), "bssxh 737: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 737: service latency drops after the patch", "lemon"), "csgbq 737: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 737: service latency drops after the patch", "a"), "round 737: service latency drops after the patch"),
    (("round 737: service latency drops after the patch", "zz"), "qntmc 737: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 737: service latency drops after the patch", "AgentU"),
        "ruyaw 737: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 737: service latency drops after the patch", "keyboard"),
        "bssor 737: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 737: service latency drops after the patch", "AA"), "round 737: service latency drops after the patch"),
    (
        ("round 737: the library caches every vector it sees", "key"),
        "bssxh 737: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 737: the library caches every vector it sees", "lemon"),
        "csgbq 737: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 737: the library caches every vector it sees", "a"), "round 737: the library caches every vector it sees"),
    (
        ("round 737: the library caches every vector it sees", "zz"),
        "qntmc 737: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 737: the library caches every vector it sees", "AgentU"),
        "ruyaw 737: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 737: the library caches every vector it sees", "keyboard"),
        "bssor 737: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 737: the library caches every vector it sees", "AA"),
        "round 737: the library caches every vector it sees",
    ),
    (("round 737: agents argue then the debate resolves", "key"), "bssxh 737: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 737: agents argue then the debate resolves", "lemon"), "csgbq 737: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 737: agents argue then the debate resolves", "a"), "round 737: agents argue then the debate resolves"),
    (("round 737: agents argue then the debate resolves", "zz"), "qntmc 737: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 737: agents argue then the debate resolves", "AgentU"),
        "ruyaw 737: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 737: agents argue then the debate resolves", "keyboard"),
        "bssor 737: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 737: agents argue then the debate resolves", "AA"), "round 737: agents argue then the debate resolves"),
    (("round 737: the filter keeps only strong matches", "key"), "bssxh 737: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 737: the filter keeps only strong matches", "lemon"), "csgbq 737: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 737: the filter keeps only strong matches", "a"), "round 737: the filter keeps only strong matches"),
    (("round 737: the filter keeps only strong matches", "zz"), "qntmc 737: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 737: the filter keeps only strong matches", "AgentU"), "ruyaw 737: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 737: the filter keeps only strong matches", "keyboard"),
        "bssor 737: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 737: the filter keeps only strong matches", "AA"), "round 737: the filter keeps only strong matches"),
    (("round 737: the model answers with a short reply", "key"), "bssxh 737: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 737: the model answers with a short reply", "lemon"), "csgbq 737: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 737: the model answers with a short reply", "a"), "round 737: the model answers with a short reply"),
    (("round 737: the model answers with a short reply", "zz"), "qntmc 737: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 737: the model answers with a short reply", "AgentU"), "ruyaw 737: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 737: the model answers with a short reply", "keyboard"),
        "bssor 737: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 737: the model answers with a short reply", "AA"), "round 737: the model answers with a short reply"),
    (
        ("round 737: the recorder stores the reasoning trace", "key"),
        "bssxh 737: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 737: the recorder stores the reasoning trace", "lemon"),
        "csgbq 737: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 737: the recorder stores the reasoning trace", "a"), "round 737: the recorder stores the reasoning trace"),
    (
        ("round 737: the recorder stores the reasoning trace", "zz"),
        "qntmc 737: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 737: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 737: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 737: the recorder stores the reasoning trace", "keyboard"),
        "bssor 737: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 737: the recorder stores the reasoning trace", "AA"),
        "round 737: the recorder stores the reasoning trace",
    ),
    (("round 737: the angel watches the processor run", "key"), "bssxh 737: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 737: the angel watches the processor run", "lemon"), "csgbq 737: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 737: the angel watches the processor run", "a"), "round 737: the angel watches the processor run"),
    (("round 737: the angel watches the processor run", "zz"), "qntmc 737: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 737: the angel watches the processor run", "AgentU"), "ruyaw 737: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 737: the angel watches the processor run", "keyboard"), "bssor 737: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 737: the angel watches the processor run", "AA"), "round 737: the angel watches the processor run"),
    (("round 737: angle of the vector decides the match", "key"), "bssxh 737: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 737: angle of the vector decides the match", "lemon"), "csgbq 737: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 737: angle of the vector decides the match", "a"), "round 737: angle of the vector decides the match"),
    (("round 737: angle of the vector decides the match", "zz"), "qntmc 737: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 737: angle of the vector decides the match", "AgentU"),
        "ruyaw 737: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 737: angle of the vector decides the match", "keyboard"),
        "bssor 737: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 737: angle of the vector decides the match", "AA"), "round 737: angle of the vector decides the match"),
    (
        ("round 737: the candle burns twice as long at night", "key"),
        "bssxh 737: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 737: the candle burns twice as long at night", "lemon"),
        "csgbq 737: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 737: the candle burns twice as long at night", "a"), "round 737: the candle burns twice as long at night"),
    (
        ("round 737: the candle burns twice as long at night", "zz"),
        "qntmc 737: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 737: the candle burns twice as long at night", "AgentU"),
        "ruyaw 737: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 737: the candle burns twice as long at night", "keyboard"),
        "bssor 737: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 737: the candle burns twice as long at night", "AA"),
        "round 737: the candle burns twice as long at night",
    ),
    (("round 737: a mirror of the universe in one line", "key"), "bssxh 737: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 737: a mirror of the universe in one line", "lemon"), "csgbq 737: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 737: a mirror of the universe in one line", "a"), "round 737: a mirror of the universe in one line"),
    (("round 737: a mirror of the universe in one line", "zz"), "qntmc 737: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 737: a mirror of the universe in one line", "AgentU"), "ruyaw 737: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 737: a mirror of the universe in one line", "keyboard"),
        "bssor 737: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 737: a mirror of the universe in one line", "AA"), "round 737: a mirror of the universe in one line"),
    (("round 737: the queue drains before the storm", "key"), "bssxh 737: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 737: the queue drains before the storm", "lemon"), "csgbq 737: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 737: the queue drains before the storm", "a"), "round 737: the queue drains before the storm"),
    (("round 737: the queue drains before the storm", "zz"), "qntmc 737: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 737: the queue drains before the storm", "AgentU"), "ruyaw 737: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 737: the queue drains before the storm", "keyboard"), "bssor 737: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 737: the queue drains before the storm", "AA"), "round 737: the queue drains before the storm"),
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
