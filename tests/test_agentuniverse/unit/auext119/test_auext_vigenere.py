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
    (("kitten119", "key"), "umrdil119"),
    (("kitten119", "lemon"), "vmfhry119"),
    (("kitten119", "a"), "kitten119"),
    (("kitten119", "zz"), "jhssdm119"),
    (("kitten119", "AgentU"), "koxgxh119"),
    (("kitten119", "keyboard"), "umrusn119"),
    (("kitten119", "AA"), "kitten119"),
    (("sitting119", "key"), "cmrdmlq119"),
    (("sitting119", "lemon"), "dmfhvyk119"),
    (("sitting119", "a"), "sitting119"),
    (("sitting119", "zz"), "rhsshmf119"),
    (("sitting119", "AgentU"), "soxgbhg119"),
    (("sitting119", "keyboard"), "cmruwnx119"),
    (("sitting119", "AA"), "sitting119"),
    (("agent119", "key"), "kkcxx119"),
    (("agent119", "lemon"), "lkqbg119"),
    (("agent119", "a"), "agent119"),
    (("agent119", "zz"), "zfdms119"),
    (("agent119", "AgentU"), "amiam119"),
    (("agent119", "keyboard"), "kkcoh119"),
    (("agent119", "AA"), "agent119"),
    (("angle119", "key"), "krevi119"),
    (("angle119", "lemon"), "lrszr119"),
    (("angle119", "a"), "angle119"),
    (("angle119", "zz"), "zmfkd119"),
    (("angle119", "AgentU"), "atkyx119"),
    (("angle119", "keyboard"), "krems119"),
    (("angle119", "AA"), "angle119"),
    (("universe119", "key"), "ergfipci119"),
    (("universe119", "lemon"), "frujrcwq119"),
    (("universe119", "a"), "universe119"),
    (("universe119", "zz"), "tmhudqrd119"),
    (("universe119", "AgentU"), "utmixlsk119"),
    (("universe119", "keyboard"), "ergwsrjh119"),
    (("universe119", "AA"), "universe119"),
    (("memory119", "key"), "wikyvw119"),
    (("memory119", "lemon"), "xiycej119"),
    (("memory119", "a"), "memory119"),
    (("memory119", "zz"), "ldlnqx119"),
    (("memory119", "AgentU"), "mkqbks119"),
    (("memory119", "keyboard"), "wikpfy119"),
    (("memory119", "AA"), "memory119"),
    (("stream119", "key"), "cxpoek119"),
    (("stream119", "lemon"), "dxdsnx119"),
    (("stream119", "a"), "stream119"),
    (("stream119", "zz"), "rsqdzl119"),
    (("stream119", "AgentU"), "szvrtg119"),
    (("stream119", "keyboard"), "cxpfom119"),
    (("stream119", "AA"), "stream119"),
    (("context119", "key"), "msldivd119"),
    (("context119", "lemon"), "nszhrix119"),
    (("context119", "a"), "context119"),
    (("context119", "zz"), "bnmsdws119"),
    (("context119", "AgentU"), "curgxrt119"),
    (("context119", "keyboard"), "mslusxk119"),
    (("context119", "AA"), "context119"),
    (("knowledge119", "key"), "urmgpcnkc119"),
    (("knowledge119", "lemon"), "vrakyphss119"),
    (("knowledge119", "a"), "knowledge119"),
    (("knowledge119", "zz"), "jmnvkdcfd119"),
    (("knowledge119", "AgentU"), "ktsjeydmi119"),
    (("knowledge119", "keyboard"), "urmxzeujo119"),
    (("knowledge119", "AA"), "knowledge119"),
    (("vector119", "key"), "fiadsp119"),
    (("vector119", "lemon"), "giohbc119"),
    (("vector119", "a"), "vector119"),
    (("vector119", "zz"), "udbsnq119"),
    (("vector119", "AgentU"), "vkgghl119"),
    (("vector119", "keyboard"), "fiaucr119"),
    (("vector119", "AA"), "vector119"),
    (("processor119", "key"), "zvmmiqcsp119"),
    (("processor119", "lemon"), "avaqrdwaf119"),
    (("processor119", "a"), "processor119"),
    (("processor119", "zz"), "oqnbdrrnq119"),
    (("processor119", "AgentU"), "pxspxmsuv119"),
    (("processor119", "keyboard"), "zvmdssjrb119"),
    (("processor119", "AA"), "processor119"),
    (("reasoning119", "key"), "biycslsre119"),
    (("reasoning119", "lemon"), "cimgbymzu119"),
    (("reasoning119", "a"), "reasoning119"),
    (("reasoning119", "zz"), "qdzrnmhmf119"),
    (("reasoning119", "AgentU"), "rkefhhitk119"),
    (("reasoning119", "keyboard"), "biytcnzqq119"),
    (("reasoning119", "AA"), "reasoning119"),
    (("machine119", "key"), "wearmlo119"),
    (("machine119", "lemon"), "xeovvyi119"),
    (("machine119", "a"), "machine119"),
    (("machine119", "zz"), "lzbghmd119"),
    (("machine119", "AgentU"), "mggubhe119"),
    (("machine119", "keyboard"), "weaiwnv119"),
    (("machine119", "AA"), "machine119"),
    (("learning119", "key"), "viybrgxk119"),
    (("learning119", "lemon"), "wimfatrs119"),
    (("learning119", "a"), "learning119"),
    (("learning119", "zz"), "kdzqmhmf119"),
    (("learning119", "AgentU"), "lkeegcnm119"),
    (("learning119", "keyboard"), "viysbiej119"),
    (("learning119", "AA"), "learning119"),
    (("model119", "key"), "wsbop119"),
    (("model119", "lemon"), "xspsy119"),
    (("model119", "a"), "model119"),
    (("model119", "zz"), "lncdk119"),
    (("model119", "AgentU"), "muhre119"),
    (("model119", "keyboard"), "wsbfz119"),
    (("model119", "AA"), "model119"),
    (("token119", "key"), "dsior119"),
    (("token119", "lemon"), "eswsa119"),
    (("token119", "a"), "token119"),
    (("token119", "zz"), "snjdm119"),
    (("token119", "AgentU"), "tuorg119"),
    (("token119", "keyboard"), "dsifb119"),
    (("token119", "AA"), "token119"),
    (("prompt119", "key"), "zvmwtr119"),
    (("prompt119", "lemon"), "avaace119"),
    (("prompt119", "a"), "prompt119"),
    (("prompt119", "zz"), "oqnlos119"),
    (("prompt119", "AgentU"), "pxszin119"),
    (("prompt119", "keyboard"), "zvmndt119"),
    (("prompt119", "AA"), "prompt119"),
    (("session119", "key"), "ciqcmmx119"),
    (("session119", "lemon"), "diegvzr119"),
    (("session119", "a"), "session119"),
    (("session119", "zz"), "rdrrhnm119"),
    (("session119", "AgentU"), "skwfbin119"),
    (("session119", "keyboard"), "ciqtwoe119"),
    (("session119", "AA"), "session119"),
    (("library119", "key"), "vmzbepi119"),
    (("library119", "lemon"), "wmnfncc119"),
    (("library119", "a"), "library119"),
    (("library119", "zz"), "khaqzqx119"),
    (("library119", "AgentU"), "lofetly119"),
    (("library119", "keyboard"), "vmzsorp119"),
    (("library119", "AA"), "library119"),
    (("service119", "key"), "cipfmao119"),
    (("service119", "lemon"), "didjvni119"),
    (("service119", "a"), "service119"),
    (("service119", "zz"), "rdquhbd119"),
    (("service119", "AgentU"), "skvibwe119"),
    (("service119", "keyboard"), "cipwwcv119"),
    (("service119", "AA"), "service119"),
    (("gateway119", "key"), "qeroayi119"),
    (("gateway119", "lemon"), "refsjlc119"),
    (("gateway119", "a"), "gateway119"),
    (("gateway119", "zz"), "fzsdvzx119"),
    (("gateway119", "AgentU"), "ggxrpuy119"),
    (("gateway119", "keyboard"), "qerfkap119"),
    (("gateway119", "AA"), "gateway119"),
    (("storage119", "key"), "cxmbeeo119"),
    (("storage119", "lemon"), "dxafnri119"),
    (("storage119", "a"), "storage119"),
    (("storage119", "zz"), "rsnqzfd119"),
    (("storage119", "AgentU"), "szsetae119"),
    (("storage119", "keyboard"), "cxmsogv119"),
    (("storage119", "AA"), "storage119"),
    (("network119", "key"), "xirgspu119"),
    (("network119", "lemon"), "yifkbco119"),
    (("network119", "a"), "network119"),
    (("network119", "zz"), "mdsvnqj119"),
    (("network119", "AgentU"), "nkxjhlk119"),
    (("network119", "keyboard"), "xirxcrb119"),
    (("network119", "AA"), "network119"),
    (("latency119", "key"), "verorai119"),
    (("latency119", "lemon"), "wefsanc119"),
    (("latency119", "a"), "latency119"),
    (("latency119", "zz"), "kzsdmbx119"),
    (("latency119", "AgentU"), "lgxrgwy119"),
    (("latency119", "keyboard"), "verfbcp119"),
    (("latency119", "AA"), "latency119"),
    (("buffer119", "key"), "lydpip119"),
    (("buffer119", "lemon"), "myrtrc119"),
    (("buffer119", "a"), "buffer119"),
    (("buffer119", "zz"), "ateedq119"),
    (("buffer119", "AgentU"), "bajsxl119"),
    (("buffer119", "keyboard"), "lydgsr119"),
    (("buffer119", "AA"), "buffer119"),
    (("queue119", "key"), "aycei119"),
    (("queue119", "lemon"), "byqir119"),
    (("queue119", "a"), "queue119"),
    (("queue119", "zz"), "ptdtd119"),
    (("queue119", "AgentU"), "qaihx119"),
    (("queue119", "keyboard"), "aycvs119"),
    (("queue119", "AA"), "queue119"),
    (("worker119", "key"), "gspuip119"),
    (("worker119", "lemon"), "hsdyrc119"),
    (("worker119", "a"), "worker119"),
    (("worker119", "zz"), "vnqjdq119"),
    (("worker119", "AgentU"), "wuvxxl119"),
    (("worker119", "keyboard"), "gsplsr119"),
    (("worker119", "AA"), "worker119"),
    (("kernel119", "key"), "uipxij119"),
    (("kernel119", "lemon"), "vidbrw119"),
    (("kernel119", "a"), "kernel119"),
    (("kernel119", "zz"), "jdqmdk119"),
    (("kernel119", "AgentU"), "kkvaxf119"),
    (("kernel119", "keyboard"), "uiposl119"),
    (("kernel119", "AA"), "kernel119"),
    (("signal119", "key"), "cmexej119"),
    (("signal119", "lemon"), "dmsbnw119"),
    (("signal119", "a"), "signal119"),
    (("signal119", "zz"), "rhfmzk119"),
    (("signal119", "AgentU"), "sokatf119"),
    (("signal119", "keyboard"), "cmeool119"),
    (("signal119", "AA"), "signal119"),
    (("packet119", "key"), "zeauir119"),
    (("packet119", "lemon"), "aeoyre119"),
    (("packet119", "a"), "packet119"),
    (("packet119", "zz"), "ozbjds119"),
    (("packet119", "AgentU"), "pggxxn119"),
    (("packet119", "keyboard"), "zealst119"),
    (("packet119", "AA"), "packet119"),
    (("router119", "key"), "bssdip119"),
    (("router119", "lemon"), "csghrc119"),
    (("router119", "a"), "router119"),
    (("router119", "zz"), "qntsdq119"),
    (("router119", "AgentU"), "ruygxl119"),
    (("router119", "keyboard"), "bssusr119"),
    (("router119", "AA"), "router119"),
    (("cluster119", "key"), "mpscxcb119"),
    (("cluster119", "lemon"), "npgggpv119"),
    (("cluster119", "a"), "cluster119"),
    (("cluster119", "zz"), "bktrsdq119"),
    (("cluster119", "AgentU"), "cryfmyr119"),
    (("cluster119", "keyboard"), "mpsthei119"),
    (("cluster119", "AA"), "cluster119"),
    (("mirror119", "key"), "wmpbsp119"),
    (("mirror119", "lemon"), "xmdfbc119"),
    (("mirror119", "a"), "mirror119"),
    (("mirror119", "zz"), "lhqqnq119"),
    (("mirror119", "AgentU"), "movehl119"),
    (("mirror119", "keyboard"), "wmpscr119"),
    (("mirror119", "AA"), "mirror119"),
    (("filter119", "key"), "pmjdip119"),
    (("filter119", "lemon"), "qmxhrc119"),
    (("filter119", "a"), "filter119"),
    (("filter119", "zz"), "ehksdq119"),
    (("filter119", "AgentU"), "fopgxl119"),
    (("filter119", "keyboard"), "pmjusr119"),
    (("filter119", "AA"), "filter119"),
    (("ranking119", "key"), "belumlq119"),
    (("ranking119", "lemon"), "cezyvyk119"),
    (("ranking119", "a"), "ranking119"),
    (("ranking119", "zz"), "qzmjhmf119"),
    (("ranking119", "AgentU"), "rgrxbhg119"),
    (("ranking119", "keyboard"), "bellwnx119"),
    (("ranking119", "AA"), "ranking119"),
    (("encoding119", "key"), "orayhgxk119"),
    (("encoding119", "lemon"), "procqtrs119"),
    (("encoding119", "a"), "encoding119"),
    (("encoding119", "zz"), "dmbnchmf119"),
    (("encoding119", "AgentU"), "etgbwcnm119"),
    (("encoding119", "keyboard"), "orapriej119"),
    (("encoding119", "AA"), "encoding119"),
    (("mapping119", "key"), "wenzmlq119"),
    (("mapping119", "lemon"), "xebdvyk119"),
    (("mapping119", "a"), "mapping119"),
    (("mapping119", "zz"), "lzoohmf119"),
    (("mapping119", "AgentU"), "mgtcbhg119"),
    (("mapping119", "keyboard"), "wenqwnx119"),
    (("mapping119", "AA"), "mapping119"),
    (("record119", "key"), "biayvb119"),
    (("record119", "lemon"), "cioceo119"),
    (("record119", "a"), "record119"),
    (("record119", "zz"), "qdbnqc119"),
    (("record119", "AgentU"), "rkgbkx119"),
    (("record119", "keyboard"), "biapfd119"),
    (("record119", "AA"), "record119"),
    (("candle119", "key"), "melnpc119"),
    (("candle119", "lemon"), "nezryp119"),
    (("candle119", "a"), "candle119"),
    (("candle119", "zz"), "bzmckd119"),
    (("candle119", "AgentU"), "cgrqey119"),
    (("candle119", "keyboard"), "meleze119"),
    (("candle119", "AA"), "candle119"),
    (("thread119", "key"), "dlpoeb119"),
    (("thread119", "lemon"), "eldsno119"),
    (("thread119", "a"), "thread119"),
    (("thread119", "zz"), "sgqdzc119"),
    (("thread119", "AgentU"), "tnvrtx119"),
    (("thread119", "keyboard"), "dlpfod119"),
    (("thread119", "AA"), "thread119"),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 119: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 119: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "a"),
        "round 119: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 119: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 119: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 119: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", "AA"),
        "round 119: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "key"),
        "bssxh 119: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 119: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "a"),
        "round 119: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 119: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 119: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 119: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", "AA"),
        "round 119: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 119: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 119: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "a"),
        "round 119: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 119: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 119: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 119: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", "AA"),
        "round 119: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 119: the processor reads the record then stops", "key"),
        "bssxh 119: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 119: the processor reads the record then stops", "lemon"),
        "csgbq 119: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 119: the processor reads the record then stops", "a"),
        "round 119: the processor reads the record then stops",
    ),
    (
        ("round 119: the processor reads the record then stops", "zz"),
        "qntmc 119: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 119: the processor reads the record then stops", "AgentU"),
        "ruyaw 119: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 119: the processor reads the record then stops", "keyboard"),
        "bssor 119: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 119: the processor reads the record then stops", "AA"),
        "round 119: the processor reads the record then stops",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "key"),
        "bssxh 119: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "lemon"),
        "csgbq 119: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "a"),
        "round 119: a worker pulls the next task from the queue",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "zz"),
        "qntmc 119: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 119: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "keyboard"),
        "bssor 119: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 119: a worker pulls the next task from the queue", "AA"),
        "round 119: a worker pulls the next task from the queue",
    ),
    (
        ("round 119: signals travel through the network layer", "key"),
        "bssxh 119: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 119: signals travel through the network layer", "lemon"),
        "csgbq 119: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 119: signals travel through the network layer", "a"),
        "round 119: signals travel through the network layer",
    ),
    (
        ("round 119: signals travel through the network layer", "zz"),
        "qntmc 119: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 119: signals travel through the network layer", "AgentU"),
        "ruyaw 119: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 119: signals travel through the network layer", "keyboard"),
        "bssor 119: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 119: signals travel through the network layer", "AA"),
        "round 119: signals travel through the network layer",
    ),
    (
        ("round 119: the gateway routes each request by policy", "key"),
        "bssxh 119: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 119: the gateway routes each request by policy", "lemon"),
        "csgbq 119: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 119: the gateway routes each request by policy", "a"),
        "round 119: the gateway routes each request by policy",
    ),
    (
        ("round 119: the gateway routes each request by policy", "zz"),
        "qntmc 119: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 119: the gateway routes each request by policy", "AgentU"),
        "ruyaw 119: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 119: the gateway routes each request by policy", "keyboard"),
        "bssor 119: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 119: the gateway routes each request by policy", "AA"),
        "round 119: the gateway routes each request by policy",
    ),
    (("round 119: memory grows until the buffer is full", "key"), "bssxh 119: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 119: memory grows until the buffer is full", "lemon"), "csgbq 119: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 119: memory grows until the buffer is full", "a"), "round 119: memory grows until the buffer is full"),
    (("round 119: memory grows until the buffer is full", "zz"), "qntmc 119: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 119: memory grows until the buffer is full", "AgentU"),
        "ruyaw 119: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 119: memory grows until the buffer is full", "keyboard"),
        "bssor 119: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 119: memory grows until the buffer is full", "AA"), "round 119: memory grows until the buffer is full"),
    (("round 119: the cluster mirrors every packet twice", "key"), "bssxh 119: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 119: the cluster mirrors every packet twice", "lemon"),
        "csgbq 119: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 119: the cluster mirrors every packet twice", "a"), "round 119: the cluster mirrors every packet twice"),
    (("round 119: the cluster mirrors every packet twice", "zz"), "qntmc 119: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 119: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 119: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 119: the cluster mirrors every packet twice", "keyboard"),
        "bssor 119: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 119: the cluster mirrors every packet twice", "AA"), "round 119: the cluster mirrors every packet twice"),
    (
        ("round 119: ranking uses tokens learned from the corpus", "key"),
        "bssxh 119: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 119: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", "a"),
        "round 119: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 119: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 119: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 119: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", "AA"),
        "round 119: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 119: a long session ends when the candle dies", "key"),
        "bssxh 119: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 119: a long session ends when the candle dies", "lemon"),
        "csgbq 119: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 119: a long session ends when the candle dies", "a"),
        "round 119: a long session ends when the candle dies",
    ),
    (
        ("round 119: a long session ends when the candle dies", "zz"),
        "qntmc 119: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 119: a long session ends when the candle dies", "AgentU"),
        "ruyaw 119: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 119: a long session ends when the candle dies", "keyboard"),
        "bssor 119: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 119: a long session ends when the candle dies", "AA"),
        "round 119: a long session ends when the candle dies",
    ),
    (("round 119: encode the prompt then map the result", "key"), "bssxh 119: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 119: encode the prompt then map the result", "lemon"), "csgbq 119: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 119: encode the prompt then map the result", "a"), "round 119: encode the prompt then map the result"),
    (("round 119: encode the prompt then map the result", "zz"), "qntmc 119: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 119: encode the prompt then map the result", "AgentU"),
        "ruyaw 119: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 119: encode the prompt then map the result", "keyboard"),
        "bssor 119: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 119: encode the prompt then map the result", "AA"), "round 119: encode the prompt then map the result"),
    (("round 119: the kernel wakes the worker at dawn", "key"), "bssxh 119: rri iovlop ukocc xfo ambocb er neux"),
    (("round 119: the kernel wakes the worker at dawn", "lemon"), "csgbq 119: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 119: the kernel wakes the worker at dawn", "a"), "round 119: the kernel wakes the worker at dawn"),
    (("round 119: the kernel wakes the worker at dawn", "zz"), "qntmc 119: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 119: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 119: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 119: the kernel wakes the worker at dawn", "keyboard"), "bssor 119: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 119: the kernel wakes the worker at dawn", "AA"), "round 119: the kernel wakes the worker at dawn"),
    (("round 119: service latency drops after the patch", "key"), "bssxh 119: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 119: service latency drops after the patch", "lemon"), "csgbq 119: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 119: service latency drops after the patch", "a"), "round 119: service latency drops after the patch"),
    (("round 119: service latency drops after the patch", "zz"), "qntmc 119: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 119: service latency drops after the patch", "AgentU"),
        "ruyaw 119: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 119: service latency drops after the patch", "keyboard"),
        "bssor 119: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 119: service latency drops after the patch", "AA"), "round 119: service latency drops after the patch"),
    (
        ("round 119: the library caches every vector it sees", "key"),
        "bssxh 119: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 119: the library caches every vector it sees", "lemon"),
        "csgbq 119: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 119: the library caches every vector it sees", "a"), "round 119: the library caches every vector it sees"),
    (
        ("round 119: the library caches every vector it sees", "zz"),
        "qntmc 119: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 119: the library caches every vector it sees", "AgentU"),
        "ruyaw 119: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 119: the library caches every vector it sees", "keyboard"),
        "bssor 119: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 119: the library caches every vector it sees", "AA"),
        "round 119: the library caches every vector it sees",
    ),
    (("round 119: agents argue then the debate resolves", "key"), "bssxh 119: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 119: agents argue then the debate resolves", "lemon"), "csgbq 119: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 119: agents argue then the debate resolves", "a"), "round 119: agents argue then the debate resolves"),
    (("round 119: agents argue then the debate resolves", "zz"), "qntmc 119: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 119: agents argue then the debate resolves", "AgentU"),
        "ruyaw 119: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 119: agents argue then the debate resolves", "keyboard"),
        "bssor 119: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 119: agents argue then the debate resolves", "AA"), "round 119: agents argue then the debate resolves"),
    (("round 119: the filter keeps only strong matches", "key"), "bssxh 119: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 119: the filter keeps only strong matches", "lemon"), "csgbq 119: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 119: the filter keeps only strong matches", "a"), "round 119: the filter keeps only strong matches"),
    (("round 119: the filter keeps only strong matches", "zz"), "qntmc 119: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 119: the filter keeps only strong matches", "AgentU"), "ruyaw 119: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 119: the filter keeps only strong matches", "keyboard"),
        "bssor 119: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 119: the filter keeps only strong matches", "AA"), "round 119: the filter keeps only strong matches"),
    (("round 119: the model answers with a short reply", "key"), "bssxh 119: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 119: the model answers with a short reply", "lemon"), "csgbq 119: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 119: the model answers with a short reply", "a"), "round 119: the model answers with a short reply"),
    (("round 119: the model answers with a short reply", "zz"), "qntmc 119: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 119: the model answers with a short reply", "AgentU"), "ruyaw 119: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 119: the model answers with a short reply", "keyboard"),
        "bssor 119: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 119: the model answers with a short reply", "AA"), "round 119: the model answers with a short reply"),
    (
        ("round 119: the recorder stores the reasoning trace", "key"),
        "bssxh 119: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 119: the recorder stores the reasoning trace", "lemon"),
        "csgbq 119: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 119: the recorder stores the reasoning trace", "a"), "round 119: the recorder stores the reasoning trace"),
    (
        ("round 119: the recorder stores the reasoning trace", "zz"),
        "qntmc 119: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 119: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 119: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 119: the recorder stores the reasoning trace", "keyboard"),
        "bssor 119: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 119: the recorder stores the reasoning trace", "AA"),
        "round 119: the recorder stores the reasoning trace",
    ),
    (("round 119: the angel watches the processor run", "key"), "bssxh 119: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 119: the angel watches the processor run", "lemon"), "csgbq 119: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 119: the angel watches the processor run", "a"), "round 119: the angel watches the processor run"),
    (("round 119: the angel watches the processor run", "zz"), "qntmc 119: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 119: the angel watches the processor run", "AgentU"), "ruyaw 119: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 119: the angel watches the processor run", "keyboard"), "bssor 119: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 119: the angel watches the processor run", "AA"), "round 119: the angel watches the processor run"),
    (("round 119: angle of the vector decides the match", "key"), "bssxh 119: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 119: angle of the vector decides the match", "lemon"), "csgbq 119: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 119: angle of the vector decides the match", "a"), "round 119: angle of the vector decides the match"),
    (("round 119: angle of the vector decides the match", "zz"), "qntmc 119: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 119: angle of the vector decides the match", "AgentU"),
        "ruyaw 119: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 119: angle of the vector decides the match", "keyboard"),
        "bssor 119: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 119: angle of the vector decides the match", "AA"), "round 119: angle of the vector decides the match"),
    (
        ("round 119: the candle burns twice as long at night", "key"),
        "bssxh 119: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 119: the candle burns twice as long at night", "lemon"),
        "csgbq 119: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 119: the candle burns twice as long at night", "a"), "round 119: the candle burns twice as long at night"),
    (
        ("round 119: the candle burns twice as long at night", "zz"),
        "qntmc 119: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 119: the candle burns twice as long at night", "AgentU"),
        "ruyaw 119: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 119: the candle burns twice as long at night", "keyboard"),
        "bssor 119: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 119: the candle burns twice as long at night", "AA"),
        "round 119: the candle burns twice as long at night",
    ),
    (("round 119: a mirror of the universe in one line", "key"), "bssxh 119: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 119: a mirror of the universe in one line", "lemon"), "csgbq 119: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 119: a mirror of the universe in one line", "a"), "round 119: a mirror of the universe in one line"),
    (("round 119: a mirror of the universe in one line", "zz"), "qntmc 119: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 119: a mirror of the universe in one line", "AgentU"), "ruyaw 119: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 119: a mirror of the universe in one line", "keyboard"),
        "bssor 119: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 119: a mirror of the universe in one line", "AA"), "round 119: a mirror of the universe in one line"),
    (("round 119: the queue drains before the storm", "key"), "bssxh 119: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 119: the queue drains before the storm", "lemon"), "csgbq 119: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 119: the queue drains before the storm", "a"), "round 119: the queue drains before the storm"),
    (("round 119: the queue drains before the storm", "zz"), "qntmc 119: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 119: the queue drains before the storm", "AgentU"), "ruyaw 119: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 119: the queue drains before the storm", "keyboard"), "bssor 119: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 119: the queue drains before the storm", "AA"), "round 119: the queue drains before the storm"),
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
