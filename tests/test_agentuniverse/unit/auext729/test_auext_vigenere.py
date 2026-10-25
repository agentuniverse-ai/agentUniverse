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
    (("kitten729", "key"), "umrdil729"),
    (("kitten729", "lemon"), "vmfhry729"),
    (("kitten729", "a"), "kitten729"),
    (("kitten729", "zz"), "jhssdm729"),
    (("kitten729", "AgentU"), "koxgxh729"),
    (("kitten729", "keyboard"), "umrusn729"),
    (("kitten729", "AA"), "kitten729"),
    (("sitting729", "key"), "cmrdmlq729"),
    (("sitting729", "lemon"), "dmfhvyk729"),
    (("sitting729", "a"), "sitting729"),
    (("sitting729", "zz"), "rhsshmf729"),
    (("sitting729", "AgentU"), "soxgbhg729"),
    (("sitting729", "keyboard"), "cmruwnx729"),
    (("sitting729", "AA"), "sitting729"),
    (("agent729", "key"), "kkcxx729"),
    (("agent729", "lemon"), "lkqbg729"),
    (("agent729", "a"), "agent729"),
    (("agent729", "zz"), "zfdms729"),
    (("agent729", "AgentU"), "amiam729"),
    (("agent729", "keyboard"), "kkcoh729"),
    (("agent729", "AA"), "agent729"),
    (("angle729", "key"), "krevi729"),
    (("angle729", "lemon"), "lrszr729"),
    (("angle729", "a"), "angle729"),
    (("angle729", "zz"), "zmfkd729"),
    (("angle729", "AgentU"), "atkyx729"),
    (("angle729", "keyboard"), "krems729"),
    (("angle729", "AA"), "angle729"),
    (("universe729", "key"), "ergfipci729"),
    (("universe729", "lemon"), "frujrcwq729"),
    (("universe729", "a"), "universe729"),
    (("universe729", "zz"), "tmhudqrd729"),
    (("universe729", "AgentU"), "utmixlsk729"),
    (("universe729", "keyboard"), "ergwsrjh729"),
    (("universe729", "AA"), "universe729"),
    (("memory729", "key"), "wikyvw729"),
    (("memory729", "lemon"), "xiycej729"),
    (("memory729", "a"), "memory729"),
    (("memory729", "zz"), "ldlnqx729"),
    (("memory729", "AgentU"), "mkqbks729"),
    (("memory729", "keyboard"), "wikpfy729"),
    (("memory729", "AA"), "memory729"),
    (("stream729", "key"), "cxpoek729"),
    (("stream729", "lemon"), "dxdsnx729"),
    (("stream729", "a"), "stream729"),
    (("stream729", "zz"), "rsqdzl729"),
    (("stream729", "AgentU"), "szvrtg729"),
    (("stream729", "keyboard"), "cxpfom729"),
    (("stream729", "AA"), "stream729"),
    (("context729", "key"), "msldivd729"),
    (("context729", "lemon"), "nszhrix729"),
    (("context729", "a"), "context729"),
    (("context729", "zz"), "bnmsdws729"),
    (("context729", "AgentU"), "curgxrt729"),
    (("context729", "keyboard"), "mslusxk729"),
    (("context729", "AA"), "context729"),
    (("knowledge729", "key"), "urmgpcnkc729"),
    (("knowledge729", "lemon"), "vrakyphss729"),
    (("knowledge729", "a"), "knowledge729"),
    (("knowledge729", "zz"), "jmnvkdcfd729"),
    (("knowledge729", "AgentU"), "ktsjeydmi729"),
    (("knowledge729", "keyboard"), "urmxzeujo729"),
    (("knowledge729", "AA"), "knowledge729"),
    (("vector729", "key"), "fiadsp729"),
    (("vector729", "lemon"), "giohbc729"),
    (("vector729", "a"), "vector729"),
    (("vector729", "zz"), "udbsnq729"),
    (("vector729", "AgentU"), "vkgghl729"),
    (("vector729", "keyboard"), "fiaucr729"),
    (("vector729", "AA"), "vector729"),
    (("processor729", "key"), "zvmmiqcsp729"),
    (("processor729", "lemon"), "avaqrdwaf729"),
    (("processor729", "a"), "processor729"),
    (("processor729", "zz"), "oqnbdrrnq729"),
    (("processor729", "AgentU"), "pxspxmsuv729"),
    (("processor729", "keyboard"), "zvmdssjrb729"),
    (("processor729", "AA"), "processor729"),
    (("reasoning729", "key"), "biycslsre729"),
    (("reasoning729", "lemon"), "cimgbymzu729"),
    (("reasoning729", "a"), "reasoning729"),
    (("reasoning729", "zz"), "qdzrnmhmf729"),
    (("reasoning729", "AgentU"), "rkefhhitk729"),
    (("reasoning729", "keyboard"), "biytcnzqq729"),
    (("reasoning729", "AA"), "reasoning729"),
    (("machine729", "key"), "wearmlo729"),
    (("machine729", "lemon"), "xeovvyi729"),
    (("machine729", "a"), "machine729"),
    (("machine729", "zz"), "lzbghmd729"),
    (("machine729", "AgentU"), "mggubhe729"),
    (("machine729", "keyboard"), "weaiwnv729"),
    (("machine729", "AA"), "machine729"),
    (("learning729", "key"), "viybrgxk729"),
    (("learning729", "lemon"), "wimfatrs729"),
    (("learning729", "a"), "learning729"),
    (("learning729", "zz"), "kdzqmhmf729"),
    (("learning729", "AgentU"), "lkeegcnm729"),
    (("learning729", "keyboard"), "viysbiej729"),
    (("learning729", "AA"), "learning729"),
    (("model729", "key"), "wsbop729"),
    (("model729", "lemon"), "xspsy729"),
    (("model729", "a"), "model729"),
    (("model729", "zz"), "lncdk729"),
    (("model729", "AgentU"), "muhre729"),
    (("model729", "keyboard"), "wsbfz729"),
    (("model729", "AA"), "model729"),
    (("token729", "key"), "dsior729"),
    (("token729", "lemon"), "eswsa729"),
    (("token729", "a"), "token729"),
    (("token729", "zz"), "snjdm729"),
    (("token729", "AgentU"), "tuorg729"),
    (("token729", "keyboard"), "dsifb729"),
    (("token729", "AA"), "token729"),
    (("prompt729", "key"), "zvmwtr729"),
    (("prompt729", "lemon"), "avaace729"),
    (("prompt729", "a"), "prompt729"),
    (("prompt729", "zz"), "oqnlos729"),
    (("prompt729", "AgentU"), "pxszin729"),
    (("prompt729", "keyboard"), "zvmndt729"),
    (("prompt729", "AA"), "prompt729"),
    (("session729", "key"), "ciqcmmx729"),
    (("session729", "lemon"), "diegvzr729"),
    (("session729", "a"), "session729"),
    (("session729", "zz"), "rdrrhnm729"),
    (("session729", "AgentU"), "skwfbin729"),
    (("session729", "keyboard"), "ciqtwoe729"),
    (("session729", "AA"), "session729"),
    (("library729", "key"), "vmzbepi729"),
    (("library729", "lemon"), "wmnfncc729"),
    (("library729", "a"), "library729"),
    (("library729", "zz"), "khaqzqx729"),
    (("library729", "AgentU"), "lofetly729"),
    (("library729", "keyboard"), "vmzsorp729"),
    (("library729", "AA"), "library729"),
    (("service729", "key"), "cipfmao729"),
    (("service729", "lemon"), "didjvni729"),
    (("service729", "a"), "service729"),
    (("service729", "zz"), "rdquhbd729"),
    (("service729", "AgentU"), "skvibwe729"),
    (("service729", "keyboard"), "cipwwcv729"),
    (("service729", "AA"), "service729"),
    (("gateway729", "key"), "qeroayi729"),
    (("gateway729", "lemon"), "refsjlc729"),
    (("gateway729", "a"), "gateway729"),
    (("gateway729", "zz"), "fzsdvzx729"),
    (("gateway729", "AgentU"), "ggxrpuy729"),
    (("gateway729", "keyboard"), "qerfkap729"),
    (("gateway729", "AA"), "gateway729"),
    (("storage729", "key"), "cxmbeeo729"),
    (("storage729", "lemon"), "dxafnri729"),
    (("storage729", "a"), "storage729"),
    (("storage729", "zz"), "rsnqzfd729"),
    (("storage729", "AgentU"), "szsetae729"),
    (("storage729", "keyboard"), "cxmsogv729"),
    (("storage729", "AA"), "storage729"),
    (("network729", "key"), "xirgspu729"),
    (("network729", "lemon"), "yifkbco729"),
    (("network729", "a"), "network729"),
    (("network729", "zz"), "mdsvnqj729"),
    (("network729", "AgentU"), "nkxjhlk729"),
    (("network729", "keyboard"), "xirxcrb729"),
    (("network729", "AA"), "network729"),
    (("latency729", "key"), "verorai729"),
    (("latency729", "lemon"), "wefsanc729"),
    (("latency729", "a"), "latency729"),
    (("latency729", "zz"), "kzsdmbx729"),
    (("latency729", "AgentU"), "lgxrgwy729"),
    (("latency729", "keyboard"), "verfbcp729"),
    (("latency729", "AA"), "latency729"),
    (("buffer729", "key"), "lydpip729"),
    (("buffer729", "lemon"), "myrtrc729"),
    (("buffer729", "a"), "buffer729"),
    (("buffer729", "zz"), "ateedq729"),
    (("buffer729", "AgentU"), "bajsxl729"),
    (("buffer729", "keyboard"), "lydgsr729"),
    (("buffer729", "AA"), "buffer729"),
    (("queue729", "key"), "aycei729"),
    (("queue729", "lemon"), "byqir729"),
    (("queue729", "a"), "queue729"),
    (("queue729", "zz"), "ptdtd729"),
    (("queue729", "AgentU"), "qaihx729"),
    (("queue729", "keyboard"), "aycvs729"),
    (("queue729", "AA"), "queue729"),
    (("worker729", "key"), "gspuip729"),
    (("worker729", "lemon"), "hsdyrc729"),
    (("worker729", "a"), "worker729"),
    (("worker729", "zz"), "vnqjdq729"),
    (("worker729", "AgentU"), "wuvxxl729"),
    (("worker729", "keyboard"), "gsplsr729"),
    (("worker729", "AA"), "worker729"),
    (("kernel729", "key"), "uipxij729"),
    (("kernel729", "lemon"), "vidbrw729"),
    (("kernel729", "a"), "kernel729"),
    (("kernel729", "zz"), "jdqmdk729"),
    (("kernel729", "AgentU"), "kkvaxf729"),
    (("kernel729", "keyboard"), "uiposl729"),
    (("kernel729", "AA"), "kernel729"),
    (("signal729", "key"), "cmexej729"),
    (("signal729", "lemon"), "dmsbnw729"),
    (("signal729", "a"), "signal729"),
    (("signal729", "zz"), "rhfmzk729"),
    (("signal729", "AgentU"), "sokatf729"),
    (("signal729", "keyboard"), "cmeool729"),
    (("signal729", "AA"), "signal729"),
    (("packet729", "key"), "zeauir729"),
    (("packet729", "lemon"), "aeoyre729"),
    (("packet729", "a"), "packet729"),
    (("packet729", "zz"), "ozbjds729"),
    (("packet729", "AgentU"), "pggxxn729"),
    (("packet729", "keyboard"), "zealst729"),
    (("packet729", "AA"), "packet729"),
    (("router729", "key"), "bssdip729"),
    (("router729", "lemon"), "csghrc729"),
    (("router729", "a"), "router729"),
    (("router729", "zz"), "qntsdq729"),
    (("router729", "AgentU"), "ruygxl729"),
    (("router729", "keyboard"), "bssusr729"),
    (("router729", "AA"), "router729"),
    (("cluster729", "key"), "mpscxcb729"),
    (("cluster729", "lemon"), "npgggpv729"),
    (("cluster729", "a"), "cluster729"),
    (("cluster729", "zz"), "bktrsdq729"),
    (("cluster729", "AgentU"), "cryfmyr729"),
    (("cluster729", "keyboard"), "mpsthei729"),
    (("cluster729", "AA"), "cluster729"),
    (("mirror729", "key"), "wmpbsp729"),
    (("mirror729", "lemon"), "xmdfbc729"),
    (("mirror729", "a"), "mirror729"),
    (("mirror729", "zz"), "lhqqnq729"),
    (("mirror729", "AgentU"), "movehl729"),
    (("mirror729", "keyboard"), "wmpscr729"),
    (("mirror729", "AA"), "mirror729"),
    (("filter729", "key"), "pmjdip729"),
    (("filter729", "lemon"), "qmxhrc729"),
    (("filter729", "a"), "filter729"),
    (("filter729", "zz"), "ehksdq729"),
    (("filter729", "AgentU"), "fopgxl729"),
    (("filter729", "keyboard"), "pmjusr729"),
    (("filter729", "AA"), "filter729"),
    (("ranking729", "key"), "belumlq729"),
    (("ranking729", "lemon"), "cezyvyk729"),
    (("ranking729", "a"), "ranking729"),
    (("ranking729", "zz"), "qzmjhmf729"),
    (("ranking729", "AgentU"), "rgrxbhg729"),
    (("ranking729", "keyboard"), "bellwnx729"),
    (("ranking729", "AA"), "ranking729"),
    (("encoding729", "key"), "orayhgxk729"),
    (("encoding729", "lemon"), "procqtrs729"),
    (("encoding729", "a"), "encoding729"),
    (("encoding729", "zz"), "dmbnchmf729"),
    (("encoding729", "AgentU"), "etgbwcnm729"),
    (("encoding729", "keyboard"), "orapriej729"),
    (("encoding729", "AA"), "encoding729"),
    (("mapping729", "key"), "wenzmlq729"),
    (("mapping729", "lemon"), "xebdvyk729"),
    (("mapping729", "a"), "mapping729"),
    (("mapping729", "zz"), "lzoohmf729"),
    (("mapping729", "AgentU"), "mgtcbhg729"),
    (("mapping729", "keyboard"), "wenqwnx729"),
    (("mapping729", "AA"), "mapping729"),
    (("record729", "key"), "biayvb729"),
    (("record729", "lemon"), "cioceo729"),
    (("record729", "a"), "record729"),
    (("record729", "zz"), "qdbnqc729"),
    (("record729", "AgentU"), "rkgbkx729"),
    (("record729", "keyboard"), "biapfd729"),
    (("record729", "AA"), "record729"),
    (("candle729", "key"), "melnpc729"),
    (("candle729", "lemon"), "nezryp729"),
    (("candle729", "a"), "candle729"),
    (("candle729", "zz"), "bzmckd729"),
    (("candle729", "AgentU"), "cgrqey729"),
    (("candle729", "keyboard"), "meleze729"),
    (("candle729", "AA"), "candle729"),
    (("thread729", "key"), "dlpoeb729"),
    (("thread729", "lemon"), "eldsno729"),
    (("thread729", "a"), "thread729"),
    (("thread729", "zz"), "sgqdzc729"),
    (("thread729", "AgentU"), "tnvrtx729"),
    (("thread729", "keyboard"), "dlpfod729"),
    (("thread729", "AA"), "thread729"),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 729: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 729: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "a"),
        "round 729: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 729: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 729: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 729: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", "AA"),
        "round 729: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "key"),
        "bssxh 729: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 729: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "a"),
        "round 729: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 729: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 729: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 729: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", "AA"),
        "round 729: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 729: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 729: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "a"),
        "round 729: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 729: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 729: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 729: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", "AA"),
        "round 729: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 729: the processor reads the record then stops", "key"),
        "bssxh 729: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 729: the processor reads the record then stops", "lemon"),
        "csgbq 729: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 729: the processor reads the record then stops", "a"),
        "round 729: the processor reads the record then stops",
    ),
    (
        ("round 729: the processor reads the record then stops", "zz"),
        "qntmc 729: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 729: the processor reads the record then stops", "AgentU"),
        "ruyaw 729: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 729: the processor reads the record then stops", "keyboard"),
        "bssor 729: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 729: the processor reads the record then stops", "AA"),
        "round 729: the processor reads the record then stops",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "key"),
        "bssxh 729: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "lemon"),
        "csgbq 729: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "a"),
        "round 729: a worker pulls the next task from the queue",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "zz"),
        "qntmc 729: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 729: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "keyboard"),
        "bssor 729: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 729: a worker pulls the next task from the queue", "AA"),
        "round 729: a worker pulls the next task from the queue",
    ),
    (
        ("round 729: signals travel through the network layer", "key"),
        "bssxh 729: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 729: signals travel through the network layer", "lemon"),
        "csgbq 729: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 729: signals travel through the network layer", "a"),
        "round 729: signals travel through the network layer",
    ),
    (
        ("round 729: signals travel through the network layer", "zz"),
        "qntmc 729: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 729: signals travel through the network layer", "AgentU"),
        "ruyaw 729: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 729: signals travel through the network layer", "keyboard"),
        "bssor 729: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 729: signals travel through the network layer", "AA"),
        "round 729: signals travel through the network layer",
    ),
    (
        ("round 729: the gateway routes each request by policy", "key"),
        "bssxh 729: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 729: the gateway routes each request by policy", "lemon"),
        "csgbq 729: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 729: the gateway routes each request by policy", "a"),
        "round 729: the gateway routes each request by policy",
    ),
    (
        ("round 729: the gateway routes each request by policy", "zz"),
        "qntmc 729: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 729: the gateway routes each request by policy", "AgentU"),
        "ruyaw 729: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 729: the gateway routes each request by policy", "keyboard"),
        "bssor 729: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 729: the gateway routes each request by policy", "AA"),
        "round 729: the gateway routes each request by policy",
    ),
    (("round 729: memory grows until the buffer is full", "key"), "bssxh 729: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 729: memory grows until the buffer is full", "lemon"), "csgbq 729: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 729: memory grows until the buffer is full", "a"), "round 729: memory grows until the buffer is full"),
    (("round 729: memory grows until the buffer is full", "zz"), "qntmc 729: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 729: memory grows until the buffer is full", "AgentU"),
        "ruyaw 729: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 729: memory grows until the buffer is full", "keyboard"),
        "bssor 729: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 729: memory grows until the buffer is full", "AA"), "round 729: memory grows until the buffer is full"),
    (("round 729: the cluster mirrors every packet twice", "key"), "bssxh 729: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 729: the cluster mirrors every packet twice", "lemon"),
        "csgbq 729: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 729: the cluster mirrors every packet twice", "a"), "round 729: the cluster mirrors every packet twice"),
    (("round 729: the cluster mirrors every packet twice", "zz"), "qntmc 729: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 729: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 729: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 729: the cluster mirrors every packet twice", "keyboard"),
        "bssor 729: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 729: the cluster mirrors every packet twice", "AA"), "round 729: the cluster mirrors every packet twice"),
    (
        ("round 729: ranking uses tokens learned from the corpus", "key"),
        "bssxh 729: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 729: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", "a"),
        "round 729: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 729: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 729: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 729: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", "AA"),
        "round 729: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 729: a long session ends when the candle dies", "key"),
        "bssxh 729: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 729: a long session ends when the candle dies", "lemon"),
        "csgbq 729: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 729: a long session ends when the candle dies", "a"),
        "round 729: a long session ends when the candle dies",
    ),
    (
        ("round 729: a long session ends when the candle dies", "zz"),
        "qntmc 729: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 729: a long session ends when the candle dies", "AgentU"),
        "ruyaw 729: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 729: a long session ends when the candle dies", "keyboard"),
        "bssor 729: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 729: a long session ends when the candle dies", "AA"),
        "round 729: a long session ends when the candle dies",
    ),
    (("round 729: encode the prompt then map the result", "key"), "bssxh 729: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 729: encode the prompt then map the result", "lemon"), "csgbq 729: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 729: encode the prompt then map the result", "a"), "round 729: encode the prompt then map the result"),
    (("round 729: encode the prompt then map the result", "zz"), "qntmc 729: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 729: encode the prompt then map the result", "AgentU"),
        "ruyaw 729: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 729: encode the prompt then map the result", "keyboard"),
        "bssor 729: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 729: encode the prompt then map the result", "AA"), "round 729: encode the prompt then map the result"),
    (("round 729: the kernel wakes the worker at dawn", "key"), "bssxh 729: rri iovlop ukocc xfo ambocb er neux"),
    (("round 729: the kernel wakes the worker at dawn", "lemon"), "csgbq 729: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 729: the kernel wakes the worker at dawn", "a"), "round 729: the kernel wakes the worker at dawn"),
    (("round 729: the kernel wakes the worker at dawn", "zz"), "qntmc 729: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 729: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 729: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 729: the kernel wakes the worker at dawn", "keyboard"), "bssor 729: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 729: the kernel wakes the worker at dawn", "AA"), "round 729: the kernel wakes the worker at dawn"),
    (("round 729: service latency drops after the patch", "key"), "bssxh 729: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 729: service latency drops after the patch", "lemon"), "csgbq 729: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 729: service latency drops after the patch", "a"), "round 729: service latency drops after the patch"),
    (("round 729: service latency drops after the patch", "zz"), "qntmc 729: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 729: service latency drops after the patch", "AgentU"),
        "ruyaw 729: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 729: service latency drops after the patch", "keyboard"),
        "bssor 729: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 729: service latency drops after the patch", "AA"), "round 729: service latency drops after the patch"),
    (
        ("round 729: the library caches every vector it sees", "key"),
        "bssxh 729: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 729: the library caches every vector it sees", "lemon"),
        "csgbq 729: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 729: the library caches every vector it sees", "a"), "round 729: the library caches every vector it sees"),
    (
        ("round 729: the library caches every vector it sees", "zz"),
        "qntmc 729: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 729: the library caches every vector it sees", "AgentU"),
        "ruyaw 729: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 729: the library caches every vector it sees", "keyboard"),
        "bssor 729: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 729: the library caches every vector it sees", "AA"),
        "round 729: the library caches every vector it sees",
    ),
    (("round 729: agents argue then the debate resolves", "key"), "bssxh 729: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 729: agents argue then the debate resolves", "lemon"), "csgbq 729: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 729: agents argue then the debate resolves", "a"), "round 729: agents argue then the debate resolves"),
    (("round 729: agents argue then the debate resolves", "zz"), "qntmc 729: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 729: agents argue then the debate resolves", "AgentU"),
        "ruyaw 729: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 729: agents argue then the debate resolves", "keyboard"),
        "bssor 729: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 729: agents argue then the debate resolves", "AA"), "round 729: agents argue then the debate resolves"),
    (("round 729: the filter keeps only strong matches", "key"), "bssxh 729: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 729: the filter keeps only strong matches", "lemon"), "csgbq 729: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 729: the filter keeps only strong matches", "a"), "round 729: the filter keeps only strong matches"),
    (("round 729: the filter keeps only strong matches", "zz"), "qntmc 729: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 729: the filter keeps only strong matches", "AgentU"), "ruyaw 729: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 729: the filter keeps only strong matches", "keyboard"),
        "bssor 729: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 729: the filter keeps only strong matches", "AA"), "round 729: the filter keeps only strong matches"),
    (("round 729: the model answers with a short reply", "key"), "bssxh 729: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 729: the model answers with a short reply", "lemon"), "csgbq 729: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 729: the model answers with a short reply", "a"), "round 729: the model answers with a short reply"),
    (("round 729: the model answers with a short reply", "zz"), "qntmc 729: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 729: the model answers with a short reply", "AgentU"), "ruyaw 729: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 729: the model answers with a short reply", "keyboard"),
        "bssor 729: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 729: the model answers with a short reply", "AA"), "round 729: the model answers with a short reply"),
    (
        ("round 729: the recorder stores the reasoning trace", "key"),
        "bssxh 729: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 729: the recorder stores the reasoning trace", "lemon"),
        "csgbq 729: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 729: the recorder stores the reasoning trace", "a"), "round 729: the recorder stores the reasoning trace"),
    (
        ("round 729: the recorder stores the reasoning trace", "zz"),
        "qntmc 729: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 729: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 729: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 729: the recorder stores the reasoning trace", "keyboard"),
        "bssor 729: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 729: the recorder stores the reasoning trace", "AA"),
        "round 729: the recorder stores the reasoning trace",
    ),
    (("round 729: the angel watches the processor run", "key"), "bssxh 729: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 729: the angel watches the processor run", "lemon"), "csgbq 729: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 729: the angel watches the processor run", "a"), "round 729: the angel watches the processor run"),
    (("round 729: the angel watches the processor run", "zz"), "qntmc 729: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 729: the angel watches the processor run", "AgentU"), "ruyaw 729: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 729: the angel watches the processor run", "keyboard"), "bssor 729: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 729: the angel watches the processor run", "AA"), "round 729: the angel watches the processor run"),
    (("round 729: angle of the vector decides the match", "key"), "bssxh 729: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 729: angle of the vector decides the match", "lemon"), "csgbq 729: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 729: angle of the vector decides the match", "a"), "round 729: angle of the vector decides the match"),
    (("round 729: angle of the vector decides the match", "zz"), "qntmc 729: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 729: angle of the vector decides the match", "AgentU"),
        "ruyaw 729: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 729: angle of the vector decides the match", "keyboard"),
        "bssor 729: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 729: angle of the vector decides the match", "AA"), "round 729: angle of the vector decides the match"),
    (
        ("round 729: the candle burns twice as long at night", "key"),
        "bssxh 729: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 729: the candle burns twice as long at night", "lemon"),
        "csgbq 729: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 729: the candle burns twice as long at night", "a"), "round 729: the candle burns twice as long at night"),
    (
        ("round 729: the candle burns twice as long at night", "zz"),
        "qntmc 729: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 729: the candle burns twice as long at night", "AgentU"),
        "ruyaw 729: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 729: the candle burns twice as long at night", "keyboard"),
        "bssor 729: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 729: the candle burns twice as long at night", "AA"),
        "round 729: the candle burns twice as long at night",
    ),
    (("round 729: a mirror of the universe in one line", "key"), "bssxh 729: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 729: a mirror of the universe in one line", "lemon"), "csgbq 729: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 729: a mirror of the universe in one line", "a"), "round 729: a mirror of the universe in one line"),
    (("round 729: a mirror of the universe in one line", "zz"), "qntmc 729: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 729: a mirror of the universe in one line", "AgentU"), "ruyaw 729: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 729: a mirror of the universe in one line", "keyboard"),
        "bssor 729: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 729: a mirror of the universe in one line", "AA"), "round 729: a mirror of the universe in one line"),
    (("round 729: the queue drains before the storm", "key"), "bssxh 729: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 729: the queue drains before the storm", "lemon"), "csgbq 729: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 729: the queue drains before the storm", "a"), "round 729: the queue drains before the storm"),
    (("round 729: the queue drains before the storm", "zz"), "qntmc 729: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 729: the queue drains before the storm", "AgentU"), "ruyaw 729: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 729: the queue drains before the storm", "keyboard"), "bssor 729: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 729: the queue drains before the storm", "AA"), "round 729: the queue drains before the storm"),
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
