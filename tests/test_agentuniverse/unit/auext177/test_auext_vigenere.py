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
    (("kitten177", "key"), "umrdil177"),
    (("kitten177", "lemon"), "vmfhry177"),
    (("kitten177", "a"), "kitten177"),
    (("kitten177", "zz"), "jhssdm177"),
    (("kitten177", "AgentU"), "koxgxh177"),
    (("kitten177", "keyboard"), "umrusn177"),
    (("kitten177", "AA"), "kitten177"),
    (("sitting177", "key"), "cmrdmlq177"),
    (("sitting177", "lemon"), "dmfhvyk177"),
    (("sitting177", "a"), "sitting177"),
    (("sitting177", "zz"), "rhsshmf177"),
    (("sitting177", "AgentU"), "soxgbhg177"),
    (("sitting177", "keyboard"), "cmruwnx177"),
    (("sitting177", "AA"), "sitting177"),
    (("agent177", "key"), "kkcxx177"),
    (("agent177", "lemon"), "lkqbg177"),
    (("agent177", "a"), "agent177"),
    (("agent177", "zz"), "zfdms177"),
    (("agent177", "AgentU"), "amiam177"),
    (("agent177", "keyboard"), "kkcoh177"),
    (("agent177", "AA"), "agent177"),
    (("angle177", "key"), "krevi177"),
    (("angle177", "lemon"), "lrszr177"),
    (("angle177", "a"), "angle177"),
    (("angle177", "zz"), "zmfkd177"),
    (("angle177", "AgentU"), "atkyx177"),
    (("angle177", "keyboard"), "krems177"),
    (("angle177", "AA"), "angle177"),
    (("universe177", "key"), "ergfipci177"),
    (("universe177", "lemon"), "frujrcwq177"),
    (("universe177", "a"), "universe177"),
    (("universe177", "zz"), "tmhudqrd177"),
    (("universe177", "AgentU"), "utmixlsk177"),
    (("universe177", "keyboard"), "ergwsrjh177"),
    (("universe177", "AA"), "universe177"),
    (("memory177", "key"), "wikyvw177"),
    (("memory177", "lemon"), "xiycej177"),
    (("memory177", "a"), "memory177"),
    (("memory177", "zz"), "ldlnqx177"),
    (("memory177", "AgentU"), "mkqbks177"),
    (("memory177", "keyboard"), "wikpfy177"),
    (("memory177", "AA"), "memory177"),
    (("stream177", "key"), "cxpoek177"),
    (("stream177", "lemon"), "dxdsnx177"),
    (("stream177", "a"), "stream177"),
    (("stream177", "zz"), "rsqdzl177"),
    (("stream177", "AgentU"), "szvrtg177"),
    (("stream177", "keyboard"), "cxpfom177"),
    (("stream177", "AA"), "stream177"),
    (("context177", "key"), "msldivd177"),
    (("context177", "lemon"), "nszhrix177"),
    (("context177", "a"), "context177"),
    (("context177", "zz"), "bnmsdws177"),
    (("context177", "AgentU"), "curgxrt177"),
    (("context177", "keyboard"), "mslusxk177"),
    (("context177", "AA"), "context177"),
    (("knowledge177", "key"), "urmgpcnkc177"),
    (("knowledge177", "lemon"), "vrakyphss177"),
    (("knowledge177", "a"), "knowledge177"),
    (("knowledge177", "zz"), "jmnvkdcfd177"),
    (("knowledge177", "AgentU"), "ktsjeydmi177"),
    (("knowledge177", "keyboard"), "urmxzeujo177"),
    (("knowledge177", "AA"), "knowledge177"),
    (("vector177", "key"), "fiadsp177"),
    (("vector177", "lemon"), "giohbc177"),
    (("vector177", "a"), "vector177"),
    (("vector177", "zz"), "udbsnq177"),
    (("vector177", "AgentU"), "vkgghl177"),
    (("vector177", "keyboard"), "fiaucr177"),
    (("vector177", "AA"), "vector177"),
    (("processor177", "key"), "zvmmiqcsp177"),
    (("processor177", "lemon"), "avaqrdwaf177"),
    (("processor177", "a"), "processor177"),
    (("processor177", "zz"), "oqnbdrrnq177"),
    (("processor177", "AgentU"), "pxspxmsuv177"),
    (("processor177", "keyboard"), "zvmdssjrb177"),
    (("processor177", "AA"), "processor177"),
    (("reasoning177", "key"), "biycslsre177"),
    (("reasoning177", "lemon"), "cimgbymzu177"),
    (("reasoning177", "a"), "reasoning177"),
    (("reasoning177", "zz"), "qdzrnmhmf177"),
    (("reasoning177", "AgentU"), "rkefhhitk177"),
    (("reasoning177", "keyboard"), "biytcnzqq177"),
    (("reasoning177", "AA"), "reasoning177"),
    (("machine177", "key"), "wearmlo177"),
    (("machine177", "lemon"), "xeovvyi177"),
    (("machine177", "a"), "machine177"),
    (("machine177", "zz"), "lzbghmd177"),
    (("machine177", "AgentU"), "mggubhe177"),
    (("machine177", "keyboard"), "weaiwnv177"),
    (("machine177", "AA"), "machine177"),
    (("learning177", "key"), "viybrgxk177"),
    (("learning177", "lemon"), "wimfatrs177"),
    (("learning177", "a"), "learning177"),
    (("learning177", "zz"), "kdzqmhmf177"),
    (("learning177", "AgentU"), "lkeegcnm177"),
    (("learning177", "keyboard"), "viysbiej177"),
    (("learning177", "AA"), "learning177"),
    (("model177", "key"), "wsbop177"),
    (("model177", "lemon"), "xspsy177"),
    (("model177", "a"), "model177"),
    (("model177", "zz"), "lncdk177"),
    (("model177", "AgentU"), "muhre177"),
    (("model177", "keyboard"), "wsbfz177"),
    (("model177", "AA"), "model177"),
    (("token177", "key"), "dsior177"),
    (("token177", "lemon"), "eswsa177"),
    (("token177", "a"), "token177"),
    (("token177", "zz"), "snjdm177"),
    (("token177", "AgentU"), "tuorg177"),
    (("token177", "keyboard"), "dsifb177"),
    (("token177", "AA"), "token177"),
    (("prompt177", "key"), "zvmwtr177"),
    (("prompt177", "lemon"), "avaace177"),
    (("prompt177", "a"), "prompt177"),
    (("prompt177", "zz"), "oqnlos177"),
    (("prompt177", "AgentU"), "pxszin177"),
    (("prompt177", "keyboard"), "zvmndt177"),
    (("prompt177", "AA"), "prompt177"),
    (("session177", "key"), "ciqcmmx177"),
    (("session177", "lemon"), "diegvzr177"),
    (("session177", "a"), "session177"),
    (("session177", "zz"), "rdrrhnm177"),
    (("session177", "AgentU"), "skwfbin177"),
    (("session177", "keyboard"), "ciqtwoe177"),
    (("session177", "AA"), "session177"),
    (("library177", "key"), "vmzbepi177"),
    (("library177", "lemon"), "wmnfncc177"),
    (("library177", "a"), "library177"),
    (("library177", "zz"), "khaqzqx177"),
    (("library177", "AgentU"), "lofetly177"),
    (("library177", "keyboard"), "vmzsorp177"),
    (("library177", "AA"), "library177"),
    (("service177", "key"), "cipfmao177"),
    (("service177", "lemon"), "didjvni177"),
    (("service177", "a"), "service177"),
    (("service177", "zz"), "rdquhbd177"),
    (("service177", "AgentU"), "skvibwe177"),
    (("service177", "keyboard"), "cipwwcv177"),
    (("service177", "AA"), "service177"),
    (("gateway177", "key"), "qeroayi177"),
    (("gateway177", "lemon"), "refsjlc177"),
    (("gateway177", "a"), "gateway177"),
    (("gateway177", "zz"), "fzsdvzx177"),
    (("gateway177", "AgentU"), "ggxrpuy177"),
    (("gateway177", "keyboard"), "qerfkap177"),
    (("gateway177", "AA"), "gateway177"),
    (("storage177", "key"), "cxmbeeo177"),
    (("storage177", "lemon"), "dxafnri177"),
    (("storage177", "a"), "storage177"),
    (("storage177", "zz"), "rsnqzfd177"),
    (("storage177", "AgentU"), "szsetae177"),
    (("storage177", "keyboard"), "cxmsogv177"),
    (("storage177", "AA"), "storage177"),
    (("network177", "key"), "xirgspu177"),
    (("network177", "lemon"), "yifkbco177"),
    (("network177", "a"), "network177"),
    (("network177", "zz"), "mdsvnqj177"),
    (("network177", "AgentU"), "nkxjhlk177"),
    (("network177", "keyboard"), "xirxcrb177"),
    (("network177", "AA"), "network177"),
    (("latency177", "key"), "verorai177"),
    (("latency177", "lemon"), "wefsanc177"),
    (("latency177", "a"), "latency177"),
    (("latency177", "zz"), "kzsdmbx177"),
    (("latency177", "AgentU"), "lgxrgwy177"),
    (("latency177", "keyboard"), "verfbcp177"),
    (("latency177", "AA"), "latency177"),
    (("buffer177", "key"), "lydpip177"),
    (("buffer177", "lemon"), "myrtrc177"),
    (("buffer177", "a"), "buffer177"),
    (("buffer177", "zz"), "ateedq177"),
    (("buffer177", "AgentU"), "bajsxl177"),
    (("buffer177", "keyboard"), "lydgsr177"),
    (("buffer177", "AA"), "buffer177"),
    (("queue177", "key"), "aycei177"),
    (("queue177", "lemon"), "byqir177"),
    (("queue177", "a"), "queue177"),
    (("queue177", "zz"), "ptdtd177"),
    (("queue177", "AgentU"), "qaihx177"),
    (("queue177", "keyboard"), "aycvs177"),
    (("queue177", "AA"), "queue177"),
    (("worker177", "key"), "gspuip177"),
    (("worker177", "lemon"), "hsdyrc177"),
    (("worker177", "a"), "worker177"),
    (("worker177", "zz"), "vnqjdq177"),
    (("worker177", "AgentU"), "wuvxxl177"),
    (("worker177", "keyboard"), "gsplsr177"),
    (("worker177", "AA"), "worker177"),
    (("kernel177", "key"), "uipxij177"),
    (("kernel177", "lemon"), "vidbrw177"),
    (("kernel177", "a"), "kernel177"),
    (("kernel177", "zz"), "jdqmdk177"),
    (("kernel177", "AgentU"), "kkvaxf177"),
    (("kernel177", "keyboard"), "uiposl177"),
    (("kernel177", "AA"), "kernel177"),
    (("signal177", "key"), "cmexej177"),
    (("signal177", "lemon"), "dmsbnw177"),
    (("signal177", "a"), "signal177"),
    (("signal177", "zz"), "rhfmzk177"),
    (("signal177", "AgentU"), "sokatf177"),
    (("signal177", "keyboard"), "cmeool177"),
    (("signal177", "AA"), "signal177"),
    (("packet177", "key"), "zeauir177"),
    (("packet177", "lemon"), "aeoyre177"),
    (("packet177", "a"), "packet177"),
    (("packet177", "zz"), "ozbjds177"),
    (("packet177", "AgentU"), "pggxxn177"),
    (("packet177", "keyboard"), "zealst177"),
    (("packet177", "AA"), "packet177"),
    (("router177", "key"), "bssdip177"),
    (("router177", "lemon"), "csghrc177"),
    (("router177", "a"), "router177"),
    (("router177", "zz"), "qntsdq177"),
    (("router177", "AgentU"), "ruygxl177"),
    (("router177", "keyboard"), "bssusr177"),
    (("router177", "AA"), "router177"),
    (("cluster177", "key"), "mpscxcb177"),
    (("cluster177", "lemon"), "npgggpv177"),
    (("cluster177", "a"), "cluster177"),
    (("cluster177", "zz"), "bktrsdq177"),
    (("cluster177", "AgentU"), "cryfmyr177"),
    (("cluster177", "keyboard"), "mpsthei177"),
    (("cluster177", "AA"), "cluster177"),
    (("mirror177", "key"), "wmpbsp177"),
    (("mirror177", "lemon"), "xmdfbc177"),
    (("mirror177", "a"), "mirror177"),
    (("mirror177", "zz"), "lhqqnq177"),
    (("mirror177", "AgentU"), "movehl177"),
    (("mirror177", "keyboard"), "wmpscr177"),
    (("mirror177", "AA"), "mirror177"),
    (("filter177", "key"), "pmjdip177"),
    (("filter177", "lemon"), "qmxhrc177"),
    (("filter177", "a"), "filter177"),
    (("filter177", "zz"), "ehksdq177"),
    (("filter177", "AgentU"), "fopgxl177"),
    (("filter177", "keyboard"), "pmjusr177"),
    (("filter177", "AA"), "filter177"),
    (("ranking177", "key"), "belumlq177"),
    (("ranking177", "lemon"), "cezyvyk177"),
    (("ranking177", "a"), "ranking177"),
    (("ranking177", "zz"), "qzmjhmf177"),
    (("ranking177", "AgentU"), "rgrxbhg177"),
    (("ranking177", "keyboard"), "bellwnx177"),
    (("ranking177", "AA"), "ranking177"),
    (("encoding177", "key"), "orayhgxk177"),
    (("encoding177", "lemon"), "procqtrs177"),
    (("encoding177", "a"), "encoding177"),
    (("encoding177", "zz"), "dmbnchmf177"),
    (("encoding177", "AgentU"), "etgbwcnm177"),
    (("encoding177", "keyboard"), "orapriej177"),
    (("encoding177", "AA"), "encoding177"),
    (("mapping177", "key"), "wenzmlq177"),
    (("mapping177", "lemon"), "xebdvyk177"),
    (("mapping177", "a"), "mapping177"),
    (("mapping177", "zz"), "lzoohmf177"),
    (("mapping177", "AgentU"), "mgtcbhg177"),
    (("mapping177", "keyboard"), "wenqwnx177"),
    (("mapping177", "AA"), "mapping177"),
    (("record177", "key"), "biayvb177"),
    (("record177", "lemon"), "cioceo177"),
    (("record177", "a"), "record177"),
    (("record177", "zz"), "qdbnqc177"),
    (("record177", "AgentU"), "rkgbkx177"),
    (("record177", "keyboard"), "biapfd177"),
    (("record177", "AA"), "record177"),
    (("candle177", "key"), "melnpc177"),
    (("candle177", "lemon"), "nezryp177"),
    (("candle177", "a"), "candle177"),
    (("candle177", "zz"), "bzmckd177"),
    (("candle177", "AgentU"), "cgrqey177"),
    (("candle177", "keyboard"), "meleze177"),
    (("candle177", "AA"), "candle177"),
    (("thread177", "key"), "dlpoeb177"),
    (("thread177", "lemon"), "eldsno177"),
    (("thread177", "a"), "thread177"),
    (("thread177", "zz"), "sgqdzc177"),
    (("thread177", "AgentU"), "tnvrtx177"),
    (("thread177", "keyboard"), "dlpfod177"),
    (("thread177", "AA"), "thread177"),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 177: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 177: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "a"),
        "round 177: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 177: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 177: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 177: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", "AA"),
        "round 177: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "key"),
        "bssxh 177: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 177: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "a"),
        "round 177: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 177: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 177: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 177: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", "AA"),
        "round 177: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 177: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 177: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "a"),
        "round 177: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 177: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 177: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 177: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", "AA"),
        "round 177: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 177: the processor reads the record then stops", "key"),
        "bssxh 177: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 177: the processor reads the record then stops", "lemon"),
        "csgbq 177: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 177: the processor reads the record then stops", "a"),
        "round 177: the processor reads the record then stops",
    ),
    (
        ("round 177: the processor reads the record then stops", "zz"),
        "qntmc 177: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 177: the processor reads the record then stops", "AgentU"),
        "ruyaw 177: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 177: the processor reads the record then stops", "keyboard"),
        "bssor 177: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 177: the processor reads the record then stops", "AA"),
        "round 177: the processor reads the record then stops",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "key"),
        "bssxh 177: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "lemon"),
        "csgbq 177: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "a"),
        "round 177: a worker pulls the next task from the queue",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "zz"),
        "qntmc 177: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 177: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "keyboard"),
        "bssor 177: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 177: a worker pulls the next task from the queue", "AA"),
        "round 177: a worker pulls the next task from the queue",
    ),
    (
        ("round 177: signals travel through the network layer", "key"),
        "bssxh 177: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 177: signals travel through the network layer", "lemon"),
        "csgbq 177: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 177: signals travel through the network layer", "a"),
        "round 177: signals travel through the network layer",
    ),
    (
        ("round 177: signals travel through the network layer", "zz"),
        "qntmc 177: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 177: signals travel through the network layer", "AgentU"),
        "ruyaw 177: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 177: signals travel through the network layer", "keyboard"),
        "bssor 177: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 177: signals travel through the network layer", "AA"),
        "round 177: signals travel through the network layer",
    ),
    (
        ("round 177: the gateway routes each request by policy", "key"),
        "bssxh 177: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 177: the gateway routes each request by policy", "lemon"),
        "csgbq 177: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 177: the gateway routes each request by policy", "a"),
        "round 177: the gateway routes each request by policy",
    ),
    (
        ("round 177: the gateway routes each request by policy", "zz"),
        "qntmc 177: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 177: the gateway routes each request by policy", "AgentU"),
        "ruyaw 177: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 177: the gateway routes each request by policy", "keyboard"),
        "bssor 177: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 177: the gateway routes each request by policy", "AA"),
        "round 177: the gateway routes each request by policy",
    ),
    (("round 177: memory grows until the buffer is full", "key"), "bssxh 177: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 177: memory grows until the buffer is full", "lemon"), "csgbq 177: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 177: memory grows until the buffer is full", "a"), "round 177: memory grows until the buffer is full"),
    (("round 177: memory grows until the buffer is full", "zz"), "qntmc 177: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 177: memory grows until the buffer is full", "AgentU"),
        "ruyaw 177: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 177: memory grows until the buffer is full", "keyboard"),
        "bssor 177: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 177: memory grows until the buffer is full", "AA"), "round 177: memory grows until the buffer is full"),
    (("round 177: the cluster mirrors every packet twice", "key"), "bssxh 177: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 177: the cluster mirrors every packet twice", "lemon"),
        "csgbq 177: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 177: the cluster mirrors every packet twice", "a"), "round 177: the cluster mirrors every packet twice"),
    (("round 177: the cluster mirrors every packet twice", "zz"), "qntmc 177: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 177: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 177: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 177: the cluster mirrors every packet twice", "keyboard"),
        "bssor 177: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 177: the cluster mirrors every packet twice", "AA"), "round 177: the cluster mirrors every packet twice"),
    (
        ("round 177: ranking uses tokens learned from the corpus", "key"),
        "bssxh 177: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 177: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", "a"),
        "round 177: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 177: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 177: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 177: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", "AA"),
        "round 177: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 177: a long session ends when the candle dies", "key"),
        "bssxh 177: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 177: a long session ends when the candle dies", "lemon"),
        "csgbq 177: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 177: a long session ends when the candle dies", "a"),
        "round 177: a long session ends when the candle dies",
    ),
    (
        ("round 177: a long session ends when the candle dies", "zz"),
        "qntmc 177: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 177: a long session ends when the candle dies", "AgentU"),
        "ruyaw 177: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 177: a long session ends when the candle dies", "keyboard"),
        "bssor 177: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 177: a long session ends when the candle dies", "AA"),
        "round 177: a long session ends when the candle dies",
    ),
    (("round 177: encode the prompt then map the result", "key"), "bssxh 177: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 177: encode the prompt then map the result", "lemon"), "csgbq 177: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 177: encode the prompt then map the result", "a"), "round 177: encode the prompt then map the result"),
    (("round 177: encode the prompt then map the result", "zz"), "qntmc 177: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 177: encode the prompt then map the result", "AgentU"),
        "ruyaw 177: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 177: encode the prompt then map the result", "keyboard"),
        "bssor 177: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 177: encode the prompt then map the result", "AA"), "round 177: encode the prompt then map the result"),
    (("round 177: the kernel wakes the worker at dawn", "key"), "bssxh 177: rri iovlop ukocc xfo ambocb er neux"),
    (("round 177: the kernel wakes the worker at dawn", "lemon"), "csgbq 177: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 177: the kernel wakes the worker at dawn", "a"), "round 177: the kernel wakes the worker at dawn"),
    (("round 177: the kernel wakes the worker at dawn", "zz"), "qntmc 177: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 177: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 177: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 177: the kernel wakes the worker at dawn", "keyboard"), "bssor 177: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 177: the kernel wakes the worker at dawn", "AA"), "round 177: the kernel wakes the worker at dawn"),
    (("round 177: service latency drops after the patch", "key"), "bssxh 177: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 177: service latency drops after the patch", "lemon"), "csgbq 177: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 177: service latency drops after the patch", "a"), "round 177: service latency drops after the patch"),
    (("round 177: service latency drops after the patch", "zz"), "qntmc 177: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 177: service latency drops after the patch", "AgentU"),
        "ruyaw 177: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 177: service latency drops after the patch", "keyboard"),
        "bssor 177: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 177: service latency drops after the patch", "AA"), "round 177: service latency drops after the patch"),
    (
        ("round 177: the library caches every vector it sees", "key"),
        "bssxh 177: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 177: the library caches every vector it sees", "lemon"),
        "csgbq 177: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 177: the library caches every vector it sees", "a"), "round 177: the library caches every vector it sees"),
    (
        ("round 177: the library caches every vector it sees", "zz"),
        "qntmc 177: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 177: the library caches every vector it sees", "AgentU"),
        "ruyaw 177: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 177: the library caches every vector it sees", "keyboard"),
        "bssor 177: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 177: the library caches every vector it sees", "AA"),
        "round 177: the library caches every vector it sees",
    ),
    (("round 177: agents argue then the debate resolves", "key"), "bssxh 177: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 177: agents argue then the debate resolves", "lemon"), "csgbq 177: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 177: agents argue then the debate resolves", "a"), "round 177: agents argue then the debate resolves"),
    (("round 177: agents argue then the debate resolves", "zz"), "qntmc 177: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 177: agents argue then the debate resolves", "AgentU"),
        "ruyaw 177: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 177: agents argue then the debate resolves", "keyboard"),
        "bssor 177: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 177: agents argue then the debate resolves", "AA"), "round 177: agents argue then the debate resolves"),
    (("round 177: the filter keeps only strong matches", "key"), "bssxh 177: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 177: the filter keeps only strong matches", "lemon"), "csgbq 177: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 177: the filter keeps only strong matches", "a"), "round 177: the filter keeps only strong matches"),
    (("round 177: the filter keeps only strong matches", "zz"), "qntmc 177: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 177: the filter keeps only strong matches", "AgentU"), "ruyaw 177: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 177: the filter keeps only strong matches", "keyboard"),
        "bssor 177: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 177: the filter keeps only strong matches", "AA"), "round 177: the filter keeps only strong matches"),
    (("round 177: the model answers with a short reply", "key"), "bssxh 177: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 177: the model answers with a short reply", "lemon"), "csgbq 177: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 177: the model answers with a short reply", "a"), "round 177: the model answers with a short reply"),
    (("round 177: the model answers with a short reply", "zz"), "qntmc 177: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 177: the model answers with a short reply", "AgentU"), "ruyaw 177: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 177: the model answers with a short reply", "keyboard"),
        "bssor 177: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 177: the model answers with a short reply", "AA"), "round 177: the model answers with a short reply"),
    (
        ("round 177: the recorder stores the reasoning trace", "key"),
        "bssxh 177: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 177: the recorder stores the reasoning trace", "lemon"),
        "csgbq 177: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 177: the recorder stores the reasoning trace", "a"), "round 177: the recorder stores the reasoning trace"),
    (
        ("round 177: the recorder stores the reasoning trace", "zz"),
        "qntmc 177: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 177: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 177: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 177: the recorder stores the reasoning trace", "keyboard"),
        "bssor 177: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 177: the recorder stores the reasoning trace", "AA"),
        "round 177: the recorder stores the reasoning trace",
    ),
    (("round 177: the angel watches the processor run", "key"), "bssxh 177: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 177: the angel watches the processor run", "lemon"), "csgbq 177: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 177: the angel watches the processor run", "a"), "round 177: the angel watches the processor run"),
    (("round 177: the angel watches the processor run", "zz"), "qntmc 177: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 177: the angel watches the processor run", "AgentU"), "ruyaw 177: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 177: the angel watches the processor run", "keyboard"), "bssor 177: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 177: the angel watches the processor run", "AA"), "round 177: the angel watches the processor run"),
    (("round 177: angle of the vector decides the match", "key"), "bssxh 177: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 177: angle of the vector decides the match", "lemon"), "csgbq 177: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 177: angle of the vector decides the match", "a"), "round 177: angle of the vector decides the match"),
    (("round 177: angle of the vector decides the match", "zz"), "qntmc 177: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 177: angle of the vector decides the match", "AgentU"),
        "ruyaw 177: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 177: angle of the vector decides the match", "keyboard"),
        "bssor 177: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 177: angle of the vector decides the match", "AA"), "round 177: angle of the vector decides the match"),
    (
        ("round 177: the candle burns twice as long at night", "key"),
        "bssxh 177: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 177: the candle burns twice as long at night", "lemon"),
        "csgbq 177: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 177: the candle burns twice as long at night", "a"), "round 177: the candle burns twice as long at night"),
    (
        ("round 177: the candle burns twice as long at night", "zz"),
        "qntmc 177: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 177: the candle burns twice as long at night", "AgentU"),
        "ruyaw 177: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 177: the candle burns twice as long at night", "keyboard"),
        "bssor 177: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 177: the candle burns twice as long at night", "AA"),
        "round 177: the candle burns twice as long at night",
    ),
    (("round 177: a mirror of the universe in one line", "key"), "bssxh 177: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 177: a mirror of the universe in one line", "lemon"), "csgbq 177: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 177: a mirror of the universe in one line", "a"), "round 177: a mirror of the universe in one line"),
    (("round 177: a mirror of the universe in one line", "zz"), "qntmc 177: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 177: a mirror of the universe in one line", "AgentU"), "ruyaw 177: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 177: a mirror of the universe in one line", "keyboard"),
        "bssor 177: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 177: a mirror of the universe in one line", "AA"), "round 177: a mirror of the universe in one line"),
    (("round 177: the queue drains before the storm", "key"), "bssxh 177: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 177: the queue drains before the storm", "lemon"), "csgbq 177: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 177: the queue drains before the storm", "a"), "round 177: the queue drains before the storm"),
    (("round 177: the queue drains before the storm", "zz"), "qntmc 177: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 177: the queue drains before the storm", "AgentU"), "ruyaw 177: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 177: the queue drains before the storm", "keyboard"), "bssor 177: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 177: the queue drains before the storm", "AA"), "round 177: the queue drains before the storm"),
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
