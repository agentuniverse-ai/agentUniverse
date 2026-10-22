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
    (("kitten147", "key"), "umrdil147"),
    (("kitten147", "lemon"), "vmfhry147"),
    (("kitten147", "a"), "kitten147"),
    (("kitten147", "zz"), "jhssdm147"),
    (("kitten147", "AgentU"), "koxgxh147"),
    (("kitten147", "keyboard"), "umrusn147"),
    (("kitten147", "AA"), "kitten147"),
    (("sitting147", "key"), "cmrdmlq147"),
    (("sitting147", "lemon"), "dmfhvyk147"),
    (("sitting147", "a"), "sitting147"),
    (("sitting147", "zz"), "rhsshmf147"),
    (("sitting147", "AgentU"), "soxgbhg147"),
    (("sitting147", "keyboard"), "cmruwnx147"),
    (("sitting147", "AA"), "sitting147"),
    (("agent147", "key"), "kkcxx147"),
    (("agent147", "lemon"), "lkqbg147"),
    (("agent147", "a"), "agent147"),
    (("agent147", "zz"), "zfdms147"),
    (("agent147", "AgentU"), "amiam147"),
    (("agent147", "keyboard"), "kkcoh147"),
    (("agent147", "AA"), "agent147"),
    (("angle147", "key"), "krevi147"),
    (("angle147", "lemon"), "lrszr147"),
    (("angle147", "a"), "angle147"),
    (("angle147", "zz"), "zmfkd147"),
    (("angle147", "AgentU"), "atkyx147"),
    (("angle147", "keyboard"), "krems147"),
    (("angle147", "AA"), "angle147"),
    (("universe147", "key"), "ergfipci147"),
    (("universe147", "lemon"), "frujrcwq147"),
    (("universe147", "a"), "universe147"),
    (("universe147", "zz"), "tmhudqrd147"),
    (("universe147", "AgentU"), "utmixlsk147"),
    (("universe147", "keyboard"), "ergwsrjh147"),
    (("universe147", "AA"), "universe147"),
    (("memory147", "key"), "wikyvw147"),
    (("memory147", "lemon"), "xiycej147"),
    (("memory147", "a"), "memory147"),
    (("memory147", "zz"), "ldlnqx147"),
    (("memory147", "AgentU"), "mkqbks147"),
    (("memory147", "keyboard"), "wikpfy147"),
    (("memory147", "AA"), "memory147"),
    (("stream147", "key"), "cxpoek147"),
    (("stream147", "lemon"), "dxdsnx147"),
    (("stream147", "a"), "stream147"),
    (("stream147", "zz"), "rsqdzl147"),
    (("stream147", "AgentU"), "szvrtg147"),
    (("stream147", "keyboard"), "cxpfom147"),
    (("stream147", "AA"), "stream147"),
    (("context147", "key"), "msldivd147"),
    (("context147", "lemon"), "nszhrix147"),
    (("context147", "a"), "context147"),
    (("context147", "zz"), "bnmsdws147"),
    (("context147", "AgentU"), "curgxrt147"),
    (("context147", "keyboard"), "mslusxk147"),
    (("context147", "AA"), "context147"),
    (("knowledge147", "key"), "urmgpcnkc147"),
    (("knowledge147", "lemon"), "vrakyphss147"),
    (("knowledge147", "a"), "knowledge147"),
    (("knowledge147", "zz"), "jmnvkdcfd147"),
    (("knowledge147", "AgentU"), "ktsjeydmi147"),
    (("knowledge147", "keyboard"), "urmxzeujo147"),
    (("knowledge147", "AA"), "knowledge147"),
    (("vector147", "key"), "fiadsp147"),
    (("vector147", "lemon"), "giohbc147"),
    (("vector147", "a"), "vector147"),
    (("vector147", "zz"), "udbsnq147"),
    (("vector147", "AgentU"), "vkgghl147"),
    (("vector147", "keyboard"), "fiaucr147"),
    (("vector147", "AA"), "vector147"),
    (("processor147", "key"), "zvmmiqcsp147"),
    (("processor147", "lemon"), "avaqrdwaf147"),
    (("processor147", "a"), "processor147"),
    (("processor147", "zz"), "oqnbdrrnq147"),
    (("processor147", "AgentU"), "pxspxmsuv147"),
    (("processor147", "keyboard"), "zvmdssjrb147"),
    (("processor147", "AA"), "processor147"),
    (("reasoning147", "key"), "biycslsre147"),
    (("reasoning147", "lemon"), "cimgbymzu147"),
    (("reasoning147", "a"), "reasoning147"),
    (("reasoning147", "zz"), "qdzrnmhmf147"),
    (("reasoning147", "AgentU"), "rkefhhitk147"),
    (("reasoning147", "keyboard"), "biytcnzqq147"),
    (("reasoning147", "AA"), "reasoning147"),
    (("machine147", "key"), "wearmlo147"),
    (("machine147", "lemon"), "xeovvyi147"),
    (("machine147", "a"), "machine147"),
    (("machine147", "zz"), "lzbghmd147"),
    (("machine147", "AgentU"), "mggubhe147"),
    (("machine147", "keyboard"), "weaiwnv147"),
    (("machine147", "AA"), "machine147"),
    (("learning147", "key"), "viybrgxk147"),
    (("learning147", "lemon"), "wimfatrs147"),
    (("learning147", "a"), "learning147"),
    (("learning147", "zz"), "kdzqmhmf147"),
    (("learning147", "AgentU"), "lkeegcnm147"),
    (("learning147", "keyboard"), "viysbiej147"),
    (("learning147", "AA"), "learning147"),
    (("model147", "key"), "wsbop147"),
    (("model147", "lemon"), "xspsy147"),
    (("model147", "a"), "model147"),
    (("model147", "zz"), "lncdk147"),
    (("model147", "AgentU"), "muhre147"),
    (("model147", "keyboard"), "wsbfz147"),
    (("model147", "AA"), "model147"),
    (("token147", "key"), "dsior147"),
    (("token147", "lemon"), "eswsa147"),
    (("token147", "a"), "token147"),
    (("token147", "zz"), "snjdm147"),
    (("token147", "AgentU"), "tuorg147"),
    (("token147", "keyboard"), "dsifb147"),
    (("token147", "AA"), "token147"),
    (("prompt147", "key"), "zvmwtr147"),
    (("prompt147", "lemon"), "avaace147"),
    (("prompt147", "a"), "prompt147"),
    (("prompt147", "zz"), "oqnlos147"),
    (("prompt147", "AgentU"), "pxszin147"),
    (("prompt147", "keyboard"), "zvmndt147"),
    (("prompt147", "AA"), "prompt147"),
    (("session147", "key"), "ciqcmmx147"),
    (("session147", "lemon"), "diegvzr147"),
    (("session147", "a"), "session147"),
    (("session147", "zz"), "rdrrhnm147"),
    (("session147", "AgentU"), "skwfbin147"),
    (("session147", "keyboard"), "ciqtwoe147"),
    (("session147", "AA"), "session147"),
    (("library147", "key"), "vmzbepi147"),
    (("library147", "lemon"), "wmnfncc147"),
    (("library147", "a"), "library147"),
    (("library147", "zz"), "khaqzqx147"),
    (("library147", "AgentU"), "lofetly147"),
    (("library147", "keyboard"), "vmzsorp147"),
    (("library147", "AA"), "library147"),
    (("service147", "key"), "cipfmao147"),
    (("service147", "lemon"), "didjvni147"),
    (("service147", "a"), "service147"),
    (("service147", "zz"), "rdquhbd147"),
    (("service147", "AgentU"), "skvibwe147"),
    (("service147", "keyboard"), "cipwwcv147"),
    (("service147", "AA"), "service147"),
    (("gateway147", "key"), "qeroayi147"),
    (("gateway147", "lemon"), "refsjlc147"),
    (("gateway147", "a"), "gateway147"),
    (("gateway147", "zz"), "fzsdvzx147"),
    (("gateway147", "AgentU"), "ggxrpuy147"),
    (("gateway147", "keyboard"), "qerfkap147"),
    (("gateway147", "AA"), "gateway147"),
    (("storage147", "key"), "cxmbeeo147"),
    (("storage147", "lemon"), "dxafnri147"),
    (("storage147", "a"), "storage147"),
    (("storage147", "zz"), "rsnqzfd147"),
    (("storage147", "AgentU"), "szsetae147"),
    (("storage147", "keyboard"), "cxmsogv147"),
    (("storage147", "AA"), "storage147"),
    (("network147", "key"), "xirgspu147"),
    (("network147", "lemon"), "yifkbco147"),
    (("network147", "a"), "network147"),
    (("network147", "zz"), "mdsvnqj147"),
    (("network147", "AgentU"), "nkxjhlk147"),
    (("network147", "keyboard"), "xirxcrb147"),
    (("network147", "AA"), "network147"),
    (("latency147", "key"), "verorai147"),
    (("latency147", "lemon"), "wefsanc147"),
    (("latency147", "a"), "latency147"),
    (("latency147", "zz"), "kzsdmbx147"),
    (("latency147", "AgentU"), "lgxrgwy147"),
    (("latency147", "keyboard"), "verfbcp147"),
    (("latency147", "AA"), "latency147"),
    (("buffer147", "key"), "lydpip147"),
    (("buffer147", "lemon"), "myrtrc147"),
    (("buffer147", "a"), "buffer147"),
    (("buffer147", "zz"), "ateedq147"),
    (("buffer147", "AgentU"), "bajsxl147"),
    (("buffer147", "keyboard"), "lydgsr147"),
    (("buffer147", "AA"), "buffer147"),
    (("queue147", "key"), "aycei147"),
    (("queue147", "lemon"), "byqir147"),
    (("queue147", "a"), "queue147"),
    (("queue147", "zz"), "ptdtd147"),
    (("queue147", "AgentU"), "qaihx147"),
    (("queue147", "keyboard"), "aycvs147"),
    (("queue147", "AA"), "queue147"),
    (("worker147", "key"), "gspuip147"),
    (("worker147", "lemon"), "hsdyrc147"),
    (("worker147", "a"), "worker147"),
    (("worker147", "zz"), "vnqjdq147"),
    (("worker147", "AgentU"), "wuvxxl147"),
    (("worker147", "keyboard"), "gsplsr147"),
    (("worker147", "AA"), "worker147"),
    (("kernel147", "key"), "uipxij147"),
    (("kernel147", "lemon"), "vidbrw147"),
    (("kernel147", "a"), "kernel147"),
    (("kernel147", "zz"), "jdqmdk147"),
    (("kernel147", "AgentU"), "kkvaxf147"),
    (("kernel147", "keyboard"), "uiposl147"),
    (("kernel147", "AA"), "kernel147"),
    (("signal147", "key"), "cmexej147"),
    (("signal147", "lemon"), "dmsbnw147"),
    (("signal147", "a"), "signal147"),
    (("signal147", "zz"), "rhfmzk147"),
    (("signal147", "AgentU"), "sokatf147"),
    (("signal147", "keyboard"), "cmeool147"),
    (("signal147", "AA"), "signal147"),
    (("packet147", "key"), "zeauir147"),
    (("packet147", "lemon"), "aeoyre147"),
    (("packet147", "a"), "packet147"),
    (("packet147", "zz"), "ozbjds147"),
    (("packet147", "AgentU"), "pggxxn147"),
    (("packet147", "keyboard"), "zealst147"),
    (("packet147", "AA"), "packet147"),
    (("router147", "key"), "bssdip147"),
    (("router147", "lemon"), "csghrc147"),
    (("router147", "a"), "router147"),
    (("router147", "zz"), "qntsdq147"),
    (("router147", "AgentU"), "ruygxl147"),
    (("router147", "keyboard"), "bssusr147"),
    (("router147", "AA"), "router147"),
    (("cluster147", "key"), "mpscxcb147"),
    (("cluster147", "lemon"), "npgggpv147"),
    (("cluster147", "a"), "cluster147"),
    (("cluster147", "zz"), "bktrsdq147"),
    (("cluster147", "AgentU"), "cryfmyr147"),
    (("cluster147", "keyboard"), "mpsthei147"),
    (("cluster147", "AA"), "cluster147"),
    (("mirror147", "key"), "wmpbsp147"),
    (("mirror147", "lemon"), "xmdfbc147"),
    (("mirror147", "a"), "mirror147"),
    (("mirror147", "zz"), "lhqqnq147"),
    (("mirror147", "AgentU"), "movehl147"),
    (("mirror147", "keyboard"), "wmpscr147"),
    (("mirror147", "AA"), "mirror147"),
    (("filter147", "key"), "pmjdip147"),
    (("filter147", "lemon"), "qmxhrc147"),
    (("filter147", "a"), "filter147"),
    (("filter147", "zz"), "ehksdq147"),
    (("filter147", "AgentU"), "fopgxl147"),
    (("filter147", "keyboard"), "pmjusr147"),
    (("filter147", "AA"), "filter147"),
    (("ranking147", "key"), "belumlq147"),
    (("ranking147", "lemon"), "cezyvyk147"),
    (("ranking147", "a"), "ranking147"),
    (("ranking147", "zz"), "qzmjhmf147"),
    (("ranking147", "AgentU"), "rgrxbhg147"),
    (("ranking147", "keyboard"), "bellwnx147"),
    (("ranking147", "AA"), "ranking147"),
    (("encoding147", "key"), "orayhgxk147"),
    (("encoding147", "lemon"), "procqtrs147"),
    (("encoding147", "a"), "encoding147"),
    (("encoding147", "zz"), "dmbnchmf147"),
    (("encoding147", "AgentU"), "etgbwcnm147"),
    (("encoding147", "keyboard"), "orapriej147"),
    (("encoding147", "AA"), "encoding147"),
    (("mapping147", "key"), "wenzmlq147"),
    (("mapping147", "lemon"), "xebdvyk147"),
    (("mapping147", "a"), "mapping147"),
    (("mapping147", "zz"), "lzoohmf147"),
    (("mapping147", "AgentU"), "mgtcbhg147"),
    (("mapping147", "keyboard"), "wenqwnx147"),
    (("mapping147", "AA"), "mapping147"),
    (("record147", "key"), "biayvb147"),
    (("record147", "lemon"), "cioceo147"),
    (("record147", "a"), "record147"),
    (("record147", "zz"), "qdbnqc147"),
    (("record147", "AgentU"), "rkgbkx147"),
    (("record147", "keyboard"), "biapfd147"),
    (("record147", "AA"), "record147"),
    (("candle147", "key"), "melnpc147"),
    (("candle147", "lemon"), "nezryp147"),
    (("candle147", "a"), "candle147"),
    (("candle147", "zz"), "bzmckd147"),
    (("candle147", "AgentU"), "cgrqey147"),
    (("candle147", "keyboard"), "meleze147"),
    (("candle147", "AA"), "candle147"),
    (("thread147", "key"), "dlpoeb147"),
    (("thread147", "lemon"), "eldsno147"),
    (("thread147", "a"), "thread147"),
    (("thread147", "zz"), "sgqdzc147"),
    (("thread147", "AgentU"), "tnvrtx147"),
    (("thread147", "keyboard"), "dlpfod147"),
    (("thread147", "AA"), "thread147"),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 147: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 147: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "a"),
        "round 147: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 147: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 147: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 147: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", "AA"),
        "round 147: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "key"),
        "bssxh 147: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 147: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "a"),
        "round 147: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 147: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 147: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 147: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", "AA"),
        "round 147: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 147: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 147: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "a"),
        "round 147: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 147: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 147: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 147: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", "AA"),
        "round 147: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 147: the processor reads the record then stops", "key"),
        "bssxh 147: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 147: the processor reads the record then stops", "lemon"),
        "csgbq 147: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 147: the processor reads the record then stops", "a"),
        "round 147: the processor reads the record then stops",
    ),
    (
        ("round 147: the processor reads the record then stops", "zz"),
        "qntmc 147: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 147: the processor reads the record then stops", "AgentU"),
        "ruyaw 147: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 147: the processor reads the record then stops", "keyboard"),
        "bssor 147: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 147: the processor reads the record then stops", "AA"),
        "round 147: the processor reads the record then stops",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "key"),
        "bssxh 147: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "lemon"),
        "csgbq 147: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "a"),
        "round 147: a worker pulls the next task from the queue",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "zz"),
        "qntmc 147: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 147: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "keyboard"),
        "bssor 147: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 147: a worker pulls the next task from the queue", "AA"),
        "round 147: a worker pulls the next task from the queue",
    ),
    (
        ("round 147: signals travel through the network layer", "key"),
        "bssxh 147: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 147: signals travel through the network layer", "lemon"),
        "csgbq 147: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 147: signals travel through the network layer", "a"),
        "round 147: signals travel through the network layer",
    ),
    (
        ("round 147: signals travel through the network layer", "zz"),
        "qntmc 147: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 147: signals travel through the network layer", "AgentU"),
        "ruyaw 147: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 147: signals travel through the network layer", "keyboard"),
        "bssor 147: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 147: signals travel through the network layer", "AA"),
        "round 147: signals travel through the network layer",
    ),
    (
        ("round 147: the gateway routes each request by policy", "key"),
        "bssxh 147: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 147: the gateway routes each request by policy", "lemon"),
        "csgbq 147: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 147: the gateway routes each request by policy", "a"),
        "round 147: the gateway routes each request by policy",
    ),
    (
        ("round 147: the gateway routes each request by policy", "zz"),
        "qntmc 147: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 147: the gateway routes each request by policy", "AgentU"),
        "ruyaw 147: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 147: the gateway routes each request by policy", "keyboard"),
        "bssor 147: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 147: the gateway routes each request by policy", "AA"),
        "round 147: the gateway routes each request by policy",
    ),
    (("round 147: memory grows until the buffer is full", "key"), "bssxh 147: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 147: memory grows until the buffer is full", "lemon"), "csgbq 147: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 147: memory grows until the buffer is full", "a"), "round 147: memory grows until the buffer is full"),
    (("round 147: memory grows until the buffer is full", "zz"), "qntmc 147: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 147: memory grows until the buffer is full", "AgentU"),
        "ruyaw 147: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 147: memory grows until the buffer is full", "keyboard"),
        "bssor 147: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 147: memory grows until the buffer is full", "AA"), "round 147: memory grows until the buffer is full"),
    (("round 147: the cluster mirrors every packet twice", "key"), "bssxh 147: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 147: the cluster mirrors every packet twice", "lemon"),
        "csgbq 147: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 147: the cluster mirrors every packet twice", "a"), "round 147: the cluster mirrors every packet twice"),
    (("round 147: the cluster mirrors every packet twice", "zz"), "qntmc 147: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 147: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 147: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 147: the cluster mirrors every packet twice", "keyboard"),
        "bssor 147: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 147: the cluster mirrors every packet twice", "AA"), "round 147: the cluster mirrors every packet twice"),
    (
        ("round 147: ranking uses tokens learned from the corpus", "key"),
        "bssxh 147: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 147: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", "a"),
        "round 147: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 147: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 147: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 147: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", "AA"),
        "round 147: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 147: a long session ends when the candle dies", "key"),
        "bssxh 147: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 147: a long session ends when the candle dies", "lemon"),
        "csgbq 147: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 147: a long session ends when the candle dies", "a"),
        "round 147: a long session ends when the candle dies",
    ),
    (
        ("round 147: a long session ends when the candle dies", "zz"),
        "qntmc 147: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 147: a long session ends when the candle dies", "AgentU"),
        "ruyaw 147: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 147: a long session ends when the candle dies", "keyboard"),
        "bssor 147: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 147: a long session ends when the candle dies", "AA"),
        "round 147: a long session ends when the candle dies",
    ),
    (("round 147: encode the prompt then map the result", "key"), "bssxh 147: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 147: encode the prompt then map the result", "lemon"), "csgbq 147: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 147: encode the prompt then map the result", "a"), "round 147: encode the prompt then map the result"),
    (("round 147: encode the prompt then map the result", "zz"), "qntmc 147: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 147: encode the prompt then map the result", "AgentU"),
        "ruyaw 147: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 147: encode the prompt then map the result", "keyboard"),
        "bssor 147: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 147: encode the prompt then map the result", "AA"), "round 147: encode the prompt then map the result"),
    (("round 147: the kernel wakes the worker at dawn", "key"), "bssxh 147: rri iovlop ukocc xfo ambocb er neux"),
    (("round 147: the kernel wakes the worker at dawn", "lemon"), "csgbq 147: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 147: the kernel wakes the worker at dawn", "a"), "round 147: the kernel wakes the worker at dawn"),
    (("round 147: the kernel wakes the worker at dawn", "zz"), "qntmc 147: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 147: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 147: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 147: the kernel wakes the worker at dawn", "keyboard"), "bssor 147: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 147: the kernel wakes the worker at dawn", "AA"), "round 147: the kernel wakes the worker at dawn"),
    (("round 147: service latency drops after the patch", "key"), "bssxh 147: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 147: service latency drops after the patch", "lemon"), "csgbq 147: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 147: service latency drops after the patch", "a"), "round 147: service latency drops after the patch"),
    (("round 147: service latency drops after the patch", "zz"), "qntmc 147: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 147: service latency drops after the patch", "AgentU"),
        "ruyaw 147: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 147: service latency drops after the patch", "keyboard"),
        "bssor 147: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 147: service latency drops after the patch", "AA"), "round 147: service latency drops after the patch"),
    (
        ("round 147: the library caches every vector it sees", "key"),
        "bssxh 147: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 147: the library caches every vector it sees", "lemon"),
        "csgbq 147: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 147: the library caches every vector it sees", "a"), "round 147: the library caches every vector it sees"),
    (
        ("round 147: the library caches every vector it sees", "zz"),
        "qntmc 147: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 147: the library caches every vector it sees", "AgentU"),
        "ruyaw 147: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 147: the library caches every vector it sees", "keyboard"),
        "bssor 147: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 147: the library caches every vector it sees", "AA"),
        "round 147: the library caches every vector it sees",
    ),
    (("round 147: agents argue then the debate resolves", "key"), "bssxh 147: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 147: agents argue then the debate resolves", "lemon"), "csgbq 147: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 147: agents argue then the debate resolves", "a"), "round 147: agents argue then the debate resolves"),
    (("round 147: agents argue then the debate resolves", "zz"), "qntmc 147: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 147: agents argue then the debate resolves", "AgentU"),
        "ruyaw 147: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 147: agents argue then the debate resolves", "keyboard"),
        "bssor 147: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 147: agents argue then the debate resolves", "AA"), "round 147: agents argue then the debate resolves"),
    (("round 147: the filter keeps only strong matches", "key"), "bssxh 147: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 147: the filter keeps only strong matches", "lemon"), "csgbq 147: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 147: the filter keeps only strong matches", "a"), "round 147: the filter keeps only strong matches"),
    (("round 147: the filter keeps only strong matches", "zz"), "qntmc 147: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 147: the filter keeps only strong matches", "AgentU"), "ruyaw 147: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 147: the filter keeps only strong matches", "keyboard"),
        "bssor 147: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 147: the filter keeps only strong matches", "AA"), "round 147: the filter keeps only strong matches"),
    (("round 147: the model answers with a short reply", "key"), "bssxh 147: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 147: the model answers with a short reply", "lemon"), "csgbq 147: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 147: the model answers with a short reply", "a"), "round 147: the model answers with a short reply"),
    (("round 147: the model answers with a short reply", "zz"), "qntmc 147: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 147: the model answers with a short reply", "AgentU"), "ruyaw 147: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 147: the model answers with a short reply", "keyboard"),
        "bssor 147: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 147: the model answers with a short reply", "AA"), "round 147: the model answers with a short reply"),
    (
        ("round 147: the recorder stores the reasoning trace", "key"),
        "bssxh 147: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 147: the recorder stores the reasoning trace", "lemon"),
        "csgbq 147: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 147: the recorder stores the reasoning trace", "a"), "round 147: the recorder stores the reasoning trace"),
    (
        ("round 147: the recorder stores the reasoning trace", "zz"),
        "qntmc 147: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 147: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 147: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 147: the recorder stores the reasoning trace", "keyboard"),
        "bssor 147: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 147: the recorder stores the reasoning trace", "AA"),
        "round 147: the recorder stores the reasoning trace",
    ),
    (("round 147: the angel watches the processor run", "key"), "bssxh 147: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 147: the angel watches the processor run", "lemon"), "csgbq 147: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 147: the angel watches the processor run", "a"), "round 147: the angel watches the processor run"),
    (("round 147: the angel watches the processor run", "zz"), "qntmc 147: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 147: the angel watches the processor run", "AgentU"), "ruyaw 147: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 147: the angel watches the processor run", "keyboard"), "bssor 147: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 147: the angel watches the processor run", "AA"), "round 147: the angel watches the processor run"),
    (("round 147: angle of the vector decides the match", "key"), "bssxh 147: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 147: angle of the vector decides the match", "lemon"), "csgbq 147: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 147: angle of the vector decides the match", "a"), "round 147: angle of the vector decides the match"),
    (("round 147: angle of the vector decides the match", "zz"), "qntmc 147: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 147: angle of the vector decides the match", "AgentU"),
        "ruyaw 147: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 147: angle of the vector decides the match", "keyboard"),
        "bssor 147: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 147: angle of the vector decides the match", "AA"), "round 147: angle of the vector decides the match"),
    (
        ("round 147: the candle burns twice as long at night", "key"),
        "bssxh 147: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 147: the candle burns twice as long at night", "lemon"),
        "csgbq 147: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 147: the candle burns twice as long at night", "a"), "round 147: the candle burns twice as long at night"),
    (
        ("round 147: the candle burns twice as long at night", "zz"),
        "qntmc 147: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 147: the candle burns twice as long at night", "AgentU"),
        "ruyaw 147: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 147: the candle burns twice as long at night", "keyboard"),
        "bssor 147: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 147: the candle burns twice as long at night", "AA"),
        "round 147: the candle burns twice as long at night",
    ),
    (("round 147: a mirror of the universe in one line", "key"), "bssxh 147: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 147: a mirror of the universe in one line", "lemon"), "csgbq 147: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 147: a mirror of the universe in one line", "a"), "round 147: a mirror of the universe in one line"),
    (("round 147: a mirror of the universe in one line", "zz"), "qntmc 147: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 147: a mirror of the universe in one line", "AgentU"), "ruyaw 147: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 147: a mirror of the universe in one line", "keyboard"),
        "bssor 147: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 147: a mirror of the universe in one line", "AA"), "round 147: a mirror of the universe in one line"),
    (("round 147: the queue drains before the storm", "key"), "bssxh 147: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 147: the queue drains before the storm", "lemon"), "csgbq 147: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 147: the queue drains before the storm", "a"), "round 147: the queue drains before the storm"),
    (("round 147: the queue drains before the storm", "zz"), "qntmc 147: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 147: the queue drains before the storm", "AgentU"), "ruyaw 147: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 147: the queue drains before the storm", "keyboard"), "bssor 147: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 147: the queue drains before the storm", "AA"), "round 147: the queue drains before the storm"),
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
