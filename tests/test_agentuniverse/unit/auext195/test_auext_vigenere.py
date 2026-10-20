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
    (("kitten195", "key"), "umrdil195"),
    (("kitten195", "lemon"), "vmfhry195"),
    (("kitten195", "a"), "kitten195"),
    (("kitten195", "zz"), "jhssdm195"),
    (("kitten195", "AgentU"), "koxgxh195"),
    (("kitten195", "keyboard"), "umrusn195"),
    (("kitten195", "AA"), "kitten195"),
    (("sitting195", "key"), "cmrdmlq195"),
    (("sitting195", "lemon"), "dmfhvyk195"),
    (("sitting195", "a"), "sitting195"),
    (("sitting195", "zz"), "rhsshmf195"),
    (("sitting195", "AgentU"), "soxgbhg195"),
    (("sitting195", "keyboard"), "cmruwnx195"),
    (("sitting195", "AA"), "sitting195"),
    (("agent195", "key"), "kkcxx195"),
    (("agent195", "lemon"), "lkqbg195"),
    (("agent195", "a"), "agent195"),
    (("agent195", "zz"), "zfdms195"),
    (("agent195", "AgentU"), "amiam195"),
    (("agent195", "keyboard"), "kkcoh195"),
    (("agent195", "AA"), "agent195"),
    (("angle195", "key"), "krevi195"),
    (("angle195", "lemon"), "lrszr195"),
    (("angle195", "a"), "angle195"),
    (("angle195", "zz"), "zmfkd195"),
    (("angle195", "AgentU"), "atkyx195"),
    (("angle195", "keyboard"), "krems195"),
    (("angle195", "AA"), "angle195"),
    (("universe195", "key"), "ergfipci195"),
    (("universe195", "lemon"), "frujrcwq195"),
    (("universe195", "a"), "universe195"),
    (("universe195", "zz"), "tmhudqrd195"),
    (("universe195", "AgentU"), "utmixlsk195"),
    (("universe195", "keyboard"), "ergwsrjh195"),
    (("universe195", "AA"), "universe195"),
    (("memory195", "key"), "wikyvw195"),
    (("memory195", "lemon"), "xiycej195"),
    (("memory195", "a"), "memory195"),
    (("memory195", "zz"), "ldlnqx195"),
    (("memory195", "AgentU"), "mkqbks195"),
    (("memory195", "keyboard"), "wikpfy195"),
    (("memory195", "AA"), "memory195"),
    (("stream195", "key"), "cxpoek195"),
    (("stream195", "lemon"), "dxdsnx195"),
    (("stream195", "a"), "stream195"),
    (("stream195", "zz"), "rsqdzl195"),
    (("stream195", "AgentU"), "szvrtg195"),
    (("stream195", "keyboard"), "cxpfom195"),
    (("stream195", "AA"), "stream195"),
    (("context195", "key"), "msldivd195"),
    (("context195", "lemon"), "nszhrix195"),
    (("context195", "a"), "context195"),
    (("context195", "zz"), "bnmsdws195"),
    (("context195", "AgentU"), "curgxrt195"),
    (("context195", "keyboard"), "mslusxk195"),
    (("context195", "AA"), "context195"),
    (("knowledge195", "key"), "urmgpcnkc195"),
    (("knowledge195", "lemon"), "vrakyphss195"),
    (("knowledge195", "a"), "knowledge195"),
    (("knowledge195", "zz"), "jmnvkdcfd195"),
    (("knowledge195", "AgentU"), "ktsjeydmi195"),
    (("knowledge195", "keyboard"), "urmxzeujo195"),
    (("knowledge195", "AA"), "knowledge195"),
    (("vector195", "key"), "fiadsp195"),
    (("vector195", "lemon"), "giohbc195"),
    (("vector195", "a"), "vector195"),
    (("vector195", "zz"), "udbsnq195"),
    (("vector195", "AgentU"), "vkgghl195"),
    (("vector195", "keyboard"), "fiaucr195"),
    (("vector195", "AA"), "vector195"),
    (("processor195", "key"), "zvmmiqcsp195"),
    (("processor195", "lemon"), "avaqrdwaf195"),
    (("processor195", "a"), "processor195"),
    (("processor195", "zz"), "oqnbdrrnq195"),
    (("processor195", "AgentU"), "pxspxmsuv195"),
    (("processor195", "keyboard"), "zvmdssjrb195"),
    (("processor195", "AA"), "processor195"),
    (("reasoning195", "key"), "biycslsre195"),
    (("reasoning195", "lemon"), "cimgbymzu195"),
    (("reasoning195", "a"), "reasoning195"),
    (("reasoning195", "zz"), "qdzrnmhmf195"),
    (("reasoning195", "AgentU"), "rkefhhitk195"),
    (("reasoning195", "keyboard"), "biytcnzqq195"),
    (("reasoning195", "AA"), "reasoning195"),
    (("machine195", "key"), "wearmlo195"),
    (("machine195", "lemon"), "xeovvyi195"),
    (("machine195", "a"), "machine195"),
    (("machine195", "zz"), "lzbghmd195"),
    (("machine195", "AgentU"), "mggubhe195"),
    (("machine195", "keyboard"), "weaiwnv195"),
    (("machine195", "AA"), "machine195"),
    (("learning195", "key"), "viybrgxk195"),
    (("learning195", "lemon"), "wimfatrs195"),
    (("learning195", "a"), "learning195"),
    (("learning195", "zz"), "kdzqmhmf195"),
    (("learning195", "AgentU"), "lkeegcnm195"),
    (("learning195", "keyboard"), "viysbiej195"),
    (("learning195", "AA"), "learning195"),
    (("model195", "key"), "wsbop195"),
    (("model195", "lemon"), "xspsy195"),
    (("model195", "a"), "model195"),
    (("model195", "zz"), "lncdk195"),
    (("model195", "AgentU"), "muhre195"),
    (("model195", "keyboard"), "wsbfz195"),
    (("model195", "AA"), "model195"),
    (("token195", "key"), "dsior195"),
    (("token195", "lemon"), "eswsa195"),
    (("token195", "a"), "token195"),
    (("token195", "zz"), "snjdm195"),
    (("token195", "AgentU"), "tuorg195"),
    (("token195", "keyboard"), "dsifb195"),
    (("token195", "AA"), "token195"),
    (("prompt195", "key"), "zvmwtr195"),
    (("prompt195", "lemon"), "avaace195"),
    (("prompt195", "a"), "prompt195"),
    (("prompt195", "zz"), "oqnlos195"),
    (("prompt195", "AgentU"), "pxszin195"),
    (("prompt195", "keyboard"), "zvmndt195"),
    (("prompt195", "AA"), "prompt195"),
    (("session195", "key"), "ciqcmmx195"),
    (("session195", "lemon"), "diegvzr195"),
    (("session195", "a"), "session195"),
    (("session195", "zz"), "rdrrhnm195"),
    (("session195", "AgentU"), "skwfbin195"),
    (("session195", "keyboard"), "ciqtwoe195"),
    (("session195", "AA"), "session195"),
    (("library195", "key"), "vmzbepi195"),
    (("library195", "lemon"), "wmnfncc195"),
    (("library195", "a"), "library195"),
    (("library195", "zz"), "khaqzqx195"),
    (("library195", "AgentU"), "lofetly195"),
    (("library195", "keyboard"), "vmzsorp195"),
    (("library195", "AA"), "library195"),
    (("service195", "key"), "cipfmao195"),
    (("service195", "lemon"), "didjvni195"),
    (("service195", "a"), "service195"),
    (("service195", "zz"), "rdquhbd195"),
    (("service195", "AgentU"), "skvibwe195"),
    (("service195", "keyboard"), "cipwwcv195"),
    (("service195", "AA"), "service195"),
    (("gateway195", "key"), "qeroayi195"),
    (("gateway195", "lemon"), "refsjlc195"),
    (("gateway195", "a"), "gateway195"),
    (("gateway195", "zz"), "fzsdvzx195"),
    (("gateway195", "AgentU"), "ggxrpuy195"),
    (("gateway195", "keyboard"), "qerfkap195"),
    (("gateway195", "AA"), "gateway195"),
    (("storage195", "key"), "cxmbeeo195"),
    (("storage195", "lemon"), "dxafnri195"),
    (("storage195", "a"), "storage195"),
    (("storage195", "zz"), "rsnqzfd195"),
    (("storage195", "AgentU"), "szsetae195"),
    (("storage195", "keyboard"), "cxmsogv195"),
    (("storage195", "AA"), "storage195"),
    (("network195", "key"), "xirgspu195"),
    (("network195", "lemon"), "yifkbco195"),
    (("network195", "a"), "network195"),
    (("network195", "zz"), "mdsvnqj195"),
    (("network195", "AgentU"), "nkxjhlk195"),
    (("network195", "keyboard"), "xirxcrb195"),
    (("network195", "AA"), "network195"),
    (("latency195", "key"), "verorai195"),
    (("latency195", "lemon"), "wefsanc195"),
    (("latency195", "a"), "latency195"),
    (("latency195", "zz"), "kzsdmbx195"),
    (("latency195", "AgentU"), "lgxrgwy195"),
    (("latency195", "keyboard"), "verfbcp195"),
    (("latency195", "AA"), "latency195"),
    (("buffer195", "key"), "lydpip195"),
    (("buffer195", "lemon"), "myrtrc195"),
    (("buffer195", "a"), "buffer195"),
    (("buffer195", "zz"), "ateedq195"),
    (("buffer195", "AgentU"), "bajsxl195"),
    (("buffer195", "keyboard"), "lydgsr195"),
    (("buffer195", "AA"), "buffer195"),
    (("queue195", "key"), "aycei195"),
    (("queue195", "lemon"), "byqir195"),
    (("queue195", "a"), "queue195"),
    (("queue195", "zz"), "ptdtd195"),
    (("queue195", "AgentU"), "qaihx195"),
    (("queue195", "keyboard"), "aycvs195"),
    (("queue195", "AA"), "queue195"),
    (("worker195", "key"), "gspuip195"),
    (("worker195", "lemon"), "hsdyrc195"),
    (("worker195", "a"), "worker195"),
    (("worker195", "zz"), "vnqjdq195"),
    (("worker195", "AgentU"), "wuvxxl195"),
    (("worker195", "keyboard"), "gsplsr195"),
    (("worker195", "AA"), "worker195"),
    (("kernel195", "key"), "uipxij195"),
    (("kernel195", "lemon"), "vidbrw195"),
    (("kernel195", "a"), "kernel195"),
    (("kernel195", "zz"), "jdqmdk195"),
    (("kernel195", "AgentU"), "kkvaxf195"),
    (("kernel195", "keyboard"), "uiposl195"),
    (("kernel195", "AA"), "kernel195"),
    (("signal195", "key"), "cmexej195"),
    (("signal195", "lemon"), "dmsbnw195"),
    (("signal195", "a"), "signal195"),
    (("signal195", "zz"), "rhfmzk195"),
    (("signal195", "AgentU"), "sokatf195"),
    (("signal195", "keyboard"), "cmeool195"),
    (("signal195", "AA"), "signal195"),
    (("packet195", "key"), "zeauir195"),
    (("packet195", "lemon"), "aeoyre195"),
    (("packet195", "a"), "packet195"),
    (("packet195", "zz"), "ozbjds195"),
    (("packet195", "AgentU"), "pggxxn195"),
    (("packet195", "keyboard"), "zealst195"),
    (("packet195", "AA"), "packet195"),
    (("router195", "key"), "bssdip195"),
    (("router195", "lemon"), "csghrc195"),
    (("router195", "a"), "router195"),
    (("router195", "zz"), "qntsdq195"),
    (("router195", "AgentU"), "ruygxl195"),
    (("router195", "keyboard"), "bssusr195"),
    (("router195", "AA"), "router195"),
    (("cluster195", "key"), "mpscxcb195"),
    (("cluster195", "lemon"), "npgggpv195"),
    (("cluster195", "a"), "cluster195"),
    (("cluster195", "zz"), "bktrsdq195"),
    (("cluster195", "AgentU"), "cryfmyr195"),
    (("cluster195", "keyboard"), "mpsthei195"),
    (("cluster195", "AA"), "cluster195"),
    (("mirror195", "key"), "wmpbsp195"),
    (("mirror195", "lemon"), "xmdfbc195"),
    (("mirror195", "a"), "mirror195"),
    (("mirror195", "zz"), "lhqqnq195"),
    (("mirror195", "AgentU"), "movehl195"),
    (("mirror195", "keyboard"), "wmpscr195"),
    (("mirror195", "AA"), "mirror195"),
    (("filter195", "key"), "pmjdip195"),
    (("filter195", "lemon"), "qmxhrc195"),
    (("filter195", "a"), "filter195"),
    (("filter195", "zz"), "ehksdq195"),
    (("filter195", "AgentU"), "fopgxl195"),
    (("filter195", "keyboard"), "pmjusr195"),
    (("filter195", "AA"), "filter195"),
    (("ranking195", "key"), "belumlq195"),
    (("ranking195", "lemon"), "cezyvyk195"),
    (("ranking195", "a"), "ranking195"),
    (("ranking195", "zz"), "qzmjhmf195"),
    (("ranking195", "AgentU"), "rgrxbhg195"),
    (("ranking195", "keyboard"), "bellwnx195"),
    (("ranking195", "AA"), "ranking195"),
    (("encoding195", "key"), "orayhgxk195"),
    (("encoding195", "lemon"), "procqtrs195"),
    (("encoding195", "a"), "encoding195"),
    (("encoding195", "zz"), "dmbnchmf195"),
    (("encoding195", "AgentU"), "etgbwcnm195"),
    (("encoding195", "keyboard"), "orapriej195"),
    (("encoding195", "AA"), "encoding195"),
    (("mapping195", "key"), "wenzmlq195"),
    (("mapping195", "lemon"), "xebdvyk195"),
    (("mapping195", "a"), "mapping195"),
    (("mapping195", "zz"), "lzoohmf195"),
    (("mapping195", "AgentU"), "mgtcbhg195"),
    (("mapping195", "keyboard"), "wenqwnx195"),
    (("mapping195", "AA"), "mapping195"),
    (("record195", "key"), "biayvb195"),
    (("record195", "lemon"), "cioceo195"),
    (("record195", "a"), "record195"),
    (("record195", "zz"), "qdbnqc195"),
    (("record195", "AgentU"), "rkgbkx195"),
    (("record195", "keyboard"), "biapfd195"),
    (("record195", "AA"), "record195"),
    (("candle195", "key"), "melnpc195"),
    (("candle195", "lemon"), "nezryp195"),
    (("candle195", "a"), "candle195"),
    (("candle195", "zz"), "bzmckd195"),
    (("candle195", "AgentU"), "cgrqey195"),
    (("candle195", "keyboard"), "meleze195"),
    (("candle195", "AA"), "candle195"),
    (("thread195", "key"), "dlpoeb195"),
    (("thread195", "lemon"), "eldsno195"),
    (("thread195", "a"), "thread195"),
    (("thread195", "zz"), "sgqdzc195"),
    (("thread195", "AgentU"), "tnvrtx195"),
    (("thread195", "keyboard"), "dlpfod195"),
    (("thread195", "AA"), "thread195"),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 195: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 195: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "a"),
        "round 195: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 195: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 195: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 195: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", "AA"),
        "round 195: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "key"),
        "bssxh 195: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 195: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "a"),
        "round 195: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 195: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 195: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 195: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", "AA"),
        "round 195: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 195: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 195: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "a"),
        "round 195: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 195: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 195: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 195: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", "AA"),
        "round 195: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 195: the processor reads the record then stops", "key"),
        "bssxh 195: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 195: the processor reads the record then stops", "lemon"),
        "csgbq 195: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 195: the processor reads the record then stops", "a"),
        "round 195: the processor reads the record then stops",
    ),
    (
        ("round 195: the processor reads the record then stops", "zz"),
        "qntmc 195: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 195: the processor reads the record then stops", "AgentU"),
        "ruyaw 195: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 195: the processor reads the record then stops", "keyboard"),
        "bssor 195: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 195: the processor reads the record then stops", "AA"),
        "round 195: the processor reads the record then stops",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "key"),
        "bssxh 195: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "lemon"),
        "csgbq 195: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "a"),
        "round 195: a worker pulls the next task from the queue",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "zz"),
        "qntmc 195: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 195: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "keyboard"),
        "bssor 195: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 195: a worker pulls the next task from the queue", "AA"),
        "round 195: a worker pulls the next task from the queue",
    ),
    (
        ("round 195: signals travel through the network layer", "key"),
        "bssxh 195: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 195: signals travel through the network layer", "lemon"),
        "csgbq 195: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 195: signals travel through the network layer", "a"),
        "round 195: signals travel through the network layer",
    ),
    (
        ("round 195: signals travel through the network layer", "zz"),
        "qntmc 195: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 195: signals travel through the network layer", "AgentU"),
        "ruyaw 195: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 195: signals travel through the network layer", "keyboard"),
        "bssor 195: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 195: signals travel through the network layer", "AA"),
        "round 195: signals travel through the network layer",
    ),
    (
        ("round 195: the gateway routes each request by policy", "key"),
        "bssxh 195: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 195: the gateway routes each request by policy", "lemon"),
        "csgbq 195: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 195: the gateway routes each request by policy", "a"),
        "round 195: the gateway routes each request by policy",
    ),
    (
        ("round 195: the gateway routes each request by policy", "zz"),
        "qntmc 195: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 195: the gateway routes each request by policy", "AgentU"),
        "ruyaw 195: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 195: the gateway routes each request by policy", "keyboard"),
        "bssor 195: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 195: the gateway routes each request by policy", "AA"),
        "round 195: the gateway routes each request by policy",
    ),
    (("round 195: memory grows until the buffer is full", "key"), "bssxh 195: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 195: memory grows until the buffer is full", "lemon"), "csgbq 195: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 195: memory grows until the buffer is full", "a"), "round 195: memory grows until the buffer is full"),
    (("round 195: memory grows until the buffer is full", "zz"), "qntmc 195: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 195: memory grows until the buffer is full", "AgentU"),
        "ruyaw 195: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 195: memory grows until the buffer is full", "keyboard"),
        "bssor 195: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 195: memory grows until the buffer is full", "AA"), "round 195: memory grows until the buffer is full"),
    (("round 195: the cluster mirrors every packet twice", "key"), "bssxh 195: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 195: the cluster mirrors every packet twice", "lemon"),
        "csgbq 195: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 195: the cluster mirrors every packet twice", "a"), "round 195: the cluster mirrors every packet twice"),
    (("round 195: the cluster mirrors every packet twice", "zz"), "qntmc 195: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 195: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 195: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 195: the cluster mirrors every packet twice", "keyboard"),
        "bssor 195: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 195: the cluster mirrors every packet twice", "AA"), "round 195: the cluster mirrors every packet twice"),
    (
        ("round 195: ranking uses tokens learned from the corpus", "key"),
        "bssxh 195: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 195: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", "a"),
        "round 195: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 195: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 195: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 195: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", "AA"),
        "round 195: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 195: a long session ends when the candle dies", "key"),
        "bssxh 195: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 195: a long session ends when the candle dies", "lemon"),
        "csgbq 195: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 195: a long session ends when the candle dies", "a"),
        "round 195: a long session ends when the candle dies",
    ),
    (
        ("round 195: a long session ends when the candle dies", "zz"),
        "qntmc 195: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 195: a long session ends when the candle dies", "AgentU"),
        "ruyaw 195: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 195: a long session ends when the candle dies", "keyboard"),
        "bssor 195: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 195: a long session ends when the candle dies", "AA"),
        "round 195: a long session ends when the candle dies",
    ),
    (("round 195: encode the prompt then map the result", "key"), "bssxh 195: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 195: encode the prompt then map the result", "lemon"), "csgbq 195: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 195: encode the prompt then map the result", "a"), "round 195: encode the prompt then map the result"),
    (("round 195: encode the prompt then map the result", "zz"), "qntmc 195: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 195: encode the prompt then map the result", "AgentU"),
        "ruyaw 195: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 195: encode the prompt then map the result", "keyboard"),
        "bssor 195: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 195: encode the prompt then map the result", "AA"), "round 195: encode the prompt then map the result"),
    (("round 195: the kernel wakes the worker at dawn", "key"), "bssxh 195: rri iovlop ukocc xfo ambocb er neux"),
    (("round 195: the kernel wakes the worker at dawn", "lemon"), "csgbq 195: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 195: the kernel wakes the worker at dawn", "a"), "round 195: the kernel wakes the worker at dawn"),
    (("round 195: the kernel wakes the worker at dawn", "zz"), "qntmc 195: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 195: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 195: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 195: the kernel wakes the worker at dawn", "keyboard"), "bssor 195: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 195: the kernel wakes the worker at dawn", "AA"), "round 195: the kernel wakes the worker at dawn"),
    (("round 195: service latency drops after the patch", "key"), "bssxh 195: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 195: service latency drops after the patch", "lemon"), "csgbq 195: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 195: service latency drops after the patch", "a"), "round 195: service latency drops after the patch"),
    (("round 195: service latency drops after the patch", "zz"), "qntmc 195: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 195: service latency drops after the patch", "AgentU"),
        "ruyaw 195: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 195: service latency drops after the patch", "keyboard"),
        "bssor 195: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 195: service latency drops after the patch", "AA"), "round 195: service latency drops after the patch"),
    (
        ("round 195: the library caches every vector it sees", "key"),
        "bssxh 195: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 195: the library caches every vector it sees", "lemon"),
        "csgbq 195: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 195: the library caches every vector it sees", "a"), "round 195: the library caches every vector it sees"),
    (
        ("round 195: the library caches every vector it sees", "zz"),
        "qntmc 195: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 195: the library caches every vector it sees", "AgentU"),
        "ruyaw 195: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 195: the library caches every vector it sees", "keyboard"),
        "bssor 195: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 195: the library caches every vector it sees", "AA"),
        "round 195: the library caches every vector it sees",
    ),
    (("round 195: agents argue then the debate resolves", "key"), "bssxh 195: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 195: agents argue then the debate resolves", "lemon"), "csgbq 195: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 195: agents argue then the debate resolves", "a"), "round 195: agents argue then the debate resolves"),
    (("round 195: agents argue then the debate resolves", "zz"), "qntmc 195: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 195: agents argue then the debate resolves", "AgentU"),
        "ruyaw 195: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 195: agents argue then the debate resolves", "keyboard"),
        "bssor 195: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 195: agents argue then the debate resolves", "AA"), "round 195: agents argue then the debate resolves"),
    (("round 195: the filter keeps only strong matches", "key"), "bssxh 195: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 195: the filter keeps only strong matches", "lemon"), "csgbq 195: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 195: the filter keeps only strong matches", "a"), "round 195: the filter keeps only strong matches"),
    (("round 195: the filter keeps only strong matches", "zz"), "qntmc 195: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 195: the filter keeps only strong matches", "AgentU"), "ruyaw 195: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 195: the filter keeps only strong matches", "keyboard"),
        "bssor 195: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 195: the filter keeps only strong matches", "AA"), "round 195: the filter keeps only strong matches"),
    (("round 195: the model answers with a short reply", "key"), "bssxh 195: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 195: the model answers with a short reply", "lemon"), "csgbq 195: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 195: the model answers with a short reply", "a"), "round 195: the model answers with a short reply"),
    (("round 195: the model answers with a short reply", "zz"), "qntmc 195: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 195: the model answers with a short reply", "AgentU"), "ruyaw 195: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 195: the model answers with a short reply", "keyboard"),
        "bssor 195: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 195: the model answers with a short reply", "AA"), "round 195: the model answers with a short reply"),
    (
        ("round 195: the recorder stores the reasoning trace", "key"),
        "bssxh 195: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 195: the recorder stores the reasoning trace", "lemon"),
        "csgbq 195: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 195: the recorder stores the reasoning trace", "a"), "round 195: the recorder stores the reasoning trace"),
    (
        ("round 195: the recorder stores the reasoning trace", "zz"),
        "qntmc 195: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 195: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 195: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 195: the recorder stores the reasoning trace", "keyboard"),
        "bssor 195: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 195: the recorder stores the reasoning trace", "AA"),
        "round 195: the recorder stores the reasoning trace",
    ),
    (("round 195: the angel watches the processor run", "key"), "bssxh 195: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 195: the angel watches the processor run", "lemon"), "csgbq 195: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 195: the angel watches the processor run", "a"), "round 195: the angel watches the processor run"),
    (("round 195: the angel watches the processor run", "zz"), "qntmc 195: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 195: the angel watches the processor run", "AgentU"), "ruyaw 195: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 195: the angel watches the processor run", "keyboard"), "bssor 195: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 195: the angel watches the processor run", "AA"), "round 195: the angel watches the processor run"),
    (("round 195: angle of the vector decides the match", "key"), "bssxh 195: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 195: angle of the vector decides the match", "lemon"), "csgbq 195: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 195: angle of the vector decides the match", "a"), "round 195: angle of the vector decides the match"),
    (("round 195: angle of the vector decides the match", "zz"), "qntmc 195: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 195: angle of the vector decides the match", "AgentU"),
        "ruyaw 195: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 195: angle of the vector decides the match", "keyboard"),
        "bssor 195: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 195: angle of the vector decides the match", "AA"), "round 195: angle of the vector decides the match"),
    (
        ("round 195: the candle burns twice as long at night", "key"),
        "bssxh 195: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 195: the candle burns twice as long at night", "lemon"),
        "csgbq 195: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 195: the candle burns twice as long at night", "a"), "round 195: the candle burns twice as long at night"),
    (
        ("round 195: the candle burns twice as long at night", "zz"),
        "qntmc 195: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 195: the candle burns twice as long at night", "AgentU"),
        "ruyaw 195: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 195: the candle burns twice as long at night", "keyboard"),
        "bssor 195: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 195: the candle burns twice as long at night", "AA"),
        "round 195: the candle burns twice as long at night",
    ),
    (("round 195: a mirror of the universe in one line", "key"), "bssxh 195: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 195: a mirror of the universe in one line", "lemon"), "csgbq 195: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 195: a mirror of the universe in one line", "a"), "round 195: a mirror of the universe in one line"),
    (("round 195: a mirror of the universe in one line", "zz"), "qntmc 195: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 195: a mirror of the universe in one line", "AgentU"), "ruyaw 195: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 195: a mirror of the universe in one line", "keyboard"),
        "bssor 195: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 195: a mirror of the universe in one line", "AA"), "round 195: a mirror of the universe in one line"),
    (("round 195: the queue drains before the storm", "key"), "bssxh 195: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 195: the queue drains before the storm", "lemon"), "csgbq 195: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 195: the queue drains before the storm", "a"), "round 195: the queue drains before the storm"),
    (("round 195: the queue drains before the storm", "zz"), "qntmc 195: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 195: the queue drains before the storm", "AgentU"), "ruyaw 195: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 195: the queue drains before the storm", "keyboard"), "bssor 195: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 195: the queue drains before the storm", "AA"), "round 195: the queue drains before the storm"),
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
