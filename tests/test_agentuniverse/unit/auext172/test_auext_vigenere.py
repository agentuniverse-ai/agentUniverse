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
    (("kitten172", "key"), "umrdil172"),
    (("kitten172", "lemon"), "vmfhry172"),
    (("kitten172", "a"), "kitten172"),
    (("kitten172", "zz"), "jhssdm172"),
    (("kitten172", "AgentU"), "koxgxh172"),
    (("kitten172", "keyboard"), "umrusn172"),
    (("kitten172", "AA"), "kitten172"),
    (("sitting172", "key"), "cmrdmlq172"),
    (("sitting172", "lemon"), "dmfhvyk172"),
    (("sitting172", "a"), "sitting172"),
    (("sitting172", "zz"), "rhsshmf172"),
    (("sitting172", "AgentU"), "soxgbhg172"),
    (("sitting172", "keyboard"), "cmruwnx172"),
    (("sitting172", "AA"), "sitting172"),
    (("agent172", "key"), "kkcxx172"),
    (("agent172", "lemon"), "lkqbg172"),
    (("agent172", "a"), "agent172"),
    (("agent172", "zz"), "zfdms172"),
    (("agent172", "AgentU"), "amiam172"),
    (("agent172", "keyboard"), "kkcoh172"),
    (("agent172", "AA"), "agent172"),
    (("angle172", "key"), "krevi172"),
    (("angle172", "lemon"), "lrszr172"),
    (("angle172", "a"), "angle172"),
    (("angle172", "zz"), "zmfkd172"),
    (("angle172", "AgentU"), "atkyx172"),
    (("angle172", "keyboard"), "krems172"),
    (("angle172", "AA"), "angle172"),
    (("universe172", "key"), "ergfipci172"),
    (("universe172", "lemon"), "frujrcwq172"),
    (("universe172", "a"), "universe172"),
    (("universe172", "zz"), "tmhudqrd172"),
    (("universe172", "AgentU"), "utmixlsk172"),
    (("universe172", "keyboard"), "ergwsrjh172"),
    (("universe172", "AA"), "universe172"),
    (("memory172", "key"), "wikyvw172"),
    (("memory172", "lemon"), "xiycej172"),
    (("memory172", "a"), "memory172"),
    (("memory172", "zz"), "ldlnqx172"),
    (("memory172", "AgentU"), "mkqbks172"),
    (("memory172", "keyboard"), "wikpfy172"),
    (("memory172", "AA"), "memory172"),
    (("stream172", "key"), "cxpoek172"),
    (("stream172", "lemon"), "dxdsnx172"),
    (("stream172", "a"), "stream172"),
    (("stream172", "zz"), "rsqdzl172"),
    (("stream172", "AgentU"), "szvrtg172"),
    (("stream172", "keyboard"), "cxpfom172"),
    (("stream172", "AA"), "stream172"),
    (("context172", "key"), "msldivd172"),
    (("context172", "lemon"), "nszhrix172"),
    (("context172", "a"), "context172"),
    (("context172", "zz"), "bnmsdws172"),
    (("context172", "AgentU"), "curgxrt172"),
    (("context172", "keyboard"), "mslusxk172"),
    (("context172", "AA"), "context172"),
    (("knowledge172", "key"), "urmgpcnkc172"),
    (("knowledge172", "lemon"), "vrakyphss172"),
    (("knowledge172", "a"), "knowledge172"),
    (("knowledge172", "zz"), "jmnvkdcfd172"),
    (("knowledge172", "AgentU"), "ktsjeydmi172"),
    (("knowledge172", "keyboard"), "urmxzeujo172"),
    (("knowledge172", "AA"), "knowledge172"),
    (("vector172", "key"), "fiadsp172"),
    (("vector172", "lemon"), "giohbc172"),
    (("vector172", "a"), "vector172"),
    (("vector172", "zz"), "udbsnq172"),
    (("vector172", "AgentU"), "vkgghl172"),
    (("vector172", "keyboard"), "fiaucr172"),
    (("vector172", "AA"), "vector172"),
    (("processor172", "key"), "zvmmiqcsp172"),
    (("processor172", "lemon"), "avaqrdwaf172"),
    (("processor172", "a"), "processor172"),
    (("processor172", "zz"), "oqnbdrrnq172"),
    (("processor172", "AgentU"), "pxspxmsuv172"),
    (("processor172", "keyboard"), "zvmdssjrb172"),
    (("processor172", "AA"), "processor172"),
    (("reasoning172", "key"), "biycslsre172"),
    (("reasoning172", "lemon"), "cimgbymzu172"),
    (("reasoning172", "a"), "reasoning172"),
    (("reasoning172", "zz"), "qdzrnmhmf172"),
    (("reasoning172", "AgentU"), "rkefhhitk172"),
    (("reasoning172", "keyboard"), "biytcnzqq172"),
    (("reasoning172", "AA"), "reasoning172"),
    (("machine172", "key"), "wearmlo172"),
    (("machine172", "lemon"), "xeovvyi172"),
    (("machine172", "a"), "machine172"),
    (("machine172", "zz"), "lzbghmd172"),
    (("machine172", "AgentU"), "mggubhe172"),
    (("machine172", "keyboard"), "weaiwnv172"),
    (("machine172", "AA"), "machine172"),
    (("learning172", "key"), "viybrgxk172"),
    (("learning172", "lemon"), "wimfatrs172"),
    (("learning172", "a"), "learning172"),
    (("learning172", "zz"), "kdzqmhmf172"),
    (("learning172", "AgentU"), "lkeegcnm172"),
    (("learning172", "keyboard"), "viysbiej172"),
    (("learning172", "AA"), "learning172"),
    (("model172", "key"), "wsbop172"),
    (("model172", "lemon"), "xspsy172"),
    (("model172", "a"), "model172"),
    (("model172", "zz"), "lncdk172"),
    (("model172", "AgentU"), "muhre172"),
    (("model172", "keyboard"), "wsbfz172"),
    (("model172", "AA"), "model172"),
    (("token172", "key"), "dsior172"),
    (("token172", "lemon"), "eswsa172"),
    (("token172", "a"), "token172"),
    (("token172", "zz"), "snjdm172"),
    (("token172", "AgentU"), "tuorg172"),
    (("token172", "keyboard"), "dsifb172"),
    (("token172", "AA"), "token172"),
    (("prompt172", "key"), "zvmwtr172"),
    (("prompt172", "lemon"), "avaace172"),
    (("prompt172", "a"), "prompt172"),
    (("prompt172", "zz"), "oqnlos172"),
    (("prompt172", "AgentU"), "pxszin172"),
    (("prompt172", "keyboard"), "zvmndt172"),
    (("prompt172", "AA"), "prompt172"),
    (("session172", "key"), "ciqcmmx172"),
    (("session172", "lemon"), "diegvzr172"),
    (("session172", "a"), "session172"),
    (("session172", "zz"), "rdrrhnm172"),
    (("session172", "AgentU"), "skwfbin172"),
    (("session172", "keyboard"), "ciqtwoe172"),
    (("session172", "AA"), "session172"),
    (("library172", "key"), "vmzbepi172"),
    (("library172", "lemon"), "wmnfncc172"),
    (("library172", "a"), "library172"),
    (("library172", "zz"), "khaqzqx172"),
    (("library172", "AgentU"), "lofetly172"),
    (("library172", "keyboard"), "vmzsorp172"),
    (("library172", "AA"), "library172"),
    (("service172", "key"), "cipfmao172"),
    (("service172", "lemon"), "didjvni172"),
    (("service172", "a"), "service172"),
    (("service172", "zz"), "rdquhbd172"),
    (("service172", "AgentU"), "skvibwe172"),
    (("service172", "keyboard"), "cipwwcv172"),
    (("service172", "AA"), "service172"),
    (("gateway172", "key"), "qeroayi172"),
    (("gateway172", "lemon"), "refsjlc172"),
    (("gateway172", "a"), "gateway172"),
    (("gateway172", "zz"), "fzsdvzx172"),
    (("gateway172", "AgentU"), "ggxrpuy172"),
    (("gateway172", "keyboard"), "qerfkap172"),
    (("gateway172", "AA"), "gateway172"),
    (("storage172", "key"), "cxmbeeo172"),
    (("storage172", "lemon"), "dxafnri172"),
    (("storage172", "a"), "storage172"),
    (("storage172", "zz"), "rsnqzfd172"),
    (("storage172", "AgentU"), "szsetae172"),
    (("storage172", "keyboard"), "cxmsogv172"),
    (("storage172", "AA"), "storage172"),
    (("network172", "key"), "xirgspu172"),
    (("network172", "lemon"), "yifkbco172"),
    (("network172", "a"), "network172"),
    (("network172", "zz"), "mdsvnqj172"),
    (("network172", "AgentU"), "nkxjhlk172"),
    (("network172", "keyboard"), "xirxcrb172"),
    (("network172", "AA"), "network172"),
    (("latency172", "key"), "verorai172"),
    (("latency172", "lemon"), "wefsanc172"),
    (("latency172", "a"), "latency172"),
    (("latency172", "zz"), "kzsdmbx172"),
    (("latency172", "AgentU"), "lgxrgwy172"),
    (("latency172", "keyboard"), "verfbcp172"),
    (("latency172", "AA"), "latency172"),
    (("buffer172", "key"), "lydpip172"),
    (("buffer172", "lemon"), "myrtrc172"),
    (("buffer172", "a"), "buffer172"),
    (("buffer172", "zz"), "ateedq172"),
    (("buffer172", "AgentU"), "bajsxl172"),
    (("buffer172", "keyboard"), "lydgsr172"),
    (("buffer172", "AA"), "buffer172"),
    (("queue172", "key"), "aycei172"),
    (("queue172", "lemon"), "byqir172"),
    (("queue172", "a"), "queue172"),
    (("queue172", "zz"), "ptdtd172"),
    (("queue172", "AgentU"), "qaihx172"),
    (("queue172", "keyboard"), "aycvs172"),
    (("queue172", "AA"), "queue172"),
    (("worker172", "key"), "gspuip172"),
    (("worker172", "lemon"), "hsdyrc172"),
    (("worker172", "a"), "worker172"),
    (("worker172", "zz"), "vnqjdq172"),
    (("worker172", "AgentU"), "wuvxxl172"),
    (("worker172", "keyboard"), "gsplsr172"),
    (("worker172", "AA"), "worker172"),
    (("kernel172", "key"), "uipxij172"),
    (("kernel172", "lemon"), "vidbrw172"),
    (("kernel172", "a"), "kernel172"),
    (("kernel172", "zz"), "jdqmdk172"),
    (("kernel172", "AgentU"), "kkvaxf172"),
    (("kernel172", "keyboard"), "uiposl172"),
    (("kernel172", "AA"), "kernel172"),
    (("signal172", "key"), "cmexej172"),
    (("signal172", "lemon"), "dmsbnw172"),
    (("signal172", "a"), "signal172"),
    (("signal172", "zz"), "rhfmzk172"),
    (("signal172", "AgentU"), "sokatf172"),
    (("signal172", "keyboard"), "cmeool172"),
    (("signal172", "AA"), "signal172"),
    (("packet172", "key"), "zeauir172"),
    (("packet172", "lemon"), "aeoyre172"),
    (("packet172", "a"), "packet172"),
    (("packet172", "zz"), "ozbjds172"),
    (("packet172", "AgentU"), "pggxxn172"),
    (("packet172", "keyboard"), "zealst172"),
    (("packet172", "AA"), "packet172"),
    (("router172", "key"), "bssdip172"),
    (("router172", "lemon"), "csghrc172"),
    (("router172", "a"), "router172"),
    (("router172", "zz"), "qntsdq172"),
    (("router172", "AgentU"), "ruygxl172"),
    (("router172", "keyboard"), "bssusr172"),
    (("router172", "AA"), "router172"),
    (("cluster172", "key"), "mpscxcb172"),
    (("cluster172", "lemon"), "npgggpv172"),
    (("cluster172", "a"), "cluster172"),
    (("cluster172", "zz"), "bktrsdq172"),
    (("cluster172", "AgentU"), "cryfmyr172"),
    (("cluster172", "keyboard"), "mpsthei172"),
    (("cluster172", "AA"), "cluster172"),
    (("mirror172", "key"), "wmpbsp172"),
    (("mirror172", "lemon"), "xmdfbc172"),
    (("mirror172", "a"), "mirror172"),
    (("mirror172", "zz"), "lhqqnq172"),
    (("mirror172", "AgentU"), "movehl172"),
    (("mirror172", "keyboard"), "wmpscr172"),
    (("mirror172", "AA"), "mirror172"),
    (("filter172", "key"), "pmjdip172"),
    (("filter172", "lemon"), "qmxhrc172"),
    (("filter172", "a"), "filter172"),
    (("filter172", "zz"), "ehksdq172"),
    (("filter172", "AgentU"), "fopgxl172"),
    (("filter172", "keyboard"), "pmjusr172"),
    (("filter172", "AA"), "filter172"),
    (("ranking172", "key"), "belumlq172"),
    (("ranking172", "lemon"), "cezyvyk172"),
    (("ranking172", "a"), "ranking172"),
    (("ranking172", "zz"), "qzmjhmf172"),
    (("ranking172", "AgentU"), "rgrxbhg172"),
    (("ranking172", "keyboard"), "bellwnx172"),
    (("ranking172", "AA"), "ranking172"),
    (("encoding172", "key"), "orayhgxk172"),
    (("encoding172", "lemon"), "procqtrs172"),
    (("encoding172", "a"), "encoding172"),
    (("encoding172", "zz"), "dmbnchmf172"),
    (("encoding172", "AgentU"), "etgbwcnm172"),
    (("encoding172", "keyboard"), "orapriej172"),
    (("encoding172", "AA"), "encoding172"),
    (("mapping172", "key"), "wenzmlq172"),
    (("mapping172", "lemon"), "xebdvyk172"),
    (("mapping172", "a"), "mapping172"),
    (("mapping172", "zz"), "lzoohmf172"),
    (("mapping172", "AgentU"), "mgtcbhg172"),
    (("mapping172", "keyboard"), "wenqwnx172"),
    (("mapping172", "AA"), "mapping172"),
    (("record172", "key"), "biayvb172"),
    (("record172", "lemon"), "cioceo172"),
    (("record172", "a"), "record172"),
    (("record172", "zz"), "qdbnqc172"),
    (("record172", "AgentU"), "rkgbkx172"),
    (("record172", "keyboard"), "biapfd172"),
    (("record172", "AA"), "record172"),
    (("candle172", "key"), "melnpc172"),
    (("candle172", "lemon"), "nezryp172"),
    (("candle172", "a"), "candle172"),
    (("candle172", "zz"), "bzmckd172"),
    (("candle172", "AgentU"), "cgrqey172"),
    (("candle172", "keyboard"), "meleze172"),
    (("candle172", "AA"), "candle172"),
    (("thread172", "key"), "dlpoeb172"),
    (("thread172", "lemon"), "eldsno172"),
    (("thread172", "a"), "thread172"),
    (("thread172", "zz"), "sgqdzc172"),
    (("thread172", "AgentU"), "tnvrtx172"),
    (("thread172", "keyboard"), "dlpfod172"),
    (("thread172", "AA"), "thread172"),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 172: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 172: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "a"),
        "round 172: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 172: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 172: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 172: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", "AA"),
        "round 172: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "key"),
        "bssxh 172: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 172: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "a"),
        "round 172: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 172: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 172: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 172: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", "AA"),
        "round 172: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 172: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 172: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "a"),
        "round 172: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 172: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 172: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 172: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", "AA"),
        "round 172: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 172: the processor reads the record then stops", "key"),
        "bssxh 172: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 172: the processor reads the record then stops", "lemon"),
        "csgbq 172: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 172: the processor reads the record then stops", "a"),
        "round 172: the processor reads the record then stops",
    ),
    (
        ("round 172: the processor reads the record then stops", "zz"),
        "qntmc 172: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 172: the processor reads the record then stops", "AgentU"),
        "ruyaw 172: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 172: the processor reads the record then stops", "keyboard"),
        "bssor 172: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 172: the processor reads the record then stops", "AA"),
        "round 172: the processor reads the record then stops",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "key"),
        "bssxh 172: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "lemon"),
        "csgbq 172: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "a"),
        "round 172: a worker pulls the next task from the queue",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "zz"),
        "qntmc 172: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 172: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "keyboard"),
        "bssor 172: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 172: a worker pulls the next task from the queue", "AA"),
        "round 172: a worker pulls the next task from the queue",
    ),
    (
        ("round 172: signals travel through the network layer", "key"),
        "bssxh 172: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 172: signals travel through the network layer", "lemon"),
        "csgbq 172: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 172: signals travel through the network layer", "a"),
        "round 172: signals travel through the network layer",
    ),
    (
        ("round 172: signals travel through the network layer", "zz"),
        "qntmc 172: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 172: signals travel through the network layer", "AgentU"),
        "ruyaw 172: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 172: signals travel through the network layer", "keyboard"),
        "bssor 172: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 172: signals travel through the network layer", "AA"),
        "round 172: signals travel through the network layer",
    ),
    (
        ("round 172: the gateway routes each request by policy", "key"),
        "bssxh 172: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 172: the gateway routes each request by policy", "lemon"),
        "csgbq 172: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 172: the gateway routes each request by policy", "a"),
        "round 172: the gateway routes each request by policy",
    ),
    (
        ("round 172: the gateway routes each request by policy", "zz"),
        "qntmc 172: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 172: the gateway routes each request by policy", "AgentU"),
        "ruyaw 172: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 172: the gateway routes each request by policy", "keyboard"),
        "bssor 172: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 172: the gateway routes each request by policy", "AA"),
        "round 172: the gateway routes each request by policy",
    ),
    (("round 172: memory grows until the buffer is full", "key"), "bssxh 172: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 172: memory grows until the buffer is full", "lemon"), "csgbq 172: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 172: memory grows until the buffer is full", "a"), "round 172: memory grows until the buffer is full"),
    (("round 172: memory grows until the buffer is full", "zz"), "qntmc 172: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 172: memory grows until the buffer is full", "AgentU"),
        "ruyaw 172: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 172: memory grows until the buffer is full", "keyboard"),
        "bssor 172: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 172: memory grows until the buffer is full", "AA"), "round 172: memory grows until the buffer is full"),
    (("round 172: the cluster mirrors every packet twice", "key"), "bssxh 172: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 172: the cluster mirrors every packet twice", "lemon"),
        "csgbq 172: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 172: the cluster mirrors every packet twice", "a"), "round 172: the cluster mirrors every packet twice"),
    (("round 172: the cluster mirrors every packet twice", "zz"), "qntmc 172: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 172: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 172: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 172: the cluster mirrors every packet twice", "keyboard"),
        "bssor 172: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 172: the cluster mirrors every packet twice", "AA"), "round 172: the cluster mirrors every packet twice"),
    (
        ("round 172: ranking uses tokens learned from the corpus", "key"),
        "bssxh 172: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 172: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", "a"),
        "round 172: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 172: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 172: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 172: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", "AA"),
        "round 172: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 172: a long session ends when the candle dies", "key"),
        "bssxh 172: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 172: a long session ends when the candle dies", "lemon"),
        "csgbq 172: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 172: a long session ends when the candle dies", "a"),
        "round 172: a long session ends when the candle dies",
    ),
    (
        ("round 172: a long session ends when the candle dies", "zz"),
        "qntmc 172: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 172: a long session ends when the candle dies", "AgentU"),
        "ruyaw 172: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 172: a long session ends when the candle dies", "keyboard"),
        "bssor 172: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 172: a long session ends when the candle dies", "AA"),
        "round 172: a long session ends when the candle dies",
    ),
    (("round 172: encode the prompt then map the result", "key"), "bssxh 172: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 172: encode the prompt then map the result", "lemon"), "csgbq 172: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 172: encode the prompt then map the result", "a"), "round 172: encode the prompt then map the result"),
    (("round 172: encode the prompt then map the result", "zz"), "qntmc 172: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 172: encode the prompt then map the result", "AgentU"),
        "ruyaw 172: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 172: encode the prompt then map the result", "keyboard"),
        "bssor 172: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 172: encode the prompt then map the result", "AA"), "round 172: encode the prompt then map the result"),
    (("round 172: the kernel wakes the worker at dawn", "key"), "bssxh 172: rri iovlop ukocc xfo ambocb er neux"),
    (("round 172: the kernel wakes the worker at dawn", "lemon"), "csgbq 172: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 172: the kernel wakes the worker at dawn", "a"), "round 172: the kernel wakes the worker at dawn"),
    (("round 172: the kernel wakes the worker at dawn", "zz"), "qntmc 172: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 172: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 172: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 172: the kernel wakes the worker at dawn", "keyboard"), "bssor 172: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 172: the kernel wakes the worker at dawn", "AA"), "round 172: the kernel wakes the worker at dawn"),
    (("round 172: service latency drops after the patch", "key"), "bssxh 172: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 172: service latency drops after the patch", "lemon"), "csgbq 172: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 172: service latency drops after the patch", "a"), "round 172: service latency drops after the patch"),
    (("round 172: service latency drops after the patch", "zz"), "qntmc 172: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 172: service latency drops after the patch", "AgentU"),
        "ruyaw 172: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 172: service latency drops after the patch", "keyboard"),
        "bssor 172: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 172: service latency drops after the patch", "AA"), "round 172: service latency drops after the patch"),
    (
        ("round 172: the library caches every vector it sees", "key"),
        "bssxh 172: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 172: the library caches every vector it sees", "lemon"),
        "csgbq 172: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 172: the library caches every vector it sees", "a"), "round 172: the library caches every vector it sees"),
    (
        ("round 172: the library caches every vector it sees", "zz"),
        "qntmc 172: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 172: the library caches every vector it sees", "AgentU"),
        "ruyaw 172: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 172: the library caches every vector it sees", "keyboard"),
        "bssor 172: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 172: the library caches every vector it sees", "AA"),
        "round 172: the library caches every vector it sees",
    ),
    (("round 172: agents argue then the debate resolves", "key"), "bssxh 172: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 172: agents argue then the debate resolves", "lemon"), "csgbq 172: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 172: agents argue then the debate resolves", "a"), "round 172: agents argue then the debate resolves"),
    (("round 172: agents argue then the debate resolves", "zz"), "qntmc 172: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 172: agents argue then the debate resolves", "AgentU"),
        "ruyaw 172: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 172: agents argue then the debate resolves", "keyboard"),
        "bssor 172: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 172: agents argue then the debate resolves", "AA"), "round 172: agents argue then the debate resolves"),
    (("round 172: the filter keeps only strong matches", "key"), "bssxh 172: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 172: the filter keeps only strong matches", "lemon"), "csgbq 172: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 172: the filter keeps only strong matches", "a"), "round 172: the filter keeps only strong matches"),
    (("round 172: the filter keeps only strong matches", "zz"), "qntmc 172: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 172: the filter keeps only strong matches", "AgentU"), "ruyaw 172: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 172: the filter keeps only strong matches", "keyboard"),
        "bssor 172: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 172: the filter keeps only strong matches", "AA"), "round 172: the filter keeps only strong matches"),
    (("round 172: the model answers with a short reply", "key"), "bssxh 172: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 172: the model answers with a short reply", "lemon"), "csgbq 172: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 172: the model answers with a short reply", "a"), "round 172: the model answers with a short reply"),
    (("round 172: the model answers with a short reply", "zz"), "qntmc 172: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 172: the model answers with a short reply", "AgentU"), "ruyaw 172: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 172: the model answers with a short reply", "keyboard"),
        "bssor 172: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 172: the model answers with a short reply", "AA"), "round 172: the model answers with a short reply"),
    (
        ("round 172: the recorder stores the reasoning trace", "key"),
        "bssxh 172: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 172: the recorder stores the reasoning trace", "lemon"),
        "csgbq 172: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 172: the recorder stores the reasoning trace", "a"), "round 172: the recorder stores the reasoning trace"),
    (
        ("round 172: the recorder stores the reasoning trace", "zz"),
        "qntmc 172: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 172: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 172: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 172: the recorder stores the reasoning trace", "keyboard"),
        "bssor 172: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 172: the recorder stores the reasoning trace", "AA"),
        "round 172: the recorder stores the reasoning trace",
    ),
    (("round 172: the angel watches the processor run", "key"), "bssxh 172: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 172: the angel watches the processor run", "lemon"), "csgbq 172: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 172: the angel watches the processor run", "a"), "round 172: the angel watches the processor run"),
    (("round 172: the angel watches the processor run", "zz"), "qntmc 172: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 172: the angel watches the processor run", "AgentU"), "ruyaw 172: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 172: the angel watches the processor run", "keyboard"), "bssor 172: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 172: the angel watches the processor run", "AA"), "round 172: the angel watches the processor run"),
    (("round 172: angle of the vector decides the match", "key"), "bssxh 172: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 172: angle of the vector decides the match", "lemon"), "csgbq 172: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 172: angle of the vector decides the match", "a"), "round 172: angle of the vector decides the match"),
    (("round 172: angle of the vector decides the match", "zz"), "qntmc 172: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 172: angle of the vector decides the match", "AgentU"),
        "ruyaw 172: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 172: angle of the vector decides the match", "keyboard"),
        "bssor 172: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 172: angle of the vector decides the match", "AA"), "round 172: angle of the vector decides the match"),
    (
        ("round 172: the candle burns twice as long at night", "key"),
        "bssxh 172: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 172: the candle burns twice as long at night", "lemon"),
        "csgbq 172: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 172: the candle burns twice as long at night", "a"), "round 172: the candle burns twice as long at night"),
    (
        ("round 172: the candle burns twice as long at night", "zz"),
        "qntmc 172: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 172: the candle burns twice as long at night", "AgentU"),
        "ruyaw 172: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 172: the candle burns twice as long at night", "keyboard"),
        "bssor 172: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 172: the candle burns twice as long at night", "AA"),
        "round 172: the candle burns twice as long at night",
    ),
    (("round 172: a mirror of the universe in one line", "key"), "bssxh 172: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 172: a mirror of the universe in one line", "lemon"), "csgbq 172: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 172: a mirror of the universe in one line", "a"), "round 172: a mirror of the universe in one line"),
    (("round 172: a mirror of the universe in one line", "zz"), "qntmc 172: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 172: a mirror of the universe in one line", "AgentU"), "ruyaw 172: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 172: a mirror of the universe in one line", "keyboard"),
        "bssor 172: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 172: a mirror of the universe in one line", "AA"), "round 172: a mirror of the universe in one line"),
    (("round 172: the queue drains before the storm", "key"), "bssxh 172: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 172: the queue drains before the storm", "lemon"), "csgbq 172: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 172: the queue drains before the storm", "a"), "round 172: the queue drains before the storm"),
    (("round 172: the queue drains before the storm", "zz"), "qntmc 172: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 172: the queue drains before the storm", "AgentU"), "ruyaw 172: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 172: the queue drains before the storm", "keyboard"), "bssor 172: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 172: the queue drains before the storm", "AA"), "round 172: the queue drains before the storm"),
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
