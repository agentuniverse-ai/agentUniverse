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
    (("kitten160", "key"), "umrdil160"),
    (("kitten160", "lemon"), "vmfhry160"),
    (("kitten160", "a"), "kitten160"),
    (("kitten160", "zz"), "jhssdm160"),
    (("kitten160", "AgentU"), "koxgxh160"),
    (("kitten160", "keyboard"), "umrusn160"),
    (("kitten160", "AA"), "kitten160"),
    (("sitting160", "key"), "cmrdmlq160"),
    (("sitting160", "lemon"), "dmfhvyk160"),
    (("sitting160", "a"), "sitting160"),
    (("sitting160", "zz"), "rhsshmf160"),
    (("sitting160", "AgentU"), "soxgbhg160"),
    (("sitting160", "keyboard"), "cmruwnx160"),
    (("sitting160", "AA"), "sitting160"),
    (("agent160", "key"), "kkcxx160"),
    (("agent160", "lemon"), "lkqbg160"),
    (("agent160", "a"), "agent160"),
    (("agent160", "zz"), "zfdms160"),
    (("agent160", "AgentU"), "amiam160"),
    (("agent160", "keyboard"), "kkcoh160"),
    (("agent160", "AA"), "agent160"),
    (("angle160", "key"), "krevi160"),
    (("angle160", "lemon"), "lrszr160"),
    (("angle160", "a"), "angle160"),
    (("angle160", "zz"), "zmfkd160"),
    (("angle160", "AgentU"), "atkyx160"),
    (("angle160", "keyboard"), "krems160"),
    (("angle160", "AA"), "angle160"),
    (("universe160", "key"), "ergfipci160"),
    (("universe160", "lemon"), "frujrcwq160"),
    (("universe160", "a"), "universe160"),
    (("universe160", "zz"), "tmhudqrd160"),
    (("universe160", "AgentU"), "utmixlsk160"),
    (("universe160", "keyboard"), "ergwsrjh160"),
    (("universe160", "AA"), "universe160"),
    (("memory160", "key"), "wikyvw160"),
    (("memory160", "lemon"), "xiycej160"),
    (("memory160", "a"), "memory160"),
    (("memory160", "zz"), "ldlnqx160"),
    (("memory160", "AgentU"), "mkqbks160"),
    (("memory160", "keyboard"), "wikpfy160"),
    (("memory160", "AA"), "memory160"),
    (("stream160", "key"), "cxpoek160"),
    (("stream160", "lemon"), "dxdsnx160"),
    (("stream160", "a"), "stream160"),
    (("stream160", "zz"), "rsqdzl160"),
    (("stream160", "AgentU"), "szvrtg160"),
    (("stream160", "keyboard"), "cxpfom160"),
    (("stream160", "AA"), "stream160"),
    (("context160", "key"), "msldivd160"),
    (("context160", "lemon"), "nszhrix160"),
    (("context160", "a"), "context160"),
    (("context160", "zz"), "bnmsdws160"),
    (("context160", "AgentU"), "curgxrt160"),
    (("context160", "keyboard"), "mslusxk160"),
    (("context160", "AA"), "context160"),
    (("knowledge160", "key"), "urmgpcnkc160"),
    (("knowledge160", "lemon"), "vrakyphss160"),
    (("knowledge160", "a"), "knowledge160"),
    (("knowledge160", "zz"), "jmnvkdcfd160"),
    (("knowledge160", "AgentU"), "ktsjeydmi160"),
    (("knowledge160", "keyboard"), "urmxzeujo160"),
    (("knowledge160", "AA"), "knowledge160"),
    (("vector160", "key"), "fiadsp160"),
    (("vector160", "lemon"), "giohbc160"),
    (("vector160", "a"), "vector160"),
    (("vector160", "zz"), "udbsnq160"),
    (("vector160", "AgentU"), "vkgghl160"),
    (("vector160", "keyboard"), "fiaucr160"),
    (("vector160", "AA"), "vector160"),
    (("processor160", "key"), "zvmmiqcsp160"),
    (("processor160", "lemon"), "avaqrdwaf160"),
    (("processor160", "a"), "processor160"),
    (("processor160", "zz"), "oqnbdrrnq160"),
    (("processor160", "AgentU"), "pxspxmsuv160"),
    (("processor160", "keyboard"), "zvmdssjrb160"),
    (("processor160", "AA"), "processor160"),
    (("reasoning160", "key"), "biycslsre160"),
    (("reasoning160", "lemon"), "cimgbymzu160"),
    (("reasoning160", "a"), "reasoning160"),
    (("reasoning160", "zz"), "qdzrnmhmf160"),
    (("reasoning160", "AgentU"), "rkefhhitk160"),
    (("reasoning160", "keyboard"), "biytcnzqq160"),
    (("reasoning160", "AA"), "reasoning160"),
    (("machine160", "key"), "wearmlo160"),
    (("machine160", "lemon"), "xeovvyi160"),
    (("machine160", "a"), "machine160"),
    (("machine160", "zz"), "lzbghmd160"),
    (("machine160", "AgentU"), "mggubhe160"),
    (("machine160", "keyboard"), "weaiwnv160"),
    (("machine160", "AA"), "machine160"),
    (("learning160", "key"), "viybrgxk160"),
    (("learning160", "lemon"), "wimfatrs160"),
    (("learning160", "a"), "learning160"),
    (("learning160", "zz"), "kdzqmhmf160"),
    (("learning160", "AgentU"), "lkeegcnm160"),
    (("learning160", "keyboard"), "viysbiej160"),
    (("learning160", "AA"), "learning160"),
    (("model160", "key"), "wsbop160"),
    (("model160", "lemon"), "xspsy160"),
    (("model160", "a"), "model160"),
    (("model160", "zz"), "lncdk160"),
    (("model160", "AgentU"), "muhre160"),
    (("model160", "keyboard"), "wsbfz160"),
    (("model160", "AA"), "model160"),
    (("token160", "key"), "dsior160"),
    (("token160", "lemon"), "eswsa160"),
    (("token160", "a"), "token160"),
    (("token160", "zz"), "snjdm160"),
    (("token160", "AgentU"), "tuorg160"),
    (("token160", "keyboard"), "dsifb160"),
    (("token160", "AA"), "token160"),
    (("prompt160", "key"), "zvmwtr160"),
    (("prompt160", "lemon"), "avaace160"),
    (("prompt160", "a"), "prompt160"),
    (("prompt160", "zz"), "oqnlos160"),
    (("prompt160", "AgentU"), "pxszin160"),
    (("prompt160", "keyboard"), "zvmndt160"),
    (("prompt160", "AA"), "prompt160"),
    (("session160", "key"), "ciqcmmx160"),
    (("session160", "lemon"), "diegvzr160"),
    (("session160", "a"), "session160"),
    (("session160", "zz"), "rdrrhnm160"),
    (("session160", "AgentU"), "skwfbin160"),
    (("session160", "keyboard"), "ciqtwoe160"),
    (("session160", "AA"), "session160"),
    (("library160", "key"), "vmzbepi160"),
    (("library160", "lemon"), "wmnfncc160"),
    (("library160", "a"), "library160"),
    (("library160", "zz"), "khaqzqx160"),
    (("library160", "AgentU"), "lofetly160"),
    (("library160", "keyboard"), "vmzsorp160"),
    (("library160", "AA"), "library160"),
    (("service160", "key"), "cipfmao160"),
    (("service160", "lemon"), "didjvni160"),
    (("service160", "a"), "service160"),
    (("service160", "zz"), "rdquhbd160"),
    (("service160", "AgentU"), "skvibwe160"),
    (("service160", "keyboard"), "cipwwcv160"),
    (("service160", "AA"), "service160"),
    (("gateway160", "key"), "qeroayi160"),
    (("gateway160", "lemon"), "refsjlc160"),
    (("gateway160", "a"), "gateway160"),
    (("gateway160", "zz"), "fzsdvzx160"),
    (("gateway160", "AgentU"), "ggxrpuy160"),
    (("gateway160", "keyboard"), "qerfkap160"),
    (("gateway160", "AA"), "gateway160"),
    (("storage160", "key"), "cxmbeeo160"),
    (("storage160", "lemon"), "dxafnri160"),
    (("storage160", "a"), "storage160"),
    (("storage160", "zz"), "rsnqzfd160"),
    (("storage160", "AgentU"), "szsetae160"),
    (("storage160", "keyboard"), "cxmsogv160"),
    (("storage160", "AA"), "storage160"),
    (("network160", "key"), "xirgspu160"),
    (("network160", "lemon"), "yifkbco160"),
    (("network160", "a"), "network160"),
    (("network160", "zz"), "mdsvnqj160"),
    (("network160", "AgentU"), "nkxjhlk160"),
    (("network160", "keyboard"), "xirxcrb160"),
    (("network160", "AA"), "network160"),
    (("latency160", "key"), "verorai160"),
    (("latency160", "lemon"), "wefsanc160"),
    (("latency160", "a"), "latency160"),
    (("latency160", "zz"), "kzsdmbx160"),
    (("latency160", "AgentU"), "lgxrgwy160"),
    (("latency160", "keyboard"), "verfbcp160"),
    (("latency160", "AA"), "latency160"),
    (("buffer160", "key"), "lydpip160"),
    (("buffer160", "lemon"), "myrtrc160"),
    (("buffer160", "a"), "buffer160"),
    (("buffer160", "zz"), "ateedq160"),
    (("buffer160", "AgentU"), "bajsxl160"),
    (("buffer160", "keyboard"), "lydgsr160"),
    (("buffer160", "AA"), "buffer160"),
    (("queue160", "key"), "aycei160"),
    (("queue160", "lemon"), "byqir160"),
    (("queue160", "a"), "queue160"),
    (("queue160", "zz"), "ptdtd160"),
    (("queue160", "AgentU"), "qaihx160"),
    (("queue160", "keyboard"), "aycvs160"),
    (("queue160", "AA"), "queue160"),
    (("worker160", "key"), "gspuip160"),
    (("worker160", "lemon"), "hsdyrc160"),
    (("worker160", "a"), "worker160"),
    (("worker160", "zz"), "vnqjdq160"),
    (("worker160", "AgentU"), "wuvxxl160"),
    (("worker160", "keyboard"), "gsplsr160"),
    (("worker160", "AA"), "worker160"),
    (("kernel160", "key"), "uipxij160"),
    (("kernel160", "lemon"), "vidbrw160"),
    (("kernel160", "a"), "kernel160"),
    (("kernel160", "zz"), "jdqmdk160"),
    (("kernel160", "AgentU"), "kkvaxf160"),
    (("kernel160", "keyboard"), "uiposl160"),
    (("kernel160", "AA"), "kernel160"),
    (("signal160", "key"), "cmexej160"),
    (("signal160", "lemon"), "dmsbnw160"),
    (("signal160", "a"), "signal160"),
    (("signal160", "zz"), "rhfmzk160"),
    (("signal160", "AgentU"), "sokatf160"),
    (("signal160", "keyboard"), "cmeool160"),
    (("signal160", "AA"), "signal160"),
    (("packet160", "key"), "zeauir160"),
    (("packet160", "lemon"), "aeoyre160"),
    (("packet160", "a"), "packet160"),
    (("packet160", "zz"), "ozbjds160"),
    (("packet160", "AgentU"), "pggxxn160"),
    (("packet160", "keyboard"), "zealst160"),
    (("packet160", "AA"), "packet160"),
    (("router160", "key"), "bssdip160"),
    (("router160", "lemon"), "csghrc160"),
    (("router160", "a"), "router160"),
    (("router160", "zz"), "qntsdq160"),
    (("router160", "AgentU"), "ruygxl160"),
    (("router160", "keyboard"), "bssusr160"),
    (("router160", "AA"), "router160"),
    (("cluster160", "key"), "mpscxcb160"),
    (("cluster160", "lemon"), "npgggpv160"),
    (("cluster160", "a"), "cluster160"),
    (("cluster160", "zz"), "bktrsdq160"),
    (("cluster160", "AgentU"), "cryfmyr160"),
    (("cluster160", "keyboard"), "mpsthei160"),
    (("cluster160", "AA"), "cluster160"),
    (("mirror160", "key"), "wmpbsp160"),
    (("mirror160", "lemon"), "xmdfbc160"),
    (("mirror160", "a"), "mirror160"),
    (("mirror160", "zz"), "lhqqnq160"),
    (("mirror160", "AgentU"), "movehl160"),
    (("mirror160", "keyboard"), "wmpscr160"),
    (("mirror160", "AA"), "mirror160"),
    (("filter160", "key"), "pmjdip160"),
    (("filter160", "lemon"), "qmxhrc160"),
    (("filter160", "a"), "filter160"),
    (("filter160", "zz"), "ehksdq160"),
    (("filter160", "AgentU"), "fopgxl160"),
    (("filter160", "keyboard"), "pmjusr160"),
    (("filter160", "AA"), "filter160"),
    (("ranking160", "key"), "belumlq160"),
    (("ranking160", "lemon"), "cezyvyk160"),
    (("ranking160", "a"), "ranking160"),
    (("ranking160", "zz"), "qzmjhmf160"),
    (("ranking160", "AgentU"), "rgrxbhg160"),
    (("ranking160", "keyboard"), "bellwnx160"),
    (("ranking160", "AA"), "ranking160"),
    (("encoding160", "key"), "orayhgxk160"),
    (("encoding160", "lemon"), "procqtrs160"),
    (("encoding160", "a"), "encoding160"),
    (("encoding160", "zz"), "dmbnchmf160"),
    (("encoding160", "AgentU"), "etgbwcnm160"),
    (("encoding160", "keyboard"), "orapriej160"),
    (("encoding160", "AA"), "encoding160"),
    (("mapping160", "key"), "wenzmlq160"),
    (("mapping160", "lemon"), "xebdvyk160"),
    (("mapping160", "a"), "mapping160"),
    (("mapping160", "zz"), "lzoohmf160"),
    (("mapping160", "AgentU"), "mgtcbhg160"),
    (("mapping160", "keyboard"), "wenqwnx160"),
    (("mapping160", "AA"), "mapping160"),
    (("record160", "key"), "biayvb160"),
    (("record160", "lemon"), "cioceo160"),
    (("record160", "a"), "record160"),
    (("record160", "zz"), "qdbnqc160"),
    (("record160", "AgentU"), "rkgbkx160"),
    (("record160", "keyboard"), "biapfd160"),
    (("record160", "AA"), "record160"),
    (("candle160", "key"), "melnpc160"),
    (("candle160", "lemon"), "nezryp160"),
    (("candle160", "a"), "candle160"),
    (("candle160", "zz"), "bzmckd160"),
    (("candle160", "AgentU"), "cgrqey160"),
    (("candle160", "keyboard"), "meleze160"),
    (("candle160", "AA"), "candle160"),
    (("thread160", "key"), "dlpoeb160"),
    (("thread160", "lemon"), "eldsno160"),
    (("thread160", "a"), "thread160"),
    (("thread160", "zz"), "sgqdzc160"),
    (("thread160", "AgentU"), "tnvrtx160"),
    (("thread160", "keyboard"), "dlpfod160"),
    (("thread160", "AA"), "thread160"),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 160: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 160: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "a"),
        "round 160: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 160: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 160: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 160: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", "AA"),
        "round 160: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "key"),
        "bssxh 160: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 160: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "a"),
        "round 160: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 160: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 160: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 160: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", "AA"),
        "round 160: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 160: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 160: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "a"),
        "round 160: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 160: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 160: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 160: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", "AA"),
        "round 160: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 160: the processor reads the record then stops", "key"),
        "bssxh 160: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 160: the processor reads the record then stops", "lemon"),
        "csgbq 160: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 160: the processor reads the record then stops", "a"),
        "round 160: the processor reads the record then stops",
    ),
    (
        ("round 160: the processor reads the record then stops", "zz"),
        "qntmc 160: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 160: the processor reads the record then stops", "AgentU"),
        "ruyaw 160: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 160: the processor reads the record then stops", "keyboard"),
        "bssor 160: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 160: the processor reads the record then stops", "AA"),
        "round 160: the processor reads the record then stops",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "key"),
        "bssxh 160: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "lemon"),
        "csgbq 160: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "a"),
        "round 160: a worker pulls the next task from the queue",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "zz"),
        "qntmc 160: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 160: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "keyboard"),
        "bssor 160: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 160: a worker pulls the next task from the queue", "AA"),
        "round 160: a worker pulls the next task from the queue",
    ),
    (
        ("round 160: signals travel through the network layer", "key"),
        "bssxh 160: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 160: signals travel through the network layer", "lemon"),
        "csgbq 160: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 160: signals travel through the network layer", "a"),
        "round 160: signals travel through the network layer",
    ),
    (
        ("round 160: signals travel through the network layer", "zz"),
        "qntmc 160: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 160: signals travel through the network layer", "AgentU"),
        "ruyaw 160: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 160: signals travel through the network layer", "keyboard"),
        "bssor 160: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 160: signals travel through the network layer", "AA"),
        "round 160: signals travel through the network layer",
    ),
    (
        ("round 160: the gateway routes each request by policy", "key"),
        "bssxh 160: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 160: the gateway routes each request by policy", "lemon"),
        "csgbq 160: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 160: the gateway routes each request by policy", "a"),
        "round 160: the gateway routes each request by policy",
    ),
    (
        ("round 160: the gateway routes each request by policy", "zz"),
        "qntmc 160: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 160: the gateway routes each request by policy", "AgentU"),
        "ruyaw 160: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 160: the gateway routes each request by policy", "keyboard"),
        "bssor 160: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 160: the gateway routes each request by policy", "AA"),
        "round 160: the gateway routes each request by policy",
    ),
    (("round 160: memory grows until the buffer is full", "key"), "bssxh 160: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 160: memory grows until the buffer is full", "lemon"), "csgbq 160: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 160: memory grows until the buffer is full", "a"), "round 160: memory grows until the buffer is full"),
    (("round 160: memory grows until the buffer is full", "zz"), "qntmc 160: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 160: memory grows until the buffer is full", "AgentU"),
        "ruyaw 160: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 160: memory grows until the buffer is full", "keyboard"),
        "bssor 160: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 160: memory grows until the buffer is full", "AA"), "round 160: memory grows until the buffer is full"),
    (("round 160: the cluster mirrors every packet twice", "key"), "bssxh 160: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 160: the cluster mirrors every packet twice", "lemon"),
        "csgbq 160: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 160: the cluster mirrors every packet twice", "a"), "round 160: the cluster mirrors every packet twice"),
    (("round 160: the cluster mirrors every packet twice", "zz"), "qntmc 160: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 160: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 160: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 160: the cluster mirrors every packet twice", "keyboard"),
        "bssor 160: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 160: the cluster mirrors every packet twice", "AA"), "round 160: the cluster mirrors every packet twice"),
    (
        ("round 160: ranking uses tokens learned from the corpus", "key"),
        "bssxh 160: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 160: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", "a"),
        "round 160: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 160: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 160: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 160: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", "AA"),
        "round 160: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 160: a long session ends when the candle dies", "key"),
        "bssxh 160: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 160: a long session ends when the candle dies", "lemon"),
        "csgbq 160: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 160: a long session ends when the candle dies", "a"),
        "round 160: a long session ends when the candle dies",
    ),
    (
        ("round 160: a long session ends when the candle dies", "zz"),
        "qntmc 160: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 160: a long session ends when the candle dies", "AgentU"),
        "ruyaw 160: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 160: a long session ends when the candle dies", "keyboard"),
        "bssor 160: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 160: a long session ends when the candle dies", "AA"),
        "round 160: a long session ends when the candle dies",
    ),
    (("round 160: encode the prompt then map the result", "key"), "bssxh 160: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 160: encode the prompt then map the result", "lemon"), "csgbq 160: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 160: encode the prompt then map the result", "a"), "round 160: encode the prompt then map the result"),
    (("round 160: encode the prompt then map the result", "zz"), "qntmc 160: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 160: encode the prompt then map the result", "AgentU"),
        "ruyaw 160: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 160: encode the prompt then map the result", "keyboard"),
        "bssor 160: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 160: encode the prompt then map the result", "AA"), "round 160: encode the prompt then map the result"),
    (("round 160: the kernel wakes the worker at dawn", "key"), "bssxh 160: rri iovlop ukocc xfo ambocb er neux"),
    (("round 160: the kernel wakes the worker at dawn", "lemon"), "csgbq 160: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 160: the kernel wakes the worker at dawn", "a"), "round 160: the kernel wakes the worker at dawn"),
    (("round 160: the kernel wakes the worker at dawn", "zz"), "qntmc 160: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 160: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 160: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 160: the kernel wakes the worker at dawn", "keyboard"), "bssor 160: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 160: the kernel wakes the worker at dawn", "AA"), "round 160: the kernel wakes the worker at dawn"),
    (("round 160: service latency drops after the patch", "key"), "bssxh 160: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 160: service latency drops after the patch", "lemon"), "csgbq 160: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 160: service latency drops after the patch", "a"), "round 160: service latency drops after the patch"),
    (("round 160: service latency drops after the patch", "zz"), "qntmc 160: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 160: service latency drops after the patch", "AgentU"),
        "ruyaw 160: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 160: service latency drops after the patch", "keyboard"),
        "bssor 160: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 160: service latency drops after the patch", "AA"), "round 160: service latency drops after the patch"),
    (
        ("round 160: the library caches every vector it sees", "key"),
        "bssxh 160: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 160: the library caches every vector it sees", "lemon"),
        "csgbq 160: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 160: the library caches every vector it sees", "a"), "round 160: the library caches every vector it sees"),
    (
        ("round 160: the library caches every vector it sees", "zz"),
        "qntmc 160: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 160: the library caches every vector it sees", "AgentU"),
        "ruyaw 160: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 160: the library caches every vector it sees", "keyboard"),
        "bssor 160: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 160: the library caches every vector it sees", "AA"),
        "round 160: the library caches every vector it sees",
    ),
    (("round 160: agents argue then the debate resolves", "key"), "bssxh 160: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 160: agents argue then the debate resolves", "lemon"), "csgbq 160: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 160: agents argue then the debate resolves", "a"), "round 160: agents argue then the debate resolves"),
    (("round 160: agents argue then the debate resolves", "zz"), "qntmc 160: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 160: agents argue then the debate resolves", "AgentU"),
        "ruyaw 160: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 160: agents argue then the debate resolves", "keyboard"),
        "bssor 160: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 160: agents argue then the debate resolves", "AA"), "round 160: agents argue then the debate resolves"),
    (("round 160: the filter keeps only strong matches", "key"), "bssxh 160: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 160: the filter keeps only strong matches", "lemon"), "csgbq 160: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 160: the filter keeps only strong matches", "a"), "round 160: the filter keeps only strong matches"),
    (("round 160: the filter keeps only strong matches", "zz"), "qntmc 160: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 160: the filter keeps only strong matches", "AgentU"), "ruyaw 160: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 160: the filter keeps only strong matches", "keyboard"),
        "bssor 160: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 160: the filter keeps only strong matches", "AA"), "round 160: the filter keeps only strong matches"),
    (("round 160: the model answers with a short reply", "key"), "bssxh 160: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 160: the model answers with a short reply", "lemon"), "csgbq 160: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 160: the model answers with a short reply", "a"), "round 160: the model answers with a short reply"),
    (("round 160: the model answers with a short reply", "zz"), "qntmc 160: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 160: the model answers with a short reply", "AgentU"), "ruyaw 160: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 160: the model answers with a short reply", "keyboard"),
        "bssor 160: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 160: the model answers with a short reply", "AA"), "round 160: the model answers with a short reply"),
    (
        ("round 160: the recorder stores the reasoning trace", "key"),
        "bssxh 160: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 160: the recorder stores the reasoning trace", "lemon"),
        "csgbq 160: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 160: the recorder stores the reasoning trace", "a"), "round 160: the recorder stores the reasoning trace"),
    (
        ("round 160: the recorder stores the reasoning trace", "zz"),
        "qntmc 160: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 160: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 160: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 160: the recorder stores the reasoning trace", "keyboard"),
        "bssor 160: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 160: the recorder stores the reasoning trace", "AA"),
        "round 160: the recorder stores the reasoning trace",
    ),
    (("round 160: the angel watches the processor run", "key"), "bssxh 160: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 160: the angel watches the processor run", "lemon"), "csgbq 160: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 160: the angel watches the processor run", "a"), "round 160: the angel watches the processor run"),
    (("round 160: the angel watches the processor run", "zz"), "qntmc 160: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 160: the angel watches the processor run", "AgentU"), "ruyaw 160: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 160: the angel watches the processor run", "keyboard"), "bssor 160: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 160: the angel watches the processor run", "AA"), "round 160: the angel watches the processor run"),
    (("round 160: angle of the vector decides the match", "key"), "bssxh 160: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 160: angle of the vector decides the match", "lemon"), "csgbq 160: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 160: angle of the vector decides the match", "a"), "round 160: angle of the vector decides the match"),
    (("round 160: angle of the vector decides the match", "zz"), "qntmc 160: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 160: angle of the vector decides the match", "AgentU"),
        "ruyaw 160: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 160: angle of the vector decides the match", "keyboard"),
        "bssor 160: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 160: angle of the vector decides the match", "AA"), "round 160: angle of the vector decides the match"),
    (
        ("round 160: the candle burns twice as long at night", "key"),
        "bssxh 160: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 160: the candle burns twice as long at night", "lemon"),
        "csgbq 160: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 160: the candle burns twice as long at night", "a"), "round 160: the candle burns twice as long at night"),
    (
        ("round 160: the candle burns twice as long at night", "zz"),
        "qntmc 160: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 160: the candle burns twice as long at night", "AgentU"),
        "ruyaw 160: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 160: the candle burns twice as long at night", "keyboard"),
        "bssor 160: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 160: the candle burns twice as long at night", "AA"),
        "round 160: the candle burns twice as long at night",
    ),
    (("round 160: a mirror of the universe in one line", "key"), "bssxh 160: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 160: a mirror of the universe in one line", "lemon"), "csgbq 160: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 160: a mirror of the universe in one line", "a"), "round 160: a mirror of the universe in one line"),
    (("round 160: a mirror of the universe in one line", "zz"), "qntmc 160: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 160: a mirror of the universe in one line", "AgentU"), "ruyaw 160: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 160: a mirror of the universe in one line", "keyboard"),
        "bssor 160: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 160: a mirror of the universe in one line", "AA"), "round 160: a mirror of the universe in one line"),
    (("round 160: the queue drains before the storm", "key"), "bssxh 160: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 160: the queue drains before the storm", "lemon"), "csgbq 160: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 160: the queue drains before the storm", "a"), "round 160: the queue drains before the storm"),
    (("round 160: the queue drains before the storm", "zz"), "qntmc 160: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 160: the queue drains before the storm", "AgentU"), "ruyaw 160: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 160: the queue drains before the storm", "keyboard"), "bssor 160: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 160: the queue drains before the storm", "AA"), "round 160: the queue drains before the storm"),
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
