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
    (("kitten186", "key"), "umrdil186"),
    (("kitten186", "lemon"), "vmfhry186"),
    (("kitten186", "a"), "kitten186"),
    (("kitten186", "zz"), "jhssdm186"),
    (("kitten186", "AgentU"), "koxgxh186"),
    (("kitten186", "keyboard"), "umrusn186"),
    (("kitten186", "AA"), "kitten186"),
    (("sitting186", "key"), "cmrdmlq186"),
    (("sitting186", "lemon"), "dmfhvyk186"),
    (("sitting186", "a"), "sitting186"),
    (("sitting186", "zz"), "rhsshmf186"),
    (("sitting186", "AgentU"), "soxgbhg186"),
    (("sitting186", "keyboard"), "cmruwnx186"),
    (("sitting186", "AA"), "sitting186"),
    (("agent186", "key"), "kkcxx186"),
    (("agent186", "lemon"), "lkqbg186"),
    (("agent186", "a"), "agent186"),
    (("agent186", "zz"), "zfdms186"),
    (("agent186", "AgentU"), "amiam186"),
    (("agent186", "keyboard"), "kkcoh186"),
    (("agent186", "AA"), "agent186"),
    (("angle186", "key"), "krevi186"),
    (("angle186", "lemon"), "lrszr186"),
    (("angle186", "a"), "angle186"),
    (("angle186", "zz"), "zmfkd186"),
    (("angle186", "AgentU"), "atkyx186"),
    (("angle186", "keyboard"), "krems186"),
    (("angle186", "AA"), "angle186"),
    (("universe186", "key"), "ergfipci186"),
    (("universe186", "lemon"), "frujrcwq186"),
    (("universe186", "a"), "universe186"),
    (("universe186", "zz"), "tmhudqrd186"),
    (("universe186", "AgentU"), "utmixlsk186"),
    (("universe186", "keyboard"), "ergwsrjh186"),
    (("universe186", "AA"), "universe186"),
    (("memory186", "key"), "wikyvw186"),
    (("memory186", "lemon"), "xiycej186"),
    (("memory186", "a"), "memory186"),
    (("memory186", "zz"), "ldlnqx186"),
    (("memory186", "AgentU"), "mkqbks186"),
    (("memory186", "keyboard"), "wikpfy186"),
    (("memory186", "AA"), "memory186"),
    (("stream186", "key"), "cxpoek186"),
    (("stream186", "lemon"), "dxdsnx186"),
    (("stream186", "a"), "stream186"),
    (("stream186", "zz"), "rsqdzl186"),
    (("stream186", "AgentU"), "szvrtg186"),
    (("stream186", "keyboard"), "cxpfom186"),
    (("stream186", "AA"), "stream186"),
    (("context186", "key"), "msldivd186"),
    (("context186", "lemon"), "nszhrix186"),
    (("context186", "a"), "context186"),
    (("context186", "zz"), "bnmsdws186"),
    (("context186", "AgentU"), "curgxrt186"),
    (("context186", "keyboard"), "mslusxk186"),
    (("context186", "AA"), "context186"),
    (("knowledge186", "key"), "urmgpcnkc186"),
    (("knowledge186", "lemon"), "vrakyphss186"),
    (("knowledge186", "a"), "knowledge186"),
    (("knowledge186", "zz"), "jmnvkdcfd186"),
    (("knowledge186", "AgentU"), "ktsjeydmi186"),
    (("knowledge186", "keyboard"), "urmxzeujo186"),
    (("knowledge186", "AA"), "knowledge186"),
    (("vector186", "key"), "fiadsp186"),
    (("vector186", "lemon"), "giohbc186"),
    (("vector186", "a"), "vector186"),
    (("vector186", "zz"), "udbsnq186"),
    (("vector186", "AgentU"), "vkgghl186"),
    (("vector186", "keyboard"), "fiaucr186"),
    (("vector186", "AA"), "vector186"),
    (("processor186", "key"), "zvmmiqcsp186"),
    (("processor186", "lemon"), "avaqrdwaf186"),
    (("processor186", "a"), "processor186"),
    (("processor186", "zz"), "oqnbdrrnq186"),
    (("processor186", "AgentU"), "pxspxmsuv186"),
    (("processor186", "keyboard"), "zvmdssjrb186"),
    (("processor186", "AA"), "processor186"),
    (("reasoning186", "key"), "biycslsre186"),
    (("reasoning186", "lemon"), "cimgbymzu186"),
    (("reasoning186", "a"), "reasoning186"),
    (("reasoning186", "zz"), "qdzrnmhmf186"),
    (("reasoning186", "AgentU"), "rkefhhitk186"),
    (("reasoning186", "keyboard"), "biytcnzqq186"),
    (("reasoning186", "AA"), "reasoning186"),
    (("machine186", "key"), "wearmlo186"),
    (("machine186", "lemon"), "xeovvyi186"),
    (("machine186", "a"), "machine186"),
    (("machine186", "zz"), "lzbghmd186"),
    (("machine186", "AgentU"), "mggubhe186"),
    (("machine186", "keyboard"), "weaiwnv186"),
    (("machine186", "AA"), "machine186"),
    (("learning186", "key"), "viybrgxk186"),
    (("learning186", "lemon"), "wimfatrs186"),
    (("learning186", "a"), "learning186"),
    (("learning186", "zz"), "kdzqmhmf186"),
    (("learning186", "AgentU"), "lkeegcnm186"),
    (("learning186", "keyboard"), "viysbiej186"),
    (("learning186", "AA"), "learning186"),
    (("model186", "key"), "wsbop186"),
    (("model186", "lemon"), "xspsy186"),
    (("model186", "a"), "model186"),
    (("model186", "zz"), "lncdk186"),
    (("model186", "AgentU"), "muhre186"),
    (("model186", "keyboard"), "wsbfz186"),
    (("model186", "AA"), "model186"),
    (("token186", "key"), "dsior186"),
    (("token186", "lemon"), "eswsa186"),
    (("token186", "a"), "token186"),
    (("token186", "zz"), "snjdm186"),
    (("token186", "AgentU"), "tuorg186"),
    (("token186", "keyboard"), "dsifb186"),
    (("token186", "AA"), "token186"),
    (("prompt186", "key"), "zvmwtr186"),
    (("prompt186", "lemon"), "avaace186"),
    (("prompt186", "a"), "prompt186"),
    (("prompt186", "zz"), "oqnlos186"),
    (("prompt186", "AgentU"), "pxszin186"),
    (("prompt186", "keyboard"), "zvmndt186"),
    (("prompt186", "AA"), "prompt186"),
    (("session186", "key"), "ciqcmmx186"),
    (("session186", "lemon"), "diegvzr186"),
    (("session186", "a"), "session186"),
    (("session186", "zz"), "rdrrhnm186"),
    (("session186", "AgentU"), "skwfbin186"),
    (("session186", "keyboard"), "ciqtwoe186"),
    (("session186", "AA"), "session186"),
    (("library186", "key"), "vmzbepi186"),
    (("library186", "lemon"), "wmnfncc186"),
    (("library186", "a"), "library186"),
    (("library186", "zz"), "khaqzqx186"),
    (("library186", "AgentU"), "lofetly186"),
    (("library186", "keyboard"), "vmzsorp186"),
    (("library186", "AA"), "library186"),
    (("service186", "key"), "cipfmao186"),
    (("service186", "lemon"), "didjvni186"),
    (("service186", "a"), "service186"),
    (("service186", "zz"), "rdquhbd186"),
    (("service186", "AgentU"), "skvibwe186"),
    (("service186", "keyboard"), "cipwwcv186"),
    (("service186", "AA"), "service186"),
    (("gateway186", "key"), "qeroayi186"),
    (("gateway186", "lemon"), "refsjlc186"),
    (("gateway186", "a"), "gateway186"),
    (("gateway186", "zz"), "fzsdvzx186"),
    (("gateway186", "AgentU"), "ggxrpuy186"),
    (("gateway186", "keyboard"), "qerfkap186"),
    (("gateway186", "AA"), "gateway186"),
    (("storage186", "key"), "cxmbeeo186"),
    (("storage186", "lemon"), "dxafnri186"),
    (("storage186", "a"), "storage186"),
    (("storage186", "zz"), "rsnqzfd186"),
    (("storage186", "AgentU"), "szsetae186"),
    (("storage186", "keyboard"), "cxmsogv186"),
    (("storage186", "AA"), "storage186"),
    (("network186", "key"), "xirgspu186"),
    (("network186", "lemon"), "yifkbco186"),
    (("network186", "a"), "network186"),
    (("network186", "zz"), "mdsvnqj186"),
    (("network186", "AgentU"), "nkxjhlk186"),
    (("network186", "keyboard"), "xirxcrb186"),
    (("network186", "AA"), "network186"),
    (("latency186", "key"), "verorai186"),
    (("latency186", "lemon"), "wefsanc186"),
    (("latency186", "a"), "latency186"),
    (("latency186", "zz"), "kzsdmbx186"),
    (("latency186", "AgentU"), "lgxrgwy186"),
    (("latency186", "keyboard"), "verfbcp186"),
    (("latency186", "AA"), "latency186"),
    (("buffer186", "key"), "lydpip186"),
    (("buffer186", "lemon"), "myrtrc186"),
    (("buffer186", "a"), "buffer186"),
    (("buffer186", "zz"), "ateedq186"),
    (("buffer186", "AgentU"), "bajsxl186"),
    (("buffer186", "keyboard"), "lydgsr186"),
    (("buffer186", "AA"), "buffer186"),
    (("queue186", "key"), "aycei186"),
    (("queue186", "lemon"), "byqir186"),
    (("queue186", "a"), "queue186"),
    (("queue186", "zz"), "ptdtd186"),
    (("queue186", "AgentU"), "qaihx186"),
    (("queue186", "keyboard"), "aycvs186"),
    (("queue186", "AA"), "queue186"),
    (("worker186", "key"), "gspuip186"),
    (("worker186", "lemon"), "hsdyrc186"),
    (("worker186", "a"), "worker186"),
    (("worker186", "zz"), "vnqjdq186"),
    (("worker186", "AgentU"), "wuvxxl186"),
    (("worker186", "keyboard"), "gsplsr186"),
    (("worker186", "AA"), "worker186"),
    (("kernel186", "key"), "uipxij186"),
    (("kernel186", "lemon"), "vidbrw186"),
    (("kernel186", "a"), "kernel186"),
    (("kernel186", "zz"), "jdqmdk186"),
    (("kernel186", "AgentU"), "kkvaxf186"),
    (("kernel186", "keyboard"), "uiposl186"),
    (("kernel186", "AA"), "kernel186"),
    (("signal186", "key"), "cmexej186"),
    (("signal186", "lemon"), "dmsbnw186"),
    (("signal186", "a"), "signal186"),
    (("signal186", "zz"), "rhfmzk186"),
    (("signal186", "AgentU"), "sokatf186"),
    (("signal186", "keyboard"), "cmeool186"),
    (("signal186", "AA"), "signal186"),
    (("packet186", "key"), "zeauir186"),
    (("packet186", "lemon"), "aeoyre186"),
    (("packet186", "a"), "packet186"),
    (("packet186", "zz"), "ozbjds186"),
    (("packet186", "AgentU"), "pggxxn186"),
    (("packet186", "keyboard"), "zealst186"),
    (("packet186", "AA"), "packet186"),
    (("router186", "key"), "bssdip186"),
    (("router186", "lemon"), "csghrc186"),
    (("router186", "a"), "router186"),
    (("router186", "zz"), "qntsdq186"),
    (("router186", "AgentU"), "ruygxl186"),
    (("router186", "keyboard"), "bssusr186"),
    (("router186", "AA"), "router186"),
    (("cluster186", "key"), "mpscxcb186"),
    (("cluster186", "lemon"), "npgggpv186"),
    (("cluster186", "a"), "cluster186"),
    (("cluster186", "zz"), "bktrsdq186"),
    (("cluster186", "AgentU"), "cryfmyr186"),
    (("cluster186", "keyboard"), "mpsthei186"),
    (("cluster186", "AA"), "cluster186"),
    (("mirror186", "key"), "wmpbsp186"),
    (("mirror186", "lemon"), "xmdfbc186"),
    (("mirror186", "a"), "mirror186"),
    (("mirror186", "zz"), "lhqqnq186"),
    (("mirror186", "AgentU"), "movehl186"),
    (("mirror186", "keyboard"), "wmpscr186"),
    (("mirror186", "AA"), "mirror186"),
    (("filter186", "key"), "pmjdip186"),
    (("filter186", "lemon"), "qmxhrc186"),
    (("filter186", "a"), "filter186"),
    (("filter186", "zz"), "ehksdq186"),
    (("filter186", "AgentU"), "fopgxl186"),
    (("filter186", "keyboard"), "pmjusr186"),
    (("filter186", "AA"), "filter186"),
    (("ranking186", "key"), "belumlq186"),
    (("ranking186", "lemon"), "cezyvyk186"),
    (("ranking186", "a"), "ranking186"),
    (("ranking186", "zz"), "qzmjhmf186"),
    (("ranking186", "AgentU"), "rgrxbhg186"),
    (("ranking186", "keyboard"), "bellwnx186"),
    (("ranking186", "AA"), "ranking186"),
    (("encoding186", "key"), "orayhgxk186"),
    (("encoding186", "lemon"), "procqtrs186"),
    (("encoding186", "a"), "encoding186"),
    (("encoding186", "zz"), "dmbnchmf186"),
    (("encoding186", "AgentU"), "etgbwcnm186"),
    (("encoding186", "keyboard"), "orapriej186"),
    (("encoding186", "AA"), "encoding186"),
    (("mapping186", "key"), "wenzmlq186"),
    (("mapping186", "lemon"), "xebdvyk186"),
    (("mapping186", "a"), "mapping186"),
    (("mapping186", "zz"), "lzoohmf186"),
    (("mapping186", "AgentU"), "mgtcbhg186"),
    (("mapping186", "keyboard"), "wenqwnx186"),
    (("mapping186", "AA"), "mapping186"),
    (("record186", "key"), "biayvb186"),
    (("record186", "lemon"), "cioceo186"),
    (("record186", "a"), "record186"),
    (("record186", "zz"), "qdbnqc186"),
    (("record186", "AgentU"), "rkgbkx186"),
    (("record186", "keyboard"), "biapfd186"),
    (("record186", "AA"), "record186"),
    (("candle186", "key"), "melnpc186"),
    (("candle186", "lemon"), "nezryp186"),
    (("candle186", "a"), "candle186"),
    (("candle186", "zz"), "bzmckd186"),
    (("candle186", "AgentU"), "cgrqey186"),
    (("candle186", "keyboard"), "meleze186"),
    (("candle186", "AA"), "candle186"),
    (("thread186", "key"), "dlpoeb186"),
    (("thread186", "lemon"), "eldsno186"),
    (("thread186", "a"), "thread186"),
    (("thread186", "zz"), "sgqdzc186"),
    (("thread186", "AgentU"), "tnvrtx186"),
    (("thread186", "keyboard"), "dlpfod186"),
    (("thread186", "AA"), "thread186"),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 186: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 186: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "a"),
        "round 186: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 186: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 186: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 186: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", "AA"),
        "round 186: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "key"),
        "bssxh 186: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 186: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "a"),
        "round 186: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 186: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 186: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 186: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", "AA"),
        "round 186: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 186: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 186: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "a"),
        "round 186: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 186: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 186: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 186: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", "AA"),
        "round 186: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 186: the processor reads the record then stops", "key"),
        "bssxh 186: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 186: the processor reads the record then stops", "lemon"),
        "csgbq 186: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 186: the processor reads the record then stops", "a"),
        "round 186: the processor reads the record then stops",
    ),
    (
        ("round 186: the processor reads the record then stops", "zz"),
        "qntmc 186: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 186: the processor reads the record then stops", "AgentU"),
        "ruyaw 186: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 186: the processor reads the record then stops", "keyboard"),
        "bssor 186: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 186: the processor reads the record then stops", "AA"),
        "round 186: the processor reads the record then stops",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "key"),
        "bssxh 186: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "lemon"),
        "csgbq 186: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "a"),
        "round 186: a worker pulls the next task from the queue",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "zz"),
        "qntmc 186: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 186: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "keyboard"),
        "bssor 186: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 186: a worker pulls the next task from the queue", "AA"),
        "round 186: a worker pulls the next task from the queue",
    ),
    (
        ("round 186: signals travel through the network layer", "key"),
        "bssxh 186: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 186: signals travel through the network layer", "lemon"),
        "csgbq 186: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 186: signals travel through the network layer", "a"),
        "round 186: signals travel through the network layer",
    ),
    (
        ("round 186: signals travel through the network layer", "zz"),
        "qntmc 186: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 186: signals travel through the network layer", "AgentU"),
        "ruyaw 186: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 186: signals travel through the network layer", "keyboard"),
        "bssor 186: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 186: signals travel through the network layer", "AA"),
        "round 186: signals travel through the network layer",
    ),
    (
        ("round 186: the gateway routes each request by policy", "key"),
        "bssxh 186: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 186: the gateway routes each request by policy", "lemon"),
        "csgbq 186: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 186: the gateway routes each request by policy", "a"),
        "round 186: the gateway routes each request by policy",
    ),
    (
        ("round 186: the gateway routes each request by policy", "zz"),
        "qntmc 186: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 186: the gateway routes each request by policy", "AgentU"),
        "ruyaw 186: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 186: the gateway routes each request by policy", "keyboard"),
        "bssor 186: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 186: the gateway routes each request by policy", "AA"),
        "round 186: the gateway routes each request by policy",
    ),
    (("round 186: memory grows until the buffer is full", "key"), "bssxh 186: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 186: memory grows until the buffer is full", "lemon"), "csgbq 186: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 186: memory grows until the buffer is full", "a"), "round 186: memory grows until the buffer is full"),
    (("round 186: memory grows until the buffer is full", "zz"), "qntmc 186: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 186: memory grows until the buffer is full", "AgentU"),
        "ruyaw 186: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 186: memory grows until the buffer is full", "keyboard"),
        "bssor 186: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 186: memory grows until the buffer is full", "AA"), "round 186: memory grows until the buffer is full"),
    (("round 186: the cluster mirrors every packet twice", "key"), "bssxh 186: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 186: the cluster mirrors every packet twice", "lemon"),
        "csgbq 186: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 186: the cluster mirrors every packet twice", "a"), "round 186: the cluster mirrors every packet twice"),
    (("round 186: the cluster mirrors every packet twice", "zz"), "qntmc 186: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 186: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 186: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 186: the cluster mirrors every packet twice", "keyboard"),
        "bssor 186: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 186: the cluster mirrors every packet twice", "AA"), "round 186: the cluster mirrors every packet twice"),
    (
        ("round 186: ranking uses tokens learned from the corpus", "key"),
        "bssxh 186: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 186: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", "a"),
        "round 186: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 186: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 186: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 186: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", "AA"),
        "round 186: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 186: a long session ends when the candle dies", "key"),
        "bssxh 186: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 186: a long session ends when the candle dies", "lemon"),
        "csgbq 186: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 186: a long session ends when the candle dies", "a"),
        "round 186: a long session ends when the candle dies",
    ),
    (
        ("round 186: a long session ends when the candle dies", "zz"),
        "qntmc 186: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 186: a long session ends when the candle dies", "AgentU"),
        "ruyaw 186: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 186: a long session ends when the candle dies", "keyboard"),
        "bssor 186: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 186: a long session ends when the candle dies", "AA"),
        "round 186: a long session ends when the candle dies",
    ),
    (("round 186: encode the prompt then map the result", "key"), "bssxh 186: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 186: encode the prompt then map the result", "lemon"), "csgbq 186: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 186: encode the prompt then map the result", "a"), "round 186: encode the prompt then map the result"),
    (("round 186: encode the prompt then map the result", "zz"), "qntmc 186: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 186: encode the prompt then map the result", "AgentU"),
        "ruyaw 186: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 186: encode the prompt then map the result", "keyboard"),
        "bssor 186: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 186: encode the prompt then map the result", "AA"), "round 186: encode the prompt then map the result"),
    (("round 186: the kernel wakes the worker at dawn", "key"), "bssxh 186: rri iovlop ukocc xfo ambocb er neux"),
    (("round 186: the kernel wakes the worker at dawn", "lemon"), "csgbq 186: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 186: the kernel wakes the worker at dawn", "a"), "round 186: the kernel wakes the worker at dawn"),
    (("round 186: the kernel wakes the worker at dawn", "zz"), "qntmc 186: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 186: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 186: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 186: the kernel wakes the worker at dawn", "keyboard"), "bssor 186: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 186: the kernel wakes the worker at dawn", "AA"), "round 186: the kernel wakes the worker at dawn"),
    (("round 186: service latency drops after the patch", "key"), "bssxh 186: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 186: service latency drops after the patch", "lemon"), "csgbq 186: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 186: service latency drops after the patch", "a"), "round 186: service latency drops after the patch"),
    (("round 186: service latency drops after the patch", "zz"), "qntmc 186: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 186: service latency drops after the patch", "AgentU"),
        "ruyaw 186: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 186: service latency drops after the patch", "keyboard"),
        "bssor 186: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 186: service latency drops after the patch", "AA"), "round 186: service latency drops after the patch"),
    (
        ("round 186: the library caches every vector it sees", "key"),
        "bssxh 186: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 186: the library caches every vector it sees", "lemon"),
        "csgbq 186: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 186: the library caches every vector it sees", "a"), "round 186: the library caches every vector it sees"),
    (
        ("round 186: the library caches every vector it sees", "zz"),
        "qntmc 186: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 186: the library caches every vector it sees", "AgentU"),
        "ruyaw 186: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 186: the library caches every vector it sees", "keyboard"),
        "bssor 186: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 186: the library caches every vector it sees", "AA"),
        "round 186: the library caches every vector it sees",
    ),
    (("round 186: agents argue then the debate resolves", "key"), "bssxh 186: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 186: agents argue then the debate resolves", "lemon"), "csgbq 186: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 186: agents argue then the debate resolves", "a"), "round 186: agents argue then the debate resolves"),
    (("round 186: agents argue then the debate resolves", "zz"), "qntmc 186: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 186: agents argue then the debate resolves", "AgentU"),
        "ruyaw 186: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 186: agents argue then the debate resolves", "keyboard"),
        "bssor 186: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 186: agents argue then the debate resolves", "AA"), "round 186: agents argue then the debate resolves"),
    (("round 186: the filter keeps only strong matches", "key"), "bssxh 186: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 186: the filter keeps only strong matches", "lemon"), "csgbq 186: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 186: the filter keeps only strong matches", "a"), "round 186: the filter keeps only strong matches"),
    (("round 186: the filter keeps only strong matches", "zz"), "qntmc 186: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 186: the filter keeps only strong matches", "AgentU"), "ruyaw 186: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 186: the filter keeps only strong matches", "keyboard"),
        "bssor 186: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 186: the filter keeps only strong matches", "AA"), "round 186: the filter keeps only strong matches"),
    (("round 186: the model answers with a short reply", "key"), "bssxh 186: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 186: the model answers with a short reply", "lemon"), "csgbq 186: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 186: the model answers with a short reply", "a"), "round 186: the model answers with a short reply"),
    (("round 186: the model answers with a short reply", "zz"), "qntmc 186: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 186: the model answers with a short reply", "AgentU"), "ruyaw 186: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 186: the model answers with a short reply", "keyboard"),
        "bssor 186: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 186: the model answers with a short reply", "AA"), "round 186: the model answers with a short reply"),
    (
        ("round 186: the recorder stores the reasoning trace", "key"),
        "bssxh 186: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 186: the recorder stores the reasoning trace", "lemon"),
        "csgbq 186: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 186: the recorder stores the reasoning trace", "a"), "round 186: the recorder stores the reasoning trace"),
    (
        ("round 186: the recorder stores the reasoning trace", "zz"),
        "qntmc 186: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 186: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 186: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 186: the recorder stores the reasoning trace", "keyboard"),
        "bssor 186: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 186: the recorder stores the reasoning trace", "AA"),
        "round 186: the recorder stores the reasoning trace",
    ),
    (("round 186: the angel watches the processor run", "key"), "bssxh 186: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 186: the angel watches the processor run", "lemon"), "csgbq 186: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 186: the angel watches the processor run", "a"), "round 186: the angel watches the processor run"),
    (("round 186: the angel watches the processor run", "zz"), "qntmc 186: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 186: the angel watches the processor run", "AgentU"), "ruyaw 186: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 186: the angel watches the processor run", "keyboard"), "bssor 186: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 186: the angel watches the processor run", "AA"), "round 186: the angel watches the processor run"),
    (("round 186: angle of the vector decides the match", "key"), "bssxh 186: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 186: angle of the vector decides the match", "lemon"), "csgbq 186: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 186: angle of the vector decides the match", "a"), "round 186: angle of the vector decides the match"),
    (("round 186: angle of the vector decides the match", "zz"), "qntmc 186: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 186: angle of the vector decides the match", "AgentU"),
        "ruyaw 186: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 186: angle of the vector decides the match", "keyboard"),
        "bssor 186: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 186: angle of the vector decides the match", "AA"), "round 186: angle of the vector decides the match"),
    (
        ("round 186: the candle burns twice as long at night", "key"),
        "bssxh 186: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 186: the candle burns twice as long at night", "lemon"),
        "csgbq 186: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 186: the candle burns twice as long at night", "a"), "round 186: the candle burns twice as long at night"),
    (
        ("round 186: the candle burns twice as long at night", "zz"),
        "qntmc 186: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 186: the candle burns twice as long at night", "AgentU"),
        "ruyaw 186: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 186: the candle burns twice as long at night", "keyboard"),
        "bssor 186: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 186: the candle burns twice as long at night", "AA"),
        "round 186: the candle burns twice as long at night",
    ),
    (("round 186: a mirror of the universe in one line", "key"), "bssxh 186: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 186: a mirror of the universe in one line", "lemon"), "csgbq 186: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 186: a mirror of the universe in one line", "a"), "round 186: a mirror of the universe in one line"),
    (("round 186: a mirror of the universe in one line", "zz"), "qntmc 186: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 186: a mirror of the universe in one line", "AgentU"), "ruyaw 186: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 186: a mirror of the universe in one line", "keyboard"),
        "bssor 186: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 186: a mirror of the universe in one line", "AA"), "round 186: a mirror of the universe in one line"),
    (("round 186: the queue drains before the storm", "key"), "bssxh 186: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 186: the queue drains before the storm", "lemon"), "csgbq 186: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 186: the queue drains before the storm", "a"), "round 186: the queue drains before the storm"),
    (("round 186: the queue drains before the storm", "zz"), "qntmc 186: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 186: the queue drains before the storm", "AgentU"), "ruyaw 186: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 186: the queue drains before the storm", "keyboard"), "bssor 186: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 186: the queue drains before the storm", "AA"), "round 186: the queue drains before the storm"),
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
