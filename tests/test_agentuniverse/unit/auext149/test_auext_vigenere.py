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
    (("kitten149", "key"), "umrdil149"),
    (("kitten149", "lemon"), "vmfhry149"),
    (("kitten149", "a"), "kitten149"),
    (("kitten149", "zz"), "jhssdm149"),
    (("kitten149", "AgentU"), "koxgxh149"),
    (("kitten149", "keyboard"), "umrusn149"),
    (("kitten149", "AA"), "kitten149"),
    (("sitting149", "key"), "cmrdmlq149"),
    (("sitting149", "lemon"), "dmfhvyk149"),
    (("sitting149", "a"), "sitting149"),
    (("sitting149", "zz"), "rhsshmf149"),
    (("sitting149", "AgentU"), "soxgbhg149"),
    (("sitting149", "keyboard"), "cmruwnx149"),
    (("sitting149", "AA"), "sitting149"),
    (("agent149", "key"), "kkcxx149"),
    (("agent149", "lemon"), "lkqbg149"),
    (("agent149", "a"), "agent149"),
    (("agent149", "zz"), "zfdms149"),
    (("agent149", "AgentU"), "amiam149"),
    (("agent149", "keyboard"), "kkcoh149"),
    (("agent149", "AA"), "agent149"),
    (("angle149", "key"), "krevi149"),
    (("angle149", "lemon"), "lrszr149"),
    (("angle149", "a"), "angle149"),
    (("angle149", "zz"), "zmfkd149"),
    (("angle149", "AgentU"), "atkyx149"),
    (("angle149", "keyboard"), "krems149"),
    (("angle149", "AA"), "angle149"),
    (("universe149", "key"), "ergfipci149"),
    (("universe149", "lemon"), "frujrcwq149"),
    (("universe149", "a"), "universe149"),
    (("universe149", "zz"), "tmhudqrd149"),
    (("universe149", "AgentU"), "utmixlsk149"),
    (("universe149", "keyboard"), "ergwsrjh149"),
    (("universe149", "AA"), "universe149"),
    (("memory149", "key"), "wikyvw149"),
    (("memory149", "lemon"), "xiycej149"),
    (("memory149", "a"), "memory149"),
    (("memory149", "zz"), "ldlnqx149"),
    (("memory149", "AgentU"), "mkqbks149"),
    (("memory149", "keyboard"), "wikpfy149"),
    (("memory149", "AA"), "memory149"),
    (("stream149", "key"), "cxpoek149"),
    (("stream149", "lemon"), "dxdsnx149"),
    (("stream149", "a"), "stream149"),
    (("stream149", "zz"), "rsqdzl149"),
    (("stream149", "AgentU"), "szvrtg149"),
    (("stream149", "keyboard"), "cxpfom149"),
    (("stream149", "AA"), "stream149"),
    (("context149", "key"), "msldivd149"),
    (("context149", "lemon"), "nszhrix149"),
    (("context149", "a"), "context149"),
    (("context149", "zz"), "bnmsdws149"),
    (("context149", "AgentU"), "curgxrt149"),
    (("context149", "keyboard"), "mslusxk149"),
    (("context149", "AA"), "context149"),
    (("knowledge149", "key"), "urmgpcnkc149"),
    (("knowledge149", "lemon"), "vrakyphss149"),
    (("knowledge149", "a"), "knowledge149"),
    (("knowledge149", "zz"), "jmnvkdcfd149"),
    (("knowledge149", "AgentU"), "ktsjeydmi149"),
    (("knowledge149", "keyboard"), "urmxzeujo149"),
    (("knowledge149", "AA"), "knowledge149"),
    (("vector149", "key"), "fiadsp149"),
    (("vector149", "lemon"), "giohbc149"),
    (("vector149", "a"), "vector149"),
    (("vector149", "zz"), "udbsnq149"),
    (("vector149", "AgentU"), "vkgghl149"),
    (("vector149", "keyboard"), "fiaucr149"),
    (("vector149", "AA"), "vector149"),
    (("processor149", "key"), "zvmmiqcsp149"),
    (("processor149", "lemon"), "avaqrdwaf149"),
    (("processor149", "a"), "processor149"),
    (("processor149", "zz"), "oqnbdrrnq149"),
    (("processor149", "AgentU"), "pxspxmsuv149"),
    (("processor149", "keyboard"), "zvmdssjrb149"),
    (("processor149", "AA"), "processor149"),
    (("reasoning149", "key"), "biycslsre149"),
    (("reasoning149", "lemon"), "cimgbymzu149"),
    (("reasoning149", "a"), "reasoning149"),
    (("reasoning149", "zz"), "qdzrnmhmf149"),
    (("reasoning149", "AgentU"), "rkefhhitk149"),
    (("reasoning149", "keyboard"), "biytcnzqq149"),
    (("reasoning149", "AA"), "reasoning149"),
    (("machine149", "key"), "wearmlo149"),
    (("machine149", "lemon"), "xeovvyi149"),
    (("machine149", "a"), "machine149"),
    (("machine149", "zz"), "lzbghmd149"),
    (("machine149", "AgentU"), "mggubhe149"),
    (("machine149", "keyboard"), "weaiwnv149"),
    (("machine149", "AA"), "machine149"),
    (("learning149", "key"), "viybrgxk149"),
    (("learning149", "lemon"), "wimfatrs149"),
    (("learning149", "a"), "learning149"),
    (("learning149", "zz"), "kdzqmhmf149"),
    (("learning149", "AgentU"), "lkeegcnm149"),
    (("learning149", "keyboard"), "viysbiej149"),
    (("learning149", "AA"), "learning149"),
    (("model149", "key"), "wsbop149"),
    (("model149", "lemon"), "xspsy149"),
    (("model149", "a"), "model149"),
    (("model149", "zz"), "lncdk149"),
    (("model149", "AgentU"), "muhre149"),
    (("model149", "keyboard"), "wsbfz149"),
    (("model149", "AA"), "model149"),
    (("token149", "key"), "dsior149"),
    (("token149", "lemon"), "eswsa149"),
    (("token149", "a"), "token149"),
    (("token149", "zz"), "snjdm149"),
    (("token149", "AgentU"), "tuorg149"),
    (("token149", "keyboard"), "dsifb149"),
    (("token149", "AA"), "token149"),
    (("prompt149", "key"), "zvmwtr149"),
    (("prompt149", "lemon"), "avaace149"),
    (("prompt149", "a"), "prompt149"),
    (("prompt149", "zz"), "oqnlos149"),
    (("prompt149", "AgentU"), "pxszin149"),
    (("prompt149", "keyboard"), "zvmndt149"),
    (("prompt149", "AA"), "prompt149"),
    (("session149", "key"), "ciqcmmx149"),
    (("session149", "lemon"), "diegvzr149"),
    (("session149", "a"), "session149"),
    (("session149", "zz"), "rdrrhnm149"),
    (("session149", "AgentU"), "skwfbin149"),
    (("session149", "keyboard"), "ciqtwoe149"),
    (("session149", "AA"), "session149"),
    (("library149", "key"), "vmzbepi149"),
    (("library149", "lemon"), "wmnfncc149"),
    (("library149", "a"), "library149"),
    (("library149", "zz"), "khaqzqx149"),
    (("library149", "AgentU"), "lofetly149"),
    (("library149", "keyboard"), "vmzsorp149"),
    (("library149", "AA"), "library149"),
    (("service149", "key"), "cipfmao149"),
    (("service149", "lemon"), "didjvni149"),
    (("service149", "a"), "service149"),
    (("service149", "zz"), "rdquhbd149"),
    (("service149", "AgentU"), "skvibwe149"),
    (("service149", "keyboard"), "cipwwcv149"),
    (("service149", "AA"), "service149"),
    (("gateway149", "key"), "qeroayi149"),
    (("gateway149", "lemon"), "refsjlc149"),
    (("gateway149", "a"), "gateway149"),
    (("gateway149", "zz"), "fzsdvzx149"),
    (("gateway149", "AgentU"), "ggxrpuy149"),
    (("gateway149", "keyboard"), "qerfkap149"),
    (("gateway149", "AA"), "gateway149"),
    (("storage149", "key"), "cxmbeeo149"),
    (("storage149", "lemon"), "dxafnri149"),
    (("storage149", "a"), "storage149"),
    (("storage149", "zz"), "rsnqzfd149"),
    (("storage149", "AgentU"), "szsetae149"),
    (("storage149", "keyboard"), "cxmsogv149"),
    (("storage149", "AA"), "storage149"),
    (("network149", "key"), "xirgspu149"),
    (("network149", "lemon"), "yifkbco149"),
    (("network149", "a"), "network149"),
    (("network149", "zz"), "mdsvnqj149"),
    (("network149", "AgentU"), "nkxjhlk149"),
    (("network149", "keyboard"), "xirxcrb149"),
    (("network149", "AA"), "network149"),
    (("latency149", "key"), "verorai149"),
    (("latency149", "lemon"), "wefsanc149"),
    (("latency149", "a"), "latency149"),
    (("latency149", "zz"), "kzsdmbx149"),
    (("latency149", "AgentU"), "lgxrgwy149"),
    (("latency149", "keyboard"), "verfbcp149"),
    (("latency149", "AA"), "latency149"),
    (("buffer149", "key"), "lydpip149"),
    (("buffer149", "lemon"), "myrtrc149"),
    (("buffer149", "a"), "buffer149"),
    (("buffer149", "zz"), "ateedq149"),
    (("buffer149", "AgentU"), "bajsxl149"),
    (("buffer149", "keyboard"), "lydgsr149"),
    (("buffer149", "AA"), "buffer149"),
    (("queue149", "key"), "aycei149"),
    (("queue149", "lemon"), "byqir149"),
    (("queue149", "a"), "queue149"),
    (("queue149", "zz"), "ptdtd149"),
    (("queue149", "AgentU"), "qaihx149"),
    (("queue149", "keyboard"), "aycvs149"),
    (("queue149", "AA"), "queue149"),
    (("worker149", "key"), "gspuip149"),
    (("worker149", "lemon"), "hsdyrc149"),
    (("worker149", "a"), "worker149"),
    (("worker149", "zz"), "vnqjdq149"),
    (("worker149", "AgentU"), "wuvxxl149"),
    (("worker149", "keyboard"), "gsplsr149"),
    (("worker149", "AA"), "worker149"),
    (("kernel149", "key"), "uipxij149"),
    (("kernel149", "lemon"), "vidbrw149"),
    (("kernel149", "a"), "kernel149"),
    (("kernel149", "zz"), "jdqmdk149"),
    (("kernel149", "AgentU"), "kkvaxf149"),
    (("kernel149", "keyboard"), "uiposl149"),
    (("kernel149", "AA"), "kernel149"),
    (("signal149", "key"), "cmexej149"),
    (("signal149", "lemon"), "dmsbnw149"),
    (("signal149", "a"), "signal149"),
    (("signal149", "zz"), "rhfmzk149"),
    (("signal149", "AgentU"), "sokatf149"),
    (("signal149", "keyboard"), "cmeool149"),
    (("signal149", "AA"), "signal149"),
    (("packet149", "key"), "zeauir149"),
    (("packet149", "lemon"), "aeoyre149"),
    (("packet149", "a"), "packet149"),
    (("packet149", "zz"), "ozbjds149"),
    (("packet149", "AgentU"), "pggxxn149"),
    (("packet149", "keyboard"), "zealst149"),
    (("packet149", "AA"), "packet149"),
    (("router149", "key"), "bssdip149"),
    (("router149", "lemon"), "csghrc149"),
    (("router149", "a"), "router149"),
    (("router149", "zz"), "qntsdq149"),
    (("router149", "AgentU"), "ruygxl149"),
    (("router149", "keyboard"), "bssusr149"),
    (("router149", "AA"), "router149"),
    (("cluster149", "key"), "mpscxcb149"),
    (("cluster149", "lemon"), "npgggpv149"),
    (("cluster149", "a"), "cluster149"),
    (("cluster149", "zz"), "bktrsdq149"),
    (("cluster149", "AgentU"), "cryfmyr149"),
    (("cluster149", "keyboard"), "mpsthei149"),
    (("cluster149", "AA"), "cluster149"),
    (("mirror149", "key"), "wmpbsp149"),
    (("mirror149", "lemon"), "xmdfbc149"),
    (("mirror149", "a"), "mirror149"),
    (("mirror149", "zz"), "lhqqnq149"),
    (("mirror149", "AgentU"), "movehl149"),
    (("mirror149", "keyboard"), "wmpscr149"),
    (("mirror149", "AA"), "mirror149"),
    (("filter149", "key"), "pmjdip149"),
    (("filter149", "lemon"), "qmxhrc149"),
    (("filter149", "a"), "filter149"),
    (("filter149", "zz"), "ehksdq149"),
    (("filter149", "AgentU"), "fopgxl149"),
    (("filter149", "keyboard"), "pmjusr149"),
    (("filter149", "AA"), "filter149"),
    (("ranking149", "key"), "belumlq149"),
    (("ranking149", "lemon"), "cezyvyk149"),
    (("ranking149", "a"), "ranking149"),
    (("ranking149", "zz"), "qzmjhmf149"),
    (("ranking149", "AgentU"), "rgrxbhg149"),
    (("ranking149", "keyboard"), "bellwnx149"),
    (("ranking149", "AA"), "ranking149"),
    (("encoding149", "key"), "orayhgxk149"),
    (("encoding149", "lemon"), "procqtrs149"),
    (("encoding149", "a"), "encoding149"),
    (("encoding149", "zz"), "dmbnchmf149"),
    (("encoding149", "AgentU"), "etgbwcnm149"),
    (("encoding149", "keyboard"), "orapriej149"),
    (("encoding149", "AA"), "encoding149"),
    (("mapping149", "key"), "wenzmlq149"),
    (("mapping149", "lemon"), "xebdvyk149"),
    (("mapping149", "a"), "mapping149"),
    (("mapping149", "zz"), "lzoohmf149"),
    (("mapping149", "AgentU"), "mgtcbhg149"),
    (("mapping149", "keyboard"), "wenqwnx149"),
    (("mapping149", "AA"), "mapping149"),
    (("record149", "key"), "biayvb149"),
    (("record149", "lemon"), "cioceo149"),
    (("record149", "a"), "record149"),
    (("record149", "zz"), "qdbnqc149"),
    (("record149", "AgentU"), "rkgbkx149"),
    (("record149", "keyboard"), "biapfd149"),
    (("record149", "AA"), "record149"),
    (("candle149", "key"), "melnpc149"),
    (("candle149", "lemon"), "nezryp149"),
    (("candle149", "a"), "candle149"),
    (("candle149", "zz"), "bzmckd149"),
    (("candle149", "AgentU"), "cgrqey149"),
    (("candle149", "keyboard"), "meleze149"),
    (("candle149", "AA"), "candle149"),
    (("thread149", "key"), "dlpoeb149"),
    (("thread149", "lemon"), "eldsno149"),
    (("thread149", "a"), "thread149"),
    (("thread149", "zz"), "sgqdzc149"),
    (("thread149", "AgentU"), "tnvrtx149"),
    (("thread149", "keyboard"), "dlpfod149"),
    (("thread149", "AA"), "thread149"),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 149: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 149: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "a"),
        "round 149: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 149: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 149: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 149: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", "AA"),
        "round 149: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "key"),
        "bssxh 149: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 149: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "a"),
        "round 149: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 149: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 149: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 149: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", "AA"),
        "round 149: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 149: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 149: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "a"),
        "round 149: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 149: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 149: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 149: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", "AA"),
        "round 149: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 149: the processor reads the record then stops", "key"),
        "bssxh 149: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 149: the processor reads the record then stops", "lemon"),
        "csgbq 149: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 149: the processor reads the record then stops", "a"),
        "round 149: the processor reads the record then stops",
    ),
    (
        ("round 149: the processor reads the record then stops", "zz"),
        "qntmc 149: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 149: the processor reads the record then stops", "AgentU"),
        "ruyaw 149: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 149: the processor reads the record then stops", "keyboard"),
        "bssor 149: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 149: the processor reads the record then stops", "AA"),
        "round 149: the processor reads the record then stops",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "key"),
        "bssxh 149: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "lemon"),
        "csgbq 149: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "a"),
        "round 149: a worker pulls the next task from the queue",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "zz"),
        "qntmc 149: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 149: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "keyboard"),
        "bssor 149: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 149: a worker pulls the next task from the queue", "AA"),
        "round 149: a worker pulls the next task from the queue",
    ),
    (
        ("round 149: signals travel through the network layer", "key"),
        "bssxh 149: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 149: signals travel through the network layer", "lemon"),
        "csgbq 149: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 149: signals travel through the network layer", "a"),
        "round 149: signals travel through the network layer",
    ),
    (
        ("round 149: signals travel through the network layer", "zz"),
        "qntmc 149: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 149: signals travel through the network layer", "AgentU"),
        "ruyaw 149: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 149: signals travel through the network layer", "keyboard"),
        "bssor 149: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 149: signals travel through the network layer", "AA"),
        "round 149: signals travel through the network layer",
    ),
    (
        ("round 149: the gateway routes each request by policy", "key"),
        "bssxh 149: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 149: the gateway routes each request by policy", "lemon"),
        "csgbq 149: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 149: the gateway routes each request by policy", "a"),
        "round 149: the gateway routes each request by policy",
    ),
    (
        ("round 149: the gateway routes each request by policy", "zz"),
        "qntmc 149: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 149: the gateway routes each request by policy", "AgentU"),
        "ruyaw 149: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 149: the gateway routes each request by policy", "keyboard"),
        "bssor 149: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 149: the gateway routes each request by policy", "AA"),
        "round 149: the gateway routes each request by policy",
    ),
    (("round 149: memory grows until the buffer is full", "key"), "bssxh 149: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 149: memory grows until the buffer is full", "lemon"), "csgbq 149: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 149: memory grows until the buffer is full", "a"), "round 149: memory grows until the buffer is full"),
    (("round 149: memory grows until the buffer is full", "zz"), "qntmc 149: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 149: memory grows until the buffer is full", "AgentU"),
        "ruyaw 149: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 149: memory grows until the buffer is full", "keyboard"),
        "bssor 149: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 149: memory grows until the buffer is full", "AA"), "round 149: memory grows until the buffer is full"),
    (("round 149: the cluster mirrors every packet twice", "key"), "bssxh 149: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 149: the cluster mirrors every packet twice", "lemon"),
        "csgbq 149: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 149: the cluster mirrors every packet twice", "a"), "round 149: the cluster mirrors every packet twice"),
    (("round 149: the cluster mirrors every packet twice", "zz"), "qntmc 149: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 149: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 149: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 149: the cluster mirrors every packet twice", "keyboard"),
        "bssor 149: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 149: the cluster mirrors every packet twice", "AA"), "round 149: the cluster mirrors every packet twice"),
    (
        ("round 149: ranking uses tokens learned from the corpus", "key"),
        "bssxh 149: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 149: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", "a"),
        "round 149: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 149: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 149: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 149: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", "AA"),
        "round 149: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 149: a long session ends when the candle dies", "key"),
        "bssxh 149: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 149: a long session ends when the candle dies", "lemon"),
        "csgbq 149: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 149: a long session ends when the candle dies", "a"),
        "round 149: a long session ends when the candle dies",
    ),
    (
        ("round 149: a long session ends when the candle dies", "zz"),
        "qntmc 149: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 149: a long session ends when the candle dies", "AgentU"),
        "ruyaw 149: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 149: a long session ends when the candle dies", "keyboard"),
        "bssor 149: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 149: a long session ends when the candle dies", "AA"),
        "round 149: a long session ends when the candle dies",
    ),
    (("round 149: encode the prompt then map the result", "key"), "bssxh 149: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 149: encode the prompt then map the result", "lemon"), "csgbq 149: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 149: encode the prompt then map the result", "a"), "round 149: encode the prompt then map the result"),
    (("round 149: encode the prompt then map the result", "zz"), "qntmc 149: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 149: encode the prompt then map the result", "AgentU"),
        "ruyaw 149: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 149: encode the prompt then map the result", "keyboard"),
        "bssor 149: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 149: encode the prompt then map the result", "AA"), "round 149: encode the prompt then map the result"),
    (("round 149: the kernel wakes the worker at dawn", "key"), "bssxh 149: rri iovlop ukocc xfo ambocb er neux"),
    (("round 149: the kernel wakes the worker at dawn", "lemon"), "csgbq 149: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 149: the kernel wakes the worker at dawn", "a"), "round 149: the kernel wakes the worker at dawn"),
    (("round 149: the kernel wakes the worker at dawn", "zz"), "qntmc 149: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 149: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 149: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 149: the kernel wakes the worker at dawn", "keyboard"), "bssor 149: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 149: the kernel wakes the worker at dawn", "AA"), "round 149: the kernel wakes the worker at dawn"),
    (("round 149: service latency drops after the patch", "key"), "bssxh 149: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 149: service latency drops after the patch", "lemon"), "csgbq 149: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 149: service latency drops after the patch", "a"), "round 149: service latency drops after the patch"),
    (("round 149: service latency drops after the patch", "zz"), "qntmc 149: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 149: service latency drops after the patch", "AgentU"),
        "ruyaw 149: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 149: service latency drops after the patch", "keyboard"),
        "bssor 149: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 149: service latency drops after the patch", "AA"), "round 149: service latency drops after the patch"),
    (
        ("round 149: the library caches every vector it sees", "key"),
        "bssxh 149: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 149: the library caches every vector it sees", "lemon"),
        "csgbq 149: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 149: the library caches every vector it sees", "a"), "round 149: the library caches every vector it sees"),
    (
        ("round 149: the library caches every vector it sees", "zz"),
        "qntmc 149: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 149: the library caches every vector it sees", "AgentU"),
        "ruyaw 149: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 149: the library caches every vector it sees", "keyboard"),
        "bssor 149: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 149: the library caches every vector it sees", "AA"),
        "round 149: the library caches every vector it sees",
    ),
    (("round 149: agents argue then the debate resolves", "key"), "bssxh 149: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 149: agents argue then the debate resolves", "lemon"), "csgbq 149: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 149: agents argue then the debate resolves", "a"), "round 149: agents argue then the debate resolves"),
    (("round 149: agents argue then the debate resolves", "zz"), "qntmc 149: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 149: agents argue then the debate resolves", "AgentU"),
        "ruyaw 149: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 149: agents argue then the debate resolves", "keyboard"),
        "bssor 149: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 149: agents argue then the debate resolves", "AA"), "round 149: agents argue then the debate resolves"),
    (("round 149: the filter keeps only strong matches", "key"), "bssxh 149: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 149: the filter keeps only strong matches", "lemon"), "csgbq 149: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 149: the filter keeps only strong matches", "a"), "round 149: the filter keeps only strong matches"),
    (("round 149: the filter keeps only strong matches", "zz"), "qntmc 149: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 149: the filter keeps only strong matches", "AgentU"), "ruyaw 149: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 149: the filter keeps only strong matches", "keyboard"),
        "bssor 149: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 149: the filter keeps only strong matches", "AA"), "round 149: the filter keeps only strong matches"),
    (("round 149: the model answers with a short reply", "key"), "bssxh 149: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 149: the model answers with a short reply", "lemon"), "csgbq 149: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 149: the model answers with a short reply", "a"), "round 149: the model answers with a short reply"),
    (("round 149: the model answers with a short reply", "zz"), "qntmc 149: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 149: the model answers with a short reply", "AgentU"), "ruyaw 149: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 149: the model answers with a short reply", "keyboard"),
        "bssor 149: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 149: the model answers with a short reply", "AA"), "round 149: the model answers with a short reply"),
    (
        ("round 149: the recorder stores the reasoning trace", "key"),
        "bssxh 149: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 149: the recorder stores the reasoning trace", "lemon"),
        "csgbq 149: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 149: the recorder stores the reasoning trace", "a"), "round 149: the recorder stores the reasoning trace"),
    (
        ("round 149: the recorder stores the reasoning trace", "zz"),
        "qntmc 149: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 149: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 149: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 149: the recorder stores the reasoning trace", "keyboard"),
        "bssor 149: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 149: the recorder stores the reasoning trace", "AA"),
        "round 149: the recorder stores the reasoning trace",
    ),
    (("round 149: the angel watches the processor run", "key"), "bssxh 149: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 149: the angel watches the processor run", "lemon"), "csgbq 149: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 149: the angel watches the processor run", "a"), "round 149: the angel watches the processor run"),
    (("round 149: the angel watches the processor run", "zz"), "qntmc 149: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 149: the angel watches the processor run", "AgentU"), "ruyaw 149: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 149: the angel watches the processor run", "keyboard"), "bssor 149: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 149: the angel watches the processor run", "AA"), "round 149: the angel watches the processor run"),
    (("round 149: angle of the vector decides the match", "key"), "bssxh 149: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 149: angle of the vector decides the match", "lemon"), "csgbq 149: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 149: angle of the vector decides the match", "a"), "round 149: angle of the vector decides the match"),
    (("round 149: angle of the vector decides the match", "zz"), "qntmc 149: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 149: angle of the vector decides the match", "AgentU"),
        "ruyaw 149: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 149: angle of the vector decides the match", "keyboard"),
        "bssor 149: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 149: angle of the vector decides the match", "AA"), "round 149: angle of the vector decides the match"),
    (
        ("round 149: the candle burns twice as long at night", "key"),
        "bssxh 149: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 149: the candle burns twice as long at night", "lemon"),
        "csgbq 149: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 149: the candle burns twice as long at night", "a"), "round 149: the candle burns twice as long at night"),
    (
        ("round 149: the candle burns twice as long at night", "zz"),
        "qntmc 149: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 149: the candle burns twice as long at night", "AgentU"),
        "ruyaw 149: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 149: the candle burns twice as long at night", "keyboard"),
        "bssor 149: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 149: the candle burns twice as long at night", "AA"),
        "round 149: the candle burns twice as long at night",
    ),
    (("round 149: a mirror of the universe in one line", "key"), "bssxh 149: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 149: a mirror of the universe in one line", "lemon"), "csgbq 149: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 149: a mirror of the universe in one line", "a"), "round 149: a mirror of the universe in one line"),
    (("round 149: a mirror of the universe in one line", "zz"), "qntmc 149: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 149: a mirror of the universe in one line", "AgentU"), "ruyaw 149: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 149: a mirror of the universe in one line", "keyboard"),
        "bssor 149: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 149: a mirror of the universe in one line", "AA"), "round 149: a mirror of the universe in one line"),
    (("round 149: the queue drains before the storm", "key"), "bssxh 149: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 149: the queue drains before the storm", "lemon"), "csgbq 149: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 149: the queue drains before the storm", "a"), "round 149: the queue drains before the storm"),
    (("round 149: the queue drains before the storm", "zz"), "qntmc 149: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 149: the queue drains before the storm", "AgentU"), "ruyaw 149: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 149: the queue drains before the storm", "keyboard"), "bssor 149: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 149: the queue drains before the storm", "AA"), "round 149: the queue drains before the storm"),
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
