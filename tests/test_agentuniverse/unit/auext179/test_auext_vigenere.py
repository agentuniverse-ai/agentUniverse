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
    (("kitten179", "key"), "umrdil179"),
    (("kitten179", "lemon"), "vmfhry179"),
    (("kitten179", "a"), "kitten179"),
    (("kitten179", "zz"), "jhssdm179"),
    (("kitten179", "AgentU"), "koxgxh179"),
    (("kitten179", "keyboard"), "umrusn179"),
    (("kitten179", "AA"), "kitten179"),
    (("sitting179", "key"), "cmrdmlq179"),
    (("sitting179", "lemon"), "dmfhvyk179"),
    (("sitting179", "a"), "sitting179"),
    (("sitting179", "zz"), "rhsshmf179"),
    (("sitting179", "AgentU"), "soxgbhg179"),
    (("sitting179", "keyboard"), "cmruwnx179"),
    (("sitting179", "AA"), "sitting179"),
    (("agent179", "key"), "kkcxx179"),
    (("agent179", "lemon"), "lkqbg179"),
    (("agent179", "a"), "agent179"),
    (("agent179", "zz"), "zfdms179"),
    (("agent179", "AgentU"), "amiam179"),
    (("agent179", "keyboard"), "kkcoh179"),
    (("agent179", "AA"), "agent179"),
    (("angle179", "key"), "krevi179"),
    (("angle179", "lemon"), "lrszr179"),
    (("angle179", "a"), "angle179"),
    (("angle179", "zz"), "zmfkd179"),
    (("angle179", "AgentU"), "atkyx179"),
    (("angle179", "keyboard"), "krems179"),
    (("angle179", "AA"), "angle179"),
    (("universe179", "key"), "ergfipci179"),
    (("universe179", "lemon"), "frujrcwq179"),
    (("universe179", "a"), "universe179"),
    (("universe179", "zz"), "tmhudqrd179"),
    (("universe179", "AgentU"), "utmixlsk179"),
    (("universe179", "keyboard"), "ergwsrjh179"),
    (("universe179", "AA"), "universe179"),
    (("memory179", "key"), "wikyvw179"),
    (("memory179", "lemon"), "xiycej179"),
    (("memory179", "a"), "memory179"),
    (("memory179", "zz"), "ldlnqx179"),
    (("memory179", "AgentU"), "mkqbks179"),
    (("memory179", "keyboard"), "wikpfy179"),
    (("memory179", "AA"), "memory179"),
    (("stream179", "key"), "cxpoek179"),
    (("stream179", "lemon"), "dxdsnx179"),
    (("stream179", "a"), "stream179"),
    (("stream179", "zz"), "rsqdzl179"),
    (("stream179", "AgentU"), "szvrtg179"),
    (("stream179", "keyboard"), "cxpfom179"),
    (("stream179", "AA"), "stream179"),
    (("context179", "key"), "msldivd179"),
    (("context179", "lemon"), "nszhrix179"),
    (("context179", "a"), "context179"),
    (("context179", "zz"), "bnmsdws179"),
    (("context179", "AgentU"), "curgxrt179"),
    (("context179", "keyboard"), "mslusxk179"),
    (("context179", "AA"), "context179"),
    (("knowledge179", "key"), "urmgpcnkc179"),
    (("knowledge179", "lemon"), "vrakyphss179"),
    (("knowledge179", "a"), "knowledge179"),
    (("knowledge179", "zz"), "jmnvkdcfd179"),
    (("knowledge179", "AgentU"), "ktsjeydmi179"),
    (("knowledge179", "keyboard"), "urmxzeujo179"),
    (("knowledge179", "AA"), "knowledge179"),
    (("vector179", "key"), "fiadsp179"),
    (("vector179", "lemon"), "giohbc179"),
    (("vector179", "a"), "vector179"),
    (("vector179", "zz"), "udbsnq179"),
    (("vector179", "AgentU"), "vkgghl179"),
    (("vector179", "keyboard"), "fiaucr179"),
    (("vector179", "AA"), "vector179"),
    (("processor179", "key"), "zvmmiqcsp179"),
    (("processor179", "lemon"), "avaqrdwaf179"),
    (("processor179", "a"), "processor179"),
    (("processor179", "zz"), "oqnbdrrnq179"),
    (("processor179", "AgentU"), "pxspxmsuv179"),
    (("processor179", "keyboard"), "zvmdssjrb179"),
    (("processor179", "AA"), "processor179"),
    (("reasoning179", "key"), "biycslsre179"),
    (("reasoning179", "lemon"), "cimgbymzu179"),
    (("reasoning179", "a"), "reasoning179"),
    (("reasoning179", "zz"), "qdzrnmhmf179"),
    (("reasoning179", "AgentU"), "rkefhhitk179"),
    (("reasoning179", "keyboard"), "biytcnzqq179"),
    (("reasoning179", "AA"), "reasoning179"),
    (("machine179", "key"), "wearmlo179"),
    (("machine179", "lemon"), "xeovvyi179"),
    (("machine179", "a"), "machine179"),
    (("machine179", "zz"), "lzbghmd179"),
    (("machine179", "AgentU"), "mggubhe179"),
    (("machine179", "keyboard"), "weaiwnv179"),
    (("machine179", "AA"), "machine179"),
    (("learning179", "key"), "viybrgxk179"),
    (("learning179", "lemon"), "wimfatrs179"),
    (("learning179", "a"), "learning179"),
    (("learning179", "zz"), "kdzqmhmf179"),
    (("learning179", "AgentU"), "lkeegcnm179"),
    (("learning179", "keyboard"), "viysbiej179"),
    (("learning179", "AA"), "learning179"),
    (("model179", "key"), "wsbop179"),
    (("model179", "lemon"), "xspsy179"),
    (("model179", "a"), "model179"),
    (("model179", "zz"), "lncdk179"),
    (("model179", "AgentU"), "muhre179"),
    (("model179", "keyboard"), "wsbfz179"),
    (("model179", "AA"), "model179"),
    (("token179", "key"), "dsior179"),
    (("token179", "lemon"), "eswsa179"),
    (("token179", "a"), "token179"),
    (("token179", "zz"), "snjdm179"),
    (("token179", "AgentU"), "tuorg179"),
    (("token179", "keyboard"), "dsifb179"),
    (("token179", "AA"), "token179"),
    (("prompt179", "key"), "zvmwtr179"),
    (("prompt179", "lemon"), "avaace179"),
    (("prompt179", "a"), "prompt179"),
    (("prompt179", "zz"), "oqnlos179"),
    (("prompt179", "AgentU"), "pxszin179"),
    (("prompt179", "keyboard"), "zvmndt179"),
    (("prompt179", "AA"), "prompt179"),
    (("session179", "key"), "ciqcmmx179"),
    (("session179", "lemon"), "diegvzr179"),
    (("session179", "a"), "session179"),
    (("session179", "zz"), "rdrrhnm179"),
    (("session179", "AgentU"), "skwfbin179"),
    (("session179", "keyboard"), "ciqtwoe179"),
    (("session179", "AA"), "session179"),
    (("library179", "key"), "vmzbepi179"),
    (("library179", "lemon"), "wmnfncc179"),
    (("library179", "a"), "library179"),
    (("library179", "zz"), "khaqzqx179"),
    (("library179", "AgentU"), "lofetly179"),
    (("library179", "keyboard"), "vmzsorp179"),
    (("library179", "AA"), "library179"),
    (("service179", "key"), "cipfmao179"),
    (("service179", "lemon"), "didjvni179"),
    (("service179", "a"), "service179"),
    (("service179", "zz"), "rdquhbd179"),
    (("service179", "AgentU"), "skvibwe179"),
    (("service179", "keyboard"), "cipwwcv179"),
    (("service179", "AA"), "service179"),
    (("gateway179", "key"), "qeroayi179"),
    (("gateway179", "lemon"), "refsjlc179"),
    (("gateway179", "a"), "gateway179"),
    (("gateway179", "zz"), "fzsdvzx179"),
    (("gateway179", "AgentU"), "ggxrpuy179"),
    (("gateway179", "keyboard"), "qerfkap179"),
    (("gateway179", "AA"), "gateway179"),
    (("storage179", "key"), "cxmbeeo179"),
    (("storage179", "lemon"), "dxafnri179"),
    (("storage179", "a"), "storage179"),
    (("storage179", "zz"), "rsnqzfd179"),
    (("storage179", "AgentU"), "szsetae179"),
    (("storage179", "keyboard"), "cxmsogv179"),
    (("storage179", "AA"), "storage179"),
    (("network179", "key"), "xirgspu179"),
    (("network179", "lemon"), "yifkbco179"),
    (("network179", "a"), "network179"),
    (("network179", "zz"), "mdsvnqj179"),
    (("network179", "AgentU"), "nkxjhlk179"),
    (("network179", "keyboard"), "xirxcrb179"),
    (("network179", "AA"), "network179"),
    (("latency179", "key"), "verorai179"),
    (("latency179", "lemon"), "wefsanc179"),
    (("latency179", "a"), "latency179"),
    (("latency179", "zz"), "kzsdmbx179"),
    (("latency179", "AgentU"), "lgxrgwy179"),
    (("latency179", "keyboard"), "verfbcp179"),
    (("latency179", "AA"), "latency179"),
    (("buffer179", "key"), "lydpip179"),
    (("buffer179", "lemon"), "myrtrc179"),
    (("buffer179", "a"), "buffer179"),
    (("buffer179", "zz"), "ateedq179"),
    (("buffer179", "AgentU"), "bajsxl179"),
    (("buffer179", "keyboard"), "lydgsr179"),
    (("buffer179", "AA"), "buffer179"),
    (("queue179", "key"), "aycei179"),
    (("queue179", "lemon"), "byqir179"),
    (("queue179", "a"), "queue179"),
    (("queue179", "zz"), "ptdtd179"),
    (("queue179", "AgentU"), "qaihx179"),
    (("queue179", "keyboard"), "aycvs179"),
    (("queue179", "AA"), "queue179"),
    (("worker179", "key"), "gspuip179"),
    (("worker179", "lemon"), "hsdyrc179"),
    (("worker179", "a"), "worker179"),
    (("worker179", "zz"), "vnqjdq179"),
    (("worker179", "AgentU"), "wuvxxl179"),
    (("worker179", "keyboard"), "gsplsr179"),
    (("worker179", "AA"), "worker179"),
    (("kernel179", "key"), "uipxij179"),
    (("kernel179", "lemon"), "vidbrw179"),
    (("kernel179", "a"), "kernel179"),
    (("kernel179", "zz"), "jdqmdk179"),
    (("kernel179", "AgentU"), "kkvaxf179"),
    (("kernel179", "keyboard"), "uiposl179"),
    (("kernel179", "AA"), "kernel179"),
    (("signal179", "key"), "cmexej179"),
    (("signal179", "lemon"), "dmsbnw179"),
    (("signal179", "a"), "signal179"),
    (("signal179", "zz"), "rhfmzk179"),
    (("signal179", "AgentU"), "sokatf179"),
    (("signal179", "keyboard"), "cmeool179"),
    (("signal179", "AA"), "signal179"),
    (("packet179", "key"), "zeauir179"),
    (("packet179", "lemon"), "aeoyre179"),
    (("packet179", "a"), "packet179"),
    (("packet179", "zz"), "ozbjds179"),
    (("packet179", "AgentU"), "pggxxn179"),
    (("packet179", "keyboard"), "zealst179"),
    (("packet179", "AA"), "packet179"),
    (("router179", "key"), "bssdip179"),
    (("router179", "lemon"), "csghrc179"),
    (("router179", "a"), "router179"),
    (("router179", "zz"), "qntsdq179"),
    (("router179", "AgentU"), "ruygxl179"),
    (("router179", "keyboard"), "bssusr179"),
    (("router179", "AA"), "router179"),
    (("cluster179", "key"), "mpscxcb179"),
    (("cluster179", "lemon"), "npgggpv179"),
    (("cluster179", "a"), "cluster179"),
    (("cluster179", "zz"), "bktrsdq179"),
    (("cluster179", "AgentU"), "cryfmyr179"),
    (("cluster179", "keyboard"), "mpsthei179"),
    (("cluster179", "AA"), "cluster179"),
    (("mirror179", "key"), "wmpbsp179"),
    (("mirror179", "lemon"), "xmdfbc179"),
    (("mirror179", "a"), "mirror179"),
    (("mirror179", "zz"), "lhqqnq179"),
    (("mirror179", "AgentU"), "movehl179"),
    (("mirror179", "keyboard"), "wmpscr179"),
    (("mirror179", "AA"), "mirror179"),
    (("filter179", "key"), "pmjdip179"),
    (("filter179", "lemon"), "qmxhrc179"),
    (("filter179", "a"), "filter179"),
    (("filter179", "zz"), "ehksdq179"),
    (("filter179", "AgentU"), "fopgxl179"),
    (("filter179", "keyboard"), "pmjusr179"),
    (("filter179", "AA"), "filter179"),
    (("ranking179", "key"), "belumlq179"),
    (("ranking179", "lemon"), "cezyvyk179"),
    (("ranking179", "a"), "ranking179"),
    (("ranking179", "zz"), "qzmjhmf179"),
    (("ranking179", "AgentU"), "rgrxbhg179"),
    (("ranking179", "keyboard"), "bellwnx179"),
    (("ranking179", "AA"), "ranking179"),
    (("encoding179", "key"), "orayhgxk179"),
    (("encoding179", "lemon"), "procqtrs179"),
    (("encoding179", "a"), "encoding179"),
    (("encoding179", "zz"), "dmbnchmf179"),
    (("encoding179", "AgentU"), "etgbwcnm179"),
    (("encoding179", "keyboard"), "orapriej179"),
    (("encoding179", "AA"), "encoding179"),
    (("mapping179", "key"), "wenzmlq179"),
    (("mapping179", "lemon"), "xebdvyk179"),
    (("mapping179", "a"), "mapping179"),
    (("mapping179", "zz"), "lzoohmf179"),
    (("mapping179", "AgentU"), "mgtcbhg179"),
    (("mapping179", "keyboard"), "wenqwnx179"),
    (("mapping179", "AA"), "mapping179"),
    (("record179", "key"), "biayvb179"),
    (("record179", "lemon"), "cioceo179"),
    (("record179", "a"), "record179"),
    (("record179", "zz"), "qdbnqc179"),
    (("record179", "AgentU"), "rkgbkx179"),
    (("record179", "keyboard"), "biapfd179"),
    (("record179", "AA"), "record179"),
    (("candle179", "key"), "melnpc179"),
    (("candle179", "lemon"), "nezryp179"),
    (("candle179", "a"), "candle179"),
    (("candle179", "zz"), "bzmckd179"),
    (("candle179", "AgentU"), "cgrqey179"),
    (("candle179", "keyboard"), "meleze179"),
    (("candle179", "AA"), "candle179"),
    (("thread179", "key"), "dlpoeb179"),
    (("thread179", "lemon"), "eldsno179"),
    (("thread179", "a"), "thread179"),
    (("thread179", "zz"), "sgqdzc179"),
    (("thread179", "AgentU"), "tnvrtx179"),
    (("thread179", "keyboard"), "dlpfod179"),
    (("thread179", "AA"), "thread179"),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 179: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 179: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "a"),
        "round 179: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 179: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 179: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 179: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", "AA"),
        "round 179: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "key"),
        "bssxh 179: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 179: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "a"),
        "round 179: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 179: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 179: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 179: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", "AA"),
        "round 179: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 179: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 179: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "a"),
        "round 179: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 179: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 179: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 179: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", "AA"),
        "round 179: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 179: the processor reads the record then stops", "key"),
        "bssxh 179: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 179: the processor reads the record then stops", "lemon"),
        "csgbq 179: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 179: the processor reads the record then stops", "a"),
        "round 179: the processor reads the record then stops",
    ),
    (
        ("round 179: the processor reads the record then stops", "zz"),
        "qntmc 179: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 179: the processor reads the record then stops", "AgentU"),
        "ruyaw 179: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 179: the processor reads the record then stops", "keyboard"),
        "bssor 179: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 179: the processor reads the record then stops", "AA"),
        "round 179: the processor reads the record then stops",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "key"),
        "bssxh 179: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "lemon"),
        "csgbq 179: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "a"),
        "round 179: a worker pulls the next task from the queue",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "zz"),
        "qntmc 179: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 179: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "keyboard"),
        "bssor 179: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 179: a worker pulls the next task from the queue", "AA"),
        "round 179: a worker pulls the next task from the queue",
    ),
    (
        ("round 179: signals travel through the network layer", "key"),
        "bssxh 179: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 179: signals travel through the network layer", "lemon"),
        "csgbq 179: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 179: signals travel through the network layer", "a"),
        "round 179: signals travel through the network layer",
    ),
    (
        ("round 179: signals travel through the network layer", "zz"),
        "qntmc 179: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 179: signals travel through the network layer", "AgentU"),
        "ruyaw 179: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 179: signals travel through the network layer", "keyboard"),
        "bssor 179: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 179: signals travel through the network layer", "AA"),
        "round 179: signals travel through the network layer",
    ),
    (
        ("round 179: the gateway routes each request by policy", "key"),
        "bssxh 179: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 179: the gateway routes each request by policy", "lemon"),
        "csgbq 179: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 179: the gateway routes each request by policy", "a"),
        "round 179: the gateway routes each request by policy",
    ),
    (
        ("round 179: the gateway routes each request by policy", "zz"),
        "qntmc 179: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 179: the gateway routes each request by policy", "AgentU"),
        "ruyaw 179: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 179: the gateway routes each request by policy", "keyboard"),
        "bssor 179: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 179: the gateway routes each request by policy", "AA"),
        "round 179: the gateway routes each request by policy",
    ),
    (("round 179: memory grows until the buffer is full", "key"), "bssxh 179: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 179: memory grows until the buffer is full", "lemon"), "csgbq 179: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 179: memory grows until the buffer is full", "a"), "round 179: memory grows until the buffer is full"),
    (("round 179: memory grows until the buffer is full", "zz"), "qntmc 179: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 179: memory grows until the buffer is full", "AgentU"),
        "ruyaw 179: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 179: memory grows until the buffer is full", "keyboard"),
        "bssor 179: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 179: memory grows until the buffer is full", "AA"), "round 179: memory grows until the buffer is full"),
    (("round 179: the cluster mirrors every packet twice", "key"), "bssxh 179: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 179: the cluster mirrors every packet twice", "lemon"),
        "csgbq 179: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 179: the cluster mirrors every packet twice", "a"), "round 179: the cluster mirrors every packet twice"),
    (("round 179: the cluster mirrors every packet twice", "zz"), "qntmc 179: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 179: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 179: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 179: the cluster mirrors every packet twice", "keyboard"),
        "bssor 179: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 179: the cluster mirrors every packet twice", "AA"), "round 179: the cluster mirrors every packet twice"),
    (
        ("round 179: ranking uses tokens learned from the corpus", "key"),
        "bssxh 179: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 179: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", "a"),
        "round 179: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 179: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 179: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 179: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", "AA"),
        "round 179: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 179: a long session ends when the candle dies", "key"),
        "bssxh 179: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 179: a long session ends when the candle dies", "lemon"),
        "csgbq 179: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 179: a long session ends when the candle dies", "a"),
        "round 179: a long session ends when the candle dies",
    ),
    (
        ("round 179: a long session ends when the candle dies", "zz"),
        "qntmc 179: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 179: a long session ends when the candle dies", "AgentU"),
        "ruyaw 179: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 179: a long session ends when the candle dies", "keyboard"),
        "bssor 179: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 179: a long session ends when the candle dies", "AA"),
        "round 179: a long session ends when the candle dies",
    ),
    (("round 179: encode the prompt then map the result", "key"), "bssxh 179: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 179: encode the prompt then map the result", "lemon"), "csgbq 179: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 179: encode the prompt then map the result", "a"), "round 179: encode the prompt then map the result"),
    (("round 179: encode the prompt then map the result", "zz"), "qntmc 179: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 179: encode the prompt then map the result", "AgentU"),
        "ruyaw 179: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 179: encode the prompt then map the result", "keyboard"),
        "bssor 179: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 179: encode the prompt then map the result", "AA"), "round 179: encode the prompt then map the result"),
    (("round 179: the kernel wakes the worker at dawn", "key"), "bssxh 179: rri iovlop ukocc xfo ambocb er neux"),
    (("round 179: the kernel wakes the worker at dawn", "lemon"), "csgbq 179: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 179: the kernel wakes the worker at dawn", "a"), "round 179: the kernel wakes the worker at dawn"),
    (("round 179: the kernel wakes the worker at dawn", "zz"), "qntmc 179: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 179: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 179: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 179: the kernel wakes the worker at dawn", "keyboard"), "bssor 179: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 179: the kernel wakes the worker at dawn", "AA"), "round 179: the kernel wakes the worker at dawn"),
    (("round 179: service latency drops after the patch", "key"), "bssxh 179: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 179: service latency drops after the patch", "lemon"), "csgbq 179: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 179: service latency drops after the patch", "a"), "round 179: service latency drops after the patch"),
    (("round 179: service latency drops after the patch", "zz"), "qntmc 179: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 179: service latency drops after the patch", "AgentU"),
        "ruyaw 179: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 179: service latency drops after the patch", "keyboard"),
        "bssor 179: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 179: service latency drops after the patch", "AA"), "round 179: service latency drops after the patch"),
    (
        ("round 179: the library caches every vector it sees", "key"),
        "bssxh 179: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 179: the library caches every vector it sees", "lemon"),
        "csgbq 179: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 179: the library caches every vector it sees", "a"), "round 179: the library caches every vector it sees"),
    (
        ("round 179: the library caches every vector it sees", "zz"),
        "qntmc 179: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 179: the library caches every vector it sees", "AgentU"),
        "ruyaw 179: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 179: the library caches every vector it sees", "keyboard"),
        "bssor 179: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 179: the library caches every vector it sees", "AA"),
        "round 179: the library caches every vector it sees",
    ),
    (("round 179: agents argue then the debate resolves", "key"), "bssxh 179: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 179: agents argue then the debate resolves", "lemon"), "csgbq 179: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 179: agents argue then the debate resolves", "a"), "round 179: agents argue then the debate resolves"),
    (("round 179: agents argue then the debate resolves", "zz"), "qntmc 179: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 179: agents argue then the debate resolves", "AgentU"),
        "ruyaw 179: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 179: agents argue then the debate resolves", "keyboard"),
        "bssor 179: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 179: agents argue then the debate resolves", "AA"), "round 179: agents argue then the debate resolves"),
    (("round 179: the filter keeps only strong matches", "key"), "bssxh 179: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 179: the filter keeps only strong matches", "lemon"), "csgbq 179: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 179: the filter keeps only strong matches", "a"), "round 179: the filter keeps only strong matches"),
    (("round 179: the filter keeps only strong matches", "zz"), "qntmc 179: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 179: the filter keeps only strong matches", "AgentU"), "ruyaw 179: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 179: the filter keeps only strong matches", "keyboard"),
        "bssor 179: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 179: the filter keeps only strong matches", "AA"), "round 179: the filter keeps only strong matches"),
    (("round 179: the model answers with a short reply", "key"), "bssxh 179: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 179: the model answers with a short reply", "lemon"), "csgbq 179: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 179: the model answers with a short reply", "a"), "round 179: the model answers with a short reply"),
    (("round 179: the model answers with a short reply", "zz"), "qntmc 179: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 179: the model answers with a short reply", "AgentU"), "ruyaw 179: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 179: the model answers with a short reply", "keyboard"),
        "bssor 179: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 179: the model answers with a short reply", "AA"), "round 179: the model answers with a short reply"),
    (
        ("round 179: the recorder stores the reasoning trace", "key"),
        "bssxh 179: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 179: the recorder stores the reasoning trace", "lemon"),
        "csgbq 179: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 179: the recorder stores the reasoning trace", "a"), "round 179: the recorder stores the reasoning trace"),
    (
        ("round 179: the recorder stores the reasoning trace", "zz"),
        "qntmc 179: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 179: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 179: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 179: the recorder stores the reasoning trace", "keyboard"),
        "bssor 179: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 179: the recorder stores the reasoning trace", "AA"),
        "round 179: the recorder stores the reasoning trace",
    ),
    (("round 179: the angel watches the processor run", "key"), "bssxh 179: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 179: the angel watches the processor run", "lemon"), "csgbq 179: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 179: the angel watches the processor run", "a"), "round 179: the angel watches the processor run"),
    (("round 179: the angel watches the processor run", "zz"), "qntmc 179: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 179: the angel watches the processor run", "AgentU"), "ruyaw 179: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 179: the angel watches the processor run", "keyboard"), "bssor 179: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 179: the angel watches the processor run", "AA"), "round 179: the angel watches the processor run"),
    (("round 179: angle of the vector decides the match", "key"), "bssxh 179: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 179: angle of the vector decides the match", "lemon"), "csgbq 179: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 179: angle of the vector decides the match", "a"), "round 179: angle of the vector decides the match"),
    (("round 179: angle of the vector decides the match", "zz"), "qntmc 179: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 179: angle of the vector decides the match", "AgentU"),
        "ruyaw 179: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 179: angle of the vector decides the match", "keyboard"),
        "bssor 179: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 179: angle of the vector decides the match", "AA"), "round 179: angle of the vector decides the match"),
    (
        ("round 179: the candle burns twice as long at night", "key"),
        "bssxh 179: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 179: the candle burns twice as long at night", "lemon"),
        "csgbq 179: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 179: the candle burns twice as long at night", "a"), "round 179: the candle burns twice as long at night"),
    (
        ("round 179: the candle burns twice as long at night", "zz"),
        "qntmc 179: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 179: the candle burns twice as long at night", "AgentU"),
        "ruyaw 179: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 179: the candle burns twice as long at night", "keyboard"),
        "bssor 179: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 179: the candle burns twice as long at night", "AA"),
        "round 179: the candle burns twice as long at night",
    ),
    (("round 179: a mirror of the universe in one line", "key"), "bssxh 179: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 179: a mirror of the universe in one line", "lemon"), "csgbq 179: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 179: a mirror of the universe in one line", "a"), "round 179: a mirror of the universe in one line"),
    (("round 179: a mirror of the universe in one line", "zz"), "qntmc 179: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 179: a mirror of the universe in one line", "AgentU"), "ruyaw 179: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 179: a mirror of the universe in one line", "keyboard"),
        "bssor 179: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 179: a mirror of the universe in one line", "AA"), "round 179: a mirror of the universe in one line"),
    (("round 179: the queue drains before the storm", "key"), "bssxh 179: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 179: the queue drains before the storm", "lemon"), "csgbq 179: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 179: the queue drains before the storm", "a"), "round 179: the queue drains before the storm"),
    (("round 179: the queue drains before the storm", "zz"), "qntmc 179: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 179: the queue drains before the storm", "AgentU"), "ruyaw 179: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 179: the queue drains before the storm", "keyboard"), "bssor 179: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 179: the queue drains before the storm", "AA"), "round 179: the queue drains before the storm"),
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
