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
    (("kitten169", "key"), "umrdil169"),
    (("kitten169", "lemon"), "vmfhry169"),
    (("kitten169", "a"), "kitten169"),
    (("kitten169", "zz"), "jhssdm169"),
    (("kitten169", "AgentU"), "koxgxh169"),
    (("kitten169", "keyboard"), "umrusn169"),
    (("kitten169", "AA"), "kitten169"),
    (("sitting169", "key"), "cmrdmlq169"),
    (("sitting169", "lemon"), "dmfhvyk169"),
    (("sitting169", "a"), "sitting169"),
    (("sitting169", "zz"), "rhsshmf169"),
    (("sitting169", "AgentU"), "soxgbhg169"),
    (("sitting169", "keyboard"), "cmruwnx169"),
    (("sitting169", "AA"), "sitting169"),
    (("agent169", "key"), "kkcxx169"),
    (("agent169", "lemon"), "lkqbg169"),
    (("agent169", "a"), "agent169"),
    (("agent169", "zz"), "zfdms169"),
    (("agent169", "AgentU"), "amiam169"),
    (("agent169", "keyboard"), "kkcoh169"),
    (("agent169", "AA"), "agent169"),
    (("angle169", "key"), "krevi169"),
    (("angle169", "lemon"), "lrszr169"),
    (("angle169", "a"), "angle169"),
    (("angle169", "zz"), "zmfkd169"),
    (("angle169", "AgentU"), "atkyx169"),
    (("angle169", "keyboard"), "krems169"),
    (("angle169", "AA"), "angle169"),
    (("universe169", "key"), "ergfipci169"),
    (("universe169", "lemon"), "frujrcwq169"),
    (("universe169", "a"), "universe169"),
    (("universe169", "zz"), "tmhudqrd169"),
    (("universe169", "AgentU"), "utmixlsk169"),
    (("universe169", "keyboard"), "ergwsrjh169"),
    (("universe169", "AA"), "universe169"),
    (("memory169", "key"), "wikyvw169"),
    (("memory169", "lemon"), "xiycej169"),
    (("memory169", "a"), "memory169"),
    (("memory169", "zz"), "ldlnqx169"),
    (("memory169", "AgentU"), "mkqbks169"),
    (("memory169", "keyboard"), "wikpfy169"),
    (("memory169", "AA"), "memory169"),
    (("stream169", "key"), "cxpoek169"),
    (("stream169", "lemon"), "dxdsnx169"),
    (("stream169", "a"), "stream169"),
    (("stream169", "zz"), "rsqdzl169"),
    (("stream169", "AgentU"), "szvrtg169"),
    (("stream169", "keyboard"), "cxpfom169"),
    (("stream169", "AA"), "stream169"),
    (("context169", "key"), "msldivd169"),
    (("context169", "lemon"), "nszhrix169"),
    (("context169", "a"), "context169"),
    (("context169", "zz"), "bnmsdws169"),
    (("context169", "AgentU"), "curgxrt169"),
    (("context169", "keyboard"), "mslusxk169"),
    (("context169", "AA"), "context169"),
    (("knowledge169", "key"), "urmgpcnkc169"),
    (("knowledge169", "lemon"), "vrakyphss169"),
    (("knowledge169", "a"), "knowledge169"),
    (("knowledge169", "zz"), "jmnvkdcfd169"),
    (("knowledge169", "AgentU"), "ktsjeydmi169"),
    (("knowledge169", "keyboard"), "urmxzeujo169"),
    (("knowledge169", "AA"), "knowledge169"),
    (("vector169", "key"), "fiadsp169"),
    (("vector169", "lemon"), "giohbc169"),
    (("vector169", "a"), "vector169"),
    (("vector169", "zz"), "udbsnq169"),
    (("vector169", "AgentU"), "vkgghl169"),
    (("vector169", "keyboard"), "fiaucr169"),
    (("vector169", "AA"), "vector169"),
    (("processor169", "key"), "zvmmiqcsp169"),
    (("processor169", "lemon"), "avaqrdwaf169"),
    (("processor169", "a"), "processor169"),
    (("processor169", "zz"), "oqnbdrrnq169"),
    (("processor169", "AgentU"), "pxspxmsuv169"),
    (("processor169", "keyboard"), "zvmdssjrb169"),
    (("processor169", "AA"), "processor169"),
    (("reasoning169", "key"), "biycslsre169"),
    (("reasoning169", "lemon"), "cimgbymzu169"),
    (("reasoning169", "a"), "reasoning169"),
    (("reasoning169", "zz"), "qdzrnmhmf169"),
    (("reasoning169", "AgentU"), "rkefhhitk169"),
    (("reasoning169", "keyboard"), "biytcnzqq169"),
    (("reasoning169", "AA"), "reasoning169"),
    (("machine169", "key"), "wearmlo169"),
    (("machine169", "lemon"), "xeovvyi169"),
    (("machine169", "a"), "machine169"),
    (("machine169", "zz"), "lzbghmd169"),
    (("machine169", "AgentU"), "mggubhe169"),
    (("machine169", "keyboard"), "weaiwnv169"),
    (("machine169", "AA"), "machine169"),
    (("learning169", "key"), "viybrgxk169"),
    (("learning169", "lemon"), "wimfatrs169"),
    (("learning169", "a"), "learning169"),
    (("learning169", "zz"), "kdzqmhmf169"),
    (("learning169", "AgentU"), "lkeegcnm169"),
    (("learning169", "keyboard"), "viysbiej169"),
    (("learning169", "AA"), "learning169"),
    (("model169", "key"), "wsbop169"),
    (("model169", "lemon"), "xspsy169"),
    (("model169", "a"), "model169"),
    (("model169", "zz"), "lncdk169"),
    (("model169", "AgentU"), "muhre169"),
    (("model169", "keyboard"), "wsbfz169"),
    (("model169", "AA"), "model169"),
    (("token169", "key"), "dsior169"),
    (("token169", "lemon"), "eswsa169"),
    (("token169", "a"), "token169"),
    (("token169", "zz"), "snjdm169"),
    (("token169", "AgentU"), "tuorg169"),
    (("token169", "keyboard"), "dsifb169"),
    (("token169", "AA"), "token169"),
    (("prompt169", "key"), "zvmwtr169"),
    (("prompt169", "lemon"), "avaace169"),
    (("prompt169", "a"), "prompt169"),
    (("prompt169", "zz"), "oqnlos169"),
    (("prompt169", "AgentU"), "pxszin169"),
    (("prompt169", "keyboard"), "zvmndt169"),
    (("prompt169", "AA"), "prompt169"),
    (("session169", "key"), "ciqcmmx169"),
    (("session169", "lemon"), "diegvzr169"),
    (("session169", "a"), "session169"),
    (("session169", "zz"), "rdrrhnm169"),
    (("session169", "AgentU"), "skwfbin169"),
    (("session169", "keyboard"), "ciqtwoe169"),
    (("session169", "AA"), "session169"),
    (("library169", "key"), "vmzbepi169"),
    (("library169", "lemon"), "wmnfncc169"),
    (("library169", "a"), "library169"),
    (("library169", "zz"), "khaqzqx169"),
    (("library169", "AgentU"), "lofetly169"),
    (("library169", "keyboard"), "vmzsorp169"),
    (("library169", "AA"), "library169"),
    (("service169", "key"), "cipfmao169"),
    (("service169", "lemon"), "didjvni169"),
    (("service169", "a"), "service169"),
    (("service169", "zz"), "rdquhbd169"),
    (("service169", "AgentU"), "skvibwe169"),
    (("service169", "keyboard"), "cipwwcv169"),
    (("service169", "AA"), "service169"),
    (("gateway169", "key"), "qeroayi169"),
    (("gateway169", "lemon"), "refsjlc169"),
    (("gateway169", "a"), "gateway169"),
    (("gateway169", "zz"), "fzsdvzx169"),
    (("gateway169", "AgentU"), "ggxrpuy169"),
    (("gateway169", "keyboard"), "qerfkap169"),
    (("gateway169", "AA"), "gateway169"),
    (("storage169", "key"), "cxmbeeo169"),
    (("storage169", "lemon"), "dxafnri169"),
    (("storage169", "a"), "storage169"),
    (("storage169", "zz"), "rsnqzfd169"),
    (("storage169", "AgentU"), "szsetae169"),
    (("storage169", "keyboard"), "cxmsogv169"),
    (("storage169", "AA"), "storage169"),
    (("network169", "key"), "xirgspu169"),
    (("network169", "lemon"), "yifkbco169"),
    (("network169", "a"), "network169"),
    (("network169", "zz"), "mdsvnqj169"),
    (("network169", "AgentU"), "nkxjhlk169"),
    (("network169", "keyboard"), "xirxcrb169"),
    (("network169", "AA"), "network169"),
    (("latency169", "key"), "verorai169"),
    (("latency169", "lemon"), "wefsanc169"),
    (("latency169", "a"), "latency169"),
    (("latency169", "zz"), "kzsdmbx169"),
    (("latency169", "AgentU"), "lgxrgwy169"),
    (("latency169", "keyboard"), "verfbcp169"),
    (("latency169", "AA"), "latency169"),
    (("buffer169", "key"), "lydpip169"),
    (("buffer169", "lemon"), "myrtrc169"),
    (("buffer169", "a"), "buffer169"),
    (("buffer169", "zz"), "ateedq169"),
    (("buffer169", "AgentU"), "bajsxl169"),
    (("buffer169", "keyboard"), "lydgsr169"),
    (("buffer169", "AA"), "buffer169"),
    (("queue169", "key"), "aycei169"),
    (("queue169", "lemon"), "byqir169"),
    (("queue169", "a"), "queue169"),
    (("queue169", "zz"), "ptdtd169"),
    (("queue169", "AgentU"), "qaihx169"),
    (("queue169", "keyboard"), "aycvs169"),
    (("queue169", "AA"), "queue169"),
    (("worker169", "key"), "gspuip169"),
    (("worker169", "lemon"), "hsdyrc169"),
    (("worker169", "a"), "worker169"),
    (("worker169", "zz"), "vnqjdq169"),
    (("worker169", "AgentU"), "wuvxxl169"),
    (("worker169", "keyboard"), "gsplsr169"),
    (("worker169", "AA"), "worker169"),
    (("kernel169", "key"), "uipxij169"),
    (("kernel169", "lemon"), "vidbrw169"),
    (("kernel169", "a"), "kernel169"),
    (("kernel169", "zz"), "jdqmdk169"),
    (("kernel169", "AgentU"), "kkvaxf169"),
    (("kernel169", "keyboard"), "uiposl169"),
    (("kernel169", "AA"), "kernel169"),
    (("signal169", "key"), "cmexej169"),
    (("signal169", "lemon"), "dmsbnw169"),
    (("signal169", "a"), "signal169"),
    (("signal169", "zz"), "rhfmzk169"),
    (("signal169", "AgentU"), "sokatf169"),
    (("signal169", "keyboard"), "cmeool169"),
    (("signal169", "AA"), "signal169"),
    (("packet169", "key"), "zeauir169"),
    (("packet169", "lemon"), "aeoyre169"),
    (("packet169", "a"), "packet169"),
    (("packet169", "zz"), "ozbjds169"),
    (("packet169", "AgentU"), "pggxxn169"),
    (("packet169", "keyboard"), "zealst169"),
    (("packet169", "AA"), "packet169"),
    (("router169", "key"), "bssdip169"),
    (("router169", "lemon"), "csghrc169"),
    (("router169", "a"), "router169"),
    (("router169", "zz"), "qntsdq169"),
    (("router169", "AgentU"), "ruygxl169"),
    (("router169", "keyboard"), "bssusr169"),
    (("router169", "AA"), "router169"),
    (("cluster169", "key"), "mpscxcb169"),
    (("cluster169", "lemon"), "npgggpv169"),
    (("cluster169", "a"), "cluster169"),
    (("cluster169", "zz"), "bktrsdq169"),
    (("cluster169", "AgentU"), "cryfmyr169"),
    (("cluster169", "keyboard"), "mpsthei169"),
    (("cluster169", "AA"), "cluster169"),
    (("mirror169", "key"), "wmpbsp169"),
    (("mirror169", "lemon"), "xmdfbc169"),
    (("mirror169", "a"), "mirror169"),
    (("mirror169", "zz"), "lhqqnq169"),
    (("mirror169", "AgentU"), "movehl169"),
    (("mirror169", "keyboard"), "wmpscr169"),
    (("mirror169", "AA"), "mirror169"),
    (("filter169", "key"), "pmjdip169"),
    (("filter169", "lemon"), "qmxhrc169"),
    (("filter169", "a"), "filter169"),
    (("filter169", "zz"), "ehksdq169"),
    (("filter169", "AgentU"), "fopgxl169"),
    (("filter169", "keyboard"), "pmjusr169"),
    (("filter169", "AA"), "filter169"),
    (("ranking169", "key"), "belumlq169"),
    (("ranking169", "lemon"), "cezyvyk169"),
    (("ranking169", "a"), "ranking169"),
    (("ranking169", "zz"), "qzmjhmf169"),
    (("ranking169", "AgentU"), "rgrxbhg169"),
    (("ranking169", "keyboard"), "bellwnx169"),
    (("ranking169", "AA"), "ranking169"),
    (("encoding169", "key"), "orayhgxk169"),
    (("encoding169", "lemon"), "procqtrs169"),
    (("encoding169", "a"), "encoding169"),
    (("encoding169", "zz"), "dmbnchmf169"),
    (("encoding169", "AgentU"), "etgbwcnm169"),
    (("encoding169", "keyboard"), "orapriej169"),
    (("encoding169", "AA"), "encoding169"),
    (("mapping169", "key"), "wenzmlq169"),
    (("mapping169", "lemon"), "xebdvyk169"),
    (("mapping169", "a"), "mapping169"),
    (("mapping169", "zz"), "lzoohmf169"),
    (("mapping169", "AgentU"), "mgtcbhg169"),
    (("mapping169", "keyboard"), "wenqwnx169"),
    (("mapping169", "AA"), "mapping169"),
    (("record169", "key"), "biayvb169"),
    (("record169", "lemon"), "cioceo169"),
    (("record169", "a"), "record169"),
    (("record169", "zz"), "qdbnqc169"),
    (("record169", "AgentU"), "rkgbkx169"),
    (("record169", "keyboard"), "biapfd169"),
    (("record169", "AA"), "record169"),
    (("candle169", "key"), "melnpc169"),
    (("candle169", "lemon"), "nezryp169"),
    (("candle169", "a"), "candle169"),
    (("candle169", "zz"), "bzmckd169"),
    (("candle169", "AgentU"), "cgrqey169"),
    (("candle169", "keyboard"), "meleze169"),
    (("candle169", "AA"), "candle169"),
    (("thread169", "key"), "dlpoeb169"),
    (("thread169", "lemon"), "eldsno169"),
    (("thread169", "a"), "thread169"),
    (("thread169", "zz"), "sgqdzc169"),
    (("thread169", "AgentU"), "tnvrtx169"),
    (("thread169", "keyboard"), "dlpfod169"),
    (("thread169", "AA"), "thread169"),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 169: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 169: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "a"),
        "round 169: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 169: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 169: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 169: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", "AA"),
        "round 169: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "key"),
        "bssxh 169: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 169: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "a"),
        "round 169: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 169: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 169: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 169: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", "AA"),
        "round 169: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 169: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 169: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "a"),
        "round 169: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 169: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 169: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 169: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", "AA"),
        "round 169: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 169: the processor reads the record then stops", "key"),
        "bssxh 169: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 169: the processor reads the record then stops", "lemon"),
        "csgbq 169: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 169: the processor reads the record then stops", "a"),
        "round 169: the processor reads the record then stops",
    ),
    (
        ("round 169: the processor reads the record then stops", "zz"),
        "qntmc 169: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 169: the processor reads the record then stops", "AgentU"),
        "ruyaw 169: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 169: the processor reads the record then stops", "keyboard"),
        "bssor 169: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 169: the processor reads the record then stops", "AA"),
        "round 169: the processor reads the record then stops",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "key"),
        "bssxh 169: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "lemon"),
        "csgbq 169: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "a"),
        "round 169: a worker pulls the next task from the queue",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "zz"),
        "qntmc 169: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 169: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "keyboard"),
        "bssor 169: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 169: a worker pulls the next task from the queue", "AA"),
        "round 169: a worker pulls the next task from the queue",
    ),
    (
        ("round 169: signals travel through the network layer", "key"),
        "bssxh 169: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 169: signals travel through the network layer", "lemon"),
        "csgbq 169: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 169: signals travel through the network layer", "a"),
        "round 169: signals travel through the network layer",
    ),
    (
        ("round 169: signals travel through the network layer", "zz"),
        "qntmc 169: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 169: signals travel through the network layer", "AgentU"),
        "ruyaw 169: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 169: signals travel through the network layer", "keyboard"),
        "bssor 169: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 169: signals travel through the network layer", "AA"),
        "round 169: signals travel through the network layer",
    ),
    (
        ("round 169: the gateway routes each request by policy", "key"),
        "bssxh 169: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 169: the gateway routes each request by policy", "lemon"),
        "csgbq 169: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 169: the gateway routes each request by policy", "a"),
        "round 169: the gateway routes each request by policy",
    ),
    (
        ("round 169: the gateway routes each request by policy", "zz"),
        "qntmc 169: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 169: the gateway routes each request by policy", "AgentU"),
        "ruyaw 169: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 169: the gateway routes each request by policy", "keyboard"),
        "bssor 169: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 169: the gateway routes each request by policy", "AA"),
        "round 169: the gateway routes each request by policy",
    ),
    (("round 169: memory grows until the buffer is full", "key"), "bssxh 169: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 169: memory grows until the buffer is full", "lemon"), "csgbq 169: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 169: memory grows until the buffer is full", "a"), "round 169: memory grows until the buffer is full"),
    (("round 169: memory grows until the buffer is full", "zz"), "qntmc 169: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 169: memory grows until the buffer is full", "AgentU"),
        "ruyaw 169: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 169: memory grows until the buffer is full", "keyboard"),
        "bssor 169: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 169: memory grows until the buffer is full", "AA"), "round 169: memory grows until the buffer is full"),
    (("round 169: the cluster mirrors every packet twice", "key"), "bssxh 169: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 169: the cluster mirrors every packet twice", "lemon"),
        "csgbq 169: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 169: the cluster mirrors every packet twice", "a"), "round 169: the cluster mirrors every packet twice"),
    (("round 169: the cluster mirrors every packet twice", "zz"), "qntmc 169: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 169: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 169: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 169: the cluster mirrors every packet twice", "keyboard"),
        "bssor 169: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 169: the cluster mirrors every packet twice", "AA"), "round 169: the cluster mirrors every packet twice"),
    (
        ("round 169: ranking uses tokens learned from the corpus", "key"),
        "bssxh 169: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 169: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", "a"),
        "round 169: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 169: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 169: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 169: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", "AA"),
        "round 169: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 169: a long session ends when the candle dies", "key"),
        "bssxh 169: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 169: a long session ends when the candle dies", "lemon"),
        "csgbq 169: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 169: a long session ends when the candle dies", "a"),
        "round 169: a long session ends when the candle dies",
    ),
    (
        ("round 169: a long session ends when the candle dies", "zz"),
        "qntmc 169: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 169: a long session ends when the candle dies", "AgentU"),
        "ruyaw 169: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 169: a long session ends when the candle dies", "keyboard"),
        "bssor 169: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 169: a long session ends when the candle dies", "AA"),
        "round 169: a long session ends when the candle dies",
    ),
    (("round 169: encode the prompt then map the result", "key"), "bssxh 169: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 169: encode the prompt then map the result", "lemon"), "csgbq 169: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 169: encode the prompt then map the result", "a"), "round 169: encode the prompt then map the result"),
    (("round 169: encode the prompt then map the result", "zz"), "qntmc 169: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 169: encode the prompt then map the result", "AgentU"),
        "ruyaw 169: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 169: encode the prompt then map the result", "keyboard"),
        "bssor 169: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 169: encode the prompt then map the result", "AA"), "round 169: encode the prompt then map the result"),
    (("round 169: the kernel wakes the worker at dawn", "key"), "bssxh 169: rri iovlop ukocc xfo ambocb er neux"),
    (("round 169: the kernel wakes the worker at dawn", "lemon"), "csgbq 169: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 169: the kernel wakes the worker at dawn", "a"), "round 169: the kernel wakes the worker at dawn"),
    (("round 169: the kernel wakes the worker at dawn", "zz"), "qntmc 169: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 169: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 169: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 169: the kernel wakes the worker at dawn", "keyboard"), "bssor 169: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 169: the kernel wakes the worker at dawn", "AA"), "round 169: the kernel wakes the worker at dawn"),
    (("round 169: service latency drops after the patch", "key"), "bssxh 169: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 169: service latency drops after the patch", "lemon"), "csgbq 169: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 169: service latency drops after the patch", "a"), "round 169: service latency drops after the patch"),
    (("round 169: service latency drops after the patch", "zz"), "qntmc 169: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 169: service latency drops after the patch", "AgentU"),
        "ruyaw 169: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 169: service latency drops after the patch", "keyboard"),
        "bssor 169: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 169: service latency drops after the patch", "AA"), "round 169: service latency drops after the patch"),
    (
        ("round 169: the library caches every vector it sees", "key"),
        "bssxh 169: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 169: the library caches every vector it sees", "lemon"),
        "csgbq 169: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 169: the library caches every vector it sees", "a"), "round 169: the library caches every vector it sees"),
    (
        ("round 169: the library caches every vector it sees", "zz"),
        "qntmc 169: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 169: the library caches every vector it sees", "AgentU"),
        "ruyaw 169: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 169: the library caches every vector it sees", "keyboard"),
        "bssor 169: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 169: the library caches every vector it sees", "AA"),
        "round 169: the library caches every vector it sees",
    ),
    (("round 169: agents argue then the debate resolves", "key"), "bssxh 169: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 169: agents argue then the debate resolves", "lemon"), "csgbq 169: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 169: agents argue then the debate resolves", "a"), "round 169: agents argue then the debate resolves"),
    (("round 169: agents argue then the debate resolves", "zz"), "qntmc 169: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 169: agents argue then the debate resolves", "AgentU"),
        "ruyaw 169: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 169: agents argue then the debate resolves", "keyboard"),
        "bssor 169: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 169: agents argue then the debate resolves", "AA"), "round 169: agents argue then the debate resolves"),
    (("round 169: the filter keeps only strong matches", "key"), "bssxh 169: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 169: the filter keeps only strong matches", "lemon"), "csgbq 169: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 169: the filter keeps only strong matches", "a"), "round 169: the filter keeps only strong matches"),
    (("round 169: the filter keeps only strong matches", "zz"), "qntmc 169: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 169: the filter keeps only strong matches", "AgentU"), "ruyaw 169: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 169: the filter keeps only strong matches", "keyboard"),
        "bssor 169: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 169: the filter keeps only strong matches", "AA"), "round 169: the filter keeps only strong matches"),
    (("round 169: the model answers with a short reply", "key"), "bssxh 169: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 169: the model answers with a short reply", "lemon"), "csgbq 169: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 169: the model answers with a short reply", "a"), "round 169: the model answers with a short reply"),
    (("round 169: the model answers with a short reply", "zz"), "qntmc 169: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 169: the model answers with a short reply", "AgentU"), "ruyaw 169: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 169: the model answers with a short reply", "keyboard"),
        "bssor 169: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 169: the model answers with a short reply", "AA"), "round 169: the model answers with a short reply"),
    (
        ("round 169: the recorder stores the reasoning trace", "key"),
        "bssxh 169: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 169: the recorder stores the reasoning trace", "lemon"),
        "csgbq 169: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 169: the recorder stores the reasoning trace", "a"), "round 169: the recorder stores the reasoning trace"),
    (
        ("round 169: the recorder stores the reasoning trace", "zz"),
        "qntmc 169: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 169: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 169: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 169: the recorder stores the reasoning trace", "keyboard"),
        "bssor 169: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 169: the recorder stores the reasoning trace", "AA"),
        "round 169: the recorder stores the reasoning trace",
    ),
    (("round 169: the angel watches the processor run", "key"), "bssxh 169: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 169: the angel watches the processor run", "lemon"), "csgbq 169: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 169: the angel watches the processor run", "a"), "round 169: the angel watches the processor run"),
    (("round 169: the angel watches the processor run", "zz"), "qntmc 169: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 169: the angel watches the processor run", "AgentU"), "ruyaw 169: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 169: the angel watches the processor run", "keyboard"), "bssor 169: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 169: the angel watches the processor run", "AA"), "round 169: the angel watches the processor run"),
    (("round 169: angle of the vector decides the match", "key"), "bssxh 169: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 169: angle of the vector decides the match", "lemon"), "csgbq 169: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 169: angle of the vector decides the match", "a"), "round 169: angle of the vector decides the match"),
    (("round 169: angle of the vector decides the match", "zz"), "qntmc 169: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 169: angle of the vector decides the match", "AgentU"),
        "ruyaw 169: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 169: angle of the vector decides the match", "keyboard"),
        "bssor 169: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 169: angle of the vector decides the match", "AA"), "round 169: angle of the vector decides the match"),
    (
        ("round 169: the candle burns twice as long at night", "key"),
        "bssxh 169: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 169: the candle burns twice as long at night", "lemon"),
        "csgbq 169: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 169: the candle burns twice as long at night", "a"), "round 169: the candle burns twice as long at night"),
    (
        ("round 169: the candle burns twice as long at night", "zz"),
        "qntmc 169: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 169: the candle burns twice as long at night", "AgentU"),
        "ruyaw 169: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 169: the candle burns twice as long at night", "keyboard"),
        "bssor 169: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 169: the candle burns twice as long at night", "AA"),
        "round 169: the candle burns twice as long at night",
    ),
    (("round 169: a mirror of the universe in one line", "key"), "bssxh 169: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 169: a mirror of the universe in one line", "lemon"), "csgbq 169: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 169: a mirror of the universe in one line", "a"), "round 169: a mirror of the universe in one line"),
    (("round 169: a mirror of the universe in one line", "zz"), "qntmc 169: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 169: a mirror of the universe in one line", "AgentU"), "ruyaw 169: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 169: a mirror of the universe in one line", "keyboard"),
        "bssor 169: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 169: a mirror of the universe in one line", "AA"), "round 169: a mirror of the universe in one line"),
    (("round 169: the queue drains before the storm", "key"), "bssxh 169: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 169: the queue drains before the storm", "lemon"), "csgbq 169: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 169: the queue drains before the storm", "a"), "round 169: the queue drains before the storm"),
    (("round 169: the queue drains before the storm", "zz"), "qntmc 169: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 169: the queue drains before the storm", "AgentU"), "ruyaw 169: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 169: the queue drains before the storm", "keyboard"), "bssor 169: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 169: the queue drains before the storm", "AA"), "round 169: the queue drains before the storm"),
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
