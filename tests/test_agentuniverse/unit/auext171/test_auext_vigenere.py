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
    (("kitten171", "key"), "umrdil171"),
    (("kitten171", "lemon"), "vmfhry171"),
    (("kitten171", "a"), "kitten171"),
    (("kitten171", "zz"), "jhssdm171"),
    (("kitten171", "AgentU"), "koxgxh171"),
    (("kitten171", "keyboard"), "umrusn171"),
    (("kitten171", "AA"), "kitten171"),
    (("sitting171", "key"), "cmrdmlq171"),
    (("sitting171", "lemon"), "dmfhvyk171"),
    (("sitting171", "a"), "sitting171"),
    (("sitting171", "zz"), "rhsshmf171"),
    (("sitting171", "AgentU"), "soxgbhg171"),
    (("sitting171", "keyboard"), "cmruwnx171"),
    (("sitting171", "AA"), "sitting171"),
    (("agent171", "key"), "kkcxx171"),
    (("agent171", "lemon"), "lkqbg171"),
    (("agent171", "a"), "agent171"),
    (("agent171", "zz"), "zfdms171"),
    (("agent171", "AgentU"), "amiam171"),
    (("agent171", "keyboard"), "kkcoh171"),
    (("agent171", "AA"), "agent171"),
    (("angle171", "key"), "krevi171"),
    (("angle171", "lemon"), "lrszr171"),
    (("angle171", "a"), "angle171"),
    (("angle171", "zz"), "zmfkd171"),
    (("angle171", "AgentU"), "atkyx171"),
    (("angle171", "keyboard"), "krems171"),
    (("angle171", "AA"), "angle171"),
    (("universe171", "key"), "ergfipci171"),
    (("universe171", "lemon"), "frujrcwq171"),
    (("universe171", "a"), "universe171"),
    (("universe171", "zz"), "tmhudqrd171"),
    (("universe171", "AgentU"), "utmixlsk171"),
    (("universe171", "keyboard"), "ergwsrjh171"),
    (("universe171", "AA"), "universe171"),
    (("memory171", "key"), "wikyvw171"),
    (("memory171", "lemon"), "xiycej171"),
    (("memory171", "a"), "memory171"),
    (("memory171", "zz"), "ldlnqx171"),
    (("memory171", "AgentU"), "mkqbks171"),
    (("memory171", "keyboard"), "wikpfy171"),
    (("memory171", "AA"), "memory171"),
    (("stream171", "key"), "cxpoek171"),
    (("stream171", "lemon"), "dxdsnx171"),
    (("stream171", "a"), "stream171"),
    (("stream171", "zz"), "rsqdzl171"),
    (("stream171", "AgentU"), "szvrtg171"),
    (("stream171", "keyboard"), "cxpfom171"),
    (("stream171", "AA"), "stream171"),
    (("context171", "key"), "msldivd171"),
    (("context171", "lemon"), "nszhrix171"),
    (("context171", "a"), "context171"),
    (("context171", "zz"), "bnmsdws171"),
    (("context171", "AgentU"), "curgxrt171"),
    (("context171", "keyboard"), "mslusxk171"),
    (("context171", "AA"), "context171"),
    (("knowledge171", "key"), "urmgpcnkc171"),
    (("knowledge171", "lemon"), "vrakyphss171"),
    (("knowledge171", "a"), "knowledge171"),
    (("knowledge171", "zz"), "jmnvkdcfd171"),
    (("knowledge171", "AgentU"), "ktsjeydmi171"),
    (("knowledge171", "keyboard"), "urmxzeujo171"),
    (("knowledge171", "AA"), "knowledge171"),
    (("vector171", "key"), "fiadsp171"),
    (("vector171", "lemon"), "giohbc171"),
    (("vector171", "a"), "vector171"),
    (("vector171", "zz"), "udbsnq171"),
    (("vector171", "AgentU"), "vkgghl171"),
    (("vector171", "keyboard"), "fiaucr171"),
    (("vector171", "AA"), "vector171"),
    (("processor171", "key"), "zvmmiqcsp171"),
    (("processor171", "lemon"), "avaqrdwaf171"),
    (("processor171", "a"), "processor171"),
    (("processor171", "zz"), "oqnbdrrnq171"),
    (("processor171", "AgentU"), "pxspxmsuv171"),
    (("processor171", "keyboard"), "zvmdssjrb171"),
    (("processor171", "AA"), "processor171"),
    (("reasoning171", "key"), "biycslsre171"),
    (("reasoning171", "lemon"), "cimgbymzu171"),
    (("reasoning171", "a"), "reasoning171"),
    (("reasoning171", "zz"), "qdzrnmhmf171"),
    (("reasoning171", "AgentU"), "rkefhhitk171"),
    (("reasoning171", "keyboard"), "biytcnzqq171"),
    (("reasoning171", "AA"), "reasoning171"),
    (("machine171", "key"), "wearmlo171"),
    (("machine171", "lemon"), "xeovvyi171"),
    (("machine171", "a"), "machine171"),
    (("machine171", "zz"), "lzbghmd171"),
    (("machine171", "AgentU"), "mggubhe171"),
    (("machine171", "keyboard"), "weaiwnv171"),
    (("machine171", "AA"), "machine171"),
    (("learning171", "key"), "viybrgxk171"),
    (("learning171", "lemon"), "wimfatrs171"),
    (("learning171", "a"), "learning171"),
    (("learning171", "zz"), "kdzqmhmf171"),
    (("learning171", "AgentU"), "lkeegcnm171"),
    (("learning171", "keyboard"), "viysbiej171"),
    (("learning171", "AA"), "learning171"),
    (("model171", "key"), "wsbop171"),
    (("model171", "lemon"), "xspsy171"),
    (("model171", "a"), "model171"),
    (("model171", "zz"), "lncdk171"),
    (("model171", "AgentU"), "muhre171"),
    (("model171", "keyboard"), "wsbfz171"),
    (("model171", "AA"), "model171"),
    (("token171", "key"), "dsior171"),
    (("token171", "lemon"), "eswsa171"),
    (("token171", "a"), "token171"),
    (("token171", "zz"), "snjdm171"),
    (("token171", "AgentU"), "tuorg171"),
    (("token171", "keyboard"), "dsifb171"),
    (("token171", "AA"), "token171"),
    (("prompt171", "key"), "zvmwtr171"),
    (("prompt171", "lemon"), "avaace171"),
    (("prompt171", "a"), "prompt171"),
    (("prompt171", "zz"), "oqnlos171"),
    (("prompt171", "AgentU"), "pxszin171"),
    (("prompt171", "keyboard"), "zvmndt171"),
    (("prompt171", "AA"), "prompt171"),
    (("session171", "key"), "ciqcmmx171"),
    (("session171", "lemon"), "diegvzr171"),
    (("session171", "a"), "session171"),
    (("session171", "zz"), "rdrrhnm171"),
    (("session171", "AgentU"), "skwfbin171"),
    (("session171", "keyboard"), "ciqtwoe171"),
    (("session171", "AA"), "session171"),
    (("library171", "key"), "vmzbepi171"),
    (("library171", "lemon"), "wmnfncc171"),
    (("library171", "a"), "library171"),
    (("library171", "zz"), "khaqzqx171"),
    (("library171", "AgentU"), "lofetly171"),
    (("library171", "keyboard"), "vmzsorp171"),
    (("library171", "AA"), "library171"),
    (("service171", "key"), "cipfmao171"),
    (("service171", "lemon"), "didjvni171"),
    (("service171", "a"), "service171"),
    (("service171", "zz"), "rdquhbd171"),
    (("service171", "AgentU"), "skvibwe171"),
    (("service171", "keyboard"), "cipwwcv171"),
    (("service171", "AA"), "service171"),
    (("gateway171", "key"), "qeroayi171"),
    (("gateway171", "lemon"), "refsjlc171"),
    (("gateway171", "a"), "gateway171"),
    (("gateway171", "zz"), "fzsdvzx171"),
    (("gateway171", "AgentU"), "ggxrpuy171"),
    (("gateway171", "keyboard"), "qerfkap171"),
    (("gateway171", "AA"), "gateway171"),
    (("storage171", "key"), "cxmbeeo171"),
    (("storage171", "lemon"), "dxafnri171"),
    (("storage171", "a"), "storage171"),
    (("storage171", "zz"), "rsnqzfd171"),
    (("storage171", "AgentU"), "szsetae171"),
    (("storage171", "keyboard"), "cxmsogv171"),
    (("storage171", "AA"), "storage171"),
    (("network171", "key"), "xirgspu171"),
    (("network171", "lemon"), "yifkbco171"),
    (("network171", "a"), "network171"),
    (("network171", "zz"), "mdsvnqj171"),
    (("network171", "AgentU"), "nkxjhlk171"),
    (("network171", "keyboard"), "xirxcrb171"),
    (("network171", "AA"), "network171"),
    (("latency171", "key"), "verorai171"),
    (("latency171", "lemon"), "wefsanc171"),
    (("latency171", "a"), "latency171"),
    (("latency171", "zz"), "kzsdmbx171"),
    (("latency171", "AgentU"), "lgxrgwy171"),
    (("latency171", "keyboard"), "verfbcp171"),
    (("latency171", "AA"), "latency171"),
    (("buffer171", "key"), "lydpip171"),
    (("buffer171", "lemon"), "myrtrc171"),
    (("buffer171", "a"), "buffer171"),
    (("buffer171", "zz"), "ateedq171"),
    (("buffer171", "AgentU"), "bajsxl171"),
    (("buffer171", "keyboard"), "lydgsr171"),
    (("buffer171", "AA"), "buffer171"),
    (("queue171", "key"), "aycei171"),
    (("queue171", "lemon"), "byqir171"),
    (("queue171", "a"), "queue171"),
    (("queue171", "zz"), "ptdtd171"),
    (("queue171", "AgentU"), "qaihx171"),
    (("queue171", "keyboard"), "aycvs171"),
    (("queue171", "AA"), "queue171"),
    (("worker171", "key"), "gspuip171"),
    (("worker171", "lemon"), "hsdyrc171"),
    (("worker171", "a"), "worker171"),
    (("worker171", "zz"), "vnqjdq171"),
    (("worker171", "AgentU"), "wuvxxl171"),
    (("worker171", "keyboard"), "gsplsr171"),
    (("worker171", "AA"), "worker171"),
    (("kernel171", "key"), "uipxij171"),
    (("kernel171", "lemon"), "vidbrw171"),
    (("kernel171", "a"), "kernel171"),
    (("kernel171", "zz"), "jdqmdk171"),
    (("kernel171", "AgentU"), "kkvaxf171"),
    (("kernel171", "keyboard"), "uiposl171"),
    (("kernel171", "AA"), "kernel171"),
    (("signal171", "key"), "cmexej171"),
    (("signal171", "lemon"), "dmsbnw171"),
    (("signal171", "a"), "signal171"),
    (("signal171", "zz"), "rhfmzk171"),
    (("signal171", "AgentU"), "sokatf171"),
    (("signal171", "keyboard"), "cmeool171"),
    (("signal171", "AA"), "signal171"),
    (("packet171", "key"), "zeauir171"),
    (("packet171", "lemon"), "aeoyre171"),
    (("packet171", "a"), "packet171"),
    (("packet171", "zz"), "ozbjds171"),
    (("packet171", "AgentU"), "pggxxn171"),
    (("packet171", "keyboard"), "zealst171"),
    (("packet171", "AA"), "packet171"),
    (("router171", "key"), "bssdip171"),
    (("router171", "lemon"), "csghrc171"),
    (("router171", "a"), "router171"),
    (("router171", "zz"), "qntsdq171"),
    (("router171", "AgentU"), "ruygxl171"),
    (("router171", "keyboard"), "bssusr171"),
    (("router171", "AA"), "router171"),
    (("cluster171", "key"), "mpscxcb171"),
    (("cluster171", "lemon"), "npgggpv171"),
    (("cluster171", "a"), "cluster171"),
    (("cluster171", "zz"), "bktrsdq171"),
    (("cluster171", "AgentU"), "cryfmyr171"),
    (("cluster171", "keyboard"), "mpsthei171"),
    (("cluster171", "AA"), "cluster171"),
    (("mirror171", "key"), "wmpbsp171"),
    (("mirror171", "lemon"), "xmdfbc171"),
    (("mirror171", "a"), "mirror171"),
    (("mirror171", "zz"), "lhqqnq171"),
    (("mirror171", "AgentU"), "movehl171"),
    (("mirror171", "keyboard"), "wmpscr171"),
    (("mirror171", "AA"), "mirror171"),
    (("filter171", "key"), "pmjdip171"),
    (("filter171", "lemon"), "qmxhrc171"),
    (("filter171", "a"), "filter171"),
    (("filter171", "zz"), "ehksdq171"),
    (("filter171", "AgentU"), "fopgxl171"),
    (("filter171", "keyboard"), "pmjusr171"),
    (("filter171", "AA"), "filter171"),
    (("ranking171", "key"), "belumlq171"),
    (("ranking171", "lemon"), "cezyvyk171"),
    (("ranking171", "a"), "ranking171"),
    (("ranking171", "zz"), "qzmjhmf171"),
    (("ranking171", "AgentU"), "rgrxbhg171"),
    (("ranking171", "keyboard"), "bellwnx171"),
    (("ranking171", "AA"), "ranking171"),
    (("encoding171", "key"), "orayhgxk171"),
    (("encoding171", "lemon"), "procqtrs171"),
    (("encoding171", "a"), "encoding171"),
    (("encoding171", "zz"), "dmbnchmf171"),
    (("encoding171", "AgentU"), "etgbwcnm171"),
    (("encoding171", "keyboard"), "orapriej171"),
    (("encoding171", "AA"), "encoding171"),
    (("mapping171", "key"), "wenzmlq171"),
    (("mapping171", "lemon"), "xebdvyk171"),
    (("mapping171", "a"), "mapping171"),
    (("mapping171", "zz"), "lzoohmf171"),
    (("mapping171", "AgentU"), "mgtcbhg171"),
    (("mapping171", "keyboard"), "wenqwnx171"),
    (("mapping171", "AA"), "mapping171"),
    (("record171", "key"), "biayvb171"),
    (("record171", "lemon"), "cioceo171"),
    (("record171", "a"), "record171"),
    (("record171", "zz"), "qdbnqc171"),
    (("record171", "AgentU"), "rkgbkx171"),
    (("record171", "keyboard"), "biapfd171"),
    (("record171", "AA"), "record171"),
    (("candle171", "key"), "melnpc171"),
    (("candle171", "lemon"), "nezryp171"),
    (("candle171", "a"), "candle171"),
    (("candle171", "zz"), "bzmckd171"),
    (("candle171", "AgentU"), "cgrqey171"),
    (("candle171", "keyboard"), "meleze171"),
    (("candle171", "AA"), "candle171"),
    (("thread171", "key"), "dlpoeb171"),
    (("thread171", "lemon"), "eldsno171"),
    (("thread171", "a"), "thread171"),
    (("thread171", "zz"), "sgqdzc171"),
    (("thread171", "AgentU"), "tnvrtx171"),
    (("thread171", "keyboard"), "dlpfod171"),
    (("thread171", "AA"), "thread171"),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 171: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 171: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "a"),
        "round 171: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 171: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 171: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 171: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", "AA"),
        "round 171: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "key"),
        "bssxh 171: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 171: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "a"),
        "round 171: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 171: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 171: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 171: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", "AA"),
        "round 171: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 171: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 171: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "a"),
        "round 171: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 171: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 171: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 171: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", "AA"),
        "round 171: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 171: the processor reads the record then stops", "key"),
        "bssxh 171: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 171: the processor reads the record then stops", "lemon"),
        "csgbq 171: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 171: the processor reads the record then stops", "a"),
        "round 171: the processor reads the record then stops",
    ),
    (
        ("round 171: the processor reads the record then stops", "zz"),
        "qntmc 171: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 171: the processor reads the record then stops", "AgentU"),
        "ruyaw 171: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 171: the processor reads the record then stops", "keyboard"),
        "bssor 171: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 171: the processor reads the record then stops", "AA"),
        "round 171: the processor reads the record then stops",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "key"),
        "bssxh 171: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "lemon"),
        "csgbq 171: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "a"),
        "round 171: a worker pulls the next task from the queue",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "zz"),
        "qntmc 171: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 171: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "keyboard"),
        "bssor 171: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 171: a worker pulls the next task from the queue", "AA"),
        "round 171: a worker pulls the next task from the queue",
    ),
    (
        ("round 171: signals travel through the network layer", "key"),
        "bssxh 171: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 171: signals travel through the network layer", "lemon"),
        "csgbq 171: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 171: signals travel through the network layer", "a"),
        "round 171: signals travel through the network layer",
    ),
    (
        ("round 171: signals travel through the network layer", "zz"),
        "qntmc 171: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 171: signals travel through the network layer", "AgentU"),
        "ruyaw 171: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 171: signals travel through the network layer", "keyboard"),
        "bssor 171: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 171: signals travel through the network layer", "AA"),
        "round 171: signals travel through the network layer",
    ),
    (
        ("round 171: the gateway routes each request by policy", "key"),
        "bssxh 171: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 171: the gateway routes each request by policy", "lemon"),
        "csgbq 171: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 171: the gateway routes each request by policy", "a"),
        "round 171: the gateway routes each request by policy",
    ),
    (
        ("round 171: the gateway routes each request by policy", "zz"),
        "qntmc 171: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 171: the gateway routes each request by policy", "AgentU"),
        "ruyaw 171: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 171: the gateway routes each request by policy", "keyboard"),
        "bssor 171: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 171: the gateway routes each request by policy", "AA"),
        "round 171: the gateway routes each request by policy",
    ),
    (("round 171: memory grows until the buffer is full", "key"), "bssxh 171: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 171: memory grows until the buffer is full", "lemon"), "csgbq 171: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 171: memory grows until the buffer is full", "a"), "round 171: memory grows until the buffer is full"),
    (("round 171: memory grows until the buffer is full", "zz"), "qntmc 171: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 171: memory grows until the buffer is full", "AgentU"),
        "ruyaw 171: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 171: memory grows until the buffer is full", "keyboard"),
        "bssor 171: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 171: memory grows until the buffer is full", "AA"), "round 171: memory grows until the buffer is full"),
    (("round 171: the cluster mirrors every packet twice", "key"), "bssxh 171: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 171: the cluster mirrors every packet twice", "lemon"),
        "csgbq 171: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 171: the cluster mirrors every packet twice", "a"), "round 171: the cluster mirrors every packet twice"),
    (("round 171: the cluster mirrors every packet twice", "zz"), "qntmc 171: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 171: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 171: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 171: the cluster mirrors every packet twice", "keyboard"),
        "bssor 171: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 171: the cluster mirrors every packet twice", "AA"), "round 171: the cluster mirrors every packet twice"),
    (
        ("round 171: ranking uses tokens learned from the corpus", "key"),
        "bssxh 171: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 171: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", "a"),
        "round 171: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 171: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 171: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 171: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", "AA"),
        "round 171: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 171: a long session ends when the candle dies", "key"),
        "bssxh 171: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 171: a long session ends when the candle dies", "lemon"),
        "csgbq 171: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 171: a long session ends when the candle dies", "a"),
        "round 171: a long session ends when the candle dies",
    ),
    (
        ("round 171: a long session ends when the candle dies", "zz"),
        "qntmc 171: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 171: a long session ends when the candle dies", "AgentU"),
        "ruyaw 171: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 171: a long session ends when the candle dies", "keyboard"),
        "bssor 171: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 171: a long session ends when the candle dies", "AA"),
        "round 171: a long session ends when the candle dies",
    ),
    (("round 171: encode the prompt then map the result", "key"), "bssxh 171: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 171: encode the prompt then map the result", "lemon"), "csgbq 171: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 171: encode the prompt then map the result", "a"), "round 171: encode the prompt then map the result"),
    (("round 171: encode the prompt then map the result", "zz"), "qntmc 171: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 171: encode the prompt then map the result", "AgentU"),
        "ruyaw 171: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 171: encode the prompt then map the result", "keyboard"),
        "bssor 171: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 171: encode the prompt then map the result", "AA"), "round 171: encode the prompt then map the result"),
    (("round 171: the kernel wakes the worker at dawn", "key"), "bssxh 171: rri iovlop ukocc xfo ambocb er neux"),
    (("round 171: the kernel wakes the worker at dawn", "lemon"), "csgbq 171: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 171: the kernel wakes the worker at dawn", "a"), "round 171: the kernel wakes the worker at dawn"),
    (("round 171: the kernel wakes the worker at dawn", "zz"), "qntmc 171: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 171: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 171: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 171: the kernel wakes the worker at dawn", "keyboard"), "bssor 171: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 171: the kernel wakes the worker at dawn", "AA"), "round 171: the kernel wakes the worker at dawn"),
    (("round 171: service latency drops after the patch", "key"), "bssxh 171: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 171: service latency drops after the patch", "lemon"), "csgbq 171: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 171: service latency drops after the patch", "a"), "round 171: service latency drops after the patch"),
    (("round 171: service latency drops after the patch", "zz"), "qntmc 171: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 171: service latency drops after the patch", "AgentU"),
        "ruyaw 171: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 171: service latency drops after the patch", "keyboard"),
        "bssor 171: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 171: service latency drops after the patch", "AA"), "round 171: service latency drops after the patch"),
    (
        ("round 171: the library caches every vector it sees", "key"),
        "bssxh 171: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 171: the library caches every vector it sees", "lemon"),
        "csgbq 171: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 171: the library caches every vector it sees", "a"), "round 171: the library caches every vector it sees"),
    (
        ("round 171: the library caches every vector it sees", "zz"),
        "qntmc 171: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 171: the library caches every vector it sees", "AgentU"),
        "ruyaw 171: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 171: the library caches every vector it sees", "keyboard"),
        "bssor 171: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 171: the library caches every vector it sees", "AA"),
        "round 171: the library caches every vector it sees",
    ),
    (("round 171: agents argue then the debate resolves", "key"), "bssxh 171: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 171: agents argue then the debate resolves", "lemon"), "csgbq 171: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 171: agents argue then the debate resolves", "a"), "round 171: agents argue then the debate resolves"),
    (("round 171: agents argue then the debate resolves", "zz"), "qntmc 171: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 171: agents argue then the debate resolves", "AgentU"),
        "ruyaw 171: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 171: agents argue then the debate resolves", "keyboard"),
        "bssor 171: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 171: agents argue then the debate resolves", "AA"), "round 171: agents argue then the debate resolves"),
    (("round 171: the filter keeps only strong matches", "key"), "bssxh 171: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 171: the filter keeps only strong matches", "lemon"), "csgbq 171: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 171: the filter keeps only strong matches", "a"), "round 171: the filter keeps only strong matches"),
    (("round 171: the filter keeps only strong matches", "zz"), "qntmc 171: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 171: the filter keeps only strong matches", "AgentU"), "ruyaw 171: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 171: the filter keeps only strong matches", "keyboard"),
        "bssor 171: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 171: the filter keeps only strong matches", "AA"), "round 171: the filter keeps only strong matches"),
    (("round 171: the model answers with a short reply", "key"), "bssxh 171: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 171: the model answers with a short reply", "lemon"), "csgbq 171: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 171: the model answers with a short reply", "a"), "round 171: the model answers with a short reply"),
    (("round 171: the model answers with a short reply", "zz"), "qntmc 171: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 171: the model answers with a short reply", "AgentU"), "ruyaw 171: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 171: the model answers with a short reply", "keyboard"),
        "bssor 171: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 171: the model answers with a short reply", "AA"), "round 171: the model answers with a short reply"),
    (
        ("round 171: the recorder stores the reasoning trace", "key"),
        "bssxh 171: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 171: the recorder stores the reasoning trace", "lemon"),
        "csgbq 171: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 171: the recorder stores the reasoning trace", "a"), "round 171: the recorder stores the reasoning trace"),
    (
        ("round 171: the recorder stores the reasoning trace", "zz"),
        "qntmc 171: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 171: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 171: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 171: the recorder stores the reasoning trace", "keyboard"),
        "bssor 171: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 171: the recorder stores the reasoning trace", "AA"),
        "round 171: the recorder stores the reasoning trace",
    ),
    (("round 171: the angel watches the processor run", "key"), "bssxh 171: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 171: the angel watches the processor run", "lemon"), "csgbq 171: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 171: the angel watches the processor run", "a"), "round 171: the angel watches the processor run"),
    (("round 171: the angel watches the processor run", "zz"), "qntmc 171: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 171: the angel watches the processor run", "AgentU"), "ruyaw 171: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 171: the angel watches the processor run", "keyboard"), "bssor 171: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 171: the angel watches the processor run", "AA"), "round 171: the angel watches the processor run"),
    (("round 171: angle of the vector decides the match", "key"), "bssxh 171: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 171: angle of the vector decides the match", "lemon"), "csgbq 171: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 171: angle of the vector decides the match", "a"), "round 171: angle of the vector decides the match"),
    (("round 171: angle of the vector decides the match", "zz"), "qntmc 171: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 171: angle of the vector decides the match", "AgentU"),
        "ruyaw 171: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 171: angle of the vector decides the match", "keyboard"),
        "bssor 171: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 171: angle of the vector decides the match", "AA"), "round 171: angle of the vector decides the match"),
    (
        ("round 171: the candle burns twice as long at night", "key"),
        "bssxh 171: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 171: the candle burns twice as long at night", "lemon"),
        "csgbq 171: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 171: the candle burns twice as long at night", "a"), "round 171: the candle burns twice as long at night"),
    (
        ("round 171: the candle burns twice as long at night", "zz"),
        "qntmc 171: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 171: the candle burns twice as long at night", "AgentU"),
        "ruyaw 171: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 171: the candle burns twice as long at night", "keyboard"),
        "bssor 171: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 171: the candle burns twice as long at night", "AA"),
        "round 171: the candle burns twice as long at night",
    ),
    (("round 171: a mirror of the universe in one line", "key"), "bssxh 171: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 171: a mirror of the universe in one line", "lemon"), "csgbq 171: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 171: a mirror of the universe in one line", "a"), "round 171: a mirror of the universe in one line"),
    (("round 171: a mirror of the universe in one line", "zz"), "qntmc 171: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 171: a mirror of the universe in one line", "AgentU"), "ruyaw 171: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 171: a mirror of the universe in one line", "keyboard"),
        "bssor 171: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 171: a mirror of the universe in one line", "AA"), "round 171: a mirror of the universe in one line"),
    (("round 171: the queue drains before the storm", "key"), "bssxh 171: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 171: the queue drains before the storm", "lemon"), "csgbq 171: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 171: the queue drains before the storm", "a"), "round 171: the queue drains before the storm"),
    (("round 171: the queue drains before the storm", "zz"), "qntmc 171: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 171: the queue drains before the storm", "AgentU"), "ruyaw 171: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 171: the queue drains before the storm", "keyboard"), "bssor 171: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 171: the queue drains before the storm", "AA"), "round 171: the queue drains before the storm"),
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
