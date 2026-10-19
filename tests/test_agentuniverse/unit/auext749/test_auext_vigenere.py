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
    (("kitten749", "key"), "umrdil749"),
    (("kitten749", "lemon"), "vmfhry749"),
    (("kitten749", "a"), "kitten749"),
    (("kitten749", "zz"), "jhssdm749"),
    (("kitten749", "AgentU"), "koxgxh749"),
    (("kitten749", "keyboard"), "umrusn749"),
    (("kitten749", "AA"), "kitten749"),
    (("sitting749", "key"), "cmrdmlq749"),
    (("sitting749", "lemon"), "dmfhvyk749"),
    (("sitting749", "a"), "sitting749"),
    (("sitting749", "zz"), "rhsshmf749"),
    (("sitting749", "AgentU"), "soxgbhg749"),
    (("sitting749", "keyboard"), "cmruwnx749"),
    (("sitting749", "AA"), "sitting749"),
    (("agent749", "key"), "kkcxx749"),
    (("agent749", "lemon"), "lkqbg749"),
    (("agent749", "a"), "agent749"),
    (("agent749", "zz"), "zfdms749"),
    (("agent749", "AgentU"), "amiam749"),
    (("agent749", "keyboard"), "kkcoh749"),
    (("agent749", "AA"), "agent749"),
    (("angle749", "key"), "krevi749"),
    (("angle749", "lemon"), "lrszr749"),
    (("angle749", "a"), "angle749"),
    (("angle749", "zz"), "zmfkd749"),
    (("angle749", "AgentU"), "atkyx749"),
    (("angle749", "keyboard"), "krems749"),
    (("angle749", "AA"), "angle749"),
    (("universe749", "key"), "ergfipci749"),
    (("universe749", "lemon"), "frujrcwq749"),
    (("universe749", "a"), "universe749"),
    (("universe749", "zz"), "tmhudqrd749"),
    (("universe749", "AgentU"), "utmixlsk749"),
    (("universe749", "keyboard"), "ergwsrjh749"),
    (("universe749", "AA"), "universe749"),
    (("memory749", "key"), "wikyvw749"),
    (("memory749", "lemon"), "xiycej749"),
    (("memory749", "a"), "memory749"),
    (("memory749", "zz"), "ldlnqx749"),
    (("memory749", "AgentU"), "mkqbks749"),
    (("memory749", "keyboard"), "wikpfy749"),
    (("memory749", "AA"), "memory749"),
    (("stream749", "key"), "cxpoek749"),
    (("stream749", "lemon"), "dxdsnx749"),
    (("stream749", "a"), "stream749"),
    (("stream749", "zz"), "rsqdzl749"),
    (("stream749", "AgentU"), "szvrtg749"),
    (("stream749", "keyboard"), "cxpfom749"),
    (("stream749", "AA"), "stream749"),
    (("context749", "key"), "msldivd749"),
    (("context749", "lemon"), "nszhrix749"),
    (("context749", "a"), "context749"),
    (("context749", "zz"), "bnmsdws749"),
    (("context749", "AgentU"), "curgxrt749"),
    (("context749", "keyboard"), "mslusxk749"),
    (("context749", "AA"), "context749"),
    (("knowledge749", "key"), "urmgpcnkc749"),
    (("knowledge749", "lemon"), "vrakyphss749"),
    (("knowledge749", "a"), "knowledge749"),
    (("knowledge749", "zz"), "jmnvkdcfd749"),
    (("knowledge749", "AgentU"), "ktsjeydmi749"),
    (("knowledge749", "keyboard"), "urmxzeujo749"),
    (("knowledge749", "AA"), "knowledge749"),
    (("vector749", "key"), "fiadsp749"),
    (("vector749", "lemon"), "giohbc749"),
    (("vector749", "a"), "vector749"),
    (("vector749", "zz"), "udbsnq749"),
    (("vector749", "AgentU"), "vkgghl749"),
    (("vector749", "keyboard"), "fiaucr749"),
    (("vector749", "AA"), "vector749"),
    (("processor749", "key"), "zvmmiqcsp749"),
    (("processor749", "lemon"), "avaqrdwaf749"),
    (("processor749", "a"), "processor749"),
    (("processor749", "zz"), "oqnbdrrnq749"),
    (("processor749", "AgentU"), "pxspxmsuv749"),
    (("processor749", "keyboard"), "zvmdssjrb749"),
    (("processor749", "AA"), "processor749"),
    (("reasoning749", "key"), "biycslsre749"),
    (("reasoning749", "lemon"), "cimgbymzu749"),
    (("reasoning749", "a"), "reasoning749"),
    (("reasoning749", "zz"), "qdzrnmhmf749"),
    (("reasoning749", "AgentU"), "rkefhhitk749"),
    (("reasoning749", "keyboard"), "biytcnzqq749"),
    (("reasoning749", "AA"), "reasoning749"),
    (("machine749", "key"), "wearmlo749"),
    (("machine749", "lemon"), "xeovvyi749"),
    (("machine749", "a"), "machine749"),
    (("machine749", "zz"), "lzbghmd749"),
    (("machine749", "AgentU"), "mggubhe749"),
    (("machine749", "keyboard"), "weaiwnv749"),
    (("machine749", "AA"), "machine749"),
    (("learning749", "key"), "viybrgxk749"),
    (("learning749", "lemon"), "wimfatrs749"),
    (("learning749", "a"), "learning749"),
    (("learning749", "zz"), "kdzqmhmf749"),
    (("learning749", "AgentU"), "lkeegcnm749"),
    (("learning749", "keyboard"), "viysbiej749"),
    (("learning749", "AA"), "learning749"),
    (("model749", "key"), "wsbop749"),
    (("model749", "lemon"), "xspsy749"),
    (("model749", "a"), "model749"),
    (("model749", "zz"), "lncdk749"),
    (("model749", "AgentU"), "muhre749"),
    (("model749", "keyboard"), "wsbfz749"),
    (("model749", "AA"), "model749"),
    (("token749", "key"), "dsior749"),
    (("token749", "lemon"), "eswsa749"),
    (("token749", "a"), "token749"),
    (("token749", "zz"), "snjdm749"),
    (("token749", "AgentU"), "tuorg749"),
    (("token749", "keyboard"), "dsifb749"),
    (("token749", "AA"), "token749"),
    (("prompt749", "key"), "zvmwtr749"),
    (("prompt749", "lemon"), "avaace749"),
    (("prompt749", "a"), "prompt749"),
    (("prompt749", "zz"), "oqnlos749"),
    (("prompt749", "AgentU"), "pxszin749"),
    (("prompt749", "keyboard"), "zvmndt749"),
    (("prompt749", "AA"), "prompt749"),
    (("session749", "key"), "ciqcmmx749"),
    (("session749", "lemon"), "diegvzr749"),
    (("session749", "a"), "session749"),
    (("session749", "zz"), "rdrrhnm749"),
    (("session749", "AgentU"), "skwfbin749"),
    (("session749", "keyboard"), "ciqtwoe749"),
    (("session749", "AA"), "session749"),
    (("library749", "key"), "vmzbepi749"),
    (("library749", "lemon"), "wmnfncc749"),
    (("library749", "a"), "library749"),
    (("library749", "zz"), "khaqzqx749"),
    (("library749", "AgentU"), "lofetly749"),
    (("library749", "keyboard"), "vmzsorp749"),
    (("library749", "AA"), "library749"),
    (("service749", "key"), "cipfmao749"),
    (("service749", "lemon"), "didjvni749"),
    (("service749", "a"), "service749"),
    (("service749", "zz"), "rdquhbd749"),
    (("service749", "AgentU"), "skvibwe749"),
    (("service749", "keyboard"), "cipwwcv749"),
    (("service749", "AA"), "service749"),
    (("gateway749", "key"), "qeroayi749"),
    (("gateway749", "lemon"), "refsjlc749"),
    (("gateway749", "a"), "gateway749"),
    (("gateway749", "zz"), "fzsdvzx749"),
    (("gateway749", "AgentU"), "ggxrpuy749"),
    (("gateway749", "keyboard"), "qerfkap749"),
    (("gateway749", "AA"), "gateway749"),
    (("storage749", "key"), "cxmbeeo749"),
    (("storage749", "lemon"), "dxafnri749"),
    (("storage749", "a"), "storage749"),
    (("storage749", "zz"), "rsnqzfd749"),
    (("storage749", "AgentU"), "szsetae749"),
    (("storage749", "keyboard"), "cxmsogv749"),
    (("storage749", "AA"), "storage749"),
    (("network749", "key"), "xirgspu749"),
    (("network749", "lemon"), "yifkbco749"),
    (("network749", "a"), "network749"),
    (("network749", "zz"), "mdsvnqj749"),
    (("network749", "AgentU"), "nkxjhlk749"),
    (("network749", "keyboard"), "xirxcrb749"),
    (("network749", "AA"), "network749"),
    (("latency749", "key"), "verorai749"),
    (("latency749", "lemon"), "wefsanc749"),
    (("latency749", "a"), "latency749"),
    (("latency749", "zz"), "kzsdmbx749"),
    (("latency749", "AgentU"), "lgxrgwy749"),
    (("latency749", "keyboard"), "verfbcp749"),
    (("latency749", "AA"), "latency749"),
    (("buffer749", "key"), "lydpip749"),
    (("buffer749", "lemon"), "myrtrc749"),
    (("buffer749", "a"), "buffer749"),
    (("buffer749", "zz"), "ateedq749"),
    (("buffer749", "AgentU"), "bajsxl749"),
    (("buffer749", "keyboard"), "lydgsr749"),
    (("buffer749", "AA"), "buffer749"),
    (("queue749", "key"), "aycei749"),
    (("queue749", "lemon"), "byqir749"),
    (("queue749", "a"), "queue749"),
    (("queue749", "zz"), "ptdtd749"),
    (("queue749", "AgentU"), "qaihx749"),
    (("queue749", "keyboard"), "aycvs749"),
    (("queue749", "AA"), "queue749"),
    (("worker749", "key"), "gspuip749"),
    (("worker749", "lemon"), "hsdyrc749"),
    (("worker749", "a"), "worker749"),
    (("worker749", "zz"), "vnqjdq749"),
    (("worker749", "AgentU"), "wuvxxl749"),
    (("worker749", "keyboard"), "gsplsr749"),
    (("worker749", "AA"), "worker749"),
    (("kernel749", "key"), "uipxij749"),
    (("kernel749", "lemon"), "vidbrw749"),
    (("kernel749", "a"), "kernel749"),
    (("kernel749", "zz"), "jdqmdk749"),
    (("kernel749", "AgentU"), "kkvaxf749"),
    (("kernel749", "keyboard"), "uiposl749"),
    (("kernel749", "AA"), "kernel749"),
    (("signal749", "key"), "cmexej749"),
    (("signal749", "lemon"), "dmsbnw749"),
    (("signal749", "a"), "signal749"),
    (("signal749", "zz"), "rhfmzk749"),
    (("signal749", "AgentU"), "sokatf749"),
    (("signal749", "keyboard"), "cmeool749"),
    (("signal749", "AA"), "signal749"),
    (("packet749", "key"), "zeauir749"),
    (("packet749", "lemon"), "aeoyre749"),
    (("packet749", "a"), "packet749"),
    (("packet749", "zz"), "ozbjds749"),
    (("packet749", "AgentU"), "pggxxn749"),
    (("packet749", "keyboard"), "zealst749"),
    (("packet749", "AA"), "packet749"),
    (("router749", "key"), "bssdip749"),
    (("router749", "lemon"), "csghrc749"),
    (("router749", "a"), "router749"),
    (("router749", "zz"), "qntsdq749"),
    (("router749", "AgentU"), "ruygxl749"),
    (("router749", "keyboard"), "bssusr749"),
    (("router749", "AA"), "router749"),
    (("cluster749", "key"), "mpscxcb749"),
    (("cluster749", "lemon"), "npgggpv749"),
    (("cluster749", "a"), "cluster749"),
    (("cluster749", "zz"), "bktrsdq749"),
    (("cluster749", "AgentU"), "cryfmyr749"),
    (("cluster749", "keyboard"), "mpsthei749"),
    (("cluster749", "AA"), "cluster749"),
    (("mirror749", "key"), "wmpbsp749"),
    (("mirror749", "lemon"), "xmdfbc749"),
    (("mirror749", "a"), "mirror749"),
    (("mirror749", "zz"), "lhqqnq749"),
    (("mirror749", "AgentU"), "movehl749"),
    (("mirror749", "keyboard"), "wmpscr749"),
    (("mirror749", "AA"), "mirror749"),
    (("filter749", "key"), "pmjdip749"),
    (("filter749", "lemon"), "qmxhrc749"),
    (("filter749", "a"), "filter749"),
    (("filter749", "zz"), "ehksdq749"),
    (("filter749", "AgentU"), "fopgxl749"),
    (("filter749", "keyboard"), "pmjusr749"),
    (("filter749", "AA"), "filter749"),
    (("ranking749", "key"), "belumlq749"),
    (("ranking749", "lemon"), "cezyvyk749"),
    (("ranking749", "a"), "ranking749"),
    (("ranking749", "zz"), "qzmjhmf749"),
    (("ranking749", "AgentU"), "rgrxbhg749"),
    (("ranking749", "keyboard"), "bellwnx749"),
    (("ranking749", "AA"), "ranking749"),
    (("encoding749", "key"), "orayhgxk749"),
    (("encoding749", "lemon"), "procqtrs749"),
    (("encoding749", "a"), "encoding749"),
    (("encoding749", "zz"), "dmbnchmf749"),
    (("encoding749", "AgentU"), "etgbwcnm749"),
    (("encoding749", "keyboard"), "orapriej749"),
    (("encoding749", "AA"), "encoding749"),
    (("mapping749", "key"), "wenzmlq749"),
    (("mapping749", "lemon"), "xebdvyk749"),
    (("mapping749", "a"), "mapping749"),
    (("mapping749", "zz"), "lzoohmf749"),
    (("mapping749", "AgentU"), "mgtcbhg749"),
    (("mapping749", "keyboard"), "wenqwnx749"),
    (("mapping749", "AA"), "mapping749"),
    (("record749", "key"), "biayvb749"),
    (("record749", "lemon"), "cioceo749"),
    (("record749", "a"), "record749"),
    (("record749", "zz"), "qdbnqc749"),
    (("record749", "AgentU"), "rkgbkx749"),
    (("record749", "keyboard"), "biapfd749"),
    (("record749", "AA"), "record749"),
    (("candle749", "key"), "melnpc749"),
    (("candle749", "lemon"), "nezryp749"),
    (("candle749", "a"), "candle749"),
    (("candle749", "zz"), "bzmckd749"),
    (("candle749", "AgentU"), "cgrqey749"),
    (("candle749", "keyboard"), "meleze749"),
    (("candle749", "AA"), "candle749"),
    (("thread749", "key"), "dlpoeb749"),
    (("thread749", "lemon"), "eldsno749"),
    (("thread749", "a"), "thread749"),
    (("thread749", "zz"), "sgqdzc749"),
    (("thread749", "AgentU"), "tnvrtx749"),
    (("thread749", "keyboard"), "dlpfod749"),
    (("thread749", "AA"), "thread749"),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 749: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 749: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "a"),
        "round 749: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 749: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 749: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 749: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", "AA"),
        "round 749: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "key"),
        "bssxh 749: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 749: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "a"),
        "round 749: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 749: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 749: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 749: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", "AA"),
        "round 749: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 749: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 749: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "a"),
        "round 749: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 749: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 749: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 749: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", "AA"),
        "round 749: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 749: the processor reads the record then stops", "key"),
        "bssxh 749: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 749: the processor reads the record then stops", "lemon"),
        "csgbq 749: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 749: the processor reads the record then stops", "a"),
        "round 749: the processor reads the record then stops",
    ),
    (
        ("round 749: the processor reads the record then stops", "zz"),
        "qntmc 749: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 749: the processor reads the record then stops", "AgentU"),
        "ruyaw 749: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 749: the processor reads the record then stops", "keyboard"),
        "bssor 749: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 749: the processor reads the record then stops", "AA"),
        "round 749: the processor reads the record then stops",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "key"),
        "bssxh 749: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "lemon"),
        "csgbq 749: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "a"),
        "round 749: a worker pulls the next task from the queue",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "zz"),
        "qntmc 749: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 749: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "keyboard"),
        "bssor 749: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 749: a worker pulls the next task from the queue", "AA"),
        "round 749: a worker pulls the next task from the queue",
    ),
    (
        ("round 749: signals travel through the network layer", "key"),
        "bssxh 749: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 749: signals travel through the network layer", "lemon"),
        "csgbq 749: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 749: signals travel through the network layer", "a"),
        "round 749: signals travel through the network layer",
    ),
    (
        ("round 749: signals travel through the network layer", "zz"),
        "qntmc 749: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 749: signals travel through the network layer", "AgentU"),
        "ruyaw 749: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 749: signals travel through the network layer", "keyboard"),
        "bssor 749: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 749: signals travel through the network layer", "AA"),
        "round 749: signals travel through the network layer",
    ),
    (
        ("round 749: the gateway routes each request by policy", "key"),
        "bssxh 749: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 749: the gateway routes each request by policy", "lemon"),
        "csgbq 749: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 749: the gateway routes each request by policy", "a"),
        "round 749: the gateway routes each request by policy",
    ),
    (
        ("round 749: the gateway routes each request by policy", "zz"),
        "qntmc 749: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 749: the gateway routes each request by policy", "AgentU"),
        "ruyaw 749: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 749: the gateway routes each request by policy", "keyboard"),
        "bssor 749: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 749: the gateway routes each request by policy", "AA"),
        "round 749: the gateway routes each request by policy",
    ),
    (("round 749: memory grows until the buffer is full", "key"), "bssxh 749: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 749: memory grows until the buffer is full", "lemon"), "csgbq 749: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 749: memory grows until the buffer is full", "a"), "round 749: memory grows until the buffer is full"),
    (("round 749: memory grows until the buffer is full", "zz"), "qntmc 749: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 749: memory grows until the buffer is full", "AgentU"),
        "ruyaw 749: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 749: memory grows until the buffer is full", "keyboard"),
        "bssor 749: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 749: memory grows until the buffer is full", "AA"), "round 749: memory grows until the buffer is full"),
    (("round 749: the cluster mirrors every packet twice", "key"), "bssxh 749: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 749: the cluster mirrors every packet twice", "lemon"),
        "csgbq 749: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 749: the cluster mirrors every packet twice", "a"), "round 749: the cluster mirrors every packet twice"),
    (("round 749: the cluster mirrors every packet twice", "zz"), "qntmc 749: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 749: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 749: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 749: the cluster mirrors every packet twice", "keyboard"),
        "bssor 749: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 749: the cluster mirrors every packet twice", "AA"), "round 749: the cluster mirrors every packet twice"),
    (
        ("round 749: ranking uses tokens learned from the corpus", "key"),
        "bssxh 749: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 749: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", "a"),
        "round 749: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 749: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 749: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 749: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", "AA"),
        "round 749: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 749: a long session ends when the candle dies", "key"),
        "bssxh 749: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 749: a long session ends when the candle dies", "lemon"),
        "csgbq 749: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 749: a long session ends when the candle dies", "a"),
        "round 749: a long session ends when the candle dies",
    ),
    (
        ("round 749: a long session ends when the candle dies", "zz"),
        "qntmc 749: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 749: a long session ends when the candle dies", "AgentU"),
        "ruyaw 749: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 749: a long session ends when the candle dies", "keyboard"),
        "bssor 749: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 749: a long session ends when the candle dies", "AA"),
        "round 749: a long session ends when the candle dies",
    ),
    (("round 749: encode the prompt then map the result", "key"), "bssxh 749: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 749: encode the prompt then map the result", "lemon"), "csgbq 749: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 749: encode the prompt then map the result", "a"), "round 749: encode the prompt then map the result"),
    (("round 749: encode the prompt then map the result", "zz"), "qntmc 749: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 749: encode the prompt then map the result", "AgentU"),
        "ruyaw 749: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 749: encode the prompt then map the result", "keyboard"),
        "bssor 749: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 749: encode the prompt then map the result", "AA"), "round 749: encode the prompt then map the result"),
    (("round 749: the kernel wakes the worker at dawn", "key"), "bssxh 749: rri iovlop ukocc xfo ambocb er neux"),
    (("round 749: the kernel wakes the worker at dawn", "lemon"), "csgbq 749: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 749: the kernel wakes the worker at dawn", "a"), "round 749: the kernel wakes the worker at dawn"),
    (("round 749: the kernel wakes the worker at dawn", "zz"), "qntmc 749: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 749: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 749: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 749: the kernel wakes the worker at dawn", "keyboard"), "bssor 749: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 749: the kernel wakes the worker at dawn", "AA"), "round 749: the kernel wakes the worker at dawn"),
    (("round 749: service latency drops after the patch", "key"), "bssxh 749: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 749: service latency drops after the patch", "lemon"), "csgbq 749: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 749: service latency drops after the patch", "a"), "round 749: service latency drops after the patch"),
    (("round 749: service latency drops after the patch", "zz"), "qntmc 749: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 749: service latency drops after the patch", "AgentU"),
        "ruyaw 749: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 749: service latency drops after the patch", "keyboard"),
        "bssor 749: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 749: service latency drops after the patch", "AA"), "round 749: service latency drops after the patch"),
    (
        ("round 749: the library caches every vector it sees", "key"),
        "bssxh 749: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 749: the library caches every vector it sees", "lemon"),
        "csgbq 749: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 749: the library caches every vector it sees", "a"), "round 749: the library caches every vector it sees"),
    (
        ("round 749: the library caches every vector it sees", "zz"),
        "qntmc 749: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 749: the library caches every vector it sees", "AgentU"),
        "ruyaw 749: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 749: the library caches every vector it sees", "keyboard"),
        "bssor 749: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 749: the library caches every vector it sees", "AA"),
        "round 749: the library caches every vector it sees",
    ),
    (("round 749: agents argue then the debate resolves", "key"), "bssxh 749: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 749: agents argue then the debate resolves", "lemon"), "csgbq 749: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 749: agents argue then the debate resolves", "a"), "round 749: agents argue then the debate resolves"),
    (("round 749: agents argue then the debate resolves", "zz"), "qntmc 749: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 749: agents argue then the debate resolves", "AgentU"),
        "ruyaw 749: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 749: agents argue then the debate resolves", "keyboard"),
        "bssor 749: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 749: agents argue then the debate resolves", "AA"), "round 749: agents argue then the debate resolves"),
    (("round 749: the filter keeps only strong matches", "key"), "bssxh 749: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 749: the filter keeps only strong matches", "lemon"), "csgbq 749: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 749: the filter keeps only strong matches", "a"), "round 749: the filter keeps only strong matches"),
    (("round 749: the filter keeps only strong matches", "zz"), "qntmc 749: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 749: the filter keeps only strong matches", "AgentU"), "ruyaw 749: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 749: the filter keeps only strong matches", "keyboard"),
        "bssor 749: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 749: the filter keeps only strong matches", "AA"), "round 749: the filter keeps only strong matches"),
    (("round 749: the model answers with a short reply", "key"), "bssxh 749: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 749: the model answers with a short reply", "lemon"), "csgbq 749: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 749: the model answers with a short reply", "a"), "round 749: the model answers with a short reply"),
    (("round 749: the model answers with a short reply", "zz"), "qntmc 749: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 749: the model answers with a short reply", "AgentU"), "ruyaw 749: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 749: the model answers with a short reply", "keyboard"),
        "bssor 749: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 749: the model answers with a short reply", "AA"), "round 749: the model answers with a short reply"),
    (
        ("round 749: the recorder stores the reasoning trace", "key"),
        "bssxh 749: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 749: the recorder stores the reasoning trace", "lemon"),
        "csgbq 749: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 749: the recorder stores the reasoning trace", "a"), "round 749: the recorder stores the reasoning trace"),
    (
        ("round 749: the recorder stores the reasoning trace", "zz"),
        "qntmc 749: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 749: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 749: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 749: the recorder stores the reasoning trace", "keyboard"),
        "bssor 749: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 749: the recorder stores the reasoning trace", "AA"),
        "round 749: the recorder stores the reasoning trace",
    ),
    (("round 749: the angel watches the processor run", "key"), "bssxh 749: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 749: the angel watches the processor run", "lemon"), "csgbq 749: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 749: the angel watches the processor run", "a"), "round 749: the angel watches the processor run"),
    (("round 749: the angel watches the processor run", "zz"), "qntmc 749: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 749: the angel watches the processor run", "AgentU"), "ruyaw 749: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 749: the angel watches the processor run", "keyboard"), "bssor 749: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 749: the angel watches the processor run", "AA"), "round 749: the angel watches the processor run"),
    (("round 749: angle of the vector decides the match", "key"), "bssxh 749: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 749: angle of the vector decides the match", "lemon"), "csgbq 749: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 749: angle of the vector decides the match", "a"), "round 749: angle of the vector decides the match"),
    (("round 749: angle of the vector decides the match", "zz"), "qntmc 749: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 749: angle of the vector decides the match", "AgentU"),
        "ruyaw 749: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 749: angle of the vector decides the match", "keyboard"),
        "bssor 749: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 749: angle of the vector decides the match", "AA"), "round 749: angle of the vector decides the match"),
    (
        ("round 749: the candle burns twice as long at night", "key"),
        "bssxh 749: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 749: the candle burns twice as long at night", "lemon"),
        "csgbq 749: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 749: the candle burns twice as long at night", "a"), "round 749: the candle burns twice as long at night"),
    (
        ("round 749: the candle burns twice as long at night", "zz"),
        "qntmc 749: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 749: the candle burns twice as long at night", "AgentU"),
        "ruyaw 749: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 749: the candle burns twice as long at night", "keyboard"),
        "bssor 749: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 749: the candle burns twice as long at night", "AA"),
        "round 749: the candle burns twice as long at night",
    ),
    (("round 749: a mirror of the universe in one line", "key"), "bssxh 749: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 749: a mirror of the universe in one line", "lemon"), "csgbq 749: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 749: a mirror of the universe in one line", "a"), "round 749: a mirror of the universe in one line"),
    (("round 749: a mirror of the universe in one line", "zz"), "qntmc 749: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 749: a mirror of the universe in one line", "AgentU"), "ruyaw 749: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 749: a mirror of the universe in one line", "keyboard"),
        "bssor 749: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 749: a mirror of the universe in one line", "AA"), "round 749: a mirror of the universe in one line"),
    (("round 749: the queue drains before the storm", "key"), "bssxh 749: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 749: the queue drains before the storm", "lemon"), "csgbq 749: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 749: the queue drains before the storm", "a"), "round 749: the queue drains before the storm"),
    (("round 749: the queue drains before the storm", "zz"), "qntmc 749: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 749: the queue drains before the storm", "AgentU"), "ruyaw 749: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 749: the queue drains before the storm", "keyboard"), "bssor 749: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 749: the queue drains before the storm", "AA"), "round 749: the queue drains before the storm"),
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
