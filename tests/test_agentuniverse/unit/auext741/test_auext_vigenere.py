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
    (("kitten741", "key"), "umrdil741"),
    (("kitten741", "lemon"), "vmfhry741"),
    (("kitten741", "a"), "kitten741"),
    (("kitten741", "zz"), "jhssdm741"),
    (("kitten741", "AgentU"), "koxgxh741"),
    (("kitten741", "keyboard"), "umrusn741"),
    (("kitten741", "AA"), "kitten741"),
    (("sitting741", "key"), "cmrdmlq741"),
    (("sitting741", "lemon"), "dmfhvyk741"),
    (("sitting741", "a"), "sitting741"),
    (("sitting741", "zz"), "rhsshmf741"),
    (("sitting741", "AgentU"), "soxgbhg741"),
    (("sitting741", "keyboard"), "cmruwnx741"),
    (("sitting741", "AA"), "sitting741"),
    (("agent741", "key"), "kkcxx741"),
    (("agent741", "lemon"), "lkqbg741"),
    (("agent741", "a"), "agent741"),
    (("agent741", "zz"), "zfdms741"),
    (("agent741", "AgentU"), "amiam741"),
    (("agent741", "keyboard"), "kkcoh741"),
    (("agent741", "AA"), "agent741"),
    (("angle741", "key"), "krevi741"),
    (("angle741", "lemon"), "lrszr741"),
    (("angle741", "a"), "angle741"),
    (("angle741", "zz"), "zmfkd741"),
    (("angle741", "AgentU"), "atkyx741"),
    (("angle741", "keyboard"), "krems741"),
    (("angle741", "AA"), "angle741"),
    (("universe741", "key"), "ergfipci741"),
    (("universe741", "lemon"), "frujrcwq741"),
    (("universe741", "a"), "universe741"),
    (("universe741", "zz"), "tmhudqrd741"),
    (("universe741", "AgentU"), "utmixlsk741"),
    (("universe741", "keyboard"), "ergwsrjh741"),
    (("universe741", "AA"), "universe741"),
    (("memory741", "key"), "wikyvw741"),
    (("memory741", "lemon"), "xiycej741"),
    (("memory741", "a"), "memory741"),
    (("memory741", "zz"), "ldlnqx741"),
    (("memory741", "AgentU"), "mkqbks741"),
    (("memory741", "keyboard"), "wikpfy741"),
    (("memory741", "AA"), "memory741"),
    (("stream741", "key"), "cxpoek741"),
    (("stream741", "lemon"), "dxdsnx741"),
    (("stream741", "a"), "stream741"),
    (("stream741", "zz"), "rsqdzl741"),
    (("stream741", "AgentU"), "szvrtg741"),
    (("stream741", "keyboard"), "cxpfom741"),
    (("stream741", "AA"), "stream741"),
    (("context741", "key"), "msldivd741"),
    (("context741", "lemon"), "nszhrix741"),
    (("context741", "a"), "context741"),
    (("context741", "zz"), "bnmsdws741"),
    (("context741", "AgentU"), "curgxrt741"),
    (("context741", "keyboard"), "mslusxk741"),
    (("context741", "AA"), "context741"),
    (("knowledge741", "key"), "urmgpcnkc741"),
    (("knowledge741", "lemon"), "vrakyphss741"),
    (("knowledge741", "a"), "knowledge741"),
    (("knowledge741", "zz"), "jmnvkdcfd741"),
    (("knowledge741", "AgentU"), "ktsjeydmi741"),
    (("knowledge741", "keyboard"), "urmxzeujo741"),
    (("knowledge741", "AA"), "knowledge741"),
    (("vector741", "key"), "fiadsp741"),
    (("vector741", "lemon"), "giohbc741"),
    (("vector741", "a"), "vector741"),
    (("vector741", "zz"), "udbsnq741"),
    (("vector741", "AgentU"), "vkgghl741"),
    (("vector741", "keyboard"), "fiaucr741"),
    (("vector741", "AA"), "vector741"),
    (("processor741", "key"), "zvmmiqcsp741"),
    (("processor741", "lemon"), "avaqrdwaf741"),
    (("processor741", "a"), "processor741"),
    (("processor741", "zz"), "oqnbdrrnq741"),
    (("processor741", "AgentU"), "pxspxmsuv741"),
    (("processor741", "keyboard"), "zvmdssjrb741"),
    (("processor741", "AA"), "processor741"),
    (("reasoning741", "key"), "biycslsre741"),
    (("reasoning741", "lemon"), "cimgbymzu741"),
    (("reasoning741", "a"), "reasoning741"),
    (("reasoning741", "zz"), "qdzrnmhmf741"),
    (("reasoning741", "AgentU"), "rkefhhitk741"),
    (("reasoning741", "keyboard"), "biytcnzqq741"),
    (("reasoning741", "AA"), "reasoning741"),
    (("machine741", "key"), "wearmlo741"),
    (("machine741", "lemon"), "xeovvyi741"),
    (("machine741", "a"), "machine741"),
    (("machine741", "zz"), "lzbghmd741"),
    (("machine741", "AgentU"), "mggubhe741"),
    (("machine741", "keyboard"), "weaiwnv741"),
    (("machine741", "AA"), "machine741"),
    (("learning741", "key"), "viybrgxk741"),
    (("learning741", "lemon"), "wimfatrs741"),
    (("learning741", "a"), "learning741"),
    (("learning741", "zz"), "kdzqmhmf741"),
    (("learning741", "AgentU"), "lkeegcnm741"),
    (("learning741", "keyboard"), "viysbiej741"),
    (("learning741", "AA"), "learning741"),
    (("model741", "key"), "wsbop741"),
    (("model741", "lemon"), "xspsy741"),
    (("model741", "a"), "model741"),
    (("model741", "zz"), "lncdk741"),
    (("model741", "AgentU"), "muhre741"),
    (("model741", "keyboard"), "wsbfz741"),
    (("model741", "AA"), "model741"),
    (("token741", "key"), "dsior741"),
    (("token741", "lemon"), "eswsa741"),
    (("token741", "a"), "token741"),
    (("token741", "zz"), "snjdm741"),
    (("token741", "AgentU"), "tuorg741"),
    (("token741", "keyboard"), "dsifb741"),
    (("token741", "AA"), "token741"),
    (("prompt741", "key"), "zvmwtr741"),
    (("prompt741", "lemon"), "avaace741"),
    (("prompt741", "a"), "prompt741"),
    (("prompt741", "zz"), "oqnlos741"),
    (("prompt741", "AgentU"), "pxszin741"),
    (("prompt741", "keyboard"), "zvmndt741"),
    (("prompt741", "AA"), "prompt741"),
    (("session741", "key"), "ciqcmmx741"),
    (("session741", "lemon"), "diegvzr741"),
    (("session741", "a"), "session741"),
    (("session741", "zz"), "rdrrhnm741"),
    (("session741", "AgentU"), "skwfbin741"),
    (("session741", "keyboard"), "ciqtwoe741"),
    (("session741", "AA"), "session741"),
    (("library741", "key"), "vmzbepi741"),
    (("library741", "lemon"), "wmnfncc741"),
    (("library741", "a"), "library741"),
    (("library741", "zz"), "khaqzqx741"),
    (("library741", "AgentU"), "lofetly741"),
    (("library741", "keyboard"), "vmzsorp741"),
    (("library741", "AA"), "library741"),
    (("service741", "key"), "cipfmao741"),
    (("service741", "lemon"), "didjvni741"),
    (("service741", "a"), "service741"),
    (("service741", "zz"), "rdquhbd741"),
    (("service741", "AgentU"), "skvibwe741"),
    (("service741", "keyboard"), "cipwwcv741"),
    (("service741", "AA"), "service741"),
    (("gateway741", "key"), "qeroayi741"),
    (("gateway741", "lemon"), "refsjlc741"),
    (("gateway741", "a"), "gateway741"),
    (("gateway741", "zz"), "fzsdvzx741"),
    (("gateway741", "AgentU"), "ggxrpuy741"),
    (("gateway741", "keyboard"), "qerfkap741"),
    (("gateway741", "AA"), "gateway741"),
    (("storage741", "key"), "cxmbeeo741"),
    (("storage741", "lemon"), "dxafnri741"),
    (("storage741", "a"), "storage741"),
    (("storage741", "zz"), "rsnqzfd741"),
    (("storage741", "AgentU"), "szsetae741"),
    (("storage741", "keyboard"), "cxmsogv741"),
    (("storage741", "AA"), "storage741"),
    (("network741", "key"), "xirgspu741"),
    (("network741", "lemon"), "yifkbco741"),
    (("network741", "a"), "network741"),
    (("network741", "zz"), "mdsvnqj741"),
    (("network741", "AgentU"), "nkxjhlk741"),
    (("network741", "keyboard"), "xirxcrb741"),
    (("network741", "AA"), "network741"),
    (("latency741", "key"), "verorai741"),
    (("latency741", "lemon"), "wefsanc741"),
    (("latency741", "a"), "latency741"),
    (("latency741", "zz"), "kzsdmbx741"),
    (("latency741", "AgentU"), "lgxrgwy741"),
    (("latency741", "keyboard"), "verfbcp741"),
    (("latency741", "AA"), "latency741"),
    (("buffer741", "key"), "lydpip741"),
    (("buffer741", "lemon"), "myrtrc741"),
    (("buffer741", "a"), "buffer741"),
    (("buffer741", "zz"), "ateedq741"),
    (("buffer741", "AgentU"), "bajsxl741"),
    (("buffer741", "keyboard"), "lydgsr741"),
    (("buffer741", "AA"), "buffer741"),
    (("queue741", "key"), "aycei741"),
    (("queue741", "lemon"), "byqir741"),
    (("queue741", "a"), "queue741"),
    (("queue741", "zz"), "ptdtd741"),
    (("queue741", "AgentU"), "qaihx741"),
    (("queue741", "keyboard"), "aycvs741"),
    (("queue741", "AA"), "queue741"),
    (("worker741", "key"), "gspuip741"),
    (("worker741", "lemon"), "hsdyrc741"),
    (("worker741", "a"), "worker741"),
    (("worker741", "zz"), "vnqjdq741"),
    (("worker741", "AgentU"), "wuvxxl741"),
    (("worker741", "keyboard"), "gsplsr741"),
    (("worker741", "AA"), "worker741"),
    (("kernel741", "key"), "uipxij741"),
    (("kernel741", "lemon"), "vidbrw741"),
    (("kernel741", "a"), "kernel741"),
    (("kernel741", "zz"), "jdqmdk741"),
    (("kernel741", "AgentU"), "kkvaxf741"),
    (("kernel741", "keyboard"), "uiposl741"),
    (("kernel741", "AA"), "kernel741"),
    (("signal741", "key"), "cmexej741"),
    (("signal741", "lemon"), "dmsbnw741"),
    (("signal741", "a"), "signal741"),
    (("signal741", "zz"), "rhfmzk741"),
    (("signal741", "AgentU"), "sokatf741"),
    (("signal741", "keyboard"), "cmeool741"),
    (("signal741", "AA"), "signal741"),
    (("packet741", "key"), "zeauir741"),
    (("packet741", "lemon"), "aeoyre741"),
    (("packet741", "a"), "packet741"),
    (("packet741", "zz"), "ozbjds741"),
    (("packet741", "AgentU"), "pggxxn741"),
    (("packet741", "keyboard"), "zealst741"),
    (("packet741", "AA"), "packet741"),
    (("router741", "key"), "bssdip741"),
    (("router741", "lemon"), "csghrc741"),
    (("router741", "a"), "router741"),
    (("router741", "zz"), "qntsdq741"),
    (("router741", "AgentU"), "ruygxl741"),
    (("router741", "keyboard"), "bssusr741"),
    (("router741", "AA"), "router741"),
    (("cluster741", "key"), "mpscxcb741"),
    (("cluster741", "lemon"), "npgggpv741"),
    (("cluster741", "a"), "cluster741"),
    (("cluster741", "zz"), "bktrsdq741"),
    (("cluster741", "AgentU"), "cryfmyr741"),
    (("cluster741", "keyboard"), "mpsthei741"),
    (("cluster741", "AA"), "cluster741"),
    (("mirror741", "key"), "wmpbsp741"),
    (("mirror741", "lemon"), "xmdfbc741"),
    (("mirror741", "a"), "mirror741"),
    (("mirror741", "zz"), "lhqqnq741"),
    (("mirror741", "AgentU"), "movehl741"),
    (("mirror741", "keyboard"), "wmpscr741"),
    (("mirror741", "AA"), "mirror741"),
    (("filter741", "key"), "pmjdip741"),
    (("filter741", "lemon"), "qmxhrc741"),
    (("filter741", "a"), "filter741"),
    (("filter741", "zz"), "ehksdq741"),
    (("filter741", "AgentU"), "fopgxl741"),
    (("filter741", "keyboard"), "pmjusr741"),
    (("filter741", "AA"), "filter741"),
    (("ranking741", "key"), "belumlq741"),
    (("ranking741", "lemon"), "cezyvyk741"),
    (("ranking741", "a"), "ranking741"),
    (("ranking741", "zz"), "qzmjhmf741"),
    (("ranking741", "AgentU"), "rgrxbhg741"),
    (("ranking741", "keyboard"), "bellwnx741"),
    (("ranking741", "AA"), "ranking741"),
    (("encoding741", "key"), "orayhgxk741"),
    (("encoding741", "lemon"), "procqtrs741"),
    (("encoding741", "a"), "encoding741"),
    (("encoding741", "zz"), "dmbnchmf741"),
    (("encoding741", "AgentU"), "etgbwcnm741"),
    (("encoding741", "keyboard"), "orapriej741"),
    (("encoding741", "AA"), "encoding741"),
    (("mapping741", "key"), "wenzmlq741"),
    (("mapping741", "lemon"), "xebdvyk741"),
    (("mapping741", "a"), "mapping741"),
    (("mapping741", "zz"), "lzoohmf741"),
    (("mapping741", "AgentU"), "mgtcbhg741"),
    (("mapping741", "keyboard"), "wenqwnx741"),
    (("mapping741", "AA"), "mapping741"),
    (("record741", "key"), "biayvb741"),
    (("record741", "lemon"), "cioceo741"),
    (("record741", "a"), "record741"),
    (("record741", "zz"), "qdbnqc741"),
    (("record741", "AgentU"), "rkgbkx741"),
    (("record741", "keyboard"), "biapfd741"),
    (("record741", "AA"), "record741"),
    (("candle741", "key"), "melnpc741"),
    (("candle741", "lemon"), "nezryp741"),
    (("candle741", "a"), "candle741"),
    (("candle741", "zz"), "bzmckd741"),
    (("candle741", "AgentU"), "cgrqey741"),
    (("candle741", "keyboard"), "meleze741"),
    (("candle741", "AA"), "candle741"),
    (("thread741", "key"), "dlpoeb741"),
    (("thread741", "lemon"), "eldsno741"),
    (("thread741", "a"), "thread741"),
    (("thread741", "zz"), "sgqdzc741"),
    (("thread741", "AgentU"), "tnvrtx741"),
    (("thread741", "keyboard"), "dlpfod741"),
    (("thread741", "AA"), "thread741"),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 741: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 741: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "a"),
        "round 741: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 741: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 741: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 741: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", "AA"),
        "round 741: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "key"),
        "bssxh 741: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 741: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "a"),
        "round 741: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 741: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 741: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 741: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", "AA"),
        "round 741: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 741: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 741: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "a"),
        "round 741: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 741: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 741: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 741: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", "AA"),
        "round 741: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 741: the processor reads the record then stops", "key"),
        "bssxh 741: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 741: the processor reads the record then stops", "lemon"),
        "csgbq 741: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 741: the processor reads the record then stops", "a"),
        "round 741: the processor reads the record then stops",
    ),
    (
        ("round 741: the processor reads the record then stops", "zz"),
        "qntmc 741: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 741: the processor reads the record then stops", "AgentU"),
        "ruyaw 741: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 741: the processor reads the record then stops", "keyboard"),
        "bssor 741: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 741: the processor reads the record then stops", "AA"),
        "round 741: the processor reads the record then stops",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "key"),
        "bssxh 741: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "lemon"),
        "csgbq 741: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "a"),
        "round 741: a worker pulls the next task from the queue",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "zz"),
        "qntmc 741: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 741: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "keyboard"),
        "bssor 741: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 741: a worker pulls the next task from the queue", "AA"),
        "round 741: a worker pulls the next task from the queue",
    ),
    (
        ("round 741: signals travel through the network layer", "key"),
        "bssxh 741: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 741: signals travel through the network layer", "lemon"),
        "csgbq 741: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 741: signals travel through the network layer", "a"),
        "round 741: signals travel through the network layer",
    ),
    (
        ("round 741: signals travel through the network layer", "zz"),
        "qntmc 741: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 741: signals travel through the network layer", "AgentU"),
        "ruyaw 741: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 741: signals travel through the network layer", "keyboard"),
        "bssor 741: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 741: signals travel through the network layer", "AA"),
        "round 741: signals travel through the network layer",
    ),
    (
        ("round 741: the gateway routes each request by policy", "key"),
        "bssxh 741: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 741: the gateway routes each request by policy", "lemon"),
        "csgbq 741: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 741: the gateway routes each request by policy", "a"),
        "round 741: the gateway routes each request by policy",
    ),
    (
        ("round 741: the gateway routes each request by policy", "zz"),
        "qntmc 741: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 741: the gateway routes each request by policy", "AgentU"),
        "ruyaw 741: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 741: the gateway routes each request by policy", "keyboard"),
        "bssor 741: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 741: the gateway routes each request by policy", "AA"),
        "round 741: the gateway routes each request by policy",
    ),
    (("round 741: memory grows until the buffer is full", "key"), "bssxh 741: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 741: memory grows until the buffer is full", "lemon"), "csgbq 741: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 741: memory grows until the buffer is full", "a"), "round 741: memory grows until the buffer is full"),
    (("round 741: memory grows until the buffer is full", "zz"), "qntmc 741: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 741: memory grows until the buffer is full", "AgentU"),
        "ruyaw 741: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 741: memory grows until the buffer is full", "keyboard"),
        "bssor 741: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 741: memory grows until the buffer is full", "AA"), "round 741: memory grows until the buffer is full"),
    (("round 741: the cluster mirrors every packet twice", "key"), "bssxh 741: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 741: the cluster mirrors every packet twice", "lemon"),
        "csgbq 741: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 741: the cluster mirrors every packet twice", "a"), "round 741: the cluster mirrors every packet twice"),
    (("round 741: the cluster mirrors every packet twice", "zz"), "qntmc 741: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 741: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 741: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 741: the cluster mirrors every packet twice", "keyboard"),
        "bssor 741: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 741: the cluster mirrors every packet twice", "AA"), "round 741: the cluster mirrors every packet twice"),
    (
        ("round 741: ranking uses tokens learned from the corpus", "key"),
        "bssxh 741: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 741: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", "a"),
        "round 741: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 741: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 741: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 741: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", "AA"),
        "round 741: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 741: a long session ends when the candle dies", "key"),
        "bssxh 741: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 741: a long session ends when the candle dies", "lemon"),
        "csgbq 741: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 741: a long session ends when the candle dies", "a"),
        "round 741: a long session ends when the candle dies",
    ),
    (
        ("round 741: a long session ends when the candle dies", "zz"),
        "qntmc 741: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 741: a long session ends when the candle dies", "AgentU"),
        "ruyaw 741: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 741: a long session ends when the candle dies", "keyboard"),
        "bssor 741: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 741: a long session ends when the candle dies", "AA"),
        "round 741: a long session ends when the candle dies",
    ),
    (("round 741: encode the prompt then map the result", "key"), "bssxh 741: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 741: encode the prompt then map the result", "lemon"), "csgbq 741: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 741: encode the prompt then map the result", "a"), "round 741: encode the prompt then map the result"),
    (("round 741: encode the prompt then map the result", "zz"), "qntmc 741: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 741: encode the prompt then map the result", "AgentU"),
        "ruyaw 741: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 741: encode the prompt then map the result", "keyboard"),
        "bssor 741: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 741: encode the prompt then map the result", "AA"), "round 741: encode the prompt then map the result"),
    (("round 741: the kernel wakes the worker at dawn", "key"), "bssxh 741: rri iovlop ukocc xfo ambocb er neux"),
    (("round 741: the kernel wakes the worker at dawn", "lemon"), "csgbq 741: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 741: the kernel wakes the worker at dawn", "a"), "round 741: the kernel wakes the worker at dawn"),
    (("round 741: the kernel wakes the worker at dawn", "zz"), "qntmc 741: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 741: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 741: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 741: the kernel wakes the worker at dawn", "keyboard"), "bssor 741: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 741: the kernel wakes the worker at dawn", "AA"), "round 741: the kernel wakes the worker at dawn"),
    (("round 741: service latency drops after the patch", "key"), "bssxh 741: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 741: service latency drops after the patch", "lemon"), "csgbq 741: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 741: service latency drops after the patch", "a"), "round 741: service latency drops after the patch"),
    (("round 741: service latency drops after the patch", "zz"), "qntmc 741: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 741: service latency drops after the patch", "AgentU"),
        "ruyaw 741: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 741: service latency drops after the patch", "keyboard"),
        "bssor 741: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 741: service latency drops after the patch", "AA"), "round 741: service latency drops after the patch"),
    (
        ("round 741: the library caches every vector it sees", "key"),
        "bssxh 741: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 741: the library caches every vector it sees", "lemon"),
        "csgbq 741: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 741: the library caches every vector it sees", "a"), "round 741: the library caches every vector it sees"),
    (
        ("round 741: the library caches every vector it sees", "zz"),
        "qntmc 741: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 741: the library caches every vector it sees", "AgentU"),
        "ruyaw 741: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 741: the library caches every vector it sees", "keyboard"),
        "bssor 741: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 741: the library caches every vector it sees", "AA"),
        "round 741: the library caches every vector it sees",
    ),
    (("round 741: agents argue then the debate resolves", "key"), "bssxh 741: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 741: agents argue then the debate resolves", "lemon"), "csgbq 741: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 741: agents argue then the debate resolves", "a"), "round 741: agents argue then the debate resolves"),
    (("round 741: agents argue then the debate resolves", "zz"), "qntmc 741: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 741: agents argue then the debate resolves", "AgentU"),
        "ruyaw 741: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 741: agents argue then the debate resolves", "keyboard"),
        "bssor 741: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 741: agents argue then the debate resolves", "AA"), "round 741: agents argue then the debate resolves"),
    (("round 741: the filter keeps only strong matches", "key"), "bssxh 741: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 741: the filter keeps only strong matches", "lemon"), "csgbq 741: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 741: the filter keeps only strong matches", "a"), "round 741: the filter keeps only strong matches"),
    (("round 741: the filter keeps only strong matches", "zz"), "qntmc 741: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 741: the filter keeps only strong matches", "AgentU"), "ruyaw 741: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 741: the filter keeps only strong matches", "keyboard"),
        "bssor 741: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 741: the filter keeps only strong matches", "AA"), "round 741: the filter keeps only strong matches"),
    (("round 741: the model answers with a short reply", "key"), "bssxh 741: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 741: the model answers with a short reply", "lemon"), "csgbq 741: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 741: the model answers with a short reply", "a"), "round 741: the model answers with a short reply"),
    (("round 741: the model answers with a short reply", "zz"), "qntmc 741: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 741: the model answers with a short reply", "AgentU"), "ruyaw 741: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 741: the model answers with a short reply", "keyboard"),
        "bssor 741: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 741: the model answers with a short reply", "AA"), "round 741: the model answers with a short reply"),
    (
        ("round 741: the recorder stores the reasoning trace", "key"),
        "bssxh 741: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 741: the recorder stores the reasoning trace", "lemon"),
        "csgbq 741: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 741: the recorder stores the reasoning trace", "a"), "round 741: the recorder stores the reasoning trace"),
    (
        ("round 741: the recorder stores the reasoning trace", "zz"),
        "qntmc 741: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 741: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 741: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 741: the recorder stores the reasoning trace", "keyboard"),
        "bssor 741: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 741: the recorder stores the reasoning trace", "AA"),
        "round 741: the recorder stores the reasoning trace",
    ),
    (("round 741: the angel watches the processor run", "key"), "bssxh 741: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 741: the angel watches the processor run", "lemon"), "csgbq 741: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 741: the angel watches the processor run", "a"), "round 741: the angel watches the processor run"),
    (("round 741: the angel watches the processor run", "zz"), "qntmc 741: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 741: the angel watches the processor run", "AgentU"), "ruyaw 741: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 741: the angel watches the processor run", "keyboard"), "bssor 741: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 741: the angel watches the processor run", "AA"), "round 741: the angel watches the processor run"),
    (("round 741: angle of the vector decides the match", "key"), "bssxh 741: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 741: angle of the vector decides the match", "lemon"), "csgbq 741: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 741: angle of the vector decides the match", "a"), "round 741: angle of the vector decides the match"),
    (("round 741: angle of the vector decides the match", "zz"), "qntmc 741: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 741: angle of the vector decides the match", "AgentU"),
        "ruyaw 741: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 741: angle of the vector decides the match", "keyboard"),
        "bssor 741: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 741: angle of the vector decides the match", "AA"), "round 741: angle of the vector decides the match"),
    (
        ("round 741: the candle burns twice as long at night", "key"),
        "bssxh 741: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 741: the candle burns twice as long at night", "lemon"),
        "csgbq 741: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 741: the candle burns twice as long at night", "a"), "round 741: the candle burns twice as long at night"),
    (
        ("round 741: the candle burns twice as long at night", "zz"),
        "qntmc 741: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 741: the candle burns twice as long at night", "AgentU"),
        "ruyaw 741: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 741: the candle burns twice as long at night", "keyboard"),
        "bssor 741: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 741: the candle burns twice as long at night", "AA"),
        "round 741: the candle burns twice as long at night",
    ),
    (("round 741: a mirror of the universe in one line", "key"), "bssxh 741: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 741: a mirror of the universe in one line", "lemon"), "csgbq 741: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 741: a mirror of the universe in one line", "a"), "round 741: a mirror of the universe in one line"),
    (("round 741: a mirror of the universe in one line", "zz"), "qntmc 741: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 741: a mirror of the universe in one line", "AgentU"), "ruyaw 741: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 741: a mirror of the universe in one line", "keyboard"),
        "bssor 741: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 741: a mirror of the universe in one line", "AA"), "round 741: a mirror of the universe in one line"),
    (("round 741: the queue drains before the storm", "key"), "bssxh 741: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 741: the queue drains before the storm", "lemon"), "csgbq 741: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 741: the queue drains before the storm", "a"), "round 741: the queue drains before the storm"),
    (("round 741: the queue drains before the storm", "zz"), "qntmc 741: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 741: the queue drains before the storm", "AgentU"), "ruyaw 741: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 741: the queue drains before the storm", "keyboard"), "bssor 741: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 741: the queue drains before the storm", "AA"), "round 741: the queue drains before the storm"),
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
