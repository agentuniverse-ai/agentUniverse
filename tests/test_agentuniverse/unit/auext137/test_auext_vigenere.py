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
    (("kitten137", "key"), "umrdil137"),
    (("kitten137", "lemon"), "vmfhry137"),
    (("kitten137", "a"), "kitten137"),
    (("kitten137", "zz"), "jhssdm137"),
    (("kitten137", "AgentU"), "koxgxh137"),
    (("kitten137", "keyboard"), "umrusn137"),
    (("kitten137", "AA"), "kitten137"),
    (("sitting137", "key"), "cmrdmlq137"),
    (("sitting137", "lemon"), "dmfhvyk137"),
    (("sitting137", "a"), "sitting137"),
    (("sitting137", "zz"), "rhsshmf137"),
    (("sitting137", "AgentU"), "soxgbhg137"),
    (("sitting137", "keyboard"), "cmruwnx137"),
    (("sitting137", "AA"), "sitting137"),
    (("agent137", "key"), "kkcxx137"),
    (("agent137", "lemon"), "lkqbg137"),
    (("agent137", "a"), "agent137"),
    (("agent137", "zz"), "zfdms137"),
    (("agent137", "AgentU"), "amiam137"),
    (("agent137", "keyboard"), "kkcoh137"),
    (("agent137", "AA"), "agent137"),
    (("angle137", "key"), "krevi137"),
    (("angle137", "lemon"), "lrszr137"),
    (("angle137", "a"), "angle137"),
    (("angle137", "zz"), "zmfkd137"),
    (("angle137", "AgentU"), "atkyx137"),
    (("angle137", "keyboard"), "krems137"),
    (("angle137", "AA"), "angle137"),
    (("universe137", "key"), "ergfipci137"),
    (("universe137", "lemon"), "frujrcwq137"),
    (("universe137", "a"), "universe137"),
    (("universe137", "zz"), "tmhudqrd137"),
    (("universe137", "AgentU"), "utmixlsk137"),
    (("universe137", "keyboard"), "ergwsrjh137"),
    (("universe137", "AA"), "universe137"),
    (("memory137", "key"), "wikyvw137"),
    (("memory137", "lemon"), "xiycej137"),
    (("memory137", "a"), "memory137"),
    (("memory137", "zz"), "ldlnqx137"),
    (("memory137", "AgentU"), "mkqbks137"),
    (("memory137", "keyboard"), "wikpfy137"),
    (("memory137", "AA"), "memory137"),
    (("stream137", "key"), "cxpoek137"),
    (("stream137", "lemon"), "dxdsnx137"),
    (("stream137", "a"), "stream137"),
    (("stream137", "zz"), "rsqdzl137"),
    (("stream137", "AgentU"), "szvrtg137"),
    (("stream137", "keyboard"), "cxpfom137"),
    (("stream137", "AA"), "stream137"),
    (("context137", "key"), "msldivd137"),
    (("context137", "lemon"), "nszhrix137"),
    (("context137", "a"), "context137"),
    (("context137", "zz"), "bnmsdws137"),
    (("context137", "AgentU"), "curgxrt137"),
    (("context137", "keyboard"), "mslusxk137"),
    (("context137", "AA"), "context137"),
    (("knowledge137", "key"), "urmgpcnkc137"),
    (("knowledge137", "lemon"), "vrakyphss137"),
    (("knowledge137", "a"), "knowledge137"),
    (("knowledge137", "zz"), "jmnvkdcfd137"),
    (("knowledge137", "AgentU"), "ktsjeydmi137"),
    (("knowledge137", "keyboard"), "urmxzeujo137"),
    (("knowledge137", "AA"), "knowledge137"),
    (("vector137", "key"), "fiadsp137"),
    (("vector137", "lemon"), "giohbc137"),
    (("vector137", "a"), "vector137"),
    (("vector137", "zz"), "udbsnq137"),
    (("vector137", "AgentU"), "vkgghl137"),
    (("vector137", "keyboard"), "fiaucr137"),
    (("vector137", "AA"), "vector137"),
    (("processor137", "key"), "zvmmiqcsp137"),
    (("processor137", "lemon"), "avaqrdwaf137"),
    (("processor137", "a"), "processor137"),
    (("processor137", "zz"), "oqnbdrrnq137"),
    (("processor137", "AgentU"), "pxspxmsuv137"),
    (("processor137", "keyboard"), "zvmdssjrb137"),
    (("processor137", "AA"), "processor137"),
    (("reasoning137", "key"), "biycslsre137"),
    (("reasoning137", "lemon"), "cimgbymzu137"),
    (("reasoning137", "a"), "reasoning137"),
    (("reasoning137", "zz"), "qdzrnmhmf137"),
    (("reasoning137", "AgentU"), "rkefhhitk137"),
    (("reasoning137", "keyboard"), "biytcnzqq137"),
    (("reasoning137", "AA"), "reasoning137"),
    (("machine137", "key"), "wearmlo137"),
    (("machine137", "lemon"), "xeovvyi137"),
    (("machine137", "a"), "machine137"),
    (("machine137", "zz"), "lzbghmd137"),
    (("machine137", "AgentU"), "mggubhe137"),
    (("machine137", "keyboard"), "weaiwnv137"),
    (("machine137", "AA"), "machine137"),
    (("learning137", "key"), "viybrgxk137"),
    (("learning137", "lemon"), "wimfatrs137"),
    (("learning137", "a"), "learning137"),
    (("learning137", "zz"), "kdzqmhmf137"),
    (("learning137", "AgentU"), "lkeegcnm137"),
    (("learning137", "keyboard"), "viysbiej137"),
    (("learning137", "AA"), "learning137"),
    (("model137", "key"), "wsbop137"),
    (("model137", "lemon"), "xspsy137"),
    (("model137", "a"), "model137"),
    (("model137", "zz"), "lncdk137"),
    (("model137", "AgentU"), "muhre137"),
    (("model137", "keyboard"), "wsbfz137"),
    (("model137", "AA"), "model137"),
    (("token137", "key"), "dsior137"),
    (("token137", "lemon"), "eswsa137"),
    (("token137", "a"), "token137"),
    (("token137", "zz"), "snjdm137"),
    (("token137", "AgentU"), "tuorg137"),
    (("token137", "keyboard"), "dsifb137"),
    (("token137", "AA"), "token137"),
    (("prompt137", "key"), "zvmwtr137"),
    (("prompt137", "lemon"), "avaace137"),
    (("prompt137", "a"), "prompt137"),
    (("prompt137", "zz"), "oqnlos137"),
    (("prompt137", "AgentU"), "pxszin137"),
    (("prompt137", "keyboard"), "zvmndt137"),
    (("prompt137", "AA"), "prompt137"),
    (("session137", "key"), "ciqcmmx137"),
    (("session137", "lemon"), "diegvzr137"),
    (("session137", "a"), "session137"),
    (("session137", "zz"), "rdrrhnm137"),
    (("session137", "AgentU"), "skwfbin137"),
    (("session137", "keyboard"), "ciqtwoe137"),
    (("session137", "AA"), "session137"),
    (("library137", "key"), "vmzbepi137"),
    (("library137", "lemon"), "wmnfncc137"),
    (("library137", "a"), "library137"),
    (("library137", "zz"), "khaqzqx137"),
    (("library137", "AgentU"), "lofetly137"),
    (("library137", "keyboard"), "vmzsorp137"),
    (("library137", "AA"), "library137"),
    (("service137", "key"), "cipfmao137"),
    (("service137", "lemon"), "didjvni137"),
    (("service137", "a"), "service137"),
    (("service137", "zz"), "rdquhbd137"),
    (("service137", "AgentU"), "skvibwe137"),
    (("service137", "keyboard"), "cipwwcv137"),
    (("service137", "AA"), "service137"),
    (("gateway137", "key"), "qeroayi137"),
    (("gateway137", "lemon"), "refsjlc137"),
    (("gateway137", "a"), "gateway137"),
    (("gateway137", "zz"), "fzsdvzx137"),
    (("gateway137", "AgentU"), "ggxrpuy137"),
    (("gateway137", "keyboard"), "qerfkap137"),
    (("gateway137", "AA"), "gateway137"),
    (("storage137", "key"), "cxmbeeo137"),
    (("storage137", "lemon"), "dxafnri137"),
    (("storage137", "a"), "storage137"),
    (("storage137", "zz"), "rsnqzfd137"),
    (("storage137", "AgentU"), "szsetae137"),
    (("storage137", "keyboard"), "cxmsogv137"),
    (("storage137", "AA"), "storage137"),
    (("network137", "key"), "xirgspu137"),
    (("network137", "lemon"), "yifkbco137"),
    (("network137", "a"), "network137"),
    (("network137", "zz"), "mdsvnqj137"),
    (("network137", "AgentU"), "nkxjhlk137"),
    (("network137", "keyboard"), "xirxcrb137"),
    (("network137", "AA"), "network137"),
    (("latency137", "key"), "verorai137"),
    (("latency137", "lemon"), "wefsanc137"),
    (("latency137", "a"), "latency137"),
    (("latency137", "zz"), "kzsdmbx137"),
    (("latency137", "AgentU"), "lgxrgwy137"),
    (("latency137", "keyboard"), "verfbcp137"),
    (("latency137", "AA"), "latency137"),
    (("buffer137", "key"), "lydpip137"),
    (("buffer137", "lemon"), "myrtrc137"),
    (("buffer137", "a"), "buffer137"),
    (("buffer137", "zz"), "ateedq137"),
    (("buffer137", "AgentU"), "bajsxl137"),
    (("buffer137", "keyboard"), "lydgsr137"),
    (("buffer137", "AA"), "buffer137"),
    (("queue137", "key"), "aycei137"),
    (("queue137", "lemon"), "byqir137"),
    (("queue137", "a"), "queue137"),
    (("queue137", "zz"), "ptdtd137"),
    (("queue137", "AgentU"), "qaihx137"),
    (("queue137", "keyboard"), "aycvs137"),
    (("queue137", "AA"), "queue137"),
    (("worker137", "key"), "gspuip137"),
    (("worker137", "lemon"), "hsdyrc137"),
    (("worker137", "a"), "worker137"),
    (("worker137", "zz"), "vnqjdq137"),
    (("worker137", "AgentU"), "wuvxxl137"),
    (("worker137", "keyboard"), "gsplsr137"),
    (("worker137", "AA"), "worker137"),
    (("kernel137", "key"), "uipxij137"),
    (("kernel137", "lemon"), "vidbrw137"),
    (("kernel137", "a"), "kernel137"),
    (("kernel137", "zz"), "jdqmdk137"),
    (("kernel137", "AgentU"), "kkvaxf137"),
    (("kernel137", "keyboard"), "uiposl137"),
    (("kernel137", "AA"), "kernel137"),
    (("signal137", "key"), "cmexej137"),
    (("signal137", "lemon"), "dmsbnw137"),
    (("signal137", "a"), "signal137"),
    (("signal137", "zz"), "rhfmzk137"),
    (("signal137", "AgentU"), "sokatf137"),
    (("signal137", "keyboard"), "cmeool137"),
    (("signal137", "AA"), "signal137"),
    (("packet137", "key"), "zeauir137"),
    (("packet137", "lemon"), "aeoyre137"),
    (("packet137", "a"), "packet137"),
    (("packet137", "zz"), "ozbjds137"),
    (("packet137", "AgentU"), "pggxxn137"),
    (("packet137", "keyboard"), "zealst137"),
    (("packet137", "AA"), "packet137"),
    (("router137", "key"), "bssdip137"),
    (("router137", "lemon"), "csghrc137"),
    (("router137", "a"), "router137"),
    (("router137", "zz"), "qntsdq137"),
    (("router137", "AgentU"), "ruygxl137"),
    (("router137", "keyboard"), "bssusr137"),
    (("router137", "AA"), "router137"),
    (("cluster137", "key"), "mpscxcb137"),
    (("cluster137", "lemon"), "npgggpv137"),
    (("cluster137", "a"), "cluster137"),
    (("cluster137", "zz"), "bktrsdq137"),
    (("cluster137", "AgentU"), "cryfmyr137"),
    (("cluster137", "keyboard"), "mpsthei137"),
    (("cluster137", "AA"), "cluster137"),
    (("mirror137", "key"), "wmpbsp137"),
    (("mirror137", "lemon"), "xmdfbc137"),
    (("mirror137", "a"), "mirror137"),
    (("mirror137", "zz"), "lhqqnq137"),
    (("mirror137", "AgentU"), "movehl137"),
    (("mirror137", "keyboard"), "wmpscr137"),
    (("mirror137", "AA"), "mirror137"),
    (("filter137", "key"), "pmjdip137"),
    (("filter137", "lemon"), "qmxhrc137"),
    (("filter137", "a"), "filter137"),
    (("filter137", "zz"), "ehksdq137"),
    (("filter137", "AgentU"), "fopgxl137"),
    (("filter137", "keyboard"), "pmjusr137"),
    (("filter137", "AA"), "filter137"),
    (("ranking137", "key"), "belumlq137"),
    (("ranking137", "lemon"), "cezyvyk137"),
    (("ranking137", "a"), "ranking137"),
    (("ranking137", "zz"), "qzmjhmf137"),
    (("ranking137", "AgentU"), "rgrxbhg137"),
    (("ranking137", "keyboard"), "bellwnx137"),
    (("ranking137", "AA"), "ranking137"),
    (("encoding137", "key"), "orayhgxk137"),
    (("encoding137", "lemon"), "procqtrs137"),
    (("encoding137", "a"), "encoding137"),
    (("encoding137", "zz"), "dmbnchmf137"),
    (("encoding137", "AgentU"), "etgbwcnm137"),
    (("encoding137", "keyboard"), "orapriej137"),
    (("encoding137", "AA"), "encoding137"),
    (("mapping137", "key"), "wenzmlq137"),
    (("mapping137", "lemon"), "xebdvyk137"),
    (("mapping137", "a"), "mapping137"),
    (("mapping137", "zz"), "lzoohmf137"),
    (("mapping137", "AgentU"), "mgtcbhg137"),
    (("mapping137", "keyboard"), "wenqwnx137"),
    (("mapping137", "AA"), "mapping137"),
    (("record137", "key"), "biayvb137"),
    (("record137", "lemon"), "cioceo137"),
    (("record137", "a"), "record137"),
    (("record137", "zz"), "qdbnqc137"),
    (("record137", "AgentU"), "rkgbkx137"),
    (("record137", "keyboard"), "biapfd137"),
    (("record137", "AA"), "record137"),
    (("candle137", "key"), "melnpc137"),
    (("candle137", "lemon"), "nezryp137"),
    (("candle137", "a"), "candle137"),
    (("candle137", "zz"), "bzmckd137"),
    (("candle137", "AgentU"), "cgrqey137"),
    (("candle137", "keyboard"), "meleze137"),
    (("candle137", "AA"), "candle137"),
    (("thread137", "key"), "dlpoeb137"),
    (("thread137", "lemon"), "eldsno137"),
    (("thread137", "a"), "thread137"),
    (("thread137", "zz"), "sgqdzc137"),
    (("thread137", "AgentU"), "tnvrtx137"),
    (("thread137", "keyboard"), "dlpfod137"),
    (("thread137", "AA"), "thread137"),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 137: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 137: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "a"),
        "round 137: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 137: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 137: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 137: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", "AA"),
        "round 137: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "key"),
        "bssxh 137: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 137: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "a"),
        "round 137: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 137: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 137: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 137: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", "AA"),
        "round 137: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 137: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 137: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "a"),
        "round 137: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 137: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 137: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 137: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", "AA"),
        "round 137: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 137: the processor reads the record then stops", "key"),
        "bssxh 137: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 137: the processor reads the record then stops", "lemon"),
        "csgbq 137: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 137: the processor reads the record then stops", "a"),
        "round 137: the processor reads the record then stops",
    ),
    (
        ("round 137: the processor reads the record then stops", "zz"),
        "qntmc 137: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 137: the processor reads the record then stops", "AgentU"),
        "ruyaw 137: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 137: the processor reads the record then stops", "keyboard"),
        "bssor 137: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 137: the processor reads the record then stops", "AA"),
        "round 137: the processor reads the record then stops",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "key"),
        "bssxh 137: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "lemon"),
        "csgbq 137: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "a"),
        "round 137: a worker pulls the next task from the queue",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "zz"),
        "qntmc 137: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 137: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "keyboard"),
        "bssor 137: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 137: a worker pulls the next task from the queue", "AA"),
        "round 137: a worker pulls the next task from the queue",
    ),
    (
        ("round 137: signals travel through the network layer", "key"),
        "bssxh 137: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 137: signals travel through the network layer", "lemon"),
        "csgbq 137: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 137: signals travel through the network layer", "a"),
        "round 137: signals travel through the network layer",
    ),
    (
        ("round 137: signals travel through the network layer", "zz"),
        "qntmc 137: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 137: signals travel through the network layer", "AgentU"),
        "ruyaw 137: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 137: signals travel through the network layer", "keyboard"),
        "bssor 137: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 137: signals travel through the network layer", "AA"),
        "round 137: signals travel through the network layer",
    ),
    (
        ("round 137: the gateway routes each request by policy", "key"),
        "bssxh 137: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 137: the gateway routes each request by policy", "lemon"),
        "csgbq 137: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 137: the gateway routes each request by policy", "a"),
        "round 137: the gateway routes each request by policy",
    ),
    (
        ("round 137: the gateway routes each request by policy", "zz"),
        "qntmc 137: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 137: the gateway routes each request by policy", "AgentU"),
        "ruyaw 137: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 137: the gateway routes each request by policy", "keyboard"),
        "bssor 137: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 137: the gateway routes each request by policy", "AA"),
        "round 137: the gateway routes each request by policy",
    ),
    (("round 137: memory grows until the buffer is full", "key"), "bssxh 137: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 137: memory grows until the buffer is full", "lemon"), "csgbq 137: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 137: memory grows until the buffer is full", "a"), "round 137: memory grows until the buffer is full"),
    (("round 137: memory grows until the buffer is full", "zz"), "qntmc 137: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 137: memory grows until the buffer is full", "AgentU"),
        "ruyaw 137: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 137: memory grows until the buffer is full", "keyboard"),
        "bssor 137: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 137: memory grows until the buffer is full", "AA"), "round 137: memory grows until the buffer is full"),
    (("round 137: the cluster mirrors every packet twice", "key"), "bssxh 137: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 137: the cluster mirrors every packet twice", "lemon"),
        "csgbq 137: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 137: the cluster mirrors every packet twice", "a"), "round 137: the cluster mirrors every packet twice"),
    (("round 137: the cluster mirrors every packet twice", "zz"), "qntmc 137: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 137: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 137: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 137: the cluster mirrors every packet twice", "keyboard"),
        "bssor 137: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 137: the cluster mirrors every packet twice", "AA"), "round 137: the cluster mirrors every packet twice"),
    (
        ("round 137: ranking uses tokens learned from the corpus", "key"),
        "bssxh 137: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 137: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", "a"),
        "round 137: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 137: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 137: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 137: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", "AA"),
        "round 137: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 137: a long session ends when the candle dies", "key"),
        "bssxh 137: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 137: a long session ends when the candle dies", "lemon"),
        "csgbq 137: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 137: a long session ends when the candle dies", "a"),
        "round 137: a long session ends when the candle dies",
    ),
    (
        ("round 137: a long session ends when the candle dies", "zz"),
        "qntmc 137: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 137: a long session ends when the candle dies", "AgentU"),
        "ruyaw 137: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 137: a long session ends when the candle dies", "keyboard"),
        "bssor 137: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 137: a long session ends when the candle dies", "AA"),
        "round 137: a long session ends when the candle dies",
    ),
    (("round 137: encode the prompt then map the result", "key"), "bssxh 137: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 137: encode the prompt then map the result", "lemon"), "csgbq 137: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 137: encode the prompt then map the result", "a"), "round 137: encode the prompt then map the result"),
    (("round 137: encode the prompt then map the result", "zz"), "qntmc 137: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 137: encode the prompt then map the result", "AgentU"),
        "ruyaw 137: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 137: encode the prompt then map the result", "keyboard"),
        "bssor 137: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 137: encode the prompt then map the result", "AA"), "round 137: encode the prompt then map the result"),
    (("round 137: the kernel wakes the worker at dawn", "key"), "bssxh 137: rri iovlop ukocc xfo ambocb er neux"),
    (("round 137: the kernel wakes the worker at dawn", "lemon"), "csgbq 137: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 137: the kernel wakes the worker at dawn", "a"), "round 137: the kernel wakes the worker at dawn"),
    (("round 137: the kernel wakes the worker at dawn", "zz"), "qntmc 137: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 137: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 137: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 137: the kernel wakes the worker at dawn", "keyboard"), "bssor 137: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 137: the kernel wakes the worker at dawn", "AA"), "round 137: the kernel wakes the worker at dawn"),
    (("round 137: service latency drops after the patch", "key"), "bssxh 137: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 137: service latency drops after the patch", "lemon"), "csgbq 137: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 137: service latency drops after the patch", "a"), "round 137: service latency drops after the patch"),
    (("round 137: service latency drops after the patch", "zz"), "qntmc 137: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 137: service latency drops after the patch", "AgentU"),
        "ruyaw 137: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 137: service latency drops after the patch", "keyboard"),
        "bssor 137: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 137: service latency drops after the patch", "AA"), "round 137: service latency drops after the patch"),
    (
        ("round 137: the library caches every vector it sees", "key"),
        "bssxh 137: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 137: the library caches every vector it sees", "lemon"),
        "csgbq 137: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 137: the library caches every vector it sees", "a"), "round 137: the library caches every vector it sees"),
    (
        ("round 137: the library caches every vector it sees", "zz"),
        "qntmc 137: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 137: the library caches every vector it sees", "AgentU"),
        "ruyaw 137: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 137: the library caches every vector it sees", "keyboard"),
        "bssor 137: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 137: the library caches every vector it sees", "AA"),
        "round 137: the library caches every vector it sees",
    ),
    (("round 137: agents argue then the debate resolves", "key"), "bssxh 137: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 137: agents argue then the debate resolves", "lemon"), "csgbq 137: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 137: agents argue then the debate resolves", "a"), "round 137: agents argue then the debate resolves"),
    (("round 137: agents argue then the debate resolves", "zz"), "qntmc 137: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 137: agents argue then the debate resolves", "AgentU"),
        "ruyaw 137: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 137: agents argue then the debate resolves", "keyboard"),
        "bssor 137: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 137: agents argue then the debate resolves", "AA"), "round 137: agents argue then the debate resolves"),
    (("round 137: the filter keeps only strong matches", "key"), "bssxh 137: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 137: the filter keeps only strong matches", "lemon"), "csgbq 137: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 137: the filter keeps only strong matches", "a"), "round 137: the filter keeps only strong matches"),
    (("round 137: the filter keeps only strong matches", "zz"), "qntmc 137: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 137: the filter keeps only strong matches", "AgentU"), "ruyaw 137: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 137: the filter keeps only strong matches", "keyboard"),
        "bssor 137: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 137: the filter keeps only strong matches", "AA"), "round 137: the filter keeps only strong matches"),
    (("round 137: the model answers with a short reply", "key"), "bssxh 137: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 137: the model answers with a short reply", "lemon"), "csgbq 137: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 137: the model answers with a short reply", "a"), "round 137: the model answers with a short reply"),
    (("round 137: the model answers with a short reply", "zz"), "qntmc 137: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 137: the model answers with a short reply", "AgentU"), "ruyaw 137: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 137: the model answers with a short reply", "keyboard"),
        "bssor 137: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 137: the model answers with a short reply", "AA"), "round 137: the model answers with a short reply"),
    (
        ("round 137: the recorder stores the reasoning trace", "key"),
        "bssxh 137: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 137: the recorder stores the reasoning trace", "lemon"),
        "csgbq 137: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 137: the recorder stores the reasoning trace", "a"), "round 137: the recorder stores the reasoning trace"),
    (
        ("round 137: the recorder stores the reasoning trace", "zz"),
        "qntmc 137: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 137: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 137: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 137: the recorder stores the reasoning trace", "keyboard"),
        "bssor 137: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 137: the recorder stores the reasoning trace", "AA"),
        "round 137: the recorder stores the reasoning trace",
    ),
    (("round 137: the angel watches the processor run", "key"), "bssxh 137: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 137: the angel watches the processor run", "lemon"), "csgbq 137: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 137: the angel watches the processor run", "a"), "round 137: the angel watches the processor run"),
    (("round 137: the angel watches the processor run", "zz"), "qntmc 137: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 137: the angel watches the processor run", "AgentU"), "ruyaw 137: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 137: the angel watches the processor run", "keyboard"), "bssor 137: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 137: the angel watches the processor run", "AA"), "round 137: the angel watches the processor run"),
    (("round 137: angle of the vector decides the match", "key"), "bssxh 137: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 137: angle of the vector decides the match", "lemon"), "csgbq 137: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 137: angle of the vector decides the match", "a"), "round 137: angle of the vector decides the match"),
    (("round 137: angle of the vector decides the match", "zz"), "qntmc 137: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 137: angle of the vector decides the match", "AgentU"),
        "ruyaw 137: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 137: angle of the vector decides the match", "keyboard"),
        "bssor 137: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 137: angle of the vector decides the match", "AA"), "round 137: angle of the vector decides the match"),
    (
        ("round 137: the candle burns twice as long at night", "key"),
        "bssxh 137: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 137: the candle burns twice as long at night", "lemon"),
        "csgbq 137: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 137: the candle burns twice as long at night", "a"), "round 137: the candle burns twice as long at night"),
    (
        ("round 137: the candle burns twice as long at night", "zz"),
        "qntmc 137: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 137: the candle burns twice as long at night", "AgentU"),
        "ruyaw 137: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 137: the candle burns twice as long at night", "keyboard"),
        "bssor 137: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 137: the candle burns twice as long at night", "AA"),
        "round 137: the candle burns twice as long at night",
    ),
    (("round 137: a mirror of the universe in one line", "key"), "bssxh 137: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 137: a mirror of the universe in one line", "lemon"), "csgbq 137: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 137: a mirror of the universe in one line", "a"), "round 137: a mirror of the universe in one line"),
    (("round 137: a mirror of the universe in one line", "zz"), "qntmc 137: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 137: a mirror of the universe in one line", "AgentU"), "ruyaw 137: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 137: a mirror of the universe in one line", "keyboard"),
        "bssor 137: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 137: a mirror of the universe in one line", "AA"), "round 137: a mirror of the universe in one line"),
    (("round 137: the queue drains before the storm", "key"), "bssxh 137: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 137: the queue drains before the storm", "lemon"), "csgbq 137: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 137: the queue drains before the storm", "a"), "round 137: the queue drains before the storm"),
    (("round 137: the queue drains before the storm", "zz"), "qntmc 137: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 137: the queue drains before the storm", "AgentU"), "ruyaw 137: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 137: the queue drains before the storm", "keyboard"), "bssor 137: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 137: the queue drains before the storm", "AA"), "round 137: the queue drains before the storm"),
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
