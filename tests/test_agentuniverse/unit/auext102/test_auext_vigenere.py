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
    (("kitten102", "key"), "umrdil102"),
    (("kitten102", "lemon"), "vmfhry102"),
    (("kitten102", "a"), "kitten102"),
    (("kitten102", "zz"), "jhssdm102"),
    (("kitten102", "AgentU"), "koxgxh102"),
    (("kitten102", "keyboard"), "umrusn102"),
    (("kitten102", "AA"), "kitten102"),
    (("sitting102", "key"), "cmrdmlq102"),
    (("sitting102", "lemon"), "dmfhvyk102"),
    (("sitting102", "a"), "sitting102"),
    (("sitting102", "zz"), "rhsshmf102"),
    (("sitting102", "AgentU"), "soxgbhg102"),
    (("sitting102", "keyboard"), "cmruwnx102"),
    (("sitting102", "AA"), "sitting102"),
    (("agent102", "key"), "kkcxx102"),
    (("agent102", "lemon"), "lkqbg102"),
    (("agent102", "a"), "agent102"),
    (("agent102", "zz"), "zfdms102"),
    (("agent102", "AgentU"), "amiam102"),
    (("agent102", "keyboard"), "kkcoh102"),
    (("agent102", "AA"), "agent102"),
    (("angle102", "key"), "krevi102"),
    (("angle102", "lemon"), "lrszr102"),
    (("angle102", "a"), "angle102"),
    (("angle102", "zz"), "zmfkd102"),
    (("angle102", "AgentU"), "atkyx102"),
    (("angle102", "keyboard"), "krems102"),
    (("angle102", "AA"), "angle102"),
    (("universe102", "key"), "ergfipci102"),
    (("universe102", "lemon"), "frujrcwq102"),
    (("universe102", "a"), "universe102"),
    (("universe102", "zz"), "tmhudqrd102"),
    (("universe102", "AgentU"), "utmixlsk102"),
    (("universe102", "keyboard"), "ergwsrjh102"),
    (("universe102", "AA"), "universe102"),
    (("memory102", "key"), "wikyvw102"),
    (("memory102", "lemon"), "xiycej102"),
    (("memory102", "a"), "memory102"),
    (("memory102", "zz"), "ldlnqx102"),
    (("memory102", "AgentU"), "mkqbks102"),
    (("memory102", "keyboard"), "wikpfy102"),
    (("memory102", "AA"), "memory102"),
    (("stream102", "key"), "cxpoek102"),
    (("stream102", "lemon"), "dxdsnx102"),
    (("stream102", "a"), "stream102"),
    (("stream102", "zz"), "rsqdzl102"),
    (("stream102", "AgentU"), "szvrtg102"),
    (("stream102", "keyboard"), "cxpfom102"),
    (("stream102", "AA"), "stream102"),
    (("context102", "key"), "msldivd102"),
    (("context102", "lemon"), "nszhrix102"),
    (("context102", "a"), "context102"),
    (("context102", "zz"), "bnmsdws102"),
    (("context102", "AgentU"), "curgxrt102"),
    (("context102", "keyboard"), "mslusxk102"),
    (("context102", "AA"), "context102"),
    (("knowledge102", "key"), "urmgpcnkc102"),
    (("knowledge102", "lemon"), "vrakyphss102"),
    (("knowledge102", "a"), "knowledge102"),
    (("knowledge102", "zz"), "jmnvkdcfd102"),
    (("knowledge102", "AgentU"), "ktsjeydmi102"),
    (("knowledge102", "keyboard"), "urmxzeujo102"),
    (("knowledge102", "AA"), "knowledge102"),
    (("vector102", "key"), "fiadsp102"),
    (("vector102", "lemon"), "giohbc102"),
    (("vector102", "a"), "vector102"),
    (("vector102", "zz"), "udbsnq102"),
    (("vector102", "AgentU"), "vkgghl102"),
    (("vector102", "keyboard"), "fiaucr102"),
    (("vector102", "AA"), "vector102"),
    (("processor102", "key"), "zvmmiqcsp102"),
    (("processor102", "lemon"), "avaqrdwaf102"),
    (("processor102", "a"), "processor102"),
    (("processor102", "zz"), "oqnbdrrnq102"),
    (("processor102", "AgentU"), "pxspxmsuv102"),
    (("processor102", "keyboard"), "zvmdssjrb102"),
    (("processor102", "AA"), "processor102"),
    (("reasoning102", "key"), "biycslsre102"),
    (("reasoning102", "lemon"), "cimgbymzu102"),
    (("reasoning102", "a"), "reasoning102"),
    (("reasoning102", "zz"), "qdzrnmhmf102"),
    (("reasoning102", "AgentU"), "rkefhhitk102"),
    (("reasoning102", "keyboard"), "biytcnzqq102"),
    (("reasoning102", "AA"), "reasoning102"),
    (("machine102", "key"), "wearmlo102"),
    (("machine102", "lemon"), "xeovvyi102"),
    (("machine102", "a"), "machine102"),
    (("machine102", "zz"), "lzbghmd102"),
    (("machine102", "AgentU"), "mggubhe102"),
    (("machine102", "keyboard"), "weaiwnv102"),
    (("machine102", "AA"), "machine102"),
    (("learning102", "key"), "viybrgxk102"),
    (("learning102", "lemon"), "wimfatrs102"),
    (("learning102", "a"), "learning102"),
    (("learning102", "zz"), "kdzqmhmf102"),
    (("learning102", "AgentU"), "lkeegcnm102"),
    (("learning102", "keyboard"), "viysbiej102"),
    (("learning102", "AA"), "learning102"),
    (("model102", "key"), "wsbop102"),
    (("model102", "lemon"), "xspsy102"),
    (("model102", "a"), "model102"),
    (("model102", "zz"), "lncdk102"),
    (("model102", "AgentU"), "muhre102"),
    (("model102", "keyboard"), "wsbfz102"),
    (("model102", "AA"), "model102"),
    (("token102", "key"), "dsior102"),
    (("token102", "lemon"), "eswsa102"),
    (("token102", "a"), "token102"),
    (("token102", "zz"), "snjdm102"),
    (("token102", "AgentU"), "tuorg102"),
    (("token102", "keyboard"), "dsifb102"),
    (("token102", "AA"), "token102"),
    (("prompt102", "key"), "zvmwtr102"),
    (("prompt102", "lemon"), "avaace102"),
    (("prompt102", "a"), "prompt102"),
    (("prompt102", "zz"), "oqnlos102"),
    (("prompt102", "AgentU"), "pxszin102"),
    (("prompt102", "keyboard"), "zvmndt102"),
    (("prompt102", "AA"), "prompt102"),
    (("session102", "key"), "ciqcmmx102"),
    (("session102", "lemon"), "diegvzr102"),
    (("session102", "a"), "session102"),
    (("session102", "zz"), "rdrrhnm102"),
    (("session102", "AgentU"), "skwfbin102"),
    (("session102", "keyboard"), "ciqtwoe102"),
    (("session102", "AA"), "session102"),
    (("library102", "key"), "vmzbepi102"),
    (("library102", "lemon"), "wmnfncc102"),
    (("library102", "a"), "library102"),
    (("library102", "zz"), "khaqzqx102"),
    (("library102", "AgentU"), "lofetly102"),
    (("library102", "keyboard"), "vmzsorp102"),
    (("library102", "AA"), "library102"),
    (("service102", "key"), "cipfmao102"),
    (("service102", "lemon"), "didjvni102"),
    (("service102", "a"), "service102"),
    (("service102", "zz"), "rdquhbd102"),
    (("service102", "AgentU"), "skvibwe102"),
    (("service102", "keyboard"), "cipwwcv102"),
    (("service102", "AA"), "service102"),
    (("gateway102", "key"), "qeroayi102"),
    (("gateway102", "lemon"), "refsjlc102"),
    (("gateway102", "a"), "gateway102"),
    (("gateway102", "zz"), "fzsdvzx102"),
    (("gateway102", "AgentU"), "ggxrpuy102"),
    (("gateway102", "keyboard"), "qerfkap102"),
    (("gateway102", "AA"), "gateway102"),
    (("storage102", "key"), "cxmbeeo102"),
    (("storage102", "lemon"), "dxafnri102"),
    (("storage102", "a"), "storage102"),
    (("storage102", "zz"), "rsnqzfd102"),
    (("storage102", "AgentU"), "szsetae102"),
    (("storage102", "keyboard"), "cxmsogv102"),
    (("storage102", "AA"), "storage102"),
    (("network102", "key"), "xirgspu102"),
    (("network102", "lemon"), "yifkbco102"),
    (("network102", "a"), "network102"),
    (("network102", "zz"), "mdsvnqj102"),
    (("network102", "AgentU"), "nkxjhlk102"),
    (("network102", "keyboard"), "xirxcrb102"),
    (("network102", "AA"), "network102"),
    (("latency102", "key"), "verorai102"),
    (("latency102", "lemon"), "wefsanc102"),
    (("latency102", "a"), "latency102"),
    (("latency102", "zz"), "kzsdmbx102"),
    (("latency102", "AgentU"), "lgxrgwy102"),
    (("latency102", "keyboard"), "verfbcp102"),
    (("latency102", "AA"), "latency102"),
    (("buffer102", "key"), "lydpip102"),
    (("buffer102", "lemon"), "myrtrc102"),
    (("buffer102", "a"), "buffer102"),
    (("buffer102", "zz"), "ateedq102"),
    (("buffer102", "AgentU"), "bajsxl102"),
    (("buffer102", "keyboard"), "lydgsr102"),
    (("buffer102", "AA"), "buffer102"),
    (("queue102", "key"), "aycei102"),
    (("queue102", "lemon"), "byqir102"),
    (("queue102", "a"), "queue102"),
    (("queue102", "zz"), "ptdtd102"),
    (("queue102", "AgentU"), "qaihx102"),
    (("queue102", "keyboard"), "aycvs102"),
    (("queue102", "AA"), "queue102"),
    (("worker102", "key"), "gspuip102"),
    (("worker102", "lemon"), "hsdyrc102"),
    (("worker102", "a"), "worker102"),
    (("worker102", "zz"), "vnqjdq102"),
    (("worker102", "AgentU"), "wuvxxl102"),
    (("worker102", "keyboard"), "gsplsr102"),
    (("worker102", "AA"), "worker102"),
    (("kernel102", "key"), "uipxij102"),
    (("kernel102", "lemon"), "vidbrw102"),
    (("kernel102", "a"), "kernel102"),
    (("kernel102", "zz"), "jdqmdk102"),
    (("kernel102", "AgentU"), "kkvaxf102"),
    (("kernel102", "keyboard"), "uiposl102"),
    (("kernel102", "AA"), "kernel102"),
    (("signal102", "key"), "cmexej102"),
    (("signal102", "lemon"), "dmsbnw102"),
    (("signal102", "a"), "signal102"),
    (("signal102", "zz"), "rhfmzk102"),
    (("signal102", "AgentU"), "sokatf102"),
    (("signal102", "keyboard"), "cmeool102"),
    (("signal102", "AA"), "signal102"),
    (("packet102", "key"), "zeauir102"),
    (("packet102", "lemon"), "aeoyre102"),
    (("packet102", "a"), "packet102"),
    (("packet102", "zz"), "ozbjds102"),
    (("packet102", "AgentU"), "pggxxn102"),
    (("packet102", "keyboard"), "zealst102"),
    (("packet102", "AA"), "packet102"),
    (("router102", "key"), "bssdip102"),
    (("router102", "lemon"), "csghrc102"),
    (("router102", "a"), "router102"),
    (("router102", "zz"), "qntsdq102"),
    (("router102", "AgentU"), "ruygxl102"),
    (("router102", "keyboard"), "bssusr102"),
    (("router102", "AA"), "router102"),
    (("cluster102", "key"), "mpscxcb102"),
    (("cluster102", "lemon"), "npgggpv102"),
    (("cluster102", "a"), "cluster102"),
    (("cluster102", "zz"), "bktrsdq102"),
    (("cluster102", "AgentU"), "cryfmyr102"),
    (("cluster102", "keyboard"), "mpsthei102"),
    (("cluster102", "AA"), "cluster102"),
    (("mirror102", "key"), "wmpbsp102"),
    (("mirror102", "lemon"), "xmdfbc102"),
    (("mirror102", "a"), "mirror102"),
    (("mirror102", "zz"), "lhqqnq102"),
    (("mirror102", "AgentU"), "movehl102"),
    (("mirror102", "keyboard"), "wmpscr102"),
    (("mirror102", "AA"), "mirror102"),
    (("filter102", "key"), "pmjdip102"),
    (("filter102", "lemon"), "qmxhrc102"),
    (("filter102", "a"), "filter102"),
    (("filter102", "zz"), "ehksdq102"),
    (("filter102", "AgentU"), "fopgxl102"),
    (("filter102", "keyboard"), "pmjusr102"),
    (("filter102", "AA"), "filter102"),
    (("ranking102", "key"), "belumlq102"),
    (("ranking102", "lemon"), "cezyvyk102"),
    (("ranking102", "a"), "ranking102"),
    (("ranking102", "zz"), "qzmjhmf102"),
    (("ranking102", "AgentU"), "rgrxbhg102"),
    (("ranking102", "keyboard"), "bellwnx102"),
    (("ranking102", "AA"), "ranking102"),
    (("encoding102", "key"), "orayhgxk102"),
    (("encoding102", "lemon"), "procqtrs102"),
    (("encoding102", "a"), "encoding102"),
    (("encoding102", "zz"), "dmbnchmf102"),
    (("encoding102", "AgentU"), "etgbwcnm102"),
    (("encoding102", "keyboard"), "orapriej102"),
    (("encoding102", "AA"), "encoding102"),
    (("mapping102", "key"), "wenzmlq102"),
    (("mapping102", "lemon"), "xebdvyk102"),
    (("mapping102", "a"), "mapping102"),
    (("mapping102", "zz"), "lzoohmf102"),
    (("mapping102", "AgentU"), "mgtcbhg102"),
    (("mapping102", "keyboard"), "wenqwnx102"),
    (("mapping102", "AA"), "mapping102"),
    (("record102", "key"), "biayvb102"),
    (("record102", "lemon"), "cioceo102"),
    (("record102", "a"), "record102"),
    (("record102", "zz"), "qdbnqc102"),
    (("record102", "AgentU"), "rkgbkx102"),
    (("record102", "keyboard"), "biapfd102"),
    (("record102", "AA"), "record102"),
    (("candle102", "key"), "melnpc102"),
    (("candle102", "lemon"), "nezryp102"),
    (("candle102", "a"), "candle102"),
    (("candle102", "zz"), "bzmckd102"),
    (("candle102", "AgentU"), "cgrqey102"),
    (("candle102", "keyboard"), "meleze102"),
    (("candle102", "AA"), "candle102"),
    (("thread102", "key"), "dlpoeb102"),
    (("thread102", "lemon"), "eldsno102"),
    (("thread102", "a"), "thread102"),
    (("thread102", "zz"), "sgqdzc102"),
    (("thread102", "AgentU"), "tnvrtx102"),
    (("thread102", "keyboard"), "dlpfod102"),
    (("thread102", "AA"), "thread102"),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 102: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 102: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "a"),
        "round 102: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 102: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 102: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 102: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", "AA"),
        "round 102: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "key"),
        "bssxh 102: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 102: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "a"),
        "round 102: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 102: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 102: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 102: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", "AA"),
        "round 102: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 102: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 102: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "a"),
        "round 102: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 102: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 102: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 102: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", "AA"),
        "round 102: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 102: the processor reads the record then stops", "key"),
        "bssxh 102: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 102: the processor reads the record then stops", "lemon"),
        "csgbq 102: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 102: the processor reads the record then stops", "a"),
        "round 102: the processor reads the record then stops",
    ),
    (
        ("round 102: the processor reads the record then stops", "zz"),
        "qntmc 102: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 102: the processor reads the record then stops", "AgentU"),
        "ruyaw 102: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 102: the processor reads the record then stops", "keyboard"),
        "bssor 102: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 102: the processor reads the record then stops", "AA"),
        "round 102: the processor reads the record then stops",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "key"),
        "bssxh 102: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "lemon"),
        "csgbq 102: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "a"),
        "round 102: a worker pulls the next task from the queue",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "zz"),
        "qntmc 102: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 102: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "keyboard"),
        "bssor 102: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 102: a worker pulls the next task from the queue", "AA"),
        "round 102: a worker pulls the next task from the queue",
    ),
    (
        ("round 102: signals travel through the network layer", "key"),
        "bssxh 102: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 102: signals travel through the network layer", "lemon"),
        "csgbq 102: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 102: signals travel through the network layer", "a"),
        "round 102: signals travel through the network layer",
    ),
    (
        ("round 102: signals travel through the network layer", "zz"),
        "qntmc 102: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 102: signals travel through the network layer", "AgentU"),
        "ruyaw 102: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 102: signals travel through the network layer", "keyboard"),
        "bssor 102: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 102: signals travel through the network layer", "AA"),
        "round 102: signals travel through the network layer",
    ),
    (
        ("round 102: the gateway routes each request by policy", "key"),
        "bssxh 102: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 102: the gateway routes each request by policy", "lemon"),
        "csgbq 102: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 102: the gateway routes each request by policy", "a"),
        "round 102: the gateway routes each request by policy",
    ),
    (
        ("round 102: the gateway routes each request by policy", "zz"),
        "qntmc 102: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 102: the gateway routes each request by policy", "AgentU"),
        "ruyaw 102: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 102: the gateway routes each request by policy", "keyboard"),
        "bssor 102: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 102: the gateway routes each request by policy", "AA"),
        "round 102: the gateway routes each request by policy",
    ),
    (("round 102: memory grows until the buffer is full", "key"), "bssxh 102: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 102: memory grows until the buffer is full", "lemon"), "csgbq 102: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 102: memory grows until the buffer is full", "a"), "round 102: memory grows until the buffer is full"),
    (("round 102: memory grows until the buffer is full", "zz"), "qntmc 102: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 102: memory grows until the buffer is full", "AgentU"),
        "ruyaw 102: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 102: memory grows until the buffer is full", "keyboard"),
        "bssor 102: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 102: memory grows until the buffer is full", "AA"), "round 102: memory grows until the buffer is full"),
    (("round 102: the cluster mirrors every packet twice", "key"), "bssxh 102: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 102: the cluster mirrors every packet twice", "lemon"),
        "csgbq 102: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 102: the cluster mirrors every packet twice", "a"), "round 102: the cluster mirrors every packet twice"),
    (("round 102: the cluster mirrors every packet twice", "zz"), "qntmc 102: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 102: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 102: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 102: the cluster mirrors every packet twice", "keyboard"),
        "bssor 102: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 102: the cluster mirrors every packet twice", "AA"), "round 102: the cluster mirrors every packet twice"),
    (
        ("round 102: ranking uses tokens learned from the corpus", "key"),
        "bssxh 102: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 102: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", "a"),
        "round 102: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 102: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 102: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 102: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", "AA"),
        "round 102: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 102: a long session ends when the candle dies", "key"),
        "bssxh 102: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 102: a long session ends when the candle dies", "lemon"),
        "csgbq 102: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 102: a long session ends when the candle dies", "a"),
        "round 102: a long session ends when the candle dies",
    ),
    (
        ("round 102: a long session ends when the candle dies", "zz"),
        "qntmc 102: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 102: a long session ends when the candle dies", "AgentU"),
        "ruyaw 102: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 102: a long session ends when the candle dies", "keyboard"),
        "bssor 102: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 102: a long session ends when the candle dies", "AA"),
        "round 102: a long session ends when the candle dies",
    ),
    (("round 102: encode the prompt then map the result", "key"), "bssxh 102: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 102: encode the prompt then map the result", "lemon"), "csgbq 102: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 102: encode the prompt then map the result", "a"), "round 102: encode the prompt then map the result"),
    (("round 102: encode the prompt then map the result", "zz"), "qntmc 102: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 102: encode the prompt then map the result", "AgentU"),
        "ruyaw 102: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 102: encode the prompt then map the result", "keyboard"),
        "bssor 102: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 102: encode the prompt then map the result", "AA"), "round 102: encode the prompt then map the result"),
    (("round 102: the kernel wakes the worker at dawn", "key"), "bssxh 102: rri iovlop ukocc xfo ambocb er neux"),
    (("round 102: the kernel wakes the worker at dawn", "lemon"), "csgbq 102: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 102: the kernel wakes the worker at dawn", "a"), "round 102: the kernel wakes the worker at dawn"),
    (("round 102: the kernel wakes the worker at dawn", "zz"), "qntmc 102: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 102: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 102: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 102: the kernel wakes the worker at dawn", "keyboard"), "bssor 102: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 102: the kernel wakes the worker at dawn", "AA"), "round 102: the kernel wakes the worker at dawn"),
    (("round 102: service latency drops after the patch", "key"), "bssxh 102: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 102: service latency drops after the patch", "lemon"), "csgbq 102: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 102: service latency drops after the patch", "a"), "round 102: service latency drops after the patch"),
    (("round 102: service latency drops after the patch", "zz"), "qntmc 102: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 102: service latency drops after the patch", "AgentU"),
        "ruyaw 102: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 102: service latency drops after the patch", "keyboard"),
        "bssor 102: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 102: service latency drops after the patch", "AA"), "round 102: service latency drops after the patch"),
    (
        ("round 102: the library caches every vector it sees", "key"),
        "bssxh 102: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 102: the library caches every vector it sees", "lemon"),
        "csgbq 102: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 102: the library caches every vector it sees", "a"), "round 102: the library caches every vector it sees"),
    (
        ("round 102: the library caches every vector it sees", "zz"),
        "qntmc 102: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 102: the library caches every vector it sees", "AgentU"),
        "ruyaw 102: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 102: the library caches every vector it sees", "keyboard"),
        "bssor 102: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 102: the library caches every vector it sees", "AA"),
        "round 102: the library caches every vector it sees",
    ),
    (("round 102: agents argue then the debate resolves", "key"), "bssxh 102: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 102: agents argue then the debate resolves", "lemon"), "csgbq 102: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 102: agents argue then the debate resolves", "a"), "round 102: agents argue then the debate resolves"),
    (("round 102: agents argue then the debate resolves", "zz"), "qntmc 102: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 102: agents argue then the debate resolves", "AgentU"),
        "ruyaw 102: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 102: agents argue then the debate resolves", "keyboard"),
        "bssor 102: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 102: agents argue then the debate resolves", "AA"), "round 102: agents argue then the debate resolves"),
    (("round 102: the filter keeps only strong matches", "key"), "bssxh 102: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 102: the filter keeps only strong matches", "lemon"), "csgbq 102: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 102: the filter keeps only strong matches", "a"), "round 102: the filter keeps only strong matches"),
    (("round 102: the filter keeps only strong matches", "zz"), "qntmc 102: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 102: the filter keeps only strong matches", "AgentU"), "ruyaw 102: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 102: the filter keeps only strong matches", "keyboard"),
        "bssor 102: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 102: the filter keeps only strong matches", "AA"), "round 102: the filter keeps only strong matches"),
    (("round 102: the model answers with a short reply", "key"), "bssxh 102: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 102: the model answers with a short reply", "lemon"), "csgbq 102: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 102: the model answers with a short reply", "a"), "round 102: the model answers with a short reply"),
    (("round 102: the model answers with a short reply", "zz"), "qntmc 102: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 102: the model answers with a short reply", "AgentU"), "ruyaw 102: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 102: the model answers with a short reply", "keyboard"),
        "bssor 102: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 102: the model answers with a short reply", "AA"), "round 102: the model answers with a short reply"),
    (
        ("round 102: the recorder stores the reasoning trace", "key"),
        "bssxh 102: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 102: the recorder stores the reasoning trace", "lemon"),
        "csgbq 102: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 102: the recorder stores the reasoning trace", "a"), "round 102: the recorder stores the reasoning trace"),
    (
        ("round 102: the recorder stores the reasoning trace", "zz"),
        "qntmc 102: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 102: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 102: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 102: the recorder stores the reasoning trace", "keyboard"),
        "bssor 102: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 102: the recorder stores the reasoning trace", "AA"),
        "round 102: the recorder stores the reasoning trace",
    ),
    (("round 102: the angel watches the processor run", "key"), "bssxh 102: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 102: the angel watches the processor run", "lemon"), "csgbq 102: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 102: the angel watches the processor run", "a"), "round 102: the angel watches the processor run"),
    (("round 102: the angel watches the processor run", "zz"), "qntmc 102: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 102: the angel watches the processor run", "AgentU"), "ruyaw 102: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 102: the angel watches the processor run", "keyboard"), "bssor 102: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 102: the angel watches the processor run", "AA"), "round 102: the angel watches the processor run"),
    (("round 102: angle of the vector decides the match", "key"), "bssxh 102: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 102: angle of the vector decides the match", "lemon"), "csgbq 102: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 102: angle of the vector decides the match", "a"), "round 102: angle of the vector decides the match"),
    (("round 102: angle of the vector decides the match", "zz"), "qntmc 102: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 102: angle of the vector decides the match", "AgentU"),
        "ruyaw 102: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 102: angle of the vector decides the match", "keyboard"),
        "bssor 102: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 102: angle of the vector decides the match", "AA"), "round 102: angle of the vector decides the match"),
    (
        ("round 102: the candle burns twice as long at night", "key"),
        "bssxh 102: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 102: the candle burns twice as long at night", "lemon"),
        "csgbq 102: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 102: the candle burns twice as long at night", "a"), "round 102: the candle burns twice as long at night"),
    (
        ("round 102: the candle burns twice as long at night", "zz"),
        "qntmc 102: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 102: the candle burns twice as long at night", "AgentU"),
        "ruyaw 102: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 102: the candle burns twice as long at night", "keyboard"),
        "bssor 102: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 102: the candle burns twice as long at night", "AA"),
        "round 102: the candle burns twice as long at night",
    ),
    (("round 102: a mirror of the universe in one line", "key"), "bssxh 102: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 102: a mirror of the universe in one line", "lemon"), "csgbq 102: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 102: a mirror of the universe in one line", "a"), "round 102: a mirror of the universe in one line"),
    (("round 102: a mirror of the universe in one line", "zz"), "qntmc 102: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 102: a mirror of the universe in one line", "AgentU"), "ruyaw 102: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 102: a mirror of the universe in one line", "keyboard"),
        "bssor 102: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 102: a mirror of the universe in one line", "AA"), "round 102: a mirror of the universe in one line"),
    (("round 102: the queue drains before the storm", "key"), "bssxh 102: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 102: the queue drains before the storm", "lemon"), "csgbq 102: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 102: the queue drains before the storm", "a"), "round 102: the queue drains before the storm"),
    (("round 102: the queue drains before the storm", "zz"), "qntmc 102: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 102: the queue drains before the storm", "AgentU"), "ruyaw 102: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 102: the queue drains before the storm", "keyboard"), "bssor 102: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 102: the queue drains before the storm", "AA"), "round 102: the queue drains before the storm"),
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
