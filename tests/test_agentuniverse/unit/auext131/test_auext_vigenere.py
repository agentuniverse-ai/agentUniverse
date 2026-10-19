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
    (("kitten131", "key"), "umrdil131"),
    (("kitten131", "lemon"), "vmfhry131"),
    (("kitten131", "a"), "kitten131"),
    (("kitten131", "zz"), "jhssdm131"),
    (("kitten131", "AgentU"), "koxgxh131"),
    (("kitten131", "keyboard"), "umrusn131"),
    (("kitten131", "AA"), "kitten131"),
    (("sitting131", "key"), "cmrdmlq131"),
    (("sitting131", "lemon"), "dmfhvyk131"),
    (("sitting131", "a"), "sitting131"),
    (("sitting131", "zz"), "rhsshmf131"),
    (("sitting131", "AgentU"), "soxgbhg131"),
    (("sitting131", "keyboard"), "cmruwnx131"),
    (("sitting131", "AA"), "sitting131"),
    (("agent131", "key"), "kkcxx131"),
    (("agent131", "lemon"), "lkqbg131"),
    (("agent131", "a"), "agent131"),
    (("agent131", "zz"), "zfdms131"),
    (("agent131", "AgentU"), "amiam131"),
    (("agent131", "keyboard"), "kkcoh131"),
    (("agent131", "AA"), "agent131"),
    (("angle131", "key"), "krevi131"),
    (("angle131", "lemon"), "lrszr131"),
    (("angle131", "a"), "angle131"),
    (("angle131", "zz"), "zmfkd131"),
    (("angle131", "AgentU"), "atkyx131"),
    (("angle131", "keyboard"), "krems131"),
    (("angle131", "AA"), "angle131"),
    (("universe131", "key"), "ergfipci131"),
    (("universe131", "lemon"), "frujrcwq131"),
    (("universe131", "a"), "universe131"),
    (("universe131", "zz"), "tmhudqrd131"),
    (("universe131", "AgentU"), "utmixlsk131"),
    (("universe131", "keyboard"), "ergwsrjh131"),
    (("universe131", "AA"), "universe131"),
    (("memory131", "key"), "wikyvw131"),
    (("memory131", "lemon"), "xiycej131"),
    (("memory131", "a"), "memory131"),
    (("memory131", "zz"), "ldlnqx131"),
    (("memory131", "AgentU"), "mkqbks131"),
    (("memory131", "keyboard"), "wikpfy131"),
    (("memory131", "AA"), "memory131"),
    (("stream131", "key"), "cxpoek131"),
    (("stream131", "lemon"), "dxdsnx131"),
    (("stream131", "a"), "stream131"),
    (("stream131", "zz"), "rsqdzl131"),
    (("stream131", "AgentU"), "szvrtg131"),
    (("stream131", "keyboard"), "cxpfom131"),
    (("stream131", "AA"), "stream131"),
    (("context131", "key"), "msldivd131"),
    (("context131", "lemon"), "nszhrix131"),
    (("context131", "a"), "context131"),
    (("context131", "zz"), "bnmsdws131"),
    (("context131", "AgentU"), "curgxrt131"),
    (("context131", "keyboard"), "mslusxk131"),
    (("context131", "AA"), "context131"),
    (("knowledge131", "key"), "urmgpcnkc131"),
    (("knowledge131", "lemon"), "vrakyphss131"),
    (("knowledge131", "a"), "knowledge131"),
    (("knowledge131", "zz"), "jmnvkdcfd131"),
    (("knowledge131", "AgentU"), "ktsjeydmi131"),
    (("knowledge131", "keyboard"), "urmxzeujo131"),
    (("knowledge131", "AA"), "knowledge131"),
    (("vector131", "key"), "fiadsp131"),
    (("vector131", "lemon"), "giohbc131"),
    (("vector131", "a"), "vector131"),
    (("vector131", "zz"), "udbsnq131"),
    (("vector131", "AgentU"), "vkgghl131"),
    (("vector131", "keyboard"), "fiaucr131"),
    (("vector131", "AA"), "vector131"),
    (("processor131", "key"), "zvmmiqcsp131"),
    (("processor131", "lemon"), "avaqrdwaf131"),
    (("processor131", "a"), "processor131"),
    (("processor131", "zz"), "oqnbdrrnq131"),
    (("processor131", "AgentU"), "pxspxmsuv131"),
    (("processor131", "keyboard"), "zvmdssjrb131"),
    (("processor131", "AA"), "processor131"),
    (("reasoning131", "key"), "biycslsre131"),
    (("reasoning131", "lemon"), "cimgbymzu131"),
    (("reasoning131", "a"), "reasoning131"),
    (("reasoning131", "zz"), "qdzrnmhmf131"),
    (("reasoning131", "AgentU"), "rkefhhitk131"),
    (("reasoning131", "keyboard"), "biytcnzqq131"),
    (("reasoning131", "AA"), "reasoning131"),
    (("machine131", "key"), "wearmlo131"),
    (("machine131", "lemon"), "xeovvyi131"),
    (("machine131", "a"), "machine131"),
    (("machine131", "zz"), "lzbghmd131"),
    (("machine131", "AgentU"), "mggubhe131"),
    (("machine131", "keyboard"), "weaiwnv131"),
    (("machine131", "AA"), "machine131"),
    (("learning131", "key"), "viybrgxk131"),
    (("learning131", "lemon"), "wimfatrs131"),
    (("learning131", "a"), "learning131"),
    (("learning131", "zz"), "kdzqmhmf131"),
    (("learning131", "AgentU"), "lkeegcnm131"),
    (("learning131", "keyboard"), "viysbiej131"),
    (("learning131", "AA"), "learning131"),
    (("model131", "key"), "wsbop131"),
    (("model131", "lemon"), "xspsy131"),
    (("model131", "a"), "model131"),
    (("model131", "zz"), "lncdk131"),
    (("model131", "AgentU"), "muhre131"),
    (("model131", "keyboard"), "wsbfz131"),
    (("model131", "AA"), "model131"),
    (("token131", "key"), "dsior131"),
    (("token131", "lemon"), "eswsa131"),
    (("token131", "a"), "token131"),
    (("token131", "zz"), "snjdm131"),
    (("token131", "AgentU"), "tuorg131"),
    (("token131", "keyboard"), "dsifb131"),
    (("token131", "AA"), "token131"),
    (("prompt131", "key"), "zvmwtr131"),
    (("prompt131", "lemon"), "avaace131"),
    (("prompt131", "a"), "prompt131"),
    (("prompt131", "zz"), "oqnlos131"),
    (("prompt131", "AgentU"), "pxszin131"),
    (("prompt131", "keyboard"), "zvmndt131"),
    (("prompt131", "AA"), "prompt131"),
    (("session131", "key"), "ciqcmmx131"),
    (("session131", "lemon"), "diegvzr131"),
    (("session131", "a"), "session131"),
    (("session131", "zz"), "rdrrhnm131"),
    (("session131", "AgentU"), "skwfbin131"),
    (("session131", "keyboard"), "ciqtwoe131"),
    (("session131", "AA"), "session131"),
    (("library131", "key"), "vmzbepi131"),
    (("library131", "lemon"), "wmnfncc131"),
    (("library131", "a"), "library131"),
    (("library131", "zz"), "khaqzqx131"),
    (("library131", "AgentU"), "lofetly131"),
    (("library131", "keyboard"), "vmzsorp131"),
    (("library131", "AA"), "library131"),
    (("service131", "key"), "cipfmao131"),
    (("service131", "lemon"), "didjvni131"),
    (("service131", "a"), "service131"),
    (("service131", "zz"), "rdquhbd131"),
    (("service131", "AgentU"), "skvibwe131"),
    (("service131", "keyboard"), "cipwwcv131"),
    (("service131", "AA"), "service131"),
    (("gateway131", "key"), "qeroayi131"),
    (("gateway131", "lemon"), "refsjlc131"),
    (("gateway131", "a"), "gateway131"),
    (("gateway131", "zz"), "fzsdvzx131"),
    (("gateway131", "AgentU"), "ggxrpuy131"),
    (("gateway131", "keyboard"), "qerfkap131"),
    (("gateway131", "AA"), "gateway131"),
    (("storage131", "key"), "cxmbeeo131"),
    (("storage131", "lemon"), "dxafnri131"),
    (("storage131", "a"), "storage131"),
    (("storage131", "zz"), "rsnqzfd131"),
    (("storage131", "AgentU"), "szsetae131"),
    (("storage131", "keyboard"), "cxmsogv131"),
    (("storage131", "AA"), "storage131"),
    (("network131", "key"), "xirgspu131"),
    (("network131", "lemon"), "yifkbco131"),
    (("network131", "a"), "network131"),
    (("network131", "zz"), "mdsvnqj131"),
    (("network131", "AgentU"), "nkxjhlk131"),
    (("network131", "keyboard"), "xirxcrb131"),
    (("network131", "AA"), "network131"),
    (("latency131", "key"), "verorai131"),
    (("latency131", "lemon"), "wefsanc131"),
    (("latency131", "a"), "latency131"),
    (("latency131", "zz"), "kzsdmbx131"),
    (("latency131", "AgentU"), "lgxrgwy131"),
    (("latency131", "keyboard"), "verfbcp131"),
    (("latency131", "AA"), "latency131"),
    (("buffer131", "key"), "lydpip131"),
    (("buffer131", "lemon"), "myrtrc131"),
    (("buffer131", "a"), "buffer131"),
    (("buffer131", "zz"), "ateedq131"),
    (("buffer131", "AgentU"), "bajsxl131"),
    (("buffer131", "keyboard"), "lydgsr131"),
    (("buffer131", "AA"), "buffer131"),
    (("queue131", "key"), "aycei131"),
    (("queue131", "lemon"), "byqir131"),
    (("queue131", "a"), "queue131"),
    (("queue131", "zz"), "ptdtd131"),
    (("queue131", "AgentU"), "qaihx131"),
    (("queue131", "keyboard"), "aycvs131"),
    (("queue131", "AA"), "queue131"),
    (("worker131", "key"), "gspuip131"),
    (("worker131", "lemon"), "hsdyrc131"),
    (("worker131", "a"), "worker131"),
    (("worker131", "zz"), "vnqjdq131"),
    (("worker131", "AgentU"), "wuvxxl131"),
    (("worker131", "keyboard"), "gsplsr131"),
    (("worker131", "AA"), "worker131"),
    (("kernel131", "key"), "uipxij131"),
    (("kernel131", "lemon"), "vidbrw131"),
    (("kernel131", "a"), "kernel131"),
    (("kernel131", "zz"), "jdqmdk131"),
    (("kernel131", "AgentU"), "kkvaxf131"),
    (("kernel131", "keyboard"), "uiposl131"),
    (("kernel131", "AA"), "kernel131"),
    (("signal131", "key"), "cmexej131"),
    (("signal131", "lemon"), "dmsbnw131"),
    (("signal131", "a"), "signal131"),
    (("signal131", "zz"), "rhfmzk131"),
    (("signal131", "AgentU"), "sokatf131"),
    (("signal131", "keyboard"), "cmeool131"),
    (("signal131", "AA"), "signal131"),
    (("packet131", "key"), "zeauir131"),
    (("packet131", "lemon"), "aeoyre131"),
    (("packet131", "a"), "packet131"),
    (("packet131", "zz"), "ozbjds131"),
    (("packet131", "AgentU"), "pggxxn131"),
    (("packet131", "keyboard"), "zealst131"),
    (("packet131", "AA"), "packet131"),
    (("router131", "key"), "bssdip131"),
    (("router131", "lemon"), "csghrc131"),
    (("router131", "a"), "router131"),
    (("router131", "zz"), "qntsdq131"),
    (("router131", "AgentU"), "ruygxl131"),
    (("router131", "keyboard"), "bssusr131"),
    (("router131", "AA"), "router131"),
    (("cluster131", "key"), "mpscxcb131"),
    (("cluster131", "lemon"), "npgggpv131"),
    (("cluster131", "a"), "cluster131"),
    (("cluster131", "zz"), "bktrsdq131"),
    (("cluster131", "AgentU"), "cryfmyr131"),
    (("cluster131", "keyboard"), "mpsthei131"),
    (("cluster131", "AA"), "cluster131"),
    (("mirror131", "key"), "wmpbsp131"),
    (("mirror131", "lemon"), "xmdfbc131"),
    (("mirror131", "a"), "mirror131"),
    (("mirror131", "zz"), "lhqqnq131"),
    (("mirror131", "AgentU"), "movehl131"),
    (("mirror131", "keyboard"), "wmpscr131"),
    (("mirror131", "AA"), "mirror131"),
    (("filter131", "key"), "pmjdip131"),
    (("filter131", "lemon"), "qmxhrc131"),
    (("filter131", "a"), "filter131"),
    (("filter131", "zz"), "ehksdq131"),
    (("filter131", "AgentU"), "fopgxl131"),
    (("filter131", "keyboard"), "pmjusr131"),
    (("filter131", "AA"), "filter131"),
    (("ranking131", "key"), "belumlq131"),
    (("ranking131", "lemon"), "cezyvyk131"),
    (("ranking131", "a"), "ranking131"),
    (("ranking131", "zz"), "qzmjhmf131"),
    (("ranking131", "AgentU"), "rgrxbhg131"),
    (("ranking131", "keyboard"), "bellwnx131"),
    (("ranking131", "AA"), "ranking131"),
    (("encoding131", "key"), "orayhgxk131"),
    (("encoding131", "lemon"), "procqtrs131"),
    (("encoding131", "a"), "encoding131"),
    (("encoding131", "zz"), "dmbnchmf131"),
    (("encoding131", "AgentU"), "etgbwcnm131"),
    (("encoding131", "keyboard"), "orapriej131"),
    (("encoding131", "AA"), "encoding131"),
    (("mapping131", "key"), "wenzmlq131"),
    (("mapping131", "lemon"), "xebdvyk131"),
    (("mapping131", "a"), "mapping131"),
    (("mapping131", "zz"), "lzoohmf131"),
    (("mapping131", "AgentU"), "mgtcbhg131"),
    (("mapping131", "keyboard"), "wenqwnx131"),
    (("mapping131", "AA"), "mapping131"),
    (("record131", "key"), "biayvb131"),
    (("record131", "lemon"), "cioceo131"),
    (("record131", "a"), "record131"),
    (("record131", "zz"), "qdbnqc131"),
    (("record131", "AgentU"), "rkgbkx131"),
    (("record131", "keyboard"), "biapfd131"),
    (("record131", "AA"), "record131"),
    (("candle131", "key"), "melnpc131"),
    (("candle131", "lemon"), "nezryp131"),
    (("candle131", "a"), "candle131"),
    (("candle131", "zz"), "bzmckd131"),
    (("candle131", "AgentU"), "cgrqey131"),
    (("candle131", "keyboard"), "meleze131"),
    (("candle131", "AA"), "candle131"),
    (("thread131", "key"), "dlpoeb131"),
    (("thread131", "lemon"), "eldsno131"),
    (("thread131", "a"), "thread131"),
    (("thread131", "zz"), "sgqdzc131"),
    (("thread131", "AgentU"), "tnvrtx131"),
    (("thread131", "keyboard"), "dlpfod131"),
    (("thread131", "AA"), "thread131"),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 131: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 131: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "a"),
        "round 131: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 131: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 131: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 131: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", "AA"),
        "round 131: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "key"),
        "bssxh 131: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 131: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "a"),
        "round 131: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 131: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 131: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 131: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", "AA"),
        "round 131: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 131: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 131: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "a"),
        "round 131: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 131: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 131: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 131: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", "AA"),
        "round 131: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 131: the processor reads the record then stops", "key"),
        "bssxh 131: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 131: the processor reads the record then stops", "lemon"),
        "csgbq 131: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 131: the processor reads the record then stops", "a"),
        "round 131: the processor reads the record then stops",
    ),
    (
        ("round 131: the processor reads the record then stops", "zz"),
        "qntmc 131: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 131: the processor reads the record then stops", "AgentU"),
        "ruyaw 131: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 131: the processor reads the record then stops", "keyboard"),
        "bssor 131: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 131: the processor reads the record then stops", "AA"),
        "round 131: the processor reads the record then stops",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "key"),
        "bssxh 131: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "lemon"),
        "csgbq 131: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "a"),
        "round 131: a worker pulls the next task from the queue",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "zz"),
        "qntmc 131: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 131: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "keyboard"),
        "bssor 131: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 131: a worker pulls the next task from the queue", "AA"),
        "round 131: a worker pulls the next task from the queue",
    ),
    (
        ("round 131: signals travel through the network layer", "key"),
        "bssxh 131: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 131: signals travel through the network layer", "lemon"),
        "csgbq 131: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 131: signals travel through the network layer", "a"),
        "round 131: signals travel through the network layer",
    ),
    (
        ("round 131: signals travel through the network layer", "zz"),
        "qntmc 131: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 131: signals travel through the network layer", "AgentU"),
        "ruyaw 131: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 131: signals travel through the network layer", "keyboard"),
        "bssor 131: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 131: signals travel through the network layer", "AA"),
        "round 131: signals travel through the network layer",
    ),
    (
        ("round 131: the gateway routes each request by policy", "key"),
        "bssxh 131: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 131: the gateway routes each request by policy", "lemon"),
        "csgbq 131: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 131: the gateway routes each request by policy", "a"),
        "round 131: the gateway routes each request by policy",
    ),
    (
        ("round 131: the gateway routes each request by policy", "zz"),
        "qntmc 131: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 131: the gateway routes each request by policy", "AgentU"),
        "ruyaw 131: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 131: the gateway routes each request by policy", "keyboard"),
        "bssor 131: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 131: the gateway routes each request by policy", "AA"),
        "round 131: the gateway routes each request by policy",
    ),
    (("round 131: memory grows until the buffer is full", "key"), "bssxh 131: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 131: memory grows until the buffer is full", "lemon"), "csgbq 131: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 131: memory grows until the buffer is full", "a"), "round 131: memory grows until the buffer is full"),
    (("round 131: memory grows until the buffer is full", "zz"), "qntmc 131: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 131: memory grows until the buffer is full", "AgentU"),
        "ruyaw 131: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 131: memory grows until the buffer is full", "keyboard"),
        "bssor 131: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 131: memory grows until the buffer is full", "AA"), "round 131: memory grows until the buffer is full"),
    (("round 131: the cluster mirrors every packet twice", "key"), "bssxh 131: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 131: the cluster mirrors every packet twice", "lemon"),
        "csgbq 131: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 131: the cluster mirrors every packet twice", "a"), "round 131: the cluster mirrors every packet twice"),
    (("round 131: the cluster mirrors every packet twice", "zz"), "qntmc 131: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 131: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 131: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 131: the cluster mirrors every packet twice", "keyboard"),
        "bssor 131: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 131: the cluster mirrors every packet twice", "AA"), "round 131: the cluster mirrors every packet twice"),
    (
        ("round 131: ranking uses tokens learned from the corpus", "key"),
        "bssxh 131: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 131: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", "a"),
        "round 131: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 131: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 131: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 131: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", "AA"),
        "round 131: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 131: a long session ends when the candle dies", "key"),
        "bssxh 131: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 131: a long session ends when the candle dies", "lemon"),
        "csgbq 131: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 131: a long session ends when the candle dies", "a"),
        "round 131: a long session ends when the candle dies",
    ),
    (
        ("round 131: a long session ends when the candle dies", "zz"),
        "qntmc 131: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 131: a long session ends when the candle dies", "AgentU"),
        "ruyaw 131: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 131: a long session ends when the candle dies", "keyboard"),
        "bssor 131: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 131: a long session ends when the candle dies", "AA"),
        "round 131: a long session ends when the candle dies",
    ),
    (("round 131: encode the prompt then map the result", "key"), "bssxh 131: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 131: encode the prompt then map the result", "lemon"), "csgbq 131: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 131: encode the prompt then map the result", "a"), "round 131: encode the prompt then map the result"),
    (("round 131: encode the prompt then map the result", "zz"), "qntmc 131: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 131: encode the prompt then map the result", "AgentU"),
        "ruyaw 131: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 131: encode the prompt then map the result", "keyboard"),
        "bssor 131: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 131: encode the prompt then map the result", "AA"), "round 131: encode the prompt then map the result"),
    (("round 131: the kernel wakes the worker at dawn", "key"), "bssxh 131: rri iovlop ukocc xfo ambocb er neux"),
    (("round 131: the kernel wakes the worker at dawn", "lemon"), "csgbq 131: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 131: the kernel wakes the worker at dawn", "a"), "round 131: the kernel wakes the worker at dawn"),
    (("round 131: the kernel wakes the worker at dawn", "zz"), "qntmc 131: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 131: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 131: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 131: the kernel wakes the worker at dawn", "keyboard"), "bssor 131: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 131: the kernel wakes the worker at dawn", "AA"), "round 131: the kernel wakes the worker at dawn"),
    (("round 131: service latency drops after the patch", "key"), "bssxh 131: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 131: service latency drops after the patch", "lemon"), "csgbq 131: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 131: service latency drops after the patch", "a"), "round 131: service latency drops after the patch"),
    (("round 131: service latency drops after the patch", "zz"), "qntmc 131: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 131: service latency drops after the patch", "AgentU"),
        "ruyaw 131: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 131: service latency drops after the patch", "keyboard"),
        "bssor 131: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 131: service latency drops after the patch", "AA"), "round 131: service latency drops after the patch"),
    (
        ("round 131: the library caches every vector it sees", "key"),
        "bssxh 131: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 131: the library caches every vector it sees", "lemon"),
        "csgbq 131: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 131: the library caches every vector it sees", "a"), "round 131: the library caches every vector it sees"),
    (
        ("round 131: the library caches every vector it sees", "zz"),
        "qntmc 131: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 131: the library caches every vector it sees", "AgentU"),
        "ruyaw 131: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 131: the library caches every vector it sees", "keyboard"),
        "bssor 131: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 131: the library caches every vector it sees", "AA"),
        "round 131: the library caches every vector it sees",
    ),
    (("round 131: agents argue then the debate resolves", "key"), "bssxh 131: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 131: agents argue then the debate resolves", "lemon"), "csgbq 131: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 131: agents argue then the debate resolves", "a"), "round 131: agents argue then the debate resolves"),
    (("round 131: agents argue then the debate resolves", "zz"), "qntmc 131: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 131: agents argue then the debate resolves", "AgentU"),
        "ruyaw 131: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 131: agents argue then the debate resolves", "keyboard"),
        "bssor 131: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 131: agents argue then the debate resolves", "AA"), "round 131: agents argue then the debate resolves"),
    (("round 131: the filter keeps only strong matches", "key"), "bssxh 131: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 131: the filter keeps only strong matches", "lemon"), "csgbq 131: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 131: the filter keeps only strong matches", "a"), "round 131: the filter keeps only strong matches"),
    (("round 131: the filter keeps only strong matches", "zz"), "qntmc 131: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 131: the filter keeps only strong matches", "AgentU"), "ruyaw 131: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 131: the filter keeps only strong matches", "keyboard"),
        "bssor 131: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 131: the filter keeps only strong matches", "AA"), "round 131: the filter keeps only strong matches"),
    (("round 131: the model answers with a short reply", "key"), "bssxh 131: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 131: the model answers with a short reply", "lemon"), "csgbq 131: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 131: the model answers with a short reply", "a"), "round 131: the model answers with a short reply"),
    (("round 131: the model answers with a short reply", "zz"), "qntmc 131: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 131: the model answers with a short reply", "AgentU"), "ruyaw 131: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 131: the model answers with a short reply", "keyboard"),
        "bssor 131: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 131: the model answers with a short reply", "AA"), "round 131: the model answers with a short reply"),
    (
        ("round 131: the recorder stores the reasoning trace", "key"),
        "bssxh 131: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 131: the recorder stores the reasoning trace", "lemon"),
        "csgbq 131: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 131: the recorder stores the reasoning trace", "a"), "round 131: the recorder stores the reasoning trace"),
    (
        ("round 131: the recorder stores the reasoning trace", "zz"),
        "qntmc 131: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 131: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 131: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 131: the recorder stores the reasoning trace", "keyboard"),
        "bssor 131: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 131: the recorder stores the reasoning trace", "AA"),
        "round 131: the recorder stores the reasoning trace",
    ),
    (("round 131: the angel watches the processor run", "key"), "bssxh 131: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 131: the angel watches the processor run", "lemon"), "csgbq 131: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 131: the angel watches the processor run", "a"), "round 131: the angel watches the processor run"),
    (("round 131: the angel watches the processor run", "zz"), "qntmc 131: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 131: the angel watches the processor run", "AgentU"), "ruyaw 131: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 131: the angel watches the processor run", "keyboard"), "bssor 131: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 131: the angel watches the processor run", "AA"), "round 131: the angel watches the processor run"),
    (("round 131: angle of the vector decides the match", "key"), "bssxh 131: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 131: angle of the vector decides the match", "lemon"), "csgbq 131: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 131: angle of the vector decides the match", "a"), "round 131: angle of the vector decides the match"),
    (("round 131: angle of the vector decides the match", "zz"), "qntmc 131: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 131: angle of the vector decides the match", "AgentU"),
        "ruyaw 131: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 131: angle of the vector decides the match", "keyboard"),
        "bssor 131: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 131: angle of the vector decides the match", "AA"), "round 131: angle of the vector decides the match"),
    (
        ("round 131: the candle burns twice as long at night", "key"),
        "bssxh 131: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 131: the candle burns twice as long at night", "lemon"),
        "csgbq 131: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 131: the candle burns twice as long at night", "a"), "round 131: the candle burns twice as long at night"),
    (
        ("round 131: the candle burns twice as long at night", "zz"),
        "qntmc 131: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 131: the candle burns twice as long at night", "AgentU"),
        "ruyaw 131: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 131: the candle burns twice as long at night", "keyboard"),
        "bssor 131: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 131: the candle burns twice as long at night", "AA"),
        "round 131: the candle burns twice as long at night",
    ),
    (("round 131: a mirror of the universe in one line", "key"), "bssxh 131: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 131: a mirror of the universe in one line", "lemon"), "csgbq 131: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 131: a mirror of the universe in one line", "a"), "round 131: a mirror of the universe in one line"),
    (("round 131: a mirror of the universe in one line", "zz"), "qntmc 131: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 131: a mirror of the universe in one line", "AgentU"), "ruyaw 131: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 131: a mirror of the universe in one line", "keyboard"),
        "bssor 131: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 131: a mirror of the universe in one line", "AA"), "round 131: a mirror of the universe in one line"),
    (("round 131: the queue drains before the storm", "key"), "bssxh 131: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 131: the queue drains before the storm", "lemon"), "csgbq 131: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 131: the queue drains before the storm", "a"), "round 131: the queue drains before the storm"),
    (("round 131: the queue drains before the storm", "zz"), "qntmc 131: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 131: the queue drains before the storm", "AgentU"), "ruyaw 131: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 131: the queue drains before the storm", "keyboard"), "bssor 131: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 131: the queue drains before the storm", "AA"), "round 131: the queue drains before the storm"),
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
