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
    (("kitten133", "key"), "umrdil133"),
    (("kitten133", "lemon"), "vmfhry133"),
    (("kitten133", "a"), "kitten133"),
    (("kitten133", "zz"), "jhssdm133"),
    (("kitten133", "AgentU"), "koxgxh133"),
    (("kitten133", "keyboard"), "umrusn133"),
    (("kitten133", "AA"), "kitten133"),
    (("sitting133", "key"), "cmrdmlq133"),
    (("sitting133", "lemon"), "dmfhvyk133"),
    (("sitting133", "a"), "sitting133"),
    (("sitting133", "zz"), "rhsshmf133"),
    (("sitting133", "AgentU"), "soxgbhg133"),
    (("sitting133", "keyboard"), "cmruwnx133"),
    (("sitting133", "AA"), "sitting133"),
    (("agent133", "key"), "kkcxx133"),
    (("agent133", "lemon"), "lkqbg133"),
    (("agent133", "a"), "agent133"),
    (("agent133", "zz"), "zfdms133"),
    (("agent133", "AgentU"), "amiam133"),
    (("agent133", "keyboard"), "kkcoh133"),
    (("agent133", "AA"), "agent133"),
    (("angle133", "key"), "krevi133"),
    (("angle133", "lemon"), "lrszr133"),
    (("angle133", "a"), "angle133"),
    (("angle133", "zz"), "zmfkd133"),
    (("angle133", "AgentU"), "atkyx133"),
    (("angle133", "keyboard"), "krems133"),
    (("angle133", "AA"), "angle133"),
    (("universe133", "key"), "ergfipci133"),
    (("universe133", "lemon"), "frujrcwq133"),
    (("universe133", "a"), "universe133"),
    (("universe133", "zz"), "tmhudqrd133"),
    (("universe133", "AgentU"), "utmixlsk133"),
    (("universe133", "keyboard"), "ergwsrjh133"),
    (("universe133", "AA"), "universe133"),
    (("memory133", "key"), "wikyvw133"),
    (("memory133", "lemon"), "xiycej133"),
    (("memory133", "a"), "memory133"),
    (("memory133", "zz"), "ldlnqx133"),
    (("memory133", "AgentU"), "mkqbks133"),
    (("memory133", "keyboard"), "wikpfy133"),
    (("memory133", "AA"), "memory133"),
    (("stream133", "key"), "cxpoek133"),
    (("stream133", "lemon"), "dxdsnx133"),
    (("stream133", "a"), "stream133"),
    (("stream133", "zz"), "rsqdzl133"),
    (("stream133", "AgentU"), "szvrtg133"),
    (("stream133", "keyboard"), "cxpfom133"),
    (("stream133", "AA"), "stream133"),
    (("context133", "key"), "msldivd133"),
    (("context133", "lemon"), "nszhrix133"),
    (("context133", "a"), "context133"),
    (("context133", "zz"), "bnmsdws133"),
    (("context133", "AgentU"), "curgxrt133"),
    (("context133", "keyboard"), "mslusxk133"),
    (("context133", "AA"), "context133"),
    (("knowledge133", "key"), "urmgpcnkc133"),
    (("knowledge133", "lemon"), "vrakyphss133"),
    (("knowledge133", "a"), "knowledge133"),
    (("knowledge133", "zz"), "jmnvkdcfd133"),
    (("knowledge133", "AgentU"), "ktsjeydmi133"),
    (("knowledge133", "keyboard"), "urmxzeujo133"),
    (("knowledge133", "AA"), "knowledge133"),
    (("vector133", "key"), "fiadsp133"),
    (("vector133", "lemon"), "giohbc133"),
    (("vector133", "a"), "vector133"),
    (("vector133", "zz"), "udbsnq133"),
    (("vector133", "AgentU"), "vkgghl133"),
    (("vector133", "keyboard"), "fiaucr133"),
    (("vector133", "AA"), "vector133"),
    (("processor133", "key"), "zvmmiqcsp133"),
    (("processor133", "lemon"), "avaqrdwaf133"),
    (("processor133", "a"), "processor133"),
    (("processor133", "zz"), "oqnbdrrnq133"),
    (("processor133", "AgentU"), "pxspxmsuv133"),
    (("processor133", "keyboard"), "zvmdssjrb133"),
    (("processor133", "AA"), "processor133"),
    (("reasoning133", "key"), "biycslsre133"),
    (("reasoning133", "lemon"), "cimgbymzu133"),
    (("reasoning133", "a"), "reasoning133"),
    (("reasoning133", "zz"), "qdzrnmhmf133"),
    (("reasoning133", "AgentU"), "rkefhhitk133"),
    (("reasoning133", "keyboard"), "biytcnzqq133"),
    (("reasoning133", "AA"), "reasoning133"),
    (("machine133", "key"), "wearmlo133"),
    (("machine133", "lemon"), "xeovvyi133"),
    (("machine133", "a"), "machine133"),
    (("machine133", "zz"), "lzbghmd133"),
    (("machine133", "AgentU"), "mggubhe133"),
    (("machine133", "keyboard"), "weaiwnv133"),
    (("machine133", "AA"), "machine133"),
    (("learning133", "key"), "viybrgxk133"),
    (("learning133", "lemon"), "wimfatrs133"),
    (("learning133", "a"), "learning133"),
    (("learning133", "zz"), "kdzqmhmf133"),
    (("learning133", "AgentU"), "lkeegcnm133"),
    (("learning133", "keyboard"), "viysbiej133"),
    (("learning133", "AA"), "learning133"),
    (("model133", "key"), "wsbop133"),
    (("model133", "lemon"), "xspsy133"),
    (("model133", "a"), "model133"),
    (("model133", "zz"), "lncdk133"),
    (("model133", "AgentU"), "muhre133"),
    (("model133", "keyboard"), "wsbfz133"),
    (("model133", "AA"), "model133"),
    (("token133", "key"), "dsior133"),
    (("token133", "lemon"), "eswsa133"),
    (("token133", "a"), "token133"),
    (("token133", "zz"), "snjdm133"),
    (("token133", "AgentU"), "tuorg133"),
    (("token133", "keyboard"), "dsifb133"),
    (("token133", "AA"), "token133"),
    (("prompt133", "key"), "zvmwtr133"),
    (("prompt133", "lemon"), "avaace133"),
    (("prompt133", "a"), "prompt133"),
    (("prompt133", "zz"), "oqnlos133"),
    (("prompt133", "AgentU"), "pxszin133"),
    (("prompt133", "keyboard"), "zvmndt133"),
    (("prompt133", "AA"), "prompt133"),
    (("session133", "key"), "ciqcmmx133"),
    (("session133", "lemon"), "diegvzr133"),
    (("session133", "a"), "session133"),
    (("session133", "zz"), "rdrrhnm133"),
    (("session133", "AgentU"), "skwfbin133"),
    (("session133", "keyboard"), "ciqtwoe133"),
    (("session133", "AA"), "session133"),
    (("library133", "key"), "vmzbepi133"),
    (("library133", "lemon"), "wmnfncc133"),
    (("library133", "a"), "library133"),
    (("library133", "zz"), "khaqzqx133"),
    (("library133", "AgentU"), "lofetly133"),
    (("library133", "keyboard"), "vmzsorp133"),
    (("library133", "AA"), "library133"),
    (("service133", "key"), "cipfmao133"),
    (("service133", "lemon"), "didjvni133"),
    (("service133", "a"), "service133"),
    (("service133", "zz"), "rdquhbd133"),
    (("service133", "AgentU"), "skvibwe133"),
    (("service133", "keyboard"), "cipwwcv133"),
    (("service133", "AA"), "service133"),
    (("gateway133", "key"), "qeroayi133"),
    (("gateway133", "lemon"), "refsjlc133"),
    (("gateway133", "a"), "gateway133"),
    (("gateway133", "zz"), "fzsdvzx133"),
    (("gateway133", "AgentU"), "ggxrpuy133"),
    (("gateway133", "keyboard"), "qerfkap133"),
    (("gateway133", "AA"), "gateway133"),
    (("storage133", "key"), "cxmbeeo133"),
    (("storage133", "lemon"), "dxafnri133"),
    (("storage133", "a"), "storage133"),
    (("storage133", "zz"), "rsnqzfd133"),
    (("storage133", "AgentU"), "szsetae133"),
    (("storage133", "keyboard"), "cxmsogv133"),
    (("storage133", "AA"), "storage133"),
    (("network133", "key"), "xirgspu133"),
    (("network133", "lemon"), "yifkbco133"),
    (("network133", "a"), "network133"),
    (("network133", "zz"), "mdsvnqj133"),
    (("network133", "AgentU"), "nkxjhlk133"),
    (("network133", "keyboard"), "xirxcrb133"),
    (("network133", "AA"), "network133"),
    (("latency133", "key"), "verorai133"),
    (("latency133", "lemon"), "wefsanc133"),
    (("latency133", "a"), "latency133"),
    (("latency133", "zz"), "kzsdmbx133"),
    (("latency133", "AgentU"), "lgxrgwy133"),
    (("latency133", "keyboard"), "verfbcp133"),
    (("latency133", "AA"), "latency133"),
    (("buffer133", "key"), "lydpip133"),
    (("buffer133", "lemon"), "myrtrc133"),
    (("buffer133", "a"), "buffer133"),
    (("buffer133", "zz"), "ateedq133"),
    (("buffer133", "AgentU"), "bajsxl133"),
    (("buffer133", "keyboard"), "lydgsr133"),
    (("buffer133", "AA"), "buffer133"),
    (("queue133", "key"), "aycei133"),
    (("queue133", "lemon"), "byqir133"),
    (("queue133", "a"), "queue133"),
    (("queue133", "zz"), "ptdtd133"),
    (("queue133", "AgentU"), "qaihx133"),
    (("queue133", "keyboard"), "aycvs133"),
    (("queue133", "AA"), "queue133"),
    (("worker133", "key"), "gspuip133"),
    (("worker133", "lemon"), "hsdyrc133"),
    (("worker133", "a"), "worker133"),
    (("worker133", "zz"), "vnqjdq133"),
    (("worker133", "AgentU"), "wuvxxl133"),
    (("worker133", "keyboard"), "gsplsr133"),
    (("worker133", "AA"), "worker133"),
    (("kernel133", "key"), "uipxij133"),
    (("kernel133", "lemon"), "vidbrw133"),
    (("kernel133", "a"), "kernel133"),
    (("kernel133", "zz"), "jdqmdk133"),
    (("kernel133", "AgentU"), "kkvaxf133"),
    (("kernel133", "keyboard"), "uiposl133"),
    (("kernel133", "AA"), "kernel133"),
    (("signal133", "key"), "cmexej133"),
    (("signal133", "lemon"), "dmsbnw133"),
    (("signal133", "a"), "signal133"),
    (("signal133", "zz"), "rhfmzk133"),
    (("signal133", "AgentU"), "sokatf133"),
    (("signal133", "keyboard"), "cmeool133"),
    (("signal133", "AA"), "signal133"),
    (("packet133", "key"), "zeauir133"),
    (("packet133", "lemon"), "aeoyre133"),
    (("packet133", "a"), "packet133"),
    (("packet133", "zz"), "ozbjds133"),
    (("packet133", "AgentU"), "pggxxn133"),
    (("packet133", "keyboard"), "zealst133"),
    (("packet133", "AA"), "packet133"),
    (("router133", "key"), "bssdip133"),
    (("router133", "lemon"), "csghrc133"),
    (("router133", "a"), "router133"),
    (("router133", "zz"), "qntsdq133"),
    (("router133", "AgentU"), "ruygxl133"),
    (("router133", "keyboard"), "bssusr133"),
    (("router133", "AA"), "router133"),
    (("cluster133", "key"), "mpscxcb133"),
    (("cluster133", "lemon"), "npgggpv133"),
    (("cluster133", "a"), "cluster133"),
    (("cluster133", "zz"), "bktrsdq133"),
    (("cluster133", "AgentU"), "cryfmyr133"),
    (("cluster133", "keyboard"), "mpsthei133"),
    (("cluster133", "AA"), "cluster133"),
    (("mirror133", "key"), "wmpbsp133"),
    (("mirror133", "lemon"), "xmdfbc133"),
    (("mirror133", "a"), "mirror133"),
    (("mirror133", "zz"), "lhqqnq133"),
    (("mirror133", "AgentU"), "movehl133"),
    (("mirror133", "keyboard"), "wmpscr133"),
    (("mirror133", "AA"), "mirror133"),
    (("filter133", "key"), "pmjdip133"),
    (("filter133", "lemon"), "qmxhrc133"),
    (("filter133", "a"), "filter133"),
    (("filter133", "zz"), "ehksdq133"),
    (("filter133", "AgentU"), "fopgxl133"),
    (("filter133", "keyboard"), "pmjusr133"),
    (("filter133", "AA"), "filter133"),
    (("ranking133", "key"), "belumlq133"),
    (("ranking133", "lemon"), "cezyvyk133"),
    (("ranking133", "a"), "ranking133"),
    (("ranking133", "zz"), "qzmjhmf133"),
    (("ranking133", "AgentU"), "rgrxbhg133"),
    (("ranking133", "keyboard"), "bellwnx133"),
    (("ranking133", "AA"), "ranking133"),
    (("encoding133", "key"), "orayhgxk133"),
    (("encoding133", "lemon"), "procqtrs133"),
    (("encoding133", "a"), "encoding133"),
    (("encoding133", "zz"), "dmbnchmf133"),
    (("encoding133", "AgentU"), "etgbwcnm133"),
    (("encoding133", "keyboard"), "orapriej133"),
    (("encoding133", "AA"), "encoding133"),
    (("mapping133", "key"), "wenzmlq133"),
    (("mapping133", "lemon"), "xebdvyk133"),
    (("mapping133", "a"), "mapping133"),
    (("mapping133", "zz"), "lzoohmf133"),
    (("mapping133", "AgentU"), "mgtcbhg133"),
    (("mapping133", "keyboard"), "wenqwnx133"),
    (("mapping133", "AA"), "mapping133"),
    (("record133", "key"), "biayvb133"),
    (("record133", "lemon"), "cioceo133"),
    (("record133", "a"), "record133"),
    (("record133", "zz"), "qdbnqc133"),
    (("record133", "AgentU"), "rkgbkx133"),
    (("record133", "keyboard"), "biapfd133"),
    (("record133", "AA"), "record133"),
    (("candle133", "key"), "melnpc133"),
    (("candle133", "lemon"), "nezryp133"),
    (("candle133", "a"), "candle133"),
    (("candle133", "zz"), "bzmckd133"),
    (("candle133", "AgentU"), "cgrqey133"),
    (("candle133", "keyboard"), "meleze133"),
    (("candle133", "AA"), "candle133"),
    (("thread133", "key"), "dlpoeb133"),
    (("thread133", "lemon"), "eldsno133"),
    (("thread133", "a"), "thread133"),
    (("thread133", "zz"), "sgqdzc133"),
    (("thread133", "AgentU"), "tnvrtx133"),
    (("thread133", "keyboard"), "dlpfod133"),
    (("thread133", "AA"), "thread133"),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 133: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 133: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "a"),
        "round 133: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 133: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 133: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 133: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", "AA"),
        "round 133: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "key"),
        "bssxh 133: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 133: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "a"),
        "round 133: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 133: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 133: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 133: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", "AA"),
        "round 133: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 133: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 133: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "a"),
        "round 133: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 133: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 133: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 133: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", "AA"),
        "round 133: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 133: the processor reads the record then stops", "key"),
        "bssxh 133: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 133: the processor reads the record then stops", "lemon"),
        "csgbq 133: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 133: the processor reads the record then stops", "a"),
        "round 133: the processor reads the record then stops",
    ),
    (
        ("round 133: the processor reads the record then stops", "zz"),
        "qntmc 133: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 133: the processor reads the record then stops", "AgentU"),
        "ruyaw 133: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 133: the processor reads the record then stops", "keyboard"),
        "bssor 133: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 133: the processor reads the record then stops", "AA"),
        "round 133: the processor reads the record then stops",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "key"),
        "bssxh 133: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "lemon"),
        "csgbq 133: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "a"),
        "round 133: a worker pulls the next task from the queue",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "zz"),
        "qntmc 133: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 133: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "keyboard"),
        "bssor 133: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 133: a worker pulls the next task from the queue", "AA"),
        "round 133: a worker pulls the next task from the queue",
    ),
    (
        ("round 133: signals travel through the network layer", "key"),
        "bssxh 133: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 133: signals travel through the network layer", "lemon"),
        "csgbq 133: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 133: signals travel through the network layer", "a"),
        "round 133: signals travel through the network layer",
    ),
    (
        ("round 133: signals travel through the network layer", "zz"),
        "qntmc 133: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 133: signals travel through the network layer", "AgentU"),
        "ruyaw 133: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 133: signals travel through the network layer", "keyboard"),
        "bssor 133: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 133: signals travel through the network layer", "AA"),
        "round 133: signals travel through the network layer",
    ),
    (
        ("round 133: the gateway routes each request by policy", "key"),
        "bssxh 133: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 133: the gateway routes each request by policy", "lemon"),
        "csgbq 133: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 133: the gateway routes each request by policy", "a"),
        "round 133: the gateway routes each request by policy",
    ),
    (
        ("round 133: the gateway routes each request by policy", "zz"),
        "qntmc 133: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 133: the gateway routes each request by policy", "AgentU"),
        "ruyaw 133: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 133: the gateway routes each request by policy", "keyboard"),
        "bssor 133: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 133: the gateway routes each request by policy", "AA"),
        "round 133: the gateway routes each request by policy",
    ),
    (("round 133: memory grows until the buffer is full", "key"), "bssxh 133: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 133: memory grows until the buffer is full", "lemon"), "csgbq 133: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 133: memory grows until the buffer is full", "a"), "round 133: memory grows until the buffer is full"),
    (("round 133: memory grows until the buffer is full", "zz"), "qntmc 133: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 133: memory grows until the buffer is full", "AgentU"),
        "ruyaw 133: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 133: memory grows until the buffer is full", "keyboard"),
        "bssor 133: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 133: memory grows until the buffer is full", "AA"), "round 133: memory grows until the buffer is full"),
    (("round 133: the cluster mirrors every packet twice", "key"), "bssxh 133: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 133: the cluster mirrors every packet twice", "lemon"),
        "csgbq 133: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 133: the cluster mirrors every packet twice", "a"), "round 133: the cluster mirrors every packet twice"),
    (("round 133: the cluster mirrors every packet twice", "zz"), "qntmc 133: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 133: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 133: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 133: the cluster mirrors every packet twice", "keyboard"),
        "bssor 133: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 133: the cluster mirrors every packet twice", "AA"), "round 133: the cluster mirrors every packet twice"),
    (
        ("round 133: ranking uses tokens learned from the corpus", "key"),
        "bssxh 133: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 133: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", "a"),
        "round 133: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 133: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 133: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 133: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", "AA"),
        "round 133: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 133: a long session ends when the candle dies", "key"),
        "bssxh 133: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 133: a long session ends when the candle dies", "lemon"),
        "csgbq 133: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 133: a long session ends when the candle dies", "a"),
        "round 133: a long session ends when the candle dies",
    ),
    (
        ("round 133: a long session ends when the candle dies", "zz"),
        "qntmc 133: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 133: a long session ends when the candle dies", "AgentU"),
        "ruyaw 133: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 133: a long session ends when the candle dies", "keyboard"),
        "bssor 133: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 133: a long session ends when the candle dies", "AA"),
        "round 133: a long session ends when the candle dies",
    ),
    (("round 133: encode the prompt then map the result", "key"), "bssxh 133: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 133: encode the prompt then map the result", "lemon"), "csgbq 133: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 133: encode the prompt then map the result", "a"), "round 133: encode the prompt then map the result"),
    (("round 133: encode the prompt then map the result", "zz"), "qntmc 133: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 133: encode the prompt then map the result", "AgentU"),
        "ruyaw 133: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 133: encode the prompt then map the result", "keyboard"),
        "bssor 133: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 133: encode the prompt then map the result", "AA"), "round 133: encode the prompt then map the result"),
    (("round 133: the kernel wakes the worker at dawn", "key"), "bssxh 133: rri iovlop ukocc xfo ambocb er neux"),
    (("round 133: the kernel wakes the worker at dawn", "lemon"), "csgbq 133: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 133: the kernel wakes the worker at dawn", "a"), "round 133: the kernel wakes the worker at dawn"),
    (("round 133: the kernel wakes the worker at dawn", "zz"), "qntmc 133: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 133: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 133: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 133: the kernel wakes the worker at dawn", "keyboard"), "bssor 133: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 133: the kernel wakes the worker at dawn", "AA"), "round 133: the kernel wakes the worker at dawn"),
    (("round 133: service latency drops after the patch", "key"), "bssxh 133: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 133: service latency drops after the patch", "lemon"), "csgbq 133: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 133: service latency drops after the patch", "a"), "round 133: service latency drops after the patch"),
    (("round 133: service latency drops after the patch", "zz"), "qntmc 133: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 133: service latency drops after the patch", "AgentU"),
        "ruyaw 133: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 133: service latency drops after the patch", "keyboard"),
        "bssor 133: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 133: service latency drops after the patch", "AA"), "round 133: service latency drops after the patch"),
    (
        ("round 133: the library caches every vector it sees", "key"),
        "bssxh 133: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 133: the library caches every vector it sees", "lemon"),
        "csgbq 133: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 133: the library caches every vector it sees", "a"), "round 133: the library caches every vector it sees"),
    (
        ("round 133: the library caches every vector it sees", "zz"),
        "qntmc 133: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 133: the library caches every vector it sees", "AgentU"),
        "ruyaw 133: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 133: the library caches every vector it sees", "keyboard"),
        "bssor 133: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 133: the library caches every vector it sees", "AA"),
        "round 133: the library caches every vector it sees",
    ),
    (("round 133: agents argue then the debate resolves", "key"), "bssxh 133: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 133: agents argue then the debate resolves", "lemon"), "csgbq 133: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 133: agents argue then the debate resolves", "a"), "round 133: agents argue then the debate resolves"),
    (("round 133: agents argue then the debate resolves", "zz"), "qntmc 133: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 133: agents argue then the debate resolves", "AgentU"),
        "ruyaw 133: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 133: agents argue then the debate resolves", "keyboard"),
        "bssor 133: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 133: agents argue then the debate resolves", "AA"), "round 133: agents argue then the debate resolves"),
    (("round 133: the filter keeps only strong matches", "key"), "bssxh 133: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 133: the filter keeps only strong matches", "lemon"), "csgbq 133: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 133: the filter keeps only strong matches", "a"), "round 133: the filter keeps only strong matches"),
    (("round 133: the filter keeps only strong matches", "zz"), "qntmc 133: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 133: the filter keeps only strong matches", "AgentU"), "ruyaw 133: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 133: the filter keeps only strong matches", "keyboard"),
        "bssor 133: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 133: the filter keeps only strong matches", "AA"), "round 133: the filter keeps only strong matches"),
    (("round 133: the model answers with a short reply", "key"), "bssxh 133: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 133: the model answers with a short reply", "lemon"), "csgbq 133: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 133: the model answers with a short reply", "a"), "round 133: the model answers with a short reply"),
    (("round 133: the model answers with a short reply", "zz"), "qntmc 133: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 133: the model answers with a short reply", "AgentU"), "ruyaw 133: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 133: the model answers with a short reply", "keyboard"),
        "bssor 133: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 133: the model answers with a short reply", "AA"), "round 133: the model answers with a short reply"),
    (
        ("round 133: the recorder stores the reasoning trace", "key"),
        "bssxh 133: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 133: the recorder stores the reasoning trace", "lemon"),
        "csgbq 133: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 133: the recorder stores the reasoning trace", "a"), "round 133: the recorder stores the reasoning trace"),
    (
        ("round 133: the recorder stores the reasoning trace", "zz"),
        "qntmc 133: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 133: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 133: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 133: the recorder stores the reasoning trace", "keyboard"),
        "bssor 133: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 133: the recorder stores the reasoning trace", "AA"),
        "round 133: the recorder stores the reasoning trace",
    ),
    (("round 133: the angel watches the processor run", "key"), "bssxh 133: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 133: the angel watches the processor run", "lemon"), "csgbq 133: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 133: the angel watches the processor run", "a"), "round 133: the angel watches the processor run"),
    (("round 133: the angel watches the processor run", "zz"), "qntmc 133: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 133: the angel watches the processor run", "AgentU"), "ruyaw 133: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 133: the angel watches the processor run", "keyboard"), "bssor 133: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 133: the angel watches the processor run", "AA"), "round 133: the angel watches the processor run"),
    (("round 133: angle of the vector decides the match", "key"), "bssxh 133: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 133: angle of the vector decides the match", "lemon"), "csgbq 133: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 133: angle of the vector decides the match", "a"), "round 133: angle of the vector decides the match"),
    (("round 133: angle of the vector decides the match", "zz"), "qntmc 133: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 133: angle of the vector decides the match", "AgentU"),
        "ruyaw 133: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 133: angle of the vector decides the match", "keyboard"),
        "bssor 133: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 133: angle of the vector decides the match", "AA"), "round 133: angle of the vector decides the match"),
    (
        ("round 133: the candle burns twice as long at night", "key"),
        "bssxh 133: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 133: the candle burns twice as long at night", "lemon"),
        "csgbq 133: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 133: the candle burns twice as long at night", "a"), "round 133: the candle burns twice as long at night"),
    (
        ("round 133: the candle burns twice as long at night", "zz"),
        "qntmc 133: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 133: the candle burns twice as long at night", "AgentU"),
        "ruyaw 133: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 133: the candle burns twice as long at night", "keyboard"),
        "bssor 133: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 133: the candle burns twice as long at night", "AA"),
        "round 133: the candle burns twice as long at night",
    ),
    (("round 133: a mirror of the universe in one line", "key"), "bssxh 133: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 133: a mirror of the universe in one line", "lemon"), "csgbq 133: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 133: a mirror of the universe in one line", "a"), "round 133: a mirror of the universe in one line"),
    (("round 133: a mirror of the universe in one line", "zz"), "qntmc 133: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 133: a mirror of the universe in one line", "AgentU"), "ruyaw 133: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 133: a mirror of the universe in one line", "keyboard"),
        "bssor 133: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 133: a mirror of the universe in one line", "AA"), "round 133: a mirror of the universe in one line"),
    (("round 133: the queue drains before the storm", "key"), "bssxh 133: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 133: the queue drains before the storm", "lemon"), "csgbq 133: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 133: the queue drains before the storm", "a"), "round 133: the queue drains before the storm"),
    (("round 133: the queue drains before the storm", "zz"), "qntmc 133: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 133: the queue drains before the storm", "AgentU"), "ruyaw 133: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 133: the queue drains before the storm", "keyboard"), "bssor 133: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 133: the queue drains before the storm", "AA"), "round 133: the queue drains before the storm"),
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
