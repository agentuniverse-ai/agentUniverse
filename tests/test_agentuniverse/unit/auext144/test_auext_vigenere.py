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
    (("kitten144", "key"), "umrdil144"),
    (("kitten144", "lemon"), "vmfhry144"),
    (("kitten144", "a"), "kitten144"),
    (("kitten144", "zz"), "jhssdm144"),
    (("kitten144", "AgentU"), "koxgxh144"),
    (("kitten144", "keyboard"), "umrusn144"),
    (("kitten144", "AA"), "kitten144"),
    (("sitting144", "key"), "cmrdmlq144"),
    (("sitting144", "lemon"), "dmfhvyk144"),
    (("sitting144", "a"), "sitting144"),
    (("sitting144", "zz"), "rhsshmf144"),
    (("sitting144", "AgentU"), "soxgbhg144"),
    (("sitting144", "keyboard"), "cmruwnx144"),
    (("sitting144", "AA"), "sitting144"),
    (("agent144", "key"), "kkcxx144"),
    (("agent144", "lemon"), "lkqbg144"),
    (("agent144", "a"), "agent144"),
    (("agent144", "zz"), "zfdms144"),
    (("agent144", "AgentU"), "amiam144"),
    (("agent144", "keyboard"), "kkcoh144"),
    (("agent144", "AA"), "agent144"),
    (("angle144", "key"), "krevi144"),
    (("angle144", "lemon"), "lrszr144"),
    (("angle144", "a"), "angle144"),
    (("angle144", "zz"), "zmfkd144"),
    (("angle144", "AgentU"), "atkyx144"),
    (("angle144", "keyboard"), "krems144"),
    (("angle144", "AA"), "angle144"),
    (("universe144", "key"), "ergfipci144"),
    (("universe144", "lemon"), "frujrcwq144"),
    (("universe144", "a"), "universe144"),
    (("universe144", "zz"), "tmhudqrd144"),
    (("universe144", "AgentU"), "utmixlsk144"),
    (("universe144", "keyboard"), "ergwsrjh144"),
    (("universe144", "AA"), "universe144"),
    (("memory144", "key"), "wikyvw144"),
    (("memory144", "lemon"), "xiycej144"),
    (("memory144", "a"), "memory144"),
    (("memory144", "zz"), "ldlnqx144"),
    (("memory144", "AgentU"), "mkqbks144"),
    (("memory144", "keyboard"), "wikpfy144"),
    (("memory144", "AA"), "memory144"),
    (("stream144", "key"), "cxpoek144"),
    (("stream144", "lemon"), "dxdsnx144"),
    (("stream144", "a"), "stream144"),
    (("stream144", "zz"), "rsqdzl144"),
    (("stream144", "AgentU"), "szvrtg144"),
    (("stream144", "keyboard"), "cxpfom144"),
    (("stream144", "AA"), "stream144"),
    (("context144", "key"), "msldivd144"),
    (("context144", "lemon"), "nszhrix144"),
    (("context144", "a"), "context144"),
    (("context144", "zz"), "bnmsdws144"),
    (("context144", "AgentU"), "curgxrt144"),
    (("context144", "keyboard"), "mslusxk144"),
    (("context144", "AA"), "context144"),
    (("knowledge144", "key"), "urmgpcnkc144"),
    (("knowledge144", "lemon"), "vrakyphss144"),
    (("knowledge144", "a"), "knowledge144"),
    (("knowledge144", "zz"), "jmnvkdcfd144"),
    (("knowledge144", "AgentU"), "ktsjeydmi144"),
    (("knowledge144", "keyboard"), "urmxzeujo144"),
    (("knowledge144", "AA"), "knowledge144"),
    (("vector144", "key"), "fiadsp144"),
    (("vector144", "lemon"), "giohbc144"),
    (("vector144", "a"), "vector144"),
    (("vector144", "zz"), "udbsnq144"),
    (("vector144", "AgentU"), "vkgghl144"),
    (("vector144", "keyboard"), "fiaucr144"),
    (("vector144", "AA"), "vector144"),
    (("processor144", "key"), "zvmmiqcsp144"),
    (("processor144", "lemon"), "avaqrdwaf144"),
    (("processor144", "a"), "processor144"),
    (("processor144", "zz"), "oqnbdrrnq144"),
    (("processor144", "AgentU"), "pxspxmsuv144"),
    (("processor144", "keyboard"), "zvmdssjrb144"),
    (("processor144", "AA"), "processor144"),
    (("reasoning144", "key"), "biycslsre144"),
    (("reasoning144", "lemon"), "cimgbymzu144"),
    (("reasoning144", "a"), "reasoning144"),
    (("reasoning144", "zz"), "qdzrnmhmf144"),
    (("reasoning144", "AgentU"), "rkefhhitk144"),
    (("reasoning144", "keyboard"), "biytcnzqq144"),
    (("reasoning144", "AA"), "reasoning144"),
    (("machine144", "key"), "wearmlo144"),
    (("machine144", "lemon"), "xeovvyi144"),
    (("machine144", "a"), "machine144"),
    (("machine144", "zz"), "lzbghmd144"),
    (("machine144", "AgentU"), "mggubhe144"),
    (("machine144", "keyboard"), "weaiwnv144"),
    (("machine144", "AA"), "machine144"),
    (("learning144", "key"), "viybrgxk144"),
    (("learning144", "lemon"), "wimfatrs144"),
    (("learning144", "a"), "learning144"),
    (("learning144", "zz"), "kdzqmhmf144"),
    (("learning144", "AgentU"), "lkeegcnm144"),
    (("learning144", "keyboard"), "viysbiej144"),
    (("learning144", "AA"), "learning144"),
    (("model144", "key"), "wsbop144"),
    (("model144", "lemon"), "xspsy144"),
    (("model144", "a"), "model144"),
    (("model144", "zz"), "lncdk144"),
    (("model144", "AgentU"), "muhre144"),
    (("model144", "keyboard"), "wsbfz144"),
    (("model144", "AA"), "model144"),
    (("token144", "key"), "dsior144"),
    (("token144", "lemon"), "eswsa144"),
    (("token144", "a"), "token144"),
    (("token144", "zz"), "snjdm144"),
    (("token144", "AgentU"), "tuorg144"),
    (("token144", "keyboard"), "dsifb144"),
    (("token144", "AA"), "token144"),
    (("prompt144", "key"), "zvmwtr144"),
    (("prompt144", "lemon"), "avaace144"),
    (("prompt144", "a"), "prompt144"),
    (("prompt144", "zz"), "oqnlos144"),
    (("prompt144", "AgentU"), "pxszin144"),
    (("prompt144", "keyboard"), "zvmndt144"),
    (("prompt144", "AA"), "prompt144"),
    (("session144", "key"), "ciqcmmx144"),
    (("session144", "lemon"), "diegvzr144"),
    (("session144", "a"), "session144"),
    (("session144", "zz"), "rdrrhnm144"),
    (("session144", "AgentU"), "skwfbin144"),
    (("session144", "keyboard"), "ciqtwoe144"),
    (("session144", "AA"), "session144"),
    (("library144", "key"), "vmzbepi144"),
    (("library144", "lemon"), "wmnfncc144"),
    (("library144", "a"), "library144"),
    (("library144", "zz"), "khaqzqx144"),
    (("library144", "AgentU"), "lofetly144"),
    (("library144", "keyboard"), "vmzsorp144"),
    (("library144", "AA"), "library144"),
    (("service144", "key"), "cipfmao144"),
    (("service144", "lemon"), "didjvni144"),
    (("service144", "a"), "service144"),
    (("service144", "zz"), "rdquhbd144"),
    (("service144", "AgentU"), "skvibwe144"),
    (("service144", "keyboard"), "cipwwcv144"),
    (("service144", "AA"), "service144"),
    (("gateway144", "key"), "qeroayi144"),
    (("gateway144", "lemon"), "refsjlc144"),
    (("gateway144", "a"), "gateway144"),
    (("gateway144", "zz"), "fzsdvzx144"),
    (("gateway144", "AgentU"), "ggxrpuy144"),
    (("gateway144", "keyboard"), "qerfkap144"),
    (("gateway144", "AA"), "gateway144"),
    (("storage144", "key"), "cxmbeeo144"),
    (("storage144", "lemon"), "dxafnri144"),
    (("storage144", "a"), "storage144"),
    (("storage144", "zz"), "rsnqzfd144"),
    (("storage144", "AgentU"), "szsetae144"),
    (("storage144", "keyboard"), "cxmsogv144"),
    (("storage144", "AA"), "storage144"),
    (("network144", "key"), "xirgspu144"),
    (("network144", "lemon"), "yifkbco144"),
    (("network144", "a"), "network144"),
    (("network144", "zz"), "mdsvnqj144"),
    (("network144", "AgentU"), "nkxjhlk144"),
    (("network144", "keyboard"), "xirxcrb144"),
    (("network144", "AA"), "network144"),
    (("latency144", "key"), "verorai144"),
    (("latency144", "lemon"), "wefsanc144"),
    (("latency144", "a"), "latency144"),
    (("latency144", "zz"), "kzsdmbx144"),
    (("latency144", "AgentU"), "lgxrgwy144"),
    (("latency144", "keyboard"), "verfbcp144"),
    (("latency144", "AA"), "latency144"),
    (("buffer144", "key"), "lydpip144"),
    (("buffer144", "lemon"), "myrtrc144"),
    (("buffer144", "a"), "buffer144"),
    (("buffer144", "zz"), "ateedq144"),
    (("buffer144", "AgentU"), "bajsxl144"),
    (("buffer144", "keyboard"), "lydgsr144"),
    (("buffer144", "AA"), "buffer144"),
    (("queue144", "key"), "aycei144"),
    (("queue144", "lemon"), "byqir144"),
    (("queue144", "a"), "queue144"),
    (("queue144", "zz"), "ptdtd144"),
    (("queue144", "AgentU"), "qaihx144"),
    (("queue144", "keyboard"), "aycvs144"),
    (("queue144", "AA"), "queue144"),
    (("worker144", "key"), "gspuip144"),
    (("worker144", "lemon"), "hsdyrc144"),
    (("worker144", "a"), "worker144"),
    (("worker144", "zz"), "vnqjdq144"),
    (("worker144", "AgentU"), "wuvxxl144"),
    (("worker144", "keyboard"), "gsplsr144"),
    (("worker144", "AA"), "worker144"),
    (("kernel144", "key"), "uipxij144"),
    (("kernel144", "lemon"), "vidbrw144"),
    (("kernel144", "a"), "kernel144"),
    (("kernel144", "zz"), "jdqmdk144"),
    (("kernel144", "AgentU"), "kkvaxf144"),
    (("kernel144", "keyboard"), "uiposl144"),
    (("kernel144", "AA"), "kernel144"),
    (("signal144", "key"), "cmexej144"),
    (("signal144", "lemon"), "dmsbnw144"),
    (("signal144", "a"), "signal144"),
    (("signal144", "zz"), "rhfmzk144"),
    (("signal144", "AgentU"), "sokatf144"),
    (("signal144", "keyboard"), "cmeool144"),
    (("signal144", "AA"), "signal144"),
    (("packet144", "key"), "zeauir144"),
    (("packet144", "lemon"), "aeoyre144"),
    (("packet144", "a"), "packet144"),
    (("packet144", "zz"), "ozbjds144"),
    (("packet144", "AgentU"), "pggxxn144"),
    (("packet144", "keyboard"), "zealst144"),
    (("packet144", "AA"), "packet144"),
    (("router144", "key"), "bssdip144"),
    (("router144", "lemon"), "csghrc144"),
    (("router144", "a"), "router144"),
    (("router144", "zz"), "qntsdq144"),
    (("router144", "AgentU"), "ruygxl144"),
    (("router144", "keyboard"), "bssusr144"),
    (("router144", "AA"), "router144"),
    (("cluster144", "key"), "mpscxcb144"),
    (("cluster144", "lemon"), "npgggpv144"),
    (("cluster144", "a"), "cluster144"),
    (("cluster144", "zz"), "bktrsdq144"),
    (("cluster144", "AgentU"), "cryfmyr144"),
    (("cluster144", "keyboard"), "mpsthei144"),
    (("cluster144", "AA"), "cluster144"),
    (("mirror144", "key"), "wmpbsp144"),
    (("mirror144", "lemon"), "xmdfbc144"),
    (("mirror144", "a"), "mirror144"),
    (("mirror144", "zz"), "lhqqnq144"),
    (("mirror144", "AgentU"), "movehl144"),
    (("mirror144", "keyboard"), "wmpscr144"),
    (("mirror144", "AA"), "mirror144"),
    (("filter144", "key"), "pmjdip144"),
    (("filter144", "lemon"), "qmxhrc144"),
    (("filter144", "a"), "filter144"),
    (("filter144", "zz"), "ehksdq144"),
    (("filter144", "AgentU"), "fopgxl144"),
    (("filter144", "keyboard"), "pmjusr144"),
    (("filter144", "AA"), "filter144"),
    (("ranking144", "key"), "belumlq144"),
    (("ranking144", "lemon"), "cezyvyk144"),
    (("ranking144", "a"), "ranking144"),
    (("ranking144", "zz"), "qzmjhmf144"),
    (("ranking144", "AgentU"), "rgrxbhg144"),
    (("ranking144", "keyboard"), "bellwnx144"),
    (("ranking144", "AA"), "ranking144"),
    (("encoding144", "key"), "orayhgxk144"),
    (("encoding144", "lemon"), "procqtrs144"),
    (("encoding144", "a"), "encoding144"),
    (("encoding144", "zz"), "dmbnchmf144"),
    (("encoding144", "AgentU"), "etgbwcnm144"),
    (("encoding144", "keyboard"), "orapriej144"),
    (("encoding144", "AA"), "encoding144"),
    (("mapping144", "key"), "wenzmlq144"),
    (("mapping144", "lemon"), "xebdvyk144"),
    (("mapping144", "a"), "mapping144"),
    (("mapping144", "zz"), "lzoohmf144"),
    (("mapping144", "AgentU"), "mgtcbhg144"),
    (("mapping144", "keyboard"), "wenqwnx144"),
    (("mapping144", "AA"), "mapping144"),
    (("record144", "key"), "biayvb144"),
    (("record144", "lemon"), "cioceo144"),
    (("record144", "a"), "record144"),
    (("record144", "zz"), "qdbnqc144"),
    (("record144", "AgentU"), "rkgbkx144"),
    (("record144", "keyboard"), "biapfd144"),
    (("record144", "AA"), "record144"),
    (("candle144", "key"), "melnpc144"),
    (("candle144", "lemon"), "nezryp144"),
    (("candle144", "a"), "candle144"),
    (("candle144", "zz"), "bzmckd144"),
    (("candle144", "AgentU"), "cgrqey144"),
    (("candle144", "keyboard"), "meleze144"),
    (("candle144", "AA"), "candle144"),
    (("thread144", "key"), "dlpoeb144"),
    (("thread144", "lemon"), "eldsno144"),
    (("thread144", "a"), "thread144"),
    (("thread144", "zz"), "sgqdzc144"),
    (("thread144", "AgentU"), "tnvrtx144"),
    (("thread144", "keyboard"), "dlpfod144"),
    (("thread144", "AA"), "thread144"),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 144: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 144: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "a"),
        "round 144: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 144: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 144: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 144: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", "AA"),
        "round 144: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "key"),
        "bssxh 144: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 144: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "a"),
        "round 144: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 144: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 144: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 144: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", "AA"),
        "round 144: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 144: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 144: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "a"),
        "round 144: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 144: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 144: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 144: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", "AA"),
        "round 144: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 144: the processor reads the record then stops", "key"),
        "bssxh 144: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 144: the processor reads the record then stops", "lemon"),
        "csgbq 144: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 144: the processor reads the record then stops", "a"),
        "round 144: the processor reads the record then stops",
    ),
    (
        ("round 144: the processor reads the record then stops", "zz"),
        "qntmc 144: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 144: the processor reads the record then stops", "AgentU"),
        "ruyaw 144: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 144: the processor reads the record then stops", "keyboard"),
        "bssor 144: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 144: the processor reads the record then stops", "AA"),
        "round 144: the processor reads the record then stops",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "key"),
        "bssxh 144: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "lemon"),
        "csgbq 144: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "a"),
        "round 144: a worker pulls the next task from the queue",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "zz"),
        "qntmc 144: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 144: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "keyboard"),
        "bssor 144: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 144: a worker pulls the next task from the queue", "AA"),
        "round 144: a worker pulls the next task from the queue",
    ),
    (
        ("round 144: signals travel through the network layer", "key"),
        "bssxh 144: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 144: signals travel through the network layer", "lemon"),
        "csgbq 144: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 144: signals travel through the network layer", "a"),
        "round 144: signals travel through the network layer",
    ),
    (
        ("round 144: signals travel through the network layer", "zz"),
        "qntmc 144: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 144: signals travel through the network layer", "AgentU"),
        "ruyaw 144: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 144: signals travel through the network layer", "keyboard"),
        "bssor 144: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 144: signals travel through the network layer", "AA"),
        "round 144: signals travel through the network layer",
    ),
    (
        ("round 144: the gateway routes each request by policy", "key"),
        "bssxh 144: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 144: the gateway routes each request by policy", "lemon"),
        "csgbq 144: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 144: the gateway routes each request by policy", "a"),
        "round 144: the gateway routes each request by policy",
    ),
    (
        ("round 144: the gateway routes each request by policy", "zz"),
        "qntmc 144: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 144: the gateway routes each request by policy", "AgentU"),
        "ruyaw 144: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 144: the gateway routes each request by policy", "keyboard"),
        "bssor 144: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 144: the gateway routes each request by policy", "AA"),
        "round 144: the gateway routes each request by policy",
    ),
    (("round 144: memory grows until the buffer is full", "key"), "bssxh 144: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 144: memory grows until the buffer is full", "lemon"), "csgbq 144: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 144: memory grows until the buffer is full", "a"), "round 144: memory grows until the buffer is full"),
    (("round 144: memory grows until the buffer is full", "zz"), "qntmc 144: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 144: memory grows until the buffer is full", "AgentU"),
        "ruyaw 144: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 144: memory grows until the buffer is full", "keyboard"),
        "bssor 144: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 144: memory grows until the buffer is full", "AA"), "round 144: memory grows until the buffer is full"),
    (("round 144: the cluster mirrors every packet twice", "key"), "bssxh 144: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 144: the cluster mirrors every packet twice", "lemon"),
        "csgbq 144: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 144: the cluster mirrors every packet twice", "a"), "round 144: the cluster mirrors every packet twice"),
    (("round 144: the cluster mirrors every packet twice", "zz"), "qntmc 144: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 144: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 144: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 144: the cluster mirrors every packet twice", "keyboard"),
        "bssor 144: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 144: the cluster mirrors every packet twice", "AA"), "round 144: the cluster mirrors every packet twice"),
    (
        ("round 144: ranking uses tokens learned from the corpus", "key"),
        "bssxh 144: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 144: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", "a"),
        "round 144: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 144: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 144: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 144: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", "AA"),
        "round 144: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 144: a long session ends when the candle dies", "key"),
        "bssxh 144: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 144: a long session ends when the candle dies", "lemon"),
        "csgbq 144: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 144: a long session ends when the candle dies", "a"),
        "round 144: a long session ends when the candle dies",
    ),
    (
        ("round 144: a long session ends when the candle dies", "zz"),
        "qntmc 144: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 144: a long session ends when the candle dies", "AgentU"),
        "ruyaw 144: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 144: a long session ends when the candle dies", "keyboard"),
        "bssor 144: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 144: a long session ends when the candle dies", "AA"),
        "round 144: a long session ends when the candle dies",
    ),
    (("round 144: encode the prompt then map the result", "key"), "bssxh 144: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 144: encode the prompt then map the result", "lemon"), "csgbq 144: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 144: encode the prompt then map the result", "a"), "round 144: encode the prompt then map the result"),
    (("round 144: encode the prompt then map the result", "zz"), "qntmc 144: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 144: encode the prompt then map the result", "AgentU"),
        "ruyaw 144: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 144: encode the prompt then map the result", "keyboard"),
        "bssor 144: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 144: encode the prompt then map the result", "AA"), "round 144: encode the prompt then map the result"),
    (("round 144: the kernel wakes the worker at dawn", "key"), "bssxh 144: rri iovlop ukocc xfo ambocb er neux"),
    (("round 144: the kernel wakes the worker at dawn", "lemon"), "csgbq 144: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 144: the kernel wakes the worker at dawn", "a"), "round 144: the kernel wakes the worker at dawn"),
    (("round 144: the kernel wakes the worker at dawn", "zz"), "qntmc 144: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 144: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 144: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 144: the kernel wakes the worker at dawn", "keyboard"), "bssor 144: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 144: the kernel wakes the worker at dawn", "AA"), "round 144: the kernel wakes the worker at dawn"),
    (("round 144: service latency drops after the patch", "key"), "bssxh 144: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 144: service latency drops after the patch", "lemon"), "csgbq 144: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 144: service latency drops after the patch", "a"), "round 144: service latency drops after the patch"),
    (("round 144: service latency drops after the patch", "zz"), "qntmc 144: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 144: service latency drops after the patch", "AgentU"),
        "ruyaw 144: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 144: service latency drops after the patch", "keyboard"),
        "bssor 144: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 144: service latency drops after the patch", "AA"), "round 144: service latency drops after the patch"),
    (
        ("round 144: the library caches every vector it sees", "key"),
        "bssxh 144: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 144: the library caches every vector it sees", "lemon"),
        "csgbq 144: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 144: the library caches every vector it sees", "a"), "round 144: the library caches every vector it sees"),
    (
        ("round 144: the library caches every vector it sees", "zz"),
        "qntmc 144: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 144: the library caches every vector it sees", "AgentU"),
        "ruyaw 144: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 144: the library caches every vector it sees", "keyboard"),
        "bssor 144: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 144: the library caches every vector it sees", "AA"),
        "round 144: the library caches every vector it sees",
    ),
    (("round 144: agents argue then the debate resolves", "key"), "bssxh 144: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 144: agents argue then the debate resolves", "lemon"), "csgbq 144: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 144: agents argue then the debate resolves", "a"), "round 144: agents argue then the debate resolves"),
    (("round 144: agents argue then the debate resolves", "zz"), "qntmc 144: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 144: agents argue then the debate resolves", "AgentU"),
        "ruyaw 144: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 144: agents argue then the debate resolves", "keyboard"),
        "bssor 144: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 144: agents argue then the debate resolves", "AA"), "round 144: agents argue then the debate resolves"),
    (("round 144: the filter keeps only strong matches", "key"), "bssxh 144: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 144: the filter keeps only strong matches", "lemon"), "csgbq 144: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 144: the filter keeps only strong matches", "a"), "round 144: the filter keeps only strong matches"),
    (("round 144: the filter keeps only strong matches", "zz"), "qntmc 144: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 144: the filter keeps only strong matches", "AgentU"), "ruyaw 144: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 144: the filter keeps only strong matches", "keyboard"),
        "bssor 144: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 144: the filter keeps only strong matches", "AA"), "round 144: the filter keeps only strong matches"),
    (("round 144: the model answers with a short reply", "key"), "bssxh 144: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 144: the model answers with a short reply", "lemon"), "csgbq 144: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 144: the model answers with a short reply", "a"), "round 144: the model answers with a short reply"),
    (("round 144: the model answers with a short reply", "zz"), "qntmc 144: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 144: the model answers with a short reply", "AgentU"), "ruyaw 144: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 144: the model answers with a short reply", "keyboard"),
        "bssor 144: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 144: the model answers with a short reply", "AA"), "round 144: the model answers with a short reply"),
    (
        ("round 144: the recorder stores the reasoning trace", "key"),
        "bssxh 144: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 144: the recorder stores the reasoning trace", "lemon"),
        "csgbq 144: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 144: the recorder stores the reasoning trace", "a"), "round 144: the recorder stores the reasoning trace"),
    (
        ("round 144: the recorder stores the reasoning trace", "zz"),
        "qntmc 144: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 144: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 144: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 144: the recorder stores the reasoning trace", "keyboard"),
        "bssor 144: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 144: the recorder stores the reasoning trace", "AA"),
        "round 144: the recorder stores the reasoning trace",
    ),
    (("round 144: the angel watches the processor run", "key"), "bssxh 144: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 144: the angel watches the processor run", "lemon"), "csgbq 144: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 144: the angel watches the processor run", "a"), "round 144: the angel watches the processor run"),
    (("round 144: the angel watches the processor run", "zz"), "qntmc 144: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 144: the angel watches the processor run", "AgentU"), "ruyaw 144: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 144: the angel watches the processor run", "keyboard"), "bssor 144: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 144: the angel watches the processor run", "AA"), "round 144: the angel watches the processor run"),
    (("round 144: angle of the vector decides the match", "key"), "bssxh 144: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 144: angle of the vector decides the match", "lemon"), "csgbq 144: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 144: angle of the vector decides the match", "a"), "round 144: angle of the vector decides the match"),
    (("round 144: angle of the vector decides the match", "zz"), "qntmc 144: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 144: angle of the vector decides the match", "AgentU"),
        "ruyaw 144: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 144: angle of the vector decides the match", "keyboard"),
        "bssor 144: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 144: angle of the vector decides the match", "AA"), "round 144: angle of the vector decides the match"),
    (
        ("round 144: the candle burns twice as long at night", "key"),
        "bssxh 144: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 144: the candle burns twice as long at night", "lemon"),
        "csgbq 144: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 144: the candle burns twice as long at night", "a"), "round 144: the candle burns twice as long at night"),
    (
        ("round 144: the candle burns twice as long at night", "zz"),
        "qntmc 144: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 144: the candle burns twice as long at night", "AgentU"),
        "ruyaw 144: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 144: the candle burns twice as long at night", "keyboard"),
        "bssor 144: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 144: the candle burns twice as long at night", "AA"),
        "round 144: the candle burns twice as long at night",
    ),
    (("round 144: a mirror of the universe in one line", "key"), "bssxh 144: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 144: a mirror of the universe in one line", "lemon"), "csgbq 144: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 144: a mirror of the universe in one line", "a"), "round 144: a mirror of the universe in one line"),
    (("round 144: a mirror of the universe in one line", "zz"), "qntmc 144: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 144: a mirror of the universe in one line", "AgentU"), "ruyaw 144: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 144: a mirror of the universe in one line", "keyboard"),
        "bssor 144: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 144: a mirror of the universe in one line", "AA"), "round 144: a mirror of the universe in one line"),
    (("round 144: the queue drains before the storm", "key"), "bssxh 144: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 144: the queue drains before the storm", "lemon"), "csgbq 144: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 144: the queue drains before the storm", "a"), "round 144: the queue drains before the storm"),
    (("round 144: the queue drains before the storm", "zz"), "qntmc 144: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 144: the queue drains before the storm", "AgentU"), "ruyaw 144: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 144: the queue drains before the storm", "keyboard"), "bssor 144: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 144: the queue drains before the storm", "AA"), "round 144: the queue drains before the storm"),
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
