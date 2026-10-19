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
    (("kitten740", "key"), "umrdil740"),
    (("kitten740", "lemon"), "vmfhry740"),
    (("kitten740", "a"), "kitten740"),
    (("kitten740", "zz"), "jhssdm740"),
    (("kitten740", "AgentU"), "koxgxh740"),
    (("kitten740", "keyboard"), "umrusn740"),
    (("kitten740", "AA"), "kitten740"),
    (("sitting740", "key"), "cmrdmlq740"),
    (("sitting740", "lemon"), "dmfhvyk740"),
    (("sitting740", "a"), "sitting740"),
    (("sitting740", "zz"), "rhsshmf740"),
    (("sitting740", "AgentU"), "soxgbhg740"),
    (("sitting740", "keyboard"), "cmruwnx740"),
    (("sitting740", "AA"), "sitting740"),
    (("agent740", "key"), "kkcxx740"),
    (("agent740", "lemon"), "lkqbg740"),
    (("agent740", "a"), "agent740"),
    (("agent740", "zz"), "zfdms740"),
    (("agent740", "AgentU"), "amiam740"),
    (("agent740", "keyboard"), "kkcoh740"),
    (("agent740", "AA"), "agent740"),
    (("angle740", "key"), "krevi740"),
    (("angle740", "lemon"), "lrszr740"),
    (("angle740", "a"), "angle740"),
    (("angle740", "zz"), "zmfkd740"),
    (("angle740", "AgentU"), "atkyx740"),
    (("angle740", "keyboard"), "krems740"),
    (("angle740", "AA"), "angle740"),
    (("universe740", "key"), "ergfipci740"),
    (("universe740", "lemon"), "frujrcwq740"),
    (("universe740", "a"), "universe740"),
    (("universe740", "zz"), "tmhudqrd740"),
    (("universe740", "AgentU"), "utmixlsk740"),
    (("universe740", "keyboard"), "ergwsrjh740"),
    (("universe740", "AA"), "universe740"),
    (("memory740", "key"), "wikyvw740"),
    (("memory740", "lemon"), "xiycej740"),
    (("memory740", "a"), "memory740"),
    (("memory740", "zz"), "ldlnqx740"),
    (("memory740", "AgentU"), "mkqbks740"),
    (("memory740", "keyboard"), "wikpfy740"),
    (("memory740", "AA"), "memory740"),
    (("stream740", "key"), "cxpoek740"),
    (("stream740", "lemon"), "dxdsnx740"),
    (("stream740", "a"), "stream740"),
    (("stream740", "zz"), "rsqdzl740"),
    (("stream740", "AgentU"), "szvrtg740"),
    (("stream740", "keyboard"), "cxpfom740"),
    (("stream740", "AA"), "stream740"),
    (("context740", "key"), "msldivd740"),
    (("context740", "lemon"), "nszhrix740"),
    (("context740", "a"), "context740"),
    (("context740", "zz"), "bnmsdws740"),
    (("context740", "AgentU"), "curgxrt740"),
    (("context740", "keyboard"), "mslusxk740"),
    (("context740", "AA"), "context740"),
    (("knowledge740", "key"), "urmgpcnkc740"),
    (("knowledge740", "lemon"), "vrakyphss740"),
    (("knowledge740", "a"), "knowledge740"),
    (("knowledge740", "zz"), "jmnvkdcfd740"),
    (("knowledge740", "AgentU"), "ktsjeydmi740"),
    (("knowledge740", "keyboard"), "urmxzeujo740"),
    (("knowledge740", "AA"), "knowledge740"),
    (("vector740", "key"), "fiadsp740"),
    (("vector740", "lemon"), "giohbc740"),
    (("vector740", "a"), "vector740"),
    (("vector740", "zz"), "udbsnq740"),
    (("vector740", "AgentU"), "vkgghl740"),
    (("vector740", "keyboard"), "fiaucr740"),
    (("vector740", "AA"), "vector740"),
    (("processor740", "key"), "zvmmiqcsp740"),
    (("processor740", "lemon"), "avaqrdwaf740"),
    (("processor740", "a"), "processor740"),
    (("processor740", "zz"), "oqnbdrrnq740"),
    (("processor740", "AgentU"), "pxspxmsuv740"),
    (("processor740", "keyboard"), "zvmdssjrb740"),
    (("processor740", "AA"), "processor740"),
    (("reasoning740", "key"), "biycslsre740"),
    (("reasoning740", "lemon"), "cimgbymzu740"),
    (("reasoning740", "a"), "reasoning740"),
    (("reasoning740", "zz"), "qdzrnmhmf740"),
    (("reasoning740", "AgentU"), "rkefhhitk740"),
    (("reasoning740", "keyboard"), "biytcnzqq740"),
    (("reasoning740", "AA"), "reasoning740"),
    (("machine740", "key"), "wearmlo740"),
    (("machine740", "lemon"), "xeovvyi740"),
    (("machine740", "a"), "machine740"),
    (("machine740", "zz"), "lzbghmd740"),
    (("machine740", "AgentU"), "mggubhe740"),
    (("machine740", "keyboard"), "weaiwnv740"),
    (("machine740", "AA"), "machine740"),
    (("learning740", "key"), "viybrgxk740"),
    (("learning740", "lemon"), "wimfatrs740"),
    (("learning740", "a"), "learning740"),
    (("learning740", "zz"), "kdzqmhmf740"),
    (("learning740", "AgentU"), "lkeegcnm740"),
    (("learning740", "keyboard"), "viysbiej740"),
    (("learning740", "AA"), "learning740"),
    (("model740", "key"), "wsbop740"),
    (("model740", "lemon"), "xspsy740"),
    (("model740", "a"), "model740"),
    (("model740", "zz"), "lncdk740"),
    (("model740", "AgentU"), "muhre740"),
    (("model740", "keyboard"), "wsbfz740"),
    (("model740", "AA"), "model740"),
    (("token740", "key"), "dsior740"),
    (("token740", "lemon"), "eswsa740"),
    (("token740", "a"), "token740"),
    (("token740", "zz"), "snjdm740"),
    (("token740", "AgentU"), "tuorg740"),
    (("token740", "keyboard"), "dsifb740"),
    (("token740", "AA"), "token740"),
    (("prompt740", "key"), "zvmwtr740"),
    (("prompt740", "lemon"), "avaace740"),
    (("prompt740", "a"), "prompt740"),
    (("prompt740", "zz"), "oqnlos740"),
    (("prompt740", "AgentU"), "pxszin740"),
    (("prompt740", "keyboard"), "zvmndt740"),
    (("prompt740", "AA"), "prompt740"),
    (("session740", "key"), "ciqcmmx740"),
    (("session740", "lemon"), "diegvzr740"),
    (("session740", "a"), "session740"),
    (("session740", "zz"), "rdrrhnm740"),
    (("session740", "AgentU"), "skwfbin740"),
    (("session740", "keyboard"), "ciqtwoe740"),
    (("session740", "AA"), "session740"),
    (("library740", "key"), "vmzbepi740"),
    (("library740", "lemon"), "wmnfncc740"),
    (("library740", "a"), "library740"),
    (("library740", "zz"), "khaqzqx740"),
    (("library740", "AgentU"), "lofetly740"),
    (("library740", "keyboard"), "vmzsorp740"),
    (("library740", "AA"), "library740"),
    (("service740", "key"), "cipfmao740"),
    (("service740", "lemon"), "didjvni740"),
    (("service740", "a"), "service740"),
    (("service740", "zz"), "rdquhbd740"),
    (("service740", "AgentU"), "skvibwe740"),
    (("service740", "keyboard"), "cipwwcv740"),
    (("service740", "AA"), "service740"),
    (("gateway740", "key"), "qeroayi740"),
    (("gateway740", "lemon"), "refsjlc740"),
    (("gateway740", "a"), "gateway740"),
    (("gateway740", "zz"), "fzsdvzx740"),
    (("gateway740", "AgentU"), "ggxrpuy740"),
    (("gateway740", "keyboard"), "qerfkap740"),
    (("gateway740", "AA"), "gateway740"),
    (("storage740", "key"), "cxmbeeo740"),
    (("storage740", "lemon"), "dxafnri740"),
    (("storage740", "a"), "storage740"),
    (("storage740", "zz"), "rsnqzfd740"),
    (("storage740", "AgentU"), "szsetae740"),
    (("storage740", "keyboard"), "cxmsogv740"),
    (("storage740", "AA"), "storage740"),
    (("network740", "key"), "xirgspu740"),
    (("network740", "lemon"), "yifkbco740"),
    (("network740", "a"), "network740"),
    (("network740", "zz"), "mdsvnqj740"),
    (("network740", "AgentU"), "nkxjhlk740"),
    (("network740", "keyboard"), "xirxcrb740"),
    (("network740", "AA"), "network740"),
    (("latency740", "key"), "verorai740"),
    (("latency740", "lemon"), "wefsanc740"),
    (("latency740", "a"), "latency740"),
    (("latency740", "zz"), "kzsdmbx740"),
    (("latency740", "AgentU"), "lgxrgwy740"),
    (("latency740", "keyboard"), "verfbcp740"),
    (("latency740", "AA"), "latency740"),
    (("buffer740", "key"), "lydpip740"),
    (("buffer740", "lemon"), "myrtrc740"),
    (("buffer740", "a"), "buffer740"),
    (("buffer740", "zz"), "ateedq740"),
    (("buffer740", "AgentU"), "bajsxl740"),
    (("buffer740", "keyboard"), "lydgsr740"),
    (("buffer740", "AA"), "buffer740"),
    (("queue740", "key"), "aycei740"),
    (("queue740", "lemon"), "byqir740"),
    (("queue740", "a"), "queue740"),
    (("queue740", "zz"), "ptdtd740"),
    (("queue740", "AgentU"), "qaihx740"),
    (("queue740", "keyboard"), "aycvs740"),
    (("queue740", "AA"), "queue740"),
    (("worker740", "key"), "gspuip740"),
    (("worker740", "lemon"), "hsdyrc740"),
    (("worker740", "a"), "worker740"),
    (("worker740", "zz"), "vnqjdq740"),
    (("worker740", "AgentU"), "wuvxxl740"),
    (("worker740", "keyboard"), "gsplsr740"),
    (("worker740", "AA"), "worker740"),
    (("kernel740", "key"), "uipxij740"),
    (("kernel740", "lemon"), "vidbrw740"),
    (("kernel740", "a"), "kernel740"),
    (("kernel740", "zz"), "jdqmdk740"),
    (("kernel740", "AgentU"), "kkvaxf740"),
    (("kernel740", "keyboard"), "uiposl740"),
    (("kernel740", "AA"), "kernel740"),
    (("signal740", "key"), "cmexej740"),
    (("signal740", "lemon"), "dmsbnw740"),
    (("signal740", "a"), "signal740"),
    (("signal740", "zz"), "rhfmzk740"),
    (("signal740", "AgentU"), "sokatf740"),
    (("signal740", "keyboard"), "cmeool740"),
    (("signal740", "AA"), "signal740"),
    (("packet740", "key"), "zeauir740"),
    (("packet740", "lemon"), "aeoyre740"),
    (("packet740", "a"), "packet740"),
    (("packet740", "zz"), "ozbjds740"),
    (("packet740", "AgentU"), "pggxxn740"),
    (("packet740", "keyboard"), "zealst740"),
    (("packet740", "AA"), "packet740"),
    (("router740", "key"), "bssdip740"),
    (("router740", "lemon"), "csghrc740"),
    (("router740", "a"), "router740"),
    (("router740", "zz"), "qntsdq740"),
    (("router740", "AgentU"), "ruygxl740"),
    (("router740", "keyboard"), "bssusr740"),
    (("router740", "AA"), "router740"),
    (("cluster740", "key"), "mpscxcb740"),
    (("cluster740", "lemon"), "npgggpv740"),
    (("cluster740", "a"), "cluster740"),
    (("cluster740", "zz"), "bktrsdq740"),
    (("cluster740", "AgentU"), "cryfmyr740"),
    (("cluster740", "keyboard"), "mpsthei740"),
    (("cluster740", "AA"), "cluster740"),
    (("mirror740", "key"), "wmpbsp740"),
    (("mirror740", "lemon"), "xmdfbc740"),
    (("mirror740", "a"), "mirror740"),
    (("mirror740", "zz"), "lhqqnq740"),
    (("mirror740", "AgentU"), "movehl740"),
    (("mirror740", "keyboard"), "wmpscr740"),
    (("mirror740", "AA"), "mirror740"),
    (("filter740", "key"), "pmjdip740"),
    (("filter740", "lemon"), "qmxhrc740"),
    (("filter740", "a"), "filter740"),
    (("filter740", "zz"), "ehksdq740"),
    (("filter740", "AgentU"), "fopgxl740"),
    (("filter740", "keyboard"), "pmjusr740"),
    (("filter740", "AA"), "filter740"),
    (("ranking740", "key"), "belumlq740"),
    (("ranking740", "lemon"), "cezyvyk740"),
    (("ranking740", "a"), "ranking740"),
    (("ranking740", "zz"), "qzmjhmf740"),
    (("ranking740", "AgentU"), "rgrxbhg740"),
    (("ranking740", "keyboard"), "bellwnx740"),
    (("ranking740", "AA"), "ranking740"),
    (("encoding740", "key"), "orayhgxk740"),
    (("encoding740", "lemon"), "procqtrs740"),
    (("encoding740", "a"), "encoding740"),
    (("encoding740", "zz"), "dmbnchmf740"),
    (("encoding740", "AgentU"), "etgbwcnm740"),
    (("encoding740", "keyboard"), "orapriej740"),
    (("encoding740", "AA"), "encoding740"),
    (("mapping740", "key"), "wenzmlq740"),
    (("mapping740", "lemon"), "xebdvyk740"),
    (("mapping740", "a"), "mapping740"),
    (("mapping740", "zz"), "lzoohmf740"),
    (("mapping740", "AgentU"), "mgtcbhg740"),
    (("mapping740", "keyboard"), "wenqwnx740"),
    (("mapping740", "AA"), "mapping740"),
    (("record740", "key"), "biayvb740"),
    (("record740", "lemon"), "cioceo740"),
    (("record740", "a"), "record740"),
    (("record740", "zz"), "qdbnqc740"),
    (("record740", "AgentU"), "rkgbkx740"),
    (("record740", "keyboard"), "biapfd740"),
    (("record740", "AA"), "record740"),
    (("candle740", "key"), "melnpc740"),
    (("candle740", "lemon"), "nezryp740"),
    (("candle740", "a"), "candle740"),
    (("candle740", "zz"), "bzmckd740"),
    (("candle740", "AgentU"), "cgrqey740"),
    (("candle740", "keyboard"), "meleze740"),
    (("candle740", "AA"), "candle740"),
    (("thread740", "key"), "dlpoeb740"),
    (("thread740", "lemon"), "eldsno740"),
    (("thread740", "a"), "thread740"),
    (("thread740", "zz"), "sgqdzc740"),
    (("thread740", "AgentU"), "tnvrtx740"),
    (("thread740", "keyboard"), "dlpfod740"),
    (("thread740", "AA"), "thread740"),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 740: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 740: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "a"),
        "round 740: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 740: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 740: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 740: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", "AA"),
        "round 740: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "key"),
        "bssxh 740: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 740: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "a"),
        "round 740: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 740: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 740: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 740: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", "AA"),
        "round 740: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 740: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 740: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "a"),
        "round 740: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 740: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 740: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 740: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", "AA"),
        "round 740: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 740: the processor reads the record then stops", "key"),
        "bssxh 740: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 740: the processor reads the record then stops", "lemon"),
        "csgbq 740: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 740: the processor reads the record then stops", "a"),
        "round 740: the processor reads the record then stops",
    ),
    (
        ("round 740: the processor reads the record then stops", "zz"),
        "qntmc 740: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 740: the processor reads the record then stops", "AgentU"),
        "ruyaw 740: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 740: the processor reads the record then stops", "keyboard"),
        "bssor 740: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 740: the processor reads the record then stops", "AA"),
        "round 740: the processor reads the record then stops",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "key"),
        "bssxh 740: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "lemon"),
        "csgbq 740: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "a"),
        "round 740: a worker pulls the next task from the queue",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "zz"),
        "qntmc 740: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 740: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "keyboard"),
        "bssor 740: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 740: a worker pulls the next task from the queue", "AA"),
        "round 740: a worker pulls the next task from the queue",
    ),
    (
        ("round 740: signals travel through the network layer", "key"),
        "bssxh 740: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 740: signals travel through the network layer", "lemon"),
        "csgbq 740: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 740: signals travel through the network layer", "a"),
        "round 740: signals travel through the network layer",
    ),
    (
        ("round 740: signals travel through the network layer", "zz"),
        "qntmc 740: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 740: signals travel through the network layer", "AgentU"),
        "ruyaw 740: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 740: signals travel through the network layer", "keyboard"),
        "bssor 740: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 740: signals travel through the network layer", "AA"),
        "round 740: signals travel through the network layer",
    ),
    (
        ("round 740: the gateway routes each request by policy", "key"),
        "bssxh 740: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 740: the gateway routes each request by policy", "lemon"),
        "csgbq 740: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 740: the gateway routes each request by policy", "a"),
        "round 740: the gateway routes each request by policy",
    ),
    (
        ("round 740: the gateway routes each request by policy", "zz"),
        "qntmc 740: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 740: the gateway routes each request by policy", "AgentU"),
        "ruyaw 740: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 740: the gateway routes each request by policy", "keyboard"),
        "bssor 740: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 740: the gateway routes each request by policy", "AA"),
        "round 740: the gateway routes each request by policy",
    ),
    (("round 740: memory grows until the buffer is full", "key"), "bssxh 740: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 740: memory grows until the buffer is full", "lemon"), "csgbq 740: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 740: memory grows until the buffer is full", "a"), "round 740: memory grows until the buffer is full"),
    (("round 740: memory grows until the buffer is full", "zz"), "qntmc 740: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 740: memory grows until the buffer is full", "AgentU"),
        "ruyaw 740: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 740: memory grows until the buffer is full", "keyboard"),
        "bssor 740: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 740: memory grows until the buffer is full", "AA"), "round 740: memory grows until the buffer is full"),
    (("round 740: the cluster mirrors every packet twice", "key"), "bssxh 740: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 740: the cluster mirrors every packet twice", "lemon"),
        "csgbq 740: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 740: the cluster mirrors every packet twice", "a"), "round 740: the cluster mirrors every packet twice"),
    (("round 740: the cluster mirrors every packet twice", "zz"), "qntmc 740: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 740: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 740: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 740: the cluster mirrors every packet twice", "keyboard"),
        "bssor 740: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 740: the cluster mirrors every packet twice", "AA"), "round 740: the cluster mirrors every packet twice"),
    (
        ("round 740: ranking uses tokens learned from the corpus", "key"),
        "bssxh 740: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 740: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", "a"),
        "round 740: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 740: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 740: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 740: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", "AA"),
        "round 740: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 740: a long session ends when the candle dies", "key"),
        "bssxh 740: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 740: a long session ends when the candle dies", "lemon"),
        "csgbq 740: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 740: a long session ends when the candle dies", "a"),
        "round 740: a long session ends when the candle dies",
    ),
    (
        ("round 740: a long session ends when the candle dies", "zz"),
        "qntmc 740: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 740: a long session ends when the candle dies", "AgentU"),
        "ruyaw 740: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 740: a long session ends when the candle dies", "keyboard"),
        "bssor 740: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 740: a long session ends when the candle dies", "AA"),
        "round 740: a long session ends when the candle dies",
    ),
    (("round 740: encode the prompt then map the result", "key"), "bssxh 740: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 740: encode the prompt then map the result", "lemon"), "csgbq 740: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 740: encode the prompt then map the result", "a"), "round 740: encode the prompt then map the result"),
    (("round 740: encode the prompt then map the result", "zz"), "qntmc 740: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 740: encode the prompt then map the result", "AgentU"),
        "ruyaw 740: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 740: encode the prompt then map the result", "keyboard"),
        "bssor 740: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 740: encode the prompt then map the result", "AA"), "round 740: encode the prompt then map the result"),
    (("round 740: the kernel wakes the worker at dawn", "key"), "bssxh 740: rri iovlop ukocc xfo ambocb er neux"),
    (("round 740: the kernel wakes the worker at dawn", "lemon"), "csgbq 740: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 740: the kernel wakes the worker at dawn", "a"), "round 740: the kernel wakes the worker at dawn"),
    (("round 740: the kernel wakes the worker at dawn", "zz"), "qntmc 740: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 740: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 740: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 740: the kernel wakes the worker at dawn", "keyboard"), "bssor 740: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 740: the kernel wakes the worker at dawn", "AA"), "round 740: the kernel wakes the worker at dawn"),
    (("round 740: service latency drops after the patch", "key"), "bssxh 740: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 740: service latency drops after the patch", "lemon"), "csgbq 740: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 740: service latency drops after the patch", "a"), "round 740: service latency drops after the patch"),
    (("round 740: service latency drops after the patch", "zz"), "qntmc 740: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 740: service latency drops after the patch", "AgentU"),
        "ruyaw 740: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 740: service latency drops after the patch", "keyboard"),
        "bssor 740: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 740: service latency drops after the patch", "AA"), "round 740: service latency drops after the patch"),
    (
        ("round 740: the library caches every vector it sees", "key"),
        "bssxh 740: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 740: the library caches every vector it sees", "lemon"),
        "csgbq 740: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 740: the library caches every vector it sees", "a"), "round 740: the library caches every vector it sees"),
    (
        ("round 740: the library caches every vector it sees", "zz"),
        "qntmc 740: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 740: the library caches every vector it sees", "AgentU"),
        "ruyaw 740: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 740: the library caches every vector it sees", "keyboard"),
        "bssor 740: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 740: the library caches every vector it sees", "AA"),
        "round 740: the library caches every vector it sees",
    ),
    (("round 740: agents argue then the debate resolves", "key"), "bssxh 740: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 740: agents argue then the debate resolves", "lemon"), "csgbq 740: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 740: agents argue then the debate resolves", "a"), "round 740: agents argue then the debate resolves"),
    (("round 740: agents argue then the debate resolves", "zz"), "qntmc 740: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 740: agents argue then the debate resolves", "AgentU"),
        "ruyaw 740: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 740: agents argue then the debate resolves", "keyboard"),
        "bssor 740: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 740: agents argue then the debate resolves", "AA"), "round 740: agents argue then the debate resolves"),
    (("round 740: the filter keeps only strong matches", "key"), "bssxh 740: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 740: the filter keeps only strong matches", "lemon"), "csgbq 740: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 740: the filter keeps only strong matches", "a"), "round 740: the filter keeps only strong matches"),
    (("round 740: the filter keeps only strong matches", "zz"), "qntmc 740: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 740: the filter keeps only strong matches", "AgentU"), "ruyaw 740: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 740: the filter keeps only strong matches", "keyboard"),
        "bssor 740: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 740: the filter keeps only strong matches", "AA"), "round 740: the filter keeps only strong matches"),
    (("round 740: the model answers with a short reply", "key"), "bssxh 740: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 740: the model answers with a short reply", "lemon"), "csgbq 740: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 740: the model answers with a short reply", "a"), "round 740: the model answers with a short reply"),
    (("round 740: the model answers with a short reply", "zz"), "qntmc 740: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 740: the model answers with a short reply", "AgentU"), "ruyaw 740: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 740: the model answers with a short reply", "keyboard"),
        "bssor 740: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 740: the model answers with a short reply", "AA"), "round 740: the model answers with a short reply"),
    (
        ("round 740: the recorder stores the reasoning trace", "key"),
        "bssxh 740: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 740: the recorder stores the reasoning trace", "lemon"),
        "csgbq 740: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 740: the recorder stores the reasoning trace", "a"), "round 740: the recorder stores the reasoning trace"),
    (
        ("round 740: the recorder stores the reasoning trace", "zz"),
        "qntmc 740: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 740: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 740: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 740: the recorder stores the reasoning trace", "keyboard"),
        "bssor 740: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 740: the recorder stores the reasoning trace", "AA"),
        "round 740: the recorder stores the reasoning trace",
    ),
    (("round 740: the angel watches the processor run", "key"), "bssxh 740: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 740: the angel watches the processor run", "lemon"), "csgbq 740: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 740: the angel watches the processor run", "a"), "round 740: the angel watches the processor run"),
    (("round 740: the angel watches the processor run", "zz"), "qntmc 740: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 740: the angel watches the processor run", "AgentU"), "ruyaw 740: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 740: the angel watches the processor run", "keyboard"), "bssor 740: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 740: the angel watches the processor run", "AA"), "round 740: the angel watches the processor run"),
    (("round 740: angle of the vector decides the match", "key"), "bssxh 740: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 740: angle of the vector decides the match", "lemon"), "csgbq 740: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 740: angle of the vector decides the match", "a"), "round 740: angle of the vector decides the match"),
    (("round 740: angle of the vector decides the match", "zz"), "qntmc 740: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 740: angle of the vector decides the match", "AgentU"),
        "ruyaw 740: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 740: angle of the vector decides the match", "keyboard"),
        "bssor 740: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 740: angle of the vector decides the match", "AA"), "round 740: angle of the vector decides the match"),
    (
        ("round 740: the candle burns twice as long at night", "key"),
        "bssxh 740: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 740: the candle burns twice as long at night", "lemon"),
        "csgbq 740: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 740: the candle burns twice as long at night", "a"), "round 740: the candle burns twice as long at night"),
    (
        ("round 740: the candle burns twice as long at night", "zz"),
        "qntmc 740: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 740: the candle burns twice as long at night", "AgentU"),
        "ruyaw 740: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 740: the candle burns twice as long at night", "keyboard"),
        "bssor 740: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 740: the candle burns twice as long at night", "AA"),
        "round 740: the candle burns twice as long at night",
    ),
    (("round 740: a mirror of the universe in one line", "key"), "bssxh 740: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 740: a mirror of the universe in one line", "lemon"), "csgbq 740: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 740: a mirror of the universe in one line", "a"), "round 740: a mirror of the universe in one line"),
    (("round 740: a mirror of the universe in one line", "zz"), "qntmc 740: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 740: a mirror of the universe in one line", "AgentU"), "ruyaw 740: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 740: a mirror of the universe in one line", "keyboard"),
        "bssor 740: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 740: a mirror of the universe in one line", "AA"), "round 740: a mirror of the universe in one line"),
    (("round 740: the queue drains before the storm", "key"), "bssxh 740: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 740: the queue drains before the storm", "lemon"), "csgbq 740: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 740: the queue drains before the storm", "a"), "round 740: the queue drains before the storm"),
    (("round 740: the queue drains before the storm", "zz"), "qntmc 740: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 740: the queue drains before the storm", "AgentU"), "ruyaw 740: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 740: the queue drains before the storm", "keyboard"), "bssor 740: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 740: the queue drains before the storm", "AA"), "round 740: the queue drains before the storm"),
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
