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
    (("kitten170", "key"), "umrdil170"),
    (("kitten170", "lemon"), "vmfhry170"),
    (("kitten170", "a"), "kitten170"),
    (("kitten170", "zz"), "jhssdm170"),
    (("kitten170", "AgentU"), "koxgxh170"),
    (("kitten170", "keyboard"), "umrusn170"),
    (("kitten170", "AA"), "kitten170"),
    (("sitting170", "key"), "cmrdmlq170"),
    (("sitting170", "lemon"), "dmfhvyk170"),
    (("sitting170", "a"), "sitting170"),
    (("sitting170", "zz"), "rhsshmf170"),
    (("sitting170", "AgentU"), "soxgbhg170"),
    (("sitting170", "keyboard"), "cmruwnx170"),
    (("sitting170", "AA"), "sitting170"),
    (("agent170", "key"), "kkcxx170"),
    (("agent170", "lemon"), "lkqbg170"),
    (("agent170", "a"), "agent170"),
    (("agent170", "zz"), "zfdms170"),
    (("agent170", "AgentU"), "amiam170"),
    (("agent170", "keyboard"), "kkcoh170"),
    (("agent170", "AA"), "agent170"),
    (("angle170", "key"), "krevi170"),
    (("angle170", "lemon"), "lrszr170"),
    (("angle170", "a"), "angle170"),
    (("angle170", "zz"), "zmfkd170"),
    (("angle170", "AgentU"), "atkyx170"),
    (("angle170", "keyboard"), "krems170"),
    (("angle170", "AA"), "angle170"),
    (("universe170", "key"), "ergfipci170"),
    (("universe170", "lemon"), "frujrcwq170"),
    (("universe170", "a"), "universe170"),
    (("universe170", "zz"), "tmhudqrd170"),
    (("universe170", "AgentU"), "utmixlsk170"),
    (("universe170", "keyboard"), "ergwsrjh170"),
    (("universe170", "AA"), "universe170"),
    (("memory170", "key"), "wikyvw170"),
    (("memory170", "lemon"), "xiycej170"),
    (("memory170", "a"), "memory170"),
    (("memory170", "zz"), "ldlnqx170"),
    (("memory170", "AgentU"), "mkqbks170"),
    (("memory170", "keyboard"), "wikpfy170"),
    (("memory170", "AA"), "memory170"),
    (("stream170", "key"), "cxpoek170"),
    (("stream170", "lemon"), "dxdsnx170"),
    (("stream170", "a"), "stream170"),
    (("stream170", "zz"), "rsqdzl170"),
    (("stream170", "AgentU"), "szvrtg170"),
    (("stream170", "keyboard"), "cxpfom170"),
    (("stream170", "AA"), "stream170"),
    (("context170", "key"), "msldivd170"),
    (("context170", "lemon"), "nszhrix170"),
    (("context170", "a"), "context170"),
    (("context170", "zz"), "bnmsdws170"),
    (("context170", "AgentU"), "curgxrt170"),
    (("context170", "keyboard"), "mslusxk170"),
    (("context170", "AA"), "context170"),
    (("knowledge170", "key"), "urmgpcnkc170"),
    (("knowledge170", "lemon"), "vrakyphss170"),
    (("knowledge170", "a"), "knowledge170"),
    (("knowledge170", "zz"), "jmnvkdcfd170"),
    (("knowledge170", "AgentU"), "ktsjeydmi170"),
    (("knowledge170", "keyboard"), "urmxzeujo170"),
    (("knowledge170", "AA"), "knowledge170"),
    (("vector170", "key"), "fiadsp170"),
    (("vector170", "lemon"), "giohbc170"),
    (("vector170", "a"), "vector170"),
    (("vector170", "zz"), "udbsnq170"),
    (("vector170", "AgentU"), "vkgghl170"),
    (("vector170", "keyboard"), "fiaucr170"),
    (("vector170", "AA"), "vector170"),
    (("processor170", "key"), "zvmmiqcsp170"),
    (("processor170", "lemon"), "avaqrdwaf170"),
    (("processor170", "a"), "processor170"),
    (("processor170", "zz"), "oqnbdrrnq170"),
    (("processor170", "AgentU"), "pxspxmsuv170"),
    (("processor170", "keyboard"), "zvmdssjrb170"),
    (("processor170", "AA"), "processor170"),
    (("reasoning170", "key"), "biycslsre170"),
    (("reasoning170", "lemon"), "cimgbymzu170"),
    (("reasoning170", "a"), "reasoning170"),
    (("reasoning170", "zz"), "qdzrnmhmf170"),
    (("reasoning170", "AgentU"), "rkefhhitk170"),
    (("reasoning170", "keyboard"), "biytcnzqq170"),
    (("reasoning170", "AA"), "reasoning170"),
    (("machine170", "key"), "wearmlo170"),
    (("machine170", "lemon"), "xeovvyi170"),
    (("machine170", "a"), "machine170"),
    (("machine170", "zz"), "lzbghmd170"),
    (("machine170", "AgentU"), "mggubhe170"),
    (("machine170", "keyboard"), "weaiwnv170"),
    (("machine170", "AA"), "machine170"),
    (("learning170", "key"), "viybrgxk170"),
    (("learning170", "lemon"), "wimfatrs170"),
    (("learning170", "a"), "learning170"),
    (("learning170", "zz"), "kdzqmhmf170"),
    (("learning170", "AgentU"), "lkeegcnm170"),
    (("learning170", "keyboard"), "viysbiej170"),
    (("learning170", "AA"), "learning170"),
    (("model170", "key"), "wsbop170"),
    (("model170", "lemon"), "xspsy170"),
    (("model170", "a"), "model170"),
    (("model170", "zz"), "lncdk170"),
    (("model170", "AgentU"), "muhre170"),
    (("model170", "keyboard"), "wsbfz170"),
    (("model170", "AA"), "model170"),
    (("token170", "key"), "dsior170"),
    (("token170", "lemon"), "eswsa170"),
    (("token170", "a"), "token170"),
    (("token170", "zz"), "snjdm170"),
    (("token170", "AgentU"), "tuorg170"),
    (("token170", "keyboard"), "dsifb170"),
    (("token170", "AA"), "token170"),
    (("prompt170", "key"), "zvmwtr170"),
    (("prompt170", "lemon"), "avaace170"),
    (("prompt170", "a"), "prompt170"),
    (("prompt170", "zz"), "oqnlos170"),
    (("prompt170", "AgentU"), "pxszin170"),
    (("prompt170", "keyboard"), "zvmndt170"),
    (("prompt170", "AA"), "prompt170"),
    (("session170", "key"), "ciqcmmx170"),
    (("session170", "lemon"), "diegvzr170"),
    (("session170", "a"), "session170"),
    (("session170", "zz"), "rdrrhnm170"),
    (("session170", "AgentU"), "skwfbin170"),
    (("session170", "keyboard"), "ciqtwoe170"),
    (("session170", "AA"), "session170"),
    (("library170", "key"), "vmzbepi170"),
    (("library170", "lemon"), "wmnfncc170"),
    (("library170", "a"), "library170"),
    (("library170", "zz"), "khaqzqx170"),
    (("library170", "AgentU"), "lofetly170"),
    (("library170", "keyboard"), "vmzsorp170"),
    (("library170", "AA"), "library170"),
    (("service170", "key"), "cipfmao170"),
    (("service170", "lemon"), "didjvni170"),
    (("service170", "a"), "service170"),
    (("service170", "zz"), "rdquhbd170"),
    (("service170", "AgentU"), "skvibwe170"),
    (("service170", "keyboard"), "cipwwcv170"),
    (("service170", "AA"), "service170"),
    (("gateway170", "key"), "qeroayi170"),
    (("gateway170", "lemon"), "refsjlc170"),
    (("gateway170", "a"), "gateway170"),
    (("gateway170", "zz"), "fzsdvzx170"),
    (("gateway170", "AgentU"), "ggxrpuy170"),
    (("gateway170", "keyboard"), "qerfkap170"),
    (("gateway170", "AA"), "gateway170"),
    (("storage170", "key"), "cxmbeeo170"),
    (("storage170", "lemon"), "dxafnri170"),
    (("storage170", "a"), "storage170"),
    (("storage170", "zz"), "rsnqzfd170"),
    (("storage170", "AgentU"), "szsetae170"),
    (("storage170", "keyboard"), "cxmsogv170"),
    (("storage170", "AA"), "storage170"),
    (("network170", "key"), "xirgspu170"),
    (("network170", "lemon"), "yifkbco170"),
    (("network170", "a"), "network170"),
    (("network170", "zz"), "mdsvnqj170"),
    (("network170", "AgentU"), "nkxjhlk170"),
    (("network170", "keyboard"), "xirxcrb170"),
    (("network170", "AA"), "network170"),
    (("latency170", "key"), "verorai170"),
    (("latency170", "lemon"), "wefsanc170"),
    (("latency170", "a"), "latency170"),
    (("latency170", "zz"), "kzsdmbx170"),
    (("latency170", "AgentU"), "lgxrgwy170"),
    (("latency170", "keyboard"), "verfbcp170"),
    (("latency170", "AA"), "latency170"),
    (("buffer170", "key"), "lydpip170"),
    (("buffer170", "lemon"), "myrtrc170"),
    (("buffer170", "a"), "buffer170"),
    (("buffer170", "zz"), "ateedq170"),
    (("buffer170", "AgentU"), "bajsxl170"),
    (("buffer170", "keyboard"), "lydgsr170"),
    (("buffer170", "AA"), "buffer170"),
    (("queue170", "key"), "aycei170"),
    (("queue170", "lemon"), "byqir170"),
    (("queue170", "a"), "queue170"),
    (("queue170", "zz"), "ptdtd170"),
    (("queue170", "AgentU"), "qaihx170"),
    (("queue170", "keyboard"), "aycvs170"),
    (("queue170", "AA"), "queue170"),
    (("worker170", "key"), "gspuip170"),
    (("worker170", "lemon"), "hsdyrc170"),
    (("worker170", "a"), "worker170"),
    (("worker170", "zz"), "vnqjdq170"),
    (("worker170", "AgentU"), "wuvxxl170"),
    (("worker170", "keyboard"), "gsplsr170"),
    (("worker170", "AA"), "worker170"),
    (("kernel170", "key"), "uipxij170"),
    (("kernel170", "lemon"), "vidbrw170"),
    (("kernel170", "a"), "kernel170"),
    (("kernel170", "zz"), "jdqmdk170"),
    (("kernel170", "AgentU"), "kkvaxf170"),
    (("kernel170", "keyboard"), "uiposl170"),
    (("kernel170", "AA"), "kernel170"),
    (("signal170", "key"), "cmexej170"),
    (("signal170", "lemon"), "dmsbnw170"),
    (("signal170", "a"), "signal170"),
    (("signal170", "zz"), "rhfmzk170"),
    (("signal170", "AgentU"), "sokatf170"),
    (("signal170", "keyboard"), "cmeool170"),
    (("signal170", "AA"), "signal170"),
    (("packet170", "key"), "zeauir170"),
    (("packet170", "lemon"), "aeoyre170"),
    (("packet170", "a"), "packet170"),
    (("packet170", "zz"), "ozbjds170"),
    (("packet170", "AgentU"), "pggxxn170"),
    (("packet170", "keyboard"), "zealst170"),
    (("packet170", "AA"), "packet170"),
    (("router170", "key"), "bssdip170"),
    (("router170", "lemon"), "csghrc170"),
    (("router170", "a"), "router170"),
    (("router170", "zz"), "qntsdq170"),
    (("router170", "AgentU"), "ruygxl170"),
    (("router170", "keyboard"), "bssusr170"),
    (("router170", "AA"), "router170"),
    (("cluster170", "key"), "mpscxcb170"),
    (("cluster170", "lemon"), "npgggpv170"),
    (("cluster170", "a"), "cluster170"),
    (("cluster170", "zz"), "bktrsdq170"),
    (("cluster170", "AgentU"), "cryfmyr170"),
    (("cluster170", "keyboard"), "mpsthei170"),
    (("cluster170", "AA"), "cluster170"),
    (("mirror170", "key"), "wmpbsp170"),
    (("mirror170", "lemon"), "xmdfbc170"),
    (("mirror170", "a"), "mirror170"),
    (("mirror170", "zz"), "lhqqnq170"),
    (("mirror170", "AgentU"), "movehl170"),
    (("mirror170", "keyboard"), "wmpscr170"),
    (("mirror170", "AA"), "mirror170"),
    (("filter170", "key"), "pmjdip170"),
    (("filter170", "lemon"), "qmxhrc170"),
    (("filter170", "a"), "filter170"),
    (("filter170", "zz"), "ehksdq170"),
    (("filter170", "AgentU"), "fopgxl170"),
    (("filter170", "keyboard"), "pmjusr170"),
    (("filter170", "AA"), "filter170"),
    (("ranking170", "key"), "belumlq170"),
    (("ranking170", "lemon"), "cezyvyk170"),
    (("ranking170", "a"), "ranking170"),
    (("ranking170", "zz"), "qzmjhmf170"),
    (("ranking170", "AgentU"), "rgrxbhg170"),
    (("ranking170", "keyboard"), "bellwnx170"),
    (("ranking170", "AA"), "ranking170"),
    (("encoding170", "key"), "orayhgxk170"),
    (("encoding170", "lemon"), "procqtrs170"),
    (("encoding170", "a"), "encoding170"),
    (("encoding170", "zz"), "dmbnchmf170"),
    (("encoding170", "AgentU"), "etgbwcnm170"),
    (("encoding170", "keyboard"), "orapriej170"),
    (("encoding170", "AA"), "encoding170"),
    (("mapping170", "key"), "wenzmlq170"),
    (("mapping170", "lemon"), "xebdvyk170"),
    (("mapping170", "a"), "mapping170"),
    (("mapping170", "zz"), "lzoohmf170"),
    (("mapping170", "AgentU"), "mgtcbhg170"),
    (("mapping170", "keyboard"), "wenqwnx170"),
    (("mapping170", "AA"), "mapping170"),
    (("record170", "key"), "biayvb170"),
    (("record170", "lemon"), "cioceo170"),
    (("record170", "a"), "record170"),
    (("record170", "zz"), "qdbnqc170"),
    (("record170", "AgentU"), "rkgbkx170"),
    (("record170", "keyboard"), "biapfd170"),
    (("record170", "AA"), "record170"),
    (("candle170", "key"), "melnpc170"),
    (("candle170", "lemon"), "nezryp170"),
    (("candle170", "a"), "candle170"),
    (("candle170", "zz"), "bzmckd170"),
    (("candle170", "AgentU"), "cgrqey170"),
    (("candle170", "keyboard"), "meleze170"),
    (("candle170", "AA"), "candle170"),
    (("thread170", "key"), "dlpoeb170"),
    (("thread170", "lemon"), "eldsno170"),
    (("thread170", "a"), "thread170"),
    (("thread170", "zz"), "sgqdzc170"),
    (("thread170", "AgentU"), "tnvrtx170"),
    (("thread170", "keyboard"), "dlpfod170"),
    (("thread170", "AA"), "thread170"),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 170: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 170: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "a"),
        "round 170: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 170: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 170: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 170: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", "AA"),
        "round 170: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "key"),
        "bssxh 170: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 170: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "a"),
        "round 170: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 170: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 170: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 170: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", "AA"),
        "round 170: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 170: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 170: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "a"),
        "round 170: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 170: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 170: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 170: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", "AA"),
        "round 170: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 170: the processor reads the record then stops", "key"),
        "bssxh 170: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 170: the processor reads the record then stops", "lemon"),
        "csgbq 170: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 170: the processor reads the record then stops", "a"),
        "round 170: the processor reads the record then stops",
    ),
    (
        ("round 170: the processor reads the record then stops", "zz"),
        "qntmc 170: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 170: the processor reads the record then stops", "AgentU"),
        "ruyaw 170: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 170: the processor reads the record then stops", "keyboard"),
        "bssor 170: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 170: the processor reads the record then stops", "AA"),
        "round 170: the processor reads the record then stops",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "key"),
        "bssxh 170: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "lemon"),
        "csgbq 170: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "a"),
        "round 170: a worker pulls the next task from the queue",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "zz"),
        "qntmc 170: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 170: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "keyboard"),
        "bssor 170: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 170: a worker pulls the next task from the queue", "AA"),
        "round 170: a worker pulls the next task from the queue",
    ),
    (
        ("round 170: signals travel through the network layer", "key"),
        "bssxh 170: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 170: signals travel through the network layer", "lemon"),
        "csgbq 170: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 170: signals travel through the network layer", "a"),
        "round 170: signals travel through the network layer",
    ),
    (
        ("round 170: signals travel through the network layer", "zz"),
        "qntmc 170: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 170: signals travel through the network layer", "AgentU"),
        "ruyaw 170: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 170: signals travel through the network layer", "keyboard"),
        "bssor 170: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 170: signals travel through the network layer", "AA"),
        "round 170: signals travel through the network layer",
    ),
    (
        ("round 170: the gateway routes each request by policy", "key"),
        "bssxh 170: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 170: the gateway routes each request by policy", "lemon"),
        "csgbq 170: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 170: the gateway routes each request by policy", "a"),
        "round 170: the gateway routes each request by policy",
    ),
    (
        ("round 170: the gateway routes each request by policy", "zz"),
        "qntmc 170: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 170: the gateway routes each request by policy", "AgentU"),
        "ruyaw 170: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 170: the gateway routes each request by policy", "keyboard"),
        "bssor 170: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 170: the gateway routes each request by policy", "AA"),
        "round 170: the gateway routes each request by policy",
    ),
    (("round 170: memory grows until the buffer is full", "key"), "bssxh 170: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 170: memory grows until the buffer is full", "lemon"), "csgbq 170: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 170: memory grows until the buffer is full", "a"), "round 170: memory grows until the buffer is full"),
    (("round 170: memory grows until the buffer is full", "zz"), "qntmc 170: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 170: memory grows until the buffer is full", "AgentU"),
        "ruyaw 170: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 170: memory grows until the buffer is full", "keyboard"),
        "bssor 170: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 170: memory grows until the buffer is full", "AA"), "round 170: memory grows until the buffer is full"),
    (("round 170: the cluster mirrors every packet twice", "key"), "bssxh 170: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 170: the cluster mirrors every packet twice", "lemon"),
        "csgbq 170: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 170: the cluster mirrors every packet twice", "a"), "round 170: the cluster mirrors every packet twice"),
    (("round 170: the cluster mirrors every packet twice", "zz"), "qntmc 170: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 170: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 170: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 170: the cluster mirrors every packet twice", "keyboard"),
        "bssor 170: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 170: the cluster mirrors every packet twice", "AA"), "round 170: the cluster mirrors every packet twice"),
    (
        ("round 170: ranking uses tokens learned from the corpus", "key"),
        "bssxh 170: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 170: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", "a"),
        "round 170: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 170: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 170: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 170: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", "AA"),
        "round 170: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 170: a long session ends when the candle dies", "key"),
        "bssxh 170: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 170: a long session ends when the candle dies", "lemon"),
        "csgbq 170: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 170: a long session ends when the candle dies", "a"),
        "round 170: a long session ends when the candle dies",
    ),
    (
        ("round 170: a long session ends when the candle dies", "zz"),
        "qntmc 170: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 170: a long session ends when the candle dies", "AgentU"),
        "ruyaw 170: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 170: a long session ends when the candle dies", "keyboard"),
        "bssor 170: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 170: a long session ends when the candle dies", "AA"),
        "round 170: a long session ends when the candle dies",
    ),
    (("round 170: encode the prompt then map the result", "key"), "bssxh 170: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 170: encode the prompt then map the result", "lemon"), "csgbq 170: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 170: encode the prompt then map the result", "a"), "round 170: encode the prompt then map the result"),
    (("round 170: encode the prompt then map the result", "zz"), "qntmc 170: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 170: encode the prompt then map the result", "AgentU"),
        "ruyaw 170: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 170: encode the prompt then map the result", "keyboard"),
        "bssor 170: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 170: encode the prompt then map the result", "AA"), "round 170: encode the prompt then map the result"),
    (("round 170: the kernel wakes the worker at dawn", "key"), "bssxh 170: rri iovlop ukocc xfo ambocb er neux"),
    (("round 170: the kernel wakes the worker at dawn", "lemon"), "csgbq 170: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 170: the kernel wakes the worker at dawn", "a"), "round 170: the kernel wakes the worker at dawn"),
    (("round 170: the kernel wakes the worker at dawn", "zz"), "qntmc 170: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 170: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 170: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 170: the kernel wakes the worker at dawn", "keyboard"), "bssor 170: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 170: the kernel wakes the worker at dawn", "AA"), "round 170: the kernel wakes the worker at dawn"),
    (("round 170: service latency drops after the patch", "key"), "bssxh 170: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 170: service latency drops after the patch", "lemon"), "csgbq 170: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 170: service latency drops after the patch", "a"), "round 170: service latency drops after the patch"),
    (("round 170: service latency drops after the patch", "zz"), "qntmc 170: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 170: service latency drops after the patch", "AgentU"),
        "ruyaw 170: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 170: service latency drops after the patch", "keyboard"),
        "bssor 170: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 170: service latency drops after the patch", "AA"), "round 170: service latency drops after the patch"),
    (
        ("round 170: the library caches every vector it sees", "key"),
        "bssxh 170: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 170: the library caches every vector it sees", "lemon"),
        "csgbq 170: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 170: the library caches every vector it sees", "a"), "round 170: the library caches every vector it sees"),
    (
        ("round 170: the library caches every vector it sees", "zz"),
        "qntmc 170: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 170: the library caches every vector it sees", "AgentU"),
        "ruyaw 170: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 170: the library caches every vector it sees", "keyboard"),
        "bssor 170: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 170: the library caches every vector it sees", "AA"),
        "round 170: the library caches every vector it sees",
    ),
    (("round 170: agents argue then the debate resolves", "key"), "bssxh 170: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 170: agents argue then the debate resolves", "lemon"), "csgbq 170: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 170: agents argue then the debate resolves", "a"), "round 170: agents argue then the debate resolves"),
    (("round 170: agents argue then the debate resolves", "zz"), "qntmc 170: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 170: agents argue then the debate resolves", "AgentU"),
        "ruyaw 170: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 170: agents argue then the debate resolves", "keyboard"),
        "bssor 170: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 170: agents argue then the debate resolves", "AA"), "round 170: agents argue then the debate resolves"),
    (("round 170: the filter keeps only strong matches", "key"), "bssxh 170: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 170: the filter keeps only strong matches", "lemon"), "csgbq 170: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 170: the filter keeps only strong matches", "a"), "round 170: the filter keeps only strong matches"),
    (("round 170: the filter keeps only strong matches", "zz"), "qntmc 170: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 170: the filter keeps only strong matches", "AgentU"), "ruyaw 170: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 170: the filter keeps only strong matches", "keyboard"),
        "bssor 170: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 170: the filter keeps only strong matches", "AA"), "round 170: the filter keeps only strong matches"),
    (("round 170: the model answers with a short reply", "key"), "bssxh 170: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 170: the model answers with a short reply", "lemon"), "csgbq 170: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 170: the model answers with a short reply", "a"), "round 170: the model answers with a short reply"),
    (("round 170: the model answers with a short reply", "zz"), "qntmc 170: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 170: the model answers with a short reply", "AgentU"), "ruyaw 170: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 170: the model answers with a short reply", "keyboard"),
        "bssor 170: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 170: the model answers with a short reply", "AA"), "round 170: the model answers with a short reply"),
    (
        ("round 170: the recorder stores the reasoning trace", "key"),
        "bssxh 170: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 170: the recorder stores the reasoning trace", "lemon"),
        "csgbq 170: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 170: the recorder stores the reasoning trace", "a"), "round 170: the recorder stores the reasoning trace"),
    (
        ("round 170: the recorder stores the reasoning trace", "zz"),
        "qntmc 170: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 170: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 170: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 170: the recorder stores the reasoning trace", "keyboard"),
        "bssor 170: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 170: the recorder stores the reasoning trace", "AA"),
        "round 170: the recorder stores the reasoning trace",
    ),
    (("round 170: the angel watches the processor run", "key"), "bssxh 170: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 170: the angel watches the processor run", "lemon"), "csgbq 170: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 170: the angel watches the processor run", "a"), "round 170: the angel watches the processor run"),
    (("round 170: the angel watches the processor run", "zz"), "qntmc 170: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 170: the angel watches the processor run", "AgentU"), "ruyaw 170: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 170: the angel watches the processor run", "keyboard"), "bssor 170: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 170: the angel watches the processor run", "AA"), "round 170: the angel watches the processor run"),
    (("round 170: angle of the vector decides the match", "key"), "bssxh 170: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 170: angle of the vector decides the match", "lemon"), "csgbq 170: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 170: angle of the vector decides the match", "a"), "round 170: angle of the vector decides the match"),
    (("round 170: angle of the vector decides the match", "zz"), "qntmc 170: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 170: angle of the vector decides the match", "AgentU"),
        "ruyaw 170: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 170: angle of the vector decides the match", "keyboard"),
        "bssor 170: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 170: angle of the vector decides the match", "AA"), "round 170: angle of the vector decides the match"),
    (
        ("round 170: the candle burns twice as long at night", "key"),
        "bssxh 170: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 170: the candle burns twice as long at night", "lemon"),
        "csgbq 170: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 170: the candle burns twice as long at night", "a"), "round 170: the candle burns twice as long at night"),
    (
        ("round 170: the candle burns twice as long at night", "zz"),
        "qntmc 170: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 170: the candle burns twice as long at night", "AgentU"),
        "ruyaw 170: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 170: the candle burns twice as long at night", "keyboard"),
        "bssor 170: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 170: the candle burns twice as long at night", "AA"),
        "round 170: the candle burns twice as long at night",
    ),
    (("round 170: a mirror of the universe in one line", "key"), "bssxh 170: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 170: a mirror of the universe in one line", "lemon"), "csgbq 170: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 170: a mirror of the universe in one line", "a"), "round 170: a mirror of the universe in one line"),
    (("round 170: a mirror of the universe in one line", "zz"), "qntmc 170: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 170: a mirror of the universe in one line", "AgentU"), "ruyaw 170: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 170: a mirror of the universe in one line", "keyboard"),
        "bssor 170: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 170: a mirror of the universe in one line", "AA"), "round 170: a mirror of the universe in one line"),
    (("round 170: the queue drains before the storm", "key"), "bssxh 170: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 170: the queue drains before the storm", "lemon"), "csgbq 170: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 170: the queue drains before the storm", "a"), "round 170: the queue drains before the storm"),
    (("round 170: the queue drains before the storm", "zz"), "qntmc 170: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 170: the queue drains before the storm", "AgentU"), "ruyaw 170: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 170: the queue drains before the storm", "keyboard"), "bssor 170: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 170: the queue drains before the storm", "AA"), "round 170: the queue drains before the storm"),
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
