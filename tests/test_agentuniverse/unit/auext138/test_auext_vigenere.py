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
    (("kitten138", "key"), "umrdil138"),
    (("kitten138", "lemon"), "vmfhry138"),
    (("kitten138", "a"), "kitten138"),
    (("kitten138", "zz"), "jhssdm138"),
    (("kitten138", "AgentU"), "koxgxh138"),
    (("kitten138", "keyboard"), "umrusn138"),
    (("kitten138", "AA"), "kitten138"),
    (("sitting138", "key"), "cmrdmlq138"),
    (("sitting138", "lemon"), "dmfhvyk138"),
    (("sitting138", "a"), "sitting138"),
    (("sitting138", "zz"), "rhsshmf138"),
    (("sitting138", "AgentU"), "soxgbhg138"),
    (("sitting138", "keyboard"), "cmruwnx138"),
    (("sitting138", "AA"), "sitting138"),
    (("agent138", "key"), "kkcxx138"),
    (("agent138", "lemon"), "lkqbg138"),
    (("agent138", "a"), "agent138"),
    (("agent138", "zz"), "zfdms138"),
    (("agent138", "AgentU"), "amiam138"),
    (("agent138", "keyboard"), "kkcoh138"),
    (("agent138", "AA"), "agent138"),
    (("angle138", "key"), "krevi138"),
    (("angle138", "lemon"), "lrszr138"),
    (("angle138", "a"), "angle138"),
    (("angle138", "zz"), "zmfkd138"),
    (("angle138", "AgentU"), "atkyx138"),
    (("angle138", "keyboard"), "krems138"),
    (("angle138", "AA"), "angle138"),
    (("universe138", "key"), "ergfipci138"),
    (("universe138", "lemon"), "frujrcwq138"),
    (("universe138", "a"), "universe138"),
    (("universe138", "zz"), "tmhudqrd138"),
    (("universe138", "AgentU"), "utmixlsk138"),
    (("universe138", "keyboard"), "ergwsrjh138"),
    (("universe138", "AA"), "universe138"),
    (("memory138", "key"), "wikyvw138"),
    (("memory138", "lemon"), "xiycej138"),
    (("memory138", "a"), "memory138"),
    (("memory138", "zz"), "ldlnqx138"),
    (("memory138", "AgentU"), "mkqbks138"),
    (("memory138", "keyboard"), "wikpfy138"),
    (("memory138", "AA"), "memory138"),
    (("stream138", "key"), "cxpoek138"),
    (("stream138", "lemon"), "dxdsnx138"),
    (("stream138", "a"), "stream138"),
    (("stream138", "zz"), "rsqdzl138"),
    (("stream138", "AgentU"), "szvrtg138"),
    (("stream138", "keyboard"), "cxpfom138"),
    (("stream138", "AA"), "stream138"),
    (("context138", "key"), "msldivd138"),
    (("context138", "lemon"), "nszhrix138"),
    (("context138", "a"), "context138"),
    (("context138", "zz"), "bnmsdws138"),
    (("context138", "AgentU"), "curgxrt138"),
    (("context138", "keyboard"), "mslusxk138"),
    (("context138", "AA"), "context138"),
    (("knowledge138", "key"), "urmgpcnkc138"),
    (("knowledge138", "lemon"), "vrakyphss138"),
    (("knowledge138", "a"), "knowledge138"),
    (("knowledge138", "zz"), "jmnvkdcfd138"),
    (("knowledge138", "AgentU"), "ktsjeydmi138"),
    (("knowledge138", "keyboard"), "urmxzeujo138"),
    (("knowledge138", "AA"), "knowledge138"),
    (("vector138", "key"), "fiadsp138"),
    (("vector138", "lemon"), "giohbc138"),
    (("vector138", "a"), "vector138"),
    (("vector138", "zz"), "udbsnq138"),
    (("vector138", "AgentU"), "vkgghl138"),
    (("vector138", "keyboard"), "fiaucr138"),
    (("vector138", "AA"), "vector138"),
    (("processor138", "key"), "zvmmiqcsp138"),
    (("processor138", "lemon"), "avaqrdwaf138"),
    (("processor138", "a"), "processor138"),
    (("processor138", "zz"), "oqnbdrrnq138"),
    (("processor138", "AgentU"), "pxspxmsuv138"),
    (("processor138", "keyboard"), "zvmdssjrb138"),
    (("processor138", "AA"), "processor138"),
    (("reasoning138", "key"), "biycslsre138"),
    (("reasoning138", "lemon"), "cimgbymzu138"),
    (("reasoning138", "a"), "reasoning138"),
    (("reasoning138", "zz"), "qdzrnmhmf138"),
    (("reasoning138", "AgentU"), "rkefhhitk138"),
    (("reasoning138", "keyboard"), "biytcnzqq138"),
    (("reasoning138", "AA"), "reasoning138"),
    (("machine138", "key"), "wearmlo138"),
    (("machine138", "lemon"), "xeovvyi138"),
    (("machine138", "a"), "machine138"),
    (("machine138", "zz"), "lzbghmd138"),
    (("machine138", "AgentU"), "mggubhe138"),
    (("machine138", "keyboard"), "weaiwnv138"),
    (("machine138", "AA"), "machine138"),
    (("learning138", "key"), "viybrgxk138"),
    (("learning138", "lemon"), "wimfatrs138"),
    (("learning138", "a"), "learning138"),
    (("learning138", "zz"), "kdzqmhmf138"),
    (("learning138", "AgentU"), "lkeegcnm138"),
    (("learning138", "keyboard"), "viysbiej138"),
    (("learning138", "AA"), "learning138"),
    (("model138", "key"), "wsbop138"),
    (("model138", "lemon"), "xspsy138"),
    (("model138", "a"), "model138"),
    (("model138", "zz"), "lncdk138"),
    (("model138", "AgentU"), "muhre138"),
    (("model138", "keyboard"), "wsbfz138"),
    (("model138", "AA"), "model138"),
    (("token138", "key"), "dsior138"),
    (("token138", "lemon"), "eswsa138"),
    (("token138", "a"), "token138"),
    (("token138", "zz"), "snjdm138"),
    (("token138", "AgentU"), "tuorg138"),
    (("token138", "keyboard"), "dsifb138"),
    (("token138", "AA"), "token138"),
    (("prompt138", "key"), "zvmwtr138"),
    (("prompt138", "lemon"), "avaace138"),
    (("prompt138", "a"), "prompt138"),
    (("prompt138", "zz"), "oqnlos138"),
    (("prompt138", "AgentU"), "pxszin138"),
    (("prompt138", "keyboard"), "zvmndt138"),
    (("prompt138", "AA"), "prompt138"),
    (("session138", "key"), "ciqcmmx138"),
    (("session138", "lemon"), "diegvzr138"),
    (("session138", "a"), "session138"),
    (("session138", "zz"), "rdrrhnm138"),
    (("session138", "AgentU"), "skwfbin138"),
    (("session138", "keyboard"), "ciqtwoe138"),
    (("session138", "AA"), "session138"),
    (("library138", "key"), "vmzbepi138"),
    (("library138", "lemon"), "wmnfncc138"),
    (("library138", "a"), "library138"),
    (("library138", "zz"), "khaqzqx138"),
    (("library138", "AgentU"), "lofetly138"),
    (("library138", "keyboard"), "vmzsorp138"),
    (("library138", "AA"), "library138"),
    (("service138", "key"), "cipfmao138"),
    (("service138", "lemon"), "didjvni138"),
    (("service138", "a"), "service138"),
    (("service138", "zz"), "rdquhbd138"),
    (("service138", "AgentU"), "skvibwe138"),
    (("service138", "keyboard"), "cipwwcv138"),
    (("service138", "AA"), "service138"),
    (("gateway138", "key"), "qeroayi138"),
    (("gateway138", "lemon"), "refsjlc138"),
    (("gateway138", "a"), "gateway138"),
    (("gateway138", "zz"), "fzsdvzx138"),
    (("gateway138", "AgentU"), "ggxrpuy138"),
    (("gateway138", "keyboard"), "qerfkap138"),
    (("gateway138", "AA"), "gateway138"),
    (("storage138", "key"), "cxmbeeo138"),
    (("storage138", "lemon"), "dxafnri138"),
    (("storage138", "a"), "storage138"),
    (("storage138", "zz"), "rsnqzfd138"),
    (("storage138", "AgentU"), "szsetae138"),
    (("storage138", "keyboard"), "cxmsogv138"),
    (("storage138", "AA"), "storage138"),
    (("network138", "key"), "xirgspu138"),
    (("network138", "lemon"), "yifkbco138"),
    (("network138", "a"), "network138"),
    (("network138", "zz"), "mdsvnqj138"),
    (("network138", "AgentU"), "nkxjhlk138"),
    (("network138", "keyboard"), "xirxcrb138"),
    (("network138", "AA"), "network138"),
    (("latency138", "key"), "verorai138"),
    (("latency138", "lemon"), "wefsanc138"),
    (("latency138", "a"), "latency138"),
    (("latency138", "zz"), "kzsdmbx138"),
    (("latency138", "AgentU"), "lgxrgwy138"),
    (("latency138", "keyboard"), "verfbcp138"),
    (("latency138", "AA"), "latency138"),
    (("buffer138", "key"), "lydpip138"),
    (("buffer138", "lemon"), "myrtrc138"),
    (("buffer138", "a"), "buffer138"),
    (("buffer138", "zz"), "ateedq138"),
    (("buffer138", "AgentU"), "bajsxl138"),
    (("buffer138", "keyboard"), "lydgsr138"),
    (("buffer138", "AA"), "buffer138"),
    (("queue138", "key"), "aycei138"),
    (("queue138", "lemon"), "byqir138"),
    (("queue138", "a"), "queue138"),
    (("queue138", "zz"), "ptdtd138"),
    (("queue138", "AgentU"), "qaihx138"),
    (("queue138", "keyboard"), "aycvs138"),
    (("queue138", "AA"), "queue138"),
    (("worker138", "key"), "gspuip138"),
    (("worker138", "lemon"), "hsdyrc138"),
    (("worker138", "a"), "worker138"),
    (("worker138", "zz"), "vnqjdq138"),
    (("worker138", "AgentU"), "wuvxxl138"),
    (("worker138", "keyboard"), "gsplsr138"),
    (("worker138", "AA"), "worker138"),
    (("kernel138", "key"), "uipxij138"),
    (("kernel138", "lemon"), "vidbrw138"),
    (("kernel138", "a"), "kernel138"),
    (("kernel138", "zz"), "jdqmdk138"),
    (("kernel138", "AgentU"), "kkvaxf138"),
    (("kernel138", "keyboard"), "uiposl138"),
    (("kernel138", "AA"), "kernel138"),
    (("signal138", "key"), "cmexej138"),
    (("signal138", "lemon"), "dmsbnw138"),
    (("signal138", "a"), "signal138"),
    (("signal138", "zz"), "rhfmzk138"),
    (("signal138", "AgentU"), "sokatf138"),
    (("signal138", "keyboard"), "cmeool138"),
    (("signal138", "AA"), "signal138"),
    (("packet138", "key"), "zeauir138"),
    (("packet138", "lemon"), "aeoyre138"),
    (("packet138", "a"), "packet138"),
    (("packet138", "zz"), "ozbjds138"),
    (("packet138", "AgentU"), "pggxxn138"),
    (("packet138", "keyboard"), "zealst138"),
    (("packet138", "AA"), "packet138"),
    (("router138", "key"), "bssdip138"),
    (("router138", "lemon"), "csghrc138"),
    (("router138", "a"), "router138"),
    (("router138", "zz"), "qntsdq138"),
    (("router138", "AgentU"), "ruygxl138"),
    (("router138", "keyboard"), "bssusr138"),
    (("router138", "AA"), "router138"),
    (("cluster138", "key"), "mpscxcb138"),
    (("cluster138", "lemon"), "npgggpv138"),
    (("cluster138", "a"), "cluster138"),
    (("cluster138", "zz"), "bktrsdq138"),
    (("cluster138", "AgentU"), "cryfmyr138"),
    (("cluster138", "keyboard"), "mpsthei138"),
    (("cluster138", "AA"), "cluster138"),
    (("mirror138", "key"), "wmpbsp138"),
    (("mirror138", "lemon"), "xmdfbc138"),
    (("mirror138", "a"), "mirror138"),
    (("mirror138", "zz"), "lhqqnq138"),
    (("mirror138", "AgentU"), "movehl138"),
    (("mirror138", "keyboard"), "wmpscr138"),
    (("mirror138", "AA"), "mirror138"),
    (("filter138", "key"), "pmjdip138"),
    (("filter138", "lemon"), "qmxhrc138"),
    (("filter138", "a"), "filter138"),
    (("filter138", "zz"), "ehksdq138"),
    (("filter138", "AgentU"), "fopgxl138"),
    (("filter138", "keyboard"), "pmjusr138"),
    (("filter138", "AA"), "filter138"),
    (("ranking138", "key"), "belumlq138"),
    (("ranking138", "lemon"), "cezyvyk138"),
    (("ranking138", "a"), "ranking138"),
    (("ranking138", "zz"), "qzmjhmf138"),
    (("ranking138", "AgentU"), "rgrxbhg138"),
    (("ranking138", "keyboard"), "bellwnx138"),
    (("ranking138", "AA"), "ranking138"),
    (("encoding138", "key"), "orayhgxk138"),
    (("encoding138", "lemon"), "procqtrs138"),
    (("encoding138", "a"), "encoding138"),
    (("encoding138", "zz"), "dmbnchmf138"),
    (("encoding138", "AgentU"), "etgbwcnm138"),
    (("encoding138", "keyboard"), "orapriej138"),
    (("encoding138", "AA"), "encoding138"),
    (("mapping138", "key"), "wenzmlq138"),
    (("mapping138", "lemon"), "xebdvyk138"),
    (("mapping138", "a"), "mapping138"),
    (("mapping138", "zz"), "lzoohmf138"),
    (("mapping138", "AgentU"), "mgtcbhg138"),
    (("mapping138", "keyboard"), "wenqwnx138"),
    (("mapping138", "AA"), "mapping138"),
    (("record138", "key"), "biayvb138"),
    (("record138", "lemon"), "cioceo138"),
    (("record138", "a"), "record138"),
    (("record138", "zz"), "qdbnqc138"),
    (("record138", "AgentU"), "rkgbkx138"),
    (("record138", "keyboard"), "biapfd138"),
    (("record138", "AA"), "record138"),
    (("candle138", "key"), "melnpc138"),
    (("candle138", "lemon"), "nezryp138"),
    (("candle138", "a"), "candle138"),
    (("candle138", "zz"), "bzmckd138"),
    (("candle138", "AgentU"), "cgrqey138"),
    (("candle138", "keyboard"), "meleze138"),
    (("candle138", "AA"), "candle138"),
    (("thread138", "key"), "dlpoeb138"),
    (("thread138", "lemon"), "eldsno138"),
    (("thread138", "a"), "thread138"),
    (("thread138", "zz"), "sgqdzc138"),
    (("thread138", "AgentU"), "tnvrtx138"),
    (("thread138", "keyboard"), "dlpfod138"),
    (("thread138", "AA"), "thread138"),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 138: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 138: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "a"),
        "round 138: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 138: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 138: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 138: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", "AA"),
        "round 138: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "key"),
        "bssxh 138: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 138: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "a"),
        "round 138: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 138: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 138: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 138: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", "AA"),
        "round 138: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 138: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 138: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "a"),
        "round 138: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 138: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 138: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 138: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", "AA"),
        "round 138: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 138: the processor reads the record then stops", "key"),
        "bssxh 138: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 138: the processor reads the record then stops", "lemon"),
        "csgbq 138: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 138: the processor reads the record then stops", "a"),
        "round 138: the processor reads the record then stops",
    ),
    (
        ("round 138: the processor reads the record then stops", "zz"),
        "qntmc 138: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 138: the processor reads the record then stops", "AgentU"),
        "ruyaw 138: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 138: the processor reads the record then stops", "keyboard"),
        "bssor 138: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 138: the processor reads the record then stops", "AA"),
        "round 138: the processor reads the record then stops",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "key"),
        "bssxh 138: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "lemon"),
        "csgbq 138: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "a"),
        "round 138: a worker pulls the next task from the queue",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "zz"),
        "qntmc 138: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 138: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "keyboard"),
        "bssor 138: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 138: a worker pulls the next task from the queue", "AA"),
        "round 138: a worker pulls the next task from the queue",
    ),
    (
        ("round 138: signals travel through the network layer", "key"),
        "bssxh 138: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 138: signals travel through the network layer", "lemon"),
        "csgbq 138: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 138: signals travel through the network layer", "a"),
        "round 138: signals travel through the network layer",
    ),
    (
        ("round 138: signals travel through the network layer", "zz"),
        "qntmc 138: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 138: signals travel through the network layer", "AgentU"),
        "ruyaw 138: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 138: signals travel through the network layer", "keyboard"),
        "bssor 138: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 138: signals travel through the network layer", "AA"),
        "round 138: signals travel through the network layer",
    ),
    (
        ("round 138: the gateway routes each request by policy", "key"),
        "bssxh 138: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 138: the gateway routes each request by policy", "lemon"),
        "csgbq 138: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 138: the gateway routes each request by policy", "a"),
        "round 138: the gateway routes each request by policy",
    ),
    (
        ("round 138: the gateway routes each request by policy", "zz"),
        "qntmc 138: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 138: the gateway routes each request by policy", "AgentU"),
        "ruyaw 138: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 138: the gateway routes each request by policy", "keyboard"),
        "bssor 138: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 138: the gateway routes each request by policy", "AA"),
        "round 138: the gateway routes each request by policy",
    ),
    (("round 138: memory grows until the buffer is full", "key"), "bssxh 138: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 138: memory grows until the buffer is full", "lemon"), "csgbq 138: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 138: memory grows until the buffer is full", "a"), "round 138: memory grows until the buffer is full"),
    (("round 138: memory grows until the buffer is full", "zz"), "qntmc 138: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 138: memory grows until the buffer is full", "AgentU"),
        "ruyaw 138: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 138: memory grows until the buffer is full", "keyboard"),
        "bssor 138: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 138: memory grows until the buffer is full", "AA"), "round 138: memory grows until the buffer is full"),
    (("round 138: the cluster mirrors every packet twice", "key"), "bssxh 138: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 138: the cluster mirrors every packet twice", "lemon"),
        "csgbq 138: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 138: the cluster mirrors every packet twice", "a"), "round 138: the cluster mirrors every packet twice"),
    (("round 138: the cluster mirrors every packet twice", "zz"), "qntmc 138: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 138: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 138: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 138: the cluster mirrors every packet twice", "keyboard"),
        "bssor 138: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 138: the cluster mirrors every packet twice", "AA"), "round 138: the cluster mirrors every packet twice"),
    (
        ("round 138: ranking uses tokens learned from the corpus", "key"),
        "bssxh 138: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 138: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", "a"),
        "round 138: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 138: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 138: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 138: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", "AA"),
        "round 138: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 138: a long session ends when the candle dies", "key"),
        "bssxh 138: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 138: a long session ends when the candle dies", "lemon"),
        "csgbq 138: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 138: a long session ends when the candle dies", "a"),
        "round 138: a long session ends when the candle dies",
    ),
    (
        ("round 138: a long session ends when the candle dies", "zz"),
        "qntmc 138: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 138: a long session ends when the candle dies", "AgentU"),
        "ruyaw 138: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 138: a long session ends when the candle dies", "keyboard"),
        "bssor 138: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 138: a long session ends when the candle dies", "AA"),
        "round 138: a long session ends when the candle dies",
    ),
    (("round 138: encode the prompt then map the result", "key"), "bssxh 138: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 138: encode the prompt then map the result", "lemon"), "csgbq 138: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 138: encode the prompt then map the result", "a"), "round 138: encode the prompt then map the result"),
    (("round 138: encode the prompt then map the result", "zz"), "qntmc 138: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 138: encode the prompt then map the result", "AgentU"),
        "ruyaw 138: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 138: encode the prompt then map the result", "keyboard"),
        "bssor 138: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 138: encode the prompt then map the result", "AA"), "round 138: encode the prompt then map the result"),
    (("round 138: the kernel wakes the worker at dawn", "key"), "bssxh 138: rri iovlop ukocc xfo ambocb er neux"),
    (("round 138: the kernel wakes the worker at dawn", "lemon"), "csgbq 138: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 138: the kernel wakes the worker at dawn", "a"), "round 138: the kernel wakes the worker at dawn"),
    (("round 138: the kernel wakes the worker at dawn", "zz"), "qntmc 138: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 138: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 138: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 138: the kernel wakes the worker at dawn", "keyboard"), "bssor 138: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 138: the kernel wakes the worker at dawn", "AA"), "round 138: the kernel wakes the worker at dawn"),
    (("round 138: service latency drops after the patch", "key"), "bssxh 138: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 138: service latency drops after the patch", "lemon"), "csgbq 138: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 138: service latency drops after the patch", "a"), "round 138: service latency drops after the patch"),
    (("round 138: service latency drops after the patch", "zz"), "qntmc 138: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 138: service latency drops after the patch", "AgentU"),
        "ruyaw 138: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 138: service latency drops after the patch", "keyboard"),
        "bssor 138: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 138: service latency drops after the patch", "AA"), "round 138: service latency drops after the patch"),
    (
        ("round 138: the library caches every vector it sees", "key"),
        "bssxh 138: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 138: the library caches every vector it sees", "lemon"),
        "csgbq 138: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 138: the library caches every vector it sees", "a"), "round 138: the library caches every vector it sees"),
    (
        ("round 138: the library caches every vector it sees", "zz"),
        "qntmc 138: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 138: the library caches every vector it sees", "AgentU"),
        "ruyaw 138: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 138: the library caches every vector it sees", "keyboard"),
        "bssor 138: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 138: the library caches every vector it sees", "AA"),
        "round 138: the library caches every vector it sees",
    ),
    (("round 138: agents argue then the debate resolves", "key"), "bssxh 138: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 138: agents argue then the debate resolves", "lemon"), "csgbq 138: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 138: agents argue then the debate resolves", "a"), "round 138: agents argue then the debate resolves"),
    (("round 138: agents argue then the debate resolves", "zz"), "qntmc 138: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 138: agents argue then the debate resolves", "AgentU"),
        "ruyaw 138: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 138: agents argue then the debate resolves", "keyboard"),
        "bssor 138: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 138: agents argue then the debate resolves", "AA"), "round 138: agents argue then the debate resolves"),
    (("round 138: the filter keeps only strong matches", "key"), "bssxh 138: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 138: the filter keeps only strong matches", "lemon"), "csgbq 138: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 138: the filter keeps only strong matches", "a"), "round 138: the filter keeps only strong matches"),
    (("round 138: the filter keeps only strong matches", "zz"), "qntmc 138: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 138: the filter keeps only strong matches", "AgentU"), "ruyaw 138: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 138: the filter keeps only strong matches", "keyboard"),
        "bssor 138: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 138: the filter keeps only strong matches", "AA"), "round 138: the filter keeps only strong matches"),
    (("round 138: the model answers with a short reply", "key"), "bssxh 138: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 138: the model answers with a short reply", "lemon"), "csgbq 138: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 138: the model answers with a short reply", "a"), "round 138: the model answers with a short reply"),
    (("round 138: the model answers with a short reply", "zz"), "qntmc 138: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 138: the model answers with a short reply", "AgentU"), "ruyaw 138: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 138: the model answers with a short reply", "keyboard"),
        "bssor 138: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 138: the model answers with a short reply", "AA"), "round 138: the model answers with a short reply"),
    (
        ("round 138: the recorder stores the reasoning trace", "key"),
        "bssxh 138: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 138: the recorder stores the reasoning trace", "lemon"),
        "csgbq 138: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 138: the recorder stores the reasoning trace", "a"), "round 138: the recorder stores the reasoning trace"),
    (
        ("round 138: the recorder stores the reasoning trace", "zz"),
        "qntmc 138: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 138: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 138: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 138: the recorder stores the reasoning trace", "keyboard"),
        "bssor 138: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 138: the recorder stores the reasoning trace", "AA"),
        "round 138: the recorder stores the reasoning trace",
    ),
    (("round 138: the angel watches the processor run", "key"), "bssxh 138: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 138: the angel watches the processor run", "lemon"), "csgbq 138: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 138: the angel watches the processor run", "a"), "round 138: the angel watches the processor run"),
    (("round 138: the angel watches the processor run", "zz"), "qntmc 138: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 138: the angel watches the processor run", "AgentU"), "ruyaw 138: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 138: the angel watches the processor run", "keyboard"), "bssor 138: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 138: the angel watches the processor run", "AA"), "round 138: the angel watches the processor run"),
    (("round 138: angle of the vector decides the match", "key"), "bssxh 138: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 138: angle of the vector decides the match", "lemon"), "csgbq 138: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 138: angle of the vector decides the match", "a"), "round 138: angle of the vector decides the match"),
    (("round 138: angle of the vector decides the match", "zz"), "qntmc 138: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 138: angle of the vector decides the match", "AgentU"),
        "ruyaw 138: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 138: angle of the vector decides the match", "keyboard"),
        "bssor 138: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 138: angle of the vector decides the match", "AA"), "round 138: angle of the vector decides the match"),
    (
        ("round 138: the candle burns twice as long at night", "key"),
        "bssxh 138: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 138: the candle burns twice as long at night", "lemon"),
        "csgbq 138: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 138: the candle burns twice as long at night", "a"), "round 138: the candle burns twice as long at night"),
    (
        ("round 138: the candle burns twice as long at night", "zz"),
        "qntmc 138: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 138: the candle burns twice as long at night", "AgentU"),
        "ruyaw 138: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 138: the candle burns twice as long at night", "keyboard"),
        "bssor 138: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 138: the candle burns twice as long at night", "AA"),
        "round 138: the candle burns twice as long at night",
    ),
    (("round 138: a mirror of the universe in one line", "key"), "bssxh 138: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 138: a mirror of the universe in one line", "lemon"), "csgbq 138: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 138: a mirror of the universe in one line", "a"), "round 138: a mirror of the universe in one line"),
    (("round 138: a mirror of the universe in one line", "zz"), "qntmc 138: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 138: a mirror of the universe in one line", "AgentU"), "ruyaw 138: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 138: a mirror of the universe in one line", "keyboard"),
        "bssor 138: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 138: a mirror of the universe in one line", "AA"), "round 138: a mirror of the universe in one line"),
    (("round 138: the queue drains before the storm", "key"), "bssxh 138: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 138: the queue drains before the storm", "lemon"), "csgbq 138: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 138: the queue drains before the storm", "a"), "round 138: the queue drains before the storm"),
    (("round 138: the queue drains before the storm", "zz"), "qntmc 138: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 138: the queue drains before the storm", "AgentU"), "ruyaw 138: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 138: the queue drains before the storm", "keyboard"), "bssor 138: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 138: the queue drains before the storm", "AA"), "round 138: the queue drains before the storm"),
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
