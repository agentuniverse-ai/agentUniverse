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
    (("kitten744", "key"), "umrdil744"),
    (("kitten744", "lemon"), "vmfhry744"),
    (("kitten744", "a"), "kitten744"),
    (("kitten744", "zz"), "jhssdm744"),
    (("kitten744", "AgentU"), "koxgxh744"),
    (("kitten744", "keyboard"), "umrusn744"),
    (("kitten744", "AA"), "kitten744"),
    (("sitting744", "key"), "cmrdmlq744"),
    (("sitting744", "lemon"), "dmfhvyk744"),
    (("sitting744", "a"), "sitting744"),
    (("sitting744", "zz"), "rhsshmf744"),
    (("sitting744", "AgentU"), "soxgbhg744"),
    (("sitting744", "keyboard"), "cmruwnx744"),
    (("sitting744", "AA"), "sitting744"),
    (("agent744", "key"), "kkcxx744"),
    (("agent744", "lemon"), "lkqbg744"),
    (("agent744", "a"), "agent744"),
    (("agent744", "zz"), "zfdms744"),
    (("agent744", "AgentU"), "amiam744"),
    (("agent744", "keyboard"), "kkcoh744"),
    (("agent744", "AA"), "agent744"),
    (("angle744", "key"), "krevi744"),
    (("angle744", "lemon"), "lrszr744"),
    (("angle744", "a"), "angle744"),
    (("angle744", "zz"), "zmfkd744"),
    (("angle744", "AgentU"), "atkyx744"),
    (("angle744", "keyboard"), "krems744"),
    (("angle744", "AA"), "angle744"),
    (("universe744", "key"), "ergfipci744"),
    (("universe744", "lemon"), "frujrcwq744"),
    (("universe744", "a"), "universe744"),
    (("universe744", "zz"), "tmhudqrd744"),
    (("universe744", "AgentU"), "utmixlsk744"),
    (("universe744", "keyboard"), "ergwsrjh744"),
    (("universe744", "AA"), "universe744"),
    (("memory744", "key"), "wikyvw744"),
    (("memory744", "lemon"), "xiycej744"),
    (("memory744", "a"), "memory744"),
    (("memory744", "zz"), "ldlnqx744"),
    (("memory744", "AgentU"), "mkqbks744"),
    (("memory744", "keyboard"), "wikpfy744"),
    (("memory744", "AA"), "memory744"),
    (("stream744", "key"), "cxpoek744"),
    (("stream744", "lemon"), "dxdsnx744"),
    (("stream744", "a"), "stream744"),
    (("stream744", "zz"), "rsqdzl744"),
    (("stream744", "AgentU"), "szvrtg744"),
    (("stream744", "keyboard"), "cxpfom744"),
    (("stream744", "AA"), "stream744"),
    (("context744", "key"), "msldivd744"),
    (("context744", "lemon"), "nszhrix744"),
    (("context744", "a"), "context744"),
    (("context744", "zz"), "bnmsdws744"),
    (("context744", "AgentU"), "curgxrt744"),
    (("context744", "keyboard"), "mslusxk744"),
    (("context744", "AA"), "context744"),
    (("knowledge744", "key"), "urmgpcnkc744"),
    (("knowledge744", "lemon"), "vrakyphss744"),
    (("knowledge744", "a"), "knowledge744"),
    (("knowledge744", "zz"), "jmnvkdcfd744"),
    (("knowledge744", "AgentU"), "ktsjeydmi744"),
    (("knowledge744", "keyboard"), "urmxzeujo744"),
    (("knowledge744", "AA"), "knowledge744"),
    (("vector744", "key"), "fiadsp744"),
    (("vector744", "lemon"), "giohbc744"),
    (("vector744", "a"), "vector744"),
    (("vector744", "zz"), "udbsnq744"),
    (("vector744", "AgentU"), "vkgghl744"),
    (("vector744", "keyboard"), "fiaucr744"),
    (("vector744", "AA"), "vector744"),
    (("processor744", "key"), "zvmmiqcsp744"),
    (("processor744", "lemon"), "avaqrdwaf744"),
    (("processor744", "a"), "processor744"),
    (("processor744", "zz"), "oqnbdrrnq744"),
    (("processor744", "AgentU"), "pxspxmsuv744"),
    (("processor744", "keyboard"), "zvmdssjrb744"),
    (("processor744", "AA"), "processor744"),
    (("reasoning744", "key"), "biycslsre744"),
    (("reasoning744", "lemon"), "cimgbymzu744"),
    (("reasoning744", "a"), "reasoning744"),
    (("reasoning744", "zz"), "qdzrnmhmf744"),
    (("reasoning744", "AgentU"), "rkefhhitk744"),
    (("reasoning744", "keyboard"), "biytcnzqq744"),
    (("reasoning744", "AA"), "reasoning744"),
    (("machine744", "key"), "wearmlo744"),
    (("machine744", "lemon"), "xeovvyi744"),
    (("machine744", "a"), "machine744"),
    (("machine744", "zz"), "lzbghmd744"),
    (("machine744", "AgentU"), "mggubhe744"),
    (("machine744", "keyboard"), "weaiwnv744"),
    (("machine744", "AA"), "machine744"),
    (("learning744", "key"), "viybrgxk744"),
    (("learning744", "lemon"), "wimfatrs744"),
    (("learning744", "a"), "learning744"),
    (("learning744", "zz"), "kdzqmhmf744"),
    (("learning744", "AgentU"), "lkeegcnm744"),
    (("learning744", "keyboard"), "viysbiej744"),
    (("learning744", "AA"), "learning744"),
    (("model744", "key"), "wsbop744"),
    (("model744", "lemon"), "xspsy744"),
    (("model744", "a"), "model744"),
    (("model744", "zz"), "lncdk744"),
    (("model744", "AgentU"), "muhre744"),
    (("model744", "keyboard"), "wsbfz744"),
    (("model744", "AA"), "model744"),
    (("token744", "key"), "dsior744"),
    (("token744", "lemon"), "eswsa744"),
    (("token744", "a"), "token744"),
    (("token744", "zz"), "snjdm744"),
    (("token744", "AgentU"), "tuorg744"),
    (("token744", "keyboard"), "dsifb744"),
    (("token744", "AA"), "token744"),
    (("prompt744", "key"), "zvmwtr744"),
    (("prompt744", "lemon"), "avaace744"),
    (("prompt744", "a"), "prompt744"),
    (("prompt744", "zz"), "oqnlos744"),
    (("prompt744", "AgentU"), "pxszin744"),
    (("prompt744", "keyboard"), "zvmndt744"),
    (("prompt744", "AA"), "prompt744"),
    (("session744", "key"), "ciqcmmx744"),
    (("session744", "lemon"), "diegvzr744"),
    (("session744", "a"), "session744"),
    (("session744", "zz"), "rdrrhnm744"),
    (("session744", "AgentU"), "skwfbin744"),
    (("session744", "keyboard"), "ciqtwoe744"),
    (("session744", "AA"), "session744"),
    (("library744", "key"), "vmzbepi744"),
    (("library744", "lemon"), "wmnfncc744"),
    (("library744", "a"), "library744"),
    (("library744", "zz"), "khaqzqx744"),
    (("library744", "AgentU"), "lofetly744"),
    (("library744", "keyboard"), "vmzsorp744"),
    (("library744", "AA"), "library744"),
    (("service744", "key"), "cipfmao744"),
    (("service744", "lemon"), "didjvni744"),
    (("service744", "a"), "service744"),
    (("service744", "zz"), "rdquhbd744"),
    (("service744", "AgentU"), "skvibwe744"),
    (("service744", "keyboard"), "cipwwcv744"),
    (("service744", "AA"), "service744"),
    (("gateway744", "key"), "qeroayi744"),
    (("gateway744", "lemon"), "refsjlc744"),
    (("gateway744", "a"), "gateway744"),
    (("gateway744", "zz"), "fzsdvzx744"),
    (("gateway744", "AgentU"), "ggxrpuy744"),
    (("gateway744", "keyboard"), "qerfkap744"),
    (("gateway744", "AA"), "gateway744"),
    (("storage744", "key"), "cxmbeeo744"),
    (("storage744", "lemon"), "dxafnri744"),
    (("storage744", "a"), "storage744"),
    (("storage744", "zz"), "rsnqzfd744"),
    (("storage744", "AgentU"), "szsetae744"),
    (("storage744", "keyboard"), "cxmsogv744"),
    (("storage744", "AA"), "storage744"),
    (("network744", "key"), "xirgspu744"),
    (("network744", "lemon"), "yifkbco744"),
    (("network744", "a"), "network744"),
    (("network744", "zz"), "mdsvnqj744"),
    (("network744", "AgentU"), "nkxjhlk744"),
    (("network744", "keyboard"), "xirxcrb744"),
    (("network744", "AA"), "network744"),
    (("latency744", "key"), "verorai744"),
    (("latency744", "lemon"), "wefsanc744"),
    (("latency744", "a"), "latency744"),
    (("latency744", "zz"), "kzsdmbx744"),
    (("latency744", "AgentU"), "lgxrgwy744"),
    (("latency744", "keyboard"), "verfbcp744"),
    (("latency744", "AA"), "latency744"),
    (("buffer744", "key"), "lydpip744"),
    (("buffer744", "lemon"), "myrtrc744"),
    (("buffer744", "a"), "buffer744"),
    (("buffer744", "zz"), "ateedq744"),
    (("buffer744", "AgentU"), "bajsxl744"),
    (("buffer744", "keyboard"), "lydgsr744"),
    (("buffer744", "AA"), "buffer744"),
    (("queue744", "key"), "aycei744"),
    (("queue744", "lemon"), "byqir744"),
    (("queue744", "a"), "queue744"),
    (("queue744", "zz"), "ptdtd744"),
    (("queue744", "AgentU"), "qaihx744"),
    (("queue744", "keyboard"), "aycvs744"),
    (("queue744", "AA"), "queue744"),
    (("worker744", "key"), "gspuip744"),
    (("worker744", "lemon"), "hsdyrc744"),
    (("worker744", "a"), "worker744"),
    (("worker744", "zz"), "vnqjdq744"),
    (("worker744", "AgentU"), "wuvxxl744"),
    (("worker744", "keyboard"), "gsplsr744"),
    (("worker744", "AA"), "worker744"),
    (("kernel744", "key"), "uipxij744"),
    (("kernel744", "lemon"), "vidbrw744"),
    (("kernel744", "a"), "kernel744"),
    (("kernel744", "zz"), "jdqmdk744"),
    (("kernel744", "AgentU"), "kkvaxf744"),
    (("kernel744", "keyboard"), "uiposl744"),
    (("kernel744", "AA"), "kernel744"),
    (("signal744", "key"), "cmexej744"),
    (("signal744", "lemon"), "dmsbnw744"),
    (("signal744", "a"), "signal744"),
    (("signal744", "zz"), "rhfmzk744"),
    (("signal744", "AgentU"), "sokatf744"),
    (("signal744", "keyboard"), "cmeool744"),
    (("signal744", "AA"), "signal744"),
    (("packet744", "key"), "zeauir744"),
    (("packet744", "lemon"), "aeoyre744"),
    (("packet744", "a"), "packet744"),
    (("packet744", "zz"), "ozbjds744"),
    (("packet744", "AgentU"), "pggxxn744"),
    (("packet744", "keyboard"), "zealst744"),
    (("packet744", "AA"), "packet744"),
    (("router744", "key"), "bssdip744"),
    (("router744", "lemon"), "csghrc744"),
    (("router744", "a"), "router744"),
    (("router744", "zz"), "qntsdq744"),
    (("router744", "AgentU"), "ruygxl744"),
    (("router744", "keyboard"), "bssusr744"),
    (("router744", "AA"), "router744"),
    (("cluster744", "key"), "mpscxcb744"),
    (("cluster744", "lemon"), "npgggpv744"),
    (("cluster744", "a"), "cluster744"),
    (("cluster744", "zz"), "bktrsdq744"),
    (("cluster744", "AgentU"), "cryfmyr744"),
    (("cluster744", "keyboard"), "mpsthei744"),
    (("cluster744", "AA"), "cluster744"),
    (("mirror744", "key"), "wmpbsp744"),
    (("mirror744", "lemon"), "xmdfbc744"),
    (("mirror744", "a"), "mirror744"),
    (("mirror744", "zz"), "lhqqnq744"),
    (("mirror744", "AgentU"), "movehl744"),
    (("mirror744", "keyboard"), "wmpscr744"),
    (("mirror744", "AA"), "mirror744"),
    (("filter744", "key"), "pmjdip744"),
    (("filter744", "lemon"), "qmxhrc744"),
    (("filter744", "a"), "filter744"),
    (("filter744", "zz"), "ehksdq744"),
    (("filter744", "AgentU"), "fopgxl744"),
    (("filter744", "keyboard"), "pmjusr744"),
    (("filter744", "AA"), "filter744"),
    (("ranking744", "key"), "belumlq744"),
    (("ranking744", "lemon"), "cezyvyk744"),
    (("ranking744", "a"), "ranking744"),
    (("ranking744", "zz"), "qzmjhmf744"),
    (("ranking744", "AgentU"), "rgrxbhg744"),
    (("ranking744", "keyboard"), "bellwnx744"),
    (("ranking744", "AA"), "ranking744"),
    (("encoding744", "key"), "orayhgxk744"),
    (("encoding744", "lemon"), "procqtrs744"),
    (("encoding744", "a"), "encoding744"),
    (("encoding744", "zz"), "dmbnchmf744"),
    (("encoding744", "AgentU"), "etgbwcnm744"),
    (("encoding744", "keyboard"), "orapriej744"),
    (("encoding744", "AA"), "encoding744"),
    (("mapping744", "key"), "wenzmlq744"),
    (("mapping744", "lemon"), "xebdvyk744"),
    (("mapping744", "a"), "mapping744"),
    (("mapping744", "zz"), "lzoohmf744"),
    (("mapping744", "AgentU"), "mgtcbhg744"),
    (("mapping744", "keyboard"), "wenqwnx744"),
    (("mapping744", "AA"), "mapping744"),
    (("record744", "key"), "biayvb744"),
    (("record744", "lemon"), "cioceo744"),
    (("record744", "a"), "record744"),
    (("record744", "zz"), "qdbnqc744"),
    (("record744", "AgentU"), "rkgbkx744"),
    (("record744", "keyboard"), "biapfd744"),
    (("record744", "AA"), "record744"),
    (("candle744", "key"), "melnpc744"),
    (("candle744", "lemon"), "nezryp744"),
    (("candle744", "a"), "candle744"),
    (("candle744", "zz"), "bzmckd744"),
    (("candle744", "AgentU"), "cgrqey744"),
    (("candle744", "keyboard"), "meleze744"),
    (("candle744", "AA"), "candle744"),
    (("thread744", "key"), "dlpoeb744"),
    (("thread744", "lemon"), "eldsno744"),
    (("thread744", "a"), "thread744"),
    (("thread744", "zz"), "sgqdzc744"),
    (("thread744", "AgentU"), "tnvrtx744"),
    (("thread744", "keyboard"), "dlpfod744"),
    (("thread744", "AA"), "thread744"),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 744: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 744: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "a"),
        "round 744: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 744: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 744: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 744: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", "AA"),
        "round 744: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "key"),
        "bssxh 744: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 744: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "a"),
        "round 744: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 744: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 744: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 744: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", "AA"),
        "round 744: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 744: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 744: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "a"),
        "round 744: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 744: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 744: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 744: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", "AA"),
        "round 744: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 744: the processor reads the record then stops", "key"),
        "bssxh 744: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 744: the processor reads the record then stops", "lemon"),
        "csgbq 744: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 744: the processor reads the record then stops", "a"),
        "round 744: the processor reads the record then stops",
    ),
    (
        ("round 744: the processor reads the record then stops", "zz"),
        "qntmc 744: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 744: the processor reads the record then stops", "AgentU"),
        "ruyaw 744: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 744: the processor reads the record then stops", "keyboard"),
        "bssor 744: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 744: the processor reads the record then stops", "AA"),
        "round 744: the processor reads the record then stops",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "key"),
        "bssxh 744: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "lemon"),
        "csgbq 744: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "a"),
        "round 744: a worker pulls the next task from the queue",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "zz"),
        "qntmc 744: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 744: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "keyboard"),
        "bssor 744: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 744: a worker pulls the next task from the queue", "AA"),
        "round 744: a worker pulls the next task from the queue",
    ),
    (
        ("round 744: signals travel through the network layer", "key"),
        "bssxh 744: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 744: signals travel through the network layer", "lemon"),
        "csgbq 744: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 744: signals travel through the network layer", "a"),
        "round 744: signals travel through the network layer",
    ),
    (
        ("round 744: signals travel through the network layer", "zz"),
        "qntmc 744: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 744: signals travel through the network layer", "AgentU"),
        "ruyaw 744: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 744: signals travel through the network layer", "keyboard"),
        "bssor 744: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 744: signals travel through the network layer", "AA"),
        "round 744: signals travel through the network layer",
    ),
    (
        ("round 744: the gateway routes each request by policy", "key"),
        "bssxh 744: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 744: the gateway routes each request by policy", "lemon"),
        "csgbq 744: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 744: the gateway routes each request by policy", "a"),
        "round 744: the gateway routes each request by policy",
    ),
    (
        ("round 744: the gateway routes each request by policy", "zz"),
        "qntmc 744: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 744: the gateway routes each request by policy", "AgentU"),
        "ruyaw 744: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 744: the gateway routes each request by policy", "keyboard"),
        "bssor 744: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 744: the gateway routes each request by policy", "AA"),
        "round 744: the gateway routes each request by policy",
    ),
    (("round 744: memory grows until the buffer is full", "key"), "bssxh 744: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 744: memory grows until the buffer is full", "lemon"), "csgbq 744: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 744: memory grows until the buffer is full", "a"), "round 744: memory grows until the buffer is full"),
    (("round 744: memory grows until the buffer is full", "zz"), "qntmc 744: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 744: memory grows until the buffer is full", "AgentU"),
        "ruyaw 744: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 744: memory grows until the buffer is full", "keyboard"),
        "bssor 744: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 744: memory grows until the buffer is full", "AA"), "round 744: memory grows until the buffer is full"),
    (("round 744: the cluster mirrors every packet twice", "key"), "bssxh 744: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 744: the cluster mirrors every packet twice", "lemon"),
        "csgbq 744: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 744: the cluster mirrors every packet twice", "a"), "round 744: the cluster mirrors every packet twice"),
    (("round 744: the cluster mirrors every packet twice", "zz"), "qntmc 744: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 744: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 744: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 744: the cluster mirrors every packet twice", "keyboard"),
        "bssor 744: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 744: the cluster mirrors every packet twice", "AA"), "round 744: the cluster mirrors every packet twice"),
    (
        ("round 744: ranking uses tokens learned from the corpus", "key"),
        "bssxh 744: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 744: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", "a"),
        "round 744: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 744: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 744: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 744: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", "AA"),
        "round 744: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 744: a long session ends when the candle dies", "key"),
        "bssxh 744: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 744: a long session ends when the candle dies", "lemon"),
        "csgbq 744: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 744: a long session ends when the candle dies", "a"),
        "round 744: a long session ends when the candle dies",
    ),
    (
        ("round 744: a long session ends when the candle dies", "zz"),
        "qntmc 744: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 744: a long session ends when the candle dies", "AgentU"),
        "ruyaw 744: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 744: a long session ends when the candle dies", "keyboard"),
        "bssor 744: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 744: a long session ends when the candle dies", "AA"),
        "round 744: a long session ends when the candle dies",
    ),
    (("round 744: encode the prompt then map the result", "key"), "bssxh 744: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 744: encode the prompt then map the result", "lemon"), "csgbq 744: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 744: encode the prompt then map the result", "a"), "round 744: encode the prompt then map the result"),
    (("round 744: encode the prompt then map the result", "zz"), "qntmc 744: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 744: encode the prompt then map the result", "AgentU"),
        "ruyaw 744: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 744: encode the prompt then map the result", "keyboard"),
        "bssor 744: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 744: encode the prompt then map the result", "AA"), "round 744: encode the prompt then map the result"),
    (("round 744: the kernel wakes the worker at dawn", "key"), "bssxh 744: rri iovlop ukocc xfo ambocb er neux"),
    (("round 744: the kernel wakes the worker at dawn", "lemon"), "csgbq 744: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 744: the kernel wakes the worker at dawn", "a"), "round 744: the kernel wakes the worker at dawn"),
    (("round 744: the kernel wakes the worker at dawn", "zz"), "qntmc 744: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 744: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 744: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 744: the kernel wakes the worker at dawn", "keyboard"), "bssor 744: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 744: the kernel wakes the worker at dawn", "AA"), "round 744: the kernel wakes the worker at dawn"),
    (("round 744: service latency drops after the patch", "key"), "bssxh 744: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 744: service latency drops after the patch", "lemon"), "csgbq 744: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 744: service latency drops after the patch", "a"), "round 744: service latency drops after the patch"),
    (("round 744: service latency drops after the patch", "zz"), "qntmc 744: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 744: service latency drops after the patch", "AgentU"),
        "ruyaw 744: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 744: service latency drops after the patch", "keyboard"),
        "bssor 744: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 744: service latency drops after the patch", "AA"), "round 744: service latency drops after the patch"),
    (
        ("round 744: the library caches every vector it sees", "key"),
        "bssxh 744: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 744: the library caches every vector it sees", "lemon"),
        "csgbq 744: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 744: the library caches every vector it sees", "a"), "round 744: the library caches every vector it sees"),
    (
        ("round 744: the library caches every vector it sees", "zz"),
        "qntmc 744: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 744: the library caches every vector it sees", "AgentU"),
        "ruyaw 744: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 744: the library caches every vector it sees", "keyboard"),
        "bssor 744: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 744: the library caches every vector it sees", "AA"),
        "round 744: the library caches every vector it sees",
    ),
    (("round 744: agents argue then the debate resolves", "key"), "bssxh 744: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 744: agents argue then the debate resolves", "lemon"), "csgbq 744: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 744: agents argue then the debate resolves", "a"), "round 744: agents argue then the debate resolves"),
    (("round 744: agents argue then the debate resolves", "zz"), "qntmc 744: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 744: agents argue then the debate resolves", "AgentU"),
        "ruyaw 744: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 744: agents argue then the debate resolves", "keyboard"),
        "bssor 744: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 744: agents argue then the debate resolves", "AA"), "round 744: agents argue then the debate resolves"),
    (("round 744: the filter keeps only strong matches", "key"), "bssxh 744: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 744: the filter keeps only strong matches", "lemon"), "csgbq 744: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 744: the filter keeps only strong matches", "a"), "round 744: the filter keeps only strong matches"),
    (("round 744: the filter keeps only strong matches", "zz"), "qntmc 744: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 744: the filter keeps only strong matches", "AgentU"), "ruyaw 744: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 744: the filter keeps only strong matches", "keyboard"),
        "bssor 744: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 744: the filter keeps only strong matches", "AA"), "round 744: the filter keeps only strong matches"),
    (("round 744: the model answers with a short reply", "key"), "bssxh 744: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 744: the model answers with a short reply", "lemon"), "csgbq 744: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 744: the model answers with a short reply", "a"), "round 744: the model answers with a short reply"),
    (("round 744: the model answers with a short reply", "zz"), "qntmc 744: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 744: the model answers with a short reply", "AgentU"), "ruyaw 744: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 744: the model answers with a short reply", "keyboard"),
        "bssor 744: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 744: the model answers with a short reply", "AA"), "round 744: the model answers with a short reply"),
    (
        ("round 744: the recorder stores the reasoning trace", "key"),
        "bssxh 744: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 744: the recorder stores the reasoning trace", "lemon"),
        "csgbq 744: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 744: the recorder stores the reasoning trace", "a"), "round 744: the recorder stores the reasoning trace"),
    (
        ("round 744: the recorder stores the reasoning trace", "zz"),
        "qntmc 744: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 744: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 744: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 744: the recorder stores the reasoning trace", "keyboard"),
        "bssor 744: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 744: the recorder stores the reasoning trace", "AA"),
        "round 744: the recorder stores the reasoning trace",
    ),
    (("round 744: the angel watches the processor run", "key"), "bssxh 744: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 744: the angel watches the processor run", "lemon"), "csgbq 744: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 744: the angel watches the processor run", "a"), "round 744: the angel watches the processor run"),
    (("round 744: the angel watches the processor run", "zz"), "qntmc 744: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 744: the angel watches the processor run", "AgentU"), "ruyaw 744: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 744: the angel watches the processor run", "keyboard"), "bssor 744: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 744: the angel watches the processor run", "AA"), "round 744: the angel watches the processor run"),
    (("round 744: angle of the vector decides the match", "key"), "bssxh 744: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 744: angle of the vector decides the match", "lemon"), "csgbq 744: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 744: angle of the vector decides the match", "a"), "round 744: angle of the vector decides the match"),
    (("round 744: angle of the vector decides the match", "zz"), "qntmc 744: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 744: angle of the vector decides the match", "AgentU"),
        "ruyaw 744: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 744: angle of the vector decides the match", "keyboard"),
        "bssor 744: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 744: angle of the vector decides the match", "AA"), "round 744: angle of the vector decides the match"),
    (
        ("round 744: the candle burns twice as long at night", "key"),
        "bssxh 744: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 744: the candle burns twice as long at night", "lemon"),
        "csgbq 744: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 744: the candle burns twice as long at night", "a"), "round 744: the candle burns twice as long at night"),
    (
        ("round 744: the candle burns twice as long at night", "zz"),
        "qntmc 744: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 744: the candle burns twice as long at night", "AgentU"),
        "ruyaw 744: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 744: the candle burns twice as long at night", "keyboard"),
        "bssor 744: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 744: the candle burns twice as long at night", "AA"),
        "round 744: the candle burns twice as long at night",
    ),
    (("round 744: a mirror of the universe in one line", "key"), "bssxh 744: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 744: a mirror of the universe in one line", "lemon"), "csgbq 744: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 744: a mirror of the universe in one line", "a"), "round 744: a mirror of the universe in one line"),
    (("round 744: a mirror of the universe in one line", "zz"), "qntmc 744: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 744: a mirror of the universe in one line", "AgentU"), "ruyaw 744: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 744: a mirror of the universe in one line", "keyboard"),
        "bssor 744: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 744: a mirror of the universe in one line", "AA"), "round 744: a mirror of the universe in one line"),
    (("round 744: the queue drains before the storm", "key"), "bssxh 744: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 744: the queue drains before the storm", "lemon"), "csgbq 744: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 744: the queue drains before the storm", "a"), "round 744: the queue drains before the storm"),
    (("round 744: the queue drains before the storm", "zz"), "qntmc 744: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 744: the queue drains before the storm", "AgentU"), "ruyaw 744: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 744: the queue drains before the storm", "keyboard"), "bssor 744: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 744: the queue drains before the storm", "AA"), "round 744: the queue drains before the storm"),
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
