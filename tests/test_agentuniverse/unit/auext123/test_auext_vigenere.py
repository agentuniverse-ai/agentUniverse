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
    (("kitten123", "key"), "umrdil123"),
    (("kitten123", "lemon"), "vmfhry123"),
    (("kitten123", "a"), "kitten123"),
    (("kitten123", "zz"), "jhssdm123"),
    (("kitten123", "AgentU"), "koxgxh123"),
    (("kitten123", "keyboard"), "umrusn123"),
    (("kitten123", "AA"), "kitten123"),
    (("sitting123", "key"), "cmrdmlq123"),
    (("sitting123", "lemon"), "dmfhvyk123"),
    (("sitting123", "a"), "sitting123"),
    (("sitting123", "zz"), "rhsshmf123"),
    (("sitting123", "AgentU"), "soxgbhg123"),
    (("sitting123", "keyboard"), "cmruwnx123"),
    (("sitting123", "AA"), "sitting123"),
    (("agent123", "key"), "kkcxx123"),
    (("agent123", "lemon"), "lkqbg123"),
    (("agent123", "a"), "agent123"),
    (("agent123", "zz"), "zfdms123"),
    (("agent123", "AgentU"), "amiam123"),
    (("agent123", "keyboard"), "kkcoh123"),
    (("agent123", "AA"), "agent123"),
    (("angle123", "key"), "krevi123"),
    (("angle123", "lemon"), "lrszr123"),
    (("angle123", "a"), "angle123"),
    (("angle123", "zz"), "zmfkd123"),
    (("angle123", "AgentU"), "atkyx123"),
    (("angle123", "keyboard"), "krems123"),
    (("angle123", "AA"), "angle123"),
    (("universe123", "key"), "ergfipci123"),
    (("universe123", "lemon"), "frujrcwq123"),
    (("universe123", "a"), "universe123"),
    (("universe123", "zz"), "tmhudqrd123"),
    (("universe123", "AgentU"), "utmixlsk123"),
    (("universe123", "keyboard"), "ergwsrjh123"),
    (("universe123", "AA"), "universe123"),
    (("memory123", "key"), "wikyvw123"),
    (("memory123", "lemon"), "xiycej123"),
    (("memory123", "a"), "memory123"),
    (("memory123", "zz"), "ldlnqx123"),
    (("memory123", "AgentU"), "mkqbks123"),
    (("memory123", "keyboard"), "wikpfy123"),
    (("memory123", "AA"), "memory123"),
    (("stream123", "key"), "cxpoek123"),
    (("stream123", "lemon"), "dxdsnx123"),
    (("stream123", "a"), "stream123"),
    (("stream123", "zz"), "rsqdzl123"),
    (("stream123", "AgentU"), "szvrtg123"),
    (("stream123", "keyboard"), "cxpfom123"),
    (("stream123", "AA"), "stream123"),
    (("context123", "key"), "msldivd123"),
    (("context123", "lemon"), "nszhrix123"),
    (("context123", "a"), "context123"),
    (("context123", "zz"), "bnmsdws123"),
    (("context123", "AgentU"), "curgxrt123"),
    (("context123", "keyboard"), "mslusxk123"),
    (("context123", "AA"), "context123"),
    (("knowledge123", "key"), "urmgpcnkc123"),
    (("knowledge123", "lemon"), "vrakyphss123"),
    (("knowledge123", "a"), "knowledge123"),
    (("knowledge123", "zz"), "jmnvkdcfd123"),
    (("knowledge123", "AgentU"), "ktsjeydmi123"),
    (("knowledge123", "keyboard"), "urmxzeujo123"),
    (("knowledge123", "AA"), "knowledge123"),
    (("vector123", "key"), "fiadsp123"),
    (("vector123", "lemon"), "giohbc123"),
    (("vector123", "a"), "vector123"),
    (("vector123", "zz"), "udbsnq123"),
    (("vector123", "AgentU"), "vkgghl123"),
    (("vector123", "keyboard"), "fiaucr123"),
    (("vector123", "AA"), "vector123"),
    (("processor123", "key"), "zvmmiqcsp123"),
    (("processor123", "lemon"), "avaqrdwaf123"),
    (("processor123", "a"), "processor123"),
    (("processor123", "zz"), "oqnbdrrnq123"),
    (("processor123", "AgentU"), "pxspxmsuv123"),
    (("processor123", "keyboard"), "zvmdssjrb123"),
    (("processor123", "AA"), "processor123"),
    (("reasoning123", "key"), "biycslsre123"),
    (("reasoning123", "lemon"), "cimgbymzu123"),
    (("reasoning123", "a"), "reasoning123"),
    (("reasoning123", "zz"), "qdzrnmhmf123"),
    (("reasoning123", "AgentU"), "rkefhhitk123"),
    (("reasoning123", "keyboard"), "biytcnzqq123"),
    (("reasoning123", "AA"), "reasoning123"),
    (("machine123", "key"), "wearmlo123"),
    (("machine123", "lemon"), "xeovvyi123"),
    (("machine123", "a"), "machine123"),
    (("machine123", "zz"), "lzbghmd123"),
    (("machine123", "AgentU"), "mggubhe123"),
    (("machine123", "keyboard"), "weaiwnv123"),
    (("machine123", "AA"), "machine123"),
    (("learning123", "key"), "viybrgxk123"),
    (("learning123", "lemon"), "wimfatrs123"),
    (("learning123", "a"), "learning123"),
    (("learning123", "zz"), "kdzqmhmf123"),
    (("learning123", "AgentU"), "lkeegcnm123"),
    (("learning123", "keyboard"), "viysbiej123"),
    (("learning123", "AA"), "learning123"),
    (("model123", "key"), "wsbop123"),
    (("model123", "lemon"), "xspsy123"),
    (("model123", "a"), "model123"),
    (("model123", "zz"), "lncdk123"),
    (("model123", "AgentU"), "muhre123"),
    (("model123", "keyboard"), "wsbfz123"),
    (("model123", "AA"), "model123"),
    (("token123", "key"), "dsior123"),
    (("token123", "lemon"), "eswsa123"),
    (("token123", "a"), "token123"),
    (("token123", "zz"), "snjdm123"),
    (("token123", "AgentU"), "tuorg123"),
    (("token123", "keyboard"), "dsifb123"),
    (("token123", "AA"), "token123"),
    (("prompt123", "key"), "zvmwtr123"),
    (("prompt123", "lemon"), "avaace123"),
    (("prompt123", "a"), "prompt123"),
    (("prompt123", "zz"), "oqnlos123"),
    (("prompt123", "AgentU"), "pxszin123"),
    (("prompt123", "keyboard"), "zvmndt123"),
    (("prompt123", "AA"), "prompt123"),
    (("session123", "key"), "ciqcmmx123"),
    (("session123", "lemon"), "diegvzr123"),
    (("session123", "a"), "session123"),
    (("session123", "zz"), "rdrrhnm123"),
    (("session123", "AgentU"), "skwfbin123"),
    (("session123", "keyboard"), "ciqtwoe123"),
    (("session123", "AA"), "session123"),
    (("library123", "key"), "vmzbepi123"),
    (("library123", "lemon"), "wmnfncc123"),
    (("library123", "a"), "library123"),
    (("library123", "zz"), "khaqzqx123"),
    (("library123", "AgentU"), "lofetly123"),
    (("library123", "keyboard"), "vmzsorp123"),
    (("library123", "AA"), "library123"),
    (("service123", "key"), "cipfmao123"),
    (("service123", "lemon"), "didjvni123"),
    (("service123", "a"), "service123"),
    (("service123", "zz"), "rdquhbd123"),
    (("service123", "AgentU"), "skvibwe123"),
    (("service123", "keyboard"), "cipwwcv123"),
    (("service123", "AA"), "service123"),
    (("gateway123", "key"), "qeroayi123"),
    (("gateway123", "lemon"), "refsjlc123"),
    (("gateway123", "a"), "gateway123"),
    (("gateway123", "zz"), "fzsdvzx123"),
    (("gateway123", "AgentU"), "ggxrpuy123"),
    (("gateway123", "keyboard"), "qerfkap123"),
    (("gateway123", "AA"), "gateway123"),
    (("storage123", "key"), "cxmbeeo123"),
    (("storage123", "lemon"), "dxafnri123"),
    (("storage123", "a"), "storage123"),
    (("storage123", "zz"), "rsnqzfd123"),
    (("storage123", "AgentU"), "szsetae123"),
    (("storage123", "keyboard"), "cxmsogv123"),
    (("storage123", "AA"), "storage123"),
    (("network123", "key"), "xirgspu123"),
    (("network123", "lemon"), "yifkbco123"),
    (("network123", "a"), "network123"),
    (("network123", "zz"), "mdsvnqj123"),
    (("network123", "AgentU"), "nkxjhlk123"),
    (("network123", "keyboard"), "xirxcrb123"),
    (("network123", "AA"), "network123"),
    (("latency123", "key"), "verorai123"),
    (("latency123", "lemon"), "wefsanc123"),
    (("latency123", "a"), "latency123"),
    (("latency123", "zz"), "kzsdmbx123"),
    (("latency123", "AgentU"), "lgxrgwy123"),
    (("latency123", "keyboard"), "verfbcp123"),
    (("latency123", "AA"), "latency123"),
    (("buffer123", "key"), "lydpip123"),
    (("buffer123", "lemon"), "myrtrc123"),
    (("buffer123", "a"), "buffer123"),
    (("buffer123", "zz"), "ateedq123"),
    (("buffer123", "AgentU"), "bajsxl123"),
    (("buffer123", "keyboard"), "lydgsr123"),
    (("buffer123", "AA"), "buffer123"),
    (("queue123", "key"), "aycei123"),
    (("queue123", "lemon"), "byqir123"),
    (("queue123", "a"), "queue123"),
    (("queue123", "zz"), "ptdtd123"),
    (("queue123", "AgentU"), "qaihx123"),
    (("queue123", "keyboard"), "aycvs123"),
    (("queue123", "AA"), "queue123"),
    (("worker123", "key"), "gspuip123"),
    (("worker123", "lemon"), "hsdyrc123"),
    (("worker123", "a"), "worker123"),
    (("worker123", "zz"), "vnqjdq123"),
    (("worker123", "AgentU"), "wuvxxl123"),
    (("worker123", "keyboard"), "gsplsr123"),
    (("worker123", "AA"), "worker123"),
    (("kernel123", "key"), "uipxij123"),
    (("kernel123", "lemon"), "vidbrw123"),
    (("kernel123", "a"), "kernel123"),
    (("kernel123", "zz"), "jdqmdk123"),
    (("kernel123", "AgentU"), "kkvaxf123"),
    (("kernel123", "keyboard"), "uiposl123"),
    (("kernel123", "AA"), "kernel123"),
    (("signal123", "key"), "cmexej123"),
    (("signal123", "lemon"), "dmsbnw123"),
    (("signal123", "a"), "signal123"),
    (("signal123", "zz"), "rhfmzk123"),
    (("signal123", "AgentU"), "sokatf123"),
    (("signal123", "keyboard"), "cmeool123"),
    (("signal123", "AA"), "signal123"),
    (("packet123", "key"), "zeauir123"),
    (("packet123", "lemon"), "aeoyre123"),
    (("packet123", "a"), "packet123"),
    (("packet123", "zz"), "ozbjds123"),
    (("packet123", "AgentU"), "pggxxn123"),
    (("packet123", "keyboard"), "zealst123"),
    (("packet123", "AA"), "packet123"),
    (("router123", "key"), "bssdip123"),
    (("router123", "lemon"), "csghrc123"),
    (("router123", "a"), "router123"),
    (("router123", "zz"), "qntsdq123"),
    (("router123", "AgentU"), "ruygxl123"),
    (("router123", "keyboard"), "bssusr123"),
    (("router123", "AA"), "router123"),
    (("cluster123", "key"), "mpscxcb123"),
    (("cluster123", "lemon"), "npgggpv123"),
    (("cluster123", "a"), "cluster123"),
    (("cluster123", "zz"), "bktrsdq123"),
    (("cluster123", "AgentU"), "cryfmyr123"),
    (("cluster123", "keyboard"), "mpsthei123"),
    (("cluster123", "AA"), "cluster123"),
    (("mirror123", "key"), "wmpbsp123"),
    (("mirror123", "lemon"), "xmdfbc123"),
    (("mirror123", "a"), "mirror123"),
    (("mirror123", "zz"), "lhqqnq123"),
    (("mirror123", "AgentU"), "movehl123"),
    (("mirror123", "keyboard"), "wmpscr123"),
    (("mirror123", "AA"), "mirror123"),
    (("filter123", "key"), "pmjdip123"),
    (("filter123", "lemon"), "qmxhrc123"),
    (("filter123", "a"), "filter123"),
    (("filter123", "zz"), "ehksdq123"),
    (("filter123", "AgentU"), "fopgxl123"),
    (("filter123", "keyboard"), "pmjusr123"),
    (("filter123", "AA"), "filter123"),
    (("ranking123", "key"), "belumlq123"),
    (("ranking123", "lemon"), "cezyvyk123"),
    (("ranking123", "a"), "ranking123"),
    (("ranking123", "zz"), "qzmjhmf123"),
    (("ranking123", "AgentU"), "rgrxbhg123"),
    (("ranking123", "keyboard"), "bellwnx123"),
    (("ranking123", "AA"), "ranking123"),
    (("encoding123", "key"), "orayhgxk123"),
    (("encoding123", "lemon"), "procqtrs123"),
    (("encoding123", "a"), "encoding123"),
    (("encoding123", "zz"), "dmbnchmf123"),
    (("encoding123", "AgentU"), "etgbwcnm123"),
    (("encoding123", "keyboard"), "orapriej123"),
    (("encoding123", "AA"), "encoding123"),
    (("mapping123", "key"), "wenzmlq123"),
    (("mapping123", "lemon"), "xebdvyk123"),
    (("mapping123", "a"), "mapping123"),
    (("mapping123", "zz"), "lzoohmf123"),
    (("mapping123", "AgentU"), "mgtcbhg123"),
    (("mapping123", "keyboard"), "wenqwnx123"),
    (("mapping123", "AA"), "mapping123"),
    (("record123", "key"), "biayvb123"),
    (("record123", "lemon"), "cioceo123"),
    (("record123", "a"), "record123"),
    (("record123", "zz"), "qdbnqc123"),
    (("record123", "AgentU"), "rkgbkx123"),
    (("record123", "keyboard"), "biapfd123"),
    (("record123", "AA"), "record123"),
    (("candle123", "key"), "melnpc123"),
    (("candle123", "lemon"), "nezryp123"),
    (("candle123", "a"), "candle123"),
    (("candle123", "zz"), "bzmckd123"),
    (("candle123", "AgentU"), "cgrqey123"),
    (("candle123", "keyboard"), "meleze123"),
    (("candle123", "AA"), "candle123"),
    (("thread123", "key"), "dlpoeb123"),
    (("thread123", "lemon"), "eldsno123"),
    (("thread123", "a"), "thread123"),
    (("thread123", "zz"), "sgqdzc123"),
    (("thread123", "AgentU"), "tnvrtx123"),
    (("thread123", "keyboard"), "dlpfod123"),
    (("thread123", "AA"), "thread123"),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 123: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 123: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "a"),
        "round 123: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 123: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 123: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 123: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", "AA"),
        "round 123: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "key"),
        "bssxh 123: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 123: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "a"),
        "round 123: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 123: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 123: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 123: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", "AA"),
        "round 123: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 123: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 123: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "a"),
        "round 123: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 123: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 123: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 123: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", "AA"),
        "round 123: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 123: the processor reads the record then stops", "key"),
        "bssxh 123: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 123: the processor reads the record then stops", "lemon"),
        "csgbq 123: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 123: the processor reads the record then stops", "a"),
        "round 123: the processor reads the record then stops",
    ),
    (
        ("round 123: the processor reads the record then stops", "zz"),
        "qntmc 123: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 123: the processor reads the record then stops", "AgentU"),
        "ruyaw 123: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 123: the processor reads the record then stops", "keyboard"),
        "bssor 123: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 123: the processor reads the record then stops", "AA"),
        "round 123: the processor reads the record then stops",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "key"),
        "bssxh 123: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "lemon"),
        "csgbq 123: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "a"),
        "round 123: a worker pulls the next task from the queue",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "zz"),
        "qntmc 123: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 123: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "keyboard"),
        "bssor 123: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 123: a worker pulls the next task from the queue", "AA"),
        "round 123: a worker pulls the next task from the queue",
    ),
    (
        ("round 123: signals travel through the network layer", "key"),
        "bssxh 123: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 123: signals travel through the network layer", "lemon"),
        "csgbq 123: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 123: signals travel through the network layer", "a"),
        "round 123: signals travel through the network layer",
    ),
    (
        ("round 123: signals travel through the network layer", "zz"),
        "qntmc 123: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 123: signals travel through the network layer", "AgentU"),
        "ruyaw 123: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 123: signals travel through the network layer", "keyboard"),
        "bssor 123: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 123: signals travel through the network layer", "AA"),
        "round 123: signals travel through the network layer",
    ),
    (
        ("round 123: the gateway routes each request by policy", "key"),
        "bssxh 123: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 123: the gateway routes each request by policy", "lemon"),
        "csgbq 123: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 123: the gateway routes each request by policy", "a"),
        "round 123: the gateway routes each request by policy",
    ),
    (
        ("round 123: the gateway routes each request by policy", "zz"),
        "qntmc 123: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 123: the gateway routes each request by policy", "AgentU"),
        "ruyaw 123: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 123: the gateway routes each request by policy", "keyboard"),
        "bssor 123: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 123: the gateway routes each request by policy", "AA"),
        "round 123: the gateway routes each request by policy",
    ),
    (("round 123: memory grows until the buffer is full", "key"), "bssxh 123: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 123: memory grows until the buffer is full", "lemon"), "csgbq 123: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 123: memory grows until the buffer is full", "a"), "round 123: memory grows until the buffer is full"),
    (("round 123: memory grows until the buffer is full", "zz"), "qntmc 123: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 123: memory grows until the buffer is full", "AgentU"),
        "ruyaw 123: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 123: memory grows until the buffer is full", "keyboard"),
        "bssor 123: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 123: memory grows until the buffer is full", "AA"), "round 123: memory grows until the buffer is full"),
    (("round 123: the cluster mirrors every packet twice", "key"), "bssxh 123: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 123: the cluster mirrors every packet twice", "lemon"),
        "csgbq 123: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 123: the cluster mirrors every packet twice", "a"), "round 123: the cluster mirrors every packet twice"),
    (("round 123: the cluster mirrors every packet twice", "zz"), "qntmc 123: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 123: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 123: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 123: the cluster mirrors every packet twice", "keyboard"),
        "bssor 123: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 123: the cluster mirrors every packet twice", "AA"), "round 123: the cluster mirrors every packet twice"),
    (
        ("round 123: ranking uses tokens learned from the corpus", "key"),
        "bssxh 123: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 123: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", "a"),
        "round 123: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 123: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 123: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 123: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", "AA"),
        "round 123: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 123: a long session ends when the candle dies", "key"),
        "bssxh 123: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 123: a long session ends when the candle dies", "lemon"),
        "csgbq 123: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 123: a long session ends when the candle dies", "a"),
        "round 123: a long session ends when the candle dies",
    ),
    (
        ("round 123: a long session ends when the candle dies", "zz"),
        "qntmc 123: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 123: a long session ends when the candle dies", "AgentU"),
        "ruyaw 123: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 123: a long session ends when the candle dies", "keyboard"),
        "bssor 123: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 123: a long session ends when the candle dies", "AA"),
        "round 123: a long session ends when the candle dies",
    ),
    (("round 123: encode the prompt then map the result", "key"), "bssxh 123: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 123: encode the prompt then map the result", "lemon"), "csgbq 123: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 123: encode the prompt then map the result", "a"), "round 123: encode the prompt then map the result"),
    (("round 123: encode the prompt then map the result", "zz"), "qntmc 123: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 123: encode the prompt then map the result", "AgentU"),
        "ruyaw 123: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 123: encode the prompt then map the result", "keyboard"),
        "bssor 123: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 123: encode the prompt then map the result", "AA"), "round 123: encode the prompt then map the result"),
    (("round 123: the kernel wakes the worker at dawn", "key"), "bssxh 123: rri iovlop ukocc xfo ambocb er neux"),
    (("round 123: the kernel wakes the worker at dawn", "lemon"), "csgbq 123: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 123: the kernel wakes the worker at dawn", "a"), "round 123: the kernel wakes the worker at dawn"),
    (("round 123: the kernel wakes the worker at dawn", "zz"), "qntmc 123: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 123: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 123: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 123: the kernel wakes the worker at dawn", "keyboard"), "bssor 123: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 123: the kernel wakes the worker at dawn", "AA"), "round 123: the kernel wakes the worker at dawn"),
    (("round 123: service latency drops after the patch", "key"), "bssxh 123: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 123: service latency drops after the patch", "lemon"), "csgbq 123: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 123: service latency drops after the patch", "a"), "round 123: service latency drops after the patch"),
    (("round 123: service latency drops after the patch", "zz"), "qntmc 123: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 123: service latency drops after the patch", "AgentU"),
        "ruyaw 123: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 123: service latency drops after the patch", "keyboard"),
        "bssor 123: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 123: service latency drops after the patch", "AA"), "round 123: service latency drops after the patch"),
    (
        ("round 123: the library caches every vector it sees", "key"),
        "bssxh 123: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 123: the library caches every vector it sees", "lemon"),
        "csgbq 123: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 123: the library caches every vector it sees", "a"), "round 123: the library caches every vector it sees"),
    (
        ("round 123: the library caches every vector it sees", "zz"),
        "qntmc 123: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 123: the library caches every vector it sees", "AgentU"),
        "ruyaw 123: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 123: the library caches every vector it sees", "keyboard"),
        "bssor 123: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 123: the library caches every vector it sees", "AA"),
        "round 123: the library caches every vector it sees",
    ),
    (("round 123: agents argue then the debate resolves", "key"), "bssxh 123: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 123: agents argue then the debate resolves", "lemon"), "csgbq 123: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 123: agents argue then the debate resolves", "a"), "round 123: agents argue then the debate resolves"),
    (("round 123: agents argue then the debate resolves", "zz"), "qntmc 123: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 123: agents argue then the debate resolves", "AgentU"),
        "ruyaw 123: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 123: agents argue then the debate resolves", "keyboard"),
        "bssor 123: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 123: agents argue then the debate resolves", "AA"), "round 123: agents argue then the debate resolves"),
    (("round 123: the filter keeps only strong matches", "key"), "bssxh 123: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 123: the filter keeps only strong matches", "lemon"), "csgbq 123: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 123: the filter keeps only strong matches", "a"), "round 123: the filter keeps only strong matches"),
    (("round 123: the filter keeps only strong matches", "zz"), "qntmc 123: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 123: the filter keeps only strong matches", "AgentU"), "ruyaw 123: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 123: the filter keeps only strong matches", "keyboard"),
        "bssor 123: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 123: the filter keeps only strong matches", "AA"), "round 123: the filter keeps only strong matches"),
    (("round 123: the model answers with a short reply", "key"), "bssxh 123: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 123: the model answers with a short reply", "lemon"), "csgbq 123: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 123: the model answers with a short reply", "a"), "round 123: the model answers with a short reply"),
    (("round 123: the model answers with a short reply", "zz"), "qntmc 123: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 123: the model answers with a short reply", "AgentU"), "ruyaw 123: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 123: the model answers with a short reply", "keyboard"),
        "bssor 123: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 123: the model answers with a short reply", "AA"), "round 123: the model answers with a short reply"),
    (
        ("round 123: the recorder stores the reasoning trace", "key"),
        "bssxh 123: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 123: the recorder stores the reasoning trace", "lemon"),
        "csgbq 123: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 123: the recorder stores the reasoning trace", "a"), "round 123: the recorder stores the reasoning trace"),
    (
        ("round 123: the recorder stores the reasoning trace", "zz"),
        "qntmc 123: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 123: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 123: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 123: the recorder stores the reasoning trace", "keyboard"),
        "bssor 123: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 123: the recorder stores the reasoning trace", "AA"),
        "round 123: the recorder stores the reasoning trace",
    ),
    (("round 123: the angel watches the processor run", "key"), "bssxh 123: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 123: the angel watches the processor run", "lemon"), "csgbq 123: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 123: the angel watches the processor run", "a"), "round 123: the angel watches the processor run"),
    (("round 123: the angel watches the processor run", "zz"), "qntmc 123: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 123: the angel watches the processor run", "AgentU"), "ruyaw 123: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 123: the angel watches the processor run", "keyboard"), "bssor 123: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 123: the angel watches the processor run", "AA"), "round 123: the angel watches the processor run"),
    (("round 123: angle of the vector decides the match", "key"), "bssxh 123: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 123: angle of the vector decides the match", "lemon"), "csgbq 123: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 123: angle of the vector decides the match", "a"), "round 123: angle of the vector decides the match"),
    (("round 123: angle of the vector decides the match", "zz"), "qntmc 123: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 123: angle of the vector decides the match", "AgentU"),
        "ruyaw 123: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 123: angle of the vector decides the match", "keyboard"),
        "bssor 123: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 123: angle of the vector decides the match", "AA"), "round 123: angle of the vector decides the match"),
    (
        ("round 123: the candle burns twice as long at night", "key"),
        "bssxh 123: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 123: the candle burns twice as long at night", "lemon"),
        "csgbq 123: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 123: the candle burns twice as long at night", "a"), "round 123: the candle burns twice as long at night"),
    (
        ("round 123: the candle burns twice as long at night", "zz"),
        "qntmc 123: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 123: the candle burns twice as long at night", "AgentU"),
        "ruyaw 123: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 123: the candle burns twice as long at night", "keyboard"),
        "bssor 123: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 123: the candle burns twice as long at night", "AA"),
        "round 123: the candle burns twice as long at night",
    ),
    (("round 123: a mirror of the universe in one line", "key"), "bssxh 123: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 123: a mirror of the universe in one line", "lemon"), "csgbq 123: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 123: a mirror of the universe in one line", "a"), "round 123: a mirror of the universe in one line"),
    (("round 123: a mirror of the universe in one line", "zz"), "qntmc 123: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 123: a mirror of the universe in one line", "AgentU"), "ruyaw 123: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 123: a mirror of the universe in one line", "keyboard"),
        "bssor 123: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 123: a mirror of the universe in one line", "AA"), "round 123: a mirror of the universe in one line"),
    (("round 123: the queue drains before the storm", "key"), "bssxh 123: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 123: the queue drains before the storm", "lemon"), "csgbq 123: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 123: the queue drains before the storm", "a"), "round 123: the queue drains before the storm"),
    (("round 123: the queue drains before the storm", "zz"), "qntmc 123: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 123: the queue drains before the storm", "AgentU"), "ruyaw 123: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 123: the queue drains before the storm", "keyboard"), "bssor 123: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 123: the queue drains before the storm", "AA"), "round 123: the queue drains before the storm"),
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
