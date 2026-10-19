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
    (("kitten731", "key"), "umrdil731"),
    (("kitten731", "lemon"), "vmfhry731"),
    (("kitten731", "a"), "kitten731"),
    (("kitten731", "zz"), "jhssdm731"),
    (("kitten731", "AgentU"), "koxgxh731"),
    (("kitten731", "keyboard"), "umrusn731"),
    (("kitten731", "AA"), "kitten731"),
    (("sitting731", "key"), "cmrdmlq731"),
    (("sitting731", "lemon"), "dmfhvyk731"),
    (("sitting731", "a"), "sitting731"),
    (("sitting731", "zz"), "rhsshmf731"),
    (("sitting731", "AgentU"), "soxgbhg731"),
    (("sitting731", "keyboard"), "cmruwnx731"),
    (("sitting731", "AA"), "sitting731"),
    (("agent731", "key"), "kkcxx731"),
    (("agent731", "lemon"), "lkqbg731"),
    (("agent731", "a"), "agent731"),
    (("agent731", "zz"), "zfdms731"),
    (("agent731", "AgentU"), "amiam731"),
    (("agent731", "keyboard"), "kkcoh731"),
    (("agent731", "AA"), "agent731"),
    (("angle731", "key"), "krevi731"),
    (("angle731", "lemon"), "lrszr731"),
    (("angle731", "a"), "angle731"),
    (("angle731", "zz"), "zmfkd731"),
    (("angle731", "AgentU"), "atkyx731"),
    (("angle731", "keyboard"), "krems731"),
    (("angle731", "AA"), "angle731"),
    (("universe731", "key"), "ergfipci731"),
    (("universe731", "lemon"), "frujrcwq731"),
    (("universe731", "a"), "universe731"),
    (("universe731", "zz"), "tmhudqrd731"),
    (("universe731", "AgentU"), "utmixlsk731"),
    (("universe731", "keyboard"), "ergwsrjh731"),
    (("universe731", "AA"), "universe731"),
    (("memory731", "key"), "wikyvw731"),
    (("memory731", "lemon"), "xiycej731"),
    (("memory731", "a"), "memory731"),
    (("memory731", "zz"), "ldlnqx731"),
    (("memory731", "AgentU"), "mkqbks731"),
    (("memory731", "keyboard"), "wikpfy731"),
    (("memory731", "AA"), "memory731"),
    (("stream731", "key"), "cxpoek731"),
    (("stream731", "lemon"), "dxdsnx731"),
    (("stream731", "a"), "stream731"),
    (("stream731", "zz"), "rsqdzl731"),
    (("stream731", "AgentU"), "szvrtg731"),
    (("stream731", "keyboard"), "cxpfom731"),
    (("stream731", "AA"), "stream731"),
    (("context731", "key"), "msldivd731"),
    (("context731", "lemon"), "nszhrix731"),
    (("context731", "a"), "context731"),
    (("context731", "zz"), "bnmsdws731"),
    (("context731", "AgentU"), "curgxrt731"),
    (("context731", "keyboard"), "mslusxk731"),
    (("context731", "AA"), "context731"),
    (("knowledge731", "key"), "urmgpcnkc731"),
    (("knowledge731", "lemon"), "vrakyphss731"),
    (("knowledge731", "a"), "knowledge731"),
    (("knowledge731", "zz"), "jmnvkdcfd731"),
    (("knowledge731", "AgentU"), "ktsjeydmi731"),
    (("knowledge731", "keyboard"), "urmxzeujo731"),
    (("knowledge731", "AA"), "knowledge731"),
    (("vector731", "key"), "fiadsp731"),
    (("vector731", "lemon"), "giohbc731"),
    (("vector731", "a"), "vector731"),
    (("vector731", "zz"), "udbsnq731"),
    (("vector731", "AgentU"), "vkgghl731"),
    (("vector731", "keyboard"), "fiaucr731"),
    (("vector731", "AA"), "vector731"),
    (("processor731", "key"), "zvmmiqcsp731"),
    (("processor731", "lemon"), "avaqrdwaf731"),
    (("processor731", "a"), "processor731"),
    (("processor731", "zz"), "oqnbdrrnq731"),
    (("processor731", "AgentU"), "pxspxmsuv731"),
    (("processor731", "keyboard"), "zvmdssjrb731"),
    (("processor731", "AA"), "processor731"),
    (("reasoning731", "key"), "biycslsre731"),
    (("reasoning731", "lemon"), "cimgbymzu731"),
    (("reasoning731", "a"), "reasoning731"),
    (("reasoning731", "zz"), "qdzrnmhmf731"),
    (("reasoning731", "AgentU"), "rkefhhitk731"),
    (("reasoning731", "keyboard"), "biytcnzqq731"),
    (("reasoning731", "AA"), "reasoning731"),
    (("machine731", "key"), "wearmlo731"),
    (("machine731", "lemon"), "xeovvyi731"),
    (("machine731", "a"), "machine731"),
    (("machine731", "zz"), "lzbghmd731"),
    (("machine731", "AgentU"), "mggubhe731"),
    (("machine731", "keyboard"), "weaiwnv731"),
    (("machine731", "AA"), "machine731"),
    (("learning731", "key"), "viybrgxk731"),
    (("learning731", "lemon"), "wimfatrs731"),
    (("learning731", "a"), "learning731"),
    (("learning731", "zz"), "kdzqmhmf731"),
    (("learning731", "AgentU"), "lkeegcnm731"),
    (("learning731", "keyboard"), "viysbiej731"),
    (("learning731", "AA"), "learning731"),
    (("model731", "key"), "wsbop731"),
    (("model731", "lemon"), "xspsy731"),
    (("model731", "a"), "model731"),
    (("model731", "zz"), "lncdk731"),
    (("model731", "AgentU"), "muhre731"),
    (("model731", "keyboard"), "wsbfz731"),
    (("model731", "AA"), "model731"),
    (("token731", "key"), "dsior731"),
    (("token731", "lemon"), "eswsa731"),
    (("token731", "a"), "token731"),
    (("token731", "zz"), "snjdm731"),
    (("token731", "AgentU"), "tuorg731"),
    (("token731", "keyboard"), "dsifb731"),
    (("token731", "AA"), "token731"),
    (("prompt731", "key"), "zvmwtr731"),
    (("prompt731", "lemon"), "avaace731"),
    (("prompt731", "a"), "prompt731"),
    (("prompt731", "zz"), "oqnlos731"),
    (("prompt731", "AgentU"), "pxszin731"),
    (("prompt731", "keyboard"), "zvmndt731"),
    (("prompt731", "AA"), "prompt731"),
    (("session731", "key"), "ciqcmmx731"),
    (("session731", "lemon"), "diegvzr731"),
    (("session731", "a"), "session731"),
    (("session731", "zz"), "rdrrhnm731"),
    (("session731", "AgentU"), "skwfbin731"),
    (("session731", "keyboard"), "ciqtwoe731"),
    (("session731", "AA"), "session731"),
    (("library731", "key"), "vmzbepi731"),
    (("library731", "lemon"), "wmnfncc731"),
    (("library731", "a"), "library731"),
    (("library731", "zz"), "khaqzqx731"),
    (("library731", "AgentU"), "lofetly731"),
    (("library731", "keyboard"), "vmzsorp731"),
    (("library731", "AA"), "library731"),
    (("service731", "key"), "cipfmao731"),
    (("service731", "lemon"), "didjvni731"),
    (("service731", "a"), "service731"),
    (("service731", "zz"), "rdquhbd731"),
    (("service731", "AgentU"), "skvibwe731"),
    (("service731", "keyboard"), "cipwwcv731"),
    (("service731", "AA"), "service731"),
    (("gateway731", "key"), "qeroayi731"),
    (("gateway731", "lemon"), "refsjlc731"),
    (("gateway731", "a"), "gateway731"),
    (("gateway731", "zz"), "fzsdvzx731"),
    (("gateway731", "AgentU"), "ggxrpuy731"),
    (("gateway731", "keyboard"), "qerfkap731"),
    (("gateway731", "AA"), "gateway731"),
    (("storage731", "key"), "cxmbeeo731"),
    (("storage731", "lemon"), "dxafnri731"),
    (("storage731", "a"), "storage731"),
    (("storage731", "zz"), "rsnqzfd731"),
    (("storage731", "AgentU"), "szsetae731"),
    (("storage731", "keyboard"), "cxmsogv731"),
    (("storage731", "AA"), "storage731"),
    (("network731", "key"), "xirgspu731"),
    (("network731", "lemon"), "yifkbco731"),
    (("network731", "a"), "network731"),
    (("network731", "zz"), "mdsvnqj731"),
    (("network731", "AgentU"), "nkxjhlk731"),
    (("network731", "keyboard"), "xirxcrb731"),
    (("network731", "AA"), "network731"),
    (("latency731", "key"), "verorai731"),
    (("latency731", "lemon"), "wefsanc731"),
    (("latency731", "a"), "latency731"),
    (("latency731", "zz"), "kzsdmbx731"),
    (("latency731", "AgentU"), "lgxrgwy731"),
    (("latency731", "keyboard"), "verfbcp731"),
    (("latency731", "AA"), "latency731"),
    (("buffer731", "key"), "lydpip731"),
    (("buffer731", "lemon"), "myrtrc731"),
    (("buffer731", "a"), "buffer731"),
    (("buffer731", "zz"), "ateedq731"),
    (("buffer731", "AgentU"), "bajsxl731"),
    (("buffer731", "keyboard"), "lydgsr731"),
    (("buffer731", "AA"), "buffer731"),
    (("queue731", "key"), "aycei731"),
    (("queue731", "lemon"), "byqir731"),
    (("queue731", "a"), "queue731"),
    (("queue731", "zz"), "ptdtd731"),
    (("queue731", "AgentU"), "qaihx731"),
    (("queue731", "keyboard"), "aycvs731"),
    (("queue731", "AA"), "queue731"),
    (("worker731", "key"), "gspuip731"),
    (("worker731", "lemon"), "hsdyrc731"),
    (("worker731", "a"), "worker731"),
    (("worker731", "zz"), "vnqjdq731"),
    (("worker731", "AgentU"), "wuvxxl731"),
    (("worker731", "keyboard"), "gsplsr731"),
    (("worker731", "AA"), "worker731"),
    (("kernel731", "key"), "uipxij731"),
    (("kernel731", "lemon"), "vidbrw731"),
    (("kernel731", "a"), "kernel731"),
    (("kernel731", "zz"), "jdqmdk731"),
    (("kernel731", "AgentU"), "kkvaxf731"),
    (("kernel731", "keyboard"), "uiposl731"),
    (("kernel731", "AA"), "kernel731"),
    (("signal731", "key"), "cmexej731"),
    (("signal731", "lemon"), "dmsbnw731"),
    (("signal731", "a"), "signal731"),
    (("signal731", "zz"), "rhfmzk731"),
    (("signal731", "AgentU"), "sokatf731"),
    (("signal731", "keyboard"), "cmeool731"),
    (("signal731", "AA"), "signal731"),
    (("packet731", "key"), "zeauir731"),
    (("packet731", "lemon"), "aeoyre731"),
    (("packet731", "a"), "packet731"),
    (("packet731", "zz"), "ozbjds731"),
    (("packet731", "AgentU"), "pggxxn731"),
    (("packet731", "keyboard"), "zealst731"),
    (("packet731", "AA"), "packet731"),
    (("router731", "key"), "bssdip731"),
    (("router731", "lemon"), "csghrc731"),
    (("router731", "a"), "router731"),
    (("router731", "zz"), "qntsdq731"),
    (("router731", "AgentU"), "ruygxl731"),
    (("router731", "keyboard"), "bssusr731"),
    (("router731", "AA"), "router731"),
    (("cluster731", "key"), "mpscxcb731"),
    (("cluster731", "lemon"), "npgggpv731"),
    (("cluster731", "a"), "cluster731"),
    (("cluster731", "zz"), "bktrsdq731"),
    (("cluster731", "AgentU"), "cryfmyr731"),
    (("cluster731", "keyboard"), "mpsthei731"),
    (("cluster731", "AA"), "cluster731"),
    (("mirror731", "key"), "wmpbsp731"),
    (("mirror731", "lemon"), "xmdfbc731"),
    (("mirror731", "a"), "mirror731"),
    (("mirror731", "zz"), "lhqqnq731"),
    (("mirror731", "AgentU"), "movehl731"),
    (("mirror731", "keyboard"), "wmpscr731"),
    (("mirror731", "AA"), "mirror731"),
    (("filter731", "key"), "pmjdip731"),
    (("filter731", "lemon"), "qmxhrc731"),
    (("filter731", "a"), "filter731"),
    (("filter731", "zz"), "ehksdq731"),
    (("filter731", "AgentU"), "fopgxl731"),
    (("filter731", "keyboard"), "pmjusr731"),
    (("filter731", "AA"), "filter731"),
    (("ranking731", "key"), "belumlq731"),
    (("ranking731", "lemon"), "cezyvyk731"),
    (("ranking731", "a"), "ranking731"),
    (("ranking731", "zz"), "qzmjhmf731"),
    (("ranking731", "AgentU"), "rgrxbhg731"),
    (("ranking731", "keyboard"), "bellwnx731"),
    (("ranking731", "AA"), "ranking731"),
    (("encoding731", "key"), "orayhgxk731"),
    (("encoding731", "lemon"), "procqtrs731"),
    (("encoding731", "a"), "encoding731"),
    (("encoding731", "zz"), "dmbnchmf731"),
    (("encoding731", "AgentU"), "etgbwcnm731"),
    (("encoding731", "keyboard"), "orapriej731"),
    (("encoding731", "AA"), "encoding731"),
    (("mapping731", "key"), "wenzmlq731"),
    (("mapping731", "lemon"), "xebdvyk731"),
    (("mapping731", "a"), "mapping731"),
    (("mapping731", "zz"), "lzoohmf731"),
    (("mapping731", "AgentU"), "mgtcbhg731"),
    (("mapping731", "keyboard"), "wenqwnx731"),
    (("mapping731", "AA"), "mapping731"),
    (("record731", "key"), "biayvb731"),
    (("record731", "lemon"), "cioceo731"),
    (("record731", "a"), "record731"),
    (("record731", "zz"), "qdbnqc731"),
    (("record731", "AgentU"), "rkgbkx731"),
    (("record731", "keyboard"), "biapfd731"),
    (("record731", "AA"), "record731"),
    (("candle731", "key"), "melnpc731"),
    (("candle731", "lemon"), "nezryp731"),
    (("candle731", "a"), "candle731"),
    (("candle731", "zz"), "bzmckd731"),
    (("candle731", "AgentU"), "cgrqey731"),
    (("candle731", "keyboard"), "meleze731"),
    (("candle731", "AA"), "candle731"),
    (("thread731", "key"), "dlpoeb731"),
    (("thread731", "lemon"), "eldsno731"),
    (("thread731", "a"), "thread731"),
    (("thread731", "zz"), "sgqdzc731"),
    (("thread731", "AgentU"), "tnvrtx731"),
    (("thread731", "keyboard"), "dlpfod731"),
    (("thread731", "AA"), "thread731"),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 731: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 731: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "a"),
        "round 731: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 731: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 731: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 731: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 731: the quick brown fox jumps over the lazy dog", "AA"),
        "round 731: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "key"),
        "bssxh 731: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 731: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "a"),
        "round 731: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 731: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 731: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 731: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 731: agentuniverse is a framework for multi agents", "AA"),
        "round 731: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 731: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 731: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "a"),
        "round 731: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 731: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 731: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 731: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 731: knowledge stored as vectors enables retrieval", "AA"),
        "round 731: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 731: the processor reads the record then stops", "key"),
        "bssxh 731: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 731: the processor reads the record then stops", "lemon"),
        "csgbq 731: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 731: the processor reads the record then stops", "a"),
        "round 731: the processor reads the record then stops",
    ),
    (
        ("round 731: the processor reads the record then stops", "zz"),
        "qntmc 731: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 731: the processor reads the record then stops", "AgentU"),
        "ruyaw 731: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 731: the processor reads the record then stops", "keyboard"),
        "bssor 731: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 731: the processor reads the record then stops", "AA"),
        "round 731: the processor reads the record then stops",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "key"),
        "bssxh 731: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "lemon"),
        "csgbq 731: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "a"),
        "round 731: a worker pulls the next task from the queue",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "zz"),
        "qntmc 731: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 731: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "keyboard"),
        "bssor 731: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 731: a worker pulls the next task from the queue", "AA"),
        "round 731: a worker pulls the next task from the queue",
    ),
    (
        ("round 731: signals travel through the network layer", "key"),
        "bssxh 731: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 731: signals travel through the network layer", "lemon"),
        "csgbq 731: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 731: signals travel through the network layer", "a"),
        "round 731: signals travel through the network layer",
    ),
    (
        ("round 731: signals travel through the network layer", "zz"),
        "qntmc 731: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 731: signals travel through the network layer", "AgentU"),
        "ruyaw 731: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 731: signals travel through the network layer", "keyboard"),
        "bssor 731: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 731: signals travel through the network layer", "AA"),
        "round 731: signals travel through the network layer",
    ),
    (
        ("round 731: the gateway routes each request by policy", "key"),
        "bssxh 731: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 731: the gateway routes each request by policy", "lemon"),
        "csgbq 731: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 731: the gateway routes each request by policy", "a"),
        "round 731: the gateway routes each request by policy",
    ),
    (
        ("round 731: the gateway routes each request by policy", "zz"),
        "qntmc 731: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 731: the gateway routes each request by policy", "AgentU"),
        "ruyaw 731: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 731: the gateway routes each request by policy", "keyboard"),
        "bssor 731: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 731: the gateway routes each request by policy", "AA"),
        "round 731: the gateway routes each request by policy",
    ),
    (("round 731: memory grows until the buffer is full", "key"), "bssxh 731: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 731: memory grows until the buffer is full", "lemon"), "csgbq 731: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 731: memory grows until the buffer is full", "a"), "round 731: memory grows until the buffer is full"),
    (("round 731: memory grows until the buffer is full", "zz"), "qntmc 731: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 731: memory grows until the buffer is full", "AgentU"),
        "ruyaw 731: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 731: memory grows until the buffer is full", "keyboard"),
        "bssor 731: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 731: memory grows until the buffer is full", "AA"), "round 731: memory grows until the buffer is full"),
    (("round 731: the cluster mirrors every packet twice", "key"), "bssxh 731: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 731: the cluster mirrors every packet twice", "lemon"),
        "csgbq 731: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 731: the cluster mirrors every packet twice", "a"), "round 731: the cluster mirrors every packet twice"),
    (("round 731: the cluster mirrors every packet twice", "zz"), "qntmc 731: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 731: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 731: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 731: the cluster mirrors every packet twice", "keyboard"),
        "bssor 731: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 731: the cluster mirrors every packet twice", "AA"), "round 731: the cluster mirrors every packet twice"),
    (
        ("round 731: ranking uses tokens learned from the corpus", "key"),
        "bssxh 731: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 731: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", "a"),
        "round 731: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 731: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 731: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 731: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 731: ranking uses tokens learned from the corpus", "AA"),
        "round 731: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 731: a long session ends when the candle dies", "key"),
        "bssxh 731: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 731: a long session ends when the candle dies", "lemon"),
        "csgbq 731: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 731: a long session ends when the candle dies", "a"),
        "round 731: a long session ends when the candle dies",
    ),
    (
        ("round 731: a long session ends when the candle dies", "zz"),
        "qntmc 731: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 731: a long session ends when the candle dies", "AgentU"),
        "ruyaw 731: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 731: a long session ends when the candle dies", "keyboard"),
        "bssor 731: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 731: a long session ends when the candle dies", "AA"),
        "round 731: a long session ends when the candle dies",
    ),
    (("round 731: encode the prompt then map the result", "key"), "bssxh 731: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 731: encode the prompt then map the result", "lemon"), "csgbq 731: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 731: encode the prompt then map the result", "a"), "round 731: encode the prompt then map the result"),
    (("round 731: encode the prompt then map the result", "zz"), "qntmc 731: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 731: encode the prompt then map the result", "AgentU"),
        "ruyaw 731: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 731: encode the prompt then map the result", "keyboard"),
        "bssor 731: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 731: encode the prompt then map the result", "AA"), "round 731: encode the prompt then map the result"),
    (("round 731: the kernel wakes the worker at dawn", "key"), "bssxh 731: rri iovlop ukocc xfo ambocb er neux"),
    (("round 731: the kernel wakes the worker at dawn", "lemon"), "csgbq 731: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 731: the kernel wakes the worker at dawn", "a"), "round 731: the kernel wakes the worker at dawn"),
    (("round 731: the kernel wakes the worker at dawn", "zz"), "qntmc 731: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 731: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 731: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 731: the kernel wakes the worker at dawn", "keyboard"), "bssor 731: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 731: the kernel wakes the worker at dawn", "AA"), "round 731: the kernel wakes the worker at dawn"),
    (("round 731: service latency drops after the patch", "key"), "bssxh 731: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 731: service latency drops after the patch", "lemon"), "csgbq 731: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 731: service latency drops after the patch", "a"), "round 731: service latency drops after the patch"),
    (("round 731: service latency drops after the patch", "zz"), "qntmc 731: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 731: service latency drops after the patch", "AgentU"),
        "ruyaw 731: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 731: service latency drops after the patch", "keyboard"),
        "bssor 731: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 731: service latency drops after the patch", "AA"), "round 731: service latency drops after the patch"),
    (
        ("round 731: the library caches every vector it sees", "key"),
        "bssxh 731: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 731: the library caches every vector it sees", "lemon"),
        "csgbq 731: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 731: the library caches every vector it sees", "a"), "round 731: the library caches every vector it sees"),
    (
        ("round 731: the library caches every vector it sees", "zz"),
        "qntmc 731: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 731: the library caches every vector it sees", "AgentU"),
        "ruyaw 731: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 731: the library caches every vector it sees", "keyboard"),
        "bssor 731: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 731: the library caches every vector it sees", "AA"),
        "round 731: the library caches every vector it sees",
    ),
    (("round 731: agents argue then the debate resolves", "key"), "bssxh 731: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 731: agents argue then the debate resolves", "lemon"), "csgbq 731: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 731: agents argue then the debate resolves", "a"), "round 731: agents argue then the debate resolves"),
    (("round 731: agents argue then the debate resolves", "zz"), "qntmc 731: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 731: agents argue then the debate resolves", "AgentU"),
        "ruyaw 731: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 731: agents argue then the debate resolves", "keyboard"),
        "bssor 731: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 731: agents argue then the debate resolves", "AA"), "round 731: agents argue then the debate resolves"),
    (("round 731: the filter keeps only strong matches", "key"), "bssxh 731: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 731: the filter keeps only strong matches", "lemon"), "csgbq 731: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 731: the filter keeps only strong matches", "a"), "round 731: the filter keeps only strong matches"),
    (("round 731: the filter keeps only strong matches", "zz"), "qntmc 731: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 731: the filter keeps only strong matches", "AgentU"), "ruyaw 731: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 731: the filter keeps only strong matches", "keyboard"),
        "bssor 731: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 731: the filter keeps only strong matches", "AA"), "round 731: the filter keeps only strong matches"),
    (("round 731: the model answers with a short reply", "key"), "bssxh 731: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 731: the model answers with a short reply", "lemon"), "csgbq 731: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 731: the model answers with a short reply", "a"), "round 731: the model answers with a short reply"),
    (("round 731: the model answers with a short reply", "zz"), "qntmc 731: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 731: the model answers with a short reply", "AgentU"), "ruyaw 731: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 731: the model answers with a short reply", "keyboard"),
        "bssor 731: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 731: the model answers with a short reply", "AA"), "round 731: the model answers with a short reply"),
    (
        ("round 731: the recorder stores the reasoning trace", "key"),
        "bssxh 731: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 731: the recorder stores the reasoning trace", "lemon"),
        "csgbq 731: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 731: the recorder stores the reasoning trace", "a"), "round 731: the recorder stores the reasoning trace"),
    (
        ("round 731: the recorder stores the reasoning trace", "zz"),
        "qntmc 731: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 731: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 731: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 731: the recorder stores the reasoning trace", "keyboard"),
        "bssor 731: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 731: the recorder stores the reasoning trace", "AA"),
        "round 731: the recorder stores the reasoning trace",
    ),
    (("round 731: the angel watches the processor run", "key"), "bssxh 731: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 731: the angel watches the processor run", "lemon"), "csgbq 731: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 731: the angel watches the processor run", "a"), "round 731: the angel watches the processor run"),
    (("round 731: the angel watches the processor run", "zz"), "qntmc 731: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 731: the angel watches the processor run", "AgentU"), "ruyaw 731: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 731: the angel watches the processor run", "keyboard"), "bssor 731: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 731: the angel watches the processor run", "AA"), "round 731: the angel watches the processor run"),
    (("round 731: angle of the vector decides the match", "key"), "bssxh 731: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 731: angle of the vector decides the match", "lemon"), "csgbq 731: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 731: angle of the vector decides the match", "a"), "round 731: angle of the vector decides the match"),
    (("round 731: angle of the vector decides the match", "zz"), "qntmc 731: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 731: angle of the vector decides the match", "AgentU"),
        "ruyaw 731: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 731: angle of the vector decides the match", "keyboard"),
        "bssor 731: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 731: angle of the vector decides the match", "AA"), "round 731: angle of the vector decides the match"),
    (
        ("round 731: the candle burns twice as long at night", "key"),
        "bssxh 731: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 731: the candle burns twice as long at night", "lemon"),
        "csgbq 731: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 731: the candle burns twice as long at night", "a"), "round 731: the candle burns twice as long at night"),
    (
        ("round 731: the candle burns twice as long at night", "zz"),
        "qntmc 731: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 731: the candle burns twice as long at night", "AgentU"),
        "ruyaw 731: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 731: the candle burns twice as long at night", "keyboard"),
        "bssor 731: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 731: the candle burns twice as long at night", "AA"),
        "round 731: the candle burns twice as long at night",
    ),
    (("round 731: a mirror of the universe in one line", "key"), "bssxh 731: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 731: a mirror of the universe in one line", "lemon"), "csgbq 731: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 731: a mirror of the universe in one line", "a"), "round 731: a mirror of the universe in one line"),
    (("round 731: a mirror of the universe in one line", "zz"), "qntmc 731: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 731: a mirror of the universe in one line", "AgentU"), "ruyaw 731: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 731: a mirror of the universe in one line", "keyboard"),
        "bssor 731: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 731: a mirror of the universe in one line", "AA"), "round 731: a mirror of the universe in one line"),
    (("round 731: the queue drains before the storm", "key"), "bssxh 731: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 731: the queue drains before the storm", "lemon"), "csgbq 731: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 731: the queue drains before the storm", "a"), "round 731: the queue drains before the storm"),
    (("round 731: the queue drains before the storm", "zz"), "qntmc 731: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 731: the queue drains before the storm", "AgentU"), "ruyaw 731: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 731: the queue drains before the storm", "keyboard"), "bssor 731: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 731: the queue drains before the storm", "AA"), "round 731: the queue drains before the storm"),
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
