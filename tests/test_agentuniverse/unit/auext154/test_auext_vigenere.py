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
    (("kitten154", "key"), "umrdil154"),
    (("kitten154", "lemon"), "vmfhry154"),
    (("kitten154", "a"), "kitten154"),
    (("kitten154", "zz"), "jhssdm154"),
    (("kitten154", "AgentU"), "koxgxh154"),
    (("kitten154", "keyboard"), "umrusn154"),
    (("kitten154", "AA"), "kitten154"),
    (("sitting154", "key"), "cmrdmlq154"),
    (("sitting154", "lemon"), "dmfhvyk154"),
    (("sitting154", "a"), "sitting154"),
    (("sitting154", "zz"), "rhsshmf154"),
    (("sitting154", "AgentU"), "soxgbhg154"),
    (("sitting154", "keyboard"), "cmruwnx154"),
    (("sitting154", "AA"), "sitting154"),
    (("agent154", "key"), "kkcxx154"),
    (("agent154", "lemon"), "lkqbg154"),
    (("agent154", "a"), "agent154"),
    (("agent154", "zz"), "zfdms154"),
    (("agent154", "AgentU"), "amiam154"),
    (("agent154", "keyboard"), "kkcoh154"),
    (("agent154", "AA"), "agent154"),
    (("angle154", "key"), "krevi154"),
    (("angle154", "lemon"), "lrszr154"),
    (("angle154", "a"), "angle154"),
    (("angle154", "zz"), "zmfkd154"),
    (("angle154", "AgentU"), "atkyx154"),
    (("angle154", "keyboard"), "krems154"),
    (("angle154", "AA"), "angle154"),
    (("universe154", "key"), "ergfipci154"),
    (("universe154", "lemon"), "frujrcwq154"),
    (("universe154", "a"), "universe154"),
    (("universe154", "zz"), "tmhudqrd154"),
    (("universe154", "AgentU"), "utmixlsk154"),
    (("universe154", "keyboard"), "ergwsrjh154"),
    (("universe154", "AA"), "universe154"),
    (("memory154", "key"), "wikyvw154"),
    (("memory154", "lemon"), "xiycej154"),
    (("memory154", "a"), "memory154"),
    (("memory154", "zz"), "ldlnqx154"),
    (("memory154", "AgentU"), "mkqbks154"),
    (("memory154", "keyboard"), "wikpfy154"),
    (("memory154", "AA"), "memory154"),
    (("stream154", "key"), "cxpoek154"),
    (("stream154", "lemon"), "dxdsnx154"),
    (("stream154", "a"), "stream154"),
    (("stream154", "zz"), "rsqdzl154"),
    (("stream154", "AgentU"), "szvrtg154"),
    (("stream154", "keyboard"), "cxpfom154"),
    (("stream154", "AA"), "stream154"),
    (("context154", "key"), "msldivd154"),
    (("context154", "lemon"), "nszhrix154"),
    (("context154", "a"), "context154"),
    (("context154", "zz"), "bnmsdws154"),
    (("context154", "AgentU"), "curgxrt154"),
    (("context154", "keyboard"), "mslusxk154"),
    (("context154", "AA"), "context154"),
    (("knowledge154", "key"), "urmgpcnkc154"),
    (("knowledge154", "lemon"), "vrakyphss154"),
    (("knowledge154", "a"), "knowledge154"),
    (("knowledge154", "zz"), "jmnvkdcfd154"),
    (("knowledge154", "AgentU"), "ktsjeydmi154"),
    (("knowledge154", "keyboard"), "urmxzeujo154"),
    (("knowledge154", "AA"), "knowledge154"),
    (("vector154", "key"), "fiadsp154"),
    (("vector154", "lemon"), "giohbc154"),
    (("vector154", "a"), "vector154"),
    (("vector154", "zz"), "udbsnq154"),
    (("vector154", "AgentU"), "vkgghl154"),
    (("vector154", "keyboard"), "fiaucr154"),
    (("vector154", "AA"), "vector154"),
    (("processor154", "key"), "zvmmiqcsp154"),
    (("processor154", "lemon"), "avaqrdwaf154"),
    (("processor154", "a"), "processor154"),
    (("processor154", "zz"), "oqnbdrrnq154"),
    (("processor154", "AgentU"), "pxspxmsuv154"),
    (("processor154", "keyboard"), "zvmdssjrb154"),
    (("processor154", "AA"), "processor154"),
    (("reasoning154", "key"), "biycslsre154"),
    (("reasoning154", "lemon"), "cimgbymzu154"),
    (("reasoning154", "a"), "reasoning154"),
    (("reasoning154", "zz"), "qdzrnmhmf154"),
    (("reasoning154", "AgentU"), "rkefhhitk154"),
    (("reasoning154", "keyboard"), "biytcnzqq154"),
    (("reasoning154", "AA"), "reasoning154"),
    (("machine154", "key"), "wearmlo154"),
    (("machine154", "lemon"), "xeovvyi154"),
    (("machine154", "a"), "machine154"),
    (("machine154", "zz"), "lzbghmd154"),
    (("machine154", "AgentU"), "mggubhe154"),
    (("machine154", "keyboard"), "weaiwnv154"),
    (("machine154", "AA"), "machine154"),
    (("learning154", "key"), "viybrgxk154"),
    (("learning154", "lemon"), "wimfatrs154"),
    (("learning154", "a"), "learning154"),
    (("learning154", "zz"), "kdzqmhmf154"),
    (("learning154", "AgentU"), "lkeegcnm154"),
    (("learning154", "keyboard"), "viysbiej154"),
    (("learning154", "AA"), "learning154"),
    (("model154", "key"), "wsbop154"),
    (("model154", "lemon"), "xspsy154"),
    (("model154", "a"), "model154"),
    (("model154", "zz"), "lncdk154"),
    (("model154", "AgentU"), "muhre154"),
    (("model154", "keyboard"), "wsbfz154"),
    (("model154", "AA"), "model154"),
    (("token154", "key"), "dsior154"),
    (("token154", "lemon"), "eswsa154"),
    (("token154", "a"), "token154"),
    (("token154", "zz"), "snjdm154"),
    (("token154", "AgentU"), "tuorg154"),
    (("token154", "keyboard"), "dsifb154"),
    (("token154", "AA"), "token154"),
    (("prompt154", "key"), "zvmwtr154"),
    (("prompt154", "lemon"), "avaace154"),
    (("prompt154", "a"), "prompt154"),
    (("prompt154", "zz"), "oqnlos154"),
    (("prompt154", "AgentU"), "pxszin154"),
    (("prompt154", "keyboard"), "zvmndt154"),
    (("prompt154", "AA"), "prompt154"),
    (("session154", "key"), "ciqcmmx154"),
    (("session154", "lemon"), "diegvzr154"),
    (("session154", "a"), "session154"),
    (("session154", "zz"), "rdrrhnm154"),
    (("session154", "AgentU"), "skwfbin154"),
    (("session154", "keyboard"), "ciqtwoe154"),
    (("session154", "AA"), "session154"),
    (("library154", "key"), "vmzbepi154"),
    (("library154", "lemon"), "wmnfncc154"),
    (("library154", "a"), "library154"),
    (("library154", "zz"), "khaqzqx154"),
    (("library154", "AgentU"), "lofetly154"),
    (("library154", "keyboard"), "vmzsorp154"),
    (("library154", "AA"), "library154"),
    (("service154", "key"), "cipfmao154"),
    (("service154", "lemon"), "didjvni154"),
    (("service154", "a"), "service154"),
    (("service154", "zz"), "rdquhbd154"),
    (("service154", "AgentU"), "skvibwe154"),
    (("service154", "keyboard"), "cipwwcv154"),
    (("service154", "AA"), "service154"),
    (("gateway154", "key"), "qeroayi154"),
    (("gateway154", "lemon"), "refsjlc154"),
    (("gateway154", "a"), "gateway154"),
    (("gateway154", "zz"), "fzsdvzx154"),
    (("gateway154", "AgentU"), "ggxrpuy154"),
    (("gateway154", "keyboard"), "qerfkap154"),
    (("gateway154", "AA"), "gateway154"),
    (("storage154", "key"), "cxmbeeo154"),
    (("storage154", "lemon"), "dxafnri154"),
    (("storage154", "a"), "storage154"),
    (("storage154", "zz"), "rsnqzfd154"),
    (("storage154", "AgentU"), "szsetae154"),
    (("storage154", "keyboard"), "cxmsogv154"),
    (("storage154", "AA"), "storage154"),
    (("network154", "key"), "xirgspu154"),
    (("network154", "lemon"), "yifkbco154"),
    (("network154", "a"), "network154"),
    (("network154", "zz"), "mdsvnqj154"),
    (("network154", "AgentU"), "nkxjhlk154"),
    (("network154", "keyboard"), "xirxcrb154"),
    (("network154", "AA"), "network154"),
    (("latency154", "key"), "verorai154"),
    (("latency154", "lemon"), "wefsanc154"),
    (("latency154", "a"), "latency154"),
    (("latency154", "zz"), "kzsdmbx154"),
    (("latency154", "AgentU"), "lgxrgwy154"),
    (("latency154", "keyboard"), "verfbcp154"),
    (("latency154", "AA"), "latency154"),
    (("buffer154", "key"), "lydpip154"),
    (("buffer154", "lemon"), "myrtrc154"),
    (("buffer154", "a"), "buffer154"),
    (("buffer154", "zz"), "ateedq154"),
    (("buffer154", "AgentU"), "bajsxl154"),
    (("buffer154", "keyboard"), "lydgsr154"),
    (("buffer154", "AA"), "buffer154"),
    (("queue154", "key"), "aycei154"),
    (("queue154", "lemon"), "byqir154"),
    (("queue154", "a"), "queue154"),
    (("queue154", "zz"), "ptdtd154"),
    (("queue154", "AgentU"), "qaihx154"),
    (("queue154", "keyboard"), "aycvs154"),
    (("queue154", "AA"), "queue154"),
    (("worker154", "key"), "gspuip154"),
    (("worker154", "lemon"), "hsdyrc154"),
    (("worker154", "a"), "worker154"),
    (("worker154", "zz"), "vnqjdq154"),
    (("worker154", "AgentU"), "wuvxxl154"),
    (("worker154", "keyboard"), "gsplsr154"),
    (("worker154", "AA"), "worker154"),
    (("kernel154", "key"), "uipxij154"),
    (("kernel154", "lemon"), "vidbrw154"),
    (("kernel154", "a"), "kernel154"),
    (("kernel154", "zz"), "jdqmdk154"),
    (("kernel154", "AgentU"), "kkvaxf154"),
    (("kernel154", "keyboard"), "uiposl154"),
    (("kernel154", "AA"), "kernel154"),
    (("signal154", "key"), "cmexej154"),
    (("signal154", "lemon"), "dmsbnw154"),
    (("signal154", "a"), "signal154"),
    (("signal154", "zz"), "rhfmzk154"),
    (("signal154", "AgentU"), "sokatf154"),
    (("signal154", "keyboard"), "cmeool154"),
    (("signal154", "AA"), "signal154"),
    (("packet154", "key"), "zeauir154"),
    (("packet154", "lemon"), "aeoyre154"),
    (("packet154", "a"), "packet154"),
    (("packet154", "zz"), "ozbjds154"),
    (("packet154", "AgentU"), "pggxxn154"),
    (("packet154", "keyboard"), "zealst154"),
    (("packet154", "AA"), "packet154"),
    (("router154", "key"), "bssdip154"),
    (("router154", "lemon"), "csghrc154"),
    (("router154", "a"), "router154"),
    (("router154", "zz"), "qntsdq154"),
    (("router154", "AgentU"), "ruygxl154"),
    (("router154", "keyboard"), "bssusr154"),
    (("router154", "AA"), "router154"),
    (("cluster154", "key"), "mpscxcb154"),
    (("cluster154", "lemon"), "npgggpv154"),
    (("cluster154", "a"), "cluster154"),
    (("cluster154", "zz"), "bktrsdq154"),
    (("cluster154", "AgentU"), "cryfmyr154"),
    (("cluster154", "keyboard"), "mpsthei154"),
    (("cluster154", "AA"), "cluster154"),
    (("mirror154", "key"), "wmpbsp154"),
    (("mirror154", "lemon"), "xmdfbc154"),
    (("mirror154", "a"), "mirror154"),
    (("mirror154", "zz"), "lhqqnq154"),
    (("mirror154", "AgentU"), "movehl154"),
    (("mirror154", "keyboard"), "wmpscr154"),
    (("mirror154", "AA"), "mirror154"),
    (("filter154", "key"), "pmjdip154"),
    (("filter154", "lemon"), "qmxhrc154"),
    (("filter154", "a"), "filter154"),
    (("filter154", "zz"), "ehksdq154"),
    (("filter154", "AgentU"), "fopgxl154"),
    (("filter154", "keyboard"), "pmjusr154"),
    (("filter154", "AA"), "filter154"),
    (("ranking154", "key"), "belumlq154"),
    (("ranking154", "lemon"), "cezyvyk154"),
    (("ranking154", "a"), "ranking154"),
    (("ranking154", "zz"), "qzmjhmf154"),
    (("ranking154", "AgentU"), "rgrxbhg154"),
    (("ranking154", "keyboard"), "bellwnx154"),
    (("ranking154", "AA"), "ranking154"),
    (("encoding154", "key"), "orayhgxk154"),
    (("encoding154", "lemon"), "procqtrs154"),
    (("encoding154", "a"), "encoding154"),
    (("encoding154", "zz"), "dmbnchmf154"),
    (("encoding154", "AgentU"), "etgbwcnm154"),
    (("encoding154", "keyboard"), "orapriej154"),
    (("encoding154", "AA"), "encoding154"),
    (("mapping154", "key"), "wenzmlq154"),
    (("mapping154", "lemon"), "xebdvyk154"),
    (("mapping154", "a"), "mapping154"),
    (("mapping154", "zz"), "lzoohmf154"),
    (("mapping154", "AgentU"), "mgtcbhg154"),
    (("mapping154", "keyboard"), "wenqwnx154"),
    (("mapping154", "AA"), "mapping154"),
    (("record154", "key"), "biayvb154"),
    (("record154", "lemon"), "cioceo154"),
    (("record154", "a"), "record154"),
    (("record154", "zz"), "qdbnqc154"),
    (("record154", "AgentU"), "rkgbkx154"),
    (("record154", "keyboard"), "biapfd154"),
    (("record154", "AA"), "record154"),
    (("candle154", "key"), "melnpc154"),
    (("candle154", "lemon"), "nezryp154"),
    (("candle154", "a"), "candle154"),
    (("candle154", "zz"), "bzmckd154"),
    (("candle154", "AgentU"), "cgrqey154"),
    (("candle154", "keyboard"), "meleze154"),
    (("candle154", "AA"), "candle154"),
    (("thread154", "key"), "dlpoeb154"),
    (("thread154", "lemon"), "eldsno154"),
    (("thread154", "a"), "thread154"),
    (("thread154", "zz"), "sgqdzc154"),
    (("thread154", "AgentU"), "tnvrtx154"),
    (("thread154", "keyboard"), "dlpfod154"),
    (("thread154", "AA"), "thread154"),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 154: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 154: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "a"),
        "round 154: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 154: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 154: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 154: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", "AA"),
        "round 154: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "key"),
        "bssxh 154: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 154: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "a"),
        "round 154: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 154: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 154: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 154: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", "AA"),
        "round 154: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 154: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 154: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "a"),
        "round 154: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 154: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 154: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 154: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", "AA"),
        "round 154: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 154: the processor reads the record then stops", "key"),
        "bssxh 154: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 154: the processor reads the record then stops", "lemon"),
        "csgbq 154: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 154: the processor reads the record then stops", "a"),
        "round 154: the processor reads the record then stops",
    ),
    (
        ("round 154: the processor reads the record then stops", "zz"),
        "qntmc 154: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 154: the processor reads the record then stops", "AgentU"),
        "ruyaw 154: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 154: the processor reads the record then stops", "keyboard"),
        "bssor 154: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 154: the processor reads the record then stops", "AA"),
        "round 154: the processor reads the record then stops",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "key"),
        "bssxh 154: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "lemon"),
        "csgbq 154: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "a"),
        "round 154: a worker pulls the next task from the queue",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "zz"),
        "qntmc 154: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 154: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "keyboard"),
        "bssor 154: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 154: a worker pulls the next task from the queue", "AA"),
        "round 154: a worker pulls the next task from the queue",
    ),
    (
        ("round 154: signals travel through the network layer", "key"),
        "bssxh 154: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 154: signals travel through the network layer", "lemon"),
        "csgbq 154: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 154: signals travel through the network layer", "a"),
        "round 154: signals travel through the network layer",
    ),
    (
        ("round 154: signals travel through the network layer", "zz"),
        "qntmc 154: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 154: signals travel through the network layer", "AgentU"),
        "ruyaw 154: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 154: signals travel through the network layer", "keyboard"),
        "bssor 154: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 154: signals travel through the network layer", "AA"),
        "round 154: signals travel through the network layer",
    ),
    (
        ("round 154: the gateway routes each request by policy", "key"),
        "bssxh 154: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 154: the gateway routes each request by policy", "lemon"),
        "csgbq 154: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 154: the gateway routes each request by policy", "a"),
        "round 154: the gateway routes each request by policy",
    ),
    (
        ("round 154: the gateway routes each request by policy", "zz"),
        "qntmc 154: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 154: the gateway routes each request by policy", "AgentU"),
        "ruyaw 154: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 154: the gateway routes each request by policy", "keyboard"),
        "bssor 154: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 154: the gateway routes each request by policy", "AA"),
        "round 154: the gateway routes each request by policy",
    ),
    (("round 154: memory grows until the buffer is full", "key"), "bssxh 154: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 154: memory grows until the buffer is full", "lemon"), "csgbq 154: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 154: memory grows until the buffer is full", "a"), "round 154: memory grows until the buffer is full"),
    (("round 154: memory grows until the buffer is full", "zz"), "qntmc 154: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 154: memory grows until the buffer is full", "AgentU"),
        "ruyaw 154: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 154: memory grows until the buffer is full", "keyboard"),
        "bssor 154: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 154: memory grows until the buffer is full", "AA"), "round 154: memory grows until the buffer is full"),
    (("round 154: the cluster mirrors every packet twice", "key"), "bssxh 154: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 154: the cluster mirrors every packet twice", "lemon"),
        "csgbq 154: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 154: the cluster mirrors every packet twice", "a"), "round 154: the cluster mirrors every packet twice"),
    (("round 154: the cluster mirrors every packet twice", "zz"), "qntmc 154: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 154: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 154: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 154: the cluster mirrors every packet twice", "keyboard"),
        "bssor 154: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 154: the cluster mirrors every packet twice", "AA"), "round 154: the cluster mirrors every packet twice"),
    (
        ("round 154: ranking uses tokens learned from the corpus", "key"),
        "bssxh 154: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 154: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", "a"),
        "round 154: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 154: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 154: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 154: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", "AA"),
        "round 154: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 154: a long session ends when the candle dies", "key"),
        "bssxh 154: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 154: a long session ends when the candle dies", "lemon"),
        "csgbq 154: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 154: a long session ends when the candle dies", "a"),
        "round 154: a long session ends when the candle dies",
    ),
    (
        ("round 154: a long session ends when the candle dies", "zz"),
        "qntmc 154: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 154: a long session ends when the candle dies", "AgentU"),
        "ruyaw 154: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 154: a long session ends when the candle dies", "keyboard"),
        "bssor 154: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 154: a long session ends when the candle dies", "AA"),
        "round 154: a long session ends when the candle dies",
    ),
    (("round 154: encode the prompt then map the result", "key"), "bssxh 154: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 154: encode the prompt then map the result", "lemon"), "csgbq 154: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 154: encode the prompt then map the result", "a"), "round 154: encode the prompt then map the result"),
    (("round 154: encode the prompt then map the result", "zz"), "qntmc 154: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 154: encode the prompt then map the result", "AgentU"),
        "ruyaw 154: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 154: encode the prompt then map the result", "keyboard"),
        "bssor 154: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 154: encode the prompt then map the result", "AA"), "round 154: encode the prompt then map the result"),
    (("round 154: the kernel wakes the worker at dawn", "key"), "bssxh 154: rri iovlop ukocc xfo ambocb er neux"),
    (("round 154: the kernel wakes the worker at dawn", "lemon"), "csgbq 154: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 154: the kernel wakes the worker at dawn", "a"), "round 154: the kernel wakes the worker at dawn"),
    (("round 154: the kernel wakes the worker at dawn", "zz"), "qntmc 154: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 154: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 154: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 154: the kernel wakes the worker at dawn", "keyboard"), "bssor 154: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 154: the kernel wakes the worker at dawn", "AA"), "round 154: the kernel wakes the worker at dawn"),
    (("round 154: service latency drops after the patch", "key"), "bssxh 154: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 154: service latency drops after the patch", "lemon"), "csgbq 154: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 154: service latency drops after the patch", "a"), "round 154: service latency drops after the patch"),
    (("round 154: service latency drops after the patch", "zz"), "qntmc 154: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 154: service latency drops after the patch", "AgentU"),
        "ruyaw 154: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 154: service latency drops after the patch", "keyboard"),
        "bssor 154: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 154: service latency drops after the patch", "AA"), "round 154: service latency drops after the patch"),
    (
        ("round 154: the library caches every vector it sees", "key"),
        "bssxh 154: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 154: the library caches every vector it sees", "lemon"),
        "csgbq 154: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 154: the library caches every vector it sees", "a"), "round 154: the library caches every vector it sees"),
    (
        ("round 154: the library caches every vector it sees", "zz"),
        "qntmc 154: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 154: the library caches every vector it sees", "AgentU"),
        "ruyaw 154: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 154: the library caches every vector it sees", "keyboard"),
        "bssor 154: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 154: the library caches every vector it sees", "AA"),
        "round 154: the library caches every vector it sees",
    ),
    (("round 154: agents argue then the debate resolves", "key"), "bssxh 154: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 154: agents argue then the debate resolves", "lemon"), "csgbq 154: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 154: agents argue then the debate resolves", "a"), "round 154: agents argue then the debate resolves"),
    (("round 154: agents argue then the debate resolves", "zz"), "qntmc 154: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 154: agents argue then the debate resolves", "AgentU"),
        "ruyaw 154: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 154: agents argue then the debate resolves", "keyboard"),
        "bssor 154: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 154: agents argue then the debate resolves", "AA"), "round 154: agents argue then the debate resolves"),
    (("round 154: the filter keeps only strong matches", "key"), "bssxh 154: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 154: the filter keeps only strong matches", "lemon"), "csgbq 154: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 154: the filter keeps only strong matches", "a"), "round 154: the filter keeps only strong matches"),
    (("round 154: the filter keeps only strong matches", "zz"), "qntmc 154: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 154: the filter keeps only strong matches", "AgentU"), "ruyaw 154: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 154: the filter keeps only strong matches", "keyboard"),
        "bssor 154: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 154: the filter keeps only strong matches", "AA"), "round 154: the filter keeps only strong matches"),
    (("round 154: the model answers with a short reply", "key"), "bssxh 154: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 154: the model answers with a short reply", "lemon"), "csgbq 154: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 154: the model answers with a short reply", "a"), "round 154: the model answers with a short reply"),
    (("round 154: the model answers with a short reply", "zz"), "qntmc 154: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 154: the model answers with a short reply", "AgentU"), "ruyaw 154: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 154: the model answers with a short reply", "keyboard"),
        "bssor 154: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 154: the model answers with a short reply", "AA"), "round 154: the model answers with a short reply"),
    (
        ("round 154: the recorder stores the reasoning trace", "key"),
        "bssxh 154: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 154: the recorder stores the reasoning trace", "lemon"),
        "csgbq 154: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 154: the recorder stores the reasoning trace", "a"), "round 154: the recorder stores the reasoning trace"),
    (
        ("round 154: the recorder stores the reasoning trace", "zz"),
        "qntmc 154: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 154: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 154: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 154: the recorder stores the reasoning trace", "keyboard"),
        "bssor 154: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 154: the recorder stores the reasoning trace", "AA"),
        "round 154: the recorder stores the reasoning trace",
    ),
    (("round 154: the angel watches the processor run", "key"), "bssxh 154: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 154: the angel watches the processor run", "lemon"), "csgbq 154: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 154: the angel watches the processor run", "a"), "round 154: the angel watches the processor run"),
    (("round 154: the angel watches the processor run", "zz"), "qntmc 154: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 154: the angel watches the processor run", "AgentU"), "ruyaw 154: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 154: the angel watches the processor run", "keyboard"), "bssor 154: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 154: the angel watches the processor run", "AA"), "round 154: the angel watches the processor run"),
    (("round 154: angle of the vector decides the match", "key"), "bssxh 154: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 154: angle of the vector decides the match", "lemon"), "csgbq 154: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 154: angle of the vector decides the match", "a"), "round 154: angle of the vector decides the match"),
    (("round 154: angle of the vector decides the match", "zz"), "qntmc 154: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 154: angle of the vector decides the match", "AgentU"),
        "ruyaw 154: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 154: angle of the vector decides the match", "keyboard"),
        "bssor 154: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 154: angle of the vector decides the match", "AA"), "round 154: angle of the vector decides the match"),
    (
        ("round 154: the candle burns twice as long at night", "key"),
        "bssxh 154: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 154: the candle burns twice as long at night", "lemon"),
        "csgbq 154: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 154: the candle burns twice as long at night", "a"), "round 154: the candle burns twice as long at night"),
    (
        ("round 154: the candle burns twice as long at night", "zz"),
        "qntmc 154: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 154: the candle burns twice as long at night", "AgentU"),
        "ruyaw 154: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 154: the candle burns twice as long at night", "keyboard"),
        "bssor 154: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 154: the candle burns twice as long at night", "AA"),
        "round 154: the candle burns twice as long at night",
    ),
    (("round 154: a mirror of the universe in one line", "key"), "bssxh 154: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 154: a mirror of the universe in one line", "lemon"), "csgbq 154: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 154: a mirror of the universe in one line", "a"), "round 154: a mirror of the universe in one line"),
    (("round 154: a mirror of the universe in one line", "zz"), "qntmc 154: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 154: a mirror of the universe in one line", "AgentU"), "ruyaw 154: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 154: a mirror of the universe in one line", "keyboard"),
        "bssor 154: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 154: a mirror of the universe in one line", "AA"), "round 154: a mirror of the universe in one line"),
    (("round 154: the queue drains before the storm", "key"), "bssxh 154: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 154: the queue drains before the storm", "lemon"), "csgbq 154: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 154: the queue drains before the storm", "a"), "round 154: the queue drains before the storm"),
    (("round 154: the queue drains before the storm", "zz"), "qntmc 154: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 154: the queue drains before the storm", "AgentU"), "ruyaw 154: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 154: the queue drains before the storm", "keyboard"), "bssor 154: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 154: the queue drains before the storm", "AA"), "round 154: the queue drains before the storm"),
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
