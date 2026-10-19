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
    (("kitten194", "key"), "umrdil194"),
    (("kitten194", "lemon"), "vmfhry194"),
    (("kitten194", "a"), "kitten194"),
    (("kitten194", "zz"), "jhssdm194"),
    (("kitten194", "AgentU"), "koxgxh194"),
    (("kitten194", "keyboard"), "umrusn194"),
    (("kitten194", "AA"), "kitten194"),
    (("sitting194", "key"), "cmrdmlq194"),
    (("sitting194", "lemon"), "dmfhvyk194"),
    (("sitting194", "a"), "sitting194"),
    (("sitting194", "zz"), "rhsshmf194"),
    (("sitting194", "AgentU"), "soxgbhg194"),
    (("sitting194", "keyboard"), "cmruwnx194"),
    (("sitting194", "AA"), "sitting194"),
    (("agent194", "key"), "kkcxx194"),
    (("agent194", "lemon"), "lkqbg194"),
    (("agent194", "a"), "agent194"),
    (("agent194", "zz"), "zfdms194"),
    (("agent194", "AgentU"), "amiam194"),
    (("agent194", "keyboard"), "kkcoh194"),
    (("agent194", "AA"), "agent194"),
    (("angle194", "key"), "krevi194"),
    (("angle194", "lemon"), "lrszr194"),
    (("angle194", "a"), "angle194"),
    (("angle194", "zz"), "zmfkd194"),
    (("angle194", "AgentU"), "atkyx194"),
    (("angle194", "keyboard"), "krems194"),
    (("angle194", "AA"), "angle194"),
    (("universe194", "key"), "ergfipci194"),
    (("universe194", "lemon"), "frujrcwq194"),
    (("universe194", "a"), "universe194"),
    (("universe194", "zz"), "tmhudqrd194"),
    (("universe194", "AgentU"), "utmixlsk194"),
    (("universe194", "keyboard"), "ergwsrjh194"),
    (("universe194", "AA"), "universe194"),
    (("memory194", "key"), "wikyvw194"),
    (("memory194", "lemon"), "xiycej194"),
    (("memory194", "a"), "memory194"),
    (("memory194", "zz"), "ldlnqx194"),
    (("memory194", "AgentU"), "mkqbks194"),
    (("memory194", "keyboard"), "wikpfy194"),
    (("memory194", "AA"), "memory194"),
    (("stream194", "key"), "cxpoek194"),
    (("stream194", "lemon"), "dxdsnx194"),
    (("stream194", "a"), "stream194"),
    (("stream194", "zz"), "rsqdzl194"),
    (("stream194", "AgentU"), "szvrtg194"),
    (("stream194", "keyboard"), "cxpfom194"),
    (("stream194", "AA"), "stream194"),
    (("context194", "key"), "msldivd194"),
    (("context194", "lemon"), "nszhrix194"),
    (("context194", "a"), "context194"),
    (("context194", "zz"), "bnmsdws194"),
    (("context194", "AgentU"), "curgxrt194"),
    (("context194", "keyboard"), "mslusxk194"),
    (("context194", "AA"), "context194"),
    (("knowledge194", "key"), "urmgpcnkc194"),
    (("knowledge194", "lemon"), "vrakyphss194"),
    (("knowledge194", "a"), "knowledge194"),
    (("knowledge194", "zz"), "jmnvkdcfd194"),
    (("knowledge194", "AgentU"), "ktsjeydmi194"),
    (("knowledge194", "keyboard"), "urmxzeujo194"),
    (("knowledge194", "AA"), "knowledge194"),
    (("vector194", "key"), "fiadsp194"),
    (("vector194", "lemon"), "giohbc194"),
    (("vector194", "a"), "vector194"),
    (("vector194", "zz"), "udbsnq194"),
    (("vector194", "AgentU"), "vkgghl194"),
    (("vector194", "keyboard"), "fiaucr194"),
    (("vector194", "AA"), "vector194"),
    (("processor194", "key"), "zvmmiqcsp194"),
    (("processor194", "lemon"), "avaqrdwaf194"),
    (("processor194", "a"), "processor194"),
    (("processor194", "zz"), "oqnbdrrnq194"),
    (("processor194", "AgentU"), "pxspxmsuv194"),
    (("processor194", "keyboard"), "zvmdssjrb194"),
    (("processor194", "AA"), "processor194"),
    (("reasoning194", "key"), "biycslsre194"),
    (("reasoning194", "lemon"), "cimgbymzu194"),
    (("reasoning194", "a"), "reasoning194"),
    (("reasoning194", "zz"), "qdzrnmhmf194"),
    (("reasoning194", "AgentU"), "rkefhhitk194"),
    (("reasoning194", "keyboard"), "biytcnzqq194"),
    (("reasoning194", "AA"), "reasoning194"),
    (("machine194", "key"), "wearmlo194"),
    (("machine194", "lemon"), "xeovvyi194"),
    (("machine194", "a"), "machine194"),
    (("machine194", "zz"), "lzbghmd194"),
    (("machine194", "AgentU"), "mggubhe194"),
    (("machine194", "keyboard"), "weaiwnv194"),
    (("machine194", "AA"), "machine194"),
    (("learning194", "key"), "viybrgxk194"),
    (("learning194", "lemon"), "wimfatrs194"),
    (("learning194", "a"), "learning194"),
    (("learning194", "zz"), "kdzqmhmf194"),
    (("learning194", "AgentU"), "lkeegcnm194"),
    (("learning194", "keyboard"), "viysbiej194"),
    (("learning194", "AA"), "learning194"),
    (("model194", "key"), "wsbop194"),
    (("model194", "lemon"), "xspsy194"),
    (("model194", "a"), "model194"),
    (("model194", "zz"), "lncdk194"),
    (("model194", "AgentU"), "muhre194"),
    (("model194", "keyboard"), "wsbfz194"),
    (("model194", "AA"), "model194"),
    (("token194", "key"), "dsior194"),
    (("token194", "lemon"), "eswsa194"),
    (("token194", "a"), "token194"),
    (("token194", "zz"), "snjdm194"),
    (("token194", "AgentU"), "tuorg194"),
    (("token194", "keyboard"), "dsifb194"),
    (("token194", "AA"), "token194"),
    (("prompt194", "key"), "zvmwtr194"),
    (("prompt194", "lemon"), "avaace194"),
    (("prompt194", "a"), "prompt194"),
    (("prompt194", "zz"), "oqnlos194"),
    (("prompt194", "AgentU"), "pxszin194"),
    (("prompt194", "keyboard"), "zvmndt194"),
    (("prompt194", "AA"), "prompt194"),
    (("session194", "key"), "ciqcmmx194"),
    (("session194", "lemon"), "diegvzr194"),
    (("session194", "a"), "session194"),
    (("session194", "zz"), "rdrrhnm194"),
    (("session194", "AgentU"), "skwfbin194"),
    (("session194", "keyboard"), "ciqtwoe194"),
    (("session194", "AA"), "session194"),
    (("library194", "key"), "vmzbepi194"),
    (("library194", "lemon"), "wmnfncc194"),
    (("library194", "a"), "library194"),
    (("library194", "zz"), "khaqzqx194"),
    (("library194", "AgentU"), "lofetly194"),
    (("library194", "keyboard"), "vmzsorp194"),
    (("library194", "AA"), "library194"),
    (("service194", "key"), "cipfmao194"),
    (("service194", "lemon"), "didjvni194"),
    (("service194", "a"), "service194"),
    (("service194", "zz"), "rdquhbd194"),
    (("service194", "AgentU"), "skvibwe194"),
    (("service194", "keyboard"), "cipwwcv194"),
    (("service194", "AA"), "service194"),
    (("gateway194", "key"), "qeroayi194"),
    (("gateway194", "lemon"), "refsjlc194"),
    (("gateway194", "a"), "gateway194"),
    (("gateway194", "zz"), "fzsdvzx194"),
    (("gateway194", "AgentU"), "ggxrpuy194"),
    (("gateway194", "keyboard"), "qerfkap194"),
    (("gateway194", "AA"), "gateway194"),
    (("storage194", "key"), "cxmbeeo194"),
    (("storage194", "lemon"), "dxafnri194"),
    (("storage194", "a"), "storage194"),
    (("storage194", "zz"), "rsnqzfd194"),
    (("storage194", "AgentU"), "szsetae194"),
    (("storage194", "keyboard"), "cxmsogv194"),
    (("storage194", "AA"), "storage194"),
    (("network194", "key"), "xirgspu194"),
    (("network194", "lemon"), "yifkbco194"),
    (("network194", "a"), "network194"),
    (("network194", "zz"), "mdsvnqj194"),
    (("network194", "AgentU"), "nkxjhlk194"),
    (("network194", "keyboard"), "xirxcrb194"),
    (("network194", "AA"), "network194"),
    (("latency194", "key"), "verorai194"),
    (("latency194", "lemon"), "wefsanc194"),
    (("latency194", "a"), "latency194"),
    (("latency194", "zz"), "kzsdmbx194"),
    (("latency194", "AgentU"), "lgxrgwy194"),
    (("latency194", "keyboard"), "verfbcp194"),
    (("latency194", "AA"), "latency194"),
    (("buffer194", "key"), "lydpip194"),
    (("buffer194", "lemon"), "myrtrc194"),
    (("buffer194", "a"), "buffer194"),
    (("buffer194", "zz"), "ateedq194"),
    (("buffer194", "AgentU"), "bajsxl194"),
    (("buffer194", "keyboard"), "lydgsr194"),
    (("buffer194", "AA"), "buffer194"),
    (("queue194", "key"), "aycei194"),
    (("queue194", "lemon"), "byqir194"),
    (("queue194", "a"), "queue194"),
    (("queue194", "zz"), "ptdtd194"),
    (("queue194", "AgentU"), "qaihx194"),
    (("queue194", "keyboard"), "aycvs194"),
    (("queue194", "AA"), "queue194"),
    (("worker194", "key"), "gspuip194"),
    (("worker194", "lemon"), "hsdyrc194"),
    (("worker194", "a"), "worker194"),
    (("worker194", "zz"), "vnqjdq194"),
    (("worker194", "AgentU"), "wuvxxl194"),
    (("worker194", "keyboard"), "gsplsr194"),
    (("worker194", "AA"), "worker194"),
    (("kernel194", "key"), "uipxij194"),
    (("kernel194", "lemon"), "vidbrw194"),
    (("kernel194", "a"), "kernel194"),
    (("kernel194", "zz"), "jdqmdk194"),
    (("kernel194", "AgentU"), "kkvaxf194"),
    (("kernel194", "keyboard"), "uiposl194"),
    (("kernel194", "AA"), "kernel194"),
    (("signal194", "key"), "cmexej194"),
    (("signal194", "lemon"), "dmsbnw194"),
    (("signal194", "a"), "signal194"),
    (("signal194", "zz"), "rhfmzk194"),
    (("signal194", "AgentU"), "sokatf194"),
    (("signal194", "keyboard"), "cmeool194"),
    (("signal194", "AA"), "signal194"),
    (("packet194", "key"), "zeauir194"),
    (("packet194", "lemon"), "aeoyre194"),
    (("packet194", "a"), "packet194"),
    (("packet194", "zz"), "ozbjds194"),
    (("packet194", "AgentU"), "pggxxn194"),
    (("packet194", "keyboard"), "zealst194"),
    (("packet194", "AA"), "packet194"),
    (("router194", "key"), "bssdip194"),
    (("router194", "lemon"), "csghrc194"),
    (("router194", "a"), "router194"),
    (("router194", "zz"), "qntsdq194"),
    (("router194", "AgentU"), "ruygxl194"),
    (("router194", "keyboard"), "bssusr194"),
    (("router194", "AA"), "router194"),
    (("cluster194", "key"), "mpscxcb194"),
    (("cluster194", "lemon"), "npgggpv194"),
    (("cluster194", "a"), "cluster194"),
    (("cluster194", "zz"), "bktrsdq194"),
    (("cluster194", "AgentU"), "cryfmyr194"),
    (("cluster194", "keyboard"), "mpsthei194"),
    (("cluster194", "AA"), "cluster194"),
    (("mirror194", "key"), "wmpbsp194"),
    (("mirror194", "lemon"), "xmdfbc194"),
    (("mirror194", "a"), "mirror194"),
    (("mirror194", "zz"), "lhqqnq194"),
    (("mirror194", "AgentU"), "movehl194"),
    (("mirror194", "keyboard"), "wmpscr194"),
    (("mirror194", "AA"), "mirror194"),
    (("filter194", "key"), "pmjdip194"),
    (("filter194", "lemon"), "qmxhrc194"),
    (("filter194", "a"), "filter194"),
    (("filter194", "zz"), "ehksdq194"),
    (("filter194", "AgentU"), "fopgxl194"),
    (("filter194", "keyboard"), "pmjusr194"),
    (("filter194", "AA"), "filter194"),
    (("ranking194", "key"), "belumlq194"),
    (("ranking194", "lemon"), "cezyvyk194"),
    (("ranking194", "a"), "ranking194"),
    (("ranking194", "zz"), "qzmjhmf194"),
    (("ranking194", "AgentU"), "rgrxbhg194"),
    (("ranking194", "keyboard"), "bellwnx194"),
    (("ranking194", "AA"), "ranking194"),
    (("encoding194", "key"), "orayhgxk194"),
    (("encoding194", "lemon"), "procqtrs194"),
    (("encoding194", "a"), "encoding194"),
    (("encoding194", "zz"), "dmbnchmf194"),
    (("encoding194", "AgentU"), "etgbwcnm194"),
    (("encoding194", "keyboard"), "orapriej194"),
    (("encoding194", "AA"), "encoding194"),
    (("mapping194", "key"), "wenzmlq194"),
    (("mapping194", "lemon"), "xebdvyk194"),
    (("mapping194", "a"), "mapping194"),
    (("mapping194", "zz"), "lzoohmf194"),
    (("mapping194", "AgentU"), "mgtcbhg194"),
    (("mapping194", "keyboard"), "wenqwnx194"),
    (("mapping194", "AA"), "mapping194"),
    (("record194", "key"), "biayvb194"),
    (("record194", "lemon"), "cioceo194"),
    (("record194", "a"), "record194"),
    (("record194", "zz"), "qdbnqc194"),
    (("record194", "AgentU"), "rkgbkx194"),
    (("record194", "keyboard"), "biapfd194"),
    (("record194", "AA"), "record194"),
    (("candle194", "key"), "melnpc194"),
    (("candle194", "lemon"), "nezryp194"),
    (("candle194", "a"), "candle194"),
    (("candle194", "zz"), "bzmckd194"),
    (("candle194", "AgentU"), "cgrqey194"),
    (("candle194", "keyboard"), "meleze194"),
    (("candle194", "AA"), "candle194"),
    (("thread194", "key"), "dlpoeb194"),
    (("thread194", "lemon"), "eldsno194"),
    (("thread194", "a"), "thread194"),
    (("thread194", "zz"), "sgqdzc194"),
    (("thread194", "AgentU"), "tnvrtx194"),
    (("thread194", "keyboard"), "dlpfod194"),
    (("thread194", "AA"), "thread194"),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 194: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 194: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "a"),
        "round 194: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 194: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 194: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 194: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", "AA"),
        "round 194: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "key"),
        "bssxh 194: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 194: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "a"),
        "round 194: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 194: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 194: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 194: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", "AA"),
        "round 194: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 194: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 194: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "a"),
        "round 194: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 194: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 194: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 194: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", "AA"),
        "round 194: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 194: the processor reads the record then stops", "key"),
        "bssxh 194: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 194: the processor reads the record then stops", "lemon"),
        "csgbq 194: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 194: the processor reads the record then stops", "a"),
        "round 194: the processor reads the record then stops",
    ),
    (
        ("round 194: the processor reads the record then stops", "zz"),
        "qntmc 194: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 194: the processor reads the record then stops", "AgentU"),
        "ruyaw 194: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 194: the processor reads the record then stops", "keyboard"),
        "bssor 194: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 194: the processor reads the record then stops", "AA"),
        "round 194: the processor reads the record then stops",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "key"),
        "bssxh 194: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "lemon"),
        "csgbq 194: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "a"),
        "round 194: a worker pulls the next task from the queue",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "zz"),
        "qntmc 194: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 194: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "keyboard"),
        "bssor 194: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 194: a worker pulls the next task from the queue", "AA"),
        "round 194: a worker pulls the next task from the queue",
    ),
    (
        ("round 194: signals travel through the network layer", "key"),
        "bssxh 194: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 194: signals travel through the network layer", "lemon"),
        "csgbq 194: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 194: signals travel through the network layer", "a"),
        "round 194: signals travel through the network layer",
    ),
    (
        ("round 194: signals travel through the network layer", "zz"),
        "qntmc 194: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 194: signals travel through the network layer", "AgentU"),
        "ruyaw 194: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 194: signals travel through the network layer", "keyboard"),
        "bssor 194: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 194: signals travel through the network layer", "AA"),
        "round 194: signals travel through the network layer",
    ),
    (
        ("round 194: the gateway routes each request by policy", "key"),
        "bssxh 194: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 194: the gateway routes each request by policy", "lemon"),
        "csgbq 194: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 194: the gateway routes each request by policy", "a"),
        "round 194: the gateway routes each request by policy",
    ),
    (
        ("round 194: the gateway routes each request by policy", "zz"),
        "qntmc 194: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 194: the gateway routes each request by policy", "AgentU"),
        "ruyaw 194: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 194: the gateway routes each request by policy", "keyboard"),
        "bssor 194: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 194: the gateway routes each request by policy", "AA"),
        "round 194: the gateway routes each request by policy",
    ),
    (("round 194: memory grows until the buffer is full", "key"), "bssxh 194: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 194: memory grows until the buffer is full", "lemon"), "csgbq 194: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 194: memory grows until the buffer is full", "a"), "round 194: memory grows until the buffer is full"),
    (("round 194: memory grows until the buffer is full", "zz"), "qntmc 194: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 194: memory grows until the buffer is full", "AgentU"),
        "ruyaw 194: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 194: memory grows until the buffer is full", "keyboard"),
        "bssor 194: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 194: memory grows until the buffer is full", "AA"), "round 194: memory grows until the buffer is full"),
    (("round 194: the cluster mirrors every packet twice", "key"), "bssxh 194: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 194: the cluster mirrors every packet twice", "lemon"),
        "csgbq 194: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 194: the cluster mirrors every packet twice", "a"), "round 194: the cluster mirrors every packet twice"),
    (("round 194: the cluster mirrors every packet twice", "zz"), "qntmc 194: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 194: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 194: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 194: the cluster mirrors every packet twice", "keyboard"),
        "bssor 194: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 194: the cluster mirrors every packet twice", "AA"), "round 194: the cluster mirrors every packet twice"),
    (
        ("round 194: ranking uses tokens learned from the corpus", "key"),
        "bssxh 194: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 194: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", "a"),
        "round 194: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 194: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 194: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 194: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", "AA"),
        "round 194: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 194: a long session ends when the candle dies", "key"),
        "bssxh 194: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 194: a long session ends when the candle dies", "lemon"),
        "csgbq 194: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 194: a long session ends when the candle dies", "a"),
        "round 194: a long session ends when the candle dies",
    ),
    (
        ("round 194: a long session ends when the candle dies", "zz"),
        "qntmc 194: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 194: a long session ends when the candle dies", "AgentU"),
        "ruyaw 194: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 194: a long session ends when the candle dies", "keyboard"),
        "bssor 194: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 194: a long session ends when the candle dies", "AA"),
        "round 194: a long session ends when the candle dies",
    ),
    (("round 194: encode the prompt then map the result", "key"), "bssxh 194: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 194: encode the prompt then map the result", "lemon"), "csgbq 194: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 194: encode the prompt then map the result", "a"), "round 194: encode the prompt then map the result"),
    (("round 194: encode the prompt then map the result", "zz"), "qntmc 194: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 194: encode the prompt then map the result", "AgentU"),
        "ruyaw 194: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 194: encode the prompt then map the result", "keyboard"),
        "bssor 194: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 194: encode the prompt then map the result", "AA"), "round 194: encode the prompt then map the result"),
    (("round 194: the kernel wakes the worker at dawn", "key"), "bssxh 194: rri iovlop ukocc xfo ambocb er neux"),
    (("round 194: the kernel wakes the worker at dawn", "lemon"), "csgbq 194: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 194: the kernel wakes the worker at dawn", "a"), "round 194: the kernel wakes the worker at dawn"),
    (("round 194: the kernel wakes the worker at dawn", "zz"), "qntmc 194: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 194: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 194: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 194: the kernel wakes the worker at dawn", "keyboard"), "bssor 194: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 194: the kernel wakes the worker at dawn", "AA"), "round 194: the kernel wakes the worker at dawn"),
    (("round 194: service latency drops after the patch", "key"), "bssxh 194: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 194: service latency drops after the patch", "lemon"), "csgbq 194: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 194: service latency drops after the patch", "a"), "round 194: service latency drops after the patch"),
    (("round 194: service latency drops after the patch", "zz"), "qntmc 194: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 194: service latency drops after the patch", "AgentU"),
        "ruyaw 194: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 194: service latency drops after the patch", "keyboard"),
        "bssor 194: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 194: service latency drops after the patch", "AA"), "round 194: service latency drops after the patch"),
    (
        ("round 194: the library caches every vector it sees", "key"),
        "bssxh 194: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 194: the library caches every vector it sees", "lemon"),
        "csgbq 194: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 194: the library caches every vector it sees", "a"), "round 194: the library caches every vector it sees"),
    (
        ("round 194: the library caches every vector it sees", "zz"),
        "qntmc 194: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 194: the library caches every vector it sees", "AgentU"),
        "ruyaw 194: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 194: the library caches every vector it sees", "keyboard"),
        "bssor 194: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 194: the library caches every vector it sees", "AA"),
        "round 194: the library caches every vector it sees",
    ),
    (("round 194: agents argue then the debate resolves", "key"), "bssxh 194: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 194: agents argue then the debate resolves", "lemon"), "csgbq 194: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 194: agents argue then the debate resolves", "a"), "round 194: agents argue then the debate resolves"),
    (("round 194: agents argue then the debate resolves", "zz"), "qntmc 194: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 194: agents argue then the debate resolves", "AgentU"),
        "ruyaw 194: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 194: agents argue then the debate resolves", "keyboard"),
        "bssor 194: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 194: agents argue then the debate resolves", "AA"), "round 194: agents argue then the debate resolves"),
    (("round 194: the filter keeps only strong matches", "key"), "bssxh 194: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 194: the filter keeps only strong matches", "lemon"), "csgbq 194: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 194: the filter keeps only strong matches", "a"), "round 194: the filter keeps only strong matches"),
    (("round 194: the filter keeps only strong matches", "zz"), "qntmc 194: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 194: the filter keeps only strong matches", "AgentU"), "ruyaw 194: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 194: the filter keeps only strong matches", "keyboard"),
        "bssor 194: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 194: the filter keeps only strong matches", "AA"), "round 194: the filter keeps only strong matches"),
    (("round 194: the model answers with a short reply", "key"), "bssxh 194: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 194: the model answers with a short reply", "lemon"), "csgbq 194: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 194: the model answers with a short reply", "a"), "round 194: the model answers with a short reply"),
    (("round 194: the model answers with a short reply", "zz"), "qntmc 194: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 194: the model answers with a short reply", "AgentU"), "ruyaw 194: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 194: the model answers with a short reply", "keyboard"),
        "bssor 194: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 194: the model answers with a short reply", "AA"), "round 194: the model answers with a short reply"),
    (
        ("round 194: the recorder stores the reasoning trace", "key"),
        "bssxh 194: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 194: the recorder stores the reasoning trace", "lemon"),
        "csgbq 194: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 194: the recorder stores the reasoning trace", "a"), "round 194: the recorder stores the reasoning trace"),
    (
        ("round 194: the recorder stores the reasoning trace", "zz"),
        "qntmc 194: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 194: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 194: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 194: the recorder stores the reasoning trace", "keyboard"),
        "bssor 194: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 194: the recorder stores the reasoning trace", "AA"),
        "round 194: the recorder stores the reasoning trace",
    ),
    (("round 194: the angel watches the processor run", "key"), "bssxh 194: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 194: the angel watches the processor run", "lemon"), "csgbq 194: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 194: the angel watches the processor run", "a"), "round 194: the angel watches the processor run"),
    (("round 194: the angel watches the processor run", "zz"), "qntmc 194: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 194: the angel watches the processor run", "AgentU"), "ruyaw 194: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 194: the angel watches the processor run", "keyboard"), "bssor 194: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 194: the angel watches the processor run", "AA"), "round 194: the angel watches the processor run"),
    (("round 194: angle of the vector decides the match", "key"), "bssxh 194: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 194: angle of the vector decides the match", "lemon"), "csgbq 194: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 194: angle of the vector decides the match", "a"), "round 194: angle of the vector decides the match"),
    (("round 194: angle of the vector decides the match", "zz"), "qntmc 194: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 194: angle of the vector decides the match", "AgentU"),
        "ruyaw 194: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 194: angle of the vector decides the match", "keyboard"),
        "bssor 194: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 194: angle of the vector decides the match", "AA"), "round 194: angle of the vector decides the match"),
    (
        ("round 194: the candle burns twice as long at night", "key"),
        "bssxh 194: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 194: the candle burns twice as long at night", "lemon"),
        "csgbq 194: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 194: the candle burns twice as long at night", "a"), "round 194: the candle burns twice as long at night"),
    (
        ("round 194: the candle burns twice as long at night", "zz"),
        "qntmc 194: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 194: the candle burns twice as long at night", "AgentU"),
        "ruyaw 194: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 194: the candle burns twice as long at night", "keyboard"),
        "bssor 194: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 194: the candle burns twice as long at night", "AA"),
        "round 194: the candle burns twice as long at night",
    ),
    (("round 194: a mirror of the universe in one line", "key"), "bssxh 194: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 194: a mirror of the universe in one line", "lemon"), "csgbq 194: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 194: a mirror of the universe in one line", "a"), "round 194: a mirror of the universe in one line"),
    (("round 194: a mirror of the universe in one line", "zz"), "qntmc 194: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 194: a mirror of the universe in one line", "AgentU"), "ruyaw 194: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 194: a mirror of the universe in one line", "keyboard"),
        "bssor 194: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 194: a mirror of the universe in one line", "AA"), "round 194: a mirror of the universe in one line"),
    (("round 194: the queue drains before the storm", "key"), "bssxh 194: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 194: the queue drains before the storm", "lemon"), "csgbq 194: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 194: the queue drains before the storm", "a"), "round 194: the queue drains before the storm"),
    (("round 194: the queue drains before the storm", "zz"), "qntmc 194: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 194: the queue drains before the storm", "AgentU"), "ruyaw 194: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 194: the queue drains before the storm", "keyboard"), "bssor 194: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 194: the queue drains before the storm", "AA"), "round 194: the queue drains before the storm"),
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
