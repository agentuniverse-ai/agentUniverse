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
    (("kitten182", "key"), "umrdil182"),
    (("kitten182", "lemon"), "vmfhry182"),
    (("kitten182", "a"), "kitten182"),
    (("kitten182", "zz"), "jhssdm182"),
    (("kitten182", "AgentU"), "koxgxh182"),
    (("kitten182", "keyboard"), "umrusn182"),
    (("kitten182", "AA"), "kitten182"),
    (("sitting182", "key"), "cmrdmlq182"),
    (("sitting182", "lemon"), "dmfhvyk182"),
    (("sitting182", "a"), "sitting182"),
    (("sitting182", "zz"), "rhsshmf182"),
    (("sitting182", "AgentU"), "soxgbhg182"),
    (("sitting182", "keyboard"), "cmruwnx182"),
    (("sitting182", "AA"), "sitting182"),
    (("agent182", "key"), "kkcxx182"),
    (("agent182", "lemon"), "lkqbg182"),
    (("agent182", "a"), "agent182"),
    (("agent182", "zz"), "zfdms182"),
    (("agent182", "AgentU"), "amiam182"),
    (("agent182", "keyboard"), "kkcoh182"),
    (("agent182", "AA"), "agent182"),
    (("angle182", "key"), "krevi182"),
    (("angle182", "lemon"), "lrszr182"),
    (("angle182", "a"), "angle182"),
    (("angle182", "zz"), "zmfkd182"),
    (("angle182", "AgentU"), "atkyx182"),
    (("angle182", "keyboard"), "krems182"),
    (("angle182", "AA"), "angle182"),
    (("universe182", "key"), "ergfipci182"),
    (("universe182", "lemon"), "frujrcwq182"),
    (("universe182", "a"), "universe182"),
    (("universe182", "zz"), "tmhudqrd182"),
    (("universe182", "AgentU"), "utmixlsk182"),
    (("universe182", "keyboard"), "ergwsrjh182"),
    (("universe182", "AA"), "universe182"),
    (("memory182", "key"), "wikyvw182"),
    (("memory182", "lemon"), "xiycej182"),
    (("memory182", "a"), "memory182"),
    (("memory182", "zz"), "ldlnqx182"),
    (("memory182", "AgentU"), "mkqbks182"),
    (("memory182", "keyboard"), "wikpfy182"),
    (("memory182", "AA"), "memory182"),
    (("stream182", "key"), "cxpoek182"),
    (("stream182", "lemon"), "dxdsnx182"),
    (("stream182", "a"), "stream182"),
    (("stream182", "zz"), "rsqdzl182"),
    (("stream182", "AgentU"), "szvrtg182"),
    (("stream182", "keyboard"), "cxpfom182"),
    (("stream182", "AA"), "stream182"),
    (("context182", "key"), "msldivd182"),
    (("context182", "lemon"), "nszhrix182"),
    (("context182", "a"), "context182"),
    (("context182", "zz"), "bnmsdws182"),
    (("context182", "AgentU"), "curgxrt182"),
    (("context182", "keyboard"), "mslusxk182"),
    (("context182", "AA"), "context182"),
    (("knowledge182", "key"), "urmgpcnkc182"),
    (("knowledge182", "lemon"), "vrakyphss182"),
    (("knowledge182", "a"), "knowledge182"),
    (("knowledge182", "zz"), "jmnvkdcfd182"),
    (("knowledge182", "AgentU"), "ktsjeydmi182"),
    (("knowledge182", "keyboard"), "urmxzeujo182"),
    (("knowledge182", "AA"), "knowledge182"),
    (("vector182", "key"), "fiadsp182"),
    (("vector182", "lemon"), "giohbc182"),
    (("vector182", "a"), "vector182"),
    (("vector182", "zz"), "udbsnq182"),
    (("vector182", "AgentU"), "vkgghl182"),
    (("vector182", "keyboard"), "fiaucr182"),
    (("vector182", "AA"), "vector182"),
    (("processor182", "key"), "zvmmiqcsp182"),
    (("processor182", "lemon"), "avaqrdwaf182"),
    (("processor182", "a"), "processor182"),
    (("processor182", "zz"), "oqnbdrrnq182"),
    (("processor182", "AgentU"), "pxspxmsuv182"),
    (("processor182", "keyboard"), "zvmdssjrb182"),
    (("processor182", "AA"), "processor182"),
    (("reasoning182", "key"), "biycslsre182"),
    (("reasoning182", "lemon"), "cimgbymzu182"),
    (("reasoning182", "a"), "reasoning182"),
    (("reasoning182", "zz"), "qdzrnmhmf182"),
    (("reasoning182", "AgentU"), "rkefhhitk182"),
    (("reasoning182", "keyboard"), "biytcnzqq182"),
    (("reasoning182", "AA"), "reasoning182"),
    (("machine182", "key"), "wearmlo182"),
    (("machine182", "lemon"), "xeovvyi182"),
    (("machine182", "a"), "machine182"),
    (("machine182", "zz"), "lzbghmd182"),
    (("machine182", "AgentU"), "mggubhe182"),
    (("machine182", "keyboard"), "weaiwnv182"),
    (("machine182", "AA"), "machine182"),
    (("learning182", "key"), "viybrgxk182"),
    (("learning182", "lemon"), "wimfatrs182"),
    (("learning182", "a"), "learning182"),
    (("learning182", "zz"), "kdzqmhmf182"),
    (("learning182", "AgentU"), "lkeegcnm182"),
    (("learning182", "keyboard"), "viysbiej182"),
    (("learning182", "AA"), "learning182"),
    (("model182", "key"), "wsbop182"),
    (("model182", "lemon"), "xspsy182"),
    (("model182", "a"), "model182"),
    (("model182", "zz"), "lncdk182"),
    (("model182", "AgentU"), "muhre182"),
    (("model182", "keyboard"), "wsbfz182"),
    (("model182", "AA"), "model182"),
    (("token182", "key"), "dsior182"),
    (("token182", "lemon"), "eswsa182"),
    (("token182", "a"), "token182"),
    (("token182", "zz"), "snjdm182"),
    (("token182", "AgentU"), "tuorg182"),
    (("token182", "keyboard"), "dsifb182"),
    (("token182", "AA"), "token182"),
    (("prompt182", "key"), "zvmwtr182"),
    (("prompt182", "lemon"), "avaace182"),
    (("prompt182", "a"), "prompt182"),
    (("prompt182", "zz"), "oqnlos182"),
    (("prompt182", "AgentU"), "pxszin182"),
    (("prompt182", "keyboard"), "zvmndt182"),
    (("prompt182", "AA"), "prompt182"),
    (("session182", "key"), "ciqcmmx182"),
    (("session182", "lemon"), "diegvzr182"),
    (("session182", "a"), "session182"),
    (("session182", "zz"), "rdrrhnm182"),
    (("session182", "AgentU"), "skwfbin182"),
    (("session182", "keyboard"), "ciqtwoe182"),
    (("session182", "AA"), "session182"),
    (("library182", "key"), "vmzbepi182"),
    (("library182", "lemon"), "wmnfncc182"),
    (("library182", "a"), "library182"),
    (("library182", "zz"), "khaqzqx182"),
    (("library182", "AgentU"), "lofetly182"),
    (("library182", "keyboard"), "vmzsorp182"),
    (("library182", "AA"), "library182"),
    (("service182", "key"), "cipfmao182"),
    (("service182", "lemon"), "didjvni182"),
    (("service182", "a"), "service182"),
    (("service182", "zz"), "rdquhbd182"),
    (("service182", "AgentU"), "skvibwe182"),
    (("service182", "keyboard"), "cipwwcv182"),
    (("service182", "AA"), "service182"),
    (("gateway182", "key"), "qeroayi182"),
    (("gateway182", "lemon"), "refsjlc182"),
    (("gateway182", "a"), "gateway182"),
    (("gateway182", "zz"), "fzsdvzx182"),
    (("gateway182", "AgentU"), "ggxrpuy182"),
    (("gateway182", "keyboard"), "qerfkap182"),
    (("gateway182", "AA"), "gateway182"),
    (("storage182", "key"), "cxmbeeo182"),
    (("storage182", "lemon"), "dxafnri182"),
    (("storage182", "a"), "storage182"),
    (("storage182", "zz"), "rsnqzfd182"),
    (("storage182", "AgentU"), "szsetae182"),
    (("storage182", "keyboard"), "cxmsogv182"),
    (("storage182", "AA"), "storage182"),
    (("network182", "key"), "xirgspu182"),
    (("network182", "lemon"), "yifkbco182"),
    (("network182", "a"), "network182"),
    (("network182", "zz"), "mdsvnqj182"),
    (("network182", "AgentU"), "nkxjhlk182"),
    (("network182", "keyboard"), "xirxcrb182"),
    (("network182", "AA"), "network182"),
    (("latency182", "key"), "verorai182"),
    (("latency182", "lemon"), "wefsanc182"),
    (("latency182", "a"), "latency182"),
    (("latency182", "zz"), "kzsdmbx182"),
    (("latency182", "AgentU"), "lgxrgwy182"),
    (("latency182", "keyboard"), "verfbcp182"),
    (("latency182", "AA"), "latency182"),
    (("buffer182", "key"), "lydpip182"),
    (("buffer182", "lemon"), "myrtrc182"),
    (("buffer182", "a"), "buffer182"),
    (("buffer182", "zz"), "ateedq182"),
    (("buffer182", "AgentU"), "bajsxl182"),
    (("buffer182", "keyboard"), "lydgsr182"),
    (("buffer182", "AA"), "buffer182"),
    (("queue182", "key"), "aycei182"),
    (("queue182", "lemon"), "byqir182"),
    (("queue182", "a"), "queue182"),
    (("queue182", "zz"), "ptdtd182"),
    (("queue182", "AgentU"), "qaihx182"),
    (("queue182", "keyboard"), "aycvs182"),
    (("queue182", "AA"), "queue182"),
    (("worker182", "key"), "gspuip182"),
    (("worker182", "lemon"), "hsdyrc182"),
    (("worker182", "a"), "worker182"),
    (("worker182", "zz"), "vnqjdq182"),
    (("worker182", "AgentU"), "wuvxxl182"),
    (("worker182", "keyboard"), "gsplsr182"),
    (("worker182", "AA"), "worker182"),
    (("kernel182", "key"), "uipxij182"),
    (("kernel182", "lemon"), "vidbrw182"),
    (("kernel182", "a"), "kernel182"),
    (("kernel182", "zz"), "jdqmdk182"),
    (("kernel182", "AgentU"), "kkvaxf182"),
    (("kernel182", "keyboard"), "uiposl182"),
    (("kernel182", "AA"), "kernel182"),
    (("signal182", "key"), "cmexej182"),
    (("signal182", "lemon"), "dmsbnw182"),
    (("signal182", "a"), "signal182"),
    (("signal182", "zz"), "rhfmzk182"),
    (("signal182", "AgentU"), "sokatf182"),
    (("signal182", "keyboard"), "cmeool182"),
    (("signal182", "AA"), "signal182"),
    (("packet182", "key"), "zeauir182"),
    (("packet182", "lemon"), "aeoyre182"),
    (("packet182", "a"), "packet182"),
    (("packet182", "zz"), "ozbjds182"),
    (("packet182", "AgentU"), "pggxxn182"),
    (("packet182", "keyboard"), "zealst182"),
    (("packet182", "AA"), "packet182"),
    (("router182", "key"), "bssdip182"),
    (("router182", "lemon"), "csghrc182"),
    (("router182", "a"), "router182"),
    (("router182", "zz"), "qntsdq182"),
    (("router182", "AgentU"), "ruygxl182"),
    (("router182", "keyboard"), "bssusr182"),
    (("router182", "AA"), "router182"),
    (("cluster182", "key"), "mpscxcb182"),
    (("cluster182", "lemon"), "npgggpv182"),
    (("cluster182", "a"), "cluster182"),
    (("cluster182", "zz"), "bktrsdq182"),
    (("cluster182", "AgentU"), "cryfmyr182"),
    (("cluster182", "keyboard"), "mpsthei182"),
    (("cluster182", "AA"), "cluster182"),
    (("mirror182", "key"), "wmpbsp182"),
    (("mirror182", "lemon"), "xmdfbc182"),
    (("mirror182", "a"), "mirror182"),
    (("mirror182", "zz"), "lhqqnq182"),
    (("mirror182", "AgentU"), "movehl182"),
    (("mirror182", "keyboard"), "wmpscr182"),
    (("mirror182", "AA"), "mirror182"),
    (("filter182", "key"), "pmjdip182"),
    (("filter182", "lemon"), "qmxhrc182"),
    (("filter182", "a"), "filter182"),
    (("filter182", "zz"), "ehksdq182"),
    (("filter182", "AgentU"), "fopgxl182"),
    (("filter182", "keyboard"), "pmjusr182"),
    (("filter182", "AA"), "filter182"),
    (("ranking182", "key"), "belumlq182"),
    (("ranking182", "lemon"), "cezyvyk182"),
    (("ranking182", "a"), "ranking182"),
    (("ranking182", "zz"), "qzmjhmf182"),
    (("ranking182", "AgentU"), "rgrxbhg182"),
    (("ranking182", "keyboard"), "bellwnx182"),
    (("ranking182", "AA"), "ranking182"),
    (("encoding182", "key"), "orayhgxk182"),
    (("encoding182", "lemon"), "procqtrs182"),
    (("encoding182", "a"), "encoding182"),
    (("encoding182", "zz"), "dmbnchmf182"),
    (("encoding182", "AgentU"), "etgbwcnm182"),
    (("encoding182", "keyboard"), "orapriej182"),
    (("encoding182", "AA"), "encoding182"),
    (("mapping182", "key"), "wenzmlq182"),
    (("mapping182", "lemon"), "xebdvyk182"),
    (("mapping182", "a"), "mapping182"),
    (("mapping182", "zz"), "lzoohmf182"),
    (("mapping182", "AgentU"), "mgtcbhg182"),
    (("mapping182", "keyboard"), "wenqwnx182"),
    (("mapping182", "AA"), "mapping182"),
    (("record182", "key"), "biayvb182"),
    (("record182", "lemon"), "cioceo182"),
    (("record182", "a"), "record182"),
    (("record182", "zz"), "qdbnqc182"),
    (("record182", "AgentU"), "rkgbkx182"),
    (("record182", "keyboard"), "biapfd182"),
    (("record182", "AA"), "record182"),
    (("candle182", "key"), "melnpc182"),
    (("candle182", "lemon"), "nezryp182"),
    (("candle182", "a"), "candle182"),
    (("candle182", "zz"), "bzmckd182"),
    (("candle182", "AgentU"), "cgrqey182"),
    (("candle182", "keyboard"), "meleze182"),
    (("candle182", "AA"), "candle182"),
    (("thread182", "key"), "dlpoeb182"),
    (("thread182", "lemon"), "eldsno182"),
    (("thread182", "a"), "thread182"),
    (("thread182", "zz"), "sgqdzc182"),
    (("thread182", "AgentU"), "tnvrtx182"),
    (("thread182", "keyboard"), "dlpfod182"),
    (("thread182", "AA"), "thread182"),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 182: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 182: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "a"),
        "round 182: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 182: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 182: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 182: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", "AA"),
        "round 182: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "key"),
        "bssxh 182: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 182: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "a"),
        "round 182: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 182: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 182: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 182: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", "AA"),
        "round 182: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 182: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 182: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "a"),
        "round 182: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 182: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 182: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 182: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", "AA"),
        "round 182: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 182: the processor reads the record then stops", "key"),
        "bssxh 182: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 182: the processor reads the record then stops", "lemon"),
        "csgbq 182: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 182: the processor reads the record then stops", "a"),
        "round 182: the processor reads the record then stops",
    ),
    (
        ("round 182: the processor reads the record then stops", "zz"),
        "qntmc 182: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 182: the processor reads the record then stops", "AgentU"),
        "ruyaw 182: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 182: the processor reads the record then stops", "keyboard"),
        "bssor 182: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 182: the processor reads the record then stops", "AA"),
        "round 182: the processor reads the record then stops",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "key"),
        "bssxh 182: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "lemon"),
        "csgbq 182: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "a"),
        "round 182: a worker pulls the next task from the queue",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "zz"),
        "qntmc 182: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 182: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "keyboard"),
        "bssor 182: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 182: a worker pulls the next task from the queue", "AA"),
        "round 182: a worker pulls the next task from the queue",
    ),
    (
        ("round 182: signals travel through the network layer", "key"),
        "bssxh 182: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 182: signals travel through the network layer", "lemon"),
        "csgbq 182: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 182: signals travel through the network layer", "a"),
        "round 182: signals travel through the network layer",
    ),
    (
        ("round 182: signals travel through the network layer", "zz"),
        "qntmc 182: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 182: signals travel through the network layer", "AgentU"),
        "ruyaw 182: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 182: signals travel through the network layer", "keyboard"),
        "bssor 182: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 182: signals travel through the network layer", "AA"),
        "round 182: signals travel through the network layer",
    ),
    (
        ("round 182: the gateway routes each request by policy", "key"),
        "bssxh 182: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 182: the gateway routes each request by policy", "lemon"),
        "csgbq 182: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 182: the gateway routes each request by policy", "a"),
        "round 182: the gateway routes each request by policy",
    ),
    (
        ("round 182: the gateway routes each request by policy", "zz"),
        "qntmc 182: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 182: the gateway routes each request by policy", "AgentU"),
        "ruyaw 182: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 182: the gateway routes each request by policy", "keyboard"),
        "bssor 182: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 182: the gateway routes each request by policy", "AA"),
        "round 182: the gateway routes each request by policy",
    ),
    (("round 182: memory grows until the buffer is full", "key"), "bssxh 182: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 182: memory grows until the buffer is full", "lemon"), "csgbq 182: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 182: memory grows until the buffer is full", "a"), "round 182: memory grows until the buffer is full"),
    (("round 182: memory grows until the buffer is full", "zz"), "qntmc 182: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 182: memory grows until the buffer is full", "AgentU"),
        "ruyaw 182: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 182: memory grows until the buffer is full", "keyboard"),
        "bssor 182: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 182: memory grows until the buffer is full", "AA"), "round 182: memory grows until the buffer is full"),
    (("round 182: the cluster mirrors every packet twice", "key"), "bssxh 182: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 182: the cluster mirrors every packet twice", "lemon"),
        "csgbq 182: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 182: the cluster mirrors every packet twice", "a"), "round 182: the cluster mirrors every packet twice"),
    (("round 182: the cluster mirrors every packet twice", "zz"), "qntmc 182: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 182: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 182: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 182: the cluster mirrors every packet twice", "keyboard"),
        "bssor 182: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 182: the cluster mirrors every packet twice", "AA"), "round 182: the cluster mirrors every packet twice"),
    (
        ("round 182: ranking uses tokens learned from the corpus", "key"),
        "bssxh 182: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 182: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", "a"),
        "round 182: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 182: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 182: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 182: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", "AA"),
        "round 182: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 182: a long session ends when the candle dies", "key"),
        "bssxh 182: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 182: a long session ends when the candle dies", "lemon"),
        "csgbq 182: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 182: a long session ends when the candle dies", "a"),
        "round 182: a long session ends when the candle dies",
    ),
    (
        ("round 182: a long session ends when the candle dies", "zz"),
        "qntmc 182: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 182: a long session ends when the candle dies", "AgentU"),
        "ruyaw 182: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 182: a long session ends when the candle dies", "keyboard"),
        "bssor 182: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 182: a long session ends when the candle dies", "AA"),
        "round 182: a long session ends when the candle dies",
    ),
    (("round 182: encode the prompt then map the result", "key"), "bssxh 182: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 182: encode the prompt then map the result", "lemon"), "csgbq 182: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 182: encode the prompt then map the result", "a"), "round 182: encode the prompt then map the result"),
    (("round 182: encode the prompt then map the result", "zz"), "qntmc 182: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 182: encode the prompt then map the result", "AgentU"),
        "ruyaw 182: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 182: encode the prompt then map the result", "keyboard"),
        "bssor 182: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 182: encode the prompt then map the result", "AA"), "round 182: encode the prompt then map the result"),
    (("round 182: the kernel wakes the worker at dawn", "key"), "bssxh 182: rri iovlop ukocc xfo ambocb er neux"),
    (("round 182: the kernel wakes the worker at dawn", "lemon"), "csgbq 182: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 182: the kernel wakes the worker at dawn", "a"), "round 182: the kernel wakes the worker at dawn"),
    (("round 182: the kernel wakes the worker at dawn", "zz"), "qntmc 182: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 182: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 182: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 182: the kernel wakes the worker at dawn", "keyboard"), "bssor 182: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 182: the kernel wakes the worker at dawn", "AA"), "round 182: the kernel wakes the worker at dawn"),
    (("round 182: service latency drops after the patch", "key"), "bssxh 182: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 182: service latency drops after the patch", "lemon"), "csgbq 182: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 182: service latency drops after the patch", "a"), "round 182: service latency drops after the patch"),
    (("round 182: service latency drops after the patch", "zz"), "qntmc 182: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 182: service latency drops after the patch", "AgentU"),
        "ruyaw 182: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 182: service latency drops after the patch", "keyboard"),
        "bssor 182: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 182: service latency drops after the patch", "AA"), "round 182: service latency drops after the patch"),
    (
        ("round 182: the library caches every vector it sees", "key"),
        "bssxh 182: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 182: the library caches every vector it sees", "lemon"),
        "csgbq 182: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 182: the library caches every vector it sees", "a"), "round 182: the library caches every vector it sees"),
    (
        ("round 182: the library caches every vector it sees", "zz"),
        "qntmc 182: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 182: the library caches every vector it sees", "AgentU"),
        "ruyaw 182: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 182: the library caches every vector it sees", "keyboard"),
        "bssor 182: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 182: the library caches every vector it sees", "AA"),
        "round 182: the library caches every vector it sees",
    ),
    (("round 182: agents argue then the debate resolves", "key"), "bssxh 182: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 182: agents argue then the debate resolves", "lemon"), "csgbq 182: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 182: agents argue then the debate resolves", "a"), "round 182: agents argue then the debate resolves"),
    (("round 182: agents argue then the debate resolves", "zz"), "qntmc 182: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 182: agents argue then the debate resolves", "AgentU"),
        "ruyaw 182: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 182: agents argue then the debate resolves", "keyboard"),
        "bssor 182: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 182: agents argue then the debate resolves", "AA"), "round 182: agents argue then the debate resolves"),
    (("round 182: the filter keeps only strong matches", "key"), "bssxh 182: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 182: the filter keeps only strong matches", "lemon"), "csgbq 182: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 182: the filter keeps only strong matches", "a"), "round 182: the filter keeps only strong matches"),
    (("round 182: the filter keeps only strong matches", "zz"), "qntmc 182: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 182: the filter keeps only strong matches", "AgentU"), "ruyaw 182: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 182: the filter keeps only strong matches", "keyboard"),
        "bssor 182: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 182: the filter keeps only strong matches", "AA"), "round 182: the filter keeps only strong matches"),
    (("round 182: the model answers with a short reply", "key"), "bssxh 182: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 182: the model answers with a short reply", "lemon"), "csgbq 182: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 182: the model answers with a short reply", "a"), "round 182: the model answers with a short reply"),
    (("round 182: the model answers with a short reply", "zz"), "qntmc 182: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 182: the model answers with a short reply", "AgentU"), "ruyaw 182: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 182: the model answers with a short reply", "keyboard"),
        "bssor 182: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 182: the model answers with a short reply", "AA"), "round 182: the model answers with a short reply"),
    (
        ("round 182: the recorder stores the reasoning trace", "key"),
        "bssxh 182: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 182: the recorder stores the reasoning trace", "lemon"),
        "csgbq 182: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 182: the recorder stores the reasoning trace", "a"), "round 182: the recorder stores the reasoning trace"),
    (
        ("round 182: the recorder stores the reasoning trace", "zz"),
        "qntmc 182: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 182: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 182: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 182: the recorder stores the reasoning trace", "keyboard"),
        "bssor 182: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 182: the recorder stores the reasoning trace", "AA"),
        "round 182: the recorder stores the reasoning trace",
    ),
    (("round 182: the angel watches the processor run", "key"), "bssxh 182: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 182: the angel watches the processor run", "lemon"), "csgbq 182: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 182: the angel watches the processor run", "a"), "round 182: the angel watches the processor run"),
    (("round 182: the angel watches the processor run", "zz"), "qntmc 182: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 182: the angel watches the processor run", "AgentU"), "ruyaw 182: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 182: the angel watches the processor run", "keyboard"), "bssor 182: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 182: the angel watches the processor run", "AA"), "round 182: the angel watches the processor run"),
    (("round 182: angle of the vector decides the match", "key"), "bssxh 182: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 182: angle of the vector decides the match", "lemon"), "csgbq 182: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 182: angle of the vector decides the match", "a"), "round 182: angle of the vector decides the match"),
    (("round 182: angle of the vector decides the match", "zz"), "qntmc 182: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 182: angle of the vector decides the match", "AgentU"),
        "ruyaw 182: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 182: angle of the vector decides the match", "keyboard"),
        "bssor 182: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 182: angle of the vector decides the match", "AA"), "round 182: angle of the vector decides the match"),
    (
        ("round 182: the candle burns twice as long at night", "key"),
        "bssxh 182: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 182: the candle burns twice as long at night", "lemon"),
        "csgbq 182: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 182: the candle burns twice as long at night", "a"), "round 182: the candle burns twice as long at night"),
    (
        ("round 182: the candle burns twice as long at night", "zz"),
        "qntmc 182: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 182: the candle burns twice as long at night", "AgentU"),
        "ruyaw 182: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 182: the candle burns twice as long at night", "keyboard"),
        "bssor 182: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 182: the candle burns twice as long at night", "AA"),
        "round 182: the candle burns twice as long at night",
    ),
    (("round 182: a mirror of the universe in one line", "key"), "bssxh 182: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 182: a mirror of the universe in one line", "lemon"), "csgbq 182: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 182: a mirror of the universe in one line", "a"), "round 182: a mirror of the universe in one line"),
    (("round 182: a mirror of the universe in one line", "zz"), "qntmc 182: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 182: a mirror of the universe in one line", "AgentU"), "ruyaw 182: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 182: a mirror of the universe in one line", "keyboard"),
        "bssor 182: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 182: a mirror of the universe in one line", "AA"), "round 182: a mirror of the universe in one line"),
    (("round 182: the queue drains before the storm", "key"), "bssxh 182: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 182: the queue drains before the storm", "lemon"), "csgbq 182: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 182: the queue drains before the storm", "a"), "round 182: the queue drains before the storm"),
    (("round 182: the queue drains before the storm", "zz"), "qntmc 182: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 182: the queue drains before the storm", "AgentU"), "ruyaw 182: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 182: the queue drains before the storm", "keyboard"), "bssor 182: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 182: the queue drains before the storm", "AA"), "round 182: the queue drains before the storm"),
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
