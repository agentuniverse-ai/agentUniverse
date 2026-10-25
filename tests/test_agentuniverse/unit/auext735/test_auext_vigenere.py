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
    (("kitten735", "key"), "umrdil735"),
    (("kitten735", "lemon"), "vmfhry735"),
    (("kitten735", "a"), "kitten735"),
    (("kitten735", "zz"), "jhssdm735"),
    (("kitten735", "AgentU"), "koxgxh735"),
    (("kitten735", "keyboard"), "umrusn735"),
    (("kitten735", "AA"), "kitten735"),
    (("sitting735", "key"), "cmrdmlq735"),
    (("sitting735", "lemon"), "dmfhvyk735"),
    (("sitting735", "a"), "sitting735"),
    (("sitting735", "zz"), "rhsshmf735"),
    (("sitting735", "AgentU"), "soxgbhg735"),
    (("sitting735", "keyboard"), "cmruwnx735"),
    (("sitting735", "AA"), "sitting735"),
    (("agent735", "key"), "kkcxx735"),
    (("agent735", "lemon"), "lkqbg735"),
    (("agent735", "a"), "agent735"),
    (("agent735", "zz"), "zfdms735"),
    (("agent735", "AgentU"), "amiam735"),
    (("agent735", "keyboard"), "kkcoh735"),
    (("agent735", "AA"), "agent735"),
    (("angle735", "key"), "krevi735"),
    (("angle735", "lemon"), "lrszr735"),
    (("angle735", "a"), "angle735"),
    (("angle735", "zz"), "zmfkd735"),
    (("angle735", "AgentU"), "atkyx735"),
    (("angle735", "keyboard"), "krems735"),
    (("angle735", "AA"), "angle735"),
    (("universe735", "key"), "ergfipci735"),
    (("universe735", "lemon"), "frujrcwq735"),
    (("universe735", "a"), "universe735"),
    (("universe735", "zz"), "tmhudqrd735"),
    (("universe735", "AgentU"), "utmixlsk735"),
    (("universe735", "keyboard"), "ergwsrjh735"),
    (("universe735", "AA"), "universe735"),
    (("memory735", "key"), "wikyvw735"),
    (("memory735", "lemon"), "xiycej735"),
    (("memory735", "a"), "memory735"),
    (("memory735", "zz"), "ldlnqx735"),
    (("memory735", "AgentU"), "mkqbks735"),
    (("memory735", "keyboard"), "wikpfy735"),
    (("memory735", "AA"), "memory735"),
    (("stream735", "key"), "cxpoek735"),
    (("stream735", "lemon"), "dxdsnx735"),
    (("stream735", "a"), "stream735"),
    (("stream735", "zz"), "rsqdzl735"),
    (("stream735", "AgentU"), "szvrtg735"),
    (("stream735", "keyboard"), "cxpfom735"),
    (("stream735", "AA"), "stream735"),
    (("context735", "key"), "msldivd735"),
    (("context735", "lemon"), "nszhrix735"),
    (("context735", "a"), "context735"),
    (("context735", "zz"), "bnmsdws735"),
    (("context735", "AgentU"), "curgxrt735"),
    (("context735", "keyboard"), "mslusxk735"),
    (("context735", "AA"), "context735"),
    (("knowledge735", "key"), "urmgpcnkc735"),
    (("knowledge735", "lemon"), "vrakyphss735"),
    (("knowledge735", "a"), "knowledge735"),
    (("knowledge735", "zz"), "jmnvkdcfd735"),
    (("knowledge735", "AgentU"), "ktsjeydmi735"),
    (("knowledge735", "keyboard"), "urmxzeujo735"),
    (("knowledge735", "AA"), "knowledge735"),
    (("vector735", "key"), "fiadsp735"),
    (("vector735", "lemon"), "giohbc735"),
    (("vector735", "a"), "vector735"),
    (("vector735", "zz"), "udbsnq735"),
    (("vector735", "AgentU"), "vkgghl735"),
    (("vector735", "keyboard"), "fiaucr735"),
    (("vector735", "AA"), "vector735"),
    (("processor735", "key"), "zvmmiqcsp735"),
    (("processor735", "lemon"), "avaqrdwaf735"),
    (("processor735", "a"), "processor735"),
    (("processor735", "zz"), "oqnbdrrnq735"),
    (("processor735", "AgentU"), "pxspxmsuv735"),
    (("processor735", "keyboard"), "zvmdssjrb735"),
    (("processor735", "AA"), "processor735"),
    (("reasoning735", "key"), "biycslsre735"),
    (("reasoning735", "lemon"), "cimgbymzu735"),
    (("reasoning735", "a"), "reasoning735"),
    (("reasoning735", "zz"), "qdzrnmhmf735"),
    (("reasoning735", "AgentU"), "rkefhhitk735"),
    (("reasoning735", "keyboard"), "biytcnzqq735"),
    (("reasoning735", "AA"), "reasoning735"),
    (("machine735", "key"), "wearmlo735"),
    (("machine735", "lemon"), "xeovvyi735"),
    (("machine735", "a"), "machine735"),
    (("machine735", "zz"), "lzbghmd735"),
    (("machine735", "AgentU"), "mggubhe735"),
    (("machine735", "keyboard"), "weaiwnv735"),
    (("machine735", "AA"), "machine735"),
    (("learning735", "key"), "viybrgxk735"),
    (("learning735", "lemon"), "wimfatrs735"),
    (("learning735", "a"), "learning735"),
    (("learning735", "zz"), "kdzqmhmf735"),
    (("learning735", "AgentU"), "lkeegcnm735"),
    (("learning735", "keyboard"), "viysbiej735"),
    (("learning735", "AA"), "learning735"),
    (("model735", "key"), "wsbop735"),
    (("model735", "lemon"), "xspsy735"),
    (("model735", "a"), "model735"),
    (("model735", "zz"), "lncdk735"),
    (("model735", "AgentU"), "muhre735"),
    (("model735", "keyboard"), "wsbfz735"),
    (("model735", "AA"), "model735"),
    (("token735", "key"), "dsior735"),
    (("token735", "lemon"), "eswsa735"),
    (("token735", "a"), "token735"),
    (("token735", "zz"), "snjdm735"),
    (("token735", "AgentU"), "tuorg735"),
    (("token735", "keyboard"), "dsifb735"),
    (("token735", "AA"), "token735"),
    (("prompt735", "key"), "zvmwtr735"),
    (("prompt735", "lemon"), "avaace735"),
    (("prompt735", "a"), "prompt735"),
    (("prompt735", "zz"), "oqnlos735"),
    (("prompt735", "AgentU"), "pxszin735"),
    (("prompt735", "keyboard"), "zvmndt735"),
    (("prompt735", "AA"), "prompt735"),
    (("session735", "key"), "ciqcmmx735"),
    (("session735", "lemon"), "diegvzr735"),
    (("session735", "a"), "session735"),
    (("session735", "zz"), "rdrrhnm735"),
    (("session735", "AgentU"), "skwfbin735"),
    (("session735", "keyboard"), "ciqtwoe735"),
    (("session735", "AA"), "session735"),
    (("library735", "key"), "vmzbepi735"),
    (("library735", "lemon"), "wmnfncc735"),
    (("library735", "a"), "library735"),
    (("library735", "zz"), "khaqzqx735"),
    (("library735", "AgentU"), "lofetly735"),
    (("library735", "keyboard"), "vmzsorp735"),
    (("library735", "AA"), "library735"),
    (("service735", "key"), "cipfmao735"),
    (("service735", "lemon"), "didjvni735"),
    (("service735", "a"), "service735"),
    (("service735", "zz"), "rdquhbd735"),
    (("service735", "AgentU"), "skvibwe735"),
    (("service735", "keyboard"), "cipwwcv735"),
    (("service735", "AA"), "service735"),
    (("gateway735", "key"), "qeroayi735"),
    (("gateway735", "lemon"), "refsjlc735"),
    (("gateway735", "a"), "gateway735"),
    (("gateway735", "zz"), "fzsdvzx735"),
    (("gateway735", "AgentU"), "ggxrpuy735"),
    (("gateway735", "keyboard"), "qerfkap735"),
    (("gateway735", "AA"), "gateway735"),
    (("storage735", "key"), "cxmbeeo735"),
    (("storage735", "lemon"), "dxafnri735"),
    (("storage735", "a"), "storage735"),
    (("storage735", "zz"), "rsnqzfd735"),
    (("storage735", "AgentU"), "szsetae735"),
    (("storage735", "keyboard"), "cxmsogv735"),
    (("storage735", "AA"), "storage735"),
    (("network735", "key"), "xirgspu735"),
    (("network735", "lemon"), "yifkbco735"),
    (("network735", "a"), "network735"),
    (("network735", "zz"), "mdsvnqj735"),
    (("network735", "AgentU"), "nkxjhlk735"),
    (("network735", "keyboard"), "xirxcrb735"),
    (("network735", "AA"), "network735"),
    (("latency735", "key"), "verorai735"),
    (("latency735", "lemon"), "wefsanc735"),
    (("latency735", "a"), "latency735"),
    (("latency735", "zz"), "kzsdmbx735"),
    (("latency735", "AgentU"), "lgxrgwy735"),
    (("latency735", "keyboard"), "verfbcp735"),
    (("latency735", "AA"), "latency735"),
    (("buffer735", "key"), "lydpip735"),
    (("buffer735", "lemon"), "myrtrc735"),
    (("buffer735", "a"), "buffer735"),
    (("buffer735", "zz"), "ateedq735"),
    (("buffer735", "AgentU"), "bajsxl735"),
    (("buffer735", "keyboard"), "lydgsr735"),
    (("buffer735", "AA"), "buffer735"),
    (("queue735", "key"), "aycei735"),
    (("queue735", "lemon"), "byqir735"),
    (("queue735", "a"), "queue735"),
    (("queue735", "zz"), "ptdtd735"),
    (("queue735", "AgentU"), "qaihx735"),
    (("queue735", "keyboard"), "aycvs735"),
    (("queue735", "AA"), "queue735"),
    (("worker735", "key"), "gspuip735"),
    (("worker735", "lemon"), "hsdyrc735"),
    (("worker735", "a"), "worker735"),
    (("worker735", "zz"), "vnqjdq735"),
    (("worker735", "AgentU"), "wuvxxl735"),
    (("worker735", "keyboard"), "gsplsr735"),
    (("worker735", "AA"), "worker735"),
    (("kernel735", "key"), "uipxij735"),
    (("kernel735", "lemon"), "vidbrw735"),
    (("kernel735", "a"), "kernel735"),
    (("kernel735", "zz"), "jdqmdk735"),
    (("kernel735", "AgentU"), "kkvaxf735"),
    (("kernel735", "keyboard"), "uiposl735"),
    (("kernel735", "AA"), "kernel735"),
    (("signal735", "key"), "cmexej735"),
    (("signal735", "lemon"), "dmsbnw735"),
    (("signal735", "a"), "signal735"),
    (("signal735", "zz"), "rhfmzk735"),
    (("signal735", "AgentU"), "sokatf735"),
    (("signal735", "keyboard"), "cmeool735"),
    (("signal735", "AA"), "signal735"),
    (("packet735", "key"), "zeauir735"),
    (("packet735", "lemon"), "aeoyre735"),
    (("packet735", "a"), "packet735"),
    (("packet735", "zz"), "ozbjds735"),
    (("packet735", "AgentU"), "pggxxn735"),
    (("packet735", "keyboard"), "zealst735"),
    (("packet735", "AA"), "packet735"),
    (("router735", "key"), "bssdip735"),
    (("router735", "lemon"), "csghrc735"),
    (("router735", "a"), "router735"),
    (("router735", "zz"), "qntsdq735"),
    (("router735", "AgentU"), "ruygxl735"),
    (("router735", "keyboard"), "bssusr735"),
    (("router735", "AA"), "router735"),
    (("cluster735", "key"), "mpscxcb735"),
    (("cluster735", "lemon"), "npgggpv735"),
    (("cluster735", "a"), "cluster735"),
    (("cluster735", "zz"), "bktrsdq735"),
    (("cluster735", "AgentU"), "cryfmyr735"),
    (("cluster735", "keyboard"), "mpsthei735"),
    (("cluster735", "AA"), "cluster735"),
    (("mirror735", "key"), "wmpbsp735"),
    (("mirror735", "lemon"), "xmdfbc735"),
    (("mirror735", "a"), "mirror735"),
    (("mirror735", "zz"), "lhqqnq735"),
    (("mirror735", "AgentU"), "movehl735"),
    (("mirror735", "keyboard"), "wmpscr735"),
    (("mirror735", "AA"), "mirror735"),
    (("filter735", "key"), "pmjdip735"),
    (("filter735", "lemon"), "qmxhrc735"),
    (("filter735", "a"), "filter735"),
    (("filter735", "zz"), "ehksdq735"),
    (("filter735", "AgentU"), "fopgxl735"),
    (("filter735", "keyboard"), "pmjusr735"),
    (("filter735", "AA"), "filter735"),
    (("ranking735", "key"), "belumlq735"),
    (("ranking735", "lemon"), "cezyvyk735"),
    (("ranking735", "a"), "ranking735"),
    (("ranking735", "zz"), "qzmjhmf735"),
    (("ranking735", "AgentU"), "rgrxbhg735"),
    (("ranking735", "keyboard"), "bellwnx735"),
    (("ranking735", "AA"), "ranking735"),
    (("encoding735", "key"), "orayhgxk735"),
    (("encoding735", "lemon"), "procqtrs735"),
    (("encoding735", "a"), "encoding735"),
    (("encoding735", "zz"), "dmbnchmf735"),
    (("encoding735", "AgentU"), "etgbwcnm735"),
    (("encoding735", "keyboard"), "orapriej735"),
    (("encoding735", "AA"), "encoding735"),
    (("mapping735", "key"), "wenzmlq735"),
    (("mapping735", "lemon"), "xebdvyk735"),
    (("mapping735", "a"), "mapping735"),
    (("mapping735", "zz"), "lzoohmf735"),
    (("mapping735", "AgentU"), "mgtcbhg735"),
    (("mapping735", "keyboard"), "wenqwnx735"),
    (("mapping735", "AA"), "mapping735"),
    (("record735", "key"), "biayvb735"),
    (("record735", "lemon"), "cioceo735"),
    (("record735", "a"), "record735"),
    (("record735", "zz"), "qdbnqc735"),
    (("record735", "AgentU"), "rkgbkx735"),
    (("record735", "keyboard"), "biapfd735"),
    (("record735", "AA"), "record735"),
    (("candle735", "key"), "melnpc735"),
    (("candle735", "lemon"), "nezryp735"),
    (("candle735", "a"), "candle735"),
    (("candle735", "zz"), "bzmckd735"),
    (("candle735", "AgentU"), "cgrqey735"),
    (("candle735", "keyboard"), "meleze735"),
    (("candle735", "AA"), "candle735"),
    (("thread735", "key"), "dlpoeb735"),
    (("thread735", "lemon"), "eldsno735"),
    (("thread735", "a"), "thread735"),
    (("thread735", "zz"), "sgqdzc735"),
    (("thread735", "AgentU"), "tnvrtx735"),
    (("thread735", "keyboard"), "dlpfod735"),
    (("thread735", "AA"), "thread735"),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 735: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 735: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "a"),
        "round 735: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 735: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 735: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 735: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", "AA"),
        "round 735: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "key"),
        "bssxh 735: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 735: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "a"),
        "round 735: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 735: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 735: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 735: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", "AA"),
        "round 735: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 735: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 735: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "a"),
        "round 735: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 735: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 735: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 735: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", "AA"),
        "round 735: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 735: the processor reads the record then stops", "key"),
        "bssxh 735: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 735: the processor reads the record then stops", "lemon"),
        "csgbq 735: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 735: the processor reads the record then stops", "a"),
        "round 735: the processor reads the record then stops",
    ),
    (
        ("round 735: the processor reads the record then stops", "zz"),
        "qntmc 735: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 735: the processor reads the record then stops", "AgentU"),
        "ruyaw 735: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 735: the processor reads the record then stops", "keyboard"),
        "bssor 735: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 735: the processor reads the record then stops", "AA"),
        "round 735: the processor reads the record then stops",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "key"),
        "bssxh 735: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "lemon"),
        "csgbq 735: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "a"),
        "round 735: a worker pulls the next task from the queue",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "zz"),
        "qntmc 735: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 735: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "keyboard"),
        "bssor 735: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 735: a worker pulls the next task from the queue", "AA"),
        "round 735: a worker pulls the next task from the queue",
    ),
    (
        ("round 735: signals travel through the network layer", "key"),
        "bssxh 735: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 735: signals travel through the network layer", "lemon"),
        "csgbq 735: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 735: signals travel through the network layer", "a"),
        "round 735: signals travel through the network layer",
    ),
    (
        ("round 735: signals travel through the network layer", "zz"),
        "qntmc 735: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 735: signals travel through the network layer", "AgentU"),
        "ruyaw 735: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 735: signals travel through the network layer", "keyboard"),
        "bssor 735: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 735: signals travel through the network layer", "AA"),
        "round 735: signals travel through the network layer",
    ),
    (
        ("round 735: the gateway routes each request by policy", "key"),
        "bssxh 735: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 735: the gateway routes each request by policy", "lemon"),
        "csgbq 735: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 735: the gateway routes each request by policy", "a"),
        "round 735: the gateway routes each request by policy",
    ),
    (
        ("round 735: the gateway routes each request by policy", "zz"),
        "qntmc 735: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 735: the gateway routes each request by policy", "AgentU"),
        "ruyaw 735: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 735: the gateway routes each request by policy", "keyboard"),
        "bssor 735: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 735: the gateway routes each request by policy", "AA"),
        "round 735: the gateway routes each request by policy",
    ),
    (("round 735: memory grows until the buffer is full", "key"), "bssxh 735: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 735: memory grows until the buffer is full", "lemon"), "csgbq 735: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 735: memory grows until the buffer is full", "a"), "round 735: memory grows until the buffer is full"),
    (("round 735: memory grows until the buffer is full", "zz"), "qntmc 735: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 735: memory grows until the buffer is full", "AgentU"),
        "ruyaw 735: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 735: memory grows until the buffer is full", "keyboard"),
        "bssor 735: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 735: memory grows until the buffer is full", "AA"), "round 735: memory grows until the buffer is full"),
    (("round 735: the cluster mirrors every packet twice", "key"), "bssxh 735: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 735: the cluster mirrors every packet twice", "lemon"),
        "csgbq 735: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 735: the cluster mirrors every packet twice", "a"), "round 735: the cluster mirrors every packet twice"),
    (("round 735: the cluster mirrors every packet twice", "zz"), "qntmc 735: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 735: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 735: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 735: the cluster mirrors every packet twice", "keyboard"),
        "bssor 735: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 735: the cluster mirrors every packet twice", "AA"), "round 735: the cluster mirrors every packet twice"),
    (
        ("round 735: ranking uses tokens learned from the corpus", "key"),
        "bssxh 735: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 735: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", "a"),
        "round 735: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 735: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 735: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 735: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", "AA"),
        "round 735: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 735: a long session ends when the candle dies", "key"),
        "bssxh 735: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 735: a long session ends when the candle dies", "lemon"),
        "csgbq 735: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 735: a long session ends when the candle dies", "a"),
        "round 735: a long session ends when the candle dies",
    ),
    (
        ("round 735: a long session ends when the candle dies", "zz"),
        "qntmc 735: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 735: a long session ends when the candle dies", "AgentU"),
        "ruyaw 735: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 735: a long session ends when the candle dies", "keyboard"),
        "bssor 735: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 735: a long session ends when the candle dies", "AA"),
        "round 735: a long session ends when the candle dies",
    ),
    (("round 735: encode the prompt then map the result", "key"), "bssxh 735: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 735: encode the prompt then map the result", "lemon"), "csgbq 735: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 735: encode the prompt then map the result", "a"), "round 735: encode the prompt then map the result"),
    (("round 735: encode the prompt then map the result", "zz"), "qntmc 735: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 735: encode the prompt then map the result", "AgentU"),
        "ruyaw 735: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 735: encode the prompt then map the result", "keyboard"),
        "bssor 735: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 735: encode the prompt then map the result", "AA"), "round 735: encode the prompt then map the result"),
    (("round 735: the kernel wakes the worker at dawn", "key"), "bssxh 735: rri iovlop ukocc xfo ambocb er neux"),
    (("round 735: the kernel wakes the worker at dawn", "lemon"), "csgbq 735: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 735: the kernel wakes the worker at dawn", "a"), "round 735: the kernel wakes the worker at dawn"),
    (("round 735: the kernel wakes the worker at dawn", "zz"), "qntmc 735: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 735: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 735: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 735: the kernel wakes the worker at dawn", "keyboard"), "bssor 735: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 735: the kernel wakes the worker at dawn", "AA"), "round 735: the kernel wakes the worker at dawn"),
    (("round 735: service latency drops after the patch", "key"), "bssxh 735: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 735: service latency drops after the patch", "lemon"), "csgbq 735: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 735: service latency drops after the patch", "a"), "round 735: service latency drops after the patch"),
    (("round 735: service latency drops after the patch", "zz"), "qntmc 735: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 735: service latency drops after the patch", "AgentU"),
        "ruyaw 735: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 735: service latency drops after the patch", "keyboard"),
        "bssor 735: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 735: service latency drops after the patch", "AA"), "round 735: service latency drops after the patch"),
    (
        ("round 735: the library caches every vector it sees", "key"),
        "bssxh 735: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 735: the library caches every vector it sees", "lemon"),
        "csgbq 735: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 735: the library caches every vector it sees", "a"), "round 735: the library caches every vector it sees"),
    (
        ("round 735: the library caches every vector it sees", "zz"),
        "qntmc 735: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 735: the library caches every vector it sees", "AgentU"),
        "ruyaw 735: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 735: the library caches every vector it sees", "keyboard"),
        "bssor 735: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 735: the library caches every vector it sees", "AA"),
        "round 735: the library caches every vector it sees",
    ),
    (("round 735: agents argue then the debate resolves", "key"), "bssxh 735: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 735: agents argue then the debate resolves", "lemon"), "csgbq 735: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 735: agents argue then the debate resolves", "a"), "round 735: agents argue then the debate resolves"),
    (("round 735: agents argue then the debate resolves", "zz"), "qntmc 735: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 735: agents argue then the debate resolves", "AgentU"),
        "ruyaw 735: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 735: agents argue then the debate resolves", "keyboard"),
        "bssor 735: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 735: agents argue then the debate resolves", "AA"), "round 735: agents argue then the debate resolves"),
    (("round 735: the filter keeps only strong matches", "key"), "bssxh 735: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 735: the filter keeps only strong matches", "lemon"), "csgbq 735: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 735: the filter keeps only strong matches", "a"), "round 735: the filter keeps only strong matches"),
    (("round 735: the filter keeps only strong matches", "zz"), "qntmc 735: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 735: the filter keeps only strong matches", "AgentU"), "ruyaw 735: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 735: the filter keeps only strong matches", "keyboard"),
        "bssor 735: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 735: the filter keeps only strong matches", "AA"), "round 735: the filter keeps only strong matches"),
    (("round 735: the model answers with a short reply", "key"), "bssxh 735: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 735: the model answers with a short reply", "lemon"), "csgbq 735: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 735: the model answers with a short reply", "a"), "round 735: the model answers with a short reply"),
    (("round 735: the model answers with a short reply", "zz"), "qntmc 735: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 735: the model answers with a short reply", "AgentU"), "ruyaw 735: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 735: the model answers with a short reply", "keyboard"),
        "bssor 735: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 735: the model answers with a short reply", "AA"), "round 735: the model answers with a short reply"),
    (
        ("round 735: the recorder stores the reasoning trace", "key"),
        "bssxh 735: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 735: the recorder stores the reasoning trace", "lemon"),
        "csgbq 735: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 735: the recorder stores the reasoning trace", "a"), "round 735: the recorder stores the reasoning trace"),
    (
        ("round 735: the recorder stores the reasoning trace", "zz"),
        "qntmc 735: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 735: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 735: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 735: the recorder stores the reasoning trace", "keyboard"),
        "bssor 735: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 735: the recorder stores the reasoning trace", "AA"),
        "round 735: the recorder stores the reasoning trace",
    ),
    (("round 735: the angel watches the processor run", "key"), "bssxh 735: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 735: the angel watches the processor run", "lemon"), "csgbq 735: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 735: the angel watches the processor run", "a"), "round 735: the angel watches the processor run"),
    (("round 735: the angel watches the processor run", "zz"), "qntmc 735: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 735: the angel watches the processor run", "AgentU"), "ruyaw 735: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 735: the angel watches the processor run", "keyboard"), "bssor 735: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 735: the angel watches the processor run", "AA"), "round 735: the angel watches the processor run"),
    (("round 735: angle of the vector decides the match", "key"), "bssxh 735: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 735: angle of the vector decides the match", "lemon"), "csgbq 735: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 735: angle of the vector decides the match", "a"), "round 735: angle of the vector decides the match"),
    (("round 735: angle of the vector decides the match", "zz"), "qntmc 735: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 735: angle of the vector decides the match", "AgentU"),
        "ruyaw 735: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 735: angle of the vector decides the match", "keyboard"),
        "bssor 735: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 735: angle of the vector decides the match", "AA"), "round 735: angle of the vector decides the match"),
    (
        ("round 735: the candle burns twice as long at night", "key"),
        "bssxh 735: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 735: the candle burns twice as long at night", "lemon"),
        "csgbq 735: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 735: the candle burns twice as long at night", "a"), "round 735: the candle burns twice as long at night"),
    (
        ("round 735: the candle burns twice as long at night", "zz"),
        "qntmc 735: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 735: the candle burns twice as long at night", "AgentU"),
        "ruyaw 735: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 735: the candle burns twice as long at night", "keyboard"),
        "bssor 735: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 735: the candle burns twice as long at night", "AA"),
        "round 735: the candle burns twice as long at night",
    ),
    (("round 735: a mirror of the universe in one line", "key"), "bssxh 735: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 735: a mirror of the universe in one line", "lemon"), "csgbq 735: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 735: a mirror of the universe in one line", "a"), "round 735: a mirror of the universe in one line"),
    (("round 735: a mirror of the universe in one line", "zz"), "qntmc 735: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 735: a mirror of the universe in one line", "AgentU"), "ruyaw 735: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 735: a mirror of the universe in one line", "keyboard"),
        "bssor 735: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 735: a mirror of the universe in one line", "AA"), "round 735: a mirror of the universe in one line"),
    (("round 735: the queue drains before the storm", "key"), "bssxh 735: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 735: the queue drains before the storm", "lemon"), "csgbq 735: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 735: the queue drains before the storm", "a"), "round 735: the queue drains before the storm"),
    (("round 735: the queue drains before the storm", "zz"), "qntmc 735: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 735: the queue drains before the storm", "AgentU"), "ruyaw 735: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 735: the queue drains before the storm", "keyboard"), "bssor 735: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 735: the queue drains before the storm", "AA"), "round 735: the queue drains before the storm"),
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
