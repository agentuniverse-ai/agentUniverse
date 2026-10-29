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
    (("kitten202", "key"), "umrdil202"),
    (("kitten202", "lemon"), "vmfhry202"),
    (("kitten202", "a"), "kitten202"),
    (("kitten202", "zz"), "jhssdm202"),
    (("kitten202", "AgentU"), "koxgxh202"),
    (("kitten202", "keyboard"), "umrusn202"),
    (("kitten202", "AA"), "kitten202"),
    (("sitting202", "key"), "cmrdmlq202"),
    (("sitting202", "lemon"), "dmfhvyk202"),
    (("sitting202", "a"), "sitting202"),
    (("sitting202", "zz"), "rhsshmf202"),
    (("sitting202", "AgentU"), "soxgbhg202"),
    (("sitting202", "keyboard"), "cmruwnx202"),
    (("sitting202", "AA"), "sitting202"),
    (("agent202", "key"), "kkcxx202"),
    (("agent202", "lemon"), "lkqbg202"),
    (("agent202", "a"), "agent202"),
    (("agent202", "zz"), "zfdms202"),
    (("agent202", "AgentU"), "amiam202"),
    (("agent202", "keyboard"), "kkcoh202"),
    (("agent202", "AA"), "agent202"),
    (("angle202", "key"), "krevi202"),
    (("angle202", "lemon"), "lrszr202"),
    (("angle202", "a"), "angle202"),
    (("angle202", "zz"), "zmfkd202"),
    (("angle202", "AgentU"), "atkyx202"),
    (("angle202", "keyboard"), "krems202"),
    (("angle202", "AA"), "angle202"),
    (("universe202", "key"), "ergfipci202"),
    (("universe202", "lemon"), "frujrcwq202"),
    (("universe202", "a"), "universe202"),
    (("universe202", "zz"), "tmhudqrd202"),
    (("universe202", "AgentU"), "utmixlsk202"),
    (("universe202", "keyboard"), "ergwsrjh202"),
    (("universe202", "AA"), "universe202"),
    (("memory202", "key"), "wikyvw202"),
    (("memory202", "lemon"), "xiycej202"),
    (("memory202", "a"), "memory202"),
    (("memory202", "zz"), "ldlnqx202"),
    (("memory202", "AgentU"), "mkqbks202"),
    (("memory202", "keyboard"), "wikpfy202"),
    (("memory202", "AA"), "memory202"),
    (("stream202", "key"), "cxpoek202"),
    (("stream202", "lemon"), "dxdsnx202"),
    (("stream202", "a"), "stream202"),
    (("stream202", "zz"), "rsqdzl202"),
    (("stream202", "AgentU"), "szvrtg202"),
    (("stream202", "keyboard"), "cxpfom202"),
    (("stream202", "AA"), "stream202"),
    (("context202", "key"), "msldivd202"),
    (("context202", "lemon"), "nszhrix202"),
    (("context202", "a"), "context202"),
    (("context202", "zz"), "bnmsdws202"),
    (("context202", "AgentU"), "curgxrt202"),
    (("context202", "keyboard"), "mslusxk202"),
    (("context202", "AA"), "context202"),
    (("knowledge202", "key"), "urmgpcnkc202"),
    (("knowledge202", "lemon"), "vrakyphss202"),
    (("knowledge202", "a"), "knowledge202"),
    (("knowledge202", "zz"), "jmnvkdcfd202"),
    (("knowledge202", "AgentU"), "ktsjeydmi202"),
    (("knowledge202", "keyboard"), "urmxzeujo202"),
    (("knowledge202", "AA"), "knowledge202"),
    (("vector202", "key"), "fiadsp202"),
    (("vector202", "lemon"), "giohbc202"),
    (("vector202", "a"), "vector202"),
    (("vector202", "zz"), "udbsnq202"),
    (("vector202", "AgentU"), "vkgghl202"),
    (("vector202", "keyboard"), "fiaucr202"),
    (("vector202", "AA"), "vector202"),
    (("processor202", "key"), "zvmmiqcsp202"),
    (("processor202", "lemon"), "avaqrdwaf202"),
    (("processor202", "a"), "processor202"),
    (("processor202", "zz"), "oqnbdrrnq202"),
    (("processor202", "AgentU"), "pxspxmsuv202"),
    (("processor202", "keyboard"), "zvmdssjrb202"),
    (("processor202", "AA"), "processor202"),
    (("reasoning202", "key"), "biycslsre202"),
    (("reasoning202", "lemon"), "cimgbymzu202"),
    (("reasoning202", "a"), "reasoning202"),
    (("reasoning202", "zz"), "qdzrnmhmf202"),
    (("reasoning202", "AgentU"), "rkefhhitk202"),
    (("reasoning202", "keyboard"), "biytcnzqq202"),
    (("reasoning202", "AA"), "reasoning202"),
    (("machine202", "key"), "wearmlo202"),
    (("machine202", "lemon"), "xeovvyi202"),
    (("machine202", "a"), "machine202"),
    (("machine202", "zz"), "lzbghmd202"),
    (("machine202", "AgentU"), "mggubhe202"),
    (("machine202", "keyboard"), "weaiwnv202"),
    (("machine202", "AA"), "machine202"),
    (("learning202", "key"), "viybrgxk202"),
    (("learning202", "lemon"), "wimfatrs202"),
    (("learning202", "a"), "learning202"),
    (("learning202", "zz"), "kdzqmhmf202"),
    (("learning202", "AgentU"), "lkeegcnm202"),
    (("learning202", "keyboard"), "viysbiej202"),
    (("learning202", "AA"), "learning202"),
    (("model202", "key"), "wsbop202"),
    (("model202", "lemon"), "xspsy202"),
    (("model202", "a"), "model202"),
    (("model202", "zz"), "lncdk202"),
    (("model202", "AgentU"), "muhre202"),
    (("model202", "keyboard"), "wsbfz202"),
    (("model202", "AA"), "model202"),
    (("token202", "key"), "dsior202"),
    (("token202", "lemon"), "eswsa202"),
    (("token202", "a"), "token202"),
    (("token202", "zz"), "snjdm202"),
    (("token202", "AgentU"), "tuorg202"),
    (("token202", "keyboard"), "dsifb202"),
    (("token202", "AA"), "token202"),
    (("prompt202", "key"), "zvmwtr202"),
    (("prompt202", "lemon"), "avaace202"),
    (("prompt202", "a"), "prompt202"),
    (("prompt202", "zz"), "oqnlos202"),
    (("prompt202", "AgentU"), "pxszin202"),
    (("prompt202", "keyboard"), "zvmndt202"),
    (("prompt202", "AA"), "prompt202"),
    (("session202", "key"), "ciqcmmx202"),
    (("session202", "lemon"), "diegvzr202"),
    (("session202", "a"), "session202"),
    (("session202", "zz"), "rdrrhnm202"),
    (("session202", "AgentU"), "skwfbin202"),
    (("session202", "keyboard"), "ciqtwoe202"),
    (("session202", "AA"), "session202"),
    (("library202", "key"), "vmzbepi202"),
    (("library202", "lemon"), "wmnfncc202"),
    (("library202", "a"), "library202"),
    (("library202", "zz"), "khaqzqx202"),
    (("library202", "AgentU"), "lofetly202"),
    (("library202", "keyboard"), "vmzsorp202"),
    (("library202", "AA"), "library202"),
    (("service202", "key"), "cipfmao202"),
    (("service202", "lemon"), "didjvni202"),
    (("service202", "a"), "service202"),
    (("service202", "zz"), "rdquhbd202"),
    (("service202", "AgentU"), "skvibwe202"),
    (("service202", "keyboard"), "cipwwcv202"),
    (("service202", "AA"), "service202"),
    (("gateway202", "key"), "qeroayi202"),
    (("gateway202", "lemon"), "refsjlc202"),
    (("gateway202", "a"), "gateway202"),
    (("gateway202", "zz"), "fzsdvzx202"),
    (("gateway202", "AgentU"), "ggxrpuy202"),
    (("gateway202", "keyboard"), "qerfkap202"),
    (("gateway202", "AA"), "gateway202"),
    (("storage202", "key"), "cxmbeeo202"),
    (("storage202", "lemon"), "dxafnri202"),
    (("storage202", "a"), "storage202"),
    (("storage202", "zz"), "rsnqzfd202"),
    (("storage202", "AgentU"), "szsetae202"),
    (("storage202", "keyboard"), "cxmsogv202"),
    (("storage202", "AA"), "storage202"),
    (("network202", "key"), "xirgspu202"),
    (("network202", "lemon"), "yifkbco202"),
    (("network202", "a"), "network202"),
    (("network202", "zz"), "mdsvnqj202"),
    (("network202", "AgentU"), "nkxjhlk202"),
    (("network202", "keyboard"), "xirxcrb202"),
    (("network202", "AA"), "network202"),
    (("latency202", "key"), "verorai202"),
    (("latency202", "lemon"), "wefsanc202"),
    (("latency202", "a"), "latency202"),
    (("latency202", "zz"), "kzsdmbx202"),
    (("latency202", "AgentU"), "lgxrgwy202"),
    (("latency202", "keyboard"), "verfbcp202"),
    (("latency202", "AA"), "latency202"),
    (("buffer202", "key"), "lydpip202"),
    (("buffer202", "lemon"), "myrtrc202"),
    (("buffer202", "a"), "buffer202"),
    (("buffer202", "zz"), "ateedq202"),
    (("buffer202", "AgentU"), "bajsxl202"),
    (("buffer202", "keyboard"), "lydgsr202"),
    (("buffer202", "AA"), "buffer202"),
    (("queue202", "key"), "aycei202"),
    (("queue202", "lemon"), "byqir202"),
    (("queue202", "a"), "queue202"),
    (("queue202", "zz"), "ptdtd202"),
    (("queue202", "AgentU"), "qaihx202"),
    (("queue202", "keyboard"), "aycvs202"),
    (("queue202", "AA"), "queue202"),
    (("worker202", "key"), "gspuip202"),
    (("worker202", "lemon"), "hsdyrc202"),
    (("worker202", "a"), "worker202"),
    (("worker202", "zz"), "vnqjdq202"),
    (("worker202", "AgentU"), "wuvxxl202"),
    (("worker202", "keyboard"), "gsplsr202"),
    (("worker202", "AA"), "worker202"),
    (("kernel202", "key"), "uipxij202"),
    (("kernel202", "lemon"), "vidbrw202"),
    (("kernel202", "a"), "kernel202"),
    (("kernel202", "zz"), "jdqmdk202"),
    (("kernel202", "AgentU"), "kkvaxf202"),
    (("kernel202", "keyboard"), "uiposl202"),
    (("kernel202", "AA"), "kernel202"),
    (("signal202", "key"), "cmexej202"),
    (("signal202", "lemon"), "dmsbnw202"),
    (("signal202", "a"), "signal202"),
    (("signal202", "zz"), "rhfmzk202"),
    (("signal202", "AgentU"), "sokatf202"),
    (("signal202", "keyboard"), "cmeool202"),
    (("signal202", "AA"), "signal202"),
    (("packet202", "key"), "zeauir202"),
    (("packet202", "lemon"), "aeoyre202"),
    (("packet202", "a"), "packet202"),
    (("packet202", "zz"), "ozbjds202"),
    (("packet202", "AgentU"), "pggxxn202"),
    (("packet202", "keyboard"), "zealst202"),
    (("packet202", "AA"), "packet202"),
    (("router202", "key"), "bssdip202"),
    (("router202", "lemon"), "csghrc202"),
    (("router202", "a"), "router202"),
    (("router202", "zz"), "qntsdq202"),
    (("router202", "AgentU"), "ruygxl202"),
    (("router202", "keyboard"), "bssusr202"),
    (("router202", "AA"), "router202"),
    (("cluster202", "key"), "mpscxcb202"),
    (("cluster202", "lemon"), "npgggpv202"),
    (("cluster202", "a"), "cluster202"),
    (("cluster202", "zz"), "bktrsdq202"),
    (("cluster202", "AgentU"), "cryfmyr202"),
    (("cluster202", "keyboard"), "mpsthei202"),
    (("cluster202", "AA"), "cluster202"),
    (("mirror202", "key"), "wmpbsp202"),
    (("mirror202", "lemon"), "xmdfbc202"),
    (("mirror202", "a"), "mirror202"),
    (("mirror202", "zz"), "lhqqnq202"),
    (("mirror202", "AgentU"), "movehl202"),
    (("mirror202", "keyboard"), "wmpscr202"),
    (("mirror202", "AA"), "mirror202"),
    (("filter202", "key"), "pmjdip202"),
    (("filter202", "lemon"), "qmxhrc202"),
    (("filter202", "a"), "filter202"),
    (("filter202", "zz"), "ehksdq202"),
    (("filter202", "AgentU"), "fopgxl202"),
    (("filter202", "keyboard"), "pmjusr202"),
    (("filter202", "AA"), "filter202"),
    (("ranking202", "key"), "belumlq202"),
    (("ranking202", "lemon"), "cezyvyk202"),
    (("ranking202", "a"), "ranking202"),
    (("ranking202", "zz"), "qzmjhmf202"),
    (("ranking202", "AgentU"), "rgrxbhg202"),
    (("ranking202", "keyboard"), "bellwnx202"),
    (("ranking202", "AA"), "ranking202"),
    (("encoding202", "key"), "orayhgxk202"),
    (("encoding202", "lemon"), "procqtrs202"),
    (("encoding202", "a"), "encoding202"),
    (("encoding202", "zz"), "dmbnchmf202"),
    (("encoding202", "AgentU"), "etgbwcnm202"),
    (("encoding202", "keyboard"), "orapriej202"),
    (("encoding202", "AA"), "encoding202"),
    (("mapping202", "key"), "wenzmlq202"),
    (("mapping202", "lemon"), "xebdvyk202"),
    (("mapping202", "a"), "mapping202"),
    (("mapping202", "zz"), "lzoohmf202"),
    (("mapping202", "AgentU"), "mgtcbhg202"),
    (("mapping202", "keyboard"), "wenqwnx202"),
    (("mapping202", "AA"), "mapping202"),
    (("record202", "key"), "biayvb202"),
    (("record202", "lemon"), "cioceo202"),
    (("record202", "a"), "record202"),
    (("record202", "zz"), "qdbnqc202"),
    (("record202", "AgentU"), "rkgbkx202"),
    (("record202", "keyboard"), "biapfd202"),
    (("record202", "AA"), "record202"),
    (("candle202", "key"), "melnpc202"),
    (("candle202", "lemon"), "nezryp202"),
    (("candle202", "a"), "candle202"),
    (("candle202", "zz"), "bzmckd202"),
    (("candle202", "AgentU"), "cgrqey202"),
    (("candle202", "keyboard"), "meleze202"),
    (("candle202", "AA"), "candle202"),
    (("thread202", "key"), "dlpoeb202"),
    (("thread202", "lemon"), "eldsno202"),
    (("thread202", "a"), "thread202"),
    (("thread202", "zz"), "sgqdzc202"),
    (("thread202", "AgentU"), "tnvrtx202"),
    (("thread202", "keyboard"), "dlpfod202"),
    (("thread202", "AA"), "thread202"),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 202: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 202: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "a"),
        "round 202: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 202: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 202: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 202: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", "AA"),
        "round 202: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "key"),
        "bssxh 202: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 202: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "a"),
        "round 202: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 202: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 202: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 202: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", "AA"),
        "round 202: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 202: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 202: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "a"),
        "round 202: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 202: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 202: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 202: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", "AA"),
        "round 202: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 202: the processor reads the record then stops", "key"),
        "bssxh 202: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 202: the processor reads the record then stops", "lemon"),
        "csgbq 202: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 202: the processor reads the record then stops", "a"),
        "round 202: the processor reads the record then stops",
    ),
    (
        ("round 202: the processor reads the record then stops", "zz"),
        "qntmc 202: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 202: the processor reads the record then stops", "AgentU"),
        "ruyaw 202: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 202: the processor reads the record then stops", "keyboard"),
        "bssor 202: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 202: the processor reads the record then stops", "AA"),
        "round 202: the processor reads the record then stops",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "key"),
        "bssxh 202: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "lemon"),
        "csgbq 202: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "a"),
        "round 202: a worker pulls the next task from the queue",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "zz"),
        "qntmc 202: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 202: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "keyboard"),
        "bssor 202: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 202: a worker pulls the next task from the queue", "AA"),
        "round 202: a worker pulls the next task from the queue",
    ),
    (
        ("round 202: signals travel through the network layer", "key"),
        "bssxh 202: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 202: signals travel through the network layer", "lemon"),
        "csgbq 202: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 202: signals travel through the network layer", "a"),
        "round 202: signals travel through the network layer",
    ),
    (
        ("round 202: signals travel through the network layer", "zz"),
        "qntmc 202: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 202: signals travel through the network layer", "AgentU"),
        "ruyaw 202: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 202: signals travel through the network layer", "keyboard"),
        "bssor 202: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 202: signals travel through the network layer", "AA"),
        "round 202: signals travel through the network layer",
    ),
    (
        ("round 202: the gateway routes each request by policy", "key"),
        "bssxh 202: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 202: the gateway routes each request by policy", "lemon"),
        "csgbq 202: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 202: the gateway routes each request by policy", "a"),
        "round 202: the gateway routes each request by policy",
    ),
    (
        ("round 202: the gateway routes each request by policy", "zz"),
        "qntmc 202: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 202: the gateway routes each request by policy", "AgentU"),
        "ruyaw 202: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 202: the gateway routes each request by policy", "keyboard"),
        "bssor 202: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 202: the gateway routes each request by policy", "AA"),
        "round 202: the gateway routes each request by policy",
    ),
    (("round 202: memory grows until the buffer is full", "key"), "bssxh 202: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 202: memory grows until the buffer is full", "lemon"), "csgbq 202: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 202: memory grows until the buffer is full", "a"), "round 202: memory grows until the buffer is full"),
    (("round 202: memory grows until the buffer is full", "zz"), "qntmc 202: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 202: memory grows until the buffer is full", "AgentU"),
        "ruyaw 202: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 202: memory grows until the buffer is full", "keyboard"),
        "bssor 202: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 202: memory grows until the buffer is full", "AA"), "round 202: memory grows until the buffer is full"),
    (("round 202: the cluster mirrors every packet twice", "key"), "bssxh 202: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 202: the cluster mirrors every packet twice", "lemon"),
        "csgbq 202: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 202: the cluster mirrors every packet twice", "a"), "round 202: the cluster mirrors every packet twice"),
    (("round 202: the cluster mirrors every packet twice", "zz"), "qntmc 202: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 202: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 202: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 202: the cluster mirrors every packet twice", "keyboard"),
        "bssor 202: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 202: the cluster mirrors every packet twice", "AA"), "round 202: the cluster mirrors every packet twice"),
    (
        ("round 202: ranking uses tokens learned from the corpus", "key"),
        "bssxh 202: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 202: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", "a"),
        "round 202: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 202: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 202: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 202: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", "AA"),
        "round 202: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 202: a long session ends when the candle dies", "key"),
        "bssxh 202: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 202: a long session ends when the candle dies", "lemon"),
        "csgbq 202: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 202: a long session ends when the candle dies", "a"),
        "round 202: a long session ends when the candle dies",
    ),
    (
        ("round 202: a long session ends when the candle dies", "zz"),
        "qntmc 202: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 202: a long session ends when the candle dies", "AgentU"),
        "ruyaw 202: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 202: a long session ends when the candle dies", "keyboard"),
        "bssor 202: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 202: a long session ends when the candle dies", "AA"),
        "round 202: a long session ends when the candle dies",
    ),
    (("round 202: encode the prompt then map the result", "key"), "bssxh 202: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 202: encode the prompt then map the result", "lemon"), "csgbq 202: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 202: encode the prompt then map the result", "a"), "round 202: encode the prompt then map the result"),
    (("round 202: encode the prompt then map the result", "zz"), "qntmc 202: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 202: encode the prompt then map the result", "AgentU"),
        "ruyaw 202: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 202: encode the prompt then map the result", "keyboard"),
        "bssor 202: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 202: encode the prompt then map the result", "AA"), "round 202: encode the prompt then map the result"),
    (("round 202: the kernel wakes the worker at dawn", "key"), "bssxh 202: rri iovlop ukocc xfo ambocb er neux"),
    (("round 202: the kernel wakes the worker at dawn", "lemon"), "csgbq 202: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 202: the kernel wakes the worker at dawn", "a"), "round 202: the kernel wakes the worker at dawn"),
    (("round 202: the kernel wakes the worker at dawn", "zz"), "qntmc 202: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 202: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 202: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 202: the kernel wakes the worker at dawn", "keyboard"), "bssor 202: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 202: the kernel wakes the worker at dawn", "AA"), "round 202: the kernel wakes the worker at dawn"),
    (("round 202: service latency drops after the patch", "key"), "bssxh 202: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 202: service latency drops after the patch", "lemon"), "csgbq 202: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 202: service latency drops after the patch", "a"), "round 202: service latency drops after the patch"),
    (("round 202: service latency drops after the patch", "zz"), "qntmc 202: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 202: service latency drops after the patch", "AgentU"),
        "ruyaw 202: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 202: service latency drops after the patch", "keyboard"),
        "bssor 202: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 202: service latency drops after the patch", "AA"), "round 202: service latency drops after the patch"),
    (
        ("round 202: the library caches every vector it sees", "key"),
        "bssxh 202: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 202: the library caches every vector it sees", "lemon"),
        "csgbq 202: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 202: the library caches every vector it sees", "a"), "round 202: the library caches every vector it sees"),
    (
        ("round 202: the library caches every vector it sees", "zz"),
        "qntmc 202: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 202: the library caches every vector it sees", "AgentU"),
        "ruyaw 202: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 202: the library caches every vector it sees", "keyboard"),
        "bssor 202: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 202: the library caches every vector it sees", "AA"),
        "round 202: the library caches every vector it sees",
    ),
    (("round 202: agents argue then the debate resolves", "key"), "bssxh 202: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 202: agents argue then the debate resolves", "lemon"), "csgbq 202: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 202: agents argue then the debate resolves", "a"), "round 202: agents argue then the debate resolves"),
    (("round 202: agents argue then the debate resolves", "zz"), "qntmc 202: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 202: agents argue then the debate resolves", "AgentU"),
        "ruyaw 202: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 202: agents argue then the debate resolves", "keyboard"),
        "bssor 202: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 202: agents argue then the debate resolves", "AA"), "round 202: agents argue then the debate resolves"),
    (("round 202: the filter keeps only strong matches", "key"), "bssxh 202: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 202: the filter keeps only strong matches", "lemon"), "csgbq 202: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 202: the filter keeps only strong matches", "a"), "round 202: the filter keeps only strong matches"),
    (("round 202: the filter keeps only strong matches", "zz"), "qntmc 202: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 202: the filter keeps only strong matches", "AgentU"), "ruyaw 202: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 202: the filter keeps only strong matches", "keyboard"),
        "bssor 202: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 202: the filter keeps only strong matches", "AA"), "round 202: the filter keeps only strong matches"),
    (("round 202: the model answers with a short reply", "key"), "bssxh 202: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 202: the model answers with a short reply", "lemon"), "csgbq 202: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 202: the model answers with a short reply", "a"), "round 202: the model answers with a short reply"),
    (("round 202: the model answers with a short reply", "zz"), "qntmc 202: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 202: the model answers with a short reply", "AgentU"), "ruyaw 202: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 202: the model answers with a short reply", "keyboard"),
        "bssor 202: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 202: the model answers with a short reply", "AA"), "round 202: the model answers with a short reply"),
    (
        ("round 202: the recorder stores the reasoning trace", "key"),
        "bssxh 202: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 202: the recorder stores the reasoning trace", "lemon"),
        "csgbq 202: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 202: the recorder stores the reasoning trace", "a"), "round 202: the recorder stores the reasoning trace"),
    (
        ("round 202: the recorder stores the reasoning trace", "zz"),
        "qntmc 202: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 202: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 202: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 202: the recorder stores the reasoning trace", "keyboard"),
        "bssor 202: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 202: the recorder stores the reasoning trace", "AA"),
        "round 202: the recorder stores the reasoning trace",
    ),
    (("round 202: the angel watches the processor run", "key"), "bssxh 202: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 202: the angel watches the processor run", "lemon"), "csgbq 202: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 202: the angel watches the processor run", "a"), "round 202: the angel watches the processor run"),
    (("round 202: the angel watches the processor run", "zz"), "qntmc 202: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 202: the angel watches the processor run", "AgentU"), "ruyaw 202: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 202: the angel watches the processor run", "keyboard"), "bssor 202: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 202: the angel watches the processor run", "AA"), "round 202: the angel watches the processor run"),
    (("round 202: angle of the vector decides the match", "key"), "bssxh 202: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 202: angle of the vector decides the match", "lemon"), "csgbq 202: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 202: angle of the vector decides the match", "a"), "round 202: angle of the vector decides the match"),
    (("round 202: angle of the vector decides the match", "zz"), "qntmc 202: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 202: angle of the vector decides the match", "AgentU"),
        "ruyaw 202: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 202: angle of the vector decides the match", "keyboard"),
        "bssor 202: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 202: angle of the vector decides the match", "AA"), "round 202: angle of the vector decides the match"),
    (
        ("round 202: the candle burns twice as long at night", "key"),
        "bssxh 202: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 202: the candle burns twice as long at night", "lemon"),
        "csgbq 202: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 202: the candle burns twice as long at night", "a"), "round 202: the candle burns twice as long at night"),
    (
        ("round 202: the candle burns twice as long at night", "zz"),
        "qntmc 202: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 202: the candle burns twice as long at night", "AgentU"),
        "ruyaw 202: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 202: the candle burns twice as long at night", "keyboard"),
        "bssor 202: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 202: the candle burns twice as long at night", "AA"),
        "round 202: the candle burns twice as long at night",
    ),
    (("round 202: a mirror of the universe in one line", "key"), "bssxh 202: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 202: a mirror of the universe in one line", "lemon"), "csgbq 202: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 202: a mirror of the universe in one line", "a"), "round 202: a mirror of the universe in one line"),
    (("round 202: a mirror of the universe in one line", "zz"), "qntmc 202: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 202: a mirror of the universe in one line", "AgentU"), "ruyaw 202: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 202: a mirror of the universe in one line", "keyboard"),
        "bssor 202: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 202: a mirror of the universe in one line", "AA"), "round 202: a mirror of the universe in one line"),
    (("round 202: the queue drains before the storm", "key"), "bssxh 202: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 202: the queue drains before the storm", "lemon"), "csgbq 202: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 202: the queue drains before the storm", "a"), "round 202: the queue drains before the storm"),
    (("round 202: the queue drains before the storm", "zz"), "qntmc 202: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 202: the queue drains before the storm", "AgentU"), "ruyaw 202: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 202: the queue drains before the storm", "keyboard"), "bssor 202: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 202: the queue drains before the storm", "AA"), "round 202: the queue drains before the storm"),
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
