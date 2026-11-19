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
    (("kitten192", "key"), "umrdil192"),
    (("kitten192", "lemon"), "vmfhry192"),
    (("kitten192", "a"), "kitten192"),
    (("kitten192", "zz"), "jhssdm192"),
    (("kitten192", "AgentU"), "koxgxh192"),
    (("kitten192", "keyboard"), "umrusn192"),
    (("kitten192", "AA"), "kitten192"),
    (("sitting192", "key"), "cmrdmlq192"),
    (("sitting192", "lemon"), "dmfhvyk192"),
    (("sitting192", "a"), "sitting192"),
    (("sitting192", "zz"), "rhsshmf192"),
    (("sitting192", "AgentU"), "soxgbhg192"),
    (("sitting192", "keyboard"), "cmruwnx192"),
    (("sitting192", "AA"), "sitting192"),
    (("agent192", "key"), "kkcxx192"),
    (("agent192", "lemon"), "lkqbg192"),
    (("agent192", "a"), "agent192"),
    (("agent192", "zz"), "zfdms192"),
    (("agent192", "AgentU"), "amiam192"),
    (("agent192", "keyboard"), "kkcoh192"),
    (("agent192", "AA"), "agent192"),
    (("angle192", "key"), "krevi192"),
    (("angle192", "lemon"), "lrszr192"),
    (("angle192", "a"), "angle192"),
    (("angle192", "zz"), "zmfkd192"),
    (("angle192", "AgentU"), "atkyx192"),
    (("angle192", "keyboard"), "krems192"),
    (("angle192", "AA"), "angle192"),
    (("universe192", "key"), "ergfipci192"),
    (("universe192", "lemon"), "frujrcwq192"),
    (("universe192", "a"), "universe192"),
    (("universe192", "zz"), "tmhudqrd192"),
    (("universe192", "AgentU"), "utmixlsk192"),
    (("universe192", "keyboard"), "ergwsrjh192"),
    (("universe192", "AA"), "universe192"),
    (("memory192", "key"), "wikyvw192"),
    (("memory192", "lemon"), "xiycej192"),
    (("memory192", "a"), "memory192"),
    (("memory192", "zz"), "ldlnqx192"),
    (("memory192", "AgentU"), "mkqbks192"),
    (("memory192", "keyboard"), "wikpfy192"),
    (("memory192", "AA"), "memory192"),
    (("stream192", "key"), "cxpoek192"),
    (("stream192", "lemon"), "dxdsnx192"),
    (("stream192", "a"), "stream192"),
    (("stream192", "zz"), "rsqdzl192"),
    (("stream192", "AgentU"), "szvrtg192"),
    (("stream192", "keyboard"), "cxpfom192"),
    (("stream192", "AA"), "stream192"),
    (("context192", "key"), "msldivd192"),
    (("context192", "lemon"), "nszhrix192"),
    (("context192", "a"), "context192"),
    (("context192", "zz"), "bnmsdws192"),
    (("context192", "AgentU"), "curgxrt192"),
    (("context192", "keyboard"), "mslusxk192"),
    (("context192", "AA"), "context192"),
    (("knowledge192", "key"), "urmgpcnkc192"),
    (("knowledge192", "lemon"), "vrakyphss192"),
    (("knowledge192", "a"), "knowledge192"),
    (("knowledge192", "zz"), "jmnvkdcfd192"),
    (("knowledge192", "AgentU"), "ktsjeydmi192"),
    (("knowledge192", "keyboard"), "urmxzeujo192"),
    (("knowledge192", "AA"), "knowledge192"),
    (("vector192", "key"), "fiadsp192"),
    (("vector192", "lemon"), "giohbc192"),
    (("vector192", "a"), "vector192"),
    (("vector192", "zz"), "udbsnq192"),
    (("vector192", "AgentU"), "vkgghl192"),
    (("vector192", "keyboard"), "fiaucr192"),
    (("vector192", "AA"), "vector192"),
    (("processor192", "key"), "zvmmiqcsp192"),
    (("processor192", "lemon"), "avaqrdwaf192"),
    (("processor192", "a"), "processor192"),
    (("processor192", "zz"), "oqnbdrrnq192"),
    (("processor192", "AgentU"), "pxspxmsuv192"),
    (("processor192", "keyboard"), "zvmdssjrb192"),
    (("processor192", "AA"), "processor192"),
    (("reasoning192", "key"), "biycslsre192"),
    (("reasoning192", "lemon"), "cimgbymzu192"),
    (("reasoning192", "a"), "reasoning192"),
    (("reasoning192", "zz"), "qdzrnmhmf192"),
    (("reasoning192", "AgentU"), "rkefhhitk192"),
    (("reasoning192", "keyboard"), "biytcnzqq192"),
    (("reasoning192", "AA"), "reasoning192"),
    (("machine192", "key"), "wearmlo192"),
    (("machine192", "lemon"), "xeovvyi192"),
    (("machine192", "a"), "machine192"),
    (("machine192", "zz"), "lzbghmd192"),
    (("machine192", "AgentU"), "mggubhe192"),
    (("machine192", "keyboard"), "weaiwnv192"),
    (("machine192", "AA"), "machine192"),
    (("learning192", "key"), "viybrgxk192"),
    (("learning192", "lemon"), "wimfatrs192"),
    (("learning192", "a"), "learning192"),
    (("learning192", "zz"), "kdzqmhmf192"),
    (("learning192", "AgentU"), "lkeegcnm192"),
    (("learning192", "keyboard"), "viysbiej192"),
    (("learning192", "AA"), "learning192"),
    (("model192", "key"), "wsbop192"),
    (("model192", "lemon"), "xspsy192"),
    (("model192", "a"), "model192"),
    (("model192", "zz"), "lncdk192"),
    (("model192", "AgentU"), "muhre192"),
    (("model192", "keyboard"), "wsbfz192"),
    (("model192", "AA"), "model192"),
    (("token192", "key"), "dsior192"),
    (("token192", "lemon"), "eswsa192"),
    (("token192", "a"), "token192"),
    (("token192", "zz"), "snjdm192"),
    (("token192", "AgentU"), "tuorg192"),
    (("token192", "keyboard"), "dsifb192"),
    (("token192", "AA"), "token192"),
    (("prompt192", "key"), "zvmwtr192"),
    (("prompt192", "lemon"), "avaace192"),
    (("prompt192", "a"), "prompt192"),
    (("prompt192", "zz"), "oqnlos192"),
    (("prompt192", "AgentU"), "pxszin192"),
    (("prompt192", "keyboard"), "zvmndt192"),
    (("prompt192", "AA"), "prompt192"),
    (("session192", "key"), "ciqcmmx192"),
    (("session192", "lemon"), "diegvzr192"),
    (("session192", "a"), "session192"),
    (("session192", "zz"), "rdrrhnm192"),
    (("session192", "AgentU"), "skwfbin192"),
    (("session192", "keyboard"), "ciqtwoe192"),
    (("session192", "AA"), "session192"),
    (("library192", "key"), "vmzbepi192"),
    (("library192", "lemon"), "wmnfncc192"),
    (("library192", "a"), "library192"),
    (("library192", "zz"), "khaqzqx192"),
    (("library192", "AgentU"), "lofetly192"),
    (("library192", "keyboard"), "vmzsorp192"),
    (("library192", "AA"), "library192"),
    (("service192", "key"), "cipfmao192"),
    (("service192", "lemon"), "didjvni192"),
    (("service192", "a"), "service192"),
    (("service192", "zz"), "rdquhbd192"),
    (("service192", "AgentU"), "skvibwe192"),
    (("service192", "keyboard"), "cipwwcv192"),
    (("service192", "AA"), "service192"),
    (("gateway192", "key"), "qeroayi192"),
    (("gateway192", "lemon"), "refsjlc192"),
    (("gateway192", "a"), "gateway192"),
    (("gateway192", "zz"), "fzsdvzx192"),
    (("gateway192", "AgentU"), "ggxrpuy192"),
    (("gateway192", "keyboard"), "qerfkap192"),
    (("gateway192", "AA"), "gateway192"),
    (("storage192", "key"), "cxmbeeo192"),
    (("storage192", "lemon"), "dxafnri192"),
    (("storage192", "a"), "storage192"),
    (("storage192", "zz"), "rsnqzfd192"),
    (("storage192", "AgentU"), "szsetae192"),
    (("storage192", "keyboard"), "cxmsogv192"),
    (("storage192", "AA"), "storage192"),
    (("network192", "key"), "xirgspu192"),
    (("network192", "lemon"), "yifkbco192"),
    (("network192", "a"), "network192"),
    (("network192", "zz"), "mdsvnqj192"),
    (("network192", "AgentU"), "nkxjhlk192"),
    (("network192", "keyboard"), "xirxcrb192"),
    (("network192", "AA"), "network192"),
    (("latency192", "key"), "verorai192"),
    (("latency192", "lemon"), "wefsanc192"),
    (("latency192", "a"), "latency192"),
    (("latency192", "zz"), "kzsdmbx192"),
    (("latency192", "AgentU"), "lgxrgwy192"),
    (("latency192", "keyboard"), "verfbcp192"),
    (("latency192", "AA"), "latency192"),
    (("buffer192", "key"), "lydpip192"),
    (("buffer192", "lemon"), "myrtrc192"),
    (("buffer192", "a"), "buffer192"),
    (("buffer192", "zz"), "ateedq192"),
    (("buffer192", "AgentU"), "bajsxl192"),
    (("buffer192", "keyboard"), "lydgsr192"),
    (("buffer192", "AA"), "buffer192"),
    (("queue192", "key"), "aycei192"),
    (("queue192", "lemon"), "byqir192"),
    (("queue192", "a"), "queue192"),
    (("queue192", "zz"), "ptdtd192"),
    (("queue192", "AgentU"), "qaihx192"),
    (("queue192", "keyboard"), "aycvs192"),
    (("queue192", "AA"), "queue192"),
    (("worker192", "key"), "gspuip192"),
    (("worker192", "lemon"), "hsdyrc192"),
    (("worker192", "a"), "worker192"),
    (("worker192", "zz"), "vnqjdq192"),
    (("worker192", "AgentU"), "wuvxxl192"),
    (("worker192", "keyboard"), "gsplsr192"),
    (("worker192", "AA"), "worker192"),
    (("kernel192", "key"), "uipxij192"),
    (("kernel192", "lemon"), "vidbrw192"),
    (("kernel192", "a"), "kernel192"),
    (("kernel192", "zz"), "jdqmdk192"),
    (("kernel192", "AgentU"), "kkvaxf192"),
    (("kernel192", "keyboard"), "uiposl192"),
    (("kernel192", "AA"), "kernel192"),
    (("signal192", "key"), "cmexej192"),
    (("signal192", "lemon"), "dmsbnw192"),
    (("signal192", "a"), "signal192"),
    (("signal192", "zz"), "rhfmzk192"),
    (("signal192", "AgentU"), "sokatf192"),
    (("signal192", "keyboard"), "cmeool192"),
    (("signal192", "AA"), "signal192"),
    (("packet192", "key"), "zeauir192"),
    (("packet192", "lemon"), "aeoyre192"),
    (("packet192", "a"), "packet192"),
    (("packet192", "zz"), "ozbjds192"),
    (("packet192", "AgentU"), "pggxxn192"),
    (("packet192", "keyboard"), "zealst192"),
    (("packet192", "AA"), "packet192"),
    (("router192", "key"), "bssdip192"),
    (("router192", "lemon"), "csghrc192"),
    (("router192", "a"), "router192"),
    (("router192", "zz"), "qntsdq192"),
    (("router192", "AgentU"), "ruygxl192"),
    (("router192", "keyboard"), "bssusr192"),
    (("router192", "AA"), "router192"),
    (("cluster192", "key"), "mpscxcb192"),
    (("cluster192", "lemon"), "npgggpv192"),
    (("cluster192", "a"), "cluster192"),
    (("cluster192", "zz"), "bktrsdq192"),
    (("cluster192", "AgentU"), "cryfmyr192"),
    (("cluster192", "keyboard"), "mpsthei192"),
    (("cluster192", "AA"), "cluster192"),
    (("mirror192", "key"), "wmpbsp192"),
    (("mirror192", "lemon"), "xmdfbc192"),
    (("mirror192", "a"), "mirror192"),
    (("mirror192", "zz"), "lhqqnq192"),
    (("mirror192", "AgentU"), "movehl192"),
    (("mirror192", "keyboard"), "wmpscr192"),
    (("mirror192", "AA"), "mirror192"),
    (("filter192", "key"), "pmjdip192"),
    (("filter192", "lemon"), "qmxhrc192"),
    (("filter192", "a"), "filter192"),
    (("filter192", "zz"), "ehksdq192"),
    (("filter192", "AgentU"), "fopgxl192"),
    (("filter192", "keyboard"), "pmjusr192"),
    (("filter192", "AA"), "filter192"),
    (("ranking192", "key"), "belumlq192"),
    (("ranking192", "lemon"), "cezyvyk192"),
    (("ranking192", "a"), "ranking192"),
    (("ranking192", "zz"), "qzmjhmf192"),
    (("ranking192", "AgentU"), "rgrxbhg192"),
    (("ranking192", "keyboard"), "bellwnx192"),
    (("ranking192", "AA"), "ranking192"),
    (("encoding192", "key"), "orayhgxk192"),
    (("encoding192", "lemon"), "procqtrs192"),
    (("encoding192", "a"), "encoding192"),
    (("encoding192", "zz"), "dmbnchmf192"),
    (("encoding192", "AgentU"), "etgbwcnm192"),
    (("encoding192", "keyboard"), "orapriej192"),
    (("encoding192", "AA"), "encoding192"),
    (("mapping192", "key"), "wenzmlq192"),
    (("mapping192", "lemon"), "xebdvyk192"),
    (("mapping192", "a"), "mapping192"),
    (("mapping192", "zz"), "lzoohmf192"),
    (("mapping192", "AgentU"), "mgtcbhg192"),
    (("mapping192", "keyboard"), "wenqwnx192"),
    (("mapping192", "AA"), "mapping192"),
    (("record192", "key"), "biayvb192"),
    (("record192", "lemon"), "cioceo192"),
    (("record192", "a"), "record192"),
    (("record192", "zz"), "qdbnqc192"),
    (("record192", "AgentU"), "rkgbkx192"),
    (("record192", "keyboard"), "biapfd192"),
    (("record192", "AA"), "record192"),
    (("candle192", "key"), "melnpc192"),
    (("candle192", "lemon"), "nezryp192"),
    (("candle192", "a"), "candle192"),
    (("candle192", "zz"), "bzmckd192"),
    (("candle192", "AgentU"), "cgrqey192"),
    (("candle192", "keyboard"), "meleze192"),
    (("candle192", "AA"), "candle192"),
    (("thread192", "key"), "dlpoeb192"),
    (("thread192", "lemon"), "eldsno192"),
    (("thread192", "a"), "thread192"),
    (("thread192", "zz"), "sgqdzc192"),
    (("thread192", "AgentU"), "tnvrtx192"),
    (("thread192", "keyboard"), "dlpfod192"),
    (("thread192", "AA"), "thread192"),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 192: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 192: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "a"),
        "round 192: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 192: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 192: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 192: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", "AA"),
        "round 192: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "key"),
        "bssxh 192: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 192: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "a"),
        "round 192: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 192: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 192: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 192: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", "AA"),
        "round 192: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 192: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 192: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "a"),
        "round 192: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 192: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 192: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 192: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", "AA"),
        "round 192: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 192: the processor reads the record then stops", "key"),
        "bssxh 192: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 192: the processor reads the record then stops", "lemon"),
        "csgbq 192: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 192: the processor reads the record then stops", "a"),
        "round 192: the processor reads the record then stops",
    ),
    (
        ("round 192: the processor reads the record then stops", "zz"),
        "qntmc 192: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 192: the processor reads the record then stops", "AgentU"),
        "ruyaw 192: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 192: the processor reads the record then stops", "keyboard"),
        "bssor 192: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 192: the processor reads the record then stops", "AA"),
        "round 192: the processor reads the record then stops",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "key"),
        "bssxh 192: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "lemon"),
        "csgbq 192: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "a"),
        "round 192: a worker pulls the next task from the queue",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "zz"),
        "qntmc 192: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 192: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "keyboard"),
        "bssor 192: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 192: a worker pulls the next task from the queue", "AA"),
        "round 192: a worker pulls the next task from the queue",
    ),
    (
        ("round 192: signals travel through the network layer", "key"),
        "bssxh 192: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 192: signals travel through the network layer", "lemon"),
        "csgbq 192: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 192: signals travel through the network layer", "a"),
        "round 192: signals travel through the network layer",
    ),
    (
        ("round 192: signals travel through the network layer", "zz"),
        "qntmc 192: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 192: signals travel through the network layer", "AgentU"),
        "ruyaw 192: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 192: signals travel through the network layer", "keyboard"),
        "bssor 192: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 192: signals travel through the network layer", "AA"),
        "round 192: signals travel through the network layer",
    ),
    (
        ("round 192: the gateway routes each request by policy", "key"),
        "bssxh 192: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 192: the gateway routes each request by policy", "lemon"),
        "csgbq 192: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 192: the gateway routes each request by policy", "a"),
        "round 192: the gateway routes each request by policy",
    ),
    (
        ("round 192: the gateway routes each request by policy", "zz"),
        "qntmc 192: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 192: the gateway routes each request by policy", "AgentU"),
        "ruyaw 192: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 192: the gateway routes each request by policy", "keyboard"),
        "bssor 192: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 192: the gateway routes each request by policy", "AA"),
        "round 192: the gateway routes each request by policy",
    ),
    (("round 192: memory grows until the buffer is full", "key"), "bssxh 192: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 192: memory grows until the buffer is full", "lemon"), "csgbq 192: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 192: memory grows until the buffer is full", "a"), "round 192: memory grows until the buffer is full"),
    (("round 192: memory grows until the buffer is full", "zz"), "qntmc 192: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 192: memory grows until the buffer is full", "AgentU"),
        "ruyaw 192: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 192: memory grows until the buffer is full", "keyboard"),
        "bssor 192: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 192: memory grows until the buffer is full", "AA"), "round 192: memory grows until the buffer is full"),
    (("round 192: the cluster mirrors every packet twice", "key"), "bssxh 192: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 192: the cluster mirrors every packet twice", "lemon"),
        "csgbq 192: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 192: the cluster mirrors every packet twice", "a"), "round 192: the cluster mirrors every packet twice"),
    (("round 192: the cluster mirrors every packet twice", "zz"), "qntmc 192: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 192: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 192: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 192: the cluster mirrors every packet twice", "keyboard"),
        "bssor 192: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 192: the cluster mirrors every packet twice", "AA"), "round 192: the cluster mirrors every packet twice"),
    (
        ("round 192: ranking uses tokens learned from the corpus", "key"),
        "bssxh 192: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 192: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", "a"),
        "round 192: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 192: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 192: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 192: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", "AA"),
        "round 192: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 192: a long session ends when the candle dies", "key"),
        "bssxh 192: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 192: a long session ends when the candle dies", "lemon"),
        "csgbq 192: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 192: a long session ends when the candle dies", "a"),
        "round 192: a long session ends when the candle dies",
    ),
    (
        ("round 192: a long session ends when the candle dies", "zz"),
        "qntmc 192: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 192: a long session ends when the candle dies", "AgentU"),
        "ruyaw 192: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 192: a long session ends when the candle dies", "keyboard"),
        "bssor 192: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 192: a long session ends when the candle dies", "AA"),
        "round 192: a long session ends when the candle dies",
    ),
    (("round 192: encode the prompt then map the result", "key"), "bssxh 192: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 192: encode the prompt then map the result", "lemon"), "csgbq 192: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 192: encode the prompt then map the result", "a"), "round 192: encode the prompt then map the result"),
    (("round 192: encode the prompt then map the result", "zz"), "qntmc 192: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 192: encode the prompt then map the result", "AgentU"),
        "ruyaw 192: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 192: encode the prompt then map the result", "keyboard"),
        "bssor 192: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 192: encode the prompt then map the result", "AA"), "round 192: encode the prompt then map the result"),
    (("round 192: the kernel wakes the worker at dawn", "key"), "bssxh 192: rri iovlop ukocc xfo ambocb er neux"),
    (("round 192: the kernel wakes the worker at dawn", "lemon"), "csgbq 192: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 192: the kernel wakes the worker at dawn", "a"), "round 192: the kernel wakes the worker at dawn"),
    (("round 192: the kernel wakes the worker at dawn", "zz"), "qntmc 192: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 192: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 192: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 192: the kernel wakes the worker at dawn", "keyboard"), "bssor 192: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 192: the kernel wakes the worker at dawn", "AA"), "round 192: the kernel wakes the worker at dawn"),
    (("round 192: service latency drops after the patch", "key"), "bssxh 192: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 192: service latency drops after the patch", "lemon"), "csgbq 192: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 192: service latency drops after the patch", "a"), "round 192: service latency drops after the patch"),
    (("round 192: service latency drops after the patch", "zz"), "qntmc 192: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 192: service latency drops after the patch", "AgentU"),
        "ruyaw 192: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 192: service latency drops after the patch", "keyboard"),
        "bssor 192: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 192: service latency drops after the patch", "AA"), "round 192: service latency drops after the patch"),
    (
        ("round 192: the library caches every vector it sees", "key"),
        "bssxh 192: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 192: the library caches every vector it sees", "lemon"),
        "csgbq 192: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 192: the library caches every vector it sees", "a"), "round 192: the library caches every vector it sees"),
    (
        ("round 192: the library caches every vector it sees", "zz"),
        "qntmc 192: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 192: the library caches every vector it sees", "AgentU"),
        "ruyaw 192: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 192: the library caches every vector it sees", "keyboard"),
        "bssor 192: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 192: the library caches every vector it sees", "AA"),
        "round 192: the library caches every vector it sees",
    ),
    (("round 192: agents argue then the debate resolves", "key"), "bssxh 192: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 192: agents argue then the debate resolves", "lemon"), "csgbq 192: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 192: agents argue then the debate resolves", "a"), "round 192: agents argue then the debate resolves"),
    (("round 192: agents argue then the debate resolves", "zz"), "qntmc 192: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 192: agents argue then the debate resolves", "AgentU"),
        "ruyaw 192: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 192: agents argue then the debate resolves", "keyboard"),
        "bssor 192: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 192: agents argue then the debate resolves", "AA"), "round 192: agents argue then the debate resolves"),
    (("round 192: the filter keeps only strong matches", "key"), "bssxh 192: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 192: the filter keeps only strong matches", "lemon"), "csgbq 192: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 192: the filter keeps only strong matches", "a"), "round 192: the filter keeps only strong matches"),
    (("round 192: the filter keeps only strong matches", "zz"), "qntmc 192: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 192: the filter keeps only strong matches", "AgentU"), "ruyaw 192: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 192: the filter keeps only strong matches", "keyboard"),
        "bssor 192: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 192: the filter keeps only strong matches", "AA"), "round 192: the filter keeps only strong matches"),
    (("round 192: the model answers with a short reply", "key"), "bssxh 192: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 192: the model answers with a short reply", "lemon"), "csgbq 192: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 192: the model answers with a short reply", "a"), "round 192: the model answers with a short reply"),
    (("round 192: the model answers with a short reply", "zz"), "qntmc 192: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 192: the model answers with a short reply", "AgentU"), "ruyaw 192: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 192: the model answers with a short reply", "keyboard"),
        "bssor 192: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 192: the model answers with a short reply", "AA"), "round 192: the model answers with a short reply"),
    (
        ("round 192: the recorder stores the reasoning trace", "key"),
        "bssxh 192: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 192: the recorder stores the reasoning trace", "lemon"),
        "csgbq 192: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 192: the recorder stores the reasoning trace", "a"), "round 192: the recorder stores the reasoning trace"),
    (
        ("round 192: the recorder stores the reasoning trace", "zz"),
        "qntmc 192: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 192: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 192: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 192: the recorder stores the reasoning trace", "keyboard"),
        "bssor 192: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 192: the recorder stores the reasoning trace", "AA"),
        "round 192: the recorder stores the reasoning trace",
    ),
    (("round 192: the angel watches the processor run", "key"), "bssxh 192: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 192: the angel watches the processor run", "lemon"), "csgbq 192: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 192: the angel watches the processor run", "a"), "round 192: the angel watches the processor run"),
    (("round 192: the angel watches the processor run", "zz"), "qntmc 192: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 192: the angel watches the processor run", "AgentU"), "ruyaw 192: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 192: the angel watches the processor run", "keyboard"), "bssor 192: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 192: the angel watches the processor run", "AA"), "round 192: the angel watches the processor run"),
    (("round 192: angle of the vector decides the match", "key"), "bssxh 192: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 192: angle of the vector decides the match", "lemon"), "csgbq 192: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 192: angle of the vector decides the match", "a"), "round 192: angle of the vector decides the match"),
    (("round 192: angle of the vector decides the match", "zz"), "qntmc 192: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 192: angle of the vector decides the match", "AgentU"),
        "ruyaw 192: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 192: angle of the vector decides the match", "keyboard"),
        "bssor 192: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 192: angle of the vector decides the match", "AA"), "round 192: angle of the vector decides the match"),
    (
        ("round 192: the candle burns twice as long at night", "key"),
        "bssxh 192: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 192: the candle burns twice as long at night", "lemon"),
        "csgbq 192: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 192: the candle burns twice as long at night", "a"), "round 192: the candle burns twice as long at night"),
    (
        ("round 192: the candle burns twice as long at night", "zz"),
        "qntmc 192: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 192: the candle burns twice as long at night", "AgentU"),
        "ruyaw 192: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 192: the candle burns twice as long at night", "keyboard"),
        "bssor 192: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 192: the candle burns twice as long at night", "AA"),
        "round 192: the candle burns twice as long at night",
    ),
    (("round 192: a mirror of the universe in one line", "key"), "bssxh 192: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 192: a mirror of the universe in one line", "lemon"), "csgbq 192: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 192: a mirror of the universe in one line", "a"), "round 192: a mirror of the universe in one line"),
    (("round 192: a mirror of the universe in one line", "zz"), "qntmc 192: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 192: a mirror of the universe in one line", "AgentU"), "ruyaw 192: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 192: a mirror of the universe in one line", "keyboard"),
        "bssor 192: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 192: a mirror of the universe in one line", "AA"), "round 192: a mirror of the universe in one line"),
    (("round 192: the queue drains before the storm", "key"), "bssxh 192: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 192: the queue drains before the storm", "lemon"), "csgbq 192: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 192: the queue drains before the storm", "a"), "round 192: the queue drains before the storm"),
    (("round 192: the queue drains before the storm", "zz"), "qntmc 192: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 192: the queue drains before the storm", "AgentU"), "ruyaw 192: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 192: the queue drains before the storm", "keyboard"), "bssor 192: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 192: the queue drains before the storm", "AA"), "round 192: the queue drains before the storm"),
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
