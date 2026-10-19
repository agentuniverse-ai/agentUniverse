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
    (("kitten158", "key"), "umrdil158"),
    (("kitten158", "lemon"), "vmfhry158"),
    (("kitten158", "a"), "kitten158"),
    (("kitten158", "zz"), "jhssdm158"),
    (("kitten158", "AgentU"), "koxgxh158"),
    (("kitten158", "keyboard"), "umrusn158"),
    (("kitten158", "AA"), "kitten158"),
    (("sitting158", "key"), "cmrdmlq158"),
    (("sitting158", "lemon"), "dmfhvyk158"),
    (("sitting158", "a"), "sitting158"),
    (("sitting158", "zz"), "rhsshmf158"),
    (("sitting158", "AgentU"), "soxgbhg158"),
    (("sitting158", "keyboard"), "cmruwnx158"),
    (("sitting158", "AA"), "sitting158"),
    (("agent158", "key"), "kkcxx158"),
    (("agent158", "lemon"), "lkqbg158"),
    (("agent158", "a"), "agent158"),
    (("agent158", "zz"), "zfdms158"),
    (("agent158", "AgentU"), "amiam158"),
    (("agent158", "keyboard"), "kkcoh158"),
    (("agent158", "AA"), "agent158"),
    (("angle158", "key"), "krevi158"),
    (("angle158", "lemon"), "lrszr158"),
    (("angle158", "a"), "angle158"),
    (("angle158", "zz"), "zmfkd158"),
    (("angle158", "AgentU"), "atkyx158"),
    (("angle158", "keyboard"), "krems158"),
    (("angle158", "AA"), "angle158"),
    (("universe158", "key"), "ergfipci158"),
    (("universe158", "lemon"), "frujrcwq158"),
    (("universe158", "a"), "universe158"),
    (("universe158", "zz"), "tmhudqrd158"),
    (("universe158", "AgentU"), "utmixlsk158"),
    (("universe158", "keyboard"), "ergwsrjh158"),
    (("universe158", "AA"), "universe158"),
    (("memory158", "key"), "wikyvw158"),
    (("memory158", "lemon"), "xiycej158"),
    (("memory158", "a"), "memory158"),
    (("memory158", "zz"), "ldlnqx158"),
    (("memory158", "AgentU"), "mkqbks158"),
    (("memory158", "keyboard"), "wikpfy158"),
    (("memory158", "AA"), "memory158"),
    (("stream158", "key"), "cxpoek158"),
    (("stream158", "lemon"), "dxdsnx158"),
    (("stream158", "a"), "stream158"),
    (("stream158", "zz"), "rsqdzl158"),
    (("stream158", "AgentU"), "szvrtg158"),
    (("stream158", "keyboard"), "cxpfom158"),
    (("stream158", "AA"), "stream158"),
    (("context158", "key"), "msldivd158"),
    (("context158", "lemon"), "nszhrix158"),
    (("context158", "a"), "context158"),
    (("context158", "zz"), "bnmsdws158"),
    (("context158", "AgentU"), "curgxrt158"),
    (("context158", "keyboard"), "mslusxk158"),
    (("context158", "AA"), "context158"),
    (("knowledge158", "key"), "urmgpcnkc158"),
    (("knowledge158", "lemon"), "vrakyphss158"),
    (("knowledge158", "a"), "knowledge158"),
    (("knowledge158", "zz"), "jmnvkdcfd158"),
    (("knowledge158", "AgentU"), "ktsjeydmi158"),
    (("knowledge158", "keyboard"), "urmxzeujo158"),
    (("knowledge158", "AA"), "knowledge158"),
    (("vector158", "key"), "fiadsp158"),
    (("vector158", "lemon"), "giohbc158"),
    (("vector158", "a"), "vector158"),
    (("vector158", "zz"), "udbsnq158"),
    (("vector158", "AgentU"), "vkgghl158"),
    (("vector158", "keyboard"), "fiaucr158"),
    (("vector158", "AA"), "vector158"),
    (("processor158", "key"), "zvmmiqcsp158"),
    (("processor158", "lemon"), "avaqrdwaf158"),
    (("processor158", "a"), "processor158"),
    (("processor158", "zz"), "oqnbdrrnq158"),
    (("processor158", "AgentU"), "pxspxmsuv158"),
    (("processor158", "keyboard"), "zvmdssjrb158"),
    (("processor158", "AA"), "processor158"),
    (("reasoning158", "key"), "biycslsre158"),
    (("reasoning158", "lemon"), "cimgbymzu158"),
    (("reasoning158", "a"), "reasoning158"),
    (("reasoning158", "zz"), "qdzrnmhmf158"),
    (("reasoning158", "AgentU"), "rkefhhitk158"),
    (("reasoning158", "keyboard"), "biytcnzqq158"),
    (("reasoning158", "AA"), "reasoning158"),
    (("machine158", "key"), "wearmlo158"),
    (("machine158", "lemon"), "xeovvyi158"),
    (("machine158", "a"), "machine158"),
    (("machine158", "zz"), "lzbghmd158"),
    (("machine158", "AgentU"), "mggubhe158"),
    (("machine158", "keyboard"), "weaiwnv158"),
    (("machine158", "AA"), "machine158"),
    (("learning158", "key"), "viybrgxk158"),
    (("learning158", "lemon"), "wimfatrs158"),
    (("learning158", "a"), "learning158"),
    (("learning158", "zz"), "kdzqmhmf158"),
    (("learning158", "AgentU"), "lkeegcnm158"),
    (("learning158", "keyboard"), "viysbiej158"),
    (("learning158", "AA"), "learning158"),
    (("model158", "key"), "wsbop158"),
    (("model158", "lemon"), "xspsy158"),
    (("model158", "a"), "model158"),
    (("model158", "zz"), "lncdk158"),
    (("model158", "AgentU"), "muhre158"),
    (("model158", "keyboard"), "wsbfz158"),
    (("model158", "AA"), "model158"),
    (("token158", "key"), "dsior158"),
    (("token158", "lemon"), "eswsa158"),
    (("token158", "a"), "token158"),
    (("token158", "zz"), "snjdm158"),
    (("token158", "AgentU"), "tuorg158"),
    (("token158", "keyboard"), "dsifb158"),
    (("token158", "AA"), "token158"),
    (("prompt158", "key"), "zvmwtr158"),
    (("prompt158", "lemon"), "avaace158"),
    (("prompt158", "a"), "prompt158"),
    (("prompt158", "zz"), "oqnlos158"),
    (("prompt158", "AgentU"), "pxszin158"),
    (("prompt158", "keyboard"), "zvmndt158"),
    (("prompt158", "AA"), "prompt158"),
    (("session158", "key"), "ciqcmmx158"),
    (("session158", "lemon"), "diegvzr158"),
    (("session158", "a"), "session158"),
    (("session158", "zz"), "rdrrhnm158"),
    (("session158", "AgentU"), "skwfbin158"),
    (("session158", "keyboard"), "ciqtwoe158"),
    (("session158", "AA"), "session158"),
    (("library158", "key"), "vmzbepi158"),
    (("library158", "lemon"), "wmnfncc158"),
    (("library158", "a"), "library158"),
    (("library158", "zz"), "khaqzqx158"),
    (("library158", "AgentU"), "lofetly158"),
    (("library158", "keyboard"), "vmzsorp158"),
    (("library158", "AA"), "library158"),
    (("service158", "key"), "cipfmao158"),
    (("service158", "lemon"), "didjvni158"),
    (("service158", "a"), "service158"),
    (("service158", "zz"), "rdquhbd158"),
    (("service158", "AgentU"), "skvibwe158"),
    (("service158", "keyboard"), "cipwwcv158"),
    (("service158", "AA"), "service158"),
    (("gateway158", "key"), "qeroayi158"),
    (("gateway158", "lemon"), "refsjlc158"),
    (("gateway158", "a"), "gateway158"),
    (("gateway158", "zz"), "fzsdvzx158"),
    (("gateway158", "AgentU"), "ggxrpuy158"),
    (("gateway158", "keyboard"), "qerfkap158"),
    (("gateway158", "AA"), "gateway158"),
    (("storage158", "key"), "cxmbeeo158"),
    (("storage158", "lemon"), "dxafnri158"),
    (("storage158", "a"), "storage158"),
    (("storage158", "zz"), "rsnqzfd158"),
    (("storage158", "AgentU"), "szsetae158"),
    (("storage158", "keyboard"), "cxmsogv158"),
    (("storage158", "AA"), "storage158"),
    (("network158", "key"), "xirgspu158"),
    (("network158", "lemon"), "yifkbco158"),
    (("network158", "a"), "network158"),
    (("network158", "zz"), "mdsvnqj158"),
    (("network158", "AgentU"), "nkxjhlk158"),
    (("network158", "keyboard"), "xirxcrb158"),
    (("network158", "AA"), "network158"),
    (("latency158", "key"), "verorai158"),
    (("latency158", "lemon"), "wefsanc158"),
    (("latency158", "a"), "latency158"),
    (("latency158", "zz"), "kzsdmbx158"),
    (("latency158", "AgentU"), "lgxrgwy158"),
    (("latency158", "keyboard"), "verfbcp158"),
    (("latency158", "AA"), "latency158"),
    (("buffer158", "key"), "lydpip158"),
    (("buffer158", "lemon"), "myrtrc158"),
    (("buffer158", "a"), "buffer158"),
    (("buffer158", "zz"), "ateedq158"),
    (("buffer158", "AgentU"), "bajsxl158"),
    (("buffer158", "keyboard"), "lydgsr158"),
    (("buffer158", "AA"), "buffer158"),
    (("queue158", "key"), "aycei158"),
    (("queue158", "lemon"), "byqir158"),
    (("queue158", "a"), "queue158"),
    (("queue158", "zz"), "ptdtd158"),
    (("queue158", "AgentU"), "qaihx158"),
    (("queue158", "keyboard"), "aycvs158"),
    (("queue158", "AA"), "queue158"),
    (("worker158", "key"), "gspuip158"),
    (("worker158", "lemon"), "hsdyrc158"),
    (("worker158", "a"), "worker158"),
    (("worker158", "zz"), "vnqjdq158"),
    (("worker158", "AgentU"), "wuvxxl158"),
    (("worker158", "keyboard"), "gsplsr158"),
    (("worker158", "AA"), "worker158"),
    (("kernel158", "key"), "uipxij158"),
    (("kernel158", "lemon"), "vidbrw158"),
    (("kernel158", "a"), "kernel158"),
    (("kernel158", "zz"), "jdqmdk158"),
    (("kernel158", "AgentU"), "kkvaxf158"),
    (("kernel158", "keyboard"), "uiposl158"),
    (("kernel158", "AA"), "kernel158"),
    (("signal158", "key"), "cmexej158"),
    (("signal158", "lemon"), "dmsbnw158"),
    (("signal158", "a"), "signal158"),
    (("signal158", "zz"), "rhfmzk158"),
    (("signal158", "AgentU"), "sokatf158"),
    (("signal158", "keyboard"), "cmeool158"),
    (("signal158", "AA"), "signal158"),
    (("packet158", "key"), "zeauir158"),
    (("packet158", "lemon"), "aeoyre158"),
    (("packet158", "a"), "packet158"),
    (("packet158", "zz"), "ozbjds158"),
    (("packet158", "AgentU"), "pggxxn158"),
    (("packet158", "keyboard"), "zealst158"),
    (("packet158", "AA"), "packet158"),
    (("router158", "key"), "bssdip158"),
    (("router158", "lemon"), "csghrc158"),
    (("router158", "a"), "router158"),
    (("router158", "zz"), "qntsdq158"),
    (("router158", "AgentU"), "ruygxl158"),
    (("router158", "keyboard"), "bssusr158"),
    (("router158", "AA"), "router158"),
    (("cluster158", "key"), "mpscxcb158"),
    (("cluster158", "lemon"), "npgggpv158"),
    (("cluster158", "a"), "cluster158"),
    (("cluster158", "zz"), "bktrsdq158"),
    (("cluster158", "AgentU"), "cryfmyr158"),
    (("cluster158", "keyboard"), "mpsthei158"),
    (("cluster158", "AA"), "cluster158"),
    (("mirror158", "key"), "wmpbsp158"),
    (("mirror158", "lemon"), "xmdfbc158"),
    (("mirror158", "a"), "mirror158"),
    (("mirror158", "zz"), "lhqqnq158"),
    (("mirror158", "AgentU"), "movehl158"),
    (("mirror158", "keyboard"), "wmpscr158"),
    (("mirror158", "AA"), "mirror158"),
    (("filter158", "key"), "pmjdip158"),
    (("filter158", "lemon"), "qmxhrc158"),
    (("filter158", "a"), "filter158"),
    (("filter158", "zz"), "ehksdq158"),
    (("filter158", "AgentU"), "fopgxl158"),
    (("filter158", "keyboard"), "pmjusr158"),
    (("filter158", "AA"), "filter158"),
    (("ranking158", "key"), "belumlq158"),
    (("ranking158", "lemon"), "cezyvyk158"),
    (("ranking158", "a"), "ranking158"),
    (("ranking158", "zz"), "qzmjhmf158"),
    (("ranking158", "AgentU"), "rgrxbhg158"),
    (("ranking158", "keyboard"), "bellwnx158"),
    (("ranking158", "AA"), "ranking158"),
    (("encoding158", "key"), "orayhgxk158"),
    (("encoding158", "lemon"), "procqtrs158"),
    (("encoding158", "a"), "encoding158"),
    (("encoding158", "zz"), "dmbnchmf158"),
    (("encoding158", "AgentU"), "etgbwcnm158"),
    (("encoding158", "keyboard"), "orapriej158"),
    (("encoding158", "AA"), "encoding158"),
    (("mapping158", "key"), "wenzmlq158"),
    (("mapping158", "lemon"), "xebdvyk158"),
    (("mapping158", "a"), "mapping158"),
    (("mapping158", "zz"), "lzoohmf158"),
    (("mapping158", "AgentU"), "mgtcbhg158"),
    (("mapping158", "keyboard"), "wenqwnx158"),
    (("mapping158", "AA"), "mapping158"),
    (("record158", "key"), "biayvb158"),
    (("record158", "lemon"), "cioceo158"),
    (("record158", "a"), "record158"),
    (("record158", "zz"), "qdbnqc158"),
    (("record158", "AgentU"), "rkgbkx158"),
    (("record158", "keyboard"), "biapfd158"),
    (("record158", "AA"), "record158"),
    (("candle158", "key"), "melnpc158"),
    (("candle158", "lemon"), "nezryp158"),
    (("candle158", "a"), "candle158"),
    (("candle158", "zz"), "bzmckd158"),
    (("candle158", "AgentU"), "cgrqey158"),
    (("candle158", "keyboard"), "meleze158"),
    (("candle158", "AA"), "candle158"),
    (("thread158", "key"), "dlpoeb158"),
    (("thread158", "lemon"), "eldsno158"),
    (("thread158", "a"), "thread158"),
    (("thread158", "zz"), "sgqdzc158"),
    (("thread158", "AgentU"), "tnvrtx158"),
    (("thread158", "keyboard"), "dlpfod158"),
    (("thread158", "AA"), "thread158"),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 158: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 158: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "a"),
        "round 158: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 158: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 158: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 158: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", "AA"),
        "round 158: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "key"),
        "bssxh 158: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 158: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "a"),
        "round 158: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 158: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 158: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 158: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", "AA"),
        "round 158: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 158: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 158: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "a"),
        "round 158: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 158: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 158: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 158: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", "AA"),
        "round 158: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 158: the processor reads the record then stops", "key"),
        "bssxh 158: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 158: the processor reads the record then stops", "lemon"),
        "csgbq 158: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 158: the processor reads the record then stops", "a"),
        "round 158: the processor reads the record then stops",
    ),
    (
        ("round 158: the processor reads the record then stops", "zz"),
        "qntmc 158: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 158: the processor reads the record then stops", "AgentU"),
        "ruyaw 158: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 158: the processor reads the record then stops", "keyboard"),
        "bssor 158: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 158: the processor reads the record then stops", "AA"),
        "round 158: the processor reads the record then stops",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "key"),
        "bssxh 158: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "lemon"),
        "csgbq 158: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "a"),
        "round 158: a worker pulls the next task from the queue",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "zz"),
        "qntmc 158: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 158: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "keyboard"),
        "bssor 158: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 158: a worker pulls the next task from the queue", "AA"),
        "round 158: a worker pulls the next task from the queue",
    ),
    (
        ("round 158: signals travel through the network layer", "key"),
        "bssxh 158: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 158: signals travel through the network layer", "lemon"),
        "csgbq 158: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 158: signals travel through the network layer", "a"),
        "round 158: signals travel through the network layer",
    ),
    (
        ("round 158: signals travel through the network layer", "zz"),
        "qntmc 158: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 158: signals travel through the network layer", "AgentU"),
        "ruyaw 158: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 158: signals travel through the network layer", "keyboard"),
        "bssor 158: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 158: signals travel through the network layer", "AA"),
        "round 158: signals travel through the network layer",
    ),
    (
        ("round 158: the gateway routes each request by policy", "key"),
        "bssxh 158: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 158: the gateway routes each request by policy", "lemon"),
        "csgbq 158: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 158: the gateway routes each request by policy", "a"),
        "round 158: the gateway routes each request by policy",
    ),
    (
        ("round 158: the gateway routes each request by policy", "zz"),
        "qntmc 158: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 158: the gateway routes each request by policy", "AgentU"),
        "ruyaw 158: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 158: the gateway routes each request by policy", "keyboard"),
        "bssor 158: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 158: the gateway routes each request by policy", "AA"),
        "round 158: the gateway routes each request by policy",
    ),
    (("round 158: memory grows until the buffer is full", "key"), "bssxh 158: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 158: memory grows until the buffer is full", "lemon"), "csgbq 158: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 158: memory grows until the buffer is full", "a"), "round 158: memory grows until the buffer is full"),
    (("round 158: memory grows until the buffer is full", "zz"), "qntmc 158: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 158: memory grows until the buffer is full", "AgentU"),
        "ruyaw 158: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 158: memory grows until the buffer is full", "keyboard"),
        "bssor 158: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 158: memory grows until the buffer is full", "AA"), "round 158: memory grows until the buffer is full"),
    (("round 158: the cluster mirrors every packet twice", "key"), "bssxh 158: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 158: the cluster mirrors every packet twice", "lemon"),
        "csgbq 158: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 158: the cluster mirrors every packet twice", "a"), "round 158: the cluster mirrors every packet twice"),
    (("round 158: the cluster mirrors every packet twice", "zz"), "qntmc 158: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 158: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 158: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 158: the cluster mirrors every packet twice", "keyboard"),
        "bssor 158: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 158: the cluster mirrors every packet twice", "AA"), "round 158: the cluster mirrors every packet twice"),
    (
        ("round 158: ranking uses tokens learned from the corpus", "key"),
        "bssxh 158: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 158: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", "a"),
        "round 158: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 158: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 158: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 158: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", "AA"),
        "round 158: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 158: a long session ends when the candle dies", "key"),
        "bssxh 158: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 158: a long session ends when the candle dies", "lemon"),
        "csgbq 158: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 158: a long session ends when the candle dies", "a"),
        "round 158: a long session ends when the candle dies",
    ),
    (
        ("round 158: a long session ends when the candle dies", "zz"),
        "qntmc 158: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 158: a long session ends when the candle dies", "AgentU"),
        "ruyaw 158: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 158: a long session ends when the candle dies", "keyboard"),
        "bssor 158: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 158: a long session ends when the candle dies", "AA"),
        "round 158: a long session ends when the candle dies",
    ),
    (("round 158: encode the prompt then map the result", "key"), "bssxh 158: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 158: encode the prompt then map the result", "lemon"), "csgbq 158: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 158: encode the prompt then map the result", "a"), "round 158: encode the prompt then map the result"),
    (("round 158: encode the prompt then map the result", "zz"), "qntmc 158: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 158: encode the prompt then map the result", "AgentU"),
        "ruyaw 158: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 158: encode the prompt then map the result", "keyboard"),
        "bssor 158: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 158: encode the prompt then map the result", "AA"), "round 158: encode the prompt then map the result"),
    (("round 158: the kernel wakes the worker at dawn", "key"), "bssxh 158: rri iovlop ukocc xfo ambocb er neux"),
    (("round 158: the kernel wakes the worker at dawn", "lemon"), "csgbq 158: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 158: the kernel wakes the worker at dawn", "a"), "round 158: the kernel wakes the worker at dawn"),
    (("round 158: the kernel wakes the worker at dawn", "zz"), "qntmc 158: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 158: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 158: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 158: the kernel wakes the worker at dawn", "keyboard"), "bssor 158: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 158: the kernel wakes the worker at dawn", "AA"), "round 158: the kernel wakes the worker at dawn"),
    (("round 158: service latency drops after the patch", "key"), "bssxh 158: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 158: service latency drops after the patch", "lemon"), "csgbq 158: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 158: service latency drops after the patch", "a"), "round 158: service latency drops after the patch"),
    (("round 158: service latency drops after the patch", "zz"), "qntmc 158: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 158: service latency drops after the patch", "AgentU"),
        "ruyaw 158: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 158: service latency drops after the patch", "keyboard"),
        "bssor 158: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 158: service latency drops after the patch", "AA"), "round 158: service latency drops after the patch"),
    (
        ("round 158: the library caches every vector it sees", "key"),
        "bssxh 158: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 158: the library caches every vector it sees", "lemon"),
        "csgbq 158: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 158: the library caches every vector it sees", "a"), "round 158: the library caches every vector it sees"),
    (
        ("round 158: the library caches every vector it sees", "zz"),
        "qntmc 158: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 158: the library caches every vector it sees", "AgentU"),
        "ruyaw 158: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 158: the library caches every vector it sees", "keyboard"),
        "bssor 158: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 158: the library caches every vector it sees", "AA"),
        "round 158: the library caches every vector it sees",
    ),
    (("round 158: agents argue then the debate resolves", "key"), "bssxh 158: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 158: agents argue then the debate resolves", "lemon"), "csgbq 158: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 158: agents argue then the debate resolves", "a"), "round 158: agents argue then the debate resolves"),
    (("round 158: agents argue then the debate resolves", "zz"), "qntmc 158: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 158: agents argue then the debate resolves", "AgentU"),
        "ruyaw 158: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 158: agents argue then the debate resolves", "keyboard"),
        "bssor 158: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 158: agents argue then the debate resolves", "AA"), "round 158: agents argue then the debate resolves"),
    (("round 158: the filter keeps only strong matches", "key"), "bssxh 158: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 158: the filter keeps only strong matches", "lemon"), "csgbq 158: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 158: the filter keeps only strong matches", "a"), "round 158: the filter keeps only strong matches"),
    (("round 158: the filter keeps only strong matches", "zz"), "qntmc 158: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 158: the filter keeps only strong matches", "AgentU"), "ruyaw 158: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 158: the filter keeps only strong matches", "keyboard"),
        "bssor 158: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 158: the filter keeps only strong matches", "AA"), "round 158: the filter keeps only strong matches"),
    (("round 158: the model answers with a short reply", "key"), "bssxh 158: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 158: the model answers with a short reply", "lemon"), "csgbq 158: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 158: the model answers with a short reply", "a"), "round 158: the model answers with a short reply"),
    (("round 158: the model answers with a short reply", "zz"), "qntmc 158: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 158: the model answers with a short reply", "AgentU"), "ruyaw 158: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 158: the model answers with a short reply", "keyboard"),
        "bssor 158: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 158: the model answers with a short reply", "AA"), "round 158: the model answers with a short reply"),
    (
        ("round 158: the recorder stores the reasoning trace", "key"),
        "bssxh 158: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 158: the recorder stores the reasoning trace", "lemon"),
        "csgbq 158: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 158: the recorder stores the reasoning trace", "a"), "round 158: the recorder stores the reasoning trace"),
    (
        ("round 158: the recorder stores the reasoning trace", "zz"),
        "qntmc 158: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 158: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 158: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 158: the recorder stores the reasoning trace", "keyboard"),
        "bssor 158: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 158: the recorder stores the reasoning trace", "AA"),
        "round 158: the recorder stores the reasoning trace",
    ),
    (("round 158: the angel watches the processor run", "key"), "bssxh 158: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 158: the angel watches the processor run", "lemon"), "csgbq 158: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 158: the angel watches the processor run", "a"), "round 158: the angel watches the processor run"),
    (("round 158: the angel watches the processor run", "zz"), "qntmc 158: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 158: the angel watches the processor run", "AgentU"), "ruyaw 158: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 158: the angel watches the processor run", "keyboard"), "bssor 158: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 158: the angel watches the processor run", "AA"), "round 158: the angel watches the processor run"),
    (("round 158: angle of the vector decides the match", "key"), "bssxh 158: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 158: angle of the vector decides the match", "lemon"), "csgbq 158: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 158: angle of the vector decides the match", "a"), "round 158: angle of the vector decides the match"),
    (("round 158: angle of the vector decides the match", "zz"), "qntmc 158: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 158: angle of the vector decides the match", "AgentU"),
        "ruyaw 158: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 158: angle of the vector decides the match", "keyboard"),
        "bssor 158: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 158: angle of the vector decides the match", "AA"), "round 158: angle of the vector decides the match"),
    (
        ("round 158: the candle burns twice as long at night", "key"),
        "bssxh 158: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 158: the candle burns twice as long at night", "lemon"),
        "csgbq 158: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 158: the candle burns twice as long at night", "a"), "round 158: the candle burns twice as long at night"),
    (
        ("round 158: the candle burns twice as long at night", "zz"),
        "qntmc 158: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 158: the candle burns twice as long at night", "AgentU"),
        "ruyaw 158: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 158: the candle burns twice as long at night", "keyboard"),
        "bssor 158: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 158: the candle burns twice as long at night", "AA"),
        "round 158: the candle burns twice as long at night",
    ),
    (("round 158: a mirror of the universe in one line", "key"), "bssxh 158: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 158: a mirror of the universe in one line", "lemon"), "csgbq 158: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 158: a mirror of the universe in one line", "a"), "round 158: a mirror of the universe in one line"),
    (("round 158: a mirror of the universe in one line", "zz"), "qntmc 158: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 158: a mirror of the universe in one line", "AgentU"), "ruyaw 158: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 158: a mirror of the universe in one line", "keyboard"),
        "bssor 158: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 158: a mirror of the universe in one line", "AA"), "round 158: a mirror of the universe in one line"),
    (("round 158: the queue drains before the storm", "key"), "bssxh 158: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 158: the queue drains before the storm", "lemon"), "csgbq 158: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 158: the queue drains before the storm", "a"), "round 158: the queue drains before the storm"),
    (("round 158: the queue drains before the storm", "zz"), "qntmc 158: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 158: the queue drains before the storm", "AgentU"), "ruyaw 158: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 158: the queue drains before the storm", "keyboard"), "bssor 158: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 158: the queue drains before the storm", "AA"), "round 158: the queue drains before the storm"),
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
