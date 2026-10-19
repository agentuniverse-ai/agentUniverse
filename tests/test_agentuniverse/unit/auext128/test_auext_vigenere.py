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
    (("kitten128", "key"), "umrdil128"),
    (("kitten128", "lemon"), "vmfhry128"),
    (("kitten128", "a"), "kitten128"),
    (("kitten128", "zz"), "jhssdm128"),
    (("kitten128", "AgentU"), "koxgxh128"),
    (("kitten128", "keyboard"), "umrusn128"),
    (("kitten128", "AA"), "kitten128"),
    (("sitting128", "key"), "cmrdmlq128"),
    (("sitting128", "lemon"), "dmfhvyk128"),
    (("sitting128", "a"), "sitting128"),
    (("sitting128", "zz"), "rhsshmf128"),
    (("sitting128", "AgentU"), "soxgbhg128"),
    (("sitting128", "keyboard"), "cmruwnx128"),
    (("sitting128", "AA"), "sitting128"),
    (("agent128", "key"), "kkcxx128"),
    (("agent128", "lemon"), "lkqbg128"),
    (("agent128", "a"), "agent128"),
    (("agent128", "zz"), "zfdms128"),
    (("agent128", "AgentU"), "amiam128"),
    (("agent128", "keyboard"), "kkcoh128"),
    (("agent128", "AA"), "agent128"),
    (("angle128", "key"), "krevi128"),
    (("angle128", "lemon"), "lrszr128"),
    (("angle128", "a"), "angle128"),
    (("angle128", "zz"), "zmfkd128"),
    (("angle128", "AgentU"), "atkyx128"),
    (("angle128", "keyboard"), "krems128"),
    (("angle128", "AA"), "angle128"),
    (("universe128", "key"), "ergfipci128"),
    (("universe128", "lemon"), "frujrcwq128"),
    (("universe128", "a"), "universe128"),
    (("universe128", "zz"), "tmhudqrd128"),
    (("universe128", "AgentU"), "utmixlsk128"),
    (("universe128", "keyboard"), "ergwsrjh128"),
    (("universe128", "AA"), "universe128"),
    (("memory128", "key"), "wikyvw128"),
    (("memory128", "lemon"), "xiycej128"),
    (("memory128", "a"), "memory128"),
    (("memory128", "zz"), "ldlnqx128"),
    (("memory128", "AgentU"), "mkqbks128"),
    (("memory128", "keyboard"), "wikpfy128"),
    (("memory128", "AA"), "memory128"),
    (("stream128", "key"), "cxpoek128"),
    (("stream128", "lemon"), "dxdsnx128"),
    (("stream128", "a"), "stream128"),
    (("stream128", "zz"), "rsqdzl128"),
    (("stream128", "AgentU"), "szvrtg128"),
    (("stream128", "keyboard"), "cxpfom128"),
    (("stream128", "AA"), "stream128"),
    (("context128", "key"), "msldivd128"),
    (("context128", "lemon"), "nszhrix128"),
    (("context128", "a"), "context128"),
    (("context128", "zz"), "bnmsdws128"),
    (("context128", "AgentU"), "curgxrt128"),
    (("context128", "keyboard"), "mslusxk128"),
    (("context128", "AA"), "context128"),
    (("knowledge128", "key"), "urmgpcnkc128"),
    (("knowledge128", "lemon"), "vrakyphss128"),
    (("knowledge128", "a"), "knowledge128"),
    (("knowledge128", "zz"), "jmnvkdcfd128"),
    (("knowledge128", "AgentU"), "ktsjeydmi128"),
    (("knowledge128", "keyboard"), "urmxzeujo128"),
    (("knowledge128", "AA"), "knowledge128"),
    (("vector128", "key"), "fiadsp128"),
    (("vector128", "lemon"), "giohbc128"),
    (("vector128", "a"), "vector128"),
    (("vector128", "zz"), "udbsnq128"),
    (("vector128", "AgentU"), "vkgghl128"),
    (("vector128", "keyboard"), "fiaucr128"),
    (("vector128", "AA"), "vector128"),
    (("processor128", "key"), "zvmmiqcsp128"),
    (("processor128", "lemon"), "avaqrdwaf128"),
    (("processor128", "a"), "processor128"),
    (("processor128", "zz"), "oqnbdrrnq128"),
    (("processor128", "AgentU"), "pxspxmsuv128"),
    (("processor128", "keyboard"), "zvmdssjrb128"),
    (("processor128", "AA"), "processor128"),
    (("reasoning128", "key"), "biycslsre128"),
    (("reasoning128", "lemon"), "cimgbymzu128"),
    (("reasoning128", "a"), "reasoning128"),
    (("reasoning128", "zz"), "qdzrnmhmf128"),
    (("reasoning128", "AgentU"), "rkefhhitk128"),
    (("reasoning128", "keyboard"), "biytcnzqq128"),
    (("reasoning128", "AA"), "reasoning128"),
    (("machine128", "key"), "wearmlo128"),
    (("machine128", "lemon"), "xeovvyi128"),
    (("machine128", "a"), "machine128"),
    (("machine128", "zz"), "lzbghmd128"),
    (("machine128", "AgentU"), "mggubhe128"),
    (("machine128", "keyboard"), "weaiwnv128"),
    (("machine128", "AA"), "machine128"),
    (("learning128", "key"), "viybrgxk128"),
    (("learning128", "lemon"), "wimfatrs128"),
    (("learning128", "a"), "learning128"),
    (("learning128", "zz"), "kdzqmhmf128"),
    (("learning128", "AgentU"), "lkeegcnm128"),
    (("learning128", "keyboard"), "viysbiej128"),
    (("learning128", "AA"), "learning128"),
    (("model128", "key"), "wsbop128"),
    (("model128", "lemon"), "xspsy128"),
    (("model128", "a"), "model128"),
    (("model128", "zz"), "lncdk128"),
    (("model128", "AgentU"), "muhre128"),
    (("model128", "keyboard"), "wsbfz128"),
    (("model128", "AA"), "model128"),
    (("token128", "key"), "dsior128"),
    (("token128", "lemon"), "eswsa128"),
    (("token128", "a"), "token128"),
    (("token128", "zz"), "snjdm128"),
    (("token128", "AgentU"), "tuorg128"),
    (("token128", "keyboard"), "dsifb128"),
    (("token128", "AA"), "token128"),
    (("prompt128", "key"), "zvmwtr128"),
    (("prompt128", "lemon"), "avaace128"),
    (("prompt128", "a"), "prompt128"),
    (("prompt128", "zz"), "oqnlos128"),
    (("prompt128", "AgentU"), "pxszin128"),
    (("prompt128", "keyboard"), "zvmndt128"),
    (("prompt128", "AA"), "prompt128"),
    (("session128", "key"), "ciqcmmx128"),
    (("session128", "lemon"), "diegvzr128"),
    (("session128", "a"), "session128"),
    (("session128", "zz"), "rdrrhnm128"),
    (("session128", "AgentU"), "skwfbin128"),
    (("session128", "keyboard"), "ciqtwoe128"),
    (("session128", "AA"), "session128"),
    (("library128", "key"), "vmzbepi128"),
    (("library128", "lemon"), "wmnfncc128"),
    (("library128", "a"), "library128"),
    (("library128", "zz"), "khaqzqx128"),
    (("library128", "AgentU"), "lofetly128"),
    (("library128", "keyboard"), "vmzsorp128"),
    (("library128", "AA"), "library128"),
    (("service128", "key"), "cipfmao128"),
    (("service128", "lemon"), "didjvni128"),
    (("service128", "a"), "service128"),
    (("service128", "zz"), "rdquhbd128"),
    (("service128", "AgentU"), "skvibwe128"),
    (("service128", "keyboard"), "cipwwcv128"),
    (("service128", "AA"), "service128"),
    (("gateway128", "key"), "qeroayi128"),
    (("gateway128", "lemon"), "refsjlc128"),
    (("gateway128", "a"), "gateway128"),
    (("gateway128", "zz"), "fzsdvzx128"),
    (("gateway128", "AgentU"), "ggxrpuy128"),
    (("gateway128", "keyboard"), "qerfkap128"),
    (("gateway128", "AA"), "gateway128"),
    (("storage128", "key"), "cxmbeeo128"),
    (("storage128", "lemon"), "dxafnri128"),
    (("storage128", "a"), "storage128"),
    (("storage128", "zz"), "rsnqzfd128"),
    (("storage128", "AgentU"), "szsetae128"),
    (("storage128", "keyboard"), "cxmsogv128"),
    (("storage128", "AA"), "storage128"),
    (("network128", "key"), "xirgspu128"),
    (("network128", "lemon"), "yifkbco128"),
    (("network128", "a"), "network128"),
    (("network128", "zz"), "mdsvnqj128"),
    (("network128", "AgentU"), "nkxjhlk128"),
    (("network128", "keyboard"), "xirxcrb128"),
    (("network128", "AA"), "network128"),
    (("latency128", "key"), "verorai128"),
    (("latency128", "lemon"), "wefsanc128"),
    (("latency128", "a"), "latency128"),
    (("latency128", "zz"), "kzsdmbx128"),
    (("latency128", "AgentU"), "lgxrgwy128"),
    (("latency128", "keyboard"), "verfbcp128"),
    (("latency128", "AA"), "latency128"),
    (("buffer128", "key"), "lydpip128"),
    (("buffer128", "lemon"), "myrtrc128"),
    (("buffer128", "a"), "buffer128"),
    (("buffer128", "zz"), "ateedq128"),
    (("buffer128", "AgentU"), "bajsxl128"),
    (("buffer128", "keyboard"), "lydgsr128"),
    (("buffer128", "AA"), "buffer128"),
    (("queue128", "key"), "aycei128"),
    (("queue128", "lemon"), "byqir128"),
    (("queue128", "a"), "queue128"),
    (("queue128", "zz"), "ptdtd128"),
    (("queue128", "AgentU"), "qaihx128"),
    (("queue128", "keyboard"), "aycvs128"),
    (("queue128", "AA"), "queue128"),
    (("worker128", "key"), "gspuip128"),
    (("worker128", "lemon"), "hsdyrc128"),
    (("worker128", "a"), "worker128"),
    (("worker128", "zz"), "vnqjdq128"),
    (("worker128", "AgentU"), "wuvxxl128"),
    (("worker128", "keyboard"), "gsplsr128"),
    (("worker128", "AA"), "worker128"),
    (("kernel128", "key"), "uipxij128"),
    (("kernel128", "lemon"), "vidbrw128"),
    (("kernel128", "a"), "kernel128"),
    (("kernel128", "zz"), "jdqmdk128"),
    (("kernel128", "AgentU"), "kkvaxf128"),
    (("kernel128", "keyboard"), "uiposl128"),
    (("kernel128", "AA"), "kernel128"),
    (("signal128", "key"), "cmexej128"),
    (("signal128", "lemon"), "dmsbnw128"),
    (("signal128", "a"), "signal128"),
    (("signal128", "zz"), "rhfmzk128"),
    (("signal128", "AgentU"), "sokatf128"),
    (("signal128", "keyboard"), "cmeool128"),
    (("signal128", "AA"), "signal128"),
    (("packet128", "key"), "zeauir128"),
    (("packet128", "lemon"), "aeoyre128"),
    (("packet128", "a"), "packet128"),
    (("packet128", "zz"), "ozbjds128"),
    (("packet128", "AgentU"), "pggxxn128"),
    (("packet128", "keyboard"), "zealst128"),
    (("packet128", "AA"), "packet128"),
    (("router128", "key"), "bssdip128"),
    (("router128", "lemon"), "csghrc128"),
    (("router128", "a"), "router128"),
    (("router128", "zz"), "qntsdq128"),
    (("router128", "AgentU"), "ruygxl128"),
    (("router128", "keyboard"), "bssusr128"),
    (("router128", "AA"), "router128"),
    (("cluster128", "key"), "mpscxcb128"),
    (("cluster128", "lemon"), "npgggpv128"),
    (("cluster128", "a"), "cluster128"),
    (("cluster128", "zz"), "bktrsdq128"),
    (("cluster128", "AgentU"), "cryfmyr128"),
    (("cluster128", "keyboard"), "mpsthei128"),
    (("cluster128", "AA"), "cluster128"),
    (("mirror128", "key"), "wmpbsp128"),
    (("mirror128", "lemon"), "xmdfbc128"),
    (("mirror128", "a"), "mirror128"),
    (("mirror128", "zz"), "lhqqnq128"),
    (("mirror128", "AgentU"), "movehl128"),
    (("mirror128", "keyboard"), "wmpscr128"),
    (("mirror128", "AA"), "mirror128"),
    (("filter128", "key"), "pmjdip128"),
    (("filter128", "lemon"), "qmxhrc128"),
    (("filter128", "a"), "filter128"),
    (("filter128", "zz"), "ehksdq128"),
    (("filter128", "AgentU"), "fopgxl128"),
    (("filter128", "keyboard"), "pmjusr128"),
    (("filter128", "AA"), "filter128"),
    (("ranking128", "key"), "belumlq128"),
    (("ranking128", "lemon"), "cezyvyk128"),
    (("ranking128", "a"), "ranking128"),
    (("ranking128", "zz"), "qzmjhmf128"),
    (("ranking128", "AgentU"), "rgrxbhg128"),
    (("ranking128", "keyboard"), "bellwnx128"),
    (("ranking128", "AA"), "ranking128"),
    (("encoding128", "key"), "orayhgxk128"),
    (("encoding128", "lemon"), "procqtrs128"),
    (("encoding128", "a"), "encoding128"),
    (("encoding128", "zz"), "dmbnchmf128"),
    (("encoding128", "AgentU"), "etgbwcnm128"),
    (("encoding128", "keyboard"), "orapriej128"),
    (("encoding128", "AA"), "encoding128"),
    (("mapping128", "key"), "wenzmlq128"),
    (("mapping128", "lemon"), "xebdvyk128"),
    (("mapping128", "a"), "mapping128"),
    (("mapping128", "zz"), "lzoohmf128"),
    (("mapping128", "AgentU"), "mgtcbhg128"),
    (("mapping128", "keyboard"), "wenqwnx128"),
    (("mapping128", "AA"), "mapping128"),
    (("record128", "key"), "biayvb128"),
    (("record128", "lemon"), "cioceo128"),
    (("record128", "a"), "record128"),
    (("record128", "zz"), "qdbnqc128"),
    (("record128", "AgentU"), "rkgbkx128"),
    (("record128", "keyboard"), "biapfd128"),
    (("record128", "AA"), "record128"),
    (("candle128", "key"), "melnpc128"),
    (("candle128", "lemon"), "nezryp128"),
    (("candle128", "a"), "candle128"),
    (("candle128", "zz"), "bzmckd128"),
    (("candle128", "AgentU"), "cgrqey128"),
    (("candle128", "keyboard"), "meleze128"),
    (("candle128", "AA"), "candle128"),
    (("thread128", "key"), "dlpoeb128"),
    (("thread128", "lemon"), "eldsno128"),
    (("thread128", "a"), "thread128"),
    (("thread128", "zz"), "sgqdzc128"),
    (("thread128", "AgentU"), "tnvrtx128"),
    (("thread128", "keyboard"), "dlpfod128"),
    (("thread128", "AA"), "thread128"),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 128: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 128: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "a"),
        "round 128: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 128: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 128: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 128: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", "AA"),
        "round 128: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "key"),
        "bssxh 128: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 128: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "a"),
        "round 128: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 128: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 128: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 128: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", "AA"),
        "round 128: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 128: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 128: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "a"),
        "round 128: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 128: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 128: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 128: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", "AA"),
        "round 128: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 128: the processor reads the record then stops", "key"),
        "bssxh 128: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 128: the processor reads the record then stops", "lemon"),
        "csgbq 128: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 128: the processor reads the record then stops", "a"),
        "round 128: the processor reads the record then stops",
    ),
    (
        ("round 128: the processor reads the record then stops", "zz"),
        "qntmc 128: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 128: the processor reads the record then stops", "AgentU"),
        "ruyaw 128: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 128: the processor reads the record then stops", "keyboard"),
        "bssor 128: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 128: the processor reads the record then stops", "AA"),
        "round 128: the processor reads the record then stops",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "key"),
        "bssxh 128: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "lemon"),
        "csgbq 128: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "a"),
        "round 128: a worker pulls the next task from the queue",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "zz"),
        "qntmc 128: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 128: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "keyboard"),
        "bssor 128: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 128: a worker pulls the next task from the queue", "AA"),
        "round 128: a worker pulls the next task from the queue",
    ),
    (
        ("round 128: signals travel through the network layer", "key"),
        "bssxh 128: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 128: signals travel through the network layer", "lemon"),
        "csgbq 128: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 128: signals travel through the network layer", "a"),
        "round 128: signals travel through the network layer",
    ),
    (
        ("round 128: signals travel through the network layer", "zz"),
        "qntmc 128: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 128: signals travel through the network layer", "AgentU"),
        "ruyaw 128: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 128: signals travel through the network layer", "keyboard"),
        "bssor 128: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 128: signals travel through the network layer", "AA"),
        "round 128: signals travel through the network layer",
    ),
    (
        ("round 128: the gateway routes each request by policy", "key"),
        "bssxh 128: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 128: the gateway routes each request by policy", "lemon"),
        "csgbq 128: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 128: the gateway routes each request by policy", "a"),
        "round 128: the gateway routes each request by policy",
    ),
    (
        ("round 128: the gateway routes each request by policy", "zz"),
        "qntmc 128: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 128: the gateway routes each request by policy", "AgentU"),
        "ruyaw 128: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 128: the gateway routes each request by policy", "keyboard"),
        "bssor 128: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 128: the gateway routes each request by policy", "AA"),
        "round 128: the gateway routes each request by policy",
    ),
    (("round 128: memory grows until the buffer is full", "key"), "bssxh 128: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 128: memory grows until the buffer is full", "lemon"), "csgbq 128: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 128: memory grows until the buffer is full", "a"), "round 128: memory grows until the buffer is full"),
    (("round 128: memory grows until the buffer is full", "zz"), "qntmc 128: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 128: memory grows until the buffer is full", "AgentU"),
        "ruyaw 128: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 128: memory grows until the buffer is full", "keyboard"),
        "bssor 128: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 128: memory grows until the buffer is full", "AA"), "round 128: memory grows until the buffer is full"),
    (("round 128: the cluster mirrors every packet twice", "key"), "bssxh 128: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 128: the cluster mirrors every packet twice", "lemon"),
        "csgbq 128: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 128: the cluster mirrors every packet twice", "a"), "round 128: the cluster mirrors every packet twice"),
    (("round 128: the cluster mirrors every packet twice", "zz"), "qntmc 128: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 128: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 128: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 128: the cluster mirrors every packet twice", "keyboard"),
        "bssor 128: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 128: the cluster mirrors every packet twice", "AA"), "round 128: the cluster mirrors every packet twice"),
    (
        ("round 128: ranking uses tokens learned from the corpus", "key"),
        "bssxh 128: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 128: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", "a"),
        "round 128: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 128: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 128: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 128: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", "AA"),
        "round 128: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 128: a long session ends when the candle dies", "key"),
        "bssxh 128: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 128: a long session ends when the candle dies", "lemon"),
        "csgbq 128: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 128: a long session ends when the candle dies", "a"),
        "round 128: a long session ends when the candle dies",
    ),
    (
        ("round 128: a long session ends when the candle dies", "zz"),
        "qntmc 128: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 128: a long session ends when the candle dies", "AgentU"),
        "ruyaw 128: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 128: a long session ends when the candle dies", "keyboard"),
        "bssor 128: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 128: a long session ends when the candle dies", "AA"),
        "round 128: a long session ends when the candle dies",
    ),
    (("round 128: encode the prompt then map the result", "key"), "bssxh 128: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 128: encode the prompt then map the result", "lemon"), "csgbq 128: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 128: encode the prompt then map the result", "a"), "round 128: encode the prompt then map the result"),
    (("round 128: encode the prompt then map the result", "zz"), "qntmc 128: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 128: encode the prompt then map the result", "AgentU"),
        "ruyaw 128: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 128: encode the prompt then map the result", "keyboard"),
        "bssor 128: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 128: encode the prompt then map the result", "AA"), "round 128: encode the prompt then map the result"),
    (("round 128: the kernel wakes the worker at dawn", "key"), "bssxh 128: rri iovlop ukocc xfo ambocb er neux"),
    (("round 128: the kernel wakes the worker at dawn", "lemon"), "csgbq 128: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 128: the kernel wakes the worker at dawn", "a"), "round 128: the kernel wakes the worker at dawn"),
    (("round 128: the kernel wakes the worker at dawn", "zz"), "qntmc 128: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 128: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 128: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 128: the kernel wakes the worker at dawn", "keyboard"), "bssor 128: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 128: the kernel wakes the worker at dawn", "AA"), "round 128: the kernel wakes the worker at dawn"),
    (("round 128: service latency drops after the patch", "key"), "bssxh 128: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 128: service latency drops after the patch", "lemon"), "csgbq 128: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 128: service latency drops after the patch", "a"), "round 128: service latency drops after the patch"),
    (("round 128: service latency drops after the patch", "zz"), "qntmc 128: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 128: service latency drops after the patch", "AgentU"),
        "ruyaw 128: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 128: service latency drops after the patch", "keyboard"),
        "bssor 128: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 128: service latency drops after the patch", "AA"), "round 128: service latency drops after the patch"),
    (
        ("round 128: the library caches every vector it sees", "key"),
        "bssxh 128: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 128: the library caches every vector it sees", "lemon"),
        "csgbq 128: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 128: the library caches every vector it sees", "a"), "round 128: the library caches every vector it sees"),
    (
        ("round 128: the library caches every vector it sees", "zz"),
        "qntmc 128: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 128: the library caches every vector it sees", "AgentU"),
        "ruyaw 128: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 128: the library caches every vector it sees", "keyboard"),
        "bssor 128: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 128: the library caches every vector it sees", "AA"),
        "round 128: the library caches every vector it sees",
    ),
    (("round 128: agents argue then the debate resolves", "key"), "bssxh 128: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 128: agents argue then the debate resolves", "lemon"), "csgbq 128: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 128: agents argue then the debate resolves", "a"), "round 128: agents argue then the debate resolves"),
    (("round 128: agents argue then the debate resolves", "zz"), "qntmc 128: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 128: agents argue then the debate resolves", "AgentU"),
        "ruyaw 128: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 128: agents argue then the debate resolves", "keyboard"),
        "bssor 128: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 128: agents argue then the debate resolves", "AA"), "round 128: agents argue then the debate resolves"),
    (("round 128: the filter keeps only strong matches", "key"), "bssxh 128: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 128: the filter keeps only strong matches", "lemon"), "csgbq 128: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 128: the filter keeps only strong matches", "a"), "round 128: the filter keeps only strong matches"),
    (("round 128: the filter keeps only strong matches", "zz"), "qntmc 128: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 128: the filter keeps only strong matches", "AgentU"), "ruyaw 128: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 128: the filter keeps only strong matches", "keyboard"),
        "bssor 128: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 128: the filter keeps only strong matches", "AA"), "round 128: the filter keeps only strong matches"),
    (("round 128: the model answers with a short reply", "key"), "bssxh 128: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 128: the model answers with a short reply", "lemon"), "csgbq 128: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 128: the model answers with a short reply", "a"), "round 128: the model answers with a short reply"),
    (("round 128: the model answers with a short reply", "zz"), "qntmc 128: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 128: the model answers with a short reply", "AgentU"), "ruyaw 128: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 128: the model answers with a short reply", "keyboard"),
        "bssor 128: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 128: the model answers with a short reply", "AA"), "round 128: the model answers with a short reply"),
    (
        ("round 128: the recorder stores the reasoning trace", "key"),
        "bssxh 128: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 128: the recorder stores the reasoning trace", "lemon"),
        "csgbq 128: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 128: the recorder stores the reasoning trace", "a"), "round 128: the recorder stores the reasoning trace"),
    (
        ("round 128: the recorder stores the reasoning trace", "zz"),
        "qntmc 128: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 128: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 128: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 128: the recorder stores the reasoning trace", "keyboard"),
        "bssor 128: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 128: the recorder stores the reasoning trace", "AA"),
        "round 128: the recorder stores the reasoning trace",
    ),
    (("round 128: the angel watches the processor run", "key"), "bssxh 128: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 128: the angel watches the processor run", "lemon"), "csgbq 128: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 128: the angel watches the processor run", "a"), "round 128: the angel watches the processor run"),
    (("round 128: the angel watches the processor run", "zz"), "qntmc 128: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 128: the angel watches the processor run", "AgentU"), "ruyaw 128: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 128: the angel watches the processor run", "keyboard"), "bssor 128: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 128: the angel watches the processor run", "AA"), "round 128: the angel watches the processor run"),
    (("round 128: angle of the vector decides the match", "key"), "bssxh 128: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 128: angle of the vector decides the match", "lemon"), "csgbq 128: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 128: angle of the vector decides the match", "a"), "round 128: angle of the vector decides the match"),
    (("round 128: angle of the vector decides the match", "zz"), "qntmc 128: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 128: angle of the vector decides the match", "AgentU"),
        "ruyaw 128: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 128: angle of the vector decides the match", "keyboard"),
        "bssor 128: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 128: angle of the vector decides the match", "AA"), "round 128: angle of the vector decides the match"),
    (
        ("round 128: the candle burns twice as long at night", "key"),
        "bssxh 128: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 128: the candle burns twice as long at night", "lemon"),
        "csgbq 128: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 128: the candle burns twice as long at night", "a"), "round 128: the candle burns twice as long at night"),
    (
        ("round 128: the candle burns twice as long at night", "zz"),
        "qntmc 128: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 128: the candle burns twice as long at night", "AgentU"),
        "ruyaw 128: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 128: the candle burns twice as long at night", "keyboard"),
        "bssor 128: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 128: the candle burns twice as long at night", "AA"),
        "round 128: the candle burns twice as long at night",
    ),
    (("round 128: a mirror of the universe in one line", "key"), "bssxh 128: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 128: a mirror of the universe in one line", "lemon"), "csgbq 128: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 128: a mirror of the universe in one line", "a"), "round 128: a mirror of the universe in one line"),
    (("round 128: a mirror of the universe in one line", "zz"), "qntmc 128: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 128: a mirror of the universe in one line", "AgentU"), "ruyaw 128: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 128: a mirror of the universe in one line", "keyboard"),
        "bssor 128: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 128: a mirror of the universe in one line", "AA"), "round 128: a mirror of the universe in one line"),
    (("round 128: the queue drains before the storm", "key"), "bssxh 128: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 128: the queue drains before the storm", "lemon"), "csgbq 128: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 128: the queue drains before the storm", "a"), "round 128: the queue drains before the storm"),
    (("round 128: the queue drains before the storm", "zz"), "qntmc 128: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 128: the queue drains before the storm", "AgentU"), "ruyaw 128: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 128: the queue drains before the storm", "keyboard"), "bssor 128: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 128: the queue drains before the storm", "AA"), "round 128: the queue drains before the storm"),
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
