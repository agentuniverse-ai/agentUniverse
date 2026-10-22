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
    (("kitten121", "key"), "umrdil121"),
    (("kitten121", "lemon"), "vmfhry121"),
    (("kitten121", "a"), "kitten121"),
    (("kitten121", "zz"), "jhssdm121"),
    (("kitten121", "AgentU"), "koxgxh121"),
    (("kitten121", "keyboard"), "umrusn121"),
    (("kitten121", "AA"), "kitten121"),
    (("sitting121", "key"), "cmrdmlq121"),
    (("sitting121", "lemon"), "dmfhvyk121"),
    (("sitting121", "a"), "sitting121"),
    (("sitting121", "zz"), "rhsshmf121"),
    (("sitting121", "AgentU"), "soxgbhg121"),
    (("sitting121", "keyboard"), "cmruwnx121"),
    (("sitting121", "AA"), "sitting121"),
    (("agent121", "key"), "kkcxx121"),
    (("agent121", "lemon"), "lkqbg121"),
    (("agent121", "a"), "agent121"),
    (("agent121", "zz"), "zfdms121"),
    (("agent121", "AgentU"), "amiam121"),
    (("agent121", "keyboard"), "kkcoh121"),
    (("agent121", "AA"), "agent121"),
    (("angle121", "key"), "krevi121"),
    (("angle121", "lemon"), "lrszr121"),
    (("angle121", "a"), "angle121"),
    (("angle121", "zz"), "zmfkd121"),
    (("angle121", "AgentU"), "atkyx121"),
    (("angle121", "keyboard"), "krems121"),
    (("angle121", "AA"), "angle121"),
    (("universe121", "key"), "ergfipci121"),
    (("universe121", "lemon"), "frujrcwq121"),
    (("universe121", "a"), "universe121"),
    (("universe121", "zz"), "tmhudqrd121"),
    (("universe121", "AgentU"), "utmixlsk121"),
    (("universe121", "keyboard"), "ergwsrjh121"),
    (("universe121", "AA"), "universe121"),
    (("memory121", "key"), "wikyvw121"),
    (("memory121", "lemon"), "xiycej121"),
    (("memory121", "a"), "memory121"),
    (("memory121", "zz"), "ldlnqx121"),
    (("memory121", "AgentU"), "mkqbks121"),
    (("memory121", "keyboard"), "wikpfy121"),
    (("memory121", "AA"), "memory121"),
    (("stream121", "key"), "cxpoek121"),
    (("stream121", "lemon"), "dxdsnx121"),
    (("stream121", "a"), "stream121"),
    (("stream121", "zz"), "rsqdzl121"),
    (("stream121", "AgentU"), "szvrtg121"),
    (("stream121", "keyboard"), "cxpfom121"),
    (("stream121", "AA"), "stream121"),
    (("context121", "key"), "msldivd121"),
    (("context121", "lemon"), "nszhrix121"),
    (("context121", "a"), "context121"),
    (("context121", "zz"), "bnmsdws121"),
    (("context121", "AgentU"), "curgxrt121"),
    (("context121", "keyboard"), "mslusxk121"),
    (("context121", "AA"), "context121"),
    (("knowledge121", "key"), "urmgpcnkc121"),
    (("knowledge121", "lemon"), "vrakyphss121"),
    (("knowledge121", "a"), "knowledge121"),
    (("knowledge121", "zz"), "jmnvkdcfd121"),
    (("knowledge121", "AgentU"), "ktsjeydmi121"),
    (("knowledge121", "keyboard"), "urmxzeujo121"),
    (("knowledge121", "AA"), "knowledge121"),
    (("vector121", "key"), "fiadsp121"),
    (("vector121", "lemon"), "giohbc121"),
    (("vector121", "a"), "vector121"),
    (("vector121", "zz"), "udbsnq121"),
    (("vector121", "AgentU"), "vkgghl121"),
    (("vector121", "keyboard"), "fiaucr121"),
    (("vector121", "AA"), "vector121"),
    (("processor121", "key"), "zvmmiqcsp121"),
    (("processor121", "lemon"), "avaqrdwaf121"),
    (("processor121", "a"), "processor121"),
    (("processor121", "zz"), "oqnbdrrnq121"),
    (("processor121", "AgentU"), "pxspxmsuv121"),
    (("processor121", "keyboard"), "zvmdssjrb121"),
    (("processor121", "AA"), "processor121"),
    (("reasoning121", "key"), "biycslsre121"),
    (("reasoning121", "lemon"), "cimgbymzu121"),
    (("reasoning121", "a"), "reasoning121"),
    (("reasoning121", "zz"), "qdzrnmhmf121"),
    (("reasoning121", "AgentU"), "rkefhhitk121"),
    (("reasoning121", "keyboard"), "biytcnzqq121"),
    (("reasoning121", "AA"), "reasoning121"),
    (("machine121", "key"), "wearmlo121"),
    (("machine121", "lemon"), "xeovvyi121"),
    (("machine121", "a"), "machine121"),
    (("machine121", "zz"), "lzbghmd121"),
    (("machine121", "AgentU"), "mggubhe121"),
    (("machine121", "keyboard"), "weaiwnv121"),
    (("machine121", "AA"), "machine121"),
    (("learning121", "key"), "viybrgxk121"),
    (("learning121", "lemon"), "wimfatrs121"),
    (("learning121", "a"), "learning121"),
    (("learning121", "zz"), "kdzqmhmf121"),
    (("learning121", "AgentU"), "lkeegcnm121"),
    (("learning121", "keyboard"), "viysbiej121"),
    (("learning121", "AA"), "learning121"),
    (("model121", "key"), "wsbop121"),
    (("model121", "lemon"), "xspsy121"),
    (("model121", "a"), "model121"),
    (("model121", "zz"), "lncdk121"),
    (("model121", "AgentU"), "muhre121"),
    (("model121", "keyboard"), "wsbfz121"),
    (("model121", "AA"), "model121"),
    (("token121", "key"), "dsior121"),
    (("token121", "lemon"), "eswsa121"),
    (("token121", "a"), "token121"),
    (("token121", "zz"), "snjdm121"),
    (("token121", "AgentU"), "tuorg121"),
    (("token121", "keyboard"), "dsifb121"),
    (("token121", "AA"), "token121"),
    (("prompt121", "key"), "zvmwtr121"),
    (("prompt121", "lemon"), "avaace121"),
    (("prompt121", "a"), "prompt121"),
    (("prompt121", "zz"), "oqnlos121"),
    (("prompt121", "AgentU"), "pxszin121"),
    (("prompt121", "keyboard"), "zvmndt121"),
    (("prompt121", "AA"), "prompt121"),
    (("session121", "key"), "ciqcmmx121"),
    (("session121", "lemon"), "diegvzr121"),
    (("session121", "a"), "session121"),
    (("session121", "zz"), "rdrrhnm121"),
    (("session121", "AgentU"), "skwfbin121"),
    (("session121", "keyboard"), "ciqtwoe121"),
    (("session121", "AA"), "session121"),
    (("library121", "key"), "vmzbepi121"),
    (("library121", "lemon"), "wmnfncc121"),
    (("library121", "a"), "library121"),
    (("library121", "zz"), "khaqzqx121"),
    (("library121", "AgentU"), "lofetly121"),
    (("library121", "keyboard"), "vmzsorp121"),
    (("library121", "AA"), "library121"),
    (("service121", "key"), "cipfmao121"),
    (("service121", "lemon"), "didjvni121"),
    (("service121", "a"), "service121"),
    (("service121", "zz"), "rdquhbd121"),
    (("service121", "AgentU"), "skvibwe121"),
    (("service121", "keyboard"), "cipwwcv121"),
    (("service121", "AA"), "service121"),
    (("gateway121", "key"), "qeroayi121"),
    (("gateway121", "lemon"), "refsjlc121"),
    (("gateway121", "a"), "gateway121"),
    (("gateway121", "zz"), "fzsdvzx121"),
    (("gateway121", "AgentU"), "ggxrpuy121"),
    (("gateway121", "keyboard"), "qerfkap121"),
    (("gateway121", "AA"), "gateway121"),
    (("storage121", "key"), "cxmbeeo121"),
    (("storage121", "lemon"), "dxafnri121"),
    (("storage121", "a"), "storage121"),
    (("storage121", "zz"), "rsnqzfd121"),
    (("storage121", "AgentU"), "szsetae121"),
    (("storage121", "keyboard"), "cxmsogv121"),
    (("storage121", "AA"), "storage121"),
    (("network121", "key"), "xirgspu121"),
    (("network121", "lemon"), "yifkbco121"),
    (("network121", "a"), "network121"),
    (("network121", "zz"), "mdsvnqj121"),
    (("network121", "AgentU"), "nkxjhlk121"),
    (("network121", "keyboard"), "xirxcrb121"),
    (("network121", "AA"), "network121"),
    (("latency121", "key"), "verorai121"),
    (("latency121", "lemon"), "wefsanc121"),
    (("latency121", "a"), "latency121"),
    (("latency121", "zz"), "kzsdmbx121"),
    (("latency121", "AgentU"), "lgxrgwy121"),
    (("latency121", "keyboard"), "verfbcp121"),
    (("latency121", "AA"), "latency121"),
    (("buffer121", "key"), "lydpip121"),
    (("buffer121", "lemon"), "myrtrc121"),
    (("buffer121", "a"), "buffer121"),
    (("buffer121", "zz"), "ateedq121"),
    (("buffer121", "AgentU"), "bajsxl121"),
    (("buffer121", "keyboard"), "lydgsr121"),
    (("buffer121", "AA"), "buffer121"),
    (("queue121", "key"), "aycei121"),
    (("queue121", "lemon"), "byqir121"),
    (("queue121", "a"), "queue121"),
    (("queue121", "zz"), "ptdtd121"),
    (("queue121", "AgentU"), "qaihx121"),
    (("queue121", "keyboard"), "aycvs121"),
    (("queue121", "AA"), "queue121"),
    (("worker121", "key"), "gspuip121"),
    (("worker121", "lemon"), "hsdyrc121"),
    (("worker121", "a"), "worker121"),
    (("worker121", "zz"), "vnqjdq121"),
    (("worker121", "AgentU"), "wuvxxl121"),
    (("worker121", "keyboard"), "gsplsr121"),
    (("worker121", "AA"), "worker121"),
    (("kernel121", "key"), "uipxij121"),
    (("kernel121", "lemon"), "vidbrw121"),
    (("kernel121", "a"), "kernel121"),
    (("kernel121", "zz"), "jdqmdk121"),
    (("kernel121", "AgentU"), "kkvaxf121"),
    (("kernel121", "keyboard"), "uiposl121"),
    (("kernel121", "AA"), "kernel121"),
    (("signal121", "key"), "cmexej121"),
    (("signal121", "lemon"), "dmsbnw121"),
    (("signal121", "a"), "signal121"),
    (("signal121", "zz"), "rhfmzk121"),
    (("signal121", "AgentU"), "sokatf121"),
    (("signal121", "keyboard"), "cmeool121"),
    (("signal121", "AA"), "signal121"),
    (("packet121", "key"), "zeauir121"),
    (("packet121", "lemon"), "aeoyre121"),
    (("packet121", "a"), "packet121"),
    (("packet121", "zz"), "ozbjds121"),
    (("packet121", "AgentU"), "pggxxn121"),
    (("packet121", "keyboard"), "zealst121"),
    (("packet121", "AA"), "packet121"),
    (("router121", "key"), "bssdip121"),
    (("router121", "lemon"), "csghrc121"),
    (("router121", "a"), "router121"),
    (("router121", "zz"), "qntsdq121"),
    (("router121", "AgentU"), "ruygxl121"),
    (("router121", "keyboard"), "bssusr121"),
    (("router121", "AA"), "router121"),
    (("cluster121", "key"), "mpscxcb121"),
    (("cluster121", "lemon"), "npgggpv121"),
    (("cluster121", "a"), "cluster121"),
    (("cluster121", "zz"), "bktrsdq121"),
    (("cluster121", "AgentU"), "cryfmyr121"),
    (("cluster121", "keyboard"), "mpsthei121"),
    (("cluster121", "AA"), "cluster121"),
    (("mirror121", "key"), "wmpbsp121"),
    (("mirror121", "lemon"), "xmdfbc121"),
    (("mirror121", "a"), "mirror121"),
    (("mirror121", "zz"), "lhqqnq121"),
    (("mirror121", "AgentU"), "movehl121"),
    (("mirror121", "keyboard"), "wmpscr121"),
    (("mirror121", "AA"), "mirror121"),
    (("filter121", "key"), "pmjdip121"),
    (("filter121", "lemon"), "qmxhrc121"),
    (("filter121", "a"), "filter121"),
    (("filter121", "zz"), "ehksdq121"),
    (("filter121", "AgentU"), "fopgxl121"),
    (("filter121", "keyboard"), "pmjusr121"),
    (("filter121", "AA"), "filter121"),
    (("ranking121", "key"), "belumlq121"),
    (("ranking121", "lemon"), "cezyvyk121"),
    (("ranking121", "a"), "ranking121"),
    (("ranking121", "zz"), "qzmjhmf121"),
    (("ranking121", "AgentU"), "rgrxbhg121"),
    (("ranking121", "keyboard"), "bellwnx121"),
    (("ranking121", "AA"), "ranking121"),
    (("encoding121", "key"), "orayhgxk121"),
    (("encoding121", "lemon"), "procqtrs121"),
    (("encoding121", "a"), "encoding121"),
    (("encoding121", "zz"), "dmbnchmf121"),
    (("encoding121", "AgentU"), "etgbwcnm121"),
    (("encoding121", "keyboard"), "orapriej121"),
    (("encoding121", "AA"), "encoding121"),
    (("mapping121", "key"), "wenzmlq121"),
    (("mapping121", "lemon"), "xebdvyk121"),
    (("mapping121", "a"), "mapping121"),
    (("mapping121", "zz"), "lzoohmf121"),
    (("mapping121", "AgentU"), "mgtcbhg121"),
    (("mapping121", "keyboard"), "wenqwnx121"),
    (("mapping121", "AA"), "mapping121"),
    (("record121", "key"), "biayvb121"),
    (("record121", "lemon"), "cioceo121"),
    (("record121", "a"), "record121"),
    (("record121", "zz"), "qdbnqc121"),
    (("record121", "AgentU"), "rkgbkx121"),
    (("record121", "keyboard"), "biapfd121"),
    (("record121", "AA"), "record121"),
    (("candle121", "key"), "melnpc121"),
    (("candle121", "lemon"), "nezryp121"),
    (("candle121", "a"), "candle121"),
    (("candle121", "zz"), "bzmckd121"),
    (("candle121", "AgentU"), "cgrqey121"),
    (("candle121", "keyboard"), "meleze121"),
    (("candle121", "AA"), "candle121"),
    (("thread121", "key"), "dlpoeb121"),
    (("thread121", "lemon"), "eldsno121"),
    (("thread121", "a"), "thread121"),
    (("thread121", "zz"), "sgqdzc121"),
    (("thread121", "AgentU"), "tnvrtx121"),
    (("thread121", "keyboard"), "dlpfod121"),
    (("thread121", "AA"), "thread121"),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 121: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 121: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "a"),
        "round 121: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 121: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 121: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 121: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", "AA"),
        "round 121: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "key"),
        "bssxh 121: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 121: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "a"),
        "round 121: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 121: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 121: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 121: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", "AA"),
        "round 121: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 121: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 121: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "a"),
        "round 121: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 121: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 121: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 121: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", "AA"),
        "round 121: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 121: the processor reads the record then stops", "key"),
        "bssxh 121: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 121: the processor reads the record then stops", "lemon"),
        "csgbq 121: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 121: the processor reads the record then stops", "a"),
        "round 121: the processor reads the record then stops",
    ),
    (
        ("round 121: the processor reads the record then stops", "zz"),
        "qntmc 121: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 121: the processor reads the record then stops", "AgentU"),
        "ruyaw 121: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 121: the processor reads the record then stops", "keyboard"),
        "bssor 121: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 121: the processor reads the record then stops", "AA"),
        "round 121: the processor reads the record then stops",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "key"),
        "bssxh 121: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "lemon"),
        "csgbq 121: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "a"),
        "round 121: a worker pulls the next task from the queue",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "zz"),
        "qntmc 121: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 121: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "keyboard"),
        "bssor 121: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 121: a worker pulls the next task from the queue", "AA"),
        "round 121: a worker pulls the next task from the queue",
    ),
    (
        ("round 121: signals travel through the network layer", "key"),
        "bssxh 121: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 121: signals travel through the network layer", "lemon"),
        "csgbq 121: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 121: signals travel through the network layer", "a"),
        "round 121: signals travel through the network layer",
    ),
    (
        ("round 121: signals travel through the network layer", "zz"),
        "qntmc 121: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 121: signals travel through the network layer", "AgentU"),
        "ruyaw 121: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 121: signals travel through the network layer", "keyboard"),
        "bssor 121: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 121: signals travel through the network layer", "AA"),
        "round 121: signals travel through the network layer",
    ),
    (
        ("round 121: the gateway routes each request by policy", "key"),
        "bssxh 121: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 121: the gateway routes each request by policy", "lemon"),
        "csgbq 121: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 121: the gateway routes each request by policy", "a"),
        "round 121: the gateway routes each request by policy",
    ),
    (
        ("round 121: the gateway routes each request by policy", "zz"),
        "qntmc 121: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 121: the gateway routes each request by policy", "AgentU"),
        "ruyaw 121: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 121: the gateway routes each request by policy", "keyboard"),
        "bssor 121: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 121: the gateway routes each request by policy", "AA"),
        "round 121: the gateway routes each request by policy",
    ),
    (("round 121: memory grows until the buffer is full", "key"), "bssxh 121: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 121: memory grows until the buffer is full", "lemon"), "csgbq 121: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 121: memory grows until the buffer is full", "a"), "round 121: memory grows until the buffer is full"),
    (("round 121: memory grows until the buffer is full", "zz"), "qntmc 121: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 121: memory grows until the buffer is full", "AgentU"),
        "ruyaw 121: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 121: memory grows until the buffer is full", "keyboard"),
        "bssor 121: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 121: memory grows until the buffer is full", "AA"), "round 121: memory grows until the buffer is full"),
    (("round 121: the cluster mirrors every packet twice", "key"), "bssxh 121: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 121: the cluster mirrors every packet twice", "lemon"),
        "csgbq 121: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 121: the cluster mirrors every packet twice", "a"), "round 121: the cluster mirrors every packet twice"),
    (("round 121: the cluster mirrors every packet twice", "zz"), "qntmc 121: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 121: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 121: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 121: the cluster mirrors every packet twice", "keyboard"),
        "bssor 121: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 121: the cluster mirrors every packet twice", "AA"), "round 121: the cluster mirrors every packet twice"),
    (
        ("round 121: ranking uses tokens learned from the corpus", "key"),
        "bssxh 121: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 121: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", "a"),
        "round 121: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 121: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 121: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 121: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", "AA"),
        "round 121: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 121: a long session ends when the candle dies", "key"),
        "bssxh 121: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 121: a long session ends when the candle dies", "lemon"),
        "csgbq 121: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 121: a long session ends when the candle dies", "a"),
        "round 121: a long session ends when the candle dies",
    ),
    (
        ("round 121: a long session ends when the candle dies", "zz"),
        "qntmc 121: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 121: a long session ends when the candle dies", "AgentU"),
        "ruyaw 121: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 121: a long session ends when the candle dies", "keyboard"),
        "bssor 121: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 121: a long session ends when the candle dies", "AA"),
        "round 121: a long session ends when the candle dies",
    ),
    (("round 121: encode the prompt then map the result", "key"), "bssxh 121: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 121: encode the prompt then map the result", "lemon"), "csgbq 121: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 121: encode the prompt then map the result", "a"), "round 121: encode the prompt then map the result"),
    (("round 121: encode the prompt then map the result", "zz"), "qntmc 121: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 121: encode the prompt then map the result", "AgentU"),
        "ruyaw 121: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 121: encode the prompt then map the result", "keyboard"),
        "bssor 121: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 121: encode the prompt then map the result", "AA"), "round 121: encode the prompt then map the result"),
    (("round 121: the kernel wakes the worker at dawn", "key"), "bssxh 121: rri iovlop ukocc xfo ambocb er neux"),
    (("round 121: the kernel wakes the worker at dawn", "lemon"), "csgbq 121: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 121: the kernel wakes the worker at dawn", "a"), "round 121: the kernel wakes the worker at dawn"),
    (("round 121: the kernel wakes the worker at dawn", "zz"), "qntmc 121: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 121: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 121: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 121: the kernel wakes the worker at dawn", "keyboard"), "bssor 121: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 121: the kernel wakes the worker at dawn", "AA"), "round 121: the kernel wakes the worker at dawn"),
    (("round 121: service latency drops after the patch", "key"), "bssxh 121: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 121: service latency drops after the patch", "lemon"), "csgbq 121: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 121: service latency drops after the patch", "a"), "round 121: service latency drops after the patch"),
    (("round 121: service latency drops after the patch", "zz"), "qntmc 121: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 121: service latency drops after the patch", "AgentU"),
        "ruyaw 121: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 121: service latency drops after the patch", "keyboard"),
        "bssor 121: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 121: service latency drops after the patch", "AA"), "round 121: service latency drops after the patch"),
    (
        ("round 121: the library caches every vector it sees", "key"),
        "bssxh 121: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 121: the library caches every vector it sees", "lemon"),
        "csgbq 121: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 121: the library caches every vector it sees", "a"), "round 121: the library caches every vector it sees"),
    (
        ("round 121: the library caches every vector it sees", "zz"),
        "qntmc 121: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 121: the library caches every vector it sees", "AgentU"),
        "ruyaw 121: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 121: the library caches every vector it sees", "keyboard"),
        "bssor 121: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 121: the library caches every vector it sees", "AA"),
        "round 121: the library caches every vector it sees",
    ),
    (("round 121: agents argue then the debate resolves", "key"), "bssxh 121: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 121: agents argue then the debate resolves", "lemon"), "csgbq 121: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 121: agents argue then the debate resolves", "a"), "round 121: agents argue then the debate resolves"),
    (("round 121: agents argue then the debate resolves", "zz"), "qntmc 121: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 121: agents argue then the debate resolves", "AgentU"),
        "ruyaw 121: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 121: agents argue then the debate resolves", "keyboard"),
        "bssor 121: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 121: agents argue then the debate resolves", "AA"), "round 121: agents argue then the debate resolves"),
    (("round 121: the filter keeps only strong matches", "key"), "bssxh 121: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 121: the filter keeps only strong matches", "lemon"), "csgbq 121: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 121: the filter keeps only strong matches", "a"), "round 121: the filter keeps only strong matches"),
    (("round 121: the filter keeps only strong matches", "zz"), "qntmc 121: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 121: the filter keeps only strong matches", "AgentU"), "ruyaw 121: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 121: the filter keeps only strong matches", "keyboard"),
        "bssor 121: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 121: the filter keeps only strong matches", "AA"), "round 121: the filter keeps only strong matches"),
    (("round 121: the model answers with a short reply", "key"), "bssxh 121: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 121: the model answers with a short reply", "lemon"), "csgbq 121: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 121: the model answers with a short reply", "a"), "round 121: the model answers with a short reply"),
    (("round 121: the model answers with a short reply", "zz"), "qntmc 121: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 121: the model answers with a short reply", "AgentU"), "ruyaw 121: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 121: the model answers with a short reply", "keyboard"),
        "bssor 121: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 121: the model answers with a short reply", "AA"), "round 121: the model answers with a short reply"),
    (
        ("round 121: the recorder stores the reasoning trace", "key"),
        "bssxh 121: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 121: the recorder stores the reasoning trace", "lemon"),
        "csgbq 121: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 121: the recorder stores the reasoning trace", "a"), "round 121: the recorder stores the reasoning trace"),
    (
        ("round 121: the recorder stores the reasoning trace", "zz"),
        "qntmc 121: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 121: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 121: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 121: the recorder stores the reasoning trace", "keyboard"),
        "bssor 121: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 121: the recorder stores the reasoning trace", "AA"),
        "round 121: the recorder stores the reasoning trace",
    ),
    (("round 121: the angel watches the processor run", "key"), "bssxh 121: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 121: the angel watches the processor run", "lemon"), "csgbq 121: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 121: the angel watches the processor run", "a"), "round 121: the angel watches the processor run"),
    (("round 121: the angel watches the processor run", "zz"), "qntmc 121: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 121: the angel watches the processor run", "AgentU"), "ruyaw 121: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 121: the angel watches the processor run", "keyboard"), "bssor 121: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 121: the angel watches the processor run", "AA"), "round 121: the angel watches the processor run"),
    (("round 121: angle of the vector decides the match", "key"), "bssxh 121: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 121: angle of the vector decides the match", "lemon"), "csgbq 121: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 121: angle of the vector decides the match", "a"), "round 121: angle of the vector decides the match"),
    (("round 121: angle of the vector decides the match", "zz"), "qntmc 121: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 121: angle of the vector decides the match", "AgentU"),
        "ruyaw 121: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 121: angle of the vector decides the match", "keyboard"),
        "bssor 121: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 121: angle of the vector decides the match", "AA"), "round 121: angle of the vector decides the match"),
    (
        ("round 121: the candle burns twice as long at night", "key"),
        "bssxh 121: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 121: the candle burns twice as long at night", "lemon"),
        "csgbq 121: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 121: the candle burns twice as long at night", "a"), "round 121: the candle burns twice as long at night"),
    (
        ("round 121: the candle burns twice as long at night", "zz"),
        "qntmc 121: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 121: the candle burns twice as long at night", "AgentU"),
        "ruyaw 121: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 121: the candle burns twice as long at night", "keyboard"),
        "bssor 121: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 121: the candle burns twice as long at night", "AA"),
        "round 121: the candle burns twice as long at night",
    ),
    (("round 121: a mirror of the universe in one line", "key"), "bssxh 121: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 121: a mirror of the universe in one line", "lemon"), "csgbq 121: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 121: a mirror of the universe in one line", "a"), "round 121: a mirror of the universe in one line"),
    (("round 121: a mirror of the universe in one line", "zz"), "qntmc 121: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 121: a mirror of the universe in one line", "AgentU"), "ruyaw 121: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 121: a mirror of the universe in one line", "keyboard"),
        "bssor 121: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 121: a mirror of the universe in one line", "AA"), "round 121: a mirror of the universe in one line"),
    (("round 121: the queue drains before the storm", "key"), "bssxh 121: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 121: the queue drains before the storm", "lemon"), "csgbq 121: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 121: the queue drains before the storm", "a"), "round 121: the queue drains before the storm"),
    (("round 121: the queue drains before the storm", "zz"), "qntmc 121: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 121: the queue drains before the storm", "AgentU"), "ruyaw 121: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 121: the queue drains before the storm", "keyboard"), "bssor 121: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 121: the queue drains before the storm", "AA"), "round 121: the queue drains before the storm"),
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
