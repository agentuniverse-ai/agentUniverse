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
    (("kitten135", "key"), "umrdil135"),
    (("kitten135", "lemon"), "vmfhry135"),
    (("kitten135", "a"), "kitten135"),
    (("kitten135", "zz"), "jhssdm135"),
    (("kitten135", "AgentU"), "koxgxh135"),
    (("kitten135", "keyboard"), "umrusn135"),
    (("kitten135", "AA"), "kitten135"),
    (("sitting135", "key"), "cmrdmlq135"),
    (("sitting135", "lemon"), "dmfhvyk135"),
    (("sitting135", "a"), "sitting135"),
    (("sitting135", "zz"), "rhsshmf135"),
    (("sitting135", "AgentU"), "soxgbhg135"),
    (("sitting135", "keyboard"), "cmruwnx135"),
    (("sitting135", "AA"), "sitting135"),
    (("agent135", "key"), "kkcxx135"),
    (("agent135", "lemon"), "lkqbg135"),
    (("agent135", "a"), "agent135"),
    (("agent135", "zz"), "zfdms135"),
    (("agent135", "AgentU"), "amiam135"),
    (("agent135", "keyboard"), "kkcoh135"),
    (("agent135", "AA"), "agent135"),
    (("angle135", "key"), "krevi135"),
    (("angle135", "lemon"), "lrszr135"),
    (("angle135", "a"), "angle135"),
    (("angle135", "zz"), "zmfkd135"),
    (("angle135", "AgentU"), "atkyx135"),
    (("angle135", "keyboard"), "krems135"),
    (("angle135", "AA"), "angle135"),
    (("universe135", "key"), "ergfipci135"),
    (("universe135", "lemon"), "frujrcwq135"),
    (("universe135", "a"), "universe135"),
    (("universe135", "zz"), "tmhudqrd135"),
    (("universe135", "AgentU"), "utmixlsk135"),
    (("universe135", "keyboard"), "ergwsrjh135"),
    (("universe135", "AA"), "universe135"),
    (("memory135", "key"), "wikyvw135"),
    (("memory135", "lemon"), "xiycej135"),
    (("memory135", "a"), "memory135"),
    (("memory135", "zz"), "ldlnqx135"),
    (("memory135", "AgentU"), "mkqbks135"),
    (("memory135", "keyboard"), "wikpfy135"),
    (("memory135", "AA"), "memory135"),
    (("stream135", "key"), "cxpoek135"),
    (("stream135", "lemon"), "dxdsnx135"),
    (("stream135", "a"), "stream135"),
    (("stream135", "zz"), "rsqdzl135"),
    (("stream135", "AgentU"), "szvrtg135"),
    (("stream135", "keyboard"), "cxpfom135"),
    (("stream135", "AA"), "stream135"),
    (("context135", "key"), "msldivd135"),
    (("context135", "lemon"), "nszhrix135"),
    (("context135", "a"), "context135"),
    (("context135", "zz"), "bnmsdws135"),
    (("context135", "AgentU"), "curgxrt135"),
    (("context135", "keyboard"), "mslusxk135"),
    (("context135", "AA"), "context135"),
    (("knowledge135", "key"), "urmgpcnkc135"),
    (("knowledge135", "lemon"), "vrakyphss135"),
    (("knowledge135", "a"), "knowledge135"),
    (("knowledge135", "zz"), "jmnvkdcfd135"),
    (("knowledge135", "AgentU"), "ktsjeydmi135"),
    (("knowledge135", "keyboard"), "urmxzeujo135"),
    (("knowledge135", "AA"), "knowledge135"),
    (("vector135", "key"), "fiadsp135"),
    (("vector135", "lemon"), "giohbc135"),
    (("vector135", "a"), "vector135"),
    (("vector135", "zz"), "udbsnq135"),
    (("vector135", "AgentU"), "vkgghl135"),
    (("vector135", "keyboard"), "fiaucr135"),
    (("vector135", "AA"), "vector135"),
    (("processor135", "key"), "zvmmiqcsp135"),
    (("processor135", "lemon"), "avaqrdwaf135"),
    (("processor135", "a"), "processor135"),
    (("processor135", "zz"), "oqnbdrrnq135"),
    (("processor135", "AgentU"), "pxspxmsuv135"),
    (("processor135", "keyboard"), "zvmdssjrb135"),
    (("processor135", "AA"), "processor135"),
    (("reasoning135", "key"), "biycslsre135"),
    (("reasoning135", "lemon"), "cimgbymzu135"),
    (("reasoning135", "a"), "reasoning135"),
    (("reasoning135", "zz"), "qdzrnmhmf135"),
    (("reasoning135", "AgentU"), "rkefhhitk135"),
    (("reasoning135", "keyboard"), "biytcnzqq135"),
    (("reasoning135", "AA"), "reasoning135"),
    (("machine135", "key"), "wearmlo135"),
    (("machine135", "lemon"), "xeovvyi135"),
    (("machine135", "a"), "machine135"),
    (("machine135", "zz"), "lzbghmd135"),
    (("machine135", "AgentU"), "mggubhe135"),
    (("machine135", "keyboard"), "weaiwnv135"),
    (("machine135", "AA"), "machine135"),
    (("learning135", "key"), "viybrgxk135"),
    (("learning135", "lemon"), "wimfatrs135"),
    (("learning135", "a"), "learning135"),
    (("learning135", "zz"), "kdzqmhmf135"),
    (("learning135", "AgentU"), "lkeegcnm135"),
    (("learning135", "keyboard"), "viysbiej135"),
    (("learning135", "AA"), "learning135"),
    (("model135", "key"), "wsbop135"),
    (("model135", "lemon"), "xspsy135"),
    (("model135", "a"), "model135"),
    (("model135", "zz"), "lncdk135"),
    (("model135", "AgentU"), "muhre135"),
    (("model135", "keyboard"), "wsbfz135"),
    (("model135", "AA"), "model135"),
    (("token135", "key"), "dsior135"),
    (("token135", "lemon"), "eswsa135"),
    (("token135", "a"), "token135"),
    (("token135", "zz"), "snjdm135"),
    (("token135", "AgentU"), "tuorg135"),
    (("token135", "keyboard"), "dsifb135"),
    (("token135", "AA"), "token135"),
    (("prompt135", "key"), "zvmwtr135"),
    (("prompt135", "lemon"), "avaace135"),
    (("prompt135", "a"), "prompt135"),
    (("prompt135", "zz"), "oqnlos135"),
    (("prompt135", "AgentU"), "pxszin135"),
    (("prompt135", "keyboard"), "zvmndt135"),
    (("prompt135", "AA"), "prompt135"),
    (("session135", "key"), "ciqcmmx135"),
    (("session135", "lemon"), "diegvzr135"),
    (("session135", "a"), "session135"),
    (("session135", "zz"), "rdrrhnm135"),
    (("session135", "AgentU"), "skwfbin135"),
    (("session135", "keyboard"), "ciqtwoe135"),
    (("session135", "AA"), "session135"),
    (("library135", "key"), "vmzbepi135"),
    (("library135", "lemon"), "wmnfncc135"),
    (("library135", "a"), "library135"),
    (("library135", "zz"), "khaqzqx135"),
    (("library135", "AgentU"), "lofetly135"),
    (("library135", "keyboard"), "vmzsorp135"),
    (("library135", "AA"), "library135"),
    (("service135", "key"), "cipfmao135"),
    (("service135", "lemon"), "didjvni135"),
    (("service135", "a"), "service135"),
    (("service135", "zz"), "rdquhbd135"),
    (("service135", "AgentU"), "skvibwe135"),
    (("service135", "keyboard"), "cipwwcv135"),
    (("service135", "AA"), "service135"),
    (("gateway135", "key"), "qeroayi135"),
    (("gateway135", "lemon"), "refsjlc135"),
    (("gateway135", "a"), "gateway135"),
    (("gateway135", "zz"), "fzsdvzx135"),
    (("gateway135", "AgentU"), "ggxrpuy135"),
    (("gateway135", "keyboard"), "qerfkap135"),
    (("gateway135", "AA"), "gateway135"),
    (("storage135", "key"), "cxmbeeo135"),
    (("storage135", "lemon"), "dxafnri135"),
    (("storage135", "a"), "storage135"),
    (("storage135", "zz"), "rsnqzfd135"),
    (("storage135", "AgentU"), "szsetae135"),
    (("storage135", "keyboard"), "cxmsogv135"),
    (("storage135", "AA"), "storage135"),
    (("network135", "key"), "xirgspu135"),
    (("network135", "lemon"), "yifkbco135"),
    (("network135", "a"), "network135"),
    (("network135", "zz"), "mdsvnqj135"),
    (("network135", "AgentU"), "nkxjhlk135"),
    (("network135", "keyboard"), "xirxcrb135"),
    (("network135", "AA"), "network135"),
    (("latency135", "key"), "verorai135"),
    (("latency135", "lemon"), "wefsanc135"),
    (("latency135", "a"), "latency135"),
    (("latency135", "zz"), "kzsdmbx135"),
    (("latency135", "AgentU"), "lgxrgwy135"),
    (("latency135", "keyboard"), "verfbcp135"),
    (("latency135", "AA"), "latency135"),
    (("buffer135", "key"), "lydpip135"),
    (("buffer135", "lemon"), "myrtrc135"),
    (("buffer135", "a"), "buffer135"),
    (("buffer135", "zz"), "ateedq135"),
    (("buffer135", "AgentU"), "bajsxl135"),
    (("buffer135", "keyboard"), "lydgsr135"),
    (("buffer135", "AA"), "buffer135"),
    (("queue135", "key"), "aycei135"),
    (("queue135", "lemon"), "byqir135"),
    (("queue135", "a"), "queue135"),
    (("queue135", "zz"), "ptdtd135"),
    (("queue135", "AgentU"), "qaihx135"),
    (("queue135", "keyboard"), "aycvs135"),
    (("queue135", "AA"), "queue135"),
    (("worker135", "key"), "gspuip135"),
    (("worker135", "lemon"), "hsdyrc135"),
    (("worker135", "a"), "worker135"),
    (("worker135", "zz"), "vnqjdq135"),
    (("worker135", "AgentU"), "wuvxxl135"),
    (("worker135", "keyboard"), "gsplsr135"),
    (("worker135", "AA"), "worker135"),
    (("kernel135", "key"), "uipxij135"),
    (("kernel135", "lemon"), "vidbrw135"),
    (("kernel135", "a"), "kernel135"),
    (("kernel135", "zz"), "jdqmdk135"),
    (("kernel135", "AgentU"), "kkvaxf135"),
    (("kernel135", "keyboard"), "uiposl135"),
    (("kernel135", "AA"), "kernel135"),
    (("signal135", "key"), "cmexej135"),
    (("signal135", "lemon"), "dmsbnw135"),
    (("signal135", "a"), "signal135"),
    (("signal135", "zz"), "rhfmzk135"),
    (("signal135", "AgentU"), "sokatf135"),
    (("signal135", "keyboard"), "cmeool135"),
    (("signal135", "AA"), "signal135"),
    (("packet135", "key"), "zeauir135"),
    (("packet135", "lemon"), "aeoyre135"),
    (("packet135", "a"), "packet135"),
    (("packet135", "zz"), "ozbjds135"),
    (("packet135", "AgentU"), "pggxxn135"),
    (("packet135", "keyboard"), "zealst135"),
    (("packet135", "AA"), "packet135"),
    (("router135", "key"), "bssdip135"),
    (("router135", "lemon"), "csghrc135"),
    (("router135", "a"), "router135"),
    (("router135", "zz"), "qntsdq135"),
    (("router135", "AgentU"), "ruygxl135"),
    (("router135", "keyboard"), "bssusr135"),
    (("router135", "AA"), "router135"),
    (("cluster135", "key"), "mpscxcb135"),
    (("cluster135", "lemon"), "npgggpv135"),
    (("cluster135", "a"), "cluster135"),
    (("cluster135", "zz"), "bktrsdq135"),
    (("cluster135", "AgentU"), "cryfmyr135"),
    (("cluster135", "keyboard"), "mpsthei135"),
    (("cluster135", "AA"), "cluster135"),
    (("mirror135", "key"), "wmpbsp135"),
    (("mirror135", "lemon"), "xmdfbc135"),
    (("mirror135", "a"), "mirror135"),
    (("mirror135", "zz"), "lhqqnq135"),
    (("mirror135", "AgentU"), "movehl135"),
    (("mirror135", "keyboard"), "wmpscr135"),
    (("mirror135", "AA"), "mirror135"),
    (("filter135", "key"), "pmjdip135"),
    (("filter135", "lemon"), "qmxhrc135"),
    (("filter135", "a"), "filter135"),
    (("filter135", "zz"), "ehksdq135"),
    (("filter135", "AgentU"), "fopgxl135"),
    (("filter135", "keyboard"), "pmjusr135"),
    (("filter135", "AA"), "filter135"),
    (("ranking135", "key"), "belumlq135"),
    (("ranking135", "lemon"), "cezyvyk135"),
    (("ranking135", "a"), "ranking135"),
    (("ranking135", "zz"), "qzmjhmf135"),
    (("ranking135", "AgentU"), "rgrxbhg135"),
    (("ranking135", "keyboard"), "bellwnx135"),
    (("ranking135", "AA"), "ranking135"),
    (("encoding135", "key"), "orayhgxk135"),
    (("encoding135", "lemon"), "procqtrs135"),
    (("encoding135", "a"), "encoding135"),
    (("encoding135", "zz"), "dmbnchmf135"),
    (("encoding135", "AgentU"), "etgbwcnm135"),
    (("encoding135", "keyboard"), "orapriej135"),
    (("encoding135", "AA"), "encoding135"),
    (("mapping135", "key"), "wenzmlq135"),
    (("mapping135", "lemon"), "xebdvyk135"),
    (("mapping135", "a"), "mapping135"),
    (("mapping135", "zz"), "lzoohmf135"),
    (("mapping135", "AgentU"), "mgtcbhg135"),
    (("mapping135", "keyboard"), "wenqwnx135"),
    (("mapping135", "AA"), "mapping135"),
    (("record135", "key"), "biayvb135"),
    (("record135", "lemon"), "cioceo135"),
    (("record135", "a"), "record135"),
    (("record135", "zz"), "qdbnqc135"),
    (("record135", "AgentU"), "rkgbkx135"),
    (("record135", "keyboard"), "biapfd135"),
    (("record135", "AA"), "record135"),
    (("candle135", "key"), "melnpc135"),
    (("candle135", "lemon"), "nezryp135"),
    (("candle135", "a"), "candle135"),
    (("candle135", "zz"), "bzmckd135"),
    (("candle135", "AgentU"), "cgrqey135"),
    (("candle135", "keyboard"), "meleze135"),
    (("candle135", "AA"), "candle135"),
    (("thread135", "key"), "dlpoeb135"),
    (("thread135", "lemon"), "eldsno135"),
    (("thread135", "a"), "thread135"),
    (("thread135", "zz"), "sgqdzc135"),
    (("thread135", "AgentU"), "tnvrtx135"),
    (("thread135", "keyboard"), "dlpfod135"),
    (("thread135", "AA"), "thread135"),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 135: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 135: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "a"),
        "round 135: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 135: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 135: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 135: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", "AA"),
        "round 135: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "key"),
        "bssxh 135: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 135: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "a"),
        "round 135: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 135: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 135: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 135: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", "AA"),
        "round 135: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 135: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 135: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "a"),
        "round 135: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 135: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 135: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 135: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", "AA"),
        "round 135: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 135: the processor reads the record then stops", "key"),
        "bssxh 135: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 135: the processor reads the record then stops", "lemon"),
        "csgbq 135: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 135: the processor reads the record then stops", "a"),
        "round 135: the processor reads the record then stops",
    ),
    (
        ("round 135: the processor reads the record then stops", "zz"),
        "qntmc 135: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 135: the processor reads the record then stops", "AgentU"),
        "ruyaw 135: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 135: the processor reads the record then stops", "keyboard"),
        "bssor 135: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 135: the processor reads the record then stops", "AA"),
        "round 135: the processor reads the record then stops",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "key"),
        "bssxh 135: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "lemon"),
        "csgbq 135: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "a"),
        "round 135: a worker pulls the next task from the queue",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "zz"),
        "qntmc 135: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 135: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "keyboard"),
        "bssor 135: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 135: a worker pulls the next task from the queue", "AA"),
        "round 135: a worker pulls the next task from the queue",
    ),
    (
        ("round 135: signals travel through the network layer", "key"),
        "bssxh 135: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 135: signals travel through the network layer", "lemon"),
        "csgbq 135: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 135: signals travel through the network layer", "a"),
        "round 135: signals travel through the network layer",
    ),
    (
        ("round 135: signals travel through the network layer", "zz"),
        "qntmc 135: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 135: signals travel through the network layer", "AgentU"),
        "ruyaw 135: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 135: signals travel through the network layer", "keyboard"),
        "bssor 135: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 135: signals travel through the network layer", "AA"),
        "round 135: signals travel through the network layer",
    ),
    (
        ("round 135: the gateway routes each request by policy", "key"),
        "bssxh 135: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 135: the gateway routes each request by policy", "lemon"),
        "csgbq 135: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 135: the gateway routes each request by policy", "a"),
        "round 135: the gateway routes each request by policy",
    ),
    (
        ("round 135: the gateway routes each request by policy", "zz"),
        "qntmc 135: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 135: the gateway routes each request by policy", "AgentU"),
        "ruyaw 135: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 135: the gateway routes each request by policy", "keyboard"),
        "bssor 135: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 135: the gateway routes each request by policy", "AA"),
        "round 135: the gateway routes each request by policy",
    ),
    (("round 135: memory grows until the buffer is full", "key"), "bssxh 135: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 135: memory grows until the buffer is full", "lemon"), "csgbq 135: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 135: memory grows until the buffer is full", "a"), "round 135: memory grows until the buffer is full"),
    (("round 135: memory grows until the buffer is full", "zz"), "qntmc 135: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 135: memory grows until the buffer is full", "AgentU"),
        "ruyaw 135: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 135: memory grows until the buffer is full", "keyboard"),
        "bssor 135: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 135: memory grows until the buffer is full", "AA"), "round 135: memory grows until the buffer is full"),
    (("round 135: the cluster mirrors every packet twice", "key"), "bssxh 135: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 135: the cluster mirrors every packet twice", "lemon"),
        "csgbq 135: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 135: the cluster mirrors every packet twice", "a"), "round 135: the cluster mirrors every packet twice"),
    (("round 135: the cluster mirrors every packet twice", "zz"), "qntmc 135: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 135: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 135: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 135: the cluster mirrors every packet twice", "keyboard"),
        "bssor 135: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 135: the cluster mirrors every packet twice", "AA"), "round 135: the cluster mirrors every packet twice"),
    (
        ("round 135: ranking uses tokens learned from the corpus", "key"),
        "bssxh 135: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 135: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", "a"),
        "round 135: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 135: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 135: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 135: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", "AA"),
        "round 135: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 135: a long session ends when the candle dies", "key"),
        "bssxh 135: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 135: a long session ends when the candle dies", "lemon"),
        "csgbq 135: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 135: a long session ends when the candle dies", "a"),
        "round 135: a long session ends when the candle dies",
    ),
    (
        ("round 135: a long session ends when the candle dies", "zz"),
        "qntmc 135: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 135: a long session ends when the candle dies", "AgentU"),
        "ruyaw 135: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 135: a long session ends when the candle dies", "keyboard"),
        "bssor 135: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 135: a long session ends when the candle dies", "AA"),
        "round 135: a long session ends when the candle dies",
    ),
    (("round 135: encode the prompt then map the result", "key"), "bssxh 135: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 135: encode the prompt then map the result", "lemon"), "csgbq 135: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 135: encode the prompt then map the result", "a"), "round 135: encode the prompt then map the result"),
    (("round 135: encode the prompt then map the result", "zz"), "qntmc 135: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 135: encode the prompt then map the result", "AgentU"),
        "ruyaw 135: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 135: encode the prompt then map the result", "keyboard"),
        "bssor 135: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 135: encode the prompt then map the result", "AA"), "round 135: encode the prompt then map the result"),
    (("round 135: the kernel wakes the worker at dawn", "key"), "bssxh 135: rri iovlop ukocc xfo ambocb er neux"),
    (("round 135: the kernel wakes the worker at dawn", "lemon"), "csgbq 135: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 135: the kernel wakes the worker at dawn", "a"), "round 135: the kernel wakes the worker at dawn"),
    (("round 135: the kernel wakes the worker at dawn", "zz"), "qntmc 135: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 135: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 135: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 135: the kernel wakes the worker at dawn", "keyboard"), "bssor 135: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 135: the kernel wakes the worker at dawn", "AA"), "round 135: the kernel wakes the worker at dawn"),
    (("round 135: service latency drops after the patch", "key"), "bssxh 135: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 135: service latency drops after the patch", "lemon"), "csgbq 135: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 135: service latency drops after the patch", "a"), "round 135: service latency drops after the patch"),
    (("round 135: service latency drops after the patch", "zz"), "qntmc 135: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 135: service latency drops after the patch", "AgentU"),
        "ruyaw 135: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 135: service latency drops after the patch", "keyboard"),
        "bssor 135: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 135: service latency drops after the patch", "AA"), "round 135: service latency drops after the patch"),
    (
        ("round 135: the library caches every vector it sees", "key"),
        "bssxh 135: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 135: the library caches every vector it sees", "lemon"),
        "csgbq 135: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 135: the library caches every vector it sees", "a"), "round 135: the library caches every vector it sees"),
    (
        ("round 135: the library caches every vector it sees", "zz"),
        "qntmc 135: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 135: the library caches every vector it sees", "AgentU"),
        "ruyaw 135: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 135: the library caches every vector it sees", "keyboard"),
        "bssor 135: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 135: the library caches every vector it sees", "AA"),
        "round 135: the library caches every vector it sees",
    ),
    (("round 135: agents argue then the debate resolves", "key"), "bssxh 135: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 135: agents argue then the debate resolves", "lemon"), "csgbq 135: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 135: agents argue then the debate resolves", "a"), "round 135: agents argue then the debate resolves"),
    (("round 135: agents argue then the debate resolves", "zz"), "qntmc 135: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 135: agents argue then the debate resolves", "AgentU"),
        "ruyaw 135: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 135: agents argue then the debate resolves", "keyboard"),
        "bssor 135: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 135: agents argue then the debate resolves", "AA"), "round 135: agents argue then the debate resolves"),
    (("round 135: the filter keeps only strong matches", "key"), "bssxh 135: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 135: the filter keeps only strong matches", "lemon"), "csgbq 135: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 135: the filter keeps only strong matches", "a"), "round 135: the filter keeps only strong matches"),
    (("round 135: the filter keeps only strong matches", "zz"), "qntmc 135: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 135: the filter keeps only strong matches", "AgentU"), "ruyaw 135: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 135: the filter keeps only strong matches", "keyboard"),
        "bssor 135: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 135: the filter keeps only strong matches", "AA"), "round 135: the filter keeps only strong matches"),
    (("round 135: the model answers with a short reply", "key"), "bssxh 135: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 135: the model answers with a short reply", "lemon"), "csgbq 135: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 135: the model answers with a short reply", "a"), "round 135: the model answers with a short reply"),
    (("round 135: the model answers with a short reply", "zz"), "qntmc 135: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 135: the model answers with a short reply", "AgentU"), "ruyaw 135: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 135: the model answers with a short reply", "keyboard"),
        "bssor 135: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 135: the model answers with a short reply", "AA"), "round 135: the model answers with a short reply"),
    (
        ("round 135: the recorder stores the reasoning trace", "key"),
        "bssxh 135: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 135: the recorder stores the reasoning trace", "lemon"),
        "csgbq 135: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 135: the recorder stores the reasoning trace", "a"), "round 135: the recorder stores the reasoning trace"),
    (
        ("round 135: the recorder stores the reasoning trace", "zz"),
        "qntmc 135: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 135: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 135: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 135: the recorder stores the reasoning trace", "keyboard"),
        "bssor 135: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 135: the recorder stores the reasoning trace", "AA"),
        "round 135: the recorder stores the reasoning trace",
    ),
    (("round 135: the angel watches the processor run", "key"), "bssxh 135: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 135: the angel watches the processor run", "lemon"), "csgbq 135: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 135: the angel watches the processor run", "a"), "round 135: the angel watches the processor run"),
    (("round 135: the angel watches the processor run", "zz"), "qntmc 135: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 135: the angel watches the processor run", "AgentU"), "ruyaw 135: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 135: the angel watches the processor run", "keyboard"), "bssor 135: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 135: the angel watches the processor run", "AA"), "round 135: the angel watches the processor run"),
    (("round 135: angle of the vector decides the match", "key"), "bssxh 135: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 135: angle of the vector decides the match", "lemon"), "csgbq 135: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 135: angle of the vector decides the match", "a"), "round 135: angle of the vector decides the match"),
    (("round 135: angle of the vector decides the match", "zz"), "qntmc 135: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 135: angle of the vector decides the match", "AgentU"),
        "ruyaw 135: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 135: angle of the vector decides the match", "keyboard"),
        "bssor 135: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 135: angle of the vector decides the match", "AA"), "round 135: angle of the vector decides the match"),
    (
        ("round 135: the candle burns twice as long at night", "key"),
        "bssxh 135: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 135: the candle burns twice as long at night", "lemon"),
        "csgbq 135: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 135: the candle burns twice as long at night", "a"), "round 135: the candle burns twice as long at night"),
    (
        ("round 135: the candle burns twice as long at night", "zz"),
        "qntmc 135: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 135: the candle burns twice as long at night", "AgentU"),
        "ruyaw 135: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 135: the candle burns twice as long at night", "keyboard"),
        "bssor 135: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 135: the candle burns twice as long at night", "AA"),
        "round 135: the candle burns twice as long at night",
    ),
    (("round 135: a mirror of the universe in one line", "key"), "bssxh 135: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 135: a mirror of the universe in one line", "lemon"), "csgbq 135: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 135: a mirror of the universe in one line", "a"), "round 135: a mirror of the universe in one line"),
    (("round 135: a mirror of the universe in one line", "zz"), "qntmc 135: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 135: a mirror of the universe in one line", "AgentU"), "ruyaw 135: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 135: a mirror of the universe in one line", "keyboard"),
        "bssor 135: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 135: a mirror of the universe in one line", "AA"), "round 135: a mirror of the universe in one line"),
    (("round 135: the queue drains before the storm", "key"), "bssxh 135: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 135: the queue drains before the storm", "lemon"), "csgbq 135: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 135: the queue drains before the storm", "a"), "round 135: the queue drains before the storm"),
    (("round 135: the queue drains before the storm", "zz"), "qntmc 135: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 135: the queue drains before the storm", "AgentU"), "ruyaw 135: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 135: the queue drains before the storm", "keyboard"), "bssor 135: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 135: the queue drains before the storm", "AA"), "round 135: the queue drains before the storm"),
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
