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
    (("kitten126", "key"), "umrdil126"),
    (("kitten126", "lemon"), "vmfhry126"),
    (("kitten126", "a"), "kitten126"),
    (("kitten126", "zz"), "jhssdm126"),
    (("kitten126", "AgentU"), "koxgxh126"),
    (("kitten126", "keyboard"), "umrusn126"),
    (("kitten126", "AA"), "kitten126"),
    (("sitting126", "key"), "cmrdmlq126"),
    (("sitting126", "lemon"), "dmfhvyk126"),
    (("sitting126", "a"), "sitting126"),
    (("sitting126", "zz"), "rhsshmf126"),
    (("sitting126", "AgentU"), "soxgbhg126"),
    (("sitting126", "keyboard"), "cmruwnx126"),
    (("sitting126", "AA"), "sitting126"),
    (("agent126", "key"), "kkcxx126"),
    (("agent126", "lemon"), "lkqbg126"),
    (("agent126", "a"), "agent126"),
    (("agent126", "zz"), "zfdms126"),
    (("agent126", "AgentU"), "amiam126"),
    (("agent126", "keyboard"), "kkcoh126"),
    (("agent126", "AA"), "agent126"),
    (("angle126", "key"), "krevi126"),
    (("angle126", "lemon"), "lrszr126"),
    (("angle126", "a"), "angle126"),
    (("angle126", "zz"), "zmfkd126"),
    (("angle126", "AgentU"), "atkyx126"),
    (("angle126", "keyboard"), "krems126"),
    (("angle126", "AA"), "angle126"),
    (("universe126", "key"), "ergfipci126"),
    (("universe126", "lemon"), "frujrcwq126"),
    (("universe126", "a"), "universe126"),
    (("universe126", "zz"), "tmhudqrd126"),
    (("universe126", "AgentU"), "utmixlsk126"),
    (("universe126", "keyboard"), "ergwsrjh126"),
    (("universe126", "AA"), "universe126"),
    (("memory126", "key"), "wikyvw126"),
    (("memory126", "lemon"), "xiycej126"),
    (("memory126", "a"), "memory126"),
    (("memory126", "zz"), "ldlnqx126"),
    (("memory126", "AgentU"), "mkqbks126"),
    (("memory126", "keyboard"), "wikpfy126"),
    (("memory126", "AA"), "memory126"),
    (("stream126", "key"), "cxpoek126"),
    (("stream126", "lemon"), "dxdsnx126"),
    (("stream126", "a"), "stream126"),
    (("stream126", "zz"), "rsqdzl126"),
    (("stream126", "AgentU"), "szvrtg126"),
    (("stream126", "keyboard"), "cxpfom126"),
    (("stream126", "AA"), "stream126"),
    (("context126", "key"), "msldivd126"),
    (("context126", "lemon"), "nszhrix126"),
    (("context126", "a"), "context126"),
    (("context126", "zz"), "bnmsdws126"),
    (("context126", "AgentU"), "curgxrt126"),
    (("context126", "keyboard"), "mslusxk126"),
    (("context126", "AA"), "context126"),
    (("knowledge126", "key"), "urmgpcnkc126"),
    (("knowledge126", "lemon"), "vrakyphss126"),
    (("knowledge126", "a"), "knowledge126"),
    (("knowledge126", "zz"), "jmnvkdcfd126"),
    (("knowledge126", "AgentU"), "ktsjeydmi126"),
    (("knowledge126", "keyboard"), "urmxzeujo126"),
    (("knowledge126", "AA"), "knowledge126"),
    (("vector126", "key"), "fiadsp126"),
    (("vector126", "lemon"), "giohbc126"),
    (("vector126", "a"), "vector126"),
    (("vector126", "zz"), "udbsnq126"),
    (("vector126", "AgentU"), "vkgghl126"),
    (("vector126", "keyboard"), "fiaucr126"),
    (("vector126", "AA"), "vector126"),
    (("processor126", "key"), "zvmmiqcsp126"),
    (("processor126", "lemon"), "avaqrdwaf126"),
    (("processor126", "a"), "processor126"),
    (("processor126", "zz"), "oqnbdrrnq126"),
    (("processor126", "AgentU"), "pxspxmsuv126"),
    (("processor126", "keyboard"), "zvmdssjrb126"),
    (("processor126", "AA"), "processor126"),
    (("reasoning126", "key"), "biycslsre126"),
    (("reasoning126", "lemon"), "cimgbymzu126"),
    (("reasoning126", "a"), "reasoning126"),
    (("reasoning126", "zz"), "qdzrnmhmf126"),
    (("reasoning126", "AgentU"), "rkefhhitk126"),
    (("reasoning126", "keyboard"), "biytcnzqq126"),
    (("reasoning126", "AA"), "reasoning126"),
    (("machine126", "key"), "wearmlo126"),
    (("machine126", "lemon"), "xeovvyi126"),
    (("machine126", "a"), "machine126"),
    (("machine126", "zz"), "lzbghmd126"),
    (("machine126", "AgentU"), "mggubhe126"),
    (("machine126", "keyboard"), "weaiwnv126"),
    (("machine126", "AA"), "machine126"),
    (("learning126", "key"), "viybrgxk126"),
    (("learning126", "lemon"), "wimfatrs126"),
    (("learning126", "a"), "learning126"),
    (("learning126", "zz"), "kdzqmhmf126"),
    (("learning126", "AgentU"), "lkeegcnm126"),
    (("learning126", "keyboard"), "viysbiej126"),
    (("learning126", "AA"), "learning126"),
    (("model126", "key"), "wsbop126"),
    (("model126", "lemon"), "xspsy126"),
    (("model126", "a"), "model126"),
    (("model126", "zz"), "lncdk126"),
    (("model126", "AgentU"), "muhre126"),
    (("model126", "keyboard"), "wsbfz126"),
    (("model126", "AA"), "model126"),
    (("token126", "key"), "dsior126"),
    (("token126", "lemon"), "eswsa126"),
    (("token126", "a"), "token126"),
    (("token126", "zz"), "snjdm126"),
    (("token126", "AgentU"), "tuorg126"),
    (("token126", "keyboard"), "dsifb126"),
    (("token126", "AA"), "token126"),
    (("prompt126", "key"), "zvmwtr126"),
    (("prompt126", "lemon"), "avaace126"),
    (("prompt126", "a"), "prompt126"),
    (("prompt126", "zz"), "oqnlos126"),
    (("prompt126", "AgentU"), "pxszin126"),
    (("prompt126", "keyboard"), "zvmndt126"),
    (("prompt126", "AA"), "prompt126"),
    (("session126", "key"), "ciqcmmx126"),
    (("session126", "lemon"), "diegvzr126"),
    (("session126", "a"), "session126"),
    (("session126", "zz"), "rdrrhnm126"),
    (("session126", "AgentU"), "skwfbin126"),
    (("session126", "keyboard"), "ciqtwoe126"),
    (("session126", "AA"), "session126"),
    (("library126", "key"), "vmzbepi126"),
    (("library126", "lemon"), "wmnfncc126"),
    (("library126", "a"), "library126"),
    (("library126", "zz"), "khaqzqx126"),
    (("library126", "AgentU"), "lofetly126"),
    (("library126", "keyboard"), "vmzsorp126"),
    (("library126", "AA"), "library126"),
    (("service126", "key"), "cipfmao126"),
    (("service126", "lemon"), "didjvni126"),
    (("service126", "a"), "service126"),
    (("service126", "zz"), "rdquhbd126"),
    (("service126", "AgentU"), "skvibwe126"),
    (("service126", "keyboard"), "cipwwcv126"),
    (("service126", "AA"), "service126"),
    (("gateway126", "key"), "qeroayi126"),
    (("gateway126", "lemon"), "refsjlc126"),
    (("gateway126", "a"), "gateway126"),
    (("gateway126", "zz"), "fzsdvzx126"),
    (("gateway126", "AgentU"), "ggxrpuy126"),
    (("gateway126", "keyboard"), "qerfkap126"),
    (("gateway126", "AA"), "gateway126"),
    (("storage126", "key"), "cxmbeeo126"),
    (("storage126", "lemon"), "dxafnri126"),
    (("storage126", "a"), "storage126"),
    (("storage126", "zz"), "rsnqzfd126"),
    (("storage126", "AgentU"), "szsetae126"),
    (("storage126", "keyboard"), "cxmsogv126"),
    (("storage126", "AA"), "storage126"),
    (("network126", "key"), "xirgspu126"),
    (("network126", "lemon"), "yifkbco126"),
    (("network126", "a"), "network126"),
    (("network126", "zz"), "mdsvnqj126"),
    (("network126", "AgentU"), "nkxjhlk126"),
    (("network126", "keyboard"), "xirxcrb126"),
    (("network126", "AA"), "network126"),
    (("latency126", "key"), "verorai126"),
    (("latency126", "lemon"), "wefsanc126"),
    (("latency126", "a"), "latency126"),
    (("latency126", "zz"), "kzsdmbx126"),
    (("latency126", "AgentU"), "lgxrgwy126"),
    (("latency126", "keyboard"), "verfbcp126"),
    (("latency126", "AA"), "latency126"),
    (("buffer126", "key"), "lydpip126"),
    (("buffer126", "lemon"), "myrtrc126"),
    (("buffer126", "a"), "buffer126"),
    (("buffer126", "zz"), "ateedq126"),
    (("buffer126", "AgentU"), "bajsxl126"),
    (("buffer126", "keyboard"), "lydgsr126"),
    (("buffer126", "AA"), "buffer126"),
    (("queue126", "key"), "aycei126"),
    (("queue126", "lemon"), "byqir126"),
    (("queue126", "a"), "queue126"),
    (("queue126", "zz"), "ptdtd126"),
    (("queue126", "AgentU"), "qaihx126"),
    (("queue126", "keyboard"), "aycvs126"),
    (("queue126", "AA"), "queue126"),
    (("worker126", "key"), "gspuip126"),
    (("worker126", "lemon"), "hsdyrc126"),
    (("worker126", "a"), "worker126"),
    (("worker126", "zz"), "vnqjdq126"),
    (("worker126", "AgentU"), "wuvxxl126"),
    (("worker126", "keyboard"), "gsplsr126"),
    (("worker126", "AA"), "worker126"),
    (("kernel126", "key"), "uipxij126"),
    (("kernel126", "lemon"), "vidbrw126"),
    (("kernel126", "a"), "kernel126"),
    (("kernel126", "zz"), "jdqmdk126"),
    (("kernel126", "AgentU"), "kkvaxf126"),
    (("kernel126", "keyboard"), "uiposl126"),
    (("kernel126", "AA"), "kernel126"),
    (("signal126", "key"), "cmexej126"),
    (("signal126", "lemon"), "dmsbnw126"),
    (("signal126", "a"), "signal126"),
    (("signal126", "zz"), "rhfmzk126"),
    (("signal126", "AgentU"), "sokatf126"),
    (("signal126", "keyboard"), "cmeool126"),
    (("signal126", "AA"), "signal126"),
    (("packet126", "key"), "zeauir126"),
    (("packet126", "lemon"), "aeoyre126"),
    (("packet126", "a"), "packet126"),
    (("packet126", "zz"), "ozbjds126"),
    (("packet126", "AgentU"), "pggxxn126"),
    (("packet126", "keyboard"), "zealst126"),
    (("packet126", "AA"), "packet126"),
    (("router126", "key"), "bssdip126"),
    (("router126", "lemon"), "csghrc126"),
    (("router126", "a"), "router126"),
    (("router126", "zz"), "qntsdq126"),
    (("router126", "AgentU"), "ruygxl126"),
    (("router126", "keyboard"), "bssusr126"),
    (("router126", "AA"), "router126"),
    (("cluster126", "key"), "mpscxcb126"),
    (("cluster126", "lemon"), "npgggpv126"),
    (("cluster126", "a"), "cluster126"),
    (("cluster126", "zz"), "bktrsdq126"),
    (("cluster126", "AgentU"), "cryfmyr126"),
    (("cluster126", "keyboard"), "mpsthei126"),
    (("cluster126", "AA"), "cluster126"),
    (("mirror126", "key"), "wmpbsp126"),
    (("mirror126", "lemon"), "xmdfbc126"),
    (("mirror126", "a"), "mirror126"),
    (("mirror126", "zz"), "lhqqnq126"),
    (("mirror126", "AgentU"), "movehl126"),
    (("mirror126", "keyboard"), "wmpscr126"),
    (("mirror126", "AA"), "mirror126"),
    (("filter126", "key"), "pmjdip126"),
    (("filter126", "lemon"), "qmxhrc126"),
    (("filter126", "a"), "filter126"),
    (("filter126", "zz"), "ehksdq126"),
    (("filter126", "AgentU"), "fopgxl126"),
    (("filter126", "keyboard"), "pmjusr126"),
    (("filter126", "AA"), "filter126"),
    (("ranking126", "key"), "belumlq126"),
    (("ranking126", "lemon"), "cezyvyk126"),
    (("ranking126", "a"), "ranking126"),
    (("ranking126", "zz"), "qzmjhmf126"),
    (("ranking126", "AgentU"), "rgrxbhg126"),
    (("ranking126", "keyboard"), "bellwnx126"),
    (("ranking126", "AA"), "ranking126"),
    (("encoding126", "key"), "orayhgxk126"),
    (("encoding126", "lemon"), "procqtrs126"),
    (("encoding126", "a"), "encoding126"),
    (("encoding126", "zz"), "dmbnchmf126"),
    (("encoding126", "AgentU"), "etgbwcnm126"),
    (("encoding126", "keyboard"), "orapriej126"),
    (("encoding126", "AA"), "encoding126"),
    (("mapping126", "key"), "wenzmlq126"),
    (("mapping126", "lemon"), "xebdvyk126"),
    (("mapping126", "a"), "mapping126"),
    (("mapping126", "zz"), "lzoohmf126"),
    (("mapping126", "AgentU"), "mgtcbhg126"),
    (("mapping126", "keyboard"), "wenqwnx126"),
    (("mapping126", "AA"), "mapping126"),
    (("record126", "key"), "biayvb126"),
    (("record126", "lemon"), "cioceo126"),
    (("record126", "a"), "record126"),
    (("record126", "zz"), "qdbnqc126"),
    (("record126", "AgentU"), "rkgbkx126"),
    (("record126", "keyboard"), "biapfd126"),
    (("record126", "AA"), "record126"),
    (("candle126", "key"), "melnpc126"),
    (("candle126", "lemon"), "nezryp126"),
    (("candle126", "a"), "candle126"),
    (("candle126", "zz"), "bzmckd126"),
    (("candle126", "AgentU"), "cgrqey126"),
    (("candle126", "keyboard"), "meleze126"),
    (("candle126", "AA"), "candle126"),
    (("thread126", "key"), "dlpoeb126"),
    (("thread126", "lemon"), "eldsno126"),
    (("thread126", "a"), "thread126"),
    (("thread126", "zz"), "sgqdzc126"),
    (("thread126", "AgentU"), "tnvrtx126"),
    (("thread126", "keyboard"), "dlpfod126"),
    (("thread126", "AA"), "thread126"),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 126: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 126: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "a"),
        "round 126: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 126: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 126: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 126: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", "AA"),
        "round 126: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "key"),
        "bssxh 126: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 126: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "a"),
        "round 126: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 126: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 126: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 126: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", "AA"),
        "round 126: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 126: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 126: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "a"),
        "round 126: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 126: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 126: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 126: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", "AA"),
        "round 126: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 126: the processor reads the record then stops", "key"),
        "bssxh 126: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 126: the processor reads the record then stops", "lemon"),
        "csgbq 126: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 126: the processor reads the record then stops", "a"),
        "round 126: the processor reads the record then stops",
    ),
    (
        ("round 126: the processor reads the record then stops", "zz"),
        "qntmc 126: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 126: the processor reads the record then stops", "AgentU"),
        "ruyaw 126: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 126: the processor reads the record then stops", "keyboard"),
        "bssor 126: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 126: the processor reads the record then stops", "AA"),
        "round 126: the processor reads the record then stops",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "key"),
        "bssxh 126: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "lemon"),
        "csgbq 126: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "a"),
        "round 126: a worker pulls the next task from the queue",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "zz"),
        "qntmc 126: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 126: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "keyboard"),
        "bssor 126: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 126: a worker pulls the next task from the queue", "AA"),
        "round 126: a worker pulls the next task from the queue",
    ),
    (
        ("round 126: signals travel through the network layer", "key"),
        "bssxh 126: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 126: signals travel through the network layer", "lemon"),
        "csgbq 126: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 126: signals travel through the network layer", "a"),
        "round 126: signals travel through the network layer",
    ),
    (
        ("round 126: signals travel through the network layer", "zz"),
        "qntmc 126: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 126: signals travel through the network layer", "AgentU"),
        "ruyaw 126: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 126: signals travel through the network layer", "keyboard"),
        "bssor 126: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 126: signals travel through the network layer", "AA"),
        "round 126: signals travel through the network layer",
    ),
    (
        ("round 126: the gateway routes each request by policy", "key"),
        "bssxh 126: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 126: the gateway routes each request by policy", "lemon"),
        "csgbq 126: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 126: the gateway routes each request by policy", "a"),
        "round 126: the gateway routes each request by policy",
    ),
    (
        ("round 126: the gateway routes each request by policy", "zz"),
        "qntmc 126: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 126: the gateway routes each request by policy", "AgentU"),
        "ruyaw 126: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 126: the gateway routes each request by policy", "keyboard"),
        "bssor 126: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 126: the gateway routes each request by policy", "AA"),
        "round 126: the gateway routes each request by policy",
    ),
    (("round 126: memory grows until the buffer is full", "key"), "bssxh 126: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 126: memory grows until the buffer is full", "lemon"), "csgbq 126: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 126: memory grows until the buffer is full", "a"), "round 126: memory grows until the buffer is full"),
    (("round 126: memory grows until the buffer is full", "zz"), "qntmc 126: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 126: memory grows until the buffer is full", "AgentU"),
        "ruyaw 126: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 126: memory grows until the buffer is full", "keyboard"),
        "bssor 126: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 126: memory grows until the buffer is full", "AA"), "round 126: memory grows until the buffer is full"),
    (("round 126: the cluster mirrors every packet twice", "key"), "bssxh 126: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 126: the cluster mirrors every packet twice", "lemon"),
        "csgbq 126: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 126: the cluster mirrors every packet twice", "a"), "round 126: the cluster mirrors every packet twice"),
    (("round 126: the cluster mirrors every packet twice", "zz"), "qntmc 126: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 126: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 126: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 126: the cluster mirrors every packet twice", "keyboard"),
        "bssor 126: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 126: the cluster mirrors every packet twice", "AA"), "round 126: the cluster mirrors every packet twice"),
    (
        ("round 126: ranking uses tokens learned from the corpus", "key"),
        "bssxh 126: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 126: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", "a"),
        "round 126: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 126: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 126: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 126: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", "AA"),
        "round 126: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 126: a long session ends when the candle dies", "key"),
        "bssxh 126: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 126: a long session ends when the candle dies", "lemon"),
        "csgbq 126: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 126: a long session ends when the candle dies", "a"),
        "round 126: a long session ends when the candle dies",
    ),
    (
        ("round 126: a long session ends when the candle dies", "zz"),
        "qntmc 126: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 126: a long session ends when the candle dies", "AgentU"),
        "ruyaw 126: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 126: a long session ends when the candle dies", "keyboard"),
        "bssor 126: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 126: a long session ends when the candle dies", "AA"),
        "round 126: a long session ends when the candle dies",
    ),
    (("round 126: encode the prompt then map the result", "key"), "bssxh 126: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 126: encode the prompt then map the result", "lemon"), "csgbq 126: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 126: encode the prompt then map the result", "a"), "round 126: encode the prompt then map the result"),
    (("round 126: encode the prompt then map the result", "zz"), "qntmc 126: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 126: encode the prompt then map the result", "AgentU"),
        "ruyaw 126: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 126: encode the prompt then map the result", "keyboard"),
        "bssor 126: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 126: encode the prompt then map the result", "AA"), "round 126: encode the prompt then map the result"),
    (("round 126: the kernel wakes the worker at dawn", "key"), "bssxh 126: rri iovlop ukocc xfo ambocb er neux"),
    (("round 126: the kernel wakes the worker at dawn", "lemon"), "csgbq 126: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 126: the kernel wakes the worker at dawn", "a"), "round 126: the kernel wakes the worker at dawn"),
    (("round 126: the kernel wakes the worker at dawn", "zz"), "qntmc 126: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 126: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 126: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 126: the kernel wakes the worker at dawn", "keyboard"), "bssor 126: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 126: the kernel wakes the worker at dawn", "AA"), "round 126: the kernel wakes the worker at dawn"),
    (("round 126: service latency drops after the patch", "key"), "bssxh 126: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 126: service latency drops after the patch", "lemon"), "csgbq 126: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 126: service latency drops after the patch", "a"), "round 126: service latency drops after the patch"),
    (("round 126: service latency drops after the patch", "zz"), "qntmc 126: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 126: service latency drops after the patch", "AgentU"),
        "ruyaw 126: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 126: service latency drops after the patch", "keyboard"),
        "bssor 126: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 126: service latency drops after the patch", "AA"), "round 126: service latency drops after the patch"),
    (
        ("round 126: the library caches every vector it sees", "key"),
        "bssxh 126: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 126: the library caches every vector it sees", "lemon"),
        "csgbq 126: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 126: the library caches every vector it sees", "a"), "round 126: the library caches every vector it sees"),
    (
        ("round 126: the library caches every vector it sees", "zz"),
        "qntmc 126: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 126: the library caches every vector it sees", "AgentU"),
        "ruyaw 126: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 126: the library caches every vector it sees", "keyboard"),
        "bssor 126: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 126: the library caches every vector it sees", "AA"),
        "round 126: the library caches every vector it sees",
    ),
    (("round 126: agents argue then the debate resolves", "key"), "bssxh 126: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 126: agents argue then the debate resolves", "lemon"), "csgbq 126: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 126: agents argue then the debate resolves", "a"), "round 126: agents argue then the debate resolves"),
    (("round 126: agents argue then the debate resolves", "zz"), "qntmc 126: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 126: agents argue then the debate resolves", "AgentU"),
        "ruyaw 126: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 126: agents argue then the debate resolves", "keyboard"),
        "bssor 126: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 126: agents argue then the debate resolves", "AA"), "round 126: agents argue then the debate resolves"),
    (("round 126: the filter keeps only strong matches", "key"), "bssxh 126: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 126: the filter keeps only strong matches", "lemon"), "csgbq 126: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 126: the filter keeps only strong matches", "a"), "round 126: the filter keeps only strong matches"),
    (("round 126: the filter keeps only strong matches", "zz"), "qntmc 126: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 126: the filter keeps only strong matches", "AgentU"), "ruyaw 126: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 126: the filter keeps only strong matches", "keyboard"),
        "bssor 126: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 126: the filter keeps only strong matches", "AA"), "round 126: the filter keeps only strong matches"),
    (("round 126: the model answers with a short reply", "key"), "bssxh 126: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 126: the model answers with a short reply", "lemon"), "csgbq 126: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 126: the model answers with a short reply", "a"), "round 126: the model answers with a short reply"),
    (("round 126: the model answers with a short reply", "zz"), "qntmc 126: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 126: the model answers with a short reply", "AgentU"), "ruyaw 126: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 126: the model answers with a short reply", "keyboard"),
        "bssor 126: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 126: the model answers with a short reply", "AA"), "round 126: the model answers with a short reply"),
    (
        ("round 126: the recorder stores the reasoning trace", "key"),
        "bssxh 126: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 126: the recorder stores the reasoning trace", "lemon"),
        "csgbq 126: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 126: the recorder stores the reasoning trace", "a"), "round 126: the recorder stores the reasoning trace"),
    (
        ("round 126: the recorder stores the reasoning trace", "zz"),
        "qntmc 126: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 126: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 126: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 126: the recorder stores the reasoning trace", "keyboard"),
        "bssor 126: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 126: the recorder stores the reasoning trace", "AA"),
        "round 126: the recorder stores the reasoning trace",
    ),
    (("round 126: the angel watches the processor run", "key"), "bssxh 126: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 126: the angel watches the processor run", "lemon"), "csgbq 126: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 126: the angel watches the processor run", "a"), "round 126: the angel watches the processor run"),
    (("round 126: the angel watches the processor run", "zz"), "qntmc 126: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 126: the angel watches the processor run", "AgentU"), "ruyaw 126: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 126: the angel watches the processor run", "keyboard"), "bssor 126: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 126: the angel watches the processor run", "AA"), "round 126: the angel watches the processor run"),
    (("round 126: angle of the vector decides the match", "key"), "bssxh 126: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 126: angle of the vector decides the match", "lemon"), "csgbq 126: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 126: angle of the vector decides the match", "a"), "round 126: angle of the vector decides the match"),
    (("round 126: angle of the vector decides the match", "zz"), "qntmc 126: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 126: angle of the vector decides the match", "AgentU"),
        "ruyaw 126: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 126: angle of the vector decides the match", "keyboard"),
        "bssor 126: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 126: angle of the vector decides the match", "AA"), "round 126: angle of the vector decides the match"),
    (
        ("round 126: the candle burns twice as long at night", "key"),
        "bssxh 126: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 126: the candle burns twice as long at night", "lemon"),
        "csgbq 126: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 126: the candle burns twice as long at night", "a"), "round 126: the candle burns twice as long at night"),
    (
        ("round 126: the candle burns twice as long at night", "zz"),
        "qntmc 126: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 126: the candle burns twice as long at night", "AgentU"),
        "ruyaw 126: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 126: the candle burns twice as long at night", "keyboard"),
        "bssor 126: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 126: the candle burns twice as long at night", "AA"),
        "round 126: the candle burns twice as long at night",
    ),
    (("round 126: a mirror of the universe in one line", "key"), "bssxh 126: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 126: a mirror of the universe in one line", "lemon"), "csgbq 126: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 126: a mirror of the universe in one line", "a"), "round 126: a mirror of the universe in one line"),
    (("round 126: a mirror of the universe in one line", "zz"), "qntmc 126: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 126: a mirror of the universe in one line", "AgentU"), "ruyaw 126: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 126: a mirror of the universe in one line", "keyboard"),
        "bssor 126: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 126: a mirror of the universe in one line", "AA"), "round 126: a mirror of the universe in one line"),
    (("round 126: the queue drains before the storm", "key"), "bssxh 126: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 126: the queue drains before the storm", "lemon"), "csgbq 126: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 126: the queue drains before the storm", "a"), "round 126: the queue drains before the storm"),
    (("round 126: the queue drains before the storm", "zz"), "qntmc 126: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 126: the queue drains before the storm", "AgentU"), "ruyaw 126: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 126: the queue drains before the storm", "keyboard"), "bssor 126: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 126: the queue drains before the storm", "AA"), "round 126: the queue drains before the storm"),
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
