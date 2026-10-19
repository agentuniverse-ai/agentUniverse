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
    (("kitten198", "key"), "umrdil198"),
    (("kitten198", "lemon"), "vmfhry198"),
    (("kitten198", "a"), "kitten198"),
    (("kitten198", "zz"), "jhssdm198"),
    (("kitten198", "AgentU"), "koxgxh198"),
    (("kitten198", "keyboard"), "umrusn198"),
    (("kitten198", "AA"), "kitten198"),
    (("sitting198", "key"), "cmrdmlq198"),
    (("sitting198", "lemon"), "dmfhvyk198"),
    (("sitting198", "a"), "sitting198"),
    (("sitting198", "zz"), "rhsshmf198"),
    (("sitting198", "AgentU"), "soxgbhg198"),
    (("sitting198", "keyboard"), "cmruwnx198"),
    (("sitting198", "AA"), "sitting198"),
    (("agent198", "key"), "kkcxx198"),
    (("agent198", "lemon"), "lkqbg198"),
    (("agent198", "a"), "agent198"),
    (("agent198", "zz"), "zfdms198"),
    (("agent198", "AgentU"), "amiam198"),
    (("agent198", "keyboard"), "kkcoh198"),
    (("agent198", "AA"), "agent198"),
    (("angle198", "key"), "krevi198"),
    (("angle198", "lemon"), "lrszr198"),
    (("angle198", "a"), "angle198"),
    (("angle198", "zz"), "zmfkd198"),
    (("angle198", "AgentU"), "atkyx198"),
    (("angle198", "keyboard"), "krems198"),
    (("angle198", "AA"), "angle198"),
    (("universe198", "key"), "ergfipci198"),
    (("universe198", "lemon"), "frujrcwq198"),
    (("universe198", "a"), "universe198"),
    (("universe198", "zz"), "tmhudqrd198"),
    (("universe198", "AgentU"), "utmixlsk198"),
    (("universe198", "keyboard"), "ergwsrjh198"),
    (("universe198", "AA"), "universe198"),
    (("memory198", "key"), "wikyvw198"),
    (("memory198", "lemon"), "xiycej198"),
    (("memory198", "a"), "memory198"),
    (("memory198", "zz"), "ldlnqx198"),
    (("memory198", "AgentU"), "mkqbks198"),
    (("memory198", "keyboard"), "wikpfy198"),
    (("memory198", "AA"), "memory198"),
    (("stream198", "key"), "cxpoek198"),
    (("stream198", "lemon"), "dxdsnx198"),
    (("stream198", "a"), "stream198"),
    (("stream198", "zz"), "rsqdzl198"),
    (("stream198", "AgentU"), "szvrtg198"),
    (("stream198", "keyboard"), "cxpfom198"),
    (("stream198", "AA"), "stream198"),
    (("context198", "key"), "msldivd198"),
    (("context198", "lemon"), "nszhrix198"),
    (("context198", "a"), "context198"),
    (("context198", "zz"), "bnmsdws198"),
    (("context198", "AgentU"), "curgxrt198"),
    (("context198", "keyboard"), "mslusxk198"),
    (("context198", "AA"), "context198"),
    (("knowledge198", "key"), "urmgpcnkc198"),
    (("knowledge198", "lemon"), "vrakyphss198"),
    (("knowledge198", "a"), "knowledge198"),
    (("knowledge198", "zz"), "jmnvkdcfd198"),
    (("knowledge198", "AgentU"), "ktsjeydmi198"),
    (("knowledge198", "keyboard"), "urmxzeujo198"),
    (("knowledge198", "AA"), "knowledge198"),
    (("vector198", "key"), "fiadsp198"),
    (("vector198", "lemon"), "giohbc198"),
    (("vector198", "a"), "vector198"),
    (("vector198", "zz"), "udbsnq198"),
    (("vector198", "AgentU"), "vkgghl198"),
    (("vector198", "keyboard"), "fiaucr198"),
    (("vector198", "AA"), "vector198"),
    (("processor198", "key"), "zvmmiqcsp198"),
    (("processor198", "lemon"), "avaqrdwaf198"),
    (("processor198", "a"), "processor198"),
    (("processor198", "zz"), "oqnbdrrnq198"),
    (("processor198", "AgentU"), "pxspxmsuv198"),
    (("processor198", "keyboard"), "zvmdssjrb198"),
    (("processor198", "AA"), "processor198"),
    (("reasoning198", "key"), "biycslsre198"),
    (("reasoning198", "lemon"), "cimgbymzu198"),
    (("reasoning198", "a"), "reasoning198"),
    (("reasoning198", "zz"), "qdzrnmhmf198"),
    (("reasoning198", "AgentU"), "rkefhhitk198"),
    (("reasoning198", "keyboard"), "biytcnzqq198"),
    (("reasoning198", "AA"), "reasoning198"),
    (("machine198", "key"), "wearmlo198"),
    (("machine198", "lemon"), "xeovvyi198"),
    (("machine198", "a"), "machine198"),
    (("machine198", "zz"), "lzbghmd198"),
    (("machine198", "AgentU"), "mggubhe198"),
    (("machine198", "keyboard"), "weaiwnv198"),
    (("machine198", "AA"), "machine198"),
    (("learning198", "key"), "viybrgxk198"),
    (("learning198", "lemon"), "wimfatrs198"),
    (("learning198", "a"), "learning198"),
    (("learning198", "zz"), "kdzqmhmf198"),
    (("learning198", "AgentU"), "lkeegcnm198"),
    (("learning198", "keyboard"), "viysbiej198"),
    (("learning198", "AA"), "learning198"),
    (("model198", "key"), "wsbop198"),
    (("model198", "lemon"), "xspsy198"),
    (("model198", "a"), "model198"),
    (("model198", "zz"), "lncdk198"),
    (("model198", "AgentU"), "muhre198"),
    (("model198", "keyboard"), "wsbfz198"),
    (("model198", "AA"), "model198"),
    (("token198", "key"), "dsior198"),
    (("token198", "lemon"), "eswsa198"),
    (("token198", "a"), "token198"),
    (("token198", "zz"), "snjdm198"),
    (("token198", "AgentU"), "tuorg198"),
    (("token198", "keyboard"), "dsifb198"),
    (("token198", "AA"), "token198"),
    (("prompt198", "key"), "zvmwtr198"),
    (("prompt198", "lemon"), "avaace198"),
    (("prompt198", "a"), "prompt198"),
    (("prompt198", "zz"), "oqnlos198"),
    (("prompt198", "AgentU"), "pxszin198"),
    (("prompt198", "keyboard"), "zvmndt198"),
    (("prompt198", "AA"), "prompt198"),
    (("session198", "key"), "ciqcmmx198"),
    (("session198", "lemon"), "diegvzr198"),
    (("session198", "a"), "session198"),
    (("session198", "zz"), "rdrrhnm198"),
    (("session198", "AgentU"), "skwfbin198"),
    (("session198", "keyboard"), "ciqtwoe198"),
    (("session198", "AA"), "session198"),
    (("library198", "key"), "vmzbepi198"),
    (("library198", "lemon"), "wmnfncc198"),
    (("library198", "a"), "library198"),
    (("library198", "zz"), "khaqzqx198"),
    (("library198", "AgentU"), "lofetly198"),
    (("library198", "keyboard"), "vmzsorp198"),
    (("library198", "AA"), "library198"),
    (("service198", "key"), "cipfmao198"),
    (("service198", "lemon"), "didjvni198"),
    (("service198", "a"), "service198"),
    (("service198", "zz"), "rdquhbd198"),
    (("service198", "AgentU"), "skvibwe198"),
    (("service198", "keyboard"), "cipwwcv198"),
    (("service198", "AA"), "service198"),
    (("gateway198", "key"), "qeroayi198"),
    (("gateway198", "lemon"), "refsjlc198"),
    (("gateway198", "a"), "gateway198"),
    (("gateway198", "zz"), "fzsdvzx198"),
    (("gateway198", "AgentU"), "ggxrpuy198"),
    (("gateway198", "keyboard"), "qerfkap198"),
    (("gateway198", "AA"), "gateway198"),
    (("storage198", "key"), "cxmbeeo198"),
    (("storage198", "lemon"), "dxafnri198"),
    (("storage198", "a"), "storage198"),
    (("storage198", "zz"), "rsnqzfd198"),
    (("storage198", "AgentU"), "szsetae198"),
    (("storage198", "keyboard"), "cxmsogv198"),
    (("storage198", "AA"), "storage198"),
    (("network198", "key"), "xirgspu198"),
    (("network198", "lemon"), "yifkbco198"),
    (("network198", "a"), "network198"),
    (("network198", "zz"), "mdsvnqj198"),
    (("network198", "AgentU"), "nkxjhlk198"),
    (("network198", "keyboard"), "xirxcrb198"),
    (("network198", "AA"), "network198"),
    (("latency198", "key"), "verorai198"),
    (("latency198", "lemon"), "wefsanc198"),
    (("latency198", "a"), "latency198"),
    (("latency198", "zz"), "kzsdmbx198"),
    (("latency198", "AgentU"), "lgxrgwy198"),
    (("latency198", "keyboard"), "verfbcp198"),
    (("latency198", "AA"), "latency198"),
    (("buffer198", "key"), "lydpip198"),
    (("buffer198", "lemon"), "myrtrc198"),
    (("buffer198", "a"), "buffer198"),
    (("buffer198", "zz"), "ateedq198"),
    (("buffer198", "AgentU"), "bajsxl198"),
    (("buffer198", "keyboard"), "lydgsr198"),
    (("buffer198", "AA"), "buffer198"),
    (("queue198", "key"), "aycei198"),
    (("queue198", "lemon"), "byqir198"),
    (("queue198", "a"), "queue198"),
    (("queue198", "zz"), "ptdtd198"),
    (("queue198", "AgentU"), "qaihx198"),
    (("queue198", "keyboard"), "aycvs198"),
    (("queue198", "AA"), "queue198"),
    (("worker198", "key"), "gspuip198"),
    (("worker198", "lemon"), "hsdyrc198"),
    (("worker198", "a"), "worker198"),
    (("worker198", "zz"), "vnqjdq198"),
    (("worker198", "AgentU"), "wuvxxl198"),
    (("worker198", "keyboard"), "gsplsr198"),
    (("worker198", "AA"), "worker198"),
    (("kernel198", "key"), "uipxij198"),
    (("kernel198", "lemon"), "vidbrw198"),
    (("kernel198", "a"), "kernel198"),
    (("kernel198", "zz"), "jdqmdk198"),
    (("kernel198", "AgentU"), "kkvaxf198"),
    (("kernel198", "keyboard"), "uiposl198"),
    (("kernel198", "AA"), "kernel198"),
    (("signal198", "key"), "cmexej198"),
    (("signal198", "lemon"), "dmsbnw198"),
    (("signal198", "a"), "signal198"),
    (("signal198", "zz"), "rhfmzk198"),
    (("signal198", "AgentU"), "sokatf198"),
    (("signal198", "keyboard"), "cmeool198"),
    (("signal198", "AA"), "signal198"),
    (("packet198", "key"), "zeauir198"),
    (("packet198", "lemon"), "aeoyre198"),
    (("packet198", "a"), "packet198"),
    (("packet198", "zz"), "ozbjds198"),
    (("packet198", "AgentU"), "pggxxn198"),
    (("packet198", "keyboard"), "zealst198"),
    (("packet198", "AA"), "packet198"),
    (("router198", "key"), "bssdip198"),
    (("router198", "lemon"), "csghrc198"),
    (("router198", "a"), "router198"),
    (("router198", "zz"), "qntsdq198"),
    (("router198", "AgentU"), "ruygxl198"),
    (("router198", "keyboard"), "bssusr198"),
    (("router198", "AA"), "router198"),
    (("cluster198", "key"), "mpscxcb198"),
    (("cluster198", "lemon"), "npgggpv198"),
    (("cluster198", "a"), "cluster198"),
    (("cluster198", "zz"), "bktrsdq198"),
    (("cluster198", "AgentU"), "cryfmyr198"),
    (("cluster198", "keyboard"), "mpsthei198"),
    (("cluster198", "AA"), "cluster198"),
    (("mirror198", "key"), "wmpbsp198"),
    (("mirror198", "lemon"), "xmdfbc198"),
    (("mirror198", "a"), "mirror198"),
    (("mirror198", "zz"), "lhqqnq198"),
    (("mirror198", "AgentU"), "movehl198"),
    (("mirror198", "keyboard"), "wmpscr198"),
    (("mirror198", "AA"), "mirror198"),
    (("filter198", "key"), "pmjdip198"),
    (("filter198", "lemon"), "qmxhrc198"),
    (("filter198", "a"), "filter198"),
    (("filter198", "zz"), "ehksdq198"),
    (("filter198", "AgentU"), "fopgxl198"),
    (("filter198", "keyboard"), "pmjusr198"),
    (("filter198", "AA"), "filter198"),
    (("ranking198", "key"), "belumlq198"),
    (("ranking198", "lemon"), "cezyvyk198"),
    (("ranking198", "a"), "ranking198"),
    (("ranking198", "zz"), "qzmjhmf198"),
    (("ranking198", "AgentU"), "rgrxbhg198"),
    (("ranking198", "keyboard"), "bellwnx198"),
    (("ranking198", "AA"), "ranking198"),
    (("encoding198", "key"), "orayhgxk198"),
    (("encoding198", "lemon"), "procqtrs198"),
    (("encoding198", "a"), "encoding198"),
    (("encoding198", "zz"), "dmbnchmf198"),
    (("encoding198", "AgentU"), "etgbwcnm198"),
    (("encoding198", "keyboard"), "orapriej198"),
    (("encoding198", "AA"), "encoding198"),
    (("mapping198", "key"), "wenzmlq198"),
    (("mapping198", "lemon"), "xebdvyk198"),
    (("mapping198", "a"), "mapping198"),
    (("mapping198", "zz"), "lzoohmf198"),
    (("mapping198", "AgentU"), "mgtcbhg198"),
    (("mapping198", "keyboard"), "wenqwnx198"),
    (("mapping198", "AA"), "mapping198"),
    (("record198", "key"), "biayvb198"),
    (("record198", "lemon"), "cioceo198"),
    (("record198", "a"), "record198"),
    (("record198", "zz"), "qdbnqc198"),
    (("record198", "AgentU"), "rkgbkx198"),
    (("record198", "keyboard"), "biapfd198"),
    (("record198", "AA"), "record198"),
    (("candle198", "key"), "melnpc198"),
    (("candle198", "lemon"), "nezryp198"),
    (("candle198", "a"), "candle198"),
    (("candle198", "zz"), "bzmckd198"),
    (("candle198", "AgentU"), "cgrqey198"),
    (("candle198", "keyboard"), "meleze198"),
    (("candle198", "AA"), "candle198"),
    (("thread198", "key"), "dlpoeb198"),
    (("thread198", "lemon"), "eldsno198"),
    (("thread198", "a"), "thread198"),
    (("thread198", "zz"), "sgqdzc198"),
    (("thread198", "AgentU"), "tnvrtx198"),
    (("thread198", "keyboard"), "dlpfod198"),
    (("thread198", "AA"), "thread198"),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 198: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 198: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "a"),
        "round 198: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 198: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 198: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 198: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", "AA"),
        "round 198: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "key"),
        "bssxh 198: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 198: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "a"),
        "round 198: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 198: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 198: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 198: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", "AA"),
        "round 198: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 198: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 198: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "a"),
        "round 198: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 198: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 198: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 198: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", "AA"),
        "round 198: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 198: the processor reads the record then stops", "key"),
        "bssxh 198: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 198: the processor reads the record then stops", "lemon"),
        "csgbq 198: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 198: the processor reads the record then stops", "a"),
        "round 198: the processor reads the record then stops",
    ),
    (
        ("round 198: the processor reads the record then stops", "zz"),
        "qntmc 198: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 198: the processor reads the record then stops", "AgentU"),
        "ruyaw 198: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 198: the processor reads the record then stops", "keyboard"),
        "bssor 198: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 198: the processor reads the record then stops", "AA"),
        "round 198: the processor reads the record then stops",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "key"),
        "bssxh 198: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "lemon"),
        "csgbq 198: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "a"),
        "round 198: a worker pulls the next task from the queue",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "zz"),
        "qntmc 198: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 198: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "keyboard"),
        "bssor 198: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 198: a worker pulls the next task from the queue", "AA"),
        "round 198: a worker pulls the next task from the queue",
    ),
    (
        ("round 198: signals travel through the network layer", "key"),
        "bssxh 198: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 198: signals travel through the network layer", "lemon"),
        "csgbq 198: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 198: signals travel through the network layer", "a"),
        "round 198: signals travel through the network layer",
    ),
    (
        ("round 198: signals travel through the network layer", "zz"),
        "qntmc 198: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 198: signals travel through the network layer", "AgentU"),
        "ruyaw 198: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 198: signals travel through the network layer", "keyboard"),
        "bssor 198: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 198: signals travel through the network layer", "AA"),
        "round 198: signals travel through the network layer",
    ),
    (
        ("round 198: the gateway routes each request by policy", "key"),
        "bssxh 198: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 198: the gateway routes each request by policy", "lemon"),
        "csgbq 198: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 198: the gateway routes each request by policy", "a"),
        "round 198: the gateway routes each request by policy",
    ),
    (
        ("round 198: the gateway routes each request by policy", "zz"),
        "qntmc 198: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 198: the gateway routes each request by policy", "AgentU"),
        "ruyaw 198: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 198: the gateway routes each request by policy", "keyboard"),
        "bssor 198: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 198: the gateway routes each request by policy", "AA"),
        "round 198: the gateway routes each request by policy",
    ),
    (("round 198: memory grows until the buffer is full", "key"), "bssxh 198: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 198: memory grows until the buffer is full", "lemon"), "csgbq 198: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 198: memory grows until the buffer is full", "a"), "round 198: memory grows until the buffer is full"),
    (("round 198: memory grows until the buffer is full", "zz"), "qntmc 198: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 198: memory grows until the buffer is full", "AgentU"),
        "ruyaw 198: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 198: memory grows until the buffer is full", "keyboard"),
        "bssor 198: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 198: memory grows until the buffer is full", "AA"), "round 198: memory grows until the buffer is full"),
    (("round 198: the cluster mirrors every packet twice", "key"), "bssxh 198: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 198: the cluster mirrors every packet twice", "lemon"),
        "csgbq 198: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 198: the cluster mirrors every packet twice", "a"), "round 198: the cluster mirrors every packet twice"),
    (("round 198: the cluster mirrors every packet twice", "zz"), "qntmc 198: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 198: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 198: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 198: the cluster mirrors every packet twice", "keyboard"),
        "bssor 198: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 198: the cluster mirrors every packet twice", "AA"), "round 198: the cluster mirrors every packet twice"),
    (
        ("round 198: ranking uses tokens learned from the corpus", "key"),
        "bssxh 198: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 198: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", "a"),
        "round 198: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 198: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 198: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 198: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", "AA"),
        "round 198: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 198: a long session ends when the candle dies", "key"),
        "bssxh 198: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 198: a long session ends when the candle dies", "lemon"),
        "csgbq 198: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 198: a long session ends when the candle dies", "a"),
        "round 198: a long session ends when the candle dies",
    ),
    (
        ("round 198: a long session ends when the candle dies", "zz"),
        "qntmc 198: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 198: a long session ends when the candle dies", "AgentU"),
        "ruyaw 198: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 198: a long session ends when the candle dies", "keyboard"),
        "bssor 198: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 198: a long session ends when the candle dies", "AA"),
        "round 198: a long session ends when the candle dies",
    ),
    (("round 198: encode the prompt then map the result", "key"), "bssxh 198: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 198: encode the prompt then map the result", "lemon"), "csgbq 198: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 198: encode the prompt then map the result", "a"), "round 198: encode the prompt then map the result"),
    (("round 198: encode the prompt then map the result", "zz"), "qntmc 198: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 198: encode the prompt then map the result", "AgentU"),
        "ruyaw 198: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 198: encode the prompt then map the result", "keyboard"),
        "bssor 198: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 198: encode the prompt then map the result", "AA"), "round 198: encode the prompt then map the result"),
    (("round 198: the kernel wakes the worker at dawn", "key"), "bssxh 198: rri iovlop ukocc xfo ambocb er neux"),
    (("round 198: the kernel wakes the worker at dawn", "lemon"), "csgbq 198: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 198: the kernel wakes the worker at dawn", "a"), "round 198: the kernel wakes the worker at dawn"),
    (("round 198: the kernel wakes the worker at dawn", "zz"), "qntmc 198: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 198: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 198: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 198: the kernel wakes the worker at dawn", "keyboard"), "bssor 198: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 198: the kernel wakes the worker at dawn", "AA"), "round 198: the kernel wakes the worker at dawn"),
    (("round 198: service latency drops after the patch", "key"), "bssxh 198: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 198: service latency drops after the patch", "lemon"), "csgbq 198: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 198: service latency drops after the patch", "a"), "round 198: service latency drops after the patch"),
    (("round 198: service latency drops after the patch", "zz"), "qntmc 198: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 198: service latency drops after the patch", "AgentU"),
        "ruyaw 198: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 198: service latency drops after the patch", "keyboard"),
        "bssor 198: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 198: service latency drops after the patch", "AA"), "round 198: service latency drops after the patch"),
    (
        ("round 198: the library caches every vector it sees", "key"),
        "bssxh 198: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 198: the library caches every vector it sees", "lemon"),
        "csgbq 198: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 198: the library caches every vector it sees", "a"), "round 198: the library caches every vector it sees"),
    (
        ("round 198: the library caches every vector it sees", "zz"),
        "qntmc 198: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 198: the library caches every vector it sees", "AgentU"),
        "ruyaw 198: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 198: the library caches every vector it sees", "keyboard"),
        "bssor 198: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 198: the library caches every vector it sees", "AA"),
        "round 198: the library caches every vector it sees",
    ),
    (("round 198: agents argue then the debate resolves", "key"), "bssxh 198: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 198: agents argue then the debate resolves", "lemon"), "csgbq 198: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 198: agents argue then the debate resolves", "a"), "round 198: agents argue then the debate resolves"),
    (("round 198: agents argue then the debate resolves", "zz"), "qntmc 198: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 198: agents argue then the debate resolves", "AgentU"),
        "ruyaw 198: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 198: agents argue then the debate resolves", "keyboard"),
        "bssor 198: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 198: agents argue then the debate resolves", "AA"), "round 198: agents argue then the debate resolves"),
    (("round 198: the filter keeps only strong matches", "key"), "bssxh 198: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 198: the filter keeps only strong matches", "lemon"), "csgbq 198: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 198: the filter keeps only strong matches", "a"), "round 198: the filter keeps only strong matches"),
    (("round 198: the filter keeps only strong matches", "zz"), "qntmc 198: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 198: the filter keeps only strong matches", "AgentU"), "ruyaw 198: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 198: the filter keeps only strong matches", "keyboard"),
        "bssor 198: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 198: the filter keeps only strong matches", "AA"), "round 198: the filter keeps only strong matches"),
    (("round 198: the model answers with a short reply", "key"), "bssxh 198: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 198: the model answers with a short reply", "lemon"), "csgbq 198: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 198: the model answers with a short reply", "a"), "round 198: the model answers with a short reply"),
    (("round 198: the model answers with a short reply", "zz"), "qntmc 198: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 198: the model answers with a short reply", "AgentU"), "ruyaw 198: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 198: the model answers with a short reply", "keyboard"),
        "bssor 198: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 198: the model answers with a short reply", "AA"), "round 198: the model answers with a short reply"),
    (
        ("round 198: the recorder stores the reasoning trace", "key"),
        "bssxh 198: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 198: the recorder stores the reasoning trace", "lemon"),
        "csgbq 198: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 198: the recorder stores the reasoning trace", "a"), "round 198: the recorder stores the reasoning trace"),
    (
        ("round 198: the recorder stores the reasoning trace", "zz"),
        "qntmc 198: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 198: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 198: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 198: the recorder stores the reasoning trace", "keyboard"),
        "bssor 198: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 198: the recorder stores the reasoning trace", "AA"),
        "round 198: the recorder stores the reasoning trace",
    ),
    (("round 198: the angel watches the processor run", "key"), "bssxh 198: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 198: the angel watches the processor run", "lemon"), "csgbq 198: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 198: the angel watches the processor run", "a"), "round 198: the angel watches the processor run"),
    (("round 198: the angel watches the processor run", "zz"), "qntmc 198: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 198: the angel watches the processor run", "AgentU"), "ruyaw 198: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 198: the angel watches the processor run", "keyboard"), "bssor 198: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 198: the angel watches the processor run", "AA"), "round 198: the angel watches the processor run"),
    (("round 198: angle of the vector decides the match", "key"), "bssxh 198: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 198: angle of the vector decides the match", "lemon"), "csgbq 198: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 198: angle of the vector decides the match", "a"), "round 198: angle of the vector decides the match"),
    (("round 198: angle of the vector decides the match", "zz"), "qntmc 198: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 198: angle of the vector decides the match", "AgentU"),
        "ruyaw 198: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 198: angle of the vector decides the match", "keyboard"),
        "bssor 198: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 198: angle of the vector decides the match", "AA"), "round 198: angle of the vector decides the match"),
    (
        ("round 198: the candle burns twice as long at night", "key"),
        "bssxh 198: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 198: the candle burns twice as long at night", "lemon"),
        "csgbq 198: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 198: the candle burns twice as long at night", "a"), "round 198: the candle burns twice as long at night"),
    (
        ("round 198: the candle burns twice as long at night", "zz"),
        "qntmc 198: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 198: the candle burns twice as long at night", "AgentU"),
        "ruyaw 198: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 198: the candle burns twice as long at night", "keyboard"),
        "bssor 198: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 198: the candle burns twice as long at night", "AA"),
        "round 198: the candle burns twice as long at night",
    ),
    (("round 198: a mirror of the universe in one line", "key"), "bssxh 198: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 198: a mirror of the universe in one line", "lemon"), "csgbq 198: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 198: a mirror of the universe in one line", "a"), "round 198: a mirror of the universe in one line"),
    (("round 198: a mirror of the universe in one line", "zz"), "qntmc 198: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 198: a mirror of the universe in one line", "AgentU"), "ruyaw 198: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 198: a mirror of the universe in one line", "keyboard"),
        "bssor 198: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 198: a mirror of the universe in one line", "AA"), "round 198: a mirror of the universe in one line"),
    (("round 198: the queue drains before the storm", "key"), "bssxh 198: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 198: the queue drains before the storm", "lemon"), "csgbq 198: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 198: the queue drains before the storm", "a"), "round 198: the queue drains before the storm"),
    (("round 198: the queue drains before the storm", "zz"), "qntmc 198: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 198: the queue drains before the storm", "AgentU"), "ruyaw 198: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 198: the queue drains before the storm", "keyboard"), "bssor 198: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 198: the queue drains before the storm", "AA"), "round 198: the queue drains before the storm"),
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
