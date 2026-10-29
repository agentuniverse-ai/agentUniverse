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
    (("kitten167", "key"), "umrdil167"),
    (("kitten167", "lemon"), "vmfhry167"),
    (("kitten167", "a"), "kitten167"),
    (("kitten167", "zz"), "jhssdm167"),
    (("kitten167", "AgentU"), "koxgxh167"),
    (("kitten167", "keyboard"), "umrusn167"),
    (("kitten167", "AA"), "kitten167"),
    (("sitting167", "key"), "cmrdmlq167"),
    (("sitting167", "lemon"), "dmfhvyk167"),
    (("sitting167", "a"), "sitting167"),
    (("sitting167", "zz"), "rhsshmf167"),
    (("sitting167", "AgentU"), "soxgbhg167"),
    (("sitting167", "keyboard"), "cmruwnx167"),
    (("sitting167", "AA"), "sitting167"),
    (("agent167", "key"), "kkcxx167"),
    (("agent167", "lemon"), "lkqbg167"),
    (("agent167", "a"), "agent167"),
    (("agent167", "zz"), "zfdms167"),
    (("agent167", "AgentU"), "amiam167"),
    (("agent167", "keyboard"), "kkcoh167"),
    (("agent167", "AA"), "agent167"),
    (("angle167", "key"), "krevi167"),
    (("angle167", "lemon"), "lrszr167"),
    (("angle167", "a"), "angle167"),
    (("angle167", "zz"), "zmfkd167"),
    (("angle167", "AgentU"), "atkyx167"),
    (("angle167", "keyboard"), "krems167"),
    (("angle167", "AA"), "angle167"),
    (("universe167", "key"), "ergfipci167"),
    (("universe167", "lemon"), "frujrcwq167"),
    (("universe167", "a"), "universe167"),
    (("universe167", "zz"), "tmhudqrd167"),
    (("universe167", "AgentU"), "utmixlsk167"),
    (("universe167", "keyboard"), "ergwsrjh167"),
    (("universe167", "AA"), "universe167"),
    (("memory167", "key"), "wikyvw167"),
    (("memory167", "lemon"), "xiycej167"),
    (("memory167", "a"), "memory167"),
    (("memory167", "zz"), "ldlnqx167"),
    (("memory167", "AgentU"), "mkqbks167"),
    (("memory167", "keyboard"), "wikpfy167"),
    (("memory167", "AA"), "memory167"),
    (("stream167", "key"), "cxpoek167"),
    (("stream167", "lemon"), "dxdsnx167"),
    (("stream167", "a"), "stream167"),
    (("stream167", "zz"), "rsqdzl167"),
    (("stream167", "AgentU"), "szvrtg167"),
    (("stream167", "keyboard"), "cxpfom167"),
    (("stream167", "AA"), "stream167"),
    (("context167", "key"), "msldivd167"),
    (("context167", "lemon"), "nszhrix167"),
    (("context167", "a"), "context167"),
    (("context167", "zz"), "bnmsdws167"),
    (("context167", "AgentU"), "curgxrt167"),
    (("context167", "keyboard"), "mslusxk167"),
    (("context167", "AA"), "context167"),
    (("knowledge167", "key"), "urmgpcnkc167"),
    (("knowledge167", "lemon"), "vrakyphss167"),
    (("knowledge167", "a"), "knowledge167"),
    (("knowledge167", "zz"), "jmnvkdcfd167"),
    (("knowledge167", "AgentU"), "ktsjeydmi167"),
    (("knowledge167", "keyboard"), "urmxzeujo167"),
    (("knowledge167", "AA"), "knowledge167"),
    (("vector167", "key"), "fiadsp167"),
    (("vector167", "lemon"), "giohbc167"),
    (("vector167", "a"), "vector167"),
    (("vector167", "zz"), "udbsnq167"),
    (("vector167", "AgentU"), "vkgghl167"),
    (("vector167", "keyboard"), "fiaucr167"),
    (("vector167", "AA"), "vector167"),
    (("processor167", "key"), "zvmmiqcsp167"),
    (("processor167", "lemon"), "avaqrdwaf167"),
    (("processor167", "a"), "processor167"),
    (("processor167", "zz"), "oqnbdrrnq167"),
    (("processor167", "AgentU"), "pxspxmsuv167"),
    (("processor167", "keyboard"), "zvmdssjrb167"),
    (("processor167", "AA"), "processor167"),
    (("reasoning167", "key"), "biycslsre167"),
    (("reasoning167", "lemon"), "cimgbymzu167"),
    (("reasoning167", "a"), "reasoning167"),
    (("reasoning167", "zz"), "qdzrnmhmf167"),
    (("reasoning167", "AgentU"), "rkefhhitk167"),
    (("reasoning167", "keyboard"), "biytcnzqq167"),
    (("reasoning167", "AA"), "reasoning167"),
    (("machine167", "key"), "wearmlo167"),
    (("machine167", "lemon"), "xeovvyi167"),
    (("machine167", "a"), "machine167"),
    (("machine167", "zz"), "lzbghmd167"),
    (("machine167", "AgentU"), "mggubhe167"),
    (("machine167", "keyboard"), "weaiwnv167"),
    (("machine167", "AA"), "machine167"),
    (("learning167", "key"), "viybrgxk167"),
    (("learning167", "lemon"), "wimfatrs167"),
    (("learning167", "a"), "learning167"),
    (("learning167", "zz"), "kdzqmhmf167"),
    (("learning167", "AgentU"), "lkeegcnm167"),
    (("learning167", "keyboard"), "viysbiej167"),
    (("learning167", "AA"), "learning167"),
    (("model167", "key"), "wsbop167"),
    (("model167", "lemon"), "xspsy167"),
    (("model167", "a"), "model167"),
    (("model167", "zz"), "lncdk167"),
    (("model167", "AgentU"), "muhre167"),
    (("model167", "keyboard"), "wsbfz167"),
    (("model167", "AA"), "model167"),
    (("token167", "key"), "dsior167"),
    (("token167", "lemon"), "eswsa167"),
    (("token167", "a"), "token167"),
    (("token167", "zz"), "snjdm167"),
    (("token167", "AgentU"), "tuorg167"),
    (("token167", "keyboard"), "dsifb167"),
    (("token167", "AA"), "token167"),
    (("prompt167", "key"), "zvmwtr167"),
    (("prompt167", "lemon"), "avaace167"),
    (("prompt167", "a"), "prompt167"),
    (("prompt167", "zz"), "oqnlos167"),
    (("prompt167", "AgentU"), "pxszin167"),
    (("prompt167", "keyboard"), "zvmndt167"),
    (("prompt167", "AA"), "prompt167"),
    (("session167", "key"), "ciqcmmx167"),
    (("session167", "lemon"), "diegvzr167"),
    (("session167", "a"), "session167"),
    (("session167", "zz"), "rdrrhnm167"),
    (("session167", "AgentU"), "skwfbin167"),
    (("session167", "keyboard"), "ciqtwoe167"),
    (("session167", "AA"), "session167"),
    (("library167", "key"), "vmzbepi167"),
    (("library167", "lemon"), "wmnfncc167"),
    (("library167", "a"), "library167"),
    (("library167", "zz"), "khaqzqx167"),
    (("library167", "AgentU"), "lofetly167"),
    (("library167", "keyboard"), "vmzsorp167"),
    (("library167", "AA"), "library167"),
    (("service167", "key"), "cipfmao167"),
    (("service167", "lemon"), "didjvni167"),
    (("service167", "a"), "service167"),
    (("service167", "zz"), "rdquhbd167"),
    (("service167", "AgentU"), "skvibwe167"),
    (("service167", "keyboard"), "cipwwcv167"),
    (("service167", "AA"), "service167"),
    (("gateway167", "key"), "qeroayi167"),
    (("gateway167", "lemon"), "refsjlc167"),
    (("gateway167", "a"), "gateway167"),
    (("gateway167", "zz"), "fzsdvzx167"),
    (("gateway167", "AgentU"), "ggxrpuy167"),
    (("gateway167", "keyboard"), "qerfkap167"),
    (("gateway167", "AA"), "gateway167"),
    (("storage167", "key"), "cxmbeeo167"),
    (("storage167", "lemon"), "dxafnri167"),
    (("storage167", "a"), "storage167"),
    (("storage167", "zz"), "rsnqzfd167"),
    (("storage167", "AgentU"), "szsetae167"),
    (("storage167", "keyboard"), "cxmsogv167"),
    (("storage167", "AA"), "storage167"),
    (("network167", "key"), "xirgspu167"),
    (("network167", "lemon"), "yifkbco167"),
    (("network167", "a"), "network167"),
    (("network167", "zz"), "mdsvnqj167"),
    (("network167", "AgentU"), "nkxjhlk167"),
    (("network167", "keyboard"), "xirxcrb167"),
    (("network167", "AA"), "network167"),
    (("latency167", "key"), "verorai167"),
    (("latency167", "lemon"), "wefsanc167"),
    (("latency167", "a"), "latency167"),
    (("latency167", "zz"), "kzsdmbx167"),
    (("latency167", "AgentU"), "lgxrgwy167"),
    (("latency167", "keyboard"), "verfbcp167"),
    (("latency167", "AA"), "latency167"),
    (("buffer167", "key"), "lydpip167"),
    (("buffer167", "lemon"), "myrtrc167"),
    (("buffer167", "a"), "buffer167"),
    (("buffer167", "zz"), "ateedq167"),
    (("buffer167", "AgentU"), "bajsxl167"),
    (("buffer167", "keyboard"), "lydgsr167"),
    (("buffer167", "AA"), "buffer167"),
    (("queue167", "key"), "aycei167"),
    (("queue167", "lemon"), "byqir167"),
    (("queue167", "a"), "queue167"),
    (("queue167", "zz"), "ptdtd167"),
    (("queue167", "AgentU"), "qaihx167"),
    (("queue167", "keyboard"), "aycvs167"),
    (("queue167", "AA"), "queue167"),
    (("worker167", "key"), "gspuip167"),
    (("worker167", "lemon"), "hsdyrc167"),
    (("worker167", "a"), "worker167"),
    (("worker167", "zz"), "vnqjdq167"),
    (("worker167", "AgentU"), "wuvxxl167"),
    (("worker167", "keyboard"), "gsplsr167"),
    (("worker167", "AA"), "worker167"),
    (("kernel167", "key"), "uipxij167"),
    (("kernel167", "lemon"), "vidbrw167"),
    (("kernel167", "a"), "kernel167"),
    (("kernel167", "zz"), "jdqmdk167"),
    (("kernel167", "AgentU"), "kkvaxf167"),
    (("kernel167", "keyboard"), "uiposl167"),
    (("kernel167", "AA"), "kernel167"),
    (("signal167", "key"), "cmexej167"),
    (("signal167", "lemon"), "dmsbnw167"),
    (("signal167", "a"), "signal167"),
    (("signal167", "zz"), "rhfmzk167"),
    (("signal167", "AgentU"), "sokatf167"),
    (("signal167", "keyboard"), "cmeool167"),
    (("signal167", "AA"), "signal167"),
    (("packet167", "key"), "zeauir167"),
    (("packet167", "lemon"), "aeoyre167"),
    (("packet167", "a"), "packet167"),
    (("packet167", "zz"), "ozbjds167"),
    (("packet167", "AgentU"), "pggxxn167"),
    (("packet167", "keyboard"), "zealst167"),
    (("packet167", "AA"), "packet167"),
    (("router167", "key"), "bssdip167"),
    (("router167", "lemon"), "csghrc167"),
    (("router167", "a"), "router167"),
    (("router167", "zz"), "qntsdq167"),
    (("router167", "AgentU"), "ruygxl167"),
    (("router167", "keyboard"), "bssusr167"),
    (("router167", "AA"), "router167"),
    (("cluster167", "key"), "mpscxcb167"),
    (("cluster167", "lemon"), "npgggpv167"),
    (("cluster167", "a"), "cluster167"),
    (("cluster167", "zz"), "bktrsdq167"),
    (("cluster167", "AgentU"), "cryfmyr167"),
    (("cluster167", "keyboard"), "mpsthei167"),
    (("cluster167", "AA"), "cluster167"),
    (("mirror167", "key"), "wmpbsp167"),
    (("mirror167", "lemon"), "xmdfbc167"),
    (("mirror167", "a"), "mirror167"),
    (("mirror167", "zz"), "lhqqnq167"),
    (("mirror167", "AgentU"), "movehl167"),
    (("mirror167", "keyboard"), "wmpscr167"),
    (("mirror167", "AA"), "mirror167"),
    (("filter167", "key"), "pmjdip167"),
    (("filter167", "lemon"), "qmxhrc167"),
    (("filter167", "a"), "filter167"),
    (("filter167", "zz"), "ehksdq167"),
    (("filter167", "AgentU"), "fopgxl167"),
    (("filter167", "keyboard"), "pmjusr167"),
    (("filter167", "AA"), "filter167"),
    (("ranking167", "key"), "belumlq167"),
    (("ranking167", "lemon"), "cezyvyk167"),
    (("ranking167", "a"), "ranking167"),
    (("ranking167", "zz"), "qzmjhmf167"),
    (("ranking167", "AgentU"), "rgrxbhg167"),
    (("ranking167", "keyboard"), "bellwnx167"),
    (("ranking167", "AA"), "ranking167"),
    (("encoding167", "key"), "orayhgxk167"),
    (("encoding167", "lemon"), "procqtrs167"),
    (("encoding167", "a"), "encoding167"),
    (("encoding167", "zz"), "dmbnchmf167"),
    (("encoding167", "AgentU"), "etgbwcnm167"),
    (("encoding167", "keyboard"), "orapriej167"),
    (("encoding167", "AA"), "encoding167"),
    (("mapping167", "key"), "wenzmlq167"),
    (("mapping167", "lemon"), "xebdvyk167"),
    (("mapping167", "a"), "mapping167"),
    (("mapping167", "zz"), "lzoohmf167"),
    (("mapping167", "AgentU"), "mgtcbhg167"),
    (("mapping167", "keyboard"), "wenqwnx167"),
    (("mapping167", "AA"), "mapping167"),
    (("record167", "key"), "biayvb167"),
    (("record167", "lemon"), "cioceo167"),
    (("record167", "a"), "record167"),
    (("record167", "zz"), "qdbnqc167"),
    (("record167", "AgentU"), "rkgbkx167"),
    (("record167", "keyboard"), "biapfd167"),
    (("record167", "AA"), "record167"),
    (("candle167", "key"), "melnpc167"),
    (("candle167", "lemon"), "nezryp167"),
    (("candle167", "a"), "candle167"),
    (("candle167", "zz"), "bzmckd167"),
    (("candle167", "AgentU"), "cgrqey167"),
    (("candle167", "keyboard"), "meleze167"),
    (("candle167", "AA"), "candle167"),
    (("thread167", "key"), "dlpoeb167"),
    (("thread167", "lemon"), "eldsno167"),
    (("thread167", "a"), "thread167"),
    (("thread167", "zz"), "sgqdzc167"),
    (("thread167", "AgentU"), "tnvrtx167"),
    (("thread167", "keyboard"), "dlpfod167"),
    (("thread167", "AA"), "thread167"),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 167: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 167: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "a"),
        "round 167: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 167: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 167: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 167: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", "AA"),
        "round 167: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "key"),
        "bssxh 167: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 167: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "a"),
        "round 167: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 167: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 167: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 167: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", "AA"),
        "round 167: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 167: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 167: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "a"),
        "round 167: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 167: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 167: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 167: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", "AA"),
        "round 167: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 167: the processor reads the record then stops", "key"),
        "bssxh 167: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 167: the processor reads the record then stops", "lemon"),
        "csgbq 167: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 167: the processor reads the record then stops", "a"),
        "round 167: the processor reads the record then stops",
    ),
    (
        ("round 167: the processor reads the record then stops", "zz"),
        "qntmc 167: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 167: the processor reads the record then stops", "AgentU"),
        "ruyaw 167: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 167: the processor reads the record then stops", "keyboard"),
        "bssor 167: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 167: the processor reads the record then stops", "AA"),
        "round 167: the processor reads the record then stops",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "key"),
        "bssxh 167: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "lemon"),
        "csgbq 167: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "a"),
        "round 167: a worker pulls the next task from the queue",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "zz"),
        "qntmc 167: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 167: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "keyboard"),
        "bssor 167: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 167: a worker pulls the next task from the queue", "AA"),
        "round 167: a worker pulls the next task from the queue",
    ),
    (
        ("round 167: signals travel through the network layer", "key"),
        "bssxh 167: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 167: signals travel through the network layer", "lemon"),
        "csgbq 167: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 167: signals travel through the network layer", "a"),
        "round 167: signals travel through the network layer",
    ),
    (
        ("round 167: signals travel through the network layer", "zz"),
        "qntmc 167: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 167: signals travel through the network layer", "AgentU"),
        "ruyaw 167: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 167: signals travel through the network layer", "keyboard"),
        "bssor 167: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 167: signals travel through the network layer", "AA"),
        "round 167: signals travel through the network layer",
    ),
    (
        ("round 167: the gateway routes each request by policy", "key"),
        "bssxh 167: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 167: the gateway routes each request by policy", "lemon"),
        "csgbq 167: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 167: the gateway routes each request by policy", "a"),
        "round 167: the gateway routes each request by policy",
    ),
    (
        ("round 167: the gateway routes each request by policy", "zz"),
        "qntmc 167: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 167: the gateway routes each request by policy", "AgentU"),
        "ruyaw 167: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 167: the gateway routes each request by policy", "keyboard"),
        "bssor 167: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 167: the gateway routes each request by policy", "AA"),
        "round 167: the gateway routes each request by policy",
    ),
    (("round 167: memory grows until the buffer is full", "key"), "bssxh 167: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 167: memory grows until the buffer is full", "lemon"), "csgbq 167: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 167: memory grows until the buffer is full", "a"), "round 167: memory grows until the buffer is full"),
    (("round 167: memory grows until the buffer is full", "zz"), "qntmc 167: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 167: memory grows until the buffer is full", "AgentU"),
        "ruyaw 167: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 167: memory grows until the buffer is full", "keyboard"),
        "bssor 167: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 167: memory grows until the buffer is full", "AA"), "round 167: memory grows until the buffer is full"),
    (("round 167: the cluster mirrors every packet twice", "key"), "bssxh 167: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 167: the cluster mirrors every packet twice", "lemon"),
        "csgbq 167: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 167: the cluster mirrors every packet twice", "a"), "round 167: the cluster mirrors every packet twice"),
    (("round 167: the cluster mirrors every packet twice", "zz"), "qntmc 167: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 167: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 167: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 167: the cluster mirrors every packet twice", "keyboard"),
        "bssor 167: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 167: the cluster mirrors every packet twice", "AA"), "round 167: the cluster mirrors every packet twice"),
    (
        ("round 167: ranking uses tokens learned from the corpus", "key"),
        "bssxh 167: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 167: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", "a"),
        "round 167: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 167: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 167: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 167: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", "AA"),
        "round 167: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 167: a long session ends when the candle dies", "key"),
        "bssxh 167: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 167: a long session ends when the candle dies", "lemon"),
        "csgbq 167: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 167: a long session ends when the candle dies", "a"),
        "round 167: a long session ends when the candle dies",
    ),
    (
        ("round 167: a long session ends when the candle dies", "zz"),
        "qntmc 167: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 167: a long session ends when the candle dies", "AgentU"),
        "ruyaw 167: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 167: a long session ends when the candle dies", "keyboard"),
        "bssor 167: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 167: a long session ends when the candle dies", "AA"),
        "round 167: a long session ends when the candle dies",
    ),
    (("round 167: encode the prompt then map the result", "key"), "bssxh 167: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 167: encode the prompt then map the result", "lemon"), "csgbq 167: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 167: encode the prompt then map the result", "a"), "round 167: encode the prompt then map the result"),
    (("round 167: encode the prompt then map the result", "zz"), "qntmc 167: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 167: encode the prompt then map the result", "AgentU"),
        "ruyaw 167: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 167: encode the prompt then map the result", "keyboard"),
        "bssor 167: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 167: encode the prompt then map the result", "AA"), "round 167: encode the prompt then map the result"),
    (("round 167: the kernel wakes the worker at dawn", "key"), "bssxh 167: rri iovlop ukocc xfo ambocb er neux"),
    (("round 167: the kernel wakes the worker at dawn", "lemon"), "csgbq 167: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 167: the kernel wakes the worker at dawn", "a"), "round 167: the kernel wakes the worker at dawn"),
    (("round 167: the kernel wakes the worker at dawn", "zz"), "qntmc 167: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 167: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 167: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 167: the kernel wakes the worker at dawn", "keyboard"), "bssor 167: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 167: the kernel wakes the worker at dawn", "AA"), "round 167: the kernel wakes the worker at dawn"),
    (("round 167: service latency drops after the patch", "key"), "bssxh 167: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 167: service latency drops after the patch", "lemon"), "csgbq 167: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 167: service latency drops after the patch", "a"), "round 167: service latency drops after the patch"),
    (("round 167: service latency drops after the patch", "zz"), "qntmc 167: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 167: service latency drops after the patch", "AgentU"),
        "ruyaw 167: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 167: service latency drops after the patch", "keyboard"),
        "bssor 167: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 167: service latency drops after the patch", "AA"), "round 167: service latency drops after the patch"),
    (
        ("round 167: the library caches every vector it sees", "key"),
        "bssxh 167: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 167: the library caches every vector it sees", "lemon"),
        "csgbq 167: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 167: the library caches every vector it sees", "a"), "round 167: the library caches every vector it sees"),
    (
        ("round 167: the library caches every vector it sees", "zz"),
        "qntmc 167: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 167: the library caches every vector it sees", "AgentU"),
        "ruyaw 167: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 167: the library caches every vector it sees", "keyboard"),
        "bssor 167: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 167: the library caches every vector it sees", "AA"),
        "round 167: the library caches every vector it sees",
    ),
    (("round 167: agents argue then the debate resolves", "key"), "bssxh 167: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 167: agents argue then the debate resolves", "lemon"), "csgbq 167: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 167: agents argue then the debate resolves", "a"), "round 167: agents argue then the debate resolves"),
    (("round 167: agents argue then the debate resolves", "zz"), "qntmc 167: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 167: agents argue then the debate resolves", "AgentU"),
        "ruyaw 167: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 167: agents argue then the debate resolves", "keyboard"),
        "bssor 167: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 167: agents argue then the debate resolves", "AA"), "round 167: agents argue then the debate resolves"),
    (("round 167: the filter keeps only strong matches", "key"), "bssxh 167: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 167: the filter keeps only strong matches", "lemon"), "csgbq 167: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 167: the filter keeps only strong matches", "a"), "round 167: the filter keeps only strong matches"),
    (("round 167: the filter keeps only strong matches", "zz"), "qntmc 167: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 167: the filter keeps only strong matches", "AgentU"), "ruyaw 167: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 167: the filter keeps only strong matches", "keyboard"),
        "bssor 167: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 167: the filter keeps only strong matches", "AA"), "round 167: the filter keeps only strong matches"),
    (("round 167: the model answers with a short reply", "key"), "bssxh 167: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 167: the model answers with a short reply", "lemon"), "csgbq 167: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 167: the model answers with a short reply", "a"), "round 167: the model answers with a short reply"),
    (("round 167: the model answers with a short reply", "zz"), "qntmc 167: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 167: the model answers with a short reply", "AgentU"), "ruyaw 167: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 167: the model answers with a short reply", "keyboard"),
        "bssor 167: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 167: the model answers with a short reply", "AA"), "round 167: the model answers with a short reply"),
    (
        ("round 167: the recorder stores the reasoning trace", "key"),
        "bssxh 167: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 167: the recorder stores the reasoning trace", "lemon"),
        "csgbq 167: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 167: the recorder stores the reasoning trace", "a"), "round 167: the recorder stores the reasoning trace"),
    (
        ("round 167: the recorder stores the reasoning trace", "zz"),
        "qntmc 167: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 167: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 167: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 167: the recorder stores the reasoning trace", "keyboard"),
        "bssor 167: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 167: the recorder stores the reasoning trace", "AA"),
        "round 167: the recorder stores the reasoning trace",
    ),
    (("round 167: the angel watches the processor run", "key"), "bssxh 167: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 167: the angel watches the processor run", "lemon"), "csgbq 167: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 167: the angel watches the processor run", "a"), "round 167: the angel watches the processor run"),
    (("round 167: the angel watches the processor run", "zz"), "qntmc 167: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 167: the angel watches the processor run", "AgentU"), "ruyaw 167: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 167: the angel watches the processor run", "keyboard"), "bssor 167: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 167: the angel watches the processor run", "AA"), "round 167: the angel watches the processor run"),
    (("round 167: angle of the vector decides the match", "key"), "bssxh 167: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 167: angle of the vector decides the match", "lemon"), "csgbq 167: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 167: angle of the vector decides the match", "a"), "round 167: angle of the vector decides the match"),
    (("round 167: angle of the vector decides the match", "zz"), "qntmc 167: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 167: angle of the vector decides the match", "AgentU"),
        "ruyaw 167: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 167: angle of the vector decides the match", "keyboard"),
        "bssor 167: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 167: angle of the vector decides the match", "AA"), "round 167: angle of the vector decides the match"),
    (
        ("round 167: the candle burns twice as long at night", "key"),
        "bssxh 167: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 167: the candle burns twice as long at night", "lemon"),
        "csgbq 167: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 167: the candle burns twice as long at night", "a"), "round 167: the candle burns twice as long at night"),
    (
        ("round 167: the candle burns twice as long at night", "zz"),
        "qntmc 167: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 167: the candle burns twice as long at night", "AgentU"),
        "ruyaw 167: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 167: the candle burns twice as long at night", "keyboard"),
        "bssor 167: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 167: the candle burns twice as long at night", "AA"),
        "round 167: the candle burns twice as long at night",
    ),
    (("round 167: a mirror of the universe in one line", "key"), "bssxh 167: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 167: a mirror of the universe in one line", "lemon"), "csgbq 167: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 167: a mirror of the universe in one line", "a"), "round 167: a mirror of the universe in one line"),
    (("round 167: a mirror of the universe in one line", "zz"), "qntmc 167: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 167: a mirror of the universe in one line", "AgentU"), "ruyaw 167: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 167: a mirror of the universe in one line", "keyboard"),
        "bssor 167: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 167: a mirror of the universe in one line", "AA"), "round 167: a mirror of the universe in one line"),
    (("round 167: the queue drains before the storm", "key"), "bssxh 167: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 167: the queue drains before the storm", "lemon"), "csgbq 167: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 167: the queue drains before the storm", "a"), "round 167: the queue drains before the storm"),
    (("round 167: the queue drains before the storm", "zz"), "qntmc 167: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 167: the queue drains before the storm", "AgentU"), "ruyaw 167: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 167: the queue drains before the storm", "keyboard"), "bssor 167: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 167: the queue drains before the storm", "AA"), "round 167: the queue drains before the storm"),
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
