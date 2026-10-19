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
    (("kitten159", "key"), "umrdil159"),
    (("kitten159", "lemon"), "vmfhry159"),
    (("kitten159", "a"), "kitten159"),
    (("kitten159", "zz"), "jhssdm159"),
    (("kitten159", "AgentU"), "koxgxh159"),
    (("kitten159", "keyboard"), "umrusn159"),
    (("kitten159", "AA"), "kitten159"),
    (("sitting159", "key"), "cmrdmlq159"),
    (("sitting159", "lemon"), "dmfhvyk159"),
    (("sitting159", "a"), "sitting159"),
    (("sitting159", "zz"), "rhsshmf159"),
    (("sitting159", "AgentU"), "soxgbhg159"),
    (("sitting159", "keyboard"), "cmruwnx159"),
    (("sitting159", "AA"), "sitting159"),
    (("agent159", "key"), "kkcxx159"),
    (("agent159", "lemon"), "lkqbg159"),
    (("agent159", "a"), "agent159"),
    (("agent159", "zz"), "zfdms159"),
    (("agent159", "AgentU"), "amiam159"),
    (("agent159", "keyboard"), "kkcoh159"),
    (("agent159", "AA"), "agent159"),
    (("angle159", "key"), "krevi159"),
    (("angle159", "lemon"), "lrszr159"),
    (("angle159", "a"), "angle159"),
    (("angle159", "zz"), "zmfkd159"),
    (("angle159", "AgentU"), "atkyx159"),
    (("angle159", "keyboard"), "krems159"),
    (("angle159", "AA"), "angle159"),
    (("universe159", "key"), "ergfipci159"),
    (("universe159", "lemon"), "frujrcwq159"),
    (("universe159", "a"), "universe159"),
    (("universe159", "zz"), "tmhudqrd159"),
    (("universe159", "AgentU"), "utmixlsk159"),
    (("universe159", "keyboard"), "ergwsrjh159"),
    (("universe159", "AA"), "universe159"),
    (("memory159", "key"), "wikyvw159"),
    (("memory159", "lemon"), "xiycej159"),
    (("memory159", "a"), "memory159"),
    (("memory159", "zz"), "ldlnqx159"),
    (("memory159", "AgentU"), "mkqbks159"),
    (("memory159", "keyboard"), "wikpfy159"),
    (("memory159", "AA"), "memory159"),
    (("stream159", "key"), "cxpoek159"),
    (("stream159", "lemon"), "dxdsnx159"),
    (("stream159", "a"), "stream159"),
    (("stream159", "zz"), "rsqdzl159"),
    (("stream159", "AgentU"), "szvrtg159"),
    (("stream159", "keyboard"), "cxpfom159"),
    (("stream159", "AA"), "stream159"),
    (("context159", "key"), "msldivd159"),
    (("context159", "lemon"), "nszhrix159"),
    (("context159", "a"), "context159"),
    (("context159", "zz"), "bnmsdws159"),
    (("context159", "AgentU"), "curgxrt159"),
    (("context159", "keyboard"), "mslusxk159"),
    (("context159", "AA"), "context159"),
    (("knowledge159", "key"), "urmgpcnkc159"),
    (("knowledge159", "lemon"), "vrakyphss159"),
    (("knowledge159", "a"), "knowledge159"),
    (("knowledge159", "zz"), "jmnvkdcfd159"),
    (("knowledge159", "AgentU"), "ktsjeydmi159"),
    (("knowledge159", "keyboard"), "urmxzeujo159"),
    (("knowledge159", "AA"), "knowledge159"),
    (("vector159", "key"), "fiadsp159"),
    (("vector159", "lemon"), "giohbc159"),
    (("vector159", "a"), "vector159"),
    (("vector159", "zz"), "udbsnq159"),
    (("vector159", "AgentU"), "vkgghl159"),
    (("vector159", "keyboard"), "fiaucr159"),
    (("vector159", "AA"), "vector159"),
    (("processor159", "key"), "zvmmiqcsp159"),
    (("processor159", "lemon"), "avaqrdwaf159"),
    (("processor159", "a"), "processor159"),
    (("processor159", "zz"), "oqnbdrrnq159"),
    (("processor159", "AgentU"), "pxspxmsuv159"),
    (("processor159", "keyboard"), "zvmdssjrb159"),
    (("processor159", "AA"), "processor159"),
    (("reasoning159", "key"), "biycslsre159"),
    (("reasoning159", "lemon"), "cimgbymzu159"),
    (("reasoning159", "a"), "reasoning159"),
    (("reasoning159", "zz"), "qdzrnmhmf159"),
    (("reasoning159", "AgentU"), "rkefhhitk159"),
    (("reasoning159", "keyboard"), "biytcnzqq159"),
    (("reasoning159", "AA"), "reasoning159"),
    (("machine159", "key"), "wearmlo159"),
    (("machine159", "lemon"), "xeovvyi159"),
    (("machine159", "a"), "machine159"),
    (("machine159", "zz"), "lzbghmd159"),
    (("machine159", "AgentU"), "mggubhe159"),
    (("machine159", "keyboard"), "weaiwnv159"),
    (("machine159", "AA"), "machine159"),
    (("learning159", "key"), "viybrgxk159"),
    (("learning159", "lemon"), "wimfatrs159"),
    (("learning159", "a"), "learning159"),
    (("learning159", "zz"), "kdzqmhmf159"),
    (("learning159", "AgentU"), "lkeegcnm159"),
    (("learning159", "keyboard"), "viysbiej159"),
    (("learning159", "AA"), "learning159"),
    (("model159", "key"), "wsbop159"),
    (("model159", "lemon"), "xspsy159"),
    (("model159", "a"), "model159"),
    (("model159", "zz"), "lncdk159"),
    (("model159", "AgentU"), "muhre159"),
    (("model159", "keyboard"), "wsbfz159"),
    (("model159", "AA"), "model159"),
    (("token159", "key"), "dsior159"),
    (("token159", "lemon"), "eswsa159"),
    (("token159", "a"), "token159"),
    (("token159", "zz"), "snjdm159"),
    (("token159", "AgentU"), "tuorg159"),
    (("token159", "keyboard"), "dsifb159"),
    (("token159", "AA"), "token159"),
    (("prompt159", "key"), "zvmwtr159"),
    (("prompt159", "lemon"), "avaace159"),
    (("prompt159", "a"), "prompt159"),
    (("prompt159", "zz"), "oqnlos159"),
    (("prompt159", "AgentU"), "pxszin159"),
    (("prompt159", "keyboard"), "zvmndt159"),
    (("prompt159", "AA"), "prompt159"),
    (("session159", "key"), "ciqcmmx159"),
    (("session159", "lemon"), "diegvzr159"),
    (("session159", "a"), "session159"),
    (("session159", "zz"), "rdrrhnm159"),
    (("session159", "AgentU"), "skwfbin159"),
    (("session159", "keyboard"), "ciqtwoe159"),
    (("session159", "AA"), "session159"),
    (("library159", "key"), "vmzbepi159"),
    (("library159", "lemon"), "wmnfncc159"),
    (("library159", "a"), "library159"),
    (("library159", "zz"), "khaqzqx159"),
    (("library159", "AgentU"), "lofetly159"),
    (("library159", "keyboard"), "vmzsorp159"),
    (("library159", "AA"), "library159"),
    (("service159", "key"), "cipfmao159"),
    (("service159", "lemon"), "didjvni159"),
    (("service159", "a"), "service159"),
    (("service159", "zz"), "rdquhbd159"),
    (("service159", "AgentU"), "skvibwe159"),
    (("service159", "keyboard"), "cipwwcv159"),
    (("service159", "AA"), "service159"),
    (("gateway159", "key"), "qeroayi159"),
    (("gateway159", "lemon"), "refsjlc159"),
    (("gateway159", "a"), "gateway159"),
    (("gateway159", "zz"), "fzsdvzx159"),
    (("gateway159", "AgentU"), "ggxrpuy159"),
    (("gateway159", "keyboard"), "qerfkap159"),
    (("gateway159", "AA"), "gateway159"),
    (("storage159", "key"), "cxmbeeo159"),
    (("storage159", "lemon"), "dxafnri159"),
    (("storage159", "a"), "storage159"),
    (("storage159", "zz"), "rsnqzfd159"),
    (("storage159", "AgentU"), "szsetae159"),
    (("storage159", "keyboard"), "cxmsogv159"),
    (("storage159", "AA"), "storage159"),
    (("network159", "key"), "xirgspu159"),
    (("network159", "lemon"), "yifkbco159"),
    (("network159", "a"), "network159"),
    (("network159", "zz"), "mdsvnqj159"),
    (("network159", "AgentU"), "nkxjhlk159"),
    (("network159", "keyboard"), "xirxcrb159"),
    (("network159", "AA"), "network159"),
    (("latency159", "key"), "verorai159"),
    (("latency159", "lemon"), "wefsanc159"),
    (("latency159", "a"), "latency159"),
    (("latency159", "zz"), "kzsdmbx159"),
    (("latency159", "AgentU"), "lgxrgwy159"),
    (("latency159", "keyboard"), "verfbcp159"),
    (("latency159", "AA"), "latency159"),
    (("buffer159", "key"), "lydpip159"),
    (("buffer159", "lemon"), "myrtrc159"),
    (("buffer159", "a"), "buffer159"),
    (("buffer159", "zz"), "ateedq159"),
    (("buffer159", "AgentU"), "bajsxl159"),
    (("buffer159", "keyboard"), "lydgsr159"),
    (("buffer159", "AA"), "buffer159"),
    (("queue159", "key"), "aycei159"),
    (("queue159", "lemon"), "byqir159"),
    (("queue159", "a"), "queue159"),
    (("queue159", "zz"), "ptdtd159"),
    (("queue159", "AgentU"), "qaihx159"),
    (("queue159", "keyboard"), "aycvs159"),
    (("queue159", "AA"), "queue159"),
    (("worker159", "key"), "gspuip159"),
    (("worker159", "lemon"), "hsdyrc159"),
    (("worker159", "a"), "worker159"),
    (("worker159", "zz"), "vnqjdq159"),
    (("worker159", "AgentU"), "wuvxxl159"),
    (("worker159", "keyboard"), "gsplsr159"),
    (("worker159", "AA"), "worker159"),
    (("kernel159", "key"), "uipxij159"),
    (("kernel159", "lemon"), "vidbrw159"),
    (("kernel159", "a"), "kernel159"),
    (("kernel159", "zz"), "jdqmdk159"),
    (("kernel159", "AgentU"), "kkvaxf159"),
    (("kernel159", "keyboard"), "uiposl159"),
    (("kernel159", "AA"), "kernel159"),
    (("signal159", "key"), "cmexej159"),
    (("signal159", "lemon"), "dmsbnw159"),
    (("signal159", "a"), "signal159"),
    (("signal159", "zz"), "rhfmzk159"),
    (("signal159", "AgentU"), "sokatf159"),
    (("signal159", "keyboard"), "cmeool159"),
    (("signal159", "AA"), "signal159"),
    (("packet159", "key"), "zeauir159"),
    (("packet159", "lemon"), "aeoyre159"),
    (("packet159", "a"), "packet159"),
    (("packet159", "zz"), "ozbjds159"),
    (("packet159", "AgentU"), "pggxxn159"),
    (("packet159", "keyboard"), "zealst159"),
    (("packet159", "AA"), "packet159"),
    (("router159", "key"), "bssdip159"),
    (("router159", "lemon"), "csghrc159"),
    (("router159", "a"), "router159"),
    (("router159", "zz"), "qntsdq159"),
    (("router159", "AgentU"), "ruygxl159"),
    (("router159", "keyboard"), "bssusr159"),
    (("router159", "AA"), "router159"),
    (("cluster159", "key"), "mpscxcb159"),
    (("cluster159", "lemon"), "npgggpv159"),
    (("cluster159", "a"), "cluster159"),
    (("cluster159", "zz"), "bktrsdq159"),
    (("cluster159", "AgentU"), "cryfmyr159"),
    (("cluster159", "keyboard"), "mpsthei159"),
    (("cluster159", "AA"), "cluster159"),
    (("mirror159", "key"), "wmpbsp159"),
    (("mirror159", "lemon"), "xmdfbc159"),
    (("mirror159", "a"), "mirror159"),
    (("mirror159", "zz"), "lhqqnq159"),
    (("mirror159", "AgentU"), "movehl159"),
    (("mirror159", "keyboard"), "wmpscr159"),
    (("mirror159", "AA"), "mirror159"),
    (("filter159", "key"), "pmjdip159"),
    (("filter159", "lemon"), "qmxhrc159"),
    (("filter159", "a"), "filter159"),
    (("filter159", "zz"), "ehksdq159"),
    (("filter159", "AgentU"), "fopgxl159"),
    (("filter159", "keyboard"), "pmjusr159"),
    (("filter159", "AA"), "filter159"),
    (("ranking159", "key"), "belumlq159"),
    (("ranking159", "lemon"), "cezyvyk159"),
    (("ranking159", "a"), "ranking159"),
    (("ranking159", "zz"), "qzmjhmf159"),
    (("ranking159", "AgentU"), "rgrxbhg159"),
    (("ranking159", "keyboard"), "bellwnx159"),
    (("ranking159", "AA"), "ranking159"),
    (("encoding159", "key"), "orayhgxk159"),
    (("encoding159", "lemon"), "procqtrs159"),
    (("encoding159", "a"), "encoding159"),
    (("encoding159", "zz"), "dmbnchmf159"),
    (("encoding159", "AgentU"), "etgbwcnm159"),
    (("encoding159", "keyboard"), "orapriej159"),
    (("encoding159", "AA"), "encoding159"),
    (("mapping159", "key"), "wenzmlq159"),
    (("mapping159", "lemon"), "xebdvyk159"),
    (("mapping159", "a"), "mapping159"),
    (("mapping159", "zz"), "lzoohmf159"),
    (("mapping159", "AgentU"), "mgtcbhg159"),
    (("mapping159", "keyboard"), "wenqwnx159"),
    (("mapping159", "AA"), "mapping159"),
    (("record159", "key"), "biayvb159"),
    (("record159", "lemon"), "cioceo159"),
    (("record159", "a"), "record159"),
    (("record159", "zz"), "qdbnqc159"),
    (("record159", "AgentU"), "rkgbkx159"),
    (("record159", "keyboard"), "biapfd159"),
    (("record159", "AA"), "record159"),
    (("candle159", "key"), "melnpc159"),
    (("candle159", "lemon"), "nezryp159"),
    (("candle159", "a"), "candle159"),
    (("candle159", "zz"), "bzmckd159"),
    (("candle159", "AgentU"), "cgrqey159"),
    (("candle159", "keyboard"), "meleze159"),
    (("candle159", "AA"), "candle159"),
    (("thread159", "key"), "dlpoeb159"),
    (("thread159", "lemon"), "eldsno159"),
    (("thread159", "a"), "thread159"),
    (("thread159", "zz"), "sgqdzc159"),
    (("thread159", "AgentU"), "tnvrtx159"),
    (("thread159", "keyboard"), "dlpfod159"),
    (("thread159", "AA"), "thread159"),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 159: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 159: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "a"),
        "round 159: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 159: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 159: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 159: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 159: the quick brown fox jumps over the lazy dog", "AA"),
        "round 159: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "key"),
        "bssxh 159: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 159: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "a"),
        "round 159: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 159: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 159: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 159: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 159: agentuniverse is a framework for multi agents", "AA"),
        "round 159: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 159: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 159: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "a"),
        "round 159: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 159: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 159: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 159: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 159: knowledge stored as vectors enables retrieval", "AA"),
        "round 159: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 159: the processor reads the record then stops", "key"),
        "bssxh 159: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 159: the processor reads the record then stops", "lemon"),
        "csgbq 159: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 159: the processor reads the record then stops", "a"),
        "round 159: the processor reads the record then stops",
    ),
    (
        ("round 159: the processor reads the record then stops", "zz"),
        "qntmc 159: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 159: the processor reads the record then stops", "AgentU"),
        "ruyaw 159: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 159: the processor reads the record then stops", "keyboard"),
        "bssor 159: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 159: the processor reads the record then stops", "AA"),
        "round 159: the processor reads the record then stops",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "key"),
        "bssxh 159: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "lemon"),
        "csgbq 159: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "a"),
        "round 159: a worker pulls the next task from the queue",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "zz"),
        "qntmc 159: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 159: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "keyboard"),
        "bssor 159: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 159: a worker pulls the next task from the queue", "AA"),
        "round 159: a worker pulls the next task from the queue",
    ),
    (
        ("round 159: signals travel through the network layer", "key"),
        "bssxh 159: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 159: signals travel through the network layer", "lemon"),
        "csgbq 159: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 159: signals travel through the network layer", "a"),
        "round 159: signals travel through the network layer",
    ),
    (
        ("round 159: signals travel through the network layer", "zz"),
        "qntmc 159: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 159: signals travel through the network layer", "AgentU"),
        "ruyaw 159: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 159: signals travel through the network layer", "keyboard"),
        "bssor 159: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 159: signals travel through the network layer", "AA"),
        "round 159: signals travel through the network layer",
    ),
    (
        ("round 159: the gateway routes each request by policy", "key"),
        "bssxh 159: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 159: the gateway routes each request by policy", "lemon"),
        "csgbq 159: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 159: the gateway routes each request by policy", "a"),
        "round 159: the gateway routes each request by policy",
    ),
    (
        ("round 159: the gateway routes each request by policy", "zz"),
        "qntmc 159: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 159: the gateway routes each request by policy", "AgentU"),
        "ruyaw 159: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 159: the gateway routes each request by policy", "keyboard"),
        "bssor 159: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 159: the gateway routes each request by policy", "AA"),
        "round 159: the gateway routes each request by policy",
    ),
    (("round 159: memory grows until the buffer is full", "key"), "bssxh 159: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 159: memory grows until the buffer is full", "lemon"), "csgbq 159: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 159: memory grows until the buffer is full", "a"), "round 159: memory grows until the buffer is full"),
    (("round 159: memory grows until the buffer is full", "zz"), "qntmc 159: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 159: memory grows until the buffer is full", "AgentU"),
        "ruyaw 159: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 159: memory grows until the buffer is full", "keyboard"),
        "bssor 159: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 159: memory grows until the buffer is full", "AA"), "round 159: memory grows until the buffer is full"),
    (("round 159: the cluster mirrors every packet twice", "key"), "bssxh 159: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 159: the cluster mirrors every packet twice", "lemon"),
        "csgbq 159: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 159: the cluster mirrors every packet twice", "a"), "round 159: the cluster mirrors every packet twice"),
    (("round 159: the cluster mirrors every packet twice", "zz"), "qntmc 159: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 159: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 159: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 159: the cluster mirrors every packet twice", "keyboard"),
        "bssor 159: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 159: the cluster mirrors every packet twice", "AA"), "round 159: the cluster mirrors every packet twice"),
    (
        ("round 159: ranking uses tokens learned from the corpus", "key"),
        "bssxh 159: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 159: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", "a"),
        "round 159: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 159: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 159: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 159: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 159: ranking uses tokens learned from the corpus", "AA"),
        "round 159: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 159: a long session ends when the candle dies", "key"),
        "bssxh 159: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 159: a long session ends when the candle dies", "lemon"),
        "csgbq 159: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 159: a long session ends when the candle dies", "a"),
        "round 159: a long session ends when the candle dies",
    ),
    (
        ("round 159: a long session ends when the candle dies", "zz"),
        "qntmc 159: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 159: a long session ends when the candle dies", "AgentU"),
        "ruyaw 159: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 159: a long session ends when the candle dies", "keyboard"),
        "bssor 159: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 159: a long session ends when the candle dies", "AA"),
        "round 159: a long session ends when the candle dies",
    ),
    (("round 159: encode the prompt then map the result", "key"), "bssxh 159: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 159: encode the prompt then map the result", "lemon"), "csgbq 159: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 159: encode the prompt then map the result", "a"), "round 159: encode the prompt then map the result"),
    (("round 159: encode the prompt then map the result", "zz"), "qntmc 159: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 159: encode the prompt then map the result", "AgentU"),
        "ruyaw 159: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 159: encode the prompt then map the result", "keyboard"),
        "bssor 159: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 159: encode the prompt then map the result", "AA"), "round 159: encode the prompt then map the result"),
    (("round 159: the kernel wakes the worker at dawn", "key"), "bssxh 159: rri iovlop ukocc xfo ambocb er neux"),
    (("round 159: the kernel wakes the worker at dawn", "lemon"), "csgbq 159: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 159: the kernel wakes the worker at dawn", "a"), "round 159: the kernel wakes the worker at dawn"),
    (("round 159: the kernel wakes the worker at dawn", "zz"), "qntmc 159: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 159: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 159: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 159: the kernel wakes the worker at dawn", "keyboard"), "bssor 159: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 159: the kernel wakes the worker at dawn", "AA"), "round 159: the kernel wakes the worker at dawn"),
    (("round 159: service latency drops after the patch", "key"), "bssxh 159: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 159: service latency drops after the patch", "lemon"), "csgbq 159: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 159: service latency drops after the patch", "a"), "round 159: service latency drops after the patch"),
    (("round 159: service latency drops after the patch", "zz"), "qntmc 159: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 159: service latency drops after the patch", "AgentU"),
        "ruyaw 159: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 159: service latency drops after the patch", "keyboard"),
        "bssor 159: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 159: service latency drops after the patch", "AA"), "round 159: service latency drops after the patch"),
    (
        ("round 159: the library caches every vector it sees", "key"),
        "bssxh 159: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 159: the library caches every vector it sees", "lemon"),
        "csgbq 159: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 159: the library caches every vector it sees", "a"), "round 159: the library caches every vector it sees"),
    (
        ("round 159: the library caches every vector it sees", "zz"),
        "qntmc 159: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 159: the library caches every vector it sees", "AgentU"),
        "ruyaw 159: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 159: the library caches every vector it sees", "keyboard"),
        "bssor 159: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 159: the library caches every vector it sees", "AA"),
        "round 159: the library caches every vector it sees",
    ),
    (("round 159: agents argue then the debate resolves", "key"), "bssxh 159: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 159: agents argue then the debate resolves", "lemon"), "csgbq 159: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 159: agents argue then the debate resolves", "a"), "round 159: agents argue then the debate resolves"),
    (("round 159: agents argue then the debate resolves", "zz"), "qntmc 159: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 159: agents argue then the debate resolves", "AgentU"),
        "ruyaw 159: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 159: agents argue then the debate resolves", "keyboard"),
        "bssor 159: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 159: agents argue then the debate resolves", "AA"), "round 159: agents argue then the debate resolves"),
    (("round 159: the filter keeps only strong matches", "key"), "bssxh 159: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 159: the filter keeps only strong matches", "lemon"), "csgbq 159: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 159: the filter keeps only strong matches", "a"), "round 159: the filter keeps only strong matches"),
    (("round 159: the filter keeps only strong matches", "zz"), "qntmc 159: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 159: the filter keeps only strong matches", "AgentU"), "ruyaw 159: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 159: the filter keeps only strong matches", "keyboard"),
        "bssor 159: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 159: the filter keeps only strong matches", "AA"), "round 159: the filter keeps only strong matches"),
    (("round 159: the model answers with a short reply", "key"), "bssxh 159: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 159: the model answers with a short reply", "lemon"), "csgbq 159: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 159: the model answers with a short reply", "a"), "round 159: the model answers with a short reply"),
    (("round 159: the model answers with a short reply", "zz"), "qntmc 159: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 159: the model answers with a short reply", "AgentU"), "ruyaw 159: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 159: the model answers with a short reply", "keyboard"),
        "bssor 159: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 159: the model answers with a short reply", "AA"), "round 159: the model answers with a short reply"),
    (
        ("round 159: the recorder stores the reasoning trace", "key"),
        "bssxh 159: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 159: the recorder stores the reasoning trace", "lemon"),
        "csgbq 159: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 159: the recorder stores the reasoning trace", "a"), "round 159: the recorder stores the reasoning trace"),
    (
        ("round 159: the recorder stores the reasoning trace", "zz"),
        "qntmc 159: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 159: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 159: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 159: the recorder stores the reasoning trace", "keyboard"),
        "bssor 159: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 159: the recorder stores the reasoning trace", "AA"),
        "round 159: the recorder stores the reasoning trace",
    ),
    (("round 159: the angel watches the processor run", "key"), "bssxh 159: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 159: the angel watches the processor run", "lemon"), "csgbq 159: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 159: the angel watches the processor run", "a"), "round 159: the angel watches the processor run"),
    (("round 159: the angel watches the processor run", "zz"), "qntmc 159: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 159: the angel watches the processor run", "AgentU"), "ruyaw 159: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 159: the angel watches the processor run", "keyboard"), "bssor 159: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 159: the angel watches the processor run", "AA"), "round 159: the angel watches the processor run"),
    (("round 159: angle of the vector decides the match", "key"), "bssxh 159: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 159: angle of the vector decides the match", "lemon"), "csgbq 159: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 159: angle of the vector decides the match", "a"), "round 159: angle of the vector decides the match"),
    (("round 159: angle of the vector decides the match", "zz"), "qntmc 159: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 159: angle of the vector decides the match", "AgentU"),
        "ruyaw 159: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 159: angle of the vector decides the match", "keyboard"),
        "bssor 159: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 159: angle of the vector decides the match", "AA"), "round 159: angle of the vector decides the match"),
    (
        ("round 159: the candle burns twice as long at night", "key"),
        "bssxh 159: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 159: the candle burns twice as long at night", "lemon"),
        "csgbq 159: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 159: the candle burns twice as long at night", "a"), "round 159: the candle burns twice as long at night"),
    (
        ("round 159: the candle burns twice as long at night", "zz"),
        "qntmc 159: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 159: the candle burns twice as long at night", "AgentU"),
        "ruyaw 159: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 159: the candle burns twice as long at night", "keyboard"),
        "bssor 159: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 159: the candle burns twice as long at night", "AA"),
        "round 159: the candle burns twice as long at night",
    ),
    (("round 159: a mirror of the universe in one line", "key"), "bssxh 159: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 159: a mirror of the universe in one line", "lemon"), "csgbq 159: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 159: a mirror of the universe in one line", "a"), "round 159: a mirror of the universe in one line"),
    (("round 159: a mirror of the universe in one line", "zz"), "qntmc 159: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 159: a mirror of the universe in one line", "AgentU"), "ruyaw 159: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 159: a mirror of the universe in one line", "keyboard"),
        "bssor 159: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 159: a mirror of the universe in one line", "AA"), "round 159: a mirror of the universe in one line"),
    (("round 159: the queue drains before the storm", "key"), "bssxh 159: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 159: the queue drains before the storm", "lemon"), "csgbq 159: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 159: the queue drains before the storm", "a"), "round 159: the queue drains before the storm"),
    (("round 159: the queue drains before the storm", "zz"), "qntmc 159: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 159: the queue drains before the storm", "AgentU"), "ruyaw 159: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 159: the queue drains before the storm", "keyboard"), "bssor 159: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 159: the queue drains before the storm", "AA"), "round 159: the queue drains before the storm"),
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
