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
    (("kitten150", "key"), "umrdil150"),
    (("kitten150", "lemon"), "vmfhry150"),
    (("kitten150", "a"), "kitten150"),
    (("kitten150", "zz"), "jhssdm150"),
    (("kitten150", "AgentU"), "koxgxh150"),
    (("kitten150", "keyboard"), "umrusn150"),
    (("kitten150", "AA"), "kitten150"),
    (("sitting150", "key"), "cmrdmlq150"),
    (("sitting150", "lemon"), "dmfhvyk150"),
    (("sitting150", "a"), "sitting150"),
    (("sitting150", "zz"), "rhsshmf150"),
    (("sitting150", "AgentU"), "soxgbhg150"),
    (("sitting150", "keyboard"), "cmruwnx150"),
    (("sitting150", "AA"), "sitting150"),
    (("agent150", "key"), "kkcxx150"),
    (("agent150", "lemon"), "lkqbg150"),
    (("agent150", "a"), "agent150"),
    (("agent150", "zz"), "zfdms150"),
    (("agent150", "AgentU"), "amiam150"),
    (("agent150", "keyboard"), "kkcoh150"),
    (("agent150", "AA"), "agent150"),
    (("angle150", "key"), "krevi150"),
    (("angle150", "lemon"), "lrszr150"),
    (("angle150", "a"), "angle150"),
    (("angle150", "zz"), "zmfkd150"),
    (("angle150", "AgentU"), "atkyx150"),
    (("angle150", "keyboard"), "krems150"),
    (("angle150", "AA"), "angle150"),
    (("universe150", "key"), "ergfipci150"),
    (("universe150", "lemon"), "frujrcwq150"),
    (("universe150", "a"), "universe150"),
    (("universe150", "zz"), "tmhudqrd150"),
    (("universe150", "AgentU"), "utmixlsk150"),
    (("universe150", "keyboard"), "ergwsrjh150"),
    (("universe150", "AA"), "universe150"),
    (("memory150", "key"), "wikyvw150"),
    (("memory150", "lemon"), "xiycej150"),
    (("memory150", "a"), "memory150"),
    (("memory150", "zz"), "ldlnqx150"),
    (("memory150", "AgentU"), "mkqbks150"),
    (("memory150", "keyboard"), "wikpfy150"),
    (("memory150", "AA"), "memory150"),
    (("stream150", "key"), "cxpoek150"),
    (("stream150", "lemon"), "dxdsnx150"),
    (("stream150", "a"), "stream150"),
    (("stream150", "zz"), "rsqdzl150"),
    (("stream150", "AgentU"), "szvrtg150"),
    (("stream150", "keyboard"), "cxpfom150"),
    (("stream150", "AA"), "stream150"),
    (("context150", "key"), "msldivd150"),
    (("context150", "lemon"), "nszhrix150"),
    (("context150", "a"), "context150"),
    (("context150", "zz"), "bnmsdws150"),
    (("context150", "AgentU"), "curgxrt150"),
    (("context150", "keyboard"), "mslusxk150"),
    (("context150", "AA"), "context150"),
    (("knowledge150", "key"), "urmgpcnkc150"),
    (("knowledge150", "lemon"), "vrakyphss150"),
    (("knowledge150", "a"), "knowledge150"),
    (("knowledge150", "zz"), "jmnvkdcfd150"),
    (("knowledge150", "AgentU"), "ktsjeydmi150"),
    (("knowledge150", "keyboard"), "urmxzeujo150"),
    (("knowledge150", "AA"), "knowledge150"),
    (("vector150", "key"), "fiadsp150"),
    (("vector150", "lemon"), "giohbc150"),
    (("vector150", "a"), "vector150"),
    (("vector150", "zz"), "udbsnq150"),
    (("vector150", "AgentU"), "vkgghl150"),
    (("vector150", "keyboard"), "fiaucr150"),
    (("vector150", "AA"), "vector150"),
    (("processor150", "key"), "zvmmiqcsp150"),
    (("processor150", "lemon"), "avaqrdwaf150"),
    (("processor150", "a"), "processor150"),
    (("processor150", "zz"), "oqnbdrrnq150"),
    (("processor150", "AgentU"), "pxspxmsuv150"),
    (("processor150", "keyboard"), "zvmdssjrb150"),
    (("processor150", "AA"), "processor150"),
    (("reasoning150", "key"), "biycslsre150"),
    (("reasoning150", "lemon"), "cimgbymzu150"),
    (("reasoning150", "a"), "reasoning150"),
    (("reasoning150", "zz"), "qdzrnmhmf150"),
    (("reasoning150", "AgentU"), "rkefhhitk150"),
    (("reasoning150", "keyboard"), "biytcnzqq150"),
    (("reasoning150", "AA"), "reasoning150"),
    (("machine150", "key"), "wearmlo150"),
    (("machine150", "lemon"), "xeovvyi150"),
    (("machine150", "a"), "machine150"),
    (("machine150", "zz"), "lzbghmd150"),
    (("machine150", "AgentU"), "mggubhe150"),
    (("machine150", "keyboard"), "weaiwnv150"),
    (("machine150", "AA"), "machine150"),
    (("learning150", "key"), "viybrgxk150"),
    (("learning150", "lemon"), "wimfatrs150"),
    (("learning150", "a"), "learning150"),
    (("learning150", "zz"), "kdzqmhmf150"),
    (("learning150", "AgentU"), "lkeegcnm150"),
    (("learning150", "keyboard"), "viysbiej150"),
    (("learning150", "AA"), "learning150"),
    (("model150", "key"), "wsbop150"),
    (("model150", "lemon"), "xspsy150"),
    (("model150", "a"), "model150"),
    (("model150", "zz"), "lncdk150"),
    (("model150", "AgentU"), "muhre150"),
    (("model150", "keyboard"), "wsbfz150"),
    (("model150", "AA"), "model150"),
    (("token150", "key"), "dsior150"),
    (("token150", "lemon"), "eswsa150"),
    (("token150", "a"), "token150"),
    (("token150", "zz"), "snjdm150"),
    (("token150", "AgentU"), "tuorg150"),
    (("token150", "keyboard"), "dsifb150"),
    (("token150", "AA"), "token150"),
    (("prompt150", "key"), "zvmwtr150"),
    (("prompt150", "lemon"), "avaace150"),
    (("prompt150", "a"), "prompt150"),
    (("prompt150", "zz"), "oqnlos150"),
    (("prompt150", "AgentU"), "pxszin150"),
    (("prompt150", "keyboard"), "zvmndt150"),
    (("prompt150", "AA"), "prompt150"),
    (("session150", "key"), "ciqcmmx150"),
    (("session150", "lemon"), "diegvzr150"),
    (("session150", "a"), "session150"),
    (("session150", "zz"), "rdrrhnm150"),
    (("session150", "AgentU"), "skwfbin150"),
    (("session150", "keyboard"), "ciqtwoe150"),
    (("session150", "AA"), "session150"),
    (("library150", "key"), "vmzbepi150"),
    (("library150", "lemon"), "wmnfncc150"),
    (("library150", "a"), "library150"),
    (("library150", "zz"), "khaqzqx150"),
    (("library150", "AgentU"), "lofetly150"),
    (("library150", "keyboard"), "vmzsorp150"),
    (("library150", "AA"), "library150"),
    (("service150", "key"), "cipfmao150"),
    (("service150", "lemon"), "didjvni150"),
    (("service150", "a"), "service150"),
    (("service150", "zz"), "rdquhbd150"),
    (("service150", "AgentU"), "skvibwe150"),
    (("service150", "keyboard"), "cipwwcv150"),
    (("service150", "AA"), "service150"),
    (("gateway150", "key"), "qeroayi150"),
    (("gateway150", "lemon"), "refsjlc150"),
    (("gateway150", "a"), "gateway150"),
    (("gateway150", "zz"), "fzsdvzx150"),
    (("gateway150", "AgentU"), "ggxrpuy150"),
    (("gateway150", "keyboard"), "qerfkap150"),
    (("gateway150", "AA"), "gateway150"),
    (("storage150", "key"), "cxmbeeo150"),
    (("storage150", "lemon"), "dxafnri150"),
    (("storage150", "a"), "storage150"),
    (("storage150", "zz"), "rsnqzfd150"),
    (("storage150", "AgentU"), "szsetae150"),
    (("storage150", "keyboard"), "cxmsogv150"),
    (("storage150", "AA"), "storage150"),
    (("network150", "key"), "xirgspu150"),
    (("network150", "lemon"), "yifkbco150"),
    (("network150", "a"), "network150"),
    (("network150", "zz"), "mdsvnqj150"),
    (("network150", "AgentU"), "nkxjhlk150"),
    (("network150", "keyboard"), "xirxcrb150"),
    (("network150", "AA"), "network150"),
    (("latency150", "key"), "verorai150"),
    (("latency150", "lemon"), "wefsanc150"),
    (("latency150", "a"), "latency150"),
    (("latency150", "zz"), "kzsdmbx150"),
    (("latency150", "AgentU"), "lgxrgwy150"),
    (("latency150", "keyboard"), "verfbcp150"),
    (("latency150", "AA"), "latency150"),
    (("buffer150", "key"), "lydpip150"),
    (("buffer150", "lemon"), "myrtrc150"),
    (("buffer150", "a"), "buffer150"),
    (("buffer150", "zz"), "ateedq150"),
    (("buffer150", "AgentU"), "bajsxl150"),
    (("buffer150", "keyboard"), "lydgsr150"),
    (("buffer150", "AA"), "buffer150"),
    (("queue150", "key"), "aycei150"),
    (("queue150", "lemon"), "byqir150"),
    (("queue150", "a"), "queue150"),
    (("queue150", "zz"), "ptdtd150"),
    (("queue150", "AgentU"), "qaihx150"),
    (("queue150", "keyboard"), "aycvs150"),
    (("queue150", "AA"), "queue150"),
    (("worker150", "key"), "gspuip150"),
    (("worker150", "lemon"), "hsdyrc150"),
    (("worker150", "a"), "worker150"),
    (("worker150", "zz"), "vnqjdq150"),
    (("worker150", "AgentU"), "wuvxxl150"),
    (("worker150", "keyboard"), "gsplsr150"),
    (("worker150", "AA"), "worker150"),
    (("kernel150", "key"), "uipxij150"),
    (("kernel150", "lemon"), "vidbrw150"),
    (("kernel150", "a"), "kernel150"),
    (("kernel150", "zz"), "jdqmdk150"),
    (("kernel150", "AgentU"), "kkvaxf150"),
    (("kernel150", "keyboard"), "uiposl150"),
    (("kernel150", "AA"), "kernel150"),
    (("signal150", "key"), "cmexej150"),
    (("signal150", "lemon"), "dmsbnw150"),
    (("signal150", "a"), "signal150"),
    (("signal150", "zz"), "rhfmzk150"),
    (("signal150", "AgentU"), "sokatf150"),
    (("signal150", "keyboard"), "cmeool150"),
    (("signal150", "AA"), "signal150"),
    (("packet150", "key"), "zeauir150"),
    (("packet150", "lemon"), "aeoyre150"),
    (("packet150", "a"), "packet150"),
    (("packet150", "zz"), "ozbjds150"),
    (("packet150", "AgentU"), "pggxxn150"),
    (("packet150", "keyboard"), "zealst150"),
    (("packet150", "AA"), "packet150"),
    (("router150", "key"), "bssdip150"),
    (("router150", "lemon"), "csghrc150"),
    (("router150", "a"), "router150"),
    (("router150", "zz"), "qntsdq150"),
    (("router150", "AgentU"), "ruygxl150"),
    (("router150", "keyboard"), "bssusr150"),
    (("router150", "AA"), "router150"),
    (("cluster150", "key"), "mpscxcb150"),
    (("cluster150", "lemon"), "npgggpv150"),
    (("cluster150", "a"), "cluster150"),
    (("cluster150", "zz"), "bktrsdq150"),
    (("cluster150", "AgentU"), "cryfmyr150"),
    (("cluster150", "keyboard"), "mpsthei150"),
    (("cluster150", "AA"), "cluster150"),
    (("mirror150", "key"), "wmpbsp150"),
    (("mirror150", "lemon"), "xmdfbc150"),
    (("mirror150", "a"), "mirror150"),
    (("mirror150", "zz"), "lhqqnq150"),
    (("mirror150", "AgentU"), "movehl150"),
    (("mirror150", "keyboard"), "wmpscr150"),
    (("mirror150", "AA"), "mirror150"),
    (("filter150", "key"), "pmjdip150"),
    (("filter150", "lemon"), "qmxhrc150"),
    (("filter150", "a"), "filter150"),
    (("filter150", "zz"), "ehksdq150"),
    (("filter150", "AgentU"), "fopgxl150"),
    (("filter150", "keyboard"), "pmjusr150"),
    (("filter150", "AA"), "filter150"),
    (("ranking150", "key"), "belumlq150"),
    (("ranking150", "lemon"), "cezyvyk150"),
    (("ranking150", "a"), "ranking150"),
    (("ranking150", "zz"), "qzmjhmf150"),
    (("ranking150", "AgentU"), "rgrxbhg150"),
    (("ranking150", "keyboard"), "bellwnx150"),
    (("ranking150", "AA"), "ranking150"),
    (("encoding150", "key"), "orayhgxk150"),
    (("encoding150", "lemon"), "procqtrs150"),
    (("encoding150", "a"), "encoding150"),
    (("encoding150", "zz"), "dmbnchmf150"),
    (("encoding150", "AgentU"), "etgbwcnm150"),
    (("encoding150", "keyboard"), "orapriej150"),
    (("encoding150", "AA"), "encoding150"),
    (("mapping150", "key"), "wenzmlq150"),
    (("mapping150", "lemon"), "xebdvyk150"),
    (("mapping150", "a"), "mapping150"),
    (("mapping150", "zz"), "lzoohmf150"),
    (("mapping150", "AgentU"), "mgtcbhg150"),
    (("mapping150", "keyboard"), "wenqwnx150"),
    (("mapping150", "AA"), "mapping150"),
    (("record150", "key"), "biayvb150"),
    (("record150", "lemon"), "cioceo150"),
    (("record150", "a"), "record150"),
    (("record150", "zz"), "qdbnqc150"),
    (("record150", "AgentU"), "rkgbkx150"),
    (("record150", "keyboard"), "biapfd150"),
    (("record150", "AA"), "record150"),
    (("candle150", "key"), "melnpc150"),
    (("candle150", "lemon"), "nezryp150"),
    (("candle150", "a"), "candle150"),
    (("candle150", "zz"), "bzmckd150"),
    (("candle150", "AgentU"), "cgrqey150"),
    (("candle150", "keyboard"), "meleze150"),
    (("candle150", "AA"), "candle150"),
    (("thread150", "key"), "dlpoeb150"),
    (("thread150", "lemon"), "eldsno150"),
    (("thread150", "a"), "thread150"),
    (("thread150", "zz"), "sgqdzc150"),
    (("thread150", "AgentU"), "tnvrtx150"),
    (("thread150", "keyboard"), "dlpfod150"),
    (("thread150", "AA"), "thread150"),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 150: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 150: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "a"),
        "round 150: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 150: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 150: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 150: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", "AA"),
        "round 150: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "key"),
        "bssxh 150: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 150: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "a"),
        "round 150: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 150: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 150: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 150: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", "AA"),
        "round 150: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 150: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 150: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "a"),
        "round 150: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 150: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 150: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 150: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", "AA"),
        "round 150: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 150: the processor reads the record then stops", "key"),
        "bssxh 150: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 150: the processor reads the record then stops", "lemon"),
        "csgbq 150: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 150: the processor reads the record then stops", "a"),
        "round 150: the processor reads the record then stops",
    ),
    (
        ("round 150: the processor reads the record then stops", "zz"),
        "qntmc 150: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 150: the processor reads the record then stops", "AgentU"),
        "ruyaw 150: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 150: the processor reads the record then stops", "keyboard"),
        "bssor 150: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 150: the processor reads the record then stops", "AA"),
        "round 150: the processor reads the record then stops",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "key"),
        "bssxh 150: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "lemon"),
        "csgbq 150: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "a"),
        "round 150: a worker pulls the next task from the queue",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "zz"),
        "qntmc 150: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 150: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "keyboard"),
        "bssor 150: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 150: a worker pulls the next task from the queue", "AA"),
        "round 150: a worker pulls the next task from the queue",
    ),
    (
        ("round 150: signals travel through the network layer", "key"),
        "bssxh 150: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 150: signals travel through the network layer", "lemon"),
        "csgbq 150: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 150: signals travel through the network layer", "a"),
        "round 150: signals travel through the network layer",
    ),
    (
        ("round 150: signals travel through the network layer", "zz"),
        "qntmc 150: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 150: signals travel through the network layer", "AgentU"),
        "ruyaw 150: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 150: signals travel through the network layer", "keyboard"),
        "bssor 150: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 150: signals travel through the network layer", "AA"),
        "round 150: signals travel through the network layer",
    ),
    (
        ("round 150: the gateway routes each request by policy", "key"),
        "bssxh 150: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 150: the gateway routes each request by policy", "lemon"),
        "csgbq 150: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 150: the gateway routes each request by policy", "a"),
        "round 150: the gateway routes each request by policy",
    ),
    (
        ("round 150: the gateway routes each request by policy", "zz"),
        "qntmc 150: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 150: the gateway routes each request by policy", "AgentU"),
        "ruyaw 150: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 150: the gateway routes each request by policy", "keyboard"),
        "bssor 150: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 150: the gateway routes each request by policy", "AA"),
        "round 150: the gateway routes each request by policy",
    ),
    (("round 150: memory grows until the buffer is full", "key"), "bssxh 150: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 150: memory grows until the buffer is full", "lemon"), "csgbq 150: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 150: memory grows until the buffer is full", "a"), "round 150: memory grows until the buffer is full"),
    (("round 150: memory grows until the buffer is full", "zz"), "qntmc 150: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 150: memory grows until the buffer is full", "AgentU"),
        "ruyaw 150: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 150: memory grows until the buffer is full", "keyboard"),
        "bssor 150: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 150: memory grows until the buffer is full", "AA"), "round 150: memory grows until the buffer is full"),
    (("round 150: the cluster mirrors every packet twice", "key"), "bssxh 150: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 150: the cluster mirrors every packet twice", "lemon"),
        "csgbq 150: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 150: the cluster mirrors every packet twice", "a"), "round 150: the cluster mirrors every packet twice"),
    (("round 150: the cluster mirrors every packet twice", "zz"), "qntmc 150: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 150: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 150: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 150: the cluster mirrors every packet twice", "keyboard"),
        "bssor 150: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 150: the cluster mirrors every packet twice", "AA"), "round 150: the cluster mirrors every packet twice"),
    (
        ("round 150: ranking uses tokens learned from the corpus", "key"),
        "bssxh 150: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 150: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", "a"),
        "round 150: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 150: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 150: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 150: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", "AA"),
        "round 150: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 150: a long session ends when the candle dies", "key"),
        "bssxh 150: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 150: a long session ends when the candle dies", "lemon"),
        "csgbq 150: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 150: a long session ends when the candle dies", "a"),
        "round 150: a long session ends when the candle dies",
    ),
    (
        ("round 150: a long session ends when the candle dies", "zz"),
        "qntmc 150: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 150: a long session ends when the candle dies", "AgentU"),
        "ruyaw 150: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 150: a long session ends when the candle dies", "keyboard"),
        "bssor 150: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 150: a long session ends when the candle dies", "AA"),
        "round 150: a long session ends when the candle dies",
    ),
    (("round 150: encode the prompt then map the result", "key"), "bssxh 150: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 150: encode the prompt then map the result", "lemon"), "csgbq 150: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 150: encode the prompt then map the result", "a"), "round 150: encode the prompt then map the result"),
    (("round 150: encode the prompt then map the result", "zz"), "qntmc 150: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 150: encode the prompt then map the result", "AgentU"),
        "ruyaw 150: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 150: encode the prompt then map the result", "keyboard"),
        "bssor 150: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 150: encode the prompt then map the result", "AA"), "round 150: encode the prompt then map the result"),
    (("round 150: the kernel wakes the worker at dawn", "key"), "bssxh 150: rri iovlop ukocc xfo ambocb er neux"),
    (("round 150: the kernel wakes the worker at dawn", "lemon"), "csgbq 150: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 150: the kernel wakes the worker at dawn", "a"), "round 150: the kernel wakes the worker at dawn"),
    (("round 150: the kernel wakes the worker at dawn", "zz"), "qntmc 150: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 150: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 150: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 150: the kernel wakes the worker at dawn", "keyboard"), "bssor 150: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 150: the kernel wakes the worker at dawn", "AA"), "round 150: the kernel wakes the worker at dawn"),
    (("round 150: service latency drops after the patch", "key"), "bssxh 150: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 150: service latency drops after the patch", "lemon"), "csgbq 150: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 150: service latency drops after the patch", "a"), "round 150: service latency drops after the patch"),
    (("round 150: service latency drops after the patch", "zz"), "qntmc 150: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 150: service latency drops after the patch", "AgentU"),
        "ruyaw 150: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 150: service latency drops after the patch", "keyboard"),
        "bssor 150: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 150: service latency drops after the patch", "AA"), "round 150: service latency drops after the patch"),
    (
        ("round 150: the library caches every vector it sees", "key"),
        "bssxh 150: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 150: the library caches every vector it sees", "lemon"),
        "csgbq 150: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 150: the library caches every vector it sees", "a"), "round 150: the library caches every vector it sees"),
    (
        ("round 150: the library caches every vector it sees", "zz"),
        "qntmc 150: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 150: the library caches every vector it sees", "AgentU"),
        "ruyaw 150: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 150: the library caches every vector it sees", "keyboard"),
        "bssor 150: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 150: the library caches every vector it sees", "AA"),
        "round 150: the library caches every vector it sees",
    ),
    (("round 150: agents argue then the debate resolves", "key"), "bssxh 150: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 150: agents argue then the debate resolves", "lemon"), "csgbq 150: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 150: agents argue then the debate resolves", "a"), "round 150: agents argue then the debate resolves"),
    (("round 150: agents argue then the debate resolves", "zz"), "qntmc 150: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 150: agents argue then the debate resolves", "AgentU"),
        "ruyaw 150: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 150: agents argue then the debate resolves", "keyboard"),
        "bssor 150: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 150: agents argue then the debate resolves", "AA"), "round 150: agents argue then the debate resolves"),
    (("round 150: the filter keeps only strong matches", "key"), "bssxh 150: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 150: the filter keeps only strong matches", "lemon"), "csgbq 150: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 150: the filter keeps only strong matches", "a"), "round 150: the filter keeps only strong matches"),
    (("round 150: the filter keeps only strong matches", "zz"), "qntmc 150: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 150: the filter keeps only strong matches", "AgentU"), "ruyaw 150: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 150: the filter keeps only strong matches", "keyboard"),
        "bssor 150: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 150: the filter keeps only strong matches", "AA"), "round 150: the filter keeps only strong matches"),
    (("round 150: the model answers with a short reply", "key"), "bssxh 150: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 150: the model answers with a short reply", "lemon"), "csgbq 150: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 150: the model answers with a short reply", "a"), "round 150: the model answers with a short reply"),
    (("round 150: the model answers with a short reply", "zz"), "qntmc 150: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 150: the model answers with a short reply", "AgentU"), "ruyaw 150: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 150: the model answers with a short reply", "keyboard"),
        "bssor 150: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 150: the model answers with a short reply", "AA"), "round 150: the model answers with a short reply"),
    (
        ("round 150: the recorder stores the reasoning trace", "key"),
        "bssxh 150: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 150: the recorder stores the reasoning trace", "lemon"),
        "csgbq 150: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 150: the recorder stores the reasoning trace", "a"), "round 150: the recorder stores the reasoning trace"),
    (
        ("round 150: the recorder stores the reasoning trace", "zz"),
        "qntmc 150: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 150: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 150: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 150: the recorder stores the reasoning trace", "keyboard"),
        "bssor 150: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 150: the recorder stores the reasoning trace", "AA"),
        "round 150: the recorder stores the reasoning trace",
    ),
    (("round 150: the angel watches the processor run", "key"), "bssxh 150: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 150: the angel watches the processor run", "lemon"), "csgbq 150: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 150: the angel watches the processor run", "a"), "round 150: the angel watches the processor run"),
    (("round 150: the angel watches the processor run", "zz"), "qntmc 150: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 150: the angel watches the processor run", "AgentU"), "ruyaw 150: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 150: the angel watches the processor run", "keyboard"), "bssor 150: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 150: the angel watches the processor run", "AA"), "round 150: the angel watches the processor run"),
    (("round 150: angle of the vector decides the match", "key"), "bssxh 150: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 150: angle of the vector decides the match", "lemon"), "csgbq 150: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 150: angle of the vector decides the match", "a"), "round 150: angle of the vector decides the match"),
    (("round 150: angle of the vector decides the match", "zz"), "qntmc 150: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 150: angle of the vector decides the match", "AgentU"),
        "ruyaw 150: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 150: angle of the vector decides the match", "keyboard"),
        "bssor 150: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 150: angle of the vector decides the match", "AA"), "round 150: angle of the vector decides the match"),
    (
        ("round 150: the candle burns twice as long at night", "key"),
        "bssxh 150: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 150: the candle burns twice as long at night", "lemon"),
        "csgbq 150: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 150: the candle burns twice as long at night", "a"), "round 150: the candle burns twice as long at night"),
    (
        ("round 150: the candle burns twice as long at night", "zz"),
        "qntmc 150: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 150: the candle burns twice as long at night", "AgentU"),
        "ruyaw 150: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 150: the candle burns twice as long at night", "keyboard"),
        "bssor 150: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 150: the candle burns twice as long at night", "AA"),
        "round 150: the candle burns twice as long at night",
    ),
    (("round 150: a mirror of the universe in one line", "key"), "bssxh 150: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 150: a mirror of the universe in one line", "lemon"), "csgbq 150: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 150: a mirror of the universe in one line", "a"), "round 150: a mirror of the universe in one line"),
    (("round 150: a mirror of the universe in one line", "zz"), "qntmc 150: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 150: a mirror of the universe in one line", "AgentU"), "ruyaw 150: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 150: a mirror of the universe in one line", "keyboard"),
        "bssor 150: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 150: a mirror of the universe in one line", "AA"), "round 150: a mirror of the universe in one line"),
    (("round 150: the queue drains before the storm", "key"), "bssxh 150: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 150: the queue drains before the storm", "lemon"), "csgbq 150: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 150: the queue drains before the storm", "a"), "round 150: the queue drains before the storm"),
    (("round 150: the queue drains before the storm", "zz"), "qntmc 150: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 150: the queue drains before the storm", "AgentU"), "ruyaw 150: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 150: the queue drains before the storm", "keyboard"), "bssor 150: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 150: the queue drains before the storm", "AA"), "round 150: the queue drains before the storm"),
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
