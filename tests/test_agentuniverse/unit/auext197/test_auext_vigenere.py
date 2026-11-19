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
    (("kitten197", "key"), "umrdil197"),
    (("kitten197", "lemon"), "vmfhry197"),
    (("kitten197", "a"), "kitten197"),
    (("kitten197", "zz"), "jhssdm197"),
    (("kitten197", "AgentU"), "koxgxh197"),
    (("kitten197", "keyboard"), "umrusn197"),
    (("kitten197", "AA"), "kitten197"),
    (("sitting197", "key"), "cmrdmlq197"),
    (("sitting197", "lemon"), "dmfhvyk197"),
    (("sitting197", "a"), "sitting197"),
    (("sitting197", "zz"), "rhsshmf197"),
    (("sitting197", "AgentU"), "soxgbhg197"),
    (("sitting197", "keyboard"), "cmruwnx197"),
    (("sitting197", "AA"), "sitting197"),
    (("agent197", "key"), "kkcxx197"),
    (("agent197", "lemon"), "lkqbg197"),
    (("agent197", "a"), "agent197"),
    (("agent197", "zz"), "zfdms197"),
    (("agent197", "AgentU"), "amiam197"),
    (("agent197", "keyboard"), "kkcoh197"),
    (("agent197", "AA"), "agent197"),
    (("angle197", "key"), "krevi197"),
    (("angle197", "lemon"), "lrszr197"),
    (("angle197", "a"), "angle197"),
    (("angle197", "zz"), "zmfkd197"),
    (("angle197", "AgentU"), "atkyx197"),
    (("angle197", "keyboard"), "krems197"),
    (("angle197", "AA"), "angle197"),
    (("universe197", "key"), "ergfipci197"),
    (("universe197", "lemon"), "frujrcwq197"),
    (("universe197", "a"), "universe197"),
    (("universe197", "zz"), "tmhudqrd197"),
    (("universe197", "AgentU"), "utmixlsk197"),
    (("universe197", "keyboard"), "ergwsrjh197"),
    (("universe197", "AA"), "universe197"),
    (("memory197", "key"), "wikyvw197"),
    (("memory197", "lemon"), "xiycej197"),
    (("memory197", "a"), "memory197"),
    (("memory197", "zz"), "ldlnqx197"),
    (("memory197", "AgentU"), "mkqbks197"),
    (("memory197", "keyboard"), "wikpfy197"),
    (("memory197", "AA"), "memory197"),
    (("stream197", "key"), "cxpoek197"),
    (("stream197", "lemon"), "dxdsnx197"),
    (("stream197", "a"), "stream197"),
    (("stream197", "zz"), "rsqdzl197"),
    (("stream197", "AgentU"), "szvrtg197"),
    (("stream197", "keyboard"), "cxpfom197"),
    (("stream197", "AA"), "stream197"),
    (("context197", "key"), "msldivd197"),
    (("context197", "lemon"), "nszhrix197"),
    (("context197", "a"), "context197"),
    (("context197", "zz"), "bnmsdws197"),
    (("context197", "AgentU"), "curgxrt197"),
    (("context197", "keyboard"), "mslusxk197"),
    (("context197", "AA"), "context197"),
    (("knowledge197", "key"), "urmgpcnkc197"),
    (("knowledge197", "lemon"), "vrakyphss197"),
    (("knowledge197", "a"), "knowledge197"),
    (("knowledge197", "zz"), "jmnvkdcfd197"),
    (("knowledge197", "AgentU"), "ktsjeydmi197"),
    (("knowledge197", "keyboard"), "urmxzeujo197"),
    (("knowledge197", "AA"), "knowledge197"),
    (("vector197", "key"), "fiadsp197"),
    (("vector197", "lemon"), "giohbc197"),
    (("vector197", "a"), "vector197"),
    (("vector197", "zz"), "udbsnq197"),
    (("vector197", "AgentU"), "vkgghl197"),
    (("vector197", "keyboard"), "fiaucr197"),
    (("vector197", "AA"), "vector197"),
    (("processor197", "key"), "zvmmiqcsp197"),
    (("processor197", "lemon"), "avaqrdwaf197"),
    (("processor197", "a"), "processor197"),
    (("processor197", "zz"), "oqnbdrrnq197"),
    (("processor197", "AgentU"), "pxspxmsuv197"),
    (("processor197", "keyboard"), "zvmdssjrb197"),
    (("processor197", "AA"), "processor197"),
    (("reasoning197", "key"), "biycslsre197"),
    (("reasoning197", "lemon"), "cimgbymzu197"),
    (("reasoning197", "a"), "reasoning197"),
    (("reasoning197", "zz"), "qdzrnmhmf197"),
    (("reasoning197", "AgentU"), "rkefhhitk197"),
    (("reasoning197", "keyboard"), "biytcnzqq197"),
    (("reasoning197", "AA"), "reasoning197"),
    (("machine197", "key"), "wearmlo197"),
    (("machine197", "lemon"), "xeovvyi197"),
    (("machine197", "a"), "machine197"),
    (("machine197", "zz"), "lzbghmd197"),
    (("machine197", "AgentU"), "mggubhe197"),
    (("machine197", "keyboard"), "weaiwnv197"),
    (("machine197", "AA"), "machine197"),
    (("learning197", "key"), "viybrgxk197"),
    (("learning197", "lemon"), "wimfatrs197"),
    (("learning197", "a"), "learning197"),
    (("learning197", "zz"), "kdzqmhmf197"),
    (("learning197", "AgentU"), "lkeegcnm197"),
    (("learning197", "keyboard"), "viysbiej197"),
    (("learning197", "AA"), "learning197"),
    (("model197", "key"), "wsbop197"),
    (("model197", "lemon"), "xspsy197"),
    (("model197", "a"), "model197"),
    (("model197", "zz"), "lncdk197"),
    (("model197", "AgentU"), "muhre197"),
    (("model197", "keyboard"), "wsbfz197"),
    (("model197", "AA"), "model197"),
    (("token197", "key"), "dsior197"),
    (("token197", "lemon"), "eswsa197"),
    (("token197", "a"), "token197"),
    (("token197", "zz"), "snjdm197"),
    (("token197", "AgentU"), "tuorg197"),
    (("token197", "keyboard"), "dsifb197"),
    (("token197", "AA"), "token197"),
    (("prompt197", "key"), "zvmwtr197"),
    (("prompt197", "lemon"), "avaace197"),
    (("prompt197", "a"), "prompt197"),
    (("prompt197", "zz"), "oqnlos197"),
    (("prompt197", "AgentU"), "pxszin197"),
    (("prompt197", "keyboard"), "zvmndt197"),
    (("prompt197", "AA"), "prompt197"),
    (("session197", "key"), "ciqcmmx197"),
    (("session197", "lemon"), "diegvzr197"),
    (("session197", "a"), "session197"),
    (("session197", "zz"), "rdrrhnm197"),
    (("session197", "AgentU"), "skwfbin197"),
    (("session197", "keyboard"), "ciqtwoe197"),
    (("session197", "AA"), "session197"),
    (("library197", "key"), "vmzbepi197"),
    (("library197", "lemon"), "wmnfncc197"),
    (("library197", "a"), "library197"),
    (("library197", "zz"), "khaqzqx197"),
    (("library197", "AgentU"), "lofetly197"),
    (("library197", "keyboard"), "vmzsorp197"),
    (("library197", "AA"), "library197"),
    (("service197", "key"), "cipfmao197"),
    (("service197", "lemon"), "didjvni197"),
    (("service197", "a"), "service197"),
    (("service197", "zz"), "rdquhbd197"),
    (("service197", "AgentU"), "skvibwe197"),
    (("service197", "keyboard"), "cipwwcv197"),
    (("service197", "AA"), "service197"),
    (("gateway197", "key"), "qeroayi197"),
    (("gateway197", "lemon"), "refsjlc197"),
    (("gateway197", "a"), "gateway197"),
    (("gateway197", "zz"), "fzsdvzx197"),
    (("gateway197", "AgentU"), "ggxrpuy197"),
    (("gateway197", "keyboard"), "qerfkap197"),
    (("gateway197", "AA"), "gateway197"),
    (("storage197", "key"), "cxmbeeo197"),
    (("storage197", "lemon"), "dxafnri197"),
    (("storage197", "a"), "storage197"),
    (("storage197", "zz"), "rsnqzfd197"),
    (("storage197", "AgentU"), "szsetae197"),
    (("storage197", "keyboard"), "cxmsogv197"),
    (("storage197", "AA"), "storage197"),
    (("network197", "key"), "xirgspu197"),
    (("network197", "lemon"), "yifkbco197"),
    (("network197", "a"), "network197"),
    (("network197", "zz"), "mdsvnqj197"),
    (("network197", "AgentU"), "nkxjhlk197"),
    (("network197", "keyboard"), "xirxcrb197"),
    (("network197", "AA"), "network197"),
    (("latency197", "key"), "verorai197"),
    (("latency197", "lemon"), "wefsanc197"),
    (("latency197", "a"), "latency197"),
    (("latency197", "zz"), "kzsdmbx197"),
    (("latency197", "AgentU"), "lgxrgwy197"),
    (("latency197", "keyboard"), "verfbcp197"),
    (("latency197", "AA"), "latency197"),
    (("buffer197", "key"), "lydpip197"),
    (("buffer197", "lemon"), "myrtrc197"),
    (("buffer197", "a"), "buffer197"),
    (("buffer197", "zz"), "ateedq197"),
    (("buffer197", "AgentU"), "bajsxl197"),
    (("buffer197", "keyboard"), "lydgsr197"),
    (("buffer197", "AA"), "buffer197"),
    (("queue197", "key"), "aycei197"),
    (("queue197", "lemon"), "byqir197"),
    (("queue197", "a"), "queue197"),
    (("queue197", "zz"), "ptdtd197"),
    (("queue197", "AgentU"), "qaihx197"),
    (("queue197", "keyboard"), "aycvs197"),
    (("queue197", "AA"), "queue197"),
    (("worker197", "key"), "gspuip197"),
    (("worker197", "lemon"), "hsdyrc197"),
    (("worker197", "a"), "worker197"),
    (("worker197", "zz"), "vnqjdq197"),
    (("worker197", "AgentU"), "wuvxxl197"),
    (("worker197", "keyboard"), "gsplsr197"),
    (("worker197", "AA"), "worker197"),
    (("kernel197", "key"), "uipxij197"),
    (("kernel197", "lemon"), "vidbrw197"),
    (("kernel197", "a"), "kernel197"),
    (("kernel197", "zz"), "jdqmdk197"),
    (("kernel197", "AgentU"), "kkvaxf197"),
    (("kernel197", "keyboard"), "uiposl197"),
    (("kernel197", "AA"), "kernel197"),
    (("signal197", "key"), "cmexej197"),
    (("signal197", "lemon"), "dmsbnw197"),
    (("signal197", "a"), "signal197"),
    (("signal197", "zz"), "rhfmzk197"),
    (("signal197", "AgentU"), "sokatf197"),
    (("signal197", "keyboard"), "cmeool197"),
    (("signal197", "AA"), "signal197"),
    (("packet197", "key"), "zeauir197"),
    (("packet197", "lemon"), "aeoyre197"),
    (("packet197", "a"), "packet197"),
    (("packet197", "zz"), "ozbjds197"),
    (("packet197", "AgentU"), "pggxxn197"),
    (("packet197", "keyboard"), "zealst197"),
    (("packet197", "AA"), "packet197"),
    (("router197", "key"), "bssdip197"),
    (("router197", "lemon"), "csghrc197"),
    (("router197", "a"), "router197"),
    (("router197", "zz"), "qntsdq197"),
    (("router197", "AgentU"), "ruygxl197"),
    (("router197", "keyboard"), "bssusr197"),
    (("router197", "AA"), "router197"),
    (("cluster197", "key"), "mpscxcb197"),
    (("cluster197", "lemon"), "npgggpv197"),
    (("cluster197", "a"), "cluster197"),
    (("cluster197", "zz"), "bktrsdq197"),
    (("cluster197", "AgentU"), "cryfmyr197"),
    (("cluster197", "keyboard"), "mpsthei197"),
    (("cluster197", "AA"), "cluster197"),
    (("mirror197", "key"), "wmpbsp197"),
    (("mirror197", "lemon"), "xmdfbc197"),
    (("mirror197", "a"), "mirror197"),
    (("mirror197", "zz"), "lhqqnq197"),
    (("mirror197", "AgentU"), "movehl197"),
    (("mirror197", "keyboard"), "wmpscr197"),
    (("mirror197", "AA"), "mirror197"),
    (("filter197", "key"), "pmjdip197"),
    (("filter197", "lemon"), "qmxhrc197"),
    (("filter197", "a"), "filter197"),
    (("filter197", "zz"), "ehksdq197"),
    (("filter197", "AgentU"), "fopgxl197"),
    (("filter197", "keyboard"), "pmjusr197"),
    (("filter197", "AA"), "filter197"),
    (("ranking197", "key"), "belumlq197"),
    (("ranking197", "lemon"), "cezyvyk197"),
    (("ranking197", "a"), "ranking197"),
    (("ranking197", "zz"), "qzmjhmf197"),
    (("ranking197", "AgentU"), "rgrxbhg197"),
    (("ranking197", "keyboard"), "bellwnx197"),
    (("ranking197", "AA"), "ranking197"),
    (("encoding197", "key"), "orayhgxk197"),
    (("encoding197", "lemon"), "procqtrs197"),
    (("encoding197", "a"), "encoding197"),
    (("encoding197", "zz"), "dmbnchmf197"),
    (("encoding197", "AgentU"), "etgbwcnm197"),
    (("encoding197", "keyboard"), "orapriej197"),
    (("encoding197", "AA"), "encoding197"),
    (("mapping197", "key"), "wenzmlq197"),
    (("mapping197", "lemon"), "xebdvyk197"),
    (("mapping197", "a"), "mapping197"),
    (("mapping197", "zz"), "lzoohmf197"),
    (("mapping197", "AgentU"), "mgtcbhg197"),
    (("mapping197", "keyboard"), "wenqwnx197"),
    (("mapping197", "AA"), "mapping197"),
    (("record197", "key"), "biayvb197"),
    (("record197", "lemon"), "cioceo197"),
    (("record197", "a"), "record197"),
    (("record197", "zz"), "qdbnqc197"),
    (("record197", "AgentU"), "rkgbkx197"),
    (("record197", "keyboard"), "biapfd197"),
    (("record197", "AA"), "record197"),
    (("candle197", "key"), "melnpc197"),
    (("candle197", "lemon"), "nezryp197"),
    (("candle197", "a"), "candle197"),
    (("candle197", "zz"), "bzmckd197"),
    (("candle197", "AgentU"), "cgrqey197"),
    (("candle197", "keyboard"), "meleze197"),
    (("candle197", "AA"), "candle197"),
    (("thread197", "key"), "dlpoeb197"),
    (("thread197", "lemon"), "eldsno197"),
    (("thread197", "a"), "thread197"),
    (("thread197", "zz"), "sgqdzc197"),
    (("thread197", "AgentU"), "tnvrtx197"),
    (("thread197", "keyboard"), "dlpfod197"),
    (("thread197", "AA"), "thread197"),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 197: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 197: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "a"),
        "round 197: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 197: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 197: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 197: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 197: the quick brown fox jumps over the lazy dog", "AA"),
        "round 197: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "key"),
        "bssxh 197: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 197: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "a"),
        "round 197: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 197: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 197: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 197: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 197: agentuniverse is a framework for multi agents", "AA"),
        "round 197: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 197: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 197: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "a"),
        "round 197: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 197: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 197: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 197: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 197: knowledge stored as vectors enables retrieval", "AA"),
        "round 197: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 197: the processor reads the record then stops", "key"),
        "bssxh 197: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 197: the processor reads the record then stops", "lemon"),
        "csgbq 197: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 197: the processor reads the record then stops", "a"),
        "round 197: the processor reads the record then stops",
    ),
    (
        ("round 197: the processor reads the record then stops", "zz"),
        "qntmc 197: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 197: the processor reads the record then stops", "AgentU"),
        "ruyaw 197: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 197: the processor reads the record then stops", "keyboard"),
        "bssor 197: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 197: the processor reads the record then stops", "AA"),
        "round 197: the processor reads the record then stops",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "key"),
        "bssxh 197: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "lemon"),
        "csgbq 197: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "a"),
        "round 197: a worker pulls the next task from the queue",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "zz"),
        "qntmc 197: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 197: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "keyboard"),
        "bssor 197: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 197: a worker pulls the next task from the queue", "AA"),
        "round 197: a worker pulls the next task from the queue",
    ),
    (
        ("round 197: signals travel through the network layer", "key"),
        "bssxh 197: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 197: signals travel through the network layer", "lemon"),
        "csgbq 197: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 197: signals travel through the network layer", "a"),
        "round 197: signals travel through the network layer",
    ),
    (
        ("round 197: signals travel through the network layer", "zz"),
        "qntmc 197: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 197: signals travel through the network layer", "AgentU"),
        "ruyaw 197: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 197: signals travel through the network layer", "keyboard"),
        "bssor 197: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 197: signals travel through the network layer", "AA"),
        "round 197: signals travel through the network layer",
    ),
    (
        ("round 197: the gateway routes each request by policy", "key"),
        "bssxh 197: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 197: the gateway routes each request by policy", "lemon"),
        "csgbq 197: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 197: the gateway routes each request by policy", "a"),
        "round 197: the gateway routes each request by policy",
    ),
    (
        ("round 197: the gateway routes each request by policy", "zz"),
        "qntmc 197: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 197: the gateway routes each request by policy", "AgentU"),
        "ruyaw 197: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 197: the gateway routes each request by policy", "keyboard"),
        "bssor 197: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 197: the gateway routes each request by policy", "AA"),
        "round 197: the gateway routes each request by policy",
    ),
    (("round 197: memory grows until the buffer is full", "key"), "bssxh 197: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 197: memory grows until the buffer is full", "lemon"), "csgbq 197: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 197: memory grows until the buffer is full", "a"), "round 197: memory grows until the buffer is full"),
    (("round 197: memory grows until the buffer is full", "zz"), "qntmc 197: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 197: memory grows until the buffer is full", "AgentU"),
        "ruyaw 197: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 197: memory grows until the buffer is full", "keyboard"),
        "bssor 197: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 197: memory grows until the buffer is full", "AA"), "round 197: memory grows until the buffer is full"),
    (("round 197: the cluster mirrors every packet twice", "key"), "bssxh 197: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 197: the cluster mirrors every packet twice", "lemon"),
        "csgbq 197: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 197: the cluster mirrors every packet twice", "a"), "round 197: the cluster mirrors every packet twice"),
    (("round 197: the cluster mirrors every packet twice", "zz"), "qntmc 197: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 197: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 197: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 197: the cluster mirrors every packet twice", "keyboard"),
        "bssor 197: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 197: the cluster mirrors every packet twice", "AA"), "round 197: the cluster mirrors every packet twice"),
    (
        ("round 197: ranking uses tokens learned from the corpus", "key"),
        "bssxh 197: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 197: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", "a"),
        "round 197: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 197: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 197: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 197: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 197: ranking uses tokens learned from the corpus", "AA"),
        "round 197: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 197: a long session ends when the candle dies", "key"),
        "bssxh 197: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 197: a long session ends when the candle dies", "lemon"),
        "csgbq 197: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 197: a long session ends when the candle dies", "a"),
        "round 197: a long session ends when the candle dies",
    ),
    (
        ("round 197: a long session ends when the candle dies", "zz"),
        "qntmc 197: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 197: a long session ends when the candle dies", "AgentU"),
        "ruyaw 197: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 197: a long session ends when the candle dies", "keyboard"),
        "bssor 197: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 197: a long session ends when the candle dies", "AA"),
        "round 197: a long session ends when the candle dies",
    ),
    (("round 197: encode the prompt then map the result", "key"), "bssxh 197: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 197: encode the prompt then map the result", "lemon"), "csgbq 197: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 197: encode the prompt then map the result", "a"), "round 197: encode the prompt then map the result"),
    (("round 197: encode the prompt then map the result", "zz"), "qntmc 197: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 197: encode the prompt then map the result", "AgentU"),
        "ruyaw 197: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 197: encode the prompt then map the result", "keyboard"),
        "bssor 197: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 197: encode the prompt then map the result", "AA"), "round 197: encode the prompt then map the result"),
    (("round 197: the kernel wakes the worker at dawn", "key"), "bssxh 197: rri iovlop ukocc xfo ambocb er neux"),
    (("round 197: the kernel wakes the worker at dawn", "lemon"), "csgbq 197: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 197: the kernel wakes the worker at dawn", "a"), "round 197: the kernel wakes the worker at dawn"),
    (("round 197: the kernel wakes the worker at dawn", "zz"), "qntmc 197: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 197: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 197: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 197: the kernel wakes the worker at dawn", "keyboard"), "bssor 197: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 197: the kernel wakes the worker at dawn", "AA"), "round 197: the kernel wakes the worker at dawn"),
    (("round 197: service latency drops after the patch", "key"), "bssxh 197: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 197: service latency drops after the patch", "lemon"), "csgbq 197: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 197: service latency drops after the patch", "a"), "round 197: service latency drops after the patch"),
    (("round 197: service latency drops after the patch", "zz"), "qntmc 197: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 197: service latency drops after the patch", "AgentU"),
        "ruyaw 197: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 197: service latency drops after the patch", "keyboard"),
        "bssor 197: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 197: service latency drops after the patch", "AA"), "round 197: service latency drops after the patch"),
    (
        ("round 197: the library caches every vector it sees", "key"),
        "bssxh 197: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 197: the library caches every vector it sees", "lemon"),
        "csgbq 197: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 197: the library caches every vector it sees", "a"), "round 197: the library caches every vector it sees"),
    (
        ("round 197: the library caches every vector it sees", "zz"),
        "qntmc 197: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 197: the library caches every vector it sees", "AgentU"),
        "ruyaw 197: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 197: the library caches every vector it sees", "keyboard"),
        "bssor 197: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 197: the library caches every vector it sees", "AA"),
        "round 197: the library caches every vector it sees",
    ),
    (("round 197: agents argue then the debate resolves", "key"), "bssxh 197: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 197: agents argue then the debate resolves", "lemon"), "csgbq 197: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 197: agents argue then the debate resolves", "a"), "round 197: agents argue then the debate resolves"),
    (("round 197: agents argue then the debate resolves", "zz"), "qntmc 197: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 197: agents argue then the debate resolves", "AgentU"),
        "ruyaw 197: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 197: agents argue then the debate resolves", "keyboard"),
        "bssor 197: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 197: agents argue then the debate resolves", "AA"), "round 197: agents argue then the debate resolves"),
    (("round 197: the filter keeps only strong matches", "key"), "bssxh 197: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 197: the filter keeps only strong matches", "lemon"), "csgbq 197: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 197: the filter keeps only strong matches", "a"), "round 197: the filter keeps only strong matches"),
    (("round 197: the filter keeps only strong matches", "zz"), "qntmc 197: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 197: the filter keeps only strong matches", "AgentU"), "ruyaw 197: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 197: the filter keeps only strong matches", "keyboard"),
        "bssor 197: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 197: the filter keeps only strong matches", "AA"), "round 197: the filter keeps only strong matches"),
    (("round 197: the model answers with a short reply", "key"), "bssxh 197: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 197: the model answers with a short reply", "lemon"), "csgbq 197: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 197: the model answers with a short reply", "a"), "round 197: the model answers with a short reply"),
    (("round 197: the model answers with a short reply", "zz"), "qntmc 197: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 197: the model answers with a short reply", "AgentU"), "ruyaw 197: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 197: the model answers with a short reply", "keyboard"),
        "bssor 197: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 197: the model answers with a short reply", "AA"), "round 197: the model answers with a short reply"),
    (
        ("round 197: the recorder stores the reasoning trace", "key"),
        "bssxh 197: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 197: the recorder stores the reasoning trace", "lemon"),
        "csgbq 197: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 197: the recorder stores the reasoning trace", "a"), "round 197: the recorder stores the reasoning trace"),
    (
        ("round 197: the recorder stores the reasoning trace", "zz"),
        "qntmc 197: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 197: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 197: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 197: the recorder stores the reasoning trace", "keyboard"),
        "bssor 197: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 197: the recorder stores the reasoning trace", "AA"),
        "round 197: the recorder stores the reasoning trace",
    ),
    (("round 197: the angel watches the processor run", "key"), "bssxh 197: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 197: the angel watches the processor run", "lemon"), "csgbq 197: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 197: the angel watches the processor run", "a"), "round 197: the angel watches the processor run"),
    (("round 197: the angel watches the processor run", "zz"), "qntmc 197: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 197: the angel watches the processor run", "AgentU"), "ruyaw 197: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 197: the angel watches the processor run", "keyboard"), "bssor 197: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 197: the angel watches the processor run", "AA"), "round 197: the angel watches the processor run"),
    (("round 197: angle of the vector decides the match", "key"), "bssxh 197: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 197: angle of the vector decides the match", "lemon"), "csgbq 197: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 197: angle of the vector decides the match", "a"), "round 197: angle of the vector decides the match"),
    (("round 197: angle of the vector decides the match", "zz"), "qntmc 197: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 197: angle of the vector decides the match", "AgentU"),
        "ruyaw 197: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 197: angle of the vector decides the match", "keyboard"),
        "bssor 197: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 197: angle of the vector decides the match", "AA"), "round 197: angle of the vector decides the match"),
    (
        ("round 197: the candle burns twice as long at night", "key"),
        "bssxh 197: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 197: the candle burns twice as long at night", "lemon"),
        "csgbq 197: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 197: the candle burns twice as long at night", "a"), "round 197: the candle burns twice as long at night"),
    (
        ("round 197: the candle burns twice as long at night", "zz"),
        "qntmc 197: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 197: the candle burns twice as long at night", "AgentU"),
        "ruyaw 197: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 197: the candle burns twice as long at night", "keyboard"),
        "bssor 197: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 197: the candle burns twice as long at night", "AA"),
        "round 197: the candle burns twice as long at night",
    ),
    (("round 197: a mirror of the universe in one line", "key"), "bssxh 197: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 197: a mirror of the universe in one line", "lemon"), "csgbq 197: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 197: a mirror of the universe in one line", "a"), "round 197: a mirror of the universe in one line"),
    (("round 197: a mirror of the universe in one line", "zz"), "qntmc 197: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 197: a mirror of the universe in one line", "AgentU"), "ruyaw 197: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 197: a mirror of the universe in one line", "keyboard"),
        "bssor 197: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 197: a mirror of the universe in one line", "AA"), "round 197: a mirror of the universe in one line"),
    (("round 197: the queue drains before the storm", "key"), "bssxh 197: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 197: the queue drains before the storm", "lemon"), "csgbq 197: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 197: the queue drains before the storm", "a"), "round 197: the queue drains before the storm"),
    (("round 197: the queue drains before the storm", "zz"), "qntmc 197: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 197: the queue drains before the storm", "AgentU"), "ruyaw 197: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 197: the queue drains before the storm", "keyboard"), "bssor 197: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 197: the queue drains before the storm", "AA"), "round 197: the queue drains before the storm"),
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
