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
    (("kitten748", "key"), "umrdil748"),
    (("kitten748", "lemon"), "vmfhry748"),
    (("kitten748", "a"), "kitten748"),
    (("kitten748", "zz"), "jhssdm748"),
    (("kitten748", "AgentU"), "koxgxh748"),
    (("kitten748", "keyboard"), "umrusn748"),
    (("kitten748", "AA"), "kitten748"),
    (("sitting748", "key"), "cmrdmlq748"),
    (("sitting748", "lemon"), "dmfhvyk748"),
    (("sitting748", "a"), "sitting748"),
    (("sitting748", "zz"), "rhsshmf748"),
    (("sitting748", "AgentU"), "soxgbhg748"),
    (("sitting748", "keyboard"), "cmruwnx748"),
    (("sitting748", "AA"), "sitting748"),
    (("agent748", "key"), "kkcxx748"),
    (("agent748", "lemon"), "lkqbg748"),
    (("agent748", "a"), "agent748"),
    (("agent748", "zz"), "zfdms748"),
    (("agent748", "AgentU"), "amiam748"),
    (("agent748", "keyboard"), "kkcoh748"),
    (("agent748", "AA"), "agent748"),
    (("angle748", "key"), "krevi748"),
    (("angle748", "lemon"), "lrszr748"),
    (("angle748", "a"), "angle748"),
    (("angle748", "zz"), "zmfkd748"),
    (("angle748", "AgentU"), "atkyx748"),
    (("angle748", "keyboard"), "krems748"),
    (("angle748", "AA"), "angle748"),
    (("universe748", "key"), "ergfipci748"),
    (("universe748", "lemon"), "frujrcwq748"),
    (("universe748", "a"), "universe748"),
    (("universe748", "zz"), "tmhudqrd748"),
    (("universe748", "AgentU"), "utmixlsk748"),
    (("universe748", "keyboard"), "ergwsrjh748"),
    (("universe748", "AA"), "universe748"),
    (("memory748", "key"), "wikyvw748"),
    (("memory748", "lemon"), "xiycej748"),
    (("memory748", "a"), "memory748"),
    (("memory748", "zz"), "ldlnqx748"),
    (("memory748", "AgentU"), "mkqbks748"),
    (("memory748", "keyboard"), "wikpfy748"),
    (("memory748", "AA"), "memory748"),
    (("stream748", "key"), "cxpoek748"),
    (("stream748", "lemon"), "dxdsnx748"),
    (("stream748", "a"), "stream748"),
    (("stream748", "zz"), "rsqdzl748"),
    (("stream748", "AgentU"), "szvrtg748"),
    (("stream748", "keyboard"), "cxpfom748"),
    (("stream748", "AA"), "stream748"),
    (("context748", "key"), "msldivd748"),
    (("context748", "lemon"), "nszhrix748"),
    (("context748", "a"), "context748"),
    (("context748", "zz"), "bnmsdws748"),
    (("context748", "AgentU"), "curgxrt748"),
    (("context748", "keyboard"), "mslusxk748"),
    (("context748", "AA"), "context748"),
    (("knowledge748", "key"), "urmgpcnkc748"),
    (("knowledge748", "lemon"), "vrakyphss748"),
    (("knowledge748", "a"), "knowledge748"),
    (("knowledge748", "zz"), "jmnvkdcfd748"),
    (("knowledge748", "AgentU"), "ktsjeydmi748"),
    (("knowledge748", "keyboard"), "urmxzeujo748"),
    (("knowledge748", "AA"), "knowledge748"),
    (("vector748", "key"), "fiadsp748"),
    (("vector748", "lemon"), "giohbc748"),
    (("vector748", "a"), "vector748"),
    (("vector748", "zz"), "udbsnq748"),
    (("vector748", "AgentU"), "vkgghl748"),
    (("vector748", "keyboard"), "fiaucr748"),
    (("vector748", "AA"), "vector748"),
    (("processor748", "key"), "zvmmiqcsp748"),
    (("processor748", "lemon"), "avaqrdwaf748"),
    (("processor748", "a"), "processor748"),
    (("processor748", "zz"), "oqnbdrrnq748"),
    (("processor748", "AgentU"), "pxspxmsuv748"),
    (("processor748", "keyboard"), "zvmdssjrb748"),
    (("processor748", "AA"), "processor748"),
    (("reasoning748", "key"), "biycslsre748"),
    (("reasoning748", "lemon"), "cimgbymzu748"),
    (("reasoning748", "a"), "reasoning748"),
    (("reasoning748", "zz"), "qdzrnmhmf748"),
    (("reasoning748", "AgentU"), "rkefhhitk748"),
    (("reasoning748", "keyboard"), "biytcnzqq748"),
    (("reasoning748", "AA"), "reasoning748"),
    (("machine748", "key"), "wearmlo748"),
    (("machine748", "lemon"), "xeovvyi748"),
    (("machine748", "a"), "machine748"),
    (("machine748", "zz"), "lzbghmd748"),
    (("machine748", "AgentU"), "mggubhe748"),
    (("machine748", "keyboard"), "weaiwnv748"),
    (("machine748", "AA"), "machine748"),
    (("learning748", "key"), "viybrgxk748"),
    (("learning748", "lemon"), "wimfatrs748"),
    (("learning748", "a"), "learning748"),
    (("learning748", "zz"), "kdzqmhmf748"),
    (("learning748", "AgentU"), "lkeegcnm748"),
    (("learning748", "keyboard"), "viysbiej748"),
    (("learning748", "AA"), "learning748"),
    (("model748", "key"), "wsbop748"),
    (("model748", "lemon"), "xspsy748"),
    (("model748", "a"), "model748"),
    (("model748", "zz"), "lncdk748"),
    (("model748", "AgentU"), "muhre748"),
    (("model748", "keyboard"), "wsbfz748"),
    (("model748", "AA"), "model748"),
    (("token748", "key"), "dsior748"),
    (("token748", "lemon"), "eswsa748"),
    (("token748", "a"), "token748"),
    (("token748", "zz"), "snjdm748"),
    (("token748", "AgentU"), "tuorg748"),
    (("token748", "keyboard"), "dsifb748"),
    (("token748", "AA"), "token748"),
    (("prompt748", "key"), "zvmwtr748"),
    (("prompt748", "lemon"), "avaace748"),
    (("prompt748", "a"), "prompt748"),
    (("prompt748", "zz"), "oqnlos748"),
    (("prompt748", "AgentU"), "pxszin748"),
    (("prompt748", "keyboard"), "zvmndt748"),
    (("prompt748", "AA"), "prompt748"),
    (("session748", "key"), "ciqcmmx748"),
    (("session748", "lemon"), "diegvzr748"),
    (("session748", "a"), "session748"),
    (("session748", "zz"), "rdrrhnm748"),
    (("session748", "AgentU"), "skwfbin748"),
    (("session748", "keyboard"), "ciqtwoe748"),
    (("session748", "AA"), "session748"),
    (("library748", "key"), "vmzbepi748"),
    (("library748", "lemon"), "wmnfncc748"),
    (("library748", "a"), "library748"),
    (("library748", "zz"), "khaqzqx748"),
    (("library748", "AgentU"), "lofetly748"),
    (("library748", "keyboard"), "vmzsorp748"),
    (("library748", "AA"), "library748"),
    (("service748", "key"), "cipfmao748"),
    (("service748", "lemon"), "didjvni748"),
    (("service748", "a"), "service748"),
    (("service748", "zz"), "rdquhbd748"),
    (("service748", "AgentU"), "skvibwe748"),
    (("service748", "keyboard"), "cipwwcv748"),
    (("service748", "AA"), "service748"),
    (("gateway748", "key"), "qeroayi748"),
    (("gateway748", "lemon"), "refsjlc748"),
    (("gateway748", "a"), "gateway748"),
    (("gateway748", "zz"), "fzsdvzx748"),
    (("gateway748", "AgentU"), "ggxrpuy748"),
    (("gateway748", "keyboard"), "qerfkap748"),
    (("gateway748", "AA"), "gateway748"),
    (("storage748", "key"), "cxmbeeo748"),
    (("storage748", "lemon"), "dxafnri748"),
    (("storage748", "a"), "storage748"),
    (("storage748", "zz"), "rsnqzfd748"),
    (("storage748", "AgentU"), "szsetae748"),
    (("storage748", "keyboard"), "cxmsogv748"),
    (("storage748", "AA"), "storage748"),
    (("network748", "key"), "xirgspu748"),
    (("network748", "lemon"), "yifkbco748"),
    (("network748", "a"), "network748"),
    (("network748", "zz"), "mdsvnqj748"),
    (("network748", "AgentU"), "nkxjhlk748"),
    (("network748", "keyboard"), "xirxcrb748"),
    (("network748", "AA"), "network748"),
    (("latency748", "key"), "verorai748"),
    (("latency748", "lemon"), "wefsanc748"),
    (("latency748", "a"), "latency748"),
    (("latency748", "zz"), "kzsdmbx748"),
    (("latency748", "AgentU"), "lgxrgwy748"),
    (("latency748", "keyboard"), "verfbcp748"),
    (("latency748", "AA"), "latency748"),
    (("buffer748", "key"), "lydpip748"),
    (("buffer748", "lemon"), "myrtrc748"),
    (("buffer748", "a"), "buffer748"),
    (("buffer748", "zz"), "ateedq748"),
    (("buffer748", "AgentU"), "bajsxl748"),
    (("buffer748", "keyboard"), "lydgsr748"),
    (("buffer748", "AA"), "buffer748"),
    (("queue748", "key"), "aycei748"),
    (("queue748", "lemon"), "byqir748"),
    (("queue748", "a"), "queue748"),
    (("queue748", "zz"), "ptdtd748"),
    (("queue748", "AgentU"), "qaihx748"),
    (("queue748", "keyboard"), "aycvs748"),
    (("queue748", "AA"), "queue748"),
    (("worker748", "key"), "gspuip748"),
    (("worker748", "lemon"), "hsdyrc748"),
    (("worker748", "a"), "worker748"),
    (("worker748", "zz"), "vnqjdq748"),
    (("worker748", "AgentU"), "wuvxxl748"),
    (("worker748", "keyboard"), "gsplsr748"),
    (("worker748", "AA"), "worker748"),
    (("kernel748", "key"), "uipxij748"),
    (("kernel748", "lemon"), "vidbrw748"),
    (("kernel748", "a"), "kernel748"),
    (("kernel748", "zz"), "jdqmdk748"),
    (("kernel748", "AgentU"), "kkvaxf748"),
    (("kernel748", "keyboard"), "uiposl748"),
    (("kernel748", "AA"), "kernel748"),
    (("signal748", "key"), "cmexej748"),
    (("signal748", "lemon"), "dmsbnw748"),
    (("signal748", "a"), "signal748"),
    (("signal748", "zz"), "rhfmzk748"),
    (("signal748", "AgentU"), "sokatf748"),
    (("signal748", "keyboard"), "cmeool748"),
    (("signal748", "AA"), "signal748"),
    (("packet748", "key"), "zeauir748"),
    (("packet748", "lemon"), "aeoyre748"),
    (("packet748", "a"), "packet748"),
    (("packet748", "zz"), "ozbjds748"),
    (("packet748", "AgentU"), "pggxxn748"),
    (("packet748", "keyboard"), "zealst748"),
    (("packet748", "AA"), "packet748"),
    (("router748", "key"), "bssdip748"),
    (("router748", "lemon"), "csghrc748"),
    (("router748", "a"), "router748"),
    (("router748", "zz"), "qntsdq748"),
    (("router748", "AgentU"), "ruygxl748"),
    (("router748", "keyboard"), "bssusr748"),
    (("router748", "AA"), "router748"),
    (("cluster748", "key"), "mpscxcb748"),
    (("cluster748", "lemon"), "npgggpv748"),
    (("cluster748", "a"), "cluster748"),
    (("cluster748", "zz"), "bktrsdq748"),
    (("cluster748", "AgentU"), "cryfmyr748"),
    (("cluster748", "keyboard"), "mpsthei748"),
    (("cluster748", "AA"), "cluster748"),
    (("mirror748", "key"), "wmpbsp748"),
    (("mirror748", "lemon"), "xmdfbc748"),
    (("mirror748", "a"), "mirror748"),
    (("mirror748", "zz"), "lhqqnq748"),
    (("mirror748", "AgentU"), "movehl748"),
    (("mirror748", "keyboard"), "wmpscr748"),
    (("mirror748", "AA"), "mirror748"),
    (("filter748", "key"), "pmjdip748"),
    (("filter748", "lemon"), "qmxhrc748"),
    (("filter748", "a"), "filter748"),
    (("filter748", "zz"), "ehksdq748"),
    (("filter748", "AgentU"), "fopgxl748"),
    (("filter748", "keyboard"), "pmjusr748"),
    (("filter748", "AA"), "filter748"),
    (("ranking748", "key"), "belumlq748"),
    (("ranking748", "lemon"), "cezyvyk748"),
    (("ranking748", "a"), "ranking748"),
    (("ranking748", "zz"), "qzmjhmf748"),
    (("ranking748", "AgentU"), "rgrxbhg748"),
    (("ranking748", "keyboard"), "bellwnx748"),
    (("ranking748", "AA"), "ranking748"),
    (("encoding748", "key"), "orayhgxk748"),
    (("encoding748", "lemon"), "procqtrs748"),
    (("encoding748", "a"), "encoding748"),
    (("encoding748", "zz"), "dmbnchmf748"),
    (("encoding748", "AgentU"), "etgbwcnm748"),
    (("encoding748", "keyboard"), "orapriej748"),
    (("encoding748", "AA"), "encoding748"),
    (("mapping748", "key"), "wenzmlq748"),
    (("mapping748", "lemon"), "xebdvyk748"),
    (("mapping748", "a"), "mapping748"),
    (("mapping748", "zz"), "lzoohmf748"),
    (("mapping748", "AgentU"), "mgtcbhg748"),
    (("mapping748", "keyboard"), "wenqwnx748"),
    (("mapping748", "AA"), "mapping748"),
    (("record748", "key"), "biayvb748"),
    (("record748", "lemon"), "cioceo748"),
    (("record748", "a"), "record748"),
    (("record748", "zz"), "qdbnqc748"),
    (("record748", "AgentU"), "rkgbkx748"),
    (("record748", "keyboard"), "biapfd748"),
    (("record748", "AA"), "record748"),
    (("candle748", "key"), "melnpc748"),
    (("candle748", "lemon"), "nezryp748"),
    (("candle748", "a"), "candle748"),
    (("candle748", "zz"), "bzmckd748"),
    (("candle748", "AgentU"), "cgrqey748"),
    (("candle748", "keyboard"), "meleze748"),
    (("candle748", "AA"), "candle748"),
    (("thread748", "key"), "dlpoeb748"),
    (("thread748", "lemon"), "eldsno748"),
    (("thread748", "a"), "thread748"),
    (("thread748", "zz"), "sgqdzc748"),
    (("thread748", "AgentU"), "tnvrtx748"),
    (("thread748", "keyboard"), "dlpfod748"),
    (("thread748", "AA"), "thread748"),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 748: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 748: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "a"),
        "round 748: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 748: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 748: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 748: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", "AA"),
        "round 748: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "key"),
        "bssxh 748: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 748: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "a"),
        "round 748: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 748: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 748: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 748: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", "AA"),
        "round 748: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 748: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 748: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "a"),
        "round 748: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 748: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 748: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 748: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", "AA"),
        "round 748: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 748: the processor reads the record then stops", "key"),
        "bssxh 748: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 748: the processor reads the record then stops", "lemon"),
        "csgbq 748: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 748: the processor reads the record then stops", "a"),
        "round 748: the processor reads the record then stops",
    ),
    (
        ("round 748: the processor reads the record then stops", "zz"),
        "qntmc 748: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 748: the processor reads the record then stops", "AgentU"),
        "ruyaw 748: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 748: the processor reads the record then stops", "keyboard"),
        "bssor 748: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 748: the processor reads the record then stops", "AA"),
        "round 748: the processor reads the record then stops",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "key"),
        "bssxh 748: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "lemon"),
        "csgbq 748: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "a"),
        "round 748: a worker pulls the next task from the queue",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "zz"),
        "qntmc 748: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 748: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "keyboard"),
        "bssor 748: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 748: a worker pulls the next task from the queue", "AA"),
        "round 748: a worker pulls the next task from the queue",
    ),
    (
        ("round 748: signals travel through the network layer", "key"),
        "bssxh 748: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 748: signals travel through the network layer", "lemon"),
        "csgbq 748: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 748: signals travel through the network layer", "a"),
        "round 748: signals travel through the network layer",
    ),
    (
        ("round 748: signals travel through the network layer", "zz"),
        "qntmc 748: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 748: signals travel through the network layer", "AgentU"),
        "ruyaw 748: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 748: signals travel through the network layer", "keyboard"),
        "bssor 748: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 748: signals travel through the network layer", "AA"),
        "round 748: signals travel through the network layer",
    ),
    (
        ("round 748: the gateway routes each request by policy", "key"),
        "bssxh 748: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 748: the gateway routes each request by policy", "lemon"),
        "csgbq 748: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 748: the gateway routes each request by policy", "a"),
        "round 748: the gateway routes each request by policy",
    ),
    (
        ("round 748: the gateway routes each request by policy", "zz"),
        "qntmc 748: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 748: the gateway routes each request by policy", "AgentU"),
        "ruyaw 748: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 748: the gateway routes each request by policy", "keyboard"),
        "bssor 748: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 748: the gateway routes each request by policy", "AA"),
        "round 748: the gateway routes each request by policy",
    ),
    (("round 748: memory grows until the buffer is full", "key"), "bssxh 748: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 748: memory grows until the buffer is full", "lemon"), "csgbq 748: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 748: memory grows until the buffer is full", "a"), "round 748: memory grows until the buffer is full"),
    (("round 748: memory grows until the buffer is full", "zz"), "qntmc 748: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 748: memory grows until the buffer is full", "AgentU"),
        "ruyaw 748: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 748: memory grows until the buffer is full", "keyboard"),
        "bssor 748: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 748: memory grows until the buffer is full", "AA"), "round 748: memory grows until the buffer is full"),
    (("round 748: the cluster mirrors every packet twice", "key"), "bssxh 748: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 748: the cluster mirrors every packet twice", "lemon"),
        "csgbq 748: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 748: the cluster mirrors every packet twice", "a"), "round 748: the cluster mirrors every packet twice"),
    (("round 748: the cluster mirrors every packet twice", "zz"), "qntmc 748: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 748: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 748: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 748: the cluster mirrors every packet twice", "keyboard"),
        "bssor 748: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 748: the cluster mirrors every packet twice", "AA"), "round 748: the cluster mirrors every packet twice"),
    (
        ("round 748: ranking uses tokens learned from the corpus", "key"),
        "bssxh 748: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 748: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", "a"),
        "round 748: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 748: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 748: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 748: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", "AA"),
        "round 748: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 748: a long session ends when the candle dies", "key"),
        "bssxh 748: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 748: a long session ends when the candle dies", "lemon"),
        "csgbq 748: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 748: a long session ends when the candle dies", "a"),
        "round 748: a long session ends when the candle dies",
    ),
    (
        ("round 748: a long session ends when the candle dies", "zz"),
        "qntmc 748: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 748: a long session ends when the candle dies", "AgentU"),
        "ruyaw 748: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 748: a long session ends when the candle dies", "keyboard"),
        "bssor 748: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 748: a long session ends when the candle dies", "AA"),
        "round 748: a long session ends when the candle dies",
    ),
    (("round 748: encode the prompt then map the result", "key"), "bssxh 748: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 748: encode the prompt then map the result", "lemon"), "csgbq 748: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 748: encode the prompt then map the result", "a"), "round 748: encode the prompt then map the result"),
    (("round 748: encode the prompt then map the result", "zz"), "qntmc 748: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 748: encode the prompt then map the result", "AgentU"),
        "ruyaw 748: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 748: encode the prompt then map the result", "keyboard"),
        "bssor 748: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 748: encode the prompt then map the result", "AA"), "round 748: encode the prompt then map the result"),
    (("round 748: the kernel wakes the worker at dawn", "key"), "bssxh 748: rri iovlop ukocc xfo ambocb er neux"),
    (("round 748: the kernel wakes the worker at dawn", "lemon"), "csgbq 748: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 748: the kernel wakes the worker at dawn", "a"), "round 748: the kernel wakes the worker at dawn"),
    (("round 748: the kernel wakes the worker at dawn", "zz"), "qntmc 748: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 748: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 748: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 748: the kernel wakes the worker at dawn", "keyboard"), "bssor 748: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 748: the kernel wakes the worker at dawn", "AA"), "round 748: the kernel wakes the worker at dawn"),
    (("round 748: service latency drops after the patch", "key"), "bssxh 748: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 748: service latency drops after the patch", "lemon"), "csgbq 748: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 748: service latency drops after the patch", "a"), "round 748: service latency drops after the patch"),
    (("round 748: service latency drops after the patch", "zz"), "qntmc 748: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 748: service latency drops after the patch", "AgentU"),
        "ruyaw 748: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 748: service latency drops after the patch", "keyboard"),
        "bssor 748: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 748: service latency drops after the patch", "AA"), "round 748: service latency drops after the patch"),
    (
        ("round 748: the library caches every vector it sees", "key"),
        "bssxh 748: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 748: the library caches every vector it sees", "lemon"),
        "csgbq 748: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 748: the library caches every vector it sees", "a"), "round 748: the library caches every vector it sees"),
    (
        ("round 748: the library caches every vector it sees", "zz"),
        "qntmc 748: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 748: the library caches every vector it sees", "AgentU"),
        "ruyaw 748: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 748: the library caches every vector it sees", "keyboard"),
        "bssor 748: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 748: the library caches every vector it sees", "AA"),
        "round 748: the library caches every vector it sees",
    ),
    (("round 748: agents argue then the debate resolves", "key"), "bssxh 748: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 748: agents argue then the debate resolves", "lemon"), "csgbq 748: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 748: agents argue then the debate resolves", "a"), "round 748: agents argue then the debate resolves"),
    (("round 748: agents argue then the debate resolves", "zz"), "qntmc 748: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 748: agents argue then the debate resolves", "AgentU"),
        "ruyaw 748: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 748: agents argue then the debate resolves", "keyboard"),
        "bssor 748: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 748: agents argue then the debate resolves", "AA"), "round 748: agents argue then the debate resolves"),
    (("round 748: the filter keeps only strong matches", "key"), "bssxh 748: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 748: the filter keeps only strong matches", "lemon"), "csgbq 748: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 748: the filter keeps only strong matches", "a"), "round 748: the filter keeps only strong matches"),
    (("round 748: the filter keeps only strong matches", "zz"), "qntmc 748: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 748: the filter keeps only strong matches", "AgentU"), "ruyaw 748: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 748: the filter keeps only strong matches", "keyboard"),
        "bssor 748: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 748: the filter keeps only strong matches", "AA"), "round 748: the filter keeps only strong matches"),
    (("round 748: the model answers with a short reply", "key"), "bssxh 748: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 748: the model answers with a short reply", "lemon"), "csgbq 748: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 748: the model answers with a short reply", "a"), "round 748: the model answers with a short reply"),
    (("round 748: the model answers with a short reply", "zz"), "qntmc 748: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 748: the model answers with a short reply", "AgentU"), "ruyaw 748: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 748: the model answers with a short reply", "keyboard"),
        "bssor 748: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 748: the model answers with a short reply", "AA"), "round 748: the model answers with a short reply"),
    (
        ("round 748: the recorder stores the reasoning trace", "key"),
        "bssxh 748: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 748: the recorder stores the reasoning trace", "lemon"),
        "csgbq 748: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 748: the recorder stores the reasoning trace", "a"), "round 748: the recorder stores the reasoning trace"),
    (
        ("round 748: the recorder stores the reasoning trace", "zz"),
        "qntmc 748: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 748: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 748: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 748: the recorder stores the reasoning trace", "keyboard"),
        "bssor 748: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 748: the recorder stores the reasoning trace", "AA"),
        "round 748: the recorder stores the reasoning trace",
    ),
    (("round 748: the angel watches the processor run", "key"), "bssxh 748: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 748: the angel watches the processor run", "lemon"), "csgbq 748: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 748: the angel watches the processor run", "a"), "round 748: the angel watches the processor run"),
    (("round 748: the angel watches the processor run", "zz"), "qntmc 748: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 748: the angel watches the processor run", "AgentU"), "ruyaw 748: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 748: the angel watches the processor run", "keyboard"), "bssor 748: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 748: the angel watches the processor run", "AA"), "round 748: the angel watches the processor run"),
    (("round 748: angle of the vector decides the match", "key"), "bssxh 748: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 748: angle of the vector decides the match", "lemon"), "csgbq 748: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 748: angle of the vector decides the match", "a"), "round 748: angle of the vector decides the match"),
    (("round 748: angle of the vector decides the match", "zz"), "qntmc 748: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 748: angle of the vector decides the match", "AgentU"),
        "ruyaw 748: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 748: angle of the vector decides the match", "keyboard"),
        "bssor 748: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 748: angle of the vector decides the match", "AA"), "round 748: angle of the vector decides the match"),
    (
        ("round 748: the candle burns twice as long at night", "key"),
        "bssxh 748: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 748: the candle burns twice as long at night", "lemon"),
        "csgbq 748: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 748: the candle burns twice as long at night", "a"), "round 748: the candle burns twice as long at night"),
    (
        ("round 748: the candle burns twice as long at night", "zz"),
        "qntmc 748: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 748: the candle burns twice as long at night", "AgentU"),
        "ruyaw 748: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 748: the candle burns twice as long at night", "keyboard"),
        "bssor 748: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 748: the candle burns twice as long at night", "AA"),
        "round 748: the candle burns twice as long at night",
    ),
    (("round 748: a mirror of the universe in one line", "key"), "bssxh 748: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 748: a mirror of the universe in one line", "lemon"), "csgbq 748: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 748: a mirror of the universe in one line", "a"), "round 748: a mirror of the universe in one line"),
    (("round 748: a mirror of the universe in one line", "zz"), "qntmc 748: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 748: a mirror of the universe in one line", "AgentU"), "ruyaw 748: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 748: a mirror of the universe in one line", "keyboard"),
        "bssor 748: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 748: a mirror of the universe in one line", "AA"), "round 748: a mirror of the universe in one line"),
    (("round 748: the queue drains before the storm", "key"), "bssxh 748: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 748: the queue drains before the storm", "lemon"), "csgbq 748: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 748: the queue drains before the storm", "a"), "round 748: the queue drains before the storm"),
    (("round 748: the queue drains before the storm", "zz"), "qntmc 748: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 748: the queue drains before the storm", "AgentU"), "ruyaw 748: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 748: the queue drains before the storm", "keyboard"), "bssor 748: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 748: the queue drains before the storm", "AA"), "round 748: the queue drains before the storm"),
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
