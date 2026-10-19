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
    (("kitten161", "key"), "umrdil161"),
    (("kitten161", "lemon"), "vmfhry161"),
    (("kitten161", "a"), "kitten161"),
    (("kitten161", "zz"), "jhssdm161"),
    (("kitten161", "AgentU"), "koxgxh161"),
    (("kitten161", "keyboard"), "umrusn161"),
    (("kitten161", "AA"), "kitten161"),
    (("sitting161", "key"), "cmrdmlq161"),
    (("sitting161", "lemon"), "dmfhvyk161"),
    (("sitting161", "a"), "sitting161"),
    (("sitting161", "zz"), "rhsshmf161"),
    (("sitting161", "AgentU"), "soxgbhg161"),
    (("sitting161", "keyboard"), "cmruwnx161"),
    (("sitting161", "AA"), "sitting161"),
    (("agent161", "key"), "kkcxx161"),
    (("agent161", "lemon"), "lkqbg161"),
    (("agent161", "a"), "agent161"),
    (("agent161", "zz"), "zfdms161"),
    (("agent161", "AgentU"), "amiam161"),
    (("agent161", "keyboard"), "kkcoh161"),
    (("agent161", "AA"), "agent161"),
    (("angle161", "key"), "krevi161"),
    (("angle161", "lemon"), "lrszr161"),
    (("angle161", "a"), "angle161"),
    (("angle161", "zz"), "zmfkd161"),
    (("angle161", "AgentU"), "atkyx161"),
    (("angle161", "keyboard"), "krems161"),
    (("angle161", "AA"), "angle161"),
    (("universe161", "key"), "ergfipci161"),
    (("universe161", "lemon"), "frujrcwq161"),
    (("universe161", "a"), "universe161"),
    (("universe161", "zz"), "tmhudqrd161"),
    (("universe161", "AgentU"), "utmixlsk161"),
    (("universe161", "keyboard"), "ergwsrjh161"),
    (("universe161", "AA"), "universe161"),
    (("memory161", "key"), "wikyvw161"),
    (("memory161", "lemon"), "xiycej161"),
    (("memory161", "a"), "memory161"),
    (("memory161", "zz"), "ldlnqx161"),
    (("memory161", "AgentU"), "mkqbks161"),
    (("memory161", "keyboard"), "wikpfy161"),
    (("memory161", "AA"), "memory161"),
    (("stream161", "key"), "cxpoek161"),
    (("stream161", "lemon"), "dxdsnx161"),
    (("stream161", "a"), "stream161"),
    (("stream161", "zz"), "rsqdzl161"),
    (("stream161", "AgentU"), "szvrtg161"),
    (("stream161", "keyboard"), "cxpfom161"),
    (("stream161", "AA"), "stream161"),
    (("context161", "key"), "msldivd161"),
    (("context161", "lemon"), "nszhrix161"),
    (("context161", "a"), "context161"),
    (("context161", "zz"), "bnmsdws161"),
    (("context161", "AgentU"), "curgxrt161"),
    (("context161", "keyboard"), "mslusxk161"),
    (("context161", "AA"), "context161"),
    (("knowledge161", "key"), "urmgpcnkc161"),
    (("knowledge161", "lemon"), "vrakyphss161"),
    (("knowledge161", "a"), "knowledge161"),
    (("knowledge161", "zz"), "jmnvkdcfd161"),
    (("knowledge161", "AgentU"), "ktsjeydmi161"),
    (("knowledge161", "keyboard"), "urmxzeujo161"),
    (("knowledge161", "AA"), "knowledge161"),
    (("vector161", "key"), "fiadsp161"),
    (("vector161", "lemon"), "giohbc161"),
    (("vector161", "a"), "vector161"),
    (("vector161", "zz"), "udbsnq161"),
    (("vector161", "AgentU"), "vkgghl161"),
    (("vector161", "keyboard"), "fiaucr161"),
    (("vector161", "AA"), "vector161"),
    (("processor161", "key"), "zvmmiqcsp161"),
    (("processor161", "lemon"), "avaqrdwaf161"),
    (("processor161", "a"), "processor161"),
    (("processor161", "zz"), "oqnbdrrnq161"),
    (("processor161", "AgentU"), "pxspxmsuv161"),
    (("processor161", "keyboard"), "zvmdssjrb161"),
    (("processor161", "AA"), "processor161"),
    (("reasoning161", "key"), "biycslsre161"),
    (("reasoning161", "lemon"), "cimgbymzu161"),
    (("reasoning161", "a"), "reasoning161"),
    (("reasoning161", "zz"), "qdzrnmhmf161"),
    (("reasoning161", "AgentU"), "rkefhhitk161"),
    (("reasoning161", "keyboard"), "biytcnzqq161"),
    (("reasoning161", "AA"), "reasoning161"),
    (("machine161", "key"), "wearmlo161"),
    (("machine161", "lemon"), "xeovvyi161"),
    (("machine161", "a"), "machine161"),
    (("machine161", "zz"), "lzbghmd161"),
    (("machine161", "AgentU"), "mggubhe161"),
    (("machine161", "keyboard"), "weaiwnv161"),
    (("machine161", "AA"), "machine161"),
    (("learning161", "key"), "viybrgxk161"),
    (("learning161", "lemon"), "wimfatrs161"),
    (("learning161", "a"), "learning161"),
    (("learning161", "zz"), "kdzqmhmf161"),
    (("learning161", "AgentU"), "lkeegcnm161"),
    (("learning161", "keyboard"), "viysbiej161"),
    (("learning161", "AA"), "learning161"),
    (("model161", "key"), "wsbop161"),
    (("model161", "lemon"), "xspsy161"),
    (("model161", "a"), "model161"),
    (("model161", "zz"), "lncdk161"),
    (("model161", "AgentU"), "muhre161"),
    (("model161", "keyboard"), "wsbfz161"),
    (("model161", "AA"), "model161"),
    (("token161", "key"), "dsior161"),
    (("token161", "lemon"), "eswsa161"),
    (("token161", "a"), "token161"),
    (("token161", "zz"), "snjdm161"),
    (("token161", "AgentU"), "tuorg161"),
    (("token161", "keyboard"), "dsifb161"),
    (("token161", "AA"), "token161"),
    (("prompt161", "key"), "zvmwtr161"),
    (("prompt161", "lemon"), "avaace161"),
    (("prompt161", "a"), "prompt161"),
    (("prompt161", "zz"), "oqnlos161"),
    (("prompt161", "AgentU"), "pxszin161"),
    (("prompt161", "keyboard"), "zvmndt161"),
    (("prompt161", "AA"), "prompt161"),
    (("session161", "key"), "ciqcmmx161"),
    (("session161", "lemon"), "diegvzr161"),
    (("session161", "a"), "session161"),
    (("session161", "zz"), "rdrrhnm161"),
    (("session161", "AgentU"), "skwfbin161"),
    (("session161", "keyboard"), "ciqtwoe161"),
    (("session161", "AA"), "session161"),
    (("library161", "key"), "vmzbepi161"),
    (("library161", "lemon"), "wmnfncc161"),
    (("library161", "a"), "library161"),
    (("library161", "zz"), "khaqzqx161"),
    (("library161", "AgentU"), "lofetly161"),
    (("library161", "keyboard"), "vmzsorp161"),
    (("library161", "AA"), "library161"),
    (("service161", "key"), "cipfmao161"),
    (("service161", "lemon"), "didjvni161"),
    (("service161", "a"), "service161"),
    (("service161", "zz"), "rdquhbd161"),
    (("service161", "AgentU"), "skvibwe161"),
    (("service161", "keyboard"), "cipwwcv161"),
    (("service161", "AA"), "service161"),
    (("gateway161", "key"), "qeroayi161"),
    (("gateway161", "lemon"), "refsjlc161"),
    (("gateway161", "a"), "gateway161"),
    (("gateway161", "zz"), "fzsdvzx161"),
    (("gateway161", "AgentU"), "ggxrpuy161"),
    (("gateway161", "keyboard"), "qerfkap161"),
    (("gateway161", "AA"), "gateway161"),
    (("storage161", "key"), "cxmbeeo161"),
    (("storage161", "lemon"), "dxafnri161"),
    (("storage161", "a"), "storage161"),
    (("storage161", "zz"), "rsnqzfd161"),
    (("storage161", "AgentU"), "szsetae161"),
    (("storage161", "keyboard"), "cxmsogv161"),
    (("storage161", "AA"), "storage161"),
    (("network161", "key"), "xirgspu161"),
    (("network161", "lemon"), "yifkbco161"),
    (("network161", "a"), "network161"),
    (("network161", "zz"), "mdsvnqj161"),
    (("network161", "AgentU"), "nkxjhlk161"),
    (("network161", "keyboard"), "xirxcrb161"),
    (("network161", "AA"), "network161"),
    (("latency161", "key"), "verorai161"),
    (("latency161", "lemon"), "wefsanc161"),
    (("latency161", "a"), "latency161"),
    (("latency161", "zz"), "kzsdmbx161"),
    (("latency161", "AgentU"), "lgxrgwy161"),
    (("latency161", "keyboard"), "verfbcp161"),
    (("latency161", "AA"), "latency161"),
    (("buffer161", "key"), "lydpip161"),
    (("buffer161", "lemon"), "myrtrc161"),
    (("buffer161", "a"), "buffer161"),
    (("buffer161", "zz"), "ateedq161"),
    (("buffer161", "AgentU"), "bajsxl161"),
    (("buffer161", "keyboard"), "lydgsr161"),
    (("buffer161", "AA"), "buffer161"),
    (("queue161", "key"), "aycei161"),
    (("queue161", "lemon"), "byqir161"),
    (("queue161", "a"), "queue161"),
    (("queue161", "zz"), "ptdtd161"),
    (("queue161", "AgentU"), "qaihx161"),
    (("queue161", "keyboard"), "aycvs161"),
    (("queue161", "AA"), "queue161"),
    (("worker161", "key"), "gspuip161"),
    (("worker161", "lemon"), "hsdyrc161"),
    (("worker161", "a"), "worker161"),
    (("worker161", "zz"), "vnqjdq161"),
    (("worker161", "AgentU"), "wuvxxl161"),
    (("worker161", "keyboard"), "gsplsr161"),
    (("worker161", "AA"), "worker161"),
    (("kernel161", "key"), "uipxij161"),
    (("kernel161", "lemon"), "vidbrw161"),
    (("kernel161", "a"), "kernel161"),
    (("kernel161", "zz"), "jdqmdk161"),
    (("kernel161", "AgentU"), "kkvaxf161"),
    (("kernel161", "keyboard"), "uiposl161"),
    (("kernel161", "AA"), "kernel161"),
    (("signal161", "key"), "cmexej161"),
    (("signal161", "lemon"), "dmsbnw161"),
    (("signal161", "a"), "signal161"),
    (("signal161", "zz"), "rhfmzk161"),
    (("signal161", "AgentU"), "sokatf161"),
    (("signal161", "keyboard"), "cmeool161"),
    (("signal161", "AA"), "signal161"),
    (("packet161", "key"), "zeauir161"),
    (("packet161", "lemon"), "aeoyre161"),
    (("packet161", "a"), "packet161"),
    (("packet161", "zz"), "ozbjds161"),
    (("packet161", "AgentU"), "pggxxn161"),
    (("packet161", "keyboard"), "zealst161"),
    (("packet161", "AA"), "packet161"),
    (("router161", "key"), "bssdip161"),
    (("router161", "lemon"), "csghrc161"),
    (("router161", "a"), "router161"),
    (("router161", "zz"), "qntsdq161"),
    (("router161", "AgentU"), "ruygxl161"),
    (("router161", "keyboard"), "bssusr161"),
    (("router161", "AA"), "router161"),
    (("cluster161", "key"), "mpscxcb161"),
    (("cluster161", "lemon"), "npgggpv161"),
    (("cluster161", "a"), "cluster161"),
    (("cluster161", "zz"), "bktrsdq161"),
    (("cluster161", "AgentU"), "cryfmyr161"),
    (("cluster161", "keyboard"), "mpsthei161"),
    (("cluster161", "AA"), "cluster161"),
    (("mirror161", "key"), "wmpbsp161"),
    (("mirror161", "lemon"), "xmdfbc161"),
    (("mirror161", "a"), "mirror161"),
    (("mirror161", "zz"), "lhqqnq161"),
    (("mirror161", "AgentU"), "movehl161"),
    (("mirror161", "keyboard"), "wmpscr161"),
    (("mirror161", "AA"), "mirror161"),
    (("filter161", "key"), "pmjdip161"),
    (("filter161", "lemon"), "qmxhrc161"),
    (("filter161", "a"), "filter161"),
    (("filter161", "zz"), "ehksdq161"),
    (("filter161", "AgentU"), "fopgxl161"),
    (("filter161", "keyboard"), "pmjusr161"),
    (("filter161", "AA"), "filter161"),
    (("ranking161", "key"), "belumlq161"),
    (("ranking161", "lemon"), "cezyvyk161"),
    (("ranking161", "a"), "ranking161"),
    (("ranking161", "zz"), "qzmjhmf161"),
    (("ranking161", "AgentU"), "rgrxbhg161"),
    (("ranking161", "keyboard"), "bellwnx161"),
    (("ranking161", "AA"), "ranking161"),
    (("encoding161", "key"), "orayhgxk161"),
    (("encoding161", "lemon"), "procqtrs161"),
    (("encoding161", "a"), "encoding161"),
    (("encoding161", "zz"), "dmbnchmf161"),
    (("encoding161", "AgentU"), "etgbwcnm161"),
    (("encoding161", "keyboard"), "orapriej161"),
    (("encoding161", "AA"), "encoding161"),
    (("mapping161", "key"), "wenzmlq161"),
    (("mapping161", "lemon"), "xebdvyk161"),
    (("mapping161", "a"), "mapping161"),
    (("mapping161", "zz"), "lzoohmf161"),
    (("mapping161", "AgentU"), "mgtcbhg161"),
    (("mapping161", "keyboard"), "wenqwnx161"),
    (("mapping161", "AA"), "mapping161"),
    (("record161", "key"), "biayvb161"),
    (("record161", "lemon"), "cioceo161"),
    (("record161", "a"), "record161"),
    (("record161", "zz"), "qdbnqc161"),
    (("record161", "AgentU"), "rkgbkx161"),
    (("record161", "keyboard"), "biapfd161"),
    (("record161", "AA"), "record161"),
    (("candle161", "key"), "melnpc161"),
    (("candle161", "lemon"), "nezryp161"),
    (("candle161", "a"), "candle161"),
    (("candle161", "zz"), "bzmckd161"),
    (("candle161", "AgentU"), "cgrqey161"),
    (("candle161", "keyboard"), "meleze161"),
    (("candle161", "AA"), "candle161"),
    (("thread161", "key"), "dlpoeb161"),
    (("thread161", "lemon"), "eldsno161"),
    (("thread161", "a"), "thread161"),
    (("thread161", "zz"), "sgqdzc161"),
    (("thread161", "AgentU"), "tnvrtx161"),
    (("thread161", "keyboard"), "dlpfod161"),
    (("thread161", "AA"), "thread161"),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 161: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 161: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "a"),
        "round 161: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 161: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 161: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 161: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", "AA"),
        "round 161: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "key"),
        "bssxh 161: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 161: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "a"),
        "round 161: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 161: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 161: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 161: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", "AA"),
        "round 161: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 161: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 161: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "a"),
        "round 161: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 161: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 161: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 161: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", "AA"),
        "round 161: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 161: the processor reads the record then stops", "key"),
        "bssxh 161: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 161: the processor reads the record then stops", "lemon"),
        "csgbq 161: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 161: the processor reads the record then stops", "a"),
        "round 161: the processor reads the record then stops",
    ),
    (
        ("round 161: the processor reads the record then stops", "zz"),
        "qntmc 161: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 161: the processor reads the record then stops", "AgentU"),
        "ruyaw 161: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 161: the processor reads the record then stops", "keyboard"),
        "bssor 161: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 161: the processor reads the record then stops", "AA"),
        "round 161: the processor reads the record then stops",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "key"),
        "bssxh 161: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "lemon"),
        "csgbq 161: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "a"),
        "round 161: a worker pulls the next task from the queue",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "zz"),
        "qntmc 161: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 161: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "keyboard"),
        "bssor 161: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 161: a worker pulls the next task from the queue", "AA"),
        "round 161: a worker pulls the next task from the queue",
    ),
    (
        ("round 161: signals travel through the network layer", "key"),
        "bssxh 161: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 161: signals travel through the network layer", "lemon"),
        "csgbq 161: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 161: signals travel through the network layer", "a"),
        "round 161: signals travel through the network layer",
    ),
    (
        ("round 161: signals travel through the network layer", "zz"),
        "qntmc 161: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 161: signals travel through the network layer", "AgentU"),
        "ruyaw 161: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 161: signals travel through the network layer", "keyboard"),
        "bssor 161: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 161: signals travel through the network layer", "AA"),
        "round 161: signals travel through the network layer",
    ),
    (
        ("round 161: the gateway routes each request by policy", "key"),
        "bssxh 161: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 161: the gateway routes each request by policy", "lemon"),
        "csgbq 161: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 161: the gateway routes each request by policy", "a"),
        "round 161: the gateway routes each request by policy",
    ),
    (
        ("round 161: the gateway routes each request by policy", "zz"),
        "qntmc 161: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 161: the gateway routes each request by policy", "AgentU"),
        "ruyaw 161: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 161: the gateway routes each request by policy", "keyboard"),
        "bssor 161: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 161: the gateway routes each request by policy", "AA"),
        "round 161: the gateway routes each request by policy",
    ),
    (("round 161: memory grows until the buffer is full", "key"), "bssxh 161: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 161: memory grows until the buffer is full", "lemon"), "csgbq 161: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 161: memory grows until the buffer is full", "a"), "round 161: memory grows until the buffer is full"),
    (("round 161: memory grows until the buffer is full", "zz"), "qntmc 161: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 161: memory grows until the buffer is full", "AgentU"),
        "ruyaw 161: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 161: memory grows until the buffer is full", "keyboard"),
        "bssor 161: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 161: memory grows until the buffer is full", "AA"), "round 161: memory grows until the buffer is full"),
    (("round 161: the cluster mirrors every packet twice", "key"), "bssxh 161: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 161: the cluster mirrors every packet twice", "lemon"),
        "csgbq 161: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 161: the cluster mirrors every packet twice", "a"), "round 161: the cluster mirrors every packet twice"),
    (("round 161: the cluster mirrors every packet twice", "zz"), "qntmc 161: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 161: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 161: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 161: the cluster mirrors every packet twice", "keyboard"),
        "bssor 161: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 161: the cluster mirrors every packet twice", "AA"), "round 161: the cluster mirrors every packet twice"),
    (
        ("round 161: ranking uses tokens learned from the corpus", "key"),
        "bssxh 161: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 161: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", "a"),
        "round 161: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 161: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 161: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 161: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", "AA"),
        "round 161: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 161: a long session ends when the candle dies", "key"),
        "bssxh 161: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 161: a long session ends when the candle dies", "lemon"),
        "csgbq 161: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 161: a long session ends when the candle dies", "a"),
        "round 161: a long session ends when the candle dies",
    ),
    (
        ("round 161: a long session ends when the candle dies", "zz"),
        "qntmc 161: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 161: a long session ends when the candle dies", "AgentU"),
        "ruyaw 161: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 161: a long session ends when the candle dies", "keyboard"),
        "bssor 161: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 161: a long session ends when the candle dies", "AA"),
        "round 161: a long session ends when the candle dies",
    ),
    (("round 161: encode the prompt then map the result", "key"), "bssxh 161: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 161: encode the prompt then map the result", "lemon"), "csgbq 161: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 161: encode the prompt then map the result", "a"), "round 161: encode the prompt then map the result"),
    (("round 161: encode the prompt then map the result", "zz"), "qntmc 161: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 161: encode the prompt then map the result", "AgentU"),
        "ruyaw 161: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 161: encode the prompt then map the result", "keyboard"),
        "bssor 161: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 161: encode the prompt then map the result", "AA"), "round 161: encode the prompt then map the result"),
    (("round 161: the kernel wakes the worker at dawn", "key"), "bssxh 161: rri iovlop ukocc xfo ambocb er neux"),
    (("round 161: the kernel wakes the worker at dawn", "lemon"), "csgbq 161: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 161: the kernel wakes the worker at dawn", "a"), "round 161: the kernel wakes the worker at dawn"),
    (("round 161: the kernel wakes the worker at dawn", "zz"), "qntmc 161: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 161: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 161: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 161: the kernel wakes the worker at dawn", "keyboard"), "bssor 161: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 161: the kernel wakes the worker at dawn", "AA"), "round 161: the kernel wakes the worker at dawn"),
    (("round 161: service latency drops after the patch", "key"), "bssxh 161: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 161: service latency drops after the patch", "lemon"), "csgbq 161: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 161: service latency drops after the patch", "a"), "round 161: service latency drops after the patch"),
    (("round 161: service latency drops after the patch", "zz"), "qntmc 161: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 161: service latency drops after the patch", "AgentU"),
        "ruyaw 161: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 161: service latency drops after the patch", "keyboard"),
        "bssor 161: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 161: service latency drops after the patch", "AA"), "round 161: service latency drops after the patch"),
    (
        ("round 161: the library caches every vector it sees", "key"),
        "bssxh 161: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 161: the library caches every vector it sees", "lemon"),
        "csgbq 161: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 161: the library caches every vector it sees", "a"), "round 161: the library caches every vector it sees"),
    (
        ("round 161: the library caches every vector it sees", "zz"),
        "qntmc 161: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 161: the library caches every vector it sees", "AgentU"),
        "ruyaw 161: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 161: the library caches every vector it sees", "keyboard"),
        "bssor 161: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 161: the library caches every vector it sees", "AA"),
        "round 161: the library caches every vector it sees",
    ),
    (("round 161: agents argue then the debate resolves", "key"), "bssxh 161: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 161: agents argue then the debate resolves", "lemon"), "csgbq 161: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 161: agents argue then the debate resolves", "a"), "round 161: agents argue then the debate resolves"),
    (("round 161: agents argue then the debate resolves", "zz"), "qntmc 161: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 161: agents argue then the debate resolves", "AgentU"),
        "ruyaw 161: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 161: agents argue then the debate resolves", "keyboard"),
        "bssor 161: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 161: agents argue then the debate resolves", "AA"), "round 161: agents argue then the debate resolves"),
    (("round 161: the filter keeps only strong matches", "key"), "bssxh 161: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 161: the filter keeps only strong matches", "lemon"), "csgbq 161: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 161: the filter keeps only strong matches", "a"), "round 161: the filter keeps only strong matches"),
    (("round 161: the filter keeps only strong matches", "zz"), "qntmc 161: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 161: the filter keeps only strong matches", "AgentU"), "ruyaw 161: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 161: the filter keeps only strong matches", "keyboard"),
        "bssor 161: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 161: the filter keeps only strong matches", "AA"), "round 161: the filter keeps only strong matches"),
    (("round 161: the model answers with a short reply", "key"), "bssxh 161: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 161: the model answers with a short reply", "lemon"), "csgbq 161: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 161: the model answers with a short reply", "a"), "round 161: the model answers with a short reply"),
    (("round 161: the model answers with a short reply", "zz"), "qntmc 161: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 161: the model answers with a short reply", "AgentU"), "ruyaw 161: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 161: the model answers with a short reply", "keyboard"),
        "bssor 161: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 161: the model answers with a short reply", "AA"), "round 161: the model answers with a short reply"),
    (
        ("round 161: the recorder stores the reasoning trace", "key"),
        "bssxh 161: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 161: the recorder stores the reasoning trace", "lemon"),
        "csgbq 161: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 161: the recorder stores the reasoning trace", "a"), "round 161: the recorder stores the reasoning trace"),
    (
        ("round 161: the recorder stores the reasoning trace", "zz"),
        "qntmc 161: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 161: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 161: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 161: the recorder stores the reasoning trace", "keyboard"),
        "bssor 161: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 161: the recorder stores the reasoning trace", "AA"),
        "round 161: the recorder stores the reasoning trace",
    ),
    (("round 161: the angel watches the processor run", "key"), "bssxh 161: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 161: the angel watches the processor run", "lemon"), "csgbq 161: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 161: the angel watches the processor run", "a"), "round 161: the angel watches the processor run"),
    (("round 161: the angel watches the processor run", "zz"), "qntmc 161: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 161: the angel watches the processor run", "AgentU"), "ruyaw 161: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 161: the angel watches the processor run", "keyboard"), "bssor 161: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 161: the angel watches the processor run", "AA"), "round 161: the angel watches the processor run"),
    (("round 161: angle of the vector decides the match", "key"), "bssxh 161: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 161: angle of the vector decides the match", "lemon"), "csgbq 161: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 161: angle of the vector decides the match", "a"), "round 161: angle of the vector decides the match"),
    (("round 161: angle of the vector decides the match", "zz"), "qntmc 161: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 161: angle of the vector decides the match", "AgentU"),
        "ruyaw 161: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 161: angle of the vector decides the match", "keyboard"),
        "bssor 161: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 161: angle of the vector decides the match", "AA"), "round 161: angle of the vector decides the match"),
    (
        ("round 161: the candle burns twice as long at night", "key"),
        "bssxh 161: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 161: the candle burns twice as long at night", "lemon"),
        "csgbq 161: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 161: the candle burns twice as long at night", "a"), "round 161: the candle burns twice as long at night"),
    (
        ("round 161: the candle burns twice as long at night", "zz"),
        "qntmc 161: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 161: the candle burns twice as long at night", "AgentU"),
        "ruyaw 161: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 161: the candle burns twice as long at night", "keyboard"),
        "bssor 161: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 161: the candle burns twice as long at night", "AA"),
        "round 161: the candle burns twice as long at night",
    ),
    (("round 161: a mirror of the universe in one line", "key"), "bssxh 161: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 161: a mirror of the universe in one line", "lemon"), "csgbq 161: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 161: a mirror of the universe in one line", "a"), "round 161: a mirror of the universe in one line"),
    (("round 161: a mirror of the universe in one line", "zz"), "qntmc 161: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 161: a mirror of the universe in one line", "AgentU"), "ruyaw 161: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 161: a mirror of the universe in one line", "keyboard"),
        "bssor 161: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 161: a mirror of the universe in one line", "AA"), "round 161: a mirror of the universe in one line"),
    (("round 161: the queue drains before the storm", "key"), "bssxh 161: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 161: the queue drains before the storm", "lemon"), "csgbq 161: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 161: the queue drains before the storm", "a"), "round 161: the queue drains before the storm"),
    (("round 161: the queue drains before the storm", "zz"), "qntmc 161: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 161: the queue drains before the storm", "AgentU"), "ruyaw 161: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 161: the queue drains before the storm", "keyboard"), "bssor 161: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 161: the queue drains before the storm", "AA"), "round 161: the queue drains before the storm"),
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
