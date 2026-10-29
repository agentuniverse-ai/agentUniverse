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
    (("kitten116", "key"), "umrdil116"),
    (("kitten116", "lemon"), "vmfhry116"),
    (("kitten116", "a"), "kitten116"),
    (("kitten116", "zz"), "jhssdm116"),
    (("kitten116", "AgentU"), "koxgxh116"),
    (("kitten116", "keyboard"), "umrusn116"),
    (("kitten116", "AA"), "kitten116"),
    (("sitting116", "key"), "cmrdmlq116"),
    (("sitting116", "lemon"), "dmfhvyk116"),
    (("sitting116", "a"), "sitting116"),
    (("sitting116", "zz"), "rhsshmf116"),
    (("sitting116", "AgentU"), "soxgbhg116"),
    (("sitting116", "keyboard"), "cmruwnx116"),
    (("sitting116", "AA"), "sitting116"),
    (("agent116", "key"), "kkcxx116"),
    (("agent116", "lemon"), "lkqbg116"),
    (("agent116", "a"), "agent116"),
    (("agent116", "zz"), "zfdms116"),
    (("agent116", "AgentU"), "amiam116"),
    (("agent116", "keyboard"), "kkcoh116"),
    (("agent116", "AA"), "agent116"),
    (("angle116", "key"), "krevi116"),
    (("angle116", "lemon"), "lrszr116"),
    (("angle116", "a"), "angle116"),
    (("angle116", "zz"), "zmfkd116"),
    (("angle116", "AgentU"), "atkyx116"),
    (("angle116", "keyboard"), "krems116"),
    (("angle116", "AA"), "angle116"),
    (("universe116", "key"), "ergfipci116"),
    (("universe116", "lemon"), "frujrcwq116"),
    (("universe116", "a"), "universe116"),
    (("universe116", "zz"), "tmhudqrd116"),
    (("universe116", "AgentU"), "utmixlsk116"),
    (("universe116", "keyboard"), "ergwsrjh116"),
    (("universe116", "AA"), "universe116"),
    (("memory116", "key"), "wikyvw116"),
    (("memory116", "lemon"), "xiycej116"),
    (("memory116", "a"), "memory116"),
    (("memory116", "zz"), "ldlnqx116"),
    (("memory116", "AgentU"), "mkqbks116"),
    (("memory116", "keyboard"), "wikpfy116"),
    (("memory116", "AA"), "memory116"),
    (("stream116", "key"), "cxpoek116"),
    (("stream116", "lemon"), "dxdsnx116"),
    (("stream116", "a"), "stream116"),
    (("stream116", "zz"), "rsqdzl116"),
    (("stream116", "AgentU"), "szvrtg116"),
    (("stream116", "keyboard"), "cxpfom116"),
    (("stream116", "AA"), "stream116"),
    (("context116", "key"), "msldivd116"),
    (("context116", "lemon"), "nszhrix116"),
    (("context116", "a"), "context116"),
    (("context116", "zz"), "bnmsdws116"),
    (("context116", "AgentU"), "curgxrt116"),
    (("context116", "keyboard"), "mslusxk116"),
    (("context116", "AA"), "context116"),
    (("knowledge116", "key"), "urmgpcnkc116"),
    (("knowledge116", "lemon"), "vrakyphss116"),
    (("knowledge116", "a"), "knowledge116"),
    (("knowledge116", "zz"), "jmnvkdcfd116"),
    (("knowledge116", "AgentU"), "ktsjeydmi116"),
    (("knowledge116", "keyboard"), "urmxzeujo116"),
    (("knowledge116", "AA"), "knowledge116"),
    (("vector116", "key"), "fiadsp116"),
    (("vector116", "lemon"), "giohbc116"),
    (("vector116", "a"), "vector116"),
    (("vector116", "zz"), "udbsnq116"),
    (("vector116", "AgentU"), "vkgghl116"),
    (("vector116", "keyboard"), "fiaucr116"),
    (("vector116", "AA"), "vector116"),
    (("processor116", "key"), "zvmmiqcsp116"),
    (("processor116", "lemon"), "avaqrdwaf116"),
    (("processor116", "a"), "processor116"),
    (("processor116", "zz"), "oqnbdrrnq116"),
    (("processor116", "AgentU"), "pxspxmsuv116"),
    (("processor116", "keyboard"), "zvmdssjrb116"),
    (("processor116", "AA"), "processor116"),
    (("reasoning116", "key"), "biycslsre116"),
    (("reasoning116", "lemon"), "cimgbymzu116"),
    (("reasoning116", "a"), "reasoning116"),
    (("reasoning116", "zz"), "qdzrnmhmf116"),
    (("reasoning116", "AgentU"), "rkefhhitk116"),
    (("reasoning116", "keyboard"), "biytcnzqq116"),
    (("reasoning116", "AA"), "reasoning116"),
    (("machine116", "key"), "wearmlo116"),
    (("machine116", "lemon"), "xeovvyi116"),
    (("machine116", "a"), "machine116"),
    (("machine116", "zz"), "lzbghmd116"),
    (("machine116", "AgentU"), "mggubhe116"),
    (("machine116", "keyboard"), "weaiwnv116"),
    (("machine116", "AA"), "machine116"),
    (("learning116", "key"), "viybrgxk116"),
    (("learning116", "lemon"), "wimfatrs116"),
    (("learning116", "a"), "learning116"),
    (("learning116", "zz"), "kdzqmhmf116"),
    (("learning116", "AgentU"), "lkeegcnm116"),
    (("learning116", "keyboard"), "viysbiej116"),
    (("learning116", "AA"), "learning116"),
    (("model116", "key"), "wsbop116"),
    (("model116", "lemon"), "xspsy116"),
    (("model116", "a"), "model116"),
    (("model116", "zz"), "lncdk116"),
    (("model116", "AgentU"), "muhre116"),
    (("model116", "keyboard"), "wsbfz116"),
    (("model116", "AA"), "model116"),
    (("token116", "key"), "dsior116"),
    (("token116", "lemon"), "eswsa116"),
    (("token116", "a"), "token116"),
    (("token116", "zz"), "snjdm116"),
    (("token116", "AgentU"), "tuorg116"),
    (("token116", "keyboard"), "dsifb116"),
    (("token116", "AA"), "token116"),
    (("prompt116", "key"), "zvmwtr116"),
    (("prompt116", "lemon"), "avaace116"),
    (("prompt116", "a"), "prompt116"),
    (("prompt116", "zz"), "oqnlos116"),
    (("prompt116", "AgentU"), "pxszin116"),
    (("prompt116", "keyboard"), "zvmndt116"),
    (("prompt116", "AA"), "prompt116"),
    (("session116", "key"), "ciqcmmx116"),
    (("session116", "lemon"), "diegvzr116"),
    (("session116", "a"), "session116"),
    (("session116", "zz"), "rdrrhnm116"),
    (("session116", "AgentU"), "skwfbin116"),
    (("session116", "keyboard"), "ciqtwoe116"),
    (("session116", "AA"), "session116"),
    (("library116", "key"), "vmzbepi116"),
    (("library116", "lemon"), "wmnfncc116"),
    (("library116", "a"), "library116"),
    (("library116", "zz"), "khaqzqx116"),
    (("library116", "AgentU"), "lofetly116"),
    (("library116", "keyboard"), "vmzsorp116"),
    (("library116", "AA"), "library116"),
    (("service116", "key"), "cipfmao116"),
    (("service116", "lemon"), "didjvni116"),
    (("service116", "a"), "service116"),
    (("service116", "zz"), "rdquhbd116"),
    (("service116", "AgentU"), "skvibwe116"),
    (("service116", "keyboard"), "cipwwcv116"),
    (("service116", "AA"), "service116"),
    (("gateway116", "key"), "qeroayi116"),
    (("gateway116", "lemon"), "refsjlc116"),
    (("gateway116", "a"), "gateway116"),
    (("gateway116", "zz"), "fzsdvzx116"),
    (("gateway116", "AgentU"), "ggxrpuy116"),
    (("gateway116", "keyboard"), "qerfkap116"),
    (("gateway116", "AA"), "gateway116"),
    (("storage116", "key"), "cxmbeeo116"),
    (("storage116", "lemon"), "dxafnri116"),
    (("storage116", "a"), "storage116"),
    (("storage116", "zz"), "rsnqzfd116"),
    (("storage116", "AgentU"), "szsetae116"),
    (("storage116", "keyboard"), "cxmsogv116"),
    (("storage116", "AA"), "storage116"),
    (("network116", "key"), "xirgspu116"),
    (("network116", "lemon"), "yifkbco116"),
    (("network116", "a"), "network116"),
    (("network116", "zz"), "mdsvnqj116"),
    (("network116", "AgentU"), "nkxjhlk116"),
    (("network116", "keyboard"), "xirxcrb116"),
    (("network116", "AA"), "network116"),
    (("latency116", "key"), "verorai116"),
    (("latency116", "lemon"), "wefsanc116"),
    (("latency116", "a"), "latency116"),
    (("latency116", "zz"), "kzsdmbx116"),
    (("latency116", "AgentU"), "lgxrgwy116"),
    (("latency116", "keyboard"), "verfbcp116"),
    (("latency116", "AA"), "latency116"),
    (("buffer116", "key"), "lydpip116"),
    (("buffer116", "lemon"), "myrtrc116"),
    (("buffer116", "a"), "buffer116"),
    (("buffer116", "zz"), "ateedq116"),
    (("buffer116", "AgentU"), "bajsxl116"),
    (("buffer116", "keyboard"), "lydgsr116"),
    (("buffer116", "AA"), "buffer116"),
    (("queue116", "key"), "aycei116"),
    (("queue116", "lemon"), "byqir116"),
    (("queue116", "a"), "queue116"),
    (("queue116", "zz"), "ptdtd116"),
    (("queue116", "AgentU"), "qaihx116"),
    (("queue116", "keyboard"), "aycvs116"),
    (("queue116", "AA"), "queue116"),
    (("worker116", "key"), "gspuip116"),
    (("worker116", "lemon"), "hsdyrc116"),
    (("worker116", "a"), "worker116"),
    (("worker116", "zz"), "vnqjdq116"),
    (("worker116", "AgentU"), "wuvxxl116"),
    (("worker116", "keyboard"), "gsplsr116"),
    (("worker116", "AA"), "worker116"),
    (("kernel116", "key"), "uipxij116"),
    (("kernel116", "lemon"), "vidbrw116"),
    (("kernel116", "a"), "kernel116"),
    (("kernel116", "zz"), "jdqmdk116"),
    (("kernel116", "AgentU"), "kkvaxf116"),
    (("kernel116", "keyboard"), "uiposl116"),
    (("kernel116", "AA"), "kernel116"),
    (("signal116", "key"), "cmexej116"),
    (("signal116", "lemon"), "dmsbnw116"),
    (("signal116", "a"), "signal116"),
    (("signal116", "zz"), "rhfmzk116"),
    (("signal116", "AgentU"), "sokatf116"),
    (("signal116", "keyboard"), "cmeool116"),
    (("signal116", "AA"), "signal116"),
    (("packet116", "key"), "zeauir116"),
    (("packet116", "lemon"), "aeoyre116"),
    (("packet116", "a"), "packet116"),
    (("packet116", "zz"), "ozbjds116"),
    (("packet116", "AgentU"), "pggxxn116"),
    (("packet116", "keyboard"), "zealst116"),
    (("packet116", "AA"), "packet116"),
    (("router116", "key"), "bssdip116"),
    (("router116", "lemon"), "csghrc116"),
    (("router116", "a"), "router116"),
    (("router116", "zz"), "qntsdq116"),
    (("router116", "AgentU"), "ruygxl116"),
    (("router116", "keyboard"), "bssusr116"),
    (("router116", "AA"), "router116"),
    (("cluster116", "key"), "mpscxcb116"),
    (("cluster116", "lemon"), "npgggpv116"),
    (("cluster116", "a"), "cluster116"),
    (("cluster116", "zz"), "bktrsdq116"),
    (("cluster116", "AgentU"), "cryfmyr116"),
    (("cluster116", "keyboard"), "mpsthei116"),
    (("cluster116", "AA"), "cluster116"),
    (("mirror116", "key"), "wmpbsp116"),
    (("mirror116", "lemon"), "xmdfbc116"),
    (("mirror116", "a"), "mirror116"),
    (("mirror116", "zz"), "lhqqnq116"),
    (("mirror116", "AgentU"), "movehl116"),
    (("mirror116", "keyboard"), "wmpscr116"),
    (("mirror116", "AA"), "mirror116"),
    (("filter116", "key"), "pmjdip116"),
    (("filter116", "lemon"), "qmxhrc116"),
    (("filter116", "a"), "filter116"),
    (("filter116", "zz"), "ehksdq116"),
    (("filter116", "AgentU"), "fopgxl116"),
    (("filter116", "keyboard"), "pmjusr116"),
    (("filter116", "AA"), "filter116"),
    (("ranking116", "key"), "belumlq116"),
    (("ranking116", "lemon"), "cezyvyk116"),
    (("ranking116", "a"), "ranking116"),
    (("ranking116", "zz"), "qzmjhmf116"),
    (("ranking116", "AgentU"), "rgrxbhg116"),
    (("ranking116", "keyboard"), "bellwnx116"),
    (("ranking116", "AA"), "ranking116"),
    (("encoding116", "key"), "orayhgxk116"),
    (("encoding116", "lemon"), "procqtrs116"),
    (("encoding116", "a"), "encoding116"),
    (("encoding116", "zz"), "dmbnchmf116"),
    (("encoding116", "AgentU"), "etgbwcnm116"),
    (("encoding116", "keyboard"), "orapriej116"),
    (("encoding116", "AA"), "encoding116"),
    (("mapping116", "key"), "wenzmlq116"),
    (("mapping116", "lemon"), "xebdvyk116"),
    (("mapping116", "a"), "mapping116"),
    (("mapping116", "zz"), "lzoohmf116"),
    (("mapping116", "AgentU"), "mgtcbhg116"),
    (("mapping116", "keyboard"), "wenqwnx116"),
    (("mapping116", "AA"), "mapping116"),
    (("record116", "key"), "biayvb116"),
    (("record116", "lemon"), "cioceo116"),
    (("record116", "a"), "record116"),
    (("record116", "zz"), "qdbnqc116"),
    (("record116", "AgentU"), "rkgbkx116"),
    (("record116", "keyboard"), "biapfd116"),
    (("record116", "AA"), "record116"),
    (("candle116", "key"), "melnpc116"),
    (("candle116", "lemon"), "nezryp116"),
    (("candle116", "a"), "candle116"),
    (("candle116", "zz"), "bzmckd116"),
    (("candle116", "AgentU"), "cgrqey116"),
    (("candle116", "keyboard"), "meleze116"),
    (("candle116", "AA"), "candle116"),
    (("thread116", "key"), "dlpoeb116"),
    (("thread116", "lemon"), "eldsno116"),
    (("thread116", "a"), "thread116"),
    (("thread116", "zz"), "sgqdzc116"),
    (("thread116", "AgentU"), "tnvrtx116"),
    (("thread116", "keyboard"), "dlpfod116"),
    (("thread116", "AA"), "thread116"),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 116: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 116: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "a"),
        "round 116: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 116: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 116: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 116: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", "AA"),
        "round 116: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "key"),
        "bssxh 116: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 116: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "a"),
        "round 116: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 116: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 116: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 116: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", "AA"),
        "round 116: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 116: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 116: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "a"),
        "round 116: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 116: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 116: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 116: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", "AA"),
        "round 116: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 116: the processor reads the record then stops", "key"),
        "bssxh 116: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 116: the processor reads the record then stops", "lemon"),
        "csgbq 116: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 116: the processor reads the record then stops", "a"),
        "round 116: the processor reads the record then stops",
    ),
    (
        ("round 116: the processor reads the record then stops", "zz"),
        "qntmc 116: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 116: the processor reads the record then stops", "AgentU"),
        "ruyaw 116: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 116: the processor reads the record then stops", "keyboard"),
        "bssor 116: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 116: the processor reads the record then stops", "AA"),
        "round 116: the processor reads the record then stops",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "key"),
        "bssxh 116: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "lemon"),
        "csgbq 116: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "a"),
        "round 116: a worker pulls the next task from the queue",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "zz"),
        "qntmc 116: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 116: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "keyboard"),
        "bssor 116: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 116: a worker pulls the next task from the queue", "AA"),
        "round 116: a worker pulls the next task from the queue",
    ),
    (
        ("round 116: signals travel through the network layer", "key"),
        "bssxh 116: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 116: signals travel through the network layer", "lemon"),
        "csgbq 116: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 116: signals travel through the network layer", "a"),
        "round 116: signals travel through the network layer",
    ),
    (
        ("round 116: signals travel through the network layer", "zz"),
        "qntmc 116: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 116: signals travel through the network layer", "AgentU"),
        "ruyaw 116: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 116: signals travel through the network layer", "keyboard"),
        "bssor 116: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 116: signals travel through the network layer", "AA"),
        "round 116: signals travel through the network layer",
    ),
    (
        ("round 116: the gateway routes each request by policy", "key"),
        "bssxh 116: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 116: the gateway routes each request by policy", "lemon"),
        "csgbq 116: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 116: the gateway routes each request by policy", "a"),
        "round 116: the gateway routes each request by policy",
    ),
    (
        ("round 116: the gateway routes each request by policy", "zz"),
        "qntmc 116: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 116: the gateway routes each request by policy", "AgentU"),
        "ruyaw 116: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 116: the gateway routes each request by policy", "keyboard"),
        "bssor 116: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 116: the gateway routes each request by policy", "AA"),
        "round 116: the gateway routes each request by policy",
    ),
    (("round 116: memory grows until the buffer is full", "key"), "bssxh 116: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 116: memory grows until the buffer is full", "lemon"), "csgbq 116: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 116: memory grows until the buffer is full", "a"), "round 116: memory grows until the buffer is full"),
    (("round 116: memory grows until the buffer is full", "zz"), "qntmc 116: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 116: memory grows until the buffer is full", "AgentU"),
        "ruyaw 116: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 116: memory grows until the buffer is full", "keyboard"),
        "bssor 116: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 116: memory grows until the buffer is full", "AA"), "round 116: memory grows until the buffer is full"),
    (("round 116: the cluster mirrors every packet twice", "key"), "bssxh 116: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 116: the cluster mirrors every packet twice", "lemon"),
        "csgbq 116: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 116: the cluster mirrors every packet twice", "a"), "round 116: the cluster mirrors every packet twice"),
    (("round 116: the cluster mirrors every packet twice", "zz"), "qntmc 116: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 116: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 116: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 116: the cluster mirrors every packet twice", "keyboard"),
        "bssor 116: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 116: the cluster mirrors every packet twice", "AA"), "round 116: the cluster mirrors every packet twice"),
    (
        ("round 116: ranking uses tokens learned from the corpus", "key"),
        "bssxh 116: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 116: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", "a"),
        "round 116: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 116: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 116: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 116: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", "AA"),
        "round 116: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 116: a long session ends when the candle dies", "key"),
        "bssxh 116: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 116: a long session ends when the candle dies", "lemon"),
        "csgbq 116: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 116: a long session ends when the candle dies", "a"),
        "round 116: a long session ends when the candle dies",
    ),
    (
        ("round 116: a long session ends when the candle dies", "zz"),
        "qntmc 116: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 116: a long session ends when the candle dies", "AgentU"),
        "ruyaw 116: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 116: a long session ends when the candle dies", "keyboard"),
        "bssor 116: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 116: a long session ends when the candle dies", "AA"),
        "round 116: a long session ends when the candle dies",
    ),
    (("round 116: encode the prompt then map the result", "key"), "bssxh 116: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 116: encode the prompt then map the result", "lemon"), "csgbq 116: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 116: encode the prompt then map the result", "a"), "round 116: encode the prompt then map the result"),
    (("round 116: encode the prompt then map the result", "zz"), "qntmc 116: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 116: encode the prompt then map the result", "AgentU"),
        "ruyaw 116: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 116: encode the prompt then map the result", "keyboard"),
        "bssor 116: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 116: encode the prompt then map the result", "AA"), "round 116: encode the prompt then map the result"),
    (("round 116: the kernel wakes the worker at dawn", "key"), "bssxh 116: rri iovlop ukocc xfo ambocb er neux"),
    (("round 116: the kernel wakes the worker at dawn", "lemon"), "csgbq 116: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 116: the kernel wakes the worker at dawn", "a"), "round 116: the kernel wakes the worker at dawn"),
    (("round 116: the kernel wakes the worker at dawn", "zz"), "qntmc 116: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 116: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 116: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 116: the kernel wakes the worker at dawn", "keyboard"), "bssor 116: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 116: the kernel wakes the worker at dawn", "AA"), "round 116: the kernel wakes the worker at dawn"),
    (("round 116: service latency drops after the patch", "key"), "bssxh 116: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 116: service latency drops after the patch", "lemon"), "csgbq 116: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 116: service latency drops after the patch", "a"), "round 116: service latency drops after the patch"),
    (("round 116: service latency drops after the patch", "zz"), "qntmc 116: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 116: service latency drops after the patch", "AgentU"),
        "ruyaw 116: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 116: service latency drops after the patch", "keyboard"),
        "bssor 116: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 116: service latency drops after the patch", "AA"), "round 116: service latency drops after the patch"),
    (
        ("round 116: the library caches every vector it sees", "key"),
        "bssxh 116: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 116: the library caches every vector it sees", "lemon"),
        "csgbq 116: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 116: the library caches every vector it sees", "a"), "round 116: the library caches every vector it sees"),
    (
        ("round 116: the library caches every vector it sees", "zz"),
        "qntmc 116: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 116: the library caches every vector it sees", "AgentU"),
        "ruyaw 116: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 116: the library caches every vector it sees", "keyboard"),
        "bssor 116: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 116: the library caches every vector it sees", "AA"),
        "round 116: the library caches every vector it sees",
    ),
    (("round 116: agents argue then the debate resolves", "key"), "bssxh 116: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 116: agents argue then the debate resolves", "lemon"), "csgbq 116: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 116: agents argue then the debate resolves", "a"), "round 116: agents argue then the debate resolves"),
    (("round 116: agents argue then the debate resolves", "zz"), "qntmc 116: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 116: agents argue then the debate resolves", "AgentU"),
        "ruyaw 116: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 116: agents argue then the debate resolves", "keyboard"),
        "bssor 116: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 116: agents argue then the debate resolves", "AA"), "round 116: agents argue then the debate resolves"),
    (("round 116: the filter keeps only strong matches", "key"), "bssxh 116: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 116: the filter keeps only strong matches", "lemon"), "csgbq 116: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 116: the filter keeps only strong matches", "a"), "round 116: the filter keeps only strong matches"),
    (("round 116: the filter keeps only strong matches", "zz"), "qntmc 116: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 116: the filter keeps only strong matches", "AgentU"), "ruyaw 116: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 116: the filter keeps only strong matches", "keyboard"),
        "bssor 116: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 116: the filter keeps only strong matches", "AA"), "round 116: the filter keeps only strong matches"),
    (("round 116: the model answers with a short reply", "key"), "bssxh 116: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 116: the model answers with a short reply", "lemon"), "csgbq 116: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 116: the model answers with a short reply", "a"), "round 116: the model answers with a short reply"),
    (("round 116: the model answers with a short reply", "zz"), "qntmc 116: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 116: the model answers with a short reply", "AgentU"), "ruyaw 116: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 116: the model answers with a short reply", "keyboard"),
        "bssor 116: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 116: the model answers with a short reply", "AA"), "round 116: the model answers with a short reply"),
    (
        ("round 116: the recorder stores the reasoning trace", "key"),
        "bssxh 116: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 116: the recorder stores the reasoning trace", "lemon"),
        "csgbq 116: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 116: the recorder stores the reasoning trace", "a"), "round 116: the recorder stores the reasoning trace"),
    (
        ("round 116: the recorder stores the reasoning trace", "zz"),
        "qntmc 116: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 116: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 116: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 116: the recorder stores the reasoning trace", "keyboard"),
        "bssor 116: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 116: the recorder stores the reasoning trace", "AA"),
        "round 116: the recorder stores the reasoning trace",
    ),
    (("round 116: the angel watches the processor run", "key"), "bssxh 116: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 116: the angel watches the processor run", "lemon"), "csgbq 116: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 116: the angel watches the processor run", "a"), "round 116: the angel watches the processor run"),
    (("round 116: the angel watches the processor run", "zz"), "qntmc 116: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 116: the angel watches the processor run", "AgentU"), "ruyaw 116: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 116: the angel watches the processor run", "keyboard"), "bssor 116: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 116: the angel watches the processor run", "AA"), "round 116: the angel watches the processor run"),
    (("round 116: angle of the vector decides the match", "key"), "bssxh 116: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 116: angle of the vector decides the match", "lemon"), "csgbq 116: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 116: angle of the vector decides the match", "a"), "round 116: angle of the vector decides the match"),
    (("round 116: angle of the vector decides the match", "zz"), "qntmc 116: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 116: angle of the vector decides the match", "AgentU"),
        "ruyaw 116: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 116: angle of the vector decides the match", "keyboard"),
        "bssor 116: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 116: angle of the vector decides the match", "AA"), "round 116: angle of the vector decides the match"),
    (
        ("round 116: the candle burns twice as long at night", "key"),
        "bssxh 116: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 116: the candle burns twice as long at night", "lemon"),
        "csgbq 116: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 116: the candle burns twice as long at night", "a"), "round 116: the candle burns twice as long at night"),
    (
        ("round 116: the candle burns twice as long at night", "zz"),
        "qntmc 116: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 116: the candle burns twice as long at night", "AgentU"),
        "ruyaw 116: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 116: the candle burns twice as long at night", "keyboard"),
        "bssor 116: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 116: the candle burns twice as long at night", "AA"),
        "round 116: the candle burns twice as long at night",
    ),
    (("round 116: a mirror of the universe in one line", "key"), "bssxh 116: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 116: a mirror of the universe in one line", "lemon"), "csgbq 116: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 116: a mirror of the universe in one line", "a"), "round 116: a mirror of the universe in one line"),
    (("round 116: a mirror of the universe in one line", "zz"), "qntmc 116: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 116: a mirror of the universe in one line", "AgentU"), "ruyaw 116: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 116: a mirror of the universe in one line", "keyboard"),
        "bssor 116: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 116: a mirror of the universe in one line", "AA"), "round 116: a mirror of the universe in one line"),
    (("round 116: the queue drains before the storm", "key"), "bssxh 116: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 116: the queue drains before the storm", "lemon"), "csgbq 116: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 116: the queue drains before the storm", "a"), "round 116: the queue drains before the storm"),
    (("round 116: the queue drains before the storm", "zz"), "qntmc 116: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 116: the queue drains before the storm", "AgentU"), "ruyaw 116: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 116: the queue drains before the storm", "keyboard"), "bssor 116: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 116: the queue drains before the storm", "AA"), "round 116: the queue drains before the storm"),
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
