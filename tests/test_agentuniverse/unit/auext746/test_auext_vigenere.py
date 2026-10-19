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
    (("kitten746", "key"), "umrdil746"),
    (("kitten746", "lemon"), "vmfhry746"),
    (("kitten746", "a"), "kitten746"),
    (("kitten746", "zz"), "jhssdm746"),
    (("kitten746", "AgentU"), "koxgxh746"),
    (("kitten746", "keyboard"), "umrusn746"),
    (("kitten746", "AA"), "kitten746"),
    (("sitting746", "key"), "cmrdmlq746"),
    (("sitting746", "lemon"), "dmfhvyk746"),
    (("sitting746", "a"), "sitting746"),
    (("sitting746", "zz"), "rhsshmf746"),
    (("sitting746", "AgentU"), "soxgbhg746"),
    (("sitting746", "keyboard"), "cmruwnx746"),
    (("sitting746", "AA"), "sitting746"),
    (("agent746", "key"), "kkcxx746"),
    (("agent746", "lemon"), "lkqbg746"),
    (("agent746", "a"), "agent746"),
    (("agent746", "zz"), "zfdms746"),
    (("agent746", "AgentU"), "amiam746"),
    (("agent746", "keyboard"), "kkcoh746"),
    (("agent746", "AA"), "agent746"),
    (("angle746", "key"), "krevi746"),
    (("angle746", "lemon"), "lrszr746"),
    (("angle746", "a"), "angle746"),
    (("angle746", "zz"), "zmfkd746"),
    (("angle746", "AgentU"), "atkyx746"),
    (("angle746", "keyboard"), "krems746"),
    (("angle746", "AA"), "angle746"),
    (("universe746", "key"), "ergfipci746"),
    (("universe746", "lemon"), "frujrcwq746"),
    (("universe746", "a"), "universe746"),
    (("universe746", "zz"), "tmhudqrd746"),
    (("universe746", "AgentU"), "utmixlsk746"),
    (("universe746", "keyboard"), "ergwsrjh746"),
    (("universe746", "AA"), "universe746"),
    (("memory746", "key"), "wikyvw746"),
    (("memory746", "lemon"), "xiycej746"),
    (("memory746", "a"), "memory746"),
    (("memory746", "zz"), "ldlnqx746"),
    (("memory746", "AgentU"), "mkqbks746"),
    (("memory746", "keyboard"), "wikpfy746"),
    (("memory746", "AA"), "memory746"),
    (("stream746", "key"), "cxpoek746"),
    (("stream746", "lemon"), "dxdsnx746"),
    (("stream746", "a"), "stream746"),
    (("stream746", "zz"), "rsqdzl746"),
    (("stream746", "AgentU"), "szvrtg746"),
    (("stream746", "keyboard"), "cxpfom746"),
    (("stream746", "AA"), "stream746"),
    (("context746", "key"), "msldivd746"),
    (("context746", "lemon"), "nszhrix746"),
    (("context746", "a"), "context746"),
    (("context746", "zz"), "bnmsdws746"),
    (("context746", "AgentU"), "curgxrt746"),
    (("context746", "keyboard"), "mslusxk746"),
    (("context746", "AA"), "context746"),
    (("knowledge746", "key"), "urmgpcnkc746"),
    (("knowledge746", "lemon"), "vrakyphss746"),
    (("knowledge746", "a"), "knowledge746"),
    (("knowledge746", "zz"), "jmnvkdcfd746"),
    (("knowledge746", "AgentU"), "ktsjeydmi746"),
    (("knowledge746", "keyboard"), "urmxzeujo746"),
    (("knowledge746", "AA"), "knowledge746"),
    (("vector746", "key"), "fiadsp746"),
    (("vector746", "lemon"), "giohbc746"),
    (("vector746", "a"), "vector746"),
    (("vector746", "zz"), "udbsnq746"),
    (("vector746", "AgentU"), "vkgghl746"),
    (("vector746", "keyboard"), "fiaucr746"),
    (("vector746", "AA"), "vector746"),
    (("processor746", "key"), "zvmmiqcsp746"),
    (("processor746", "lemon"), "avaqrdwaf746"),
    (("processor746", "a"), "processor746"),
    (("processor746", "zz"), "oqnbdrrnq746"),
    (("processor746", "AgentU"), "pxspxmsuv746"),
    (("processor746", "keyboard"), "zvmdssjrb746"),
    (("processor746", "AA"), "processor746"),
    (("reasoning746", "key"), "biycslsre746"),
    (("reasoning746", "lemon"), "cimgbymzu746"),
    (("reasoning746", "a"), "reasoning746"),
    (("reasoning746", "zz"), "qdzrnmhmf746"),
    (("reasoning746", "AgentU"), "rkefhhitk746"),
    (("reasoning746", "keyboard"), "biytcnzqq746"),
    (("reasoning746", "AA"), "reasoning746"),
    (("machine746", "key"), "wearmlo746"),
    (("machine746", "lemon"), "xeovvyi746"),
    (("machine746", "a"), "machine746"),
    (("machine746", "zz"), "lzbghmd746"),
    (("machine746", "AgentU"), "mggubhe746"),
    (("machine746", "keyboard"), "weaiwnv746"),
    (("machine746", "AA"), "machine746"),
    (("learning746", "key"), "viybrgxk746"),
    (("learning746", "lemon"), "wimfatrs746"),
    (("learning746", "a"), "learning746"),
    (("learning746", "zz"), "kdzqmhmf746"),
    (("learning746", "AgentU"), "lkeegcnm746"),
    (("learning746", "keyboard"), "viysbiej746"),
    (("learning746", "AA"), "learning746"),
    (("model746", "key"), "wsbop746"),
    (("model746", "lemon"), "xspsy746"),
    (("model746", "a"), "model746"),
    (("model746", "zz"), "lncdk746"),
    (("model746", "AgentU"), "muhre746"),
    (("model746", "keyboard"), "wsbfz746"),
    (("model746", "AA"), "model746"),
    (("token746", "key"), "dsior746"),
    (("token746", "lemon"), "eswsa746"),
    (("token746", "a"), "token746"),
    (("token746", "zz"), "snjdm746"),
    (("token746", "AgentU"), "tuorg746"),
    (("token746", "keyboard"), "dsifb746"),
    (("token746", "AA"), "token746"),
    (("prompt746", "key"), "zvmwtr746"),
    (("prompt746", "lemon"), "avaace746"),
    (("prompt746", "a"), "prompt746"),
    (("prompt746", "zz"), "oqnlos746"),
    (("prompt746", "AgentU"), "pxszin746"),
    (("prompt746", "keyboard"), "zvmndt746"),
    (("prompt746", "AA"), "prompt746"),
    (("session746", "key"), "ciqcmmx746"),
    (("session746", "lemon"), "diegvzr746"),
    (("session746", "a"), "session746"),
    (("session746", "zz"), "rdrrhnm746"),
    (("session746", "AgentU"), "skwfbin746"),
    (("session746", "keyboard"), "ciqtwoe746"),
    (("session746", "AA"), "session746"),
    (("library746", "key"), "vmzbepi746"),
    (("library746", "lemon"), "wmnfncc746"),
    (("library746", "a"), "library746"),
    (("library746", "zz"), "khaqzqx746"),
    (("library746", "AgentU"), "lofetly746"),
    (("library746", "keyboard"), "vmzsorp746"),
    (("library746", "AA"), "library746"),
    (("service746", "key"), "cipfmao746"),
    (("service746", "lemon"), "didjvni746"),
    (("service746", "a"), "service746"),
    (("service746", "zz"), "rdquhbd746"),
    (("service746", "AgentU"), "skvibwe746"),
    (("service746", "keyboard"), "cipwwcv746"),
    (("service746", "AA"), "service746"),
    (("gateway746", "key"), "qeroayi746"),
    (("gateway746", "lemon"), "refsjlc746"),
    (("gateway746", "a"), "gateway746"),
    (("gateway746", "zz"), "fzsdvzx746"),
    (("gateway746", "AgentU"), "ggxrpuy746"),
    (("gateway746", "keyboard"), "qerfkap746"),
    (("gateway746", "AA"), "gateway746"),
    (("storage746", "key"), "cxmbeeo746"),
    (("storage746", "lemon"), "dxafnri746"),
    (("storage746", "a"), "storage746"),
    (("storage746", "zz"), "rsnqzfd746"),
    (("storage746", "AgentU"), "szsetae746"),
    (("storage746", "keyboard"), "cxmsogv746"),
    (("storage746", "AA"), "storage746"),
    (("network746", "key"), "xirgspu746"),
    (("network746", "lemon"), "yifkbco746"),
    (("network746", "a"), "network746"),
    (("network746", "zz"), "mdsvnqj746"),
    (("network746", "AgentU"), "nkxjhlk746"),
    (("network746", "keyboard"), "xirxcrb746"),
    (("network746", "AA"), "network746"),
    (("latency746", "key"), "verorai746"),
    (("latency746", "lemon"), "wefsanc746"),
    (("latency746", "a"), "latency746"),
    (("latency746", "zz"), "kzsdmbx746"),
    (("latency746", "AgentU"), "lgxrgwy746"),
    (("latency746", "keyboard"), "verfbcp746"),
    (("latency746", "AA"), "latency746"),
    (("buffer746", "key"), "lydpip746"),
    (("buffer746", "lemon"), "myrtrc746"),
    (("buffer746", "a"), "buffer746"),
    (("buffer746", "zz"), "ateedq746"),
    (("buffer746", "AgentU"), "bajsxl746"),
    (("buffer746", "keyboard"), "lydgsr746"),
    (("buffer746", "AA"), "buffer746"),
    (("queue746", "key"), "aycei746"),
    (("queue746", "lemon"), "byqir746"),
    (("queue746", "a"), "queue746"),
    (("queue746", "zz"), "ptdtd746"),
    (("queue746", "AgentU"), "qaihx746"),
    (("queue746", "keyboard"), "aycvs746"),
    (("queue746", "AA"), "queue746"),
    (("worker746", "key"), "gspuip746"),
    (("worker746", "lemon"), "hsdyrc746"),
    (("worker746", "a"), "worker746"),
    (("worker746", "zz"), "vnqjdq746"),
    (("worker746", "AgentU"), "wuvxxl746"),
    (("worker746", "keyboard"), "gsplsr746"),
    (("worker746", "AA"), "worker746"),
    (("kernel746", "key"), "uipxij746"),
    (("kernel746", "lemon"), "vidbrw746"),
    (("kernel746", "a"), "kernel746"),
    (("kernel746", "zz"), "jdqmdk746"),
    (("kernel746", "AgentU"), "kkvaxf746"),
    (("kernel746", "keyboard"), "uiposl746"),
    (("kernel746", "AA"), "kernel746"),
    (("signal746", "key"), "cmexej746"),
    (("signal746", "lemon"), "dmsbnw746"),
    (("signal746", "a"), "signal746"),
    (("signal746", "zz"), "rhfmzk746"),
    (("signal746", "AgentU"), "sokatf746"),
    (("signal746", "keyboard"), "cmeool746"),
    (("signal746", "AA"), "signal746"),
    (("packet746", "key"), "zeauir746"),
    (("packet746", "lemon"), "aeoyre746"),
    (("packet746", "a"), "packet746"),
    (("packet746", "zz"), "ozbjds746"),
    (("packet746", "AgentU"), "pggxxn746"),
    (("packet746", "keyboard"), "zealst746"),
    (("packet746", "AA"), "packet746"),
    (("router746", "key"), "bssdip746"),
    (("router746", "lemon"), "csghrc746"),
    (("router746", "a"), "router746"),
    (("router746", "zz"), "qntsdq746"),
    (("router746", "AgentU"), "ruygxl746"),
    (("router746", "keyboard"), "bssusr746"),
    (("router746", "AA"), "router746"),
    (("cluster746", "key"), "mpscxcb746"),
    (("cluster746", "lemon"), "npgggpv746"),
    (("cluster746", "a"), "cluster746"),
    (("cluster746", "zz"), "bktrsdq746"),
    (("cluster746", "AgentU"), "cryfmyr746"),
    (("cluster746", "keyboard"), "mpsthei746"),
    (("cluster746", "AA"), "cluster746"),
    (("mirror746", "key"), "wmpbsp746"),
    (("mirror746", "lemon"), "xmdfbc746"),
    (("mirror746", "a"), "mirror746"),
    (("mirror746", "zz"), "lhqqnq746"),
    (("mirror746", "AgentU"), "movehl746"),
    (("mirror746", "keyboard"), "wmpscr746"),
    (("mirror746", "AA"), "mirror746"),
    (("filter746", "key"), "pmjdip746"),
    (("filter746", "lemon"), "qmxhrc746"),
    (("filter746", "a"), "filter746"),
    (("filter746", "zz"), "ehksdq746"),
    (("filter746", "AgentU"), "fopgxl746"),
    (("filter746", "keyboard"), "pmjusr746"),
    (("filter746", "AA"), "filter746"),
    (("ranking746", "key"), "belumlq746"),
    (("ranking746", "lemon"), "cezyvyk746"),
    (("ranking746", "a"), "ranking746"),
    (("ranking746", "zz"), "qzmjhmf746"),
    (("ranking746", "AgentU"), "rgrxbhg746"),
    (("ranking746", "keyboard"), "bellwnx746"),
    (("ranking746", "AA"), "ranking746"),
    (("encoding746", "key"), "orayhgxk746"),
    (("encoding746", "lemon"), "procqtrs746"),
    (("encoding746", "a"), "encoding746"),
    (("encoding746", "zz"), "dmbnchmf746"),
    (("encoding746", "AgentU"), "etgbwcnm746"),
    (("encoding746", "keyboard"), "orapriej746"),
    (("encoding746", "AA"), "encoding746"),
    (("mapping746", "key"), "wenzmlq746"),
    (("mapping746", "lemon"), "xebdvyk746"),
    (("mapping746", "a"), "mapping746"),
    (("mapping746", "zz"), "lzoohmf746"),
    (("mapping746", "AgentU"), "mgtcbhg746"),
    (("mapping746", "keyboard"), "wenqwnx746"),
    (("mapping746", "AA"), "mapping746"),
    (("record746", "key"), "biayvb746"),
    (("record746", "lemon"), "cioceo746"),
    (("record746", "a"), "record746"),
    (("record746", "zz"), "qdbnqc746"),
    (("record746", "AgentU"), "rkgbkx746"),
    (("record746", "keyboard"), "biapfd746"),
    (("record746", "AA"), "record746"),
    (("candle746", "key"), "melnpc746"),
    (("candle746", "lemon"), "nezryp746"),
    (("candle746", "a"), "candle746"),
    (("candle746", "zz"), "bzmckd746"),
    (("candle746", "AgentU"), "cgrqey746"),
    (("candle746", "keyboard"), "meleze746"),
    (("candle746", "AA"), "candle746"),
    (("thread746", "key"), "dlpoeb746"),
    (("thread746", "lemon"), "eldsno746"),
    (("thread746", "a"), "thread746"),
    (("thread746", "zz"), "sgqdzc746"),
    (("thread746", "AgentU"), "tnvrtx746"),
    (("thread746", "keyboard"), "dlpfod746"),
    (("thread746", "AA"), "thread746"),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 746: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 746: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "a"),
        "round 746: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 746: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 746: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 746: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", "AA"),
        "round 746: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "key"),
        "bssxh 746: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 746: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "a"),
        "round 746: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 746: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 746: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 746: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", "AA"),
        "round 746: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 746: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 746: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "a"),
        "round 746: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 746: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 746: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 746: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", "AA"),
        "round 746: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 746: the processor reads the record then stops", "key"),
        "bssxh 746: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 746: the processor reads the record then stops", "lemon"),
        "csgbq 746: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 746: the processor reads the record then stops", "a"),
        "round 746: the processor reads the record then stops",
    ),
    (
        ("round 746: the processor reads the record then stops", "zz"),
        "qntmc 746: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 746: the processor reads the record then stops", "AgentU"),
        "ruyaw 746: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 746: the processor reads the record then stops", "keyboard"),
        "bssor 746: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 746: the processor reads the record then stops", "AA"),
        "round 746: the processor reads the record then stops",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "key"),
        "bssxh 746: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "lemon"),
        "csgbq 746: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "a"),
        "round 746: a worker pulls the next task from the queue",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "zz"),
        "qntmc 746: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 746: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "keyboard"),
        "bssor 746: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 746: a worker pulls the next task from the queue", "AA"),
        "round 746: a worker pulls the next task from the queue",
    ),
    (
        ("round 746: signals travel through the network layer", "key"),
        "bssxh 746: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 746: signals travel through the network layer", "lemon"),
        "csgbq 746: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 746: signals travel through the network layer", "a"),
        "round 746: signals travel through the network layer",
    ),
    (
        ("round 746: signals travel through the network layer", "zz"),
        "qntmc 746: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 746: signals travel through the network layer", "AgentU"),
        "ruyaw 746: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 746: signals travel through the network layer", "keyboard"),
        "bssor 746: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 746: signals travel through the network layer", "AA"),
        "round 746: signals travel through the network layer",
    ),
    (
        ("round 746: the gateway routes each request by policy", "key"),
        "bssxh 746: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 746: the gateway routes each request by policy", "lemon"),
        "csgbq 746: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 746: the gateway routes each request by policy", "a"),
        "round 746: the gateway routes each request by policy",
    ),
    (
        ("round 746: the gateway routes each request by policy", "zz"),
        "qntmc 746: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 746: the gateway routes each request by policy", "AgentU"),
        "ruyaw 746: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 746: the gateway routes each request by policy", "keyboard"),
        "bssor 746: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 746: the gateway routes each request by policy", "AA"),
        "round 746: the gateway routes each request by policy",
    ),
    (("round 746: memory grows until the buffer is full", "key"), "bssxh 746: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 746: memory grows until the buffer is full", "lemon"), "csgbq 746: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 746: memory grows until the buffer is full", "a"), "round 746: memory grows until the buffer is full"),
    (("round 746: memory grows until the buffer is full", "zz"), "qntmc 746: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 746: memory grows until the buffer is full", "AgentU"),
        "ruyaw 746: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 746: memory grows until the buffer is full", "keyboard"),
        "bssor 746: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 746: memory grows until the buffer is full", "AA"), "round 746: memory grows until the buffer is full"),
    (("round 746: the cluster mirrors every packet twice", "key"), "bssxh 746: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 746: the cluster mirrors every packet twice", "lemon"),
        "csgbq 746: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 746: the cluster mirrors every packet twice", "a"), "round 746: the cluster mirrors every packet twice"),
    (("round 746: the cluster mirrors every packet twice", "zz"), "qntmc 746: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 746: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 746: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 746: the cluster mirrors every packet twice", "keyboard"),
        "bssor 746: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 746: the cluster mirrors every packet twice", "AA"), "round 746: the cluster mirrors every packet twice"),
    (
        ("round 746: ranking uses tokens learned from the corpus", "key"),
        "bssxh 746: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 746: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", "a"),
        "round 746: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 746: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 746: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 746: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", "AA"),
        "round 746: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 746: a long session ends when the candle dies", "key"),
        "bssxh 746: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 746: a long session ends when the candle dies", "lemon"),
        "csgbq 746: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 746: a long session ends when the candle dies", "a"),
        "round 746: a long session ends when the candle dies",
    ),
    (
        ("round 746: a long session ends when the candle dies", "zz"),
        "qntmc 746: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 746: a long session ends when the candle dies", "AgentU"),
        "ruyaw 746: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 746: a long session ends when the candle dies", "keyboard"),
        "bssor 746: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 746: a long session ends when the candle dies", "AA"),
        "round 746: a long session ends when the candle dies",
    ),
    (("round 746: encode the prompt then map the result", "key"), "bssxh 746: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 746: encode the prompt then map the result", "lemon"), "csgbq 746: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 746: encode the prompt then map the result", "a"), "round 746: encode the prompt then map the result"),
    (("round 746: encode the prompt then map the result", "zz"), "qntmc 746: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 746: encode the prompt then map the result", "AgentU"),
        "ruyaw 746: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 746: encode the prompt then map the result", "keyboard"),
        "bssor 746: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 746: encode the prompt then map the result", "AA"), "round 746: encode the prompt then map the result"),
    (("round 746: the kernel wakes the worker at dawn", "key"), "bssxh 746: rri iovlop ukocc xfo ambocb er neux"),
    (("round 746: the kernel wakes the worker at dawn", "lemon"), "csgbq 746: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 746: the kernel wakes the worker at dawn", "a"), "round 746: the kernel wakes the worker at dawn"),
    (("round 746: the kernel wakes the worker at dawn", "zz"), "qntmc 746: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 746: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 746: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 746: the kernel wakes the worker at dawn", "keyboard"), "bssor 746: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 746: the kernel wakes the worker at dawn", "AA"), "round 746: the kernel wakes the worker at dawn"),
    (("round 746: service latency drops after the patch", "key"), "bssxh 746: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 746: service latency drops after the patch", "lemon"), "csgbq 746: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 746: service latency drops after the patch", "a"), "round 746: service latency drops after the patch"),
    (("round 746: service latency drops after the patch", "zz"), "qntmc 746: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 746: service latency drops after the patch", "AgentU"),
        "ruyaw 746: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 746: service latency drops after the patch", "keyboard"),
        "bssor 746: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 746: service latency drops after the patch", "AA"), "round 746: service latency drops after the patch"),
    (
        ("round 746: the library caches every vector it sees", "key"),
        "bssxh 746: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 746: the library caches every vector it sees", "lemon"),
        "csgbq 746: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 746: the library caches every vector it sees", "a"), "round 746: the library caches every vector it sees"),
    (
        ("round 746: the library caches every vector it sees", "zz"),
        "qntmc 746: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 746: the library caches every vector it sees", "AgentU"),
        "ruyaw 746: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 746: the library caches every vector it sees", "keyboard"),
        "bssor 746: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 746: the library caches every vector it sees", "AA"),
        "round 746: the library caches every vector it sees",
    ),
    (("round 746: agents argue then the debate resolves", "key"), "bssxh 746: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 746: agents argue then the debate resolves", "lemon"), "csgbq 746: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 746: agents argue then the debate resolves", "a"), "round 746: agents argue then the debate resolves"),
    (("round 746: agents argue then the debate resolves", "zz"), "qntmc 746: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 746: agents argue then the debate resolves", "AgentU"),
        "ruyaw 746: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 746: agents argue then the debate resolves", "keyboard"),
        "bssor 746: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 746: agents argue then the debate resolves", "AA"), "round 746: agents argue then the debate resolves"),
    (("round 746: the filter keeps only strong matches", "key"), "bssxh 746: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 746: the filter keeps only strong matches", "lemon"), "csgbq 746: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 746: the filter keeps only strong matches", "a"), "round 746: the filter keeps only strong matches"),
    (("round 746: the filter keeps only strong matches", "zz"), "qntmc 746: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 746: the filter keeps only strong matches", "AgentU"), "ruyaw 746: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 746: the filter keeps only strong matches", "keyboard"),
        "bssor 746: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 746: the filter keeps only strong matches", "AA"), "round 746: the filter keeps only strong matches"),
    (("round 746: the model answers with a short reply", "key"), "bssxh 746: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 746: the model answers with a short reply", "lemon"), "csgbq 746: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 746: the model answers with a short reply", "a"), "round 746: the model answers with a short reply"),
    (("round 746: the model answers with a short reply", "zz"), "qntmc 746: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 746: the model answers with a short reply", "AgentU"), "ruyaw 746: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 746: the model answers with a short reply", "keyboard"),
        "bssor 746: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 746: the model answers with a short reply", "AA"), "round 746: the model answers with a short reply"),
    (
        ("round 746: the recorder stores the reasoning trace", "key"),
        "bssxh 746: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 746: the recorder stores the reasoning trace", "lemon"),
        "csgbq 746: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 746: the recorder stores the reasoning trace", "a"), "round 746: the recorder stores the reasoning trace"),
    (
        ("round 746: the recorder stores the reasoning trace", "zz"),
        "qntmc 746: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 746: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 746: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 746: the recorder stores the reasoning trace", "keyboard"),
        "bssor 746: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 746: the recorder stores the reasoning trace", "AA"),
        "round 746: the recorder stores the reasoning trace",
    ),
    (("round 746: the angel watches the processor run", "key"), "bssxh 746: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 746: the angel watches the processor run", "lemon"), "csgbq 746: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 746: the angel watches the processor run", "a"), "round 746: the angel watches the processor run"),
    (("round 746: the angel watches the processor run", "zz"), "qntmc 746: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 746: the angel watches the processor run", "AgentU"), "ruyaw 746: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 746: the angel watches the processor run", "keyboard"), "bssor 746: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 746: the angel watches the processor run", "AA"), "round 746: the angel watches the processor run"),
    (("round 746: angle of the vector decides the match", "key"), "bssxh 746: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 746: angle of the vector decides the match", "lemon"), "csgbq 746: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 746: angle of the vector decides the match", "a"), "round 746: angle of the vector decides the match"),
    (("round 746: angle of the vector decides the match", "zz"), "qntmc 746: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 746: angle of the vector decides the match", "AgentU"),
        "ruyaw 746: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 746: angle of the vector decides the match", "keyboard"),
        "bssor 746: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 746: angle of the vector decides the match", "AA"), "round 746: angle of the vector decides the match"),
    (
        ("round 746: the candle burns twice as long at night", "key"),
        "bssxh 746: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 746: the candle burns twice as long at night", "lemon"),
        "csgbq 746: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 746: the candle burns twice as long at night", "a"), "round 746: the candle burns twice as long at night"),
    (
        ("round 746: the candle burns twice as long at night", "zz"),
        "qntmc 746: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 746: the candle burns twice as long at night", "AgentU"),
        "ruyaw 746: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 746: the candle burns twice as long at night", "keyboard"),
        "bssor 746: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 746: the candle burns twice as long at night", "AA"),
        "round 746: the candle burns twice as long at night",
    ),
    (("round 746: a mirror of the universe in one line", "key"), "bssxh 746: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 746: a mirror of the universe in one line", "lemon"), "csgbq 746: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 746: a mirror of the universe in one line", "a"), "round 746: a mirror of the universe in one line"),
    (("round 746: a mirror of the universe in one line", "zz"), "qntmc 746: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 746: a mirror of the universe in one line", "AgentU"), "ruyaw 746: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 746: a mirror of the universe in one line", "keyboard"),
        "bssor 746: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 746: a mirror of the universe in one line", "AA"), "round 746: a mirror of the universe in one line"),
    (("round 746: the queue drains before the storm", "key"), "bssxh 746: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 746: the queue drains before the storm", "lemon"), "csgbq 746: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 746: the queue drains before the storm", "a"), "round 746: the queue drains before the storm"),
    (("round 746: the queue drains before the storm", "zz"), "qntmc 746: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 746: the queue drains before the storm", "AgentU"), "ruyaw 746: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 746: the queue drains before the storm", "keyboard"), "bssor 746: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 746: the queue drains before the storm", "AA"), "round 746: the queue drains before the storm"),
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
