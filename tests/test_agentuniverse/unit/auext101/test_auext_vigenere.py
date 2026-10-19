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
    (("kitten101", "key"), "umrdil101"),
    (("kitten101", "lemon"), "vmfhry101"),
    (("kitten101", "a"), "kitten101"),
    (("kitten101", "zz"), "jhssdm101"),
    (("kitten101", "AgentU"), "koxgxh101"),
    (("kitten101", "keyboard"), "umrusn101"),
    (("kitten101", "AA"), "kitten101"),
    (("sitting101", "key"), "cmrdmlq101"),
    (("sitting101", "lemon"), "dmfhvyk101"),
    (("sitting101", "a"), "sitting101"),
    (("sitting101", "zz"), "rhsshmf101"),
    (("sitting101", "AgentU"), "soxgbhg101"),
    (("sitting101", "keyboard"), "cmruwnx101"),
    (("sitting101", "AA"), "sitting101"),
    (("agent101", "key"), "kkcxx101"),
    (("agent101", "lemon"), "lkqbg101"),
    (("agent101", "a"), "agent101"),
    (("agent101", "zz"), "zfdms101"),
    (("agent101", "AgentU"), "amiam101"),
    (("agent101", "keyboard"), "kkcoh101"),
    (("agent101", "AA"), "agent101"),
    (("angle101", "key"), "krevi101"),
    (("angle101", "lemon"), "lrszr101"),
    (("angle101", "a"), "angle101"),
    (("angle101", "zz"), "zmfkd101"),
    (("angle101", "AgentU"), "atkyx101"),
    (("angle101", "keyboard"), "krems101"),
    (("angle101", "AA"), "angle101"),
    (("universe101", "key"), "ergfipci101"),
    (("universe101", "lemon"), "frujrcwq101"),
    (("universe101", "a"), "universe101"),
    (("universe101", "zz"), "tmhudqrd101"),
    (("universe101", "AgentU"), "utmixlsk101"),
    (("universe101", "keyboard"), "ergwsrjh101"),
    (("universe101", "AA"), "universe101"),
    (("memory101", "key"), "wikyvw101"),
    (("memory101", "lemon"), "xiycej101"),
    (("memory101", "a"), "memory101"),
    (("memory101", "zz"), "ldlnqx101"),
    (("memory101", "AgentU"), "mkqbks101"),
    (("memory101", "keyboard"), "wikpfy101"),
    (("memory101", "AA"), "memory101"),
    (("stream101", "key"), "cxpoek101"),
    (("stream101", "lemon"), "dxdsnx101"),
    (("stream101", "a"), "stream101"),
    (("stream101", "zz"), "rsqdzl101"),
    (("stream101", "AgentU"), "szvrtg101"),
    (("stream101", "keyboard"), "cxpfom101"),
    (("stream101", "AA"), "stream101"),
    (("context101", "key"), "msldivd101"),
    (("context101", "lemon"), "nszhrix101"),
    (("context101", "a"), "context101"),
    (("context101", "zz"), "bnmsdws101"),
    (("context101", "AgentU"), "curgxrt101"),
    (("context101", "keyboard"), "mslusxk101"),
    (("context101", "AA"), "context101"),
    (("knowledge101", "key"), "urmgpcnkc101"),
    (("knowledge101", "lemon"), "vrakyphss101"),
    (("knowledge101", "a"), "knowledge101"),
    (("knowledge101", "zz"), "jmnvkdcfd101"),
    (("knowledge101", "AgentU"), "ktsjeydmi101"),
    (("knowledge101", "keyboard"), "urmxzeujo101"),
    (("knowledge101", "AA"), "knowledge101"),
    (("vector101", "key"), "fiadsp101"),
    (("vector101", "lemon"), "giohbc101"),
    (("vector101", "a"), "vector101"),
    (("vector101", "zz"), "udbsnq101"),
    (("vector101", "AgentU"), "vkgghl101"),
    (("vector101", "keyboard"), "fiaucr101"),
    (("vector101", "AA"), "vector101"),
    (("processor101", "key"), "zvmmiqcsp101"),
    (("processor101", "lemon"), "avaqrdwaf101"),
    (("processor101", "a"), "processor101"),
    (("processor101", "zz"), "oqnbdrrnq101"),
    (("processor101", "AgentU"), "pxspxmsuv101"),
    (("processor101", "keyboard"), "zvmdssjrb101"),
    (("processor101", "AA"), "processor101"),
    (("reasoning101", "key"), "biycslsre101"),
    (("reasoning101", "lemon"), "cimgbymzu101"),
    (("reasoning101", "a"), "reasoning101"),
    (("reasoning101", "zz"), "qdzrnmhmf101"),
    (("reasoning101", "AgentU"), "rkefhhitk101"),
    (("reasoning101", "keyboard"), "biytcnzqq101"),
    (("reasoning101", "AA"), "reasoning101"),
    (("machine101", "key"), "wearmlo101"),
    (("machine101", "lemon"), "xeovvyi101"),
    (("machine101", "a"), "machine101"),
    (("machine101", "zz"), "lzbghmd101"),
    (("machine101", "AgentU"), "mggubhe101"),
    (("machine101", "keyboard"), "weaiwnv101"),
    (("machine101", "AA"), "machine101"),
    (("learning101", "key"), "viybrgxk101"),
    (("learning101", "lemon"), "wimfatrs101"),
    (("learning101", "a"), "learning101"),
    (("learning101", "zz"), "kdzqmhmf101"),
    (("learning101", "AgentU"), "lkeegcnm101"),
    (("learning101", "keyboard"), "viysbiej101"),
    (("learning101", "AA"), "learning101"),
    (("model101", "key"), "wsbop101"),
    (("model101", "lemon"), "xspsy101"),
    (("model101", "a"), "model101"),
    (("model101", "zz"), "lncdk101"),
    (("model101", "AgentU"), "muhre101"),
    (("model101", "keyboard"), "wsbfz101"),
    (("model101", "AA"), "model101"),
    (("token101", "key"), "dsior101"),
    (("token101", "lemon"), "eswsa101"),
    (("token101", "a"), "token101"),
    (("token101", "zz"), "snjdm101"),
    (("token101", "AgentU"), "tuorg101"),
    (("token101", "keyboard"), "dsifb101"),
    (("token101", "AA"), "token101"),
    (("prompt101", "key"), "zvmwtr101"),
    (("prompt101", "lemon"), "avaace101"),
    (("prompt101", "a"), "prompt101"),
    (("prompt101", "zz"), "oqnlos101"),
    (("prompt101", "AgentU"), "pxszin101"),
    (("prompt101", "keyboard"), "zvmndt101"),
    (("prompt101", "AA"), "prompt101"),
    (("session101", "key"), "ciqcmmx101"),
    (("session101", "lemon"), "diegvzr101"),
    (("session101", "a"), "session101"),
    (("session101", "zz"), "rdrrhnm101"),
    (("session101", "AgentU"), "skwfbin101"),
    (("session101", "keyboard"), "ciqtwoe101"),
    (("session101", "AA"), "session101"),
    (("library101", "key"), "vmzbepi101"),
    (("library101", "lemon"), "wmnfncc101"),
    (("library101", "a"), "library101"),
    (("library101", "zz"), "khaqzqx101"),
    (("library101", "AgentU"), "lofetly101"),
    (("library101", "keyboard"), "vmzsorp101"),
    (("library101", "AA"), "library101"),
    (("service101", "key"), "cipfmao101"),
    (("service101", "lemon"), "didjvni101"),
    (("service101", "a"), "service101"),
    (("service101", "zz"), "rdquhbd101"),
    (("service101", "AgentU"), "skvibwe101"),
    (("service101", "keyboard"), "cipwwcv101"),
    (("service101", "AA"), "service101"),
    (("gateway101", "key"), "qeroayi101"),
    (("gateway101", "lemon"), "refsjlc101"),
    (("gateway101", "a"), "gateway101"),
    (("gateway101", "zz"), "fzsdvzx101"),
    (("gateway101", "AgentU"), "ggxrpuy101"),
    (("gateway101", "keyboard"), "qerfkap101"),
    (("gateway101", "AA"), "gateway101"),
    (("storage101", "key"), "cxmbeeo101"),
    (("storage101", "lemon"), "dxafnri101"),
    (("storage101", "a"), "storage101"),
    (("storage101", "zz"), "rsnqzfd101"),
    (("storage101", "AgentU"), "szsetae101"),
    (("storage101", "keyboard"), "cxmsogv101"),
    (("storage101", "AA"), "storage101"),
    (("network101", "key"), "xirgspu101"),
    (("network101", "lemon"), "yifkbco101"),
    (("network101", "a"), "network101"),
    (("network101", "zz"), "mdsvnqj101"),
    (("network101", "AgentU"), "nkxjhlk101"),
    (("network101", "keyboard"), "xirxcrb101"),
    (("network101", "AA"), "network101"),
    (("latency101", "key"), "verorai101"),
    (("latency101", "lemon"), "wefsanc101"),
    (("latency101", "a"), "latency101"),
    (("latency101", "zz"), "kzsdmbx101"),
    (("latency101", "AgentU"), "lgxrgwy101"),
    (("latency101", "keyboard"), "verfbcp101"),
    (("latency101", "AA"), "latency101"),
    (("buffer101", "key"), "lydpip101"),
    (("buffer101", "lemon"), "myrtrc101"),
    (("buffer101", "a"), "buffer101"),
    (("buffer101", "zz"), "ateedq101"),
    (("buffer101", "AgentU"), "bajsxl101"),
    (("buffer101", "keyboard"), "lydgsr101"),
    (("buffer101", "AA"), "buffer101"),
    (("queue101", "key"), "aycei101"),
    (("queue101", "lemon"), "byqir101"),
    (("queue101", "a"), "queue101"),
    (("queue101", "zz"), "ptdtd101"),
    (("queue101", "AgentU"), "qaihx101"),
    (("queue101", "keyboard"), "aycvs101"),
    (("queue101", "AA"), "queue101"),
    (("worker101", "key"), "gspuip101"),
    (("worker101", "lemon"), "hsdyrc101"),
    (("worker101", "a"), "worker101"),
    (("worker101", "zz"), "vnqjdq101"),
    (("worker101", "AgentU"), "wuvxxl101"),
    (("worker101", "keyboard"), "gsplsr101"),
    (("worker101", "AA"), "worker101"),
    (("kernel101", "key"), "uipxij101"),
    (("kernel101", "lemon"), "vidbrw101"),
    (("kernel101", "a"), "kernel101"),
    (("kernel101", "zz"), "jdqmdk101"),
    (("kernel101", "AgentU"), "kkvaxf101"),
    (("kernel101", "keyboard"), "uiposl101"),
    (("kernel101", "AA"), "kernel101"),
    (("signal101", "key"), "cmexej101"),
    (("signal101", "lemon"), "dmsbnw101"),
    (("signal101", "a"), "signal101"),
    (("signal101", "zz"), "rhfmzk101"),
    (("signal101", "AgentU"), "sokatf101"),
    (("signal101", "keyboard"), "cmeool101"),
    (("signal101", "AA"), "signal101"),
    (("packet101", "key"), "zeauir101"),
    (("packet101", "lemon"), "aeoyre101"),
    (("packet101", "a"), "packet101"),
    (("packet101", "zz"), "ozbjds101"),
    (("packet101", "AgentU"), "pggxxn101"),
    (("packet101", "keyboard"), "zealst101"),
    (("packet101", "AA"), "packet101"),
    (("router101", "key"), "bssdip101"),
    (("router101", "lemon"), "csghrc101"),
    (("router101", "a"), "router101"),
    (("router101", "zz"), "qntsdq101"),
    (("router101", "AgentU"), "ruygxl101"),
    (("router101", "keyboard"), "bssusr101"),
    (("router101", "AA"), "router101"),
    (("cluster101", "key"), "mpscxcb101"),
    (("cluster101", "lemon"), "npgggpv101"),
    (("cluster101", "a"), "cluster101"),
    (("cluster101", "zz"), "bktrsdq101"),
    (("cluster101", "AgentU"), "cryfmyr101"),
    (("cluster101", "keyboard"), "mpsthei101"),
    (("cluster101", "AA"), "cluster101"),
    (("mirror101", "key"), "wmpbsp101"),
    (("mirror101", "lemon"), "xmdfbc101"),
    (("mirror101", "a"), "mirror101"),
    (("mirror101", "zz"), "lhqqnq101"),
    (("mirror101", "AgentU"), "movehl101"),
    (("mirror101", "keyboard"), "wmpscr101"),
    (("mirror101", "AA"), "mirror101"),
    (("filter101", "key"), "pmjdip101"),
    (("filter101", "lemon"), "qmxhrc101"),
    (("filter101", "a"), "filter101"),
    (("filter101", "zz"), "ehksdq101"),
    (("filter101", "AgentU"), "fopgxl101"),
    (("filter101", "keyboard"), "pmjusr101"),
    (("filter101", "AA"), "filter101"),
    (("ranking101", "key"), "belumlq101"),
    (("ranking101", "lemon"), "cezyvyk101"),
    (("ranking101", "a"), "ranking101"),
    (("ranking101", "zz"), "qzmjhmf101"),
    (("ranking101", "AgentU"), "rgrxbhg101"),
    (("ranking101", "keyboard"), "bellwnx101"),
    (("ranking101", "AA"), "ranking101"),
    (("encoding101", "key"), "orayhgxk101"),
    (("encoding101", "lemon"), "procqtrs101"),
    (("encoding101", "a"), "encoding101"),
    (("encoding101", "zz"), "dmbnchmf101"),
    (("encoding101", "AgentU"), "etgbwcnm101"),
    (("encoding101", "keyboard"), "orapriej101"),
    (("encoding101", "AA"), "encoding101"),
    (("mapping101", "key"), "wenzmlq101"),
    (("mapping101", "lemon"), "xebdvyk101"),
    (("mapping101", "a"), "mapping101"),
    (("mapping101", "zz"), "lzoohmf101"),
    (("mapping101", "AgentU"), "mgtcbhg101"),
    (("mapping101", "keyboard"), "wenqwnx101"),
    (("mapping101", "AA"), "mapping101"),
    (("record101", "key"), "biayvb101"),
    (("record101", "lemon"), "cioceo101"),
    (("record101", "a"), "record101"),
    (("record101", "zz"), "qdbnqc101"),
    (("record101", "AgentU"), "rkgbkx101"),
    (("record101", "keyboard"), "biapfd101"),
    (("record101", "AA"), "record101"),
    (("candle101", "key"), "melnpc101"),
    (("candle101", "lemon"), "nezryp101"),
    (("candle101", "a"), "candle101"),
    (("candle101", "zz"), "bzmckd101"),
    (("candle101", "AgentU"), "cgrqey101"),
    (("candle101", "keyboard"), "meleze101"),
    (("candle101", "AA"), "candle101"),
    (("thread101", "key"), "dlpoeb101"),
    (("thread101", "lemon"), "eldsno101"),
    (("thread101", "a"), "thread101"),
    (("thread101", "zz"), "sgqdzc101"),
    (("thread101", "AgentU"), "tnvrtx101"),
    (("thread101", "keyboard"), "dlpfod101"),
    (("thread101", "AA"), "thread101"),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 101: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 101: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "a"),
        "round 101: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 101: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 101: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 101: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", "AA"),
        "round 101: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "key"),
        "bssxh 101: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 101: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "a"),
        "round 101: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 101: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 101: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 101: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", "AA"),
        "round 101: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 101: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 101: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "a"),
        "round 101: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 101: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 101: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 101: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", "AA"),
        "round 101: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 101: the processor reads the record then stops", "key"),
        "bssxh 101: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 101: the processor reads the record then stops", "lemon"),
        "csgbq 101: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 101: the processor reads the record then stops", "a"),
        "round 101: the processor reads the record then stops",
    ),
    (
        ("round 101: the processor reads the record then stops", "zz"),
        "qntmc 101: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 101: the processor reads the record then stops", "AgentU"),
        "ruyaw 101: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 101: the processor reads the record then stops", "keyboard"),
        "bssor 101: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 101: the processor reads the record then stops", "AA"),
        "round 101: the processor reads the record then stops",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "key"),
        "bssxh 101: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "lemon"),
        "csgbq 101: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "a"),
        "round 101: a worker pulls the next task from the queue",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "zz"),
        "qntmc 101: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 101: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "keyboard"),
        "bssor 101: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 101: a worker pulls the next task from the queue", "AA"),
        "round 101: a worker pulls the next task from the queue",
    ),
    (
        ("round 101: signals travel through the network layer", "key"),
        "bssxh 101: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 101: signals travel through the network layer", "lemon"),
        "csgbq 101: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 101: signals travel through the network layer", "a"),
        "round 101: signals travel through the network layer",
    ),
    (
        ("round 101: signals travel through the network layer", "zz"),
        "qntmc 101: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 101: signals travel through the network layer", "AgentU"),
        "ruyaw 101: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 101: signals travel through the network layer", "keyboard"),
        "bssor 101: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 101: signals travel through the network layer", "AA"),
        "round 101: signals travel through the network layer",
    ),
    (
        ("round 101: the gateway routes each request by policy", "key"),
        "bssxh 101: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 101: the gateway routes each request by policy", "lemon"),
        "csgbq 101: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 101: the gateway routes each request by policy", "a"),
        "round 101: the gateway routes each request by policy",
    ),
    (
        ("round 101: the gateway routes each request by policy", "zz"),
        "qntmc 101: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 101: the gateway routes each request by policy", "AgentU"),
        "ruyaw 101: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 101: the gateway routes each request by policy", "keyboard"),
        "bssor 101: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 101: the gateway routes each request by policy", "AA"),
        "round 101: the gateway routes each request by policy",
    ),
    (("round 101: memory grows until the buffer is full", "key"), "bssxh 101: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 101: memory grows until the buffer is full", "lemon"), "csgbq 101: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 101: memory grows until the buffer is full", "a"), "round 101: memory grows until the buffer is full"),
    (("round 101: memory grows until the buffer is full", "zz"), "qntmc 101: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 101: memory grows until the buffer is full", "AgentU"),
        "ruyaw 101: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 101: memory grows until the buffer is full", "keyboard"),
        "bssor 101: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 101: memory grows until the buffer is full", "AA"), "round 101: memory grows until the buffer is full"),
    (("round 101: the cluster mirrors every packet twice", "key"), "bssxh 101: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 101: the cluster mirrors every packet twice", "lemon"),
        "csgbq 101: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 101: the cluster mirrors every packet twice", "a"), "round 101: the cluster mirrors every packet twice"),
    (("round 101: the cluster mirrors every packet twice", "zz"), "qntmc 101: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 101: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 101: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 101: the cluster mirrors every packet twice", "keyboard"),
        "bssor 101: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 101: the cluster mirrors every packet twice", "AA"), "round 101: the cluster mirrors every packet twice"),
    (
        ("round 101: ranking uses tokens learned from the corpus", "key"),
        "bssxh 101: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 101: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", "a"),
        "round 101: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 101: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 101: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 101: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", "AA"),
        "round 101: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 101: a long session ends when the candle dies", "key"),
        "bssxh 101: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 101: a long session ends when the candle dies", "lemon"),
        "csgbq 101: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 101: a long session ends when the candle dies", "a"),
        "round 101: a long session ends when the candle dies",
    ),
    (
        ("round 101: a long session ends when the candle dies", "zz"),
        "qntmc 101: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 101: a long session ends when the candle dies", "AgentU"),
        "ruyaw 101: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 101: a long session ends when the candle dies", "keyboard"),
        "bssor 101: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 101: a long session ends when the candle dies", "AA"),
        "round 101: a long session ends when the candle dies",
    ),
    (("round 101: encode the prompt then map the result", "key"), "bssxh 101: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 101: encode the prompt then map the result", "lemon"), "csgbq 101: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 101: encode the prompt then map the result", "a"), "round 101: encode the prompt then map the result"),
    (("round 101: encode the prompt then map the result", "zz"), "qntmc 101: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 101: encode the prompt then map the result", "AgentU"),
        "ruyaw 101: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 101: encode the prompt then map the result", "keyboard"),
        "bssor 101: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 101: encode the prompt then map the result", "AA"), "round 101: encode the prompt then map the result"),
    (("round 101: the kernel wakes the worker at dawn", "key"), "bssxh 101: rri iovlop ukocc xfo ambocb er neux"),
    (("round 101: the kernel wakes the worker at dawn", "lemon"), "csgbq 101: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 101: the kernel wakes the worker at dawn", "a"), "round 101: the kernel wakes the worker at dawn"),
    (("round 101: the kernel wakes the worker at dawn", "zz"), "qntmc 101: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 101: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 101: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 101: the kernel wakes the worker at dawn", "keyboard"), "bssor 101: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 101: the kernel wakes the worker at dawn", "AA"), "round 101: the kernel wakes the worker at dawn"),
    (("round 101: service latency drops after the patch", "key"), "bssxh 101: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 101: service latency drops after the patch", "lemon"), "csgbq 101: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 101: service latency drops after the patch", "a"), "round 101: service latency drops after the patch"),
    (("round 101: service latency drops after the patch", "zz"), "qntmc 101: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 101: service latency drops after the patch", "AgentU"),
        "ruyaw 101: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 101: service latency drops after the patch", "keyboard"),
        "bssor 101: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 101: service latency drops after the patch", "AA"), "round 101: service latency drops after the patch"),
    (
        ("round 101: the library caches every vector it sees", "key"),
        "bssxh 101: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 101: the library caches every vector it sees", "lemon"),
        "csgbq 101: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 101: the library caches every vector it sees", "a"), "round 101: the library caches every vector it sees"),
    (
        ("round 101: the library caches every vector it sees", "zz"),
        "qntmc 101: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 101: the library caches every vector it sees", "AgentU"),
        "ruyaw 101: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 101: the library caches every vector it sees", "keyboard"),
        "bssor 101: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 101: the library caches every vector it sees", "AA"),
        "round 101: the library caches every vector it sees",
    ),
    (("round 101: agents argue then the debate resolves", "key"), "bssxh 101: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 101: agents argue then the debate resolves", "lemon"), "csgbq 101: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 101: agents argue then the debate resolves", "a"), "round 101: agents argue then the debate resolves"),
    (("round 101: agents argue then the debate resolves", "zz"), "qntmc 101: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 101: agents argue then the debate resolves", "AgentU"),
        "ruyaw 101: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 101: agents argue then the debate resolves", "keyboard"),
        "bssor 101: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 101: agents argue then the debate resolves", "AA"), "round 101: agents argue then the debate resolves"),
    (("round 101: the filter keeps only strong matches", "key"), "bssxh 101: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 101: the filter keeps only strong matches", "lemon"), "csgbq 101: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 101: the filter keeps only strong matches", "a"), "round 101: the filter keeps only strong matches"),
    (("round 101: the filter keeps only strong matches", "zz"), "qntmc 101: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 101: the filter keeps only strong matches", "AgentU"), "ruyaw 101: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 101: the filter keeps only strong matches", "keyboard"),
        "bssor 101: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 101: the filter keeps only strong matches", "AA"), "round 101: the filter keeps only strong matches"),
    (("round 101: the model answers with a short reply", "key"), "bssxh 101: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 101: the model answers with a short reply", "lemon"), "csgbq 101: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 101: the model answers with a short reply", "a"), "round 101: the model answers with a short reply"),
    (("round 101: the model answers with a short reply", "zz"), "qntmc 101: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 101: the model answers with a short reply", "AgentU"), "ruyaw 101: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 101: the model answers with a short reply", "keyboard"),
        "bssor 101: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 101: the model answers with a short reply", "AA"), "round 101: the model answers with a short reply"),
    (
        ("round 101: the recorder stores the reasoning trace", "key"),
        "bssxh 101: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 101: the recorder stores the reasoning trace", "lemon"),
        "csgbq 101: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 101: the recorder stores the reasoning trace", "a"), "round 101: the recorder stores the reasoning trace"),
    (
        ("round 101: the recorder stores the reasoning trace", "zz"),
        "qntmc 101: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 101: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 101: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 101: the recorder stores the reasoning trace", "keyboard"),
        "bssor 101: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 101: the recorder stores the reasoning trace", "AA"),
        "round 101: the recorder stores the reasoning trace",
    ),
    (("round 101: the angel watches the processor run", "key"), "bssxh 101: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 101: the angel watches the processor run", "lemon"), "csgbq 101: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 101: the angel watches the processor run", "a"), "round 101: the angel watches the processor run"),
    (("round 101: the angel watches the processor run", "zz"), "qntmc 101: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 101: the angel watches the processor run", "AgentU"), "ruyaw 101: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 101: the angel watches the processor run", "keyboard"), "bssor 101: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 101: the angel watches the processor run", "AA"), "round 101: the angel watches the processor run"),
    (("round 101: angle of the vector decides the match", "key"), "bssxh 101: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 101: angle of the vector decides the match", "lemon"), "csgbq 101: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 101: angle of the vector decides the match", "a"), "round 101: angle of the vector decides the match"),
    (("round 101: angle of the vector decides the match", "zz"), "qntmc 101: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 101: angle of the vector decides the match", "AgentU"),
        "ruyaw 101: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 101: angle of the vector decides the match", "keyboard"),
        "bssor 101: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 101: angle of the vector decides the match", "AA"), "round 101: angle of the vector decides the match"),
    (
        ("round 101: the candle burns twice as long at night", "key"),
        "bssxh 101: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 101: the candle burns twice as long at night", "lemon"),
        "csgbq 101: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 101: the candle burns twice as long at night", "a"), "round 101: the candle burns twice as long at night"),
    (
        ("round 101: the candle burns twice as long at night", "zz"),
        "qntmc 101: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 101: the candle burns twice as long at night", "AgentU"),
        "ruyaw 101: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 101: the candle burns twice as long at night", "keyboard"),
        "bssor 101: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 101: the candle burns twice as long at night", "AA"),
        "round 101: the candle burns twice as long at night",
    ),
    (("round 101: a mirror of the universe in one line", "key"), "bssxh 101: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 101: a mirror of the universe in one line", "lemon"), "csgbq 101: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 101: a mirror of the universe in one line", "a"), "round 101: a mirror of the universe in one line"),
    (("round 101: a mirror of the universe in one line", "zz"), "qntmc 101: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 101: a mirror of the universe in one line", "AgentU"), "ruyaw 101: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 101: a mirror of the universe in one line", "keyboard"),
        "bssor 101: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 101: a mirror of the universe in one line", "AA"), "round 101: a mirror of the universe in one line"),
    (("round 101: the queue drains before the storm", "key"), "bssxh 101: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 101: the queue drains before the storm", "lemon"), "csgbq 101: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 101: the queue drains before the storm", "a"), "round 101: the queue drains before the storm"),
    (("round 101: the queue drains before the storm", "zz"), "qntmc 101: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 101: the queue drains before the storm", "AgentU"), "ruyaw 101: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 101: the queue drains before the storm", "keyboard"), "bssor 101: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 101: the queue drains before the storm", "AA"), "round 101: the queue drains before the storm"),
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
