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
    (("kitten184", "key"), "umrdil184"),
    (("kitten184", "lemon"), "vmfhry184"),
    (("kitten184", "a"), "kitten184"),
    (("kitten184", "zz"), "jhssdm184"),
    (("kitten184", "AgentU"), "koxgxh184"),
    (("kitten184", "keyboard"), "umrusn184"),
    (("kitten184", "AA"), "kitten184"),
    (("sitting184", "key"), "cmrdmlq184"),
    (("sitting184", "lemon"), "dmfhvyk184"),
    (("sitting184", "a"), "sitting184"),
    (("sitting184", "zz"), "rhsshmf184"),
    (("sitting184", "AgentU"), "soxgbhg184"),
    (("sitting184", "keyboard"), "cmruwnx184"),
    (("sitting184", "AA"), "sitting184"),
    (("agent184", "key"), "kkcxx184"),
    (("agent184", "lemon"), "lkqbg184"),
    (("agent184", "a"), "agent184"),
    (("agent184", "zz"), "zfdms184"),
    (("agent184", "AgentU"), "amiam184"),
    (("agent184", "keyboard"), "kkcoh184"),
    (("agent184", "AA"), "agent184"),
    (("angle184", "key"), "krevi184"),
    (("angle184", "lemon"), "lrszr184"),
    (("angle184", "a"), "angle184"),
    (("angle184", "zz"), "zmfkd184"),
    (("angle184", "AgentU"), "atkyx184"),
    (("angle184", "keyboard"), "krems184"),
    (("angle184", "AA"), "angle184"),
    (("universe184", "key"), "ergfipci184"),
    (("universe184", "lemon"), "frujrcwq184"),
    (("universe184", "a"), "universe184"),
    (("universe184", "zz"), "tmhudqrd184"),
    (("universe184", "AgentU"), "utmixlsk184"),
    (("universe184", "keyboard"), "ergwsrjh184"),
    (("universe184", "AA"), "universe184"),
    (("memory184", "key"), "wikyvw184"),
    (("memory184", "lemon"), "xiycej184"),
    (("memory184", "a"), "memory184"),
    (("memory184", "zz"), "ldlnqx184"),
    (("memory184", "AgentU"), "mkqbks184"),
    (("memory184", "keyboard"), "wikpfy184"),
    (("memory184", "AA"), "memory184"),
    (("stream184", "key"), "cxpoek184"),
    (("stream184", "lemon"), "dxdsnx184"),
    (("stream184", "a"), "stream184"),
    (("stream184", "zz"), "rsqdzl184"),
    (("stream184", "AgentU"), "szvrtg184"),
    (("stream184", "keyboard"), "cxpfom184"),
    (("stream184", "AA"), "stream184"),
    (("context184", "key"), "msldivd184"),
    (("context184", "lemon"), "nszhrix184"),
    (("context184", "a"), "context184"),
    (("context184", "zz"), "bnmsdws184"),
    (("context184", "AgentU"), "curgxrt184"),
    (("context184", "keyboard"), "mslusxk184"),
    (("context184", "AA"), "context184"),
    (("knowledge184", "key"), "urmgpcnkc184"),
    (("knowledge184", "lemon"), "vrakyphss184"),
    (("knowledge184", "a"), "knowledge184"),
    (("knowledge184", "zz"), "jmnvkdcfd184"),
    (("knowledge184", "AgentU"), "ktsjeydmi184"),
    (("knowledge184", "keyboard"), "urmxzeujo184"),
    (("knowledge184", "AA"), "knowledge184"),
    (("vector184", "key"), "fiadsp184"),
    (("vector184", "lemon"), "giohbc184"),
    (("vector184", "a"), "vector184"),
    (("vector184", "zz"), "udbsnq184"),
    (("vector184", "AgentU"), "vkgghl184"),
    (("vector184", "keyboard"), "fiaucr184"),
    (("vector184", "AA"), "vector184"),
    (("processor184", "key"), "zvmmiqcsp184"),
    (("processor184", "lemon"), "avaqrdwaf184"),
    (("processor184", "a"), "processor184"),
    (("processor184", "zz"), "oqnbdrrnq184"),
    (("processor184", "AgentU"), "pxspxmsuv184"),
    (("processor184", "keyboard"), "zvmdssjrb184"),
    (("processor184", "AA"), "processor184"),
    (("reasoning184", "key"), "biycslsre184"),
    (("reasoning184", "lemon"), "cimgbymzu184"),
    (("reasoning184", "a"), "reasoning184"),
    (("reasoning184", "zz"), "qdzrnmhmf184"),
    (("reasoning184", "AgentU"), "rkefhhitk184"),
    (("reasoning184", "keyboard"), "biytcnzqq184"),
    (("reasoning184", "AA"), "reasoning184"),
    (("machine184", "key"), "wearmlo184"),
    (("machine184", "lemon"), "xeovvyi184"),
    (("machine184", "a"), "machine184"),
    (("machine184", "zz"), "lzbghmd184"),
    (("machine184", "AgentU"), "mggubhe184"),
    (("machine184", "keyboard"), "weaiwnv184"),
    (("machine184", "AA"), "machine184"),
    (("learning184", "key"), "viybrgxk184"),
    (("learning184", "lemon"), "wimfatrs184"),
    (("learning184", "a"), "learning184"),
    (("learning184", "zz"), "kdzqmhmf184"),
    (("learning184", "AgentU"), "lkeegcnm184"),
    (("learning184", "keyboard"), "viysbiej184"),
    (("learning184", "AA"), "learning184"),
    (("model184", "key"), "wsbop184"),
    (("model184", "lemon"), "xspsy184"),
    (("model184", "a"), "model184"),
    (("model184", "zz"), "lncdk184"),
    (("model184", "AgentU"), "muhre184"),
    (("model184", "keyboard"), "wsbfz184"),
    (("model184", "AA"), "model184"),
    (("token184", "key"), "dsior184"),
    (("token184", "lemon"), "eswsa184"),
    (("token184", "a"), "token184"),
    (("token184", "zz"), "snjdm184"),
    (("token184", "AgentU"), "tuorg184"),
    (("token184", "keyboard"), "dsifb184"),
    (("token184", "AA"), "token184"),
    (("prompt184", "key"), "zvmwtr184"),
    (("prompt184", "lemon"), "avaace184"),
    (("prompt184", "a"), "prompt184"),
    (("prompt184", "zz"), "oqnlos184"),
    (("prompt184", "AgentU"), "pxszin184"),
    (("prompt184", "keyboard"), "zvmndt184"),
    (("prompt184", "AA"), "prompt184"),
    (("session184", "key"), "ciqcmmx184"),
    (("session184", "lemon"), "diegvzr184"),
    (("session184", "a"), "session184"),
    (("session184", "zz"), "rdrrhnm184"),
    (("session184", "AgentU"), "skwfbin184"),
    (("session184", "keyboard"), "ciqtwoe184"),
    (("session184", "AA"), "session184"),
    (("library184", "key"), "vmzbepi184"),
    (("library184", "lemon"), "wmnfncc184"),
    (("library184", "a"), "library184"),
    (("library184", "zz"), "khaqzqx184"),
    (("library184", "AgentU"), "lofetly184"),
    (("library184", "keyboard"), "vmzsorp184"),
    (("library184", "AA"), "library184"),
    (("service184", "key"), "cipfmao184"),
    (("service184", "lemon"), "didjvni184"),
    (("service184", "a"), "service184"),
    (("service184", "zz"), "rdquhbd184"),
    (("service184", "AgentU"), "skvibwe184"),
    (("service184", "keyboard"), "cipwwcv184"),
    (("service184", "AA"), "service184"),
    (("gateway184", "key"), "qeroayi184"),
    (("gateway184", "lemon"), "refsjlc184"),
    (("gateway184", "a"), "gateway184"),
    (("gateway184", "zz"), "fzsdvzx184"),
    (("gateway184", "AgentU"), "ggxrpuy184"),
    (("gateway184", "keyboard"), "qerfkap184"),
    (("gateway184", "AA"), "gateway184"),
    (("storage184", "key"), "cxmbeeo184"),
    (("storage184", "lemon"), "dxafnri184"),
    (("storage184", "a"), "storage184"),
    (("storage184", "zz"), "rsnqzfd184"),
    (("storage184", "AgentU"), "szsetae184"),
    (("storage184", "keyboard"), "cxmsogv184"),
    (("storage184", "AA"), "storage184"),
    (("network184", "key"), "xirgspu184"),
    (("network184", "lemon"), "yifkbco184"),
    (("network184", "a"), "network184"),
    (("network184", "zz"), "mdsvnqj184"),
    (("network184", "AgentU"), "nkxjhlk184"),
    (("network184", "keyboard"), "xirxcrb184"),
    (("network184", "AA"), "network184"),
    (("latency184", "key"), "verorai184"),
    (("latency184", "lemon"), "wefsanc184"),
    (("latency184", "a"), "latency184"),
    (("latency184", "zz"), "kzsdmbx184"),
    (("latency184", "AgentU"), "lgxrgwy184"),
    (("latency184", "keyboard"), "verfbcp184"),
    (("latency184", "AA"), "latency184"),
    (("buffer184", "key"), "lydpip184"),
    (("buffer184", "lemon"), "myrtrc184"),
    (("buffer184", "a"), "buffer184"),
    (("buffer184", "zz"), "ateedq184"),
    (("buffer184", "AgentU"), "bajsxl184"),
    (("buffer184", "keyboard"), "lydgsr184"),
    (("buffer184", "AA"), "buffer184"),
    (("queue184", "key"), "aycei184"),
    (("queue184", "lemon"), "byqir184"),
    (("queue184", "a"), "queue184"),
    (("queue184", "zz"), "ptdtd184"),
    (("queue184", "AgentU"), "qaihx184"),
    (("queue184", "keyboard"), "aycvs184"),
    (("queue184", "AA"), "queue184"),
    (("worker184", "key"), "gspuip184"),
    (("worker184", "lemon"), "hsdyrc184"),
    (("worker184", "a"), "worker184"),
    (("worker184", "zz"), "vnqjdq184"),
    (("worker184", "AgentU"), "wuvxxl184"),
    (("worker184", "keyboard"), "gsplsr184"),
    (("worker184", "AA"), "worker184"),
    (("kernel184", "key"), "uipxij184"),
    (("kernel184", "lemon"), "vidbrw184"),
    (("kernel184", "a"), "kernel184"),
    (("kernel184", "zz"), "jdqmdk184"),
    (("kernel184", "AgentU"), "kkvaxf184"),
    (("kernel184", "keyboard"), "uiposl184"),
    (("kernel184", "AA"), "kernel184"),
    (("signal184", "key"), "cmexej184"),
    (("signal184", "lemon"), "dmsbnw184"),
    (("signal184", "a"), "signal184"),
    (("signal184", "zz"), "rhfmzk184"),
    (("signal184", "AgentU"), "sokatf184"),
    (("signal184", "keyboard"), "cmeool184"),
    (("signal184", "AA"), "signal184"),
    (("packet184", "key"), "zeauir184"),
    (("packet184", "lemon"), "aeoyre184"),
    (("packet184", "a"), "packet184"),
    (("packet184", "zz"), "ozbjds184"),
    (("packet184", "AgentU"), "pggxxn184"),
    (("packet184", "keyboard"), "zealst184"),
    (("packet184", "AA"), "packet184"),
    (("router184", "key"), "bssdip184"),
    (("router184", "lemon"), "csghrc184"),
    (("router184", "a"), "router184"),
    (("router184", "zz"), "qntsdq184"),
    (("router184", "AgentU"), "ruygxl184"),
    (("router184", "keyboard"), "bssusr184"),
    (("router184", "AA"), "router184"),
    (("cluster184", "key"), "mpscxcb184"),
    (("cluster184", "lemon"), "npgggpv184"),
    (("cluster184", "a"), "cluster184"),
    (("cluster184", "zz"), "bktrsdq184"),
    (("cluster184", "AgentU"), "cryfmyr184"),
    (("cluster184", "keyboard"), "mpsthei184"),
    (("cluster184", "AA"), "cluster184"),
    (("mirror184", "key"), "wmpbsp184"),
    (("mirror184", "lemon"), "xmdfbc184"),
    (("mirror184", "a"), "mirror184"),
    (("mirror184", "zz"), "lhqqnq184"),
    (("mirror184", "AgentU"), "movehl184"),
    (("mirror184", "keyboard"), "wmpscr184"),
    (("mirror184", "AA"), "mirror184"),
    (("filter184", "key"), "pmjdip184"),
    (("filter184", "lemon"), "qmxhrc184"),
    (("filter184", "a"), "filter184"),
    (("filter184", "zz"), "ehksdq184"),
    (("filter184", "AgentU"), "fopgxl184"),
    (("filter184", "keyboard"), "pmjusr184"),
    (("filter184", "AA"), "filter184"),
    (("ranking184", "key"), "belumlq184"),
    (("ranking184", "lemon"), "cezyvyk184"),
    (("ranking184", "a"), "ranking184"),
    (("ranking184", "zz"), "qzmjhmf184"),
    (("ranking184", "AgentU"), "rgrxbhg184"),
    (("ranking184", "keyboard"), "bellwnx184"),
    (("ranking184", "AA"), "ranking184"),
    (("encoding184", "key"), "orayhgxk184"),
    (("encoding184", "lemon"), "procqtrs184"),
    (("encoding184", "a"), "encoding184"),
    (("encoding184", "zz"), "dmbnchmf184"),
    (("encoding184", "AgentU"), "etgbwcnm184"),
    (("encoding184", "keyboard"), "orapriej184"),
    (("encoding184", "AA"), "encoding184"),
    (("mapping184", "key"), "wenzmlq184"),
    (("mapping184", "lemon"), "xebdvyk184"),
    (("mapping184", "a"), "mapping184"),
    (("mapping184", "zz"), "lzoohmf184"),
    (("mapping184", "AgentU"), "mgtcbhg184"),
    (("mapping184", "keyboard"), "wenqwnx184"),
    (("mapping184", "AA"), "mapping184"),
    (("record184", "key"), "biayvb184"),
    (("record184", "lemon"), "cioceo184"),
    (("record184", "a"), "record184"),
    (("record184", "zz"), "qdbnqc184"),
    (("record184", "AgentU"), "rkgbkx184"),
    (("record184", "keyboard"), "biapfd184"),
    (("record184", "AA"), "record184"),
    (("candle184", "key"), "melnpc184"),
    (("candle184", "lemon"), "nezryp184"),
    (("candle184", "a"), "candle184"),
    (("candle184", "zz"), "bzmckd184"),
    (("candle184", "AgentU"), "cgrqey184"),
    (("candle184", "keyboard"), "meleze184"),
    (("candle184", "AA"), "candle184"),
    (("thread184", "key"), "dlpoeb184"),
    (("thread184", "lemon"), "eldsno184"),
    (("thread184", "a"), "thread184"),
    (("thread184", "zz"), "sgqdzc184"),
    (("thread184", "AgentU"), "tnvrtx184"),
    (("thread184", "keyboard"), "dlpfod184"),
    (("thread184", "AA"), "thread184"),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 184: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 184: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "a"),
        "round 184: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 184: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 184: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 184: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", "AA"),
        "round 184: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "key"),
        "bssxh 184: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 184: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "a"),
        "round 184: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 184: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 184: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 184: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", "AA"),
        "round 184: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 184: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 184: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "a"),
        "round 184: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 184: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 184: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 184: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", "AA"),
        "round 184: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 184: the processor reads the record then stops", "key"),
        "bssxh 184: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 184: the processor reads the record then stops", "lemon"),
        "csgbq 184: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 184: the processor reads the record then stops", "a"),
        "round 184: the processor reads the record then stops",
    ),
    (
        ("round 184: the processor reads the record then stops", "zz"),
        "qntmc 184: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 184: the processor reads the record then stops", "AgentU"),
        "ruyaw 184: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 184: the processor reads the record then stops", "keyboard"),
        "bssor 184: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 184: the processor reads the record then stops", "AA"),
        "round 184: the processor reads the record then stops",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "key"),
        "bssxh 184: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "lemon"),
        "csgbq 184: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "a"),
        "round 184: a worker pulls the next task from the queue",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "zz"),
        "qntmc 184: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 184: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "keyboard"),
        "bssor 184: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 184: a worker pulls the next task from the queue", "AA"),
        "round 184: a worker pulls the next task from the queue",
    ),
    (
        ("round 184: signals travel through the network layer", "key"),
        "bssxh 184: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 184: signals travel through the network layer", "lemon"),
        "csgbq 184: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 184: signals travel through the network layer", "a"),
        "round 184: signals travel through the network layer",
    ),
    (
        ("round 184: signals travel through the network layer", "zz"),
        "qntmc 184: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 184: signals travel through the network layer", "AgentU"),
        "ruyaw 184: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 184: signals travel through the network layer", "keyboard"),
        "bssor 184: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 184: signals travel through the network layer", "AA"),
        "round 184: signals travel through the network layer",
    ),
    (
        ("round 184: the gateway routes each request by policy", "key"),
        "bssxh 184: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 184: the gateway routes each request by policy", "lemon"),
        "csgbq 184: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 184: the gateway routes each request by policy", "a"),
        "round 184: the gateway routes each request by policy",
    ),
    (
        ("round 184: the gateway routes each request by policy", "zz"),
        "qntmc 184: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 184: the gateway routes each request by policy", "AgentU"),
        "ruyaw 184: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 184: the gateway routes each request by policy", "keyboard"),
        "bssor 184: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 184: the gateway routes each request by policy", "AA"),
        "round 184: the gateway routes each request by policy",
    ),
    (("round 184: memory grows until the buffer is full", "key"), "bssxh 184: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 184: memory grows until the buffer is full", "lemon"), "csgbq 184: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 184: memory grows until the buffer is full", "a"), "round 184: memory grows until the buffer is full"),
    (("round 184: memory grows until the buffer is full", "zz"), "qntmc 184: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 184: memory grows until the buffer is full", "AgentU"),
        "ruyaw 184: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 184: memory grows until the buffer is full", "keyboard"),
        "bssor 184: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 184: memory grows until the buffer is full", "AA"), "round 184: memory grows until the buffer is full"),
    (("round 184: the cluster mirrors every packet twice", "key"), "bssxh 184: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 184: the cluster mirrors every packet twice", "lemon"),
        "csgbq 184: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 184: the cluster mirrors every packet twice", "a"), "round 184: the cluster mirrors every packet twice"),
    (("round 184: the cluster mirrors every packet twice", "zz"), "qntmc 184: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 184: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 184: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 184: the cluster mirrors every packet twice", "keyboard"),
        "bssor 184: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 184: the cluster mirrors every packet twice", "AA"), "round 184: the cluster mirrors every packet twice"),
    (
        ("round 184: ranking uses tokens learned from the corpus", "key"),
        "bssxh 184: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 184: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", "a"),
        "round 184: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 184: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 184: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 184: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", "AA"),
        "round 184: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 184: a long session ends when the candle dies", "key"),
        "bssxh 184: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 184: a long session ends when the candle dies", "lemon"),
        "csgbq 184: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 184: a long session ends when the candle dies", "a"),
        "round 184: a long session ends when the candle dies",
    ),
    (
        ("round 184: a long session ends when the candle dies", "zz"),
        "qntmc 184: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 184: a long session ends when the candle dies", "AgentU"),
        "ruyaw 184: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 184: a long session ends when the candle dies", "keyboard"),
        "bssor 184: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 184: a long session ends when the candle dies", "AA"),
        "round 184: a long session ends when the candle dies",
    ),
    (("round 184: encode the prompt then map the result", "key"), "bssxh 184: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 184: encode the prompt then map the result", "lemon"), "csgbq 184: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 184: encode the prompt then map the result", "a"), "round 184: encode the prompt then map the result"),
    (("round 184: encode the prompt then map the result", "zz"), "qntmc 184: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 184: encode the prompt then map the result", "AgentU"),
        "ruyaw 184: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 184: encode the prompt then map the result", "keyboard"),
        "bssor 184: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 184: encode the prompt then map the result", "AA"), "round 184: encode the prompt then map the result"),
    (("round 184: the kernel wakes the worker at dawn", "key"), "bssxh 184: rri iovlop ukocc xfo ambocb er neux"),
    (("round 184: the kernel wakes the worker at dawn", "lemon"), "csgbq 184: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 184: the kernel wakes the worker at dawn", "a"), "round 184: the kernel wakes the worker at dawn"),
    (("round 184: the kernel wakes the worker at dawn", "zz"), "qntmc 184: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 184: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 184: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 184: the kernel wakes the worker at dawn", "keyboard"), "bssor 184: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 184: the kernel wakes the worker at dawn", "AA"), "round 184: the kernel wakes the worker at dawn"),
    (("round 184: service latency drops after the patch", "key"), "bssxh 184: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 184: service latency drops after the patch", "lemon"), "csgbq 184: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 184: service latency drops after the patch", "a"), "round 184: service latency drops after the patch"),
    (("round 184: service latency drops after the patch", "zz"), "qntmc 184: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 184: service latency drops after the patch", "AgentU"),
        "ruyaw 184: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 184: service latency drops after the patch", "keyboard"),
        "bssor 184: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 184: service latency drops after the patch", "AA"), "round 184: service latency drops after the patch"),
    (
        ("round 184: the library caches every vector it sees", "key"),
        "bssxh 184: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 184: the library caches every vector it sees", "lemon"),
        "csgbq 184: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 184: the library caches every vector it sees", "a"), "round 184: the library caches every vector it sees"),
    (
        ("round 184: the library caches every vector it sees", "zz"),
        "qntmc 184: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 184: the library caches every vector it sees", "AgentU"),
        "ruyaw 184: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 184: the library caches every vector it sees", "keyboard"),
        "bssor 184: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 184: the library caches every vector it sees", "AA"),
        "round 184: the library caches every vector it sees",
    ),
    (("round 184: agents argue then the debate resolves", "key"), "bssxh 184: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 184: agents argue then the debate resolves", "lemon"), "csgbq 184: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 184: agents argue then the debate resolves", "a"), "round 184: agents argue then the debate resolves"),
    (("round 184: agents argue then the debate resolves", "zz"), "qntmc 184: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 184: agents argue then the debate resolves", "AgentU"),
        "ruyaw 184: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 184: agents argue then the debate resolves", "keyboard"),
        "bssor 184: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 184: agents argue then the debate resolves", "AA"), "round 184: agents argue then the debate resolves"),
    (("round 184: the filter keeps only strong matches", "key"), "bssxh 184: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 184: the filter keeps only strong matches", "lemon"), "csgbq 184: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 184: the filter keeps only strong matches", "a"), "round 184: the filter keeps only strong matches"),
    (("round 184: the filter keeps only strong matches", "zz"), "qntmc 184: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 184: the filter keeps only strong matches", "AgentU"), "ruyaw 184: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 184: the filter keeps only strong matches", "keyboard"),
        "bssor 184: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 184: the filter keeps only strong matches", "AA"), "round 184: the filter keeps only strong matches"),
    (("round 184: the model answers with a short reply", "key"), "bssxh 184: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 184: the model answers with a short reply", "lemon"), "csgbq 184: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 184: the model answers with a short reply", "a"), "round 184: the model answers with a short reply"),
    (("round 184: the model answers with a short reply", "zz"), "qntmc 184: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 184: the model answers with a short reply", "AgentU"), "ruyaw 184: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 184: the model answers with a short reply", "keyboard"),
        "bssor 184: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 184: the model answers with a short reply", "AA"), "round 184: the model answers with a short reply"),
    (
        ("round 184: the recorder stores the reasoning trace", "key"),
        "bssxh 184: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 184: the recorder stores the reasoning trace", "lemon"),
        "csgbq 184: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 184: the recorder stores the reasoning trace", "a"), "round 184: the recorder stores the reasoning trace"),
    (
        ("round 184: the recorder stores the reasoning trace", "zz"),
        "qntmc 184: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 184: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 184: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 184: the recorder stores the reasoning trace", "keyboard"),
        "bssor 184: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 184: the recorder stores the reasoning trace", "AA"),
        "round 184: the recorder stores the reasoning trace",
    ),
    (("round 184: the angel watches the processor run", "key"), "bssxh 184: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 184: the angel watches the processor run", "lemon"), "csgbq 184: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 184: the angel watches the processor run", "a"), "round 184: the angel watches the processor run"),
    (("round 184: the angel watches the processor run", "zz"), "qntmc 184: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 184: the angel watches the processor run", "AgentU"), "ruyaw 184: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 184: the angel watches the processor run", "keyboard"), "bssor 184: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 184: the angel watches the processor run", "AA"), "round 184: the angel watches the processor run"),
    (("round 184: angle of the vector decides the match", "key"), "bssxh 184: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 184: angle of the vector decides the match", "lemon"), "csgbq 184: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 184: angle of the vector decides the match", "a"), "round 184: angle of the vector decides the match"),
    (("round 184: angle of the vector decides the match", "zz"), "qntmc 184: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 184: angle of the vector decides the match", "AgentU"),
        "ruyaw 184: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 184: angle of the vector decides the match", "keyboard"),
        "bssor 184: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 184: angle of the vector decides the match", "AA"), "round 184: angle of the vector decides the match"),
    (
        ("round 184: the candle burns twice as long at night", "key"),
        "bssxh 184: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 184: the candle burns twice as long at night", "lemon"),
        "csgbq 184: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 184: the candle burns twice as long at night", "a"), "round 184: the candle burns twice as long at night"),
    (
        ("round 184: the candle burns twice as long at night", "zz"),
        "qntmc 184: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 184: the candle burns twice as long at night", "AgentU"),
        "ruyaw 184: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 184: the candle burns twice as long at night", "keyboard"),
        "bssor 184: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 184: the candle burns twice as long at night", "AA"),
        "round 184: the candle burns twice as long at night",
    ),
    (("round 184: a mirror of the universe in one line", "key"), "bssxh 184: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 184: a mirror of the universe in one line", "lemon"), "csgbq 184: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 184: a mirror of the universe in one line", "a"), "round 184: a mirror of the universe in one line"),
    (("round 184: a mirror of the universe in one line", "zz"), "qntmc 184: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 184: a mirror of the universe in one line", "AgentU"), "ruyaw 184: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 184: a mirror of the universe in one line", "keyboard"),
        "bssor 184: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 184: a mirror of the universe in one line", "AA"), "round 184: a mirror of the universe in one line"),
    (("round 184: the queue drains before the storm", "key"), "bssxh 184: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 184: the queue drains before the storm", "lemon"), "csgbq 184: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 184: the queue drains before the storm", "a"), "round 184: the queue drains before the storm"),
    (("round 184: the queue drains before the storm", "zz"), "qntmc 184: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 184: the queue drains before the storm", "AgentU"), "ruyaw 184: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 184: the queue drains before the storm", "keyboard"), "bssor 184: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 184: the queue drains before the storm", "AA"), "round 184: the queue drains before the storm"),
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
