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
    (("kitten163", "key"), "umrdil163"),
    (("kitten163", "lemon"), "vmfhry163"),
    (("kitten163", "a"), "kitten163"),
    (("kitten163", "zz"), "jhssdm163"),
    (("kitten163", "AgentU"), "koxgxh163"),
    (("kitten163", "keyboard"), "umrusn163"),
    (("kitten163", "AA"), "kitten163"),
    (("sitting163", "key"), "cmrdmlq163"),
    (("sitting163", "lemon"), "dmfhvyk163"),
    (("sitting163", "a"), "sitting163"),
    (("sitting163", "zz"), "rhsshmf163"),
    (("sitting163", "AgentU"), "soxgbhg163"),
    (("sitting163", "keyboard"), "cmruwnx163"),
    (("sitting163", "AA"), "sitting163"),
    (("agent163", "key"), "kkcxx163"),
    (("agent163", "lemon"), "lkqbg163"),
    (("agent163", "a"), "agent163"),
    (("agent163", "zz"), "zfdms163"),
    (("agent163", "AgentU"), "amiam163"),
    (("agent163", "keyboard"), "kkcoh163"),
    (("agent163", "AA"), "agent163"),
    (("angle163", "key"), "krevi163"),
    (("angle163", "lemon"), "lrszr163"),
    (("angle163", "a"), "angle163"),
    (("angle163", "zz"), "zmfkd163"),
    (("angle163", "AgentU"), "atkyx163"),
    (("angle163", "keyboard"), "krems163"),
    (("angle163", "AA"), "angle163"),
    (("universe163", "key"), "ergfipci163"),
    (("universe163", "lemon"), "frujrcwq163"),
    (("universe163", "a"), "universe163"),
    (("universe163", "zz"), "tmhudqrd163"),
    (("universe163", "AgentU"), "utmixlsk163"),
    (("universe163", "keyboard"), "ergwsrjh163"),
    (("universe163", "AA"), "universe163"),
    (("memory163", "key"), "wikyvw163"),
    (("memory163", "lemon"), "xiycej163"),
    (("memory163", "a"), "memory163"),
    (("memory163", "zz"), "ldlnqx163"),
    (("memory163", "AgentU"), "mkqbks163"),
    (("memory163", "keyboard"), "wikpfy163"),
    (("memory163", "AA"), "memory163"),
    (("stream163", "key"), "cxpoek163"),
    (("stream163", "lemon"), "dxdsnx163"),
    (("stream163", "a"), "stream163"),
    (("stream163", "zz"), "rsqdzl163"),
    (("stream163", "AgentU"), "szvrtg163"),
    (("stream163", "keyboard"), "cxpfom163"),
    (("stream163", "AA"), "stream163"),
    (("context163", "key"), "msldivd163"),
    (("context163", "lemon"), "nszhrix163"),
    (("context163", "a"), "context163"),
    (("context163", "zz"), "bnmsdws163"),
    (("context163", "AgentU"), "curgxrt163"),
    (("context163", "keyboard"), "mslusxk163"),
    (("context163", "AA"), "context163"),
    (("knowledge163", "key"), "urmgpcnkc163"),
    (("knowledge163", "lemon"), "vrakyphss163"),
    (("knowledge163", "a"), "knowledge163"),
    (("knowledge163", "zz"), "jmnvkdcfd163"),
    (("knowledge163", "AgentU"), "ktsjeydmi163"),
    (("knowledge163", "keyboard"), "urmxzeujo163"),
    (("knowledge163", "AA"), "knowledge163"),
    (("vector163", "key"), "fiadsp163"),
    (("vector163", "lemon"), "giohbc163"),
    (("vector163", "a"), "vector163"),
    (("vector163", "zz"), "udbsnq163"),
    (("vector163", "AgentU"), "vkgghl163"),
    (("vector163", "keyboard"), "fiaucr163"),
    (("vector163", "AA"), "vector163"),
    (("processor163", "key"), "zvmmiqcsp163"),
    (("processor163", "lemon"), "avaqrdwaf163"),
    (("processor163", "a"), "processor163"),
    (("processor163", "zz"), "oqnbdrrnq163"),
    (("processor163", "AgentU"), "pxspxmsuv163"),
    (("processor163", "keyboard"), "zvmdssjrb163"),
    (("processor163", "AA"), "processor163"),
    (("reasoning163", "key"), "biycslsre163"),
    (("reasoning163", "lemon"), "cimgbymzu163"),
    (("reasoning163", "a"), "reasoning163"),
    (("reasoning163", "zz"), "qdzrnmhmf163"),
    (("reasoning163", "AgentU"), "rkefhhitk163"),
    (("reasoning163", "keyboard"), "biytcnzqq163"),
    (("reasoning163", "AA"), "reasoning163"),
    (("machine163", "key"), "wearmlo163"),
    (("machine163", "lemon"), "xeovvyi163"),
    (("machine163", "a"), "machine163"),
    (("machine163", "zz"), "lzbghmd163"),
    (("machine163", "AgentU"), "mggubhe163"),
    (("machine163", "keyboard"), "weaiwnv163"),
    (("machine163", "AA"), "machine163"),
    (("learning163", "key"), "viybrgxk163"),
    (("learning163", "lemon"), "wimfatrs163"),
    (("learning163", "a"), "learning163"),
    (("learning163", "zz"), "kdzqmhmf163"),
    (("learning163", "AgentU"), "lkeegcnm163"),
    (("learning163", "keyboard"), "viysbiej163"),
    (("learning163", "AA"), "learning163"),
    (("model163", "key"), "wsbop163"),
    (("model163", "lemon"), "xspsy163"),
    (("model163", "a"), "model163"),
    (("model163", "zz"), "lncdk163"),
    (("model163", "AgentU"), "muhre163"),
    (("model163", "keyboard"), "wsbfz163"),
    (("model163", "AA"), "model163"),
    (("token163", "key"), "dsior163"),
    (("token163", "lemon"), "eswsa163"),
    (("token163", "a"), "token163"),
    (("token163", "zz"), "snjdm163"),
    (("token163", "AgentU"), "tuorg163"),
    (("token163", "keyboard"), "dsifb163"),
    (("token163", "AA"), "token163"),
    (("prompt163", "key"), "zvmwtr163"),
    (("prompt163", "lemon"), "avaace163"),
    (("prompt163", "a"), "prompt163"),
    (("prompt163", "zz"), "oqnlos163"),
    (("prompt163", "AgentU"), "pxszin163"),
    (("prompt163", "keyboard"), "zvmndt163"),
    (("prompt163", "AA"), "prompt163"),
    (("session163", "key"), "ciqcmmx163"),
    (("session163", "lemon"), "diegvzr163"),
    (("session163", "a"), "session163"),
    (("session163", "zz"), "rdrrhnm163"),
    (("session163", "AgentU"), "skwfbin163"),
    (("session163", "keyboard"), "ciqtwoe163"),
    (("session163", "AA"), "session163"),
    (("library163", "key"), "vmzbepi163"),
    (("library163", "lemon"), "wmnfncc163"),
    (("library163", "a"), "library163"),
    (("library163", "zz"), "khaqzqx163"),
    (("library163", "AgentU"), "lofetly163"),
    (("library163", "keyboard"), "vmzsorp163"),
    (("library163", "AA"), "library163"),
    (("service163", "key"), "cipfmao163"),
    (("service163", "lemon"), "didjvni163"),
    (("service163", "a"), "service163"),
    (("service163", "zz"), "rdquhbd163"),
    (("service163", "AgentU"), "skvibwe163"),
    (("service163", "keyboard"), "cipwwcv163"),
    (("service163", "AA"), "service163"),
    (("gateway163", "key"), "qeroayi163"),
    (("gateway163", "lemon"), "refsjlc163"),
    (("gateway163", "a"), "gateway163"),
    (("gateway163", "zz"), "fzsdvzx163"),
    (("gateway163", "AgentU"), "ggxrpuy163"),
    (("gateway163", "keyboard"), "qerfkap163"),
    (("gateway163", "AA"), "gateway163"),
    (("storage163", "key"), "cxmbeeo163"),
    (("storage163", "lemon"), "dxafnri163"),
    (("storage163", "a"), "storage163"),
    (("storage163", "zz"), "rsnqzfd163"),
    (("storage163", "AgentU"), "szsetae163"),
    (("storage163", "keyboard"), "cxmsogv163"),
    (("storage163", "AA"), "storage163"),
    (("network163", "key"), "xirgspu163"),
    (("network163", "lemon"), "yifkbco163"),
    (("network163", "a"), "network163"),
    (("network163", "zz"), "mdsvnqj163"),
    (("network163", "AgentU"), "nkxjhlk163"),
    (("network163", "keyboard"), "xirxcrb163"),
    (("network163", "AA"), "network163"),
    (("latency163", "key"), "verorai163"),
    (("latency163", "lemon"), "wefsanc163"),
    (("latency163", "a"), "latency163"),
    (("latency163", "zz"), "kzsdmbx163"),
    (("latency163", "AgentU"), "lgxrgwy163"),
    (("latency163", "keyboard"), "verfbcp163"),
    (("latency163", "AA"), "latency163"),
    (("buffer163", "key"), "lydpip163"),
    (("buffer163", "lemon"), "myrtrc163"),
    (("buffer163", "a"), "buffer163"),
    (("buffer163", "zz"), "ateedq163"),
    (("buffer163", "AgentU"), "bajsxl163"),
    (("buffer163", "keyboard"), "lydgsr163"),
    (("buffer163", "AA"), "buffer163"),
    (("queue163", "key"), "aycei163"),
    (("queue163", "lemon"), "byqir163"),
    (("queue163", "a"), "queue163"),
    (("queue163", "zz"), "ptdtd163"),
    (("queue163", "AgentU"), "qaihx163"),
    (("queue163", "keyboard"), "aycvs163"),
    (("queue163", "AA"), "queue163"),
    (("worker163", "key"), "gspuip163"),
    (("worker163", "lemon"), "hsdyrc163"),
    (("worker163", "a"), "worker163"),
    (("worker163", "zz"), "vnqjdq163"),
    (("worker163", "AgentU"), "wuvxxl163"),
    (("worker163", "keyboard"), "gsplsr163"),
    (("worker163", "AA"), "worker163"),
    (("kernel163", "key"), "uipxij163"),
    (("kernel163", "lemon"), "vidbrw163"),
    (("kernel163", "a"), "kernel163"),
    (("kernel163", "zz"), "jdqmdk163"),
    (("kernel163", "AgentU"), "kkvaxf163"),
    (("kernel163", "keyboard"), "uiposl163"),
    (("kernel163", "AA"), "kernel163"),
    (("signal163", "key"), "cmexej163"),
    (("signal163", "lemon"), "dmsbnw163"),
    (("signal163", "a"), "signal163"),
    (("signal163", "zz"), "rhfmzk163"),
    (("signal163", "AgentU"), "sokatf163"),
    (("signal163", "keyboard"), "cmeool163"),
    (("signal163", "AA"), "signal163"),
    (("packet163", "key"), "zeauir163"),
    (("packet163", "lemon"), "aeoyre163"),
    (("packet163", "a"), "packet163"),
    (("packet163", "zz"), "ozbjds163"),
    (("packet163", "AgentU"), "pggxxn163"),
    (("packet163", "keyboard"), "zealst163"),
    (("packet163", "AA"), "packet163"),
    (("router163", "key"), "bssdip163"),
    (("router163", "lemon"), "csghrc163"),
    (("router163", "a"), "router163"),
    (("router163", "zz"), "qntsdq163"),
    (("router163", "AgentU"), "ruygxl163"),
    (("router163", "keyboard"), "bssusr163"),
    (("router163", "AA"), "router163"),
    (("cluster163", "key"), "mpscxcb163"),
    (("cluster163", "lemon"), "npgggpv163"),
    (("cluster163", "a"), "cluster163"),
    (("cluster163", "zz"), "bktrsdq163"),
    (("cluster163", "AgentU"), "cryfmyr163"),
    (("cluster163", "keyboard"), "mpsthei163"),
    (("cluster163", "AA"), "cluster163"),
    (("mirror163", "key"), "wmpbsp163"),
    (("mirror163", "lemon"), "xmdfbc163"),
    (("mirror163", "a"), "mirror163"),
    (("mirror163", "zz"), "lhqqnq163"),
    (("mirror163", "AgentU"), "movehl163"),
    (("mirror163", "keyboard"), "wmpscr163"),
    (("mirror163", "AA"), "mirror163"),
    (("filter163", "key"), "pmjdip163"),
    (("filter163", "lemon"), "qmxhrc163"),
    (("filter163", "a"), "filter163"),
    (("filter163", "zz"), "ehksdq163"),
    (("filter163", "AgentU"), "fopgxl163"),
    (("filter163", "keyboard"), "pmjusr163"),
    (("filter163", "AA"), "filter163"),
    (("ranking163", "key"), "belumlq163"),
    (("ranking163", "lemon"), "cezyvyk163"),
    (("ranking163", "a"), "ranking163"),
    (("ranking163", "zz"), "qzmjhmf163"),
    (("ranking163", "AgentU"), "rgrxbhg163"),
    (("ranking163", "keyboard"), "bellwnx163"),
    (("ranking163", "AA"), "ranking163"),
    (("encoding163", "key"), "orayhgxk163"),
    (("encoding163", "lemon"), "procqtrs163"),
    (("encoding163", "a"), "encoding163"),
    (("encoding163", "zz"), "dmbnchmf163"),
    (("encoding163", "AgentU"), "etgbwcnm163"),
    (("encoding163", "keyboard"), "orapriej163"),
    (("encoding163", "AA"), "encoding163"),
    (("mapping163", "key"), "wenzmlq163"),
    (("mapping163", "lemon"), "xebdvyk163"),
    (("mapping163", "a"), "mapping163"),
    (("mapping163", "zz"), "lzoohmf163"),
    (("mapping163", "AgentU"), "mgtcbhg163"),
    (("mapping163", "keyboard"), "wenqwnx163"),
    (("mapping163", "AA"), "mapping163"),
    (("record163", "key"), "biayvb163"),
    (("record163", "lemon"), "cioceo163"),
    (("record163", "a"), "record163"),
    (("record163", "zz"), "qdbnqc163"),
    (("record163", "AgentU"), "rkgbkx163"),
    (("record163", "keyboard"), "biapfd163"),
    (("record163", "AA"), "record163"),
    (("candle163", "key"), "melnpc163"),
    (("candle163", "lemon"), "nezryp163"),
    (("candle163", "a"), "candle163"),
    (("candle163", "zz"), "bzmckd163"),
    (("candle163", "AgentU"), "cgrqey163"),
    (("candle163", "keyboard"), "meleze163"),
    (("candle163", "AA"), "candle163"),
    (("thread163", "key"), "dlpoeb163"),
    (("thread163", "lemon"), "eldsno163"),
    (("thread163", "a"), "thread163"),
    (("thread163", "zz"), "sgqdzc163"),
    (("thread163", "AgentU"), "tnvrtx163"),
    (("thread163", "keyboard"), "dlpfod163"),
    (("thread163", "AA"), "thread163"),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 163: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 163: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "a"),
        "round 163: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 163: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 163: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 163: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", "AA"),
        "round 163: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "key"),
        "bssxh 163: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 163: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "a"),
        "round 163: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 163: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 163: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 163: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", "AA"),
        "round 163: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 163: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 163: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "a"),
        "round 163: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 163: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 163: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 163: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", "AA"),
        "round 163: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 163: the processor reads the record then stops", "key"),
        "bssxh 163: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 163: the processor reads the record then stops", "lemon"),
        "csgbq 163: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 163: the processor reads the record then stops", "a"),
        "round 163: the processor reads the record then stops",
    ),
    (
        ("round 163: the processor reads the record then stops", "zz"),
        "qntmc 163: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 163: the processor reads the record then stops", "AgentU"),
        "ruyaw 163: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 163: the processor reads the record then stops", "keyboard"),
        "bssor 163: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 163: the processor reads the record then stops", "AA"),
        "round 163: the processor reads the record then stops",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "key"),
        "bssxh 163: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "lemon"),
        "csgbq 163: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "a"),
        "round 163: a worker pulls the next task from the queue",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "zz"),
        "qntmc 163: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 163: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "keyboard"),
        "bssor 163: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 163: a worker pulls the next task from the queue", "AA"),
        "round 163: a worker pulls the next task from the queue",
    ),
    (
        ("round 163: signals travel through the network layer", "key"),
        "bssxh 163: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 163: signals travel through the network layer", "lemon"),
        "csgbq 163: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 163: signals travel through the network layer", "a"),
        "round 163: signals travel through the network layer",
    ),
    (
        ("round 163: signals travel through the network layer", "zz"),
        "qntmc 163: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 163: signals travel through the network layer", "AgentU"),
        "ruyaw 163: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 163: signals travel through the network layer", "keyboard"),
        "bssor 163: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 163: signals travel through the network layer", "AA"),
        "round 163: signals travel through the network layer",
    ),
    (
        ("round 163: the gateway routes each request by policy", "key"),
        "bssxh 163: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 163: the gateway routes each request by policy", "lemon"),
        "csgbq 163: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 163: the gateway routes each request by policy", "a"),
        "round 163: the gateway routes each request by policy",
    ),
    (
        ("round 163: the gateway routes each request by policy", "zz"),
        "qntmc 163: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 163: the gateway routes each request by policy", "AgentU"),
        "ruyaw 163: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 163: the gateway routes each request by policy", "keyboard"),
        "bssor 163: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 163: the gateway routes each request by policy", "AA"),
        "round 163: the gateway routes each request by policy",
    ),
    (("round 163: memory grows until the buffer is full", "key"), "bssxh 163: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 163: memory grows until the buffer is full", "lemon"), "csgbq 163: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 163: memory grows until the buffer is full", "a"), "round 163: memory grows until the buffer is full"),
    (("round 163: memory grows until the buffer is full", "zz"), "qntmc 163: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 163: memory grows until the buffer is full", "AgentU"),
        "ruyaw 163: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 163: memory grows until the buffer is full", "keyboard"),
        "bssor 163: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 163: memory grows until the buffer is full", "AA"), "round 163: memory grows until the buffer is full"),
    (("round 163: the cluster mirrors every packet twice", "key"), "bssxh 163: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 163: the cluster mirrors every packet twice", "lemon"),
        "csgbq 163: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 163: the cluster mirrors every packet twice", "a"), "round 163: the cluster mirrors every packet twice"),
    (("round 163: the cluster mirrors every packet twice", "zz"), "qntmc 163: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 163: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 163: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 163: the cluster mirrors every packet twice", "keyboard"),
        "bssor 163: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 163: the cluster mirrors every packet twice", "AA"), "round 163: the cluster mirrors every packet twice"),
    (
        ("round 163: ranking uses tokens learned from the corpus", "key"),
        "bssxh 163: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 163: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", "a"),
        "round 163: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 163: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 163: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 163: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", "AA"),
        "round 163: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 163: a long session ends when the candle dies", "key"),
        "bssxh 163: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 163: a long session ends when the candle dies", "lemon"),
        "csgbq 163: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 163: a long session ends when the candle dies", "a"),
        "round 163: a long session ends when the candle dies",
    ),
    (
        ("round 163: a long session ends when the candle dies", "zz"),
        "qntmc 163: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 163: a long session ends when the candle dies", "AgentU"),
        "ruyaw 163: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 163: a long session ends when the candle dies", "keyboard"),
        "bssor 163: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 163: a long session ends when the candle dies", "AA"),
        "round 163: a long session ends when the candle dies",
    ),
    (("round 163: encode the prompt then map the result", "key"), "bssxh 163: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 163: encode the prompt then map the result", "lemon"), "csgbq 163: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 163: encode the prompt then map the result", "a"), "round 163: encode the prompt then map the result"),
    (("round 163: encode the prompt then map the result", "zz"), "qntmc 163: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 163: encode the prompt then map the result", "AgentU"),
        "ruyaw 163: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 163: encode the prompt then map the result", "keyboard"),
        "bssor 163: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 163: encode the prompt then map the result", "AA"), "round 163: encode the prompt then map the result"),
    (("round 163: the kernel wakes the worker at dawn", "key"), "bssxh 163: rri iovlop ukocc xfo ambocb er neux"),
    (("round 163: the kernel wakes the worker at dawn", "lemon"), "csgbq 163: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 163: the kernel wakes the worker at dawn", "a"), "round 163: the kernel wakes the worker at dawn"),
    (("round 163: the kernel wakes the worker at dawn", "zz"), "qntmc 163: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 163: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 163: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 163: the kernel wakes the worker at dawn", "keyboard"), "bssor 163: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 163: the kernel wakes the worker at dawn", "AA"), "round 163: the kernel wakes the worker at dawn"),
    (("round 163: service latency drops after the patch", "key"), "bssxh 163: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 163: service latency drops after the patch", "lemon"), "csgbq 163: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 163: service latency drops after the patch", "a"), "round 163: service latency drops after the patch"),
    (("round 163: service latency drops after the patch", "zz"), "qntmc 163: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 163: service latency drops after the patch", "AgentU"),
        "ruyaw 163: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 163: service latency drops after the patch", "keyboard"),
        "bssor 163: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 163: service latency drops after the patch", "AA"), "round 163: service latency drops after the patch"),
    (
        ("round 163: the library caches every vector it sees", "key"),
        "bssxh 163: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 163: the library caches every vector it sees", "lemon"),
        "csgbq 163: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 163: the library caches every vector it sees", "a"), "round 163: the library caches every vector it sees"),
    (
        ("round 163: the library caches every vector it sees", "zz"),
        "qntmc 163: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 163: the library caches every vector it sees", "AgentU"),
        "ruyaw 163: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 163: the library caches every vector it sees", "keyboard"),
        "bssor 163: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 163: the library caches every vector it sees", "AA"),
        "round 163: the library caches every vector it sees",
    ),
    (("round 163: agents argue then the debate resolves", "key"), "bssxh 163: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 163: agents argue then the debate resolves", "lemon"), "csgbq 163: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 163: agents argue then the debate resolves", "a"), "round 163: agents argue then the debate resolves"),
    (("round 163: agents argue then the debate resolves", "zz"), "qntmc 163: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 163: agents argue then the debate resolves", "AgentU"),
        "ruyaw 163: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 163: agents argue then the debate resolves", "keyboard"),
        "bssor 163: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 163: agents argue then the debate resolves", "AA"), "round 163: agents argue then the debate resolves"),
    (("round 163: the filter keeps only strong matches", "key"), "bssxh 163: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 163: the filter keeps only strong matches", "lemon"), "csgbq 163: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 163: the filter keeps only strong matches", "a"), "round 163: the filter keeps only strong matches"),
    (("round 163: the filter keeps only strong matches", "zz"), "qntmc 163: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 163: the filter keeps only strong matches", "AgentU"), "ruyaw 163: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 163: the filter keeps only strong matches", "keyboard"),
        "bssor 163: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 163: the filter keeps only strong matches", "AA"), "round 163: the filter keeps only strong matches"),
    (("round 163: the model answers with a short reply", "key"), "bssxh 163: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 163: the model answers with a short reply", "lemon"), "csgbq 163: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 163: the model answers with a short reply", "a"), "round 163: the model answers with a short reply"),
    (("round 163: the model answers with a short reply", "zz"), "qntmc 163: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 163: the model answers with a short reply", "AgentU"), "ruyaw 163: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 163: the model answers with a short reply", "keyboard"),
        "bssor 163: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 163: the model answers with a short reply", "AA"), "round 163: the model answers with a short reply"),
    (
        ("round 163: the recorder stores the reasoning trace", "key"),
        "bssxh 163: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 163: the recorder stores the reasoning trace", "lemon"),
        "csgbq 163: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 163: the recorder stores the reasoning trace", "a"), "round 163: the recorder stores the reasoning trace"),
    (
        ("round 163: the recorder stores the reasoning trace", "zz"),
        "qntmc 163: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 163: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 163: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 163: the recorder stores the reasoning trace", "keyboard"),
        "bssor 163: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 163: the recorder stores the reasoning trace", "AA"),
        "round 163: the recorder stores the reasoning trace",
    ),
    (("round 163: the angel watches the processor run", "key"), "bssxh 163: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 163: the angel watches the processor run", "lemon"), "csgbq 163: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 163: the angel watches the processor run", "a"), "round 163: the angel watches the processor run"),
    (("round 163: the angel watches the processor run", "zz"), "qntmc 163: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 163: the angel watches the processor run", "AgentU"), "ruyaw 163: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 163: the angel watches the processor run", "keyboard"), "bssor 163: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 163: the angel watches the processor run", "AA"), "round 163: the angel watches the processor run"),
    (("round 163: angle of the vector decides the match", "key"), "bssxh 163: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 163: angle of the vector decides the match", "lemon"), "csgbq 163: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 163: angle of the vector decides the match", "a"), "round 163: angle of the vector decides the match"),
    (("round 163: angle of the vector decides the match", "zz"), "qntmc 163: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 163: angle of the vector decides the match", "AgentU"),
        "ruyaw 163: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 163: angle of the vector decides the match", "keyboard"),
        "bssor 163: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 163: angle of the vector decides the match", "AA"), "round 163: angle of the vector decides the match"),
    (
        ("round 163: the candle burns twice as long at night", "key"),
        "bssxh 163: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 163: the candle burns twice as long at night", "lemon"),
        "csgbq 163: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 163: the candle burns twice as long at night", "a"), "round 163: the candle burns twice as long at night"),
    (
        ("round 163: the candle burns twice as long at night", "zz"),
        "qntmc 163: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 163: the candle burns twice as long at night", "AgentU"),
        "ruyaw 163: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 163: the candle burns twice as long at night", "keyboard"),
        "bssor 163: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 163: the candle burns twice as long at night", "AA"),
        "round 163: the candle burns twice as long at night",
    ),
    (("round 163: a mirror of the universe in one line", "key"), "bssxh 163: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 163: a mirror of the universe in one line", "lemon"), "csgbq 163: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 163: a mirror of the universe in one line", "a"), "round 163: a mirror of the universe in one line"),
    (("round 163: a mirror of the universe in one line", "zz"), "qntmc 163: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 163: a mirror of the universe in one line", "AgentU"), "ruyaw 163: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 163: a mirror of the universe in one line", "keyboard"),
        "bssor 163: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 163: a mirror of the universe in one line", "AA"), "round 163: a mirror of the universe in one line"),
    (("round 163: the queue drains before the storm", "key"), "bssxh 163: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 163: the queue drains before the storm", "lemon"), "csgbq 163: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 163: the queue drains before the storm", "a"), "round 163: the queue drains before the storm"),
    (("round 163: the queue drains before the storm", "zz"), "qntmc 163: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 163: the queue drains before the storm", "AgentU"), "ruyaw 163: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 163: the queue drains before the storm", "keyboard"), "bssor 163: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 163: the queue drains before the storm", "AA"), "round 163: the queue drains before the storm"),
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
