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
    (("kitten199", "key"), "umrdil199"),
    (("kitten199", "lemon"), "vmfhry199"),
    (("kitten199", "a"), "kitten199"),
    (("kitten199", "zz"), "jhssdm199"),
    (("kitten199", "AgentU"), "koxgxh199"),
    (("kitten199", "keyboard"), "umrusn199"),
    (("kitten199", "AA"), "kitten199"),
    (("sitting199", "key"), "cmrdmlq199"),
    (("sitting199", "lemon"), "dmfhvyk199"),
    (("sitting199", "a"), "sitting199"),
    (("sitting199", "zz"), "rhsshmf199"),
    (("sitting199", "AgentU"), "soxgbhg199"),
    (("sitting199", "keyboard"), "cmruwnx199"),
    (("sitting199", "AA"), "sitting199"),
    (("agent199", "key"), "kkcxx199"),
    (("agent199", "lemon"), "lkqbg199"),
    (("agent199", "a"), "agent199"),
    (("agent199", "zz"), "zfdms199"),
    (("agent199", "AgentU"), "amiam199"),
    (("agent199", "keyboard"), "kkcoh199"),
    (("agent199", "AA"), "agent199"),
    (("angle199", "key"), "krevi199"),
    (("angle199", "lemon"), "lrszr199"),
    (("angle199", "a"), "angle199"),
    (("angle199", "zz"), "zmfkd199"),
    (("angle199", "AgentU"), "atkyx199"),
    (("angle199", "keyboard"), "krems199"),
    (("angle199", "AA"), "angle199"),
    (("universe199", "key"), "ergfipci199"),
    (("universe199", "lemon"), "frujrcwq199"),
    (("universe199", "a"), "universe199"),
    (("universe199", "zz"), "tmhudqrd199"),
    (("universe199", "AgentU"), "utmixlsk199"),
    (("universe199", "keyboard"), "ergwsrjh199"),
    (("universe199", "AA"), "universe199"),
    (("memory199", "key"), "wikyvw199"),
    (("memory199", "lemon"), "xiycej199"),
    (("memory199", "a"), "memory199"),
    (("memory199", "zz"), "ldlnqx199"),
    (("memory199", "AgentU"), "mkqbks199"),
    (("memory199", "keyboard"), "wikpfy199"),
    (("memory199", "AA"), "memory199"),
    (("stream199", "key"), "cxpoek199"),
    (("stream199", "lemon"), "dxdsnx199"),
    (("stream199", "a"), "stream199"),
    (("stream199", "zz"), "rsqdzl199"),
    (("stream199", "AgentU"), "szvrtg199"),
    (("stream199", "keyboard"), "cxpfom199"),
    (("stream199", "AA"), "stream199"),
    (("context199", "key"), "msldivd199"),
    (("context199", "lemon"), "nszhrix199"),
    (("context199", "a"), "context199"),
    (("context199", "zz"), "bnmsdws199"),
    (("context199", "AgentU"), "curgxrt199"),
    (("context199", "keyboard"), "mslusxk199"),
    (("context199", "AA"), "context199"),
    (("knowledge199", "key"), "urmgpcnkc199"),
    (("knowledge199", "lemon"), "vrakyphss199"),
    (("knowledge199", "a"), "knowledge199"),
    (("knowledge199", "zz"), "jmnvkdcfd199"),
    (("knowledge199", "AgentU"), "ktsjeydmi199"),
    (("knowledge199", "keyboard"), "urmxzeujo199"),
    (("knowledge199", "AA"), "knowledge199"),
    (("vector199", "key"), "fiadsp199"),
    (("vector199", "lemon"), "giohbc199"),
    (("vector199", "a"), "vector199"),
    (("vector199", "zz"), "udbsnq199"),
    (("vector199", "AgentU"), "vkgghl199"),
    (("vector199", "keyboard"), "fiaucr199"),
    (("vector199", "AA"), "vector199"),
    (("processor199", "key"), "zvmmiqcsp199"),
    (("processor199", "lemon"), "avaqrdwaf199"),
    (("processor199", "a"), "processor199"),
    (("processor199", "zz"), "oqnbdrrnq199"),
    (("processor199", "AgentU"), "pxspxmsuv199"),
    (("processor199", "keyboard"), "zvmdssjrb199"),
    (("processor199", "AA"), "processor199"),
    (("reasoning199", "key"), "biycslsre199"),
    (("reasoning199", "lemon"), "cimgbymzu199"),
    (("reasoning199", "a"), "reasoning199"),
    (("reasoning199", "zz"), "qdzrnmhmf199"),
    (("reasoning199", "AgentU"), "rkefhhitk199"),
    (("reasoning199", "keyboard"), "biytcnzqq199"),
    (("reasoning199", "AA"), "reasoning199"),
    (("machine199", "key"), "wearmlo199"),
    (("machine199", "lemon"), "xeovvyi199"),
    (("machine199", "a"), "machine199"),
    (("machine199", "zz"), "lzbghmd199"),
    (("machine199", "AgentU"), "mggubhe199"),
    (("machine199", "keyboard"), "weaiwnv199"),
    (("machine199", "AA"), "machine199"),
    (("learning199", "key"), "viybrgxk199"),
    (("learning199", "lemon"), "wimfatrs199"),
    (("learning199", "a"), "learning199"),
    (("learning199", "zz"), "kdzqmhmf199"),
    (("learning199", "AgentU"), "lkeegcnm199"),
    (("learning199", "keyboard"), "viysbiej199"),
    (("learning199", "AA"), "learning199"),
    (("model199", "key"), "wsbop199"),
    (("model199", "lemon"), "xspsy199"),
    (("model199", "a"), "model199"),
    (("model199", "zz"), "lncdk199"),
    (("model199", "AgentU"), "muhre199"),
    (("model199", "keyboard"), "wsbfz199"),
    (("model199", "AA"), "model199"),
    (("token199", "key"), "dsior199"),
    (("token199", "lemon"), "eswsa199"),
    (("token199", "a"), "token199"),
    (("token199", "zz"), "snjdm199"),
    (("token199", "AgentU"), "tuorg199"),
    (("token199", "keyboard"), "dsifb199"),
    (("token199", "AA"), "token199"),
    (("prompt199", "key"), "zvmwtr199"),
    (("prompt199", "lemon"), "avaace199"),
    (("prompt199", "a"), "prompt199"),
    (("prompt199", "zz"), "oqnlos199"),
    (("prompt199", "AgentU"), "pxszin199"),
    (("prompt199", "keyboard"), "zvmndt199"),
    (("prompt199", "AA"), "prompt199"),
    (("session199", "key"), "ciqcmmx199"),
    (("session199", "lemon"), "diegvzr199"),
    (("session199", "a"), "session199"),
    (("session199", "zz"), "rdrrhnm199"),
    (("session199", "AgentU"), "skwfbin199"),
    (("session199", "keyboard"), "ciqtwoe199"),
    (("session199", "AA"), "session199"),
    (("library199", "key"), "vmzbepi199"),
    (("library199", "lemon"), "wmnfncc199"),
    (("library199", "a"), "library199"),
    (("library199", "zz"), "khaqzqx199"),
    (("library199", "AgentU"), "lofetly199"),
    (("library199", "keyboard"), "vmzsorp199"),
    (("library199", "AA"), "library199"),
    (("service199", "key"), "cipfmao199"),
    (("service199", "lemon"), "didjvni199"),
    (("service199", "a"), "service199"),
    (("service199", "zz"), "rdquhbd199"),
    (("service199", "AgentU"), "skvibwe199"),
    (("service199", "keyboard"), "cipwwcv199"),
    (("service199", "AA"), "service199"),
    (("gateway199", "key"), "qeroayi199"),
    (("gateway199", "lemon"), "refsjlc199"),
    (("gateway199", "a"), "gateway199"),
    (("gateway199", "zz"), "fzsdvzx199"),
    (("gateway199", "AgentU"), "ggxrpuy199"),
    (("gateway199", "keyboard"), "qerfkap199"),
    (("gateway199", "AA"), "gateway199"),
    (("storage199", "key"), "cxmbeeo199"),
    (("storage199", "lemon"), "dxafnri199"),
    (("storage199", "a"), "storage199"),
    (("storage199", "zz"), "rsnqzfd199"),
    (("storage199", "AgentU"), "szsetae199"),
    (("storage199", "keyboard"), "cxmsogv199"),
    (("storage199", "AA"), "storage199"),
    (("network199", "key"), "xirgspu199"),
    (("network199", "lemon"), "yifkbco199"),
    (("network199", "a"), "network199"),
    (("network199", "zz"), "mdsvnqj199"),
    (("network199", "AgentU"), "nkxjhlk199"),
    (("network199", "keyboard"), "xirxcrb199"),
    (("network199", "AA"), "network199"),
    (("latency199", "key"), "verorai199"),
    (("latency199", "lemon"), "wefsanc199"),
    (("latency199", "a"), "latency199"),
    (("latency199", "zz"), "kzsdmbx199"),
    (("latency199", "AgentU"), "lgxrgwy199"),
    (("latency199", "keyboard"), "verfbcp199"),
    (("latency199", "AA"), "latency199"),
    (("buffer199", "key"), "lydpip199"),
    (("buffer199", "lemon"), "myrtrc199"),
    (("buffer199", "a"), "buffer199"),
    (("buffer199", "zz"), "ateedq199"),
    (("buffer199", "AgentU"), "bajsxl199"),
    (("buffer199", "keyboard"), "lydgsr199"),
    (("buffer199", "AA"), "buffer199"),
    (("queue199", "key"), "aycei199"),
    (("queue199", "lemon"), "byqir199"),
    (("queue199", "a"), "queue199"),
    (("queue199", "zz"), "ptdtd199"),
    (("queue199", "AgentU"), "qaihx199"),
    (("queue199", "keyboard"), "aycvs199"),
    (("queue199", "AA"), "queue199"),
    (("worker199", "key"), "gspuip199"),
    (("worker199", "lemon"), "hsdyrc199"),
    (("worker199", "a"), "worker199"),
    (("worker199", "zz"), "vnqjdq199"),
    (("worker199", "AgentU"), "wuvxxl199"),
    (("worker199", "keyboard"), "gsplsr199"),
    (("worker199", "AA"), "worker199"),
    (("kernel199", "key"), "uipxij199"),
    (("kernel199", "lemon"), "vidbrw199"),
    (("kernel199", "a"), "kernel199"),
    (("kernel199", "zz"), "jdqmdk199"),
    (("kernel199", "AgentU"), "kkvaxf199"),
    (("kernel199", "keyboard"), "uiposl199"),
    (("kernel199", "AA"), "kernel199"),
    (("signal199", "key"), "cmexej199"),
    (("signal199", "lemon"), "dmsbnw199"),
    (("signal199", "a"), "signal199"),
    (("signal199", "zz"), "rhfmzk199"),
    (("signal199", "AgentU"), "sokatf199"),
    (("signal199", "keyboard"), "cmeool199"),
    (("signal199", "AA"), "signal199"),
    (("packet199", "key"), "zeauir199"),
    (("packet199", "lemon"), "aeoyre199"),
    (("packet199", "a"), "packet199"),
    (("packet199", "zz"), "ozbjds199"),
    (("packet199", "AgentU"), "pggxxn199"),
    (("packet199", "keyboard"), "zealst199"),
    (("packet199", "AA"), "packet199"),
    (("router199", "key"), "bssdip199"),
    (("router199", "lemon"), "csghrc199"),
    (("router199", "a"), "router199"),
    (("router199", "zz"), "qntsdq199"),
    (("router199", "AgentU"), "ruygxl199"),
    (("router199", "keyboard"), "bssusr199"),
    (("router199", "AA"), "router199"),
    (("cluster199", "key"), "mpscxcb199"),
    (("cluster199", "lemon"), "npgggpv199"),
    (("cluster199", "a"), "cluster199"),
    (("cluster199", "zz"), "bktrsdq199"),
    (("cluster199", "AgentU"), "cryfmyr199"),
    (("cluster199", "keyboard"), "mpsthei199"),
    (("cluster199", "AA"), "cluster199"),
    (("mirror199", "key"), "wmpbsp199"),
    (("mirror199", "lemon"), "xmdfbc199"),
    (("mirror199", "a"), "mirror199"),
    (("mirror199", "zz"), "lhqqnq199"),
    (("mirror199", "AgentU"), "movehl199"),
    (("mirror199", "keyboard"), "wmpscr199"),
    (("mirror199", "AA"), "mirror199"),
    (("filter199", "key"), "pmjdip199"),
    (("filter199", "lemon"), "qmxhrc199"),
    (("filter199", "a"), "filter199"),
    (("filter199", "zz"), "ehksdq199"),
    (("filter199", "AgentU"), "fopgxl199"),
    (("filter199", "keyboard"), "pmjusr199"),
    (("filter199", "AA"), "filter199"),
    (("ranking199", "key"), "belumlq199"),
    (("ranking199", "lemon"), "cezyvyk199"),
    (("ranking199", "a"), "ranking199"),
    (("ranking199", "zz"), "qzmjhmf199"),
    (("ranking199", "AgentU"), "rgrxbhg199"),
    (("ranking199", "keyboard"), "bellwnx199"),
    (("ranking199", "AA"), "ranking199"),
    (("encoding199", "key"), "orayhgxk199"),
    (("encoding199", "lemon"), "procqtrs199"),
    (("encoding199", "a"), "encoding199"),
    (("encoding199", "zz"), "dmbnchmf199"),
    (("encoding199", "AgentU"), "etgbwcnm199"),
    (("encoding199", "keyboard"), "orapriej199"),
    (("encoding199", "AA"), "encoding199"),
    (("mapping199", "key"), "wenzmlq199"),
    (("mapping199", "lemon"), "xebdvyk199"),
    (("mapping199", "a"), "mapping199"),
    (("mapping199", "zz"), "lzoohmf199"),
    (("mapping199", "AgentU"), "mgtcbhg199"),
    (("mapping199", "keyboard"), "wenqwnx199"),
    (("mapping199", "AA"), "mapping199"),
    (("record199", "key"), "biayvb199"),
    (("record199", "lemon"), "cioceo199"),
    (("record199", "a"), "record199"),
    (("record199", "zz"), "qdbnqc199"),
    (("record199", "AgentU"), "rkgbkx199"),
    (("record199", "keyboard"), "biapfd199"),
    (("record199", "AA"), "record199"),
    (("candle199", "key"), "melnpc199"),
    (("candle199", "lemon"), "nezryp199"),
    (("candle199", "a"), "candle199"),
    (("candle199", "zz"), "bzmckd199"),
    (("candle199", "AgentU"), "cgrqey199"),
    (("candle199", "keyboard"), "meleze199"),
    (("candle199", "AA"), "candle199"),
    (("thread199", "key"), "dlpoeb199"),
    (("thread199", "lemon"), "eldsno199"),
    (("thread199", "a"), "thread199"),
    (("thread199", "zz"), "sgqdzc199"),
    (("thread199", "AgentU"), "tnvrtx199"),
    (("thread199", "keyboard"), "dlpfod199"),
    (("thread199", "AA"), "thread199"),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 199: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 199: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "a"),
        "round 199: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 199: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 199: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 199: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", "AA"),
        "round 199: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "key"),
        "bssxh 199: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 199: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "a"),
        "round 199: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 199: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 199: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 199: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", "AA"),
        "round 199: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 199: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 199: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "a"),
        "round 199: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 199: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 199: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 199: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", "AA"),
        "round 199: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 199: the processor reads the record then stops", "key"),
        "bssxh 199: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 199: the processor reads the record then stops", "lemon"),
        "csgbq 199: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 199: the processor reads the record then stops", "a"),
        "round 199: the processor reads the record then stops",
    ),
    (
        ("round 199: the processor reads the record then stops", "zz"),
        "qntmc 199: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 199: the processor reads the record then stops", "AgentU"),
        "ruyaw 199: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 199: the processor reads the record then stops", "keyboard"),
        "bssor 199: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 199: the processor reads the record then stops", "AA"),
        "round 199: the processor reads the record then stops",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "key"),
        "bssxh 199: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "lemon"),
        "csgbq 199: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "a"),
        "round 199: a worker pulls the next task from the queue",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "zz"),
        "qntmc 199: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 199: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "keyboard"),
        "bssor 199: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 199: a worker pulls the next task from the queue", "AA"),
        "round 199: a worker pulls the next task from the queue",
    ),
    (
        ("round 199: signals travel through the network layer", "key"),
        "bssxh 199: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 199: signals travel through the network layer", "lemon"),
        "csgbq 199: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 199: signals travel through the network layer", "a"),
        "round 199: signals travel through the network layer",
    ),
    (
        ("round 199: signals travel through the network layer", "zz"),
        "qntmc 199: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 199: signals travel through the network layer", "AgentU"),
        "ruyaw 199: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 199: signals travel through the network layer", "keyboard"),
        "bssor 199: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 199: signals travel through the network layer", "AA"),
        "round 199: signals travel through the network layer",
    ),
    (
        ("round 199: the gateway routes each request by policy", "key"),
        "bssxh 199: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 199: the gateway routes each request by policy", "lemon"),
        "csgbq 199: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 199: the gateway routes each request by policy", "a"),
        "round 199: the gateway routes each request by policy",
    ),
    (
        ("round 199: the gateway routes each request by policy", "zz"),
        "qntmc 199: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 199: the gateway routes each request by policy", "AgentU"),
        "ruyaw 199: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 199: the gateway routes each request by policy", "keyboard"),
        "bssor 199: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 199: the gateway routes each request by policy", "AA"),
        "round 199: the gateway routes each request by policy",
    ),
    (("round 199: memory grows until the buffer is full", "key"), "bssxh 199: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 199: memory grows until the buffer is full", "lemon"), "csgbq 199: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 199: memory grows until the buffer is full", "a"), "round 199: memory grows until the buffer is full"),
    (("round 199: memory grows until the buffer is full", "zz"), "qntmc 199: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 199: memory grows until the buffer is full", "AgentU"),
        "ruyaw 199: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 199: memory grows until the buffer is full", "keyboard"),
        "bssor 199: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 199: memory grows until the buffer is full", "AA"), "round 199: memory grows until the buffer is full"),
    (("round 199: the cluster mirrors every packet twice", "key"), "bssxh 199: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 199: the cluster mirrors every packet twice", "lemon"),
        "csgbq 199: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 199: the cluster mirrors every packet twice", "a"), "round 199: the cluster mirrors every packet twice"),
    (("round 199: the cluster mirrors every packet twice", "zz"), "qntmc 199: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 199: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 199: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 199: the cluster mirrors every packet twice", "keyboard"),
        "bssor 199: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 199: the cluster mirrors every packet twice", "AA"), "round 199: the cluster mirrors every packet twice"),
    (
        ("round 199: ranking uses tokens learned from the corpus", "key"),
        "bssxh 199: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 199: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", "a"),
        "round 199: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 199: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 199: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 199: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", "AA"),
        "round 199: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 199: a long session ends when the candle dies", "key"),
        "bssxh 199: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 199: a long session ends when the candle dies", "lemon"),
        "csgbq 199: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 199: a long session ends when the candle dies", "a"),
        "round 199: a long session ends when the candle dies",
    ),
    (
        ("round 199: a long session ends when the candle dies", "zz"),
        "qntmc 199: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 199: a long session ends when the candle dies", "AgentU"),
        "ruyaw 199: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 199: a long session ends when the candle dies", "keyboard"),
        "bssor 199: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 199: a long session ends when the candle dies", "AA"),
        "round 199: a long session ends when the candle dies",
    ),
    (("round 199: encode the prompt then map the result", "key"), "bssxh 199: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 199: encode the prompt then map the result", "lemon"), "csgbq 199: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 199: encode the prompt then map the result", "a"), "round 199: encode the prompt then map the result"),
    (("round 199: encode the prompt then map the result", "zz"), "qntmc 199: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 199: encode the prompt then map the result", "AgentU"),
        "ruyaw 199: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 199: encode the prompt then map the result", "keyboard"),
        "bssor 199: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 199: encode the prompt then map the result", "AA"), "round 199: encode the prompt then map the result"),
    (("round 199: the kernel wakes the worker at dawn", "key"), "bssxh 199: rri iovlop ukocc xfo ambocb er neux"),
    (("round 199: the kernel wakes the worker at dawn", "lemon"), "csgbq 199: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 199: the kernel wakes the worker at dawn", "a"), "round 199: the kernel wakes the worker at dawn"),
    (("round 199: the kernel wakes the worker at dawn", "zz"), "qntmc 199: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 199: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 199: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 199: the kernel wakes the worker at dawn", "keyboard"), "bssor 199: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 199: the kernel wakes the worker at dawn", "AA"), "round 199: the kernel wakes the worker at dawn"),
    (("round 199: service latency drops after the patch", "key"), "bssxh 199: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 199: service latency drops after the patch", "lemon"), "csgbq 199: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 199: service latency drops after the patch", "a"), "round 199: service latency drops after the patch"),
    (("round 199: service latency drops after the patch", "zz"), "qntmc 199: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 199: service latency drops after the patch", "AgentU"),
        "ruyaw 199: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 199: service latency drops after the patch", "keyboard"),
        "bssor 199: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 199: service latency drops after the patch", "AA"), "round 199: service latency drops after the patch"),
    (
        ("round 199: the library caches every vector it sees", "key"),
        "bssxh 199: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 199: the library caches every vector it sees", "lemon"),
        "csgbq 199: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 199: the library caches every vector it sees", "a"), "round 199: the library caches every vector it sees"),
    (
        ("round 199: the library caches every vector it sees", "zz"),
        "qntmc 199: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 199: the library caches every vector it sees", "AgentU"),
        "ruyaw 199: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 199: the library caches every vector it sees", "keyboard"),
        "bssor 199: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 199: the library caches every vector it sees", "AA"),
        "round 199: the library caches every vector it sees",
    ),
    (("round 199: agents argue then the debate resolves", "key"), "bssxh 199: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 199: agents argue then the debate resolves", "lemon"), "csgbq 199: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 199: agents argue then the debate resolves", "a"), "round 199: agents argue then the debate resolves"),
    (("round 199: agents argue then the debate resolves", "zz"), "qntmc 199: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 199: agents argue then the debate resolves", "AgentU"),
        "ruyaw 199: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 199: agents argue then the debate resolves", "keyboard"),
        "bssor 199: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 199: agents argue then the debate resolves", "AA"), "round 199: agents argue then the debate resolves"),
    (("round 199: the filter keeps only strong matches", "key"), "bssxh 199: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 199: the filter keeps only strong matches", "lemon"), "csgbq 199: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 199: the filter keeps only strong matches", "a"), "round 199: the filter keeps only strong matches"),
    (("round 199: the filter keeps only strong matches", "zz"), "qntmc 199: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 199: the filter keeps only strong matches", "AgentU"), "ruyaw 199: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 199: the filter keeps only strong matches", "keyboard"),
        "bssor 199: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 199: the filter keeps only strong matches", "AA"), "round 199: the filter keeps only strong matches"),
    (("round 199: the model answers with a short reply", "key"), "bssxh 199: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 199: the model answers with a short reply", "lemon"), "csgbq 199: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 199: the model answers with a short reply", "a"), "round 199: the model answers with a short reply"),
    (("round 199: the model answers with a short reply", "zz"), "qntmc 199: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 199: the model answers with a short reply", "AgentU"), "ruyaw 199: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 199: the model answers with a short reply", "keyboard"),
        "bssor 199: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 199: the model answers with a short reply", "AA"), "round 199: the model answers with a short reply"),
    (
        ("round 199: the recorder stores the reasoning trace", "key"),
        "bssxh 199: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 199: the recorder stores the reasoning trace", "lemon"),
        "csgbq 199: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 199: the recorder stores the reasoning trace", "a"), "round 199: the recorder stores the reasoning trace"),
    (
        ("round 199: the recorder stores the reasoning trace", "zz"),
        "qntmc 199: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 199: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 199: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 199: the recorder stores the reasoning trace", "keyboard"),
        "bssor 199: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 199: the recorder stores the reasoning trace", "AA"),
        "round 199: the recorder stores the reasoning trace",
    ),
    (("round 199: the angel watches the processor run", "key"), "bssxh 199: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 199: the angel watches the processor run", "lemon"), "csgbq 199: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 199: the angel watches the processor run", "a"), "round 199: the angel watches the processor run"),
    (("round 199: the angel watches the processor run", "zz"), "qntmc 199: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 199: the angel watches the processor run", "AgentU"), "ruyaw 199: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 199: the angel watches the processor run", "keyboard"), "bssor 199: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 199: the angel watches the processor run", "AA"), "round 199: the angel watches the processor run"),
    (("round 199: angle of the vector decides the match", "key"), "bssxh 199: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 199: angle of the vector decides the match", "lemon"), "csgbq 199: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 199: angle of the vector decides the match", "a"), "round 199: angle of the vector decides the match"),
    (("round 199: angle of the vector decides the match", "zz"), "qntmc 199: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 199: angle of the vector decides the match", "AgentU"),
        "ruyaw 199: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 199: angle of the vector decides the match", "keyboard"),
        "bssor 199: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 199: angle of the vector decides the match", "AA"), "round 199: angle of the vector decides the match"),
    (
        ("round 199: the candle burns twice as long at night", "key"),
        "bssxh 199: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 199: the candle burns twice as long at night", "lemon"),
        "csgbq 199: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 199: the candle burns twice as long at night", "a"), "round 199: the candle burns twice as long at night"),
    (
        ("round 199: the candle burns twice as long at night", "zz"),
        "qntmc 199: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 199: the candle burns twice as long at night", "AgentU"),
        "ruyaw 199: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 199: the candle burns twice as long at night", "keyboard"),
        "bssor 199: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 199: the candle burns twice as long at night", "AA"),
        "round 199: the candle burns twice as long at night",
    ),
    (("round 199: a mirror of the universe in one line", "key"), "bssxh 199: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 199: a mirror of the universe in one line", "lemon"), "csgbq 199: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 199: a mirror of the universe in one line", "a"), "round 199: a mirror of the universe in one line"),
    (("round 199: a mirror of the universe in one line", "zz"), "qntmc 199: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 199: a mirror of the universe in one line", "AgentU"), "ruyaw 199: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 199: a mirror of the universe in one line", "keyboard"),
        "bssor 199: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 199: a mirror of the universe in one line", "AA"), "round 199: a mirror of the universe in one line"),
    (("round 199: the queue drains before the storm", "key"), "bssxh 199: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 199: the queue drains before the storm", "lemon"), "csgbq 199: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 199: the queue drains before the storm", "a"), "round 199: the queue drains before the storm"),
    (("round 199: the queue drains before the storm", "zz"), "qntmc 199: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 199: the queue drains before the storm", "AgentU"), "ruyaw 199: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 199: the queue drains before the storm", "keyboard"), "bssor 199: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 199: the queue drains before the storm", "AA"), "round 199: the queue drains before the storm"),
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
