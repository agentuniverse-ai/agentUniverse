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
    (("kitten168", "key"), "umrdil168"),
    (("kitten168", "lemon"), "vmfhry168"),
    (("kitten168", "a"), "kitten168"),
    (("kitten168", "zz"), "jhssdm168"),
    (("kitten168", "AgentU"), "koxgxh168"),
    (("kitten168", "keyboard"), "umrusn168"),
    (("kitten168", "AA"), "kitten168"),
    (("sitting168", "key"), "cmrdmlq168"),
    (("sitting168", "lemon"), "dmfhvyk168"),
    (("sitting168", "a"), "sitting168"),
    (("sitting168", "zz"), "rhsshmf168"),
    (("sitting168", "AgentU"), "soxgbhg168"),
    (("sitting168", "keyboard"), "cmruwnx168"),
    (("sitting168", "AA"), "sitting168"),
    (("agent168", "key"), "kkcxx168"),
    (("agent168", "lemon"), "lkqbg168"),
    (("agent168", "a"), "agent168"),
    (("agent168", "zz"), "zfdms168"),
    (("agent168", "AgentU"), "amiam168"),
    (("agent168", "keyboard"), "kkcoh168"),
    (("agent168", "AA"), "agent168"),
    (("angle168", "key"), "krevi168"),
    (("angle168", "lemon"), "lrszr168"),
    (("angle168", "a"), "angle168"),
    (("angle168", "zz"), "zmfkd168"),
    (("angle168", "AgentU"), "atkyx168"),
    (("angle168", "keyboard"), "krems168"),
    (("angle168", "AA"), "angle168"),
    (("universe168", "key"), "ergfipci168"),
    (("universe168", "lemon"), "frujrcwq168"),
    (("universe168", "a"), "universe168"),
    (("universe168", "zz"), "tmhudqrd168"),
    (("universe168", "AgentU"), "utmixlsk168"),
    (("universe168", "keyboard"), "ergwsrjh168"),
    (("universe168", "AA"), "universe168"),
    (("memory168", "key"), "wikyvw168"),
    (("memory168", "lemon"), "xiycej168"),
    (("memory168", "a"), "memory168"),
    (("memory168", "zz"), "ldlnqx168"),
    (("memory168", "AgentU"), "mkqbks168"),
    (("memory168", "keyboard"), "wikpfy168"),
    (("memory168", "AA"), "memory168"),
    (("stream168", "key"), "cxpoek168"),
    (("stream168", "lemon"), "dxdsnx168"),
    (("stream168", "a"), "stream168"),
    (("stream168", "zz"), "rsqdzl168"),
    (("stream168", "AgentU"), "szvrtg168"),
    (("stream168", "keyboard"), "cxpfom168"),
    (("stream168", "AA"), "stream168"),
    (("context168", "key"), "msldivd168"),
    (("context168", "lemon"), "nszhrix168"),
    (("context168", "a"), "context168"),
    (("context168", "zz"), "bnmsdws168"),
    (("context168", "AgentU"), "curgxrt168"),
    (("context168", "keyboard"), "mslusxk168"),
    (("context168", "AA"), "context168"),
    (("knowledge168", "key"), "urmgpcnkc168"),
    (("knowledge168", "lemon"), "vrakyphss168"),
    (("knowledge168", "a"), "knowledge168"),
    (("knowledge168", "zz"), "jmnvkdcfd168"),
    (("knowledge168", "AgentU"), "ktsjeydmi168"),
    (("knowledge168", "keyboard"), "urmxzeujo168"),
    (("knowledge168", "AA"), "knowledge168"),
    (("vector168", "key"), "fiadsp168"),
    (("vector168", "lemon"), "giohbc168"),
    (("vector168", "a"), "vector168"),
    (("vector168", "zz"), "udbsnq168"),
    (("vector168", "AgentU"), "vkgghl168"),
    (("vector168", "keyboard"), "fiaucr168"),
    (("vector168", "AA"), "vector168"),
    (("processor168", "key"), "zvmmiqcsp168"),
    (("processor168", "lemon"), "avaqrdwaf168"),
    (("processor168", "a"), "processor168"),
    (("processor168", "zz"), "oqnbdrrnq168"),
    (("processor168", "AgentU"), "pxspxmsuv168"),
    (("processor168", "keyboard"), "zvmdssjrb168"),
    (("processor168", "AA"), "processor168"),
    (("reasoning168", "key"), "biycslsre168"),
    (("reasoning168", "lemon"), "cimgbymzu168"),
    (("reasoning168", "a"), "reasoning168"),
    (("reasoning168", "zz"), "qdzrnmhmf168"),
    (("reasoning168", "AgentU"), "rkefhhitk168"),
    (("reasoning168", "keyboard"), "biytcnzqq168"),
    (("reasoning168", "AA"), "reasoning168"),
    (("machine168", "key"), "wearmlo168"),
    (("machine168", "lemon"), "xeovvyi168"),
    (("machine168", "a"), "machine168"),
    (("machine168", "zz"), "lzbghmd168"),
    (("machine168", "AgentU"), "mggubhe168"),
    (("machine168", "keyboard"), "weaiwnv168"),
    (("machine168", "AA"), "machine168"),
    (("learning168", "key"), "viybrgxk168"),
    (("learning168", "lemon"), "wimfatrs168"),
    (("learning168", "a"), "learning168"),
    (("learning168", "zz"), "kdzqmhmf168"),
    (("learning168", "AgentU"), "lkeegcnm168"),
    (("learning168", "keyboard"), "viysbiej168"),
    (("learning168", "AA"), "learning168"),
    (("model168", "key"), "wsbop168"),
    (("model168", "lemon"), "xspsy168"),
    (("model168", "a"), "model168"),
    (("model168", "zz"), "lncdk168"),
    (("model168", "AgentU"), "muhre168"),
    (("model168", "keyboard"), "wsbfz168"),
    (("model168", "AA"), "model168"),
    (("token168", "key"), "dsior168"),
    (("token168", "lemon"), "eswsa168"),
    (("token168", "a"), "token168"),
    (("token168", "zz"), "snjdm168"),
    (("token168", "AgentU"), "tuorg168"),
    (("token168", "keyboard"), "dsifb168"),
    (("token168", "AA"), "token168"),
    (("prompt168", "key"), "zvmwtr168"),
    (("prompt168", "lemon"), "avaace168"),
    (("prompt168", "a"), "prompt168"),
    (("prompt168", "zz"), "oqnlos168"),
    (("prompt168", "AgentU"), "pxszin168"),
    (("prompt168", "keyboard"), "zvmndt168"),
    (("prompt168", "AA"), "prompt168"),
    (("session168", "key"), "ciqcmmx168"),
    (("session168", "lemon"), "diegvzr168"),
    (("session168", "a"), "session168"),
    (("session168", "zz"), "rdrrhnm168"),
    (("session168", "AgentU"), "skwfbin168"),
    (("session168", "keyboard"), "ciqtwoe168"),
    (("session168", "AA"), "session168"),
    (("library168", "key"), "vmzbepi168"),
    (("library168", "lemon"), "wmnfncc168"),
    (("library168", "a"), "library168"),
    (("library168", "zz"), "khaqzqx168"),
    (("library168", "AgentU"), "lofetly168"),
    (("library168", "keyboard"), "vmzsorp168"),
    (("library168", "AA"), "library168"),
    (("service168", "key"), "cipfmao168"),
    (("service168", "lemon"), "didjvni168"),
    (("service168", "a"), "service168"),
    (("service168", "zz"), "rdquhbd168"),
    (("service168", "AgentU"), "skvibwe168"),
    (("service168", "keyboard"), "cipwwcv168"),
    (("service168", "AA"), "service168"),
    (("gateway168", "key"), "qeroayi168"),
    (("gateway168", "lemon"), "refsjlc168"),
    (("gateway168", "a"), "gateway168"),
    (("gateway168", "zz"), "fzsdvzx168"),
    (("gateway168", "AgentU"), "ggxrpuy168"),
    (("gateway168", "keyboard"), "qerfkap168"),
    (("gateway168", "AA"), "gateway168"),
    (("storage168", "key"), "cxmbeeo168"),
    (("storage168", "lemon"), "dxafnri168"),
    (("storage168", "a"), "storage168"),
    (("storage168", "zz"), "rsnqzfd168"),
    (("storage168", "AgentU"), "szsetae168"),
    (("storage168", "keyboard"), "cxmsogv168"),
    (("storage168", "AA"), "storage168"),
    (("network168", "key"), "xirgspu168"),
    (("network168", "lemon"), "yifkbco168"),
    (("network168", "a"), "network168"),
    (("network168", "zz"), "mdsvnqj168"),
    (("network168", "AgentU"), "nkxjhlk168"),
    (("network168", "keyboard"), "xirxcrb168"),
    (("network168", "AA"), "network168"),
    (("latency168", "key"), "verorai168"),
    (("latency168", "lemon"), "wefsanc168"),
    (("latency168", "a"), "latency168"),
    (("latency168", "zz"), "kzsdmbx168"),
    (("latency168", "AgentU"), "lgxrgwy168"),
    (("latency168", "keyboard"), "verfbcp168"),
    (("latency168", "AA"), "latency168"),
    (("buffer168", "key"), "lydpip168"),
    (("buffer168", "lemon"), "myrtrc168"),
    (("buffer168", "a"), "buffer168"),
    (("buffer168", "zz"), "ateedq168"),
    (("buffer168", "AgentU"), "bajsxl168"),
    (("buffer168", "keyboard"), "lydgsr168"),
    (("buffer168", "AA"), "buffer168"),
    (("queue168", "key"), "aycei168"),
    (("queue168", "lemon"), "byqir168"),
    (("queue168", "a"), "queue168"),
    (("queue168", "zz"), "ptdtd168"),
    (("queue168", "AgentU"), "qaihx168"),
    (("queue168", "keyboard"), "aycvs168"),
    (("queue168", "AA"), "queue168"),
    (("worker168", "key"), "gspuip168"),
    (("worker168", "lemon"), "hsdyrc168"),
    (("worker168", "a"), "worker168"),
    (("worker168", "zz"), "vnqjdq168"),
    (("worker168", "AgentU"), "wuvxxl168"),
    (("worker168", "keyboard"), "gsplsr168"),
    (("worker168", "AA"), "worker168"),
    (("kernel168", "key"), "uipxij168"),
    (("kernel168", "lemon"), "vidbrw168"),
    (("kernel168", "a"), "kernel168"),
    (("kernel168", "zz"), "jdqmdk168"),
    (("kernel168", "AgentU"), "kkvaxf168"),
    (("kernel168", "keyboard"), "uiposl168"),
    (("kernel168", "AA"), "kernel168"),
    (("signal168", "key"), "cmexej168"),
    (("signal168", "lemon"), "dmsbnw168"),
    (("signal168", "a"), "signal168"),
    (("signal168", "zz"), "rhfmzk168"),
    (("signal168", "AgentU"), "sokatf168"),
    (("signal168", "keyboard"), "cmeool168"),
    (("signal168", "AA"), "signal168"),
    (("packet168", "key"), "zeauir168"),
    (("packet168", "lemon"), "aeoyre168"),
    (("packet168", "a"), "packet168"),
    (("packet168", "zz"), "ozbjds168"),
    (("packet168", "AgentU"), "pggxxn168"),
    (("packet168", "keyboard"), "zealst168"),
    (("packet168", "AA"), "packet168"),
    (("router168", "key"), "bssdip168"),
    (("router168", "lemon"), "csghrc168"),
    (("router168", "a"), "router168"),
    (("router168", "zz"), "qntsdq168"),
    (("router168", "AgentU"), "ruygxl168"),
    (("router168", "keyboard"), "bssusr168"),
    (("router168", "AA"), "router168"),
    (("cluster168", "key"), "mpscxcb168"),
    (("cluster168", "lemon"), "npgggpv168"),
    (("cluster168", "a"), "cluster168"),
    (("cluster168", "zz"), "bktrsdq168"),
    (("cluster168", "AgentU"), "cryfmyr168"),
    (("cluster168", "keyboard"), "mpsthei168"),
    (("cluster168", "AA"), "cluster168"),
    (("mirror168", "key"), "wmpbsp168"),
    (("mirror168", "lemon"), "xmdfbc168"),
    (("mirror168", "a"), "mirror168"),
    (("mirror168", "zz"), "lhqqnq168"),
    (("mirror168", "AgentU"), "movehl168"),
    (("mirror168", "keyboard"), "wmpscr168"),
    (("mirror168", "AA"), "mirror168"),
    (("filter168", "key"), "pmjdip168"),
    (("filter168", "lemon"), "qmxhrc168"),
    (("filter168", "a"), "filter168"),
    (("filter168", "zz"), "ehksdq168"),
    (("filter168", "AgentU"), "fopgxl168"),
    (("filter168", "keyboard"), "pmjusr168"),
    (("filter168", "AA"), "filter168"),
    (("ranking168", "key"), "belumlq168"),
    (("ranking168", "lemon"), "cezyvyk168"),
    (("ranking168", "a"), "ranking168"),
    (("ranking168", "zz"), "qzmjhmf168"),
    (("ranking168", "AgentU"), "rgrxbhg168"),
    (("ranking168", "keyboard"), "bellwnx168"),
    (("ranking168", "AA"), "ranking168"),
    (("encoding168", "key"), "orayhgxk168"),
    (("encoding168", "lemon"), "procqtrs168"),
    (("encoding168", "a"), "encoding168"),
    (("encoding168", "zz"), "dmbnchmf168"),
    (("encoding168", "AgentU"), "etgbwcnm168"),
    (("encoding168", "keyboard"), "orapriej168"),
    (("encoding168", "AA"), "encoding168"),
    (("mapping168", "key"), "wenzmlq168"),
    (("mapping168", "lemon"), "xebdvyk168"),
    (("mapping168", "a"), "mapping168"),
    (("mapping168", "zz"), "lzoohmf168"),
    (("mapping168", "AgentU"), "mgtcbhg168"),
    (("mapping168", "keyboard"), "wenqwnx168"),
    (("mapping168", "AA"), "mapping168"),
    (("record168", "key"), "biayvb168"),
    (("record168", "lemon"), "cioceo168"),
    (("record168", "a"), "record168"),
    (("record168", "zz"), "qdbnqc168"),
    (("record168", "AgentU"), "rkgbkx168"),
    (("record168", "keyboard"), "biapfd168"),
    (("record168", "AA"), "record168"),
    (("candle168", "key"), "melnpc168"),
    (("candle168", "lemon"), "nezryp168"),
    (("candle168", "a"), "candle168"),
    (("candle168", "zz"), "bzmckd168"),
    (("candle168", "AgentU"), "cgrqey168"),
    (("candle168", "keyboard"), "meleze168"),
    (("candle168", "AA"), "candle168"),
    (("thread168", "key"), "dlpoeb168"),
    (("thread168", "lemon"), "eldsno168"),
    (("thread168", "a"), "thread168"),
    (("thread168", "zz"), "sgqdzc168"),
    (("thread168", "AgentU"), "tnvrtx168"),
    (("thread168", "keyboard"), "dlpfod168"),
    (("thread168", "AA"), "thread168"),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 168: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 168: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "a"),
        "round 168: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 168: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 168: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 168: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", "AA"),
        "round 168: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "key"),
        "bssxh 168: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 168: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "a"),
        "round 168: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 168: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 168: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 168: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", "AA"),
        "round 168: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 168: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 168: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "a"),
        "round 168: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 168: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 168: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 168: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", "AA"),
        "round 168: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 168: the processor reads the record then stops", "key"),
        "bssxh 168: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 168: the processor reads the record then stops", "lemon"),
        "csgbq 168: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 168: the processor reads the record then stops", "a"),
        "round 168: the processor reads the record then stops",
    ),
    (
        ("round 168: the processor reads the record then stops", "zz"),
        "qntmc 168: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 168: the processor reads the record then stops", "AgentU"),
        "ruyaw 168: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 168: the processor reads the record then stops", "keyboard"),
        "bssor 168: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 168: the processor reads the record then stops", "AA"),
        "round 168: the processor reads the record then stops",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "key"),
        "bssxh 168: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "lemon"),
        "csgbq 168: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "a"),
        "round 168: a worker pulls the next task from the queue",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "zz"),
        "qntmc 168: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 168: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "keyboard"),
        "bssor 168: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 168: a worker pulls the next task from the queue", "AA"),
        "round 168: a worker pulls the next task from the queue",
    ),
    (
        ("round 168: signals travel through the network layer", "key"),
        "bssxh 168: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 168: signals travel through the network layer", "lemon"),
        "csgbq 168: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 168: signals travel through the network layer", "a"),
        "round 168: signals travel through the network layer",
    ),
    (
        ("round 168: signals travel through the network layer", "zz"),
        "qntmc 168: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 168: signals travel through the network layer", "AgentU"),
        "ruyaw 168: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 168: signals travel through the network layer", "keyboard"),
        "bssor 168: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 168: signals travel through the network layer", "AA"),
        "round 168: signals travel through the network layer",
    ),
    (
        ("round 168: the gateway routes each request by policy", "key"),
        "bssxh 168: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 168: the gateway routes each request by policy", "lemon"),
        "csgbq 168: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 168: the gateway routes each request by policy", "a"),
        "round 168: the gateway routes each request by policy",
    ),
    (
        ("round 168: the gateway routes each request by policy", "zz"),
        "qntmc 168: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 168: the gateway routes each request by policy", "AgentU"),
        "ruyaw 168: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 168: the gateway routes each request by policy", "keyboard"),
        "bssor 168: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 168: the gateway routes each request by policy", "AA"),
        "round 168: the gateway routes each request by policy",
    ),
    (("round 168: memory grows until the buffer is full", "key"), "bssxh 168: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 168: memory grows until the buffer is full", "lemon"), "csgbq 168: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 168: memory grows until the buffer is full", "a"), "round 168: memory grows until the buffer is full"),
    (("round 168: memory grows until the buffer is full", "zz"), "qntmc 168: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 168: memory grows until the buffer is full", "AgentU"),
        "ruyaw 168: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 168: memory grows until the buffer is full", "keyboard"),
        "bssor 168: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 168: memory grows until the buffer is full", "AA"), "round 168: memory grows until the buffer is full"),
    (("round 168: the cluster mirrors every packet twice", "key"), "bssxh 168: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 168: the cluster mirrors every packet twice", "lemon"),
        "csgbq 168: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 168: the cluster mirrors every packet twice", "a"), "round 168: the cluster mirrors every packet twice"),
    (("round 168: the cluster mirrors every packet twice", "zz"), "qntmc 168: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 168: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 168: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 168: the cluster mirrors every packet twice", "keyboard"),
        "bssor 168: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 168: the cluster mirrors every packet twice", "AA"), "round 168: the cluster mirrors every packet twice"),
    (
        ("round 168: ranking uses tokens learned from the corpus", "key"),
        "bssxh 168: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 168: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", "a"),
        "round 168: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 168: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 168: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 168: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", "AA"),
        "round 168: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 168: a long session ends when the candle dies", "key"),
        "bssxh 168: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 168: a long session ends when the candle dies", "lemon"),
        "csgbq 168: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 168: a long session ends when the candle dies", "a"),
        "round 168: a long session ends when the candle dies",
    ),
    (
        ("round 168: a long session ends when the candle dies", "zz"),
        "qntmc 168: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 168: a long session ends when the candle dies", "AgentU"),
        "ruyaw 168: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 168: a long session ends when the candle dies", "keyboard"),
        "bssor 168: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 168: a long session ends when the candle dies", "AA"),
        "round 168: a long session ends when the candle dies",
    ),
    (("round 168: encode the prompt then map the result", "key"), "bssxh 168: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 168: encode the prompt then map the result", "lemon"), "csgbq 168: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 168: encode the prompt then map the result", "a"), "round 168: encode the prompt then map the result"),
    (("round 168: encode the prompt then map the result", "zz"), "qntmc 168: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 168: encode the prompt then map the result", "AgentU"),
        "ruyaw 168: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 168: encode the prompt then map the result", "keyboard"),
        "bssor 168: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 168: encode the prompt then map the result", "AA"), "round 168: encode the prompt then map the result"),
    (("round 168: the kernel wakes the worker at dawn", "key"), "bssxh 168: rri iovlop ukocc xfo ambocb er neux"),
    (("round 168: the kernel wakes the worker at dawn", "lemon"), "csgbq 168: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 168: the kernel wakes the worker at dawn", "a"), "round 168: the kernel wakes the worker at dawn"),
    (("round 168: the kernel wakes the worker at dawn", "zz"), "qntmc 168: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 168: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 168: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 168: the kernel wakes the worker at dawn", "keyboard"), "bssor 168: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 168: the kernel wakes the worker at dawn", "AA"), "round 168: the kernel wakes the worker at dawn"),
    (("round 168: service latency drops after the patch", "key"), "bssxh 168: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 168: service latency drops after the patch", "lemon"), "csgbq 168: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 168: service latency drops after the patch", "a"), "round 168: service latency drops after the patch"),
    (("round 168: service latency drops after the patch", "zz"), "qntmc 168: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 168: service latency drops after the patch", "AgentU"),
        "ruyaw 168: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 168: service latency drops after the patch", "keyboard"),
        "bssor 168: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 168: service latency drops after the patch", "AA"), "round 168: service latency drops after the patch"),
    (
        ("round 168: the library caches every vector it sees", "key"),
        "bssxh 168: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 168: the library caches every vector it sees", "lemon"),
        "csgbq 168: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 168: the library caches every vector it sees", "a"), "round 168: the library caches every vector it sees"),
    (
        ("round 168: the library caches every vector it sees", "zz"),
        "qntmc 168: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 168: the library caches every vector it sees", "AgentU"),
        "ruyaw 168: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 168: the library caches every vector it sees", "keyboard"),
        "bssor 168: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 168: the library caches every vector it sees", "AA"),
        "round 168: the library caches every vector it sees",
    ),
    (("round 168: agents argue then the debate resolves", "key"), "bssxh 168: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 168: agents argue then the debate resolves", "lemon"), "csgbq 168: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 168: agents argue then the debate resolves", "a"), "round 168: agents argue then the debate resolves"),
    (("round 168: agents argue then the debate resolves", "zz"), "qntmc 168: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 168: agents argue then the debate resolves", "AgentU"),
        "ruyaw 168: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 168: agents argue then the debate resolves", "keyboard"),
        "bssor 168: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 168: agents argue then the debate resolves", "AA"), "round 168: agents argue then the debate resolves"),
    (("round 168: the filter keeps only strong matches", "key"), "bssxh 168: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 168: the filter keeps only strong matches", "lemon"), "csgbq 168: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 168: the filter keeps only strong matches", "a"), "round 168: the filter keeps only strong matches"),
    (("round 168: the filter keeps only strong matches", "zz"), "qntmc 168: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 168: the filter keeps only strong matches", "AgentU"), "ruyaw 168: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 168: the filter keeps only strong matches", "keyboard"),
        "bssor 168: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 168: the filter keeps only strong matches", "AA"), "round 168: the filter keeps only strong matches"),
    (("round 168: the model answers with a short reply", "key"), "bssxh 168: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 168: the model answers with a short reply", "lemon"), "csgbq 168: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 168: the model answers with a short reply", "a"), "round 168: the model answers with a short reply"),
    (("round 168: the model answers with a short reply", "zz"), "qntmc 168: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 168: the model answers with a short reply", "AgentU"), "ruyaw 168: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 168: the model answers with a short reply", "keyboard"),
        "bssor 168: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 168: the model answers with a short reply", "AA"), "round 168: the model answers with a short reply"),
    (
        ("round 168: the recorder stores the reasoning trace", "key"),
        "bssxh 168: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 168: the recorder stores the reasoning trace", "lemon"),
        "csgbq 168: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 168: the recorder stores the reasoning trace", "a"), "round 168: the recorder stores the reasoning trace"),
    (
        ("round 168: the recorder stores the reasoning trace", "zz"),
        "qntmc 168: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 168: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 168: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 168: the recorder stores the reasoning trace", "keyboard"),
        "bssor 168: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 168: the recorder stores the reasoning trace", "AA"),
        "round 168: the recorder stores the reasoning trace",
    ),
    (("round 168: the angel watches the processor run", "key"), "bssxh 168: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 168: the angel watches the processor run", "lemon"), "csgbq 168: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 168: the angel watches the processor run", "a"), "round 168: the angel watches the processor run"),
    (("round 168: the angel watches the processor run", "zz"), "qntmc 168: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 168: the angel watches the processor run", "AgentU"), "ruyaw 168: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 168: the angel watches the processor run", "keyboard"), "bssor 168: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 168: the angel watches the processor run", "AA"), "round 168: the angel watches the processor run"),
    (("round 168: angle of the vector decides the match", "key"), "bssxh 168: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 168: angle of the vector decides the match", "lemon"), "csgbq 168: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 168: angle of the vector decides the match", "a"), "round 168: angle of the vector decides the match"),
    (("round 168: angle of the vector decides the match", "zz"), "qntmc 168: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 168: angle of the vector decides the match", "AgentU"),
        "ruyaw 168: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 168: angle of the vector decides the match", "keyboard"),
        "bssor 168: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 168: angle of the vector decides the match", "AA"), "round 168: angle of the vector decides the match"),
    (
        ("round 168: the candle burns twice as long at night", "key"),
        "bssxh 168: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 168: the candle burns twice as long at night", "lemon"),
        "csgbq 168: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 168: the candle burns twice as long at night", "a"), "round 168: the candle burns twice as long at night"),
    (
        ("round 168: the candle burns twice as long at night", "zz"),
        "qntmc 168: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 168: the candle burns twice as long at night", "AgentU"),
        "ruyaw 168: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 168: the candle burns twice as long at night", "keyboard"),
        "bssor 168: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 168: the candle burns twice as long at night", "AA"),
        "round 168: the candle burns twice as long at night",
    ),
    (("round 168: a mirror of the universe in one line", "key"), "bssxh 168: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 168: a mirror of the universe in one line", "lemon"), "csgbq 168: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 168: a mirror of the universe in one line", "a"), "round 168: a mirror of the universe in one line"),
    (("round 168: a mirror of the universe in one line", "zz"), "qntmc 168: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 168: a mirror of the universe in one line", "AgentU"), "ruyaw 168: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 168: a mirror of the universe in one line", "keyboard"),
        "bssor 168: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 168: a mirror of the universe in one line", "AA"), "round 168: a mirror of the universe in one line"),
    (("round 168: the queue drains before the storm", "key"), "bssxh 168: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 168: the queue drains before the storm", "lemon"), "csgbq 168: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 168: the queue drains before the storm", "a"), "round 168: the queue drains before the storm"),
    (("round 168: the queue drains before the storm", "zz"), "qntmc 168: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 168: the queue drains before the storm", "AgentU"), "ruyaw 168: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 168: the queue drains before the storm", "keyboard"), "bssor 168: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 168: the queue drains before the storm", "AA"), "round 168: the queue drains before the storm"),
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
