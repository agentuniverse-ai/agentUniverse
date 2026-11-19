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
    (("kitten193", "key"), "umrdil193"),
    (("kitten193", "lemon"), "vmfhry193"),
    (("kitten193", "a"), "kitten193"),
    (("kitten193", "zz"), "jhssdm193"),
    (("kitten193", "AgentU"), "koxgxh193"),
    (("kitten193", "keyboard"), "umrusn193"),
    (("kitten193", "AA"), "kitten193"),
    (("sitting193", "key"), "cmrdmlq193"),
    (("sitting193", "lemon"), "dmfhvyk193"),
    (("sitting193", "a"), "sitting193"),
    (("sitting193", "zz"), "rhsshmf193"),
    (("sitting193", "AgentU"), "soxgbhg193"),
    (("sitting193", "keyboard"), "cmruwnx193"),
    (("sitting193", "AA"), "sitting193"),
    (("agent193", "key"), "kkcxx193"),
    (("agent193", "lemon"), "lkqbg193"),
    (("agent193", "a"), "agent193"),
    (("agent193", "zz"), "zfdms193"),
    (("agent193", "AgentU"), "amiam193"),
    (("agent193", "keyboard"), "kkcoh193"),
    (("agent193", "AA"), "agent193"),
    (("angle193", "key"), "krevi193"),
    (("angle193", "lemon"), "lrszr193"),
    (("angle193", "a"), "angle193"),
    (("angle193", "zz"), "zmfkd193"),
    (("angle193", "AgentU"), "atkyx193"),
    (("angle193", "keyboard"), "krems193"),
    (("angle193", "AA"), "angle193"),
    (("universe193", "key"), "ergfipci193"),
    (("universe193", "lemon"), "frujrcwq193"),
    (("universe193", "a"), "universe193"),
    (("universe193", "zz"), "tmhudqrd193"),
    (("universe193", "AgentU"), "utmixlsk193"),
    (("universe193", "keyboard"), "ergwsrjh193"),
    (("universe193", "AA"), "universe193"),
    (("memory193", "key"), "wikyvw193"),
    (("memory193", "lemon"), "xiycej193"),
    (("memory193", "a"), "memory193"),
    (("memory193", "zz"), "ldlnqx193"),
    (("memory193", "AgentU"), "mkqbks193"),
    (("memory193", "keyboard"), "wikpfy193"),
    (("memory193", "AA"), "memory193"),
    (("stream193", "key"), "cxpoek193"),
    (("stream193", "lemon"), "dxdsnx193"),
    (("stream193", "a"), "stream193"),
    (("stream193", "zz"), "rsqdzl193"),
    (("stream193", "AgentU"), "szvrtg193"),
    (("stream193", "keyboard"), "cxpfom193"),
    (("stream193", "AA"), "stream193"),
    (("context193", "key"), "msldivd193"),
    (("context193", "lemon"), "nszhrix193"),
    (("context193", "a"), "context193"),
    (("context193", "zz"), "bnmsdws193"),
    (("context193", "AgentU"), "curgxrt193"),
    (("context193", "keyboard"), "mslusxk193"),
    (("context193", "AA"), "context193"),
    (("knowledge193", "key"), "urmgpcnkc193"),
    (("knowledge193", "lemon"), "vrakyphss193"),
    (("knowledge193", "a"), "knowledge193"),
    (("knowledge193", "zz"), "jmnvkdcfd193"),
    (("knowledge193", "AgentU"), "ktsjeydmi193"),
    (("knowledge193", "keyboard"), "urmxzeujo193"),
    (("knowledge193", "AA"), "knowledge193"),
    (("vector193", "key"), "fiadsp193"),
    (("vector193", "lemon"), "giohbc193"),
    (("vector193", "a"), "vector193"),
    (("vector193", "zz"), "udbsnq193"),
    (("vector193", "AgentU"), "vkgghl193"),
    (("vector193", "keyboard"), "fiaucr193"),
    (("vector193", "AA"), "vector193"),
    (("processor193", "key"), "zvmmiqcsp193"),
    (("processor193", "lemon"), "avaqrdwaf193"),
    (("processor193", "a"), "processor193"),
    (("processor193", "zz"), "oqnbdrrnq193"),
    (("processor193", "AgentU"), "pxspxmsuv193"),
    (("processor193", "keyboard"), "zvmdssjrb193"),
    (("processor193", "AA"), "processor193"),
    (("reasoning193", "key"), "biycslsre193"),
    (("reasoning193", "lemon"), "cimgbymzu193"),
    (("reasoning193", "a"), "reasoning193"),
    (("reasoning193", "zz"), "qdzrnmhmf193"),
    (("reasoning193", "AgentU"), "rkefhhitk193"),
    (("reasoning193", "keyboard"), "biytcnzqq193"),
    (("reasoning193", "AA"), "reasoning193"),
    (("machine193", "key"), "wearmlo193"),
    (("machine193", "lemon"), "xeovvyi193"),
    (("machine193", "a"), "machine193"),
    (("machine193", "zz"), "lzbghmd193"),
    (("machine193", "AgentU"), "mggubhe193"),
    (("machine193", "keyboard"), "weaiwnv193"),
    (("machine193", "AA"), "machine193"),
    (("learning193", "key"), "viybrgxk193"),
    (("learning193", "lemon"), "wimfatrs193"),
    (("learning193", "a"), "learning193"),
    (("learning193", "zz"), "kdzqmhmf193"),
    (("learning193", "AgentU"), "lkeegcnm193"),
    (("learning193", "keyboard"), "viysbiej193"),
    (("learning193", "AA"), "learning193"),
    (("model193", "key"), "wsbop193"),
    (("model193", "lemon"), "xspsy193"),
    (("model193", "a"), "model193"),
    (("model193", "zz"), "lncdk193"),
    (("model193", "AgentU"), "muhre193"),
    (("model193", "keyboard"), "wsbfz193"),
    (("model193", "AA"), "model193"),
    (("token193", "key"), "dsior193"),
    (("token193", "lemon"), "eswsa193"),
    (("token193", "a"), "token193"),
    (("token193", "zz"), "snjdm193"),
    (("token193", "AgentU"), "tuorg193"),
    (("token193", "keyboard"), "dsifb193"),
    (("token193", "AA"), "token193"),
    (("prompt193", "key"), "zvmwtr193"),
    (("prompt193", "lemon"), "avaace193"),
    (("prompt193", "a"), "prompt193"),
    (("prompt193", "zz"), "oqnlos193"),
    (("prompt193", "AgentU"), "pxszin193"),
    (("prompt193", "keyboard"), "zvmndt193"),
    (("prompt193", "AA"), "prompt193"),
    (("session193", "key"), "ciqcmmx193"),
    (("session193", "lemon"), "diegvzr193"),
    (("session193", "a"), "session193"),
    (("session193", "zz"), "rdrrhnm193"),
    (("session193", "AgentU"), "skwfbin193"),
    (("session193", "keyboard"), "ciqtwoe193"),
    (("session193", "AA"), "session193"),
    (("library193", "key"), "vmzbepi193"),
    (("library193", "lemon"), "wmnfncc193"),
    (("library193", "a"), "library193"),
    (("library193", "zz"), "khaqzqx193"),
    (("library193", "AgentU"), "lofetly193"),
    (("library193", "keyboard"), "vmzsorp193"),
    (("library193", "AA"), "library193"),
    (("service193", "key"), "cipfmao193"),
    (("service193", "lemon"), "didjvni193"),
    (("service193", "a"), "service193"),
    (("service193", "zz"), "rdquhbd193"),
    (("service193", "AgentU"), "skvibwe193"),
    (("service193", "keyboard"), "cipwwcv193"),
    (("service193", "AA"), "service193"),
    (("gateway193", "key"), "qeroayi193"),
    (("gateway193", "lemon"), "refsjlc193"),
    (("gateway193", "a"), "gateway193"),
    (("gateway193", "zz"), "fzsdvzx193"),
    (("gateway193", "AgentU"), "ggxrpuy193"),
    (("gateway193", "keyboard"), "qerfkap193"),
    (("gateway193", "AA"), "gateway193"),
    (("storage193", "key"), "cxmbeeo193"),
    (("storage193", "lemon"), "dxafnri193"),
    (("storage193", "a"), "storage193"),
    (("storage193", "zz"), "rsnqzfd193"),
    (("storage193", "AgentU"), "szsetae193"),
    (("storage193", "keyboard"), "cxmsogv193"),
    (("storage193", "AA"), "storage193"),
    (("network193", "key"), "xirgspu193"),
    (("network193", "lemon"), "yifkbco193"),
    (("network193", "a"), "network193"),
    (("network193", "zz"), "mdsvnqj193"),
    (("network193", "AgentU"), "nkxjhlk193"),
    (("network193", "keyboard"), "xirxcrb193"),
    (("network193", "AA"), "network193"),
    (("latency193", "key"), "verorai193"),
    (("latency193", "lemon"), "wefsanc193"),
    (("latency193", "a"), "latency193"),
    (("latency193", "zz"), "kzsdmbx193"),
    (("latency193", "AgentU"), "lgxrgwy193"),
    (("latency193", "keyboard"), "verfbcp193"),
    (("latency193", "AA"), "latency193"),
    (("buffer193", "key"), "lydpip193"),
    (("buffer193", "lemon"), "myrtrc193"),
    (("buffer193", "a"), "buffer193"),
    (("buffer193", "zz"), "ateedq193"),
    (("buffer193", "AgentU"), "bajsxl193"),
    (("buffer193", "keyboard"), "lydgsr193"),
    (("buffer193", "AA"), "buffer193"),
    (("queue193", "key"), "aycei193"),
    (("queue193", "lemon"), "byqir193"),
    (("queue193", "a"), "queue193"),
    (("queue193", "zz"), "ptdtd193"),
    (("queue193", "AgentU"), "qaihx193"),
    (("queue193", "keyboard"), "aycvs193"),
    (("queue193", "AA"), "queue193"),
    (("worker193", "key"), "gspuip193"),
    (("worker193", "lemon"), "hsdyrc193"),
    (("worker193", "a"), "worker193"),
    (("worker193", "zz"), "vnqjdq193"),
    (("worker193", "AgentU"), "wuvxxl193"),
    (("worker193", "keyboard"), "gsplsr193"),
    (("worker193", "AA"), "worker193"),
    (("kernel193", "key"), "uipxij193"),
    (("kernel193", "lemon"), "vidbrw193"),
    (("kernel193", "a"), "kernel193"),
    (("kernel193", "zz"), "jdqmdk193"),
    (("kernel193", "AgentU"), "kkvaxf193"),
    (("kernel193", "keyboard"), "uiposl193"),
    (("kernel193", "AA"), "kernel193"),
    (("signal193", "key"), "cmexej193"),
    (("signal193", "lemon"), "dmsbnw193"),
    (("signal193", "a"), "signal193"),
    (("signal193", "zz"), "rhfmzk193"),
    (("signal193", "AgentU"), "sokatf193"),
    (("signal193", "keyboard"), "cmeool193"),
    (("signal193", "AA"), "signal193"),
    (("packet193", "key"), "zeauir193"),
    (("packet193", "lemon"), "aeoyre193"),
    (("packet193", "a"), "packet193"),
    (("packet193", "zz"), "ozbjds193"),
    (("packet193", "AgentU"), "pggxxn193"),
    (("packet193", "keyboard"), "zealst193"),
    (("packet193", "AA"), "packet193"),
    (("router193", "key"), "bssdip193"),
    (("router193", "lemon"), "csghrc193"),
    (("router193", "a"), "router193"),
    (("router193", "zz"), "qntsdq193"),
    (("router193", "AgentU"), "ruygxl193"),
    (("router193", "keyboard"), "bssusr193"),
    (("router193", "AA"), "router193"),
    (("cluster193", "key"), "mpscxcb193"),
    (("cluster193", "lemon"), "npgggpv193"),
    (("cluster193", "a"), "cluster193"),
    (("cluster193", "zz"), "bktrsdq193"),
    (("cluster193", "AgentU"), "cryfmyr193"),
    (("cluster193", "keyboard"), "mpsthei193"),
    (("cluster193", "AA"), "cluster193"),
    (("mirror193", "key"), "wmpbsp193"),
    (("mirror193", "lemon"), "xmdfbc193"),
    (("mirror193", "a"), "mirror193"),
    (("mirror193", "zz"), "lhqqnq193"),
    (("mirror193", "AgentU"), "movehl193"),
    (("mirror193", "keyboard"), "wmpscr193"),
    (("mirror193", "AA"), "mirror193"),
    (("filter193", "key"), "pmjdip193"),
    (("filter193", "lemon"), "qmxhrc193"),
    (("filter193", "a"), "filter193"),
    (("filter193", "zz"), "ehksdq193"),
    (("filter193", "AgentU"), "fopgxl193"),
    (("filter193", "keyboard"), "pmjusr193"),
    (("filter193", "AA"), "filter193"),
    (("ranking193", "key"), "belumlq193"),
    (("ranking193", "lemon"), "cezyvyk193"),
    (("ranking193", "a"), "ranking193"),
    (("ranking193", "zz"), "qzmjhmf193"),
    (("ranking193", "AgentU"), "rgrxbhg193"),
    (("ranking193", "keyboard"), "bellwnx193"),
    (("ranking193", "AA"), "ranking193"),
    (("encoding193", "key"), "orayhgxk193"),
    (("encoding193", "lemon"), "procqtrs193"),
    (("encoding193", "a"), "encoding193"),
    (("encoding193", "zz"), "dmbnchmf193"),
    (("encoding193", "AgentU"), "etgbwcnm193"),
    (("encoding193", "keyboard"), "orapriej193"),
    (("encoding193", "AA"), "encoding193"),
    (("mapping193", "key"), "wenzmlq193"),
    (("mapping193", "lemon"), "xebdvyk193"),
    (("mapping193", "a"), "mapping193"),
    (("mapping193", "zz"), "lzoohmf193"),
    (("mapping193", "AgentU"), "mgtcbhg193"),
    (("mapping193", "keyboard"), "wenqwnx193"),
    (("mapping193", "AA"), "mapping193"),
    (("record193", "key"), "biayvb193"),
    (("record193", "lemon"), "cioceo193"),
    (("record193", "a"), "record193"),
    (("record193", "zz"), "qdbnqc193"),
    (("record193", "AgentU"), "rkgbkx193"),
    (("record193", "keyboard"), "biapfd193"),
    (("record193", "AA"), "record193"),
    (("candle193", "key"), "melnpc193"),
    (("candle193", "lemon"), "nezryp193"),
    (("candle193", "a"), "candle193"),
    (("candle193", "zz"), "bzmckd193"),
    (("candle193", "AgentU"), "cgrqey193"),
    (("candle193", "keyboard"), "meleze193"),
    (("candle193", "AA"), "candle193"),
    (("thread193", "key"), "dlpoeb193"),
    (("thread193", "lemon"), "eldsno193"),
    (("thread193", "a"), "thread193"),
    (("thread193", "zz"), "sgqdzc193"),
    (("thread193", "AgentU"), "tnvrtx193"),
    (("thread193", "keyboard"), "dlpfod193"),
    (("thread193", "AA"), "thread193"),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 193: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 193: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "a"),
        "round 193: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 193: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 193: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 193: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", "AA"),
        "round 193: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "key"),
        "bssxh 193: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 193: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "a"),
        "round 193: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 193: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 193: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 193: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", "AA"),
        "round 193: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 193: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 193: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "a"),
        "round 193: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 193: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 193: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 193: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", "AA"),
        "round 193: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 193: the processor reads the record then stops", "key"),
        "bssxh 193: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 193: the processor reads the record then stops", "lemon"),
        "csgbq 193: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 193: the processor reads the record then stops", "a"),
        "round 193: the processor reads the record then stops",
    ),
    (
        ("round 193: the processor reads the record then stops", "zz"),
        "qntmc 193: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 193: the processor reads the record then stops", "AgentU"),
        "ruyaw 193: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 193: the processor reads the record then stops", "keyboard"),
        "bssor 193: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 193: the processor reads the record then stops", "AA"),
        "round 193: the processor reads the record then stops",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "key"),
        "bssxh 193: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "lemon"),
        "csgbq 193: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "a"),
        "round 193: a worker pulls the next task from the queue",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "zz"),
        "qntmc 193: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 193: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "keyboard"),
        "bssor 193: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 193: a worker pulls the next task from the queue", "AA"),
        "round 193: a worker pulls the next task from the queue",
    ),
    (
        ("round 193: signals travel through the network layer", "key"),
        "bssxh 193: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 193: signals travel through the network layer", "lemon"),
        "csgbq 193: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 193: signals travel through the network layer", "a"),
        "round 193: signals travel through the network layer",
    ),
    (
        ("round 193: signals travel through the network layer", "zz"),
        "qntmc 193: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 193: signals travel through the network layer", "AgentU"),
        "ruyaw 193: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 193: signals travel through the network layer", "keyboard"),
        "bssor 193: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 193: signals travel through the network layer", "AA"),
        "round 193: signals travel through the network layer",
    ),
    (
        ("round 193: the gateway routes each request by policy", "key"),
        "bssxh 193: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 193: the gateway routes each request by policy", "lemon"),
        "csgbq 193: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 193: the gateway routes each request by policy", "a"),
        "round 193: the gateway routes each request by policy",
    ),
    (
        ("round 193: the gateway routes each request by policy", "zz"),
        "qntmc 193: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 193: the gateway routes each request by policy", "AgentU"),
        "ruyaw 193: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 193: the gateway routes each request by policy", "keyboard"),
        "bssor 193: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 193: the gateway routes each request by policy", "AA"),
        "round 193: the gateway routes each request by policy",
    ),
    (("round 193: memory grows until the buffer is full", "key"), "bssxh 193: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 193: memory grows until the buffer is full", "lemon"), "csgbq 193: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 193: memory grows until the buffer is full", "a"), "round 193: memory grows until the buffer is full"),
    (("round 193: memory grows until the buffer is full", "zz"), "qntmc 193: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 193: memory grows until the buffer is full", "AgentU"),
        "ruyaw 193: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 193: memory grows until the buffer is full", "keyboard"),
        "bssor 193: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 193: memory grows until the buffer is full", "AA"), "round 193: memory grows until the buffer is full"),
    (("round 193: the cluster mirrors every packet twice", "key"), "bssxh 193: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 193: the cluster mirrors every packet twice", "lemon"),
        "csgbq 193: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 193: the cluster mirrors every packet twice", "a"), "round 193: the cluster mirrors every packet twice"),
    (("round 193: the cluster mirrors every packet twice", "zz"), "qntmc 193: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 193: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 193: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 193: the cluster mirrors every packet twice", "keyboard"),
        "bssor 193: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 193: the cluster mirrors every packet twice", "AA"), "round 193: the cluster mirrors every packet twice"),
    (
        ("round 193: ranking uses tokens learned from the corpus", "key"),
        "bssxh 193: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 193: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", "a"),
        "round 193: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 193: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 193: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 193: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", "AA"),
        "round 193: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 193: a long session ends when the candle dies", "key"),
        "bssxh 193: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 193: a long session ends when the candle dies", "lemon"),
        "csgbq 193: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 193: a long session ends when the candle dies", "a"),
        "round 193: a long session ends when the candle dies",
    ),
    (
        ("round 193: a long session ends when the candle dies", "zz"),
        "qntmc 193: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 193: a long session ends when the candle dies", "AgentU"),
        "ruyaw 193: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 193: a long session ends when the candle dies", "keyboard"),
        "bssor 193: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 193: a long session ends when the candle dies", "AA"),
        "round 193: a long session ends when the candle dies",
    ),
    (("round 193: encode the prompt then map the result", "key"), "bssxh 193: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 193: encode the prompt then map the result", "lemon"), "csgbq 193: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 193: encode the prompt then map the result", "a"), "round 193: encode the prompt then map the result"),
    (("round 193: encode the prompt then map the result", "zz"), "qntmc 193: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 193: encode the prompt then map the result", "AgentU"),
        "ruyaw 193: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 193: encode the prompt then map the result", "keyboard"),
        "bssor 193: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 193: encode the prompt then map the result", "AA"), "round 193: encode the prompt then map the result"),
    (("round 193: the kernel wakes the worker at dawn", "key"), "bssxh 193: rri iovlop ukocc xfo ambocb er neux"),
    (("round 193: the kernel wakes the worker at dawn", "lemon"), "csgbq 193: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 193: the kernel wakes the worker at dawn", "a"), "round 193: the kernel wakes the worker at dawn"),
    (("round 193: the kernel wakes the worker at dawn", "zz"), "qntmc 193: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 193: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 193: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 193: the kernel wakes the worker at dawn", "keyboard"), "bssor 193: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 193: the kernel wakes the worker at dawn", "AA"), "round 193: the kernel wakes the worker at dawn"),
    (("round 193: service latency drops after the patch", "key"), "bssxh 193: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 193: service latency drops after the patch", "lemon"), "csgbq 193: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 193: service latency drops after the patch", "a"), "round 193: service latency drops after the patch"),
    (("round 193: service latency drops after the patch", "zz"), "qntmc 193: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 193: service latency drops after the patch", "AgentU"),
        "ruyaw 193: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 193: service latency drops after the patch", "keyboard"),
        "bssor 193: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 193: service latency drops after the patch", "AA"), "round 193: service latency drops after the patch"),
    (
        ("round 193: the library caches every vector it sees", "key"),
        "bssxh 193: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 193: the library caches every vector it sees", "lemon"),
        "csgbq 193: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 193: the library caches every vector it sees", "a"), "round 193: the library caches every vector it sees"),
    (
        ("round 193: the library caches every vector it sees", "zz"),
        "qntmc 193: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 193: the library caches every vector it sees", "AgentU"),
        "ruyaw 193: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 193: the library caches every vector it sees", "keyboard"),
        "bssor 193: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 193: the library caches every vector it sees", "AA"),
        "round 193: the library caches every vector it sees",
    ),
    (("round 193: agents argue then the debate resolves", "key"), "bssxh 193: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 193: agents argue then the debate resolves", "lemon"), "csgbq 193: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 193: agents argue then the debate resolves", "a"), "round 193: agents argue then the debate resolves"),
    (("round 193: agents argue then the debate resolves", "zz"), "qntmc 193: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 193: agents argue then the debate resolves", "AgentU"),
        "ruyaw 193: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 193: agents argue then the debate resolves", "keyboard"),
        "bssor 193: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 193: agents argue then the debate resolves", "AA"), "round 193: agents argue then the debate resolves"),
    (("round 193: the filter keeps only strong matches", "key"), "bssxh 193: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 193: the filter keeps only strong matches", "lemon"), "csgbq 193: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 193: the filter keeps only strong matches", "a"), "round 193: the filter keeps only strong matches"),
    (("round 193: the filter keeps only strong matches", "zz"), "qntmc 193: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 193: the filter keeps only strong matches", "AgentU"), "ruyaw 193: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 193: the filter keeps only strong matches", "keyboard"),
        "bssor 193: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 193: the filter keeps only strong matches", "AA"), "round 193: the filter keeps only strong matches"),
    (("round 193: the model answers with a short reply", "key"), "bssxh 193: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 193: the model answers with a short reply", "lemon"), "csgbq 193: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 193: the model answers with a short reply", "a"), "round 193: the model answers with a short reply"),
    (("round 193: the model answers with a short reply", "zz"), "qntmc 193: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 193: the model answers with a short reply", "AgentU"), "ruyaw 193: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 193: the model answers with a short reply", "keyboard"),
        "bssor 193: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 193: the model answers with a short reply", "AA"), "round 193: the model answers with a short reply"),
    (
        ("round 193: the recorder stores the reasoning trace", "key"),
        "bssxh 193: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 193: the recorder stores the reasoning trace", "lemon"),
        "csgbq 193: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 193: the recorder stores the reasoning trace", "a"), "round 193: the recorder stores the reasoning trace"),
    (
        ("round 193: the recorder stores the reasoning trace", "zz"),
        "qntmc 193: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 193: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 193: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 193: the recorder stores the reasoning trace", "keyboard"),
        "bssor 193: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 193: the recorder stores the reasoning trace", "AA"),
        "round 193: the recorder stores the reasoning trace",
    ),
    (("round 193: the angel watches the processor run", "key"), "bssxh 193: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 193: the angel watches the processor run", "lemon"), "csgbq 193: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 193: the angel watches the processor run", "a"), "round 193: the angel watches the processor run"),
    (("round 193: the angel watches the processor run", "zz"), "qntmc 193: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 193: the angel watches the processor run", "AgentU"), "ruyaw 193: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 193: the angel watches the processor run", "keyboard"), "bssor 193: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 193: the angel watches the processor run", "AA"), "round 193: the angel watches the processor run"),
    (("round 193: angle of the vector decides the match", "key"), "bssxh 193: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 193: angle of the vector decides the match", "lemon"), "csgbq 193: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 193: angle of the vector decides the match", "a"), "round 193: angle of the vector decides the match"),
    (("round 193: angle of the vector decides the match", "zz"), "qntmc 193: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 193: angle of the vector decides the match", "AgentU"),
        "ruyaw 193: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 193: angle of the vector decides the match", "keyboard"),
        "bssor 193: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 193: angle of the vector decides the match", "AA"), "round 193: angle of the vector decides the match"),
    (
        ("round 193: the candle burns twice as long at night", "key"),
        "bssxh 193: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 193: the candle burns twice as long at night", "lemon"),
        "csgbq 193: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 193: the candle burns twice as long at night", "a"), "round 193: the candle burns twice as long at night"),
    (
        ("round 193: the candle burns twice as long at night", "zz"),
        "qntmc 193: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 193: the candle burns twice as long at night", "AgentU"),
        "ruyaw 193: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 193: the candle burns twice as long at night", "keyboard"),
        "bssor 193: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 193: the candle burns twice as long at night", "AA"),
        "round 193: the candle burns twice as long at night",
    ),
    (("round 193: a mirror of the universe in one line", "key"), "bssxh 193: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 193: a mirror of the universe in one line", "lemon"), "csgbq 193: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 193: a mirror of the universe in one line", "a"), "round 193: a mirror of the universe in one line"),
    (("round 193: a mirror of the universe in one line", "zz"), "qntmc 193: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 193: a mirror of the universe in one line", "AgentU"), "ruyaw 193: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 193: a mirror of the universe in one line", "keyboard"),
        "bssor 193: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 193: a mirror of the universe in one line", "AA"), "round 193: a mirror of the universe in one line"),
    (("round 193: the queue drains before the storm", "key"), "bssxh 193: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 193: the queue drains before the storm", "lemon"), "csgbq 193: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 193: the queue drains before the storm", "a"), "round 193: the queue drains before the storm"),
    (("round 193: the queue drains before the storm", "zz"), "qntmc 193: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 193: the queue drains before the storm", "AgentU"), "ruyaw 193: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 193: the queue drains before the storm", "keyboard"), "bssor 193: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 193: the queue drains before the storm", "AA"), "round 193: the queue drains before the storm"),
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
