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
    (("kitten152", "key"), "umrdil152"),
    (("kitten152", "lemon"), "vmfhry152"),
    (("kitten152", "a"), "kitten152"),
    (("kitten152", "zz"), "jhssdm152"),
    (("kitten152", "AgentU"), "koxgxh152"),
    (("kitten152", "keyboard"), "umrusn152"),
    (("kitten152", "AA"), "kitten152"),
    (("sitting152", "key"), "cmrdmlq152"),
    (("sitting152", "lemon"), "dmfhvyk152"),
    (("sitting152", "a"), "sitting152"),
    (("sitting152", "zz"), "rhsshmf152"),
    (("sitting152", "AgentU"), "soxgbhg152"),
    (("sitting152", "keyboard"), "cmruwnx152"),
    (("sitting152", "AA"), "sitting152"),
    (("agent152", "key"), "kkcxx152"),
    (("agent152", "lemon"), "lkqbg152"),
    (("agent152", "a"), "agent152"),
    (("agent152", "zz"), "zfdms152"),
    (("agent152", "AgentU"), "amiam152"),
    (("agent152", "keyboard"), "kkcoh152"),
    (("agent152", "AA"), "agent152"),
    (("angle152", "key"), "krevi152"),
    (("angle152", "lemon"), "lrszr152"),
    (("angle152", "a"), "angle152"),
    (("angle152", "zz"), "zmfkd152"),
    (("angle152", "AgentU"), "atkyx152"),
    (("angle152", "keyboard"), "krems152"),
    (("angle152", "AA"), "angle152"),
    (("universe152", "key"), "ergfipci152"),
    (("universe152", "lemon"), "frujrcwq152"),
    (("universe152", "a"), "universe152"),
    (("universe152", "zz"), "tmhudqrd152"),
    (("universe152", "AgentU"), "utmixlsk152"),
    (("universe152", "keyboard"), "ergwsrjh152"),
    (("universe152", "AA"), "universe152"),
    (("memory152", "key"), "wikyvw152"),
    (("memory152", "lemon"), "xiycej152"),
    (("memory152", "a"), "memory152"),
    (("memory152", "zz"), "ldlnqx152"),
    (("memory152", "AgentU"), "mkqbks152"),
    (("memory152", "keyboard"), "wikpfy152"),
    (("memory152", "AA"), "memory152"),
    (("stream152", "key"), "cxpoek152"),
    (("stream152", "lemon"), "dxdsnx152"),
    (("stream152", "a"), "stream152"),
    (("stream152", "zz"), "rsqdzl152"),
    (("stream152", "AgentU"), "szvrtg152"),
    (("stream152", "keyboard"), "cxpfom152"),
    (("stream152", "AA"), "stream152"),
    (("context152", "key"), "msldivd152"),
    (("context152", "lemon"), "nszhrix152"),
    (("context152", "a"), "context152"),
    (("context152", "zz"), "bnmsdws152"),
    (("context152", "AgentU"), "curgxrt152"),
    (("context152", "keyboard"), "mslusxk152"),
    (("context152", "AA"), "context152"),
    (("knowledge152", "key"), "urmgpcnkc152"),
    (("knowledge152", "lemon"), "vrakyphss152"),
    (("knowledge152", "a"), "knowledge152"),
    (("knowledge152", "zz"), "jmnvkdcfd152"),
    (("knowledge152", "AgentU"), "ktsjeydmi152"),
    (("knowledge152", "keyboard"), "urmxzeujo152"),
    (("knowledge152", "AA"), "knowledge152"),
    (("vector152", "key"), "fiadsp152"),
    (("vector152", "lemon"), "giohbc152"),
    (("vector152", "a"), "vector152"),
    (("vector152", "zz"), "udbsnq152"),
    (("vector152", "AgentU"), "vkgghl152"),
    (("vector152", "keyboard"), "fiaucr152"),
    (("vector152", "AA"), "vector152"),
    (("processor152", "key"), "zvmmiqcsp152"),
    (("processor152", "lemon"), "avaqrdwaf152"),
    (("processor152", "a"), "processor152"),
    (("processor152", "zz"), "oqnbdrrnq152"),
    (("processor152", "AgentU"), "pxspxmsuv152"),
    (("processor152", "keyboard"), "zvmdssjrb152"),
    (("processor152", "AA"), "processor152"),
    (("reasoning152", "key"), "biycslsre152"),
    (("reasoning152", "lemon"), "cimgbymzu152"),
    (("reasoning152", "a"), "reasoning152"),
    (("reasoning152", "zz"), "qdzrnmhmf152"),
    (("reasoning152", "AgentU"), "rkefhhitk152"),
    (("reasoning152", "keyboard"), "biytcnzqq152"),
    (("reasoning152", "AA"), "reasoning152"),
    (("machine152", "key"), "wearmlo152"),
    (("machine152", "lemon"), "xeovvyi152"),
    (("machine152", "a"), "machine152"),
    (("machine152", "zz"), "lzbghmd152"),
    (("machine152", "AgentU"), "mggubhe152"),
    (("machine152", "keyboard"), "weaiwnv152"),
    (("machine152", "AA"), "machine152"),
    (("learning152", "key"), "viybrgxk152"),
    (("learning152", "lemon"), "wimfatrs152"),
    (("learning152", "a"), "learning152"),
    (("learning152", "zz"), "kdzqmhmf152"),
    (("learning152", "AgentU"), "lkeegcnm152"),
    (("learning152", "keyboard"), "viysbiej152"),
    (("learning152", "AA"), "learning152"),
    (("model152", "key"), "wsbop152"),
    (("model152", "lemon"), "xspsy152"),
    (("model152", "a"), "model152"),
    (("model152", "zz"), "lncdk152"),
    (("model152", "AgentU"), "muhre152"),
    (("model152", "keyboard"), "wsbfz152"),
    (("model152", "AA"), "model152"),
    (("token152", "key"), "dsior152"),
    (("token152", "lemon"), "eswsa152"),
    (("token152", "a"), "token152"),
    (("token152", "zz"), "snjdm152"),
    (("token152", "AgentU"), "tuorg152"),
    (("token152", "keyboard"), "dsifb152"),
    (("token152", "AA"), "token152"),
    (("prompt152", "key"), "zvmwtr152"),
    (("prompt152", "lemon"), "avaace152"),
    (("prompt152", "a"), "prompt152"),
    (("prompt152", "zz"), "oqnlos152"),
    (("prompt152", "AgentU"), "pxszin152"),
    (("prompt152", "keyboard"), "zvmndt152"),
    (("prompt152", "AA"), "prompt152"),
    (("session152", "key"), "ciqcmmx152"),
    (("session152", "lemon"), "diegvzr152"),
    (("session152", "a"), "session152"),
    (("session152", "zz"), "rdrrhnm152"),
    (("session152", "AgentU"), "skwfbin152"),
    (("session152", "keyboard"), "ciqtwoe152"),
    (("session152", "AA"), "session152"),
    (("library152", "key"), "vmzbepi152"),
    (("library152", "lemon"), "wmnfncc152"),
    (("library152", "a"), "library152"),
    (("library152", "zz"), "khaqzqx152"),
    (("library152", "AgentU"), "lofetly152"),
    (("library152", "keyboard"), "vmzsorp152"),
    (("library152", "AA"), "library152"),
    (("service152", "key"), "cipfmao152"),
    (("service152", "lemon"), "didjvni152"),
    (("service152", "a"), "service152"),
    (("service152", "zz"), "rdquhbd152"),
    (("service152", "AgentU"), "skvibwe152"),
    (("service152", "keyboard"), "cipwwcv152"),
    (("service152", "AA"), "service152"),
    (("gateway152", "key"), "qeroayi152"),
    (("gateway152", "lemon"), "refsjlc152"),
    (("gateway152", "a"), "gateway152"),
    (("gateway152", "zz"), "fzsdvzx152"),
    (("gateway152", "AgentU"), "ggxrpuy152"),
    (("gateway152", "keyboard"), "qerfkap152"),
    (("gateway152", "AA"), "gateway152"),
    (("storage152", "key"), "cxmbeeo152"),
    (("storage152", "lemon"), "dxafnri152"),
    (("storage152", "a"), "storage152"),
    (("storage152", "zz"), "rsnqzfd152"),
    (("storage152", "AgentU"), "szsetae152"),
    (("storage152", "keyboard"), "cxmsogv152"),
    (("storage152", "AA"), "storage152"),
    (("network152", "key"), "xirgspu152"),
    (("network152", "lemon"), "yifkbco152"),
    (("network152", "a"), "network152"),
    (("network152", "zz"), "mdsvnqj152"),
    (("network152", "AgentU"), "nkxjhlk152"),
    (("network152", "keyboard"), "xirxcrb152"),
    (("network152", "AA"), "network152"),
    (("latency152", "key"), "verorai152"),
    (("latency152", "lemon"), "wefsanc152"),
    (("latency152", "a"), "latency152"),
    (("latency152", "zz"), "kzsdmbx152"),
    (("latency152", "AgentU"), "lgxrgwy152"),
    (("latency152", "keyboard"), "verfbcp152"),
    (("latency152", "AA"), "latency152"),
    (("buffer152", "key"), "lydpip152"),
    (("buffer152", "lemon"), "myrtrc152"),
    (("buffer152", "a"), "buffer152"),
    (("buffer152", "zz"), "ateedq152"),
    (("buffer152", "AgentU"), "bajsxl152"),
    (("buffer152", "keyboard"), "lydgsr152"),
    (("buffer152", "AA"), "buffer152"),
    (("queue152", "key"), "aycei152"),
    (("queue152", "lemon"), "byqir152"),
    (("queue152", "a"), "queue152"),
    (("queue152", "zz"), "ptdtd152"),
    (("queue152", "AgentU"), "qaihx152"),
    (("queue152", "keyboard"), "aycvs152"),
    (("queue152", "AA"), "queue152"),
    (("worker152", "key"), "gspuip152"),
    (("worker152", "lemon"), "hsdyrc152"),
    (("worker152", "a"), "worker152"),
    (("worker152", "zz"), "vnqjdq152"),
    (("worker152", "AgentU"), "wuvxxl152"),
    (("worker152", "keyboard"), "gsplsr152"),
    (("worker152", "AA"), "worker152"),
    (("kernel152", "key"), "uipxij152"),
    (("kernel152", "lemon"), "vidbrw152"),
    (("kernel152", "a"), "kernel152"),
    (("kernel152", "zz"), "jdqmdk152"),
    (("kernel152", "AgentU"), "kkvaxf152"),
    (("kernel152", "keyboard"), "uiposl152"),
    (("kernel152", "AA"), "kernel152"),
    (("signal152", "key"), "cmexej152"),
    (("signal152", "lemon"), "dmsbnw152"),
    (("signal152", "a"), "signal152"),
    (("signal152", "zz"), "rhfmzk152"),
    (("signal152", "AgentU"), "sokatf152"),
    (("signal152", "keyboard"), "cmeool152"),
    (("signal152", "AA"), "signal152"),
    (("packet152", "key"), "zeauir152"),
    (("packet152", "lemon"), "aeoyre152"),
    (("packet152", "a"), "packet152"),
    (("packet152", "zz"), "ozbjds152"),
    (("packet152", "AgentU"), "pggxxn152"),
    (("packet152", "keyboard"), "zealst152"),
    (("packet152", "AA"), "packet152"),
    (("router152", "key"), "bssdip152"),
    (("router152", "lemon"), "csghrc152"),
    (("router152", "a"), "router152"),
    (("router152", "zz"), "qntsdq152"),
    (("router152", "AgentU"), "ruygxl152"),
    (("router152", "keyboard"), "bssusr152"),
    (("router152", "AA"), "router152"),
    (("cluster152", "key"), "mpscxcb152"),
    (("cluster152", "lemon"), "npgggpv152"),
    (("cluster152", "a"), "cluster152"),
    (("cluster152", "zz"), "bktrsdq152"),
    (("cluster152", "AgentU"), "cryfmyr152"),
    (("cluster152", "keyboard"), "mpsthei152"),
    (("cluster152", "AA"), "cluster152"),
    (("mirror152", "key"), "wmpbsp152"),
    (("mirror152", "lemon"), "xmdfbc152"),
    (("mirror152", "a"), "mirror152"),
    (("mirror152", "zz"), "lhqqnq152"),
    (("mirror152", "AgentU"), "movehl152"),
    (("mirror152", "keyboard"), "wmpscr152"),
    (("mirror152", "AA"), "mirror152"),
    (("filter152", "key"), "pmjdip152"),
    (("filter152", "lemon"), "qmxhrc152"),
    (("filter152", "a"), "filter152"),
    (("filter152", "zz"), "ehksdq152"),
    (("filter152", "AgentU"), "fopgxl152"),
    (("filter152", "keyboard"), "pmjusr152"),
    (("filter152", "AA"), "filter152"),
    (("ranking152", "key"), "belumlq152"),
    (("ranking152", "lemon"), "cezyvyk152"),
    (("ranking152", "a"), "ranking152"),
    (("ranking152", "zz"), "qzmjhmf152"),
    (("ranking152", "AgentU"), "rgrxbhg152"),
    (("ranking152", "keyboard"), "bellwnx152"),
    (("ranking152", "AA"), "ranking152"),
    (("encoding152", "key"), "orayhgxk152"),
    (("encoding152", "lemon"), "procqtrs152"),
    (("encoding152", "a"), "encoding152"),
    (("encoding152", "zz"), "dmbnchmf152"),
    (("encoding152", "AgentU"), "etgbwcnm152"),
    (("encoding152", "keyboard"), "orapriej152"),
    (("encoding152", "AA"), "encoding152"),
    (("mapping152", "key"), "wenzmlq152"),
    (("mapping152", "lemon"), "xebdvyk152"),
    (("mapping152", "a"), "mapping152"),
    (("mapping152", "zz"), "lzoohmf152"),
    (("mapping152", "AgentU"), "mgtcbhg152"),
    (("mapping152", "keyboard"), "wenqwnx152"),
    (("mapping152", "AA"), "mapping152"),
    (("record152", "key"), "biayvb152"),
    (("record152", "lemon"), "cioceo152"),
    (("record152", "a"), "record152"),
    (("record152", "zz"), "qdbnqc152"),
    (("record152", "AgentU"), "rkgbkx152"),
    (("record152", "keyboard"), "biapfd152"),
    (("record152", "AA"), "record152"),
    (("candle152", "key"), "melnpc152"),
    (("candle152", "lemon"), "nezryp152"),
    (("candle152", "a"), "candle152"),
    (("candle152", "zz"), "bzmckd152"),
    (("candle152", "AgentU"), "cgrqey152"),
    (("candle152", "keyboard"), "meleze152"),
    (("candle152", "AA"), "candle152"),
    (("thread152", "key"), "dlpoeb152"),
    (("thread152", "lemon"), "eldsno152"),
    (("thread152", "a"), "thread152"),
    (("thread152", "zz"), "sgqdzc152"),
    (("thread152", "AgentU"), "tnvrtx152"),
    (("thread152", "keyboard"), "dlpfod152"),
    (("thread152", "AA"), "thread152"),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 152: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 152: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "a"),
        "round 152: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 152: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 152: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 152: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", "AA"),
        "round 152: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "key"),
        "bssxh 152: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 152: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "a"),
        "round 152: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 152: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 152: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 152: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", "AA"),
        "round 152: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 152: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 152: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "a"),
        "round 152: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 152: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 152: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 152: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", "AA"),
        "round 152: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 152: the processor reads the record then stops", "key"),
        "bssxh 152: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 152: the processor reads the record then stops", "lemon"),
        "csgbq 152: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 152: the processor reads the record then stops", "a"),
        "round 152: the processor reads the record then stops",
    ),
    (
        ("round 152: the processor reads the record then stops", "zz"),
        "qntmc 152: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 152: the processor reads the record then stops", "AgentU"),
        "ruyaw 152: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 152: the processor reads the record then stops", "keyboard"),
        "bssor 152: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 152: the processor reads the record then stops", "AA"),
        "round 152: the processor reads the record then stops",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "key"),
        "bssxh 152: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "lemon"),
        "csgbq 152: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "a"),
        "round 152: a worker pulls the next task from the queue",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "zz"),
        "qntmc 152: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 152: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "keyboard"),
        "bssor 152: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 152: a worker pulls the next task from the queue", "AA"),
        "round 152: a worker pulls the next task from the queue",
    ),
    (
        ("round 152: signals travel through the network layer", "key"),
        "bssxh 152: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 152: signals travel through the network layer", "lemon"),
        "csgbq 152: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 152: signals travel through the network layer", "a"),
        "round 152: signals travel through the network layer",
    ),
    (
        ("round 152: signals travel through the network layer", "zz"),
        "qntmc 152: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 152: signals travel through the network layer", "AgentU"),
        "ruyaw 152: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 152: signals travel through the network layer", "keyboard"),
        "bssor 152: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 152: signals travel through the network layer", "AA"),
        "round 152: signals travel through the network layer",
    ),
    (
        ("round 152: the gateway routes each request by policy", "key"),
        "bssxh 152: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 152: the gateway routes each request by policy", "lemon"),
        "csgbq 152: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 152: the gateway routes each request by policy", "a"),
        "round 152: the gateway routes each request by policy",
    ),
    (
        ("round 152: the gateway routes each request by policy", "zz"),
        "qntmc 152: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 152: the gateway routes each request by policy", "AgentU"),
        "ruyaw 152: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 152: the gateway routes each request by policy", "keyboard"),
        "bssor 152: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 152: the gateway routes each request by policy", "AA"),
        "round 152: the gateway routes each request by policy",
    ),
    (("round 152: memory grows until the buffer is full", "key"), "bssxh 152: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 152: memory grows until the buffer is full", "lemon"), "csgbq 152: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 152: memory grows until the buffer is full", "a"), "round 152: memory grows until the buffer is full"),
    (("round 152: memory grows until the buffer is full", "zz"), "qntmc 152: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 152: memory grows until the buffer is full", "AgentU"),
        "ruyaw 152: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 152: memory grows until the buffer is full", "keyboard"),
        "bssor 152: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 152: memory grows until the buffer is full", "AA"), "round 152: memory grows until the buffer is full"),
    (("round 152: the cluster mirrors every packet twice", "key"), "bssxh 152: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 152: the cluster mirrors every packet twice", "lemon"),
        "csgbq 152: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 152: the cluster mirrors every packet twice", "a"), "round 152: the cluster mirrors every packet twice"),
    (("round 152: the cluster mirrors every packet twice", "zz"), "qntmc 152: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 152: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 152: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 152: the cluster mirrors every packet twice", "keyboard"),
        "bssor 152: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 152: the cluster mirrors every packet twice", "AA"), "round 152: the cluster mirrors every packet twice"),
    (
        ("round 152: ranking uses tokens learned from the corpus", "key"),
        "bssxh 152: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 152: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", "a"),
        "round 152: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 152: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 152: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 152: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", "AA"),
        "round 152: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 152: a long session ends when the candle dies", "key"),
        "bssxh 152: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 152: a long session ends when the candle dies", "lemon"),
        "csgbq 152: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 152: a long session ends when the candle dies", "a"),
        "round 152: a long session ends when the candle dies",
    ),
    (
        ("round 152: a long session ends when the candle dies", "zz"),
        "qntmc 152: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 152: a long session ends when the candle dies", "AgentU"),
        "ruyaw 152: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 152: a long session ends when the candle dies", "keyboard"),
        "bssor 152: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 152: a long session ends when the candle dies", "AA"),
        "round 152: a long session ends when the candle dies",
    ),
    (("round 152: encode the prompt then map the result", "key"), "bssxh 152: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 152: encode the prompt then map the result", "lemon"), "csgbq 152: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 152: encode the prompt then map the result", "a"), "round 152: encode the prompt then map the result"),
    (("round 152: encode the prompt then map the result", "zz"), "qntmc 152: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 152: encode the prompt then map the result", "AgentU"),
        "ruyaw 152: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 152: encode the prompt then map the result", "keyboard"),
        "bssor 152: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 152: encode the prompt then map the result", "AA"), "round 152: encode the prompt then map the result"),
    (("round 152: the kernel wakes the worker at dawn", "key"), "bssxh 152: rri iovlop ukocc xfo ambocb er neux"),
    (("round 152: the kernel wakes the worker at dawn", "lemon"), "csgbq 152: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 152: the kernel wakes the worker at dawn", "a"), "round 152: the kernel wakes the worker at dawn"),
    (("round 152: the kernel wakes the worker at dawn", "zz"), "qntmc 152: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 152: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 152: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 152: the kernel wakes the worker at dawn", "keyboard"), "bssor 152: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 152: the kernel wakes the worker at dawn", "AA"), "round 152: the kernel wakes the worker at dawn"),
    (("round 152: service latency drops after the patch", "key"), "bssxh 152: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 152: service latency drops after the patch", "lemon"), "csgbq 152: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 152: service latency drops after the patch", "a"), "round 152: service latency drops after the patch"),
    (("round 152: service latency drops after the patch", "zz"), "qntmc 152: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 152: service latency drops after the patch", "AgentU"),
        "ruyaw 152: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 152: service latency drops after the patch", "keyboard"),
        "bssor 152: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 152: service latency drops after the patch", "AA"), "round 152: service latency drops after the patch"),
    (
        ("round 152: the library caches every vector it sees", "key"),
        "bssxh 152: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 152: the library caches every vector it sees", "lemon"),
        "csgbq 152: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 152: the library caches every vector it sees", "a"), "round 152: the library caches every vector it sees"),
    (
        ("round 152: the library caches every vector it sees", "zz"),
        "qntmc 152: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 152: the library caches every vector it sees", "AgentU"),
        "ruyaw 152: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 152: the library caches every vector it sees", "keyboard"),
        "bssor 152: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 152: the library caches every vector it sees", "AA"),
        "round 152: the library caches every vector it sees",
    ),
    (("round 152: agents argue then the debate resolves", "key"), "bssxh 152: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 152: agents argue then the debate resolves", "lemon"), "csgbq 152: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 152: agents argue then the debate resolves", "a"), "round 152: agents argue then the debate resolves"),
    (("round 152: agents argue then the debate resolves", "zz"), "qntmc 152: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 152: agents argue then the debate resolves", "AgentU"),
        "ruyaw 152: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 152: agents argue then the debate resolves", "keyboard"),
        "bssor 152: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 152: agents argue then the debate resolves", "AA"), "round 152: agents argue then the debate resolves"),
    (("round 152: the filter keeps only strong matches", "key"), "bssxh 152: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 152: the filter keeps only strong matches", "lemon"), "csgbq 152: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 152: the filter keeps only strong matches", "a"), "round 152: the filter keeps only strong matches"),
    (("round 152: the filter keeps only strong matches", "zz"), "qntmc 152: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 152: the filter keeps only strong matches", "AgentU"), "ruyaw 152: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 152: the filter keeps only strong matches", "keyboard"),
        "bssor 152: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 152: the filter keeps only strong matches", "AA"), "round 152: the filter keeps only strong matches"),
    (("round 152: the model answers with a short reply", "key"), "bssxh 152: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 152: the model answers with a short reply", "lemon"), "csgbq 152: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 152: the model answers with a short reply", "a"), "round 152: the model answers with a short reply"),
    (("round 152: the model answers with a short reply", "zz"), "qntmc 152: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 152: the model answers with a short reply", "AgentU"), "ruyaw 152: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 152: the model answers with a short reply", "keyboard"),
        "bssor 152: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 152: the model answers with a short reply", "AA"), "round 152: the model answers with a short reply"),
    (
        ("round 152: the recorder stores the reasoning trace", "key"),
        "bssxh 152: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 152: the recorder stores the reasoning trace", "lemon"),
        "csgbq 152: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 152: the recorder stores the reasoning trace", "a"), "round 152: the recorder stores the reasoning trace"),
    (
        ("round 152: the recorder stores the reasoning trace", "zz"),
        "qntmc 152: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 152: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 152: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 152: the recorder stores the reasoning trace", "keyboard"),
        "bssor 152: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 152: the recorder stores the reasoning trace", "AA"),
        "round 152: the recorder stores the reasoning trace",
    ),
    (("round 152: the angel watches the processor run", "key"), "bssxh 152: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 152: the angel watches the processor run", "lemon"), "csgbq 152: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 152: the angel watches the processor run", "a"), "round 152: the angel watches the processor run"),
    (("round 152: the angel watches the processor run", "zz"), "qntmc 152: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 152: the angel watches the processor run", "AgentU"), "ruyaw 152: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 152: the angel watches the processor run", "keyboard"), "bssor 152: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 152: the angel watches the processor run", "AA"), "round 152: the angel watches the processor run"),
    (("round 152: angle of the vector decides the match", "key"), "bssxh 152: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 152: angle of the vector decides the match", "lemon"), "csgbq 152: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 152: angle of the vector decides the match", "a"), "round 152: angle of the vector decides the match"),
    (("round 152: angle of the vector decides the match", "zz"), "qntmc 152: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 152: angle of the vector decides the match", "AgentU"),
        "ruyaw 152: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 152: angle of the vector decides the match", "keyboard"),
        "bssor 152: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 152: angle of the vector decides the match", "AA"), "round 152: angle of the vector decides the match"),
    (
        ("round 152: the candle burns twice as long at night", "key"),
        "bssxh 152: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 152: the candle burns twice as long at night", "lemon"),
        "csgbq 152: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 152: the candle burns twice as long at night", "a"), "round 152: the candle burns twice as long at night"),
    (
        ("round 152: the candle burns twice as long at night", "zz"),
        "qntmc 152: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 152: the candle burns twice as long at night", "AgentU"),
        "ruyaw 152: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 152: the candle burns twice as long at night", "keyboard"),
        "bssor 152: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 152: the candle burns twice as long at night", "AA"),
        "round 152: the candle burns twice as long at night",
    ),
    (("round 152: a mirror of the universe in one line", "key"), "bssxh 152: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 152: a mirror of the universe in one line", "lemon"), "csgbq 152: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 152: a mirror of the universe in one line", "a"), "round 152: a mirror of the universe in one line"),
    (("round 152: a mirror of the universe in one line", "zz"), "qntmc 152: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 152: a mirror of the universe in one line", "AgentU"), "ruyaw 152: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 152: a mirror of the universe in one line", "keyboard"),
        "bssor 152: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 152: a mirror of the universe in one line", "AA"), "round 152: a mirror of the universe in one line"),
    (("round 152: the queue drains before the storm", "key"), "bssxh 152: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 152: the queue drains before the storm", "lemon"), "csgbq 152: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 152: the queue drains before the storm", "a"), "round 152: the queue drains before the storm"),
    (("round 152: the queue drains before the storm", "zz"), "qntmc 152: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 152: the queue drains before the storm", "AgentU"), "ruyaw 152: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 152: the queue drains before the storm", "keyboard"), "bssor 152: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 152: the queue drains before the storm", "AA"), "round 152: the queue drains before the storm"),
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
