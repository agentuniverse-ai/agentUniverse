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
    (("kitten111", "key"), "umrdil111"),
    (("kitten111", "lemon"), "vmfhry111"),
    (("kitten111", "a"), "kitten111"),
    (("kitten111", "zz"), "jhssdm111"),
    (("kitten111", "AgentU"), "koxgxh111"),
    (("kitten111", "keyboard"), "umrusn111"),
    (("kitten111", "AA"), "kitten111"),
    (("sitting111", "key"), "cmrdmlq111"),
    (("sitting111", "lemon"), "dmfhvyk111"),
    (("sitting111", "a"), "sitting111"),
    (("sitting111", "zz"), "rhsshmf111"),
    (("sitting111", "AgentU"), "soxgbhg111"),
    (("sitting111", "keyboard"), "cmruwnx111"),
    (("sitting111", "AA"), "sitting111"),
    (("agent111", "key"), "kkcxx111"),
    (("agent111", "lemon"), "lkqbg111"),
    (("agent111", "a"), "agent111"),
    (("agent111", "zz"), "zfdms111"),
    (("agent111", "AgentU"), "amiam111"),
    (("agent111", "keyboard"), "kkcoh111"),
    (("agent111", "AA"), "agent111"),
    (("angle111", "key"), "krevi111"),
    (("angle111", "lemon"), "lrszr111"),
    (("angle111", "a"), "angle111"),
    (("angle111", "zz"), "zmfkd111"),
    (("angle111", "AgentU"), "atkyx111"),
    (("angle111", "keyboard"), "krems111"),
    (("angle111", "AA"), "angle111"),
    (("universe111", "key"), "ergfipci111"),
    (("universe111", "lemon"), "frujrcwq111"),
    (("universe111", "a"), "universe111"),
    (("universe111", "zz"), "tmhudqrd111"),
    (("universe111", "AgentU"), "utmixlsk111"),
    (("universe111", "keyboard"), "ergwsrjh111"),
    (("universe111", "AA"), "universe111"),
    (("memory111", "key"), "wikyvw111"),
    (("memory111", "lemon"), "xiycej111"),
    (("memory111", "a"), "memory111"),
    (("memory111", "zz"), "ldlnqx111"),
    (("memory111", "AgentU"), "mkqbks111"),
    (("memory111", "keyboard"), "wikpfy111"),
    (("memory111", "AA"), "memory111"),
    (("stream111", "key"), "cxpoek111"),
    (("stream111", "lemon"), "dxdsnx111"),
    (("stream111", "a"), "stream111"),
    (("stream111", "zz"), "rsqdzl111"),
    (("stream111", "AgentU"), "szvrtg111"),
    (("stream111", "keyboard"), "cxpfom111"),
    (("stream111", "AA"), "stream111"),
    (("context111", "key"), "msldivd111"),
    (("context111", "lemon"), "nszhrix111"),
    (("context111", "a"), "context111"),
    (("context111", "zz"), "bnmsdws111"),
    (("context111", "AgentU"), "curgxrt111"),
    (("context111", "keyboard"), "mslusxk111"),
    (("context111", "AA"), "context111"),
    (("knowledge111", "key"), "urmgpcnkc111"),
    (("knowledge111", "lemon"), "vrakyphss111"),
    (("knowledge111", "a"), "knowledge111"),
    (("knowledge111", "zz"), "jmnvkdcfd111"),
    (("knowledge111", "AgentU"), "ktsjeydmi111"),
    (("knowledge111", "keyboard"), "urmxzeujo111"),
    (("knowledge111", "AA"), "knowledge111"),
    (("vector111", "key"), "fiadsp111"),
    (("vector111", "lemon"), "giohbc111"),
    (("vector111", "a"), "vector111"),
    (("vector111", "zz"), "udbsnq111"),
    (("vector111", "AgentU"), "vkgghl111"),
    (("vector111", "keyboard"), "fiaucr111"),
    (("vector111", "AA"), "vector111"),
    (("processor111", "key"), "zvmmiqcsp111"),
    (("processor111", "lemon"), "avaqrdwaf111"),
    (("processor111", "a"), "processor111"),
    (("processor111", "zz"), "oqnbdrrnq111"),
    (("processor111", "AgentU"), "pxspxmsuv111"),
    (("processor111", "keyboard"), "zvmdssjrb111"),
    (("processor111", "AA"), "processor111"),
    (("reasoning111", "key"), "biycslsre111"),
    (("reasoning111", "lemon"), "cimgbymzu111"),
    (("reasoning111", "a"), "reasoning111"),
    (("reasoning111", "zz"), "qdzrnmhmf111"),
    (("reasoning111", "AgentU"), "rkefhhitk111"),
    (("reasoning111", "keyboard"), "biytcnzqq111"),
    (("reasoning111", "AA"), "reasoning111"),
    (("machine111", "key"), "wearmlo111"),
    (("machine111", "lemon"), "xeovvyi111"),
    (("machine111", "a"), "machine111"),
    (("machine111", "zz"), "lzbghmd111"),
    (("machine111", "AgentU"), "mggubhe111"),
    (("machine111", "keyboard"), "weaiwnv111"),
    (("machine111", "AA"), "machine111"),
    (("learning111", "key"), "viybrgxk111"),
    (("learning111", "lemon"), "wimfatrs111"),
    (("learning111", "a"), "learning111"),
    (("learning111", "zz"), "kdzqmhmf111"),
    (("learning111", "AgentU"), "lkeegcnm111"),
    (("learning111", "keyboard"), "viysbiej111"),
    (("learning111", "AA"), "learning111"),
    (("model111", "key"), "wsbop111"),
    (("model111", "lemon"), "xspsy111"),
    (("model111", "a"), "model111"),
    (("model111", "zz"), "lncdk111"),
    (("model111", "AgentU"), "muhre111"),
    (("model111", "keyboard"), "wsbfz111"),
    (("model111", "AA"), "model111"),
    (("token111", "key"), "dsior111"),
    (("token111", "lemon"), "eswsa111"),
    (("token111", "a"), "token111"),
    (("token111", "zz"), "snjdm111"),
    (("token111", "AgentU"), "tuorg111"),
    (("token111", "keyboard"), "dsifb111"),
    (("token111", "AA"), "token111"),
    (("prompt111", "key"), "zvmwtr111"),
    (("prompt111", "lemon"), "avaace111"),
    (("prompt111", "a"), "prompt111"),
    (("prompt111", "zz"), "oqnlos111"),
    (("prompt111", "AgentU"), "pxszin111"),
    (("prompt111", "keyboard"), "zvmndt111"),
    (("prompt111", "AA"), "prompt111"),
    (("session111", "key"), "ciqcmmx111"),
    (("session111", "lemon"), "diegvzr111"),
    (("session111", "a"), "session111"),
    (("session111", "zz"), "rdrrhnm111"),
    (("session111", "AgentU"), "skwfbin111"),
    (("session111", "keyboard"), "ciqtwoe111"),
    (("session111", "AA"), "session111"),
    (("library111", "key"), "vmzbepi111"),
    (("library111", "lemon"), "wmnfncc111"),
    (("library111", "a"), "library111"),
    (("library111", "zz"), "khaqzqx111"),
    (("library111", "AgentU"), "lofetly111"),
    (("library111", "keyboard"), "vmzsorp111"),
    (("library111", "AA"), "library111"),
    (("service111", "key"), "cipfmao111"),
    (("service111", "lemon"), "didjvni111"),
    (("service111", "a"), "service111"),
    (("service111", "zz"), "rdquhbd111"),
    (("service111", "AgentU"), "skvibwe111"),
    (("service111", "keyboard"), "cipwwcv111"),
    (("service111", "AA"), "service111"),
    (("gateway111", "key"), "qeroayi111"),
    (("gateway111", "lemon"), "refsjlc111"),
    (("gateway111", "a"), "gateway111"),
    (("gateway111", "zz"), "fzsdvzx111"),
    (("gateway111", "AgentU"), "ggxrpuy111"),
    (("gateway111", "keyboard"), "qerfkap111"),
    (("gateway111", "AA"), "gateway111"),
    (("storage111", "key"), "cxmbeeo111"),
    (("storage111", "lemon"), "dxafnri111"),
    (("storage111", "a"), "storage111"),
    (("storage111", "zz"), "rsnqzfd111"),
    (("storage111", "AgentU"), "szsetae111"),
    (("storage111", "keyboard"), "cxmsogv111"),
    (("storage111", "AA"), "storage111"),
    (("network111", "key"), "xirgspu111"),
    (("network111", "lemon"), "yifkbco111"),
    (("network111", "a"), "network111"),
    (("network111", "zz"), "mdsvnqj111"),
    (("network111", "AgentU"), "nkxjhlk111"),
    (("network111", "keyboard"), "xirxcrb111"),
    (("network111", "AA"), "network111"),
    (("latency111", "key"), "verorai111"),
    (("latency111", "lemon"), "wefsanc111"),
    (("latency111", "a"), "latency111"),
    (("latency111", "zz"), "kzsdmbx111"),
    (("latency111", "AgentU"), "lgxrgwy111"),
    (("latency111", "keyboard"), "verfbcp111"),
    (("latency111", "AA"), "latency111"),
    (("buffer111", "key"), "lydpip111"),
    (("buffer111", "lemon"), "myrtrc111"),
    (("buffer111", "a"), "buffer111"),
    (("buffer111", "zz"), "ateedq111"),
    (("buffer111", "AgentU"), "bajsxl111"),
    (("buffer111", "keyboard"), "lydgsr111"),
    (("buffer111", "AA"), "buffer111"),
    (("queue111", "key"), "aycei111"),
    (("queue111", "lemon"), "byqir111"),
    (("queue111", "a"), "queue111"),
    (("queue111", "zz"), "ptdtd111"),
    (("queue111", "AgentU"), "qaihx111"),
    (("queue111", "keyboard"), "aycvs111"),
    (("queue111", "AA"), "queue111"),
    (("worker111", "key"), "gspuip111"),
    (("worker111", "lemon"), "hsdyrc111"),
    (("worker111", "a"), "worker111"),
    (("worker111", "zz"), "vnqjdq111"),
    (("worker111", "AgentU"), "wuvxxl111"),
    (("worker111", "keyboard"), "gsplsr111"),
    (("worker111", "AA"), "worker111"),
    (("kernel111", "key"), "uipxij111"),
    (("kernel111", "lemon"), "vidbrw111"),
    (("kernel111", "a"), "kernel111"),
    (("kernel111", "zz"), "jdqmdk111"),
    (("kernel111", "AgentU"), "kkvaxf111"),
    (("kernel111", "keyboard"), "uiposl111"),
    (("kernel111", "AA"), "kernel111"),
    (("signal111", "key"), "cmexej111"),
    (("signal111", "lemon"), "dmsbnw111"),
    (("signal111", "a"), "signal111"),
    (("signal111", "zz"), "rhfmzk111"),
    (("signal111", "AgentU"), "sokatf111"),
    (("signal111", "keyboard"), "cmeool111"),
    (("signal111", "AA"), "signal111"),
    (("packet111", "key"), "zeauir111"),
    (("packet111", "lemon"), "aeoyre111"),
    (("packet111", "a"), "packet111"),
    (("packet111", "zz"), "ozbjds111"),
    (("packet111", "AgentU"), "pggxxn111"),
    (("packet111", "keyboard"), "zealst111"),
    (("packet111", "AA"), "packet111"),
    (("router111", "key"), "bssdip111"),
    (("router111", "lemon"), "csghrc111"),
    (("router111", "a"), "router111"),
    (("router111", "zz"), "qntsdq111"),
    (("router111", "AgentU"), "ruygxl111"),
    (("router111", "keyboard"), "bssusr111"),
    (("router111", "AA"), "router111"),
    (("cluster111", "key"), "mpscxcb111"),
    (("cluster111", "lemon"), "npgggpv111"),
    (("cluster111", "a"), "cluster111"),
    (("cluster111", "zz"), "bktrsdq111"),
    (("cluster111", "AgentU"), "cryfmyr111"),
    (("cluster111", "keyboard"), "mpsthei111"),
    (("cluster111", "AA"), "cluster111"),
    (("mirror111", "key"), "wmpbsp111"),
    (("mirror111", "lemon"), "xmdfbc111"),
    (("mirror111", "a"), "mirror111"),
    (("mirror111", "zz"), "lhqqnq111"),
    (("mirror111", "AgentU"), "movehl111"),
    (("mirror111", "keyboard"), "wmpscr111"),
    (("mirror111", "AA"), "mirror111"),
    (("filter111", "key"), "pmjdip111"),
    (("filter111", "lemon"), "qmxhrc111"),
    (("filter111", "a"), "filter111"),
    (("filter111", "zz"), "ehksdq111"),
    (("filter111", "AgentU"), "fopgxl111"),
    (("filter111", "keyboard"), "pmjusr111"),
    (("filter111", "AA"), "filter111"),
    (("ranking111", "key"), "belumlq111"),
    (("ranking111", "lemon"), "cezyvyk111"),
    (("ranking111", "a"), "ranking111"),
    (("ranking111", "zz"), "qzmjhmf111"),
    (("ranking111", "AgentU"), "rgrxbhg111"),
    (("ranking111", "keyboard"), "bellwnx111"),
    (("ranking111", "AA"), "ranking111"),
    (("encoding111", "key"), "orayhgxk111"),
    (("encoding111", "lemon"), "procqtrs111"),
    (("encoding111", "a"), "encoding111"),
    (("encoding111", "zz"), "dmbnchmf111"),
    (("encoding111", "AgentU"), "etgbwcnm111"),
    (("encoding111", "keyboard"), "orapriej111"),
    (("encoding111", "AA"), "encoding111"),
    (("mapping111", "key"), "wenzmlq111"),
    (("mapping111", "lemon"), "xebdvyk111"),
    (("mapping111", "a"), "mapping111"),
    (("mapping111", "zz"), "lzoohmf111"),
    (("mapping111", "AgentU"), "mgtcbhg111"),
    (("mapping111", "keyboard"), "wenqwnx111"),
    (("mapping111", "AA"), "mapping111"),
    (("record111", "key"), "biayvb111"),
    (("record111", "lemon"), "cioceo111"),
    (("record111", "a"), "record111"),
    (("record111", "zz"), "qdbnqc111"),
    (("record111", "AgentU"), "rkgbkx111"),
    (("record111", "keyboard"), "biapfd111"),
    (("record111", "AA"), "record111"),
    (("candle111", "key"), "melnpc111"),
    (("candle111", "lemon"), "nezryp111"),
    (("candle111", "a"), "candle111"),
    (("candle111", "zz"), "bzmckd111"),
    (("candle111", "AgentU"), "cgrqey111"),
    (("candle111", "keyboard"), "meleze111"),
    (("candle111", "AA"), "candle111"),
    (("thread111", "key"), "dlpoeb111"),
    (("thread111", "lemon"), "eldsno111"),
    (("thread111", "a"), "thread111"),
    (("thread111", "zz"), "sgqdzc111"),
    (("thread111", "AgentU"), "tnvrtx111"),
    (("thread111", "keyboard"), "dlpfod111"),
    (("thread111", "AA"), "thread111"),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 111: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 111: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "a"),
        "round 111: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 111: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 111: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 111: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", "AA"),
        "round 111: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "key"),
        "bssxh 111: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 111: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "a"),
        "round 111: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 111: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 111: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 111: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", "AA"),
        "round 111: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 111: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 111: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "a"),
        "round 111: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 111: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 111: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 111: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", "AA"),
        "round 111: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 111: the processor reads the record then stops", "key"),
        "bssxh 111: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 111: the processor reads the record then stops", "lemon"),
        "csgbq 111: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 111: the processor reads the record then stops", "a"),
        "round 111: the processor reads the record then stops",
    ),
    (
        ("round 111: the processor reads the record then stops", "zz"),
        "qntmc 111: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 111: the processor reads the record then stops", "AgentU"),
        "ruyaw 111: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 111: the processor reads the record then stops", "keyboard"),
        "bssor 111: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 111: the processor reads the record then stops", "AA"),
        "round 111: the processor reads the record then stops",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "key"),
        "bssxh 111: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "lemon"),
        "csgbq 111: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "a"),
        "round 111: a worker pulls the next task from the queue",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "zz"),
        "qntmc 111: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 111: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "keyboard"),
        "bssor 111: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 111: a worker pulls the next task from the queue", "AA"),
        "round 111: a worker pulls the next task from the queue",
    ),
    (
        ("round 111: signals travel through the network layer", "key"),
        "bssxh 111: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 111: signals travel through the network layer", "lemon"),
        "csgbq 111: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 111: signals travel through the network layer", "a"),
        "round 111: signals travel through the network layer",
    ),
    (
        ("round 111: signals travel through the network layer", "zz"),
        "qntmc 111: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 111: signals travel through the network layer", "AgentU"),
        "ruyaw 111: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 111: signals travel through the network layer", "keyboard"),
        "bssor 111: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 111: signals travel through the network layer", "AA"),
        "round 111: signals travel through the network layer",
    ),
    (
        ("round 111: the gateway routes each request by policy", "key"),
        "bssxh 111: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 111: the gateway routes each request by policy", "lemon"),
        "csgbq 111: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 111: the gateway routes each request by policy", "a"),
        "round 111: the gateway routes each request by policy",
    ),
    (
        ("round 111: the gateway routes each request by policy", "zz"),
        "qntmc 111: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 111: the gateway routes each request by policy", "AgentU"),
        "ruyaw 111: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 111: the gateway routes each request by policy", "keyboard"),
        "bssor 111: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 111: the gateway routes each request by policy", "AA"),
        "round 111: the gateway routes each request by policy",
    ),
    (("round 111: memory grows until the buffer is full", "key"), "bssxh 111: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 111: memory grows until the buffer is full", "lemon"), "csgbq 111: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 111: memory grows until the buffer is full", "a"), "round 111: memory grows until the buffer is full"),
    (("round 111: memory grows until the buffer is full", "zz"), "qntmc 111: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 111: memory grows until the buffer is full", "AgentU"),
        "ruyaw 111: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 111: memory grows until the buffer is full", "keyboard"),
        "bssor 111: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 111: memory grows until the buffer is full", "AA"), "round 111: memory grows until the buffer is full"),
    (("round 111: the cluster mirrors every packet twice", "key"), "bssxh 111: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 111: the cluster mirrors every packet twice", "lemon"),
        "csgbq 111: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 111: the cluster mirrors every packet twice", "a"), "round 111: the cluster mirrors every packet twice"),
    (("round 111: the cluster mirrors every packet twice", "zz"), "qntmc 111: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 111: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 111: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 111: the cluster mirrors every packet twice", "keyboard"),
        "bssor 111: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 111: the cluster mirrors every packet twice", "AA"), "round 111: the cluster mirrors every packet twice"),
    (
        ("round 111: ranking uses tokens learned from the corpus", "key"),
        "bssxh 111: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 111: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", "a"),
        "round 111: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 111: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 111: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 111: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", "AA"),
        "round 111: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 111: a long session ends when the candle dies", "key"),
        "bssxh 111: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 111: a long session ends when the candle dies", "lemon"),
        "csgbq 111: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 111: a long session ends when the candle dies", "a"),
        "round 111: a long session ends when the candle dies",
    ),
    (
        ("round 111: a long session ends when the candle dies", "zz"),
        "qntmc 111: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 111: a long session ends when the candle dies", "AgentU"),
        "ruyaw 111: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 111: a long session ends when the candle dies", "keyboard"),
        "bssor 111: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 111: a long session ends when the candle dies", "AA"),
        "round 111: a long session ends when the candle dies",
    ),
    (("round 111: encode the prompt then map the result", "key"), "bssxh 111: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 111: encode the prompt then map the result", "lemon"), "csgbq 111: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 111: encode the prompt then map the result", "a"), "round 111: encode the prompt then map the result"),
    (("round 111: encode the prompt then map the result", "zz"), "qntmc 111: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 111: encode the prompt then map the result", "AgentU"),
        "ruyaw 111: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 111: encode the prompt then map the result", "keyboard"),
        "bssor 111: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 111: encode the prompt then map the result", "AA"), "round 111: encode the prompt then map the result"),
    (("round 111: the kernel wakes the worker at dawn", "key"), "bssxh 111: rri iovlop ukocc xfo ambocb er neux"),
    (("round 111: the kernel wakes the worker at dawn", "lemon"), "csgbq 111: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 111: the kernel wakes the worker at dawn", "a"), "round 111: the kernel wakes the worker at dawn"),
    (("round 111: the kernel wakes the worker at dawn", "zz"), "qntmc 111: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 111: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 111: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 111: the kernel wakes the worker at dawn", "keyboard"), "bssor 111: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 111: the kernel wakes the worker at dawn", "AA"), "round 111: the kernel wakes the worker at dawn"),
    (("round 111: service latency drops after the patch", "key"), "bssxh 111: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 111: service latency drops after the patch", "lemon"), "csgbq 111: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 111: service latency drops after the patch", "a"), "round 111: service latency drops after the patch"),
    (("round 111: service latency drops after the patch", "zz"), "qntmc 111: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 111: service latency drops after the patch", "AgentU"),
        "ruyaw 111: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 111: service latency drops after the patch", "keyboard"),
        "bssor 111: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 111: service latency drops after the patch", "AA"), "round 111: service latency drops after the patch"),
    (
        ("round 111: the library caches every vector it sees", "key"),
        "bssxh 111: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 111: the library caches every vector it sees", "lemon"),
        "csgbq 111: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 111: the library caches every vector it sees", "a"), "round 111: the library caches every vector it sees"),
    (
        ("round 111: the library caches every vector it sees", "zz"),
        "qntmc 111: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 111: the library caches every vector it sees", "AgentU"),
        "ruyaw 111: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 111: the library caches every vector it sees", "keyboard"),
        "bssor 111: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 111: the library caches every vector it sees", "AA"),
        "round 111: the library caches every vector it sees",
    ),
    (("round 111: agents argue then the debate resolves", "key"), "bssxh 111: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 111: agents argue then the debate resolves", "lemon"), "csgbq 111: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 111: agents argue then the debate resolves", "a"), "round 111: agents argue then the debate resolves"),
    (("round 111: agents argue then the debate resolves", "zz"), "qntmc 111: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 111: agents argue then the debate resolves", "AgentU"),
        "ruyaw 111: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 111: agents argue then the debate resolves", "keyboard"),
        "bssor 111: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 111: agents argue then the debate resolves", "AA"), "round 111: agents argue then the debate resolves"),
    (("round 111: the filter keeps only strong matches", "key"), "bssxh 111: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 111: the filter keeps only strong matches", "lemon"), "csgbq 111: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 111: the filter keeps only strong matches", "a"), "round 111: the filter keeps only strong matches"),
    (("round 111: the filter keeps only strong matches", "zz"), "qntmc 111: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 111: the filter keeps only strong matches", "AgentU"), "ruyaw 111: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 111: the filter keeps only strong matches", "keyboard"),
        "bssor 111: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 111: the filter keeps only strong matches", "AA"), "round 111: the filter keeps only strong matches"),
    (("round 111: the model answers with a short reply", "key"), "bssxh 111: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 111: the model answers with a short reply", "lemon"), "csgbq 111: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 111: the model answers with a short reply", "a"), "round 111: the model answers with a short reply"),
    (("round 111: the model answers with a short reply", "zz"), "qntmc 111: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 111: the model answers with a short reply", "AgentU"), "ruyaw 111: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 111: the model answers with a short reply", "keyboard"),
        "bssor 111: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 111: the model answers with a short reply", "AA"), "round 111: the model answers with a short reply"),
    (
        ("round 111: the recorder stores the reasoning trace", "key"),
        "bssxh 111: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 111: the recorder stores the reasoning trace", "lemon"),
        "csgbq 111: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 111: the recorder stores the reasoning trace", "a"), "round 111: the recorder stores the reasoning trace"),
    (
        ("round 111: the recorder stores the reasoning trace", "zz"),
        "qntmc 111: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 111: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 111: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 111: the recorder stores the reasoning trace", "keyboard"),
        "bssor 111: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 111: the recorder stores the reasoning trace", "AA"),
        "round 111: the recorder stores the reasoning trace",
    ),
    (("round 111: the angel watches the processor run", "key"), "bssxh 111: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 111: the angel watches the processor run", "lemon"), "csgbq 111: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 111: the angel watches the processor run", "a"), "round 111: the angel watches the processor run"),
    (("round 111: the angel watches the processor run", "zz"), "qntmc 111: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 111: the angel watches the processor run", "AgentU"), "ruyaw 111: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 111: the angel watches the processor run", "keyboard"), "bssor 111: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 111: the angel watches the processor run", "AA"), "round 111: the angel watches the processor run"),
    (("round 111: angle of the vector decides the match", "key"), "bssxh 111: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 111: angle of the vector decides the match", "lemon"), "csgbq 111: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 111: angle of the vector decides the match", "a"), "round 111: angle of the vector decides the match"),
    (("round 111: angle of the vector decides the match", "zz"), "qntmc 111: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 111: angle of the vector decides the match", "AgentU"),
        "ruyaw 111: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 111: angle of the vector decides the match", "keyboard"),
        "bssor 111: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 111: angle of the vector decides the match", "AA"), "round 111: angle of the vector decides the match"),
    (
        ("round 111: the candle burns twice as long at night", "key"),
        "bssxh 111: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 111: the candle burns twice as long at night", "lemon"),
        "csgbq 111: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 111: the candle burns twice as long at night", "a"), "round 111: the candle burns twice as long at night"),
    (
        ("round 111: the candle burns twice as long at night", "zz"),
        "qntmc 111: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 111: the candle burns twice as long at night", "AgentU"),
        "ruyaw 111: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 111: the candle burns twice as long at night", "keyboard"),
        "bssor 111: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 111: the candle burns twice as long at night", "AA"),
        "round 111: the candle burns twice as long at night",
    ),
    (("round 111: a mirror of the universe in one line", "key"), "bssxh 111: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 111: a mirror of the universe in one line", "lemon"), "csgbq 111: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 111: a mirror of the universe in one line", "a"), "round 111: a mirror of the universe in one line"),
    (("round 111: a mirror of the universe in one line", "zz"), "qntmc 111: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 111: a mirror of the universe in one line", "AgentU"), "ruyaw 111: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 111: a mirror of the universe in one line", "keyboard"),
        "bssor 111: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 111: a mirror of the universe in one line", "AA"), "round 111: a mirror of the universe in one line"),
    (("round 111: the queue drains before the storm", "key"), "bssxh 111: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 111: the queue drains before the storm", "lemon"), "csgbq 111: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 111: the queue drains before the storm", "a"), "round 111: the queue drains before the storm"),
    (("round 111: the queue drains before the storm", "zz"), "qntmc 111: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 111: the queue drains before the storm", "AgentU"), "ruyaw 111: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 111: the queue drains before the storm", "keyboard"), "bssor 111: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 111: the queue drains before the storm", "AA"), "round 111: the queue drains before the storm"),
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
