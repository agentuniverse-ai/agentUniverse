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
    (("kitten124", "key"), "umrdil124"),
    (("kitten124", "lemon"), "vmfhry124"),
    (("kitten124", "a"), "kitten124"),
    (("kitten124", "zz"), "jhssdm124"),
    (("kitten124", "AgentU"), "koxgxh124"),
    (("kitten124", "keyboard"), "umrusn124"),
    (("kitten124", "AA"), "kitten124"),
    (("sitting124", "key"), "cmrdmlq124"),
    (("sitting124", "lemon"), "dmfhvyk124"),
    (("sitting124", "a"), "sitting124"),
    (("sitting124", "zz"), "rhsshmf124"),
    (("sitting124", "AgentU"), "soxgbhg124"),
    (("sitting124", "keyboard"), "cmruwnx124"),
    (("sitting124", "AA"), "sitting124"),
    (("agent124", "key"), "kkcxx124"),
    (("agent124", "lemon"), "lkqbg124"),
    (("agent124", "a"), "agent124"),
    (("agent124", "zz"), "zfdms124"),
    (("agent124", "AgentU"), "amiam124"),
    (("agent124", "keyboard"), "kkcoh124"),
    (("agent124", "AA"), "agent124"),
    (("angle124", "key"), "krevi124"),
    (("angle124", "lemon"), "lrszr124"),
    (("angle124", "a"), "angle124"),
    (("angle124", "zz"), "zmfkd124"),
    (("angle124", "AgentU"), "atkyx124"),
    (("angle124", "keyboard"), "krems124"),
    (("angle124", "AA"), "angle124"),
    (("universe124", "key"), "ergfipci124"),
    (("universe124", "lemon"), "frujrcwq124"),
    (("universe124", "a"), "universe124"),
    (("universe124", "zz"), "tmhudqrd124"),
    (("universe124", "AgentU"), "utmixlsk124"),
    (("universe124", "keyboard"), "ergwsrjh124"),
    (("universe124", "AA"), "universe124"),
    (("memory124", "key"), "wikyvw124"),
    (("memory124", "lemon"), "xiycej124"),
    (("memory124", "a"), "memory124"),
    (("memory124", "zz"), "ldlnqx124"),
    (("memory124", "AgentU"), "mkqbks124"),
    (("memory124", "keyboard"), "wikpfy124"),
    (("memory124", "AA"), "memory124"),
    (("stream124", "key"), "cxpoek124"),
    (("stream124", "lemon"), "dxdsnx124"),
    (("stream124", "a"), "stream124"),
    (("stream124", "zz"), "rsqdzl124"),
    (("stream124", "AgentU"), "szvrtg124"),
    (("stream124", "keyboard"), "cxpfom124"),
    (("stream124", "AA"), "stream124"),
    (("context124", "key"), "msldivd124"),
    (("context124", "lemon"), "nszhrix124"),
    (("context124", "a"), "context124"),
    (("context124", "zz"), "bnmsdws124"),
    (("context124", "AgentU"), "curgxrt124"),
    (("context124", "keyboard"), "mslusxk124"),
    (("context124", "AA"), "context124"),
    (("knowledge124", "key"), "urmgpcnkc124"),
    (("knowledge124", "lemon"), "vrakyphss124"),
    (("knowledge124", "a"), "knowledge124"),
    (("knowledge124", "zz"), "jmnvkdcfd124"),
    (("knowledge124", "AgentU"), "ktsjeydmi124"),
    (("knowledge124", "keyboard"), "urmxzeujo124"),
    (("knowledge124", "AA"), "knowledge124"),
    (("vector124", "key"), "fiadsp124"),
    (("vector124", "lemon"), "giohbc124"),
    (("vector124", "a"), "vector124"),
    (("vector124", "zz"), "udbsnq124"),
    (("vector124", "AgentU"), "vkgghl124"),
    (("vector124", "keyboard"), "fiaucr124"),
    (("vector124", "AA"), "vector124"),
    (("processor124", "key"), "zvmmiqcsp124"),
    (("processor124", "lemon"), "avaqrdwaf124"),
    (("processor124", "a"), "processor124"),
    (("processor124", "zz"), "oqnbdrrnq124"),
    (("processor124", "AgentU"), "pxspxmsuv124"),
    (("processor124", "keyboard"), "zvmdssjrb124"),
    (("processor124", "AA"), "processor124"),
    (("reasoning124", "key"), "biycslsre124"),
    (("reasoning124", "lemon"), "cimgbymzu124"),
    (("reasoning124", "a"), "reasoning124"),
    (("reasoning124", "zz"), "qdzrnmhmf124"),
    (("reasoning124", "AgentU"), "rkefhhitk124"),
    (("reasoning124", "keyboard"), "biytcnzqq124"),
    (("reasoning124", "AA"), "reasoning124"),
    (("machine124", "key"), "wearmlo124"),
    (("machine124", "lemon"), "xeovvyi124"),
    (("machine124", "a"), "machine124"),
    (("machine124", "zz"), "lzbghmd124"),
    (("machine124", "AgentU"), "mggubhe124"),
    (("machine124", "keyboard"), "weaiwnv124"),
    (("machine124", "AA"), "machine124"),
    (("learning124", "key"), "viybrgxk124"),
    (("learning124", "lemon"), "wimfatrs124"),
    (("learning124", "a"), "learning124"),
    (("learning124", "zz"), "kdzqmhmf124"),
    (("learning124", "AgentU"), "lkeegcnm124"),
    (("learning124", "keyboard"), "viysbiej124"),
    (("learning124", "AA"), "learning124"),
    (("model124", "key"), "wsbop124"),
    (("model124", "lemon"), "xspsy124"),
    (("model124", "a"), "model124"),
    (("model124", "zz"), "lncdk124"),
    (("model124", "AgentU"), "muhre124"),
    (("model124", "keyboard"), "wsbfz124"),
    (("model124", "AA"), "model124"),
    (("token124", "key"), "dsior124"),
    (("token124", "lemon"), "eswsa124"),
    (("token124", "a"), "token124"),
    (("token124", "zz"), "snjdm124"),
    (("token124", "AgentU"), "tuorg124"),
    (("token124", "keyboard"), "dsifb124"),
    (("token124", "AA"), "token124"),
    (("prompt124", "key"), "zvmwtr124"),
    (("prompt124", "lemon"), "avaace124"),
    (("prompt124", "a"), "prompt124"),
    (("prompt124", "zz"), "oqnlos124"),
    (("prompt124", "AgentU"), "pxszin124"),
    (("prompt124", "keyboard"), "zvmndt124"),
    (("prompt124", "AA"), "prompt124"),
    (("session124", "key"), "ciqcmmx124"),
    (("session124", "lemon"), "diegvzr124"),
    (("session124", "a"), "session124"),
    (("session124", "zz"), "rdrrhnm124"),
    (("session124", "AgentU"), "skwfbin124"),
    (("session124", "keyboard"), "ciqtwoe124"),
    (("session124", "AA"), "session124"),
    (("library124", "key"), "vmzbepi124"),
    (("library124", "lemon"), "wmnfncc124"),
    (("library124", "a"), "library124"),
    (("library124", "zz"), "khaqzqx124"),
    (("library124", "AgentU"), "lofetly124"),
    (("library124", "keyboard"), "vmzsorp124"),
    (("library124", "AA"), "library124"),
    (("service124", "key"), "cipfmao124"),
    (("service124", "lemon"), "didjvni124"),
    (("service124", "a"), "service124"),
    (("service124", "zz"), "rdquhbd124"),
    (("service124", "AgentU"), "skvibwe124"),
    (("service124", "keyboard"), "cipwwcv124"),
    (("service124", "AA"), "service124"),
    (("gateway124", "key"), "qeroayi124"),
    (("gateway124", "lemon"), "refsjlc124"),
    (("gateway124", "a"), "gateway124"),
    (("gateway124", "zz"), "fzsdvzx124"),
    (("gateway124", "AgentU"), "ggxrpuy124"),
    (("gateway124", "keyboard"), "qerfkap124"),
    (("gateway124", "AA"), "gateway124"),
    (("storage124", "key"), "cxmbeeo124"),
    (("storage124", "lemon"), "dxafnri124"),
    (("storage124", "a"), "storage124"),
    (("storage124", "zz"), "rsnqzfd124"),
    (("storage124", "AgentU"), "szsetae124"),
    (("storage124", "keyboard"), "cxmsogv124"),
    (("storage124", "AA"), "storage124"),
    (("network124", "key"), "xirgspu124"),
    (("network124", "lemon"), "yifkbco124"),
    (("network124", "a"), "network124"),
    (("network124", "zz"), "mdsvnqj124"),
    (("network124", "AgentU"), "nkxjhlk124"),
    (("network124", "keyboard"), "xirxcrb124"),
    (("network124", "AA"), "network124"),
    (("latency124", "key"), "verorai124"),
    (("latency124", "lemon"), "wefsanc124"),
    (("latency124", "a"), "latency124"),
    (("latency124", "zz"), "kzsdmbx124"),
    (("latency124", "AgentU"), "lgxrgwy124"),
    (("latency124", "keyboard"), "verfbcp124"),
    (("latency124", "AA"), "latency124"),
    (("buffer124", "key"), "lydpip124"),
    (("buffer124", "lemon"), "myrtrc124"),
    (("buffer124", "a"), "buffer124"),
    (("buffer124", "zz"), "ateedq124"),
    (("buffer124", "AgentU"), "bajsxl124"),
    (("buffer124", "keyboard"), "lydgsr124"),
    (("buffer124", "AA"), "buffer124"),
    (("queue124", "key"), "aycei124"),
    (("queue124", "lemon"), "byqir124"),
    (("queue124", "a"), "queue124"),
    (("queue124", "zz"), "ptdtd124"),
    (("queue124", "AgentU"), "qaihx124"),
    (("queue124", "keyboard"), "aycvs124"),
    (("queue124", "AA"), "queue124"),
    (("worker124", "key"), "gspuip124"),
    (("worker124", "lemon"), "hsdyrc124"),
    (("worker124", "a"), "worker124"),
    (("worker124", "zz"), "vnqjdq124"),
    (("worker124", "AgentU"), "wuvxxl124"),
    (("worker124", "keyboard"), "gsplsr124"),
    (("worker124", "AA"), "worker124"),
    (("kernel124", "key"), "uipxij124"),
    (("kernel124", "lemon"), "vidbrw124"),
    (("kernel124", "a"), "kernel124"),
    (("kernel124", "zz"), "jdqmdk124"),
    (("kernel124", "AgentU"), "kkvaxf124"),
    (("kernel124", "keyboard"), "uiposl124"),
    (("kernel124", "AA"), "kernel124"),
    (("signal124", "key"), "cmexej124"),
    (("signal124", "lemon"), "dmsbnw124"),
    (("signal124", "a"), "signal124"),
    (("signal124", "zz"), "rhfmzk124"),
    (("signal124", "AgentU"), "sokatf124"),
    (("signal124", "keyboard"), "cmeool124"),
    (("signal124", "AA"), "signal124"),
    (("packet124", "key"), "zeauir124"),
    (("packet124", "lemon"), "aeoyre124"),
    (("packet124", "a"), "packet124"),
    (("packet124", "zz"), "ozbjds124"),
    (("packet124", "AgentU"), "pggxxn124"),
    (("packet124", "keyboard"), "zealst124"),
    (("packet124", "AA"), "packet124"),
    (("router124", "key"), "bssdip124"),
    (("router124", "lemon"), "csghrc124"),
    (("router124", "a"), "router124"),
    (("router124", "zz"), "qntsdq124"),
    (("router124", "AgentU"), "ruygxl124"),
    (("router124", "keyboard"), "bssusr124"),
    (("router124", "AA"), "router124"),
    (("cluster124", "key"), "mpscxcb124"),
    (("cluster124", "lemon"), "npgggpv124"),
    (("cluster124", "a"), "cluster124"),
    (("cluster124", "zz"), "bktrsdq124"),
    (("cluster124", "AgentU"), "cryfmyr124"),
    (("cluster124", "keyboard"), "mpsthei124"),
    (("cluster124", "AA"), "cluster124"),
    (("mirror124", "key"), "wmpbsp124"),
    (("mirror124", "lemon"), "xmdfbc124"),
    (("mirror124", "a"), "mirror124"),
    (("mirror124", "zz"), "lhqqnq124"),
    (("mirror124", "AgentU"), "movehl124"),
    (("mirror124", "keyboard"), "wmpscr124"),
    (("mirror124", "AA"), "mirror124"),
    (("filter124", "key"), "pmjdip124"),
    (("filter124", "lemon"), "qmxhrc124"),
    (("filter124", "a"), "filter124"),
    (("filter124", "zz"), "ehksdq124"),
    (("filter124", "AgentU"), "fopgxl124"),
    (("filter124", "keyboard"), "pmjusr124"),
    (("filter124", "AA"), "filter124"),
    (("ranking124", "key"), "belumlq124"),
    (("ranking124", "lemon"), "cezyvyk124"),
    (("ranking124", "a"), "ranking124"),
    (("ranking124", "zz"), "qzmjhmf124"),
    (("ranking124", "AgentU"), "rgrxbhg124"),
    (("ranking124", "keyboard"), "bellwnx124"),
    (("ranking124", "AA"), "ranking124"),
    (("encoding124", "key"), "orayhgxk124"),
    (("encoding124", "lemon"), "procqtrs124"),
    (("encoding124", "a"), "encoding124"),
    (("encoding124", "zz"), "dmbnchmf124"),
    (("encoding124", "AgentU"), "etgbwcnm124"),
    (("encoding124", "keyboard"), "orapriej124"),
    (("encoding124", "AA"), "encoding124"),
    (("mapping124", "key"), "wenzmlq124"),
    (("mapping124", "lemon"), "xebdvyk124"),
    (("mapping124", "a"), "mapping124"),
    (("mapping124", "zz"), "lzoohmf124"),
    (("mapping124", "AgentU"), "mgtcbhg124"),
    (("mapping124", "keyboard"), "wenqwnx124"),
    (("mapping124", "AA"), "mapping124"),
    (("record124", "key"), "biayvb124"),
    (("record124", "lemon"), "cioceo124"),
    (("record124", "a"), "record124"),
    (("record124", "zz"), "qdbnqc124"),
    (("record124", "AgentU"), "rkgbkx124"),
    (("record124", "keyboard"), "biapfd124"),
    (("record124", "AA"), "record124"),
    (("candle124", "key"), "melnpc124"),
    (("candle124", "lemon"), "nezryp124"),
    (("candle124", "a"), "candle124"),
    (("candle124", "zz"), "bzmckd124"),
    (("candle124", "AgentU"), "cgrqey124"),
    (("candle124", "keyboard"), "meleze124"),
    (("candle124", "AA"), "candle124"),
    (("thread124", "key"), "dlpoeb124"),
    (("thread124", "lemon"), "eldsno124"),
    (("thread124", "a"), "thread124"),
    (("thread124", "zz"), "sgqdzc124"),
    (("thread124", "AgentU"), "tnvrtx124"),
    (("thread124", "keyboard"), "dlpfod124"),
    (("thread124", "AA"), "thread124"),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 124: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 124: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "a"),
        "round 124: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 124: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 124: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 124: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", "AA"),
        "round 124: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "key"),
        "bssxh 124: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 124: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "a"),
        "round 124: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 124: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 124: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 124: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", "AA"),
        "round 124: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 124: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 124: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "a"),
        "round 124: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 124: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 124: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 124: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", "AA"),
        "round 124: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 124: the processor reads the record then stops", "key"),
        "bssxh 124: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 124: the processor reads the record then stops", "lemon"),
        "csgbq 124: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 124: the processor reads the record then stops", "a"),
        "round 124: the processor reads the record then stops",
    ),
    (
        ("round 124: the processor reads the record then stops", "zz"),
        "qntmc 124: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 124: the processor reads the record then stops", "AgentU"),
        "ruyaw 124: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 124: the processor reads the record then stops", "keyboard"),
        "bssor 124: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 124: the processor reads the record then stops", "AA"),
        "round 124: the processor reads the record then stops",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "key"),
        "bssxh 124: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "lemon"),
        "csgbq 124: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "a"),
        "round 124: a worker pulls the next task from the queue",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "zz"),
        "qntmc 124: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 124: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "keyboard"),
        "bssor 124: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 124: a worker pulls the next task from the queue", "AA"),
        "round 124: a worker pulls the next task from the queue",
    ),
    (
        ("round 124: signals travel through the network layer", "key"),
        "bssxh 124: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 124: signals travel through the network layer", "lemon"),
        "csgbq 124: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 124: signals travel through the network layer", "a"),
        "round 124: signals travel through the network layer",
    ),
    (
        ("round 124: signals travel through the network layer", "zz"),
        "qntmc 124: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 124: signals travel through the network layer", "AgentU"),
        "ruyaw 124: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 124: signals travel through the network layer", "keyboard"),
        "bssor 124: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 124: signals travel through the network layer", "AA"),
        "round 124: signals travel through the network layer",
    ),
    (
        ("round 124: the gateway routes each request by policy", "key"),
        "bssxh 124: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 124: the gateway routes each request by policy", "lemon"),
        "csgbq 124: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 124: the gateway routes each request by policy", "a"),
        "round 124: the gateway routes each request by policy",
    ),
    (
        ("round 124: the gateway routes each request by policy", "zz"),
        "qntmc 124: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 124: the gateway routes each request by policy", "AgentU"),
        "ruyaw 124: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 124: the gateway routes each request by policy", "keyboard"),
        "bssor 124: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 124: the gateway routes each request by policy", "AA"),
        "round 124: the gateway routes each request by policy",
    ),
    (("round 124: memory grows until the buffer is full", "key"), "bssxh 124: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 124: memory grows until the buffer is full", "lemon"), "csgbq 124: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 124: memory grows until the buffer is full", "a"), "round 124: memory grows until the buffer is full"),
    (("round 124: memory grows until the buffer is full", "zz"), "qntmc 124: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 124: memory grows until the buffer is full", "AgentU"),
        "ruyaw 124: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 124: memory grows until the buffer is full", "keyboard"),
        "bssor 124: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 124: memory grows until the buffer is full", "AA"), "round 124: memory grows until the buffer is full"),
    (("round 124: the cluster mirrors every packet twice", "key"), "bssxh 124: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 124: the cluster mirrors every packet twice", "lemon"),
        "csgbq 124: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 124: the cluster mirrors every packet twice", "a"), "round 124: the cluster mirrors every packet twice"),
    (("round 124: the cluster mirrors every packet twice", "zz"), "qntmc 124: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 124: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 124: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 124: the cluster mirrors every packet twice", "keyboard"),
        "bssor 124: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 124: the cluster mirrors every packet twice", "AA"), "round 124: the cluster mirrors every packet twice"),
    (
        ("round 124: ranking uses tokens learned from the corpus", "key"),
        "bssxh 124: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 124: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", "a"),
        "round 124: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 124: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 124: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 124: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", "AA"),
        "round 124: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 124: a long session ends when the candle dies", "key"),
        "bssxh 124: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 124: a long session ends when the candle dies", "lemon"),
        "csgbq 124: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 124: a long session ends when the candle dies", "a"),
        "round 124: a long session ends when the candle dies",
    ),
    (
        ("round 124: a long session ends when the candle dies", "zz"),
        "qntmc 124: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 124: a long session ends when the candle dies", "AgentU"),
        "ruyaw 124: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 124: a long session ends when the candle dies", "keyboard"),
        "bssor 124: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 124: a long session ends when the candle dies", "AA"),
        "round 124: a long session ends when the candle dies",
    ),
    (("round 124: encode the prompt then map the result", "key"), "bssxh 124: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 124: encode the prompt then map the result", "lemon"), "csgbq 124: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 124: encode the prompt then map the result", "a"), "round 124: encode the prompt then map the result"),
    (("round 124: encode the prompt then map the result", "zz"), "qntmc 124: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 124: encode the prompt then map the result", "AgentU"),
        "ruyaw 124: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 124: encode the prompt then map the result", "keyboard"),
        "bssor 124: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 124: encode the prompt then map the result", "AA"), "round 124: encode the prompt then map the result"),
    (("round 124: the kernel wakes the worker at dawn", "key"), "bssxh 124: rri iovlop ukocc xfo ambocb er neux"),
    (("round 124: the kernel wakes the worker at dawn", "lemon"), "csgbq 124: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 124: the kernel wakes the worker at dawn", "a"), "round 124: the kernel wakes the worker at dawn"),
    (("round 124: the kernel wakes the worker at dawn", "zz"), "qntmc 124: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 124: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 124: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 124: the kernel wakes the worker at dawn", "keyboard"), "bssor 124: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 124: the kernel wakes the worker at dawn", "AA"), "round 124: the kernel wakes the worker at dawn"),
    (("round 124: service latency drops after the patch", "key"), "bssxh 124: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 124: service latency drops after the patch", "lemon"), "csgbq 124: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 124: service latency drops after the patch", "a"), "round 124: service latency drops after the patch"),
    (("round 124: service latency drops after the patch", "zz"), "qntmc 124: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 124: service latency drops after the patch", "AgentU"),
        "ruyaw 124: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 124: service latency drops after the patch", "keyboard"),
        "bssor 124: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 124: service latency drops after the patch", "AA"), "round 124: service latency drops after the patch"),
    (
        ("round 124: the library caches every vector it sees", "key"),
        "bssxh 124: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 124: the library caches every vector it sees", "lemon"),
        "csgbq 124: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 124: the library caches every vector it sees", "a"), "round 124: the library caches every vector it sees"),
    (
        ("round 124: the library caches every vector it sees", "zz"),
        "qntmc 124: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 124: the library caches every vector it sees", "AgentU"),
        "ruyaw 124: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 124: the library caches every vector it sees", "keyboard"),
        "bssor 124: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 124: the library caches every vector it sees", "AA"),
        "round 124: the library caches every vector it sees",
    ),
    (("round 124: agents argue then the debate resolves", "key"), "bssxh 124: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 124: agents argue then the debate resolves", "lemon"), "csgbq 124: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 124: agents argue then the debate resolves", "a"), "round 124: agents argue then the debate resolves"),
    (("round 124: agents argue then the debate resolves", "zz"), "qntmc 124: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 124: agents argue then the debate resolves", "AgentU"),
        "ruyaw 124: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 124: agents argue then the debate resolves", "keyboard"),
        "bssor 124: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 124: agents argue then the debate resolves", "AA"), "round 124: agents argue then the debate resolves"),
    (("round 124: the filter keeps only strong matches", "key"), "bssxh 124: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 124: the filter keeps only strong matches", "lemon"), "csgbq 124: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 124: the filter keeps only strong matches", "a"), "round 124: the filter keeps only strong matches"),
    (("round 124: the filter keeps only strong matches", "zz"), "qntmc 124: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 124: the filter keeps only strong matches", "AgentU"), "ruyaw 124: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 124: the filter keeps only strong matches", "keyboard"),
        "bssor 124: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 124: the filter keeps only strong matches", "AA"), "round 124: the filter keeps only strong matches"),
    (("round 124: the model answers with a short reply", "key"), "bssxh 124: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 124: the model answers with a short reply", "lemon"), "csgbq 124: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 124: the model answers with a short reply", "a"), "round 124: the model answers with a short reply"),
    (("round 124: the model answers with a short reply", "zz"), "qntmc 124: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 124: the model answers with a short reply", "AgentU"), "ruyaw 124: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 124: the model answers with a short reply", "keyboard"),
        "bssor 124: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 124: the model answers with a short reply", "AA"), "round 124: the model answers with a short reply"),
    (
        ("round 124: the recorder stores the reasoning trace", "key"),
        "bssxh 124: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 124: the recorder stores the reasoning trace", "lemon"),
        "csgbq 124: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 124: the recorder stores the reasoning trace", "a"), "round 124: the recorder stores the reasoning trace"),
    (
        ("round 124: the recorder stores the reasoning trace", "zz"),
        "qntmc 124: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 124: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 124: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 124: the recorder stores the reasoning trace", "keyboard"),
        "bssor 124: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 124: the recorder stores the reasoning trace", "AA"),
        "round 124: the recorder stores the reasoning trace",
    ),
    (("round 124: the angel watches the processor run", "key"), "bssxh 124: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 124: the angel watches the processor run", "lemon"), "csgbq 124: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 124: the angel watches the processor run", "a"), "round 124: the angel watches the processor run"),
    (("round 124: the angel watches the processor run", "zz"), "qntmc 124: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 124: the angel watches the processor run", "AgentU"), "ruyaw 124: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 124: the angel watches the processor run", "keyboard"), "bssor 124: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 124: the angel watches the processor run", "AA"), "round 124: the angel watches the processor run"),
    (("round 124: angle of the vector decides the match", "key"), "bssxh 124: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 124: angle of the vector decides the match", "lemon"), "csgbq 124: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 124: angle of the vector decides the match", "a"), "round 124: angle of the vector decides the match"),
    (("round 124: angle of the vector decides the match", "zz"), "qntmc 124: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 124: angle of the vector decides the match", "AgentU"),
        "ruyaw 124: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 124: angle of the vector decides the match", "keyboard"),
        "bssor 124: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 124: angle of the vector decides the match", "AA"), "round 124: angle of the vector decides the match"),
    (
        ("round 124: the candle burns twice as long at night", "key"),
        "bssxh 124: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 124: the candle burns twice as long at night", "lemon"),
        "csgbq 124: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 124: the candle burns twice as long at night", "a"), "round 124: the candle burns twice as long at night"),
    (
        ("round 124: the candle burns twice as long at night", "zz"),
        "qntmc 124: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 124: the candle burns twice as long at night", "AgentU"),
        "ruyaw 124: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 124: the candle burns twice as long at night", "keyboard"),
        "bssor 124: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 124: the candle burns twice as long at night", "AA"),
        "round 124: the candle burns twice as long at night",
    ),
    (("round 124: a mirror of the universe in one line", "key"), "bssxh 124: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 124: a mirror of the universe in one line", "lemon"), "csgbq 124: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 124: a mirror of the universe in one line", "a"), "round 124: a mirror of the universe in one line"),
    (("round 124: a mirror of the universe in one line", "zz"), "qntmc 124: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 124: a mirror of the universe in one line", "AgentU"), "ruyaw 124: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 124: a mirror of the universe in one line", "keyboard"),
        "bssor 124: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 124: a mirror of the universe in one line", "AA"), "round 124: a mirror of the universe in one line"),
    (("round 124: the queue drains before the storm", "key"), "bssxh 124: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 124: the queue drains before the storm", "lemon"), "csgbq 124: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 124: the queue drains before the storm", "a"), "round 124: the queue drains before the storm"),
    (("round 124: the queue drains before the storm", "zz"), "qntmc 124: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 124: the queue drains before the storm", "AgentU"), "ruyaw 124: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 124: the queue drains before the storm", "keyboard"), "bssor 124: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 124: the queue drains before the storm", "AA"), "round 124: the queue drains before the storm"),
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
