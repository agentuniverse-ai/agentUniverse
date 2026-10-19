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
    (("kitten190", "key"), "umrdil190"),
    (("kitten190", "lemon"), "vmfhry190"),
    (("kitten190", "a"), "kitten190"),
    (("kitten190", "zz"), "jhssdm190"),
    (("kitten190", "AgentU"), "koxgxh190"),
    (("kitten190", "keyboard"), "umrusn190"),
    (("kitten190", "AA"), "kitten190"),
    (("sitting190", "key"), "cmrdmlq190"),
    (("sitting190", "lemon"), "dmfhvyk190"),
    (("sitting190", "a"), "sitting190"),
    (("sitting190", "zz"), "rhsshmf190"),
    (("sitting190", "AgentU"), "soxgbhg190"),
    (("sitting190", "keyboard"), "cmruwnx190"),
    (("sitting190", "AA"), "sitting190"),
    (("agent190", "key"), "kkcxx190"),
    (("agent190", "lemon"), "lkqbg190"),
    (("agent190", "a"), "agent190"),
    (("agent190", "zz"), "zfdms190"),
    (("agent190", "AgentU"), "amiam190"),
    (("agent190", "keyboard"), "kkcoh190"),
    (("agent190", "AA"), "agent190"),
    (("angle190", "key"), "krevi190"),
    (("angle190", "lemon"), "lrszr190"),
    (("angle190", "a"), "angle190"),
    (("angle190", "zz"), "zmfkd190"),
    (("angle190", "AgentU"), "atkyx190"),
    (("angle190", "keyboard"), "krems190"),
    (("angle190", "AA"), "angle190"),
    (("universe190", "key"), "ergfipci190"),
    (("universe190", "lemon"), "frujrcwq190"),
    (("universe190", "a"), "universe190"),
    (("universe190", "zz"), "tmhudqrd190"),
    (("universe190", "AgentU"), "utmixlsk190"),
    (("universe190", "keyboard"), "ergwsrjh190"),
    (("universe190", "AA"), "universe190"),
    (("memory190", "key"), "wikyvw190"),
    (("memory190", "lemon"), "xiycej190"),
    (("memory190", "a"), "memory190"),
    (("memory190", "zz"), "ldlnqx190"),
    (("memory190", "AgentU"), "mkqbks190"),
    (("memory190", "keyboard"), "wikpfy190"),
    (("memory190", "AA"), "memory190"),
    (("stream190", "key"), "cxpoek190"),
    (("stream190", "lemon"), "dxdsnx190"),
    (("stream190", "a"), "stream190"),
    (("stream190", "zz"), "rsqdzl190"),
    (("stream190", "AgentU"), "szvrtg190"),
    (("stream190", "keyboard"), "cxpfom190"),
    (("stream190", "AA"), "stream190"),
    (("context190", "key"), "msldivd190"),
    (("context190", "lemon"), "nszhrix190"),
    (("context190", "a"), "context190"),
    (("context190", "zz"), "bnmsdws190"),
    (("context190", "AgentU"), "curgxrt190"),
    (("context190", "keyboard"), "mslusxk190"),
    (("context190", "AA"), "context190"),
    (("knowledge190", "key"), "urmgpcnkc190"),
    (("knowledge190", "lemon"), "vrakyphss190"),
    (("knowledge190", "a"), "knowledge190"),
    (("knowledge190", "zz"), "jmnvkdcfd190"),
    (("knowledge190", "AgentU"), "ktsjeydmi190"),
    (("knowledge190", "keyboard"), "urmxzeujo190"),
    (("knowledge190", "AA"), "knowledge190"),
    (("vector190", "key"), "fiadsp190"),
    (("vector190", "lemon"), "giohbc190"),
    (("vector190", "a"), "vector190"),
    (("vector190", "zz"), "udbsnq190"),
    (("vector190", "AgentU"), "vkgghl190"),
    (("vector190", "keyboard"), "fiaucr190"),
    (("vector190", "AA"), "vector190"),
    (("processor190", "key"), "zvmmiqcsp190"),
    (("processor190", "lemon"), "avaqrdwaf190"),
    (("processor190", "a"), "processor190"),
    (("processor190", "zz"), "oqnbdrrnq190"),
    (("processor190", "AgentU"), "pxspxmsuv190"),
    (("processor190", "keyboard"), "zvmdssjrb190"),
    (("processor190", "AA"), "processor190"),
    (("reasoning190", "key"), "biycslsre190"),
    (("reasoning190", "lemon"), "cimgbymzu190"),
    (("reasoning190", "a"), "reasoning190"),
    (("reasoning190", "zz"), "qdzrnmhmf190"),
    (("reasoning190", "AgentU"), "rkefhhitk190"),
    (("reasoning190", "keyboard"), "biytcnzqq190"),
    (("reasoning190", "AA"), "reasoning190"),
    (("machine190", "key"), "wearmlo190"),
    (("machine190", "lemon"), "xeovvyi190"),
    (("machine190", "a"), "machine190"),
    (("machine190", "zz"), "lzbghmd190"),
    (("machine190", "AgentU"), "mggubhe190"),
    (("machine190", "keyboard"), "weaiwnv190"),
    (("machine190", "AA"), "machine190"),
    (("learning190", "key"), "viybrgxk190"),
    (("learning190", "lemon"), "wimfatrs190"),
    (("learning190", "a"), "learning190"),
    (("learning190", "zz"), "kdzqmhmf190"),
    (("learning190", "AgentU"), "lkeegcnm190"),
    (("learning190", "keyboard"), "viysbiej190"),
    (("learning190", "AA"), "learning190"),
    (("model190", "key"), "wsbop190"),
    (("model190", "lemon"), "xspsy190"),
    (("model190", "a"), "model190"),
    (("model190", "zz"), "lncdk190"),
    (("model190", "AgentU"), "muhre190"),
    (("model190", "keyboard"), "wsbfz190"),
    (("model190", "AA"), "model190"),
    (("token190", "key"), "dsior190"),
    (("token190", "lemon"), "eswsa190"),
    (("token190", "a"), "token190"),
    (("token190", "zz"), "snjdm190"),
    (("token190", "AgentU"), "tuorg190"),
    (("token190", "keyboard"), "dsifb190"),
    (("token190", "AA"), "token190"),
    (("prompt190", "key"), "zvmwtr190"),
    (("prompt190", "lemon"), "avaace190"),
    (("prompt190", "a"), "prompt190"),
    (("prompt190", "zz"), "oqnlos190"),
    (("prompt190", "AgentU"), "pxszin190"),
    (("prompt190", "keyboard"), "zvmndt190"),
    (("prompt190", "AA"), "prompt190"),
    (("session190", "key"), "ciqcmmx190"),
    (("session190", "lemon"), "diegvzr190"),
    (("session190", "a"), "session190"),
    (("session190", "zz"), "rdrrhnm190"),
    (("session190", "AgentU"), "skwfbin190"),
    (("session190", "keyboard"), "ciqtwoe190"),
    (("session190", "AA"), "session190"),
    (("library190", "key"), "vmzbepi190"),
    (("library190", "lemon"), "wmnfncc190"),
    (("library190", "a"), "library190"),
    (("library190", "zz"), "khaqzqx190"),
    (("library190", "AgentU"), "lofetly190"),
    (("library190", "keyboard"), "vmzsorp190"),
    (("library190", "AA"), "library190"),
    (("service190", "key"), "cipfmao190"),
    (("service190", "lemon"), "didjvni190"),
    (("service190", "a"), "service190"),
    (("service190", "zz"), "rdquhbd190"),
    (("service190", "AgentU"), "skvibwe190"),
    (("service190", "keyboard"), "cipwwcv190"),
    (("service190", "AA"), "service190"),
    (("gateway190", "key"), "qeroayi190"),
    (("gateway190", "lemon"), "refsjlc190"),
    (("gateway190", "a"), "gateway190"),
    (("gateway190", "zz"), "fzsdvzx190"),
    (("gateway190", "AgentU"), "ggxrpuy190"),
    (("gateway190", "keyboard"), "qerfkap190"),
    (("gateway190", "AA"), "gateway190"),
    (("storage190", "key"), "cxmbeeo190"),
    (("storage190", "lemon"), "dxafnri190"),
    (("storage190", "a"), "storage190"),
    (("storage190", "zz"), "rsnqzfd190"),
    (("storage190", "AgentU"), "szsetae190"),
    (("storage190", "keyboard"), "cxmsogv190"),
    (("storage190", "AA"), "storage190"),
    (("network190", "key"), "xirgspu190"),
    (("network190", "lemon"), "yifkbco190"),
    (("network190", "a"), "network190"),
    (("network190", "zz"), "mdsvnqj190"),
    (("network190", "AgentU"), "nkxjhlk190"),
    (("network190", "keyboard"), "xirxcrb190"),
    (("network190", "AA"), "network190"),
    (("latency190", "key"), "verorai190"),
    (("latency190", "lemon"), "wefsanc190"),
    (("latency190", "a"), "latency190"),
    (("latency190", "zz"), "kzsdmbx190"),
    (("latency190", "AgentU"), "lgxrgwy190"),
    (("latency190", "keyboard"), "verfbcp190"),
    (("latency190", "AA"), "latency190"),
    (("buffer190", "key"), "lydpip190"),
    (("buffer190", "lemon"), "myrtrc190"),
    (("buffer190", "a"), "buffer190"),
    (("buffer190", "zz"), "ateedq190"),
    (("buffer190", "AgentU"), "bajsxl190"),
    (("buffer190", "keyboard"), "lydgsr190"),
    (("buffer190", "AA"), "buffer190"),
    (("queue190", "key"), "aycei190"),
    (("queue190", "lemon"), "byqir190"),
    (("queue190", "a"), "queue190"),
    (("queue190", "zz"), "ptdtd190"),
    (("queue190", "AgentU"), "qaihx190"),
    (("queue190", "keyboard"), "aycvs190"),
    (("queue190", "AA"), "queue190"),
    (("worker190", "key"), "gspuip190"),
    (("worker190", "lemon"), "hsdyrc190"),
    (("worker190", "a"), "worker190"),
    (("worker190", "zz"), "vnqjdq190"),
    (("worker190", "AgentU"), "wuvxxl190"),
    (("worker190", "keyboard"), "gsplsr190"),
    (("worker190", "AA"), "worker190"),
    (("kernel190", "key"), "uipxij190"),
    (("kernel190", "lemon"), "vidbrw190"),
    (("kernel190", "a"), "kernel190"),
    (("kernel190", "zz"), "jdqmdk190"),
    (("kernel190", "AgentU"), "kkvaxf190"),
    (("kernel190", "keyboard"), "uiposl190"),
    (("kernel190", "AA"), "kernel190"),
    (("signal190", "key"), "cmexej190"),
    (("signal190", "lemon"), "dmsbnw190"),
    (("signal190", "a"), "signal190"),
    (("signal190", "zz"), "rhfmzk190"),
    (("signal190", "AgentU"), "sokatf190"),
    (("signal190", "keyboard"), "cmeool190"),
    (("signal190", "AA"), "signal190"),
    (("packet190", "key"), "zeauir190"),
    (("packet190", "lemon"), "aeoyre190"),
    (("packet190", "a"), "packet190"),
    (("packet190", "zz"), "ozbjds190"),
    (("packet190", "AgentU"), "pggxxn190"),
    (("packet190", "keyboard"), "zealst190"),
    (("packet190", "AA"), "packet190"),
    (("router190", "key"), "bssdip190"),
    (("router190", "lemon"), "csghrc190"),
    (("router190", "a"), "router190"),
    (("router190", "zz"), "qntsdq190"),
    (("router190", "AgentU"), "ruygxl190"),
    (("router190", "keyboard"), "bssusr190"),
    (("router190", "AA"), "router190"),
    (("cluster190", "key"), "mpscxcb190"),
    (("cluster190", "lemon"), "npgggpv190"),
    (("cluster190", "a"), "cluster190"),
    (("cluster190", "zz"), "bktrsdq190"),
    (("cluster190", "AgentU"), "cryfmyr190"),
    (("cluster190", "keyboard"), "mpsthei190"),
    (("cluster190", "AA"), "cluster190"),
    (("mirror190", "key"), "wmpbsp190"),
    (("mirror190", "lemon"), "xmdfbc190"),
    (("mirror190", "a"), "mirror190"),
    (("mirror190", "zz"), "lhqqnq190"),
    (("mirror190", "AgentU"), "movehl190"),
    (("mirror190", "keyboard"), "wmpscr190"),
    (("mirror190", "AA"), "mirror190"),
    (("filter190", "key"), "pmjdip190"),
    (("filter190", "lemon"), "qmxhrc190"),
    (("filter190", "a"), "filter190"),
    (("filter190", "zz"), "ehksdq190"),
    (("filter190", "AgentU"), "fopgxl190"),
    (("filter190", "keyboard"), "pmjusr190"),
    (("filter190", "AA"), "filter190"),
    (("ranking190", "key"), "belumlq190"),
    (("ranking190", "lemon"), "cezyvyk190"),
    (("ranking190", "a"), "ranking190"),
    (("ranking190", "zz"), "qzmjhmf190"),
    (("ranking190", "AgentU"), "rgrxbhg190"),
    (("ranking190", "keyboard"), "bellwnx190"),
    (("ranking190", "AA"), "ranking190"),
    (("encoding190", "key"), "orayhgxk190"),
    (("encoding190", "lemon"), "procqtrs190"),
    (("encoding190", "a"), "encoding190"),
    (("encoding190", "zz"), "dmbnchmf190"),
    (("encoding190", "AgentU"), "etgbwcnm190"),
    (("encoding190", "keyboard"), "orapriej190"),
    (("encoding190", "AA"), "encoding190"),
    (("mapping190", "key"), "wenzmlq190"),
    (("mapping190", "lemon"), "xebdvyk190"),
    (("mapping190", "a"), "mapping190"),
    (("mapping190", "zz"), "lzoohmf190"),
    (("mapping190", "AgentU"), "mgtcbhg190"),
    (("mapping190", "keyboard"), "wenqwnx190"),
    (("mapping190", "AA"), "mapping190"),
    (("record190", "key"), "biayvb190"),
    (("record190", "lemon"), "cioceo190"),
    (("record190", "a"), "record190"),
    (("record190", "zz"), "qdbnqc190"),
    (("record190", "AgentU"), "rkgbkx190"),
    (("record190", "keyboard"), "biapfd190"),
    (("record190", "AA"), "record190"),
    (("candle190", "key"), "melnpc190"),
    (("candle190", "lemon"), "nezryp190"),
    (("candle190", "a"), "candle190"),
    (("candle190", "zz"), "bzmckd190"),
    (("candle190", "AgentU"), "cgrqey190"),
    (("candle190", "keyboard"), "meleze190"),
    (("candle190", "AA"), "candle190"),
    (("thread190", "key"), "dlpoeb190"),
    (("thread190", "lemon"), "eldsno190"),
    (("thread190", "a"), "thread190"),
    (("thread190", "zz"), "sgqdzc190"),
    (("thread190", "AgentU"), "tnvrtx190"),
    (("thread190", "keyboard"), "dlpfod190"),
    (("thread190", "AA"), "thread190"),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 190: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 190: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "a"),
        "round 190: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 190: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 190: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 190: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", "AA"),
        "round 190: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "key"),
        "bssxh 190: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 190: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "a"),
        "round 190: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 190: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 190: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 190: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", "AA"),
        "round 190: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 190: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 190: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "a"),
        "round 190: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 190: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 190: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 190: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", "AA"),
        "round 190: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 190: the processor reads the record then stops", "key"),
        "bssxh 190: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 190: the processor reads the record then stops", "lemon"),
        "csgbq 190: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 190: the processor reads the record then stops", "a"),
        "round 190: the processor reads the record then stops",
    ),
    (
        ("round 190: the processor reads the record then stops", "zz"),
        "qntmc 190: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 190: the processor reads the record then stops", "AgentU"),
        "ruyaw 190: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 190: the processor reads the record then stops", "keyboard"),
        "bssor 190: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 190: the processor reads the record then stops", "AA"),
        "round 190: the processor reads the record then stops",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "key"),
        "bssxh 190: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "lemon"),
        "csgbq 190: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "a"),
        "round 190: a worker pulls the next task from the queue",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "zz"),
        "qntmc 190: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 190: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "keyboard"),
        "bssor 190: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 190: a worker pulls the next task from the queue", "AA"),
        "round 190: a worker pulls the next task from the queue",
    ),
    (
        ("round 190: signals travel through the network layer", "key"),
        "bssxh 190: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 190: signals travel through the network layer", "lemon"),
        "csgbq 190: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 190: signals travel through the network layer", "a"),
        "round 190: signals travel through the network layer",
    ),
    (
        ("round 190: signals travel through the network layer", "zz"),
        "qntmc 190: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 190: signals travel through the network layer", "AgentU"),
        "ruyaw 190: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 190: signals travel through the network layer", "keyboard"),
        "bssor 190: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 190: signals travel through the network layer", "AA"),
        "round 190: signals travel through the network layer",
    ),
    (
        ("round 190: the gateway routes each request by policy", "key"),
        "bssxh 190: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 190: the gateway routes each request by policy", "lemon"),
        "csgbq 190: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 190: the gateway routes each request by policy", "a"),
        "round 190: the gateway routes each request by policy",
    ),
    (
        ("round 190: the gateway routes each request by policy", "zz"),
        "qntmc 190: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 190: the gateway routes each request by policy", "AgentU"),
        "ruyaw 190: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 190: the gateway routes each request by policy", "keyboard"),
        "bssor 190: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 190: the gateway routes each request by policy", "AA"),
        "round 190: the gateway routes each request by policy",
    ),
    (("round 190: memory grows until the buffer is full", "key"), "bssxh 190: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 190: memory grows until the buffer is full", "lemon"), "csgbq 190: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 190: memory grows until the buffer is full", "a"), "round 190: memory grows until the buffer is full"),
    (("round 190: memory grows until the buffer is full", "zz"), "qntmc 190: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 190: memory grows until the buffer is full", "AgentU"),
        "ruyaw 190: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 190: memory grows until the buffer is full", "keyboard"),
        "bssor 190: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 190: memory grows until the buffer is full", "AA"), "round 190: memory grows until the buffer is full"),
    (("round 190: the cluster mirrors every packet twice", "key"), "bssxh 190: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 190: the cluster mirrors every packet twice", "lemon"),
        "csgbq 190: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 190: the cluster mirrors every packet twice", "a"), "round 190: the cluster mirrors every packet twice"),
    (("round 190: the cluster mirrors every packet twice", "zz"), "qntmc 190: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 190: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 190: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 190: the cluster mirrors every packet twice", "keyboard"),
        "bssor 190: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 190: the cluster mirrors every packet twice", "AA"), "round 190: the cluster mirrors every packet twice"),
    (
        ("round 190: ranking uses tokens learned from the corpus", "key"),
        "bssxh 190: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 190: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", "a"),
        "round 190: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 190: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 190: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 190: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", "AA"),
        "round 190: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 190: a long session ends when the candle dies", "key"),
        "bssxh 190: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 190: a long session ends when the candle dies", "lemon"),
        "csgbq 190: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 190: a long session ends when the candle dies", "a"),
        "round 190: a long session ends when the candle dies",
    ),
    (
        ("round 190: a long session ends when the candle dies", "zz"),
        "qntmc 190: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 190: a long session ends when the candle dies", "AgentU"),
        "ruyaw 190: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 190: a long session ends when the candle dies", "keyboard"),
        "bssor 190: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 190: a long session ends when the candle dies", "AA"),
        "round 190: a long session ends when the candle dies",
    ),
    (("round 190: encode the prompt then map the result", "key"), "bssxh 190: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 190: encode the prompt then map the result", "lemon"), "csgbq 190: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 190: encode the prompt then map the result", "a"), "round 190: encode the prompt then map the result"),
    (("round 190: encode the prompt then map the result", "zz"), "qntmc 190: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 190: encode the prompt then map the result", "AgentU"),
        "ruyaw 190: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 190: encode the prompt then map the result", "keyboard"),
        "bssor 190: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 190: encode the prompt then map the result", "AA"), "round 190: encode the prompt then map the result"),
    (("round 190: the kernel wakes the worker at dawn", "key"), "bssxh 190: rri iovlop ukocc xfo ambocb er neux"),
    (("round 190: the kernel wakes the worker at dawn", "lemon"), "csgbq 190: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 190: the kernel wakes the worker at dawn", "a"), "round 190: the kernel wakes the worker at dawn"),
    (("round 190: the kernel wakes the worker at dawn", "zz"), "qntmc 190: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 190: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 190: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 190: the kernel wakes the worker at dawn", "keyboard"), "bssor 190: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 190: the kernel wakes the worker at dawn", "AA"), "round 190: the kernel wakes the worker at dawn"),
    (("round 190: service latency drops after the patch", "key"), "bssxh 190: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 190: service latency drops after the patch", "lemon"), "csgbq 190: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 190: service latency drops after the patch", "a"), "round 190: service latency drops after the patch"),
    (("round 190: service latency drops after the patch", "zz"), "qntmc 190: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 190: service latency drops after the patch", "AgentU"),
        "ruyaw 190: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 190: service latency drops after the patch", "keyboard"),
        "bssor 190: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 190: service latency drops after the patch", "AA"), "round 190: service latency drops after the patch"),
    (
        ("round 190: the library caches every vector it sees", "key"),
        "bssxh 190: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 190: the library caches every vector it sees", "lemon"),
        "csgbq 190: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 190: the library caches every vector it sees", "a"), "round 190: the library caches every vector it sees"),
    (
        ("round 190: the library caches every vector it sees", "zz"),
        "qntmc 190: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 190: the library caches every vector it sees", "AgentU"),
        "ruyaw 190: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 190: the library caches every vector it sees", "keyboard"),
        "bssor 190: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 190: the library caches every vector it sees", "AA"),
        "round 190: the library caches every vector it sees",
    ),
    (("round 190: agents argue then the debate resolves", "key"), "bssxh 190: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 190: agents argue then the debate resolves", "lemon"), "csgbq 190: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 190: agents argue then the debate resolves", "a"), "round 190: agents argue then the debate resolves"),
    (("round 190: agents argue then the debate resolves", "zz"), "qntmc 190: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 190: agents argue then the debate resolves", "AgentU"),
        "ruyaw 190: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 190: agents argue then the debate resolves", "keyboard"),
        "bssor 190: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 190: agents argue then the debate resolves", "AA"), "round 190: agents argue then the debate resolves"),
    (("round 190: the filter keeps only strong matches", "key"), "bssxh 190: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 190: the filter keeps only strong matches", "lemon"), "csgbq 190: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 190: the filter keeps only strong matches", "a"), "round 190: the filter keeps only strong matches"),
    (("round 190: the filter keeps only strong matches", "zz"), "qntmc 190: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 190: the filter keeps only strong matches", "AgentU"), "ruyaw 190: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 190: the filter keeps only strong matches", "keyboard"),
        "bssor 190: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 190: the filter keeps only strong matches", "AA"), "round 190: the filter keeps only strong matches"),
    (("round 190: the model answers with a short reply", "key"), "bssxh 190: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 190: the model answers with a short reply", "lemon"), "csgbq 190: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 190: the model answers with a short reply", "a"), "round 190: the model answers with a short reply"),
    (("round 190: the model answers with a short reply", "zz"), "qntmc 190: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 190: the model answers with a short reply", "AgentU"), "ruyaw 190: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 190: the model answers with a short reply", "keyboard"),
        "bssor 190: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 190: the model answers with a short reply", "AA"), "round 190: the model answers with a short reply"),
    (
        ("round 190: the recorder stores the reasoning trace", "key"),
        "bssxh 190: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 190: the recorder stores the reasoning trace", "lemon"),
        "csgbq 190: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 190: the recorder stores the reasoning trace", "a"), "round 190: the recorder stores the reasoning trace"),
    (
        ("round 190: the recorder stores the reasoning trace", "zz"),
        "qntmc 190: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 190: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 190: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 190: the recorder stores the reasoning trace", "keyboard"),
        "bssor 190: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 190: the recorder stores the reasoning trace", "AA"),
        "round 190: the recorder stores the reasoning trace",
    ),
    (("round 190: the angel watches the processor run", "key"), "bssxh 190: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 190: the angel watches the processor run", "lemon"), "csgbq 190: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 190: the angel watches the processor run", "a"), "round 190: the angel watches the processor run"),
    (("round 190: the angel watches the processor run", "zz"), "qntmc 190: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 190: the angel watches the processor run", "AgentU"), "ruyaw 190: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 190: the angel watches the processor run", "keyboard"), "bssor 190: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 190: the angel watches the processor run", "AA"), "round 190: the angel watches the processor run"),
    (("round 190: angle of the vector decides the match", "key"), "bssxh 190: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 190: angle of the vector decides the match", "lemon"), "csgbq 190: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 190: angle of the vector decides the match", "a"), "round 190: angle of the vector decides the match"),
    (("round 190: angle of the vector decides the match", "zz"), "qntmc 190: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 190: angle of the vector decides the match", "AgentU"),
        "ruyaw 190: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 190: angle of the vector decides the match", "keyboard"),
        "bssor 190: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 190: angle of the vector decides the match", "AA"), "round 190: angle of the vector decides the match"),
    (
        ("round 190: the candle burns twice as long at night", "key"),
        "bssxh 190: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 190: the candle burns twice as long at night", "lemon"),
        "csgbq 190: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 190: the candle burns twice as long at night", "a"), "round 190: the candle burns twice as long at night"),
    (
        ("round 190: the candle burns twice as long at night", "zz"),
        "qntmc 190: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 190: the candle burns twice as long at night", "AgentU"),
        "ruyaw 190: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 190: the candle burns twice as long at night", "keyboard"),
        "bssor 190: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 190: the candle burns twice as long at night", "AA"),
        "round 190: the candle burns twice as long at night",
    ),
    (("round 190: a mirror of the universe in one line", "key"), "bssxh 190: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 190: a mirror of the universe in one line", "lemon"), "csgbq 190: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 190: a mirror of the universe in one line", "a"), "round 190: a mirror of the universe in one line"),
    (("round 190: a mirror of the universe in one line", "zz"), "qntmc 190: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 190: a mirror of the universe in one line", "AgentU"), "ruyaw 190: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 190: a mirror of the universe in one line", "keyboard"),
        "bssor 190: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 190: a mirror of the universe in one line", "AA"), "round 190: a mirror of the universe in one line"),
    (("round 190: the queue drains before the storm", "key"), "bssxh 190: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 190: the queue drains before the storm", "lemon"), "csgbq 190: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 190: the queue drains before the storm", "a"), "round 190: the queue drains before the storm"),
    (("round 190: the queue drains before the storm", "zz"), "qntmc 190: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 190: the queue drains before the storm", "AgentU"), "ruyaw 190: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 190: the queue drains before the storm", "keyboard"), "bssor 190: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 190: the queue drains before the storm", "AA"), "round 190: the queue drains before the storm"),
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
