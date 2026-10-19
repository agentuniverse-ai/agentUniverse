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
    (("kitten155", "key"), "umrdil155"),
    (("kitten155", "lemon"), "vmfhry155"),
    (("kitten155", "a"), "kitten155"),
    (("kitten155", "zz"), "jhssdm155"),
    (("kitten155", "AgentU"), "koxgxh155"),
    (("kitten155", "keyboard"), "umrusn155"),
    (("kitten155", "AA"), "kitten155"),
    (("sitting155", "key"), "cmrdmlq155"),
    (("sitting155", "lemon"), "dmfhvyk155"),
    (("sitting155", "a"), "sitting155"),
    (("sitting155", "zz"), "rhsshmf155"),
    (("sitting155", "AgentU"), "soxgbhg155"),
    (("sitting155", "keyboard"), "cmruwnx155"),
    (("sitting155", "AA"), "sitting155"),
    (("agent155", "key"), "kkcxx155"),
    (("agent155", "lemon"), "lkqbg155"),
    (("agent155", "a"), "agent155"),
    (("agent155", "zz"), "zfdms155"),
    (("agent155", "AgentU"), "amiam155"),
    (("agent155", "keyboard"), "kkcoh155"),
    (("agent155", "AA"), "agent155"),
    (("angle155", "key"), "krevi155"),
    (("angle155", "lemon"), "lrszr155"),
    (("angle155", "a"), "angle155"),
    (("angle155", "zz"), "zmfkd155"),
    (("angle155", "AgentU"), "atkyx155"),
    (("angle155", "keyboard"), "krems155"),
    (("angle155", "AA"), "angle155"),
    (("universe155", "key"), "ergfipci155"),
    (("universe155", "lemon"), "frujrcwq155"),
    (("universe155", "a"), "universe155"),
    (("universe155", "zz"), "tmhudqrd155"),
    (("universe155", "AgentU"), "utmixlsk155"),
    (("universe155", "keyboard"), "ergwsrjh155"),
    (("universe155", "AA"), "universe155"),
    (("memory155", "key"), "wikyvw155"),
    (("memory155", "lemon"), "xiycej155"),
    (("memory155", "a"), "memory155"),
    (("memory155", "zz"), "ldlnqx155"),
    (("memory155", "AgentU"), "mkqbks155"),
    (("memory155", "keyboard"), "wikpfy155"),
    (("memory155", "AA"), "memory155"),
    (("stream155", "key"), "cxpoek155"),
    (("stream155", "lemon"), "dxdsnx155"),
    (("stream155", "a"), "stream155"),
    (("stream155", "zz"), "rsqdzl155"),
    (("stream155", "AgentU"), "szvrtg155"),
    (("stream155", "keyboard"), "cxpfom155"),
    (("stream155", "AA"), "stream155"),
    (("context155", "key"), "msldivd155"),
    (("context155", "lemon"), "nszhrix155"),
    (("context155", "a"), "context155"),
    (("context155", "zz"), "bnmsdws155"),
    (("context155", "AgentU"), "curgxrt155"),
    (("context155", "keyboard"), "mslusxk155"),
    (("context155", "AA"), "context155"),
    (("knowledge155", "key"), "urmgpcnkc155"),
    (("knowledge155", "lemon"), "vrakyphss155"),
    (("knowledge155", "a"), "knowledge155"),
    (("knowledge155", "zz"), "jmnvkdcfd155"),
    (("knowledge155", "AgentU"), "ktsjeydmi155"),
    (("knowledge155", "keyboard"), "urmxzeujo155"),
    (("knowledge155", "AA"), "knowledge155"),
    (("vector155", "key"), "fiadsp155"),
    (("vector155", "lemon"), "giohbc155"),
    (("vector155", "a"), "vector155"),
    (("vector155", "zz"), "udbsnq155"),
    (("vector155", "AgentU"), "vkgghl155"),
    (("vector155", "keyboard"), "fiaucr155"),
    (("vector155", "AA"), "vector155"),
    (("processor155", "key"), "zvmmiqcsp155"),
    (("processor155", "lemon"), "avaqrdwaf155"),
    (("processor155", "a"), "processor155"),
    (("processor155", "zz"), "oqnbdrrnq155"),
    (("processor155", "AgentU"), "pxspxmsuv155"),
    (("processor155", "keyboard"), "zvmdssjrb155"),
    (("processor155", "AA"), "processor155"),
    (("reasoning155", "key"), "biycslsre155"),
    (("reasoning155", "lemon"), "cimgbymzu155"),
    (("reasoning155", "a"), "reasoning155"),
    (("reasoning155", "zz"), "qdzrnmhmf155"),
    (("reasoning155", "AgentU"), "rkefhhitk155"),
    (("reasoning155", "keyboard"), "biytcnzqq155"),
    (("reasoning155", "AA"), "reasoning155"),
    (("machine155", "key"), "wearmlo155"),
    (("machine155", "lemon"), "xeovvyi155"),
    (("machine155", "a"), "machine155"),
    (("machine155", "zz"), "lzbghmd155"),
    (("machine155", "AgentU"), "mggubhe155"),
    (("machine155", "keyboard"), "weaiwnv155"),
    (("machine155", "AA"), "machine155"),
    (("learning155", "key"), "viybrgxk155"),
    (("learning155", "lemon"), "wimfatrs155"),
    (("learning155", "a"), "learning155"),
    (("learning155", "zz"), "kdzqmhmf155"),
    (("learning155", "AgentU"), "lkeegcnm155"),
    (("learning155", "keyboard"), "viysbiej155"),
    (("learning155", "AA"), "learning155"),
    (("model155", "key"), "wsbop155"),
    (("model155", "lemon"), "xspsy155"),
    (("model155", "a"), "model155"),
    (("model155", "zz"), "lncdk155"),
    (("model155", "AgentU"), "muhre155"),
    (("model155", "keyboard"), "wsbfz155"),
    (("model155", "AA"), "model155"),
    (("token155", "key"), "dsior155"),
    (("token155", "lemon"), "eswsa155"),
    (("token155", "a"), "token155"),
    (("token155", "zz"), "snjdm155"),
    (("token155", "AgentU"), "tuorg155"),
    (("token155", "keyboard"), "dsifb155"),
    (("token155", "AA"), "token155"),
    (("prompt155", "key"), "zvmwtr155"),
    (("prompt155", "lemon"), "avaace155"),
    (("prompt155", "a"), "prompt155"),
    (("prompt155", "zz"), "oqnlos155"),
    (("prompt155", "AgentU"), "pxszin155"),
    (("prompt155", "keyboard"), "zvmndt155"),
    (("prompt155", "AA"), "prompt155"),
    (("session155", "key"), "ciqcmmx155"),
    (("session155", "lemon"), "diegvzr155"),
    (("session155", "a"), "session155"),
    (("session155", "zz"), "rdrrhnm155"),
    (("session155", "AgentU"), "skwfbin155"),
    (("session155", "keyboard"), "ciqtwoe155"),
    (("session155", "AA"), "session155"),
    (("library155", "key"), "vmzbepi155"),
    (("library155", "lemon"), "wmnfncc155"),
    (("library155", "a"), "library155"),
    (("library155", "zz"), "khaqzqx155"),
    (("library155", "AgentU"), "lofetly155"),
    (("library155", "keyboard"), "vmzsorp155"),
    (("library155", "AA"), "library155"),
    (("service155", "key"), "cipfmao155"),
    (("service155", "lemon"), "didjvni155"),
    (("service155", "a"), "service155"),
    (("service155", "zz"), "rdquhbd155"),
    (("service155", "AgentU"), "skvibwe155"),
    (("service155", "keyboard"), "cipwwcv155"),
    (("service155", "AA"), "service155"),
    (("gateway155", "key"), "qeroayi155"),
    (("gateway155", "lemon"), "refsjlc155"),
    (("gateway155", "a"), "gateway155"),
    (("gateway155", "zz"), "fzsdvzx155"),
    (("gateway155", "AgentU"), "ggxrpuy155"),
    (("gateway155", "keyboard"), "qerfkap155"),
    (("gateway155", "AA"), "gateway155"),
    (("storage155", "key"), "cxmbeeo155"),
    (("storage155", "lemon"), "dxafnri155"),
    (("storage155", "a"), "storage155"),
    (("storage155", "zz"), "rsnqzfd155"),
    (("storage155", "AgentU"), "szsetae155"),
    (("storage155", "keyboard"), "cxmsogv155"),
    (("storage155", "AA"), "storage155"),
    (("network155", "key"), "xirgspu155"),
    (("network155", "lemon"), "yifkbco155"),
    (("network155", "a"), "network155"),
    (("network155", "zz"), "mdsvnqj155"),
    (("network155", "AgentU"), "nkxjhlk155"),
    (("network155", "keyboard"), "xirxcrb155"),
    (("network155", "AA"), "network155"),
    (("latency155", "key"), "verorai155"),
    (("latency155", "lemon"), "wefsanc155"),
    (("latency155", "a"), "latency155"),
    (("latency155", "zz"), "kzsdmbx155"),
    (("latency155", "AgentU"), "lgxrgwy155"),
    (("latency155", "keyboard"), "verfbcp155"),
    (("latency155", "AA"), "latency155"),
    (("buffer155", "key"), "lydpip155"),
    (("buffer155", "lemon"), "myrtrc155"),
    (("buffer155", "a"), "buffer155"),
    (("buffer155", "zz"), "ateedq155"),
    (("buffer155", "AgentU"), "bajsxl155"),
    (("buffer155", "keyboard"), "lydgsr155"),
    (("buffer155", "AA"), "buffer155"),
    (("queue155", "key"), "aycei155"),
    (("queue155", "lemon"), "byqir155"),
    (("queue155", "a"), "queue155"),
    (("queue155", "zz"), "ptdtd155"),
    (("queue155", "AgentU"), "qaihx155"),
    (("queue155", "keyboard"), "aycvs155"),
    (("queue155", "AA"), "queue155"),
    (("worker155", "key"), "gspuip155"),
    (("worker155", "lemon"), "hsdyrc155"),
    (("worker155", "a"), "worker155"),
    (("worker155", "zz"), "vnqjdq155"),
    (("worker155", "AgentU"), "wuvxxl155"),
    (("worker155", "keyboard"), "gsplsr155"),
    (("worker155", "AA"), "worker155"),
    (("kernel155", "key"), "uipxij155"),
    (("kernel155", "lemon"), "vidbrw155"),
    (("kernel155", "a"), "kernel155"),
    (("kernel155", "zz"), "jdqmdk155"),
    (("kernel155", "AgentU"), "kkvaxf155"),
    (("kernel155", "keyboard"), "uiposl155"),
    (("kernel155", "AA"), "kernel155"),
    (("signal155", "key"), "cmexej155"),
    (("signal155", "lemon"), "dmsbnw155"),
    (("signal155", "a"), "signal155"),
    (("signal155", "zz"), "rhfmzk155"),
    (("signal155", "AgentU"), "sokatf155"),
    (("signal155", "keyboard"), "cmeool155"),
    (("signal155", "AA"), "signal155"),
    (("packet155", "key"), "zeauir155"),
    (("packet155", "lemon"), "aeoyre155"),
    (("packet155", "a"), "packet155"),
    (("packet155", "zz"), "ozbjds155"),
    (("packet155", "AgentU"), "pggxxn155"),
    (("packet155", "keyboard"), "zealst155"),
    (("packet155", "AA"), "packet155"),
    (("router155", "key"), "bssdip155"),
    (("router155", "lemon"), "csghrc155"),
    (("router155", "a"), "router155"),
    (("router155", "zz"), "qntsdq155"),
    (("router155", "AgentU"), "ruygxl155"),
    (("router155", "keyboard"), "bssusr155"),
    (("router155", "AA"), "router155"),
    (("cluster155", "key"), "mpscxcb155"),
    (("cluster155", "lemon"), "npgggpv155"),
    (("cluster155", "a"), "cluster155"),
    (("cluster155", "zz"), "bktrsdq155"),
    (("cluster155", "AgentU"), "cryfmyr155"),
    (("cluster155", "keyboard"), "mpsthei155"),
    (("cluster155", "AA"), "cluster155"),
    (("mirror155", "key"), "wmpbsp155"),
    (("mirror155", "lemon"), "xmdfbc155"),
    (("mirror155", "a"), "mirror155"),
    (("mirror155", "zz"), "lhqqnq155"),
    (("mirror155", "AgentU"), "movehl155"),
    (("mirror155", "keyboard"), "wmpscr155"),
    (("mirror155", "AA"), "mirror155"),
    (("filter155", "key"), "pmjdip155"),
    (("filter155", "lemon"), "qmxhrc155"),
    (("filter155", "a"), "filter155"),
    (("filter155", "zz"), "ehksdq155"),
    (("filter155", "AgentU"), "fopgxl155"),
    (("filter155", "keyboard"), "pmjusr155"),
    (("filter155", "AA"), "filter155"),
    (("ranking155", "key"), "belumlq155"),
    (("ranking155", "lemon"), "cezyvyk155"),
    (("ranking155", "a"), "ranking155"),
    (("ranking155", "zz"), "qzmjhmf155"),
    (("ranking155", "AgentU"), "rgrxbhg155"),
    (("ranking155", "keyboard"), "bellwnx155"),
    (("ranking155", "AA"), "ranking155"),
    (("encoding155", "key"), "orayhgxk155"),
    (("encoding155", "lemon"), "procqtrs155"),
    (("encoding155", "a"), "encoding155"),
    (("encoding155", "zz"), "dmbnchmf155"),
    (("encoding155", "AgentU"), "etgbwcnm155"),
    (("encoding155", "keyboard"), "orapriej155"),
    (("encoding155", "AA"), "encoding155"),
    (("mapping155", "key"), "wenzmlq155"),
    (("mapping155", "lemon"), "xebdvyk155"),
    (("mapping155", "a"), "mapping155"),
    (("mapping155", "zz"), "lzoohmf155"),
    (("mapping155", "AgentU"), "mgtcbhg155"),
    (("mapping155", "keyboard"), "wenqwnx155"),
    (("mapping155", "AA"), "mapping155"),
    (("record155", "key"), "biayvb155"),
    (("record155", "lemon"), "cioceo155"),
    (("record155", "a"), "record155"),
    (("record155", "zz"), "qdbnqc155"),
    (("record155", "AgentU"), "rkgbkx155"),
    (("record155", "keyboard"), "biapfd155"),
    (("record155", "AA"), "record155"),
    (("candle155", "key"), "melnpc155"),
    (("candle155", "lemon"), "nezryp155"),
    (("candle155", "a"), "candle155"),
    (("candle155", "zz"), "bzmckd155"),
    (("candle155", "AgentU"), "cgrqey155"),
    (("candle155", "keyboard"), "meleze155"),
    (("candle155", "AA"), "candle155"),
    (("thread155", "key"), "dlpoeb155"),
    (("thread155", "lemon"), "eldsno155"),
    (("thread155", "a"), "thread155"),
    (("thread155", "zz"), "sgqdzc155"),
    (("thread155", "AgentU"), "tnvrtx155"),
    (("thread155", "keyboard"), "dlpfod155"),
    (("thread155", "AA"), "thread155"),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 155: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 155: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "a"),
        "round 155: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 155: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 155: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 155: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", "AA"),
        "round 155: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "key"),
        "bssxh 155: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 155: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "a"),
        "round 155: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 155: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 155: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 155: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", "AA"),
        "round 155: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 155: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 155: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "a"),
        "round 155: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 155: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 155: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 155: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", "AA"),
        "round 155: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 155: the processor reads the record then stops", "key"),
        "bssxh 155: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 155: the processor reads the record then stops", "lemon"),
        "csgbq 155: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 155: the processor reads the record then stops", "a"),
        "round 155: the processor reads the record then stops",
    ),
    (
        ("round 155: the processor reads the record then stops", "zz"),
        "qntmc 155: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 155: the processor reads the record then stops", "AgentU"),
        "ruyaw 155: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 155: the processor reads the record then stops", "keyboard"),
        "bssor 155: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 155: the processor reads the record then stops", "AA"),
        "round 155: the processor reads the record then stops",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "key"),
        "bssxh 155: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "lemon"),
        "csgbq 155: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "a"),
        "round 155: a worker pulls the next task from the queue",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "zz"),
        "qntmc 155: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 155: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "keyboard"),
        "bssor 155: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 155: a worker pulls the next task from the queue", "AA"),
        "round 155: a worker pulls the next task from the queue",
    ),
    (
        ("round 155: signals travel through the network layer", "key"),
        "bssxh 155: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 155: signals travel through the network layer", "lemon"),
        "csgbq 155: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 155: signals travel through the network layer", "a"),
        "round 155: signals travel through the network layer",
    ),
    (
        ("round 155: signals travel through the network layer", "zz"),
        "qntmc 155: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 155: signals travel through the network layer", "AgentU"),
        "ruyaw 155: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 155: signals travel through the network layer", "keyboard"),
        "bssor 155: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 155: signals travel through the network layer", "AA"),
        "round 155: signals travel through the network layer",
    ),
    (
        ("round 155: the gateway routes each request by policy", "key"),
        "bssxh 155: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 155: the gateway routes each request by policy", "lemon"),
        "csgbq 155: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 155: the gateway routes each request by policy", "a"),
        "round 155: the gateway routes each request by policy",
    ),
    (
        ("round 155: the gateway routes each request by policy", "zz"),
        "qntmc 155: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 155: the gateway routes each request by policy", "AgentU"),
        "ruyaw 155: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 155: the gateway routes each request by policy", "keyboard"),
        "bssor 155: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 155: the gateway routes each request by policy", "AA"),
        "round 155: the gateway routes each request by policy",
    ),
    (("round 155: memory grows until the buffer is full", "key"), "bssxh 155: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 155: memory grows until the buffer is full", "lemon"), "csgbq 155: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 155: memory grows until the buffer is full", "a"), "round 155: memory grows until the buffer is full"),
    (("round 155: memory grows until the buffer is full", "zz"), "qntmc 155: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 155: memory grows until the buffer is full", "AgentU"),
        "ruyaw 155: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 155: memory grows until the buffer is full", "keyboard"),
        "bssor 155: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 155: memory grows until the buffer is full", "AA"), "round 155: memory grows until the buffer is full"),
    (("round 155: the cluster mirrors every packet twice", "key"), "bssxh 155: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 155: the cluster mirrors every packet twice", "lemon"),
        "csgbq 155: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 155: the cluster mirrors every packet twice", "a"), "round 155: the cluster mirrors every packet twice"),
    (("round 155: the cluster mirrors every packet twice", "zz"), "qntmc 155: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 155: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 155: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 155: the cluster mirrors every packet twice", "keyboard"),
        "bssor 155: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 155: the cluster mirrors every packet twice", "AA"), "round 155: the cluster mirrors every packet twice"),
    (
        ("round 155: ranking uses tokens learned from the corpus", "key"),
        "bssxh 155: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 155: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", "a"),
        "round 155: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 155: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 155: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 155: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", "AA"),
        "round 155: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 155: a long session ends when the candle dies", "key"),
        "bssxh 155: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 155: a long session ends when the candle dies", "lemon"),
        "csgbq 155: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 155: a long session ends when the candle dies", "a"),
        "round 155: a long session ends when the candle dies",
    ),
    (
        ("round 155: a long session ends when the candle dies", "zz"),
        "qntmc 155: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 155: a long session ends when the candle dies", "AgentU"),
        "ruyaw 155: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 155: a long session ends when the candle dies", "keyboard"),
        "bssor 155: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 155: a long session ends when the candle dies", "AA"),
        "round 155: a long session ends when the candle dies",
    ),
    (("round 155: encode the prompt then map the result", "key"), "bssxh 155: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 155: encode the prompt then map the result", "lemon"), "csgbq 155: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 155: encode the prompt then map the result", "a"), "round 155: encode the prompt then map the result"),
    (("round 155: encode the prompt then map the result", "zz"), "qntmc 155: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 155: encode the prompt then map the result", "AgentU"),
        "ruyaw 155: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 155: encode the prompt then map the result", "keyboard"),
        "bssor 155: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 155: encode the prompt then map the result", "AA"), "round 155: encode the prompt then map the result"),
    (("round 155: the kernel wakes the worker at dawn", "key"), "bssxh 155: rri iovlop ukocc xfo ambocb er neux"),
    (("round 155: the kernel wakes the worker at dawn", "lemon"), "csgbq 155: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 155: the kernel wakes the worker at dawn", "a"), "round 155: the kernel wakes the worker at dawn"),
    (("round 155: the kernel wakes the worker at dawn", "zz"), "qntmc 155: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 155: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 155: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 155: the kernel wakes the worker at dawn", "keyboard"), "bssor 155: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 155: the kernel wakes the worker at dawn", "AA"), "round 155: the kernel wakes the worker at dawn"),
    (("round 155: service latency drops after the patch", "key"), "bssxh 155: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 155: service latency drops after the patch", "lemon"), "csgbq 155: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 155: service latency drops after the patch", "a"), "round 155: service latency drops after the patch"),
    (("round 155: service latency drops after the patch", "zz"), "qntmc 155: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 155: service latency drops after the patch", "AgentU"),
        "ruyaw 155: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 155: service latency drops after the patch", "keyboard"),
        "bssor 155: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 155: service latency drops after the patch", "AA"), "round 155: service latency drops after the patch"),
    (
        ("round 155: the library caches every vector it sees", "key"),
        "bssxh 155: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 155: the library caches every vector it sees", "lemon"),
        "csgbq 155: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 155: the library caches every vector it sees", "a"), "round 155: the library caches every vector it sees"),
    (
        ("round 155: the library caches every vector it sees", "zz"),
        "qntmc 155: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 155: the library caches every vector it sees", "AgentU"),
        "ruyaw 155: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 155: the library caches every vector it sees", "keyboard"),
        "bssor 155: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 155: the library caches every vector it sees", "AA"),
        "round 155: the library caches every vector it sees",
    ),
    (("round 155: agents argue then the debate resolves", "key"), "bssxh 155: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 155: agents argue then the debate resolves", "lemon"), "csgbq 155: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 155: agents argue then the debate resolves", "a"), "round 155: agents argue then the debate resolves"),
    (("round 155: agents argue then the debate resolves", "zz"), "qntmc 155: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 155: agents argue then the debate resolves", "AgentU"),
        "ruyaw 155: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 155: agents argue then the debate resolves", "keyboard"),
        "bssor 155: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 155: agents argue then the debate resolves", "AA"), "round 155: agents argue then the debate resolves"),
    (("round 155: the filter keeps only strong matches", "key"), "bssxh 155: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 155: the filter keeps only strong matches", "lemon"), "csgbq 155: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 155: the filter keeps only strong matches", "a"), "round 155: the filter keeps only strong matches"),
    (("round 155: the filter keeps only strong matches", "zz"), "qntmc 155: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 155: the filter keeps only strong matches", "AgentU"), "ruyaw 155: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 155: the filter keeps only strong matches", "keyboard"),
        "bssor 155: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 155: the filter keeps only strong matches", "AA"), "round 155: the filter keeps only strong matches"),
    (("round 155: the model answers with a short reply", "key"), "bssxh 155: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 155: the model answers with a short reply", "lemon"), "csgbq 155: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 155: the model answers with a short reply", "a"), "round 155: the model answers with a short reply"),
    (("round 155: the model answers with a short reply", "zz"), "qntmc 155: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 155: the model answers with a short reply", "AgentU"), "ruyaw 155: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 155: the model answers with a short reply", "keyboard"),
        "bssor 155: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 155: the model answers with a short reply", "AA"), "round 155: the model answers with a short reply"),
    (
        ("round 155: the recorder stores the reasoning trace", "key"),
        "bssxh 155: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 155: the recorder stores the reasoning trace", "lemon"),
        "csgbq 155: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 155: the recorder stores the reasoning trace", "a"), "round 155: the recorder stores the reasoning trace"),
    (
        ("round 155: the recorder stores the reasoning trace", "zz"),
        "qntmc 155: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 155: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 155: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 155: the recorder stores the reasoning trace", "keyboard"),
        "bssor 155: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 155: the recorder stores the reasoning trace", "AA"),
        "round 155: the recorder stores the reasoning trace",
    ),
    (("round 155: the angel watches the processor run", "key"), "bssxh 155: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 155: the angel watches the processor run", "lemon"), "csgbq 155: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 155: the angel watches the processor run", "a"), "round 155: the angel watches the processor run"),
    (("round 155: the angel watches the processor run", "zz"), "qntmc 155: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 155: the angel watches the processor run", "AgentU"), "ruyaw 155: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 155: the angel watches the processor run", "keyboard"), "bssor 155: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 155: the angel watches the processor run", "AA"), "round 155: the angel watches the processor run"),
    (("round 155: angle of the vector decides the match", "key"), "bssxh 155: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 155: angle of the vector decides the match", "lemon"), "csgbq 155: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 155: angle of the vector decides the match", "a"), "round 155: angle of the vector decides the match"),
    (("round 155: angle of the vector decides the match", "zz"), "qntmc 155: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 155: angle of the vector decides the match", "AgentU"),
        "ruyaw 155: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 155: angle of the vector decides the match", "keyboard"),
        "bssor 155: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 155: angle of the vector decides the match", "AA"), "round 155: angle of the vector decides the match"),
    (
        ("round 155: the candle burns twice as long at night", "key"),
        "bssxh 155: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 155: the candle burns twice as long at night", "lemon"),
        "csgbq 155: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 155: the candle burns twice as long at night", "a"), "round 155: the candle burns twice as long at night"),
    (
        ("round 155: the candle burns twice as long at night", "zz"),
        "qntmc 155: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 155: the candle burns twice as long at night", "AgentU"),
        "ruyaw 155: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 155: the candle burns twice as long at night", "keyboard"),
        "bssor 155: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 155: the candle burns twice as long at night", "AA"),
        "round 155: the candle burns twice as long at night",
    ),
    (("round 155: a mirror of the universe in one line", "key"), "bssxh 155: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 155: a mirror of the universe in one line", "lemon"), "csgbq 155: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 155: a mirror of the universe in one line", "a"), "round 155: a mirror of the universe in one line"),
    (("round 155: a mirror of the universe in one line", "zz"), "qntmc 155: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 155: a mirror of the universe in one line", "AgentU"), "ruyaw 155: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 155: a mirror of the universe in one line", "keyboard"),
        "bssor 155: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 155: a mirror of the universe in one line", "AA"), "round 155: a mirror of the universe in one line"),
    (("round 155: the queue drains before the storm", "key"), "bssxh 155: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 155: the queue drains before the storm", "lemon"), "csgbq 155: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 155: the queue drains before the storm", "a"), "round 155: the queue drains before the storm"),
    (("round 155: the queue drains before the storm", "zz"), "qntmc 155: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 155: the queue drains before the storm", "AgentU"), "ruyaw 155: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 155: the queue drains before the storm", "keyboard"), "bssor 155: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 155: the queue drains before the storm", "AA"), "round 155: the queue drains before the storm"),
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
