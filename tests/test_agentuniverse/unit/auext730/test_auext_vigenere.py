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
    (("kitten730", "key"), "umrdil730"),
    (("kitten730", "lemon"), "vmfhry730"),
    (("kitten730", "a"), "kitten730"),
    (("kitten730", "zz"), "jhssdm730"),
    (("kitten730", "AgentU"), "koxgxh730"),
    (("kitten730", "keyboard"), "umrusn730"),
    (("kitten730", "AA"), "kitten730"),
    (("sitting730", "key"), "cmrdmlq730"),
    (("sitting730", "lemon"), "dmfhvyk730"),
    (("sitting730", "a"), "sitting730"),
    (("sitting730", "zz"), "rhsshmf730"),
    (("sitting730", "AgentU"), "soxgbhg730"),
    (("sitting730", "keyboard"), "cmruwnx730"),
    (("sitting730", "AA"), "sitting730"),
    (("agent730", "key"), "kkcxx730"),
    (("agent730", "lemon"), "lkqbg730"),
    (("agent730", "a"), "agent730"),
    (("agent730", "zz"), "zfdms730"),
    (("agent730", "AgentU"), "amiam730"),
    (("agent730", "keyboard"), "kkcoh730"),
    (("agent730", "AA"), "agent730"),
    (("angle730", "key"), "krevi730"),
    (("angle730", "lemon"), "lrszr730"),
    (("angle730", "a"), "angle730"),
    (("angle730", "zz"), "zmfkd730"),
    (("angle730", "AgentU"), "atkyx730"),
    (("angle730", "keyboard"), "krems730"),
    (("angle730", "AA"), "angle730"),
    (("universe730", "key"), "ergfipci730"),
    (("universe730", "lemon"), "frujrcwq730"),
    (("universe730", "a"), "universe730"),
    (("universe730", "zz"), "tmhudqrd730"),
    (("universe730", "AgentU"), "utmixlsk730"),
    (("universe730", "keyboard"), "ergwsrjh730"),
    (("universe730", "AA"), "universe730"),
    (("memory730", "key"), "wikyvw730"),
    (("memory730", "lemon"), "xiycej730"),
    (("memory730", "a"), "memory730"),
    (("memory730", "zz"), "ldlnqx730"),
    (("memory730", "AgentU"), "mkqbks730"),
    (("memory730", "keyboard"), "wikpfy730"),
    (("memory730", "AA"), "memory730"),
    (("stream730", "key"), "cxpoek730"),
    (("stream730", "lemon"), "dxdsnx730"),
    (("stream730", "a"), "stream730"),
    (("stream730", "zz"), "rsqdzl730"),
    (("stream730", "AgentU"), "szvrtg730"),
    (("stream730", "keyboard"), "cxpfom730"),
    (("stream730", "AA"), "stream730"),
    (("context730", "key"), "msldivd730"),
    (("context730", "lemon"), "nszhrix730"),
    (("context730", "a"), "context730"),
    (("context730", "zz"), "bnmsdws730"),
    (("context730", "AgentU"), "curgxrt730"),
    (("context730", "keyboard"), "mslusxk730"),
    (("context730", "AA"), "context730"),
    (("knowledge730", "key"), "urmgpcnkc730"),
    (("knowledge730", "lemon"), "vrakyphss730"),
    (("knowledge730", "a"), "knowledge730"),
    (("knowledge730", "zz"), "jmnvkdcfd730"),
    (("knowledge730", "AgentU"), "ktsjeydmi730"),
    (("knowledge730", "keyboard"), "urmxzeujo730"),
    (("knowledge730", "AA"), "knowledge730"),
    (("vector730", "key"), "fiadsp730"),
    (("vector730", "lemon"), "giohbc730"),
    (("vector730", "a"), "vector730"),
    (("vector730", "zz"), "udbsnq730"),
    (("vector730", "AgentU"), "vkgghl730"),
    (("vector730", "keyboard"), "fiaucr730"),
    (("vector730", "AA"), "vector730"),
    (("processor730", "key"), "zvmmiqcsp730"),
    (("processor730", "lemon"), "avaqrdwaf730"),
    (("processor730", "a"), "processor730"),
    (("processor730", "zz"), "oqnbdrrnq730"),
    (("processor730", "AgentU"), "pxspxmsuv730"),
    (("processor730", "keyboard"), "zvmdssjrb730"),
    (("processor730", "AA"), "processor730"),
    (("reasoning730", "key"), "biycslsre730"),
    (("reasoning730", "lemon"), "cimgbymzu730"),
    (("reasoning730", "a"), "reasoning730"),
    (("reasoning730", "zz"), "qdzrnmhmf730"),
    (("reasoning730", "AgentU"), "rkefhhitk730"),
    (("reasoning730", "keyboard"), "biytcnzqq730"),
    (("reasoning730", "AA"), "reasoning730"),
    (("machine730", "key"), "wearmlo730"),
    (("machine730", "lemon"), "xeovvyi730"),
    (("machine730", "a"), "machine730"),
    (("machine730", "zz"), "lzbghmd730"),
    (("machine730", "AgentU"), "mggubhe730"),
    (("machine730", "keyboard"), "weaiwnv730"),
    (("machine730", "AA"), "machine730"),
    (("learning730", "key"), "viybrgxk730"),
    (("learning730", "lemon"), "wimfatrs730"),
    (("learning730", "a"), "learning730"),
    (("learning730", "zz"), "kdzqmhmf730"),
    (("learning730", "AgentU"), "lkeegcnm730"),
    (("learning730", "keyboard"), "viysbiej730"),
    (("learning730", "AA"), "learning730"),
    (("model730", "key"), "wsbop730"),
    (("model730", "lemon"), "xspsy730"),
    (("model730", "a"), "model730"),
    (("model730", "zz"), "lncdk730"),
    (("model730", "AgentU"), "muhre730"),
    (("model730", "keyboard"), "wsbfz730"),
    (("model730", "AA"), "model730"),
    (("token730", "key"), "dsior730"),
    (("token730", "lemon"), "eswsa730"),
    (("token730", "a"), "token730"),
    (("token730", "zz"), "snjdm730"),
    (("token730", "AgentU"), "tuorg730"),
    (("token730", "keyboard"), "dsifb730"),
    (("token730", "AA"), "token730"),
    (("prompt730", "key"), "zvmwtr730"),
    (("prompt730", "lemon"), "avaace730"),
    (("prompt730", "a"), "prompt730"),
    (("prompt730", "zz"), "oqnlos730"),
    (("prompt730", "AgentU"), "pxszin730"),
    (("prompt730", "keyboard"), "zvmndt730"),
    (("prompt730", "AA"), "prompt730"),
    (("session730", "key"), "ciqcmmx730"),
    (("session730", "lemon"), "diegvzr730"),
    (("session730", "a"), "session730"),
    (("session730", "zz"), "rdrrhnm730"),
    (("session730", "AgentU"), "skwfbin730"),
    (("session730", "keyboard"), "ciqtwoe730"),
    (("session730", "AA"), "session730"),
    (("library730", "key"), "vmzbepi730"),
    (("library730", "lemon"), "wmnfncc730"),
    (("library730", "a"), "library730"),
    (("library730", "zz"), "khaqzqx730"),
    (("library730", "AgentU"), "lofetly730"),
    (("library730", "keyboard"), "vmzsorp730"),
    (("library730", "AA"), "library730"),
    (("service730", "key"), "cipfmao730"),
    (("service730", "lemon"), "didjvni730"),
    (("service730", "a"), "service730"),
    (("service730", "zz"), "rdquhbd730"),
    (("service730", "AgentU"), "skvibwe730"),
    (("service730", "keyboard"), "cipwwcv730"),
    (("service730", "AA"), "service730"),
    (("gateway730", "key"), "qeroayi730"),
    (("gateway730", "lemon"), "refsjlc730"),
    (("gateway730", "a"), "gateway730"),
    (("gateway730", "zz"), "fzsdvzx730"),
    (("gateway730", "AgentU"), "ggxrpuy730"),
    (("gateway730", "keyboard"), "qerfkap730"),
    (("gateway730", "AA"), "gateway730"),
    (("storage730", "key"), "cxmbeeo730"),
    (("storage730", "lemon"), "dxafnri730"),
    (("storage730", "a"), "storage730"),
    (("storage730", "zz"), "rsnqzfd730"),
    (("storage730", "AgentU"), "szsetae730"),
    (("storage730", "keyboard"), "cxmsogv730"),
    (("storage730", "AA"), "storage730"),
    (("network730", "key"), "xirgspu730"),
    (("network730", "lemon"), "yifkbco730"),
    (("network730", "a"), "network730"),
    (("network730", "zz"), "mdsvnqj730"),
    (("network730", "AgentU"), "nkxjhlk730"),
    (("network730", "keyboard"), "xirxcrb730"),
    (("network730", "AA"), "network730"),
    (("latency730", "key"), "verorai730"),
    (("latency730", "lemon"), "wefsanc730"),
    (("latency730", "a"), "latency730"),
    (("latency730", "zz"), "kzsdmbx730"),
    (("latency730", "AgentU"), "lgxrgwy730"),
    (("latency730", "keyboard"), "verfbcp730"),
    (("latency730", "AA"), "latency730"),
    (("buffer730", "key"), "lydpip730"),
    (("buffer730", "lemon"), "myrtrc730"),
    (("buffer730", "a"), "buffer730"),
    (("buffer730", "zz"), "ateedq730"),
    (("buffer730", "AgentU"), "bajsxl730"),
    (("buffer730", "keyboard"), "lydgsr730"),
    (("buffer730", "AA"), "buffer730"),
    (("queue730", "key"), "aycei730"),
    (("queue730", "lemon"), "byqir730"),
    (("queue730", "a"), "queue730"),
    (("queue730", "zz"), "ptdtd730"),
    (("queue730", "AgentU"), "qaihx730"),
    (("queue730", "keyboard"), "aycvs730"),
    (("queue730", "AA"), "queue730"),
    (("worker730", "key"), "gspuip730"),
    (("worker730", "lemon"), "hsdyrc730"),
    (("worker730", "a"), "worker730"),
    (("worker730", "zz"), "vnqjdq730"),
    (("worker730", "AgentU"), "wuvxxl730"),
    (("worker730", "keyboard"), "gsplsr730"),
    (("worker730", "AA"), "worker730"),
    (("kernel730", "key"), "uipxij730"),
    (("kernel730", "lemon"), "vidbrw730"),
    (("kernel730", "a"), "kernel730"),
    (("kernel730", "zz"), "jdqmdk730"),
    (("kernel730", "AgentU"), "kkvaxf730"),
    (("kernel730", "keyboard"), "uiposl730"),
    (("kernel730", "AA"), "kernel730"),
    (("signal730", "key"), "cmexej730"),
    (("signal730", "lemon"), "dmsbnw730"),
    (("signal730", "a"), "signal730"),
    (("signal730", "zz"), "rhfmzk730"),
    (("signal730", "AgentU"), "sokatf730"),
    (("signal730", "keyboard"), "cmeool730"),
    (("signal730", "AA"), "signal730"),
    (("packet730", "key"), "zeauir730"),
    (("packet730", "lemon"), "aeoyre730"),
    (("packet730", "a"), "packet730"),
    (("packet730", "zz"), "ozbjds730"),
    (("packet730", "AgentU"), "pggxxn730"),
    (("packet730", "keyboard"), "zealst730"),
    (("packet730", "AA"), "packet730"),
    (("router730", "key"), "bssdip730"),
    (("router730", "lemon"), "csghrc730"),
    (("router730", "a"), "router730"),
    (("router730", "zz"), "qntsdq730"),
    (("router730", "AgentU"), "ruygxl730"),
    (("router730", "keyboard"), "bssusr730"),
    (("router730", "AA"), "router730"),
    (("cluster730", "key"), "mpscxcb730"),
    (("cluster730", "lemon"), "npgggpv730"),
    (("cluster730", "a"), "cluster730"),
    (("cluster730", "zz"), "bktrsdq730"),
    (("cluster730", "AgentU"), "cryfmyr730"),
    (("cluster730", "keyboard"), "mpsthei730"),
    (("cluster730", "AA"), "cluster730"),
    (("mirror730", "key"), "wmpbsp730"),
    (("mirror730", "lemon"), "xmdfbc730"),
    (("mirror730", "a"), "mirror730"),
    (("mirror730", "zz"), "lhqqnq730"),
    (("mirror730", "AgentU"), "movehl730"),
    (("mirror730", "keyboard"), "wmpscr730"),
    (("mirror730", "AA"), "mirror730"),
    (("filter730", "key"), "pmjdip730"),
    (("filter730", "lemon"), "qmxhrc730"),
    (("filter730", "a"), "filter730"),
    (("filter730", "zz"), "ehksdq730"),
    (("filter730", "AgentU"), "fopgxl730"),
    (("filter730", "keyboard"), "pmjusr730"),
    (("filter730", "AA"), "filter730"),
    (("ranking730", "key"), "belumlq730"),
    (("ranking730", "lemon"), "cezyvyk730"),
    (("ranking730", "a"), "ranking730"),
    (("ranking730", "zz"), "qzmjhmf730"),
    (("ranking730", "AgentU"), "rgrxbhg730"),
    (("ranking730", "keyboard"), "bellwnx730"),
    (("ranking730", "AA"), "ranking730"),
    (("encoding730", "key"), "orayhgxk730"),
    (("encoding730", "lemon"), "procqtrs730"),
    (("encoding730", "a"), "encoding730"),
    (("encoding730", "zz"), "dmbnchmf730"),
    (("encoding730", "AgentU"), "etgbwcnm730"),
    (("encoding730", "keyboard"), "orapriej730"),
    (("encoding730", "AA"), "encoding730"),
    (("mapping730", "key"), "wenzmlq730"),
    (("mapping730", "lemon"), "xebdvyk730"),
    (("mapping730", "a"), "mapping730"),
    (("mapping730", "zz"), "lzoohmf730"),
    (("mapping730", "AgentU"), "mgtcbhg730"),
    (("mapping730", "keyboard"), "wenqwnx730"),
    (("mapping730", "AA"), "mapping730"),
    (("record730", "key"), "biayvb730"),
    (("record730", "lemon"), "cioceo730"),
    (("record730", "a"), "record730"),
    (("record730", "zz"), "qdbnqc730"),
    (("record730", "AgentU"), "rkgbkx730"),
    (("record730", "keyboard"), "biapfd730"),
    (("record730", "AA"), "record730"),
    (("candle730", "key"), "melnpc730"),
    (("candle730", "lemon"), "nezryp730"),
    (("candle730", "a"), "candle730"),
    (("candle730", "zz"), "bzmckd730"),
    (("candle730", "AgentU"), "cgrqey730"),
    (("candle730", "keyboard"), "meleze730"),
    (("candle730", "AA"), "candle730"),
    (("thread730", "key"), "dlpoeb730"),
    (("thread730", "lemon"), "eldsno730"),
    (("thread730", "a"), "thread730"),
    (("thread730", "zz"), "sgqdzc730"),
    (("thread730", "AgentU"), "tnvrtx730"),
    (("thread730", "keyboard"), "dlpfod730"),
    (("thread730", "AA"), "thread730"),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 730: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 730: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "a"),
        "round 730: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 730: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 730: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 730: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", "AA"),
        "round 730: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "key"),
        "bssxh 730: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 730: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "a"),
        "round 730: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 730: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 730: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 730: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", "AA"),
        "round 730: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 730: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 730: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "a"),
        "round 730: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 730: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 730: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 730: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", "AA"),
        "round 730: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 730: the processor reads the record then stops", "key"),
        "bssxh 730: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 730: the processor reads the record then stops", "lemon"),
        "csgbq 730: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 730: the processor reads the record then stops", "a"),
        "round 730: the processor reads the record then stops",
    ),
    (
        ("round 730: the processor reads the record then stops", "zz"),
        "qntmc 730: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 730: the processor reads the record then stops", "AgentU"),
        "ruyaw 730: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 730: the processor reads the record then stops", "keyboard"),
        "bssor 730: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 730: the processor reads the record then stops", "AA"),
        "round 730: the processor reads the record then stops",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "key"),
        "bssxh 730: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "lemon"),
        "csgbq 730: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "a"),
        "round 730: a worker pulls the next task from the queue",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "zz"),
        "qntmc 730: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 730: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "keyboard"),
        "bssor 730: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 730: a worker pulls the next task from the queue", "AA"),
        "round 730: a worker pulls the next task from the queue",
    ),
    (
        ("round 730: signals travel through the network layer", "key"),
        "bssxh 730: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 730: signals travel through the network layer", "lemon"),
        "csgbq 730: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 730: signals travel through the network layer", "a"),
        "round 730: signals travel through the network layer",
    ),
    (
        ("round 730: signals travel through the network layer", "zz"),
        "qntmc 730: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 730: signals travel through the network layer", "AgentU"),
        "ruyaw 730: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 730: signals travel through the network layer", "keyboard"),
        "bssor 730: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 730: signals travel through the network layer", "AA"),
        "round 730: signals travel through the network layer",
    ),
    (
        ("round 730: the gateway routes each request by policy", "key"),
        "bssxh 730: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 730: the gateway routes each request by policy", "lemon"),
        "csgbq 730: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 730: the gateway routes each request by policy", "a"),
        "round 730: the gateway routes each request by policy",
    ),
    (
        ("round 730: the gateway routes each request by policy", "zz"),
        "qntmc 730: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 730: the gateway routes each request by policy", "AgentU"),
        "ruyaw 730: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 730: the gateway routes each request by policy", "keyboard"),
        "bssor 730: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 730: the gateway routes each request by policy", "AA"),
        "round 730: the gateway routes each request by policy",
    ),
    (("round 730: memory grows until the buffer is full", "key"), "bssxh 730: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 730: memory grows until the buffer is full", "lemon"), "csgbq 730: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 730: memory grows until the buffer is full", "a"), "round 730: memory grows until the buffer is full"),
    (("round 730: memory grows until the buffer is full", "zz"), "qntmc 730: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 730: memory grows until the buffer is full", "AgentU"),
        "ruyaw 730: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 730: memory grows until the buffer is full", "keyboard"),
        "bssor 730: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 730: memory grows until the buffer is full", "AA"), "round 730: memory grows until the buffer is full"),
    (("round 730: the cluster mirrors every packet twice", "key"), "bssxh 730: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 730: the cluster mirrors every packet twice", "lemon"),
        "csgbq 730: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 730: the cluster mirrors every packet twice", "a"), "round 730: the cluster mirrors every packet twice"),
    (("round 730: the cluster mirrors every packet twice", "zz"), "qntmc 730: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 730: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 730: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 730: the cluster mirrors every packet twice", "keyboard"),
        "bssor 730: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 730: the cluster mirrors every packet twice", "AA"), "round 730: the cluster mirrors every packet twice"),
    (
        ("round 730: ranking uses tokens learned from the corpus", "key"),
        "bssxh 730: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 730: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", "a"),
        "round 730: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 730: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 730: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 730: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", "AA"),
        "round 730: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 730: a long session ends when the candle dies", "key"),
        "bssxh 730: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 730: a long session ends when the candle dies", "lemon"),
        "csgbq 730: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 730: a long session ends when the candle dies", "a"),
        "round 730: a long session ends when the candle dies",
    ),
    (
        ("round 730: a long session ends when the candle dies", "zz"),
        "qntmc 730: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 730: a long session ends when the candle dies", "AgentU"),
        "ruyaw 730: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 730: a long session ends when the candle dies", "keyboard"),
        "bssor 730: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 730: a long session ends when the candle dies", "AA"),
        "round 730: a long session ends when the candle dies",
    ),
    (("round 730: encode the prompt then map the result", "key"), "bssxh 730: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 730: encode the prompt then map the result", "lemon"), "csgbq 730: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 730: encode the prompt then map the result", "a"), "round 730: encode the prompt then map the result"),
    (("round 730: encode the prompt then map the result", "zz"), "qntmc 730: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 730: encode the prompt then map the result", "AgentU"),
        "ruyaw 730: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 730: encode the prompt then map the result", "keyboard"),
        "bssor 730: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 730: encode the prompt then map the result", "AA"), "round 730: encode the prompt then map the result"),
    (("round 730: the kernel wakes the worker at dawn", "key"), "bssxh 730: rri iovlop ukocc xfo ambocb er neux"),
    (("round 730: the kernel wakes the worker at dawn", "lemon"), "csgbq 730: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 730: the kernel wakes the worker at dawn", "a"), "round 730: the kernel wakes the worker at dawn"),
    (("round 730: the kernel wakes the worker at dawn", "zz"), "qntmc 730: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 730: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 730: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 730: the kernel wakes the worker at dawn", "keyboard"), "bssor 730: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 730: the kernel wakes the worker at dawn", "AA"), "round 730: the kernel wakes the worker at dawn"),
    (("round 730: service latency drops after the patch", "key"), "bssxh 730: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 730: service latency drops after the patch", "lemon"), "csgbq 730: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 730: service latency drops after the patch", "a"), "round 730: service latency drops after the patch"),
    (("round 730: service latency drops after the patch", "zz"), "qntmc 730: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 730: service latency drops after the patch", "AgentU"),
        "ruyaw 730: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 730: service latency drops after the patch", "keyboard"),
        "bssor 730: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 730: service latency drops after the patch", "AA"), "round 730: service latency drops after the patch"),
    (
        ("round 730: the library caches every vector it sees", "key"),
        "bssxh 730: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 730: the library caches every vector it sees", "lemon"),
        "csgbq 730: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 730: the library caches every vector it sees", "a"), "round 730: the library caches every vector it sees"),
    (
        ("round 730: the library caches every vector it sees", "zz"),
        "qntmc 730: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 730: the library caches every vector it sees", "AgentU"),
        "ruyaw 730: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 730: the library caches every vector it sees", "keyboard"),
        "bssor 730: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 730: the library caches every vector it sees", "AA"),
        "round 730: the library caches every vector it sees",
    ),
    (("round 730: agents argue then the debate resolves", "key"), "bssxh 730: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 730: agents argue then the debate resolves", "lemon"), "csgbq 730: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 730: agents argue then the debate resolves", "a"), "round 730: agents argue then the debate resolves"),
    (("round 730: agents argue then the debate resolves", "zz"), "qntmc 730: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 730: agents argue then the debate resolves", "AgentU"),
        "ruyaw 730: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 730: agents argue then the debate resolves", "keyboard"),
        "bssor 730: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 730: agents argue then the debate resolves", "AA"), "round 730: agents argue then the debate resolves"),
    (("round 730: the filter keeps only strong matches", "key"), "bssxh 730: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 730: the filter keeps only strong matches", "lemon"), "csgbq 730: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 730: the filter keeps only strong matches", "a"), "round 730: the filter keeps only strong matches"),
    (("round 730: the filter keeps only strong matches", "zz"), "qntmc 730: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 730: the filter keeps only strong matches", "AgentU"), "ruyaw 730: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 730: the filter keeps only strong matches", "keyboard"),
        "bssor 730: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 730: the filter keeps only strong matches", "AA"), "round 730: the filter keeps only strong matches"),
    (("round 730: the model answers with a short reply", "key"), "bssxh 730: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 730: the model answers with a short reply", "lemon"), "csgbq 730: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 730: the model answers with a short reply", "a"), "round 730: the model answers with a short reply"),
    (("round 730: the model answers with a short reply", "zz"), "qntmc 730: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 730: the model answers with a short reply", "AgentU"), "ruyaw 730: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 730: the model answers with a short reply", "keyboard"),
        "bssor 730: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 730: the model answers with a short reply", "AA"), "round 730: the model answers with a short reply"),
    (
        ("round 730: the recorder stores the reasoning trace", "key"),
        "bssxh 730: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 730: the recorder stores the reasoning trace", "lemon"),
        "csgbq 730: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 730: the recorder stores the reasoning trace", "a"), "round 730: the recorder stores the reasoning trace"),
    (
        ("round 730: the recorder stores the reasoning trace", "zz"),
        "qntmc 730: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 730: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 730: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 730: the recorder stores the reasoning trace", "keyboard"),
        "bssor 730: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 730: the recorder stores the reasoning trace", "AA"),
        "round 730: the recorder stores the reasoning trace",
    ),
    (("round 730: the angel watches the processor run", "key"), "bssxh 730: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 730: the angel watches the processor run", "lemon"), "csgbq 730: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 730: the angel watches the processor run", "a"), "round 730: the angel watches the processor run"),
    (("round 730: the angel watches the processor run", "zz"), "qntmc 730: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 730: the angel watches the processor run", "AgentU"), "ruyaw 730: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 730: the angel watches the processor run", "keyboard"), "bssor 730: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 730: the angel watches the processor run", "AA"), "round 730: the angel watches the processor run"),
    (("round 730: angle of the vector decides the match", "key"), "bssxh 730: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 730: angle of the vector decides the match", "lemon"), "csgbq 730: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 730: angle of the vector decides the match", "a"), "round 730: angle of the vector decides the match"),
    (("round 730: angle of the vector decides the match", "zz"), "qntmc 730: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 730: angle of the vector decides the match", "AgentU"),
        "ruyaw 730: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 730: angle of the vector decides the match", "keyboard"),
        "bssor 730: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 730: angle of the vector decides the match", "AA"), "round 730: angle of the vector decides the match"),
    (
        ("round 730: the candle burns twice as long at night", "key"),
        "bssxh 730: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 730: the candle burns twice as long at night", "lemon"),
        "csgbq 730: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 730: the candle burns twice as long at night", "a"), "round 730: the candle burns twice as long at night"),
    (
        ("round 730: the candle burns twice as long at night", "zz"),
        "qntmc 730: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 730: the candle burns twice as long at night", "AgentU"),
        "ruyaw 730: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 730: the candle burns twice as long at night", "keyboard"),
        "bssor 730: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 730: the candle burns twice as long at night", "AA"),
        "round 730: the candle burns twice as long at night",
    ),
    (("round 730: a mirror of the universe in one line", "key"), "bssxh 730: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 730: a mirror of the universe in one line", "lemon"), "csgbq 730: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 730: a mirror of the universe in one line", "a"), "round 730: a mirror of the universe in one line"),
    (("round 730: a mirror of the universe in one line", "zz"), "qntmc 730: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 730: a mirror of the universe in one line", "AgentU"), "ruyaw 730: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 730: a mirror of the universe in one line", "keyboard"),
        "bssor 730: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 730: a mirror of the universe in one line", "AA"), "round 730: a mirror of the universe in one line"),
    (("round 730: the queue drains before the storm", "key"), "bssxh 730: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 730: the queue drains before the storm", "lemon"), "csgbq 730: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 730: the queue drains before the storm", "a"), "round 730: the queue drains before the storm"),
    (("round 730: the queue drains before the storm", "zz"), "qntmc 730: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 730: the queue drains before the storm", "AgentU"), "ruyaw 730: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 730: the queue drains before the storm", "keyboard"), "bssor 730: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 730: the queue drains before the storm", "AA"), "round 730: the queue drains before the storm"),
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
