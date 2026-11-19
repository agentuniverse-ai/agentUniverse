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
    (("kitten156", "key"), "umrdil156"),
    (("kitten156", "lemon"), "vmfhry156"),
    (("kitten156", "a"), "kitten156"),
    (("kitten156", "zz"), "jhssdm156"),
    (("kitten156", "AgentU"), "koxgxh156"),
    (("kitten156", "keyboard"), "umrusn156"),
    (("kitten156", "AA"), "kitten156"),
    (("sitting156", "key"), "cmrdmlq156"),
    (("sitting156", "lemon"), "dmfhvyk156"),
    (("sitting156", "a"), "sitting156"),
    (("sitting156", "zz"), "rhsshmf156"),
    (("sitting156", "AgentU"), "soxgbhg156"),
    (("sitting156", "keyboard"), "cmruwnx156"),
    (("sitting156", "AA"), "sitting156"),
    (("agent156", "key"), "kkcxx156"),
    (("agent156", "lemon"), "lkqbg156"),
    (("agent156", "a"), "agent156"),
    (("agent156", "zz"), "zfdms156"),
    (("agent156", "AgentU"), "amiam156"),
    (("agent156", "keyboard"), "kkcoh156"),
    (("agent156", "AA"), "agent156"),
    (("angle156", "key"), "krevi156"),
    (("angle156", "lemon"), "lrszr156"),
    (("angle156", "a"), "angle156"),
    (("angle156", "zz"), "zmfkd156"),
    (("angle156", "AgentU"), "atkyx156"),
    (("angle156", "keyboard"), "krems156"),
    (("angle156", "AA"), "angle156"),
    (("universe156", "key"), "ergfipci156"),
    (("universe156", "lemon"), "frujrcwq156"),
    (("universe156", "a"), "universe156"),
    (("universe156", "zz"), "tmhudqrd156"),
    (("universe156", "AgentU"), "utmixlsk156"),
    (("universe156", "keyboard"), "ergwsrjh156"),
    (("universe156", "AA"), "universe156"),
    (("memory156", "key"), "wikyvw156"),
    (("memory156", "lemon"), "xiycej156"),
    (("memory156", "a"), "memory156"),
    (("memory156", "zz"), "ldlnqx156"),
    (("memory156", "AgentU"), "mkqbks156"),
    (("memory156", "keyboard"), "wikpfy156"),
    (("memory156", "AA"), "memory156"),
    (("stream156", "key"), "cxpoek156"),
    (("stream156", "lemon"), "dxdsnx156"),
    (("stream156", "a"), "stream156"),
    (("stream156", "zz"), "rsqdzl156"),
    (("stream156", "AgentU"), "szvrtg156"),
    (("stream156", "keyboard"), "cxpfom156"),
    (("stream156", "AA"), "stream156"),
    (("context156", "key"), "msldivd156"),
    (("context156", "lemon"), "nszhrix156"),
    (("context156", "a"), "context156"),
    (("context156", "zz"), "bnmsdws156"),
    (("context156", "AgentU"), "curgxrt156"),
    (("context156", "keyboard"), "mslusxk156"),
    (("context156", "AA"), "context156"),
    (("knowledge156", "key"), "urmgpcnkc156"),
    (("knowledge156", "lemon"), "vrakyphss156"),
    (("knowledge156", "a"), "knowledge156"),
    (("knowledge156", "zz"), "jmnvkdcfd156"),
    (("knowledge156", "AgentU"), "ktsjeydmi156"),
    (("knowledge156", "keyboard"), "urmxzeujo156"),
    (("knowledge156", "AA"), "knowledge156"),
    (("vector156", "key"), "fiadsp156"),
    (("vector156", "lemon"), "giohbc156"),
    (("vector156", "a"), "vector156"),
    (("vector156", "zz"), "udbsnq156"),
    (("vector156", "AgentU"), "vkgghl156"),
    (("vector156", "keyboard"), "fiaucr156"),
    (("vector156", "AA"), "vector156"),
    (("processor156", "key"), "zvmmiqcsp156"),
    (("processor156", "lemon"), "avaqrdwaf156"),
    (("processor156", "a"), "processor156"),
    (("processor156", "zz"), "oqnbdrrnq156"),
    (("processor156", "AgentU"), "pxspxmsuv156"),
    (("processor156", "keyboard"), "zvmdssjrb156"),
    (("processor156", "AA"), "processor156"),
    (("reasoning156", "key"), "biycslsre156"),
    (("reasoning156", "lemon"), "cimgbymzu156"),
    (("reasoning156", "a"), "reasoning156"),
    (("reasoning156", "zz"), "qdzrnmhmf156"),
    (("reasoning156", "AgentU"), "rkefhhitk156"),
    (("reasoning156", "keyboard"), "biytcnzqq156"),
    (("reasoning156", "AA"), "reasoning156"),
    (("machine156", "key"), "wearmlo156"),
    (("machine156", "lemon"), "xeovvyi156"),
    (("machine156", "a"), "machine156"),
    (("machine156", "zz"), "lzbghmd156"),
    (("machine156", "AgentU"), "mggubhe156"),
    (("machine156", "keyboard"), "weaiwnv156"),
    (("machine156", "AA"), "machine156"),
    (("learning156", "key"), "viybrgxk156"),
    (("learning156", "lemon"), "wimfatrs156"),
    (("learning156", "a"), "learning156"),
    (("learning156", "zz"), "kdzqmhmf156"),
    (("learning156", "AgentU"), "lkeegcnm156"),
    (("learning156", "keyboard"), "viysbiej156"),
    (("learning156", "AA"), "learning156"),
    (("model156", "key"), "wsbop156"),
    (("model156", "lemon"), "xspsy156"),
    (("model156", "a"), "model156"),
    (("model156", "zz"), "lncdk156"),
    (("model156", "AgentU"), "muhre156"),
    (("model156", "keyboard"), "wsbfz156"),
    (("model156", "AA"), "model156"),
    (("token156", "key"), "dsior156"),
    (("token156", "lemon"), "eswsa156"),
    (("token156", "a"), "token156"),
    (("token156", "zz"), "snjdm156"),
    (("token156", "AgentU"), "tuorg156"),
    (("token156", "keyboard"), "dsifb156"),
    (("token156", "AA"), "token156"),
    (("prompt156", "key"), "zvmwtr156"),
    (("prompt156", "lemon"), "avaace156"),
    (("prompt156", "a"), "prompt156"),
    (("prompt156", "zz"), "oqnlos156"),
    (("prompt156", "AgentU"), "pxszin156"),
    (("prompt156", "keyboard"), "zvmndt156"),
    (("prompt156", "AA"), "prompt156"),
    (("session156", "key"), "ciqcmmx156"),
    (("session156", "lemon"), "diegvzr156"),
    (("session156", "a"), "session156"),
    (("session156", "zz"), "rdrrhnm156"),
    (("session156", "AgentU"), "skwfbin156"),
    (("session156", "keyboard"), "ciqtwoe156"),
    (("session156", "AA"), "session156"),
    (("library156", "key"), "vmzbepi156"),
    (("library156", "lemon"), "wmnfncc156"),
    (("library156", "a"), "library156"),
    (("library156", "zz"), "khaqzqx156"),
    (("library156", "AgentU"), "lofetly156"),
    (("library156", "keyboard"), "vmzsorp156"),
    (("library156", "AA"), "library156"),
    (("service156", "key"), "cipfmao156"),
    (("service156", "lemon"), "didjvni156"),
    (("service156", "a"), "service156"),
    (("service156", "zz"), "rdquhbd156"),
    (("service156", "AgentU"), "skvibwe156"),
    (("service156", "keyboard"), "cipwwcv156"),
    (("service156", "AA"), "service156"),
    (("gateway156", "key"), "qeroayi156"),
    (("gateway156", "lemon"), "refsjlc156"),
    (("gateway156", "a"), "gateway156"),
    (("gateway156", "zz"), "fzsdvzx156"),
    (("gateway156", "AgentU"), "ggxrpuy156"),
    (("gateway156", "keyboard"), "qerfkap156"),
    (("gateway156", "AA"), "gateway156"),
    (("storage156", "key"), "cxmbeeo156"),
    (("storage156", "lemon"), "dxafnri156"),
    (("storage156", "a"), "storage156"),
    (("storage156", "zz"), "rsnqzfd156"),
    (("storage156", "AgentU"), "szsetae156"),
    (("storage156", "keyboard"), "cxmsogv156"),
    (("storage156", "AA"), "storage156"),
    (("network156", "key"), "xirgspu156"),
    (("network156", "lemon"), "yifkbco156"),
    (("network156", "a"), "network156"),
    (("network156", "zz"), "mdsvnqj156"),
    (("network156", "AgentU"), "nkxjhlk156"),
    (("network156", "keyboard"), "xirxcrb156"),
    (("network156", "AA"), "network156"),
    (("latency156", "key"), "verorai156"),
    (("latency156", "lemon"), "wefsanc156"),
    (("latency156", "a"), "latency156"),
    (("latency156", "zz"), "kzsdmbx156"),
    (("latency156", "AgentU"), "lgxrgwy156"),
    (("latency156", "keyboard"), "verfbcp156"),
    (("latency156", "AA"), "latency156"),
    (("buffer156", "key"), "lydpip156"),
    (("buffer156", "lemon"), "myrtrc156"),
    (("buffer156", "a"), "buffer156"),
    (("buffer156", "zz"), "ateedq156"),
    (("buffer156", "AgentU"), "bajsxl156"),
    (("buffer156", "keyboard"), "lydgsr156"),
    (("buffer156", "AA"), "buffer156"),
    (("queue156", "key"), "aycei156"),
    (("queue156", "lemon"), "byqir156"),
    (("queue156", "a"), "queue156"),
    (("queue156", "zz"), "ptdtd156"),
    (("queue156", "AgentU"), "qaihx156"),
    (("queue156", "keyboard"), "aycvs156"),
    (("queue156", "AA"), "queue156"),
    (("worker156", "key"), "gspuip156"),
    (("worker156", "lemon"), "hsdyrc156"),
    (("worker156", "a"), "worker156"),
    (("worker156", "zz"), "vnqjdq156"),
    (("worker156", "AgentU"), "wuvxxl156"),
    (("worker156", "keyboard"), "gsplsr156"),
    (("worker156", "AA"), "worker156"),
    (("kernel156", "key"), "uipxij156"),
    (("kernel156", "lemon"), "vidbrw156"),
    (("kernel156", "a"), "kernel156"),
    (("kernel156", "zz"), "jdqmdk156"),
    (("kernel156", "AgentU"), "kkvaxf156"),
    (("kernel156", "keyboard"), "uiposl156"),
    (("kernel156", "AA"), "kernel156"),
    (("signal156", "key"), "cmexej156"),
    (("signal156", "lemon"), "dmsbnw156"),
    (("signal156", "a"), "signal156"),
    (("signal156", "zz"), "rhfmzk156"),
    (("signal156", "AgentU"), "sokatf156"),
    (("signal156", "keyboard"), "cmeool156"),
    (("signal156", "AA"), "signal156"),
    (("packet156", "key"), "zeauir156"),
    (("packet156", "lemon"), "aeoyre156"),
    (("packet156", "a"), "packet156"),
    (("packet156", "zz"), "ozbjds156"),
    (("packet156", "AgentU"), "pggxxn156"),
    (("packet156", "keyboard"), "zealst156"),
    (("packet156", "AA"), "packet156"),
    (("router156", "key"), "bssdip156"),
    (("router156", "lemon"), "csghrc156"),
    (("router156", "a"), "router156"),
    (("router156", "zz"), "qntsdq156"),
    (("router156", "AgentU"), "ruygxl156"),
    (("router156", "keyboard"), "bssusr156"),
    (("router156", "AA"), "router156"),
    (("cluster156", "key"), "mpscxcb156"),
    (("cluster156", "lemon"), "npgggpv156"),
    (("cluster156", "a"), "cluster156"),
    (("cluster156", "zz"), "bktrsdq156"),
    (("cluster156", "AgentU"), "cryfmyr156"),
    (("cluster156", "keyboard"), "mpsthei156"),
    (("cluster156", "AA"), "cluster156"),
    (("mirror156", "key"), "wmpbsp156"),
    (("mirror156", "lemon"), "xmdfbc156"),
    (("mirror156", "a"), "mirror156"),
    (("mirror156", "zz"), "lhqqnq156"),
    (("mirror156", "AgentU"), "movehl156"),
    (("mirror156", "keyboard"), "wmpscr156"),
    (("mirror156", "AA"), "mirror156"),
    (("filter156", "key"), "pmjdip156"),
    (("filter156", "lemon"), "qmxhrc156"),
    (("filter156", "a"), "filter156"),
    (("filter156", "zz"), "ehksdq156"),
    (("filter156", "AgentU"), "fopgxl156"),
    (("filter156", "keyboard"), "pmjusr156"),
    (("filter156", "AA"), "filter156"),
    (("ranking156", "key"), "belumlq156"),
    (("ranking156", "lemon"), "cezyvyk156"),
    (("ranking156", "a"), "ranking156"),
    (("ranking156", "zz"), "qzmjhmf156"),
    (("ranking156", "AgentU"), "rgrxbhg156"),
    (("ranking156", "keyboard"), "bellwnx156"),
    (("ranking156", "AA"), "ranking156"),
    (("encoding156", "key"), "orayhgxk156"),
    (("encoding156", "lemon"), "procqtrs156"),
    (("encoding156", "a"), "encoding156"),
    (("encoding156", "zz"), "dmbnchmf156"),
    (("encoding156", "AgentU"), "etgbwcnm156"),
    (("encoding156", "keyboard"), "orapriej156"),
    (("encoding156", "AA"), "encoding156"),
    (("mapping156", "key"), "wenzmlq156"),
    (("mapping156", "lemon"), "xebdvyk156"),
    (("mapping156", "a"), "mapping156"),
    (("mapping156", "zz"), "lzoohmf156"),
    (("mapping156", "AgentU"), "mgtcbhg156"),
    (("mapping156", "keyboard"), "wenqwnx156"),
    (("mapping156", "AA"), "mapping156"),
    (("record156", "key"), "biayvb156"),
    (("record156", "lemon"), "cioceo156"),
    (("record156", "a"), "record156"),
    (("record156", "zz"), "qdbnqc156"),
    (("record156", "AgentU"), "rkgbkx156"),
    (("record156", "keyboard"), "biapfd156"),
    (("record156", "AA"), "record156"),
    (("candle156", "key"), "melnpc156"),
    (("candle156", "lemon"), "nezryp156"),
    (("candle156", "a"), "candle156"),
    (("candle156", "zz"), "bzmckd156"),
    (("candle156", "AgentU"), "cgrqey156"),
    (("candle156", "keyboard"), "meleze156"),
    (("candle156", "AA"), "candle156"),
    (("thread156", "key"), "dlpoeb156"),
    (("thread156", "lemon"), "eldsno156"),
    (("thread156", "a"), "thread156"),
    (("thread156", "zz"), "sgqdzc156"),
    (("thread156", "AgentU"), "tnvrtx156"),
    (("thread156", "keyboard"), "dlpfod156"),
    (("thread156", "AA"), "thread156"),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 156: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 156: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "a"),
        "round 156: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 156: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 156: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 156: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", "AA"),
        "round 156: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "key"),
        "bssxh 156: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 156: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "a"),
        "round 156: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 156: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 156: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 156: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", "AA"),
        "round 156: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 156: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 156: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "a"),
        "round 156: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 156: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 156: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 156: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", "AA"),
        "round 156: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 156: the processor reads the record then stops", "key"),
        "bssxh 156: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 156: the processor reads the record then stops", "lemon"),
        "csgbq 156: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 156: the processor reads the record then stops", "a"),
        "round 156: the processor reads the record then stops",
    ),
    (
        ("round 156: the processor reads the record then stops", "zz"),
        "qntmc 156: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 156: the processor reads the record then stops", "AgentU"),
        "ruyaw 156: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 156: the processor reads the record then stops", "keyboard"),
        "bssor 156: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 156: the processor reads the record then stops", "AA"),
        "round 156: the processor reads the record then stops",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "key"),
        "bssxh 156: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "lemon"),
        "csgbq 156: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "a"),
        "round 156: a worker pulls the next task from the queue",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "zz"),
        "qntmc 156: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 156: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "keyboard"),
        "bssor 156: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 156: a worker pulls the next task from the queue", "AA"),
        "round 156: a worker pulls the next task from the queue",
    ),
    (
        ("round 156: signals travel through the network layer", "key"),
        "bssxh 156: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 156: signals travel through the network layer", "lemon"),
        "csgbq 156: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 156: signals travel through the network layer", "a"),
        "round 156: signals travel through the network layer",
    ),
    (
        ("round 156: signals travel through the network layer", "zz"),
        "qntmc 156: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 156: signals travel through the network layer", "AgentU"),
        "ruyaw 156: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 156: signals travel through the network layer", "keyboard"),
        "bssor 156: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 156: signals travel through the network layer", "AA"),
        "round 156: signals travel through the network layer",
    ),
    (
        ("round 156: the gateway routes each request by policy", "key"),
        "bssxh 156: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 156: the gateway routes each request by policy", "lemon"),
        "csgbq 156: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 156: the gateway routes each request by policy", "a"),
        "round 156: the gateway routes each request by policy",
    ),
    (
        ("round 156: the gateway routes each request by policy", "zz"),
        "qntmc 156: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 156: the gateway routes each request by policy", "AgentU"),
        "ruyaw 156: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 156: the gateway routes each request by policy", "keyboard"),
        "bssor 156: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 156: the gateway routes each request by policy", "AA"),
        "round 156: the gateway routes each request by policy",
    ),
    (("round 156: memory grows until the buffer is full", "key"), "bssxh 156: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 156: memory grows until the buffer is full", "lemon"), "csgbq 156: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 156: memory grows until the buffer is full", "a"), "round 156: memory grows until the buffer is full"),
    (("round 156: memory grows until the buffer is full", "zz"), "qntmc 156: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 156: memory grows until the buffer is full", "AgentU"),
        "ruyaw 156: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 156: memory grows until the buffer is full", "keyboard"),
        "bssor 156: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 156: memory grows until the buffer is full", "AA"), "round 156: memory grows until the buffer is full"),
    (("round 156: the cluster mirrors every packet twice", "key"), "bssxh 156: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 156: the cluster mirrors every packet twice", "lemon"),
        "csgbq 156: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 156: the cluster mirrors every packet twice", "a"), "round 156: the cluster mirrors every packet twice"),
    (("round 156: the cluster mirrors every packet twice", "zz"), "qntmc 156: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 156: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 156: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 156: the cluster mirrors every packet twice", "keyboard"),
        "bssor 156: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 156: the cluster mirrors every packet twice", "AA"), "round 156: the cluster mirrors every packet twice"),
    (
        ("round 156: ranking uses tokens learned from the corpus", "key"),
        "bssxh 156: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 156: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", "a"),
        "round 156: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 156: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 156: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 156: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", "AA"),
        "round 156: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 156: a long session ends when the candle dies", "key"),
        "bssxh 156: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 156: a long session ends when the candle dies", "lemon"),
        "csgbq 156: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 156: a long session ends when the candle dies", "a"),
        "round 156: a long session ends when the candle dies",
    ),
    (
        ("round 156: a long session ends when the candle dies", "zz"),
        "qntmc 156: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 156: a long session ends when the candle dies", "AgentU"),
        "ruyaw 156: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 156: a long session ends when the candle dies", "keyboard"),
        "bssor 156: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 156: a long session ends when the candle dies", "AA"),
        "round 156: a long session ends when the candle dies",
    ),
    (("round 156: encode the prompt then map the result", "key"), "bssxh 156: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 156: encode the prompt then map the result", "lemon"), "csgbq 156: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 156: encode the prompt then map the result", "a"), "round 156: encode the prompt then map the result"),
    (("round 156: encode the prompt then map the result", "zz"), "qntmc 156: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 156: encode the prompt then map the result", "AgentU"),
        "ruyaw 156: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 156: encode the prompt then map the result", "keyboard"),
        "bssor 156: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 156: encode the prompt then map the result", "AA"), "round 156: encode the prompt then map the result"),
    (("round 156: the kernel wakes the worker at dawn", "key"), "bssxh 156: rri iovlop ukocc xfo ambocb er neux"),
    (("round 156: the kernel wakes the worker at dawn", "lemon"), "csgbq 156: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 156: the kernel wakes the worker at dawn", "a"), "round 156: the kernel wakes the worker at dawn"),
    (("round 156: the kernel wakes the worker at dawn", "zz"), "qntmc 156: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 156: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 156: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 156: the kernel wakes the worker at dawn", "keyboard"), "bssor 156: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 156: the kernel wakes the worker at dawn", "AA"), "round 156: the kernel wakes the worker at dawn"),
    (("round 156: service latency drops after the patch", "key"), "bssxh 156: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 156: service latency drops after the patch", "lemon"), "csgbq 156: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 156: service latency drops after the patch", "a"), "round 156: service latency drops after the patch"),
    (("round 156: service latency drops after the patch", "zz"), "qntmc 156: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 156: service latency drops after the patch", "AgentU"),
        "ruyaw 156: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 156: service latency drops after the patch", "keyboard"),
        "bssor 156: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 156: service latency drops after the patch", "AA"), "round 156: service latency drops after the patch"),
    (
        ("round 156: the library caches every vector it sees", "key"),
        "bssxh 156: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 156: the library caches every vector it sees", "lemon"),
        "csgbq 156: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 156: the library caches every vector it sees", "a"), "round 156: the library caches every vector it sees"),
    (
        ("round 156: the library caches every vector it sees", "zz"),
        "qntmc 156: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 156: the library caches every vector it sees", "AgentU"),
        "ruyaw 156: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 156: the library caches every vector it sees", "keyboard"),
        "bssor 156: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 156: the library caches every vector it sees", "AA"),
        "round 156: the library caches every vector it sees",
    ),
    (("round 156: agents argue then the debate resolves", "key"), "bssxh 156: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 156: agents argue then the debate resolves", "lemon"), "csgbq 156: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 156: agents argue then the debate resolves", "a"), "round 156: agents argue then the debate resolves"),
    (("round 156: agents argue then the debate resolves", "zz"), "qntmc 156: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 156: agents argue then the debate resolves", "AgentU"),
        "ruyaw 156: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 156: agents argue then the debate resolves", "keyboard"),
        "bssor 156: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 156: agents argue then the debate resolves", "AA"), "round 156: agents argue then the debate resolves"),
    (("round 156: the filter keeps only strong matches", "key"), "bssxh 156: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 156: the filter keeps only strong matches", "lemon"), "csgbq 156: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 156: the filter keeps only strong matches", "a"), "round 156: the filter keeps only strong matches"),
    (("round 156: the filter keeps only strong matches", "zz"), "qntmc 156: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 156: the filter keeps only strong matches", "AgentU"), "ruyaw 156: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 156: the filter keeps only strong matches", "keyboard"),
        "bssor 156: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 156: the filter keeps only strong matches", "AA"), "round 156: the filter keeps only strong matches"),
    (("round 156: the model answers with a short reply", "key"), "bssxh 156: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 156: the model answers with a short reply", "lemon"), "csgbq 156: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 156: the model answers with a short reply", "a"), "round 156: the model answers with a short reply"),
    (("round 156: the model answers with a short reply", "zz"), "qntmc 156: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 156: the model answers with a short reply", "AgentU"), "ruyaw 156: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 156: the model answers with a short reply", "keyboard"),
        "bssor 156: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 156: the model answers with a short reply", "AA"), "round 156: the model answers with a short reply"),
    (
        ("round 156: the recorder stores the reasoning trace", "key"),
        "bssxh 156: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 156: the recorder stores the reasoning trace", "lemon"),
        "csgbq 156: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 156: the recorder stores the reasoning trace", "a"), "round 156: the recorder stores the reasoning trace"),
    (
        ("round 156: the recorder stores the reasoning trace", "zz"),
        "qntmc 156: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 156: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 156: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 156: the recorder stores the reasoning trace", "keyboard"),
        "bssor 156: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 156: the recorder stores the reasoning trace", "AA"),
        "round 156: the recorder stores the reasoning trace",
    ),
    (("round 156: the angel watches the processor run", "key"), "bssxh 156: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 156: the angel watches the processor run", "lemon"), "csgbq 156: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 156: the angel watches the processor run", "a"), "round 156: the angel watches the processor run"),
    (("round 156: the angel watches the processor run", "zz"), "qntmc 156: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 156: the angel watches the processor run", "AgentU"), "ruyaw 156: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 156: the angel watches the processor run", "keyboard"), "bssor 156: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 156: the angel watches the processor run", "AA"), "round 156: the angel watches the processor run"),
    (("round 156: angle of the vector decides the match", "key"), "bssxh 156: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 156: angle of the vector decides the match", "lemon"), "csgbq 156: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 156: angle of the vector decides the match", "a"), "round 156: angle of the vector decides the match"),
    (("round 156: angle of the vector decides the match", "zz"), "qntmc 156: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 156: angle of the vector decides the match", "AgentU"),
        "ruyaw 156: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 156: angle of the vector decides the match", "keyboard"),
        "bssor 156: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 156: angle of the vector decides the match", "AA"), "round 156: angle of the vector decides the match"),
    (
        ("round 156: the candle burns twice as long at night", "key"),
        "bssxh 156: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 156: the candle burns twice as long at night", "lemon"),
        "csgbq 156: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 156: the candle burns twice as long at night", "a"), "round 156: the candle burns twice as long at night"),
    (
        ("round 156: the candle burns twice as long at night", "zz"),
        "qntmc 156: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 156: the candle burns twice as long at night", "AgentU"),
        "ruyaw 156: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 156: the candle burns twice as long at night", "keyboard"),
        "bssor 156: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 156: the candle burns twice as long at night", "AA"),
        "round 156: the candle burns twice as long at night",
    ),
    (("round 156: a mirror of the universe in one line", "key"), "bssxh 156: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 156: a mirror of the universe in one line", "lemon"), "csgbq 156: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 156: a mirror of the universe in one line", "a"), "round 156: a mirror of the universe in one line"),
    (("round 156: a mirror of the universe in one line", "zz"), "qntmc 156: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 156: a mirror of the universe in one line", "AgentU"), "ruyaw 156: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 156: a mirror of the universe in one line", "keyboard"),
        "bssor 156: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 156: a mirror of the universe in one line", "AA"), "round 156: a mirror of the universe in one line"),
    (("round 156: the queue drains before the storm", "key"), "bssxh 156: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 156: the queue drains before the storm", "lemon"), "csgbq 156: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 156: the queue drains before the storm", "a"), "round 156: the queue drains before the storm"),
    (("round 156: the queue drains before the storm", "zz"), "qntmc 156: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 156: the queue drains before the storm", "AgentU"), "ruyaw 156: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 156: the queue drains before the storm", "keyboard"), "bssor 156: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 156: the queue drains before the storm", "AA"), "round 156: the queue drains before the storm"),
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
