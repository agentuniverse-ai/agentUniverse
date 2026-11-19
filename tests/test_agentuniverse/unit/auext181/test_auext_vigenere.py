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
    (("kitten181", "key"), "umrdil181"),
    (("kitten181", "lemon"), "vmfhry181"),
    (("kitten181", "a"), "kitten181"),
    (("kitten181", "zz"), "jhssdm181"),
    (("kitten181", "AgentU"), "koxgxh181"),
    (("kitten181", "keyboard"), "umrusn181"),
    (("kitten181", "AA"), "kitten181"),
    (("sitting181", "key"), "cmrdmlq181"),
    (("sitting181", "lemon"), "dmfhvyk181"),
    (("sitting181", "a"), "sitting181"),
    (("sitting181", "zz"), "rhsshmf181"),
    (("sitting181", "AgentU"), "soxgbhg181"),
    (("sitting181", "keyboard"), "cmruwnx181"),
    (("sitting181", "AA"), "sitting181"),
    (("agent181", "key"), "kkcxx181"),
    (("agent181", "lemon"), "lkqbg181"),
    (("agent181", "a"), "agent181"),
    (("agent181", "zz"), "zfdms181"),
    (("agent181", "AgentU"), "amiam181"),
    (("agent181", "keyboard"), "kkcoh181"),
    (("agent181", "AA"), "agent181"),
    (("angle181", "key"), "krevi181"),
    (("angle181", "lemon"), "lrszr181"),
    (("angle181", "a"), "angle181"),
    (("angle181", "zz"), "zmfkd181"),
    (("angle181", "AgentU"), "atkyx181"),
    (("angle181", "keyboard"), "krems181"),
    (("angle181", "AA"), "angle181"),
    (("universe181", "key"), "ergfipci181"),
    (("universe181", "lemon"), "frujrcwq181"),
    (("universe181", "a"), "universe181"),
    (("universe181", "zz"), "tmhudqrd181"),
    (("universe181", "AgentU"), "utmixlsk181"),
    (("universe181", "keyboard"), "ergwsrjh181"),
    (("universe181", "AA"), "universe181"),
    (("memory181", "key"), "wikyvw181"),
    (("memory181", "lemon"), "xiycej181"),
    (("memory181", "a"), "memory181"),
    (("memory181", "zz"), "ldlnqx181"),
    (("memory181", "AgentU"), "mkqbks181"),
    (("memory181", "keyboard"), "wikpfy181"),
    (("memory181", "AA"), "memory181"),
    (("stream181", "key"), "cxpoek181"),
    (("stream181", "lemon"), "dxdsnx181"),
    (("stream181", "a"), "stream181"),
    (("stream181", "zz"), "rsqdzl181"),
    (("stream181", "AgentU"), "szvrtg181"),
    (("stream181", "keyboard"), "cxpfom181"),
    (("stream181", "AA"), "stream181"),
    (("context181", "key"), "msldivd181"),
    (("context181", "lemon"), "nszhrix181"),
    (("context181", "a"), "context181"),
    (("context181", "zz"), "bnmsdws181"),
    (("context181", "AgentU"), "curgxrt181"),
    (("context181", "keyboard"), "mslusxk181"),
    (("context181", "AA"), "context181"),
    (("knowledge181", "key"), "urmgpcnkc181"),
    (("knowledge181", "lemon"), "vrakyphss181"),
    (("knowledge181", "a"), "knowledge181"),
    (("knowledge181", "zz"), "jmnvkdcfd181"),
    (("knowledge181", "AgentU"), "ktsjeydmi181"),
    (("knowledge181", "keyboard"), "urmxzeujo181"),
    (("knowledge181", "AA"), "knowledge181"),
    (("vector181", "key"), "fiadsp181"),
    (("vector181", "lemon"), "giohbc181"),
    (("vector181", "a"), "vector181"),
    (("vector181", "zz"), "udbsnq181"),
    (("vector181", "AgentU"), "vkgghl181"),
    (("vector181", "keyboard"), "fiaucr181"),
    (("vector181", "AA"), "vector181"),
    (("processor181", "key"), "zvmmiqcsp181"),
    (("processor181", "lemon"), "avaqrdwaf181"),
    (("processor181", "a"), "processor181"),
    (("processor181", "zz"), "oqnbdrrnq181"),
    (("processor181", "AgentU"), "pxspxmsuv181"),
    (("processor181", "keyboard"), "zvmdssjrb181"),
    (("processor181", "AA"), "processor181"),
    (("reasoning181", "key"), "biycslsre181"),
    (("reasoning181", "lemon"), "cimgbymzu181"),
    (("reasoning181", "a"), "reasoning181"),
    (("reasoning181", "zz"), "qdzrnmhmf181"),
    (("reasoning181", "AgentU"), "rkefhhitk181"),
    (("reasoning181", "keyboard"), "biytcnzqq181"),
    (("reasoning181", "AA"), "reasoning181"),
    (("machine181", "key"), "wearmlo181"),
    (("machine181", "lemon"), "xeovvyi181"),
    (("machine181", "a"), "machine181"),
    (("machine181", "zz"), "lzbghmd181"),
    (("machine181", "AgentU"), "mggubhe181"),
    (("machine181", "keyboard"), "weaiwnv181"),
    (("machine181", "AA"), "machine181"),
    (("learning181", "key"), "viybrgxk181"),
    (("learning181", "lemon"), "wimfatrs181"),
    (("learning181", "a"), "learning181"),
    (("learning181", "zz"), "kdzqmhmf181"),
    (("learning181", "AgentU"), "lkeegcnm181"),
    (("learning181", "keyboard"), "viysbiej181"),
    (("learning181", "AA"), "learning181"),
    (("model181", "key"), "wsbop181"),
    (("model181", "lemon"), "xspsy181"),
    (("model181", "a"), "model181"),
    (("model181", "zz"), "lncdk181"),
    (("model181", "AgentU"), "muhre181"),
    (("model181", "keyboard"), "wsbfz181"),
    (("model181", "AA"), "model181"),
    (("token181", "key"), "dsior181"),
    (("token181", "lemon"), "eswsa181"),
    (("token181", "a"), "token181"),
    (("token181", "zz"), "snjdm181"),
    (("token181", "AgentU"), "tuorg181"),
    (("token181", "keyboard"), "dsifb181"),
    (("token181", "AA"), "token181"),
    (("prompt181", "key"), "zvmwtr181"),
    (("prompt181", "lemon"), "avaace181"),
    (("prompt181", "a"), "prompt181"),
    (("prompt181", "zz"), "oqnlos181"),
    (("prompt181", "AgentU"), "pxszin181"),
    (("prompt181", "keyboard"), "zvmndt181"),
    (("prompt181", "AA"), "prompt181"),
    (("session181", "key"), "ciqcmmx181"),
    (("session181", "lemon"), "diegvzr181"),
    (("session181", "a"), "session181"),
    (("session181", "zz"), "rdrrhnm181"),
    (("session181", "AgentU"), "skwfbin181"),
    (("session181", "keyboard"), "ciqtwoe181"),
    (("session181", "AA"), "session181"),
    (("library181", "key"), "vmzbepi181"),
    (("library181", "lemon"), "wmnfncc181"),
    (("library181", "a"), "library181"),
    (("library181", "zz"), "khaqzqx181"),
    (("library181", "AgentU"), "lofetly181"),
    (("library181", "keyboard"), "vmzsorp181"),
    (("library181", "AA"), "library181"),
    (("service181", "key"), "cipfmao181"),
    (("service181", "lemon"), "didjvni181"),
    (("service181", "a"), "service181"),
    (("service181", "zz"), "rdquhbd181"),
    (("service181", "AgentU"), "skvibwe181"),
    (("service181", "keyboard"), "cipwwcv181"),
    (("service181", "AA"), "service181"),
    (("gateway181", "key"), "qeroayi181"),
    (("gateway181", "lemon"), "refsjlc181"),
    (("gateway181", "a"), "gateway181"),
    (("gateway181", "zz"), "fzsdvzx181"),
    (("gateway181", "AgentU"), "ggxrpuy181"),
    (("gateway181", "keyboard"), "qerfkap181"),
    (("gateway181", "AA"), "gateway181"),
    (("storage181", "key"), "cxmbeeo181"),
    (("storage181", "lemon"), "dxafnri181"),
    (("storage181", "a"), "storage181"),
    (("storage181", "zz"), "rsnqzfd181"),
    (("storage181", "AgentU"), "szsetae181"),
    (("storage181", "keyboard"), "cxmsogv181"),
    (("storage181", "AA"), "storage181"),
    (("network181", "key"), "xirgspu181"),
    (("network181", "lemon"), "yifkbco181"),
    (("network181", "a"), "network181"),
    (("network181", "zz"), "mdsvnqj181"),
    (("network181", "AgentU"), "nkxjhlk181"),
    (("network181", "keyboard"), "xirxcrb181"),
    (("network181", "AA"), "network181"),
    (("latency181", "key"), "verorai181"),
    (("latency181", "lemon"), "wefsanc181"),
    (("latency181", "a"), "latency181"),
    (("latency181", "zz"), "kzsdmbx181"),
    (("latency181", "AgentU"), "lgxrgwy181"),
    (("latency181", "keyboard"), "verfbcp181"),
    (("latency181", "AA"), "latency181"),
    (("buffer181", "key"), "lydpip181"),
    (("buffer181", "lemon"), "myrtrc181"),
    (("buffer181", "a"), "buffer181"),
    (("buffer181", "zz"), "ateedq181"),
    (("buffer181", "AgentU"), "bajsxl181"),
    (("buffer181", "keyboard"), "lydgsr181"),
    (("buffer181", "AA"), "buffer181"),
    (("queue181", "key"), "aycei181"),
    (("queue181", "lemon"), "byqir181"),
    (("queue181", "a"), "queue181"),
    (("queue181", "zz"), "ptdtd181"),
    (("queue181", "AgentU"), "qaihx181"),
    (("queue181", "keyboard"), "aycvs181"),
    (("queue181", "AA"), "queue181"),
    (("worker181", "key"), "gspuip181"),
    (("worker181", "lemon"), "hsdyrc181"),
    (("worker181", "a"), "worker181"),
    (("worker181", "zz"), "vnqjdq181"),
    (("worker181", "AgentU"), "wuvxxl181"),
    (("worker181", "keyboard"), "gsplsr181"),
    (("worker181", "AA"), "worker181"),
    (("kernel181", "key"), "uipxij181"),
    (("kernel181", "lemon"), "vidbrw181"),
    (("kernel181", "a"), "kernel181"),
    (("kernel181", "zz"), "jdqmdk181"),
    (("kernel181", "AgentU"), "kkvaxf181"),
    (("kernel181", "keyboard"), "uiposl181"),
    (("kernel181", "AA"), "kernel181"),
    (("signal181", "key"), "cmexej181"),
    (("signal181", "lemon"), "dmsbnw181"),
    (("signal181", "a"), "signal181"),
    (("signal181", "zz"), "rhfmzk181"),
    (("signal181", "AgentU"), "sokatf181"),
    (("signal181", "keyboard"), "cmeool181"),
    (("signal181", "AA"), "signal181"),
    (("packet181", "key"), "zeauir181"),
    (("packet181", "lemon"), "aeoyre181"),
    (("packet181", "a"), "packet181"),
    (("packet181", "zz"), "ozbjds181"),
    (("packet181", "AgentU"), "pggxxn181"),
    (("packet181", "keyboard"), "zealst181"),
    (("packet181", "AA"), "packet181"),
    (("router181", "key"), "bssdip181"),
    (("router181", "lemon"), "csghrc181"),
    (("router181", "a"), "router181"),
    (("router181", "zz"), "qntsdq181"),
    (("router181", "AgentU"), "ruygxl181"),
    (("router181", "keyboard"), "bssusr181"),
    (("router181", "AA"), "router181"),
    (("cluster181", "key"), "mpscxcb181"),
    (("cluster181", "lemon"), "npgggpv181"),
    (("cluster181", "a"), "cluster181"),
    (("cluster181", "zz"), "bktrsdq181"),
    (("cluster181", "AgentU"), "cryfmyr181"),
    (("cluster181", "keyboard"), "mpsthei181"),
    (("cluster181", "AA"), "cluster181"),
    (("mirror181", "key"), "wmpbsp181"),
    (("mirror181", "lemon"), "xmdfbc181"),
    (("mirror181", "a"), "mirror181"),
    (("mirror181", "zz"), "lhqqnq181"),
    (("mirror181", "AgentU"), "movehl181"),
    (("mirror181", "keyboard"), "wmpscr181"),
    (("mirror181", "AA"), "mirror181"),
    (("filter181", "key"), "pmjdip181"),
    (("filter181", "lemon"), "qmxhrc181"),
    (("filter181", "a"), "filter181"),
    (("filter181", "zz"), "ehksdq181"),
    (("filter181", "AgentU"), "fopgxl181"),
    (("filter181", "keyboard"), "pmjusr181"),
    (("filter181", "AA"), "filter181"),
    (("ranking181", "key"), "belumlq181"),
    (("ranking181", "lemon"), "cezyvyk181"),
    (("ranking181", "a"), "ranking181"),
    (("ranking181", "zz"), "qzmjhmf181"),
    (("ranking181", "AgentU"), "rgrxbhg181"),
    (("ranking181", "keyboard"), "bellwnx181"),
    (("ranking181", "AA"), "ranking181"),
    (("encoding181", "key"), "orayhgxk181"),
    (("encoding181", "lemon"), "procqtrs181"),
    (("encoding181", "a"), "encoding181"),
    (("encoding181", "zz"), "dmbnchmf181"),
    (("encoding181", "AgentU"), "etgbwcnm181"),
    (("encoding181", "keyboard"), "orapriej181"),
    (("encoding181", "AA"), "encoding181"),
    (("mapping181", "key"), "wenzmlq181"),
    (("mapping181", "lemon"), "xebdvyk181"),
    (("mapping181", "a"), "mapping181"),
    (("mapping181", "zz"), "lzoohmf181"),
    (("mapping181", "AgentU"), "mgtcbhg181"),
    (("mapping181", "keyboard"), "wenqwnx181"),
    (("mapping181", "AA"), "mapping181"),
    (("record181", "key"), "biayvb181"),
    (("record181", "lemon"), "cioceo181"),
    (("record181", "a"), "record181"),
    (("record181", "zz"), "qdbnqc181"),
    (("record181", "AgentU"), "rkgbkx181"),
    (("record181", "keyboard"), "biapfd181"),
    (("record181", "AA"), "record181"),
    (("candle181", "key"), "melnpc181"),
    (("candle181", "lemon"), "nezryp181"),
    (("candle181", "a"), "candle181"),
    (("candle181", "zz"), "bzmckd181"),
    (("candle181", "AgentU"), "cgrqey181"),
    (("candle181", "keyboard"), "meleze181"),
    (("candle181", "AA"), "candle181"),
    (("thread181", "key"), "dlpoeb181"),
    (("thread181", "lemon"), "eldsno181"),
    (("thread181", "a"), "thread181"),
    (("thread181", "zz"), "sgqdzc181"),
    (("thread181", "AgentU"), "tnvrtx181"),
    (("thread181", "keyboard"), "dlpfod181"),
    (("thread181", "AA"), "thread181"),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 181: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 181: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "a"),
        "round 181: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 181: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 181: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 181: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", "AA"),
        "round 181: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "key"),
        "bssxh 181: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 181: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "a"),
        "round 181: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 181: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 181: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 181: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", "AA"),
        "round 181: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 181: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 181: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "a"),
        "round 181: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 181: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 181: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 181: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", "AA"),
        "round 181: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 181: the processor reads the record then stops", "key"),
        "bssxh 181: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 181: the processor reads the record then stops", "lemon"),
        "csgbq 181: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 181: the processor reads the record then stops", "a"),
        "round 181: the processor reads the record then stops",
    ),
    (
        ("round 181: the processor reads the record then stops", "zz"),
        "qntmc 181: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 181: the processor reads the record then stops", "AgentU"),
        "ruyaw 181: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 181: the processor reads the record then stops", "keyboard"),
        "bssor 181: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 181: the processor reads the record then stops", "AA"),
        "round 181: the processor reads the record then stops",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "key"),
        "bssxh 181: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "lemon"),
        "csgbq 181: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "a"),
        "round 181: a worker pulls the next task from the queue",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "zz"),
        "qntmc 181: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 181: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "keyboard"),
        "bssor 181: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 181: a worker pulls the next task from the queue", "AA"),
        "round 181: a worker pulls the next task from the queue",
    ),
    (
        ("round 181: signals travel through the network layer", "key"),
        "bssxh 181: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 181: signals travel through the network layer", "lemon"),
        "csgbq 181: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 181: signals travel through the network layer", "a"),
        "round 181: signals travel through the network layer",
    ),
    (
        ("round 181: signals travel through the network layer", "zz"),
        "qntmc 181: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 181: signals travel through the network layer", "AgentU"),
        "ruyaw 181: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 181: signals travel through the network layer", "keyboard"),
        "bssor 181: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 181: signals travel through the network layer", "AA"),
        "round 181: signals travel through the network layer",
    ),
    (
        ("round 181: the gateway routes each request by policy", "key"),
        "bssxh 181: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 181: the gateway routes each request by policy", "lemon"),
        "csgbq 181: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 181: the gateway routes each request by policy", "a"),
        "round 181: the gateway routes each request by policy",
    ),
    (
        ("round 181: the gateway routes each request by policy", "zz"),
        "qntmc 181: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 181: the gateway routes each request by policy", "AgentU"),
        "ruyaw 181: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 181: the gateway routes each request by policy", "keyboard"),
        "bssor 181: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 181: the gateway routes each request by policy", "AA"),
        "round 181: the gateway routes each request by policy",
    ),
    (("round 181: memory grows until the buffer is full", "key"), "bssxh 181: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 181: memory grows until the buffer is full", "lemon"), "csgbq 181: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 181: memory grows until the buffer is full", "a"), "round 181: memory grows until the buffer is full"),
    (("round 181: memory grows until the buffer is full", "zz"), "qntmc 181: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 181: memory grows until the buffer is full", "AgentU"),
        "ruyaw 181: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 181: memory grows until the buffer is full", "keyboard"),
        "bssor 181: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 181: memory grows until the buffer is full", "AA"), "round 181: memory grows until the buffer is full"),
    (("round 181: the cluster mirrors every packet twice", "key"), "bssxh 181: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 181: the cluster mirrors every packet twice", "lemon"),
        "csgbq 181: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 181: the cluster mirrors every packet twice", "a"), "round 181: the cluster mirrors every packet twice"),
    (("round 181: the cluster mirrors every packet twice", "zz"), "qntmc 181: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 181: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 181: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 181: the cluster mirrors every packet twice", "keyboard"),
        "bssor 181: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 181: the cluster mirrors every packet twice", "AA"), "round 181: the cluster mirrors every packet twice"),
    (
        ("round 181: ranking uses tokens learned from the corpus", "key"),
        "bssxh 181: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 181: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", "a"),
        "round 181: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 181: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 181: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 181: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", "AA"),
        "round 181: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 181: a long session ends when the candle dies", "key"),
        "bssxh 181: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 181: a long session ends when the candle dies", "lemon"),
        "csgbq 181: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 181: a long session ends when the candle dies", "a"),
        "round 181: a long session ends when the candle dies",
    ),
    (
        ("round 181: a long session ends when the candle dies", "zz"),
        "qntmc 181: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 181: a long session ends when the candle dies", "AgentU"),
        "ruyaw 181: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 181: a long session ends when the candle dies", "keyboard"),
        "bssor 181: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 181: a long session ends when the candle dies", "AA"),
        "round 181: a long session ends when the candle dies",
    ),
    (("round 181: encode the prompt then map the result", "key"), "bssxh 181: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 181: encode the prompt then map the result", "lemon"), "csgbq 181: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 181: encode the prompt then map the result", "a"), "round 181: encode the prompt then map the result"),
    (("round 181: encode the prompt then map the result", "zz"), "qntmc 181: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 181: encode the prompt then map the result", "AgentU"),
        "ruyaw 181: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 181: encode the prompt then map the result", "keyboard"),
        "bssor 181: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 181: encode the prompt then map the result", "AA"), "round 181: encode the prompt then map the result"),
    (("round 181: the kernel wakes the worker at dawn", "key"), "bssxh 181: rri iovlop ukocc xfo ambocb er neux"),
    (("round 181: the kernel wakes the worker at dawn", "lemon"), "csgbq 181: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 181: the kernel wakes the worker at dawn", "a"), "round 181: the kernel wakes the worker at dawn"),
    (("round 181: the kernel wakes the worker at dawn", "zz"), "qntmc 181: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 181: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 181: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 181: the kernel wakes the worker at dawn", "keyboard"), "bssor 181: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 181: the kernel wakes the worker at dawn", "AA"), "round 181: the kernel wakes the worker at dawn"),
    (("round 181: service latency drops after the patch", "key"), "bssxh 181: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 181: service latency drops after the patch", "lemon"), "csgbq 181: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 181: service latency drops after the patch", "a"), "round 181: service latency drops after the patch"),
    (("round 181: service latency drops after the patch", "zz"), "qntmc 181: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 181: service latency drops after the patch", "AgentU"),
        "ruyaw 181: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 181: service latency drops after the patch", "keyboard"),
        "bssor 181: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 181: service latency drops after the patch", "AA"), "round 181: service latency drops after the patch"),
    (
        ("round 181: the library caches every vector it sees", "key"),
        "bssxh 181: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 181: the library caches every vector it sees", "lemon"),
        "csgbq 181: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 181: the library caches every vector it sees", "a"), "round 181: the library caches every vector it sees"),
    (
        ("round 181: the library caches every vector it sees", "zz"),
        "qntmc 181: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 181: the library caches every vector it sees", "AgentU"),
        "ruyaw 181: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 181: the library caches every vector it sees", "keyboard"),
        "bssor 181: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 181: the library caches every vector it sees", "AA"),
        "round 181: the library caches every vector it sees",
    ),
    (("round 181: agents argue then the debate resolves", "key"), "bssxh 181: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 181: agents argue then the debate resolves", "lemon"), "csgbq 181: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 181: agents argue then the debate resolves", "a"), "round 181: agents argue then the debate resolves"),
    (("round 181: agents argue then the debate resolves", "zz"), "qntmc 181: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 181: agents argue then the debate resolves", "AgentU"),
        "ruyaw 181: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 181: agents argue then the debate resolves", "keyboard"),
        "bssor 181: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 181: agents argue then the debate resolves", "AA"), "round 181: agents argue then the debate resolves"),
    (("round 181: the filter keeps only strong matches", "key"), "bssxh 181: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 181: the filter keeps only strong matches", "lemon"), "csgbq 181: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 181: the filter keeps only strong matches", "a"), "round 181: the filter keeps only strong matches"),
    (("round 181: the filter keeps only strong matches", "zz"), "qntmc 181: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 181: the filter keeps only strong matches", "AgentU"), "ruyaw 181: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 181: the filter keeps only strong matches", "keyboard"),
        "bssor 181: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 181: the filter keeps only strong matches", "AA"), "round 181: the filter keeps only strong matches"),
    (("round 181: the model answers with a short reply", "key"), "bssxh 181: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 181: the model answers with a short reply", "lemon"), "csgbq 181: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 181: the model answers with a short reply", "a"), "round 181: the model answers with a short reply"),
    (("round 181: the model answers with a short reply", "zz"), "qntmc 181: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 181: the model answers with a short reply", "AgentU"), "ruyaw 181: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 181: the model answers with a short reply", "keyboard"),
        "bssor 181: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 181: the model answers with a short reply", "AA"), "round 181: the model answers with a short reply"),
    (
        ("round 181: the recorder stores the reasoning trace", "key"),
        "bssxh 181: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 181: the recorder stores the reasoning trace", "lemon"),
        "csgbq 181: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 181: the recorder stores the reasoning trace", "a"), "round 181: the recorder stores the reasoning trace"),
    (
        ("round 181: the recorder stores the reasoning trace", "zz"),
        "qntmc 181: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 181: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 181: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 181: the recorder stores the reasoning trace", "keyboard"),
        "bssor 181: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 181: the recorder stores the reasoning trace", "AA"),
        "round 181: the recorder stores the reasoning trace",
    ),
    (("round 181: the angel watches the processor run", "key"), "bssxh 181: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 181: the angel watches the processor run", "lemon"), "csgbq 181: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 181: the angel watches the processor run", "a"), "round 181: the angel watches the processor run"),
    (("round 181: the angel watches the processor run", "zz"), "qntmc 181: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 181: the angel watches the processor run", "AgentU"), "ruyaw 181: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 181: the angel watches the processor run", "keyboard"), "bssor 181: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 181: the angel watches the processor run", "AA"), "round 181: the angel watches the processor run"),
    (("round 181: angle of the vector decides the match", "key"), "bssxh 181: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 181: angle of the vector decides the match", "lemon"), "csgbq 181: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 181: angle of the vector decides the match", "a"), "round 181: angle of the vector decides the match"),
    (("round 181: angle of the vector decides the match", "zz"), "qntmc 181: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 181: angle of the vector decides the match", "AgentU"),
        "ruyaw 181: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 181: angle of the vector decides the match", "keyboard"),
        "bssor 181: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 181: angle of the vector decides the match", "AA"), "round 181: angle of the vector decides the match"),
    (
        ("round 181: the candle burns twice as long at night", "key"),
        "bssxh 181: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 181: the candle burns twice as long at night", "lemon"),
        "csgbq 181: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 181: the candle burns twice as long at night", "a"), "round 181: the candle burns twice as long at night"),
    (
        ("round 181: the candle burns twice as long at night", "zz"),
        "qntmc 181: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 181: the candle burns twice as long at night", "AgentU"),
        "ruyaw 181: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 181: the candle burns twice as long at night", "keyboard"),
        "bssor 181: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 181: the candle burns twice as long at night", "AA"),
        "round 181: the candle burns twice as long at night",
    ),
    (("round 181: a mirror of the universe in one line", "key"), "bssxh 181: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 181: a mirror of the universe in one line", "lemon"), "csgbq 181: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 181: a mirror of the universe in one line", "a"), "round 181: a mirror of the universe in one line"),
    (("round 181: a mirror of the universe in one line", "zz"), "qntmc 181: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 181: a mirror of the universe in one line", "AgentU"), "ruyaw 181: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 181: a mirror of the universe in one line", "keyboard"),
        "bssor 181: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 181: a mirror of the universe in one line", "AA"), "round 181: a mirror of the universe in one line"),
    (("round 181: the queue drains before the storm", "key"), "bssxh 181: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 181: the queue drains before the storm", "lemon"), "csgbq 181: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 181: the queue drains before the storm", "a"), "round 181: the queue drains before the storm"),
    (("round 181: the queue drains before the storm", "zz"), "qntmc 181: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 181: the queue drains before the storm", "AgentU"), "ruyaw 181: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 181: the queue drains before the storm", "keyboard"), "bssor 181: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 181: the queue drains before the storm", "AA"), "round 181: the queue drains before the storm"),
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
