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
    (("kitten203", "key"), "umrdil203"),
    (("kitten203", "lemon"), "vmfhry203"),
    (("kitten203", "a"), "kitten203"),
    (("kitten203", "zz"), "jhssdm203"),
    (("kitten203", "AgentU"), "koxgxh203"),
    (("kitten203", "keyboard"), "umrusn203"),
    (("kitten203", "AA"), "kitten203"),
    (("sitting203", "key"), "cmrdmlq203"),
    (("sitting203", "lemon"), "dmfhvyk203"),
    (("sitting203", "a"), "sitting203"),
    (("sitting203", "zz"), "rhsshmf203"),
    (("sitting203", "AgentU"), "soxgbhg203"),
    (("sitting203", "keyboard"), "cmruwnx203"),
    (("sitting203", "AA"), "sitting203"),
    (("agent203", "key"), "kkcxx203"),
    (("agent203", "lemon"), "lkqbg203"),
    (("agent203", "a"), "agent203"),
    (("agent203", "zz"), "zfdms203"),
    (("agent203", "AgentU"), "amiam203"),
    (("agent203", "keyboard"), "kkcoh203"),
    (("agent203", "AA"), "agent203"),
    (("angle203", "key"), "krevi203"),
    (("angle203", "lemon"), "lrszr203"),
    (("angle203", "a"), "angle203"),
    (("angle203", "zz"), "zmfkd203"),
    (("angle203", "AgentU"), "atkyx203"),
    (("angle203", "keyboard"), "krems203"),
    (("angle203", "AA"), "angle203"),
    (("universe203", "key"), "ergfipci203"),
    (("universe203", "lemon"), "frujrcwq203"),
    (("universe203", "a"), "universe203"),
    (("universe203", "zz"), "tmhudqrd203"),
    (("universe203", "AgentU"), "utmixlsk203"),
    (("universe203", "keyboard"), "ergwsrjh203"),
    (("universe203", "AA"), "universe203"),
    (("memory203", "key"), "wikyvw203"),
    (("memory203", "lemon"), "xiycej203"),
    (("memory203", "a"), "memory203"),
    (("memory203", "zz"), "ldlnqx203"),
    (("memory203", "AgentU"), "mkqbks203"),
    (("memory203", "keyboard"), "wikpfy203"),
    (("memory203", "AA"), "memory203"),
    (("stream203", "key"), "cxpoek203"),
    (("stream203", "lemon"), "dxdsnx203"),
    (("stream203", "a"), "stream203"),
    (("stream203", "zz"), "rsqdzl203"),
    (("stream203", "AgentU"), "szvrtg203"),
    (("stream203", "keyboard"), "cxpfom203"),
    (("stream203", "AA"), "stream203"),
    (("context203", "key"), "msldivd203"),
    (("context203", "lemon"), "nszhrix203"),
    (("context203", "a"), "context203"),
    (("context203", "zz"), "bnmsdws203"),
    (("context203", "AgentU"), "curgxrt203"),
    (("context203", "keyboard"), "mslusxk203"),
    (("context203", "AA"), "context203"),
    (("knowledge203", "key"), "urmgpcnkc203"),
    (("knowledge203", "lemon"), "vrakyphss203"),
    (("knowledge203", "a"), "knowledge203"),
    (("knowledge203", "zz"), "jmnvkdcfd203"),
    (("knowledge203", "AgentU"), "ktsjeydmi203"),
    (("knowledge203", "keyboard"), "urmxzeujo203"),
    (("knowledge203", "AA"), "knowledge203"),
    (("vector203", "key"), "fiadsp203"),
    (("vector203", "lemon"), "giohbc203"),
    (("vector203", "a"), "vector203"),
    (("vector203", "zz"), "udbsnq203"),
    (("vector203", "AgentU"), "vkgghl203"),
    (("vector203", "keyboard"), "fiaucr203"),
    (("vector203", "AA"), "vector203"),
    (("processor203", "key"), "zvmmiqcsp203"),
    (("processor203", "lemon"), "avaqrdwaf203"),
    (("processor203", "a"), "processor203"),
    (("processor203", "zz"), "oqnbdrrnq203"),
    (("processor203", "AgentU"), "pxspxmsuv203"),
    (("processor203", "keyboard"), "zvmdssjrb203"),
    (("processor203", "AA"), "processor203"),
    (("reasoning203", "key"), "biycslsre203"),
    (("reasoning203", "lemon"), "cimgbymzu203"),
    (("reasoning203", "a"), "reasoning203"),
    (("reasoning203", "zz"), "qdzrnmhmf203"),
    (("reasoning203", "AgentU"), "rkefhhitk203"),
    (("reasoning203", "keyboard"), "biytcnzqq203"),
    (("reasoning203", "AA"), "reasoning203"),
    (("machine203", "key"), "wearmlo203"),
    (("machine203", "lemon"), "xeovvyi203"),
    (("machine203", "a"), "machine203"),
    (("machine203", "zz"), "lzbghmd203"),
    (("machine203", "AgentU"), "mggubhe203"),
    (("machine203", "keyboard"), "weaiwnv203"),
    (("machine203", "AA"), "machine203"),
    (("learning203", "key"), "viybrgxk203"),
    (("learning203", "lemon"), "wimfatrs203"),
    (("learning203", "a"), "learning203"),
    (("learning203", "zz"), "kdzqmhmf203"),
    (("learning203", "AgentU"), "lkeegcnm203"),
    (("learning203", "keyboard"), "viysbiej203"),
    (("learning203", "AA"), "learning203"),
    (("model203", "key"), "wsbop203"),
    (("model203", "lemon"), "xspsy203"),
    (("model203", "a"), "model203"),
    (("model203", "zz"), "lncdk203"),
    (("model203", "AgentU"), "muhre203"),
    (("model203", "keyboard"), "wsbfz203"),
    (("model203", "AA"), "model203"),
    (("token203", "key"), "dsior203"),
    (("token203", "lemon"), "eswsa203"),
    (("token203", "a"), "token203"),
    (("token203", "zz"), "snjdm203"),
    (("token203", "AgentU"), "tuorg203"),
    (("token203", "keyboard"), "dsifb203"),
    (("token203", "AA"), "token203"),
    (("prompt203", "key"), "zvmwtr203"),
    (("prompt203", "lemon"), "avaace203"),
    (("prompt203", "a"), "prompt203"),
    (("prompt203", "zz"), "oqnlos203"),
    (("prompt203", "AgentU"), "pxszin203"),
    (("prompt203", "keyboard"), "zvmndt203"),
    (("prompt203", "AA"), "prompt203"),
    (("session203", "key"), "ciqcmmx203"),
    (("session203", "lemon"), "diegvzr203"),
    (("session203", "a"), "session203"),
    (("session203", "zz"), "rdrrhnm203"),
    (("session203", "AgentU"), "skwfbin203"),
    (("session203", "keyboard"), "ciqtwoe203"),
    (("session203", "AA"), "session203"),
    (("library203", "key"), "vmzbepi203"),
    (("library203", "lemon"), "wmnfncc203"),
    (("library203", "a"), "library203"),
    (("library203", "zz"), "khaqzqx203"),
    (("library203", "AgentU"), "lofetly203"),
    (("library203", "keyboard"), "vmzsorp203"),
    (("library203", "AA"), "library203"),
    (("service203", "key"), "cipfmao203"),
    (("service203", "lemon"), "didjvni203"),
    (("service203", "a"), "service203"),
    (("service203", "zz"), "rdquhbd203"),
    (("service203", "AgentU"), "skvibwe203"),
    (("service203", "keyboard"), "cipwwcv203"),
    (("service203", "AA"), "service203"),
    (("gateway203", "key"), "qeroayi203"),
    (("gateway203", "lemon"), "refsjlc203"),
    (("gateway203", "a"), "gateway203"),
    (("gateway203", "zz"), "fzsdvzx203"),
    (("gateway203", "AgentU"), "ggxrpuy203"),
    (("gateway203", "keyboard"), "qerfkap203"),
    (("gateway203", "AA"), "gateway203"),
    (("storage203", "key"), "cxmbeeo203"),
    (("storage203", "lemon"), "dxafnri203"),
    (("storage203", "a"), "storage203"),
    (("storage203", "zz"), "rsnqzfd203"),
    (("storage203", "AgentU"), "szsetae203"),
    (("storage203", "keyboard"), "cxmsogv203"),
    (("storage203", "AA"), "storage203"),
    (("network203", "key"), "xirgspu203"),
    (("network203", "lemon"), "yifkbco203"),
    (("network203", "a"), "network203"),
    (("network203", "zz"), "mdsvnqj203"),
    (("network203", "AgentU"), "nkxjhlk203"),
    (("network203", "keyboard"), "xirxcrb203"),
    (("network203", "AA"), "network203"),
    (("latency203", "key"), "verorai203"),
    (("latency203", "lemon"), "wefsanc203"),
    (("latency203", "a"), "latency203"),
    (("latency203", "zz"), "kzsdmbx203"),
    (("latency203", "AgentU"), "lgxrgwy203"),
    (("latency203", "keyboard"), "verfbcp203"),
    (("latency203", "AA"), "latency203"),
    (("buffer203", "key"), "lydpip203"),
    (("buffer203", "lemon"), "myrtrc203"),
    (("buffer203", "a"), "buffer203"),
    (("buffer203", "zz"), "ateedq203"),
    (("buffer203", "AgentU"), "bajsxl203"),
    (("buffer203", "keyboard"), "lydgsr203"),
    (("buffer203", "AA"), "buffer203"),
    (("queue203", "key"), "aycei203"),
    (("queue203", "lemon"), "byqir203"),
    (("queue203", "a"), "queue203"),
    (("queue203", "zz"), "ptdtd203"),
    (("queue203", "AgentU"), "qaihx203"),
    (("queue203", "keyboard"), "aycvs203"),
    (("queue203", "AA"), "queue203"),
    (("worker203", "key"), "gspuip203"),
    (("worker203", "lemon"), "hsdyrc203"),
    (("worker203", "a"), "worker203"),
    (("worker203", "zz"), "vnqjdq203"),
    (("worker203", "AgentU"), "wuvxxl203"),
    (("worker203", "keyboard"), "gsplsr203"),
    (("worker203", "AA"), "worker203"),
    (("kernel203", "key"), "uipxij203"),
    (("kernel203", "lemon"), "vidbrw203"),
    (("kernel203", "a"), "kernel203"),
    (("kernel203", "zz"), "jdqmdk203"),
    (("kernel203", "AgentU"), "kkvaxf203"),
    (("kernel203", "keyboard"), "uiposl203"),
    (("kernel203", "AA"), "kernel203"),
    (("signal203", "key"), "cmexej203"),
    (("signal203", "lemon"), "dmsbnw203"),
    (("signal203", "a"), "signal203"),
    (("signal203", "zz"), "rhfmzk203"),
    (("signal203", "AgentU"), "sokatf203"),
    (("signal203", "keyboard"), "cmeool203"),
    (("signal203", "AA"), "signal203"),
    (("packet203", "key"), "zeauir203"),
    (("packet203", "lemon"), "aeoyre203"),
    (("packet203", "a"), "packet203"),
    (("packet203", "zz"), "ozbjds203"),
    (("packet203", "AgentU"), "pggxxn203"),
    (("packet203", "keyboard"), "zealst203"),
    (("packet203", "AA"), "packet203"),
    (("router203", "key"), "bssdip203"),
    (("router203", "lemon"), "csghrc203"),
    (("router203", "a"), "router203"),
    (("router203", "zz"), "qntsdq203"),
    (("router203", "AgentU"), "ruygxl203"),
    (("router203", "keyboard"), "bssusr203"),
    (("router203", "AA"), "router203"),
    (("cluster203", "key"), "mpscxcb203"),
    (("cluster203", "lemon"), "npgggpv203"),
    (("cluster203", "a"), "cluster203"),
    (("cluster203", "zz"), "bktrsdq203"),
    (("cluster203", "AgentU"), "cryfmyr203"),
    (("cluster203", "keyboard"), "mpsthei203"),
    (("cluster203", "AA"), "cluster203"),
    (("mirror203", "key"), "wmpbsp203"),
    (("mirror203", "lemon"), "xmdfbc203"),
    (("mirror203", "a"), "mirror203"),
    (("mirror203", "zz"), "lhqqnq203"),
    (("mirror203", "AgentU"), "movehl203"),
    (("mirror203", "keyboard"), "wmpscr203"),
    (("mirror203", "AA"), "mirror203"),
    (("filter203", "key"), "pmjdip203"),
    (("filter203", "lemon"), "qmxhrc203"),
    (("filter203", "a"), "filter203"),
    (("filter203", "zz"), "ehksdq203"),
    (("filter203", "AgentU"), "fopgxl203"),
    (("filter203", "keyboard"), "pmjusr203"),
    (("filter203", "AA"), "filter203"),
    (("ranking203", "key"), "belumlq203"),
    (("ranking203", "lemon"), "cezyvyk203"),
    (("ranking203", "a"), "ranking203"),
    (("ranking203", "zz"), "qzmjhmf203"),
    (("ranking203", "AgentU"), "rgrxbhg203"),
    (("ranking203", "keyboard"), "bellwnx203"),
    (("ranking203", "AA"), "ranking203"),
    (("encoding203", "key"), "orayhgxk203"),
    (("encoding203", "lemon"), "procqtrs203"),
    (("encoding203", "a"), "encoding203"),
    (("encoding203", "zz"), "dmbnchmf203"),
    (("encoding203", "AgentU"), "etgbwcnm203"),
    (("encoding203", "keyboard"), "orapriej203"),
    (("encoding203", "AA"), "encoding203"),
    (("mapping203", "key"), "wenzmlq203"),
    (("mapping203", "lemon"), "xebdvyk203"),
    (("mapping203", "a"), "mapping203"),
    (("mapping203", "zz"), "lzoohmf203"),
    (("mapping203", "AgentU"), "mgtcbhg203"),
    (("mapping203", "keyboard"), "wenqwnx203"),
    (("mapping203", "AA"), "mapping203"),
    (("record203", "key"), "biayvb203"),
    (("record203", "lemon"), "cioceo203"),
    (("record203", "a"), "record203"),
    (("record203", "zz"), "qdbnqc203"),
    (("record203", "AgentU"), "rkgbkx203"),
    (("record203", "keyboard"), "biapfd203"),
    (("record203", "AA"), "record203"),
    (("candle203", "key"), "melnpc203"),
    (("candle203", "lemon"), "nezryp203"),
    (("candle203", "a"), "candle203"),
    (("candle203", "zz"), "bzmckd203"),
    (("candle203", "AgentU"), "cgrqey203"),
    (("candle203", "keyboard"), "meleze203"),
    (("candle203", "AA"), "candle203"),
    (("thread203", "key"), "dlpoeb203"),
    (("thread203", "lemon"), "eldsno203"),
    (("thread203", "a"), "thread203"),
    (("thread203", "zz"), "sgqdzc203"),
    (("thread203", "AgentU"), "tnvrtx203"),
    (("thread203", "keyboard"), "dlpfod203"),
    (("thread203", "AA"), "thread203"),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 203: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 203: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "a"),
        "round 203: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 203: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 203: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 203: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", "AA"),
        "round 203: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "key"),
        "bssxh 203: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 203: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "a"),
        "round 203: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 203: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 203: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 203: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", "AA"),
        "round 203: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 203: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 203: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "a"),
        "round 203: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 203: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 203: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 203: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", "AA"),
        "round 203: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 203: the processor reads the record then stops", "key"),
        "bssxh 203: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 203: the processor reads the record then stops", "lemon"),
        "csgbq 203: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 203: the processor reads the record then stops", "a"),
        "round 203: the processor reads the record then stops",
    ),
    (
        ("round 203: the processor reads the record then stops", "zz"),
        "qntmc 203: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 203: the processor reads the record then stops", "AgentU"),
        "ruyaw 203: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 203: the processor reads the record then stops", "keyboard"),
        "bssor 203: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 203: the processor reads the record then stops", "AA"),
        "round 203: the processor reads the record then stops",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "key"),
        "bssxh 203: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "lemon"),
        "csgbq 203: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "a"),
        "round 203: a worker pulls the next task from the queue",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "zz"),
        "qntmc 203: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 203: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "keyboard"),
        "bssor 203: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 203: a worker pulls the next task from the queue", "AA"),
        "round 203: a worker pulls the next task from the queue",
    ),
    (
        ("round 203: signals travel through the network layer", "key"),
        "bssxh 203: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 203: signals travel through the network layer", "lemon"),
        "csgbq 203: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 203: signals travel through the network layer", "a"),
        "round 203: signals travel through the network layer",
    ),
    (
        ("round 203: signals travel through the network layer", "zz"),
        "qntmc 203: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 203: signals travel through the network layer", "AgentU"),
        "ruyaw 203: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 203: signals travel through the network layer", "keyboard"),
        "bssor 203: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 203: signals travel through the network layer", "AA"),
        "round 203: signals travel through the network layer",
    ),
    (
        ("round 203: the gateway routes each request by policy", "key"),
        "bssxh 203: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 203: the gateway routes each request by policy", "lemon"),
        "csgbq 203: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 203: the gateway routes each request by policy", "a"),
        "round 203: the gateway routes each request by policy",
    ),
    (
        ("round 203: the gateway routes each request by policy", "zz"),
        "qntmc 203: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 203: the gateway routes each request by policy", "AgentU"),
        "ruyaw 203: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 203: the gateway routes each request by policy", "keyboard"),
        "bssor 203: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 203: the gateway routes each request by policy", "AA"),
        "round 203: the gateway routes each request by policy",
    ),
    (("round 203: memory grows until the buffer is full", "key"), "bssxh 203: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 203: memory grows until the buffer is full", "lemon"), "csgbq 203: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 203: memory grows until the buffer is full", "a"), "round 203: memory grows until the buffer is full"),
    (("round 203: memory grows until the buffer is full", "zz"), "qntmc 203: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 203: memory grows until the buffer is full", "AgentU"),
        "ruyaw 203: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 203: memory grows until the buffer is full", "keyboard"),
        "bssor 203: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 203: memory grows until the buffer is full", "AA"), "round 203: memory grows until the buffer is full"),
    (("round 203: the cluster mirrors every packet twice", "key"), "bssxh 203: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 203: the cluster mirrors every packet twice", "lemon"),
        "csgbq 203: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 203: the cluster mirrors every packet twice", "a"), "round 203: the cluster mirrors every packet twice"),
    (("round 203: the cluster mirrors every packet twice", "zz"), "qntmc 203: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 203: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 203: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 203: the cluster mirrors every packet twice", "keyboard"),
        "bssor 203: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 203: the cluster mirrors every packet twice", "AA"), "round 203: the cluster mirrors every packet twice"),
    (
        ("round 203: ranking uses tokens learned from the corpus", "key"),
        "bssxh 203: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 203: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", "a"),
        "round 203: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 203: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 203: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 203: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", "AA"),
        "round 203: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 203: a long session ends when the candle dies", "key"),
        "bssxh 203: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 203: a long session ends when the candle dies", "lemon"),
        "csgbq 203: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 203: a long session ends when the candle dies", "a"),
        "round 203: a long session ends when the candle dies",
    ),
    (
        ("round 203: a long session ends when the candle dies", "zz"),
        "qntmc 203: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 203: a long session ends when the candle dies", "AgentU"),
        "ruyaw 203: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 203: a long session ends when the candle dies", "keyboard"),
        "bssor 203: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 203: a long session ends when the candle dies", "AA"),
        "round 203: a long session ends when the candle dies",
    ),
    (("round 203: encode the prompt then map the result", "key"), "bssxh 203: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 203: encode the prompt then map the result", "lemon"), "csgbq 203: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 203: encode the prompt then map the result", "a"), "round 203: encode the prompt then map the result"),
    (("round 203: encode the prompt then map the result", "zz"), "qntmc 203: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 203: encode the prompt then map the result", "AgentU"),
        "ruyaw 203: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 203: encode the prompt then map the result", "keyboard"),
        "bssor 203: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 203: encode the prompt then map the result", "AA"), "round 203: encode the prompt then map the result"),
    (("round 203: the kernel wakes the worker at dawn", "key"), "bssxh 203: rri iovlop ukocc xfo ambocb er neux"),
    (("round 203: the kernel wakes the worker at dawn", "lemon"), "csgbq 203: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 203: the kernel wakes the worker at dawn", "a"), "round 203: the kernel wakes the worker at dawn"),
    (("round 203: the kernel wakes the worker at dawn", "zz"), "qntmc 203: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 203: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 203: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 203: the kernel wakes the worker at dawn", "keyboard"), "bssor 203: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 203: the kernel wakes the worker at dawn", "AA"), "round 203: the kernel wakes the worker at dawn"),
    (("round 203: service latency drops after the patch", "key"), "bssxh 203: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 203: service latency drops after the patch", "lemon"), "csgbq 203: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 203: service latency drops after the patch", "a"), "round 203: service latency drops after the patch"),
    (("round 203: service latency drops after the patch", "zz"), "qntmc 203: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 203: service latency drops after the patch", "AgentU"),
        "ruyaw 203: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 203: service latency drops after the patch", "keyboard"),
        "bssor 203: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 203: service latency drops after the patch", "AA"), "round 203: service latency drops after the patch"),
    (
        ("round 203: the library caches every vector it sees", "key"),
        "bssxh 203: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 203: the library caches every vector it sees", "lemon"),
        "csgbq 203: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 203: the library caches every vector it sees", "a"), "round 203: the library caches every vector it sees"),
    (
        ("round 203: the library caches every vector it sees", "zz"),
        "qntmc 203: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 203: the library caches every vector it sees", "AgentU"),
        "ruyaw 203: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 203: the library caches every vector it sees", "keyboard"),
        "bssor 203: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 203: the library caches every vector it sees", "AA"),
        "round 203: the library caches every vector it sees",
    ),
    (("round 203: agents argue then the debate resolves", "key"), "bssxh 203: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 203: agents argue then the debate resolves", "lemon"), "csgbq 203: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 203: agents argue then the debate resolves", "a"), "round 203: agents argue then the debate resolves"),
    (("round 203: agents argue then the debate resolves", "zz"), "qntmc 203: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 203: agents argue then the debate resolves", "AgentU"),
        "ruyaw 203: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 203: agents argue then the debate resolves", "keyboard"),
        "bssor 203: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 203: agents argue then the debate resolves", "AA"), "round 203: agents argue then the debate resolves"),
    (("round 203: the filter keeps only strong matches", "key"), "bssxh 203: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 203: the filter keeps only strong matches", "lemon"), "csgbq 203: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 203: the filter keeps only strong matches", "a"), "round 203: the filter keeps only strong matches"),
    (("round 203: the filter keeps only strong matches", "zz"), "qntmc 203: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 203: the filter keeps only strong matches", "AgentU"), "ruyaw 203: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 203: the filter keeps only strong matches", "keyboard"),
        "bssor 203: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 203: the filter keeps only strong matches", "AA"), "round 203: the filter keeps only strong matches"),
    (("round 203: the model answers with a short reply", "key"), "bssxh 203: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 203: the model answers with a short reply", "lemon"), "csgbq 203: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 203: the model answers with a short reply", "a"), "round 203: the model answers with a short reply"),
    (("round 203: the model answers with a short reply", "zz"), "qntmc 203: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 203: the model answers with a short reply", "AgentU"), "ruyaw 203: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 203: the model answers with a short reply", "keyboard"),
        "bssor 203: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 203: the model answers with a short reply", "AA"), "round 203: the model answers with a short reply"),
    (
        ("round 203: the recorder stores the reasoning trace", "key"),
        "bssxh 203: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 203: the recorder stores the reasoning trace", "lemon"),
        "csgbq 203: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 203: the recorder stores the reasoning trace", "a"), "round 203: the recorder stores the reasoning trace"),
    (
        ("round 203: the recorder stores the reasoning trace", "zz"),
        "qntmc 203: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 203: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 203: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 203: the recorder stores the reasoning trace", "keyboard"),
        "bssor 203: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 203: the recorder stores the reasoning trace", "AA"),
        "round 203: the recorder stores the reasoning trace",
    ),
    (("round 203: the angel watches the processor run", "key"), "bssxh 203: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 203: the angel watches the processor run", "lemon"), "csgbq 203: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 203: the angel watches the processor run", "a"), "round 203: the angel watches the processor run"),
    (("round 203: the angel watches the processor run", "zz"), "qntmc 203: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 203: the angel watches the processor run", "AgentU"), "ruyaw 203: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 203: the angel watches the processor run", "keyboard"), "bssor 203: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 203: the angel watches the processor run", "AA"), "round 203: the angel watches the processor run"),
    (("round 203: angle of the vector decides the match", "key"), "bssxh 203: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 203: angle of the vector decides the match", "lemon"), "csgbq 203: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 203: angle of the vector decides the match", "a"), "round 203: angle of the vector decides the match"),
    (("round 203: angle of the vector decides the match", "zz"), "qntmc 203: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 203: angle of the vector decides the match", "AgentU"),
        "ruyaw 203: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 203: angle of the vector decides the match", "keyboard"),
        "bssor 203: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 203: angle of the vector decides the match", "AA"), "round 203: angle of the vector decides the match"),
    (
        ("round 203: the candle burns twice as long at night", "key"),
        "bssxh 203: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 203: the candle burns twice as long at night", "lemon"),
        "csgbq 203: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 203: the candle burns twice as long at night", "a"), "round 203: the candle burns twice as long at night"),
    (
        ("round 203: the candle burns twice as long at night", "zz"),
        "qntmc 203: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 203: the candle burns twice as long at night", "AgentU"),
        "ruyaw 203: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 203: the candle burns twice as long at night", "keyboard"),
        "bssor 203: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 203: the candle burns twice as long at night", "AA"),
        "round 203: the candle burns twice as long at night",
    ),
    (("round 203: a mirror of the universe in one line", "key"), "bssxh 203: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 203: a mirror of the universe in one line", "lemon"), "csgbq 203: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 203: a mirror of the universe in one line", "a"), "round 203: a mirror of the universe in one line"),
    (("round 203: a mirror of the universe in one line", "zz"), "qntmc 203: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 203: a mirror of the universe in one line", "AgentU"), "ruyaw 203: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 203: a mirror of the universe in one line", "keyboard"),
        "bssor 203: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 203: a mirror of the universe in one line", "AA"), "round 203: a mirror of the universe in one line"),
    (("round 203: the queue drains before the storm", "key"), "bssxh 203: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 203: the queue drains before the storm", "lemon"), "csgbq 203: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 203: the queue drains before the storm", "a"), "round 203: the queue drains before the storm"),
    (("round 203: the queue drains before the storm", "zz"), "qntmc 203: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 203: the queue drains before the storm", "AgentU"), "ruyaw 203: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 203: the queue drains before the storm", "keyboard"), "bssor 203: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 203: the queue drains before the storm", "AA"), "round 203: the queue drains before the storm"),
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
