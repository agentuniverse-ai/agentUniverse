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
    (("kitten166", "key"), "umrdil166"),
    (("kitten166", "lemon"), "vmfhry166"),
    (("kitten166", "a"), "kitten166"),
    (("kitten166", "zz"), "jhssdm166"),
    (("kitten166", "AgentU"), "koxgxh166"),
    (("kitten166", "keyboard"), "umrusn166"),
    (("kitten166", "AA"), "kitten166"),
    (("sitting166", "key"), "cmrdmlq166"),
    (("sitting166", "lemon"), "dmfhvyk166"),
    (("sitting166", "a"), "sitting166"),
    (("sitting166", "zz"), "rhsshmf166"),
    (("sitting166", "AgentU"), "soxgbhg166"),
    (("sitting166", "keyboard"), "cmruwnx166"),
    (("sitting166", "AA"), "sitting166"),
    (("agent166", "key"), "kkcxx166"),
    (("agent166", "lemon"), "lkqbg166"),
    (("agent166", "a"), "agent166"),
    (("agent166", "zz"), "zfdms166"),
    (("agent166", "AgentU"), "amiam166"),
    (("agent166", "keyboard"), "kkcoh166"),
    (("agent166", "AA"), "agent166"),
    (("angle166", "key"), "krevi166"),
    (("angle166", "lemon"), "lrszr166"),
    (("angle166", "a"), "angle166"),
    (("angle166", "zz"), "zmfkd166"),
    (("angle166", "AgentU"), "atkyx166"),
    (("angle166", "keyboard"), "krems166"),
    (("angle166", "AA"), "angle166"),
    (("universe166", "key"), "ergfipci166"),
    (("universe166", "lemon"), "frujrcwq166"),
    (("universe166", "a"), "universe166"),
    (("universe166", "zz"), "tmhudqrd166"),
    (("universe166", "AgentU"), "utmixlsk166"),
    (("universe166", "keyboard"), "ergwsrjh166"),
    (("universe166", "AA"), "universe166"),
    (("memory166", "key"), "wikyvw166"),
    (("memory166", "lemon"), "xiycej166"),
    (("memory166", "a"), "memory166"),
    (("memory166", "zz"), "ldlnqx166"),
    (("memory166", "AgentU"), "mkqbks166"),
    (("memory166", "keyboard"), "wikpfy166"),
    (("memory166", "AA"), "memory166"),
    (("stream166", "key"), "cxpoek166"),
    (("stream166", "lemon"), "dxdsnx166"),
    (("stream166", "a"), "stream166"),
    (("stream166", "zz"), "rsqdzl166"),
    (("stream166", "AgentU"), "szvrtg166"),
    (("stream166", "keyboard"), "cxpfom166"),
    (("stream166", "AA"), "stream166"),
    (("context166", "key"), "msldivd166"),
    (("context166", "lemon"), "nszhrix166"),
    (("context166", "a"), "context166"),
    (("context166", "zz"), "bnmsdws166"),
    (("context166", "AgentU"), "curgxrt166"),
    (("context166", "keyboard"), "mslusxk166"),
    (("context166", "AA"), "context166"),
    (("knowledge166", "key"), "urmgpcnkc166"),
    (("knowledge166", "lemon"), "vrakyphss166"),
    (("knowledge166", "a"), "knowledge166"),
    (("knowledge166", "zz"), "jmnvkdcfd166"),
    (("knowledge166", "AgentU"), "ktsjeydmi166"),
    (("knowledge166", "keyboard"), "urmxzeujo166"),
    (("knowledge166", "AA"), "knowledge166"),
    (("vector166", "key"), "fiadsp166"),
    (("vector166", "lemon"), "giohbc166"),
    (("vector166", "a"), "vector166"),
    (("vector166", "zz"), "udbsnq166"),
    (("vector166", "AgentU"), "vkgghl166"),
    (("vector166", "keyboard"), "fiaucr166"),
    (("vector166", "AA"), "vector166"),
    (("processor166", "key"), "zvmmiqcsp166"),
    (("processor166", "lemon"), "avaqrdwaf166"),
    (("processor166", "a"), "processor166"),
    (("processor166", "zz"), "oqnbdrrnq166"),
    (("processor166", "AgentU"), "pxspxmsuv166"),
    (("processor166", "keyboard"), "zvmdssjrb166"),
    (("processor166", "AA"), "processor166"),
    (("reasoning166", "key"), "biycslsre166"),
    (("reasoning166", "lemon"), "cimgbymzu166"),
    (("reasoning166", "a"), "reasoning166"),
    (("reasoning166", "zz"), "qdzrnmhmf166"),
    (("reasoning166", "AgentU"), "rkefhhitk166"),
    (("reasoning166", "keyboard"), "biytcnzqq166"),
    (("reasoning166", "AA"), "reasoning166"),
    (("machine166", "key"), "wearmlo166"),
    (("machine166", "lemon"), "xeovvyi166"),
    (("machine166", "a"), "machine166"),
    (("machine166", "zz"), "lzbghmd166"),
    (("machine166", "AgentU"), "mggubhe166"),
    (("machine166", "keyboard"), "weaiwnv166"),
    (("machine166", "AA"), "machine166"),
    (("learning166", "key"), "viybrgxk166"),
    (("learning166", "lemon"), "wimfatrs166"),
    (("learning166", "a"), "learning166"),
    (("learning166", "zz"), "kdzqmhmf166"),
    (("learning166", "AgentU"), "lkeegcnm166"),
    (("learning166", "keyboard"), "viysbiej166"),
    (("learning166", "AA"), "learning166"),
    (("model166", "key"), "wsbop166"),
    (("model166", "lemon"), "xspsy166"),
    (("model166", "a"), "model166"),
    (("model166", "zz"), "lncdk166"),
    (("model166", "AgentU"), "muhre166"),
    (("model166", "keyboard"), "wsbfz166"),
    (("model166", "AA"), "model166"),
    (("token166", "key"), "dsior166"),
    (("token166", "lemon"), "eswsa166"),
    (("token166", "a"), "token166"),
    (("token166", "zz"), "snjdm166"),
    (("token166", "AgentU"), "tuorg166"),
    (("token166", "keyboard"), "dsifb166"),
    (("token166", "AA"), "token166"),
    (("prompt166", "key"), "zvmwtr166"),
    (("prompt166", "lemon"), "avaace166"),
    (("prompt166", "a"), "prompt166"),
    (("prompt166", "zz"), "oqnlos166"),
    (("prompt166", "AgentU"), "pxszin166"),
    (("prompt166", "keyboard"), "zvmndt166"),
    (("prompt166", "AA"), "prompt166"),
    (("session166", "key"), "ciqcmmx166"),
    (("session166", "lemon"), "diegvzr166"),
    (("session166", "a"), "session166"),
    (("session166", "zz"), "rdrrhnm166"),
    (("session166", "AgentU"), "skwfbin166"),
    (("session166", "keyboard"), "ciqtwoe166"),
    (("session166", "AA"), "session166"),
    (("library166", "key"), "vmzbepi166"),
    (("library166", "lemon"), "wmnfncc166"),
    (("library166", "a"), "library166"),
    (("library166", "zz"), "khaqzqx166"),
    (("library166", "AgentU"), "lofetly166"),
    (("library166", "keyboard"), "vmzsorp166"),
    (("library166", "AA"), "library166"),
    (("service166", "key"), "cipfmao166"),
    (("service166", "lemon"), "didjvni166"),
    (("service166", "a"), "service166"),
    (("service166", "zz"), "rdquhbd166"),
    (("service166", "AgentU"), "skvibwe166"),
    (("service166", "keyboard"), "cipwwcv166"),
    (("service166", "AA"), "service166"),
    (("gateway166", "key"), "qeroayi166"),
    (("gateway166", "lemon"), "refsjlc166"),
    (("gateway166", "a"), "gateway166"),
    (("gateway166", "zz"), "fzsdvzx166"),
    (("gateway166", "AgentU"), "ggxrpuy166"),
    (("gateway166", "keyboard"), "qerfkap166"),
    (("gateway166", "AA"), "gateway166"),
    (("storage166", "key"), "cxmbeeo166"),
    (("storage166", "lemon"), "dxafnri166"),
    (("storage166", "a"), "storage166"),
    (("storage166", "zz"), "rsnqzfd166"),
    (("storage166", "AgentU"), "szsetae166"),
    (("storage166", "keyboard"), "cxmsogv166"),
    (("storage166", "AA"), "storage166"),
    (("network166", "key"), "xirgspu166"),
    (("network166", "lemon"), "yifkbco166"),
    (("network166", "a"), "network166"),
    (("network166", "zz"), "mdsvnqj166"),
    (("network166", "AgentU"), "nkxjhlk166"),
    (("network166", "keyboard"), "xirxcrb166"),
    (("network166", "AA"), "network166"),
    (("latency166", "key"), "verorai166"),
    (("latency166", "lemon"), "wefsanc166"),
    (("latency166", "a"), "latency166"),
    (("latency166", "zz"), "kzsdmbx166"),
    (("latency166", "AgentU"), "lgxrgwy166"),
    (("latency166", "keyboard"), "verfbcp166"),
    (("latency166", "AA"), "latency166"),
    (("buffer166", "key"), "lydpip166"),
    (("buffer166", "lemon"), "myrtrc166"),
    (("buffer166", "a"), "buffer166"),
    (("buffer166", "zz"), "ateedq166"),
    (("buffer166", "AgentU"), "bajsxl166"),
    (("buffer166", "keyboard"), "lydgsr166"),
    (("buffer166", "AA"), "buffer166"),
    (("queue166", "key"), "aycei166"),
    (("queue166", "lemon"), "byqir166"),
    (("queue166", "a"), "queue166"),
    (("queue166", "zz"), "ptdtd166"),
    (("queue166", "AgentU"), "qaihx166"),
    (("queue166", "keyboard"), "aycvs166"),
    (("queue166", "AA"), "queue166"),
    (("worker166", "key"), "gspuip166"),
    (("worker166", "lemon"), "hsdyrc166"),
    (("worker166", "a"), "worker166"),
    (("worker166", "zz"), "vnqjdq166"),
    (("worker166", "AgentU"), "wuvxxl166"),
    (("worker166", "keyboard"), "gsplsr166"),
    (("worker166", "AA"), "worker166"),
    (("kernel166", "key"), "uipxij166"),
    (("kernel166", "lemon"), "vidbrw166"),
    (("kernel166", "a"), "kernel166"),
    (("kernel166", "zz"), "jdqmdk166"),
    (("kernel166", "AgentU"), "kkvaxf166"),
    (("kernel166", "keyboard"), "uiposl166"),
    (("kernel166", "AA"), "kernel166"),
    (("signal166", "key"), "cmexej166"),
    (("signal166", "lemon"), "dmsbnw166"),
    (("signal166", "a"), "signal166"),
    (("signal166", "zz"), "rhfmzk166"),
    (("signal166", "AgentU"), "sokatf166"),
    (("signal166", "keyboard"), "cmeool166"),
    (("signal166", "AA"), "signal166"),
    (("packet166", "key"), "zeauir166"),
    (("packet166", "lemon"), "aeoyre166"),
    (("packet166", "a"), "packet166"),
    (("packet166", "zz"), "ozbjds166"),
    (("packet166", "AgentU"), "pggxxn166"),
    (("packet166", "keyboard"), "zealst166"),
    (("packet166", "AA"), "packet166"),
    (("router166", "key"), "bssdip166"),
    (("router166", "lemon"), "csghrc166"),
    (("router166", "a"), "router166"),
    (("router166", "zz"), "qntsdq166"),
    (("router166", "AgentU"), "ruygxl166"),
    (("router166", "keyboard"), "bssusr166"),
    (("router166", "AA"), "router166"),
    (("cluster166", "key"), "mpscxcb166"),
    (("cluster166", "lemon"), "npgggpv166"),
    (("cluster166", "a"), "cluster166"),
    (("cluster166", "zz"), "bktrsdq166"),
    (("cluster166", "AgentU"), "cryfmyr166"),
    (("cluster166", "keyboard"), "mpsthei166"),
    (("cluster166", "AA"), "cluster166"),
    (("mirror166", "key"), "wmpbsp166"),
    (("mirror166", "lemon"), "xmdfbc166"),
    (("mirror166", "a"), "mirror166"),
    (("mirror166", "zz"), "lhqqnq166"),
    (("mirror166", "AgentU"), "movehl166"),
    (("mirror166", "keyboard"), "wmpscr166"),
    (("mirror166", "AA"), "mirror166"),
    (("filter166", "key"), "pmjdip166"),
    (("filter166", "lemon"), "qmxhrc166"),
    (("filter166", "a"), "filter166"),
    (("filter166", "zz"), "ehksdq166"),
    (("filter166", "AgentU"), "fopgxl166"),
    (("filter166", "keyboard"), "pmjusr166"),
    (("filter166", "AA"), "filter166"),
    (("ranking166", "key"), "belumlq166"),
    (("ranking166", "lemon"), "cezyvyk166"),
    (("ranking166", "a"), "ranking166"),
    (("ranking166", "zz"), "qzmjhmf166"),
    (("ranking166", "AgentU"), "rgrxbhg166"),
    (("ranking166", "keyboard"), "bellwnx166"),
    (("ranking166", "AA"), "ranking166"),
    (("encoding166", "key"), "orayhgxk166"),
    (("encoding166", "lemon"), "procqtrs166"),
    (("encoding166", "a"), "encoding166"),
    (("encoding166", "zz"), "dmbnchmf166"),
    (("encoding166", "AgentU"), "etgbwcnm166"),
    (("encoding166", "keyboard"), "orapriej166"),
    (("encoding166", "AA"), "encoding166"),
    (("mapping166", "key"), "wenzmlq166"),
    (("mapping166", "lemon"), "xebdvyk166"),
    (("mapping166", "a"), "mapping166"),
    (("mapping166", "zz"), "lzoohmf166"),
    (("mapping166", "AgentU"), "mgtcbhg166"),
    (("mapping166", "keyboard"), "wenqwnx166"),
    (("mapping166", "AA"), "mapping166"),
    (("record166", "key"), "biayvb166"),
    (("record166", "lemon"), "cioceo166"),
    (("record166", "a"), "record166"),
    (("record166", "zz"), "qdbnqc166"),
    (("record166", "AgentU"), "rkgbkx166"),
    (("record166", "keyboard"), "biapfd166"),
    (("record166", "AA"), "record166"),
    (("candle166", "key"), "melnpc166"),
    (("candle166", "lemon"), "nezryp166"),
    (("candle166", "a"), "candle166"),
    (("candle166", "zz"), "bzmckd166"),
    (("candle166", "AgentU"), "cgrqey166"),
    (("candle166", "keyboard"), "meleze166"),
    (("candle166", "AA"), "candle166"),
    (("thread166", "key"), "dlpoeb166"),
    (("thread166", "lemon"), "eldsno166"),
    (("thread166", "a"), "thread166"),
    (("thread166", "zz"), "sgqdzc166"),
    (("thread166", "AgentU"), "tnvrtx166"),
    (("thread166", "keyboard"), "dlpfod166"),
    (("thread166", "AA"), "thread166"),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 166: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 166: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "a"),
        "round 166: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 166: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 166: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 166: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", "AA"),
        "round 166: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "key"),
        "bssxh 166: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 166: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "a"),
        "round 166: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 166: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 166: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 166: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", "AA"),
        "round 166: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 166: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 166: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "a"),
        "round 166: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 166: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 166: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 166: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", "AA"),
        "round 166: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 166: the processor reads the record then stops", "key"),
        "bssxh 166: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 166: the processor reads the record then stops", "lemon"),
        "csgbq 166: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 166: the processor reads the record then stops", "a"),
        "round 166: the processor reads the record then stops",
    ),
    (
        ("round 166: the processor reads the record then stops", "zz"),
        "qntmc 166: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 166: the processor reads the record then stops", "AgentU"),
        "ruyaw 166: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 166: the processor reads the record then stops", "keyboard"),
        "bssor 166: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 166: the processor reads the record then stops", "AA"),
        "round 166: the processor reads the record then stops",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "key"),
        "bssxh 166: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "lemon"),
        "csgbq 166: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "a"),
        "round 166: a worker pulls the next task from the queue",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "zz"),
        "qntmc 166: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 166: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "keyboard"),
        "bssor 166: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 166: a worker pulls the next task from the queue", "AA"),
        "round 166: a worker pulls the next task from the queue",
    ),
    (
        ("round 166: signals travel through the network layer", "key"),
        "bssxh 166: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 166: signals travel through the network layer", "lemon"),
        "csgbq 166: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 166: signals travel through the network layer", "a"),
        "round 166: signals travel through the network layer",
    ),
    (
        ("round 166: signals travel through the network layer", "zz"),
        "qntmc 166: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 166: signals travel through the network layer", "AgentU"),
        "ruyaw 166: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 166: signals travel through the network layer", "keyboard"),
        "bssor 166: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 166: signals travel through the network layer", "AA"),
        "round 166: signals travel through the network layer",
    ),
    (
        ("round 166: the gateway routes each request by policy", "key"),
        "bssxh 166: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 166: the gateway routes each request by policy", "lemon"),
        "csgbq 166: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 166: the gateway routes each request by policy", "a"),
        "round 166: the gateway routes each request by policy",
    ),
    (
        ("round 166: the gateway routes each request by policy", "zz"),
        "qntmc 166: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 166: the gateway routes each request by policy", "AgentU"),
        "ruyaw 166: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 166: the gateway routes each request by policy", "keyboard"),
        "bssor 166: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 166: the gateway routes each request by policy", "AA"),
        "round 166: the gateway routes each request by policy",
    ),
    (("round 166: memory grows until the buffer is full", "key"), "bssxh 166: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 166: memory grows until the buffer is full", "lemon"), "csgbq 166: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 166: memory grows until the buffer is full", "a"), "round 166: memory grows until the buffer is full"),
    (("round 166: memory grows until the buffer is full", "zz"), "qntmc 166: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 166: memory grows until the buffer is full", "AgentU"),
        "ruyaw 166: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 166: memory grows until the buffer is full", "keyboard"),
        "bssor 166: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 166: memory grows until the buffer is full", "AA"), "round 166: memory grows until the buffer is full"),
    (("round 166: the cluster mirrors every packet twice", "key"), "bssxh 166: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 166: the cluster mirrors every packet twice", "lemon"),
        "csgbq 166: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 166: the cluster mirrors every packet twice", "a"), "round 166: the cluster mirrors every packet twice"),
    (("round 166: the cluster mirrors every packet twice", "zz"), "qntmc 166: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 166: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 166: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 166: the cluster mirrors every packet twice", "keyboard"),
        "bssor 166: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 166: the cluster mirrors every packet twice", "AA"), "round 166: the cluster mirrors every packet twice"),
    (
        ("round 166: ranking uses tokens learned from the corpus", "key"),
        "bssxh 166: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 166: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", "a"),
        "round 166: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 166: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 166: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 166: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", "AA"),
        "round 166: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 166: a long session ends when the candle dies", "key"),
        "bssxh 166: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 166: a long session ends when the candle dies", "lemon"),
        "csgbq 166: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 166: a long session ends when the candle dies", "a"),
        "round 166: a long session ends when the candle dies",
    ),
    (
        ("round 166: a long session ends when the candle dies", "zz"),
        "qntmc 166: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 166: a long session ends when the candle dies", "AgentU"),
        "ruyaw 166: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 166: a long session ends when the candle dies", "keyboard"),
        "bssor 166: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 166: a long session ends when the candle dies", "AA"),
        "round 166: a long session ends when the candle dies",
    ),
    (("round 166: encode the prompt then map the result", "key"), "bssxh 166: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 166: encode the prompt then map the result", "lemon"), "csgbq 166: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 166: encode the prompt then map the result", "a"), "round 166: encode the prompt then map the result"),
    (("round 166: encode the prompt then map the result", "zz"), "qntmc 166: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 166: encode the prompt then map the result", "AgentU"),
        "ruyaw 166: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 166: encode the prompt then map the result", "keyboard"),
        "bssor 166: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 166: encode the prompt then map the result", "AA"), "round 166: encode the prompt then map the result"),
    (("round 166: the kernel wakes the worker at dawn", "key"), "bssxh 166: rri iovlop ukocc xfo ambocb er neux"),
    (("round 166: the kernel wakes the worker at dawn", "lemon"), "csgbq 166: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 166: the kernel wakes the worker at dawn", "a"), "round 166: the kernel wakes the worker at dawn"),
    (("round 166: the kernel wakes the worker at dawn", "zz"), "qntmc 166: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 166: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 166: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 166: the kernel wakes the worker at dawn", "keyboard"), "bssor 166: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 166: the kernel wakes the worker at dawn", "AA"), "round 166: the kernel wakes the worker at dawn"),
    (("round 166: service latency drops after the patch", "key"), "bssxh 166: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 166: service latency drops after the patch", "lemon"), "csgbq 166: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 166: service latency drops after the patch", "a"), "round 166: service latency drops after the patch"),
    (("round 166: service latency drops after the patch", "zz"), "qntmc 166: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 166: service latency drops after the patch", "AgentU"),
        "ruyaw 166: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 166: service latency drops after the patch", "keyboard"),
        "bssor 166: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 166: service latency drops after the patch", "AA"), "round 166: service latency drops after the patch"),
    (
        ("round 166: the library caches every vector it sees", "key"),
        "bssxh 166: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 166: the library caches every vector it sees", "lemon"),
        "csgbq 166: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 166: the library caches every vector it sees", "a"), "round 166: the library caches every vector it sees"),
    (
        ("round 166: the library caches every vector it sees", "zz"),
        "qntmc 166: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 166: the library caches every vector it sees", "AgentU"),
        "ruyaw 166: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 166: the library caches every vector it sees", "keyboard"),
        "bssor 166: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 166: the library caches every vector it sees", "AA"),
        "round 166: the library caches every vector it sees",
    ),
    (("round 166: agents argue then the debate resolves", "key"), "bssxh 166: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 166: agents argue then the debate resolves", "lemon"), "csgbq 166: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 166: agents argue then the debate resolves", "a"), "round 166: agents argue then the debate resolves"),
    (("round 166: agents argue then the debate resolves", "zz"), "qntmc 166: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 166: agents argue then the debate resolves", "AgentU"),
        "ruyaw 166: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 166: agents argue then the debate resolves", "keyboard"),
        "bssor 166: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 166: agents argue then the debate resolves", "AA"), "round 166: agents argue then the debate resolves"),
    (("round 166: the filter keeps only strong matches", "key"), "bssxh 166: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 166: the filter keeps only strong matches", "lemon"), "csgbq 166: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 166: the filter keeps only strong matches", "a"), "round 166: the filter keeps only strong matches"),
    (("round 166: the filter keeps only strong matches", "zz"), "qntmc 166: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 166: the filter keeps only strong matches", "AgentU"), "ruyaw 166: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 166: the filter keeps only strong matches", "keyboard"),
        "bssor 166: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 166: the filter keeps only strong matches", "AA"), "round 166: the filter keeps only strong matches"),
    (("round 166: the model answers with a short reply", "key"), "bssxh 166: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 166: the model answers with a short reply", "lemon"), "csgbq 166: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 166: the model answers with a short reply", "a"), "round 166: the model answers with a short reply"),
    (("round 166: the model answers with a short reply", "zz"), "qntmc 166: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 166: the model answers with a short reply", "AgentU"), "ruyaw 166: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 166: the model answers with a short reply", "keyboard"),
        "bssor 166: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 166: the model answers with a short reply", "AA"), "round 166: the model answers with a short reply"),
    (
        ("round 166: the recorder stores the reasoning trace", "key"),
        "bssxh 166: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 166: the recorder stores the reasoning trace", "lemon"),
        "csgbq 166: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 166: the recorder stores the reasoning trace", "a"), "round 166: the recorder stores the reasoning trace"),
    (
        ("round 166: the recorder stores the reasoning trace", "zz"),
        "qntmc 166: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 166: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 166: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 166: the recorder stores the reasoning trace", "keyboard"),
        "bssor 166: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 166: the recorder stores the reasoning trace", "AA"),
        "round 166: the recorder stores the reasoning trace",
    ),
    (("round 166: the angel watches the processor run", "key"), "bssxh 166: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 166: the angel watches the processor run", "lemon"), "csgbq 166: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 166: the angel watches the processor run", "a"), "round 166: the angel watches the processor run"),
    (("round 166: the angel watches the processor run", "zz"), "qntmc 166: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 166: the angel watches the processor run", "AgentU"), "ruyaw 166: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 166: the angel watches the processor run", "keyboard"), "bssor 166: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 166: the angel watches the processor run", "AA"), "round 166: the angel watches the processor run"),
    (("round 166: angle of the vector decides the match", "key"), "bssxh 166: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 166: angle of the vector decides the match", "lemon"), "csgbq 166: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 166: angle of the vector decides the match", "a"), "round 166: angle of the vector decides the match"),
    (("round 166: angle of the vector decides the match", "zz"), "qntmc 166: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 166: angle of the vector decides the match", "AgentU"),
        "ruyaw 166: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 166: angle of the vector decides the match", "keyboard"),
        "bssor 166: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 166: angle of the vector decides the match", "AA"), "round 166: angle of the vector decides the match"),
    (
        ("round 166: the candle burns twice as long at night", "key"),
        "bssxh 166: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 166: the candle burns twice as long at night", "lemon"),
        "csgbq 166: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 166: the candle burns twice as long at night", "a"), "round 166: the candle burns twice as long at night"),
    (
        ("round 166: the candle burns twice as long at night", "zz"),
        "qntmc 166: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 166: the candle burns twice as long at night", "AgentU"),
        "ruyaw 166: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 166: the candle burns twice as long at night", "keyboard"),
        "bssor 166: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 166: the candle burns twice as long at night", "AA"),
        "round 166: the candle burns twice as long at night",
    ),
    (("round 166: a mirror of the universe in one line", "key"), "bssxh 166: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 166: a mirror of the universe in one line", "lemon"), "csgbq 166: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 166: a mirror of the universe in one line", "a"), "round 166: a mirror of the universe in one line"),
    (("round 166: a mirror of the universe in one line", "zz"), "qntmc 166: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 166: a mirror of the universe in one line", "AgentU"), "ruyaw 166: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 166: a mirror of the universe in one line", "keyboard"),
        "bssor 166: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 166: a mirror of the universe in one line", "AA"), "round 166: a mirror of the universe in one line"),
    (("round 166: the queue drains before the storm", "key"), "bssxh 166: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 166: the queue drains before the storm", "lemon"), "csgbq 166: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 166: the queue drains before the storm", "a"), "round 166: the queue drains before the storm"),
    (("round 166: the queue drains before the storm", "zz"), "qntmc 166: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 166: the queue drains before the storm", "AgentU"), "ruyaw 166: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 166: the queue drains before the storm", "keyboard"), "bssor 166: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 166: the queue drains before the storm", "AA"), "round 166: the queue drains before the storm"),
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
