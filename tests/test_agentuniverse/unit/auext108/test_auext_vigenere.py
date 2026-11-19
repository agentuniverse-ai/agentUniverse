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
    (("kitten108", "key"), "umrdil108"),
    (("kitten108", "lemon"), "vmfhry108"),
    (("kitten108", "a"), "kitten108"),
    (("kitten108", "zz"), "jhssdm108"),
    (("kitten108", "AgentU"), "koxgxh108"),
    (("kitten108", "keyboard"), "umrusn108"),
    (("kitten108", "AA"), "kitten108"),
    (("sitting108", "key"), "cmrdmlq108"),
    (("sitting108", "lemon"), "dmfhvyk108"),
    (("sitting108", "a"), "sitting108"),
    (("sitting108", "zz"), "rhsshmf108"),
    (("sitting108", "AgentU"), "soxgbhg108"),
    (("sitting108", "keyboard"), "cmruwnx108"),
    (("sitting108", "AA"), "sitting108"),
    (("agent108", "key"), "kkcxx108"),
    (("agent108", "lemon"), "lkqbg108"),
    (("agent108", "a"), "agent108"),
    (("agent108", "zz"), "zfdms108"),
    (("agent108", "AgentU"), "amiam108"),
    (("agent108", "keyboard"), "kkcoh108"),
    (("agent108", "AA"), "agent108"),
    (("angle108", "key"), "krevi108"),
    (("angle108", "lemon"), "lrszr108"),
    (("angle108", "a"), "angle108"),
    (("angle108", "zz"), "zmfkd108"),
    (("angle108", "AgentU"), "atkyx108"),
    (("angle108", "keyboard"), "krems108"),
    (("angle108", "AA"), "angle108"),
    (("universe108", "key"), "ergfipci108"),
    (("universe108", "lemon"), "frujrcwq108"),
    (("universe108", "a"), "universe108"),
    (("universe108", "zz"), "tmhudqrd108"),
    (("universe108", "AgentU"), "utmixlsk108"),
    (("universe108", "keyboard"), "ergwsrjh108"),
    (("universe108", "AA"), "universe108"),
    (("memory108", "key"), "wikyvw108"),
    (("memory108", "lemon"), "xiycej108"),
    (("memory108", "a"), "memory108"),
    (("memory108", "zz"), "ldlnqx108"),
    (("memory108", "AgentU"), "mkqbks108"),
    (("memory108", "keyboard"), "wikpfy108"),
    (("memory108", "AA"), "memory108"),
    (("stream108", "key"), "cxpoek108"),
    (("stream108", "lemon"), "dxdsnx108"),
    (("stream108", "a"), "stream108"),
    (("stream108", "zz"), "rsqdzl108"),
    (("stream108", "AgentU"), "szvrtg108"),
    (("stream108", "keyboard"), "cxpfom108"),
    (("stream108", "AA"), "stream108"),
    (("context108", "key"), "msldivd108"),
    (("context108", "lemon"), "nszhrix108"),
    (("context108", "a"), "context108"),
    (("context108", "zz"), "bnmsdws108"),
    (("context108", "AgentU"), "curgxrt108"),
    (("context108", "keyboard"), "mslusxk108"),
    (("context108", "AA"), "context108"),
    (("knowledge108", "key"), "urmgpcnkc108"),
    (("knowledge108", "lemon"), "vrakyphss108"),
    (("knowledge108", "a"), "knowledge108"),
    (("knowledge108", "zz"), "jmnvkdcfd108"),
    (("knowledge108", "AgentU"), "ktsjeydmi108"),
    (("knowledge108", "keyboard"), "urmxzeujo108"),
    (("knowledge108", "AA"), "knowledge108"),
    (("vector108", "key"), "fiadsp108"),
    (("vector108", "lemon"), "giohbc108"),
    (("vector108", "a"), "vector108"),
    (("vector108", "zz"), "udbsnq108"),
    (("vector108", "AgentU"), "vkgghl108"),
    (("vector108", "keyboard"), "fiaucr108"),
    (("vector108", "AA"), "vector108"),
    (("processor108", "key"), "zvmmiqcsp108"),
    (("processor108", "lemon"), "avaqrdwaf108"),
    (("processor108", "a"), "processor108"),
    (("processor108", "zz"), "oqnbdrrnq108"),
    (("processor108", "AgentU"), "pxspxmsuv108"),
    (("processor108", "keyboard"), "zvmdssjrb108"),
    (("processor108", "AA"), "processor108"),
    (("reasoning108", "key"), "biycslsre108"),
    (("reasoning108", "lemon"), "cimgbymzu108"),
    (("reasoning108", "a"), "reasoning108"),
    (("reasoning108", "zz"), "qdzrnmhmf108"),
    (("reasoning108", "AgentU"), "rkefhhitk108"),
    (("reasoning108", "keyboard"), "biytcnzqq108"),
    (("reasoning108", "AA"), "reasoning108"),
    (("machine108", "key"), "wearmlo108"),
    (("machine108", "lemon"), "xeovvyi108"),
    (("machine108", "a"), "machine108"),
    (("machine108", "zz"), "lzbghmd108"),
    (("machine108", "AgentU"), "mggubhe108"),
    (("machine108", "keyboard"), "weaiwnv108"),
    (("machine108", "AA"), "machine108"),
    (("learning108", "key"), "viybrgxk108"),
    (("learning108", "lemon"), "wimfatrs108"),
    (("learning108", "a"), "learning108"),
    (("learning108", "zz"), "kdzqmhmf108"),
    (("learning108", "AgentU"), "lkeegcnm108"),
    (("learning108", "keyboard"), "viysbiej108"),
    (("learning108", "AA"), "learning108"),
    (("model108", "key"), "wsbop108"),
    (("model108", "lemon"), "xspsy108"),
    (("model108", "a"), "model108"),
    (("model108", "zz"), "lncdk108"),
    (("model108", "AgentU"), "muhre108"),
    (("model108", "keyboard"), "wsbfz108"),
    (("model108", "AA"), "model108"),
    (("token108", "key"), "dsior108"),
    (("token108", "lemon"), "eswsa108"),
    (("token108", "a"), "token108"),
    (("token108", "zz"), "snjdm108"),
    (("token108", "AgentU"), "tuorg108"),
    (("token108", "keyboard"), "dsifb108"),
    (("token108", "AA"), "token108"),
    (("prompt108", "key"), "zvmwtr108"),
    (("prompt108", "lemon"), "avaace108"),
    (("prompt108", "a"), "prompt108"),
    (("prompt108", "zz"), "oqnlos108"),
    (("prompt108", "AgentU"), "pxszin108"),
    (("prompt108", "keyboard"), "zvmndt108"),
    (("prompt108", "AA"), "prompt108"),
    (("session108", "key"), "ciqcmmx108"),
    (("session108", "lemon"), "diegvzr108"),
    (("session108", "a"), "session108"),
    (("session108", "zz"), "rdrrhnm108"),
    (("session108", "AgentU"), "skwfbin108"),
    (("session108", "keyboard"), "ciqtwoe108"),
    (("session108", "AA"), "session108"),
    (("library108", "key"), "vmzbepi108"),
    (("library108", "lemon"), "wmnfncc108"),
    (("library108", "a"), "library108"),
    (("library108", "zz"), "khaqzqx108"),
    (("library108", "AgentU"), "lofetly108"),
    (("library108", "keyboard"), "vmzsorp108"),
    (("library108", "AA"), "library108"),
    (("service108", "key"), "cipfmao108"),
    (("service108", "lemon"), "didjvni108"),
    (("service108", "a"), "service108"),
    (("service108", "zz"), "rdquhbd108"),
    (("service108", "AgentU"), "skvibwe108"),
    (("service108", "keyboard"), "cipwwcv108"),
    (("service108", "AA"), "service108"),
    (("gateway108", "key"), "qeroayi108"),
    (("gateway108", "lemon"), "refsjlc108"),
    (("gateway108", "a"), "gateway108"),
    (("gateway108", "zz"), "fzsdvzx108"),
    (("gateway108", "AgentU"), "ggxrpuy108"),
    (("gateway108", "keyboard"), "qerfkap108"),
    (("gateway108", "AA"), "gateway108"),
    (("storage108", "key"), "cxmbeeo108"),
    (("storage108", "lemon"), "dxafnri108"),
    (("storage108", "a"), "storage108"),
    (("storage108", "zz"), "rsnqzfd108"),
    (("storage108", "AgentU"), "szsetae108"),
    (("storage108", "keyboard"), "cxmsogv108"),
    (("storage108", "AA"), "storage108"),
    (("network108", "key"), "xirgspu108"),
    (("network108", "lemon"), "yifkbco108"),
    (("network108", "a"), "network108"),
    (("network108", "zz"), "mdsvnqj108"),
    (("network108", "AgentU"), "nkxjhlk108"),
    (("network108", "keyboard"), "xirxcrb108"),
    (("network108", "AA"), "network108"),
    (("latency108", "key"), "verorai108"),
    (("latency108", "lemon"), "wefsanc108"),
    (("latency108", "a"), "latency108"),
    (("latency108", "zz"), "kzsdmbx108"),
    (("latency108", "AgentU"), "lgxrgwy108"),
    (("latency108", "keyboard"), "verfbcp108"),
    (("latency108", "AA"), "latency108"),
    (("buffer108", "key"), "lydpip108"),
    (("buffer108", "lemon"), "myrtrc108"),
    (("buffer108", "a"), "buffer108"),
    (("buffer108", "zz"), "ateedq108"),
    (("buffer108", "AgentU"), "bajsxl108"),
    (("buffer108", "keyboard"), "lydgsr108"),
    (("buffer108", "AA"), "buffer108"),
    (("queue108", "key"), "aycei108"),
    (("queue108", "lemon"), "byqir108"),
    (("queue108", "a"), "queue108"),
    (("queue108", "zz"), "ptdtd108"),
    (("queue108", "AgentU"), "qaihx108"),
    (("queue108", "keyboard"), "aycvs108"),
    (("queue108", "AA"), "queue108"),
    (("worker108", "key"), "gspuip108"),
    (("worker108", "lemon"), "hsdyrc108"),
    (("worker108", "a"), "worker108"),
    (("worker108", "zz"), "vnqjdq108"),
    (("worker108", "AgentU"), "wuvxxl108"),
    (("worker108", "keyboard"), "gsplsr108"),
    (("worker108", "AA"), "worker108"),
    (("kernel108", "key"), "uipxij108"),
    (("kernel108", "lemon"), "vidbrw108"),
    (("kernel108", "a"), "kernel108"),
    (("kernel108", "zz"), "jdqmdk108"),
    (("kernel108", "AgentU"), "kkvaxf108"),
    (("kernel108", "keyboard"), "uiposl108"),
    (("kernel108", "AA"), "kernel108"),
    (("signal108", "key"), "cmexej108"),
    (("signal108", "lemon"), "dmsbnw108"),
    (("signal108", "a"), "signal108"),
    (("signal108", "zz"), "rhfmzk108"),
    (("signal108", "AgentU"), "sokatf108"),
    (("signal108", "keyboard"), "cmeool108"),
    (("signal108", "AA"), "signal108"),
    (("packet108", "key"), "zeauir108"),
    (("packet108", "lemon"), "aeoyre108"),
    (("packet108", "a"), "packet108"),
    (("packet108", "zz"), "ozbjds108"),
    (("packet108", "AgentU"), "pggxxn108"),
    (("packet108", "keyboard"), "zealst108"),
    (("packet108", "AA"), "packet108"),
    (("router108", "key"), "bssdip108"),
    (("router108", "lemon"), "csghrc108"),
    (("router108", "a"), "router108"),
    (("router108", "zz"), "qntsdq108"),
    (("router108", "AgentU"), "ruygxl108"),
    (("router108", "keyboard"), "bssusr108"),
    (("router108", "AA"), "router108"),
    (("cluster108", "key"), "mpscxcb108"),
    (("cluster108", "lemon"), "npgggpv108"),
    (("cluster108", "a"), "cluster108"),
    (("cluster108", "zz"), "bktrsdq108"),
    (("cluster108", "AgentU"), "cryfmyr108"),
    (("cluster108", "keyboard"), "mpsthei108"),
    (("cluster108", "AA"), "cluster108"),
    (("mirror108", "key"), "wmpbsp108"),
    (("mirror108", "lemon"), "xmdfbc108"),
    (("mirror108", "a"), "mirror108"),
    (("mirror108", "zz"), "lhqqnq108"),
    (("mirror108", "AgentU"), "movehl108"),
    (("mirror108", "keyboard"), "wmpscr108"),
    (("mirror108", "AA"), "mirror108"),
    (("filter108", "key"), "pmjdip108"),
    (("filter108", "lemon"), "qmxhrc108"),
    (("filter108", "a"), "filter108"),
    (("filter108", "zz"), "ehksdq108"),
    (("filter108", "AgentU"), "fopgxl108"),
    (("filter108", "keyboard"), "pmjusr108"),
    (("filter108", "AA"), "filter108"),
    (("ranking108", "key"), "belumlq108"),
    (("ranking108", "lemon"), "cezyvyk108"),
    (("ranking108", "a"), "ranking108"),
    (("ranking108", "zz"), "qzmjhmf108"),
    (("ranking108", "AgentU"), "rgrxbhg108"),
    (("ranking108", "keyboard"), "bellwnx108"),
    (("ranking108", "AA"), "ranking108"),
    (("encoding108", "key"), "orayhgxk108"),
    (("encoding108", "lemon"), "procqtrs108"),
    (("encoding108", "a"), "encoding108"),
    (("encoding108", "zz"), "dmbnchmf108"),
    (("encoding108", "AgentU"), "etgbwcnm108"),
    (("encoding108", "keyboard"), "orapriej108"),
    (("encoding108", "AA"), "encoding108"),
    (("mapping108", "key"), "wenzmlq108"),
    (("mapping108", "lemon"), "xebdvyk108"),
    (("mapping108", "a"), "mapping108"),
    (("mapping108", "zz"), "lzoohmf108"),
    (("mapping108", "AgentU"), "mgtcbhg108"),
    (("mapping108", "keyboard"), "wenqwnx108"),
    (("mapping108", "AA"), "mapping108"),
    (("record108", "key"), "biayvb108"),
    (("record108", "lemon"), "cioceo108"),
    (("record108", "a"), "record108"),
    (("record108", "zz"), "qdbnqc108"),
    (("record108", "AgentU"), "rkgbkx108"),
    (("record108", "keyboard"), "biapfd108"),
    (("record108", "AA"), "record108"),
    (("candle108", "key"), "melnpc108"),
    (("candle108", "lemon"), "nezryp108"),
    (("candle108", "a"), "candle108"),
    (("candle108", "zz"), "bzmckd108"),
    (("candle108", "AgentU"), "cgrqey108"),
    (("candle108", "keyboard"), "meleze108"),
    (("candle108", "AA"), "candle108"),
    (("thread108", "key"), "dlpoeb108"),
    (("thread108", "lemon"), "eldsno108"),
    (("thread108", "a"), "thread108"),
    (("thread108", "zz"), "sgqdzc108"),
    (("thread108", "AgentU"), "tnvrtx108"),
    (("thread108", "keyboard"), "dlpfod108"),
    (("thread108", "AA"), "thread108"),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 108: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 108: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "a"),
        "round 108: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 108: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 108: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 108: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", "AA"),
        "round 108: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "key"),
        "bssxh 108: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 108: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "a"),
        "round 108: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 108: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 108: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 108: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", "AA"),
        "round 108: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 108: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 108: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "a"),
        "round 108: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 108: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 108: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 108: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", "AA"),
        "round 108: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 108: the processor reads the record then stops", "key"),
        "bssxh 108: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 108: the processor reads the record then stops", "lemon"),
        "csgbq 108: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 108: the processor reads the record then stops", "a"),
        "round 108: the processor reads the record then stops",
    ),
    (
        ("round 108: the processor reads the record then stops", "zz"),
        "qntmc 108: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 108: the processor reads the record then stops", "AgentU"),
        "ruyaw 108: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 108: the processor reads the record then stops", "keyboard"),
        "bssor 108: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 108: the processor reads the record then stops", "AA"),
        "round 108: the processor reads the record then stops",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "key"),
        "bssxh 108: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "lemon"),
        "csgbq 108: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "a"),
        "round 108: a worker pulls the next task from the queue",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "zz"),
        "qntmc 108: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 108: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "keyboard"),
        "bssor 108: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 108: a worker pulls the next task from the queue", "AA"),
        "round 108: a worker pulls the next task from the queue",
    ),
    (
        ("round 108: signals travel through the network layer", "key"),
        "bssxh 108: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 108: signals travel through the network layer", "lemon"),
        "csgbq 108: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 108: signals travel through the network layer", "a"),
        "round 108: signals travel through the network layer",
    ),
    (
        ("round 108: signals travel through the network layer", "zz"),
        "qntmc 108: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 108: signals travel through the network layer", "AgentU"),
        "ruyaw 108: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 108: signals travel through the network layer", "keyboard"),
        "bssor 108: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 108: signals travel through the network layer", "AA"),
        "round 108: signals travel through the network layer",
    ),
    (
        ("round 108: the gateway routes each request by policy", "key"),
        "bssxh 108: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 108: the gateway routes each request by policy", "lemon"),
        "csgbq 108: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 108: the gateway routes each request by policy", "a"),
        "round 108: the gateway routes each request by policy",
    ),
    (
        ("round 108: the gateway routes each request by policy", "zz"),
        "qntmc 108: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 108: the gateway routes each request by policy", "AgentU"),
        "ruyaw 108: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 108: the gateway routes each request by policy", "keyboard"),
        "bssor 108: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 108: the gateway routes each request by policy", "AA"),
        "round 108: the gateway routes each request by policy",
    ),
    (("round 108: memory grows until the buffer is full", "key"), "bssxh 108: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 108: memory grows until the buffer is full", "lemon"), "csgbq 108: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 108: memory grows until the buffer is full", "a"), "round 108: memory grows until the buffer is full"),
    (("round 108: memory grows until the buffer is full", "zz"), "qntmc 108: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 108: memory grows until the buffer is full", "AgentU"),
        "ruyaw 108: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 108: memory grows until the buffer is full", "keyboard"),
        "bssor 108: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 108: memory grows until the buffer is full", "AA"), "round 108: memory grows until the buffer is full"),
    (("round 108: the cluster mirrors every packet twice", "key"), "bssxh 108: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 108: the cluster mirrors every packet twice", "lemon"),
        "csgbq 108: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 108: the cluster mirrors every packet twice", "a"), "round 108: the cluster mirrors every packet twice"),
    (("round 108: the cluster mirrors every packet twice", "zz"), "qntmc 108: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 108: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 108: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 108: the cluster mirrors every packet twice", "keyboard"),
        "bssor 108: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 108: the cluster mirrors every packet twice", "AA"), "round 108: the cluster mirrors every packet twice"),
    (
        ("round 108: ranking uses tokens learned from the corpus", "key"),
        "bssxh 108: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 108: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", "a"),
        "round 108: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 108: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 108: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 108: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", "AA"),
        "round 108: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 108: a long session ends when the candle dies", "key"),
        "bssxh 108: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 108: a long session ends when the candle dies", "lemon"),
        "csgbq 108: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 108: a long session ends when the candle dies", "a"),
        "round 108: a long session ends when the candle dies",
    ),
    (
        ("round 108: a long session ends when the candle dies", "zz"),
        "qntmc 108: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 108: a long session ends when the candle dies", "AgentU"),
        "ruyaw 108: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 108: a long session ends when the candle dies", "keyboard"),
        "bssor 108: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 108: a long session ends when the candle dies", "AA"),
        "round 108: a long session ends when the candle dies",
    ),
    (("round 108: encode the prompt then map the result", "key"), "bssxh 108: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 108: encode the prompt then map the result", "lemon"), "csgbq 108: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 108: encode the prompt then map the result", "a"), "round 108: encode the prompt then map the result"),
    (("round 108: encode the prompt then map the result", "zz"), "qntmc 108: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 108: encode the prompt then map the result", "AgentU"),
        "ruyaw 108: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 108: encode the prompt then map the result", "keyboard"),
        "bssor 108: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 108: encode the prompt then map the result", "AA"), "round 108: encode the prompt then map the result"),
    (("round 108: the kernel wakes the worker at dawn", "key"), "bssxh 108: rri iovlop ukocc xfo ambocb er neux"),
    (("round 108: the kernel wakes the worker at dawn", "lemon"), "csgbq 108: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 108: the kernel wakes the worker at dawn", "a"), "round 108: the kernel wakes the worker at dawn"),
    (("round 108: the kernel wakes the worker at dawn", "zz"), "qntmc 108: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 108: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 108: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 108: the kernel wakes the worker at dawn", "keyboard"), "bssor 108: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 108: the kernel wakes the worker at dawn", "AA"), "round 108: the kernel wakes the worker at dawn"),
    (("round 108: service latency drops after the patch", "key"), "bssxh 108: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 108: service latency drops after the patch", "lemon"), "csgbq 108: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 108: service latency drops after the patch", "a"), "round 108: service latency drops after the patch"),
    (("round 108: service latency drops after the patch", "zz"), "qntmc 108: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 108: service latency drops after the patch", "AgentU"),
        "ruyaw 108: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 108: service latency drops after the patch", "keyboard"),
        "bssor 108: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 108: service latency drops after the patch", "AA"), "round 108: service latency drops after the patch"),
    (
        ("round 108: the library caches every vector it sees", "key"),
        "bssxh 108: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 108: the library caches every vector it sees", "lemon"),
        "csgbq 108: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 108: the library caches every vector it sees", "a"), "round 108: the library caches every vector it sees"),
    (
        ("round 108: the library caches every vector it sees", "zz"),
        "qntmc 108: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 108: the library caches every vector it sees", "AgentU"),
        "ruyaw 108: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 108: the library caches every vector it sees", "keyboard"),
        "bssor 108: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 108: the library caches every vector it sees", "AA"),
        "round 108: the library caches every vector it sees",
    ),
    (("round 108: agents argue then the debate resolves", "key"), "bssxh 108: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 108: agents argue then the debate resolves", "lemon"), "csgbq 108: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 108: agents argue then the debate resolves", "a"), "round 108: agents argue then the debate resolves"),
    (("round 108: agents argue then the debate resolves", "zz"), "qntmc 108: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 108: agents argue then the debate resolves", "AgentU"),
        "ruyaw 108: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 108: agents argue then the debate resolves", "keyboard"),
        "bssor 108: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 108: agents argue then the debate resolves", "AA"), "round 108: agents argue then the debate resolves"),
    (("round 108: the filter keeps only strong matches", "key"), "bssxh 108: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 108: the filter keeps only strong matches", "lemon"), "csgbq 108: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 108: the filter keeps only strong matches", "a"), "round 108: the filter keeps only strong matches"),
    (("round 108: the filter keeps only strong matches", "zz"), "qntmc 108: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 108: the filter keeps only strong matches", "AgentU"), "ruyaw 108: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 108: the filter keeps only strong matches", "keyboard"),
        "bssor 108: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 108: the filter keeps only strong matches", "AA"), "round 108: the filter keeps only strong matches"),
    (("round 108: the model answers with a short reply", "key"), "bssxh 108: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 108: the model answers with a short reply", "lemon"), "csgbq 108: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 108: the model answers with a short reply", "a"), "round 108: the model answers with a short reply"),
    (("round 108: the model answers with a short reply", "zz"), "qntmc 108: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 108: the model answers with a short reply", "AgentU"), "ruyaw 108: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 108: the model answers with a short reply", "keyboard"),
        "bssor 108: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 108: the model answers with a short reply", "AA"), "round 108: the model answers with a short reply"),
    (
        ("round 108: the recorder stores the reasoning trace", "key"),
        "bssxh 108: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 108: the recorder stores the reasoning trace", "lemon"),
        "csgbq 108: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 108: the recorder stores the reasoning trace", "a"), "round 108: the recorder stores the reasoning trace"),
    (
        ("round 108: the recorder stores the reasoning trace", "zz"),
        "qntmc 108: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 108: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 108: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 108: the recorder stores the reasoning trace", "keyboard"),
        "bssor 108: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 108: the recorder stores the reasoning trace", "AA"),
        "round 108: the recorder stores the reasoning trace",
    ),
    (("round 108: the angel watches the processor run", "key"), "bssxh 108: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 108: the angel watches the processor run", "lemon"), "csgbq 108: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 108: the angel watches the processor run", "a"), "round 108: the angel watches the processor run"),
    (("round 108: the angel watches the processor run", "zz"), "qntmc 108: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 108: the angel watches the processor run", "AgentU"), "ruyaw 108: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 108: the angel watches the processor run", "keyboard"), "bssor 108: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 108: the angel watches the processor run", "AA"), "round 108: the angel watches the processor run"),
    (("round 108: angle of the vector decides the match", "key"), "bssxh 108: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 108: angle of the vector decides the match", "lemon"), "csgbq 108: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 108: angle of the vector decides the match", "a"), "round 108: angle of the vector decides the match"),
    (("round 108: angle of the vector decides the match", "zz"), "qntmc 108: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 108: angle of the vector decides the match", "AgentU"),
        "ruyaw 108: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 108: angle of the vector decides the match", "keyboard"),
        "bssor 108: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 108: angle of the vector decides the match", "AA"), "round 108: angle of the vector decides the match"),
    (
        ("round 108: the candle burns twice as long at night", "key"),
        "bssxh 108: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 108: the candle burns twice as long at night", "lemon"),
        "csgbq 108: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 108: the candle burns twice as long at night", "a"), "round 108: the candle burns twice as long at night"),
    (
        ("round 108: the candle burns twice as long at night", "zz"),
        "qntmc 108: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 108: the candle burns twice as long at night", "AgentU"),
        "ruyaw 108: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 108: the candle burns twice as long at night", "keyboard"),
        "bssor 108: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 108: the candle burns twice as long at night", "AA"),
        "round 108: the candle burns twice as long at night",
    ),
    (("round 108: a mirror of the universe in one line", "key"), "bssxh 108: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 108: a mirror of the universe in one line", "lemon"), "csgbq 108: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 108: a mirror of the universe in one line", "a"), "round 108: a mirror of the universe in one line"),
    (("round 108: a mirror of the universe in one line", "zz"), "qntmc 108: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 108: a mirror of the universe in one line", "AgentU"), "ruyaw 108: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 108: a mirror of the universe in one line", "keyboard"),
        "bssor 108: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 108: a mirror of the universe in one line", "AA"), "round 108: a mirror of the universe in one line"),
    (("round 108: the queue drains before the storm", "key"), "bssxh 108: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 108: the queue drains before the storm", "lemon"), "csgbq 108: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 108: the queue drains before the storm", "a"), "round 108: the queue drains before the storm"),
    (("round 108: the queue drains before the storm", "zz"), "qntmc 108: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 108: the queue drains before the storm", "AgentU"), "ruyaw 108: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 108: the queue drains before the storm", "keyboard"), "bssor 108: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 108: the queue drains before the storm", "AA"), "round 108: the queue drains before the storm"),
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
