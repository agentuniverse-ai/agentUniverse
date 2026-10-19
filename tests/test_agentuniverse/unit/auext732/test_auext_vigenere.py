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
    (("kitten732", "key"), "umrdil732"),
    (("kitten732", "lemon"), "vmfhry732"),
    (("kitten732", "a"), "kitten732"),
    (("kitten732", "zz"), "jhssdm732"),
    (("kitten732", "AgentU"), "koxgxh732"),
    (("kitten732", "keyboard"), "umrusn732"),
    (("kitten732", "AA"), "kitten732"),
    (("sitting732", "key"), "cmrdmlq732"),
    (("sitting732", "lemon"), "dmfhvyk732"),
    (("sitting732", "a"), "sitting732"),
    (("sitting732", "zz"), "rhsshmf732"),
    (("sitting732", "AgentU"), "soxgbhg732"),
    (("sitting732", "keyboard"), "cmruwnx732"),
    (("sitting732", "AA"), "sitting732"),
    (("agent732", "key"), "kkcxx732"),
    (("agent732", "lemon"), "lkqbg732"),
    (("agent732", "a"), "agent732"),
    (("agent732", "zz"), "zfdms732"),
    (("agent732", "AgentU"), "amiam732"),
    (("agent732", "keyboard"), "kkcoh732"),
    (("agent732", "AA"), "agent732"),
    (("angle732", "key"), "krevi732"),
    (("angle732", "lemon"), "lrszr732"),
    (("angle732", "a"), "angle732"),
    (("angle732", "zz"), "zmfkd732"),
    (("angle732", "AgentU"), "atkyx732"),
    (("angle732", "keyboard"), "krems732"),
    (("angle732", "AA"), "angle732"),
    (("universe732", "key"), "ergfipci732"),
    (("universe732", "lemon"), "frujrcwq732"),
    (("universe732", "a"), "universe732"),
    (("universe732", "zz"), "tmhudqrd732"),
    (("universe732", "AgentU"), "utmixlsk732"),
    (("universe732", "keyboard"), "ergwsrjh732"),
    (("universe732", "AA"), "universe732"),
    (("memory732", "key"), "wikyvw732"),
    (("memory732", "lemon"), "xiycej732"),
    (("memory732", "a"), "memory732"),
    (("memory732", "zz"), "ldlnqx732"),
    (("memory732", "AgentU"), "mkqbks732"),
    (("memory732", "keyboard"), "wikpfy732"),
    (("memory732", "AA"), "memory732"),
    (("stream732", "key"), "cxpoek732"),
    (("stream732", "lemon"), "dxdsnx732"),
    (("stream732", "a"), "stream732"),
    (("stream732", "zz"), "rsqdzl732"),
    (("stream732", "AgentU"), "szvrtg732"),
    (("stream732", "keyboard"), "cxpfom732"),
    (("stream732", "AA"), "stream732"),
    (("context732", "key"), "msldivd732"),
    (("context732", "lemon"), "nszhrix732"),
    (("context732", "a"), "context732"),
    (("context732", "zz"), "bnmsdws732"),
    (("context732", "AgentU"), "curgxrt732"),
    (("context732", "keyboard"), "mslusxk732"),
    (("context732", "AA"), "context732"),
    (("knowledge732", "key"), "urmgpcnkc732"),
    (("knowledge732", "lemon"), "vrakyphss732"),
    (("knowledge732", "a"), "knowledge732"),
    (("knowledge732", "zz"), "jmnvkdcfd732"),
    (("knowledge732", "AgentU"), "ktsjeydmi732"),
    (("knowledge732", "keyboard"), "urmxzeujo732"),
    (("knowledge732", "AA"), "knowledge732"),
    (("vector732", "key"), "fiadsp732"),
    (("vector732", "lemon"), "giohbc732"),
    (("vector732", "a"), "vector732"),
    (("vector732", "zz"), "udbsnq732"),
    (("vector732", "AgentU"), "vkgghl732"),
    (("vector732", "keyboard"), "fiaucr732"),
    (("vector732", "AA"), "vector732"),
    (("processor732", "key"), "zvmmiqcsp732"),
    (("processor732", "lemon"), "avaqrdwaf732"),
    (("processor732", "a"), "processor732"),
    (("processor732", "zz"), "oqnbdrrnq732"),
    (("processor732", "AgentU"), "pxspxmsuv732"),
    (("processor732", "keyboard"), "zvmdssjrb732"),
    (("processor732", "AA"), "processor732"),
    (("reasoning732", "key"), "biycslsre732"),
    (("reasoning732", "lemon"), "cimgbymzu732"),
    (("reasoning732", "a"), "reasoning732"),
    (("reasoning732", "zz"), "qdzrnmhmf732"),
    (("reasoning732", "AgentU"), "rkefhhitk732"),
    (("reasoning732", "keyboard"), "biytcnzqq732"),
    (("reasoning732", "AA"), "reasoning732"),
    (("machine732", "key"), "wearmlo732"),
    (("machine732", "lemon"), "xeovvyi732"),
    (("machine732", "a"), "machine732"),
    (("machine732", "zz"), "lzbghmd732"),
    (("machine732", "AgentU"), "mggubhe732"),
    (("machine732", "keyboard"), "weaiwnv732"),
    (("machine732", "AA"), "machine732"),
    (("learning732", "key"), "viybrgxk732"),
    (("learning732", "lemon"), "wimfatrs732"),
    (("learning732", "a"), "learning732"),
    (("learning732", "zz"), "kdzqmhmf732"),
    (("learning732", "AgentU"), "lkeegcnm732"),
    (("learning732", "keyboard"), "viysbiej732"),
    (("learning732", "AA"), "learning732"),
    (("model732", "key"), "wsbop732"),
    (("model732", "lemon"), "xspsy732"),
    (("model732", "a"), "model732"),
    (("model732", "zz"), "lncdk732"),
    (("model732", "AgentU"), "muhre732"),
    (("model732", "keyboard"), "wsbfz732"),
    (("model732", "AA"), "model732"),
    (("token732", "key"), "dsior732"),
    (("token732", "lemon"), "eswsa732"),
    (("token732", "a"), "token732"),
    (("token732", "zz"), "snjdm732"),
    (("token732", "AgentU"), "tuorg732"),
    (("token732", "keyboard"), "dsifb732"),
    (("token732", "AA"), "token732"),
    (("prompt732", "key"), "zvmwtr732"),
    (("prompt732", "lemon"), "avaace732"),
    (("prompt732", "a"), "prompt732"),
    (("prompt732", "zz"), "oqnlos732"),
    (("prompt732", "AgentU"), "pxszin732"),
    (("prompt732", "keyboard"), "zvmndt732"),
    (("prompt732", "AA"), "prompt732"),
    (("session732", "key"), "ciqcmmx732"),
    (("session732", "lemon"), "diegvzr732"),
    (("session732", "a"), "session732"),
    (("session732", "zz"), "rdrrhnm732"),
    (("session732", "AgentU"), "skwfbin732"),
    (("session732", "keyboard"), "ciqtwoe732"),
    (("session732", "AA"), "session732"),
    (("library732", "key"), "vmzbepi732"),
    (("library732", "lemon"), "wmnfncc732"),
    (("library732", "a"), "library732"),
    (("library732", "zz"), "khaqzqx732"),
    (("library732", "AgentU"), "lofetly732"),
    (("library732", "keyboard"), "vmzsorp732"),
    (("library732", "AA"), "library732"),
    (("service732", "key"), "cipfmao732"),
    (("service732", "lemon"), "didjvni732"),
    (("service732", "a"), "service732"),
    (("service732", "zz"), "rdquhbd732"),
    (("service732", "AgentU"), "skvibwe732"),
    (("service732", "keyboard"), "cipwwcv732"),
    (("service732", "AA"), "service732"),
    (("gateway732", "key"), "qeroayi732"),
    (("gateway732", "lemon"), "refsjlc732"),
    (("gateway732", "a"), "gateway732"),
    (("gateway732", "zz"), "fzsdvzx732"),
    (("gateway732", "AgentU"), "ggxrpuy732"),
    (("gateway732", "keyboard"), "qerfkap732"),
    (("gateway732", "AA"), "gateway732"),
    (("storage732", "key"), "cxmbeeo732"),
    (("storage732", "lemon"), "dxafnri732"),
    (("storage732", "a"), "storage732"),
    (("storage732", "zz"), "rsnqzfd732"),
    (("storage732", "AgentU"), "szsetae732"),
    (("storage732", "keyboard"), "cxmsogv732"),
    (("storage732", "AA"), "storage732"),
    (("network732", "key"), "xirgspu732"),
    (("network732", "lemon"), "yifkbco732"),
    (("network732", "a"), "network732"),
    (("network732", "zz"), "mdsvnqj732"),
    (("network732", "AgentU"), "nkxjhlk732"),
    (("network732", "keyboard"), "xirxcrb732"),
    (("network732", "AA"), "network732"),
    (("latency732", "key"), "verorai732"),
    (("latency732", "lemon"), "wefsanc732"),
    (("latency732", "a"), "latency732"),
    (("latency732", "zz"), "kzsdmbx732"),
    (("latency732", "AgentU"), "lgxrgwy732"),
    (("latency732", "keyboard"), "verfbcp732"),
    (("latency732", "AA"), "latency732"),
    (("buffer732", "key"), "lydpip732"),
    (("buffer732", "lemon"), "myrtrc732"),
    (("buffer732", "a"), "buffer732"),
    (("buffer732", "zz"), "ateedq732"),
    (("buffer732", "AgentU"), "bajsxl732"),
    (("buffer732", "keyboard"), "lydgsr732"),
    (("buffer732", "AA"), "buffer732"),
    (("queue732", "key"), "aycei732"),
    (("queue732", "lemon"), "byqir732"),
    (("queue732", "a"), "queue732"),
    (("queue732", "zz"), "ptdtd732"),
    (("queue732", "AgentU"), "qaihx732"),
    (("queue732", "keyboard"), "aycvs732"),
    (("queue732", "AA"), "queue732"),
    (("worker732", "key"), "gspuip732"),
    (("worker732", "lemon"), "hsdyrc732"),
    (("worker732", "a"), "worker732"),
    (("worker732", "zz"), "vnqjdq732"),
    (("worker732", "AgentU"), "wuvxxl732"),
    (("worker732", "keyboard"), "gsplsr732"),
    (("worker732", "AA"), "worker732"),
    (("kernel732", "key"), "uipxij732"),
    (("kernel732", "lemon"), "vidbrw732"),
    (("kernel732", "a"), "kernel732"),
    (("kernel732", "zz"), "jdqmdk732"),
    (("kernel732", "AgentU"), "kkvaxf732"),
    (("kernel732", "keyboard"), "uiposl732"),
    (("kernel732", "AA"), "kernel732"),
    (("signal732", "key"), "cmexej732"),
    (("signal732", "lemon"), "dmsbnw732"),
    (("signal732", "a"), "signal732"),
    (("signal732", "zz"), "rhfmzk732"),
    (("signal732", "AgentU"), "sokatf732"),
    (("signal732", "keyboard"), "cmeool732"),
    (("signal732", "AA"), "signal732"),
    (("packet732", "key"), "zeauir732"),
    (("packet732", "lemon"), "aeoyre732"),
    (("packet732", "a"), "packet732"),
    (("packet732", "zz"), "ozbjds732"),
    (("packet732", "AgentU"), "pggxxn732"),
    (("packet732", "keyboard"), "zealst732"),
    (("packet732", "AA"), "packet732"),
    (("router732", "key"), "bssdip732"),
    (("router732", "lemon"), "csghrc732"),
    (("router732", "a"), "router732"),
    (("router732", "zz"), "qntsdq732"),
    (("router732", "AgentU"), "ruygxl732"),
    (("router732", "keyboard"), "bssusr732"),
    (("router732", "AA"), "router732"),
    (("cluster732", "key"), "mpscxcb732"),
    (("cluster732", "lemon"), "npgggpv732"),
    (("cluster732", "a"), "cluster732"),
    (("cluster732", "zz"), "bktrsdq732"),
    (("cluster732", "AgentU"), "cryfmyr732"),
    (("cluster732", "keyboard"), "mpsthei732"),
    (("cluster732", "AA"), "cluster732"),
    (("mirror732", "key"), "wmpbsp732"),
    (("mirror732", "lemon"), "xmdfbc732"),
    (("mirror732", "a"), "mirror732"),
    (("mirror732", "zz"), "lhqqnq732"),
    (("mirror732", "AgentU"), "movehl732"),
    (("mirror732", "keyboard"), "wmpscr732"),
    (("mirror732", "AA"), "mirror732"),
    (("filter732", "key"), "pmjdip732"),
    (("filter732", "lemon"), "qmxhrc732"),
    (("filter732", "a"), "filter732"),
    (("filter732", "zz"), "ehksdq732"),
    (("filter732", "AgentU"), "fopgxl732"),
    (("filter732", "keyboard"), "pmjusr732"),
    (("filter732", "AA"), "filter732"),
    (("ranking732", "key"), "belumlq732"),
    (("ranking732", "lemon"), "cezyvyk732"),
    (("ranking732", "a"), "ranking732"),
    (("ranking732", "zz"), "qzmjhmf732"),
    (("ranking732", "AgentU"), "rgrxbhg732"),
    (("ranking732", "keyboard"), "bellwnx732"),
    (("ranking732", "AA"), "ranking732"),
    (("encoding732", "key"), "orayhgxk732"),
    (("encoding732", "lemon"), "procqtrs732"),
    (("encoding732", "a"), "encoding732"),
    (("encoding732", "zz"), "dmbnchmf732"),
    (("encoding732", "AgentU"), "etgbwcnm732"),
    (("encoding732", "keyboard"), "orapriej732"),
    (("encoding732", "AA"), "encoding732"),
    (("mapping732", "key"), "wenzmlq732"),
    (("mapping732", "lemon"), "xebdvyk732"),
    (("mapping732", "a"), "mapping732"),
    (("mapping732", "zz"), "lzoohmf732"),
    (("mapping732", "AgentU"), "mgtcbhg732"),
    (("mapping732", "keyboard"), "wenqwnx732"),
    (("mapping732", "AA"), "mapping732"),
    (("record732", "key"), "biayvb732"),
    (("record732", "lemon"), "cioceo732"),
    (("record732", "a"), "record732"),
    (("record732", "zz"), "qdbnqc732"),
    (("record732", "AgentU"), "rkgbkx732"),
    (("record732", "keyboard"), "biapfd732"),
    (("record732", "AA"), "record732"),
    (("candle732", "key"), "melnpc732"),
    (("candle732", "lemon"), "nezryp732"),
    (("candle732", "a"), "candle732"),
    (("candle732", "zz"), "bzmckd732"),
    (("candle732", "AgentU"), "cgrqey732"),
    (("candle732", "keyboard"), "meleze732"),
    (("candle732", "AA"), "candle732"),
    (("thread732", "key"), "dlpoeb732"),
    (("thread732", "lemon"), "eldsno732"),
    (("thread732", "a"), "thread732"),
    (("thread732", "zz"), "sgqdzc732"),
    (("thread732", "AgentU"), "tnvrtx732"),
    (("thread732", "keyboard"), "dlpfod732"),
    (("thread732", "AA"), "thread732"),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 732: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 732: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "a"),
        "round 732: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 732: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 732: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 732: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", "AA"),
        "round 732: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "key"),
        "bssxh 732: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 732: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "a"),
        "round 732: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 732: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 732: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 732: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", "AA"),
        "round 732: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 732: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 732: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "a"),
        "round 732: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 732: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 732: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 732: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", "AA"),
        "round 732: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 732: the processor reads the record then stops", "key"),
        "bssxh 732: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 732: the processor reads the record then stops", "lemon"),
        "csgbq 732: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 732: the processor reads the record then stops", "a"),
        "round 732: the processor reads the record then stops",
    ),
    (
        ("round 732: the processor reads the record then stops", "zz"),
        "qntmc 732: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 732: the processor reads the record then stops", "AgentU"),
        "ruyaw 732: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 732: the processor reads the record then stops", "keyboard"),
        "bssor 732: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 732: the processor reads the record then stops", "AA"),
        "round 732: the processor reads the record then stops",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "key"),
        "bssxh 732: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "lemon"),
        "csgbq 732: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "a"),
        "round 732: a worker pulls the next task from the queue",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "zz"),
        "qntmc 732: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 732: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "keyboard"),
        "bssor 732: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 732: a worker pulls the next task from the queue", "AA"),
        "round 732: a worker pulls the next task from the queue",
    ),
    (
        ("round 732: signals travel through the network layer", "key"),
        "bssxh 732: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 732: signals travel through the network layer", "lemon"),
        "csgbq 732: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 732: signals travel through the network layer", "a"),
        "round 732: signals travel through the network layer",
    ),
    (
        ("round 732: signals travel through the network layer", "zz"),
        "qntmc 732: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 732: signals travel through the network layer", "AgentU"),
        "ruyaw 732: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 732: signals travel through the network layer", "keyboard"),
        "bssor 732: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 732: signals travel through the network layer", "AA"),
        "round 732: signals travel through the network layer",
    ),
    (
        ("round 732: the gateway routes each request by policy", "key"),
        "bssxh 732: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 732: the gateway routes each request by policy", "lemon"),
        "csgbq 732: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 732: the gateway routes each request by policy", "a"),
        "round 732: the gateway routes each request by policy",
    ),
    (
        ("round 732: the gateway routes each request by policy", "zz"),
        "qntmc 732: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 732: the gateway routes each request by policy", "AgentU"),
        "ruyaw 732: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 732: the gateway routes each request by policy", "keyboard"),
        "bssor 732: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 732: the gateway routes each request by policy", "AA"),
        "round 732: the gateway routes each request by policy",
    ),
    (("round 732: memory grows until the buffer is full", "key"), "bssxh 732: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 732: memory grows until the buffer is full", "lemon"), "csgbq 732: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 732: memory grows until the buffer is full", "a"), "round 732: memory grows until the buffer is full"),
    (("round 732: memory grows until the buffer is full", "zz"), "qntmc 732: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 732: memory grows until the buffer is full", "AgentU"),
        "ruyaw 732: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 732: memory grows until the buffer is full", "keyboard"),
        "bssor 732: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 732: memory grows until the buffer is full", "AA"), "round 732: memory grows until the buffer is full"),
    (("round 732: the cluster mirrors every packet twice", "key"), "bssxh 732: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 732: the cluster mirrors every packet twice", "lemon"),
        "csgbq 732: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 732: the cluster mirrors every packet twice", "a"), "round 732: the cluster mirrors every packet twice"),
    (("round 732: the cluster mirrors every packet twice", "zz"), "qntmc 732: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 732: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 732: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 732: the cluster mirrors every packet twice", "keyboard"),
        "bssor 732: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 732: the cluster mirrors every packet twice", "AA"), "round 732: the cluster mirrors every packet twice"),
    (
        ("round 732: ranking uses tokens learned from the corpus", "key"),
        "bssxh 732: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 732: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", "a"),
        "round 732: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 732: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 732: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 732: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", "AA"),
        "round 732: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 732: a long session ends when the candle dies", "key"),
        "bssxh 732: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 732: a long session ends when the candle dies", "lemon"),
        "csgbq 732: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 732: a long session ends when the candle dies", "a"),
        "round 732: a long session ends when the candle dies",
    ),
    (
        ("round 732: a long session ends when the candle dies", "zz"),
        "qntmc 732: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 732: a long session ends when the candle dies", "AgentU"),
        "ruyaw 732: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 732: a long session ends when the candle dies", "keyboard"),
        "bssor 732: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 732: a long session ends when the candle dies", "AA"),
        "round 732: a long session ends when the candle dies",
    ),
    (("round 732: encode the prompt then map the result", "key"), "bssxh 732: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 732: encode the prompt then map the result", "lemon"), "csgbq 732: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 732: encode the prompt then map the result", "a"), "round 732: encode the prompt then map the result"),
    (("round 732: encode the prompt then map the result", "zz"), "qntmc 732: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 732: encode the prompt then map the result", "AgentU"),
        "ruyaw 732: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 732: encode the prompt then map the result", "keyboard"),
        "bssor 732: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 732: encode the prompt then map the result", "AA"), "round 732: encode the prompt then map the result"),
    (("round 732: the kernel wakes the worker at dawn", "key"), "bssxh 732: rri iovlop ukocc xfo ambocb er neux"),
    (("round 732: the kernel wakes the worker at dawn", "lemon"), "csgbq 732: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 732: the kernel wakes the worker at dawn", "a"), "round 732: the kernel wakes the worker at dawn"),
    (("round 732: the kernel wakes the worker at dawn", "zz"), "qntmc 732: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 732: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 732: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 732: the kernel wakes the worker at dawn", "keyboard"), "bssor 732: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 732: the kernel wakes the worker at dawn", "AA"), "round 732: the kernel wakes the worker at dawn"),
    (("round 732: service latency drops after the patch", "key"), "bssxh 732: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 732: service latency drops after the patch", "lemon"), "csgbq 732: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 732: service latency drops after the patch", "a"), "round 732: service latency drops after the patch"),
    (("round 732: service latency drops after the patch", "zz"), "qntmc 732: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 732: service latency drops after the patch", "AgentU"),
        "ruyaw 732: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 732: service latency drops after the patch", "keyboard"),
        "bssor 732: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 732: service latency drops after the patch", "AA"), "round 732: service latency drops after the patch"),
    (
        ("round 732: the library caches every vector it sees", "key"),
        "bssxh 732: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 732: the library caches every vector it sees", "lemon"),
        "csgbq 732: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 732: the library caches every vector it sees", "a"), "round 732: the library caches every vector it sees"),
    (
        ("round 732: the library caches every vector it sees", "zz"),
        "qntmc 732: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 732: the library caches every vector it sees", "AgentU"),
        "ruyaw 732: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 732: the library caches every vector it sees", "keyboard"),
        "bssor 732: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 732: the library caches every vector it sees", "AA"),
        "round 732: the library caches every vector it sees",
    ),
    (("round 732: agents argue then the debate resolves", "key"), "bssxh 732: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 732: agents argue then the debate resolves", "lemon"), "csgbq 732: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 732: agents argue then the debate resolves", "a"), "round 732: agents argue then the debate resolves"),
    (("round 732: agents argue then the debate resolves", "zz"), "qntmc 732: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 732: agents argue then the debate resolves", "AgentU"),
        "ruyaw 732: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 732: agents argue then the debate resolves", "keyboard"),
        "bssor 732: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 732: agents argue then the debate resolves", "AA"), "round 732: agents argue then the debate resolves"),
    (("round 732: the filter keeps only strong matches", "key"), "bssxh 732: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 732: the filter keeps only strong matches", "lemon"), "csgbq 732: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 732: the filter keeps only strong matches", "a"), "round 732: the filter keeps only strong matches"),
    (("round 732: the filter keeps only strong matches", "zz"), "qntmc 732: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 732: the filter keeps only strong matches", "AgentU"), "ruyaw 732: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 732: the filter keeps only strong matches", "keyboard"),
        "bssor 732: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 732: the filter keeps only strong matches", "AA"), "round 732: the filter keeps only strong matches"),
    (("round 732: the model answers with a short reply", "key"), "bssxh 732: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 732: the model answers with a short reply", "lemon"), "csgbq 732: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 732: the model answers with a short reply", "a"), "round 732: the model answers with a short reply"),
    (("round 732: the model answers with a short reply", "zz"), "qntmc 732: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 732: the model answers with a short reply", "AgentU"), "ruyaw 732: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 732: the model answers with a short reply", "keyboard"),
        "bssor 732: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 732: the model answers with a short reply", "AA"), "round 732: the model answers with a short reply"),
    (
        ("round 732: the recorder stores the reasoning trace", "key"),
        "bssxh 732: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 732: the recorder stores the reasoning trace", "lemon"),
        "csgbq 732: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 732: the recorder stores the reasoning trace", "a"), "round 732: the recorder stores the reasoning trace"),
    (
        ("round 732: the recorder stores the reasoning trace", "zz"),
        "qntmc 732: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 732: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 732: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 732: the recorder stores the reasoning trace", "keyboard"),
        "bssor 732: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 732: the recorder stores the reasoning trace", "AA"),
        "round 732: the recorder stores the reasoning trace",
    ),
    (("round 732: the angel watches the processor run", "key"), "bssxh 732: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 732: the angel watches the processor run", "lemon"), "csgbq 732: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 732: the angel watches the processor run", "a"), "round 732: the angel watches the processor run"),
    (("round 732: the angel watches the processor run", "zz"), "qntmc 732: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 732: the angel watches the processor run", "AgentU"), "ruyaw 732: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 732: the angel watches the processor run", "keyboard"), "bssor 732: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 732: the angel watches the processor run", "AA"), "round 732: the angel watches the processor run"),
    (("round 732: angle of the vector decides the match", "key"), "bssxh 732: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 732: angle of the vector decides the match", "lemon"), "csgbq 732: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 732: angle of the vector decides the match", "a"), "round 732: angle of the vector decides the match"),
    (("round 732: angle of the vector decides the match", "zz"), "qntmc 732: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 732: angle of the vector decides the match", "AgentU"),
        "ruyaw 732: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 732: angle of the vector decides the match", "keyboard"),
        "bssor 732: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 732: angle of the vector decides the match", "AA"), "round 732: angle of the vector decides the match"),
    (
        ("round 732: the candle burns twice as long at night", "key"),
        "bssxh 732: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 732: the candle burns twice as long at night", "lemon"),
        "csgbq 732: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 732: the candle burns twice as long at night", "a"), "round 732: the candle burns twice as long at night"),
    (
        ("round 732: the candle burns twice as long at night", "zz"),
        "qntmc 732: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 732: the candle burns twice as long at night", "AgentU"),
        "ruyaw 732: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 732: the candle burns twice as long at night", "keyboard"),
        "bssor 732: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 732: the candle burns twice as long at night", "AA"),
        "round 732: the candle burns twice as long at night",
    ),
    (("round 732: a mirror of the universe in one line", "key"), "bssxh 732: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 732: a mirror of the universe in one line", "lemon"), "csgbq 732: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 732: a mirror of the universe in one line", "a"), "round 732: a mirror of the universe in one line"),
    (("round 732: a mirror of the universe in one line", "zz"), "qntmc 732: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 732: a mirror of the universe in one line", "AgentU"), "ruyaw 732: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 732: a mirror of the universe in one line", "keyboard"),
        "bssor 732: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 732: a mirror of the universe in one line", "AA"), "round 732: a mirror of the universe in one line"),
    (("round 732: the queue drains before the storm", "key"), "bssxh 732: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 732: the queue drains before the storm", "lemon"), "csgbq 732: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 732: the queue drains before the storm", "a"), "round 732: the queue drains before the storm"),
    (("round 732: the queue drains before the storm", "zz"), "qntmc 732: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 732: the queue drains before the storm", "AgentU"), "ruyaw 732: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 732: the queue drains before the storm", "keyboard"), "bssor 732: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 732: the queue drains before the storm", "AA"), "round 732: the queue drains before the storm"),
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
