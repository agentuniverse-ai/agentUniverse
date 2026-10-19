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
    (("kitten745", "key"), "umrdil745"),
    (("kitten745", "lemon"), "vmfhry745"),
    (("kitten745", "a"), "kitten745"),
    (("kitten745", "zz"), "jhssdm745"),
    (("kitten745", "AgentU"), "koxgxh745"),
    (("kitten745", "keyboard"), "umrusn745"),
    (("kitten745", "AA"), "kitten745"),
    (("sitting745", "key"), "cmrdmlq745"),
    (("sitting745", "lemon"), "dmfhvyk745"),
    (("sitting745", "a"), "sitting745"),
    (("sitting745", "zz"), "rhsshmf745"),
    (("sitting745", "AgentU"), "soxgbhg745"),
    (("sitting745", "keyboard"), "cmruwnx745"),
    (("sitting745", "AA"), "sitting745"),
    (("agent745", "key"), "kkcxx745"),
    (("agent745", "lemon"), "lkqbg745"),
    (("agent745", "a"), "agent745"),
    (("agent745", "zz"), "zfdms745"),
    (("agent745", "AgentU"), "amiam745"),
    (("agent745", "keyboard"), "kkcoh745"),
    (("agent745", "AA"), "agent745"),
    (("angle745", "key"), "krevi745"),
    (("angle745", "lemon"), "lrszr745"),
    (("angle745", "a"), "angle745"),
    (("angle745", "zz"), "zmfkd745"),
    (("angle745", "AgentU"), "atkyx745"),
    (("angle745", "keyboard"), "krems745"),
    (("angle745", "AA"), "angle745"),
    (("universe745", "key"), "ergfipci745"),
    (("universe745", "lemon"), "frujrcwq745"),
    (("universe745", "a"), "universe745"),
    (("universe745", "zz"), "tmhudqrd745"),
    (("universe745", "AgentU"), "utmixlsk745"),
    (("universe745", "keyboard"), "ergwsrjh745"),
    (("universe745", "AA"), "universe745"),
    (("memory745", "key"), "wikyvw745"),
    (("memory745", "lemon"), "xiycej745"),
    (("memory745", "a"), "memory745"),
    (("memory745", "zz"), "ldlnqx745"),
    (("memory745", "AgentU"), "mkqbks745"),
    (("memory745", "keyboard"), "wikpfy745"),
    (("memory745", "AA"), "memory745"),
    (("stream745", "key"), "cxpoek745"),
    (("stream745", "lemon"), "dxdsnx745"),
    (("stream745", "a"), "stream745"),
    (("stream745", "zz"), "rsqdzl745"),
    (("stream745", "AgentU"), "szvrtg745"),
    (("stream745", "keyboard"), "cxpfom745"),
    (("stream745", "AA"), "stream745"),
    (("context745", "key"), "msldivd745"),
    (("context745", "lemon"), "nszhrix745"),
    (("context745", "a"), "context745"),
    (("context745", "zz"), "bnmsdws745"),
    (("context745", "AgentU"), "curgxrt745"),
    (("context745", "keyboard"), "mslusxk745"),
    (("context745", "AA"), "context745"),
    (("knowledge745", "key"), "urmgpcnkc745"),
    (("knowledge745", "lemon"), "vrakyphss745"),
    (("knowledge745", "a"), "knowledge745"),
    (("knowledge745", "zz"), "jmnvkdcfd745"),
    (("knowledge745", "AgentU"), "ktsjeydmi745"),
    (("knowledge745", "keyboard"), "urmxzeujo745"),
    (("knowledge745", "AA"), "knowledge745"),
    (("vector745", "key"), "fiadsp745"),
    (("vector745", "lemon"), "giohbc745"),
    (("vector745", "a"), "vector745"),
    (("vector745", "zz"), "udbsnq745"),
    (("vector745", "AgentU"), "vkgghl745"),
    (("vector745", "keyboard"), "fiaucr745"),
    (("vector745", "AA"), "vector745"),
    (("processor745", "key"), "zvmmiqcsp745"),
    (("processor745", "lemon"), "avaqrdwaf745"),
    (("processor745", "a"), "processor745"),
    (("processor745", "zz"), "oqnbdrrnq745"),
    (("processor745", "AgentU"), "pxspxmsuv745"),
    (("processor745", "keyboard"), "zvmdssjrb745"),
    (("processor745", "AA"), "processor745"),
    (("reasoning745", "key"), "biycslsre745"),
    (("reasoning745", "lemon"), "cimgbymzu745"),
    (("reasoning745", "a"), "reasoning745"),
    (("reasoning745", "zz"), "qdzrnmhmf745"),
    (("reasoning745", "AgentU"), "rkefhhitk745"),
    (("reasoning745", "keyboard"), "biytcnzqq745"),
    (("reasoning745", "AA"), "reasoning745"),
    (("machine745", "key"), "wearmlo745"),
    (("machine745", "lemon"), "xeovvyi745"),
    (("machine745", "a"), "machine745"),
    (("machine745", "zz"), "lzbghmd745"),
    (("machine745", "AgentU"), "mggubhe745"),
    (("machine745", "keyboard"), "weaiwnv745"),
    (("machine745", "AA"), "machine745"),
    (("learning745", "key"), "viybrgxk745"),
    (("learning745", "lemon"), "wimfatrs745"),
    (("learning745", "a"), "learning745"),
    (("learning745", "zz"), "kdzqmhmf745"),
    (("learning745", "AgentU"), "lkeegcnm745"),
    (("learning745", "keyboard"), "viysbiej745"),
    (("learning745", "AA"), "learning745"),
    (("model745", "key"), "wsbop745"),
    (("model745", "lemon"), "xspsy745"),
    (("model745", "a"), "model745"),
    (("model745", "zz"), "lncdk745"),
    (("model745", "AgentU"), "muhre745"),
    (("model745", "keyboard"), "wsbfz745"),
    (("model745", "AA"), "model745"),
    (("token745", "key"), "dsior745"),
    (("token745", "lemon"), "eswsa745"),
    (("token745", "a"), "token745"),
    (("token745", "zz"), "snjdm745"),
    (("token745", "AgentU"), "tuorg745"),
    (("token745", "keyboard"), "dsifb745"),
    (("token745", "AA"), "token745"),
    (("prompt745", "key"), "zvmwtr745"),
    (("prompt745", "lemon"), "avaace745"),
    (("prompt745", "a"), "prompt745"),
    (("prompt745", "zz"), "oqnlos745"),
    (("prompt745", "AgentU"), "pxszin745"),
    (("prompt745", "keyboard"), "zvmndt745"),
    (("prompt745", "AA"), "prompt745"),
    (("session745", "key"), "ciqcmmx745"),
    (("session745", "lemon"), "diegvzr745"),
    (("session745", "a"), "session745"),
    (("session745", "zz"), "rdrrhnm745"),
    (("session745", "AgentU"), "skwfbin745"),
    (("session745", "keyboard"), "ciqtwoe745"),
    (("session745", "AA"), "session745"),
    (("library745", "key"), "vmzbepi745"),
    (("library745", "lemon"), "wmnfncc745"),
    (("library745", "a"), "library745"),
    (("library745", "zz"), "khaqzqx745"),
    (("library745", "AgentU"), "lofetly745"),
    (("library745", "keyboard"), "vmzsorp745"),
    (("library745", "AA"), "library745"),
    (("service745", "key"), "cipfmao745"),
    (("service745", "lemon"), "didjvni745"),
    (("service745", "a"), "service745"),
    (("service745", "zz"), "rdquhbd745"),
    (("service745", "AgentU"), "skvibwe745"),
    (("service745", "keyboard"), "cipwwcv745"),
    (("service745", "AA"), "service745"),
    (("gateway745", "key"), "qeroayi745"),
    (("gateway745", "lemon"), "refsjlc745"),
    (("gateway745", "a"), "gateway745"),
    (("gateway745", "zz"), "fzsdvzx745"),
    (("gateway745", "AgentU"), "ggxrpuy745"),
    (("gateway745", "keyboard"), "qerfkap745"),
    (("gateway745", "AA"), "gateway745"),
    (("storage745", "key"), "cxmbeeo745"),
    (("storage745", "lemon"), "dxafnri745"),
    (("storage745", "a"), "storage745"),
    (("storage745", "zz"), "rsnqzfd745"),
    (("storage745", "AgentU"), "szsetae745"),
    (("storage745", "keyboard"), "cxmsogv745"),
    (("storage745", "AA"), "storage745"),
    (("network745", "key"), "xirgspu745"),
    (("network745", "lemon"), "yifkbco745"),
    (("network745", "a"), "network745"),
    (("network745", "zz"), "mdsvnqj745"),
    (("network745", "AgentU"), "nkxjhlk745"),
    (("network745", "keyboard"), "xirxcrb745"),
    (("network745", "AA"), "network745"),
    (("latency745", "key"), "verorai745"),
    (("latency745", "lemon"), "wefsanc745"),
    (("latency745", "a"), "latency745"),
    (("latency745", "zz"), "kzsdmbx745"),
    (("latency745", "AgentU"), "lgxrgwy745"),
    (("latency745", "keyboard"), "verfbcp745"),
    (("latency745", "AA"), "latency745"),
    (("buffer745", "key"), "lydpip745"),
    (("buffer745", "lemon"), "myrtrc745"),
    (("buffer745", "a"), "buffer745"),
    (("buffer745", "zz"), "ateedq745"),
    (("buffer745", "AgentU"), "bajsxl745"),
    (("buffer745", "keyboard"), "lydgsr745"),
    (("buffer745", "AA"), "buffer745"),
    (("queue745", "key"), "aycei745"),
    (("queue745", "lemon"), "byqir745"),
    (("queue745", "a"), "queue745"),
    (("queue745", "zz"), "ptdtd745"),
    (("queue745", "AgentU"), "qaihx745"),
    (("queue745", "keyboard"), "aycvs745"),
    (("queue745", "AA"), "queue745"),
    (("worker745", "key"), "gspuip745"),
    (("worker745", "lemon"), "hsdyrc745"),
    (("worker745", "a"), "worker745"),
    (("worker745", "zz"), "vnqjdq745"),
    (("worker745", "AgentU"), "wuvxxl745"),
    (("worker745", "keyboard"), "gsplsr745"),
    (("worker745", "AA"), "worker745"),
    (("kernel745", "key"), "uipxij745"),
    (("kernel745", "lemon"), "vidbrw745"),
    (("kernel745", "a"), "kernel745"),
    (("kernel745", "zz"), "jdqmdk745"),
    (("kernel745", "AgentU"), "kkvaxf745"),
    (("kernel745", "keyboard"), "uiposl745"),
    (("kernel745", "AA"), "kernel745"),
    (("signal745", "key"), "cmexej745"),
    (("signal745", "lemon"), "dmsbnw745"),
    (("signal745", "a"), "signal745"),
    (("signal745", "zz"), "rhfmzk745"),
    (("signal745", "AgentU"), "sokatf745"),
    (("signal745", "keyboard"), "cmeool745"),
    (("signal745", "AA"), "signal745"),
    (("packet745", "key"), "zeauir745"),
    (("packet745", "lemon"), "aeoyre745"),
    (("packet745", "a"), "packet745"),
    (("packet745", "zz"), "ozbjds745"),
    (("packet745", "AgentU"), "pggxxn745"),
    (("packet745", "keyboard"), "zealst745"),
    (("packet745", "AA"), "packet745"),
    (("router745", "key"), "bssdip745"),
    (("router745", "lemon"), "csghrc745"),
    (("router745", "a"), "router745"),
    (("router745", "zz"), "qntsdq745"),
    (("router745", "AgentU"), "ruygxl745"),
    (("router745", "keyboard"), "bssusr745"),
    (("router745", "AA"), "router745"),
    (("cluster745", "key"), "mpscxcb745"),
    (("cluster745", "lemon"), "npgggpv745"),
    (("cluster745", "a"), "cluster745"),
    (("cluster745", "zz"), "bktrsdq745"),
    (("cluster745", "AgentU"), "cryfmyr745"),
    (("cluster745", "keyboard"), "mpsthei745"),
    (("cluster745", "AA"), "cluster745"),
    (("mirror745", "key"), "wmpbsp745"),
    (("mirror745", "lemon"), "xmdfbc745"),
    (("mirror745", "a"), "mirror745"),
    (("mirror745", "zz"), "lhqqnq745"),
    (("mirror745", "AgentU"), "movehl745"),
    (("mirror745", "keyboard"), "wmpscr745"),
    (("mirror745", "AA"), "mirror745"),
    (("filter745", "key"), "pmjdip745"),
    (("filter745", "lemon"), "qmxhrc745"),
    (("filter745", "a"), "filter745"),
    (("filter745", "zz"), "ehksdq745"),
    (("filter745", "AgentU"), "fopgxl745"),
    (("filter745", "keyboard"), "pmjusr745"),
    (("filter745", "AA"), "filter745"),
    (("ranking745", "key"), "belumlq745"),
    (("ranking745", "lemon"), "cezyvyk745"),
    (("ranking745", "a"), "ranking745"),
    (("ranking745", "zz"), "qzmjhmf745"),
    (("ranking745", "AgentU"), "rgrxbhg745"),
    (("ranking745", "keyboard"), "bellwnx745"),
    (("ranking745", "AA"), "ranking745"),
    (("encoding745", "key"), "orayhgxk745"),
    (("encoding745", "lemon"), "procqtrs745"),
    (("encoding745", "a"), "encoding745"),
    (("encoding745", "zz"), "dmbnchmf745"),
    (("encoding745", "AgentU"), "etgbwcnm745"),
    (("encoding745", "keyboard"), "orapriej745"),
    (("encoding745", "AA"), "encoding745"),
    (("mapping745", "key"), "wenzmlq745"),
    (("mapping745", "lemon"), "xebdvyk745"),
    (("mapping745", "a"), "mapping745"),
    (("mapping745", "zz"), "lzoohmf745"),
    (("mapping745", "AgentU"), "mgtcbhg745"),
    (("mapping745", "keyboard"), "wenqwnx745"),
    (("mapping745", "AA"), "mapping745"),
    (("record745", "key"), "biayvb745"),
    (("record745", "lemon"), "cioceo745"),
    (("record745", "a"), "record745"),
    (("record745", "zz"), "qdbnqc745"),
    (("record745", "AgentU"), "rkgbkx745"),
    (("record745", "keyboard"), "biapfd745"),
    (("record745", "AA"), "record745"),
    (("candle745", "key"), "melnpc745"),
    (("candle745", "lemon"), "nezryp745"),
    (("candle745", "a"), "candle745"),
    (("candle745", "zz"), "bzmckd745"),
    (("candle745", "AgentU"), "cgrqey745"),
    (("candle745", "keyboard"), "meleze745"),
    (("candle745", "AA"), "candle745"),
    (("thread745", "key"), "dlpoeb745"),
    (("thread745", "lemon"), "eldsno745"),
    (("thread745", "a"), "thread745"),
    (("thread745", "zz"), "sgqdzc745"),
    (("thread745", "AgentU"), "tnvrtx745"),
    (("thread745", "keyboard"), "dlpfod745"),
    (("thread745", "AA"), "thread745"),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 745: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 745: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "a"),
        "round 745: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 745: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 745: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 745: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", "AA"),
        "round 745: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "key"),
        "bssxh 745: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 745: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "a"),
        "round 745: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 745: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 745: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 745: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", "AA"),
        "round 745: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 745: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 745: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "a"),
        "round 745: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 745: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 745: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 745: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", "AA"),
        "round 745: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 745: the processor reads the record then stops", "key"),
        "bssxh 745: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 745: the processor reads the record then stops", "lemon"),
        "csgbq 745: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 745: the processor reads the record then stops", "a"),
        "round 745: the processor reads the record then stops",
    ),
    (
        ("round 745: the processor reads the record then stops", "zz"),
        "qntmc 745: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 745: the processor reads the record then stops", "AgentU"),
        "ruyaw 745: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 745: the processor reads the record then stops", "keyboard"),
        "bssor 745: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 745: the processor reads the record then stops", "AA"),
        "round 745: the processor reads the record then stops",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "key"),
        "bssxh 745: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "lemon"),
        "csgbq 745: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "a"),
        "round 745: a worker pulls the next task from the queue",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "zz"),
        "qntmc 745: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 745: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "keyboard"),
        "bssor 745: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 745: a worker pulls the next task from the queue", "AA"),
        "round 745: a worker pulls the next task from the queue",
    ),
    (
        ("round 745: signals travel through the network layer", "key"),
        "bssxh 745: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 745: signals travel through the network layer", "lemon"),
        "csgbq 745: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 745: signals travel through the network layer", "a"),
        "round 745: signals travel through the network layer",
    ),
    (
        ("round 745: signals travel through the network layer", "zz"),
        "qntmc 745: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 745: signals travel through the network layer", "AgentU"),
        "ruyaw 745: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 745: signals travel through the network layer", "keyboard"),
        "bssor 745: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 745: signals travel through the network layer", "AA"),
        "round 745: signals travel through the network layer",
    ),
    (
        ("round 745: the gateway routes each request by policy", "key"),
        "bssxh 745: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 745: the gateway routes each request by policy", "lemon"),
        "csgbq 745: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 745: the gateway routes each request by policy", "a"),
        "round 745: the gateway routes each request by policy",
    ),
    (
        ("round 745: the gateway routes each request by policy", "zz"),
        "qntmc 745: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 745: the gateway routes each request by policy", "AgentU"),
        "ruyaw 745: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 745: the gateway routes each request by policy", "keyboard"),
        "bssor 745: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 745: the gateway routes each request by policy", "AA"),
        "round 745: the gateway routes each request by policy",
    ),
    (("round 745: memory grows until the buffer is full", "key"), "bssxh 745: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 745: memory grows until the buffer is full", "lemon"), "csgbq 745: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 745: memory grows until the buffer is full", "a"), "round 745: memory grows until the buffer is full"),
    (("round 745: memory grows until the buffer is full", "zz"), "qntmc 745: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 745: memory grows until the buffer is full", "AgentU"),
        "ruyaw 745: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 745: memory grows until the buffer is full", "keyboard"),
        "bssor 745: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 745: memory grows until the buffer is full", "AA"), "round 745: memory grows until the buffer is full"),
    (("round 745: the cluster mirrors every packet twice", "key"), "bssxh 745: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 745: the cluster mirrors every packet twice", "lemon"),
        "csgbq 745: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 745: the cluster mirrors every packet twice", "a"), "round 745: the cluster mirrors every packet twice"),
    (("round 745: the cluster mirrors every packet twice", "zz"), "qntmc 745: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 745: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 745: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 745: the cluster mirrors every packet twice", "keyboard"),
        "bssor 745: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 745: the cluster mirrors every packet twice", "AA"), "round 745: the cluster mirrors every packet twice"),
    (
        ("round 745: ranking uses tokens learned from the corpus", "key"),
        "bssxh 745: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 745: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", "a"),
        "round 745: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 745: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 745: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 745: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", "AA"),
        "round 745: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 745: a long session ends when the candle dies", "key"),
        "bssxh 745: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 745: a long session ends when the candle dies", "lemon"),
        "csgbq 745: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 745: a long session ends when the candle dies", "a"),
        "round 745: a long session ends when the candle dies",
    ),
    (
        ("round 745: a long session ends when the candle dies", "zz"),
        "qntmc 745: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 745: a long session ends when the candle dies", "AgentU"),
        "ruyaw 745: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 745: a long session ends when the candle dies", "keyboard"),
        "bssor 745: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 745: a long session ends when the candle dies", "AA"),
        "round 745: a long session ends when the candle dies",
    ),
    (("round 745: encode the prompt then map the result", "key"), "bssxh 745: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 745: encode the prompt then map the result", "lemon"), "csgbq 745: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 745: encode the prompt then map the result", "a"), "round 745: encode the prompt then map the result"),
    (("round 745: encode the prompt then map the result", "zz"), "qntmc 745: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 745: encode the prompt then map the result", "AgentU"),
        "ruyaw 745: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 745: encode the prompt then map the result", "keyboard"),
        "bssor 745: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 745: encode the prompt then map the result", "AA"), "round 745: encode the prompt then map the result"),
    (("round 745: the kernel wakes the worker at dawn", "key"), "bssxh 745: rri iovlop ukocc xfo ambocb er neux"),
    (("round 745: the kernel wakes the worker at dawn", "lemon"), "csgbq 745: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 745: the kernel wakes the worker at dawn", "a"), "round 745: the kernel wakes the worker at dawn"),
    (("round 745: the kernel wakes the worker at dawn", "zz"), "qntmc 745: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 745: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 745: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 745: the kernel wakes the worker at dawn", "keyboard"), "bssor 745: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 745: the kernel wakes the worker at dawn", "AA"), "round 745: the kernel wakes the worker at dawn"),
    (("round 745: service latency drops after the patch", "key"), "bssxh 745: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 745: service latency drops after the patch", "lemon"), "csgbq 745: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 745: service latency drops after the patch", "a"), "round 745: service latency drops after the patch"),
    (("round 745: service latency drops after the patch", "zz"), "qntmc 745: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 745: service latency drops after the patch", "AgentU"),
        "ruyaw 745: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 745: service latency drops after the patch", "keyboard"),
        "bssor 745: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 745: service latency drops after the patch", "AA"), "round 745: service latency drops after the patch"),
    (
        ("round 745: the library caches every vector it sees", "key"),
        "bssxh 745: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 745: the library caches every vector it sees", "lemon"),
        "csgbq 745: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 745: the library caches every vector it sees", "a"), "round 745: the library caches every vector it sees"),
    (
        ("round 745: the library caches every vector it sees", "zz"),
        "qntmc 745: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 745: the library caches every vector it sees", "AgentU"),
        "ruyaw 745: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 745: the library caches every vector it sees", "keyboard"),
        "bssor 745: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 745: the library caches every vector it sees", "AA"),
        "round 745: the library caches every vector it sees",
    ),
    (("round 745: agents argue then the debate resolves", "key"), "bssxh 745: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 745: agents argue then the debate resolves", "lemon"), "csgbq 745: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 745: agents argue then the debate resolves", "a"), "round 745: agents argue then the debate resolves"),
    (("round 745: agents argue then the debate resolves", "zz"), "qntmc 745: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 745: agents argue then the debate resolves", "AgentU"),
        "ruyaw 745: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 745: agents argue then the debate resolves", "keyboard"),
        "bssor 745: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 745: agents argue then the debate resolves", "AA"), "round 745: agents argue then the debate resolves"),
    (("round 745: the filter keeps only strong matches", "key"), "bssxh 745: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 745: the filter keeps only strong matches", "lemon"), "csgbq 745: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 745: the filter keeps only strong matches", "a"), "round 745: the filter keeps only strong matches"),
    (("round 745: the filter keeps only strong matches", "zz"), "qntmc 745: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 745: the filter keeps only strong matches", "AgentU"), "ruyaw 745: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 745: the filter keeps only strong matches", "keyboard"),
        "bssor 745: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 745: the filter keeps only strong matches", "AA"), "round 745: the filter keeps only strong matches"),
    (("round 745: the model answers with a short reply", "key"), "bssxh 745: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 745: the model answers with a short reply", "lemon"), "csgbq 745: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 745: the model answers with a short reply", "a"), "round 745: the model answers with a short reply"),
    (("round 745: the model answers with a short reply", "zz"), "qntmc 745: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 745: the model answers with a short reply", "AgentU"), "ruyaw 745: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 745: the model answers with a short reply", "keyboard"),
        "bssor 745: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 745: the model answers with a short reply", "AA"), "round 745: the model answers with a short reply"),
    (
        ("round 745: the recorder stores the reasoning trace", "key"),
        "bssxh 745: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 745: the recorder stores the reasoning trace", "lemon"),
        "csgbq 745: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 745: the recorder stores the reasoning trace", "a"), "round 745: the recorder stores the reasoning trace"),
    (
        ("round 745: the recorder stores the reasoning trace", "zz"),
        "qntmc 745: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 745: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 745: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 745: the recorder stores the reasoning trace", "keyboard"),
        "bssor 745: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 745: the recorder stores the reasoning trace", "AA"),
        "round 745: the recorder stores the reasoning trace",
    ),
    (("round 745: the angel watches the processor run", "key"), "bssxh 745: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 745: the angel watches the processor run", "lemon"), "csgbq 745: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 745: the angel watches the processor run", "a"), "round 745: the angel watches the processor run"),
    (("round 745: the angel watches the processor run", "zz"), "qntmc 745: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 745: the angel watches the processor run", "AgentU"), "ruyaw 745: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 745: the angel watches the processor run", "keyboard"), "bssor 745: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 745: the angel watches the processor run", "AA"), "round 745: the angel watches the processor run"),
    (("round 745: angle of the vector decides the match", "key"), "bssxh 745: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 745: angle of the vector decides the match", "lemon"), "csgbq 745: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 745: angle of the vector decides the match", "a"), "round 745: angle of the vector decides the match"),
    (("round 745: angle of the vector decides the match", "zz"), "qntmc 745: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 745: angle of the vector decides the match", "AgentU"),
        "ruyaw 745: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 745: angle of the vector decides the match", "keyboard"),
        "bssor 745: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 745: angle of the vector decides the match", "AA"), "round 745: angle of the vector decides the match"),
    (
        ("round 745: the candle burns twice as long at night", "key"),
        "bssxh 745: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 745: the candle burns twice as long at night", "lemon"),
        "csgbq 745: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 745: the candle burns twice as long at night", "a"), "round 745: the candle burns twice as long at night"),
    (
        ("round 745: the candle burns twice as long at night", "zz"),
        "qntmc 745: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 745: the candle burns twice as long at night", "AgentU"),
        "ruyaw 745: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 745: the candle burns twice as long at night", "keyboard"),
        "bssor 745: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 745: the candle burns twice as long at night", "AA"),
        "round 745: the candle burns twice as long at night",
    ),
    (("round 745: a mirror of the universe in one line", "key"), "bssxh 745: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 745: a mirror of the universe in one line", "lemon"), "csgbq 745: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 745: a mirror of the universe in one line", "a"), "round 745: a mirror of the universe in one line"),
    (("round 745: a mirror of the universe in one line", "zz"), "qntmc 745: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 745: a mirror of the universe in one line", "AgentU"), "ruyaw 745: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 745: a mirror of the universe in one line", "keyboard"),
        "bssor 745: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 745: a mirror of the universe in one line", "AA"), "round 745: a mirror of the universe in one line"),
    (("round 745: the queue drains before the storm", "key"), "bssxh 745: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 745: the queue drains before the storm", "lemon"), "csgbq 745: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 745: the queue drains before the storm", "a"), "round 745: the queue drains before the storm"),
    (("round 745: the queue drains before the storm", "zz"), "qntmc 745: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 745: the queue drains before the storm", "AgentU"), "ruyaw 745: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 745: the queue drains before the storm", "keyboard"), "bssor 745: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 745: the queue drains before the storm", "AA"), "round 745: the queue drains before the storm"),
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
