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
    (("kitten151", "key"), "umrdil151"),
    (("kitten151", "lemon"), "vmfhry151"),
    (("kitten151", "a"), "kitten151"),
    (("kitten151", "zz"), "jhssdm151"),
    (("kitten151", "AgentU"), "koxgxh151"),
    (("kitten151", "keyboard"), "umrusn151"),
    (("kitten151", "AA"), "kitten151"),
    (("sitting151", "key"), "cmrdmlq151"),
    (("sitting151", "lemon"), "dmfhvyk151"),
    (("sitting151", "a"), "sitting151"),
    (("sitting151", "zz"), "rhsshmf151"),
    (("sitting151", "AgentU"), "soxgbhg151"),
    (("sitting151", "keyboard"), "cmruwnx151"),
    (("sitting151", "AA"), "sitting151"),
    (("agent151", "key"), "kkcxx151"),
    (("agent151", "lemon"), "lkqbg151"),
    (("agent151", "a"), "agent151"),
    (("agent151", "zz"), "zfdms151"),
    (("agent151", "AgentU"), "amiam151"),
    (("agent151", "keyboard"), "kkcoh151"),
    (("agent151", "AA"), "agent151"),
    (("angle151", "key"), "krevi151"),
    (("angle151", "lemon"), "lrszr151"),
    (("angle151", "a"), "angle151"),
    (("angle151", "zz"), "zmfkd151"),
    (("angle151", "AgentU"), "atkyx151"),
    (("angle151", "keyboard"), "krems151"),
    (("angle151", "AA"), "angle151"),
    (("universe151", "key"), "ergfipci151"),
    (("universe151", "lemon"), "frujrcwq151"),
    (("universe151", "a"), "universe151"),
    (("universe151", "zz"), "tmhudqrd151"),
    (("universe151", "AgentU"), "utmixlsk151"),
    (("universe151", "keyboard"), "ergwsrjh151"),
    (("universe151", "AA"), "universe151"),
    (("memory151", "key"), "wikyvw151"),
    (("memory151", "lemon"), "xiycej151"),
    (("memory151", "a"), "memory151"),
    (("memory151", "zz"), "ldlnqx151"),
    (("memory151", "AgentU"), "mkqbks151"),
    (("memory151", "keyboard"), "wikpfy151"),
    (("memory151", "AA"), "memory151"),
    (("stream151", "key"), "cxpoek151"),
    (("stream151", "lemon"), "dxdsnx151"),
    (("stream151", "a"), "stream151"),
    (("stream151", "zz"), "rsqdzl151"),
    (("stream151", "AgentU"), "szvrtg151"),
    (("stream151", "keyboard"), "cxpfom151"),
    (("stream151", "AA"), "stream151"),
    (("context151", "key"), "msldivd151"),
    (("context151", "lemon"), "nszhrix151"),
    (("context151", "a"), "context151"),
    (("context151", "zz"), "bnmsdws151"),
    (("context151", "AgentU"), "curgxrt151"),
    (("context151", "keyboard"), "mslusxk151"),
    (("context151", "AA"), "context151"),
    (("knowledge151", "key"), "urmgpcnkc151"),
    (("knowledge151", "lemon"), "vrakyphss151"),
    (("knowledge151", "a"), "knowledge151"),
    (("knowledge151", "zz"), "jmnvkdcfd151"),
    (("knowledge151", "AgentU"), "ktsjeydmi151"),
    (("knowledge151", "keyboard"), "urmxzeujo151"),
    (("knowledge151", "AA"), "knowledge151"),
    (("vector151", "key"), "fiadsp151"),
    (("vector151", "lemon"), "giohbc151"),
    (("vector151", "a"), "vector151"),
    (("vector151", "zz"), "udbsnq151"),
    (("vector151", "AgentU"), "vkgghl151"),
    (("vector151", "keyboard"), "fiaucr151"),
    (("vector151", "AA"), "vector151"),
    (("processor151", "key"), "zvmmiqcsp151"),
    (("processor151", "lemon"), "avaqrdwaf151"),
    (("processor151", "a"), "processor151"),
    (("processor151", "zz"), "oqnbdrrnq151"),
    (("processor151", "AgentU"), "pxspxmsuv151"),
    (("processor151", "keyboard"), "zvmdssjrb151"),
    (("processor151", "AA"), "processor151"),
    (("reasoning151", "key"), "biycslsre151"),
    (("reasoning151", "lemon"), "cimgbymzu151"),
    (("reasoning151", "a"), "reasoning151"),
    (("reasoning151", "zz"), "qdzrnmhmf151"),
    (("reasoning151", "AgentU"), "rkefhhitk151"),
    (("reasoning151", "keyboard"), "biytcnzqq151"),
    (("reasoning151", "AA"), "reasoning151"),
    (("machine151", "key"), "wearmlo151"),
    (("machine151", "lemon"), "xeovvyi151"),
    (("machine151", "a"), "machine151"),
    (("machine151", "zz"), "lzbghmd151"),
    (("machine151", "AgentU"), "mggubhe151"),
    (("machine151", "keyboard"), "weaiwnv151"),
    (("machine151", "AA"), "machine151"),
    (("learning151", "key"), "viybrgxk151"),
    (("learning151", "lemon"), "wimfatrs151"),
    (("learning151", "a"), "learning151"),
    (("learning151", "zz"), "kdzqmhmf151"),
    (("learning151", "AgentU"), "lkeegcnm151"),
    (("learning151", "keyboard"), "viysbiej151"),
    (("learning151", "AA"), "learning151"),
    (("model151", "key"), "wsbop151"),
    (("model151", "lemon"), "xspsy151"),
    (("model151", "a"), "model151"),
    (("model151", "zz"), "lncdk151"),
    (("model151", "AgentU"), "muhre151"),
    (("model151", "keyboard"), "wsbfz151"),
    (("model151", "AA"), "model151"),
    (("token151", "key"), "dsior151"),
    (("token151", "lemon"), "eswsa151"),
    (("token151", "a"), "token151"),
    (("token151", "zz"), "snjdm151"),
    (("token151", "AgentU"), "tuorg151"),
    (("token151", "keyboard"), "dsifb151"),
    (("token151", "AA"), "token151"),
    (("prompt151", "key"), "zvmwtr151"),
    (("prompt151", "lemon"), "avaace151"),
    (("prompt151", "a"), "prompt151"),
    (("prompt151", "zz"), "oqnlos151"),
    (("prompt151", "AgentU"), "pxszin151"),
    (("prompt151", "keyboard"), "zvmndt151"),
    (("prompt151", "AA"), "prompt151"),
    (("session151", "key"), "ciqcmmx151"),
    (("session151", "lemon"), "diegvzr151"),
    (("session151", "a"), "session151"),
    (("session151", "zz"), "rdrrhnm151"),
    (("session151", "AgentU"), "skwfbin151"),
    (("session151", "keyboard"), "ciqtwoe151"),
    (("session151", "AA"), "session151"),
    (("library151", "key"), "vmzbepi151"),
    (("library151", "lemon"), "wmnfncc151"),
    (("library151", "a"), "library151"),
    (("library151", "zz"), "khaqzqx151"),
    (("library151", "AgentU"), "lofetly151"),
    (("library151", "keyboard"), "vmzsorp151"),
    (("library151", "AA"), "library151"),
    (("service151", "key"), "cipfmao151"),
    (("service151", "lemon"), "didjvni151"),
    (("service151", "a"), "service151"),
    (("service151", "zz"), "rdquhbd151"),
    (("service151", "AgentU"), "skvibwe151"),
    (("service151", "keyboard"), "cipwwcv151"),
    (("service151", "AA"), "service151"),
    (("gateway151", "key"), "qeroayi151"),
    (("gateway151", "lemon"), "refsjlc151"),
    (("gateway151", "a"), "gateway151"),
    (("gateway151", "zz"), "fzsdvzx151"),
    (("gateway151", "AgentU"), "ggxrpuy151"),
    (("gateway151", "keyboard"), "qerfkap151"),
    (("gateway151", "AA"), "gateway151"),
    (("storage151", "key"), "cxmbeeo151"),
    (("storage151", "lemon"), "dxafnri151"),
    (("storage151", "a"), "storage151"),
    (("storage151", "zz"), "rsnqzfd151"),
    (("storage151", "AgentU"), "szsetae151"),
    (("storage151", "keyboard"), "cxmsogv151"),
    (("storage151", "AA"), "storage151"),
    (("network151", "key"), "xirgspu151"),
    (("network151", "lemon"), "yifkbco151"),
    (("network151", "a"), "network151"),
    (("network151", "zz"), "mdsvnqj151"),
    (("network151", "AgentU"), "nkxjhlk151"),
    (("network151", "keyboard"), "xirxcrb151"),
    (("network151", "AA"), "network151"),
    (("latency151", "key"), "verorai151"),
    (("latency151", "lemon"), "wefsanc151"),
    (("latency151", "a"), "latency151"),
    (("latency151", "zz"), "kzsdmbx151"),
    (("latency151", "AgentU"), "lgxrgwy151"),
    (("latency151", "keyboard"), "verfbcp151"),
    (("latency151", "AA"), "latency151"),
    (("buffer151", "key"), "lydpip151"),
    (("buffer151", "lemon"), "myrtrc151"),
    (("buffer151", "a"), "buffer151"),
    (("buffer151", "zz"), "ateedq151"),
    (("buffer151", "AgentU"), "bajsxl151"),
    (("buffer151", "keyboard"), "lydgsr151"),
    (("buffer151", "AA"), "buffer151"),
    (("queue151", "key"), "aycei151"),
    (("queue151", "lemon"), "byqir151"),
    (("queue151", "a"), "queue151"),
    (("queue151", "zz"), "ptdtd151"),
    (("queue151", "AgentU"), "qaihx151"),
    (("queue151", "keyboard"), "aycvs151"),
    (("queue151", "AA"), "queue151"),
    (("worker151", "key"), "gspuip151"),
    (("worker151", "lemon"), "hsdyrc151"),
    (("worker151", "a"), "worker151"),
    (("worker151", "zz"), "vnqjdq151"),
    (("worker151", "AgentU"), "wuvxxl151"),
    (("worker151", "keyboard"), "gsplsr151"),
    (("worker151", "AA"), "worker151"),
    (("kernel151", "key"), "uipxij151"),
    (("kernel151", "lemon"), "vidbrw151"),
    (("kernel151", "a"), "kernel151"),
    (("kernel151", "zz"), "jdqmdk151"),
    (("kernel151", "AgentU"), "kkvaxf151"),
    (("kernel151", "keyboard"), "uiposl151"),
    (("kernel151", "AA"), "kernel151"),
    (("signal151", "key"), "cmexej151"),
    (("signal151", "lemon"), "dmsbnw151"),
    (("signal151", "a"), "signal151"),
    (("signal151", "zz"), "rhfmzk151"),
    (("signal151", "AgentU"), "sokatf151"),
    (("signal151", "keyboard"), "cmeool151"),
    (("signal151", "AA"), "signal151"),
    (("packet151", "key"), "zeauir151"),
    (("packet151", "lemon"), "aeoyre151"),
    (("packet151", "a"), "packet151"),
    (("packet151", "zz"), "ozbjds151"),
    (("packet151", "AgentU"), "pggxxn151"),
    (("packet151", "keyboard"), "zealst151"),
    (("packet151", "AA"), "packet151"),
    (("router151", "key"), "bssdip151"),
    (("router151", "lemon"), "csghrc151"),
    (("router151", "a"), "router151"),
    (("router151", "zz"), "qntsdq151"),
    (("router151", "AgentU"), "ruygxl151"),
    (("router151", "keyboard"), "bssusr151"),
    (("router151", "AA"), "router151"),
    (("cluster151", "key"), "mpscxcb151"),
    (("cluster151", "lemon"), "npgggpv151"),
    (("cluster151", "a"), "cluster151"),
    (("cluster151", "zz"), "bktrsdq151"),
    (("cluster151", "AgentU"), "cryfmyr151"),
    (("cluster151", "keyboard"), "mpsthei151"),
    (("cluster151", "AA"), "cluster151"),
    (("mirror151", "key"), "wmpbsp151"),
    (("mirror151", "lemon"), "xmdfbc151"),
    (("mirror151", "a"), "mirror151"),
    (("mirror151", "zz"), "lhqqnq151"),
    (("mirror151", "AgentU"), "movehl151"),
    (("mirror151", "keyboard"), "wmpscr151"),
    (("mirror151", "AA"), "mirror151"),
    (("filter151", "key"), "pmjdip151"),
    (("filter151", "lemon"), "qmxhrc151"),
    (("filter151", "a"), "filter151"),
    (("filter151", "zz"), "ehksdq151"),
    (("filter151", "AgentU"), "fopgxl151"),
    (("filter151", "keyboard"), "pmjusr151"),
    (("filter151", "AA"), "filter151"),
    (("ranking151", "key"), "belumlq151"),
    (("ranking151", "lemon"), "cezyvyk151"),
    (("ranking151", "a"), "ranking151"),
    (("ranking151", "zz"), "qzmjhmf151"),
    (("ranking151", "AgentU"), "rgrxbhg151"),
    (("ranking151", "keyboard"), "bellwnx151"),
    (("ranking151", "AA"), "ranking151"),
    (("encoding151", "key"), "orayhgxk151"),
    (("encoding151", "lemon"), "procqtrs151"),
    (("encoding151", "a"), "encoding151"),
    (("encoding151", "zz"), "dmbnchmf151"),
    (("encoding151", "AgentU"), "etgbwcnm151"),
    (("encoding151", "keyboard"), "orapriej151"),
    (("encoding151", "AA"), "encoding151"),
    (("mapping151", "key"), "wenzmlq151"),
    (("mapping151", "lemon"), "xebdvyk151"),
    (("mapping151", "a"), "mapping151"),
    (("mapping151", "zz"), "lzoohmf151"),
    (("mapping151", "AgentU"), "mgtcbhg151"),
    (("mapping151", "keyboard"), "wenqwnx151"),
    (("mapping151", "AA"), "mapping151"),
    (("record151", "key"), "biayvb151"),
    (("record151", "lemon"), "cioceo151"),
    (("record151", "a"), "record151"),
    (("record151", "zz"), "qdbnqc151"),
    (("record151", "AgentU"), "rkgbkx151"),
    (("record151", "keyboard"), "biapfd151"),
    (("record151", "AA"), "record151"),
    (("candle151", "key"), "melnpc151"),
    (("candle151", "lemon"), "nezryp151"),
    (("candle151", "a"), "candle151"),
    (("candle151", "zz"), "bzmckd151"),
    (("candle151", "AgentU"), "cgrqey151"),
    (("candle151", "keyboard"), "meleze151"),
    (("candle151", "AA"), "candle151"),
    (("thread151", "key"), "dlpoeb151"),
    (("thread151", "lemon"), "eldsno151"),
    (("thread151", "a"), "thread151"),
    (("thread151", "zz"), "sgqdzc151"),
    (("thread151", "AgentU"), "tnvrtx151"),
    (("thread151", "keyboard"), "dlpfod151"),
    (("thread151", "AA"), "thread151"),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 151: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 151: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "a"),
        "round 151: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 151: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 151: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 151: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", "AA"),
        "round 151: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "key"),
        "bssxh 151: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 151: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "a"),
        "round 151: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 151: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 151: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 151: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", "AA"),
        "round 151: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 151: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 151: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "a"),
        "round 151: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 151: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 151: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 151: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", "AA"),
        "round 151: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 151: the processor reads the record then stops", "key"),
        "bssxh 151: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 151: the processor reads the record then stops", "lemon"),
        "csgbq 151: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 151: the processor reads the record then stops", "a"),
        "round 151: the processor reads the record then stops",
    ),
    (
        ("round 151: the processor reads the record then stops", "zz"),
        "qntmc 151: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 151: the processor reads the record then stops", "AgentU"),
        "ruyaw 151: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 151: the processor reads the record then stops", "keyboard"),
        "bssor 151: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 151: the processor reads the record then stops", "AA"),
        "round 151: the processor reads the record then stops",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "key"),
        "bssxh 151: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "lemon"),
        "csgbq 151: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "a"),
        "round 151: a worker pulls the next task from the queue",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "zz"),
        "qntmc 151: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 151: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "keyboard"),
        "bssor 151: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 151: a worker pulls the next task from the queue", "AA"),
        "round 151: a worker pulls the next task from the queue",
    ),
    (
        ("round 151: signals travel through the network layer", "key"),
        "bssxh 151: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 151: signals travel through the network layer", "lemon"),
        "csgbq 151: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 151: signals travel through the network layer", "a"),
        "round 151: signals travel through the network layer",
    ),
    (
        ("round 151: signals travel through the network layer", "zz"),
        "qntmc 151: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 151: signals travel through the network layer", "AgentU"),
        "ruyaw 151: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 151: signals travel through the network layer", "keyboard"),
        "bssor 151: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 151: signals travel through the network layer", "AA"),
        "round 151: signals travel through the network layer",
    ),
    (
        ("round 151: the gateway routes each request by policy", "key"),
        "bssxh 151: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 151: the gateway routes each request by policy", "lemon"),
        "csgbq 151: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 151: the gateway routes each request by policy", "a"),
        "round 151: the gateway routes each request by policy",
    ),
    (
        ("round 151: the gateway routes each request by policy", "zz"),
        "qntmc 151: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 151: the gateway routes each request by policy", "AgentU"),
        "ruyaw 151: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 151: the gateway routes each request by policy", "keyboard"),
        "bssor 151: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 151: the gateway routes each request by policy", "AA"),
        "round 151: the gateway routes each request by policy",
    ),
    (("round 151: memory grows until the buffer is full", "key"), "bssxh 151: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 151: memory grows until the buffer is full", "lemon"), "csgbq 151: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 151: memory grows until the buffer is full", "a"), "round 151: memory grows until the buffer is full"),
    (("round 151: memory grows until the buffer is full", "zz"), "qntmc 151: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 151: memory grows until the buffer is full", "AgentU"),
        "ruyaw 151: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 151: memory grows until the buffer is full", "keyboard"),
        "bssor 151: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 151: memory grows until the buffer is full", "AA"), "round 151: memory grows until the buffer is full"),
    (("round 151: the cluster mirrors every packet twice", "key"), "bssxh 151: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 151: the cluster mirrors every packet twice", "lemon"),
        "csgbq 151: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 151: the cluster mirrors every packet twice", "a"), "round 151: the cluster mirrors every packet twice"),
    (("round 151: the cluster mirrors every packet twice", "zz"), "qntmc 151: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 151: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 151: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 151: the cluster mirrors every packet twice", "keyboard"),
        "bssor 151: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 151: the cluster mirrors every packet twice", "AA"), "round 151: the cluster mirrors every packet twice"),
    (
        ("round 151: ranking uses tokens learned from the corpus", "key"),
        "bssxh 151: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 151: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", "a"),
        "round 151: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 151: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 151: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 151: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", "AA"),
        "round 151: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 151: a long session ends when the candle dies", "key"),
        "bssxh 151: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 151: a long session ends when the candle dies", "lemon"),
        "csgbq 151: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 151: a long session ends when the candle dies", "a"),
        "round 151: a long session ends when the candle dies",
    ),
    (
        ("round 151: a long session ends when the candle dies", "zz"),
        "qntmc 151: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 151: a long session ends when the candle dies", "AgentU"),
        "ruyaw 151: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 151: a long session ends when the candle dies", "keyboard"),
        "bssor 151: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 151: a long session ends when the candle dies", "AA"),
        "round 151: a long session ends when the candle dies",
    ),
    (("round 151: encode the prompt then map the result", "key"), "bssxh 151: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 151: encode the prompt then map the result", "lemon"), "csgbq 151: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 151: encode the prompt then map the result", "a"), "round 151: encode the prompt then map the result"),
    (("round 151: encode the prompt then map the result", "zz"), "qntmc 151: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 151: encode the prompt then map the result", "AgentU"),
        "ruyaw 151: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 151: encode the prompt then map the result", "keyboard"),
        "bssor 151: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 151: encode the prompt then map the result", "AA"), "round 151: encode the prompt then map the result"),
    (("round 151: the kernel wakes the worker at dawn", "key"), "bssxh 151: rri iovlop ukocc xfo ambocb er neux"),
    (("round 151: the kernel wakes the worker at dawn", "lemon"), "csgbq 151: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 151: the kernel wakes the worker at dawn", "a"), "round 151: the kernel wakes the worker at dawn"),
    (("round 151: the kernel wakes the worker at dawn", "zz"), "qntmc 151: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 151: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 151: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 151: the kernel wakes the worker at dawn", "keyboard"), "bssor 151: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 151: the kernel wakes the worker at dawn", "AA"), "round 151: the kernel wakes the worker at dawn"),
    (("round 151: service latency drops after the patch", "key"), "bssxh 151: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 151: service latency drops after the patch", "lemon"), "csgbq 151: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 151: service latency drops after the patch", "a"), "round 151: service latency drops after the patch"),
    (("round 151: service latency drops after the patch", "zz"), "qntmc 151: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 151: service latency drops after the patch", "AgentU"),
        "ruyaw 151: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 151: service latency drops after the patch", "keyboard"),
        "bssor 151: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 151: service latency drops after the patch", "AA"), "round 151: service latency drops after the patch"),
    (
        ("round 151: the library caches every vector it sees", "key"),
        "bssxh 151: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 151: the library caches every vector it sees", "lemon"),
        "csgbq 151: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 151: the library caches every vector it sees", "a"), "round 151: the library caches every vector it sees"),
    (
        ("round 151: the library caches every vector it sees", "zz"),
        "qntmc 151: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 151: the library caches every vector it sees", "AgentU"),
        "ruyaw 151: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 151: the library caches every vector it sees", "keyboard"),
        "bssor 151: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 151: the library caches every vector it sees", "AA"),
        "round 151: the library caches every vector it sees",
    ),
    (("round 151: agents argue then the debate resolves", "key"), "bssxh 151: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 151: agents argue then the debate resolves", "lemon"), "csgbq 151: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 151: agents argue then the debate resolves", "a"), "round 151: agents argue then the debate resolves"),
    (("round 151: agents argue then the debate resolves", "zz"), "qntmc 151: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 151: agents argue then the debate resolves", "AgentU"),
        "ruyaw 151: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 151: agents argue then the debate resolves", "keyboard"),
        "bssor 151: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 151: agents argue then the debate resolves", "AA"), "round 151: agents argue then the debate resolves"),
    (("round 151: the filter keeps only strong matches", "key"), "bssxh 151: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 151: the filter keeps only strong matches", "lemon"), "csgbq 151: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 151: the filter keeps only strong matches", "a"), "round 151: the filter keeps only strong matches"),
    (("round 151: the filter keeps only strong matches", "zz"), "qntmc 151: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 151: the filter keeps only strong matches", "AgentU"), "ruyaw 151: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 151: the filter keeps only strong matches", "keyboard"),
        "bssor 151: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 151: the filter keeps only strong matches", "AA"), "round 151: the filter keeps only strong matches"),
    (("round 151: the model answers with a short reply", "key"), "bssxh 151: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 151: the model answers with a short reply", "lemon"), "csgbq 151: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 151: the model answers with a short reply", "a"), "round 151: the model answers with a short reply"),
    (("round 151: the model answers with a short reply", "zz"), "qntmc 151: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 151: the model answers with a short reply", "AgentU"), "ruyaw 151: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 151: the model answers with a short reply", "keyboard"),
        "bssor 151: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 151: the model answers with a short reply", "AA"), "round 151: the model answers with a short reply"),
    (
        ("round 151: the recorder stores the reasoning trace", "key"),
        "bssxh 151: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 151: the recorder stores the reasoning trace", "lemon"),
        "csgbq 151: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 151: the recorder stores the reasoning trace", "a"), "round 151: the recorder stores the reasoning trace"),
    (
        ("round 151: the recorder stores the reasoning trace", "zz"),
        "qntmc 151: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 151: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 151: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 151: the recorder stores the reasoning trace", "keyboard"),
        "bssor 151: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 151: the recorder stores the reasoning trace", "AA"),
        "round 151: the recorder stores the reasoning trace",
    ),
    (("round 151: the angel watches the processor run", "key"), "bssxh 151: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 151: the angel watches the processor run", "lemon"), "csgbq 151: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 151: the angel watches the processor run", "a"), "round 151: the angel watches the processor run"),
    (("round 151: the angel watches the processor run", "zz"), "qntmc 151: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 151: the angel watches the processor run", "AgentU"), "ruyaw 151: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 151: the angel watches the processor run", "keyboard"), "bssor 151: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 151: the angel watches the processor run", "AA"), "round 151: the angel watches the processor run"),
    (("round 151: angle of the vector decides the match", "key"), "bssxh 151: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 151: angle of the vector decides the match", "lemon"), "csgbq 151: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 151: angle of the vector decides the match", "a"), "round 151: angle of the vector decides the match"),
    (("round 151: angle of the vector decides the match", "zz"), "qntmc 151: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 151: angle of the vector decides the match", "AgentU"),
        "ruyaw 151: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 151: angle of the vector decides the match", "keyboard"),
        "bssor 151: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 151: angle of the vector decides the match", "AA"), "round 151: angle of the vector decides the match"),
    (
        ("round 151: the candle burns twice as long at night", "key"),
        "bssxh 151: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 151: the candle burns twice as long at night", "lemon"),
        "csgbq 151: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 151: the candle burns twice as long at night", "a"), "round 151: the candle burns twice as long at night"),
    (
        ("round 151: the candle burns twice as long at night", "zz"),
        "qntmc 151: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 151: the candle burns twice as long at night", "AgentU"),
        "ruyaw 151: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 151: the candle burns twice as long at night", "keyboard"),
        "bssor 151: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 151: the candle burns twice as long at night", "AA"),
        "round 151: the candle burns twice as long at night",
    ),
    (("round 151: a mirror of the universe in one line", "key"), "bssxh 151: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 151: a mirror of the universe in one line", "lemon"), "csgbq 151: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 151: a mirror of the universe in one line", "a"), "round 151: a mirror of the universe in one line"),
    (("round 151: a mirror of the universe in one line", "zz"), "qntmc 151: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 151: a mirror of the universe in one line", "AgentU"), "ruyaw 151: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 151: a mirror of the universe in one line", "keyboard"),
        "bssor 151: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 151: a mirror of the universe in one line", "AA"), "round 151: a mirror of the universe in one line"),
    (("round 151: the queue drains before the storm", "key"), "bssxh 151: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 151: the queue drains before the storm", "lemon"), "csgbq 151: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 151: the queue drains before the storm", "a"), "round 151: the queue drains before the storm"),
    (("round 151: the queue drains before the storm", "zz"), "qntmc 151: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 151: the queue drains before the storm", "AgentU"), "ruyaw 151: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 151: the queue drains before the storm", "keyboard"), "bssor 151: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 151: the queue drains before the storm", "AA"), "round 151: the queue drains before the storm"),
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
