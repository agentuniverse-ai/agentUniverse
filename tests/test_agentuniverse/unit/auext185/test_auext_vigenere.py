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
    (("kitten185", "key"), "umrdil185"),
    (("kitten185", "lemon"), "vmfhry185"),
    (("kitten185", "a"), "kitten185"),
    (("kitten185", "zz"), "jhssdm185"),
    (("kitten185", "AgentU"), "koxgxh185"),
    (("kitten185", "keyboard"), "umrusn185"),
    (("kitten185", "AA"), "kitten185"),
    (("sitting185", "key"), "cmrdmlq185"),
    (("sitting185", "lemon"), "dmfhvyk185"),
    (("sitting185", "a"), "sitting185"),
    (("sitting185", "zz"), "rhsshmf185"),
    (("sitting185", "AgentU"), "soxgbhg185"),
    (("sitting185", "keyboard"), "cmruwnx185"),
    (("sitting185", "AA"), "sitting185"),
    (("agent185", "key"), "kkcxx185"),
    (("agent185", "lemon"), "lkqbg185"),
    (("agent185", "a"), "agent185"),
    (("agent185", "zz"), "zfdms185"),
    (("agent185", "AgentU"), "amiam185"),
    (("agent185", "keyboard"), "kkcoh185"),
    (("agent185", "AA"), "agent185"),
    (("angle185", "key"), "krevi185"),
    (("angle185", "lemon"), "lrszr185"),
    (("angle185", "a"), "angle185"),
    (("angle185", "zz"), "zmfkd185"),
    (("angle185", "AgentU"), "atkyx185"),
    (("angle185", "keyboard"), "krems185"),
    (("angle185", "AA"), "angle185"),
    (("universe185", "key"), "ergfipci185"),
    (("universe185", "lemon"), "frujrcwq185"),
    (("universe185", "a"), "universe185"),
    (("universe185", "zz"), "tmhudqrd185"),
    (("universe185", "AgentU"), "utmixlsk185"),
    (("universe185", "keyboard"), "ergwsrjh185"),
    (("universe185", "AA"), "universe185"),
    (("memory185", "key"), "wikyvw185"),
    (("memory185", "lemon"), "xiycej185"),
    (("memory185", "a"), "memory185"),
    (("memory185", "zz"), "ldlnqx185"),
    (("memory185", "AgentU"), "mkqbks185"),
    (("memory185", "keyboard"), "wikpfy185"),
    (("memory185", "AA"), "memory185"),
    (("stream185", "key"), "cxpoek185"),
    (("stream185", "lemon"), "dxdsnx185"),
    (("stream185", "a"), "stream185"),
    (("stream185", "zz"), "rsqdzl185"),
    (("stream185", "AgentU"), "szvrtg185"),
    (("stream185", "keyboard"), "cxpfom185"),
    (("stream185", "AA"), "stream185"),
    (("context185", "key"), "msldivd185"),
    (("context185", "lemon"), "nszhrix185"),
    (("context185", "a"), "context185"),
    (("context185", "zz"), "bnmsdws185"),
    (("context185", "AgentU"), "curgxrt185"),
    (("context185", "keyboard"), "mslusxk185"),
    (("context185", "AA"), "context185"),
    (("knowledge185", "key"), "urmgpcnkc185"),
    (("knowledge185", "lemon"), "vrakyphss185"),
    (("knowledge185", "a"), "knowledge185"),
    (("knowledge185", "zz"), "jmnvkdcfd185"),
    (("knowledge185", "AgentU"), "ktsjeydmi185"),
    (("knowledge185", "keyboard"), "urmxzeujo185"),
    (("knowledge185", "AA"), "knowledge185"),
    (("vector185", "key"), "fiadsp185"),
    (("vector185", "lemon"), "giohbc185"),
    (("vector185", "a"), "vector185"),
    (("vector185", "zz"), "udbsnq185"),
    (("vector185", "AgentU"), "vkgghl185"),
    (("vector185", "keyboard"), "fiaucr185"),
    (("vector185", "AA"), "vector185"),
    (("processor185", "key"), "zvmmiqcsp185"),
    (("processor185", "lemon"), "avaqrdwaf185"),
    (("processor185", "a"), "processor185"),
    (("processor185", "zz"), "oqnbdrrnq185"),
    (("processor185", "AgentU"), "pxspxmsuv185"),
    (("processor185", "keyboard"), "zvmdssjrb185"),
    (("processor185", "AA"), "processor185"),
    (("reasoning185", "key"), "biycslsre185"),
    (("reasoning185", "lemon"), "cimgbymzu185"),
    (("reasoning185", "a"), "reasoning185"),
    (("reasoning185", "zz"), "qdzrnmhmf185"),
    (("reasoning185", "AgentU"), "rkefhhitk185"),
    (("reasoning185", "keyboard"), "biytcnzqq185"),
    (("reasoning185", "AA"), "reasoning185"),
    (("machine185", "key"), "wearmlo185"),
    (("machine185", "lemon"), "xeovvyi185"),
    (("machine185", "a"), "machine185"),
    (("machine185", "zz"), "lzbghmd185"),
    (("machine185", "AgentU"), "mggubhe185"),
    (("machine185", "keyboard"), "weaiwnv185"),
    (("machine185", "AA"), "machine185"),
    (("learning185", "key"), "viybrgxk185"),
    (("learning185", "lemon"), "wimfatrs185"),
    (("learning185", "a"), "learning185"),
    (("learning185", "zz"), "kdzqmhmf185"),
    (("learning185", "AgentU"), "lkeegcnm185"),
    (("learning185", "keyboard"), "viysbiej185"),
    (("learning185", "AA"), "learning185"),
    (("model185", "key"), "wsbop185"),
    (("model185", "lemon"), "xspsy185"),
    (("model185", "a"), "model185"),
    (("model185", "zz"), "lncdk185"),
    (("model185", "AgentU"), "muhre185"),
    (("model185", "keyboard"), "wsbfz185"),
    (("model185", "AA"), "model185"),
    (("token185", "key"), "dsior185"),
    (("token185", "lemon"), "eswsa185"),
    (("token185", "a"), "token185"),
    (("token185", "zz"), "snjdm185"),
    (("token185", "AgentU"), "tuorg185"),
    (("token185", "keyboard"), "dsifb185"),
    (("token185", "AA"), "token185"),
    (("prompt185", "key"), "zvmwtr185"),
    (("prompt185", "lemon"), "avaace185"),
    (("prompt185", "a"), "prompt185"),
    (("prompt185", "zz"), "oqnlos185"),
    (("prompt185", "AgentU"), "pxszin185"),
    (("prompt185", "keyboard"), "zvmndt185"),
    (("prompt185", "AA"), "prompt185"),
    (("session185", "key"), "ciqcmmx185"),
    (("session185", "lemon"), "diegvzr185"),
    (("session185", "a"), "session185"),
    (("session185", "zz"), "rdrrhnm185"),
    (("session185", "AgentU"), "skwfbin185"),
    (("session185", "keyboard"), "ciqtwoe185"),
    (("session185", "AA"), "session185"),
    (("library185", "key"), "vmzbepi185"),
    (("library185", "lemon"), "wmnfncc185"),
    (("library185", "a"), "library185"),
    (("library185", "zz"), "khaqzqx185"),
    (("library185", "AgentU"), "lofetly185"),
    (("library185", "keyboard"), "vmzsorp185"),
    (("library185", "AA"), "library185"),
    (("service185", "key"), "cipfmao185"),
    (("service185", "lemon"), "didjvni185"),
    (("service185", "a"), "service185"),
    (("service185", "zz"), "rdquhbd185"),
    (("service185", "AgentU"), "skvibwe185"),
    (("service185", "keyboard"), "cipwwcv185"),
    (("service185", "AA"), "service185"),
    (("gateway185", "key"), "qeroayi185"),
    (("gateway185", "lemon"), "refsjlc185"),
    (("gateway185", "a"), "gateway185"),
    (("gateway185", "zz"), "fzsdvzx185"),
    (("gateway185", "AgentU"), "ggxrpuy185"),
    (("gateway185", "keyboard"), "qerfkap185"),
    (("gateway185", "AA"), "gateway185"),
    (("storage185", "key"), "cxmbeeo185"),
    (("storage185", "lemon"), "dxafnri185"),
    (("storage185", "a"), "storage185"),
    (("storage185", "zz"), "rsnqzfd185"),
    (("storage185", "AgentU"), "szsetae185"),
    (("storage185", "keyboard"), "cxmsogv185"),
    (("storage185", "AA"), "storage185"),
    (("network185", "key"), "xirgspu185"),
    (("network185", "lemon"), "yifkbco185"),
    (("network185", "a"), "network185"),
    (("network185", "zz"), "mdsvnqj185"),
    (("network185", "AgentU"), "nkxjhlk185"),
    (("network185", "keyboard"), "xirxcrb185"),
    (("network185", "AA"), "network185"),
    (("latency185", "key"), "verorai185"),
    (("latency185", "lemon"), "wefsanc185"),
    (("latency185", "a"), "latency185"),
    (("latency185", "zz"), "kzsdmbx185"),
    (("latency185", "AgentU"), "lgxrgwy185"),
    (("latency185", "keyboard"), "verfbcp185"),
    (("latency185", "AA"), "latency185"),
    (("buffer185", "key"), "lydpip185"),
    (("buffer185", "lemon"), "myrtrc185"),
    (("buffer185", "a"), "buffer185"),
    (("buffer185", "zz"), "ateedq185"),
    (("buffer185", "AgentU"), "bajsxl185"),
    (("buffer185", "keyboard"), "lydgsr185"),
    (("buffer185", "AA"), "buffer185"),
    (("queue185", "key"), "aycei185"),
    (("queue185", "lemon"), "byqir185"),
    (("queue185", "a"), "queue185"),
    (("queue185", "zz"), "ptdtd185"),
    (("queue185", "AgentU"), "qaihx185"),
    (("queue185", "keyboard"), "aycvs185"),
    (("queue185", "AA"), "queue185"),
    (("worker185", "key"), "gspuip185"),
    (("worker185", "lemon"), "hsdyrc185"),
    (("worker185", "a"), "worker185"),
    (("worker185", "zz"), "vnqjdq185"),
    (("worker185", "AgentU"), "wuvxxl185"),
    (("worker185", "keyboard"), "gsplsr185"),
    (("worker185", "AA"), "worker185"),
    (("kernel185", "key"), "uipxij185"),
    (("kernel185", "lemon"), "vidbrw185"),
    (("kernel185", "a"), "kernel185"),
    (("kernel185", "zz"), "jdqmdk185"),
    (("kernel185", "AgentU"), "kkvaxf185"),
    (("kernel185", "keyboard"), "uiposl185"),
    (("kernel185", "AA"), "kernel185"),
    (("signal185", "key"), "cmexej185"),
    (("signal185", "lemon"), "dmsbnw185"),
    (("signal185", "a"), "signal185"),
    (("signal185", "zz"), "rhfmzk185"),
    (("signal185", "AgentU"), "sokatf185"),
    (("signal185", "keyboard"), "cmeool185"),
    (("signal185", "AA"), "signal185"),
    (("packet185", "key"), "zeauir185"),
    (("packet185", "lemon"), "aeoyre185"),
    (("packet185", "a"), "packet185"),
    (("packet185", "zz"), "ozbjds185"),
    (("packet185", "AgentU"), "pggxxn185"),
    (("packet185", "keyboard"), "zealst185"),
    (("packet185", "AA"), "packet185"),
    (("router185", "key"), "bssdip185"),
    (("router185", "lemon"), "csghrc185"),
    (("router185", "a"), "router185"),
    (("router185", "zz"), "qntsdq185"),
    (("router185", "AgentU"), "ruygxl185"),
    (("router185", "keyboard"), "bssusr185"),
    (("router185", "AA"), "router185"),
    (("cluster185", "key"), "mpscxcb185"),
    (("cluster185", "lemon"), "npgggpv185"),
    (("cluster185", "a"), "cluster185"),
    (("cluster185", "zz"), "bktrsdq185"),
    (("cluster185", "AgentU"), "cryfmyr185"),
    (("cluster185", "keyboard"), "mpsthei185"),
    (("cluster185", "AA"), "cluster185"),
    (("mirror185", "key"), "wmpbsp185"),
    (("mirror185", "lemon"), "xmdfbc185"),
    (("mirror185", "a"), "mirror185"),
    (("mirror185", "zz"), "lhqqnq185"),
    (("mirror185", "AgentU"), "movehl185"),
    (("mirror185", "keyboard"), "wmpscr185"),
    (("mirror185", "AA"), "mirror185"),
    (("filter185", "key"), "pmjdip185"),
    (("filter185", "lemon"), "qmxhrc185"),
    (("filter185", "a"), "filter185"),
    (("filter185", "zz"), "ehksdq185"),
    (("filter185", "AgentU"), "fopgxl185"),
    (("filter185", "keyboard"), "pmjusr185"),
    (("filter185", "AA"), "filter185"),
    (("ranking185", "key"), "belumlq185"),
    (("ranking185", "lemon"), "cezyvyk185"),
    (("ranking185", "a"), "ranking185"),
    (("ranking185", "zz"), "qzmjhmf185"),
    (("ranking185", "AgentU"), "rgrxbhg185"),
    (("ranking185", "keyboard"), "bellwnx185"),
    (("ranking185", "AA"), "ranking185"),
    (("encoding185", "key"), "orayhgxk185"),
    (("encoding185", "lemon"), "procqtrs185"),
    (("encoding185", "a"), "encoding185"),
    (("encoding185", "zz"), "dmbnchmf185"),
    (("encoding185", "AgentU"), "etgbwcnm185"),
    (("encoding185", "keyboard"), "orapriej185"),
    (("encoding185", "AA"), "encoding185"),
    (("mapping185", "key"), "wenzmlq185"),
    (("mapping185", "lemon"), "xebdvyk185"),
    (("mapping185", "a"), "mapping185"),
    (("mapping185", "zz"), "lzoohmf185"),
    (("mapping185", "AgentU"), "mgtcbhg185"),
    (("mapping185", "keyboard"), "wenqwnx185"),
    (("mapping185", "AA"), "mapping185"),
    (("record185", "key"), "biayvb185"),
    (("record185", "lemon"), "cioceo185"),
    (("record185", "a"), "record185"),
    (("record185", "zz"), "qdbnqc185"),
    (("record185", "AgentU"), "rkgbkx185"),
    (("record185", "keyboard"), "biapfd185"),
    (("record185", "AA"), "record185"),
    (("candle185", "key"), "melnpc185"),
    (("candle185", "lemon"), "nezryp185"),
    (("candle185", "a"), "candle185"),
    (("candle185", "zz"), "bzmckd185"),
    (("candle185", "AgentU"), "cgrqey185"),
    (("candle185", "keyboard"), "meleze185"),
    (("candle185", "AA"), "candle185"),
    (("thread185", "key"), "dlpoeb185"),
    (("thread185", "lemon"), "eldsno185"),
    (("thread185", "a"), "thread185"),
    (("thread185", "zz"), "sgqdzc185"),
    (("thread185", "AgentU"), "tnvrtx185"),
    (("thread185", "keyboard"), "dlpfod185"),
    (("thread185", "AA"), "thread185"),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 185: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 185: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "a"),
        "round 185: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 185: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 185: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 185: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", "AA"),
        "round 185: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "key"),
        "bssxh 185: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 185: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "a"),
        "round 185: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 185: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 185: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 185: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", "AA"),
        "round 185: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 185: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 185: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "a"),
        "round 185: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 185: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 185: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 185: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", "AA"),
        "round 185: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 185: the processor reads the record then stops", "key"),
        "bssxh 185: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 185: the processor reads the record then stops", "lemon"),
        "csgbq 185: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 185: the processor reads the record then stops", "a"),
        "round 185: the processor reads the record then stops",
    ),
    (
        ("round 185: the processor reads the record then stops", "zz"),
        "qntmc 185: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 185: the processor reads the record then stops", "AgentU"),
        "ruyaw 185: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 185: the processor reads the record then stops", "keyboard"),
        "bssor 185: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 185: the processor reads the record then stops", "AA"),
        "round 185: the processor reads the record then stops",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "key"),
        "bssxh 185: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "lemon"),
        "csgbq 185: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "a"),
        "round 185: a worker pulls the next task from the queue",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "zz"),
        "qntmc 185: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 185: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "keyboard"),
        "bssor 185: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 185: a worker pulls the next task from the queue", "AA"),
        "round 185: a worker pulls the next task from the queue",
    ),
    (
        ("round 185: signals travel through the network layer", "key"),
        "bssxh 185: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 185: signals travel through the network layer", "lemon"),
        "csgbq 185: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 185: signals travel through the network layer", "a"),
        "round 185: signals travel through the network layer",
    ),
    (
        ("round 185: signals travel through the network layer", "zz"),
        "qntmc 185: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 185: signals travel through the network layer", "AgentU"),
        "ruyaw 185: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 185: signals travel through the network layer", "keyboard"),
        "bssor 185: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 185: signals travel through the network layer", "AA"),
        "round 185: signals travel through the network layer",
    ),
    (
        ("round 185: the gateway routes each request by policy", "key"),
        "bssxh 185: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 185: the gateway routes each request by policy", "lemon"),
        "csgbq 185: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 185: the gateway routes each request by policy", "a"),
        "round 185: the gateway routes each request by policy",
    ),
    (
        ("round 185: the gateway routes each request by policy", "zz"),
        "qntmc 185: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 185: the gateway routes each request by policy", "AgentU"),
        "ruyaw 185: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 185: the gateway routes each request by policy", "keyboard"),
        "bssor 185: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 185: the gateway routes each request by policy", "AA"),
        "round 185: the gateway routes each request by policy",
    ),
    (("round 185: memory grows until the buffer is full", "key"), "bssxh 185: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 185: memory grows until the buffer is full", "lemon"), "csgbq 185: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 185: memory grows until the buffer is full", "a"), "round 185: memory grows until the buffer is full"),
    (("round 185: memory grows until the buffer is full", "zz"), "qntmc 185: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 185: memory grows until the buffer is full", "AgentU"),
        "ruyaw 185: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 185: memory grows until the buffer is full", "keyboard"),
        "bssor 185: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 185: memory grows until the buffer is full", "AA"), "round 185: memory grows until the buffer is full"),
    (("round 185: the cluster mirrors every packet twice", "key"), "bssxh 185: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 185: the cluster mirrors every packet twice", "lemon"),
        "csgbq 185: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 185: the cluster mirrors every packet twice", "a"), "round 185: the cluster mirrors every packet twice"),
    (("round 185: the cluster mirrors every packet twice", "zz"), "qntmc 185: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 185: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 185: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 185: the cluster mirrors every packet twice", "keyboard"),
        "bssor 185: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 185: the cluster mirrors every packet twice", "AA"), "round 185: the cluster mirrors every packet twice"),
    (
        ("round 185: ranking uses tokens learned from the corpus", "key"),
        "bssxh 185: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 185: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", "a"),
        "round 185: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 185: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 185: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 185: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", "AA"),
        "round 185: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 185: a long session ends when the candle dies", "key"),
        "bssxh 185: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 185: a long session ends when the candle dies", "lemon"),
        "csgbq 185: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 185: a long session ends when the candle dies", "a"),
        "round 185: a long session ends when the candle dies",
    ),
    (
        ("round 185: a long session ends when the candle dies", "zz"),
        "qntmc 185: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 185: a long session ends when the candle dies", "AgentU"),
        "ruyaw 185: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 185: a long session ends when the candle dies", "keyboard"),
        "bssor 185: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 185: a long session ends when the candle dies", "AA"),
        "round 185: a long session ends when the candle dies",
    ),
    (("round 185: encode the prompt then map the result", "key"), "bssxh 185: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 185: encode the prompt then map the result", "lemon"), "csgbq 185: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 185: encode the prompt then map the result", "a"), "round 185: encode the prompt then map the result"),
    (("round 185: encode the prompt then map the result", "zz"), "qntmc 185: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 185: encode the prompt then map the result", "AgentU"),
        "ruyaw 185: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 185: encode the prompt then map the result", "keyboard"),
        "bssor 185: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 185: encode the prompt then map the result", "AA"), "round 185: encode the prompt then map the result"),
    (("round 185: the kernel wakes the worker at dawn", "key"), "bssxh 185: rri iovlop ukocc xfo ambocb er neux"),
    (("round 185: the kernel wakes the worker at dawn", "lemon"), "csgbq 185: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 185: the kernel wakes the worker at dawn", "a"), "round 185: the kernel wakes the worker at dawn"),
    (("round 185: the kernel wakes the worker at dawn", "zz"), "qntmc 185: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 185: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 185: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 185: the kernel wakes the worker at dawn", "keyboard"), "bssor 185: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 185: the kernel wakes the worker at dawn", "AA"), "round 185: the kernel wakes the worker at dawn"),
    (("round 185: service latency drops after the patch", "key"), "bssxh 185: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 185: service latency drops after the patch", "lemon"), "csgbq 185: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 185: service latency drops after the patch", "a"), "round 185: service latency drops after the patch"),
    (("round 185: service latency drops after the patch", "zz"), "qntmc 185: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 185: service latency drops after the patch", "AgentU"),
        "ruyaw 185: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 185: service latency drops after the patch", "keyboard"),
        "bssor 185: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 185: service latency drops after the patch", "AA"), "round 185: service latency drops after the patch"),
    (
        ("round 185: the library caches every vector it sees", "key"),
        "bssxh 185: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 185: the library caches every vector it sees", "lemon"),
        "csgbq 185: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 185: the library caches every vector it sees", "a"), "round 185: the library caches every vector it sees"),
    (
        ("round 185: the library caches every vector it sees", "zz"),
        "qntmc 185: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 185: the library caches every vector it sees", "AgentU"),
        "ruyaw 185: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 185: the library caches every vector it sees", "keyboard"),
        "bssor 185: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 185: the library caches every vector it sees", "AA"),
        "round 185: the library caches every vector it sees",
    ),
    (("round 185: agents argue then the debate resolves", "key"), "bssxh 185: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 185: agents argue then the debate resolves", "lemon"), "csgbq 185: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 185: agents argue then the debate resolves", "a"), "round 185: agents argue then the debate resolves"),
    (("round 185: agents argue then the debate resolves", "zz"), "qntmc 185: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 185: agents argue then the debate resolves", "AgentU"),
        "ruyaw 185: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 185: agents argue then the debate resolves", "keyboard"),
        "bssor 185: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 185: agents argue then the debate resolves", "AA"), "round 185: agents argue then the debate resolves"),
    (("round 185: the filter keeps only strong matches", "key"), "bssxh 185: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 185: the filter keeps only strong matches", "lemon"), "csgbq 185: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 185: the filter keeps only strong matches", "a"), "round 185: the filter keeps only strong matches"),
    (("round 185: the filter keeps only strong matches", "zz"), "qntmc 185: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 185: the filter keeps only strong matches", "AgentU"), "ruyaw 185: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 185: the filter keeps only strong matches", "keyboard"),
        "bssor 185: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 185: the filter keeps only strong matches", "AA"), "round 185: the filter keeps only strong matches"),
    (("round 185: the model answers with a short reply", "key"), "bssxh 185: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 185: the model answers with a short reply", "lemon"), "csgbq 185: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 185: the model answers with a short reply", "a"), "round 185: the model answers with a short reply"),
    (("round 185: the model answers with a short reply", "zz"), "qntmc 185: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 185: the model answers with a short reply", "AgentU"), "ruyaw 185: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 185: the model answers with a short reply", "keyboard"),
        "bssor 185: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 185: the model answers with a short reply", "AA"), "round 185: the model answers with a short reply"),
    (
        ("round 185: the recorder stores the reasoning trace", "key"),
        "bssxh 185: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 185: the recorder stores the reasoning trace", "lemon"),
        "csgbq 185: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 185: the recorder stores the reasoning trace", "a"), "round 185: the recorder stores the reasoning trace"),
    (
        ("round 185: the recorder stores the reasoning trace", "zz"),
        "qntmc 185: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 185: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 185: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 185: the recorder stores the reasoning trace", "keyboard"),
        "bssor 185: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 185: the recorder stores the reasoning trace", "AA"),
        "round 185: the recorder stores the reasoning trace",
    ),
    (("round 185: the angel watches the processor run", "key"), "bssxh 185: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 185: the angel watches the processor run", "lemon"), "csgbq 185: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 185: the angel watches the processor run", "a"), "round 185: the angel watches the processor run"),
    (("round 185: the angel watches the processor run", "zz"), "qntmc 185: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 185: the angel watches the processor run", "AgentU"), "ruyaw 185: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 185: the angel watches the processor run", "keyboard"), "bssor 185: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 185: the angel watches the processor run", "AA"), "round 185: the angel watches the processor run"),
    (("round 185: angle of the vector decides the match", "key"), "bssxh 185: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 185: angle of the vector decides the match", "lemon"), "csgbq 185: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 185: angle of the vector decides the match", "a"), "round 185: angle of the vector decides the match"),
    (("round 185: angle of the vector decides the match", "zz"), "qntmc 185: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 185: angle of the vector decides the match", "AgentU"),
        "ruyaw 185: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 185: angle of the vector decides the match", "keyboard"),
        "bssor 185: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 185: angle of the vector decides the match", "AA"), "round 185: angle of the vector decides the match"),
    (
        ("round 185: the candle burns twice as long at night", "key"),
        "bssxh 185: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 185: the candle burns twice as long at night", "lemon"),
        "csgbq 185: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 185: the candle burns twice as long at night", "a"), "round 185: the candle burns twice as long at night"),
    (
        ("round 185: the candle burns twice as long at night", "zz"),
        "qntmc 185: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 185: the candle burns twice as long at night", "AgentU"),
        "ruyaw 185: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 185: the candle burns twice as long at night", "keyboard"),
        "bssor 185: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 185: the candle burns twice as long at night", "AA"),
        "round 185: the candle burns twice as long at night",
    ),
    (("round 185: a mirror of the universe in one line", "key"), "bssxh 185: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 185: a mirror of the universe in one line", "lemon"), "csgbq 185: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 185: a mirror of the universe in one line", "a"), "round 185: a mirror of the universe in one line"),
    (("round 185: a mirror of the universe in one line", "zz"), "qntmc 185: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 185: a mirror of the universe in one line", "AgentU"), "ruyaw 185: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 185: a mirror of the universe in one line", "keyboard"),
        "bssor 185: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 185: a mirror of the universe in one line", "AA"), "round 185: a mirror of the universe in one line"),
    (("round 185: the queue drains before the storm", "key"), "bssxh 185: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 185: the queue drains before the storm", "lemon"), "csgbq 185: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 185: the queue drains before the storm", "a"), "round 185: the queue drains before the storm"),
    (("round 185: the queue drains before the storm", "zz"), "qntmc 185: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 185: the queue drains before the storm", "AgentU"), "ruyaw 185: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 185: the queue drains before the storm", "keyboard"), "bssor 185: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 185: the queue drains before the storm", "AA"), "round 185: the queue drains before the storm"),
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
