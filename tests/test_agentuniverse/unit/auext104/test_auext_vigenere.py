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
    (("kitten104", "key"), "umrdil104"),
    (("kitten104", "lemon"), "vmfhry104"),
    (("kitten104", "a"), "kitten104"),
    (("kitten104", "zz"), "jhssdm104"),
    (("kitten104", "AgentU"), "koxgxh104"),
    (("kitten104", "keyboard"), "umrusn104"),
    (("kitten104", "AA"), "kitten104"),
    (("sitting104", "key"), "cmrdmlq104"),
    (("sitting104", "lemon"), "dmfhvyk104"),
    (("sitting104", "a"), "sitting104"),
    (("sitting104", "zz"), "rhsshmf104"),
    (("sitting104", "AgentU"), "soxgbhg104"),
    (("sitting104", "keyboard"), "cmruwnx104"),
    (("sitting104", "AA"), "sitting104"),
    (("agent104", "key"), "kkcxx104"),
    (("agent104", "lemon"), "lkqbg104"),
    (("agent104", "a"), "agent104"),
    (("agent104", "zz"), "zfdms104"),
    (("agent104", "AgentU"), "amiam104"),
    (("agent104", "keyboard"), "kkcoh104"),
    (("agent104", "AA"), "agent104"),
    (("angle104", "key"), "krevi104"),
    (("angle104", "lemon"), "lrszr104"),
    (("angle104", "a"), "angle104"),
    (("angle104", "zz"), "zmfkd104"),
    (("angle104", "AgentU"), "atkyx104"),
    (("angle104", "keyboard"), "krems104"),
    (("angle104", "AA"), "angle104"),
    (("universe104", "key"), "ergfipci104"),
    (("universe104", "lemon"), "frujrcwq104"),
    (("universe104", "a"), "universe104"),
    (("universe104", "zz"), "tmhudqrd104"),
    (("universe104", "AgentU"), "utmixlsk104"),
    (("universe104", "keyboard"), "ergwsrjh104"),
    (("universe104", "AA"), "universe104"),
    (("memory104", "key"), "wikyvw104"),
    (("memory104", "lemon"), "xiycej104"),
    (("memory104", "a"), "memory104"),
    (("memory104", "zz"), "ldlnqx104"),
    (("memory104", "AgentU"), "mkqbks104"),
    (("memory104", "keyboard"), "wikpfy104"),
    (("memory104", "AA"), "memory104"),
    (("stream104", "key"), "cxpoek104"),
    (("stream104", "lemon"), "dxdsnx104"),
    (("stream104", "a"), "stream104"),
    (("stream104", "zz"), "rsqdzl104"),
    (("stream104", "AgentU"), "szvrtg104"),
    (("stream104", "keyboard"), "cxpfom104"),
    (("stream104", "AA"), "stream104"),
    (("context104", "key"), "msldivd104"),
    (("context104", "lemon"), "nszhrix104"),
    (("context104", "a"), "context104"),
    (("context104", "zz"), "bnmsdws104"),
    (("context104", "AgentU"), "curgxrt104"),
    (("context104", "keyboard"), "mslusxk104"),
    (("context104", "AA"), "context104"),
    (("knowledge104", "key"), "urmgpcnkc104"),
    (("knowledge104", "lemon"), "vrakyphss104"),
    (("knowledge104", "a"), "knowledge104"),
    (("knowledge104", "zz"), "jmnvkdcfd104"),
    (("knowledge104", "AgentU"), "ktsjeydmi104"),
    (("knowledge104", "keyboard"), "urmxzeujo104"),
    (("knowledge104", "AA"), "knowledge104"),
    (("vector104", "key"), "fiadsp104"),
    (("vector104", "lemon"), "giohbc104"),
    (("vector104", "a"), "vector104"),
    (("vector104", "zz"), "udbsnq104"),
    (("vector104", "AgentU"), "vkgghl104"),
    (("vector104", "keyboard"), "fiaucr104"),
    (("vector104", "AA"), "vector104"),
    (("processor104", "key"), "zvmmiqcsp104"),
    (("processor104", "lemon"), "avaqrdwaf104"),
    (("processor104", "a"), "processor104"),
    (("processor104", "zz"), "oqnbdrrnq104"),
    (("processor104", "AgentU"), "pxspxmsuv104"),
    (("processor104", "keyboard"), "zvmdssjrb104"),
    (("processor104", "AA"), "processor104"),
    (("reasoning104", "key"), "biycslsre104"),
    (("reasoning104", "lemon"), "cimgbymzu104"),
    (("reasoning104", "a"), "reasoning104"),
    (("reasoning104", "zz"), "qdzrnmhmf104"),
    (("reasoning104", "AgentU"), "rkefhhitk104"),
    (("reasoning104", "keyboard"), "biytcnzqq104"),
    (("reasoning104", "AA"), "reasoning104"),
    (("machine104", "key"), "wearmlo104"),
    (("machine104", "lemon"), "xeovvyi104"),
    (("machine104", "a"), "machine104"),
    (("machine104", "zz"), "lzbghmd104"),
    (("machine104", "AgentU"), "mggubhe104"),
    (("machine104", "keyboard"), "weaiwnv104"),
    (("machine104", "AA"), "machine104"),
    (("learning104", "key"), "viybrgxk104"),
    (("learning104", "lemon"), "wimfatrs104"),
    (("learning104", "a"), "learning104"),
    (("learning104", "zz"), "kdzqmhmf104"),
    (("learning104", "AgentU"), "lkeegcnm104"),
    (("learning104", "keyboard"), "viysbiej104"),
    (("learning104", "AA"), "learning104"),
    (("model104", "key"), "wsbop104"),
    (("model104", "lemon"), "xspsy104"),
    (("model104", "a"), "model104"),
    (("model104", "zz"), "lncdk104"),
    (("model104", "AgentU"), "muhre104"),
    (("model104", "keyboard"), "wsbfz104"),
    (("model104", "AA"), "model104"),
    (("token104", "key"), "dsior104"),
    (("token104", "lemon"), "eswsa104"),
    (("token104", "a"), "token104"),
    (("token104", "zz"), "snjdm104"),
    (("token104", "AgentU"), "tuorg104"),
    (("token104", "keyboard"), "dsifb104"),
    (("token104", "AA"), "token104"),
    (("prompt104", "key"), "zvmwtr104"),
    (("prompt104", "lemon"), "avaace104"),
    (("prompt104", "a"), "prompt104"),
    (("prompt104", "zz"), "oqnlos104"),
    (("prompt104", "AgentU"), "pxszin104"),
    (("prompt104", "keyboard"), "zvmndt104"),
    (("prompt104", "AA"), "prompt104"),
    (("session104", "key"), "ciqcmmx104"),
    (("session104", "lemon"), "diegvzr104"),
    (("session104", "a"), "session104"),
    (("session104", "zz"), "rdrrhnm104"),
    (("session104", "AgentU"), "skwfbin104"),
    (("session104", "keyboard"), "ciqtwoe104"),
    (("session104", "AA"), "session104"),
    (("library104", "key"), "vmzbepi104"),
    (("library104", "lemon"), "wmnfncc104"),
    (("library104", "a"), "library104"),
    (("library104", "zz"), "khaqzqx104"),
    (("library104", "AgentU"), "lofetly104"),
    (("library104", "keyboard"), "vmzsorp104"),
    (("library104", "AA"), "library104"),
    (("service104", "key"), "cipfmao104"),
    (("service104", "lemon"), "didjvni104"),
    (("service104", "a"), "service104"),
    (("service104", "zz"), "rdquhbd104"),
    (("service104", "AgentU"), "skvibwe104"),
    (("service104", "keyboard"), "cipwwcv104"),
    (("service104", "AA"), "service104"),
    (("gateway104", "key"), "qeroayi104"),
    (("gateway104", "lemon"), "refsjlc104"),
    (("gateway104", "a"), "gateway104"),
    (("gateway104", "zz"), "fzsdvzx104"),
    (("gateway104", "AgentU"), "ggxrpuy104"),
    (("gateway104", "keyboard"), "qerfkap104"),
    (("gateway104", "AA"), "gateway104"),
    (("storage104", "key"), "cxmbeeo104"),
    (("storage104", "lemon"), "dxafnri104"),
    (("storage104", "a"), "storage104"),
    (("storage104", "zz"), "rsnqzfd104"),
    (("storage104", "AgentU"), "szsetae104"),
    (("storage104", "keyboard"), "cxmsogv104"),
    (("storage104", "AA"), "storage104"),
    (("network104", "key"), "xirgspu104"),
    (("network104", "lemon"), "yifkbco104"),
    (("network104", "a"), "network104"),
    (("network104", "zz"), "mdsvnqj104"),
    (("network104", "AgentU"), "nkxjhlk104"),
    (("network104", "keyboard"), "xirxcrb104"),
    (("network104", "AA"), "network104"),
    (("latency104", "key"), "verorai104"),
    (("latency104", "lemon"), "wefsanc104"),
    (("latency104", "a"), "latency104"),
    (("latency104", "zz"), "kzsdmbx104"),
    (("latency104", "AgentU"), "lgxrgwy104"),
    (("latency104", "keyboard"), "verfbcp104"),
    (("latency104", "AA"), "latency104"),
    (("buffer104", "key"), "lydpip104"),
    (("buffer104", "lemon"), "myrtrc104"),
    (("buffer104", "a"), "buffer104"),
    (("buffer104", "zz"), "ateedq104"),
    (("buffer104", "AgentU"), "bajsxl104"),
    (("buffer104", "keyboard"), "lydgsr104"),
    (("buffer104", "AA"), "buffer104"),
    (("queue104", "key"), "aycei104"),
    (("queue104", "lemon"), "byqir104"),
    (("queue104", "a"), "queue104"),
    (("queue104", "zz"), "ptdtd104"),
    (("queue104", "AgentU"), "qaihx104"),
    (("queue104", "keyboard"), "aycvs104"),
    (("queue104", "AA"), "queue104"),
    (("worker104", "key"), "gspuip104"),
    (("worker104", "lemon"), "hsdyrc104"),
    (("worker104", "a"), "worker104"),
    (("worker104", "zz"), "vnqjdq104"),
    (("worker104", "AgentU"), "wuvxxl104"),
    (("worker104", "keyboard"), "gsplsr104"),
    (("worker104", "AA"), "worker104"),
    (("kernel104", "key"), "uipxij104"),
    (("kernel104", "lemon"), "vidbrw104"),
    (("kernel104", "a"), "kernel104"),
    (("kernel104", "zz"), "jdqmdk104"),
    (("kernel104", "AgentU"), "kkvaxf104"),
    (("kernel104", "keyboard"), "uiposl104"),
    (("kernel104", "AA"), "kernel104"),
    (("signal104", "key"), "cmexej104"),
    (("signal104", "lemon"), "dmsbnw104"),
    (("signal104", "a"), "signal104"),
    (("signal104", "zz"), "rhfmzk104"),
    (("signal104", "AgentU"), "sokatf104"),
    (("signal104", "keyboard"), "cmeool104"),
    (("signal104", "AA"), "signal104"),
    (("packet104", "key"), "zeauir104"),
    (("packet104", "lemon"), "aeoyre104"),
    (("packet104", "a"), "packet104"),
    (("packet104", "zz"), "ozbjds104"),
    (("packet104", "AgentU"), "pggxxn104"),
    (("packet104", "keyboard"), "zealst104"),
    (("packet104", "AA"), "packet104"),
    (("router104", "key"), "bssdip104"),
    (("router104", "lemon"), "csghrc104"),
    (("router104", "a"), "router104"),
    (("router104", "zz"), "qntsdq104"),
    (("router104", "AgentU"), "ruygxl104"),
    (("router104", "keyboard"), "bssusr104"),
    (("router104", "AA"), "router104"),
    (("cluster104", "key"), "mpscxcb104"),
    (("cluster104", "lemon"), "npgggpv104"),
    (("cluster104", "a"), "cluster104"),
    (("cluster104", "zz"), "bktrsdq104"),
    (("cluster104", "AgentU"), "cryfmyr104"),
    (("cluster104", "keyboard"), "mpsthei104"),
    (("cluster104", "AA"), "cluster104"),
    (("mirror104", "key"), "wmpbsp104"),
    (("mirror104", "lemon"), "xmdfbc104"),
    (("mirror104", "a"), "mirror104"),
    (("mirror104", "zz"), "lhqqnq104"),
    (("mirror104", "AgentU"), "movehl104"),
    (("mirror104", "keyboard"), "wmpscr104"),
    (("mirror104", "AA"), "mirror104"),
    (("filter104", "key"), "pmjdip104"),
    (("filter104", "lemon"), "qmxhrc104"),
    (("filter104", "a"), "filter104"),
    (("filter104", "zz"), "ehksdq104"),
    (("filter104", "AgentU"), "fopgxl104"),
    (("filter104", "keyboard"), "pmjusr104"),
    (("filter104", "AA"), "filter104"),
    (("ranking104", "key"), "belumlq104"),
    (("ranking104", "lemon"), "cezyvyk104"),
    (("ranking104", "a"), "ranking104"),
    (("ranking104", "zz"), "qzmjhmf104"),
    (("ranking104", "AgentU"), "rgrxbhg104"),
    (("ranking104", "keyboard"), "bellwnx104"),
    (("ranking104", "AA"), "ranking104"),
    (("encoding104", "key"), "orayhgxk104"),
    (("encoding104", "lemon"), "procqtrs104"),
    (("encoding104", "a"), "encoding104"),
    (("encoding104", "zz"), "dmbnchmf104"),
    (("encoding104", "AgentU"), "etgbwcnm104"),
    (("encoding104", "keyboard"), "orapriej104"),
    (("encoding104", "AA"), "encoding104"),
    (("mapping104", "key"), "wenzmlq104"),
    (("mapping104", "lemon"), "xebdvyk104"),
    (("mapping104", "a"), "mapping104"),
    (("mapping104", "zz"), "lzoohmf104"),
    (("mapping104", "AgentU"), "mgtcbhg104"),
    (("mapping104", "keyboard"), "wenqwnx104"),
    (("mapping104", "AA"), "mapping104"),
    (("record104", "key"), "biayvb104"),
    (("record104", "lemon"), "cioceo104"),
    (("record104", "a"), "record104"),
    (("record104", "zz"), "qdbnqc104"),
    (("record104", "AgentU"), "rkgbkx104"),
    (("record104", "keyboard"), "biapfd104"),
    (("record104", "AA"), "record104"),
    (("candle104", "key"), "melnpc104"),
    (("candle104", "lemon"), "nezryp104"),
    (("candle104", "a"), "candle104"),
    (("candle104", "zz"), "bzmckd104"),
    (("candle104", "AgentU"), "cgrqey104"),
    (("candle104", "keyboard"), "meleze104"),
    (("candle104", "AA"), "candle104"),
    (("thread104", "key"), "dlpoeb104"),
    (("thread104", "lemon"), "eldsno104"),
    (("thread104", "a"), "thread104"),
    (("thread104", "zz"), "sgqdzc104"),
    (("thread104", "AgentU"), "tnvrtx104"),
    (("thread104", "keyboard"), "dlpfod104"),
    (("thread104", "AA"), "thread104"),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 104: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 104: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "a"),
        "round 104: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 104: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 104: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 104: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", "AA"),
        "round 104: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "key"),
        "bssxh 104: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 104: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "a"),
        "round 104: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 104: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 104: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 104: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", "AA"),
        "round 104: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 104: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 104: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "a"),
        "round 104: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 104: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 104: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 104: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", "AA"),
        "round 104: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 104: the processor reads the record then stops", "key"),
        "bssxh 104: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 104: the processor reads the record then stops", "lemon"),
        "csgbq 104: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 104: the processor reads the record then stops", "a"),
        "round 104: the processor reads the record then stops",
    ),
    (
        ("round 104: the processor reads the record then stops", "zz"),
        "qntmc 104: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 104: the processor reads the record then stops", "AgentU"),
        "ruyaw 104: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 104: the processor reads the record then stops", "keyboard"),
        "bssor 104: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 104: the processor reads the record then stops", "AA"),
        "round 104: the processor reads the record then stops",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "key"),
        "bssxh 104: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "lemon"),
        "csgbq 104: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "a"),
        "round 104: a worker pulls the next task from the queue",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "zz"),
        "qntmc 104: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 104: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "keyboard"),
        "bssor 104: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 104: a worker pulls the next task from the queue", "AA"),
        "round 104: a worker pulls the next task from the queue",
    ),
    (
        ("round 104: signals travel through the network layer", "key"),
        "bssxh 104: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 104: signals travel through the network layer", "lemon"),
        "csgbq 104: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 104: signals travel through the network layer", "a"),
        "round 104: signals travel through the network layer",
    ),
    (
        ("round 104: signals travel through the network layer", "zz"),
        "qntmc 104: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 104: signals travel through the network layer", "AgentU"),
        "ruyaw 104: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 104: signals travel through the network layer", "keyboard"),
        "bssor 104: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 104: signals travel through the network layer", "AA"),
        "round 104: signals travel through the network layer",
    ),
    (
        ("round 104: the gateway routes each request by policy", "key"),
        "bssxh 104: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 104: the gateway routes each request by policy", "lemon"),
        "csgbq 104: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 104: the gateway routes each request by policy", "a"),
        "round 104: the gateway routes each request by policy",
    ),
    (
        ("round 104: the gateway routes each request by policy", "zz"),
        "qntmc 104: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 104: the gateway routes each request by policy", "AgentU"),
        "ruyaw 104: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 104: the gateway routes each request by policy", "keyboard"),
        "bssor 104: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 104: the gateway routes each request by policy", "AA"),
        "round 104: the gateway routes each request by policy",
    ),
    (("round 104: memory grows until the buffer is full", "key"), "bssxh 104: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 104: memory grows until the buffer is full", "lemon"), "csgbq 104: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 104: memory grows until the buffer is full", "a"), "round 104: memory grows until the buffer is full"),
    (("round 104: memory grows until the buffer is full", "zz"), "qntmc 104: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 104: memory grows until the buffer is full", "AgentU"),
        "ruyaw 104: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 104: memory grows until the buffer is full", "keyboard"),
        "bssor 104: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 104: memory grows until the buffer is full", "AA"), "round 104: memory grows until the buffer is full"),
    (("round 104: the cluster mirrors every packet twice", "key"), "bssxh 104: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 104: the cluster mirrors every packet twice", "lemon"),
        "csgbq 104: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 104: the cluster mirrors every packet twice", "a"), "round 104: the cluster mirrors every packet twice"),
    (("round 104: the cluster mirrors every packet twice", "zz"), "qntmc 104: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 104: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 104: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 104: the cluster mirrors every packet twice", "keyboard"),
        "bssor 104: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 104: the cluster mirrors every packet twice", "AA"), "round 104: the cluster mirrors every packet twice"),
    (
        ("round 104: ranking uses tokens learned from the corpus", "key"),
        "bssxh 104: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 104: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", "a"),
        "round 104: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 104: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 104: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 104: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", "AA"),
        "round 104: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 104: a long session ends when the candle dies", "key"),
        "bssxh 104: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 104: a long session ends when the candle dies", "lemon"),
        "csgbq 104: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 104: a long session ends when the candle dies", "a"),
        "round 104: a long session ends when the candle dies",
    ),
    (
        ("round 104: a long session ends when the candle dies", "zz"),
        "qntmc 104: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 104: a long session ends when the candle dies", "AgentU"),
        "ruyaw 104: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 104: a long session ends when the candle dies", "keyboard"),
        "bssor 104: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 104: a long session ends when the candle dies", "AA"),
        "round 104: a long session ends when the candle dies",
    ),
    (("round 104: encode the prompt then map the result", "key"), "bssxh 104: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 104: encode the prompt then map the result", "lemon"), "csgbq 104: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 104: encode the prompt then map the result", "a"), "round 104: encode the prompt then map the result"),
    (("round 104: encode the prompt then map the result", "zz"), "qntmc 104: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 104: encode the prompt then map the result", "AgentU"),
        "ruyaw 104: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 104: encode the prompt then map the result", "keyboard"),
        "bssor 104: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 104: encode the prompt then map the result", "AA"), "round 104: encode the prompt then map the result"),
    (("round 104: the kernel wakes the worker at dawn", "key"), "bssxh 104: rri iovlop ukocc xfo ambocb er neux"),
    (("round 104: the kernel wakes the worker at dawn", "lemon"), "csgbq 104: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 104: the kernel wakes the worker at dawn", "a"), "round 104: the kernel wakes the worker at dawn"),
    (("round 104: the kernel wakes the worker at dawn", "zz"), "qntmc 104: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 104: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 104: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 104: the kernel wakes the worker at dawn", "keyboard"), "bssor 104: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 104: the kernel wakes the worker at dawn", "AA"), "round 104: the kernel wakes the worker at dawn"),
    (("round 104: service latency drops after the patch", "key"), "bssxh 104: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 104: service latency drops after the patch", "lemon"), "csgbq 104: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 104: service latency drops after the patch", "a"), "round 104: service latency drops after the patch"),
    (("round 104: service latency drops after the patch", "zz"), "qntmc 104: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 104: service latency drops after the patch", "AgentU"),
        "ruyaw 104: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 104: service latency drops after the patch", "keyboard"),
        "bssor 104: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 104: service latency drops after the patch", "AA"), "round 104: service latency drops after the patch"),
    (
        ("round 104: the library caches every vector it sees", "key"),
        "bssxh 104: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 104: the library caches every vector it sees", "lemon"),
        "csgbq 104: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 104: the library caches every vector it sees", "a"), "round 104: the library caches every vector it sees"),
    (
        ("round 104: the library caches every vector it sees", "zz"),
        "qntmc 104: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 104: the library caches every vector it sees", "AgentU"),
        "ruyaw 104: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 104: the library caches every vector it sees", "keyboard"),
        "bssor 104: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 104: the library caches every vector it sees", "AA"),
        "round 104: the library caches every vector it sees",
    ),
    (("round 104: agents argue then the debate resolves", "key"), "bssxh 104: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 104: agents argue then the debate resolves", "lemon"), "csgbq 104: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 104: agents argue then the debate resolves", "a"), "round 104: agents argue then the debate resolves"),
    (("round 104: agents argue then the debate resolves", "zz"), "qntmc 104: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 104: agents argue then the debate resolves", "AgentU"),
        "ruyaw 104: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 104: agents argue then the debate resolves", "keyboard"),
        "bssor 104: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 104: agents argue then the debate resolves", "AA"), "round 104: agents argue then the debate resolves"),
    (("round 104: the filter keeps only strong matches", "key"), "bssxh 104: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 104: the filter keeps only strong matches", "lemon"), "csgbq 104: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 104: the filter keeps only strong matches", "a"), "round 104: the filter keeps only strong matches"),
    (("round 104: the filter keeps only strong matches", "zz"), "qntmc 104: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 104: the filter keeps only strong matches", "AgentU"), "ruyaw 104: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 104: the filter keeps only strong matches", "keyboard"),
        "bssor 104: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 104: the filter keeps only strong matches", "AA"), "round 104: the filter keeps only strong matches"),
    (("round 104: the model answers with a short reply", "key"), "bssxh 104: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 104: the model answers with a short reply", "lemon"), "csgbq 104: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 104: the model answers with a short reply", "a"), "round 104: the model answers with a short reply"),
    (("round 104: the model answers with a short reply", "zz"), "qntmc 104: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 104: the model answers with a short reply", "AgentU"), "ruyaw 104: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 104: the model answers with a short reply", "keyboard"),
        "bssor 104: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 104: the model answers with a short reply", "AA"), "round 104: the model answers with a short reply"),
    (
        ("round 104: the recorder stores the reasoning trace", "key"),
        "bssxh 104: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 104: the recorder stores the reasoning trace", "lemon"),
        "csgbq 104: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 104: the recorder stores the reasoning trace", "a"), "round 104: the recorder stores the reasoning trace"),
    (
        ("round 104: the recorder stores the reasoning trace", "zz"),
        "qntmc 104: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 104: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 104: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 104: the recorder stores the reasoning trace", "keyboard"),
        "bssor 104: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 104: the recorder stores the reasoning trace", "AA"),
        "round 104: the recorder stores the reasoning trace",
    ),
    (("round 104: the angel watches the processor run", "key"), "bssxh 104: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 104: the angel watches the processor run", "lemon"), "csgbq 104: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 104: the angel watches the processor run", "a"), "round 104: the angel watches the processor run"),
    (("round 104: the angel watches the processor run", "zz"), "qntmc 104: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 104: the angel watches the processor run", "AgentU"), "ruyaw 104: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 104: the angel watches the processor run", "keyboard"), "bssor 104: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 104: the angel watches the processor run", "AA"), "round 104: the angel watches the processor run"),
    (("round 104: angle of the vector decides the match", "key"), "bssxh 104: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 104: angle of the vector decides the match", "lemon"), "csgbq 104: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 104: angle of the vector decides the match", "a"), "round 104: angle of the vector decides the match"),
    (("round 104: angle of the vector decides the match", "zz"), "qntmc 104: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 104: angle of the vector decides the match", "AgentU"),
        "ruyaw 104: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 104: angle of the vector decides the match", "keyboard"),
        "bssor 104: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 104: angle of the vector decides the match", "AA"), "round 104: angle of the vector decides the match"),
    (
        ("round 104: the candle burns twice as long at night", "key"),
        "bssxh 104: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 104: the candle burns twice as long at night", "lemon"),
        "csgbq 104: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 104: the candle burns twice as long at night", "a"), "round 104: the candle burns twice as long at night"),
    (
        ("round 104: the candle burns twice as long at night", "zz"),
        "qntmc 104: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 104: the candle burns twice as long at night", "AgentU"),
        "ruyaw 104: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 104: the candle burns twice as long at night", "keyboard"),
        "bssor 104: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 104: the candle burns twice as long at night", "AA"),
        "round 104: the candle burns twice as long at night",
    ),
    (("round 104: a mirror of the universe in one line", "key"), "bssxh 104: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 104: a mirror of the universe in one line", "lemon"), "csgbq 104: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 104: a mirror of the universe in one line", "a"), "round 104: a mirror of the universe in one line"),
    (("round 104: a mirror of the universe in one line", "zz"), "qntmc 104: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 104: a mirror of the universe in one line", "AgentU"), "ruyaw 104: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 104: a mirror of the universe in one line", "keyboard"),
        "bssor 104: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 104: a mirror of the universe in one line", "AA"), "round 104: a mirror of the universe in one line"),
    (("round 104: the queue drains before the storm", "key"), "bssxh 104: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 104: the queue drains before the storm", "lemon"), "csgbq 104: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 104: the queue drains before the storm", "a"), "round 104: the queue drains before the storm"),
    (("round 104: the queue drains before the storm", "zz"), "qntmc 104: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 104: the queue drains before the storm", "AgentU"), "ruyaw 104: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 104: the queue drains before the storm", "keyboard"), "bssor 104: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 104: the queue drains before the storm", "AA"), "round 104: the queue drains before the storm"),
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
