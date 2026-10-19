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
    (("kitten196", "key"), "umrdil196"),
    (("kitten196", "lemon"), "vmfhry196"),
    (("kitten196", "a"), "kitten196"),
    (("kitten196", "zz"), "jhssdm196"),
    (("kitten196", "AgentU"), "koxgxh196"),
    (("kitten196", "keyboard"), "umrusn196"),
    (("kitten196", "AA"), "kitten196"),
    (("sitting196", "key"), "cmrdmlq196"),
    (("sitting196", "lemon"), "dmfhvyk196"),
    (("sitting196", "a"), "sitting196"),
    (("sitting196", "zz"), "rhsshmf196"),
    (("sitting196", "AgentU"), "soxgbhg196"),
    (("sitting196", "keyboard"), "cmruwnx196"),
    (("sitting196", "AA"), "sitting196"),
    (("agent196", "key"), "kkcxx196"),
    (("agent196", "lemon"), "lkqbg196"),
    (("agent196", "a"), "agent196"),
    (("agent196", "zz"), "zfdms196"),
    (("agent196", "AgentU"), "amiam196"),
    (("agent196", "keyboard"), "kkcoh196"),
    (("agent196", "AA"), "agent196"),
    (("angle196", "key"), "krevi196"),
    (("angle196", "lemon"), "lrszr196"),
    (("angle196", "a"), "angle196"),
    (("angle196", "zz"), "zmfkd196"),
    (("angle196", "AgentU"), "atkyx196"),
    (("angle196", "keyboard"), "krems196"),
    (("angle196", "AA"), "angle196"),
    (("universe196", "key"), "ergfipci196"),
    (("universe196", "lemon"), "frujrcwq196"),
    (("universe196", "a"), "universe196"),
    (("universe196", "zz"), "tmhudqrd196"),
    (("universe196", "AgentU"), "utmixlsk196"),
    (("universe196", "keyboard"), "ergwsrjh196"),
    (("universe196", "AA"), "universe196"),
    (("memory196", "key"), "wikyvw196"),
    (("memory196", "lemon"), "xiycej196"),
    (("memory196", "a"), "memory196"),
    (("memory196", "zz"), "ldlnqx196"),
    (("memory196", "AgentU"), "mkqbks196"),
    (("memory196", "keyboard"), "wikpfy196"),
    (("memory196", "AA"), "memory196"),
    (("stream196", "key"), "cxpoek196"),
    (("stream196", "lemon"), "dxdsnx196"),
    (("stream196", "a"), "stream196"),
    (("stream196", "zz"), "rsqdzl196"),
    (("stream196", "AgentU"), "szvrtg196"),
    (("stream196", "keyboard"), "cxpfom196"),
    (("stream196", "AA"), "stream196"),
    (("context196", "key"), "msldivd196"),
    (("context196", "lemon"), "nszhrix196"),
    (("context196", "a"), "context196"),
    (("context196", "zz"), "bnmsdws196"),
    (("context196", "AgentU"), "curgxrt196"),
    (("context196", "keyboard"), "mslusxk196"),
    (("context196", "AA"), "context196"),
    (("knowledge196", "key"), "urmgpcnkc196"),
    (("knowledge196", "lemon"), "vrakyphss196"),
    (("knowledge196", "a"), "knowledge196"),
    (("knowledge196", "zz"), "jmnvkdcfd196"),
    (("knowledge196", "AgentU"), "ktsjeydmi196"),
    (("knowledge196", "keyboard"), "urmxzeujo196"),
    (("knowledge196", "AA"), "knowledge196"),
    (("vector196", "key"), "fiadsp196"),
    (("vector196", "lemon"), "giohbc196"),
    (("vector196", "a"), "vector196"),
    (("vector196", "zz"), "udbsnq196"),
    (("vector196", "AgentU"), "vkgghl196"),
    (("vector196", "keyboard"), "fiaucr196"),
    (("vector196", "AA"), "vector196"),
    (("processor196", "key"), "zvmmiqcsp196"),
    (("processor196", "lemon"), "avaqrdwaf196"),
    (("processor196", "a"), "processor196"),
    (("processor196", "zz"), "oqnbdrrnq196"),
    (("processor196", "AgentU"), "pxspxmsuv196"),
    (("processor196", "keyboard"), "zvmdssjrb196"),
    (("processor196", "AA"), "processor196"),
    (("reasoning196", "key"), "biycslsre196"),
    (("reasoning196", "lemon"), "cimgbymzu196"),
    (("reasoning196", "a"), "reasoning196"),
    (("reasoning196", "zz"), "qdzrnmhmf196"),
    (("reasoning196", "AgentU"), "rkefhhitk196"),
    (("reasoning196", "keyboard"), "biytcnzqq196"),
    (("reasoning196", "AA"), "reasoning196"),
    (("machine196", "key"), "wearmlo196"),
    (("machine196", "lemon"), "xeovvyi196"),
    (("machine196", "a"), "machine196"),
    (("machine196", "zz"), "lzbghmd196"),
    (("machine196", "AgentU"), "mggubhe196"),
    (("machine196", "keyboard"), "weaiwnv196"),
    (("machine196", "AA"), "machine196"),
    (("learning196", "key"), "viybrgxk196"),
    (("learning196", "lemon"), "wimfatrs196"),
    (("learning196", "a"), "learning196"),
    (("learning196", "zz"), "kdzqmhmf196"),
    (("learning196", "AgentU"), "lkeegcnm196"),
    (("learning196", "keyboard"), "viysbiej196"),
    (("learning196", "AA"), "learning196"),
    (("model196", "key"), "wsbop196"),
    (("model196", "lemon"), "xspsy196"),
    (("model196", "a"), "model196"),
    (("model196", "zz"), "lncdk196"),
    (("model196", "AgentU"), "muhre196"),
    (("model196", "keyboard"), "wsbfz196"),
    (("model196", "AA"), "model196"),
    (("token196", "key"), "dsior196"),
    (("token196", "lemon"), "eswsa196"),
    (("token196", "a"), "token196"),
    (("token196", "zz"), "snjdm196"),
    (("token196", "AgentU"), "tuorg196"),
    (("token196", "keyboard"), "dsifb196"),
    (("token196", "AA"), "token196"),
    (("prompt196", "key"), "zvmwtr196"),
    (("prompt196", "lemon"), "avaace196"),
    (("prompt196", "a"), "prompt196"),
    (("prompt196", "zz"), "oqnlos196"),
    (("prompt196", "AgentU"), "pxszin196"),
    (("prompt196", "keyboard"), "zvmndt196"),
    (("prompt196", "AA"), "prompt196"),
    (("session196", "key"), "ciqcmmx196"),
    (("session196", "lemon"), "diegvzr196"),
    (("session196", "a"), "session196"),
    (("session196", "zz"), "rdrrhnm196"),
    (("session196", "AgentU"), "skwfbin196"),
    (("session196", "keyboard"), "ciqtwoe196"),
    (("session196", "AA"), "session196"),
    (("library196", "key"), "vmzbepi196"),
    (("library196", "lemon"), "wmnfncc196"),
    (("library196", "a"), "library196"),
    (("library196", "zz"), "khaqzqx196"),
    (("library196", "AgentU"), "lofetly196"),
    (("library196", "keyboard"), "vmzsorp196"),
    (("library196", "AA"), "library196"),
    (("service196", "key"), "cipfmao196"),
    (("service196", "lemon"), "didjvni196"),
    (("service196", "a"), "service196"),
    (("service196", "zz"), "rdquhbd196"),
    (("service196", "AgentU"), "skvibwe196"),
    (("service196", "keyboard"), "cipwwcv196"),
    (("service196", "AA"), "service196"),
    (("gateway196", "key"), "qeroayi196"),
    (("gateway196", "lemon"), "refsjlc196"),
    (("gateway196", "a"), "gateway196"),
    (("gateway196", "zz"), "fzsdvzx196"),
    (("gateway196", "AgentU"), "ggxrpuy196"),
    (("gateway196", "keyboard"), "qerfkap196"),
    (("gateway196", "AA"), "gateway196"),
    (("storage196", "key"), "cxmbeeo196"),
    (("storage196", "lemon"), "dxafnri196"),
    (("storage196", "a"), "storage196"),
    (("storage196", "zz"), "rsnqzfd196"),
    (("storage196", "AgentU"), "szsetae196"),
    (("storage196", "keyboard"), "cxmsogv196"),
    (("storage196", "AA"), "storage196"),
    (("network196", "key"), "xirgspu196"),
    (("network196", "lemon"), "yifkbco196"),
    (("network196", "a"), "network196"),
    (("network196", "zz"), "mdsvnqj196"),
    (("network196", "AgentU"), "nkxjhlk196"),
    (("network196", "keyboard"), "xirxcrb196"),
    (("network196", "AA"), "network196"),
    (("latency196", "key"), "verorai196"),
    (("latency196", "lemon"), "wefsanc196"),
    (("latency196", "a"), "latency196"),
    (("latency196", "zz"), "kzsdmbx196"),
    (("latency196", "AgentU"), "lgxrgwy196"),
    (("latency196", "keyboard"), "verfbcp196"),
    (("latency196", "AA"), "latency196"),
    (("buffer196", "key"), "lydpip196"),
    (("buffer196", "lemon"), "myrtrc196"),
    (("buffer196", "a"), "buffer196"),
    (("buffer196", "zz"), "ateedq196"),
    (("buffer196", "AgentU"), "bajsxl196"),
    (("buffer196", "keyboard"), "lydgsr196"),
    (("buffer196", "AA"), "buffer196"),
    (("queue196", "key"), "aycei196"),
    (("queue196", "lemon"), "byqir196"),
    (("queue196", "a"), "queue196"),
    (("queue196", "zz"), "ptdtd196"),
    (("queue196", "AgentU"), "qaihx196"),
    (("queue196", "keyboard"), "aycvs196"),
    (("queue196", "AA"), "queue196"),
    (("worker196", "key"), "gspuip196"),
    (("worker196", "lemon"), "hsdyrc196"),
    (("worker196", "a"), "worker196"),
    (("worker196", "zz"), "vnqjdq196"),
    (("worker196", "AgentU"), "wuvxxl196"),
    (("worker196", "keyboard"), "gsplsr196"),
    (("worker196", "AA"), "worker196"),
    (("kernel196", "key"), "uipxij196"),
    (("kernel196", "lemon"), "vidbrw196"),
    (("kernel196", "a"), "kernel196"),
    (("kernel196", "zz"), "jdqmdk196"),
    (("kernel196", "AgentU"), "kkvaxf196"),
    (("kernel196", "keyboard"), "uiposl196"),
    (("kernel196", "AA"), "kernel196"),
    (("signal196", "key"), "cmexej196"),
    (("signal196", "lemon"), "dmsbnw196"),
    (("signal196", "a"), "signal196"),
    (("signal196", "zz"), "rhfmzk196"),
    (("signal196", "AgentU"), "sokatf196"),
    (("signal196", "keyboard"), "cmeool196"),
    (("signal196", "AA"), "signal196"),
    (("packet196", "key"), "zeauir196"),
    (("packet196", "lemon"), "aeoyre196"),
    (("packet196", "a"), "packet196"),
    (("packet196", "zz"), "ozbjds196"),
    (("packet196", "AgentU"), "pggxxn196"),
    (("packet196", "keyboard"), "zealst196"),
    (("packet196", "AA"), "packet196"),
    (("router196", "key"), "bssdip196"),
    (("router196", "lemon"), "csghrc196"),
    (("router196", "a"), "router196"),
    (("router196", "zz"), "qntsdq196"),
    (("router196", "AgentU"), "ruygxl196"),
    (("router196", "keyboard"), "bssusr196"),
    (("router196", "AA"), "router196"),
    (("cluster196", "key"), "mpscxcb196"),
    (("cluster196", "lemon"), "npgggpv196"),
    (("cluster196", "a"), "cluster196"),
    (("cluster196", "zz"), "bktrsdq196"),
    (("cluster196", "AgentU"), "cryfmyr196"),
    (("cluster196", "keyboard"), "mpsthei196"),
    (("cluster196", "AA"), "cluster196"),
    (("mirror196", "key"), "wmpbsp196"),
    (("mirror196", "lemon"), "xmdfbc196"),
    (("mirror196", "a"), "mirror196"),
    (("mirror196", "zz"), "lhqqnq196"),
    (("mirror196", "AgentU"), "movehl196"),
    (("mirror196", "keyboard"), "wmpscr196"),
    (("mirror196", "AA"), "mirror196"),
    (("filter196", "key"), "pmjdip196"),
    (("filter196", "lemon"), "qmxhrc196"),
    (("filter196", "a"), "filter196"),
    (("filter196", "zz"), "ehksdq196"),
    (("filter196", "AgentU"), "fopgxl196"),
    (("filter196", "keyboard"), "pmjusr196"),
    (("filter196", "AA"), "filter196"),
    (("ranking196", "key"), "belumlq196"),
    (("ranking196", "lemon"), "cezyvyk196"),
    (("ranking196", "a"), "ranking196"),
    (("ranking196", "zz"), "qzmjhmf196"),
    (("ranking196", "AgentU"), "rgrxbhg196"),
    (("ranking196", "keyboard"), "bellwnx196"),
    (("ranking196", "AA"), "ranking196"),
    (("encoding196", "key"), "orayhgxk196"),
    (("encoding196", "lemon"), "procqtrs196"),
    (("encoding196", "a"), "encoding196"),
    (("encoding196", "zz"), "dmbnchmf196"),
    (("encoding196", "AgentU"), "etgbwcnm196"),
    (("encoding196", "keyboard"), "orapriej196"),
    (("encoding196", "AA"), "encoding196"),
    (("mapping196", "key"), "wenzmlq196"),
    (("mapping196", "lemon"), "xebdvyk196"),
    (("mapping196", "a"), "mapping196"),
    (("mapping196", "zz"), "lzoohmf196"),
    (("mapping196", "AgentU"), "mgtcbhg196"),
    (("mapping196", "keyboard"), "wenqwnx196"),
    (("mapping196", "AA"), "mapping196"),
    (("record196", "key"), "biayvb196"),
    (("record196", "lemon"), "cioceo196"),
    (("record196", "a"), "record196"),
    (("record196", "zz"), "qdbnqc196"),
    (("record196", "AgentU"), "rkgbkx196"),
    (("record196", "keyboard"), "biapfd196"),
    (("record196", "AA"), "record196"),
    (("candle196", "key"), "melnpc196"),
    (("candle196", "lemon"), "nezryp196"),
    (("candle196", "a"), "candle196"),
    (("candle196", "zz"), "bzmckd196"),
    (("candle196", "AgentU"), "cgrqey196"),
    (("candle196", "keyboard"), "meleze196"),
    (("candle196", "AA"), "candle196"),
    (("thread196", "key"), "dlpoeb196"),
    (("thread196", "lemon"), "eldsno196"),
    (("thread196", "a"), "thread196"),
    (("thread196", "zz"), "sgqdzc196"),
    (("thread196", "AgentU"), "tnvrtx196"),
    (("thread196", "keyboard"), "dlpfod196"),
    (("thread196", "AA"), "thread196"),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 196: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 196: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "a"),
        "round 196: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 196: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 196: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 196: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", "AA"),
        "round 196: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "key"),
        "bssxh 196: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 196: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "a"),
        "round 196: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 196: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 196: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 196: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", "AA"),
        "round 196: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 196: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 196: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "a"),
        "round 196: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 196: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 196: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 196: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", "AA"),
        "round 196: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 196: the processor reads the record then stops", "key"),
        "bssxh 196: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 196: the processor reads the record then stops", "lemon"),
        "csgbq 196: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 196: the processor reads the record then stops", "a"),
        "round 196: the processor reads the record then stops",
    ),
    (
        ("round 196: the processor reads the record then stops", "zz"),
        "qntmc 196: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 196: the processor reads the record then stops", "AgentU"),
        "ruyaw 196: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 196: the processor reads the record then stops", "keyboard"),
        "bssor 196: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 196: the processor reads the record then stops", "AA"),
        "round 196: the processor reads the record then stops",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "key"),
        "bssxh 196: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "lemon"),
        "csgbq 196: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "a"),
        "round 196: a worker pulls the next task from the queue",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "zz"),
        "qntmc 196: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 196: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "keyboard"),
        "bssor 196: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 196: a worker pulls the next task from the queue", "AA"),
        "round 196: a worker pulls the next task from the queue",
    ),
    (
        ("round 196: signals travel through the network layer", "key"),
        "bssxh 196: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 196: signals travel through the network layer", "lemon"),
        "csgbq 196: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 196: signals travel through the network layer", "a"),
        "round 196: signals travel through the network layer",
    ),
    (
        ("round 196: signals travel through the network layer", "zz"),
        "qntmc 196: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 196: signals travel through the network layer", "AgentU"),
        "ruyaw 196: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 196: signals travel through the network layer", "keyboard"),
        "bssor 196: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 196: signals travel through the network layer", "AA"),
        "round 196: signals travel through the network layer",
    ),
    (
        ("round 196: the gateway routes each request by policy", "key"),
        "bssxh 196: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 196: the gateway routes each request by policy", "lemon"),
        "csgbq 196: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 196: the gateway routes each request by policy", "a"),
        "round 196: the gateway routes each request by policy",
    ),
    (
        ("round 196: the gateway routes each request by policy", "zz"),
        "qntmc 196: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 196: the gateway routes each request by policy", "AgentU"),
        "ruyaw 196: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 196: the gateway routes each request by policy", "keyboard"),
        "bssor 196: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 196: the gateway routes each request by policy", "AA"),
        "round 196: the gateway routes each request by policy",
    ),
    (("round 196: memory grows until the buffer is full", "key"), "bssxh 196: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 196: memory grows until the buffer is full", "lemon"), "csgbq 196: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 196: memory grows until the buffer is full", "a"), "round 196: memory grows until the buffer is full"),
    (("round 196: memory grows until the buffer is full", "zz"), "qntmc 196: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 196: memory grows until the buffer is full", "AgentU"),
        "ruyaw 196: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 196: memory grows until the buffer is full", "keyboard"),
        "bssor 196: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 196: memory grows until the buffer is full", "AA"), "round 196: memory grows until the buffer is full"),
    (("round 196: the cluster mirrors every packet twice", "key"), "bssxh 196: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 196: the cluster mirrors every packet twice", "lemon"),
        "csgbq 196: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 196: the cluster mirrors every packet twice", "a"), "round 196: the cluster mirrors every packet twice"),
    (("round 196: the cluster mirrors every packet twice", "zz"), "qntmc 196: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 196: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 196: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 196: the cluster mirrors every packet twice", "keyboard"),
        "bssor 196: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 196: the cluster mirrors every packet twice", "AA"), "round 196: the cluster mirrors every packet twice"),
    (
        ("round 196: ranking uses tokens learned from the corpus", "key"),
        "bssxh 196: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 196: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", "a"),
        "round 196: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 196: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 196: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 196: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", "AA"),
        "round 196: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 196: a long session ends when the candle dies", "key"),
        "bssxh 196: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 196: a long session ends when the candle dies", "lemon"),
        "csgbq 196: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 196: a long session ends when the candle dies", "a"),
        "round 196: a long session ends when the candle dies",
    ),
    (
        ("round 196: a long session ends when the candle dies", "zz"),
        "qntmc 196: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 196: a long session ends when the candle dies", "AgentU"),
        "ruyaw 196: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 196: a long session ends when the candle dies", "keyboard"),
        "bssor 196: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 196: a long session ends when the candle dies", "AA"),
        "round 196: a long session ends when the candle dies",
    ),
    (("round 196: encode the prompt then map the result", "key"), "bssxh 196: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 196: encode the prompt then map the result", "lemon"), "csgbq 196: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 196: encode the prompt then map the result", "a"), "round 196: encode the prompt then map the result"),
    (("round 196: encode the prompt then map the result", "zz"), "qntmc 196: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 196: encode the prompt then map the result", "AgentU"),
        "ruyaw 196: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 196: encode the prompt then map the result", "keyboard"),
        "bssor 196: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 196: encode the prompt then map the result", "AA"), "round 196: encode the prompt then map the result"),
    (("round 196: the kernel wakes the worker at dawn", "key"), "bssxh 196: rri iovlop ukocc xfo ambocb er neux"),
    (("round 196: the kernel wakes the worker at dawn", "lemon"), "csgbq 196: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 196: the kernel wakes the worker at dawn", "a"), "round 196: the kernel wakes the worker at dawn"),
    (("round 196: the kernel wakes the worker at dawn", "zz"), "qntmc 196: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 196: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 196: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 196: the kernel wakes the worker at dawn", "keyboard"), "bssor 196: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 196: the kernel wakes the worker at dawn", "AA"), "round 196: the kernel wakes the worker at dawn"),
    (("round 196: service latency drops after the patch", "key"), "bssxh 196: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 196: service latency drops after the patch", "lemon"), "csgbq 196: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 196: service latency drops after the patch", "a"), "round 196: service latency drops after the patch"),
    (("round 196: service latency drops after the patch", "zz"), "qntmc 196: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 196: service latency drops after the patch", "AgentU"),
        "ruyaw 196: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 196: service latency drops after the patch", "keyboard"),
        "bssor 196: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 196: service latency drops after the patch", "AA"), "round 196: service latency drops after the patch"),
    (
        ("round 196: the library caches every vector it sees", "key"),
        "bssxh 196: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 196: the library caches every vector it sees", "lemon"),
        "csgbq 196: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 196: the library caches every vector it sees", "a"), "round 196: the library caches every vector it sees"),
    (
        ("round 196: the library caches every vector it sees", "zz"),
        "qntmc 196: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 196: the library caches every vector it sees", "AgentU"),
        "ruyaw 196: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 196: the library caches every vector it sees", "keyboard"),
        "bssor 196: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 196: the library caches every vector it sees", "AA"),
        "round 196: the library caches every vector it sees",
    ),
    (("round 196: agents argue then the debate resolves", "key"), "bssxh 196: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 196: agents argue then the debate resolves", "lemon"), "csgbq 196: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 196: agents argue then the debate resolves", "a"), "round 196: agents argue then the debate resolves"),
    (("round 196: agents argue then the debate resolves", "zz"), "qntmc 196: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 196: agents argue then the debate resolves", "AgentU"),
        "ruyaw 196: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 196: agents argue then the debate resolves", "keyboard"),
        "bssor 196: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 196: agents argue then the debate resolves", "AA"), "round 196: agents argue then the debate resolves"),
    (("round 196: the filter keeps only strong matches", "key"), "bssxh 196: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 196: the filter keeps only strong matches", "lemon"), "csgbq 196: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 196: the filter keeps only strong matches", "a"), "round 196: the filter keeps only strong matches"),
    (("round 196: the filter keeps only strong matches", "zz"), "qntmc 196: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 196: the filter keeps only strong matches", "AgentU"), "ruyaw 196: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 196: the filter keeps only strong matches", "keyboard"),
        "bssor 196: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 196: the filter keeps only strong matches", "AA"), "round 196: the filter keeps only strong matches"),
    (("round 196: the model answers with a short reply", "key"), "bssxh 196: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 196: the model answers with a short reply", "lemon"), "csgbq 196: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 196: the model answers with a short reply", "a"), "round 196: the model answers with a short reply"),
    (("round 196: the model answers with a short reply", "zz"), "qntmc 196: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 196: the model answers with a short reply", "AgentU"), "ruyaw 196: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 196: the model answers with a short reply", "keyboard"),
        "bssor 196: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 196: the model answers with a short reply", "AA"), "round 196: the model answers with a short reply"),
    (
        ("round 196: the recorder stores the reasoning trace", "key"),
        "bssxh 196: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 196: the recorder stores the reasoning trace", "lemon"),
        "csgbq 196: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 196: the recorder stores the reasoning trace", "a"), "round 196: the recorder stores the reasoning trace"),
    (
        ("round 196: the recorder stores the reasoning trace", "zz"),
        "qntmc 196: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 196: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 196: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 196: the recorder stores the reasoning trace", "keyboard"),
        "bssor 196: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 196: the recorder stores the reasoning trace", "AA"),
        "round 196: the recorder stores the reasoning trace",
    ),
    (("round 196: the angel watches the processor run", "key"), "bssxh 196: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 196: the angel watches the processor run", "lemon"), "csgbq 196: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 196: the angel watches the processor run", "a"), "round 196: the angel watches the processor run"),
    (("round 196: the angel watches the processor run", "zz"), "qntmc 196: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 196: the angel watches the processor run", "AgentU"), "ruyaw 196: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 196: the angel watches the processor run", "keyboard"), "bssor 196: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 196: the angel watches the processor run", "AA"), "round 196: the angel watches the processor run"),
    (("round 196: angle of the vector decides the match", "key"), "bssxh 196: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 196: angle of the vector decides the match", "lemon"), "csgbq 196: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 196: angle of the vector decides the match", "a"), "round 196: angle of the vector decides the match"),
    (("round 196: angle of the vector decides the match", "zz"), "qntmc 196: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 196: angle of the vector decides the match", "AgentU"),
        "ruyaw 196: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 196: angle of the vector decides the match", "keyboard"),
        "bssor 196: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 196: angle of the vector decides the match", "AA"), "round 196: angle of the vector decides the match"),
    (
        ("round 196: the candle burns twice as long at night", "key"),
        "bssxh 196: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 196: the candle burns twice as long at night", "lemon"),
        "csgbq 196: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 196: the candle burns twice as long at night", "a"), "round 196: the candle burns twice as long at night"),
    (
        ("round 196: the candle burns twice as long at night", "zz"),
        "qntmc 196: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 196: the candle burns twice as long at night", "AgentU"),
        "ruyaw 196: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 196: the candle burns twice as long at night", "keyboard"),
        "bssor 196: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 196: the candle burns twice as long at night", "AA"),
        "round 196: the candle burns twice as long at night",
    ),
    (("round 196: a mirror of the universe in one line", "key"), "bssxh 196: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 196: a mirror of the universe in one line", "lemon"), "csgbq 196: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 196: a mirror of the universe in one line", "a"), "round 196: a mirror of the universe in one line"),
    (("round 196: a mirror of the universe in one line", "zz"), "qntmc 196: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 196: a mirror of the universe in one line", "AgentU"), "ruyaw 196: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 196: a mirror of the universe in one line", "keyboard"),
        "bssor 196: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 196: a mirror of the universe in one line", "AA"), "round 196: a mirror of the universe in one line"),
    (("round 196: the queue drains before the storm", "key"), "bssxh 196: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 196: the queue drains before the storm", "lemon"), "csgbq 196: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 196: the queue drains before the storm", "a"), "round 196: the queue drains before the storm"),
    (("round 196: the queue drains before the storm", "zz"), "qntmc 196: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 196: the queue drains before the storm", "AgentU"), "ruyaw 196: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 196: the queue drains before the storm", "keyboard"), "bssor 196: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 196: the queue drains before the storm", "AA"), "round 196: the queue drains before the storm"),
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
