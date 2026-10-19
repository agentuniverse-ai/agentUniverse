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
    (("kitten141", "key"), "umrdil141"),
    (("kitten141", "lemon"), "vmfhry141"),
    (("kitten141", "a"), "kitten141"),
    (("kitten141", "zz"), "jhssdm141"),
    (("kitten141", "AgentU"), "koxgxh141"),
    (("kitten141", "keyboard"), "umrusn141"),
    (("kitten141", "AA"), "kitten141"),
    (("sitting141", "key"), "cmrdmlq141"),
    (("sitting141", "lemon"), "dmfhvyk141"),
    (("sitting141", "a"), "sitting141"),
    (("sitting141", "zz"), "rhsshmf141"),
    (("sitting141", "AgentU"), "soxgbhg141"),
    (("sitting141", "keyboard"), "cmruwnx141"),
    (("sitting141", "AA"), "sitting141"),
    (("agent141", "key"), "kkcxx141"),
    (("agent141", "lemon"), "lkqbg141"),
    (("agent141", "a"), "agent141"),
    (("agent141", "zz"), "zfdms141"),
    (("agent141", "AgentU"), "amiam141"),
    (("agent141", "keyboard"), "kkcoh141"),
    (("agent141", "AA"), "agent141"),
    (("angle141", "key"), "krevi141"),
    (("angle141", "lemon"), "lrszr141"),
    (("angle141", "a"), "angle141"),
    (("angle141", "zz"), "zmfkd141"),
    (("angle141", "AgentU"), "atkyx141"),
    (("angle141", "keyboard"), "krems141"),
    (("angle141", "AA"), "angle141"),
    (("universe141", "key"), "ergfipci141"),
    (("universe141", "lemon"), "frujrcwq141"),
    (("universe141", "a"), "universe141"),
    (("universe141", "zz"), "tmhudqrd141"),
    (("universe141", "AgentU"), "utmixlsk141"),
    (("universe141", "keyboard"), "ergwsrjh141"),
    (("universe141", "AA"), "universe141"),
    (("memory141", "key"), "wikyvw141"),
    (("memory141", "lemon"), "xiycej141"),
    (("memory141", "a"), "memory141"),
    (("memory141", "zz"), "ldlnqx141"),
    (("memory141", "AgentU"), "mkqbks141"),
    (("memory141", "keyboard"), "wikpfy141"),
    (("memory141", "AA"), "memory141"),
    (("stream141", "key"), "cxpoek141"),
    (("stream141", "lemon"), "dxdsnx141"),
    (("stream141", "a"), "stream141"),
    (("stream141", "zz"), "rsqdzl141"),
    (("stream141", "AgentU"), "szvrtg141"),
    (("stream141", "keyboard"), "cxpfom141"),
    (("stream141", "AA"), "stream141"),
    (("context141", "key"), "msldivd141"),
    (("context141", "lemon"), "nszhrix141"),
    (("context141", "a"), "context141"),
    (("context141", "zz"), "bnmsdws141"),
    (("context141", "AgentU"), "curgxrt141"),
    (("context141", "keyboard"), "mslusxk141"),
    (("context141", "AA"), "context141"),
    (("knowledge141", "key"), "urmgpcnkc141"),
    (("knowledge141", "lemon"), "vrakyphss141"),
    (("knowledge141", "a"), "knowledge141"),
    (("knowledge141", "zz"), "jmnvkdcfd141"),
    (("knowledge141", "AgentU"), "ktsjeydmi141"),
    (("knowledge141", "keyboard"), "urmxzeujo141"),
    (("knowledge141", "AA"), "knowledge141"),
    (("vector141", "key"), "fiadsp141"),
    (("vector141", "lemon"), "giohbc141"),
    (("vector141", "a"), "vector141"),
    (("vector141", "zz"), "udbsnq141"),
    (("vector141", "AgentU"), "vkgghl141"),
    (("vector141", "keyboard"), "fiaucr141"),
    (("vector141", "AA"), "vector141"),
    (("processor141", "key"), "zvmmiqcsp141"),
    (("processor141", "lemon"), "avaqrdwaf141"),
    (("processor141", "a"), "processor141"),
    (("processor141", "zz"), "oqnbdrrnq141"),
    (("processor141", "AgentU"), "pxspxmsuv141"),
    (("processor141", "keyboard"), "zvmdssjrb141"),
    (("processor141", "AA"), "processor141"),
    (("reasoning141", "key"), "biycslsre141"),
    (("reasoning141", "lemon"), "cimgbymzu141"),
    (("reasoning141", "a"), "reasoning141"),
    (("reasoning141", "zz"), "qdzrnmhmf141"),
    (("reasoning141", "AgentU"), "rkefhhitk141"),
    (("reasoning141", "keyboard"), "biytcnzqq141"),
    (("reasoning141", "AA"), "reasoning141"),
    (("machine141", "key"), "wearmlo141"),
    (("machine141", "lemon"), "xeovvyi141"),
    (("machine141", "a"), "machine141"),
    (("machine141", "zz"), "lzbghmd141"),
    (("machine141", "AgentU"), "mggubhe141"),
    (("machine141", "keyboard"), "weaiwnv141"),
    (("machine141", "AA"), "machine141"),
    (("learning141", "key"), "viybrgxk141"),
    (("learning141", "lemon"), "wimfatrs141"),
    (("learning141", "a"), "learning141"),
    (("learning141", "zz"), "kdzqmhmf141"),
    (("learning141", "AgentU"), "lkeegcnm141"),
    (("learning141", "keyboard"), "viysbiej141"),
    (("learning141", "AA"), "learning141"),
    (("model141", "key"), "wsbop141"),
    (("model141", "lemon"), "xspsy141"),
    (("model141", "a"), "model141"),
    (("model141", "zz"), "lncdk141"),
    (("model141", "AgentU"), "muhre141"),
    (("model141", "keyboard"), "wsbfz141"),
    (("model141", "AA"), "model141"),
    (("token141", "key"), "dsior141"),
    (("token141", "lemon"), "eswsa141"),
    (("token141", "a"), "token141"),
    (("token141", "zz"), "snjdm141"),
    (("token141", "AgentU"), "tuorg141"),
    (("token141", "keyboard"), "dsifb141"),
    (("token141", "AA"), "token141"),
    (("prompt141", "key"), "zvmwtr141"),
    (("prompt141", "lemon"), "avaace141"),
    (("prompt141", "a"), "prompt141"),
    (("prompt141", "zz"), "oqnlos141"),
    (("prompt141", "AgentU"), "pxszin141"),
    (("prompt141", "keyboard"), "zvmndt141"),
    (("prompt141", "AA"), "prompt141"),
    (("session141", "key"), "ciqcmmx141"),
    (("session141", "lemon"), "diegvzr141"),
    (("session141", "a"), "session141"),
    (("session141", "zz"), "rdrrhnm141"),
    (("session141", "AgentU"), "skwfbin141"),
    (("session141", "keyboard"), "ciqtwoe141"),
    (("session141", "AA"), "session141"),
    (("library141", "key"), "vmzbepi141"),
    (("library141", "lemon"), "wmnfncc141"),
    (("library141", "a"), "library141"),
    (("library141", "zz"), "khaqzqx141"),
    (("library141", "AgentU"), "lofetly141"),
    (("library141", "keyboard"), "vmzsorp141"),
    (("library141", "AA"), "library141"),
    (("service141", "key"), "cipfmao141"),
    (("service141", "lemon"), "didjvni141"),
    (("service141", "a"), "service141"),
    (("service141", "zz"), "rdquhbd141"),
    (("service141", "AgentU"), "skvibwe141"),
    (("service141", "keyboard"), "cipwwcv141"),
    (("service141", "AA"), "service141"),
    (("gateway141", "key"), "qeroayi141"),
    (("gateway141", "lemon"), "refsjlc141"),
    (("gateway141", "a"), "gateway141"),
    (("gateway141", "zz"), "fzsdvzx141"),
    (("gateway141", "AgentU"), "ggxrpuy141"),
    (("gateway141", "keyboard"), "qerfkap141"),
    (("gateway141", "AA"), "gateway141"),
    (("storage141", "key"), "cxmbeeo141"),
    (("storage141", "lemon"), "dxafnri141"),
    (("storage141", "a"), "storage141"),
    (("storage141", "zz"), "rsnqzfd141"),
    (("storage141", "AgentU"), "szsetae141"),
    (("storage141", "keyboard"), "cxmsogv141"),
    (("storage141", "AA"), "storage141"),
    (("network141", "key"), "xirgspu141"),
    (("network141", "lemon"), "yifkbco141"),
    (("network141", "a"), "network141"),
    (("network141", "zz"), "mdsvnqj141"),
    (("network141", "AgentU"), "nkxjhlk141"),
    (("network141", "keyboard"), "xirxcrb141"),
    (("network141", "AA"), "network141"),
    (("latency141", "key"), "verorai141"),
    (("latency141", "lemon"), "wefsanc141"),
    (("latency141", "a"), "latency141"),
    (("latency141", "zz"), "kzsdmbx141"),
    (("latency141", "AgentU"), "lgxrgwy141"),
    (("latency141", "keyboard"), "verfbcp141"),
    (("latency141", "AA"), "latency141"),
    (("buffer141", "key"), "lydpip141"),
    (("buffer141", "lemon"), "myrtrc141"),
    (("buffer141", "a"), "buffer141"),
    (("buffer141", "zz"), "ateedq141"),
    (("buffer141", "AgentU"), "bajsxl141"),
    (("buffer141", "keyboard"), "lydgsr141"),
    (("buffer141", "AA"), "buffer141"),
    (("queue141", "key"), "aycei141"),
    (("queue141", "lemon"), "byqir141"),
    (("queue141", "a"), "queue141"),
    (("queue141", "zz"), "ptdtd141"),
    (("queue141", "AgentU"), "qaihx141"),
    (("queue141", "keyboard"), "aycvs141"),
    (("queue141", "AA"), "queue141"),
    (("worker141", "key"), "gspuip141"),
    (("worker141", "lemon"), "hsdyrc141"),
    (("worker141", "a"), "worker141"),
    (("worker141", "zz"), "vnqjdq141"),
    (("worker141", "AgentU"), "wuvxxl141"),
    (("worker141", "keyboard"), "gsplsr141"),
    (("worker141", "AA"), "worker141"),
    (("kernel141", "key"), "uipxij141"),
    (("kernel141", "lemon"), "vidbrw141"),
    (("kernel141", "a"), "kernel141"),
    (("kernel141", "zz"), "jdqmdk141"),
    (("kernel141", "AgentU"), "kkvaxf141"),
    (("kernel141", "keyboard"), "uiposl141"),
    (("kernel141", "AA"), "kernel141"),
    (("signal141", "key"), "cmexej141"),
    (("signal141", "lemon"), "dmsbnw141"),
    (("signal141", "a"), "signal141"),
    (("signal141", "zz"), "rhfmzk141"),
    (("signal141", "AgentU"), "sokatf141"),
    (("signal141", "keyboard"), "cmeool141"),
    (("signal141", "AA"), "signal141"),
    (("packet141", "key"), "zeauir141"),
    (("packet141", "lemon"), "aeoyre141"),
    (("packet141", "a"), "packet141"),
    (("packet141", "zz"), "ozbjds141"),
    (("packet141", "AgentU"), "pggxxn141"),
    (("packet141", "keyboard"), "zealst141"),
    (("packet141", "AA"), "packet141"),
    (("router141", "key"), "bssdip141"),
    (("router141", "lemon"), "csghrc141"),
    (("router141", "a"), "router141"),
    (("router141", "zz"), "qntsdq141"),
    (("router141", "AgentU"), "ruygxl141"),
    (("router141", "keyboard"), "bssusr141"),
    (("router141", "AA"), "router141"),
    (("cluster141", "key"), "mpscxcb141"),
    (("cluster141", "lemon"), "npgggpv141"),
    (("cluster141", "a"), "cluster141"),
    (("cluster141", "zz"), "bktrsdq141"),
    (("cluster141", "AgentU"), "cryfmyr141"),
    (("cluster141", "keyboard"), "mpsthei141"),
    (("cluster141", "AA"), "cluster141"),
    (("mirror141", "key"), "wmpbsp141"),
    (("mirror141", "lemon"), "xmdfbc141"),
    (("mirror141", "a"), "mirror141"),
    (("mirror141", "zz"), "lhqqnq141"),
    (("mirror141", "AgentU"), "movehl141"),
    (("mirror141", "keyboard"), "wmpscr141"),
    (("mirror141", "AA"), "mirror141"),
    (("filter141", "key"), "pmjdip141"),
    (("filter141", "lemon"), "qmxhrc141"),
    (("filter141", "a"), "filter141"),
    (("filter141", "zz"), "ehksdq141"),
    (("filter141", "AgentU"), "fopgxl141"),
    (("filter141", "keyboard"), "pmjusr141"),
    (("filter141", "AA"), "filter141"),
    (("ranking141", "key"), "belumlq141"),
    (("ranking141", "lemon"), "cezyvyk141"),
    (("ranking141", "a"), "ranking141"),
    (("ranking141", "zz"), "qzmjhmf141"),
    (("ranking141", "AgentU"), "rgrxbhg141"),
    (("ranking141", "keyboard"), "bellwnx141"),
    (("ranking141", "AA"), "ranking141"),
    (("encoding141", "key"), "orayhgxk141"),
    (("encoding141", "lemon"), "procqtrs141"),
    (("encoding141", "a"), "encoding141"),
    (("encoding141", "zz"), "dmbnchmf141"),
    (("encoding141", "AgentU"), "etgbwcnm141"),
    (("encoding141", "keyboard"), "orapriej141"),
    (("encoding141", "AA"), "encoding141"),
    (("mapping141", "key"), "wenzmlq141"),
    (("mapping141", "lemon"), "xebdvyk141"),
    (("mapping141", "a"), "mapping141"),
    (("mapping141", "zz"), "lzoohmf141"),
    (("mapping141", "AgentU"), "mgtcbhg141"),
    (("mapping141", "keyboard"), "wenqwnx141"),
    (("mapping141", "AA"), "mapping141"),
    (("record141", "key"), "biayvb141"),
    (("record141", "lemon"), "cioceo141"),
    (("record141", "a"), "record141"),
    (("record141", "zz"), "qdbnqc141"),
    (("record141", "AgentU"), "rkgbkx141"),
    (("record141", "keyboard"), "biapfd141"),
    (("record141", "AA"), "record141"),
    (("candle141", "key"), "melnpc141"),
    (("candle141", "lemon"), "nezryp141"),
    (("candle141", "a"), "candle141"),
    (("candle141", "zz"), "bzmckd141"),
    (("candle141", "AgentU"), "cgrqey141"),
    (("candle141", "keyboard"), "meleze141"),
    (("candle141", "AA"), "candle141"),
    (("thread141", "key"), "dlpoeb141"),
    (("thread141", "lemon"), "eldsno141"),
    (("thread141", "a"), "thread141"),
    (("thread141", "zz"), "sgqdzc141"),
    (("thread141", "AgentU"), "tnvrtx141"),
    (("thread141", "keyboard"), "dlpfod141"),
    (("thread141", "AA"), "thread141"),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 141: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 141: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "a"),
        "round 141: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 141: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 141: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 141: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", "AA"),
        "round 141: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "key"),
        "bssxh 141: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 141: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "a"),
        "round 141: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 141: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 141: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 141: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", "AA"),
        "round 141: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 141: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 141: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "a"),
        "round 141: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 141: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 141: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 141: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", "AA"),
        "round 141: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 141: the processor reads the record then stops", "key"),
        "bssxh 141: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 141: the processor reads the record then stops", "lemon"),
        "csgbq 141: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 141: the processor reads the record then stops", "a"),
        "round 141: the processor reads the record then stops",
    ),
    (
        ("round 141: the processor reads the record then stops", "zz"),
        "qntmc 141: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 141: the processor reads the record then stops", "AgentU"),
        "ruyaw 141: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 141: the processor reads the record then stops", "keyboard"),
        "bssor 141: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 141: the processor reads the record then stops", "AA"),
        "round 141: the processor reads the record then stops",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "key"),
        "bssxh 141: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "lemon"),
        "csgbq 141: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "a"),
        "round 141: a worker pulls the next task from the queue",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "zz"),
        "qntmc 141: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 141: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "keyboard"),
        "bssor 141: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 141: a worker pulls the next task from the queue", "AA"),
        "round 141: a worker pulls the next task from the queue",
    ),
    (
        ("round 141: signals travel through the network layer", "key"),
        "bssxh 141: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 141: signals travel through the network layer", "lemon"),
        "csgbq 141: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 141: signals travel through the network layer", "a"),
        "round 141: signals travel through the network layer",
    ),
    (
        ("round 141: signals travel through the network layer", "zz"),
        "qntmc 141: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 141: signals travel through the network layer", "AgentU"),
        "ruyaw 141: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 141: signals travel through the network layer", "keyboard"),
        "bssor 141: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 141: signals travel through the network layer", "AA"),
        "round 141: signals travel through the network layer",
    ),
    (
        ("round 141: the gateway routes each request by policy", "key"),
        "bssxh 141: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 141: the gateway routes each request by policy", "lemon"),
        "csgbq 141: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 141: the gateway routes each request by policy", "a"),
        "round 141: the gateway routes each request by policy",
    ),
    (
        ("round 141: the gateway routes each request by policy", "zz"),
        "qntmc 141: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 141: the gateway routes each request by policy", "AgentU"),
        "ruyaw 141: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 141: the gateway routes each request by policy", "keyboard"),
        "bssor 141: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 141: the gateway routes each request by policy", "AA"),
        "round 141: the gateway routes each request by policy",
    ),
    (("round 141: memory grows until the buffer is full", "key"), "bssxh 141: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 141: memory grows until the buffer is full", "lemon"), "csgbq 141: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 141: memory grows until the buffer is full", "a"), "round 141: memory grows until the buffer is full"),
    (("round 141: memory grows until the buffer is full", "zz"), "qntmc 141: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 141: memory grows until the buffer is full", "AgentU"),
        "ruyaw 141: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 141: memory grows until the buffer is full", "keyboard"),
        "bssor 141: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 141: memory grows until the buffer is full", "AA"), "round 141: memory grows until the buffer is full"),
    (("round 141: the cluster mirrors every packet twice", "key"), "bssxh 141: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 141: the cluster mirrors every packet twice", "lemon"),
        "csgbq 141: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 141: the cluster mirrors every packet twice", "a"), "round 141: the cluster mirrors every packet twice"),
    (("round 141: the cluster mirrors every packet twice", "zz"), "qntmc 141: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 141: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 141: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 141: the cluster mirrors every packet twice", "keyboard"),
        "bssor 141: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 141: the cluster mirrors every packet twice", "AA"), "round 141: the cluster mirrors every packet twice"),
    (
        ("round 141: ranking uses tokens learned from the corpus", "key"),
        "bssxh 141: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 141: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", "a"),
        "round 141: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 141: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 141: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 141: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", "AA"),
        "round 141: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 141: a long session ends when the candle dies", "key"),
        "bssxh 141: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 141: a long session ends when the candle dies", "lemon"),
        "csgbq 141: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 141: a long session ends when the candle dies", "a"),
        "round 141: a long session ends when the candle dies",
    ),
    (
        ("round 141: a long session ends when the candle dies", "zz"),
        "qntmc 141: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 141: a long session ends when the candle dies", "AgentU"),
        "ruyaw 141: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 141: a long session ends when the candle dies", "keyboard"),
        "bssor 141: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 141: a long session ends when the candle dies", "AA"),
        "round 141: a long session ends when the candle dies",
    ),
    (("round 141: encode the prompt then map the result", "key"), "bssxh 141: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 141: encode the prompt then map the result", "lemon"), "csgbq 141: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 141: encode the prompt then map the result", "a"), "round 141: encode the prompt then map the result"),
    (("round 141: encode the prompt then map the result", "zz"), "qntmc 141: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 141: encode the prompt then map the result", "AgentU"),
        "ruyaw 141: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 141: encode the prompt then map the result", "keyboard"),
        "bssor 141: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 141: encode the prompt then map the result", "AA"), "round 141: encode the prompt then map the result"),
    (("round 141: the kernel wakes the worker at dawn", "key"), "bssxh 141: rri iovlop ukocc xfo ambocb er neux"),
    (("round 141: the kernel wakes the worker at dawn", "lemon"), "csgbq 141: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 141: the kernel wakes the worker at dawn", "a"), "round 141: the kernel wakes the worker at dawn"),
    (("round 141: the kernel wakes the worker at dawn", "zz"), "qntmc 141: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 141: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 141: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 141: the kernel wakes the worker at dawn", "keyboard"), "bssor 141: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 141: the kernel wakes the worker at dawn", "AA"), "round 141: the kernel wakes the worker at dawn"),
    (("round 141: service latency drops after the patch", "key"), "bssxh 141: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 141: service latency drops after the patch", "lemon"), "csgbq 141: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 141: service latency drops after the patch", "a"), "round 141: service latency drops after the patch"),
    (("round 141: service latency drops after the patch", "zz"), "qntmc 141: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 141: service latency drops after the patch", "AgentU"),
        "ruyaw 141: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 141: service latency drops after the patch", "keyboard"),
        "bssor 141: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 141: service latency drops after the patch", "AA"), "round 141: service latency drops after the patch"),
    (
        ("round 141: the library caches every vector it sees", "key"),
        "bssxh 141: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 141: the library caches every vector it sees", "lemon"),
        "csgbq 141: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 141: the library caches every vector it sees", "a"), "round 141: the library caches every vector it sees"),
    (
        ("round 141: the library caches every vector it sees", "zz"),
        "qntmc 141: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 141: the library caches every vector it sees", "AgentU"),
        "ruyaw 141: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 141: the library caches every vector it sees", "keyboard"),
        "bssor 141: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 141: the library caches every vector it sees", "AA"),
        "round 141: the library caches every vector it sees",
    ),
    (("round 141: agents argue then the debate resolves", "key"), "bssxh 141: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 141: agents argue then the debate resolves", "lemon"), "csgbq 141: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 141: agents argue then the debate resolves", "a"), "round 141: agents argue then the debate resolves"),
    (("round 141: agents argue then the debate resolves", "zz"), "qntmc 141: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 141: agents argue then the debate resolves", "AgentU"),
        "ruyaw 141: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 141: agents argue then the debate resolves", "keyboard"),
        "bssor 141: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 141: agents argue then the debate resolves", "AA"), "round 141: agents argue then the debate resolves"),
    (("round 141: the filter keeps only strong matches", "key"), "bssxh 141: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 141: the filter keeps only strong matches", "lemon"), "csgbq 141: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 141: the filter keeps only strong matches", "a"), "round 141: the filter keeps only strong matches"),
    (("round 141: the filter keeps only strong matches", "zz"), "qntmc 141: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 141: the filter keeps only strong matches", "AgentU"), "ruyaw 141: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 141: the filter keeps only strong matches", "keyboard"),
        "bssor 141: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 141: the filter keeps only strong matches", "AA"), "round 141: the filter keeps only strong matches"),
    (("round 141: the model answers with a short reply", "key"), "bssxh 141: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 141: the model answers with a short reply", "lemon"), "csgbq 141: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 141: the model answers with a short reply", "a"), "round 141: the model answers with a short reply"),
    (("round 141: the model answers with a short reply", "zz"), "qntmc 141: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 141: the model answers with a short reply", "AgentU"), "ruyaw 141: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 141: the model answers with a short reply", "keyboard"),
        "bssor 141: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 141: the model answers with a short reply", "AA"), "round 141: the model answers with a short reply"),
    (
        ("round 141: the recorder stores the reasoning trace", "key"),
        "bssxh 141: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 141: the recorder stores the reasoning trace", "lemon"),
        "csgbq 141: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 141: the recorder stores the reasoning trace", "a"), "round 141: the recorder stores the reasoning trace"),
    (
        ("round 141: the recorder stores the reasoning trace", "zz"),
        "qntmc 141: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 141: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 141: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 141: the recorder stores the reasoning trace", "keyboard"),
        "bssor 141: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 141: the recorder stores the reasoning trace", "AA"),
        "round 141: the recorder stores the reasoning trace",
    ),
    (("round 141: the angel watches the processor run", "key"), "bssxh 141: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 141: the angel watches the processor run", "lemon"), "csgbq 141: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 141: the angel watches the processor run", "a"), "round 141: the angel watches the processor run"),
    (("round 141: the angel watches the processor run", "zz"), "qntmc 141: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 141: the angel watches the processor run", "AgentU"), "ruyaw 141: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 141: the angel watches the processor run", "keyboard"), "bssor 141: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 141: the angel watches the processor run", "AA"), "round 141: the angel watches the processor run"),
    (("round 141: angle of the vector decides the match", "key"), "bssxh 141: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 141: angle of the vector decides the match", "lemon"), "csgbq 141: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 141: angle of the vector decides the match", "a"), "round 141: angle of the vector decides the match"),
    (("round 141: angle of the vector decides the match", "zz"), "qntmc 141: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 141: angle of the vector decides the match", "AgentU"),
        "ruyaw 141: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 141: angle of the vector decides the match", "keyboard"),
        "bssor 141: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 141: angle of the vector decides the match", "AA"), "round 141: angle of the vector decides the match"),
    (
        ("round 141: the candle burns twice as long at night", "key"),
        "bssxh 141: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 141: the candle burns twice as long at night", "lemon"),
        "csgbq 141: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 141: the candle burns twice as long at night", "a"), "round 141: the candle burns twice as long at night"),
    (
        ("round 141: the candle burns twice as long at night", "zz"),
        "qntmc 141: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 141: the candle burns twice as long at night", "AgentU"),
        "ruyaw 141: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 141: the candle burns twice as long at night", "keyboard"),
        "bssor 141: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 141: the candle burns twice as long at night", "AA"),
        "round 141: the candle burns twice as long at night",
    ),
    (("round 141: a mirror of the universe in one line", "key"), "bssxh 141: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 141: a mirror of the universe in one line", "lemon"), "csgbq 141: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 141: a mirror of the universe in one line", "a"), "round 141: a mirror of the universe in one line"),
    (("round 141: a mirror of the universe in one line", "zz"), "qntmc 141: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 141: a mirror of the universe in one line", "AgentU"), "ruyaw 141: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 141: a mirror of the universe in one line", "keyboard"),
        "bssor 141: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 141: a mirror of the universe in one line", "AA"), "round 141: a mirror of the universe in one line"),
    (("round 141: the queue drains before the storm", "key"), "bssxh 141: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 141: the queue drains before the storm", "lemon"), "csgbq 141: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 141: the queue drains before the storm", "a"), "round 141: the queue drains before the storm"),
    (("round 141: the queue drains before the storm", "zz"), "qntmc 141: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 141: the queue drains before the storm", "AgentU"), "ruyaw 141: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 141: the queue drains before the storm", "keyboard"), "bssor 141: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 141: the queue drains before the storm", "AA"), "round 141: the queue drains before the storm"),
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
