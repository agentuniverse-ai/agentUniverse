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
    (("kitten200", "key"), "umrdil200"),
    (("kitten200", "lemon"), "vmfhry200"),
    (("kitten200", "a"), "kitten200"),
    (("kitten200", "zz"), "jhssdm200"),
    (("kitten200", "AgentU"), "koxgxh200"),
    (("kitten200", "keyboard"), "umrusn200"),
    (("kitten200", "AA"), "kitten200"),
    (("sitting200", "key"), "cmrdmlq200"),
    (("sitting200", "lemon"), "dmfhvyk200"),
    (("sitting200", "a"), "sitting200"),
    (("sitting200", "zz"), "rhsshmf200"),
    (("sitting200", "AgentU"), "soxgbhg200"),
    (("sitting200", "keyboard"), "cmruwnx200"),
    (("sitting200", "AA"), "sitting200"),
    (("agent200", "key"), "kkcxx200"),
    (("agent200", "lemon"), "lkqbg200"),
    (("agent200", "a"), "agent200"),
    (("agent200", "zz"), "zfdms200"),
    (("agent200", "AgentU"), "amiam200"),
    (("agent200", "keyboard"), "kkcoh200"),
    (("agent200", "AA"), "agent200"),
    (("angle200", "key"), "krevi200"),
    (("angle200", "lemon"), "lrszr200"),
    (("angle200", "a"), "angle200"),
    (("angle200", "zz"), "zmfkd200"),
    (("angle200", "AgentU"), "atkyx200"),
    (("angle200", "keyboard"), "krems200"),
    (("angle200", "AA"), "angle200"),
    (("universe200", "key"), "ergfipci200"),
    (("universe200", "lemon"), "frujrcwq200"),
    (("universe200", "a"), "universe200"),
    (("universe200", "zz"), "tmhudqrd200"),
    (("universe200", "AgentU"), "utmixlsk200"),
    (("universe200", "keyboard"), "ergwsrjh200"),
    (("universe200", "AA"), "universe200"),
    (("memory200", "key"), "wikyvw200"),
    (("memory200", "lemon"), "xiycej200"),
    (("memory200", "a"), "memory200"),
    (("memory200", "zz"), "ldlnqx200"),
    (("memory200", "AgentU"), "mkqbks200"),
    (("memory200", "keyboard"), "wikpfy200"),
    (("memory200", "AA"), "memory200"),
    (("stream200", "key"), "cxpoek200"),
    (("stream200", "lemon"), "dxdsnx200"),
    (("stream200", "a"), "stream200"),
    (("stream200", "zz"), "rsqdzl200"),
    (("stream200", "AgentU"), "szvrtg200"),
    (("stream200", "keyboard"), "cxpfom200"),
    (("stream200", "AA"), "stream200"),
    (("context200", "key"), "msldivd200"),
    (("context200", "lemon"), "nszhrix200"),
    (("context200", "a"), "context200"),
    (("context200", "zz"), "bnmsdws200"),
    (("context200", "AgentU"), "curgxrt200"),
    (("context200", "keyboard"), "mslusxk200"),
    (("context200", "AA"), "context200"),
    (("knowledge200", "key"), "urmgpcnkc200"),
    (("knowledge200", "lemon"), "vrakyphss200"),
    (("knowledge200", "a"), "knowledge200"),
    (("knowledge200", "zz"), "jmnvkdcfd200"),
    (("knowledge200", "AgentU"), "ktsjeydmi200"),
    (("knowledge200", "keyboard"), "urmxzeujo200"),
    (("knowledge200", "AA"), "knowledge200"),
    (("vector200", "key"), "fiadsp200"),
    (("vector200", "lemon"), "giohbc200"),
    (("vector200", "a"), "vector200"),
    (("vector200", "zz"), "udbsnq200"),
    (("vector200", "AgentU"), "vkgghl200"),
    (("vector200", "keyboard"), "fiaucr200"),
    (("vector200", "AA"), "vector200"),
    (("processor200", "key"), "zvmmiqcsp200"),
    (("processor200", "lemon"), "avaqrdwaf200"),
    (("processor200", "a"), "processor200"),
    (("processor200", "zz"), "oqnbdrrnq200"),
    (("processor200", "AgentU"), "pxspxmsuv200"),
    (("processor200", "keyboard"), "zvmdssjrb200"),
    (("processor200", "AA"), "processor200"),
    (("reasoning200", "key"), "biycslsre200"),
    (("reasoning200", "lemon"), "cimgbymzu200"),
    (("reasoning200", "a"), "reasoning200"),
    (("reasoning200", "zz"), "qdzrnmhmf200"),
    (("reasoning200", "AgentU"), "rkefhhitk200"),
    (("reasoning200", "keyboard"), "biytcnzqq200"),
    (("reasoning200", "AA"), "reasoning200"),
    (("machine200", "key"), "wearmlo200"),
    (("machine200", "lemon"), "xeovvyi200"),
    (("machine200", "a"), "machine200"),
    (("machine200", "zz"), "lzbghmd200"),
    (("machine200", "AgentU"), "mggubhe200"),
    (("machine200", "keyboard"), "weaiwnv200"),
    (("machine200", "AA"), "machine200"),
    (("learning200", "key"), "viybrgxk200"),
    (("learning200", "lemon"), "wimfatrs200"),
    (("learning200", "a"), "learning200"),
    (("learning200", "zz"), "kdzqmhmf200"),
    (("learning200", "AgentU"), "lkeegcnm200"),
    (("learning200", "keyboard"), "viysbiej200"),
    (("learning200", "AA"), "learning200"),
    (("model200", "key"), "wsbop200"),
    (("model200", "lemon"), "xspsy200"),
    (("model200", "a"), "model200"),
    (("model200", "zz"), "lncdk200"),
    (("model200", "AgentU"), "muhre200"),
    (("model200", "keyboard"), "wsbfz200"),
    (("model200", "AA"), "model200"),
    (("token200", "key"), "dsior200"),
    (("token200", "lemon"), "eswsa200"),
    (("token200", "a"), "token200"),
    (("token200", "zz"), "snjdm200"),
    (("token200", "AgentU"), "tuorg200"),
    (("token200", "keyboard"), "dsifb200"),
    (("token200", "AA"), "token200"),
    (("prompt200", "key"), "zvmwtr200"),
    (("prompt200", "lemon"), "avaace200"),
    (("prompt200", "a"), "prompt200"),
    (("prompt200", "zz"), "oqnlos200"),
    (("prompt200", "AgentU"), "pxszin200"),
    (("prompt200", "keyboard"), "zvmndt200"),
    (("prompt200", "AA"), "prompt200"),
    (("session200", "key"), "ciqcmmx200"),
    (("session200", "lemon"), "diegvzr200"),
    (("session200", "a"), "session200"),
    (("session200", "zz"), "rdrrhnm200"),
    (("session200", "AgentU"), "skwfbin200"),
    (("session200", "keyboard"), "ciqtwoe200"),
    (("session200", "AA"), "session200"),
    (("library200", "key"), "vmzbepi200"),
    (("library200", "lemon"), "wmnfncc200"),
    (("library200", "a"), "library200"),
    (("library200", "zz"), "khaqzqx200"),
    (("library200", "AgentU"), "lofetly200"),
    (("library200", "keyboard"), "vmzsorp200"),
    (("library200", "AA"), "library200"),
    (("service200", "key"), "cipfmao200"),
    (("service200", "lemon"), "didjvni200"),
    (("service200", "a"), "service200"),
    (("service200", "zz"), "rdquhbd200"),
    (("service200", "AgentU"), "skvibwe200"),
    (("service200", "keyboard"), "cipwwcv200"),
    (("service200", "AA"), "service200"),
    (("gateway200", "key"), "qeroayi200"),
    (("gateway200", "lemon"), "refsjlc200"),
    (("gateway200", "a"), "gateway200"),
    (("gateway200", "zz"), "fzsdvzx200"),
    (("gateway200", "AgentU"), "ggxrpuy200"),
    (("gateway200", "keyboard"), "qerfkap200"),
    (("gateway200", "AA"), "gateway200"),
    (("storage200", "key"), "cxmbeeo200"),
    (("storage200", "lemon"), "dxafnri200"),
    (("storage200", "a"), "storage200"),
    (("storage200", "zz"), "rsnqzfd200"),
    (("storage200", "AgentU"), "szsetae200"),
    (("storage200", "keyboard"), "cxmsogv200"),
    (("storage200", "AA"), "storage200"),
    (("network200", "key"), "xirgspu200"),
    (("network200", "lemon"), "yifkbco200"),
    (("network200", "a"), "network200"),
    (("network200", "zz"), "mdsvnqj200"),
    (("network200", "AgentU"), "nkxjhlk200"),
    (("network200", "keyboard"), "xirxcrb200"),
    (("network200", "AA"), "network200"),
    (("latency200", "key"), "verorai200"),
    (("latency200", "lemon"), "wefsanc200"),
    (("latency200", "a"), "latency200"),
    (("latency200", "zz"), "kzsdmbx200"),
    (("latency200", "AgentU"), "lgxrgwy200"),
    (("latency200", "keyboard"), "verfbcp200"),
    (("latency200", "AA"), "latency200"),
    (("buffer200", "key"), "lydpip200"),
    (("buffer200", "lemon"), "myrtrc200"),
    (("buffer200", "a"), "buffer200"),
    (("buffer200", "zz"), "ateedq200"),
    (("buffer200", "AgentU"), "bajsxl200"),
    (("buffer200", "keyboard"), "lydgsr200"),
    (("buffer200", "AA"), "buffer200"),
    (("queue200", "key"), "aycei200"),
    (("queue200", "lemon"), "byqir200"),
    (("queue200", "a"), "queue200"),
    (("queue200", "zz"), "ptdtd200"),
    (("queue200", "AgentU"), "qaihx200"),
    (("queue200", "keyboard"), "aycvs200"),
    (("queue200", "AA"), "queue200"),
    (("worker200", "key"), "gspuip200"),
    (("worker200", "lemon"), "hsdyrc200"),
    (("worker200", "a"), "worker200"),
    (("worker200", "zz"), "vnqjdq200"),
    (("worker200", "AgentU"), "wuvxxl200"),
    (("worker200", "keyboard"), "gsplsr200"),
    (("worker200", "AA"), "worker200"),
    (("kernel200", "key"), "uipxij200"),
    (("kernel200", "lemon"), "vidbrw200"),
    (("kernel200", "a"), "kernel200"),
    (("kernel200", "zz"), "jdqmdk200"),
    (("kernel200", "AgentU"), "kkvaxf200"),
    (("kernel200", "keyboard"), "uiposl200"),
    (("kernel200", "AA"), "kernel200"),
    (("signal200", "key"), "cmexej200"),
    (("signal200", "lemon"), "dmsbnw200"),
    (("signal200", "a"), "signal200"),
    (("signal200", "zz"), "rhfmzk200"),
    (("signal200", "AgentU"), "sokatf200"),
    (("signal200", "keyboard"), "cmeool200"),
    (("signal200", "AA"), "signal200"),
    (("packet200", "key"), "zeauir200"),
    (("packet200", "lemon"), "aeoyre200"),
    (("packet200", "a"), "packet200"),
    (("packet200", "zz"), "ozbjds200"),
    (("packet200", "AgentU"), "pggxxn200"),
    (("packet200", "keyboard"), "zealst200"),
    (("packet200", "AA"), "packet200"),
    (("router200", "key"), "bssdip200"),
    (("router200", "lemon"), "csghrc200"),
    (("router200", "a"), "router200"),
    (("router200", "zz"), "qntsdq200"),
    (("router200", "AgentU"), "ruygxl200"),
    (("router200", "keyboard"), "bssusr200"),
    (("router200", "AA"), "router200"),
    (("cluster200", "key"), "mpscxcb200"),
    (("cluster200", "lemon"), "npgggpv200"),
    (("cluster200", "a"), "cluster200"),
    (("cluster200", "zz"), "bktrsdq200"),
    (("cluster200", "AgentU"), "cryfmyr200"),
    (("cluster200", "keyboard"), "mpsthei200"),
    (("cluster200", "AA"), "cluster200"),
    (("mirror200", "key"), "wmpbsp200"),
    (("mirror200", "lemon"), "xmdfbc200"),
    (("mirror200", "a"), "mirror200"),
    (("mirror200", "zz"), "lhqqnq200"),
    (("mirror200", "AgentU"), "movehl200"),
    (("mirror200", "keyboard"), "wmpscr200"),
    (("mirror200", "AA"), "mirror200"),
    (("filter200", "key"), "pmjdip200"),
    (("filter200", "lemon"), "qmxhrc200"),
    (("filter200", "a"), "filter200"),
    (("filter200", "zz"), "ehksdq200"),
    (("filter200", "AgentU"), "fopgxl200"),
    (("filter200", "keyboard"), "pmjusr200"),
    (("filter200", "AA"), "filter200"),
    (("ranking200", "key"), "belumlq200"),
    (("ranking200", "lemon"), "cezyvyk200"),
    (("ranking200", "a"), "ranking200"),
    (("ranking200", "zz"), "qzmjhmf200"),
    (("ranking200", "AgentU"), "rgrxbhg200"),
    (("ranking200", "keyboard"), "bellwnx200"),
    (("ranking200", "AA"), "ranking200"),
    (("encoding200", "key"), "orayhgxk200"),
    (("encoding200", "lemon"), "procqtrs200"),
    (("encoding200", "a"), "encoding200"),
    (("encoding200", "zz"), "dmbnchmf200"),
    (("encoding200", "AgentU"), "etgbwcnm200"),
    (("encoding200", "keyboard"), "orapriej200"),
    (("encoding200", "AA"), "encoding200"),
    (("mapping200", "key"), "wenzmlq200"),
    (("mapping200", "lemon"), "xebdvyk200"),
    (("mapping200", "a"), "mapping200"),
    (("mapping200", "zz"), "lzoohmf200"),
    (("mapping200", "AgentU"), "mgtcbhg200"),
    (("mapping200", "keyboard"), "wenqwnx200"),
    (("mapping200", "AA"), "mapping200"),
    (("record200", "key"), "biayvb200"),
    (("record200", "lemon"), "cioceo200"),
    (("record200", "a"), "record200"),
    (("record200", "zz"), "qdbnqc200"),
    (("record200", "AgentU"), "rkgbkx200"),
    (("record200", "keyboard"), "biapfd200"),
    (("record200", "AA"), "record200"),
    (("candle200", "key"), "melnpc200"),
    (("candle200", "lemon"), "nezryp200"),
    (("candle200", "a"), "candle200"),
    (("candle200", "zz"), "bzmckd200"),
    (("candle200", "AgentU"), "cgrqey200"),
    (("candle200", "keyboard"), "meleze200"),
    (("candle200", "AA"), "candle200"),
    (("thread200", "key"), "dlpoeb200"),
    (("thread200", "lemon"), "eldsno200"),
    (("thread200", "a"), "thread200"),
    (("thread200", "zz"), "sgqdzc200"),
    (("thread200", "AgentU"), "tnvrtx200"),
    (("thread200", "keyboard"), "dlpfod200"),
    (("thread200", "AA"), "thread200"),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 200: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 200: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "a"),
        "round 200: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 200: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 200: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 200: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", "AA"),
        "round 200: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "key"),
        "bssxh 200: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 200: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "a"),
        "round 200: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 200: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 200: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 200: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", "AA"),
        "round 200: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 200: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 200: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "a"),
        "round 200: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 200: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 200: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 200: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", "AA"),
        "round 200: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 200: the processor reads the record then stops", "key"),
        "bssxh 200: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 200: the processor reads the record then stops", "lemon"),
        "csgbq 200: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 200: the processor reads the record then stops", "a"),
        "round 200: the processor reads the record then stops",
    ),
    (
        ("round 200: the processor reads the record then stops", "zz"),
        "qntmc 200: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 200: the processor reads the record then stops", "AgentU"),
        "ruyaw 200: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 200: the processor reads the record then stops", "keyboard"),
        "bssor 200: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 200: the processor reads the record then stops", "AA"),
        "round 200: the processor reads the record then stops",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "key"),
        "bssxh 200: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "lemon"),
        "csgbq 200: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "a"),
        "round 200: a worker pulls the next task from the queue",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "zz"),
        "qntmc 200: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 200: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "keyboard"),
        "bssor 200: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 200: a worker pulls the next task from the queue", "AA"),
        "round 200: a worker pulls the next task from the queue",
    ),
    (
        ("round 200: signals travel through the network layer", "key"),
        "bssxh 200: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 200: signals travel through the network layer", "lemon"),
        "csgbq 200: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 200: signals travel through the network layer", "a"),
        "round 200: signals travel through the network layer",
    ),
    (
        ("round 200: signals travel through the network layer", "zz"),
        "qntmc 200: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 200: signals travel through the network layer", "AgentU"),
        "ruyaw 200: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 200: signals travel through the network layer", "keyboard"),
        "bssor 200: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 200: signals travel through the network layer", "AA"),
        "round 200: signals travel through the network layer",
    ),
    (
        ("round 200: the gateway routes each request by policy", "key"),
        "bssxh 200: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 200: the gateway routes each request by policy", "lemon"),
        "csgbq 200: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 200: the gateway routes each request by policy", "a"),
        "round 200: the gateway routes each request by policy",
    ),
    (
        ("round 200: the gateway routes each request by policy", "zz"),
        "qntmc 200: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 200: the gateway routes each request by policy", "AgentU"),
        "ruyaw 200: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 200: the gateway routes each request by policy", "keyboard"),
        "bssor 200: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 200: the gateway routes each request by policy", "AA"),
        "round 200: the gateway routes each request by policy",
    ),
    (("round 200: memory grows until the buffer is full", "key"), "bssxh 200: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 200: memory grows until the buffer is full", "lemon"), "csgbq 200: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 200: memory grows until the buffer is full", "a"), "round 200: memory grows until the buffer is full"),
    (("round 200: memory grows until the buffer is full", "zz"), "qntmc 200: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 200: memory grows until the buffer is full", "AgentU"),
        "ruyaw 200: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 200: memory grows until the buffer is full", "keyboard"),
        "bssor 200: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 200: memory grows until the buffer is full", "AA"), "round 200: memory grows until the buffer is full"),
    (("round 200: the cluster mirrors every packet twice", "key"), "bssxh 200: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 200: the cluster mirrors every packet twice", "lemon"),
        "csgbq 200: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 200: the cluster mirrors every packet twice", "a"), "round 200: the cluster mirrors every packet twice"),
    (("round 200: the cluster mirrors every packet twice", "zz"), "qntmc 200: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 200: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 200: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 200: the cluster mirrors every packet twice", "keyboard"),
        "bssor 200: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 200: the cluster mirrors every packet twice", "AA"), "round 200: the cluster mirrors every packet twice"),
    (
        ("round 200: ranking uses tokens learned from the corpus", "key"),
        "bssxh 200: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 200: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", "a"),
        "round 200: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 200: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 200: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 200: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", "AA"),
        "round 200: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 200: a long session ends when the candle dies", "key"),
        "bssxh 200: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 200: a long session ends when the candle dies", "lemon"),
        "csgbq 200: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 200: a long session ends when the candle dies", "a"),
        "round 200: a long session ends when the candle dies",
    ),
    (
        ("round 200: a long session ends when the candle dies", "zz"),
        "qntmc 200: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 200: a long session ends when the candle dies", "AgentU"),
        "ruyaw 200: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 200: a long session ends when the candle dies", "keyboard"),
        "bssor 200: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 200: a long session ends when the candle dies", "AA"),
        "round 200: a long session ends when the candle dies",
    ),
    (("round 200: encode the prompt then map the result", "key"), "bssxh 200: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 200: encode the prompt then map the result", "lemon"), "csgbq 200: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 200: encode the prompt then map the result", "a"), "round 200: encode the prompt then map the result"),
    (("round 200: encode the prompt then map the result", "zz"), "qntmc 200: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 200: encode the prompt then map the result", "AgentU"),
        "ruyaw 200: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 200: encode the prompt then map the result", "keyboard"),
        "bssor 200: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 200: encode the prompt then map the result", "AA"), "round 200: encode the prompt then map the result"),
    (("round 200: the kernel wakes the worker at dawn", "key"), "bssxh 200: rri iovlop ukocc xfo ambocb er neux"),
    (("round 200: the kernel wakes the worker at dawn", "lemon"), "csgbq 200: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 200: the kernel wakes the worker at dawn", "a"), "round 200: the kernel wakes the worker at dawn"),
    (("round 200: the kernel wakes the worker at dawn", "zz"), "qntmc 200: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 200: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 200: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 200: the kernel wakes the worker at dawn", "keyboard"), "bssor 200: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 200: the kernel wakes the worker at dawn", "AA"), "round 200: the kernel wakes the worker at dawn"),
    (("round 200: service latency drops after the patch", "key"), "bssxh 200: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 200: service latency drops after the patch", "lemon"), "csgbq 200: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 200: service latency drops after the patch", "a"), "round 200: service latency drops after the patch"),
    (("round 200: service latency drops after the patch", "zz"), "qntmc 200: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 200: service latency drops after the patch", "AgentU"),
        "ruyaw 200: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 200: service latency drops after the patch", "keyboard"),
        "bssor 200: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 200: service latency drops after the patch", "AA"), "round 200: service latency drops after the patch"),
    (
        ("round 200: the library caches every vector it sees", "key"),
        "bssxh 200: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 200: the library caches every vector it sees", "lemon"),
        "csgbq 200: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 200: the library caches every vector it sees", "a"), "round 200: the library caches every vector it sees"),
    (
        ("round 200: the library caches every vector it sees", "zz"),
        "qntmc 200: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 200: the library caches every vector it sees", "AgentU"),
        "ruyaw 200: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 200: the library caches every vector it sees", "keyboard"),
        "bssor 200: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 200: the library caches every vector it sees", "AA"),
        "round 200: the library caches every vector it sees",
    ),
    (("round 200: agents argue then the debate resolves", "key"), "bssxh 200: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 200: agents argue then the debate resolves", "lemon"), "csgbq 200: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 200: agents argue then the debate resolves", "a"), "round 200: agents argue then the debate resolves"),
    (("round 200: agents argue then the debate resolves", "zz"), "qntmc 200: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 200: agents argue then the debate resolves", "AgentU"),
        "ruyaw 200: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 200: agents argue then the debate resolves", "keyboard"),
        "bssor 200: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 200: agents argue then the debate resolves", "AA"), "round 200: agents argue then the debate resolves"),
    (("round 200: the filter keeps only strong matches", "key"), "bssxh 200: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 200: the filter keeps only strong matches", "lemon"), "csgbq 200: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 200: the filter keeps only strong matches", "a"), "round 200: the filter keeps only strong matches"),
    (("round 200: the filter keeps only strong matches", "zz"), "qntmc 200: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 200: the filter keeps only strong matches", "AgentU"), "ruyaw 200: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 200: the filter keeps only strong matches", "keyboard"),
        "bssor 200: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 200: the filter keeps only strong matches", "AA"), "round 200: the filter keeps only strong matches"),
    (("round 200: the model answers with a short reply", "key"), "bssxh 200: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 200: the model answers with a short reply", "lemon"), "csgbq 200: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 200: the model answers with a short reply", "a"), "round 200: the model answers with a short reply"),
    (("round 200: the model answers with a short reply", "zz"), "qntmc 200: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 200: the model answers with a short reply", "AgentU"), "ruyaw 200: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 200: the model answers with a short reply", "keyboard"),
        "bssor 200: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 200: the model answers with a short reply", "AA"), "round 200: the model answers with a short reply"),
    (
        ("round 200: the recorder stores the reasoning trace", "key"),
        "bssxh 200: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 200: the recorder stores the reasoning trace", "lemon"),
        "csgbq 200: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 200: the recorder stores the reasoning trace", "a"), "round 200: the recorder stores the reasoning trace"),
    (
        ("round 200: the recorder stores the reasoning trace", "zz"),
        "qntmc 200: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 200: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 200: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 200: the recorder stores the reasoning trace", "keyboard"),
        "bssor 200: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 200: the recorder stores the reasoning trace", "AA"),
        "round 200: the recorder stores the reasoning trace",
    ),
    (("round 200: the angel watches the processor run", "key"), "bssxh 200: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 200: the angel watches the processor run", "lemon"), "csgbq 200: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 200: the angel watches the processor run", "a"), "round 200: the angel watches the processor run"),
    (("round 200: the angel watches the processor run", "zz"), "qntmc 200: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 200: the angel watches the processor run", "AgentU"), "ruyaw 200: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 200: the angel watches the processor run", "keyboard"), "bssor 200: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 200: the angel watches the processor run", "AA"), "round 200: the angel watches the processor run"),
    (("round 200: angle of the vector decides the match", "key"), "bssxh 200: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 200: angle of the vector decides the match", "lemon"), "csgbq 200: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 200: angle of the vector decides the match", "a"), "round 200: angle of the vector decides the match"),
    (("round 200: angle of the vector decides the match", "zz"), "qntmc 200: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 200: angle of the vector decides the match", "AgentU"),
        "ruyaw 200: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 200: angle of the vector decides the match", "keyboard"),
        "bssor 200: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 200: angle of the vector decides the match", "AA"), "round 200: angle of the vector decides the match"),
    (
        ("round 200: the candle burns twice as long at night", "key"),
        "bssxh 200: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 200: the candle burns twice as long at night", "lemon"),
        "csgbq 200: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 200: the candle burns twice as long at night", "a"), "round 200: the candle burns twice as long at night"),
    (
        ("round 200: the candle burns twice as long at night", "zz"),
        "qntmc 200: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 200: the candle burns twice as long at night", "AgentU"),
        "ruyaw 200: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 200: the candle burns twice as long at night", "keyboard"),
        "bssor 200: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 200: the candle burns twice as long at night", "AA"),
        "round 200: the candle burns twice as long at night",
    ),
    (("round 200: a mirror of the universe in one line", "key"), "bssxh 200: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 200: a mirror of the universe in one line", "lemon"), "csgbq 200: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 200: a mirror of the universe in one line", "a"), "round 200: a mirror of the universe in one line"),
    (("round 200: a mirror of the universe in one line", "zz"), "qntmc 200: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 200: a mirror of the universe in one line", "AgentU"), "ruyaw 200: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 200: a mirror of the universe in one line", "keyboard"),
        "bssor 200: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 200: a mirror of the universe in one line", "AA"), "round 200: a mirror of the universe in one line"),
    (("round 200: the queue drains before the storm", "key"), "bssxh 200: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 200: the queue drains before the storm", "lemon"), "csgbq 200: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 200: the queue drains before the storm", "a"), "round 200: the queue drains before the storm"),
    (("round 200: the queue drains before the storm", "zz"), "qntmc 200: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 200: the queue drains before the storm", "AgentU"), "ruyaw 200: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 200: the queue drains before the storm", "keyboard"), "bssor 200: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 200: the queue drains before the storm", "AA"), "round 200: the queue drains before the storm"),
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
