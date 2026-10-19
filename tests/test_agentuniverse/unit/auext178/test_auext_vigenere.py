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
    (("kitten178", "key"), "umrdil178"),
    (("kitten178", "lemon"), "vmfhry178"),
    (("kitten178", "a"), "kitten178"),
    (("kitten178", "zz"), "jhssdm178"),
    (("kitten178", "AgentU"), "koxgxh178"),
    (("kitten178", "keyboard"), "umrusn178"),
    (("kitten178", "AA"), "kitten178"),
    (("sitting178", "key"), "cmrdmlq178"),
    (("sitting178", "lemon"), "dmfhvyk178"),
    (("sitting178", "a"), "sitting178"),
    (("sitting178", "zz"), "rhsshmf178"),
    (("sitting178", "AgentU"), "soxgbhg178"),
    (("sitting178", "keyboard"), "cmruwnx178"),
    (("sitting178", "AA"), "sitting178"),
    (("agent178", "key"), "kkcxx178"),
    (("agent178", "lemon"), "lkqbg178"),
    (("agent178", "a"), "agent178"),
    (("agent178", "zz"), "zfdms178"),
    (("agent178", "AgentU"), "amiam178"),
    (("agent178", "keyboard"), "kkcoh178"),
    (("agent178", "AA"), "agent178"),
    (("angle178", "key"), "krevi178"),
    (("angle178", "lemon"), "lrszr178"),
    (("angle178", "a"), "angle178"),
    (("angle178", "zz"), "zmfkd178"),
    (("angle178", "AgentU"), "atkyx178"),
    (("angle178", "keyboard"), "krems178"),
    (("angle178", "AA"), "angle178"),
    (("universe178", "key"), "ergfipci178"),
    (("universe178", "lemon"), "frujrcwq178"),
    (("universe178", "a"), "universe178"),
    (("universe178", "zz"), "tmhudqrd178"),
    (("universe178", "AgentU"), "utmixlsk178"),
    (("universe178", "keyboard"), "ergwsrjh178"),
    (("universe178", "AA"), "universe178"),
    (("memory178", "key"), "wikyvw178"),
    (("memory178", "lemon"), "xiycej178"),
    (("memory178", "a"), "memory178"),
    (("memory178", "zz"), "ldlnqx178"),
    (("memory178", "AgentU"), "mkqbks178"),
    (("memory178", "keyboard"), "wikpfy178"),
    (("memory178", "AA"), "memory178"),
    (("stream178", "key"), "cxpoek178"),
    (("stream178", "lemon"), "dxdsnx178"),
    (("stream178", "a"), "stream178"),
    (("stream178", "zz"), "rsqdzl178"),
    (("stream178", "AgentU"), "szvrtg178"),
    (("stream178", "keyboard"), "cxpfom178"),
    (("stream178", "AA"), "stream178"),
    (("context178", "key"), "msldivd178"),
    (("context178", "lemon"), "nszhrix178"),
    (("context178", "a"), "context178"),
    (("context178", "zz"), "bnmsdws178"),
    (("context178", "AgentU"), "curgxrt178"),
    (("context178", "keyboard"), "mslusxk178"),
    (("context178", "AA"), "context178"),
    (("knowledge178", "key"), "urmgpcnkc178"),
    (("knowledge178", "lemon"), "vrakyphss178"),
    (("knowledge178", "a"), "knowledge178"),
    (("knowledge178", "zz"), "jmnvkdcfd178"),
    (("knowledge178", "AgentU"), "ktsjeydmi178"),
    (("knowledge178", "keyboard"), "urmxzeujo178"),
    (("knowledge178", "AA"), "knowledge178"),
    (("vector178", "key"), "fiadsp178"),
    (("vector178", "lemon"), "giohbc178"),
    (("vector178", "a"), "vector178"),
    (("vector178", "zz"), "udbsnq178"),
    (("vector178", "AgentU"), "vkgghl178"),
    (("vector178", "keyboard"), "fiaucr178"),
    (("vector178", "AA"), "vector178"),
    (("processor178", "key"), "zvmmiqcsp178"),
    (("processor178", "lemon"), "avaqrdwaf178"),
    (("processor178", "a"), "processor178"),
    (("processor178", "zz"), "oqnbdrrnq178"),
    (("processor178", "AgentU"), "pxspxmsuv178"),
    (("processor178", "keyboard"), "zvmdssjrb178"),
    (("processor178", "AA"), "processor178"),
    (("reasoning178", "key"), "biycslsre178"),
    (("reasoning178", "lemon"), "cimgbymzu178"),
    (("reasoning178", "a"), "reasoning178"),
    (("reasoning178", "zz"), "qdzrnmhmf178"),
    (("reasoning178", "AgentU"), "rkefhhitk178"),
    (("reasoning178", "keyboard"), "biytcnzqq178"),
    (("reasoning178", "AA"), "reasoning178"),
    (("machine178", "key"), "wearmlo178"),
    (("machine178", "lemon"), "xeovvyi178"),
    (("machine178", "a"), "machine178"),
    (("machine178", "zz"), "lzbghmd178"),
    (("machine178", "AgentU"), "mggubhe178"),
    (("machine178", "keyboard"), "weaiwnv178"),
    (("machine178", "AA"), "machine178"),
    (("learning178", "key"), "viybrgxk178"),
    (("learning178", "lemon"), "wimfatrs178"),
    (("learning178", "a"), "learning178"),
    (("learning178", "zz"), "kdzqmhmf178"),
    (("learning178", "AgentU"), "lkeegcnm178"),
    (("learning178", "keyboard"), "viysbiej178"),
    (("learning178", "AA"), "learning178"),
    (("model178", "key"), "wsbop178"),
    (("model178", "lemon"), "xspsy178"),
    (("model178", "a"), "model178"),
    (("model178", "zz"), "lncdk178"),
    (("model178", "AgentU"), "muhre178"),
    (("model178", "keyboard"), "wsbfz178"),
    (("model178", "AA"), "model178"),
    (("token178", "key"), "dsior178"),
    (("token178", "lemon"), "eswsa178"),
    (("token178", "a"), "token178"),
    (("token178", "zz"), "snjdm178"),
    (("token178", "AgentU"), "tuorg178"),
    (("token178", "keyboard"), "dsifb178"),
    (("token178", "AA"), "token178"),
    (("prompt178", "key"), "zvmwtr178"),
    (("prompt178", "lemon"), "avaace178"),
    (("prompt178", "a"), "prompt178"),
    (("prompt178", "zz"), "oqnlos178"),
    (("prompt178", "AgentU"), "pxszin178"),
    (("prompt178", "keyboard"), "zvmndt178"),
    (("prompt178", "AA"), "prompt178"),
    (("session178", "key"), "ciqcmmx178"),
    (("session178", "lemon"), "diegvzr178"),
    (("session178", "a"), "session178"),
    (("session178", "zz"), "rdrrhnm178"),
    (("session178", "AgentU"), "skwfbin178"),
    (("session178", "keyboard"), "ciqtwoe178"),
    (("session178", "AA"), "session178"),
    (("library178", "key"), "vmzbepi178"),
    (("library178", "lemon"), "wmnfncc178"),
    (("library178", "a"), "library178"),
    (("library178", "zz"), "khaqzqx178"),
    (("library178", "AgentU"), "lofetly178"),
    (("library178", "keyboard"), "vmzsorp178"),
    (("library178", "AA"), "library178"),
    (("service178", "key"), "cipfmao178"),
    (("service178", "lemon"), "didjvni178"),
    (("service178", "a"), "service178"),
    (("service178", "zz"), "rdquhbd178"),
    (("service178", "AgentU"), "skvibwe178"),
    (("service178", "keyboard"), "cipwwcv178"),
    (("service178", "AA"), "service178"),
    (("gateway178", "key"), "qeroayi178"),
    (("gateway178", "lemon"), "refsjlc178"),
    (("gateway178", "a"), "gateway178"),
    (("gateway178", "zz"), "fzsdvzx178"),
    (("gateway178", "AgentU"), "ggxrpuy178"),
    (("gateway178", "keyboard"), "qerfkap178"),
    (("gateway178", "AA"), "gateway178"),
    (("storage178", "key"), "cxmbeeo178"),
    (("storage178", "lemon"), "dxafnri178"),
    (("storage178", "a"), "storage178"),
    (("storage178", "zz"), "rsnqzfd178"),
    (("storage178", "AgentU"), "szsetae178"),
    (("storage178", "keyboard"), "cxmsogv178"),
    (("storage178", "AA"), "storage178"),
    (("network178", "key"), "xirgspu178"),
    (("network178", "lemon"), "yifkbco178"),
    (("network178", "a"), "network178"),
    (("network178", "zz"), "mdsvnqj178"),
    (("network178", "AgentU"), "nkxjhlk178"),
    (("network178", "keyboard"), "xirxcrb178"),
    (("network178", "AA"), "network178"),
    (("latency178", "key"), "verorai178"),
    (("latency178", "lemon"), "wefsanc178"),
    (("latency178", "a"), "latency178"),
    (("latency178", "zz"), "kzsdmbx178"),
    (("latency178", "AgentU"), "lgxrgwy178"),
    (("latency178", "keyboard"), "verfbcp178"),
    (("latency178", "AA"), "latency178"),
    (("buffer178", "key"), "lydpip178"),
    (("buffer178", "lemon"), "myrtrc178"),
    (("buffer178", "a"), "buffer178"),
    (("buffer178", "zz"), "ateedq178"),
    (("buffer178", "AgentU"), "bajsxl178"),
    (("buffer178", "keyboard"), "lydgsr178"),
    (("buffer178", "AA"), "buffer178"),
    (("queue178", "key"), "aycei178"),
    (("queue178", "lemon"), "byqir178"),
    (("queue178", "a"), "queue178"),
    (("queue178", "zz"), "ptdtd178"),
    (("queue178", "AgentU"), "qaihx178"),
    (("queue178", "keyboard"), "aycvs178"),
    (("queue178", "AA"), "queue178"),
    (("worker178", "key"), "gspuip178"),
    (("worker178", "lemon"), "hsdyrc178"),
    (("worker178", "a"), "worker178"),
    (("worker178", "zz"), "vnqjdq178"),
    (("worker178", "AgentU"), "wuvxxl178"),
    (("worker178", "keyboard"), "gsplsr178"),
    (("worker178", "AA"), "worker178"),
    (("kernel178", "key"), "uipxij178"),
    (("kernel178", "lemon"), "vidbrw178"),
    (("kernel178", "a"), "kernel178"),
    (("kernel178", "zz"), "jdqmdk178"),
    (("kernel178", "AgentU"), "kkvaxf178"),
    (("kernel178", "keyboard"), "uiposl178"),
    (("kernel178", "AA"), "kernel178"),
    (("signal178", "key"), "cmexej178"),
    (("signal178", "lemon"), "dmsbnw178"),
    (("signal178", "a"), "signal178"),
    (("signal178", "zz"), "rhfmzk178"),
    (("signal178", "AgentU"), "sokatf178"),
    (("signal178", "keyboard"), "cmeool178"),
    (("signal178", "AA"), "signal178"),
    (("packet178", "key"), "zeauir178"),
    (("packet178", "lemon"), "aeoyre178"),
    (("packet178", "a"), "packet178"),
    (("packet178", "zz"), "ozbjds178"),
    (("packet178", "AgentU"), "pggxxn178"),
    (("packet178", "keyboard"), "zealst178"),
    (("packet178", "AA"), "packet178"),
    (("router178", "key"), "bssdip178"),
    (("router178", "lemon"), "csghrc178"),
    (("router178", "a"), "router178"),
    (("router178", "zz"), "qntsdq178"),
    (("router178", "AgentU"), "ruygxl178"),
    (("router178", "keyboard"), "bssusr178"),
    (("router178", "AA"), "router178"),
    (("cluster178", "key"), "mpscxcb178"),
    (("cluster178", "lemon"), "npgggpv178"),
    (("cluster178", "a"), "cluster178"),
    (("cluster178", "zz"), "bktrsdq178"),
    (("cluster178", "AgentU"), "cryfmyr178"),
    (("cluster178", "keyboard"), "mpsthei178"),
    (("cluster178", "AA"), "cluster178"),
    (("mirror178", "key"), "wmpbsp178"),
    (("mirror178", "lemon"), "xmdfbc178"),
    (("mirror178", "a"), "mirror178"),
    (("mirror178", "zz"), "lhqqnq178"),
    (("mirror178", "AgentU"), "movehl178"),
    (("mirror178", "keyboard"), "wmpscr178"),
    (("mirror178", "AA"), "mirror178"),
    (("filter178", "key"), "pmjdip178"),
    (("filter178", "lemon"), "qmxhrc178"),
    (("filter178", "a"), "filter178"),
    (("filter178", "zz"), "ehksdq178"),
    (("filter178", "AgentU"), "fopgxl178"),
    (("filter178", "keyboard"), "pmjusr178"),
    (("filter178", "AA"), "filter178"),
    (("ranking178", "key"), "belumlq178"),
    (("ranking178", "lemon"), "cezyvyk178"),
    (("ranking178", "a"), "ranking178"),
    (("ranking178", "zz"), "qzmjhmf178"),
    (("ranking178", "AgentU"), "rgrxbhg178"),
    (("ranking178", "keyboard"), "bellwnx178"),
    (("ranking178", "AA"), "ranking178"),
    (("encoding178", "key"), "orayhgxk178"),
    (("encoding178", "lemon"), "procqtrs178"),
    (("encoding178", "a"), "encoding178"),
    (("encoding178", "zz"), "dmbnchmf178"),
    (("encoding178", "AgentU"), "etgbwcnm178"),
    (("encoding178", "keyboard"), "orapriej178"),
    (("encoding178", "AA"), "encoding178"),
    (("mapping178", "key"), "wenzmlq178"),
    (("mapping178", "lemon"), "xebdvyk178"),
    (("mapping178", "a"), "mapping178"),
    (("mapping178", "zz"), "lzoohmf178"),
    (("mapping178", "AgentU"), "mgtcbhg178"),
    (("mapping178", "keyboard"), "wenqwnx178"),
    (("mapping178", "AA"), "mapping178"),
    (("record178", "key"), "biayvb178"),
    (("record178", "lemon"), "cioceo178"),
    (("record178", "a"), "record178"),
    (("record178", "zz"), "qdbnqc178"),
    (("record178", "AgentU"), "rkgbkx178"),
    (("record178", "keyboard"), "biapfd178"),
    (("record178", "AA"), "record178"),
    (("candle178", "key"), "melnpc178"),
    (("candle178", "lemon"), "nezryp178"),
    (("candle178", "a"), "candle178"),
    (("candle178", "zz"), "bzmckd178"),
    (("candle178", "AgentU"), "cgrqey178"),
    (("candle178", "keyboard"), "meleze178"),
    (("candle178", "AA"), "candle178"),
    (("thread178", "key"), "dlpoeb178"),
    (("thread178", "lemon"), "eldsno178"),
    (("thread178", "a"), "thread178"),
    (("thread178", "zz"), "sgqdzc178"),
    (("thread178", "AgentU"), "tnvrtx178"),
    (("thread178", "keyboard"), "dlpfod178"),
    (("thread178", "AA"), "thread178"),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 178: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 178: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "a"),
        "round 178: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 178: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 178: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 178: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", "AA"),
        "round 178: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "key"),
        "bssxh 178: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 178: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "a"),
        "round 178: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 178: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 178: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 178: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", "AA"),
        "round 178: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 178: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 178: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "a"),
        "round 178: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 178: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 178: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 178: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", "AA"),
        "round 178: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 178: the processor reads the record then stops", "key"),
        "bssxh 178: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 178: the processor reads the record then stops", "lemon"),
        "csgbq 178: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 178: the processor reads the record then stops", "a"),
        "round 178: the processor reads the record then stops",
    ),
    (
        ("round 178: the processor reads the record then stops", "zz"),
        "qntmc 178: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 178: the processor reads the record then stops", "AgentU"),
        "ruyaw 178: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 178: the processor reads the record then stops", "keyboard"),
        "bssor 178: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 178: the processor reads the record then stops", "AA"),
        "round 178: the processor reads the record then stops",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "key"),
        "bssxh 178: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "lemon"),
        "csgbq 178: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "a"),
        "round 178: a worker pulls the next task from the queue",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "zz"),
        "qntmc 178: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 178: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "keyboard"),
        "bssor 178: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 178: a worker pulls the next task from the queue", "AA"),
        "round 178: a worker pulls the next task from the queue",
    ),
    (
        ("round 178: signals travel through the network layer", "key"),
        "bssxh 178: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 178: signals travel through the network layer", "lemon"),
        "csgbq 178: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 178: signals travel through the network layer", "a"),
        "round 178: signals travel through the network layer",
    ),
    (
        ("round 178: signals travel through the network layer", "zz"),
        "qntmc 178: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 178: signals travel through the network layer", "AgentU"),
        "ruyaw 178: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 178: signals travel through the network layer", "keyboard"),
        "bssor 178: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 178: signals travel through the network layer", "AA"),
        "round 178: signals travel through the network layer",
    ),
    (
        ("round 178: the gateway routes each request by policy", "key"),
        "bssxh 178: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 178: the gateway routes each request by policy", "lemon"),
        "csgbq 178: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 178: the gateway routes each request by policy", "a"),
        "round 178: the gateway routes each request by policy",
    ),
    (
        ("round 178: the gateway routes each request by policy", "zz"),
        "qntmc 178: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 178: the gateway routes each request by policy", "AgentU"),
        "ruyaw 178: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 178: the gateway routes each request by policy", "keyboard"),
        "bssor 178: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 178: the gateway routes each request by policy", "AA"),
        "round 178: the gateway routes each request by policy",
    ),
    (("round 178: memory grows until the buffer is full", "key"), "bssxh 178: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 178: memory grows until the buffer is full", "lemon"), "csgbq 178: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 178: memory grows until the buffer is full", "a"), "round 178: memory grows until the buffer is full"),
    (("round 178: memory grows until the buffer is full", "zz"), "qntmc 178: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 178: memory grows until the buffer is full", "AgentU"),
        "ruyaw 178: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 178: memory grows until the buffer is full", "keyboard"),
        "bssor 178: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 178: memory grows until the buffer is full", "AA"), "round 178: memory grows until the buffer is full"),
    (("round 178: the cluster mirrors every packet twice", "key"), "bssxh 178: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 178: the cluster mirrors every packet twice", "lemon"),
        "csgbq 178: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 178: the cluster mirrors every packet twice", "a"), "round 178: the cluster mirrors every packet twice"),
    (("round 178: the cluster mirrors every packet twice", "zz"), "qntmc 178: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 178: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 178: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 178: the cluster mirrors every packet twice", "keyboard"),
        "bssor 178: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 178: the cluster mirrors every packet twice", "AA"), "round 178: the cluster mirrors every packet twice"),
    (
        ("round 178: ranking uses tokens learned from the corpus", "key"),
        "bssxh 178: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 178: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", "a"),
        "round 178: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 178: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 178: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 178: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", "AA"),
        "round 178: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 178: a long session ends when the candle dies", "key"),
        "bssxh 178: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 178: a long session ends when the candle dies", "lemon"),
        "csgbq 178: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 178: a long session ends when the candle dies", "a"),
        "round 178: a long session ends when the candle dies",
    ),
    (
        ("round 178: a long session ends when the candle dies", "zz"),
        "qntmc 178: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 178: a long session ends when the candle dies", "AgentU"),
        "ruyaw 178: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 178: a long session ends when the candle dies", "keyboard"),
        "bssor 178: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 178: a long session ends when the candle dies", "AA"),
        "round 178: a long session ends when the candle dies",
    ),
    (("round 178: encode the prompt then map the result", "key"), "bssxh 178: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 178: encode the prompt then map the result", "lemon"), "csgbq 178: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 178: encode the prompt then map the result", "a"), "round 178: encode the prompt then map the result"),
    (("round 178: encode the prompt then map the result", "zz"), "qntmc 178: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 178: encode the prompt then map the result", "AgentU"),
        "ruyaw 178: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 178: encode the prompt then map the result", "keyboard"),
        "bssor 178: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 178: encode the prompt then map the result", "AA"), "round 178: encode the prompt then map the result"),
    (("round 178: the kernel wakes the worker at dawn", "key"), "bssxh 178: rri iovlop ukocc xfo ambocb er neux"),
    (("round 178: the kernel wakes the worker at dawn", "lemon"), "csgbq 178: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 178: the kernel wakes the worker at dawn", "a"), "round 178: the kernel wakes the worker at dawn"),
    (("round 178: the kernel wakes the worker at dawn", "zz"), "qntmc 178: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 178: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 178: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 178: the kernel wakes the worker at dawn", "keyboard"), "bssor 178: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 178: the kernel wakes the worker at dawn", "AA"), "round 178: the kernel wakes the worker at dawn"),
    (("round 178: service latency drops after the patch", "key"), "bssxh 178: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 178: service latency drops after the patch", "lemon"), "csgbq 178: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 178: service latency drops after the patch", "a"), "round 178: service latency drops after the patch"),
    (("round 178: service latency drops after the patch", "zz"), "qntmc 178: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 178: service latency drops after the patch", "AgentU"),
        "ruyaw 178: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 178: service latency drops after the patch", "keyboard"),
        "bssor 178: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 178: service latency drops after the patch", "AA"), "round 178: service latency drops after the patch"),
    (
        ("round 178: the library caches every vector it sees", "key"),
        "bssxh 178: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 178: the library caches every vector it sees", "lemon"),
        "csgbq 178: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 178: the library caches every vector it sees", "a"), "round 178: the library caches every vector it sees"),
    (
        ("round 178: the library caches every vector it sees", "zz"),
        "qntmc 178: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 178: the library caches every vector it sees", "AgentU"),
        "ruyaw 178: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 178: the library caches every vector it sees", "keyboard"),
        "bssor 178: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 178: the library caches every vector it sees", "AA"),
        "round 178: the library caches every vector it sees",
    ),
    (("round 178: agents argue then the debate resolves", "key"), "bssxh 178: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 178: agents argue then the debate resolves", "lemon"), "csgbq 178: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 178: agents argue then the debate resolves", "a"), "round 178: agents argue then the debate resolves"),
    (("round 178: agents argue then the debate resolves", "zz"), "qntmc 178: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 178: agents argue then the debate resolves", "AgentU"),
        "ruyaw 178: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 178: agents argue then the debate resolves", "keyboard"),
        "bssor 178: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 178: agents argue then the debate resolves", "AA"), "round 178: agents argue then the debate resolves"),
    (("round 178: the filter keeps only strong matches", "key"), "bssxh 178: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 178: the filter keeps only strong matches", "lemon"), "csgbq 178: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 178: the filter keeps only strong matches", "a"), "round 178: the filter keeps only strong matches"),
    (("round 178: the filter keeps only strong matches", "zz"), "qntmc 178: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 178: the filter keeps only strong matches", "AgentU"), "ruyaw 178: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 178: the filter keeps only strong matches", "keyboard"),
        "bssor 178: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 178: the filter keeps only strong matches", "AA"), "round 178: the filter keeps only strong matches"),
    (("round 178: the model answers with a short reply", "key"), "bssxh 178: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 178: the model answers with a short reply", "lemon"), "csgbq 178: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 178: the model answers with a short reply", "a"), "round 178: the model answers with a short reply"),
    (("round 178: the model answers with a short reply", "zz"), "qntmc 178: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 178: the model answers with a short reply", "AgentU"), "ruyaw 178: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 178: the model answers with a short reply", "keyboard"),
        "bssor 178: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 178: the model answers with a short reply", "AA"), "round 178: the model answers with a short reply"),
    (
        ("round 178: the recorder stores the reasoning trace", "key"),
        "bssxh 178: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 178: the recorder stores the reasoning trace", "lemon"),
        "csgbq 178: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 178: the recorder stores the reasoning trace", "a"), "round 178: the recorder stores the reasoning trace"),
    (
        ("round 178: the recorder stores the reasoning trace", "zz"),
        "qntmc 178: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 178: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 178: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 178: the recorder stores the reasoning trace", "keyboard"),
        "bssor 178: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 178: the recorder stores the reasoning trace", "AA"),
        "round 178: the recorder stores the reasoning trace",
    ),
    (("round 178: the angel watches the processor run", "key"), "bssxh 178: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 178: the angel watches the processor run", "lemon"), "csgbq 178: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 178: the angel watches the processor run", "a"), "round 178: the angel watches the processor run"),
    (("round 178: the angel watches the processor run", "zz"), "qntmc 178: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 178: the angel watches the processor run", "AgentU"), "ruyaw 178: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 178: the angel watches the processor run", "keyboard"), "bssor 178: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 178: the angel watches the processor run", "AA"), "round 178: the angel watches the processor run"),
    (("round 178: angle of the vector decides the match", "key"), "bssxh 178: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 178: angle of the vector decides the match", "lemon"), "csgbq 178: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 178: angle of the vector decides the match", "a"), "round 178: angle of the vector decides the match"),
    (("round 178: angle of the vector decides the match", "zz"), "qntmc 178: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 178: angle of the vector decides the match", "AgentU"),
        "ruyaw 178: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 178: angle of the vector decides the match", "keyboard"),
        "bssor 178: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 178: angle of the vector decides the match", "AA"), "round 178: angle of the vector decides the match"),
    (
        ("round 178: the candle burns twice as long at night", "key"),
        "bssxh 178: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 178: the candle burns twice as long at night", "lemon"),
        "csgbq 178: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 178: the candle burns twice as long at night", "a"), "round 178: the candle burns twice as long at night"),
    (
        ("round 178: the candle burns twice as long at night", "zz"),
        "qntmc 178: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 178: the candle burns twice as long at night", "AgentU"),
        "ruyaw 178: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 178: the candle burns twice as long at night", "keyboard"),
        "bssor 178: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 178: the candle burns twice as long at night", "AA"),
        "round 178: the candle burns twice as long at night",
    ),
    (("round 178: a mirror of the universe in one line", "key"), "bssxh 178: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 178: a mirror of the universe in one line", "lemon"), "csgbq 178: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 178: a mirror of the universe in one line", "a"), "round 178: a mirror of the universe in one line"),
    (("round 178: a mirror of the universe in one line", "zz"), "qntmc 178: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 178: a mirror of the universe in one line", "AgentU"), "ruyaw 178: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 178: a mirror of the universe in one line", "keyboard"),
        "bssor 178: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 178: a mirror of the universe in one line", "AA"), "round 178: a mirror of the universe in one line"),
    (("round 178: the queue drains before the storm", "key"), "bssxh 178: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 178: the queue drains before the storm", "lemon"), "csgbq 178: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 178: the queue drains before the storm", "a"), "round 178: the queue drains before the storm"),
    (("round 178: the queue drains before the storm", "zz"), "qntmc 178: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 178: the queue drains before the storm", "AgentU"), "ruyaw 178: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 178: the queue drains before the storm", "keyboard"), "bssor 178: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 178: the queue drains before the storm", "AA"), "round 178: the queue drains before the storm"),
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
