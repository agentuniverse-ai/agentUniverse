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
    (("kitten191", "key"), "umrdil191"),
    (("kitten191", "lemon"), "vmfhry191"),
    (("kitten191", "a"), "kitten191"),
    (("kitten191", "zz"), "jhssdm191"),
    (("kitten191", "AgentU"), "koxgxh191"),
    (("kitten191", "keyboard"), "umrusn191"),
    (("kitten191", "AA"), "kitten191"),
    (("sitting191", "key"), "cmrdmlq191"),
    (("sitting191", "lemon"), "dmfhvyk191"),
    (("sitting191", "a"), "sitting191"),
    (("sitting191", "zz"), "rhsshmf191"),
    (("sitting191", "AgentU"), "soxgbhg191"),
    (("sitting191", "keyboard"), "cmruwnx191"),
    (("sitting191", "AA"), "sitting191"),
    (("agent191", "key"), "kkcxx191"),
    (("agent191", "lemon"), "lkqbg191"),
    (("agent191", "a"), "agent191"),
    (("agent191", "zz"), "zfdms191"),
    (("agent191", "AgentU"), "amiam191"),
    (("agent191", "keyboard"), "kkcoh191"),
    (("agent191", "AA"), "agent191"),
    (("angle191", "key"), "krevi191"),
    (("angle191", "lemon"), "lrszr191"),
    (("angle191", "a"), "angle191"),
    (("angle191", "zz"), "zmfkd191"),
    (("angle191", "AgentU"), "atkyx191"),
    (("angle191", "keyboard"), "krems191"),
    (("angle191", "AA"), "angle191"),
    (("universe191", "key"), "ergfipci191"),
    (("universe191", "lemon"), "frujrcwq191"),
    (("universe191", "a"), "universe191"),
    (("universe191", "zz"), "tmhudqrd191"),
    (("universe191", "AgentU"), "utmixlsk191"),
    (("universe191", "keyboard"), "ergwsrjh191"),
    (("universe191", "AA"), "universe191"),
    (("memory191", "key"), "wikyvw191"),
    (("memory191", "lemon"), "xiycej191"),
    (("memory191", "a"), "memory191"),
    (("memory191", "zz"), "ldlnqx191"),
    (("memory191", "AgentU"), "mkqbks191"),
    (("memory191", "keyboard"), "wikpfy191"),
    (("memory191", "AA"), "memory191"),
    (("stream191", "key"), "cxpoek191"),
    (("stream191", "lemon"), "dxdsnx191"),
    (("stream191", "a"), "stream191"),
    (("stream191", "zz"), "rsqdzl191"),
    (("stream191", "AgentU"), "szvrtg191"),
    (("stream191", "keyboard"), "cxpfom191"),
    (("stream191", "AA"), "stream191"),
    (("context191", "key"), "msldivd191"),
    (("context191", "lemon"), "nszhrix191"),
    (("context191", "a"), "context191"),
    (("context191", "zz"), "bnmsdws191"),
    (("context191", "AgentU"), "curgxrt191"),
    (("context191", "keyboard"), "mslusxk191"),
    (("context191", "AA"), "context191"),
    (("knowledge191", "key"), "urmgpcnkc191"),
    (("knowledge191", "lemon"), "vrakyphss191"),
    (("knowledge191", "a"), "knowledge191"),
    (("knowledge191", "zz"), "jmnvkdcfd191"),
    (("knowledge191", "AgentU"), "ktsjeydmi191"),
    (("knowledge191", "keyboard"), "urmxzeujo191"),
    (("knowledge191", "AA"), "knowledge191"),
    (("vector191", "key"), "fiadsp191"),
    (("vector191", "lemon"), "giohbc191"),
    (("vector191", "a"), "vector191"),
    (("vector191", "zz"), "udbsnq191"),
    (("vector191", "AgentU"), "vkgghl191"),
    (("vector191", "keyboard"), "fiaucr191"),
    (("vector191", "AA"), "vector191"),
    (("processor191", "key"), "zvmmiqcsp191"),
    (("processor191", "lemon"), "avaqrdwaf191"),
    (("processor191", "a"), "processor191"),
    (("processor191", "zz"), "oqnbdrrnq191"),
    (("processor191", "AgentU"), "pxspxmsuv191"),
    (("processor191", "keyboard"), "zvmdssjrb191"),
    (("processor191", "AA"), "processor191"),
    (("reasoning191", "key"), "biycslsre191"),
    (("reasoning191", "lemon"), "cimgbymzu191"),
    (("reasoning191", "a"), "reasoning191"),
    (("reasoning191", "zz"), "qdzrnmhmf191"),
    (("reasoning191", "AgentU"), "rkefhhitk191"),
    (("reasoning191", "keyboard"), "biytcnzqq191"),
    (("reasoning191", "AA"), "reasoning191"),
    (("machine191", "key"), "wearmlo191"),
    (("machine191", "lemon"), "xeovvyi191"),
    (("machine191", "a"), "machine191"),
    (("machine191", "zz"), "lzbghmd191"),
    (("machine191", "AgentU"), "mggubhe191"),
    (("machine191", "keyboard"), "weaiwnv191"),
    (("machine191", "AA"), "machine191"),
    (("learning191", "key"), "viybrgxk191"),
    (("learning191", "lemon"), "wimfatrs191"),
    (("learning191", "a"), "learning191"),
    (("learning191", "zz"), "kdzqmhmf191"),
    (("learning191", "AgentU"), "lkeegcnm191"),
    (("learning191", "keyboard"), "viysbiej191"),
    (("learning191", "AA"), "learning191"),
    (("model191", "key"), "wsbop191"),
    (("model191", "lemon"), "xspsy191"),
    (("model191", "a"), "model191"),
    (("model191", "zz"), "lncdk191"),
    (("model191", "AgentU"), "muhre191"),
    (("model191", "keyboard"), "wsbfz191"),
    (("model191", "AA"), "model191"),
    (("token191", "key"), "dsior191"),
    (("token191", "lemon"), "eswsa191"),
    (("token191", "a"), "token191"),
    (("token191", "zz"), "snjdm191"),
    (("token191", "AgentU"), "tuorg191"),
    (("token191", "keyboard"), "dsifb191"),
    (("token191", "AA"), "token191"),
    (("prompt191", "key"), "zvmwtr191"),
    (("prompt191", "lemon"), "avaace191"),
    (("prompt191", "a"), "prompt191"),
    (("prompt191", "zz"), "oqnlos191"),
    (("prompt191", "AgentU"), "pxszin191"),
    (("prompt191", "keyboard"), "zvmndt191"),
    (("prompt191", "AA"), "prompt191"),
    (("session191", "key"), "ciqcmmx191"),
    (("session191", "lemon"), "diegvzr191"),
    (("session191", "a"), "session191"),
    (("session191", "zz"), "rdrrhnm191"),
    (("session191", "AgentU"), "skwfbin191"),
    (("session191", "keyboard"), "ciqtwoe191"),
    (("session191", "AA"), "session191"),
    (("library191", "key"), "vmzbepi191"),
    (("library191", "lemon"), "wmnfncc191"),
    (("library191", "a"), "library191"),
    (("library191", "zz"), "khaqzqx191"),
    (("library191", "AgentU"), "lofetly191"),
    (("library191", "keyboard"), "vmzsorp191"),
    (("library191", "AA"), "library191"),
    (("service191", "key"), "cipfmao191"),
    (("service191", "lemon"), "didjvni191"),
    (("service191", "a"), "service191"),
    (("service191", "zz"), "rdquhbd191"),
    (("service191", "AgentU"), "skvibwe191"),
    (("service191", "keyboard"), "cipwwcv191"),
    (("service191", "AA"), "service191"),
    (("gateway191", "key"), "qeroayi191"),
    (("gateway191", "lemon"), "refsjlc191"),
    (("gateway191", "a"), "gateway191"),
    (("gateway191", "zz"), "fzsdvzx191"),
    (("gateway191", "AgentU"), "ggxrpuy191"),
    (("gateway191", "keyboard"), "qerfkap191"),
    (("gateway191", "AA"), "gateway191"),
    (("storage191", "key"), "cxmbeeo191"),
    (("storage191", "lemon"), "dxafnri191"),
    (("storage191", "a"), "storage191"),
    (("storage191", "zz"), "rsnqzfd191"),
    (("storage191", "AgentU"), "szsetae191"),
    (("storage191", "keyboard"), "cxmsogv191"),
    (("storage191", "AA"), "storage191"),
    (("network191", "key"), "xirgspu191"),
    (("network191", "lemon"), "yifkbco191"),
    (("network191", "a"), "network191"),
    (("network191", "zz"), "mdsvnqj191"),
    (("network191", "AgentU"), "nkxjhlk191"),
    (("network191", "keyboard"), "xirxcrb191"),
    (("network191", "AA"), "network191"),
    (("latency191", "key"), "verorai191"),
    (("latency191", "lemon"), "wefsanc191"),
    (("latency191", "a"), "latency191"),
    (("latency191", "zz"), "kzsdmbx191"),
    (("latency191", "AgentU"), "lgxrgwy191"),
    (("latency191", "keyboard"), "verfbcp191"),
    (("latency191", "AA"), "latency191"),
    (("buffer191", "key"), "lydpip191"),
    (("buffer191", "lemon"), "myrtrc191"),
    (("buffer191", "a"), "buffer191"),
    (("buffer191", "zz"), "ateedq191"),
    (("buffer191", "AgentU"), "bajsxl191"),
    (("buffer191", "keyboard"), "lydgsr191"),
    (("buffer191", "AA"), "buffer191"),
    (("queue191", "key"), "aycei191"),
    (("queue191", "lemon"), "byqir191"),
    (("queue191", "a"), "queue191"),
    (("queue191", "zz"), "ptdtd191"),
    (("queue191", "AgentU"), "qaihx191"),
    (("queue191", "keyboard"), "aycvs191"),
    (("queue191", "AA"), "queue191"),
    (("worker191", "key"), "gspuip191"),
    (("worker191", "lemon"), "hsdyrc191"),
    (("worker191", "a"), "worker191"),
    (("worker191", "zz"), "vnqjdq191"),
    (("worker191", "AgentU"), "wuvxxl191"),
    (("worker191", "keyboard"), "gsplsr191"),
    (("worker191", "AA"), "worker191"),
    (("kernel191", "key"), "uipxij191"),
    (("kernel191", "lemon"), "vidbrw191"),
    (("kernel191", "a"), "kernel191"),
    (("kernel191", "zz"), "jdqmdk191"),
    (("kernel191", "AgentU"), "kkvaxf191"),
    (("kernel191", "keyboard"), "uiposl191"),
    (("kernel191", "AA"), "kernel191"),
    (("signal191", "key"), "cmexej191"),
    (("signal191", "lemon"), "dmsbnw191"),
    (("signal191", "a"), "signal191"),
    (("signal191", "zz"), "rhfmzk191"),
    (("signal191", "AgentU"), "sokatf191"),
    (("signal191", "keyboard"), "cmeool191"),
    (("signal191", "AA"), "signal191"),
    (("packet191", "key"), "zeauir191"),
    (("packet191", "lemon"), "aeoyre191"),
    (("packet191", "a"), "packet191"),
    (("packet191", "zz"), "ozbjds191"),
    (("packet191", "AgentU"), "pggxxn191"),
    (("packet191", "keyboard"), "zealst191"),
    (("packet191", "AA"), "packet191"),
    (("router191", "key"), "bssdip191"),
    (("router191", "lemon"), "csghrc191"),
    (("router191", "a"), "router191"),
    (("router191", "zz"), "qntsdq191"),
    (("router191", "AgentU"), "ruygxl191"),
    (("router191", "keyboard"), "bssusr191"),
    (("router191", "AA"), "router191"),
    (("cluster191", "key"), "mpscxcb191"),
    (("cluster191", "lemon"), "npgggpv191"),
    (("cluster191", "a"), "cluster191"),
    (("cluster191", "zz"), "bktrsdq191"),
    (("cluster191", "AgentU"), "cryfmyr191"),
    (("cluster191", "keyboard"), "mpsthei191"),
    (("cluster191", "AA"), "cluster191"),
    (("mirror191", "key"), "wmpbsp191"),
    (("mirror191", "lemon"), "xmdfbc191"),
    (("mirror191", "a"), "mirror191"),
    (("mirror191", "zz"), "lhqqnq191"),
    (("mirror191", "AgentU"), "movehl191"),
    (("mirror191", "keyboard"), "wmpscr191"),
    (("mirror191", "AA"), "mirror191"),
    (("filter191", "key"), "pmjdip191"),
    (("filter191", "lemon"), "qmxhrc191"),
    (("filter191", "a"), "filter191"),
    (("filter191", "zz"), "ehksdq191"),
    (("filter191", "AgentU"), "fopgxl191"),
    (("filter191", "keyboard"), "pmjusr191"),
    (("filter191", "AA"), "filter191"),
    (("ranking191", "key"), "belumlq191"),
    (("ranking191", "lemon"), "cezyvyk191"),
    (("ranking191", "a"), "ranking191"),
    (("ranking191", "zz"), "qzmjhmf191"),
    (("ranking191", "AgentU"), "rgrxbhg191"),
    (("ranking191", "keyboard"), "bellwnx191"),
    (("ranking191", "AA"), "ranking191"),
    (("encoding191", "key"), "orayhgxk191"),
    (("encoding191", "lemon"), "procqtrs191"),
    (("encoding191", "a"), "encoding191"),
    (("encoding191", "zz"), "dmbnchmf191"),
    (("encoding191", "AgentU"), "etgbwcnm191"),
    (("encoding191", "keyboard"), "orapriej191"),
    (("encoding191", "AA"), "encoding191"),
    (("mapping191", "key"), "wenzmlq191"),
    (("mapping191", "lemon"), "xebdvyk191"),
    (("mapping191", "a"), "mapping191"),
    (("mapping191", "zz"), "lzoohmf191"),
    (("mapping191", "AgentU"), "mgtcbhg191"),
    (("mapping191", "keyboard"), "wenqwnx191"),
    (("mapping191", "AA"), "mapping191"),
    (("record191", "key"), "biayvb191"),
    (("record191", "lemon"), "cioceo191"),
    (("record191", "a"), "record191"),
    (("record191", "zz"), "qdbnqc191"),
    (("record191", "AgentU"), "rkgbkx191"),
    (("record191", "keyboard"), "biapfd191"),
    (("record191", "AA"), "record191"),
    (("candle191", "key"), "melnpc191"),
    (("candle191", "lemon"), "nezryp191"),
    (("candle191", "a"), "candle191"),
    (("candle191", "zz"), "bzmckd191"),
    (("candle191", "AgentU"), "cgrqey191"),
    (("candle191", "keyboard"), "meleze191"),
    (("candle191", "AA"), "candle191"),
    (("thread191", "key"), "dlpoeb191"),
    (("thread191", "lemon"), "eldsno191"),
    (("thread191", "a"), "thread191"),
    (("thread191", "zz"), "sgqdzc191"),
    (("thread191", "AgentU"), "tnvrtx191"),
    (("thread191", "keyboard"), "dlpfod191"),
    (("thread191", "AA"), "thread191"),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 191: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 191: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "a"),
        "round 191: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 191: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 191: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 191: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", "AA"),
        "round 191: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "key"),
        "bssxh 191: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 191: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "a"),
        "round 191: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 191: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 191: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 191: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", "AA"),
        "round 191: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 191: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 191: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "a"),
        "round 191: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 191: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 191: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 191: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", "AA"),
        "round 191: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 191: the processor reads the record then stops", "key"),
        "bssxh 191: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 191: the processor reads the record then stops", "lemon"),
        "csgbq 191: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 191: the processor reads the record then stops", "a"),
        "round 191: the processor reads the record then stops",
    ),
    (
        ("round 191: the processor reads the record then stops", "zz"),
        "qntmc 191: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 191: the processor reads the record then stops", "AgentU"),
        "ruyaw 191: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 191: the processor reads the record then stops", "keyboard"),
        "bssor 191: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 191: the processor reads the record then stops", "AA"),
        "round 191: the processor reads the record then stops",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "key"),
        "bssxh 191: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "lemon"),
        "csgbq 191: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "a"),
        "round 191: a worker pulls the next task from the queue",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "zz"),
        "qntmc 191: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 191: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "keyboard"),
        "bssor 191: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 191: a worker pulls the next task from the queue", "AA"),
        "round 191: a worker pulls the next task from the queue",
    ),
    (
        ("round 191: signals travel through the network layer", "key"),
        "bssxh 191: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 191: signals travel through the network layer", "lemon"),
        "csgbq 191: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 191: signals travel through the network layer", "a"),
        "round 191: signals travel through the network layer",
    ),
    (
        ("round 191: signals travel through the network layer", "zz"),
        "qntmc 191: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 191: signals travel through the network layer", "AgentU"),
        "ruyaw 191: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 191: signals travel through the network layer", "keyboard"),
        "bssor 191: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 191: signals travel through the network layer", "AA"),
        "round 191: signals travel through the network layer",
    ),
    (
        ("round 191: the gateway routes each request by policy", "key"),
        "bssxh 191: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 191: the gateway routes each request by policy", "lemon"),
        "csgbq 191: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 191: the gateway routes each request by policy", "a"),
        "round 191: the gateway routes each request by policy",
    ),
    (
        ("round 191: the gateway routes each request by policy", "zz"),
        "qntmc 191: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 191: the gateway routes each request by policy", "AgentU"),
        "ruyaw 191: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 191: the gateway routes each request by policy", "keyboard"),
        "bssor 191: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 191: the gateway routes each request by policy", "AA"),
        "round 191: the gateway routes each request by policy",
    ),
    (("round 191: memory grows until the buffer is full", "key"), "bssxh 191: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 191: memory grows until the buffer is full", "lemon"), "csgbq 191: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 191: memory grows until the buffer is full", "a"), "round 191: memory grows until the buffer is full"),
    (("round 191: memory grows until the buffer is full", "zz"), "qntmc 191: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 191: memory grows until the buffer is full", "AgentU"),
        "ruyaw 191: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 191: memory grows until the buffer is full", "keyboard"),
        "bssor 191: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 191: memory grows until the buffer is full", "AA"), "round 191: memory grows until the buffer is full"),
    (("round 191: the cluster mirrors every packet twice", "key"), "bssxh 191: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 191: the cluster mirrors every packet twice", "lemon"),
        "csgbq 191: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 191: the cluster mirrors every packet twice", "a"), "round 191: the cluster mirrors every packet twice"),
    (("round 191: the cluster mirrors every packet twice", "zz"), "qntmc 191: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 191: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 191: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 191: the cluster mirrors every packet twice", "keyboard"),
        "bssor 191: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 191: the cluster mirrors every packet twice", "AA"), "round 191: the cluster mirrors every packet twice"),
    (
        ("round 191: ranking uses tokens learned from the corpus", "key"),
        "bssxh 191: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 191: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", "a"),
        "round 191: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 191: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 191: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 191: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", "AA"),
        "round 191: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 191: a long session ends when the candle dies", "key"),
        "bssxh 191: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 191: a long session ends when the candle dies", "lemon"),
        "csgbq 191: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 191: a long session ends when the candle dies", "a"),
        "round 191: a long session ends when the candle dies",
    ),
    (
        ("round 191: a long session ends when the candle dies", "zz"),
        "qntmc 191: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 191: a long session ends when the candle dies", "AgentU"),
        "ruyaw 191: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 191: a long session ends when the candle dies", "keyboard"),
        "bssor 191: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 191: a long session ends when the candle dies", "AA"),
        "round 191: a long session ends when the candle dies",
    ),
    (("round 191: encode the prompt then map the result", "key"), "bssxh 191: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 191: encode the prompt then map the result", "lemon"), "csgbq 191: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 191: encode the prompt then map the result", "a"), "round 191: encode the prompt then map the result"),
    (("round 191: encode the prompt then map the result", "zz"), "qntmc 191: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 191: encode the prompt then map the result", "AgentU"),
        "ruyaw 191: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 191: encode the prompt then map the result", "keyboard"),
        "bssor 191: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 191: encode the prompt then map the result", "AA"), "round 191: encode the prompt then map the result"),
    (("round 191: the kernel wakes the worker at dawn", "key"), "bssxh 191: rri iovlop ukocc xfo ambocb er neux"),
    (("round 191: the kernel wakes the worker at dawn", "lemon"), "csgbq 191: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 191: the kernel wakes the worker at dawn", "a"), "round 191: the kernel wakes the worker at dawn"),
    (("round 191: the kernel wakes the worker at dawn", "zz"), "qntmc 191: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 191: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 191: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 191: the kernel wakes the worker at dawn", "keyboard"), "bssor 191: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 191: the kernel wakes the worker at dawn", "AA"), "round 191: the kernel wakes the worker at dawn"),
    (("round 191: service latency drops after the patch", "key"), "bssxh 191: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 191: service latency drops after the patch", "lemon"), "csgbq 191: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 191: service latency drops after the patch", "a"), "round 191: service latency drops after the patch"),
    (("round 191: service latency drops after the patch", "zz"), "qntmc 191: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 191: service latency drops after the patch", "AgentU"),
        "ruyaw 191: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 191: service latency drops after the patch", "keyboard"),
        "bssor 191: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 191: service latency drops after the patch", "AA"), "round 191: service latency drops after the patch"),
    (
        ("round 191: the library caches every vector it sees", "key"),
        "bssxh 191: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 191: the library caches every vector it sees", "lemon"),
        "csgbq 191: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 191: the library caches every vector it sees", "a"), "round 191: the library caches every vector it sees"),
    (
        ("round 191: the library caches every vector it sees", "zz"),
        "qntmc 191: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 191: the library caches every vector it sees", "AgentU"),
        "ruyaw 191: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 191: the library caches every vector it sees", "keyboard"),
        "bssor 191: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 191: the library caches every vector it sees", "AA"),
        "round 191: the library caches every vector it sees",
    ),
    (("round 191: agents argue then the debate resolves", "key"), "bssxh 191: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 191: agents argue then the debate resolves", "lemon"), "csgbq 191: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 191: agents argue then the debate resolves", "a"), "round 191: agents argue then the debate resolves"),
    (("round 191: agents argue then the debate resolves", "zz"), "qntmc 191: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 191: agents argue then the debate resolves", "AgentU"),
        "ruyaw 191: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 191: agents argue then the debate resolves", "keyboard"),
        "bssor 191: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 191: agents argue then the debate resolves", "AA"), "round 191: agents argue then the debate resolves"),
    (("round 191: the filter keeps only strong matches", "key"), "bssxh 191: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 191: the filter keeps only strong matches", "lemon"), "csgbq 191: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 191: the filter keeps only strong matches", "a"), "round 191: the filter keeps only strong matches"),
    (("round 191: the filter keeps only strong matches", "zz"), "qntmc 191: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 191: the filter keeps only strong matches", "AgentU"), "ruyaw 191: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 191: the filter keeps only strong matches", "keyboard"),
        "bssor 191: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 191: the filter keeps only strong matches", "AA"), "round 191: the filter keeps only strong matches"),
    (("round 191: the model answers with a short reply", "key"), "bssxh 191: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 191: the model answers with a short reply", "lemon"), "csgbq 191: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 191: the model answers with a short reply", "a"), "round 191: the model answers with a short reply"),
    (("round 191: the model answers with a short reply", "zz"), "qntmc 191: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 191: the model answers with a short reply", "AgentU"), "ruyaw 191: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 191: the model answers with a short reply", "keyboard"),
        "bssor 191: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 191: the model answers with a short reply", "AA"), "round 191: the model answers with a short reply"),
    (
        ("round 191: the recorder stores the reasoning trace", "key"),
        "bssxh 191: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 191: the recorder stores the reasoning trace", "lemon"),
        "csgbq 191: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 191: the recorder stores the reasoning trace", "a"), "round 191: the recorder stores the reasoning trace"),
    (
        ("round 191: the recorder stores the reasoning trace", "zz"),
        "qntmc 191: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 191: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 191: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 191: the recorder stores the reasoning trace", "keyboard"),
        "bssor 191: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 191: the recorder stores the reasoning trace", "AA"),
        "round 191: the recorder stores the reasoning trace",
    ),
    (("round 191: the angel watches the processor run", "key"), "bssxh 191: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 191: the angel watches the processor run", "lemon"), "csgbq 191: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 191: the angel watches the processor run", "a"), "round 191: the angel watches the processor run"),
    (("round 191: the angel watches the processor run", "zz"), "qntmc 191: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 191: the angel watches the processor run", "AgentU"), "ruyaw 191: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 191: the angel watches the processor run", "keyboard"), "bssor 191: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 191: the angel watches the processor run", "AA"), "round 191: the angel watches the processor run"),
    (("round 191: angle of the vector decides the match", "key"), "bssxh 191: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 191: angle of the vector decides the match", "lemon"), "csgbq 191: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 191: angle of the vector decides the match", "a"), "round 191: angle of the vector decides the match"),
    (("round 191: angle of the vector decides the match", "zz"), "qntmc 191: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 191: angle of the vector decides the match", "AgentU"),
        "ruyaw 191: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 191: angle of the vector decides the match", "keyboard"),
        "bssor 191: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 191: angle of the vector decides the match", "AA"), "round 191: angle of the vector decides the match"),
    (
        ("round 191: the candle burns twice as long at night", "key"),
        "bssxh 191: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 191: the candle burns twice as long at night", "lemon"),
        "csgbq 191: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 191: the candle burns twice as long at night", "a"), "round 191: the candle burns twice as long at night"),
    (
        ("round 191: the candle burns twice as long at night", "zz"),
        "qntmc 191: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 191: the candle burns twice as long at night", "AgentU"),
        "ruyaw 191: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 191: the candle burns twice as long at night", "keyboard"),
        "bssor 191: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 191: the candle burns twice as long at night", "AA"),
        "round 191: the candle burns twice as long at night",
    ),
    (("round 191: a mirror of the universe in one line", "key"), "bssxh 191: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 191: a mirror of the universe in one line", "lemon"), "csgbq 191: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 191: a mirror of the universe in one line", "a"), "round 191: a mirror of the universe in one line"),
    (("round 191: a mirror of the universe in one line", "zz"), "qntmc 191: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 191: a mirror of the universe in one line", "AgentU"), "ruyaw 191: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 191: a mirror of the universe in one line", "keyboard"),
        "bssor 191: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 191: a mirror of the universe in one line", "AA"), "round 191: a mirror of the universe in one line"),
    (("round 191: the queue drains before the storm", "key"), "bssxh 191: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 191: the queue drains before the storm", "lemon"), "csgbq 191: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 191: the queue drains before the storm", "a"), "round 191: the queue drains before the storm"),
    (("round 191: the queue drains before the storm", "zz"), "qntmc 191: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 191: the queue drains before the storm", "AgentU"), "ruyaw 191: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 191: the queue drains before the storm", "keyboard"), "bssor 191: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 191: the queue drains before the storm", "AA"), "round 191: the queue drains before the storm"),
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
