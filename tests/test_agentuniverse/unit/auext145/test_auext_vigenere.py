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
    (("kitten145", "key"), "umrdil145"),
    (("kitten145", "lemon"), "vmfhry145"),
    (("kitten145", "a"), "kitten145"),
    (("kitten145", "zz"), "jhssdm145"),
    (("kitten145", "AgentU"), "koxgxh145"),
    (("kitten145", "keyboard"), "umrusn145"),
    (("kitten145", "AA"), "kitten145"),
    (("sitting145", "key"), "cmrdmlq145"),
    (("sitting145", "lemon"), "dmfhvyk145"),
    (("sitting145", "a"), "sitting145"),
    (("sitting145", "zz"), "rhsshmf145"),
    (("sitting145", "AgentU"), "soxgbhg145"),
    (("sitting145", "keyboard"), "cmruwnx145"),
    (("sitting145", "AA"), "sitting145"),
    (("agent145", "key"), "kkcxx145"),
    (("agent145", "lemon"), "lkqbg145"),
    (("agent145", "a"), "agent145"),
    (("agent145", "zz"), "zfdms145"),
    (("agent145", "AgentU"), "amiam145"),
    (("agent145", "keyboard"), "kkcoh145"),
    (("agent145", "AA"), "agent145"),
    (("angle145", "key"), "krevi145"),
    (("angle145", "lemon"), "lrszr145"),
    (("angle145", "a"), "angle145"),
    (("angle145", "zz"), "zmfkd145"),
    (("angle145", "AgentU"), "atkyx145"),
    (("angle145", "keyboard"), "krems145"),
    (("angle145", "AA"), "angle145"),
    (("universe145", "key"), "ergfipci145"),
    (("universe145", "lemon"), "frujrcwq145"),
    (("universe145", "a"), "universe145"),
    (("universe145", "zz"), "tmhudqrd145"),
    (("universe145", "AgentU"), "utmixlsk145"),
    (("universe145", "keyboard"), "ergwsrjh145"),
    (("universe145", "AA"), "universe145"),
    (("memory145", "key"), "wikyvw145"),
    (("memory145", "lemon"), "xiycej145"),
    (("memory145", "a"), "memory145"),
    (("memory145", "zz"), "ldlnqx145"),
    (("memory145", "AgentU"), "mkqbks145"),
    (("memory145", "keyboard"), "wikpfy145"),
    (("memory145", "AA"), "memory145"),
    (("stream145", "key"), "cxpoek145"),
    (("stream145", "lemon"), "dxdsnx145"),
    (("stream145", "a"), "stream145"),
    (("stream145", "zz"), "rsqdzl145"),
    (("stream145", "AgentU"), "szvrtg145"),
    (("stream145", "keyboard"), "cxpfom145"),
    (("stream145", "AA"), "stream145"),
    (("context145", "key"), "msldivd145"),
    (("context145", "lemon"), "nszhrix145"),
    (("context145", "a"), "context145"),
    (("context145", "zz"), "bnmsdws145"),
    (("context145", "AgentU"), "curgxrt145"),
    (("context145", "keyboard"), "mslusxk145"),
    (("context145", "AA"), "context145"),
    (("knowledge145", "key"), "urmgpcnkc145"),
    (("knowledge145", "lemon"), "vrakyphss145"),
    (("knowledge145", "a"), "knowledge145"),
    (("knowledge145", "zz"), "jmnvkdcfd145"),
    (("knowledge145", "AgentU"), "ktsjeydmi145"),
    (("knowledge145", "keyboard"), "urmxzeujo145"),
    (("knowledge145", "AA"), "knowledge145"),
    (("vector145", "key"), "fiadsp145"),
    (("vector145", "lemon"), "giohbc145"),
    (("vector145", "a"), "vector145"),
    (("vector145", "zz"), "udbsnq145"),
    (("vector145", "AgentU"), "vkgghl145"),
    (("vector145", "keyboard"), "fiaucr145"),
    (("vector145", "AA"), "vector145"),
    (("processor145", "key"), "zvmmiqcsp145"),
    (("processor145", "lemon"), "avaqrdwaf145"),
    (("processor145", "a"), "processor145"),
    (("processor145", "zz"), "oqnbdrrnq145"),
    (("processor145", "AgentU"), "pxspxmsuv145"),
    (("processor145", "keyboard"), "zvmdssjrb145"),
    (("processor145", "AA"), "processor145"),
    (("reasoning145", "key"), "biycslsre145"),
    (("reasoning145", "lemon"), "cimgbymzu145"),
    (("reasoning145", "a"), "reasoning145"),
    (("reasoning145", "zz"), "qdzrnmhmf145"),
    (("reasoning145", "AgentU"), "rkefhhitk145"),
    (("reasoning145", "keyboard"), "biytcnzqq145"),
    (("reasoning145", "AA"), "reasoning145"),
    (("machine145", "key"), "wearmlo145"),
    (("machine145", "lemon"), "xeovvyi145"),
    (("machine145", "a"), "machine145"),
    (("machine145", "zz"), "lzbghmd145"),
    (("machine145", "AgentU"), "mggubhe145"),
    (("machine145", "keyboard"), "weaiwnv145"),
    (("machine145", "AA"), "machine145"),
    (("learning145", "key"), "viybrgxk145"),
    (("learning145", "lemon"), "wimfatrs145"),
    (("learning145", "a"), "learning145"),
    (("learning145", "zz"), "kdzqmhmf145"),
    (("learning145", "AgentU"), "lkeegcnm145"),
    (("learning145", "keyboard"), "viysbiej145"),
    (("learning145", "AA"), "learning145"),
    (("model145", "key"), "wsbop145"),
    (("model145", "lemon"), "xspsy145"),
    (("model145", "a"), "model145"),
    (("model145", "zz"), "lncdk145"),
    (("model145", "AgentU"), "muhre145"),
    (("model145", "keyboard"), "wsbfz145"),
    (("model145", "AA"), "model145"),
    (("token145", "key"), "dsior145"),
    (("token145", "lemon"), "eswsa145"),
    (("token145", "a"), "token145"),
    (("token145", "zz"), "snjdm145"),
    (("token145", "AgentU"), "tuorg145"),
    (("token145", "keyboard"), "dsifb145"),
    (("token145", "AA"), "token145"),
    (("prompt145", "key"), "zvmwtr145"),
    (("prompt145", "lemon"), "avaace145"),
    (("prompt145", "a"), "prompt145"),
    (("prompt145", "zz"), "oqnlos145"),
    (("prompt145", "AgentU"), "pxszin145"),
    (("prompt145", "keyboard"), "zvmndt145"),
    (("prompt145", "AA"), "prompt145"),
    (("session145", "key"), "ciqcmmx145"),
    (("session145", "lemon"), "diegvzr145"),
    (("session145", "a"), "session145"),
    (("session145", "zz"), "rdrrhnm145"),
    (("session145", "AgentU"), "skwfbin145"),
    (("session145", "keyboard"), "ciqtwoe145"),
    (("session145", "AA"), "session145"),
    (("library145", "key"), "vmzbepi145"),
    (("library145", "lemon"), "wmnfncc145"),
    (("library145", "a"), "library145"),
    (("library145", "zz"), "khaqzqx145"),
    (("library145", "AgentU"), "lofetly145"),
    (("library145", "keyboard"), "vmzsorp145"),
    (("library145", "AA"), "library145"),
    (("service145", "key"), "cipfmao145"),
    (("service145", "lemon"), "didjvni145"),
    (("service145", "a"), "service145"),
    (("service145", "zz"), "rdquhbd145"),
    (("service145", "AgentU"), "skvibwe145"),
    (("service145", "keyboard"), "cipwwcv145"),
    (("service145", "AA"), "service145"),
    (("gateway145", "key"), "qeroayi145"),
    (("gateway145", "lemon"), "refsjlc145"),
    (("gateway145", "a"), "gateway145"),
    (("gateway145", "zz"), "fzsdvzx145"),
    (("gateway145", "AgentU"), "ggxrpuy145"),
    (("gateway145", "keyboard"), "qerfkap145"),
    (("gateway145", "AA"), "gateway145"),
    (("storage145", "key"), "cxmbeeo145"),
    (("storage145", "lemon"), "dxafnri145"),
    (("storage145", "a"), "storage145"),
    (("storage145", "zz"), "rsnqzfd145"),
    (("storage145", "AgentU"), "szsetae145"),
    (("storage145", "keyboard"), "cxmsogv145"),
    (("storage145", "AA"), "storage145"),
    (("network145", "key"), "xirgspu145"),
    (("network145", "lemon"), "yifkbco145"),
    (("network145", "a"), "network145"),
    (("network145", "zz"), "mdsvnqj145"),
    (("network145", "AgentU"), "nkxjhlk145"),
    (("network145", "keyboard"), "xirxcrb145"),
    (("network145", "AA"), "network145"),
    (("latency145", "key"), "verorai145"),
    (("latency145", "lemon"), "wefsanc145"),
    (("latency145", "a"), "latency145"),
    (("latency145", "zz"), "kzsdmbx145"),
    (("latency145", "AgentU"), "lgxrgwy145"),
    (("latency145", "keyboard"), "verfbcp145"),
    (("latency145", "AA"), "latency145"),
    (("buffer145", "key"), "lydpip145"),
    (("buffer145", "lemon"), "myrtrc145"),
    (("buffer145", "a"), "buffer145"),
    (("buffer145", "zz"), "ateedq145"),
    (("buffer145", "AgentU"), "bajsxl145"),
    (("buffer145", "keyboard"), "lydgsr145"),
    (("buffer145", "AA"), "buffer145"),
    (("queue145", "key"), "aycei145"),
    (("queue145", "lemon"), "byqir145"),
    (("queue145", "a"), "queue145"),
    (("queue145", "zz"), "ptdtd145"),
    (("queue145", "AgentU"), "qaihx145"),
    (("queue145", "keyboard"), "aycvs145"),
    (("queue145", "AA"), "queue145"),
    (("worker145", "key"), "gspuip145"),
    (("worker145", "lemon"), "hsdyrc145"),
    (("worker145", "a"), "worker145"),
    (("worker145", "zz"), "vnqjdq145"),
    (("worker145", "AgentU"), "wuvxxl145"),
    (("worker145", "keyboard"), "gsplsr145"),
    (("worker145", "AA"), "worker145"),
    (("kernel145", "key"), "uipxij145"),
    (("kernel145", "lemon"), "vidbrw145"),
    (("kernel145", "a"), "kernel145"),
    (("kernel145", "zz"), "jdqmdk145"),
    (("kernel145", "AgentU"), "kkvaxf145"),
    (("kernel145", "keyboard"), "uiposl145"),
    (("kernel145", "AA"), "kernel145"),
    (("signal145", "key"), "cmexej145"),
    (("signal145", "lemon"), "dmsbnw145"),
    (("signal145", "a"), "signal145"),
    (("signal145", "zz"), "rhfmzk145"),
    (("signal145", "AgentU"), "sokatf145"),
    (("signal145", "keyboard"), "cmeool145"),
    (("signal145", "AA"), "signal145"),
    (("packet145", "key"), "zeauir145"),
    (("packet145", "lemon"), "aeoyre145"),
    (("packet145", "a"), "packet145"),
    (("packet145", "zz"), "ozbjds145"),
    (("packet145", "AgentU"), "pggxxn145"),
    (("packet145", "keyboard"), "zealst145"),
    (("packet145", "AA"), "packet145"),
    (("router145", "key"), "bssdip145"),
    (("router145", "lemon"), "csghrc145"),
    (("router145", "a"), "router145"),
    (("router145", "zz"), "qntsdq145"),
    (("router145", "AgentU"), "ruygxl145"),
    (("router145", "keyboard"), "bssusr145"),
    (("router145", "AA"), "router145"),
    (("cluster145", "key"), "mpscxcb145"),
    (("cluster145", "lemon"), "npgggpv145"),
    (("cluster145", "a"), "cluster145"),
    (("cluster145", "zz"), "bktrsdq145"),
    (("cluster145", "AgentU"), "cryfmyr145"),
    (("cluster145", "keyboard"), "mpsthei145"),
    (("cluster145", "AA"), "cluster145"),
    (("mirror145", "key"), "wmpbsp145"),
    (("mirror145", "lemon"), "xmdfbc145"),
    (("mirror145", "a"), "mirror145"),
    (("mirror145", "zz"), "lhqqnq145"),
    (("mirror145", "AgentU"), "movehl145"),
    (("mirror145", "keyboard"), "wmpscr145"),
    (("mirror145", "AA"), "mirror145"),
    (("filter145", "key"), "pmjdip145"),
    (("filter145", "lemon"), "qmxhrc145"),
    (("filter145", "a"), "filter145"),
    (("filter145", "zz"), "ehksdq145"),
    (("filter145", "AgentU"), "fopgxl145"),
    (("filter145", "keyboard"), "pmjusr145"),
    (("filter145", "AA"), "filter145"),
    (("ranking145", "key"), "belumlq145"),
    (("ranking145", "lemon"), "cezyvyk145"),
    (("ranking145", "a"), "ranking145"),
    (("ranking145", "zz"), "qzmjhmf145"),
    (("ranking145", "AgentU"), "rgrxbhg145"),
    (("ranking145", "keyboard"), "bellwnx145"),
    (("ranking145", "AA"), "ranking145"),
    (("encoding145", "key"), "orayhgxk145"),
    (("encoding145", "lemon"), "procqtrs145"),
    (("encoding145", "a"), "encoding145"),
    (("encoding145", "zz"), "dmbnchmf145"),
    (("encoding145", "AgentU"), "etgbwcnm145"),
    (("encoding145", "keyboard"), "orapriej145"),
    (("encoding145", "AA"), "encoding145"),
    (("mapping145", "key"), "wenzmlq145"),
    (("mapping145", "lemon"), "xebdvyk145"),
    (("mapping145", "a"), "mapping145"),
    (("mapping145", "zz"), "lzoohmf145"),
    (("mapping145", "AgentU"), "mgtcbhg145"),
    (("mapping145", "keyboard"), "wenqwnx145"),
    (("mapping145", "AA"), "mapping145"),
    (("record145", "key"), "biayvb145"),
    (("record145", "lemon"), "cioceo145"),
    (("record145", "a"), "record145"),
    (("record145", "zz"), "qdbnqc145"),
    (("record145", "AgentU"), "rkgbkx145"),
    (("record145", "keyboard"), "biapfd145"),
    (("record145", "AA"), "record145"),
    (("candle145", "key"), "melnpc145"),
    (("candle145", "lemon"), "nezryp145"),
    (("candle145", "a"), "candle145"),
    (("candle145", "zz"), "bzmckd145"),
    (("candle145", "AgentU"), "cgrqey145"),
    (("candle145", "keyboard"), "meleze145"),
    (("candle145", "AA"), "candle145"),
    (("thread145", "key"), "dlpoeb145"),
    (("thread145", "lemon"), "eldsno145"),
    (("thread145", "a"), "thread145"),
    (("thread145", "zz"), "sgqdzc145"),
    (("thread145", "AgentU"), "tnvrtx145"),
    (("thread145", "keyboard"), "dlpfod145"),
    (("thread145", "AA"), "thread145"),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 145: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 145: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "a"),
        "round 145: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 145: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 145: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 145: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", "AA"),
        "round 145: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "key"),
        "bssxh 145: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 145: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "a"),
        "round 145: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 145: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 145: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 145: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", "AA"),
        "round 145: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 145: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 145: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "a"),
        "round 145: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 145: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 145: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 145: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", "AA"),
        "round 145: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 145: the processor reads the record then stops", "key"),
        "bssxh 145: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 145: the processor reads the record then stops", "lemon"),
        "csgbq 145: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 145: the processor reads the record then stops", "a"),
        "round 145: the processor reads the record then stops",
    ),
    (
        ("round 145: the processor reads the record then stops", "zz"),
        "qntmc 145: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 145: the processor reads the record then stops", "AgentU"),
        "ruyaw 145: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 145: the processor reads the record then stops", "keyboard"),
        "bssor 145: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 145: the processor reads the record then stops", "AA"),
        "round 145: the processor reads the record then stops",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "key"),
        "bssxh 145: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "lemon"),
        "csgbq 145: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "a"),
        "round 145: a worker pulls the next task from the queue",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "zz"),
        "qntmc 145: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 145: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "keyboard"),
        "bssor 145: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 145: a worker pulls the next task from the queue", "AA"),
        "round 145: a worker pulls the next task from the queue",
    ),
    (
        ("round 145: signals travel through the network layer", "key"),
        "bssxh 145: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 145: signals travel through the network layer", "lemon"),
        "csgbq 145: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 145: signals travel through the network layer", "a"),
        "round 145: signals travel through the network layer",
    ),
    (
        ("round 145: signals travel through the network layer", "zz"),
        "qntmc 145: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 145: signals travel through the network layer", "AgentU"),
        "ruyaw 145: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 145: signals travel through the network layer", "keyboard"),
        "bssor 145: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 145: signals travel through the network layer", "AA"),
        "round 145: signals travel through the network layer",
    ),
    (
        ("round 145: the gateway routes each request by policy", "key"),
        "bssxh 145: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 145: the gateway routes each request by policy", "lemon"),
        "csgbq 145: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 145: the gateway routes each request by policy", "a"),
        "round 145: the gateway routes each request by policy",
    ),
    (
        ("round 145: the gateway routes each request by policy", "zz"),
        "qntmc 145: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 145: the gateway routes each request by policy", "AgentU"),
        "ruyaw 145: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 145: the gateway routes each request by policy", "keyboard"),
        "bssor 145: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 145: the gateway routes each request by policy", "AA"),
        "round 145: the gateway routes each request by policy",
    ),
    (("round 145: memory grows until the buffer is full", "key"), "bssxh 145: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 145: memory grows until the buffer is full", "lemon"), "csgbq 145: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 145: memory grows until the buffer is full", "a"), "round 145: memory grows until the buffer is full"),
    (("round 145: memory grows until the buffer is full", "zz"), "qntmc 145: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 145: memory grows until the buffer is full", "AgentU"),
        "ruyaw 145: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 145: memory grows until the buffer is full", "keyboard"),
        "bssor 145: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 145: memory grows until the buffer is full", "AA"), "round 145: memory grows until the buffer is full"),
    (("round 145: the cluster mirrors every packet twice", "key"), "bssxh 145: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 145: the cluster mirrors every packet twice", "lemon"),
        "csgbq 145: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 145: the cluster mirrors every packet twice", "a"), "round 145: the cluster mirrors every packet twice"),
    (("round 145: the cluster mirrors every packet twice", "zz"), "qntmc 145: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 145: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 145: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 145: the cluster mirrors every packet twice", "keyboard"),
        "bssor 145: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 145: the cluster mirrors every packet twice", "AA"), "round 145: the cluster mirrors every packet twice"),
    (
        ("round 145: ranking uses tokens learned from the corpus", "key"),
        "bssxh 145: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 145: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", "a"),
        "round 145: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 145: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 145: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 145: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", "AA"),
        "round 145: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 145: a long session ends when the candle dies", "key"),
        "bssxh 145: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 145: a long session ends when the candle dies", "lemon"),
        "csgbq 145: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 145: a long session ends when the candle dies", "a"),
        "round 145: a long session ends when the candle dies",
    ),
    (
        ("round 145: a long session ends when the candle dies", "zz"),
        "qntmc 145: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 145: a long session ends when the candle dies", "AgentU"),
        "ruyaw 145: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 145: a long session ends when the candle dies", "keyboard"),
        "bssor 145: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 145: a long session ends when the candle dies", "AA"),
        "round 145: a long session ends when the candle dies",
    ),
    (("round 145: encode the prompt then map the result", "key"), "bssxh 145: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 145: encode the prompt then map the result", "lemon"), "csgbq 145: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 145: encode the prompt then map the result", "a"), "round 145: encode the prompt then map the result"),
    (("round 145: encode the prompt then map the result", "zz"), "qntmc 145: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 145: encode the prompt then map the result", "AgentU"),
        "ruyaw 145: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 145: encode the prompt then map the result", "keyboard"),
        "bssor 145: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 145: encode the prompt then map the result", "AA"), "round 145: encode the prompt then map the result"),
    (("round 145: the kernel wakes the worker at dawn", "key"), "bssxh 145: rri iovlop ukocc xfo ambocb er neux"),
    (("round 145: the kernel wakes the worker at dawn", "lemon"), "csgbq 145: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 145: the kernel wakes the worker at dawn", "a"), "round 145: the kernel wakes the worker at dawn"),
    (("round 145: the kernel wakes the worker at dawn", "zz"), "qntmc 145: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 145: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 145: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 145: the kernel wakes the worker at dawn", "keyboard"), "bssor 145: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 145: the kernel wakes the worker at dawn", "AA"), "round 145: the kernel wakes the worker at dawn"),
    (("round 145: service latency drops after the patch", "key"), "bssxh 145: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 145: service latency drops after the patch", "lemon"), "csgbq 145: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 145: service latency drops after the patch", "a"), "round 145: service latency drops after the patch"),
    (("round 145: service latency drops after the patch", "zz"), "qntmc 145: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 145: service latency drops after the patch", "AgentU"),
        "ruyaw 145: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 145: service latency drops after the patch", "keyboard"),
        "bssor 145: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 145: service latency drops after the patch", "AA"), "round 145: service latency drops after the patch"),
    (
        ("round 145: the library caches every vector it sees", "key"),
        "bssxh 145: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 145: the library caches every vector it sees", "lemon"),
        "csgbq 145: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 145: the library caches every vector it sees", "a"), "round 145: the library caches every vector it sees"),
    (
        ("round 145: the library caches every vector it sees", "zz"),
        "qntmc 145: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 145: the library caches every vector it sees", "AgentU"),
        "ruyaw 145: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 145: the library caches every vector it sees", "keyboard"),
        "bssor 145: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 145: the library caches every vector it sees", "AA"),
        "round 145: the library caches every vector it sees",
    ),
    (("round 145: agents argue then the debate resolves", "key"), "bssxh 145: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 145: agents argue then the debate resolves", "lemon"), "csgbq 145: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 145: agents argue then the debate resolves", "a"), "round 145: agents argue then the debate resolves"),
    (("round 145: agents argue then the debate resolves", "zz"), "qntmc 145: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 145: agents argue then the debate resolves", "AgentU"),
        "ruyaw 145: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 145: agents argue then the debate resolves", "keyboard"),
        "bssor 145: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 145: agents argue then the debate resolves", "AA"), "round 145: agents argue then the debate resolves"),
    (("round 145: the filter keeps only strong matches", "key"), "bssxh 145: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 145: the filter keeps only strong matches", "lemon"), "csgbq 145: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 145: the filter keeps only strong matches", "a"), "round 145: the filter keeps only strong matches"),
    (("round 145: the filter keeps only strong matches", "zz"), "qntmc 145: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 145: the filter keeps only strong matches", "AgentU"), "ruyaw 145: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 145: the filter keeps only strong matches", "keyboard"),
        "bssor 145: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 145: the filter keeps only strong matches", "AA"), "round 145: the filter keeps only strong matches"),
    (("round 145: the model answers with a short reply", "key"), "bssxh 145: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 145: the model answers with a short reply", "lemon"), "csgbq 145: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 145: the model answers with a short reply", "a"), "round 145: the model answers with a short reply"),
    (("round 145: the model answers with a short reply", "zz"), "qntmc 145: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 145: the model answers with a short reply", "AgentU"), "ruyaw 145: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 145: the model answers with a short reply", "keyboard"),
        "bssor 145: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 145: the model answers with a short reply", "AA"), "round 145: the model answers with a short reply"),
    (
        ("round 145: the recorder stores the reasoning trace", "key"),
        "bssxh 145: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 145: the recorder stores the reasoning trace", "lemon"),
        "csgbq 145: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 145: the recorder stores the reasoning trace", "a"), "round 145: the recorder stores the reasoning trace"),
    (
        ("round 145: the recorder stores the reasoning trace", "zz"),
        "qntmc 145: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 145: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 145: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 145: the recorder stores the reasoning trace", "keyboard"),
        "bssor 145: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 145: the recorder stores the reasoning trace", "AA"),
        "round 145: the recorder stores the reasoning trace",
    ),
    (("round 145: the angel watches the processor run", "key"), "bssxh 145: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 145: the angel watches the processor run", "lemon"), "csgbq 145: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 145: the angel watches the processor run", "a"), "round 145: the angel watches the processor run"),
    (("round 145: the angel watches the processor run", "zz"), "qntmc 145: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 145: the angel watches the processor run", "AgentU"), "ruyaw 145: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 145: the angel watches the processor run", "keyboard"), "bssor 145: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 145: the angel watches the processor run", "AA"), "round 145: the angel watches the processor run"),
    (("round 145: angle of the vector decides the match", "key"), "bssxh 145: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 145: angle of the vector decides the match", "lemon"), "csgbq 145: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 145: angle of the vector decides the match", "a"), "round 145: angle of the vector decides the match"),
    (("round 145: angle of the vector decides the match", "zz"), "qntmc 145: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 145: angle of the vector decides the match", "AgentU"),
        "ruyaw 145: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 145: angle of the vector decides the match", "keyboard"),
        "bssor 145: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 145: angle of the vector decides the match", "AA"), "round 145: angle of the vector decides the match"),
    (
        ("round 145: the candle burns twice as long at night", "key"),
        "bssxh 145: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 145: the candle burns twice as long at night", "lemon"),
        "csgbq 145: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 145: the candle burns twice as long at night", "a"), "round 145: the candle burns twice as long at night"),
    (
        ("round 145: the candle burns twice as long at night", "zz"),
        "qntmc 145: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 145: the candle burns twice as long at night", "AgentU"),
        "ruyaw 145: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 145: the candle burns twice as long at night", "keyboard"),
        "bssor 145: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 145: the candle burns twice as long at night", "AA"),
        "round 145: the candle burns twice as long at night",
    ),
    (("round 145: a mirror of the universe in one line", "key"), "bssxh 145: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 145: a mirror of the universe in one line", "lemon"), "csgbq 145: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 145: a mirror of the universe in one line", "a"), "round 145: a mirror of the universe in one line"),
    (("round 145: a mirror of the universe in one line", "zz"), "qntmc 145: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 145: a mirror of the universe in one line", "AgentU"), "ruyaw 145: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 145: a mirror of the universe in one line", "keyboard"),
        "bssor 145: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 145: a mirror of the universe in one line", "AA"), "round 145: a mirror of the universe in one line"),
    (("round 145: the queue drains before the storm", "key"), "bssxh 145: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 145: the queue drains before the storm", "lemon"), "csgbq 145: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 145: the queue drains before the storm", "a"), "round 145: the queue drains before the storm"),
    (("round 145: the queue drains before the storm", "zz"), "qntmc 145: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 145: the queue drains before the storm", "AgentU"), "ruyaw 145: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 145: the queue drains before the storm", "keyboard"), "bssor 145: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 145: the queue drains before the storm", "AA"), "round 145: the queue drains before the storm"),
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
