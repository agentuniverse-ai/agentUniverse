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
    (("kitten157", "key"), "umrdil157"),
    (("kitten157", "lemon"), "vmfhry157"),
    (("kitten157", "a"), "kitten157"),
    (("kitten157", "zz"), "jhssdm157"),
    (("kitten157", "AgentU"), "koxgxh157"),
    (("kitten157", "keyboard"), "umrusn157"),
    (("kitten157", "AA"), "kitten157"),
    (("sitting157", "key"), "cmrdmlq157"),
    (("sitting157", "lemon"), "dmfhvyk157"),
    (("sitting157", "a"), "sitting157"),
    (("sitting157", "zz"), "rhsshmf157"),
    (("sitting157", "AgentU"), "soxgbhg157"),
    (("sitting157", "keyboard"), "cmruwnx157"),
    (("sitting157", "AA"), "sitting157"),
    (("agent157", "key"), "kkcxx157"),
    (("agent157", "lemon"), "lkqbg157"),
    (("agent157", "a"), "agent157"),
    (("agent157", "zz"), "zfdms157"),
    (("agent157", "AgentU"), "amiam157"),
    (("agent157", "keyboard"), "kkcoh157"),
    (("agent157", "AA"), "agent157"),
    (("angle157", "key"), "krevi157"),
    (("angle157", "lemon"), "lrszr157"),
    (("angle157", "a"), "angle157"),
    (("angle157", "zz"), "zmfkd157"),
    (("angle157", "AgentU"), "atkyx157"),
    (("angle157", "keyboard"), "krems157"),
    (("angle157", "AA"), "angle157"),
    (("universe157", "key"), "ergfipci157"),
    (("universe157", "lemon"), "frujrcwq157"),
    (("universe157", "a"), "universe157"),
    (("universe157", "zz"), "tmhudqrd157"),
    (("universe157", "AgentU"), "utmixlsk157"),
    (("universe157", "keyboard"), "ergwsrjh157"),
    (("universe157", "AA"), "universe157"),
    (("memory157", "key"), "wikyvw157"),
    (("memory157", "lemon"), "xiycej157"),
    (("memory157", "a"), "memory157"),
    (("memory157", "zz"), "ldlnqx157"),
    (("memory157", "AgentU"), "mkqbks157"),
    (("memory157", "keyboard"), "wikpfy157"),
    (("memory157", "AA"), "memory157"),
    (("stream157", "key"), "cxpoek157"),
    (("stream157", "lemon"), "dxdsnx157"),
    (("stream157", "a"), "stream157"),
    (("stream157", "zz"), "rsqdzl157"),
    (("stream157", "AgentU"), "szvrtg157"),
    (("stream157", "keyboard"), "cxpfom157"),
    (("stream157", "AA"), "stream157"),
    (("context157", "key"), "msldivd157"),
    (("context157", "lemon"), "nszhrix157"),
    (("context157", "a"), "context157"),
    (("context157", "zz"), "bnmsdws157"),
    (("context157", "AgentU"), "curgxrt157"),
    (("context157", "keyboard"), "mslusxk157"),
    (("context157", "AA"), "context157"),
    (("knowledge157", "key"), "urmgpcnkc157"),
    (("knowledge157", "lemon"), "vrakyphss157"),
    (("knowledge157", "a"), "knowledge157"),
    (("knowledge157", "zz"), "jmnvkdcfd157"),
    (("knowledge157", "AgentU"), "ktsjeydmi157"),
    (("knowledge157", "keyboard"), "urmxzeujo157"),
    (("knowledge157", "AA"), "knowledge157"),
    (("vector157", "key"), "fiadsp157"),
    (("vector157", "lemon"), "giohbc157"),
    (("vector157", "a"), "vector157"),
    (("vector157", "zz"), "udbsnq157"),
    (("vector157", "AgentU"), "vkgghl157"),
    (("vector157", "keyboard"), "fiaucr157"),
    (("vector157", "AA"), "vector157"),
    (("processor157", "key"), "zvmmiqcsp157"),
    (("processor157", "lemon"), "avaqrdwaf157"),
    (("processor157", "a"), "processor157"),
    (("processor157", "zz"), "oqnbdrrnq157"),
    (("processor157", "AgentU"), "pxspxmsuv157"),
    (("processor157", "keyboard"), "zvmdssjrb157"),
    (("processor157", "AA"), "processor157"),
    (("reasoning157", "key"), "biycslsre157"),
    (("reasoning157", "lemon"), "cimgbymzu157"),
    (("reasoning157", "a"), "reasoning157"),
    (("reasoning157", "zz"), "qdzrnmhmf157"),
    (("reasoning157", "AgentU"), "rkefhhitk157"),
    (("reasoning157", "keyboard"), "biytcnzqq157"),
    (("reasoning157", "AA"), "reasoning157"),
    (("machine157", "key"), "wearmlo157"),
    (("machine157", "lemon"), "xeovvyi157"),
    (("machine157", "a"), "machine157"),
    (("machine157", "zz"), "lzbghmd157"),
    (("machine157", "AgentU"), "mggubhe157"),
    (("machine157", "keyboard"), "weaiwnv157"),
    (("machine157", "AA"), "machine157"),
    (("learning157", "key"), "viybrgxk157"),
    (("learning157", "lemon"), "wimfatrs157"),
    (("learning157", "a"), "learning157"),
    (("learning157", "zz"), "kdzqmhmf157"),
    (("learning157", "AgentU"), "lkeegcnm157"),
    (("learning157", "keyboard"), "viysbiej157"),
    (("learning157", "AA"), "learning157"),
    (("model157", "key"), "wsbop157"),
    (("model157", "lemon"), "xspsy157"),
    (("model157", "a"), "model157"),
    (("model157", "zz"), "lncdk157"),
    (("model157", "AgentU"), "muhre157"),
    (("model157", "keyboard"), "wsbfz157"),
    (("model157", "AA"), "model157"),
    (("token157", "key"), "dsior157"),
    (("token157", "lemon"), "eswsa157"),
    (("token157", "a"), "token157"),
    (("token157", "zz"), "snjdm157"),
    (("token157", "AgentU"), "tuorg157"),
    (("token157", "keyboard"), "dsifb157"),
    (("token157", "AA"), "token157"),
    (("prompt157", "key"), "zvmwtr157"),
    (("prompt157", "lemon"), "avaace157"),
    (("prompt157", "a"), "prompt157"),
    (("prompt157", "zz"), "oqnlos157"),
    (("prompt157", "AgentU"), "pxszin157"),
    (("prompt157", "keyboard"), "zvmndt157"),
    (("prompt157", "AA"), "prompt157"),
    (("session157", "key"), "ciqcmmx157"),
    (("session157", "lemon"), "diegvzr157"),
    (("session157", "a"), "session157"),
    (("session157", "zz"), "rdrrhnm157"),
    (("session157", "AgentU"), "skwfbin157"),
    (("session157", "keyboard"), "ciqtwoe157"),
    (("session157", "AA"), "session157"),
    (("library157", "key"), "vmzbepi157"),
    (("library157", "lemon"), "wmnfncc157"),
    (("library157", "a"), "library157"),
    (("library157", "zz"), "khaqzqx157"),
    (("library157", "AgentU"), "lofetly157"),
    (("library157", "keyboard"), "vmzsorp157"),
    (("library157", "AA"), "library157"),
    (("service157", "key"), "cipfmao157"),
    (("service157", "lemon"), "didjvni157"),
    (("service157", "a"), "service157"),
    (("service157", "zz"), "rdquhbd157"),
    (("service157", "AgentU"), "skvibwe157"),
    (("service157", "keyboard"), "cipwwcv157"),
    (("service157", "AA"), "service157"),
    (("gateway157", "key"), "qeroayi157"),
    (("gateway157", "lemon"), "refsjlc157"),
    (("gateway157", "a"), "gateway157"),
    (("gateway157", "zz"), "fzsdvzx157"),
    (("gateway157", "AgentU"), "ggxrpuy157"),
    (("gateway157", "keyboard"), "qerfkap157"),
    (("gateway157", "AA"), "gateway157"),
    (("storage157", "key"), "cxmbeeo157"),
    (("storage157", "lemon"), "dxafnri157"),
    (("storage157", "a"), "storage157"),
    (("storage157", "zz"), "rsnqzfd157"),
    (("storage157", "AgentU"), "szsetae157"),
    (("storage157", "keyboard"), "cxmsogv157"),
    (("storage157", "AA"), "storage157"),
    (("network157", "key"), "xirgspu157"),
    (("network157", "lemon"), "yifkbco157"),
    (("network157", "a"), "network157"),
    (("network157", "zz"), "mdsvnqj157"),
    (("network157", "AgentU"), "nkxjhlk157"),
    (("network157", "keyboard"), "xirxcrb157"),
    (("network157", "AA"), "network157"),
    (("latency157", "key"), "verorai157"),
    (("latency157", "lemon"), "wefsanc157"),
    (("latency157", "a"), "latency157"),
    (("latency157", "zz"), "kzsdmbx157"),
    (("latency157", "AgentU"), "lgxrgwy157"),
    (("latency157", "keyboard"), "verfbcp157"),
    (("latency157", "AA"), "latency157"),
    (("buffer157", "key"), "lydpip157"),
    (("buffer157", "lemon"), "myrtrc157"),
    (("buffer157", "a"), "buffer157"),
    (("buffer157", "zz"), "ateedq157"),
    (("buffer157", "AgentU"), "bajsxl157"),
    (("buffer157", "keyboard"), "lydgsr157"),
    (("buffer157", "AA"), "buffer157"),
    (("queue157", "key"), "aycei157"),
    (("queue157", "lemon"), "byqir157"),
    (("queue157", "a"), "queue157"),
    (("queue157", "zz"), "ptdtd157"),
    (("queue157", "AgentU"), "qaihx157"),
    (("queue157", "keyboard"), "aycvs157"),
    (("queue157", "AA"), "queue157"),
    (("worker157", "key"), "gspuip157"),
    (("worker157", "lemon"), "hsdyrc157"),
    (("worker157", "a"), "worker157"),
    (("worker157", "zz"), "vnqjdq157"),
    (("worker157", "AgentU"), "wuvxxl157"),
    (("worker157", "keyboard"), "gsplsr157"),
    (("worker157", "AA"), "worker157"),
    (("kernel157", "key"), "uipxij157"),
    (("kernel157", "lemon"), "vidbrw157"),
    (("kernel157", "a"), "kernel157"),
    (("kernel157", "zz"), "jdqmdk157"),
    (("kernel157", "AgentU"), "kkvaxf157"),
    (("kernel157", "keyboard"), "uiposl157"),
    (("kernel157", "AA"), "kernel157"),
    (("signal157", "key"), "cmexej157"),
    (("signal157", "lemon"), "dmsbnw157"),
    (("signal157", "a"), "signal157"),
    (("signal157", "zz"), "rhfmzk157"),
    (("signal157", "AgentU"), "sokatf157"),
    (("signal157", "keyboard"), "cmeool157"),
    (("signal157", "AA"), "signal157"),
    (("packet157", "key"), "zeauir157"),
    (("packet157", "lemon"), "aeoyre157"),
    (("packet157", "a"), "packet157"),
    (("packet157", "zz"), "ozbjds157"),
    (("packet157", "AgentU"), "pggxxn157"),
    (("packet157", "keyboard"), "zealst157"),
    (("packet157", "AA"), "packet157"),
    (("router157", "key"), "bssdip157"),
    (("router157", "lemon"), "csghrc157"),
    (("router157", "a"), "router157"),
    (("router157", "zz"), "qntsdq157"),
    (("router157", "AgentU"), "ruygxl157"),
    (("router157", "keyboard"), "bssusr157"),
    (("router157", "AA"), "router157"),
    (("cluster157", "key"), "mpscxcb157"),
    (("cluster157", "lemon"), "npgggpv157"),
    (("cluster157", "a"), "cluster157"),
    (("cluster157", "zz"), "bktrsdq157"),
    (("cluster157", "AgentU"), "cryfmyr157"),
    (("cluster157", "keyboard"), "mpsthei157"),
    (("cluster157", "AA"), "cluster157"),
    (("mirror157", "key"), "wmpbsp157"),
    (("mirror157", "lemon"), "xmdfbc157"),
    (("mirror157", "a"), "mirror157"),
    (("mirror157", "zz"), "lhqqnq157"),
    (("mirror157", "AgentU"), "movehl157"),
    (("mirror157", "keyboard"), "wmpscr157"),
    (("mirror157", "AA"), "mirror157"),
    (("filter157", "key"), "pmjdip157"),
    (("filter157", "lemon"), "qmxhrc157"),
    (("filter157", "a"), "filter157"),
    (("filter157", "zz"), "ehksdq157"),
    (("filter157", "AgentU"), "fopgxl157"),
    (("filter157", "keyboard"), "pmjusr157"),
    (("filter157", "AA"), "filter157"),
    (("ranking157", "key"), "belumlq157"),
    (("ranking157", "lemon"), "cezyvyk157"),
    (("ranking157", "a"), "ranking157"),
    (("ranking157", "zz"), "qzmjhmf157"),
    (("ranking157", "AgentU"), "rgrxbhg157"),
    (("ranking157", "keyboard"), "bellwnx157"),
    (("ranking157", "AA"), "ranking157"),
    (("encoding157", "key"), "orayhgxk157"),
    (("encoding157", "lemon"), "procqtrs157"),
    (("encoding157", "a"), "encoding157"),
    (("encoding157", "zz"), "dmbnchmf157"),
    (("encoding157", "AgentU"), "etgbwcnm157"),
    (("encoding157", "keyboard"), "orapriej157"),
    (("encoding157", "AA"), "encoding157"),
    (("mapping157", "key"), "wenzmlq157"),
    (("mapping157", "lemon"), "xebdvyk157"),
    (("mapping157", "a"), "mapping157"),
    (("mapping157", "zz"), "lzoohmf157"),
    (("mapping157", "AgentU"), "mgtcbhg157"),
    (("mapping157", "keyboard"), "wenqwnx157"),
    (("mapping157", "AA"), "mapping157"),
    (("record157", "key"), "biayvb157"),
    (("record157", "lemon"), "cioceo157"),
    (("record157", "a"), "record157"),
    (("record157", "zz"), "qdbnqc157"),
    (("record157", "AgentU"), "rkgbkx157"),
    (("record157", "keyboard"), "biapfd157"),
    (("record157", "AA"), "record157"),
    (("candle157", "key"), "melnpc157"),
    (("candle157", "lemon"), "nezryp157"),
    (("candle157", "a"), "candle157"),
    (("candle157", "zz"), "bzmckd157"),
    (("candle157", "AgentU"), "cgrqey157"),
    (("candle157", "keyboard"), "meleze157"),
    (("candle157", "AA"), "candle157"),
    (("thread157", "key"), "dlpoeb157"),
    (("thread157", "lemon"), "eldsno157"),
    (("thread157", "a"), "thread157"),
    (("thread157", "zz"), "sgqdzc157"),
    (("thread157", "AgentU"), "tnvrtx157"),
    (("thread157", "keyboard"), "dlpfod157"),
    (("thread157", "AA"), "thread157"),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 157: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 157: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "a"),
        "round 157: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 157: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 157: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 157: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", "AA"),
        "round 157: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "key"),
        "bssxh 157: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 157: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "a"),
        "round 157: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 157: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 157: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 157: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", "AA"),
        "round 157: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 157: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 157: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "a"),
        "round 157: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 157: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 157: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 157: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", "AA"),
        "round 157: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 157: the processor reads the record then stops", "key"),
        "bssxh 157: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 157: the processor reads the record then stops", "lemon"),
        "csgbq 157: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 157: the processor reads the record then stops", "a"),
        "round 157: the processor reads the record then stops",
    ),
    (
        ("round 157: the processor reads the record then stops", "zz"),
        "qntmc 157: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 157: the processor reads the record then stops", "AgentU"),
        "ruyaw 157: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 157: the processor reads the record then stops", "keyboard"),
        "bssor 157: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 157: the processor reads the record then stops", "AA"),
        "round 157: the processor reads the record then stops",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "key"),
        "bssxh 157: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "lemon"),
        "csgbq 157: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "a"),
        "round 157: a worker pulls the next task from the queue",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "zz"),
        "qntmc 157: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 157: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "keyboard"),
        "bssor 157: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 157: a worker pulls the next task from the queue", "AA"),
        "round 157: a worker pulls the next task from the queue",
    ),
    (
        ("round 157: signals travel through the network layer", "key"),
        "bssxh 157: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 157: signals travel through the network layer", "lemon"),
        "csgbq 157: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 157: signals travel through the network layer", "a"),
        "round 157: signals travel through the network layer",
    ),
    (
        ("round 157: signals travel through the network layer", "zz"),
        "qntmc 157: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 157: signals travel through the network layer", "AgentU"),
        "ruyaw 157: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 157: signals travel through the network layer", "keyboard"),
        "bssor 157: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 157: signals travel through the network layer", "AA"),
        "round 157: signals travel through the network layer",
    ),
    (
        ("round 157: the gateway routes each request by policy", "key"),
        "bssxh 157: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 157: the gateway routes each request by policy", "lemon"),
        "csgbq 157: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 157: the gateway routes each request by policy", "a"),
        "round 157: the gateway routes each request by policy",
    ),
    (
        ("round 157: the gateway routes each request by policy", "zz"),
        "qntmc 157: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 157: the gateway routes each request by policy", "AgentU"),
        "ruyaw 157: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 157: the gateway routes each request by policy", "keyboard"),
        "bssor 157: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 157: the gateway routes each request by policy", "AA"),
        "round 157: the gateway routes each request by policy",
    ),
    (("round 157: memory grows until the buffer is full", "key"), "bssxh 157: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 157: memory grows until the buffer is full", "lemon"), "csgbq 157: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 157: memory grows until the buffer is full", "a"), "round 157: memory grows until the buffer is full"),
    (("round 157: memory grows until the buffer is full", "zz"), "qntmc 157: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 157: memory grows until the buffer is full", "AgentU"),
        "ruyaw 157: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 157: memory grows until the buffer is full", "keyboard"),
        "bssor 157: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 157: memory grows until the buffer is full", "AA"), "round 157: memory grows until the buffer is full"),
    (("round 157: the cluster mirrors every packet twice", "key"), "bssxh 157: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 157: the cluster mirrors every packet twice", "lemon"),
        "csgbq 157: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 157: the cluster mirrors every packet twice", "a"), "round 157: the cluster mirrors every packet twice"),
    (("round 157: the cluster mirrors every packet twice", "zz"), "qntmc 157: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 157: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 157: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 157: the cluster mirrors every packet twice", "keyboard"),
        "bssor 157: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 157: the cluster mirrors every packet twice", "AA"), "round 157: the cluster mirrors every packet twice"),
    (
        ("round 157: ranking uses tokens learned from the corpus", "key"),
        "bssxh 157: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 157: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", "a"),
        "round 157: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 157: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 157: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 157: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", "AA"),
        "round 157: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 157: a long session ends when the candle dies", "key"),
        "bssxh 157: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 157: a long session ends when the candle dies", "lemon"),
        "csgbq 157: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 157: a long session ends when the candle dies", "a"),
        "round 157: a long session ends when the candle dies",
    ),
    (
        ("round 157: a long session ends when the candle dies", "zz"),
        "qntmc 157: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 157: a long session ends when the candle dies", "AgentU"),
        "ruyaw 157: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 157: a long session ends when the candle dies", "keyboard"),
        "bssor 157: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 157: a long session ends when the candle dies", "AA"),
        "round 157: a long session ends when the candle dies",
    ),
    (("round 157: encode the prompt then map the result", "key"), "bssxh 157: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 157: encode the prompt then map the result", "lemon"), "csgbq 157: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 157: encode the prompt then map the result", "a"), "round 157: encode the prompt then map the result"),
    (("round 157: encode the prompt then map the result", "zz"), "qntmc 157: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 157: encode the prompt then map the result", "AgentU"),
        "ruyaw 157: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 157: encode the prompt then map the result", "keyboard"),
        "bssor 157: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 157: encode the prompt then map the result", "AA"), "round 157: encode the prompt then map the result"),
    (("round 157: the kernel wakes the worker at dawn", "key"), "bssxh 157: rri iovlop ukocc xfo ambocb er neux"),
    (("round 157: the kernel wakes the worker at dawn", "lemon"), "csgbq 157: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 157: the kernel wakes the worker at dawn", "a"), "round 157: the kernel wakes the worker at dawn"),
    (("round 157: the kernel wakes the worker at dawn", "zz"), "qntmc 157: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 157: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 157: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 157: the kernel wakes the worker at dawn", "keyboard"), "bssor 157: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 157: the kernel wakes the worker at dawn", "AA"), "round 157: the kernel wakes the worker at dawn"),
    (("round 157: service latency drops after the patch", "key"), "bssxh 157: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 157: service latency drops after the patch", "lemon"), "csgbq 157: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 157: service latency drops after the patch", "a"), "round 157: service latency drops after the patch"),
    (("round 157: service latency drops after the patch", "zz"), "qntmc 157: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 157: service latency drops after the patch", "AgentU"),
        "ruyaw 157: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 157: service latency drops after the patch", "keyboard"),
        "bssor 157: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 157: service latency drops after the patch", "AA"), "round 157: service latency drops after the patch"),
    (
        ("round 157: the library caches every vector it sees", "key"),
        "bssxh 157: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 157: the library caches every vector it sees", "lemon"),
        "csgbq 157: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 157: the library caches every vector it sees", "a"), "round 157: the library caches every vector it sees"),
    (
        ("round 157: the library caches every vector it sees", "zz"),
        "qntmc 157: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 157: the library caches every vector it sees", "AgentU"),
        "ruyaw 157: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 157: the library caches every vector it sees", "keyboard"),
        "bssor 157: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 157: the library caches every vector it sees", "AA"),
        "round 157: the library caches every vector it sees",
    ),
    (("round 157: agents argue then the debate resolves", "key"), "bssxh 157: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 157: agents argue then the debate resolves", "lemon"), "csgbq 157: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 157: agents argue then the debate resolves", "a"), "round 157: agents argue then the debate resolves"),
    (("round 157: agents argue then the debate resolves", "zz"), "qntmc 157: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 157: agents argue then the debate resolves", "AgentU"),
        "ruyaw 157: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 157: agents argue then the debate resolves", "keyboard"),
        "bssor 157: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 157: agents argue then the debate resolves", "AA"), "round 157: agents argue then the debate resolves"),
    (("round 157: the filter keeps only strong matches", "key"), "bssxh 157: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 157: the filter keeps only strong matches", "lemon"), "csgbq 157: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 157: the filter keeps only strong matches", "a"), "round 157: the filter keeps only strong matches"),
    (("round 157: the filter keeps only strong matches", "zz"), "qntmc 157: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 157: the filter keeps only strong matches", "AgentU"), "ruyaw 157: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 157: the filter keeps only strong matches", "keyboard"),
        "bssor 157: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 157: the filter keeps only strong matches", "AA"), "round 157: the filter keeps only strong matches"),
    (("round 157: the model answers with a short reply", "key"), "bssxh 157: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 157: the model answers with a short reply", "lemon"), "csgbq 157: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 157: the model answers with a short reply", "a"), "round 157: the model answers with a short reply"),
    (("round 157: the model answers with a short reply", "zz"), "qntmc 157: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 157: the model answers with a short reply", "AgentU"), "ruyaw 157: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 157: the model answers with a short reply", "keyboard"),
        "bssor 157: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 157: the model answers with a short reply", "AA"), "round 157: the model answers with a short reply"),
    (
        ("round 157: the recorder stores the reasoning trace", "key"),
        "bssxh 157: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 157: the recorder stores the reasoning trace", "lemon"),
        "csgbq 157: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 157: the recorder stores the reasoning trace", "a"), "round 157: the recorder stores the reasoning trace"),
    (
        ("round 157: the recorder stores the reasoning trace", "zz"),
        "qntmc 157: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 157: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 157: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 157: the recorder stores the reasoning trace", "keyboard"),
        "bssor 157: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 157: the recorder stores the reasoning trace", "AA"),
        "round 157: the recorder stores the reasoning trace",
    ),
    (("round 157: the angel watches the processor run", "key"), "bssxh 157: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 157: the angel watches the processor run", "lemon"), "csgbq 157: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 157: the angel watches the processor run", "a"), "round 157: the angel watches the processor run"),
    (("round 157: the angel watches the processor run", "zz"), "qntmc 157: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 157: the angel watches the processor run", "AgentU"), "ruyaw 157: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 157: the angel watches the processor run", "keyboard"), "bssor 157: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 157: the angel watches the processor run", "AA"), "round 157: the angel watches the processor run"),
    (("round 157: angle of the vector decides the match", "key"), "bssxh 157: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 157: angle of the vector decides the match", "lemon"), "csgbq 157: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 157: angle of the vector decides the match", "a"), "round 157: angle of the vector decides the match"),
    (("round 157: angle of the vector decides the match", "zz"), "qntmc 157: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 157: angle of the vector decides the match", "AgentU"),
        "ruyaw 157: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 157: angle of the vector decides the match", "keyboard"),
        "bssor 157: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 157: angle of the vector decides the match", "AA"), "round 157: angle of the vector decides the match"),
    (
        ("round 157: the candle burns twice as long at night", "key"),
        "bssxh 157: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 157: the candle burns twice as long at night", "lemon"),
        "csgbq 157: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 157: the candle burns twice as long at night", "a"), "round 157: the candle burns twice as long at night"),
    (
        ("round 157: the candle burns twice as long at night", "zz"),
        "qntmc 157: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 157: the candle burns twice as long at night", "AgentU"),
        "ruyaw 157: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 157: the candle burns twice as long at night", "keyboard"),
        "bssor 157: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 157: the candle burns twice as long at night", "AA"),
        "round 157: the candle burns twice as long at night",
    ),
    (("round 157: a mirror of the universe in one line", "key"), "bssxh 157: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 157: a mirror of the universe in one line", "lemon"), "csgbq 157: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 157: a mirror of the universe in one line", "a"), "round 157: a mirror of the universe in one line"),
    (("round 157: a mirror of the universe in one line", "zz"), "qntmc 157: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 157: a mirror of the universe in one line", "AgentU"), "ruyaw 157: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 157: a mirror of the universe in one line", "keyboard"),
        "bssor 157: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 157: a mirror of the universe in one line", "AA"), "round 157: a mirror of the universe in one line"),
    (("round 157: the queue drains before the storm", "key"), "bssxh 157: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 157: the queue drains before the storm", "lemon"), "csgbq 157: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 157: the queue drains before the storm", "a"), "round 157: the queue drains before the storm"),
    (("round 157: the queue drains before the storm", "zz"), "qntmc 157: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 157: the queue drains before the storm", "AgentU"), "ruyaw 157: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 157: the queue drains before the storm", "keyboard"), "bssor 157: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 157: the queue drains before the storm", "AA"), "round 157: the queue drains before the storm"),
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
