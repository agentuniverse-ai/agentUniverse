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
    (("kitten174", "key"), "umrdil174"),
    (("kitten174", "lemon"), "vmfhry174"),
    (("kitten174", "a"), "kitten174"),
    (("kitten174", "zz"), "jhssdm174"),
    (("kitten174", "AgentU"), "koxgxh174"),
    (("kitten174", "keyboard"), "umrusn174"),
    (("kitten174", "AA"), "kitten174"),
    (("sitting174", "key"), "cmrdmlq174"),
    (("sitting174", "lemon"), "dmfhvyk174"),
    (("sitting174", "a"), "sitting174"),
    (("sitting174", "zz"), "rhsshmf174"),
    (("sitting174", "AgentU"), "soxgbhg174"),
    (("sitting174", "keyboard"), "cmruwnx174"),
    (("sitting174", "AA"), "sitting174"),
    (("agent174", "key"), "kkcxx174"),
    (("agent174", "lemon"), "lkqbg174"),
    (("agent174", "a"), "agent174"),
    (("agent174", "zz"), "zfdms174"),
    (("agent174", "AgentU"), "amiam174"),
    (("agent174", "keyboard"), "kkcoh174"),
    (("agent174", "AA"), "agent174"),
    (("angle174", "key"), "krevi174"),
    (("angle174", "lemon"), "lrszr174"),
    (("angle174", "a"), "angle174"),
    (("angle174", "zz"), "zmfkd174"),
    (("angle174", "AgentU"), "atkyx174"),
    (("angle174", "keyboard"), "krems174"),
    (("angle174", "AA"), "angle174"),
    (("universe174", "key"), "ergfipci174"),
    (("universe174", "lemon"), "frujrcwq174"),
    (("universe174", "a"), "universe174"),
    (("universe174", "zz"), "tmhudqrd174"),
    (("universe174", "AgentU"), "utmixlsk174"),
    (("universe174", "keyboard"), "ergwsrjh174"),
    (("universe174", "AA"), "universe174"),
    (("memory174", "key"), "wikyvw174"),
    (("memory174", "lemon"), "xiycej174"),
    (("memory174", "a"), "memory174"),
    (("memory174", "zz"), "ldlnqx174"),
    (("memory174", "AgentU"), "mkqbks174"),
    (("memory174", "keyboard"), "wikpfy174"),
    (("memory174", "AA"), "memory174"),
    (("stream174", "key"), "cxpoek174"),
    (("stream174", "lemon"), "dxdsnx174"),
    (("stream174", "a"), "stream174"),
    (("stream174", "zz"), "rsqdzl174"),
    (("stream174", "AgentU"), "szvrtg174"),
    (("stream174", "keyboard"), "cxpfom174"),
    (("stream174", "AA"), "stream174"),
    (("context174", "key"), "msldivd174"),
    (("context174", "lemon"), "nszhrix174"),
    (("context174", "a"), "context174"),
    (("context174", "zz"), "bnmsdws174"),
    (("context174", "AgentU"), "curgxrt174"),
    (("context174", "keyboard"), "mslusxk174"),
    (("context174", "AA"), "context174"),
    (("knowledge174", "key"), "urmgpcnkc174"),
    (("knowledge174", "lemon"), "vrakyphss174"),
    (("knowledge174", "a"), "knowledge174"),
    (("knowledge174", "zz"), "jmnvkdcfd174"),
    (("knowledge174", "AgentU"), "ktsjeydmi174"),
    (("knowledge174", "keyboard"), "urmxzeujo174"),
    (("knowledge174", "AA"), "knowledge174"),
    (("vector174", "key"), "fiadsp174"),
    (("vector174", "lemon"), "giohbc174"),
    (("vector174", "a"), "vector174"),
    (("vector174", "zz"), "udbsnq174"),
    (("vector174", "AgentU"), "vkgghl174"),
    (("vector174", "keyboard"), "fiaucr174"),
    (("vector174", "AA"), "vector174"),
    (("processor174", "key"), "zvmmiqcsp174"),
    (("processor174", "lemon"), "avaqrdwaf174"),
    (("processor174", "a"), "processor174"),
    (("processor174", "zz"), "oqnbdrrnq174"),
    (("processor174", "AgentU"), "pxspxmsuv174"),
    (("processor174", "keyboard"), "zvmdssjrb174"),
    (("processor174", "AA"), "processor174"),
    (("reasoning174", "key"), "biycslsre174"),
    (("reasoning174", "lemon"), "cimgbymzu174"),
    (("reasoning174", "a"), "reasoning174"),
    (("reasoning174", "zz"), "qdzrnmhmf174"),
    (("reasoning174", "AgentU"), "rkefhhitk174"),
    (("reasoning174", "keyboard"), "biytcnzqq174"),
    (("reasoning174", "AA"), "reasoning174"),
    (("machine174", "key"), "wearmlo174"),
    (("machine174", "lemon"), "xeovvyi174"),
    (("machine174", "a"), "machine174"),
    (("machine174", "zz"), "lzbghmd174"),
    (("machine174", "AgentU"), "mggubhe174"),
    (("machine174", "keyboard"), "weaiwnv174"),
    (("machine174", "AA"), "machine174"),
    (("learning174", "key"), "viybrgxk174"),
    (("learning174", "lemon"), "wimfatrs174"),
    (("learning174", "a"), "learning174"),
    (("learning174", "zz"), "kdzqmhmf174"),
    (("learning174", "AgentU"), "lkeegcnm174"),
    (("learning174", "keyboard"), "viysbiej174"),
    (("learning174", "AA"), "learning174"),
    (("model174", "key"), "wsbop174"),
    (("model174", "lemon"), "xspsy174"),
    (("model174", "a"), "model174"),
    (("model174", "zz"), "lncdk174"),
    (("model174", "AgentU"), "muhre174"),
    (("model174", "keyboard"), "wsbfz174"),
    (("model174", "AA"), "model174"),
    (("token174", "key"), "dsior174"),
    (("token174", "lemon"), "eswsa174"),
    (("token174", "a"), "token174"),
    (("token174", "zz"), "snjdm174"),
    (("token174", "AgentU"), "tuorg174"),
    (("token174", "keyboard"), "dsifb174"),
    (("token174", "AA"), "token174"),
    (("prompt174", "key"), "zvmwtr174"),
    (("prompt174", "lemon"), "avaace174"),
    (("prompt174", "a"), "prompt174"),
    (("prompt174", "zz"), "oqnlos174"),
    (("prompt174", "AgentU"), "pxszin174"),
    (("prompt174", "keyboard"), "zvmndt174"),
    (("prompt174", "AA"), "prompt174"),
    (("session174", "key"), "ciqcmmx174"),
    (("session174", "lemon"), "diegvzr174"),
    (("session174", "a"), "session174"),
    (("session174", "zz"), "rdrrhnm174"),
    (("session174", "AgentU"), "skwfbin174"),
    (("session174", "keyboard"), "ciqtwoe174"),
    (("session174", "AA"), "session174"),
    (("library174", "key"), "vmzbepi174"),
    (("library174", "lemon"), "wmnfncc174"),
    (("library174", "a"), "library174"),
    (("library174", "zz"), "khaqzqx174"),
    (("library174", "AgentU"), "lofetly174"),
    (("library174", "keyboard"), "vmzsorp174"),
    (("library174", "AA"), "library174"),
    (("service174", "key"), "cipfmao174"),
    (("service174", "lemon"), "didjvni174"),
    (("service174", "a"), "service174"),
    (("service174", "zz"), "rdquhbd174"),
    (("service174", "AgentU"), "skvibwe174"),
    (("service174", "keyboard"), "cipwwcv174"),
    (("service174", "AA"), "service174"),
    (("gateway174", "key"), "qeroayi174"),
    (("gateway174", "lemon"), "refsjlc174"),
    (("gateway174", "a"), "gateway174"),
    (("gateway174", "zz"), "fzsdvzx174"),
    (("gateway174", "AgentU"), "ggxrpuy174"),
    (("gateway174", "keyboard"), "qerfkap174"),
    (("gateway174", "AA"), "gateway174"),
    (("storage174", "key"), "cxmbeeo174"),
    (("storage174", "lemon"), "dxafnri174"),
    (("storage174", "a"), "storage174"),
    (("storage174", "zz"), "rsnqzfd174"),
    (("storage174", "AgentU"), "szsetae174"),
    (("storage174", "keyboard"), "cxmsogv174"),
    (("storage174", "AA"), "storage174"),
    (("network174", "key"), "xirgspu174"),
    (("network174", "lemon"), "yifkbco174"),
    (("network174", "a"), "network174"),
    (("network174", "zz"), "mdsvnqj174"),
    (("network174", "AgentU"), "nkxjhlk174"),
    (("network174", "keyboard"), "xirxcrb174"),
    (("network174", "AA"), "network174"),
    (("latency174", "key"), "verorai174"),
    (("latency174", "lemon"), "wefsanc174"),
    (("latency174", "a"), "latency174"),
    (("latency174", "zz"), "kzsdmbx174"),
    (("latency174", "AgentU"), "lgxrgwy174"),
    (("latency174", "keyboard"), "verfbcp174"),
    (("latency174", "AA"), "latency174"),
    (("buffer174", "key"), "lydpip174"),
    (("buffer174", "lemon"), "myrtrc174"),
    (("buffer174", "a"), "buffer174"),
    (("buffer174", "zz"), "ateedq174"),
    (("buffer174", "AgentU"), "bajsxl174"),
    (("buffer174", "keyboard"), "lydgsr174"),
    (("buffer174", "AA"), "buffer174"),
    (("queue174", "key"), "aycei174"),
    (("queue174", "lemon"), "byqir174"),
    (("queue174", "a"), "queue174"),
    (("queue174", "zz"), "ptdtd174"),
    (("queue174", "AgentU"), "qaihx174"),
    (("queue174", "keyboard"), "aycvs174"),
    (("queue174", "AA"), "queue174"),
    (("worker174", "key"), "gspuip174"),
    (("worker174", "lemon"), "hsdyrc174"),
    (("worker174", "a"), "worker174"),
    (("worker174", "zz"), "vnqjdq174"),
    (("worker174", "AgentU"), "wuvxxl174"),
    (("worker174", "keyboard"), "gsplsr174"),
    (("worker174", "AA"), "worker174"),
    (("kernel174", "key"), "uipxij174"),
    (("kernel174", "lemon"), "vidbrw174"),
    (("kernel174", "a"), "kernel174"),
    (("kernel174", "zz"), "jdqmdk174"),
    (("kernel174", "AgentU"), "kkvaxf174"),
    (("kernel174", "keyboard"), "uiposl174"),
    (("kernel174", "AA"), "kernel174"),
    (("signal174", "key"), "cmexej174"),
    (("signal174", "lemon"), "dmsbnw174"),
    (("signal174", "a"), "signal174"),
    (("signal174", "zz"), "rhfmzk174"),
    (("signal174", "AgentU"), "sokatf174"),
    (("signal174", "keyboard"), "cmeool174"),
    (("signal174", "AA"), "signal174"),
    (("packet174", "key"), "zeauir174"),
    (("packet174", "lemon"), "aeoyre174"),
    (("packet174", "a"), "packet174"),
    (("packet174", "zz"), "ozbjds174"),
    (("packet174", "AgentU"), "pggxxn174"),
    (("packet174", "keyboard"), "zealst174"),
    (("packet174", "AA"), "packet174"),
    (("router174", "key"), "bssdip174"),
    (("router174", "lemon"), "csghrc174"),
    (("router174", "a"), "router174"),
    (("router174", "zz"), "qntsdq174"),
    (("router174", "AgentU"), "ruygxl174"),
    (("router174", "keyboard"), "bssusr174"),
    (("router174", "AA"), "router174"),
    (("cluster174", "key"), "mpscxcb174"),
    (("cluster174", "lemon"), "npgggpv174"),
    (("cluster174", "a"), "cluster174"),
    (("cluster174", "zz"), "bktrsdq174"),
    (("cluster174", "AgentU"), "cryfmyr174"),
    (("cluster174", "keyboard"), "mpsthei174"),
    (("cluster174", "AA"), "cluster174"),
    (("mirror174", "key"), "wmpbsp174"),
    (("mirror174", "lemon"), "xmdfbc174"),
    (("mirror174", "a"), "mirror174"),
    (("mirror174", "zz"), "lhqqnq174"),
    (("mirror174", "AgentU"), "movehl174"),
    (("mirror174", "keyboard"), "wmpscr174"),
    (("mirror174", "AA"), "mirror174"),
    (("filter174", "key"), "pmjdip174"),
    (("filter174", "lemon"), "qmxhrc174"),
    (("filter174", "a"), "filter174"),
    (("filter174", "zz"), "ehksdq174"),
    (("filter174", "AgentU"), "fopgxl174"),
    (("filter174", "keyboard"), "pmjusr174"),
    (("filter174", "AA"), "filter174"),
    (("ranking174", "key"), "belumlq174"),
    (("ranking174", "lemon"), "cezyvyk174"),
    (("ranking174", "a"), "ranking174"),
    (("ranking174", "zz"), "qzmjhmf174"),
    (("ranking174", "AgentU"), "rgrxbhg174"),
    (("ranking174", "keyboard"), "bellwnx174"),
    (("ranking174", "AA"), "ranking174"),
    (("encoding174", "key"), "orayhgxk174"),
    (("encoding174", "lemon"), "procqtrs174"),
    (("encoding174", "a"), "encoding174"),
    (("encoding174", "zz"), "dmbnchmf174"),
    (("encoding174", "AgentU"), "etgbwcnm174"),
    (("encoding174", "keyboard"), "orapriej174"),
    (("encoding174", "AA"), "encoding174"),
    (("mapping174", "key"), "wenzmlq174"),
    (("mapping174", "lemon"), "xebdvyk174"),
    (("mapping174", "a"), "mapping174"),
    (("mapping174", "zz"), "lzoohmf174"),
    (("mapping174", "AgentU"), "mgtcbhg174"),
    (("mapping174", "keyboard"), "wenqwnx174"),
    (("mapping174", "AA"), "mapping174"),
    (("record174", "key"), "biayvb174"),
    (("record174", "lemon"), "cioceo174"),
    (("record174", "a"), "record174"),
    (("record174", "zz"), "qdbnqc174"),
    (("record174", "AgentU"), "rkgbkx174"),
    (("record174", "keyboard"), "biapfd174"),
    (("record174", "AA"), "record174"),
    (("candle174", "key"), "melnpc174"),
    (("candle174", "lemon"), "nezryp174"),
    (("candle174", "a"), "candle174"),
    (("candle174", "zz"), "bzmckd174"),
    (("candle174", "AgentU"), "cgrqey174"),
    (("candle174", "keyboard"), "meleze174"),
    (("candle174", "AA"), "candle174"),
    (("thread174", "key"), "dlpoeb174"),
    (("thread174", "lemon"), "eldsno174"),
    (("thread174", "a"), "thread174"),
    (("thread174", "zz"), "sgqdzc174"),
    (("thread174", "AgentU"), "tnvrtx174"),
    (("thread174", "keyboard"), "dlpfod174"),
    (("thread174", "AA"), "thread174"),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 174: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 174: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "a"),
        "round 174: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 174: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 174: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 174: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", "AA"),
        "round 174: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "key"),
        "bssxh 174: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 174: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "a"),
        "round 174: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 174: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 174: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 174: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", "AA"),
        "round 174: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 174: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 174: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "a"),
        "round 174: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 174: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 174: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 174: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", "AA"),
        "round 174: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 174: the processor reads the record then stops", "key"),
        "bssxh 174: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 174: the processor reads the record then stops", "lemon"),
        "csgbq 174: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 174: the processor reads the record then stops", "a"),
        "round 174: the processor reads the record then stops",
    ),
    (
        ("round 174: the processor reads the record then stops", "zz"),
        "qntmc 174: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 174: the processor reads the record then stops", "AgentU"),
        "ruyaw 174: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 174: the processor reads the record then stops", "keyboard"),
        "bssor 174: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 174: the processor reads the record then stops", "AA"),
        "round 174: the processor reads the record then stops",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "key"),
        "bssxh 174: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "lemon"),
        "csgbq 174: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "a"),
        "round 174: a worker pulls the next task from the queue",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "zz"),
        "qntmc 174: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 174: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "keyboard"),
        "bssor 174: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 174: a worker pulls the next task from the queue", "AA"),
        "round 174: a worker pulls the next task from the queue",
    ),
    (
        ("round 174: signals travel through the network layer", "key"),
        "bssxh 174: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 174: signals travel through the network layer", "lemon"),
        "csgbq 174: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 174: signals travel through the network layer", "a"),
        "round 174: signals travel through the network layer",
    ),
    (
        ("round 174: signals travel through the network layer", "zz"),
        "qntmc 174: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 174: signals travel through the network layer", "AgentU"),
        "ruyaw 174: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 174: signals travel through the network layer", "keyboard"),
        "bssor 174: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 174: signals travel through the network layer", "AA"),
        "round 174: signals travel through the network layer",
    ),
    (
        ("round 174: the gateway routes each request by policy", "key"),
        "bssxh 174: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 174: the gateway routes each request by policy", "lemon"),
        "csgbq 174: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 174: the gateway routes each request by policy", "a"),
        "round 174: the gateway routes each request by policy",
    ),
    (
        ("round 174: the gateway routes each request by policy", "zz"),
        "qntmc 174: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 174: the gateway routes each request by policy", "AgentU"),
        "ruyaw 174: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 174: the gateway routes each request by policy", "keyboard"),
        "bssor 174: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 174: the gateway routes each request by policy", "AA"),
        "round 174: the gateway routes each request by policy",
    ),
    (("round 174: memory grows until the buffer is full", "key"), "bssxh 174: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 174: memory grows until the buffer is full", "lemon"), "csgbq 174: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 174: memory grows until the buffer is full", "a"), "round 174: memory grows until the buffer is full"),
    (("round 174: memory grows until the buffer is full", "zz"), "qntmc 174: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 174: memory grows until the buffer is full", "AgentU"),
        "ruyaw 174: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 174: memory grows until the buffer is full", "keyboard"),
        "bssor 174: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 174: memory grows until the buffer is full", "AA"), "round 174: memory grows until the buffer is full"),
    (("round 174: the cluster mirrors every packet twice", "key"), "bssxh 174: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 174: the cluster mirrors every packet twice", "lemon"),
        "csgbq 174: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 174: the cluster mirrors every packet twice", "a"), "round 174: the cluster mirrors every packet twice"),
    (("round 174: the cluster mirrors every packet twice", "zz"), "qntmc 174: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 174: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 174: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 174: the cluster mirrors every packet twice", "keyboard"),
        "bssor 174: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 174: the cluster mirrors every packet twice", "AA"), "round 174: the cluster mirrors every packet twice"),
    (
        ("round 174: ranking uses tokens learned from the corpus", "key"),
        "bssxh 174: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 174: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", "a"),
        "round 174: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 174: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 174: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 174: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", "AA"),
        "round 174: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 174: a long session ends when the candle dies", "key"),
        "bssxh 174: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 174: a long session ends when the candle dies", "lemon"),
        "csgbq 174: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 174: a long session ends when the candle dies", "a"),
        "round 174: a long session ends when the candle dies",
    ),
    (
        ("round 174: a long session ends when the candle dies", "zz"),
        "qntmc 174: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 174: a long session ends when the candle dies", "AgentU"),
        "ruyaw 174: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 174: a long session ends when the candle dies", "keyboard"),
        "bssor 174: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 174: a long session ends when the candle dies", "AA"),
        "round 174: a long session ends when the candle dies",
    ),
    (("round 174: encode the prompt then map the result", "key"), "bssxh 174: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 174: encode the prompt then map the result", "lemon"), "csgbq 174: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 174: encode the prompt then map the result", "a"), "round 174: encode the prompt then map the result"),
    (("round 174: encode the prompt then map the result", "zz"), "qntmc 174: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 174: encode the prompt then map the result", "AgentU"),
        "ruyaw 174: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 174: encode the prompt then map the result", "keyboard"),
        "bssor 174: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 174: encode the prompt then map the result", "AA"), "round 174: encode the prompt then map the result"),
    (("round 174: the kernel wakes the worker at dawn", "key"), "bssxh 174: rri iovlop ukocc xfo ambocb er neux"),
    (("round 174: the kernel wakes the worker at dawn", "lemon"), "csgbq 174: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 174: the kernel wakes the worker at dawn", "a"), "round 174: the kernel wakes the worker at dawn"),
    (("round 174: the kernel wakes the worker at dawn", "zz"), "qntmc 174: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 174: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 174: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 174: the kernel wakes the worker at dawn", "keyboard"), "bssor 174: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 174: the kernel wakes the worker at dawn", "AA"), "round 174: the kernel wakes the worker at dawn"),
    (("round 174: service latency drops after the patch", "key"), "bssxh 174: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 174: service latency drops after the patch", "lemon"), "csgbq 174: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 174: service latency drops after the patch", "a"), "round 174: service latency drops after the patch"),
    (("round 174: service latency drops after the patch", "zz"), "qntmc 174: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 174: service latency drops after the patch", "AgentU"),
        "ruyaw 174: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 174: service latency drops after the patch", "keyboard"),
        "bssor 174: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 174: service latency drops after the patch", "AA"), "round 174: service latency drops after the patch"),
    (
        ("round 174: the library caches every vector it sees", "key"),
        "bssxh 174: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 174: the library caches every vector it sees", "lemon"),
        "csgbq 174: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 174: the library caches every vector it sees", "a"), "round 174: the library caches every vector it sees"),
    (
        ("round 174: the library caches every vector it sees", "zz"),
        "qntmc 174: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 174: the library caches every vector it sees", "AgentU"),
        "ruyaw 174: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 174: the library caches every vector it sees", "keyboard"),
        "bssor 174: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 174: the library caches every vector it sees", "AA"),
        "round 174: the library caches every vector it sees",
    ),
    (("round 174: agents argue then the debate resolves", "key"), "bssxh 174: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 174: agents argue then the debate resolves", "lemon"), "csgbq 174: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 174: agents argue then the debate resolves", "a"), "round 174: agents argue then the debate resolves"),
    (("round 174: agents argue then the debate resolves", "zz"), "qntmc 174: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 174: agents argue then the debate resolves", "AgentU"),
        "ruyaw 174: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 174: agents argue then the debate resolves", "keyboard"),
        "bssor 174: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 174: agents argue then the debate resolves", "AA"), "round 174: agents argue then the debate resolves"),
    (("round 174: the filter keeps only strong matches", "key"), "bssxh 174: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 174: the filter keeps only strong matches", "lemon"), "csgbq 174: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 174: the filter keeps only strong matches", "a"), "round 174: the filter keeps only strong matches"),
    (("round 174: the filter keeps only strong matches", "zz"), "qntmc 174: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 174: the filter keeps only strong matches", "AgentU"), "ruyaw 174: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 174: the filter keeps only strong matches", "keyboard"),
        "bssor 174: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 174: the filter keeps only strong matches", "AA"), "round 174: the filter keeps only strong matches"),
    (("round 174: the model answers with a short reply", "key"), "bssxh 174: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 174: the model answers with a short reply", "lemon"), "csgbq 174: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 174: the model answers with a short reply", "a"), "round 174: the model answers with a short reply"),
    (("round 174: the model answers with a short reply", "zz"), "qntmc 174: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 174: the model answers with a short reply", "AgentU"), "ruyaw 174: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 174: the model answers with a short reply", "keyboard"),
        "bssor 174: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 174: the model answers with a short reply", "AA"), "round 174: the model answers with a short reply"),
    (
        ("round 174: the recorder stores the reasoning trace", "key"),
        "bssxh 174: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 174: the recorder stores the reasoning trace", "lemon"),
        "csgbq 174: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 174: the recorder stores the reasoning trace", "a"), "round 174: the recorder stores the reasoning trace"),
    (
        ("round 174: the recorder stores the reasoning trace", "zz"),
        "qntmc 174: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 174: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 174: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 174: the recorder stores the reasoning trace", "keyboard"),
        "bssor 174: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 174: the recorder stores the reasoning trace", "AA"),
        "round 174: the recorder stores the reasoning trace",
    ),
    (("round 174: the angel watches the processor run", "key"), "bssxh 174: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 174: the angel watches the processor run", "lemon"), "csgbq 174: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 174: the angel watches the processor run", "a"), "round 174: the angel watches the processor run"),
    (("round 174: the angel watches the processor run", "zz"), "qntmc 174: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 174: the angel watches the processor run", "AgentU"), "ruyaw 174: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 174: the angel watches the processor run", "keyboard"), "bssor 174: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 174: the angel watches the processor run", "AA"), "round 174: the angel watches the processor run"),
    (("round 174: angle of the vector decides the match", "key"), "bssxh 174: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 174: angle of the vector decides the match", "lemon"), "csgbq 174: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 174: angle of the vector decides the match", "a"), "round 174: angle of the vector decides the match"),
    (("round 174: angle of the vector decides the match", "zz"), "qntmc 174: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 174: angle of the vector decides the match", "AgentU"),
        "ruyaw 174: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 174: angle of the vector decides the match", "keyboard"),
        "bssor 174: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 174: angle of the vector decides the match", "AA"), "round 174: angle of the vector decides the match"),
    (
        ("round 174: the candle burns twice as long at night", "key"),
        "bssxh 174: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 174: the candle burns twice as long at night", "lemon"),
        "csgbq 174: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 174: the candle burns twice as long at night", "a"), "round 174: the candle burns twice as long at night"),
    (
        ("round 174: the candle burns twice as long at night", "zz"),
        "qntmc 174: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 174: the candle burns twice as long at night", "AgentU"),
        "ruyaw 174: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 174: the candle burns twice as long at night", "keyboard"),
        "bssor 174: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 174: the candle burns twice as long at night", "AA"),
        "round 174: the candle burns twice as long at night",
    ),
    (("round 174: a mirror of the universe in one line", "key"), "bssxh 174: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 174: a mirror of the universe in one line", "lemon"), "csgbq 174: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 174: a mirror of the universe in one line", "a"), "round 174: a mirror of the universe in one line"),
    (("round 174: a mirror of the universe in one line", "zz"), "qntmc 174: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 174: a mirror of the universe in one line", "AgentU"), "ruyaw 174: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 174: a mirror of the universe in one line", "keyboard"),
        "bssor 174: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 174: a mirror of the universe in one line", "AA"), "round 174: a mirror of the universe in one line"),
    (("round 174: the queue drains before the storm", "key"), "bssxh 174: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 174: the queue drains before the storm", "lemon"), "csgbq 174: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 174: the queue drains before the storm", "a"), "round 174: the queue drains before the storm"),
    (("round 174: the queue drains before the storm", "zz"), "qntmc 174: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 174: the queue drains before the storm", "AgentU"), "ruyaw 174: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 174: the queue drains before the storm", "keyboard"), "bssor 174: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 174: the queue drains before the storm", "AA"), "round 174: the queue drains before the storm"),
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
