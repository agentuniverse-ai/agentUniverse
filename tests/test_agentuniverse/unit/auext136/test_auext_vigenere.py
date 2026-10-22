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
    (("kitten136", "key"), "umrdil136"),
    (("kitten136", "lemon"), "vmfhry136"),
    (("kitten136", "a"), "kitten136"),
    (("kitten136", "zz"), "jhssdm136"),
    (("kitten136", "AgentU"), "koxgxh136"),
    (("kitten136", "keyboard"), "umrusn136"),
    (("kitten136", "AA"), "kitten136"),
    (("sitting136", "key"), "cmrdmlq136"),
    (("sitting136", "lemon"), "dmfhvyk136"),
    (("sitting136", "a"), "sitting136"),
    (("sitting136", "zz"), "rhsshmf136"),
    (("sitting136", "AgentU"), "soxgbhg136"),
    (("sitting136", "keyboard"), "cmruwnx136"),
    (("sitting136", "AA"), "sitting136"),
    (("agent136", "key"), "kkcxx136"),
    (("agent136", "lemon"), "lkqbg136"),
    (("agent136", "a"), "agent136"),
    (("agent136", "zz"), "zfdms136"),
    (("agent136", "AgentU"), "amiam136"),
    (("agent136", "keyboard"), "kkcoh136"),
    (("agent136", "AA"), "agent136"),
    (("angle136", "key"), "krevi136"),
    (("angle136", "lemon"), "lrszr136"),
    (("angle136", "a"), "angle136"),
    (("angle136", "zz"), "zmfkd136"),
    (("angle136", "AgentU"), "atkyx136"),
    (("angle136", "keyboard"), "krems136"),
    (("angle136", "AA"), "angle136"),
    (("universe136", "key"), "ergfipci136"),
    (("universe136", "lemon"), "frujrcwq136"),
    (("universe136", "a"), "universe136"),
    (("universe136", "zz"), "tmhudqrd136"),
    (("universe136", "AgentU"), "utmixlsk136"),
    (("universe136", "keyboard"), "ergwsrjh136"),
    (("universe136", "AA"), "universe136"),
    (("memory136", "key"), "wikyvw136"),
    (("memory136", "lemon"), "xiycej136"),
    (("memory136", "a"), "memory136"),
    (("memory136", "zz"), "ldlnqx136"),
    (("memory136", "AgentU"), "mkqbks136"),
    (("memory136", "keyboard"), "wikpfy136"),
    (("memory136", "AA"), "memory136"),
    (("stream136", "key"), "cxpoek136"),
    (("stream136", "lemon"), "dxdsnx136"),
    (("stream136", "a"), "stream136"),
    (("stream136", "zz"), "rsqdzl136"),
    (("stream136", "AgentU"), "szvrtg136"),
    (("stream136", "keyboard"), "cxpfom136"),
    (("stream136", "AA"), "stream136"),
    (("context136", "key"), "msldivd136"),
    (("context136", "lemon"), "nszhrix136"),
    (("context136", "a"), "context136"),
    (("context136", "zz"), "bnmsdws136"),
    (("context136", "AgentU"), "curgxrt136"),
    (("context136", "keyboard"), "mslusxk136"),
    (("context136", "AA"), "context136"),
    (("knowledge136", "key"), "urmgpcnkc136"),
    (("knowledge136", "lemon"), "vrakyphss136"),
    (("knowledge136", "a"), "knowledge136"),
    (("knowledge136", "zz"), "jmnvkdcfd136"),
    (("knowledge136", "AgentU"), "ktsjeydmi136"),
    (("knowledge136", "keyboard"), "urmxzeujo136"),
    (("knowledge136", "AA"), "knowledge136"),
    (("vector136", "key"), "fiadsp136"),
    (("vector136", "lemon"), "giohbc136"),
    (("vector136", "a"), "vector136"),
    (("vector136", "zz"), "udbsnq136"),
    (("vector136", "AgentU"), "vkgghl136"),
    (("vector136", "keyboard"), "fiaucr136"),
    (("vector136", "AA"), "vector136"),
    (("processor136", "key"), "zvmmiqcsp136"),
    (("processor136", "lemon"), "avaqrdwaf136"),
    (("processor136", "a"), "processor136"),
    (("processor136", "zz"), "oqnbdrrnq136"),
    (("processor136", "AgentU"), "pxspxmsuv136"),
    (("processor136", "keyboard"), "zvmdssjrb136"),
    (("processor136", "AA"), "processor136"),
    (("reasoning136", "key"), "biycslsre136"),
    (("reasoning136", "lemon"), "cimgbymzu136"),
    (("reasoning136", "a"), "reasoning136"),
    (("reasoning136", "zz"), "qdzrnmhmf136"),
    (("reasoning136", "AgentU"), "rkefhhitk136"),
    (("reasoning136", "keyboard"), "biytcnzqq136"),
    (("reasoning136", "AA"), "reasoning136"),
    (("machine136", "key"), "wearmlo136"),
    (("machine136", "lemon"), "xeovvyi136"),
    (("machine136", "a"), "machine136"),
    (("machine136", "zz"), "lzbghmd136"),
    (("machine136", "AgentU"), "mggubhe136"),
    (("machine136", "keyboard"), "weaiwnv136"),
    (("machine136", "AA"), "machine136"),
    (("learning136", "key"), "viybrgxk136"),
    (("learning136", "lemon"), "wimfatrs136"),
    (("learning136", "a"), "learning136"),
    (("learning136", "zz"), "kdzqmhmf136"),
    (("learning136", "AgentU"), "lkeegcnm136"),
    (("learning136", "keyboard"), "viysbiej136"),
    (("learning136", "AA"), "learning136"),
    (("model136", "key"), "wsbop136"),
    (("model136", "lemon"), "xspsy136"),
    (("model136", "a"), "model136"),
    (("model136", "zz"), "lncdk136"),
    (("model136", "AgentU"), "muhre136"),
    (("model136", "keyboard"), "wsbfz136"),
    (("model136", "AA"), "model136"),
    (("token136", "key"), "dsior136"),
    (("token136", "lemon"), "eswsa136"),
    (("token136", "a"), "token136"),
    (("token136", "zz"), "snjdm136"),
    (("token136", "AgentU"), "tuorg136"),
    (("token136", "keyboard"), "dsifb136"),
    (("token136", "AA"), "token136"),
    (("prompt136", "key"), "zvmwtr136"),
    (("prompt136", "lemon"), "avaace136"),
    (("prompt136", "a"), "prompt136"),
    (("prompt136", "zz"), "oqnlos136"),
    (("prompt136", "AgentU"), "pxszin136"),
    (("prompt136", "keyboard"), "zvmndt136"),
    (("prompt136", "AA"), "prompt136"),
    (("session136", "key"), "ciqcmmx136"),
    (("session136", "lemon"), "diegvzr136"),
    (("session136", "a"), "session136"),
    (("session136", "zz"), "rdrrhnm136"),
    (("session136", "AgentU"), "skwfbin136"),
    (("session136", "keyboard"), "ciqtwoe136"),
    (("session136", "AA"), "session136"),
    (("library136", "key"), "vmzbepi136"),
    (("library136", "lemon"), "wmnfncc136"),
    (("library136", "a"), "library136"),
    (("library136", "zz"), "khaqzqx136"),
    (("library136", "AgentU"), "lofetly136"),
    (("library136", "keyboard"), "vmzsorp136"),
    (("library136", "AA"), "library136"),
    (("service136", "key"), "cipfmao136"),
    (("service136", "lemon"), "didjvni136"),
    (("service136", "a"), "service136"),
    (("service136", "zz"), "rdquhbd136"),
    (("service136", "AgentU"), "skvibwe136"),
    (("service136", "keyboard"), "cipwwcv136"),
    (("service136", "AA"), "service136"),
    (("gateway136", "key"), "qeroayi136"),
    (("gateway136", "lemon"), "refsjlc136"),
    (("gateway136", "a"), "gateway136"),
    (("gateway136", "zz"), "fzsdvzx136"),
    (("gateway136", "AgentU"), "ggxrpuy136"),
    (("gateway136", "keyboard"), "qerfkap136"),
    (("gateway136", "AA"), "gateway136"),
    (("storage136", "key"), "cxmbeeo136"),
    (("storage136", "lemon"), "dxafnri136"),
    (("storage136", "a"), "storage136"),
    (("storage136", "zz"), "rsnqzfd136"),
    (("storage136", "AgentU"), "szsetae136"),
    (("storage136", "keyboard"), "cxmsogv136"),
    (("storage136", "AA"), "storage136"),
    (("network136", "key"), "xirgspu136"),
    (("network136", "lemon"), "yifkbco136"),
    (("network136", "a"), "network136"),
    (("network136", "zz"), "mdsvnqj136"),
    (("network136", "AgentU"), "nkxjhlk136"),
    (("network136", "keyboard"), "xirxcrb136"),
    (("network136", "AA"), "network136"),
    (("latency136", "key"), "verorai136"),
    (("latency136", "lemon"), "wefsanc136"),
    (("latency136", "a"), "latency136"),
    (("latency136", "zz"), "kzsdmbx136"),
    (("latency136", "AgentU"), "lgxrgwy136"),
    (("latency136", "keyboard"), "verfbcp136"),
    (("latency136", "AA"), "latency136"),
    (("buffer136", "key"), "lydpip136"),
    (("buffer136", "lemon"), "myrtrc136"),
    (("buffer136", "a"), "buffer136"),
    (("buffer136", "zz"), "ateedq136"),
    (("buffer136", "AgentU"), "bajsxl136"),
    (("buffer136", "keyboard"), "lydgsr136"),
    (("buffer136", "AA"), "buffer136"),
    (("queue136", "key"), "aycei136"),
    (("queue136", "lemon"), "byqir136"),
    (("queue136", "a"), "queue136"),
    (("queue136", "zz"), "ptdtd136"),
    (("queue136", "AgentU"), "qaihx136"),
    (("queue136", "keyboard"), "aycvs136"),
    (("queue136", "AA"), "queue136"),
    (("worker136", "key"), "gspuip136"),
    (("worker136", "lemon"), "hsdyrc136"),
    (("worker136", "a"), "worker136"),
    (("worker136", "zz"), "vnqjdq136"),
    (("worker136", "AgentU"), "wuvxxl136"),
    (("worker136", "keyboard"), "gsplsr136"),
    (("worker136", "AA"), "worker136"),
    (("kernel136", "key"), "uipxij136"),
    (("kernel136", "lemon"), "vidbrw136"),
    (("kernel136", "a"), "kernel136"),
    (("kernel136", "zz"), "jdqmdk136"),
    (("kernel136", "AgentU"), "kkvaxf136"),
    (("kernel136", "keyboard"), "uiposl136"),
    (("kernel136", "AA"), "kernel136"),
    (("signal136", "key"), "cmexej136"),
    (("signal136", "lemon"), "dmsbnw136"),
    (("signal136", "a"), "signal136"),
    (("signal136", "zz"), "rhfmzk136"),
    (("signal136", "AgentU"), "sokatf136"),
    (("signal136", "keyboard"), "cmeool136"),
    (("signal136", "AA"), "signal136"),
    (("packet136", "key"), "zeauir136"),
    (("packet136", "lemon"), "aeoyre136"),
    (("packet136", "a"), "packet136"),
    (("packet136", "zz"), "ozbjds136"),
    (("packet136", "AgentU"), "pggxxn136"),
    (("packet136", "keyboard"), "zealst136"),
    (("packet136", "AA"), "packet136"),
    (("router136", "key"), "bssdip136"),
    (("router136", "lemon"), "csghrc136"),
    (("router136", "a"), "router136"),
    (("router136", "zz"), "qntsdq136"),
    (("router136", "AgentU"), "ruygxl136"),
    (("router136", "keyboard"), "bssusr136"),
    (("router136", "AA"), "router136"),
    (("cluster136", "key"), "mpscxcb136"),
    (("cluster136", "lemon"), "npgggpv136"),
    (("cluster136", "a"), "cluster136"),
    (("cluster136", "zz"), "bktrsdq136"),
    (("cluster136", "AgentU"), "cryfmyr136"),
    (("cluster136", "keyboard"), "mpsthei136"),
    (("cluster136", "AA"), "cluster136"),
    (("mirror136", "key"), "wmpbsp136"),
    (("mirror136", "lemon"), "xmdfbc136"),
    (("mirror136", "a"), "mirror136"),
    (("mirror136", "zz"), "lhqqnq136"),
    (("mirror136", "AgentU"), "movehl136"),
    (("mirror136", "keyboard"), "wmpscr136"),
    (("mirror136", "AA"), "mirror136"),
    (("filter136", "key"), "pmjdip136"),
    (("filter136", "lemon"), "qmxhrc136"),
    (("filter136", "a"), "filter136"),
    (("filter136", "zz"), "ehksdq136"),
    (("filter136", "AgentU"), "fopgxl136"),
    (("filter136", "keyboard"), "pmjusr136"),
    (("filter136", "AA"), "filter136"),
    (("ranking136", "key"), "belumlq136"),
    (("ranking136", "lemon"), "cezyvyk136"),
    (("ranking136", "a"), "ranking136"),
    (("ranking136", "zz"), "qzmjhmf136"),
    (("ranking136", "AgentU"), "rgrxbhg136"),
    (("ranking136", "keyboard"), "bellwnx136"),
    (("ranking136", "AA"), "ranking136"),
    (("encoding136", "key"), "orayhgxk136"),
    (("encoding136", "lemon"), "procqtrs136"),
    (("encoding136", "a"), "encoding136"),
    (("encoding136", "zz"), "dmbnchmf136"),
    (("encoding136", "AgentU"), "etgbwcnm136"),
    (("encoding136", "keyboard"), "orapriej136"),
    (("encoding136", "AA"), "encoding136"),
    (("mapping136", "key"), "wenzmlq136"),
    (("mapping136", "lemon"), "xebdvyk136"),
    (("mapping136", "a"), "mapping136"),
    (("mapping136", "zz"), "lzoohmf136"),
    (("mapping136", "AgentU"), "mgtcbhg136"),
    (("mapping136", "keyboard"), "wenqwnx136"),
    (("mapping136", "AA"), "mapping136"),
    (("record136", "key"), "biayvb136"),
    (("record136", "lemon"), "cioceo136"),
    (("record136", "a"), "record136"),
    (("record136", "zz"), "qdbnqc136"),
    (("record136", "AgentU"), "rkgbkx136"),
    (("record136", "keyboard"), "biapfd136"),
    (("record136", "AA"), "record136"),
    (("candle136", "key"), "melnpc136"),
    (("candle136", "lemon"), "nezryp136"),
    (("candle136", "a"), "candle136"),
    (("candle136", "zz"), "bzmckd136"),
    (("candle136", "AgentU"), "cgrqey136"),
    (("candle136", "keyboard"), "meleze136"),
    (("candle136", "AA"), "candle136"),
    (("thread136", "key"), "dlpoeb136"),
    (("thread136", "lemon"), "eldsno136"),
    (("thread136", "a"), "thread136"),
    (("thread136", "zz"), "sgqdzc136"),
    (("thread136", "AgentU"), "tnvrtx136"),
    (("thread136", "keyboard"), "dlpfod136"),
    (("thread136", "AA"), "thread136"),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 136: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 136: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "a"),
        "round 136: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 136: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 136: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 136: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", "AA"),
        "round 136: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "key"),
        "bssxh 136: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 136: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "a"),
        "round 136: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 136: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 136: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 136: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", "AA"),
        "round 136: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 136: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 136: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "a"),
        "round 136: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 136: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 136: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 136: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", "AA"),
        "round 136: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 136: the processor reads the record then stops", "key"),
        "bssxh 136: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 136: the processor reads the record then stops", "lemon"),
        "csgbq 136: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 136: the processor reads the record then stops", "a"),
        "round 136: the processor reads the record then stops",
    ),
    (
        ("round 136: the processor reads the record then stops", "zz"),
        "qntmc 136: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 136: the processor reads the record then stops", "AgentU"),
        "ruyaw 136: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 136: the processor reads the record then stops", "keyboard"),
        "bssor 136: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 136: the processor reads the record then stops", "AA"),
        "round 136: the processor reads the record then stops",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "key"),
        "bssxh 136: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "lemon"),
        "csgbq 136: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "a"),
        "round 136: a worker pulls the next task from the queue",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "zz"),
        "qntmc 136: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 136: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "keyboard"),
        "bssor 136: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 136: a worker pulls the next task from the queue", "AA"),
        "round 136: a worker pulls the next task from the queue",
    ),
    (
        ("round 136: signals travel through the network layer", "key"),
        "bssxh 136: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 136: signals travel through the network layer", "lemon"),
        "csgbq 136: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 136: signals travel through the network layer", "a"),
        "round 136: signals travel through the network layer",
    ),
    (
        ("round 136: signals travel through the network layer", "zz"),
        "qntmc 136: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 136: signals travel through the network layer", "AgentU"),
        "ruyaw 136: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 136: signals travel through the network layer", "keyboard"),
        "bssor 136: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 136: signals travel through the network layer", "AA"),
        "round 136: signals travel through the network layer",
    ),
    (
        ("round 136: the gateway routes each request by policy", "key"),
        "bssxh 136: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 136: the gateway routes each request by policy", "lemon"),
        "csgbq 136: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 136: the gateway routes each request by policy", "a"),
        "round 136: the gateway routes each request by policy",
    ),
    (
        ("round 136: the gateway routes each request by policy", "zz"),
        "qntmc 136: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 136: the gateway routes each request by policy", "AgentU"),
        "ruyaw 136: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 136: the gateway routes each request by policy", "keyboard"),
        "bssor 136: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 136: the gateway routes each request by policy", "AA"),
        "round 136: the gateway routes each request by policy",
    ),
    (("round 136: memory grows until the buffer is full", "key"), "bssxh 136: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 136: memory grows until the buffer is full", "lemon"), "csgbq 136: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 136: memory grows until the buffer is full", "a"), "round 136: memory grows until the buffer is full"),
    (("round 136: memory grows until the buffer is full", "zz"), "qntmc 136: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 136: memory grows until the buffer is full", "AgentU"),
        "ruyaw 136: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 136: memory grows until the buffer is full", "keyboard"),
        "bssor 136: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 136: memory grows until the buffer is full", "AA"), "round 136: memory grows until the buffer is full"),
    (("round 136: the cluster mirrors every packet twice", "key"), "bssxh 136: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 136: the cluster mirrors every packet twice", "lemon"),
        "csgbq 136: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 136: the cluster mirrors every packet twice", "a"), "round 136: the cluster mirrors every packet twice"),
    (("round 136: the cluster mirrors every packet twice", "zz"), "qntmc 136: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 136: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 136: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 136: the cluster mirrors every packet twice", "keyboard"),
        "bssor 136: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 136: the cluster mirrors every packet twice", "AA"), "round 136: the cluster mirrors every packet twice"),
    (
        ("round 136: ranking uses tokens learned from the corpus", "key"),
        "bssxh 136: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 136: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", "a"),
        "round 136: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 136: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 136: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 136: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", "AA"),
        "round 136: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 136: a long session ends when the candle dies", "key"),
        "bssxh 136: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 136: a long session ends when the candle dies", "lemon"),
        "csgbq 136: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 136: a long session ends when the candle dies", "a"),
        "round 136: a long session ends when the candle dies",
    ),
    (
        ("round 136: a long session ends when the candle dies", "zz"),
        "qntmc 136: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 136: a long session ends when the candle dies", "AgentU"),
        "ruyaw 136: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 136: a long session ends when the candle dies", "keyboard"),
        "bssor 136: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 136: a long session ends when the candle dies", "AA"),
        "round 136: a long session ends when the candle dies",
    ),
    (("round 136: encode the prompt then map the result", "key"), "bssxh 136: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 136: encode the prompt then map the result", "lemon"), "csgbq 136: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 136: encode the prompt then map the result", "a"), "round 136: encode the prompt then map the result"),
    (("round 136: encode the prompt then map the result", "zz"), "qntmc 136: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 136: encode the prompt then map the result", "AgentU"),
        "ruyaw 136: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 136: encode the prompt then map the result", "keyboard"),
        "bssor 136: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 136: encode the prompt then map the result", "AA"), "round 136: encode the prompt then map the result"),
    (("round 136: the kernel wakes the worker at dawn", "key"), "bssxh 136: rri iovlop ukocc xfo ambocb er neux"),
    (("round 136: the kernel wakes the worker at dawn", "lemon"), "csgbq 136: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 136: the kernel wakes the worker at dawn", "a"), "round 136: the kernel wakes the worker at dawn"),
    (("round 136: the kernel wakes the worker at dawn", "zz"), "qntmc 136: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 136: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 136: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 136: the kernel wakes the worker at dawn", "keyboard"), "bssor 136: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 136: the kernel wakes the worker at dawn", "AA"), "round 136: the kernel wakes the worker at dawn"),
    (("round 136: service latency drops after the patch", "key"), "bssxh 136: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 136: service latency drops after the patch", "lemon"), "csgbq 136: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 136: service latency drops after the patch", "a"), "round 136: service latency drops after the patch"),
    (("round 136: service latency drops after the patch", "zz"), "qntmc 136: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 136: service latency drops after the patch", "AgentU"),
        "ruyaw 136: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 136: service latency drops after the patch", "keyboard"),
        "bssor 136: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 136: service latency drops after the patch", "AA"), "round 136: service latency drops after the patch"),
    (
        ("round 136: the library caches every vector it sees", "key"),
        "bssxh 136: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 136: the library caches every vector it sees", "lemon"),
        "csgbq 136: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 136: the library caches every vector it sees", "a"), "round 136: the library caches every vector it sees"),
    (
        ("round 136: the library caches every vector it sees", "zz"),
        "qntmc 136: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 136: the library caches every vector it sees", "AgentU"),
        "ruyaw 136: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 136: the library caches every vector it sees", "keyboard"),
        "bssor 136: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 136: the library caches every vector it sees", "AA"),
        "round 136: the library caches every vector it sees",
    ),
    (("round 136: agents argue then the debate resolves", "key"), "bssxh 136: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 136: agents argue then the debate resolves", "lemon"), "csgbq 136: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 136: agents argue then the debate resolves", "a"), "round 136: agents argue then the debate resolves"),
    (("round 136: agents argue then the debate resolves", "zz"), "qntmc 136: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 136: agents argue then the debate resolves", "AgentU"),
        "ruyaw 136: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 136: agents argue then the debate resolves", "keyboard"),
        "bssor 136: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 136: agents argue then the debate resolves", "AA"), "round 136: agents argue then the debate resolves"),
    (("round 136: the filter keeps only strong matches", "key"), "bssxh 136: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 136: the filter keeps only strong matches", "lemon"), "csgbq 136: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 136: the filter keeps only strong matches", "a"), "round 136: the filter keeps only strong matches"),
    (("round 136: the filter keeps only strong matches", "zz"), "qntmc 136: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 136: the filter keeps only strong matches", "AgentU"), "ruyaw 136: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 136: the filter keeps only strong matches", "keyboard"),
        "bssor 136: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 136: the filter keeps only strong matches", "AA"), "round 136: the filter keeps only strong matches"),
    (("round 136: the model answers with a short reply", "key"), "bssxh 136: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 136: the model answers with a short reply", "lemon"), "csgbq 136: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 136: the model answers with a short reply", "a"), "round 136: the model answers with a short reply"),
    (("round 136: the model answers with a short reply", "zz"), "qntmc 136: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 136: the model answers with a short reply", "AgentU"), "ruyaw 136: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 136: the model answers with a short reply", "keyboard"),
        "bssor 136: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 136: the model answers with a short reply", "AA"), "round 136: the model answers with a short reply"),
    (
        ("round 136: the recorder stores the reasoning trace", "key"),
        "bssxh 136: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 136: the recorder stores the reasoning trace", "lemon"),
        "csgbq 136: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 136: the recorder stores the reasoning trace", "a"), "round 136: the recorder stores the reasoning trace"),
    (
        ("round 136: the recorder stores the reasoning trace", "zz"),
        "qntmc 136: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 136: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 136: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 136: the recorder stores the reasoning trace", "keyboard"),
        "bssor 136: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 136: the recorder stores the reasoning trace", "AA"),
        "round 136: the recorder stores the reasoning trace",
    ),
    (("round 136: the angel watches the processor run", "key"), "bssxh 136: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 136: the angel watches the processor run", "lemon"), "csgbq 136: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 136: the angel watches the processor run", "a"), "round 136: the angel watches the processor run"),
    (("round 136: the angel watches the processor run", "zz"), "qntmc 136: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 136: the angel watches the processor run", "AgentU"), "ruyaw 136: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 136: the angel watches the processor run", "keyboard"), "bssor 136: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 136: the angel watches the processor run", "AA"), "round 136: the angel watches the processor run"),
    (("round 136: angle of the vector decides the match", "key"), "bssxh 136: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 136: angle of the vector decides the match", "lemon"), "csgbq 136: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 136: angle of the vector decides the match", "a"), "round 136: angle of the vector decides the match"),
    (("round 136: angle of the vector decides the match", "zz"), "qntmc 136: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 136: angle of the vector decides the match", "AgentU"),
        "ruyaw 136: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 136: angle of the vector decides the match", "keyboard"),
        "bssor 136: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 136: angle of the vector decides the match", "AA"), "round 136: angle of the vector decides the match"),
    (
        ("round 136: the candle burns twice as long at night", "key"),
        "bssxh 136: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 136: the candle burns twice as long at night", "lemon"),
        "csgbq 136: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 136: the candle burns twice as long at night", "a"), "round 136: the candle burns twice as long at night"),
    (
        ("round 136: the candle burns twice as long at night", "zz"),
        "qntmc 136: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 136: the candle burns twice as long at night", "AgentU"),
        "ruyaw 136: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 136: the candle burns twice as long at night", "keyboard"),
        "bssor 136: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 136: the candle burns twice as long at night", "AA"),
        "round 136: the candle burns twice as long at night",
    ),
    (("round 136: a mirror of the universe in one line", "key"), "bssxh 136: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 136: a mirror of the universe in one line", "lemon"), "csgbq 136: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 136: a mirror of the universe in one line", "a"), "round 136: a mirror of the universe in one line"),
    (("round 136: a mirror of the universe in one line", "zz"), "qntmc 136: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 136: a mirror of the universe in one line", "AgentU"), "ruyaw 136: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 136: a mirror of the universe in one line", "keyboard"),
        "bssor 136: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 136: a mirror of the universe in one line", "AA"), "round 136: a mirror of the universe in one line"),
    (("round 136: the queue drains before the storm", "key"), "bssxh 136: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 136: the queue drains before the storm", "lemon"), "csgbq 136: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 136: the queue drains before the storm", "a"), "round 136: the queue drains before the storm"),
    (("round 136: the queue drains before the storm", "zz"), "qntmc 136: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 136: the queue drains before the storm", "AgentU"), "ruyaw 136: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 136: the queue drains before the storm", "keyboard"), "bssor 136: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 136: the queue drains before the storm", "AA"), "round 136: the queue drains before the storm"),
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
