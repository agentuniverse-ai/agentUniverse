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
    (("kitten110", "key"), "umrdil110"),
    (("kitten110", "lemon"), "vmfhry110"),
    (("kitten110", "a"), "kitten110"),
    (("kitten110", "zz"), "jhssdm110"),
    (("kitten110", "AgentU"), "koxgxh110"),
    (("kitten110", "keyboard"), "umrusn110"),
    (("kitten110", "AA"), "kitten110"),
    (("sitting110", "key"), "cmrdmlq110"),
    (("sitting110", "lemon"), "dmfhvyk110"),
    (("sitting110", "a"), "sitting110"),
    (("sitting110", "zz"), "rhsshmf110"),
    (("sitting110", "AgentU"), "soxgbhg110"),
    (("sitting110", "keyboard"), "cmruwnx110"),
    (("sitting110", "AA"), "sitting110"),
    (("agent110", "key"), "kkcxx110"),
    (("agent110", "lemon"), "lkqbg110"),
    (("agent110", "a"), "agent110"),
    (("agent110", "zz"), "zfdms110"),
    (("agent110", "AgentU"), "amiam110"),
    (("agent110", "keyboard"), "kkcoh110"),
    (("agent110", "AA"), "agent110"),
    (("angle110", "key"), "krevi110"),
    (("angle110", "lemon"), "lrszr110"),
    (("angle110", "a"), "angle110"),
    (("angle110", "zz"), "zmfkd110"),
    (("angle110", "AgentU"), "atkyx110"),
    (("angle110", "keyboard"), "krems110"),
    (("angle110", "AA"), "angle110"),
    (("universe110", "key"), "ergfipci110"),
    (("universe110", "lemon"), "frujrcwq110"),
    (("universe110", "a"), "universe110"),
    (("universe110", "zz"), "tmhudqrd110"),
    (("universe110", "AgentU"), "utmixlsk110"),
    (("universe110", "keyboard"), "ergwsrjh110"),
    (("universe110", "AA"), "universe110"),
    (("memory110", "key"), "wikyvw110"),
    (("memory110", "lemon"), "xiycej110"),
    (("memory110", "a"), "memory110"),
    (("memory110", "zz"), "ldlnqx110"),
    (("memory110", "AgentU"), "mkqbks110"),
    (("memory110", "keyboard"), "wikpfy110"),
    (("memory110", "AA"), "memory110"),
    (("stream110", "key"), "cxpoek110"),
    (("stream110", "lemon"), "dxdsnx110"),
    (("stream110", "a"), "stream110"),
    (("stream110", "zz"), "rsqdzl110"),
    (("stream110", "AgentU"), "szvrtg110"),
    (("stream110", "keyboard"), "cxpfom110"),
    (("stream110", "AA"), "stream110"),
    (("context110", "key"), "msldivd110"),
    (("context110", "lemon"), "nszhrix110"),
    (("context110", "a"), "context110"),
    (("context110", "zz"), "bnmsdws110"),
    (("context110", "AgentU"), "curgxrt110"),
    (("context110", "keyboard"), "mslusxk110"),
    (("context110", "AA"), "context110"),
    (("knowledge110", "key"), "urmgpcnkc110"),
    (("knowledge110", "lemon"), "vrakyphss110"),
    (("knowledge110", "a"), "knowledge110"),
    (("knowledge110", "zz"), "jmnvkdcfd110"),
    (("knowledge110", "AgentU"), "ktsjeydmi110"),
    (("knowledge110", "keyboard"), "urmxzeujo110"),
    (("knowledge110", "AA"), "knowledge110"),
    (("vector110", "key"), "fiadsp110"),
    (("vector110", "lemon"), "giohbc110"),
    (("vector110", "a"), "vector110"),
    (("vector110", "zz"), "udbsnq110"),
    (("vector110", "AgentU"), "vkgghl110"),
    (("vector110", "keyboard"), "fiaucr110"),
    (("vector110", "AA"), "vector110"),
    (("processor110", "key"), "zvmmiqcsp110"),
    (("processor110", "lemon"), "avaqrdwaf110"),
    (("processor110", "a"), "processor110"),
    (("processor110", "zz"), "oqnbdrrnq110"),
    (("processor110", "AgentU"), "pxspxmsuv110"),
    (("processor110", "keyboard"), "zvmdssjrb110"),
    (("processor110", "AA"), "processor110"),
    (("reasoning110", "key"), "biycslsre110"),
    (("reasoning110", "lemon"), "cimgbymzu110"),
    (("reasoning110", "a"), "reasoning110"),
    (("reasoning110", "zz"), "qdzrnmhmf110"),
    (("reasoning110", "AgentU"), "rkefhhitk110"),
    (("reasoning110", "keyboard"), "biytcnzqq110"),
    (("reasoning110", "AA"), "reasoning110"),
    (("machine110", "key"), "wearmlo110"),
    (("machine110", "lemon"), "xeovvyi110"),
    (("machine110", "a"), "machine110"),
    (("machine110", "zz"), "lzbghmd110"),
    (("machine110", "AgentU"), "mggubhe110"),
    (("machine110", "keyboard"), "weaiwnv110"),
    (("machine110", "AA"), "machine110"),
    (("learning110", "key"), "viybrgxk110"),
    (("learning110", "lemon"), "wimfatrs110"),
    (("learning110", "a"), "learning110"),
    (("learning110", "zz"), "kdzqmhmf110"),
    (("learning110", "AgentU"), "lkeegcnm110"),
    (("learning110", "keyboard"), "viysbiej110"),
    (("learning110", "AA"), "learning110"),
    (("model110", "key"), "wsbop110"),
    (("model110", "lemon"), "xspsy110"),
    (("model110", "a"), "model110"),
    (("model110", "zz"), "lncdk110"),
    (("model110", "AgentU"), "muhre110"),
    (("model110", "keyboard"), "wsbfz110"),
    (("model110", "AA"), "model110"),
    (("token110", "key"), "dsior110"),
    (("token110", "lemon"), "eswsa110"),
    (("token110", "a"), "token110"),
    (("token110", "zz"), "snjdm110"),
    (("token110", "AgentU"), "tuorg110"),
    (("token110", "keyboard"), "dsifb110"),
    (("token110", "AA"), "token110"),
    (("prompt110", "key"), "zvmwtr110"),
    (("prompt110", "lemon"), "avaace110"),
    (("prompt110", "a"), "prompt110"),
    (("prompt110", "zz"), "oqnlos110"),
    (("prompt110", "AgentU"), "pxszin110"),
    (("prompt110", "keyboard"), "zvmndt110"),
    (("prompt110", "AA"), "prompt110"),
    (("session110", "key"), "ciqcmmx110"),
    (("session110", "lemon"), "diegvzr110"),
    (("session110", "a"), "session110"),
    (("session110", "zz"), "rdrrhnm110"),
    (("session110", "AgentU"), "skwfbin110"),
    (("session110", "keyboard"), "ciqtwoe110"),
    (("session110", "AA"), "session110"),
    (("library110", "key"), "vmzbepi110"),
    (("library110", "lemon"), "wmnfncc110"),
    (("library110", "a"), "library110"),
    (("library110", "zz"), "khaqzqx110"),
    (("library110", "AgentU"), "lofetly110"),
    (("library110", "keyboard"), "vmzsorp110"),
    (("library110", "AA"), "library110"),
    (("service110", "key"), "cipfmao110"),
    (("service110", "lemon"), "didjvni110"),
    (("service110", "a"), "service110"),
    (("service110", "zz"), "rdquhbd110"),
    (("service110", "AgentU"), "skvibwe110"),
    (("service110", "keyboard"), "cipwwcv110"),
    (("service110", "AA"), "service110"),
    (("gateway110", "key"), "qeroayi110"),
    (("gateway110", "lemon"), "refsjlc110"),
    (("gateway110", "a"), "gateway110"),
    (("gateway110", "zz"), "fzsdvzx110"),
    (("gateway110", "AgentU"), "ggxrpuy110"),
    (("gateway110", "keyboard"), "qerfkap110"),
    (("gateway110", "AA"), "gateway110"),
    (("storage110", "key"), "cxmbeeo110"),
    (("storage110", "lemon"), "dxafnri110"),
    (("storage110", "a"), "storage110"),
    (("storage110", "zz"), "rsnqzfd110"),
    (("storage110", "AgentU"), "szsetae110"),
    (("storage110", "keyboard"), "cxmsogv110"),
    (("storage110", "AA"), "storage110"),
    (("network110", "key"), "xirgspu110"),
    (("network110", "lemon"), "yifkbco110"),
    (("network110", "a"), "network110"),
    (("network110", "zz"), "mdsvnqj110"),
    (("network110", "AgentU"), "nkxjhlk110"),
    (("network110", "keyboard"), "xirxcrb110"),
    (("network110", "AA"), "network110"),
    (("latency110", "key"), "verorai110"),
    (("latency110", "lemon"), "wefsanc110"),
    (("latency110", "a"), "latency110"),
    (("latency110", "zz"), "kzsdmbx110"),
    (("latency110", "AgentU"), "lgxrgwy110"),
    (("latency110", "keyboard"), "verfbcp110"),
    (("latency110", "AA"), "latency110"),
    (("buffer110", "key"), "lydpip110"),
    (("buffer110", "lemon"), "myrtrc110"),
    (("buffer110", "a"), "buffer110"),
    (("buffer110", "zz"), "ateedq110"),
    (("buffer110", "AgentU"), "bajsxl110"),
    (("buffer110", "keyboard"), "lydgsr110"),
    (("buffer110", "AA"), "buffer110"),
    (("queue110", "key"), "aycei110"),
    (("queue110", "lemon"), "byqir110"),
    (("queue110", "a"), "queue110"),
    (("queue110", "zz"), "ptdtd110"),
    (("queue110", "AgentU"), "qaihx110"),
    (("queue110", "keyboard"), "aycvs110"),
    (("queue110", "AA"), "queue110"),
    (("worker110", "key"), "gspuip110"),
    (("worker110", "lemon"), "hsdyrc110"),
    (("worker110", "a"), "worker110"),
    (("worker110", "zz"), "vnqjdq110"),
    (("worker110", "AgentU"), "wuvxxl110"),
    (("worker110", "keyboard"), "gsplsr110"),
    (("worker110", "AA"), "worker110"),
    (("kernel110", "key"), "uipxij110"),
    (("kernel110", "lemon"), "vidbrw110"),
    (("kernel110", "a"), "kernel110"),
    (("kernel110", "zz"), "jdqmdk110"),
    (("kernel110", "AgentU"), "kkvaxf110"),
    (("kernel110", "keyboard"), "uiposl110"),
    (("kernel110", "AA"), "kernel110"),
    (("signal110", "key"), "cmexej110"),
    (("signal110", "lemon"), "dmsbnw110"),
    (("signal110", "a"), "signal110"),
    (("signal110", "zz"), "rhfmzk110"),
    (("signal110", "AgentU"), "sokatf110"),
    (("signal110", "keyboard"), "cmeool110"),
    (("signal110", "AA"), "signal110"),
    (("packet110", "key"), "zeauir110"),
    (("packet110", "lemon"), "aeoyre110"),
    (("packet110", "a"), "packet110"),
    (("packet110", "zz"), "ozbjds110"),
    (("packet110", "AgentU"), "pggxxn110"),
    (("packet110", "keyboard"), "zealst110"),
    (("packet110", "AA"), "packet110"),
    (("router110", "key"), "bssdip110"),
    (("router110", "lemon"), "csghrc110"),
    (("router110", "a"), "router110"),
    (("router110", "zz"), "qntsdq110"),
    (("router110", "AgentU"), "ruygxl110"),
    (("router110", "keyboard"), "bssusr110"),
    (("router110", "AA"), "router110"),
    (("cluster110", "key"), "mpscxcb110"),
    (("cluster110", "lemon"), "npgggpv110"),
    (("cluster110", "a"), "cluster110"),
    (("cluster110", "zz"), "bktrsdq110"),
    (("cluster110", "AgentU"), "cryfmyr110"),
    (("cluster110", "keyboard"), "mpsthei110"),
    (("cluster110", "AA"), "cluster110"),
    (("mirror110", "key"), "wmpbsp110"),
    (("mirror110", "lemon"), "xmdfbc110"),
    (("mirror110", "a"), "mirror110"),
    (("mirror110", "zz"), "lhqqnq110"),
    (("mirror110", "AgentU"), "movehl110"),
    (("mirror110", "keyboard"), "wmpscr110"),
    (("mirror110", "AA"), "mirror110"),
    (("filter110", "key"), "pmjdip110"),
    (("filter110", "lemon"), "qmxhrc110"),
    (("filter110", "a"), "filter110"),
    (("filter110", "zz"), "ehksdq110"),
    (("filter110", "AgentU"), "fopgxl110"),
    (("filter110", "keyboard"), "pmjusr110"),
    (("filter110", "AA"), "filter110"),
    (("ranking110", "key"), "belumlq110"),
    (("ranking110", "lemon"), "cezyvyk110"),
    (("ranking110", "a"), "ranking110"),
    (("ranking110", "zz"), "qzmjhmf110"),
    (("ranking110", "AgentU"), "rgrxbhg110"),
    (("ranking110", "keyboard"), "bellwnx110"),
    (("ranking110", "AA"), "ranking110"),
    (("encoding110", "key"), "orayhgxk110"),
    (("encoding110", "lemon"), "procqtrs110"),
    (("encoding110", "a"), "encoding110"),
    (("encoding110", "zz"), "dmbnchmf110"),
    (("encoding110", "AgentU"), "etgbwcnm110"),
    (("encoding110", "keyboard"), "orapriej110"),
    (("encoding110", "AA"), "encoding110"),
    (("mapping110", "key"), "wenzmlq110"),
    (("mapping110", "lemon"), "xebdvyk110"),
    (("mapping110", "a"), "mapping110"),
    (("mapping110", "zz"), "lzoohmf110"),
    (("mapping110", "AgentU"), "mgtcbhg110"),
    (("mapping110", "keyboard"), "wenqwnx110"),
    (("mapping110", "AA"), "mapping110"),
    (("record110", "key"), "biayvb110"),
    (("record110", "lemon"), "cioceo110"),
    (("record110", "a"), "record110"),
    (("record110", "zz"), "qdbnqc110"),
    (("record110", "AgentU"), "rkgbkx110"),
    (("record110", "keyboard"), "biapfd110"),
    (("record110", "AA"), "record110"),
    (("candle110", "key"), "melnpc110"),
    (("candle110", "lemon"), "nezryp110"),
    (("candle110", "a"), "candle110"),
    (("candle110", "zz"), "bzmckd110"),
    (("candle110", "AgentU"), "cgrqey110"),
    (("candle110", "keyboard"), "meleze110"),
    (("candle110", "AA"), "candle110"),
    (("thread110", "key"), "dlpoeb110"),
    (("thread110", "lemon"), "eldsno110"),
    (("thread110", "a"), "thread110"),
    (("thread110", "zz"), "sgqdzc110"),
    (("thread110", "AgentU"), "tnvrtx110"),
    (("thread110", "keyboard"), "dlpfod110"),
    (("thread110", "AA"), "thread110"),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 110: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 110: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "a"),
        "round 110: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 110: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 110: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 110: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", "AA"),
        "round 110: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "key"),
        "bssxh 110: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 110: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "a"),
        "round 110: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 110: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 110: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 110: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", "AA"),
        "round 110: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 110: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 110: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "a"),
        "round 110: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 110: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 110: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 110: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", "AA"),
        "round 110: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 110: the processor reads the record then stops", "key"),
        "bssxh 110: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 110: the processor reads the record then stops", "lemon"),
        "csgbq 110: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 110: the processor reads the record then stops", "a"),
        "round 110: the processor reads the record then stops",
    ),
    (
        ("round 110: the processor reads the record then stops", "zz"),
        "qntmc 110: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 110: the processor reads the record then stops", "AgentU"),
        "ruyaw 110: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 110: the processor reads the record then stops", "keyboard"),
        "bssor 110: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 110: the processor reads the record then stops", "AA"),
        "round 110: the processor reads the record then stops",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "key"),
        "bssxh 110: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "lemon"),
        "csgbq 110: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "a"),
        "round 110: a worker pulls the next task from the queue",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "zz"),
        "qntmc 110: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 110: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "keyboard"),
        "bssor 110: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 110: a worker pulls the next task from the queue", "AA"),
        "round 110: a worker pulls the next task from the queue",
    ),
    (
        ("round 110: signals travel through the network layer", "key"),
        "bssxh 110: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 110: signals travel through the network layer", "lemon"),
        "csgbq 110: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 110: signals travel through the network layer", "a"),
        "round 110: signals travel through the network layer",
    ),
    (
        ("round 110: signals travel through the network layer", "zz"),
        "qntmc 110: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 110: signals travel through the network layer", "AgentU"),
        "ruyaw 110: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 110: signals travel through the network layer", "keyboard"),
        "bssor 110: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 110: signals travel through the network layer", "AA"),
        "round 110: signals travel through the network layer",
    ),
    (
        ("round 110: the gateway routes each request by policy", "key"),
        "bssxh 110: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 110: the gateway routes each request by policy", "lemon"),
        "csgbq 110: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 110: the gateway routes each request by policy", "a"),
        "round 110: the gateway routes each request by policy",
    ),
    (
        ("round 110: the gateway routes each request by policy", "zz"),
        "qntmc 110: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 110: the gateway routes each request by policy", "AgentU"),
        "ruyaw 110: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 110: the gateway routes each request by policy", "keyboard"),
        "bssor 110: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 110: the gateway routes each request by policy", "AA"),
        "round 110: the gateway routes each request by policy",
    ),
    (("round 110: memory grows until the buffer is full", "key"), "bssxh 110: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 110: memory grows until the buffer is full", "lemon"), "csgbq 110: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 110: memory grows until the buffer is full", "a"), "round 110: memory grows until the buffer is full"),
    (("round 110: memory grows until the buffer is full", "zz"), "qntmc 110: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 110: memory grows until the buffer is full", "AgentU"),
        "ruyaw 110: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 110: memory grows until the buffer is full", "keyboard"),
        "bssor 110: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 110: memory grows until the buffer is full", "AA"), "round 110: memory grows until the buffer is full"),
    (("round 110: the cluster mirrors every packet twice", "key"), "bssxh 110: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 110: the cluster mirrors every packet twice", "lemon"),
        "csgbq 110: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 110: the cluster mirrors every packet twice", "a"), "round 110: the cluster mirrors every packet twice"),
    (("round 110: the cluster mirrors every packet twice", "zz"), "qntmc 110: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 110: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 110: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 110: the cluster mirrors every packet twice", "keyboard"),
        "bssor 110: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 110: the cluster mirrors every packet twice", "AA"), "round 110: the cluster mirrors every packet twice"),
    (
        ("round 110: ranking uses tokens learned from the corpus", "key"),
        "bssxh 110: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 110: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", "a"),
        "round 110: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 110: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 110: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 110: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", "AA"),
        "round 110: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 110: a long session ends when the candle dies", "key"),
        "bssxh 110: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 110: a long session ends when the candle dies", "lemon"),
        "csgbq 110: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 110: a long session ends when the candle dies", "a"),
        "round 110: a long session ends when the candle dies",
    ),
    (
        ("round 110: a long session ends when the candle dies", "zz"),
        "qntmc 110: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 110: a long session ends when the candle dies", "AgentU"),
        "ruyaw 110: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 110: a long session ends when the candle dies", "keyboard"),
        "bssor 110: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 110: a long session ends when the candle dies", "AA"),
        "round 110: a long session ends when the candle dies",
    ),
    (("round 110: encode the prompt then map the result", "key"), "bssxh 110: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 110: encode the prompt then map the result", "lemon"), "csgbq 110: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 110: encode the prompt then map the result", "a"), "round 110: encode the prompt then map the result"),
    (("round 110: encode the prompt then map the result", "zz"), "qntmc 110: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 110: encode the prompt then map the result", "AgentU"),
        "ruyaw 110: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 110: encode the prompt then map the result", "keyboard"),
        "bssor 110: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 110: encode the prompt then map the result", "AA"), "round 110: encode the prompt then map the result"),
    (("round 110: the kernel wakes the worker at dawn", "key"), "bssxh 110: rri iovlop ukocc xfo ambocb er neux"),
    (("round 110: the kernel wakes the worker at dawn", "lemon"), "csgbq 110: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 110: the kernel wakes the worker at dawn", "a"), "round 110: the kernel wakes the worker at dawn"),
    (("round 110: the kernel wakes the worker at dawn", "zz"), "qntmc 110: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 110: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 110: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 110: the kernel wakes the worker at dawn", "keyboard"), "bssor 110: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 110: the kernel wakes the worker at dawn", "AA"), "round 110: the kernel wakes the worker at dawn"),
    (("round 110: service latency drops after the patch", "key"), "bssxh 110: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 110: service latency drops after the patch", "lemon"), "csgbq 110: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 110: service latency drops after the patch", "a"), "round 110: service latency drops after the patch"),
    (("round 110: service latency drops after the patch", "zz"), "qntmc 110: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 110: service latency drops after the patch", "AgentU"),
        "ruyaw 110: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 110: service latency drops after the patch", "keyboard"),
        "bssor 110: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 110: service latency drops after the patch", "AA"), "round 110: service latency drops after the patch"),
    (
        ("round 110: the library caches every vector it sees", "key"),
        "bssxh 110: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 110: the library caches every vector it sees", "lemon"),
        "csgbq 110: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 110: the library caches every vector it sees", "a"), "round 110: the library caches every vector it sees"),
    (
        ("round 110: the library caches every vector it sees", "zz"),
        "qntmc 110: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 110: the library caches every vector it sees", "AgentU"),
        "ruyaw 110: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 110: the library caches every vector it sees", "keyboard"),
        "bssor 110: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 110: the library caches every vector it sees", "AA"),
        "round 110: the library caches every vector it sees",
    ),
    (("round 110: agents argue then the debate resolves", "key"), "bssxh 110: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 110: agents argue then the debate resolves", "lemon"), "csgbq 110: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 110: agents argue then the debate resolves", "a"), "round 110: agents argue then the debate resolves"),
    (("round 110: agents argue then the debate resolves", "zz"), "qntmc 110: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 110: agents argue then the debate resolves", "AgentU"),
        "ruyaw 110: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 110: agents argue then the debate resolves", "keyboard"),
        "bssor 110: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 110: agents argue then the debate resolves", "AA"), "round 110: agents argue then the debate resolves"),
    (("round 110: the filter keeps only strong matches", "key"), "bssxh 110: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 110: the filter keeps only strong matches", "lemon"), "csgbq 110: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 110: the filter keeps only strong matches", "a"), "round 110: the filter keeps only strong matches"),
    (("round 110: the filter keeps only strong matches", "zz"), "qntmc 110: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 110: the filter keeps only strong matches", "AgentU"), "ruyaw 110: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 110: the filter keeps only strong matches", "keyboard"),
        "bssor 110: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 110: the filter keeps only strong matches", "AA"), "round 110: the filter keeps only strong matches"),
    (("round 110: the model answers with a short reply", "key"), "bssxh 110: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 110: the model answers with a short reply", "lemon"), "csgbq 110: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 110: the model answers with a short reply", "a"), "round 110: the model answers with a short reply"),
    (("round 110: the model answers with a short reply", "zz"), "qntmc 110: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 110: the model answers with a short reply", "AgentU"), "ruyaw 110: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 110: the model answers with a short reply", "keyboard"),
        "bssor 110: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 110: the model answers with a short reply", "AA"), "round 110: the model answers with a short reply"),
    (
        ("round 110: the recorder stores the reasoning trace", "key"),
        "bssxh 110: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 110: the recorder stores the reasoning trace", "lemon"),
        "csgbq 110: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 110: the recorder stores the reasoning trace", "a"), "round 110: the recorder stores the reasoning trace"),
    (
        ("round 110: the recorder stores the reasoning trace", "zz"),
        "qntmc 110: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 110: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 110: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 110: the recorder stores the reasoning trace", "keyboard"),
        "bssor 110: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 110: the recorder stores the reasoning trace", "AA"),
        "round 110: the recorder stores the reasoning trace",
    ),
    (("round 110: the angel watches the processor run", "key"), "bssxh 110: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 110: the angel watches the processor run", "lemon"), "csgbq 110: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 110: the angel watches the processor run", "a"), "round 110: the angel watches the processor run"),
    (("round 110: the angel watches the processor run", "zz"), "qntmc 110: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 110: the angel watches the processor run", "AgentU"), "ruyaw 110: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 110: the angel watches the processor run", "keyboard"), "bssor 110: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 110: the angel watches the processor run", "AA"), "round 110: the angel watches the processor run"),
    (("round 110: angle of the vector decides the match", "key"), "bssxh 110: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 110: angle of the vector decides the match", "lemon"), "csgbq 110: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 110: angle of the vector decides the match", "a"), "round 110: angle of the vector decides the match"),
    (("round 110: angle of the vector decides the match", "zz"), "qntmc 110: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 110: angle of the vector decides the match", "AgentU"),
        "ruyaw 110: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 110: angle of the vector decides the match", "keyboard"),
        "bssor 110: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 110: angle of the vector decides the match", "AA"), "round 110: angle of the vector decides the match"),
    (
        ("round 110: the candle burns twice as long at night", "key"),
        "bssxh 110: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 110: the candle burns twice as long at night", "lemon"),
        "csgbq 110: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 110: the candle burns twice as long at night", "a"), "round 110: the candle burns twice as long at night"),
    (
        ("round 110: the candle burns twice as long at night", "zz"),
        "qntmc 110: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 110: the candle burns twice as long at night", "AgentU"),
        "ruyaw 110: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 110: the candle burns twice as long at night", "keyboard"),
        "bssor 110: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 110: the candle burns twice as long at night", "AA"),
        "round 110: the candle burns twice as long at night",
    ),
    (("round 110: a mirror of the universe in one line", "key"), "bssxh 110: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 110: a mirror of the universe in one line", "lemon"), "csgbq 110: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 110: a mirror of the universe in one line", "a"), "round 110: a mirror of the universe in one line"),
    (("round 110: a mirror of the universe in one line", "zz"), "qntmc 110: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 110: a mirror of the universe in one line", "AgentU"), "ruyaw 110: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 110: a mirror of the universe in one line", "keyboard"),
        "bssor 110: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 110: a mirror of the universe in one line", "AA"), "round 110: a mirror of the universe in one line"),
    (("round 110: the queue drains before the storm", "key"), "bssxh 110: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 110: the queue drains before the storm", "lemon"), "csgbq 110: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 110: the queue drains before the storm", "a"), "round 110: the queue drains before the storm"),
    (("round 110: the queue drains before the storm", "zz"), "qntmc 110: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 110: the queue drains before the storm", "AgentU"), "ruyaw 110: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 110: the queue drains before the storm", "keyboard"), "bssor 110: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 110: the queue drains before the storm", "AA"), "round 110: the queue drains before the storm"),
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
