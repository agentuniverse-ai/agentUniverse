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
    (("kitten125", "key"), "umrdil125"),
    (("kitten125", "lemon"), "vmfhry125"),
    (("kitten125", "a"), "kitten125"),
    (("kitten125", "zz"), "jhssdm125"),
    (("kitten125", "AgentU"), "koxgxh125"),
    (("kitten125", "keyboard"), "umrusn125"),
    (("kitten125", "AA"), "kitten125"),
    (("sitting125", "key"), "cmrdmlq125"),
    (("sitting125", "lemon"), "dmfhvyk125"),
    (("sitting125", "a"), "sitting125"),
    (("sitting125", "zz"), "rhsshmf125"),
    (("sitting125", "AgentU"), "soxgbhg125"),
    (("sitting125", "keyboard"), "cmruwnx125"),
    (("sitting125", "AA"), "sitting125"),
    (("agent125", "key"), "kkcxx125"),
    (("agent125", "lemon"), "lkqbg125"),
    (("agent125", "a"), "agent125"),
    (("agent125", "zz"), "zfdms125"),
    (("agent125", "AgentU"), "amiam125"),
    (("agent125", "keyboard"), "kkcoh125"),
    (("agent125", "AA"), "agent125"),
    (("angle125", "key"), "krevi125"),
    (("angle125", "lemon"), "lrszr125"),
    (("angle125", "a"), "angle125"),
    (("angle125", "zz"), "zmfkd125"),
    (("angle125", "AgentU"), "atkyx125"),
    (("angle125", "keyboard"), "krems125"),
    (("angle125", "AA"), "angle125"),
    (("universe125", "key"), "ergfipci125"),
    (("universe125", "lemon"), "frujrcwq125"),
    (("universe125", "a"), "universe125"),
    (("universe125", "zz"), "tmhudqrd125"),
    (("universe125", "AgentU"), "utmixlsk125"),
    (("universe125", "keyboard"), "ergwsrjh125"),
    (("universe125", "AA"), "universe125"),
    (("memory125", "key"), "wikyvw125"),
    (("memory125", "lemon"), "xiycej125"),
    (("memory125", "a"), "memory125"),
    (("memory125", "zz"), "ldlnqx125"),
    (("memory125", "AgentU"), "mkqbks125"),
    (("memory125", "keyboard"), "wikpfy125"),
    (("memory125", "AA"), "memory125"),
    (("stream125", "key"), "cxpoek125"),
    (("stream125", "lemon"), "dxdsnx125"),
    (("stream125", "a"), "stream125"),
    (("stream125", "zz"), "rsqdzl125"),
    (("stream125", "AgentU"), "szvrtg125"),
    (("stream125", "keyboard"), "cxpfom125"),
    (("stream125", "AA"), "stream125"),
    (("context125", "key"), "msldivd125"),
    (("context125", "lemon"), "nszhrix125"),
    (("context125", "a"), "context125"),
    (("context125", "zz"), "bnmsdws125"),
    (("context125", "AgentU"), "curgxrt125"),
    (("context125", "keyboard"), "mslusxk125"),
    (("context125", "AA"), "context125"),
    (("knowledge125", "key"), "urmgpcnkc125"),
    (("knowledge125", "lemon"), "vrakyphss125"),
    (("knowledge125", "a"), "knowledge125"),
    (("knowledge125", "zz"), "jmnvkdcfd125"),
    (("knowledge125", "AgentU"), "ktsjeydmi125"),
    (("knowledge125", "keyboard"), "urmxzeujo125"),
    (("knowledge125", "AA"), "knowledge125"),
    (("vector125", "key"), "fiadsp125"),
    (("vector125", "lemon"), "giohbc125"),
    (("vector125", "a"), "vector125"),
    (("vector125", "zz"), "udbsnq125"),
    (("vector125", "AgentU"), "vkgghl125"),
    (("vector125", "keyboard"), "fiaucr125"),
    (("vector125", "AA"), "vector125"),
    (("processor125", "key"), "zvmmiqcsp125"),
    (("processor125", "lemon"), "avaqrdwaf125"),
    (("processor125", "a"), "processor125"),
    (("processor125", "zz"), "oqnbdrrnq125"),
    (("processor125", "AgentU"), "pxspxmsuv125"),
    (("processor125", "keyboard"), "zvmdssjrb125"),
    (("processor125", "AA"), "processor125"),
    (("reasoning125", "key"), "biycslsre125"),
    (("reasoning125", "lemon"), "cimgbymzu125"),
    (("reasoning125", "a"), "reasoning125"),
    (("reasoning125", "zz"), "qdzrnmhmf125"),
    (("reasoning125", "AgentU"), "rkefhhitk125"),
    (("reasoning125", "keyboard"), "biytcnzqq125"),
    (("reasoning125", "AA"), "reasoning125"),
    (("machine125", "key"), "wearmlo125"),
    (("machine125", "lemon"), "xeovvyi125"),
    (("machine125", "a"), "machine125"),
    (("machine125", "zz"), "lzbghmd125"),
    (("machine125", "AgentU"), "mggubhe125"),
    (("machine125", "keyboard"), "weaiwnv125"),
    (("machine125", "AA"), "machine125"),
    (("learning125", "key"), "viybrgxk125"),
    (("learning125", "lemon"), "wimfatrs125"),
    (("learning125", "a"), "learning125"),
    (("learning125", "zz"), "kdzqmhmf125"),
    (("learning125", "AgentU"), "lkeegcnm125"),
    (("learning125", "keyboard"), "viysbiej125"),
    (("learning125", "AA"), "learning125"),
    (("model125", "key"), "wsbop125"),
    (("model125", "lemon"), "xspsy125"),
    (("model125", "a"), "model125"),
    (("model125", "zz"), "lncdk125"),
    (("model125", "AgentU"), "muhre125"),
    (("model125", "keyboard"), "wsbfz125"),
    (("model125", "AA"), "model125"),
    (("token125", "key"), "dsior125"),
    (("token125", "lemon"), "eswsa125"),
    (("token125", "a"), "token125"),
    (("token125", "zz"), "snjdm125"),
    (("token125", "AgentU"), "tuorg125"),
    (("token125", "keyboard"), "dsifb125"),
    (("token125", "AA"), "token125"),
    (("prompt125", "key"), "zvmwtr125"),
    (("prompt125", "lemon"), "avaace125"),
    (("prompt125", "a"), "prompt125"),
    (("prompt125", "zz"), "oqnlos125"),
    (("prompt125", "AgentU"), "pxszin125"),
    (("prompt125", "keyboard"), "zvmndt125"),
    (("prompt125", "AA"), "prompt125"),
    (("session125", "key"), "ciqcmmx125"),
    (("session125", "lemon"), "diegvzr125"),
    (("session125", "a"), "session125"),
    (("session125", "zz"), "rdrrhnm125"),
    (("session125", "AgentU"), "skwfbin125"),
    (("session125", "keyboard"), "ciqtwoe125"),
    (("session125", "AA"), "session125"),
    (("library125", "key"), "vmzbepi125"),
    (("library125", "lemon"), "wmnfncc125"),
    (("library125", "a"), "library125"),
    (("library125", "zz"), "khaqzqx125"),
    (("library125", "AgentU"), "lofetly125"),
    (("library125", "keyboard"), "vmzsorp125"),
    (("library125", "AA"), "library125"),
    (("service125", "key"), "cipfmao125"),
    (("service125", "lemon"), "didjvni125"),
    (("service125", "a"), "service125"),
    (("service125", "zz"), "rdquhbd125"),
    (("service125", "AgentU"), "skvibwe125"),
    (("service125", "keyboard"), "cipwwcv125"),
    (("service125", "AA"), "service125"),
    (("gateway125", "key"), "qeroayi125"),
    (("gateway125", "lemon"), "refsjlc125"),
    (("gateway125", "a"), "gateway125"),
    (("gateway125", "zz"), "fzsdvzx125"),
    (("gateway125", "AgentU"), "ggxrpuy125"),
    (("gateway125", "keyboard"), "qerfkap125"),
    (("gateway125", "AA"), "gateway125"),
    (("storage125", "key"), "cxmbeeo125"),
    (("storage125", "lemon"), "dxafnri125"),
    (("storage125", "a"), "storage125"),
    (("storage125", "zz"), "rsnqzfd125"),
    (("storage125", "AgentU"), "szsetae125"),
    (("storage125", "keyboard"), "cxmsogv125"),
    (("storage125", "AA"), "storage125"),
    (("network125", "key"), "xirgspu125"),
    (("network125", "lemon"), "yifkbco125"),
    (("network125", "a"), "network125"),
    (("network125", "zz"), "mdsvnqj125"),
    (("network125", "AgentU"), "nkxjhlk125"),
    (("network125", "keyboard"), "xirxcrb125"),
    (("network125", "AA"), "network125"),
    (("latency125", "key"), "verorai125"),
    (("latency125", "lemon"), "wefsanc125"),
    (("latency125", "a"), "latency125"),
    (("latency125", "zz"), "kzsdmbx125"),
    (("latency125", "AgentU"), "lgxrgwy125"),
    (("latency125", "keyboard"), "verfbcp125"),
    (("latency125", "AA"), "latency125"),
    (("buffer125", "key"), "lydpip125"),
    (("buffer125", "lemon"), "myrtrc125"),
    (("buffer125", "a"), "buffer125"),
    (("buffer125", "zz"), "ateedq125"),
    (("buffer125", "AgentU"), "bajsxl125"),
    (("buffer125", "keyboard"), "lydgsr125"),
    (("buffer125", "AA"), "buffer125"),
    (("queue125", "key"), "aycei125"),
    (("queue125", "lemon"), "byqir125"),
    (("queue125", "a"), "queue125"),
    (("queue125", "zz"), "ptdtd125"),
    (("queue125", "AgentU"), "qaihx125"),
    (("queue125", "keyboard"), "aycvs125"),
    (("queue125", "AA"), "queue125"),
    (("worker125", "key"), "gspuip125"),
    (("worker125", "lemon"), "hsdyrc125"),
    (("worker125", "a"), "worker125"),
    (("worker125", "zz"), "vnqjdq125"),
    (("worker125", "AgentU"), "wuvxxl125"),
    (("worker125", "keyboard"), "gsplsr125"),
    (("worker125", "AA"), "worker125"),
    (("kernel125", "key"), "uipxij125"),
    (("kernel125", "lemon"), "vidbrw125"),
    (("kernel125", "a"), "kernel125"),
    (("kernel125", "zz"), "jdqmdk125"),
    (("kernel125", "AgentU"), "kkvaxf125"),
    (("kernel125", "keyboard"), "uiposl125"),
    (("kernel125", "AA"), "kernel125"),
    (("signal125", "key"), "cmexej125"),
    (("signal125", "lemon"), "dmsbnw125"),
    (("signal125", "a"), "signal125"),
    (("signal125", "zz"), "rhfmzk125"),
    (("signal125", "AgentU"), "sokatf125"),
    (("signal125", "keyboard"), "cmeool125"),
    (("signal125", "AA"), "signal125"),
    (("packet125", "key"), "zeauir125"),
    (("packet125", "lemon"), "aeoyre125"),
    (("packet125", "a"), "packet125"),
    (("packet125", "zz"), "ozbjds125"),
    (("packet125", "AgentU"), "pggxxn125"),
    (("packet125", "keyboard"), "zealst125"),
    (("packet125", "AA"), "packet125"),
    (("router125", "key"), "bssdip125"),
    (("router125", "lemon"), "csghrc125"),
    (("router125", "a"), "router125"),
    (("router125", "zz"), "qntsdq125"),
    (("router125", "AgentU"), "ruygxl125"),
    (("router125", "keyboard"), "bssusr125"),
    (("router125", "AA"), "router125"),
    (("cluster125", "key"), "mpscxcb125"),
    (("cluster125", "lemon"), "npgggpv125"),
    (("cluster125", "a"), "cluster125"),
    (("cluster125", "zz"), "bktrsdq125"),
    (("cluster125", "AgentU"), "cryfmyr125"),
    (("cluster125", "keyboard"), "mpsthei125"),
    (("cluster125", "AA"), "cluster125"),
    (("mirror125", "key"), "wmpbsp125"),
    (("mirror125", "lemon"), "xmdfbc125"),
    (("mirror125", "a"), "mirror125"),
    (("mirror125", "zz"), "lhqqnq125"),
    (("mirror125", "AgentU"), "movehl125"),
    (("mirror125", "keyboard"), "wmpscr125"),
    (("mirror125", "AA"), "mirror125"),
    (("filter125", "key"), "pmjdip125"),
    (("filter125", "lemon"), "qmxhrc125"),
    (("filter125", "a"), "filter125"),
    (("filter125", "zz"), "ehksdq125"),
    (("filter125", "AgentU"), "fopgxl125"),
    (("filter125", "keyboard"), "pmjusr125"),
    (("filter125", "AA"), "filter125"),
    (("ranking125", "key"), "belumlq125"),
    (("ranking125", "lemon"), "cezyvyk125"),
    (("ranking125", "a"), "ranking125"),
    (("ranking125", "zz"), "qzmjhmf125"),
    (("ranking125", "AgentU"), "rgrxbhg125"),
    (("ranking125", "keyboard"), "bellwnx125"),
    (("ranking125", "AA"), "ranking125"),
    (("encoding125", "key"), "orayhgxk125"),
    (("encoding125", "lemon"), "procqtrs125"),
    (("encoding125", "a"), "encoding125"),
    (("encoding125", "zz"), "dmbnchmf125"),
    (("encoding125", "AgentU"), "etgbwcnm125"),
    (("encoding125", "keyboard"), "orapriej125"),
    (("encoding125", "AA"), "encoding125"),
    (("mapping125", "key"), "wenzmlq125"),
    (("mapping125", "lemon"), "xebdvyk125"),
    (("mapping125", "a"), "mapping125"),
    (("mapping125", "zz"), "lzoohmf125"),
    (("mapping125", "AgentU"), "mgtcbhg125"),
    (("mapping125", "keyboard"), "wenqwnx125"),
    (("mapping125", "AA"), "mapping125"),
    (("record125", "key"), "biayvb125"),
    (("record125", "lemon"), "cioceo125"),
    (("record125", "a"), "record125"),
    (("record125", "zz"), "qdbnqc125"),
    (("record125", "AgentU"), "rkgbkx125"),
    (("record125", "keyboard"), "biapfd125"),
    (("record125", "AA"), "record125"),
    (("candle125", "key"), "melnpc125"),
    (("candle125", "lemon"), "nezryp125"),
    (("candle125", "a"), "candle125"),
    (("candle125", "zz"), "bzmckd125"),
    (("candle125", "AgentU"), "cgrqey125"),
    (("candle125", "keyboard"), "meleze125"),
    (("candle125", "AA"), "candle125"),
    (("thread125", "key"), "dlpoeb125"),
    (("thread125", "lemon"), "eldsno125"),
    (("thread125", "a"), "thread125"),
    (("thread125", "zz"), "sgqdzc125"),
    (("thread125", "AgentU"), "tnvrtx125"),
    (("thread125", "keyboard"), "dlpfod125"),
    (("thread125", "AA"), "thread125"),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 125: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 125: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "a"),
        "round 125: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 125: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 125: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 125: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", "AA"),
        "round 125: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "key"),
        "bssxh 125: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 125: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "a"),
        "round 125: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 125: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 125: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 125: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", "AA"),
        "round 125: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 125: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 125: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "a"),
        "round 125: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 125: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 125: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 125: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", "AA"),
        "round 125: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 125: the processor reads the record then stops", "key"),
        "bssxh 125: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 125: the processor reads the record then stops", "lemon"),
        "csgbq 125: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 125: the processor reads the record then stops", "a"),
        "round 125: the processor reads the record then stops",
    ),
    (
        ("round 125: the processor reads the record then stops", "zz"),
        "qntmc 125: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 125: the processor reads the record then stops", "AgentU"),
        "ruyaw 125: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 125: the processor reads the record then stops", "keyboard"),
        "bssor 125: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 125: the processor reads the record then stops", "AA"),
        "round 125: the processor reads the record then stops",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "key"),
        "bssxh 125: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "lemon"),
        "csgbq 125: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "a"),
        "round 125: a worker pulls the next task from the queue",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "zz"),
        "qntmc 125: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 125: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "keyboard"),
        "bssor 125: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 125: a worker pulls the next task from the queue", "AA"),
        "round 125: a worker pulls the next task from the queue",
    ),
    (
        ("round 125: signals travel through the network layer", "key"),
        "bssxh 125: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 125: signals travel through the network layer", "lemon"),
        "csgbq 125: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 125: signals travel through the network layer", "a"),
        "round 125: signals travel through the network layer",
    ),
    (
        ("round 125: signals travel through the network layer", "zz"),
        "qntmc 125: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 125: signals travel through the network layer", "AgentU"),
        "ruyaw 125: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 125: signals travel through the network layer", "keyboard"),
        "bssor 125: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 125: signals travel through the network layer", "AA"),
        "round 125: signals travel through the network layer",
    ),
    (
        ("round 125: the gateway routes each request by policy", "key"),
        "bssxh 125: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 125: the gateway routes each request by policy", "lemon"),
        "csgbq 125: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 125: the gateway routes each request by policy", "a"),
        "round 125: the gateway routes each request by policy",
    ),
    (
        ("round 125: the gateway routes each request by policy", "zz"),
        "qntmc 125: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 125: the gateway routes each request by policy", "AgentU"),
        "ruyaw 125: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 125: the gateway routes each request by policy", "keyboard"),
        "bssor 125: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 125: the gateway routes each request by policy", "AA"),
        "round 125: the gateway routes each request by policy",
    ),
    (("round 125: memory grows until the buffer is full", "key"), "bssxh 125: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 125: memory grows until the buffer is full", "lemon"), "csgbq 125: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 125: memory grows until the buffer is full", "a"), "round 125: memory grows until the buffer is full"),
    (("round 125: memory grows until the buffer is full", "zz"), "qntmc 125: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 125: memory grows until the buffer is full", "AgentU"),
        "ruyaw 125: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 125: memory grows until the buffer is full", "keyboard"),
        "bssor 125: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 125: memory grows until the buffer is full", "AA"), "round 125: memory grows until the buffer is full"),
    (("round 125: the cluster mirrors every packet twice", "key"), "bssxh 125: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 125: the cluster mirrors every packet twice", "lemon"),
        "csgbq 125: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 125: the cluster mirrors every packet twice", "a"), "round 125: the cluster mirrors every packet twice"),
    (("round 125: the cluster mirrors every packet twice", "zz"), "qntmc 125: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 125: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 125: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 125: the cluster mirrors every packet twice", "keyboard"),
        "bssor 125: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 125: the cluster mirrors every packet twice", "AA"), "round 125: the cluster mirrors every packet twice"),
    (
        ("round 125: ranking uses tokens learned from the corpus", "key"),
        "bssxh 125: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 125: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", "a"),
        "round 125: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 125: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 125: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 125: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", "AA"),
        "round 125: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 125: a long session ends when the candle dies", "key"),
        "bssxh 125: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 125: a long session ends when the candle dies", "lemon"),
        "csgbq 125: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 125: a long session ends when the candle dies", "a"),
        "round 125: a long session ends when the candle dies",
    ),
    (
        ("round 125: a long session ends when the candle dies", "zz"),
        "qntmc 125: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 125: a long session ends when the candle dies", "AgentU"),
        "ruyaw 125: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 125: a long session ends when the candle dies", "keyboard"),
        "bssor 125: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 125: a long session ends when the candle dies", "AA"),
        "round 125: a long session ends when the candle dies",
    ),
    (("round 125: encode the prompt then map the result", "key"), "bssxh 125: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 125: encode the prompt then map the result", "lemon"), "csgbq 125: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 125: encode the prompt then map the result", "a"), "round 125: encode the prompt then map the result"),
    (("round 125: encode the prompt then map the result", "zz"), "qntmc 125: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 125: encode the prompt then map the result", "AgentU"),
        "ruyaw 125: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 125: encode the prompt then map the result", "keyboard"),
        "bssor 125: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 125: encode the prompt then map the result", "AA"), "round 125: encode the prompt then map the result"),
    (("round 125: the kernel wakes the worker at dawn", "key"), "bssxh 125: rri iovlop ukocc xfo ambocb er neux"),
    (("round 125: the kernel wakes the worker at dawn", "lemon"), "csgbq 125: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 125: the kernel wakes the worker at dawn", "a"), "round 125: the kernel wakes the worker at dawn"),
    (("round 125: the kernel wakes the worker at dawn", "zz"), "qntmc 125: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 125: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 125: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 125: the kernel wakes the worker at dawn", "keyboard"), "bssor 125: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 125: the kernel wakes the worker at dawn", "AA"), "round 125: the kernel wakes the worker at dawn"),
    (("round 125: service latency drops after the patch", "key"), "bssxh 125: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 125: service latency drops after the patch", "lemon"), "csgbq 125: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 125: service latency drops after the patch", "a"), "round 125: service latency drops after the patch"),
    (("round 125: service latency drops after the patch", "zz"), "qntmc 125: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 125: service latency drops after the patch", "AgentU"),
        "ruyaw 125: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 125: service latency drops after the patch", "keyboard"),
        "bssor 125: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 125: service latency drops after the patch", "AA"), "round 125: service latency drops after the patch"),
    (
        ("round 125: the library caches every vector it sees", "key"),
        "bssxh 125: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 125: the library caches every vector it sees", "lemon"),
        "csgbq 125: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 125: the library caches every vector it sees", "a"), "round 125: the library caches every vector it sees"),
    (
        ("round 125: the library caches every vector it sees", "zz"),
        "qntmc 125: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 125: the library caches every vector it sees", "AgentU"),
        "ruyaw 125: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 125: the library caches every vector it sees", "keyboard"),
        "bssor 125: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 125: the library caches every vector it sees", "AA"),
        "round 125: the library caches every vector it sees",
    ),
    (("round 125: agents argue then the debate resolves", "key"), "bssxh 125: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 125: agents argue then the debate resolves", "lemon"), "csgbq 125: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 125: agents argue then the debate resolves", "a"), "round 125: agents argue then the debate resolves"),
    (("round 125: agents argue then the debate resolves", "zz"), "qntmc 125: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 125: agents argue then the debate resolves", "AgentU"),
        "ruyaw 125: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 125: agents argue then the debate resolves", "keyboard"),
        "bssor 125: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 125: agents argue then the debate resolves", "AA"), "round 125: agents argue then the debate resolves"),
    (("round 125: the filter keeps only strong matches", "key"), "bssxh 125: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 125: the filter keeps only strong matches", "lemon"), "csgbq 125: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 125: the filter keeps only strong matches", "a"), "round 125: the filter keeps only strong matches"),
    (("round 125: the filter keeps only strong matches", "zz"), "qntmc 125: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 125: the filter keeps only strong matches", "AgentU"), "ruyaw 125: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 125: the filter keeps only strong matches", "keyboard"),
        "bssor 125: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 125: the filter keeps only strong matches", "AA"), "round 125: the filter keeps only strong matches"),
    (("round 125: the model answers with a short reply", "key"), "bssxh 125: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 125: the model answers with a short reply", "lemon"), "csgbq 125: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 125: the model answers with a short reply", "a"), "round 125: the model answers with a short reply"),
    (("round 125: the model answers with a short reply", "zz"), "qntmc 125: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 125: the model answers with a short reply", "AgentU"), "ruyaw 125: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 125: the model answers with a short reply", "keyboard"),
        "bssor 125: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 125: the model answers with a short reply", "AA"), "round 125: the model answers with a short reply"),
    (
        ("round 125: the recorder stores the reasoning trace", "key"),
        "bssxh 125: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 125: the recorder stores the reasoning trace", "lemon"),
        "csgbq 125: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 125: the recorder stores the reasoning trace", "a"), "round 125: the recorder stores the reasoning trace"),
    (
        ("round 125: the recorder stores the reasoning trace", "zz"),
        "qntmc 125: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 125: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 125: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 125: the recorder stores the reasoning trace", "keyboard"),
        "bssor 125: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 125: the recorder stores the reasoning trace", "AA"),
        "round 125: the recorder stores the reasoning trace",
    ),
    (("round 125: the angel watches the processor run", "key"), "bssxh 125: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 125: the angel watches the processor run", "lemon"), "csgbq 125: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 125: the angel watches the processor run", "a"), "round 125: the angel watches the processor run"),
    (("round 125: the angel watches the processor run", "zz"), "qntmc 125: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 125: the angel watches the processor run", "AgentU"), "ruyaw 125: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 125: the angel watches the processor run", "keyboard"), "bssor 125: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 125: the angel watches the processor run", "AA"), "round 125: the angel watches the processor run"),
    (("round 125: angle of the vector decides the match", "key"), "bssxh 125: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 125: angle of the vector decides the match", "lemon"), "csgbq 125: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 125: angle of the vector decides the match", "a"), "round 125: angle of the vector decides the match"),
    (("round 125: angle of the vector decides the match", "zz"), "qntmc 125: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 125: angle of the vector decides the match", "AgentU"),
        "ruyaw 125: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 125: angle of the vector decides the match", "keyboard"),
        "bssor 125: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 125: angle of the vector decides the match", "AA"), "round 125: angle of the vector decides the match"),
    (
        ("round 125: the candle burns twice as long at night", "key"),
        "bssxh 125: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 125: the candle burns twice as long at night", "lemon"),
        "csgbq 125: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 125: the candle burns twice as long at night", "a"), "round 125: the candle burns twice as long at night"),
    (
        ("round 125: the candle burns twice as long at night", "zz"),
        "qntmc 125: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 125: the candle burns twice as long at night", "AgentU"),
        "ruyaw 125: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 125: the candle burns twice as long at night", "keyboard"),
        "bssor 125: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 125: the candle burns twice as long at night", "AA"),
        "round 125: the candle burns twice as long at night",
    ),
    (("round 125: a mirror of the universe in one line", "key"), "bssxh 125: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 125: a mirror of the universe in one line", "lemon"), "csgbq 125: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 125: a mirror of the universe in one line", "a"), "round 125: a mirror of the universe in one line"),
    (("round 125: a mirror of the universe in one line", "zz"), "qntmc 125: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 125: a mirror of the universe in one line", "AgentU"), "ruyaw 125: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 125: a mirror of the universe in one line", "keyboard"),
        "bssor 125: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 125: a mirror of the universe in one line", "AA"), "round 125: a mirror of the universe in one line"),
    (("round 125: the queue drains before the storm", "key"), "bssxh 125: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 125: the queue drains before the storm", "lemon"), "csgbq 125: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 125: the queue drains before the storm", "a"), "round 125: the queue drains before the storm"),
    (("round 125: the queue drains before the storm", "zz"), "qntmc 125: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 125: the queue drains before the storm", "AgentU"), "ruyaw 125: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 125: the queue drains before the storm", "keyboard"), "bssor 125: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 125: the queue drains before the storm", "AA"), "round 125: the queue drains before the storm"),
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
