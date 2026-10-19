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
    (("kitten175", "key"), "umrdil175"),
    (("kitten175", "lemon"), "vmfhry175"),
    (("kitten175", "a"), "kitten175"),
    (("kitten175", "zz"), "jhssdm175"),
    (("kitten175", "AgentU"), "koxgxh175"),
    (("kitten175", "keyboard"), "umrusn175"),
    (("kitten175", "AA"), "kitten175"),
    (("sitting175", "key"), "cmrdmlq175"),
    (("sitting175", "lemon"), "dmfhvyk175"),
    (("sitting175", "a"), "sitting175"),
    (("sitting175", "zz"), "rhsshmf175"),
    (("sitting175", "AgentU"), "soxgbhg175"),
    (("sitting175", "keyboard"), "cmruwnx175"),
    (("sitting175", "AA"), "sitting175"),
    (("agent175", "key"), "kkcxx175"),
    (("agent175", "lemon"), "lkqbg175"),
    (("agent175", "a"), "agent175"),
    (("agent175", "zz"), "zfdms175"),
    (("agent175", "AgentU"), "amiam175"),
    (("agent175", "keyboard"), "kkcoh175"),
    (("agent175", "AA"), "agent175"),
    (("angle175", "key"), "krevi175"),
    (("angle175", "lemon"), "lrszr175"),
    (("angle175", "a"), "angle175"),
    (("angle175", "zz"), "zmfkd175"),
    (("angle175", "AgentU"), "atkyx175"),
    (("angle175", "keyboard"), "krems175"),
    (("angle175", "AA"), "angle175"),
    (("universe175", "key"), "ergfipci175"),
    (("universe175", "lemon"), "frujrcwq175"),
    (("universe175", "a"), "universe175"),
    (("universe175", "zz"), "tmhudqrd175"),
    (("universe175", "AgentU"), "utmixlsk175"),
    (("universe175", "keyboard"), "ergwsrjh175"),
    (("universe175", "AA"), "universe175"),
    (("memory175", "key"), "wikyvw175"),
    (("memory175", "lemon"), "xiycej175"),
    (("memory175", "a"), "memory175"),
    (("memory175", "zz"), "ldlnqx175"),
    (("memory175", "AgentU"), "mkqbks175"),
    (("memory175", "keyboard"), "wikpfy175"),
    (("memory175", "AA"), "memory175"),
    (("stream175", "key"), "cxpoek175"),
    (("stream175", "lemon"), "dxdsnx175"),
    (("stream175", "a"), "stream175"),
    (("stream175", "zz"), "rsqdzl175"),
    (("stream175", "AgentU"), "szvrtg175"),
    (("stream175", "keyboard"), "cxpfom175"),
    (("stream175", "AA"), "stream175"),
    (("context175", "key"), "msldivd175"),
    (("context175", "lemon"), "nszhrix175"),
    (("context175", "a"), "context175"),
    (("context175", "zz"), "bnmsdws175"),
    (("context175", "AgentU"), "curgxrt175"),
    (("context175", "keyboard"), "mslusxk175"),
    (("context175", "AA"), "context175"),
    (("knowledge175", "key"), "urmgpcnkc175"),
    (("knowledge175", "lemon"), "vrakyphss175"),
    (("knowledge175", "a"), "knowledge175"),
    (("knowledge175", "zz"), "jmnvkdcfd175"),
    (("knowledge175", "AgentU"), "ktsjeydmi175"),
    (("knowledge175", "keyboard"), "urmxzeujo175"),
    (("knowledge175", "AA"), "knowledge175"),
    (("vector175", "key"), "fiadsp175"),
    (("vector175", "lemon"), "giohbc175"),
    (("vector175", "a"), "vector175"),
    (("vector175", "zz"), "udbsnq175"),
    (("vector175", "AgentU"), "vkgghl175"),
    (("vector175", "keyboard"), "fiaucr175"),
    (("vector175", "AA"), "vector175"),
    (("processor175", "key"), "zvmmiqcsp175"),
    (("processor175", "lemon"), "avaqrdwaf175"),
    (("processor175", "a"), "processor175"),
    (("processor175", "zz"), "oqnbdrrnq175"),
    (("processor175", "AgentU"), "pxspxmsuv175"),
    (("processor175", "keyboard"), "zvmdssjrb175"),
    (("processor175", "AA"), "processor175"),
    (("reasoning175", "key"), "biycslsre175"),
    (("reasoning175", "lemon"), "cimgbymzu175"),
    (("reasoning175", "a"), "reasoning175"),
    (("reasoning175", "zz"), "qdzrnmhmf175"),
    (("reasoning175", "AgentU"), "rkefhhitk175"),
    (("reasoning175", "keyboard"), "biytcnzqq175"),
    (("reasoning175", "AA"), "reasoning175"),
    (("machine175", "key"), "wearmlo175"),
    (("machine175", "lemon"), "xeovvyi175"),
    (("machine175", "a"), "machine175"),
    (("machine175", "zz"), "lzbghmd175"),
    (("machine175", "AgentU"), "mggubhe175"),
    (("machine175", "keyboard"), "weaiwnv175"),
    (("machine175", "AA"), "machine175"),
    (("learning175", "key"), "viybrgxk175"),
    (("learning175", "lemon"), "wimfatrs175"),
    (("learning175", "a"), "learning175"),
    (("learning175", "zz"), "kdzqmhmf175"),
    (("learning175", "AgentU"), "lkeegcnm175"),
    (("learning175", "keyboard"), "viysbiej175"),
    (("learning175", "AA"), "learning175"),
    (("model175", "key"), "wsbop175"),
    (("model175", "lemon"), "xspsy175"),
    (("model175", "a"), "model175"),
    (("model175", "zz"), "lncdk175"),
    (("model175", "AgentU"), "muhre175"),
    (("model175", "keyboard"), "wsbfz175"),
    (("model175", "AA"), "model175"),
    (("token175", "key"), "dsior175"),
    (("token175", "lemon"), "eswsa175"),
    (("token175", "a"), "token175"),
    (("token175", "zz"), "snjdm175"),
    (("token175", "AgentU"), "tuorg175"),
    (("token175", "keyboard"), "dsifb175"),
    (("token175", "AA"), "token175"),
    (("prompt175", "key"), "zvmwtr175"),
    (("prompt175", "lemon"), "avaace175"),
    (("prompt175", "a"), "prompt175"),
    (("prompt175", "zz"), "oqnlos175"),
    (("prompt175", "AgentU"), "pxszin175"),
    (("prompt175", "keyboard"), "zvmndt175"),
    (("prompt175", "AA"), "prompt175"),
    (("session175", "key"), "ciqcmmx175"),
    (("session175", "lemon"), "diegvzr175"),
    (("session175", "a"), "session175"),
    (("session175", "zz"), "rdrrhnm175"),
    (("session175", "AgentU"), "skwfbin175"),
    (("session175", "keyboard"), "ciqtwoe175"),
    (("session175", "AA"), "session175"),
    (("library175", "key"), "vmzbepi175"),
    (("library175", "lemon"), "wmnfncc175"),
    (("library175", "a"), "library175"),
    (("library175", "zz"), "khaqzqx175"),
    (("library175", "AgentU"), "lofetly175"),
    (("library175", "keyboard"), "vmzsorp175"),
    (("library175", "AA"), "library175"),
    (("service175", "key"), "cipfmao175"),
    (("service175", "lemon"), "didjvni175"),
    (("service175", "a"), "service175"),
    (("service175", "zz"), "rdquhbd175"),
    (("service175", "AgentU"), "skvibwe175"),
    (("service175", "keyboard"), "cipwwcv175"),
    (("service175", "AA"), "service175"),
    (("gateway175", "key"), "qeroayi175"),
    (("gateway175", "lemon"), "refsjlc175"),
    (("gateway175", "a"), "gateway175"),
    (("gateway175", "zz"), "fzsdvzx175"),
    (("gateway175", "AgentU"), "ggxrpuy175"),
    (("gateway175", "keyboard"), "qerfkap175"),
    (("gateway175", "AA"), "gateway175"),
    (("storage175", "key"), "cxmbeeo175"),
    (("storage175", "lemon"), "dxafnri175"),
    (("storage175", "a"), "storage175"),
    (("storage175", "zz"), "rsnqzfd175"),
    (("storage175", "AgentU"), "szsetae175"),
    (("storage175", "keyboard"), "cxmsogv175"),
    (("storage175", "AA"), "storage175"),
    (("network175", "key"), "xirgspu175"),
    (("network175", "lemon"), "yifkbco175"),
    (("network175", "a"), "network175"),
    (("network175", "zz"), "mdsvnqj175"),
    (("network175", "AgentU"), "nkxjhlk175"),
    (("network175", "keyboard"), "xirxcrb175"),
    (("network175", "AA"), "network175"),
    (("latency175", "key"), "verorai175"),
    (("latency175", "lemon"), "wefsanc175"),
    (("latency175", "a"), "latency175"),
    (("latency175", "zz"), "kzsdmbx175"),
    (("latency175", "AgentU"), "lgxrgwy175"),
    (("latency175", "keyboard"), "verfbcp175"),
    (("latency175", "AA"), "latency175"),
    (("buffer175", "key"), "lydpip175"),
    (("buffer175", "lemon"), "myrtrc175"),
    (("buffer175", "a"), "buffer175"),
    (("buffer175", "zz"), "ateedq175"),
    (("buffer175", "AgentU"), "bajsxl175"),
    (("buffer175", "keyboard"), "lydgsr175"),
    (("buffer175", "AA"), "buffer175"),
    (("queue175", "key"), "aycei175"),
    (("queue175", "lemon"), "byqir175"),
    (("queue175", "a"), "queue175"),
    (("queue175", "zz"), "ptdtd175"),
    (("queue175", "AgentU"), "qaihx175"),
    (("queue175", "keyboard"), "aycvs175"),
    (("queue175", "AA"), "queue175"),
    (("worker175", "key"), "gspuip175"),
    (("worker175", "lemon"), "hsdyrc175"),
    (("worker175", "a"), "worker175"),
    (("worker175", "zz"), "vnqjdq175"),
    (("worker175", "AgentU"), "wuvxxl175"),
    (("worker175", "keyboard"), "gsplsr175"),
    (("worker175", "AA"), "worker175"),
    (("kernel175", "key"), "uipxij175"),
    (("kernel175", "lemon"), "vidbrw175"),
    (("kernel175", "a"), "kernel175"),
    (("kernel175", "zz"), "jdqmdk175"),
    (("kernel175", "AgentU"), "kkvaxf175"),
    (("kernel175", "keyboard"), "uiposl175"),
    (("kernel175", "AA"), "kernel175"),
    (("signal175", "key"), "cmexej175"),
    (("signal175", "lemon"), "dmsbnw175"),
    (("signal175", "a"), "signal175"),
    (("signal175", "zz"), "rhfmzk175"),
    (("signal175", "AgentU"), "sokatf175"),
    (("signal175", "keyboard"), "cmeool175"),
    (("signal175", "AA"), "signal175"),
    (("packet175", "key"), "zeauir175"),
    (("packet175", "lemon"), "aeoyre175"),
    (("packet175", "a"), "packet175"),
    (("packet175", "zz"), "ozbjds175"),
    (("packet175", "AgentU"), "pggxxn175"),
    (("packet175", "keyboard"), "zealst175"),
    (("packet175", "AA"), "packet175"),
    (("router175", "key"), "bssdip175"),
    (("router175", "lemon"), "csghrc175"),
    (("router175", "a"), "router175"),
    (("router175", "zz"), "qntsdq175"),
    (("router175", "AgentU"), "ruygxl175"),
    (("router175", "keyboard"), "bssusr175"),
    (("router175", "AA"), "router175"),
    (("cluster175", "key"), "mpscxcb175"),
    (("cluster175", "lemon"), "npgggpv175"),
    (("cluster175", "a"), "cluster175"),
    (("cluster175", "zz"), "bktrsdq175"),
    (("cluster175", "AgentU"), "cryfmyr175"),
    (("cluster175", "keyboard"), "mpsthei175"),
    (("cluster175", "AA"), "cluster175"),
    (("mirror175", "key"), "wmpbsp175"),
    (("mirror175", "lemon"), "xmdfbc175"),
    (("mirror175", "a"), "mirror175"),
    (("mirror175", "zz"), "lhqqnq175"),
    (("mirror175", "AgentU"), "movehl175"),
    (("mirror175", "keyboard"), "wmpscr175"),
    (("mirror175", "AA"), "mirror175"),
    (("filter175", "key"), "pmjdip175"),
    (("filter175", "lemon"), "qmxhrc175"),
    (("filter175", "a"), "filter175"),
    (("filter175", "zz"), "ehksdq175"),
    (("filter175", "AgentU"), "fopgxl175"),
    (("filter175", "keyboard"), "pmjusr175"),
    (("filter175", "AA"), "filter175"),
    (("ranking175", "key"), "belumlq175"),
    (("ranking175", "lemon"), "cezyvyk175"),
    (("ranking175", "a"), "ranking175"),
    (("ranking175", "zz"), "qzmjhmf175"),
    (("ranking175", "AgentU"), "rgrxbhg175"),
    (("ranking175", "keyboard"), "bellwnx175"),
    (("ranking175", "AA"), "ranking175"),
    (("encoding175", "key"), "orayhgxk175"),
    (("encoding175", "lemon"), "procqtrs175"),
    (("encoding175", "a"), "encoding175"),
    (("encoding175", "zz"), "dmbnchmf175"),
    (("encoding175", "AgentU"), "etgbwcnm175"),
    (("encoding175", "keyboard"), "orapriej175"),
    (("encoding175", "AA"), "encoding175"),
    (("mapping175", "key"), "wenzmlq175"),
    (("mapping175", "lemon"), "xebdvyk175"),
    (("mapping175", "a"), "mapping175"),
    (("mapping175", "zz"), "lzoohmf175"),
    (("mapping175", "AgentU"), "mgtcbhg175"),
    (("mapping175", "keyboard"), "wenqwnx175"),
    (("mapping175", "AA"), "mapping175"),
    (("record175", "key"), "biayvb175"),
    (("record175", "lemon"), "cioceo175"),
    (("record175", "a"), "record175"),
    (("record175", "zz"), "qdbnqc175"),
    (("record175", "AgentU"), "rkgbkx175"),
    (("record175", "keyboard"), "biapfd175"),
    (("record175", "AA"), "record175"),
    (("candle175", "key"), "melnpc175"),
    (("candle175", "lemon"), "nezryp175"),
    (("candle175", "a"), "candle175"),
    (("candle175", "zz"), "bzmckd175"),
    (("candle175", "AgentU"), "cgrqey175"),
    (("candle175", "keyboard"), "meleze175"),
    (("candle175", "AA"), "candle175"),
    (("thread175", "key"), "dlpoeb175"),
    (("thread175", "lemon"), "eldsno175"),
    (("thread175", "a"), "thread175"),
    (("thread175", "zz"), "sgqdzc175"),
    (("thread175", "AgentU"), "tnvrtx175"),
    (("thread175", "keyboard"), "dlpfod175"),
    (("thread175", "AA"), "thread175"),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 175: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 175: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "a"),
        "round 175: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 175: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 175: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 175: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", "AA"),
        "round 175: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "key"),
        "bssxh 175: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 175: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "a"),
        "round 175: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 175: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 175: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 175: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", "AA"),
        "round 175: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 175: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 175: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "a"),
        "round 175: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 175: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 175: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 175: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", "AA"),
        "round 175: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 175: the processor reads the record then stops", "key"),
        "bssxh 175: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 175: the processor reads the record then stops", "lemon"),
        "csgbq 175: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 175: the processor reads the record then stops", "a"),
        "round 175: the processor reads the record then stops",
    ),
    (
        ("round 175: the processor reads the record then stops", "zz"),
        "qntmc 175: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 175: the processor reads the record then stops", "AgentU"),
        "ruyaw 175: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 175: the processor reads the record then stops", "keyboard"),
        "bssor 175: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 175: the processor reads the record then stops", "AA"),
        "round 175: the processor reads the record then stops",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "key"),
        "bssxh 175: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "lemon"),
        "csgbq 175: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "a"),
        "round 175: a worker pulls the next task from the queue",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "zz"),
        "qntmc 175: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 175: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "keyboard"),
        "bssor 175: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 175: a worker pulls the next task from the queue", "AA"),
        "round 175: a worker pulls the next task from the queue",
    ),
    (
        ("round 175: signals travel through the network layer", "key"),
        "bssxh 175: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 175: signals travel through the network layer", "lemon"),
        "csgbq 175: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 175: signals travel through the network layer", "a"),
        "round 175: signals travel through the network layer",
    ),
    (
        ("round 175: signals travel through the network layer", "zz"),
        "qntmc 175: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 175: signals travel through the network layer", "AgentU"),
        "ruyaw 175: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 175: signals travel through the network layer", "keyboard"),
        "bssor 175: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 175: signals travel through the network layer", "AA"),
        "round 175: signals travel through the network layer",
    ),
    (
        ("round 175: the gateway routes each request by policy", "key"),
        "bssxh 175: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 175: the gateway routes each request by policy", "lemon"),
        "csgbq 175: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 175: the gateway routes each request by policy", "a"),
        "round 175: the gateway routes each request by policy",
    ),
    (
        ("round 175: the gateway routes each request by policy", "zz"),
        "qntmc 175: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 175: the gateway routes each request by policy", "AgentU"),
        "ruyaw 175: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 175: the gateway routes each request by policy", "keyboard"),
        "bssor 175: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 175: the gateway routes each request by policy", "AA"),
        "round 175: the gateway routes each request by policy",
    ),
    (("round 175: memory grows until the buffer is full", "key"), "bssxh 175: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 175: memory grows until the buffer is full", "lemon"), "csgbq 175: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 175: memory grows until the buffer is full", "a"), "round 175: memory grows until the buffer is full"),
    (("round 175: memory grows until the buffer is full", "zz"), "qntmc 175: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 175: memory grows until the buffer is full", "AgentU"),
        "ruyaw 175: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 175: memory grows until the buffer is full", "keyboard"),
        "bssor 175: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 175: memory grows until the buffer is full", "AA"), "round 175: memory grows until the buffer is full"),
    (("round 175: the cluster mirrors every packet twice", "key"), "bssxh 175: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 175: the cluster mirrors every packet twice", "lemon"),
        "csgbq 175: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 175: the cluster mirrors every packet twice", "a"), "round 175: the cluster mirrors every packet twice"),
    (("round 175: the cluster mirrors every packet twice", "zz"), "qntmc 175: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 175: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 175: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 175: the cluster mirrors every packet twice", "keyboard"),
        "bssor 175: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 175: the cluster mirrors every packet twice", "AA"), "round 175: the cluster mirrors every packet twice"),
    (
        ("round 175: ranking uses tokens learned from the corpus", "key"),
        "bssxh 175: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 175: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", "a"),
        "round 175: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 175: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 175: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 175: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", "AA"),
        "round 175: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 175: a long session ends when the candle dies", "key"),
        "bssxh 175: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 175: a long session ends when the candle dies", "lemon"),
        "csgbq 175: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 175: a long session ends when the candle dies", "a"),
        "round 175: a long session ends when the candle dies",
    ),
    (
        ("round 175: a long session ends when the candle dies", "zz"),
        "qntmc 175: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 175: a long session ends when the candle dies", "AgentU"),
        "ruyaw 175: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 175: a long session ends when the candle dies", "keyboard"),
        "bssor 175: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 175: a long session ends when the candle dies", "AA"),
        "round 175: a long session ends when the candle dies",
    ),
    (("round 175: encode the prompt then map the result", "key"), "bssxh 175: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 175: encode the prompt then map the result", "lemon"), "csgbq 175: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 175: encode the prompt then map the result", "a"), "round 175: encode the prompt then map the result"),
    (("round 175: encode the prompt then map the result", "zz"), "qntmc 175: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 175: encode the prompt then map the result", "AgentU"),
        "ruyaw 175: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 175: encode the prompt then map the result", "keyboard"),
        "bssor 175: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 175: encode the prompt then map the result", "AA"), "round 175: encode the prompt then map the result"),
    (("round 175: the kernel wakes the worker at dawn", "key"), "bssxh 175: rri iovlop ukocc xfo ambocb er neux"),
    (("round 175: the kernel wakes the worker at dawn", "lemon"), "csgbq 175: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 175: the kernel wakes the worker at dawn", "a"), "round 175: the kernel wakes the worker at dawn"),
    (("round 175: the kernel wakes the worker at dawn", "zz"), "qntmc 175: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 175: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 175: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 175: the kernel wakes the worker at dawn", "keyboard"), "bssor 175: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 175: the kernel wakes the worker at dawn", "AA"), "round 175: the kernel wakes the worker at dawn"),
    (("round 175: service latency drops after the patch", "key"), "bssxh 175: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 175: service latency drops after the patch", "lemon"), "csgbq 175: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 175: service latency drops after the patch", "a"), "round 175: service latency drops after the patch"),
    (("round 175: service latency drops after the patch", "zz"), "qntmc 175: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 175: service latency drops after the patch", "AgentU"),
        "ruyaw 175: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 175: service latency drops after the patch", "keyboard"),
        "bssor 175: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 175: service latency drops after the patch", "AA"), "round 175: service latency drops after the patch"),
    (
        ("round 175: the library caches every vector it sees", "key"),
        "bssxh 175: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 175: the library caches every vector it sees", "lemon"),
        "csgbq 175: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 175: the library caches every vector it sees", "a"), "round 175: the library caches every vector it sees"),
    (
        ("round 175: the library caches every vector it sees", "zz"),
        "qntmc 175: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 175: the library caches every vector it sees", "AgentU"),
        "ruyaw 175: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 175: the library caches every vector it sees", "keyboard"),
        "bssor 175: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 175: the library caches every vector it sees", "AA"),
        "round 175: the library caches every vector it sees",
    ),
    (("round 175: agents argue then the debate resolves", "key"), "bssxh 175: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 175: agents argue then the debate resolves", "lemon"), "csgbq 175: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 175: agents argue then the debate resolves", "a"), "round 175: agents argue then the debate resolves"),
    (("round 175: agents argue then the debate resolves", "zz"), "qntmc 175: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 175: agents argue then the debate resolves", "AgentU"),
        "ruyaw 175: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 175: agents argue then the debate resolves", "keyboard"),
        "bssor 175: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 175: agents argue then the debate resolves", "AA"), "round 175: agents argue then the debate resolves"),
    (("round 175: the filter keeps only strong matches", "key"), "bssxh 175: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 175: the filter keeps only strong matches", "lemon"), "csgbq 175: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 175: the filter keeps only strong matches", "a"), "round 175: the filter keeps only strong matches"),
    (("round 175: the filter keeps only strong matches", "zz"), "qntmc 175: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 175: the filter keeps only strong matches", "AgentU"), "ruyaw 175: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 175: the filter keeps only strong matches", "keyboard"),
        "bssor 175: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 175: the filter keeps only strong matches", "AA"), "round 175: the filter keeps only strong matches"),
    (("round 175: the model answers with a short reply", "key"), "bssxh 175: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 175: the model answers with a short reply", "lemon"), "csgbq 175: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 175: the model answers with a short reply", "a"), "round 175: the model answers with a short reply"),
    (("round 175: the model answers with a short reply", "zz"), "qntmc 175: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 175: the model answers with a short reply", "AgentU"), "ruyaw 175: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 175: the model answers with a short reply", "keyboard"),
        "bssor 175: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 175: the model answers with a short reply", "AA"), "round 175: the model answers with a short reply"),
    (
        ("round 175: the recorder stores the reasoning trace", "key"),
        "bssxh 175: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 175: the recorder stores the reasoning trace", "lemon"),
        "csgbq 175: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 175: the recorder stores the reasoning trace", "a"), "round 175: the recorder stores the reasoning trace"),
    (
        ("round 175: the recorder stores the reasoning trace", "zz"),
        "qntmc 175: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 175: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 175: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 175: the recorder stores the reasoning trace", "keyboard"),
        "bssor 175: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 175: the recorder stores the reasoning trace", "AA"),
        "round 175: the recorder stores the reasoning trace",
    ),
    (("round 175: the angel watches the processor run", "key"), "bssxh 175: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 175: the angel watches the processor run", "lemon"), "csgbq 175: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 175: the angel watches the processor run", "a"), "round 175: the angel watches the processor run"),
    (("round 175: the angel watches the processor run", "zz"), "qntmc 175: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 175: the angel watches the processor run", "AgentU"), "ruyaw 175: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 175: the angel watches the processor run", "keyboard"), "bssor 175: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 175: the angel watches the processor run", "AA"), "round 175: the angel watches the processor run"),
    (("round 175: angle of the vector decides the match", "key"), "bssxh 175: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 175: angle of the vector decides the match", "lemon"), "csgbq 175: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 175: angle of the vector decides the match", "a"), "round 175: angle of the vector decides the match"),
    (("round 175: angle of the vector decides the match", "zz"), "qntmc 175: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 175: angle of the vector decides the match", "AgentU"),
        "ruyaw 175: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 175: angle of the vector decides the match", "keyboard"),
        "bssor 175: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 175: angle of the vector decides the match", "AA"), "round 175: angle of the vector decides the match"),
    (
        ("round 175: the candle burns twice as long at night", "key"),
        "bssxh 175: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 175: the candle burns twice as long at night", "lemon"),
        "csgbq 175: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 175: the candle burns twice as long at night", "a"), "round 175: the candle burns twice as long at night"),
    (
        ("round 175: the candle burns twice as long at night", "zz"),
        "qntmc 175: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 175: the candle burns twice as long at night", "AgentU"),
        "ruyaw 175: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 175: the candle burns twice as long at night", "keyboard"),
        "bssor 175: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 175: the candle burns twice as long at night", "AA"),
        "round 175: the candle burns twice as long at night",
    ),
    (("round 175: a mirror of the universe in one line", "key"), "bssxh 175: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 175: a mirror of the universe in one line", "lemon"), "csgbq 175: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 175: a mirror of the universe in one line", "a"), "round 175: a mirror of the universe in one line"),
    (("round 175: a mirror of the universe in one line", "zz"), "qntmc 175: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 175: a mirror of the universe in one line", "AgentU"), "ruyaw 175: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 175: a mirror of the universe in one line", "keyboard"),
        "bssor 175: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 175: a mirror of the universe in one line", "AA"), "round 175: a mirror of the universe in one line"),
    (("round 175: the queue drains before the storm", "key"), "bssxh 175: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 175: the queue drains before the storm", "lemon"), "csgbq 175: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 175: the queue drains before the storm", "a"), "round 175: the queue drains before the storm"),
    (("round 175: the queue drains before the storm", "zz"), "qntmc 175: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 175: the queue drains before the storm", "AgentU"), "ruyaw 175: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 175: the queue drains before the storm", "keyboard"), "bssor 175: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 175: the queue drains before the storm", "AA"), "round 175: the queue drains before the storm"),
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
