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
    (("kitten100", "key"), "umrdil100"),
    (("kitten100", "lemon"), "vmfhry100"),
    (("kitten100", "a"), "kitten100"),
    (("kitten100", "zz"), "jhssdm100"),
    (("kitten100", "AgentU"), "koxgxh100"),
    (("kitten100", "keyboard"), "umrusn100"),
    (("kitten100", "AA"), "kitten100"),
    (("sitting100", "key"), "cmrdmlq100"),
    (("sitting100", "lemon"), "dmfhvyk100"),
    (("sitting100", "a"), "sitting100"),
    (("sitting100", "zz"), "rhsshmf100"),
    (("sitting100", "AgentU"), "soxgbhg100"),
    (("sitting100", "keyboard"), "cmruwnx100"),
    (("sitting100", "AA"), "sitting100"),
    (("agent100", "key"), "kkcxx100"),
    (("agent100", "lemon"), "lkqbg100"),
    (("agent100", "a"), "agent100"),
    (("agent100", "zz"), "zfdms100"),
    (("agent100", "AgentU"), "amiam100"),
    (("agent100", "keyboard"), "kkcoh100"),
    (("agent100", "AA"), "agent100"),
    (("angle100", "key"), "krevi100"),
    (("angle100", "lemon"), "lrszr100"),
    (("angle100", "a"), "angle100"),
    (("angle100", "zz"), "zmfkd100"),
    (("angle100", "AgentU"), "atkyx100"),
    (("angle100", "keyboard"), "krems100"),
    (("angle100", "AA"), "angle100"),
    (("universe100", "key"), "ergfipci100"),
    (("universe100", "lemon"), "frujrcwq100"),
    (("universe100", "a"), "universe100"),
    (("universe100", "zz"), "tmhudqrd100"),
    (("universe100", "AgentU"), "utmixlsk100"),
    (("universe100", "keyboard"), "ergwsrjh100"),
    (("universe100", "AA"), "universe100"),
    (("memory100", "key"), "wikyvw100"),
    (("memory100", "lemon"), "xiycej100"),
    (("memory100", "a"), "memory100"),
    (("memory100", "zz"), "ldlnqx100"),
    (("memory100", "AgentU"), "mkqbks100"),
    (("memory100", "keyboard"), "wikpfy100"),
    (("memory100", "AA"), "memory100"),
    (("stream100", "key"), "cxpoek100"),
    (("stream100", "lemon"), "dxdsnx100"),
    (("stream100", "a"), "stream100"),
    (("stream100", "zz"), "rsqdzl100"),
    (("stream100", "AgentU"), "szvrtg100"),
    (("stream100", "keyboard"), "cxpfom100"),
    (("stream100", "AA"), "stream100"),
    (("context100", "key"), "msldivd100"),
    (("context100", "lemon"), "nszhrix100"),
    (("context100", "a"), "context100"),
    (("context100", "zz"), "bnmsdws100"),
    (("context100", "AgentU"), "curgxrt100"),
    (("context100", "keyboard"), "mslusxk100"),
    (("context100", "AA"), "context100"),
    (("knowledge100", "key"), "urmgpcnkc100"),
    (("knowledge100", "lemon"), "vrakyphss100"),
    (("knowledge100", "a"), "knowledge100"),
    (("knowledge100", "zz"), "jmnvkdcfd100"),
    (("knowledge100", "AgentU"), "ktsjeydmi100"),
    (("knowledge100", "keyboard"), "urmxzeujo100"),
    (("knowledge100", "AA"), "knowledge100"),
    (("vector100", "key"), "fiadsp100"),
    (("vector100", "lemon"), "giohbc100"),
    (("vector100", "a"), "vector100"),
    (("vector100", "zz"), "udbsnq100"),
    (("vector100", "AgentU"), "vkgghl100"),
    (("vector100", "keyboard"), "fiaucr100"),
    (("vector100", "AA"), "vector100"),
    (("processor100", "key"), "zvmmiqcsp100"),
    (("processor100", "lemon"), "avaqrdwaf100"),
    (("processor100", "a"), "processor100"),
    (("processor100", "zz"), "oqnbdrrnq100"),
    (("processor100", "AgentU"), "pxspxmsuv100"),
    (("processor100", "keyboard"), "zvmdssjrb100"),
    (("processor100", "AA"), "processor100"),
    (("reasoning100", "key"), "biycslsre100"),
    (("reasoning100", "lemon"), "cimgbymzu100"),
    (("reasoning100", "a"), "reasoning100"),
    (("reasoning100", "zz"), "qdzrnmhmf100"),
    (("reasoning100", "AgentU"), "rkefhhitk100"),
    (("reasoning100", "keyboard"), "biytcnzqq100"),
    (("reasoning100", "AA"), "reasoning100"),
    (("machine100", "key"), "wearmlo100"),
    (("machine100", "lemon"), "xeovvyi100"),
    (("machine100", "a"), "machine100"),
    (("machine100", "zz"), "lzbghmd100"),
    (("machine100", "AgentU"), "mggubhe100"),
    (("machine100", "keyboard"), "weaiwnv100"),
    (("machine100", "AA"), "machine100"),
    (("learning100", "key"), "viybrgxk100"),
    (("learning100", "lemon"), "wimfatrs100"),
    (("learning100", "a"), "learning100"),
    (("learning100", "zz"), "kdzqmhmf100"),
    (("learning100", "AgentU"), "lkeegcnm100"),
    (("learning100", "keyboard"), "viysbiej100"),
    (("learning100", "AA"), "learning100"),
    (("model100", "key"), "wsbop100"),
    (("model100", "lemon"), "xspsy100"),
    (("model100", "a"), "model100"),
    (("model100", "zz"), "lncdk100"),
    (("model100", "AgentU"), "muhre100"),
    (("model100", "keyboard"), "wsbfz100"),
    (("model100", "AA"), "model100"),
    (("token100", "key"), "dsior100"),
    (("token100", "lemon"), "eswsa100"),
    (("token100", "a"), "token100"),
    (("token100", "zz"), "snjdm100"),
    (("token100", "AgentU"), "tuorg100"),
    (("token100", "keyboard"), "dsifb100"),
    (("token100", "AA"), "token100"),
    (("prompt100", "key"), "zvmwtr100"),
    (("prompt100", "lemon"), "avaace100"),
    (("prompt100", "a"), "prompt100"),
    (("prompt100", "zz"), "oqnlos100"),
    (("prompt100", "AgentU"), "pxszin100"),
    (("prompt100", "keyboard"), "zvmndt100"),
    (("prompt100", "AA"), "prompt100"),
    (("session100", "key"), "ciqcmmx100"),
    (("session100", "lemon"), "diegvzr100"),
    (("session100", "a"), "session100"),
    (("session100", "zz"), "rdrrhnm100"),
    (("session100", "AgentU"), "skwfbin100"),
    (("session100", "keyboard"), "ciqtwoe100"),
    (("session100", "AA"), "session100"),
    (("library100", "key"), "vmzbepi100"),
    (("library100", "lemon"), "wmnfncc100"),
    (("library100", "a"), "library100"),
    (("library100", "zz"), "khaqzqx100"),
    (("library100", "AgentU"), "lofetly100"),
    (("library100", "keyboard"), "vmzsorp100"),
    (("library100", "AA"), "library100"),
    (("service100", "key"), "cipfmao100"),
    (("service100", "lemon"), "didjvni100"),
    (("service100", "a"), "service100"),
    (("service100", "zz"), "rdquhbd100"),
    (("service100", "AgentU"), "skvibwe100"),
    (("service100", "keyboard"), "cipwwcv100"),
    (("service100", "AA"), "service100"),
    (("gateway100", "key"), "qeroayi100"),
    (("gateway100", "lemon"), "refsjlc100"),
    (("gateway100", "a"), "gateway100"),
    (("gateway100", "zz"), "fzsdvzx100"),
    (("gateway100", "AgentU"), "ggxrpuy100"),
    (("gateway100", "keyboard"), "qerfkap100"),
    (("gateway100", "AA"), "gateway100"),
    (("storage100", "key"), "cxmbeeo100"),
    (("storage100", "lemon"), "dxafnri100"),
    (("storage100", "a"), "storage100"),
    (("storage100", "zz"), "rsnqzfd100"),
    (("storage100", "AgentU"), "szsetae100"),
    (("storage100", "keyboard"), "cxmsogv100"),
    (("storage100", "AA"), "storage100"),
    (("network100", "key"), "xirgspu100"),
    (("network100", "lemon"), "yifkbco100"),
    (("network100", "a"), "network100"),
    (("network100", "zz"), "mdsvnqj100"),
    (("network100", "AgentU"), "nkxjhlk100"),
    (("network100", "keyboard"), "xirxcrb100"),
    (("network100", "AA"), "network100"),
    (("latency100", "key"), "verorai100"),
    (("latency100", "lemon"), "wefsanc100"),
    (("latency100", "a"), "latency100"),
    (("latency100", "zz"), "kzsdmbx100"),
    (("latency100", "AgentU"), "lgxrgwy100"),
    (("latency100", "keyboard"), "verfbcp100"),
    (("latency100", "AA"), "latency100"),
    (("buffer100", "key"), "lydpip100"),
    (("buffer100", "lemon"), "myrtrc100"),
    (("buffer100", "a"), "buffer100"),
    (("buffer100", "zz"), "ateedq100"),
    (("buffer100", "AgentU"), "bajsxl100"),
    (("buffer100", "keyboard"), "lydgsr100"),
    (("buffer100", "AA"), "buffer100"),
    (("queue100", "key"), "aycei100"),
    (("queue100", "lemon"), "byqir100"),
    (("queue100", "a"), "queue100"),
    (("queue100", "zz"), "ptdtd100"),
    (("queue100", "AgentU"), "qaihx100"),
    (("queue100", "keyboard"), "aycvs100"),
    (("queue100", "AA"), "queue100"),
    (("worker100", "key"), "gspuip100"),
    (("worker100", "lemon"), "hsdyrc100"),
    (("worker100", "a"), "worker100"),
    (("worker100", "zz"), "vnqjdq100"),
    (("worker100", "AgentU"), "wuvxxl100"),
    (("worker100", "keyboard"), "gsplsr100"),
    (("worker100", "AA"), "worker100"),
    (("kernel100", "key"), "uipxij100"),
    (("kernel100", "lemon"), "vidbrw100"),
    (("kernel100", "a"), "kernel100"),
    (("kernel100", "zz"), "jdqmdk100"),
    (("kernel100", "AgentU"), "kkvaxf100"),
    (("kernel100", "keyboard"), "uiposl100"),
    (("kernel100", "AA"), "kernel100"),
    (("signal100", "key"), "cmexej100"),
    (("signal100", "lemon"), "dmsbnw100"),
    (("signal100", "a"), "signal100"),
    (("signal100", "zz"), "rhfmzk100"),
    (("signal100", "AgentU"), "sokatf100"),
    (("signal100", "keyboard"), "cmeool100"),
    (("signal100", "AA"), "signal100"),
    (("packet100", "key"), "zeauir100"),
    (("packet100", "lemon"), "aeoyre100"),
    (("packet100", "a"), "packet100"),
    (("packet100", "zz"), "ozbjds100"),
    (("packet100", "AgentU"), "pggxxn100"),
    (("packet100", "keyboard"), "zealst100"),
    (("packet100", "AA"), "packet100"),
    (("router100", "key"), "bssdip100"),
    (("router100", "lemon"), "csghrc100"),
    (("router100", "a"), "router100"),
    (("router100", "zz"), "qntsdq100"),
    (("router100", "AgentU"), "ruygxl100"),
    (("router100", "keyboard"), "bssusr100"),
    (("router100", "AA"), "router100"),
    (("cluster100", "key"), "mpscxcb100"),
    (("cluster100", "lemon"), "npgggpv100"),
    (("cluster100", "a"), "cluster100"),
    (("cluster100", "zz"), "bktrsdq100"),
    (("cluster100", "AgentU"), "cryfmyr100"),
    (("cluster100", "keyboard"), "mpsthei100"),
    (("cluster100", "AA"), "cluster100"),
    (("mirror100", "key"), "wmpbsp100"),
    (("mirror100", "lemon"), "xmdfbc100"),
    (("mirror100", "a"), "mirror100"),
    (("mirror100", "zz"), "lhqqnq100"),
    (("mirror100", "AgentU"), "movehl100"),
    (("mirror100", "keyboard"), "wmpscr100"),
    (("mirror100", "AA"), "mirror100"),
    (("filter100", "key"), "pmjdip100"),
    (("filter100", "lemon"), "qmxhrc100"),
    (("filter100", "a"), "filter100"),
    (("filter100", "zz"), "ehksdq100"),
    (("filter100", "AgentU"), "fopgxl100"),
    (("filter100", "keyboard"), "pmjusr100"),
    (("filter100", "AA"), "filter100"),
    (("ranking100", "key"), "belumlq100"),
    (("ranking100", "lemon"), "cezyvyk100"),
    (("ranking100", "a"), "ranking100"),
    (("ranking100", "zz"), "qzmjhmf100"),
    (("ranking100", "AgentU"), "rgrxbhg100"),
    (("ranking100", "keyboard"), "bellwnx100"),
    (("ranking100", "AA"), "ranking100"),
    (("encoding100", "key"), "orayhgxk100"),
    (("encoding100", "lemon"), "procqtrs100"),
    (("encoding100", "a"), "encoding100"),
    (("encoding100", "zz"), "dmbnchmf100"),
    (("encoding100", "AgentU"), "etgbwcnm100"),
    (("encoding100", "keyboard"), "orapriej100"),
    (("encoding100", "AA"), "encoding100"),
    (("mapping100", "key"), "wenzmlq100"),
    (("mapping100", "lemon"), "xebdvyk100"),
    (("mapping100", "a"), "mapping100"),
    (("mapping100", "zz"), "lzoohmf100"),
    (("mapping100", "AgentU"), "mgtcbhg100"),
    (("mapping100", "keyboard"), "wenqwnx100"),
    (("mapping100", "AA"), "mapping100"),
    (("record100", "key"), "biayvb100"),
    (("record100", "lemon"), "cioceo100"),
    (("record100", "a"), "record100"),
    (("record100", "zz"), "qdbnqc100"),
    (("record100", "AgentU"), "rkgbkx100"),
    (("record100", "keyboard"), "biapfd100"),
    (("record100", "AA"), "record100"),
    (("candle100", "key"), "melnpc100"),
    (("candle100", "lemon"), "nezryp100"),
    (("candle100", "a"), "candle100"),
    (("candle100", "zz"), "bzmckd100"),
    (("candle100", "AgentU"), "cgrqey100"),
    (("candle100", "keyboard"), "meleze100"),
    (("candle100", "AA"), "candle100"),
    (("thread100", "key"), "dlpoeb100"),
    (("thread100", "lemon"), "eldsno100"),
    (("thread100", "a"), "thread100"),
    (("thread100", "zz"), "sgqdzc100"),
    (("thread100", "AgentU"), "tnvrtx100"),
    (("thread100", "keyboard"), "dlpfod100"),
    (("thread100", "AA"), "thread100"),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 100: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 100: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "a"),
        "round 100: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 100: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 100: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 100: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", "AA"),
        "round 100: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "key"),
        "bssxh 100: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 100: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "a"),
        "round 100: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 100: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 100: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 100: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", "AA"),
        "round 100: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 100: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 100: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "a"),
        "round 100: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 100: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 100: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 100: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", "AA"),
        "round 100: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 100: the processor reads the record then stops", "key"),
        "bssxh 100: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 100: the processor reads the record then stops", "lemon"),
        "csgbq 100: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 100: the processor reads the record then stops", "a"),
        "round 100: the processor reads the record then stops",
    ),
    (
        ("round 100: the processor reads the record then stops", "zz"),
        "qntmc 100: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 100: the processor reads the record then stops", "AgentU"),
        "ruyaw 100: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 100: the processor reads the record then stops", "keyboard"),
        "bssor 100: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 100: the processor reads the record then stops", "AA"),
        "round 100: the processor reads the record then stops",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "key"),
        "bssxh 100: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "lemon"),
        "csgbq 100: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "a"),
        "round 100: a worker pulls the next task from the queue",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "zz"),
        "qntmc 100: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 100: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "keyboard"),
        "bssor 100: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 100: a worker pulls the next task from the queue", "AA"),
        "round 100: a worker pulls the next task from the queue",
    ),
    (
        ("round 100: signals travel through the network layer", "key"),
        "bssxh 100: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 100: signals travel through the network layer", "lemon"),
        "csgbq 100: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 100: signals travel through the network layer", "a"),
        "round 100: signals travel through the network layer",
    ),
    (
        ("round 100: signals travel through the network layer", "zz"),
        "qntmc 100: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 100: signals travel through the network layer", "AgentU"),
        "ruyaw 100: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 100: signals travel through the network layer", "keyboard"),
        "bssor 100: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 100: signals travel through the network layer", "AA"),
        "round 100: signals travel through the network layer",
    ),
    (
        ("round 100: the gateway routes each request by policy", "key"),
        "bssxh 100: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 100: the gateway routes each request by policy", "lemon"),
        "csgbq 100: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 100: the gateway routes each request by policy", "a"),
        "round 100: the gateway routes each request by policy",
    ),
    (
        ("round 100: the gateway routes each request by policy", "zz"),
        "qntmc 100: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 100: the gateway routes each request by policy", "AgentU"),
        "ruyaw 100: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 100: the gateway routes each request by policy", "keyboard"),
        "bssor 100: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 100: the gateway routes each request by policy", "AA"),
        "round 100: the gateway routes each request by policy",
    ),
    (("round 100: memory grows until the buffer is full", "key"), "bssxh 100: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 100: memory grows until the buffer is full", "lemon"), "csgbq 100: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 100: memory grows until the buffer is full", "a"), "round 100: memory grows until the buffer is full"),
    (("round 100: memory grows until the buffer is full", "zz"), "qntmc 100: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 100: memory grows until the buffer is full", "AgentU"),
        "ruyaw 100: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 100: memory grows until the buffer is full", "keyboard"),
        "bssor 100: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 100: memory grows until the buffer is full", "AA"), "round 100: memory grows until the buffer is full"),
    (("round 100: the cluster mirrors every packet twice", "key"), "bssxh 100: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 100: the cluster mirrors every packet twice", "lemon"),
        "csgbq 100: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 100: the cluster mirrors every packet twice", "a"), "round 100: the cluster mirrors every packet twice"),
    (("round 100: the cluster mirrors every packet twice", "zz"), "qntmc 100: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 100: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 100: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 100: the cluster mirrors every packet twice", "keyboard"),
        "bssor 100: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 100: the cluster mirrors every packet twice", "AA"), "round 100: the cluster mirrors every packet twice"),
    (
        ("round 100: ranking uses tokens learned from the corpus", "key"),
        "bssxh 100: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 100: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", "a"),
        "round 100: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 100: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 100: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 100: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", "AA"),
        "round 100: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 100: a long session ends when the candle dies", "key"),
        "bssxh 100: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 100: a long session ends when the candle dies", "lemon"),
        "csgbq 100: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 100: a long session ends when the candle dies", "a"),
        "round 100: a long session ends when the candle dies",
    ),
    (
        ("round 100: a long session ends when the candle dies", "zz"),
        "qntmc 100: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 100: a long session ends when the candle dies", "AgentU"),
        "ruyaw 100: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 100: a long session ends when the candle dies", "keyboard"),
        "bssor 100: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 100: a long session ends when the candle dies", "AA"),
        "round 100: a long session ends when the candle dies",
    ),
    (("round 100: encode the prompt then map the result", "key"), "bssxh 100: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 100: encode the prompt then map the result", "lemon"), "csgbq 100: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 100: encode the prompt then map the result", "a"), "round 100: encode the prompt then map the result"),
    (("round 100: encode the prompt then map the result", "zz"), "qntmc 100: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 100: encode the prompt then map the result", "AgentU"),
        "ruyaw 100: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 100: encode the prompt then map the result", "keyboard"),
        "bssor 100: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 100: encode the prompt then map the result", "AA"), "round 100: encode the prompt then map the result"),
    (("round 100: the kernel wakes the worker at dawn", "key"), "bssxh 100: rri iovlop ukocc xfo ambocb er neux"),
    (("round 100: the kernel wakes the worker at dawn", "lemon"), "csgbq 100: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 100: the kernel wakes the worker at dawn", "a"), "round 100: the kernel wakes the worker at dawn"),
    (("round 100: the kernel wakes the worker at dawn", "zz"), "qntmc 100: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 100: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 100: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 100: the kernel wakes the worker at dawn", "keyboard"), "bssor 100: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 100: the kernel wakes the worker at dawn", "AA"), "round 100: the kernel wakes the worker at dawn"),
    (("round 100: service latency drops after the patch", "key"), "bssxh 100: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 100: service latency drops after the patch", "lemon"), "csgbq 100: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 100: service latency drops after the patch", "a"), "round 100: service latency drops after the patch"),
    (("round 100: service latency drops after the patch", "zz"), "qntmc 100: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 100: service latency drops after the patch", "AgentU"),
        "ruyaw 100: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 100: service latency drops after the patch", "keyboard"),
        "bssor 100: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 100: service latency drops after the patch", "AA"), "round 100: service latency drops after the patch"),
    (
        ("round 100: the library caches every vector it sees", "key"),
        "bssxh 100: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 100: the library caches every vector it sees", "lemon"),
        "csgbq 100: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 100: the library caches every vector it sees", "a"), "round 100: the library caches every vector it sees"),
    (
        ("round 100: the library caches every vector it sees", "zz"),
        "qntmc 100: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 100: the library caches every vector it sees", "AgentU"),
        "ruyaw 100: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 100: the library caches every vector it sees", "keyboard"),
        "bssor 100: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 100: the library caches every vector it sees", "AA"),
        "round 100: the library caches every vector it sees",
    ),
    (("round 100: agents argue then the debate resolves", "key"), "bssxh 100: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 100: agents argue then the debate resolves", "lemon"), "csgbq 100: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 100: agents argue then the debate resolves", "a"), "round 100: agents argue then the debate resolves"),
    (("round 100: agents argue then the debate resolves", "zz"), "qntmc 100: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 100: agents argue then the debate resolves", "AgentU"),
        "ruyaw 100: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 100: agents argue then the debate resolves", "keyboard"),
        "bssor 100: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 100: agents argue then the debate resolves", "AA"), "round 100: agents argue then the debate resolves"),
    (("round 100: the filter keeps only strong matches", "key"), "bssxh 100: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 100: the filter keeps only strong matches", "lemon"), "csgbq 100: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 100: the filter keeps only strong matches", "a"), "round 100: the filter keeps only strong matches"),
    (("round 100: the filter keeps only strong matches", "zz"), "qntmc 100: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 100: the filter keeps only strong matches", "AgentU"), "ruyaw 100: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 100: the filter keeps only strong matches", "keyboard"),
        "bssor 100: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 100: the filter keeps only strong matches", "AA"), "round 100: the filter keeps only strong matches"),
    (("round 100: the model answers with a short reply", "key"), "bssxh 100: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 100: the model answers with a short reply", "lemon"), "csgbq 100: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 100: the model answers with a short reply", "a"), "round 100: the model answers with a short reply"),
    (("round 100: the model answers with a short reply", "zz"), "qntmc 100: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 100: the model answers with a short reply", "AgentU"), "ruyaw 100: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 100: the model answers with a short reply", "keyboard"),
        "bssor 100: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 100: the model answers with a short reply", "AA"), "round 100: the model answers with a short reply"),
    (
        ("round 100: the recorder stores the reasoning trace", "key"),
        "bssxh 100: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 100: the recorder stores the reasoning trace", "lemon"),
        "csgbq 100: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 100: the recorder stores the reasoning trace", "a"), "round 100: the recorder stores the reasoning trace"),
    (
        ("round 100: the recorder stores the reasoning trace", "zz"),
        "qntmc 100: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 100: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 100: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 100: the recorder stores the reasoning trace", "keyboard"),
        "bssor 100: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 100: the recorder stores the reasoning trace", "AA"),
        "round 100: the recorder stores the reasoning trace",
    ),
    (("round 100: the angel watches the processor run", "key"), "bssxh 100: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 100: the angel watches the processor run", "lemon"), "csgbq 100: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 100: the angel watches the processor run", "a"), "round 100: the angel watches the processor run"),
    (("round 100: the angel watches the processor run", "zz"), "qntmc 100: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 100: the angel watches the processor run", "AgentU"), "ruyaw 100: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 100: the angel watches the processor run", "keyboard"), "bssor 100: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 100: the angel watches the processor run", "AA"), "round 100: the angel watches the processor run"),
    (("round 100: angle of the vector decides the match", "key"), "bssxh 100: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 100: angle of the vector decides the match", "lemon"), "csgbq 100: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 100: angle of the vector decides the match", "a"), "round 100: angle of the vector decides the match"),
    (("round 100: angle of the vector decides the match", "zz"), "qntmc 100: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 100: angle of the vector decides the match", "AgentU"),
        "ruyaw 100: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 100: angle of the vector decides the match", "keyboard"),
        "bssor 100: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 100: angle of the vector decides the match", "AA"), "round 100: angle of the vector decides the match"),
    (
        ("round 100: the candle burns twice as long at night", "key"),
        "bssxh 100: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 100: the candle burns twice as long at night", "lemon"),
        "csgbq 100: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 100: the candle burns twice as long at night", "a"), "round 100: the candle burns twice as long at night"),
    (
        ("round 100: the candle burns twice as long at night", "zz"),
        "qntmc 100: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 100: the candle burns twice as long at night", "AgentU"),
        "ruyaw 100: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 100: the candle burns twice as long at night", "keyboard"),
        "bssor 100: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 100: the candle burns twice as long at night", "AA"),
        "round 100: the candle burns twice as long at night",
    ),
    (("round 100: a mirror of the universe in one line", "key"), "bssxh 100: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 100: a mirror of the universe in one line", "lemon"), "csgbq 100: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 100: a mirror of the universe in one line", "a"), "round 100: a mirror of the universe in one line"),
    (("round 100: a mirror of the universe in one line", "zz"), "qntmc 100: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 100: a mirror of the universe in one line", "AgentU"), "ruyaw 100: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 100: a mirror of the universe in one line", "keyboard"),
        "bssor 100: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 100: a mirror of the universe in one line", "AA"), "round 100: a mirror of the universe in one line"),
    (("round 100: the queue drains before the storm", "key"), "bssxh 100: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 100: the queue drains before the storm", "lemon"), "csgbq 100: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 100: the queue drains before the storm", "a"), "round 100: the queue drains before the storm"),
    (("round 100: the queue drains before the storm", "zz"), "qntmc 100: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 100: the queue drains before the storm", "AgentU"), "ruyaw 100: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 100: the queue drains before the storm", "keyboard"), "bssor 100: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 100: the queue drains before the storm", "AA"), "round 100: the queue drains before the storm"),
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
