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
    (("kitten183", "key"), "umrdil183"),
    (("kitten183", "lemon"), "vmfhry183"),
    (("kitten183", "a"), "kitten183"),
    (("kitten183", "zz"), "jhssdm183"),
    (("kitten183", "AgentU"), "koxgxh183"),
    (("kitten183", "keyboard"), "umrusn183"),
    (("kitten183", "AA"), "kitten183"),
    (("sitting183", "key"), "cmrdmlq183"),
    (("sitting183", "lemon"), "dmfhvyk183"),
    (("sitting183", "a"), "sitting183"),
    (("sitting183", "zz"), "rhsshmf183"),
    (("sitting183", "AgentU"), "soxgbhg183"),
    (("sitting183", "keyboard"), "cmruwnx183"),
    (("sitting183", "AA"), "sitting183"),
    (("agent183", "key"), "kkcxx183"),
    (("agent183", "lemon"), "lkqbg183"),
    (("agent183", "a"), "agent183"),
    (("agent183", "zz"), "zfdms183"),
    (("agent183", "AgentU"), "amiam183"),
    (("agent183", "keyboard"), "kkcoh183"),
    (("agent183", "AA"), "agent183"),
    (("angle183", "key"), "krevi183"),
    (("angle183", "lemon"), "lrszr183"),
    (("angle183", "a"), "angle183"),
    (("angle183", "zz"), "zmfkd183"),
    (("angle183", "AgentU"), "atkyx183"),
    (("angle183", "keyboard"), "krems183"),
    (("angle183", "AA"), "angle183"),
    (("universe183", "key"), "ergfipci183"),
    (("universe183", "lemon"), "frujrcwq183"),
    (("universe183", "a"), "universe183"),
    (("universe183", "zz"), "tmhudqrd183"),
    (("universe183", "AgentU"), "utmixlsk183"),
    (("universe183", "keyboard"), "ergwsrjh183"),
    (("universe183", "AA"), "universe183"),
    (("memory183", "key"), "wikyvw183"),
    (("memory183", "lemon"), "xiycej183"),
    (("memory183", "a"), "memory183"),
    (("memory183", "zz"), "ldlnqx183"),
    (("memory183", "AgentU"), "mkqbks183"),
    (("memory183", "keyboard"), "wikpfy183"),
    (("memory183", "AA"), "memory183"),
    (("stream183", "key"), "cxpoek183"),
    (("stream183", "lemon"), "dxdsnx183"),
    (("stream183", "a"), "stream183"),
    (("stream183", "zz"), "rsqdzl183"),
    (("stream183", "AgentU"), "szvrtg183"),
    (("stream183", "keyboard"), "cxpfom183"),
    (("stream183", "AA"), "stream183"),
    (("context183", "key"), "msldivd183"),
    (("context183", "lemon"), "nszhrix183"),
    (("context183", "a"), "context183"),
    (("context183", "zz"), "bnmsdws183"),
    (("context183", "AgentU"), "curgxrt183"),
    (("context183", "keyboard"), "mslusxk183"),
    (("context183", "AA"), "context183"),
    (("knowledge183", "key"), "urmgpcnkc183"),
    (("knowledge183", "lemon"), "vrakyphss183"),
    (("knowledge183", "a"), "knowledge183"),
    (("knowledge183", "zz"), "jmnvkdcfd183"),
    (("knowledge183", "AgentU"), "ktsjeydmi183"),
    (("knowledge183", "keyboard"), "urmxzeujo183"),
    (("knowledge183", "AA"), "knowledge183"),
    (("vector183", "key"), "fiadsp183"),
    (("vector183", "lemon"), "giohbc183"),
    (("vector183", "a"), "vector183"),
    (("vector183", "zz"), "udbsnq183"),
    (("vector183", "AgentU"), "vkgghl183"),
    (("vector183", "keyboard"), "fiaucr183"),
    (("vector183", "AA"), "vector183"),
    (("processor183", "key"), "zvmmiqcsp183"),
    (("processor183", "lemon"), "avaqrdwaf183"),
    (("processor183", "a"), "processor183"),
    (("processor183", "zz"), "oqnbdrrnq183"),
    (("processor183", "AgentU"), "pxspxmsuv183"),
    (("processor183", "keyboard"), "zvmdssjrb183"),
    (("processor183", "AA"), "processor183"),
    (("reasoning183", "key"), "biycslsre183"),
    (("reasoning183", "lemon"), "cimgbymzu183"),
    (("reasoning183", "a"), "reasoning183"),
    (("reasoning183", "zz"), "qdzrnmhmf183"),
    (("reasoning183", "AgentU"), "rkefhhitk183"),
    (("reasoning183", "keyboard"), "biytcnzqq183"),
    (("reasoning183", "AA"), "reasoning183"),
    (("machine183", "key"), "wearmlo183"),
    (("machine183", "lemon"), "xeovvyi183"),
    (("machine183", "a"), "machine183"),
    (("machine183", "zz"), "lzbghmd183"),
    (("machine183", "AgentU"), "mggubhe183"),
    (("machine183", "keyboard"), "weaiwnv183"),
    (("machine183", "AA"), "machine183"),
    (("learning183", "key"), "viybrgxk183"),
    (("learning183", "lemon"), "wimfatrs183"),
    (("learning183", "a"), "learning183"),
    (("learning183", "zz"), "kdzqmhmf183"),
    (("learning183", "AgentU"), "lkeegcnm183"),
    (("learning183", "keyboard"), "viysbiej183"),
    (("learning183", "AA"), "learning183"),
    (("model183", "key"), "wsbop183"),
    (("model183", "lemon"), "xspsy183"),
    (("model183", "a"), "model183"),
    (("model183", "zz"), "lncdk183"),
    (("model183", "AgentU"), "muhre183"),
    (("model183", "keyboard"), "wsbfz183"),
    (("model183", "AA"), "model183"),
    (("token183", "key"), "dsior183"),
    (("token183", "lemon"), "eswsa183"),
    (("token183", "a"), "token183"),
    (("token183", "zz"), "snjdm183"),
    (("token183", "AgentU"), "tuorg183"),
    (("token183", "keyboard"), "dsifb183"),
    (("token183", "AA"), "token183"),
    (("prompt183", "key"), "zvmwtr183"),
    (("prompt183", "lemon"), "avaace183"),
    (("prompt183", "a"), "prompt183"),
    (("prompt183", "zz"), "oqnlos183"),
    (("prompt183", "AgentU"), "pxszin183"),
    (("prompt183", "keyboard"), "zvmndt183"),
    (("prompt183", "AA"), "prompt183"),
    (("session183", "key"), "ciqcmmx183"),
    (("session183", "lemon"), "diegvzr183"),
    (("session183", "a"), "session183"),
    (("session183", "zz"), "rdrrhnm183"),
    (("session183", "AgentU"), "skwfbin183"),
    (("session183", "keyboard"), "ciqtwoe183"),
    (("session183", "AA"), "session183"),
    (("library183", "key"), "vmzbepi183"),
    (("library183", "lemon"), "wmnfncc183"),
    (("library183", "a"), "library183"),
    (("library183", "zz"), "khaqzqx183"),
    (("library183", "AgentU"), "lofetly183"),
    (("library183", "keyboard"), "vmzsorp183"),
    (("library183", "AA"), "library183"),
    (("service183", "key"), "cipfmao183"),
    (("service183", "lemon"), "didjvni183"),
    (("service183", "a"), "service183"),
    (("service183", "zz"), "rdquhbd183"),
    (("service183", "AgentU"), "skvibwe183"),
    (("service183", "keyboard"), "cipwwcv183"),
    (("service183", "AA"), "service183"),
    (("gateway183", "key"), "qeroayi183"),
    (("gateway183", "lemon"), "refsjlc183"),
    (("gateway183", "a"), "gateway183"),
    (("gateway183", "zz"), "fzsdvzx183"),
    (("gateway183", "AgentU"), "ggxrpuy183"),
    (("gateway183", "keyboard"), "qerfkap183"),
    (("gateway183", "AA"), "gateway183"),
    (("storage183", "key"), "cxmbeeo183"),
    (("storage183", "lemon"), "dxafnri183"),
    (("storage183", "a"), "storage183"),
    (("storage183", "zz"), "rsnqzfd183"),
    (("storage183", "AgentU"), "szsetae183"),
    (("storage183", "keyboard"), "cxmsogv183"),
    (("storage183", "AA"), "storage183"),
    (("network183", "key"), "xirgspu183"),
    (("network183", "lemon"), "yifkbco183"),
    (("network183", "a"), "network183"),
    (("network183", "zz"), "mdsvnqj183"),
    (("network183", "AgentU"), "nkxjhlk183"),
    (("network183", "keyboard"), "xirxcrb183"),
    (("network183", "AA"), "network183"),
    (("latency183", "key"), "verorai183"),
    (("latency183", "lemon"), "wefsanc183"),
    (("latency183", "a"), "latency183"),
    (("latency183", "zz"), "kzsdmbx183"),
    (("latency183", "AgentU"), "lgxrgwy183"),
    (("latency183", "keyboard"), "verfbcp183"),
    (("latency183", "AA"), "latency183"),
    (("buffer183", "key"), "lydpip183"),
    (("buffer183", "lemon"), "myrtrc183"),
    (("buffer183", "a"), "buffer183"),
    (("buffer183", "zz"), "ateedq183"),
    (("buffer183", "AgentU"), "bajsxl183"),
    (("buffer183", "keyboard"), "lydgsr183"),
    (("buffer183", "AA"), "buffer183"),
    (("queue183", "key"), "aycei183"),
    (("queue183", "lemon"), "byqir183"),
    (("queue183", "a"), "queue183"),
    (("queue183", "zz"), "ptdtd183"),
    (("queue183", "AgentU"), "qaihx183"),
    (("queue183", "keyboard"), "aycvs183"),
    (("queue183", "AA"), "queue183"),
    (("worker183", "key"), "gspuip183"),
    (("worker183", "lemon"), "hsdyrc183"),
    (("worker183", "a"), "worker183"),
    (("worker183", "zz"), "vnqjdq183"),
    (("worker183", "AgentU"), "wuvxxl183"),
    (("worker183", "keyboard"), "gsplsr183"),
    (("worker183", "AA"), "worker183"),
    (("kernel183", "key"), "uipxij183"),
    (("kernel183", "lemon"), "vidbrw183"),
    (("kernel183", "a"), "kernel183"),
    (("kernel183", "zz"), "jdqmdk183"),
    (("kernel183", "AgentU"), "kkvaxf183"),
    (("kernel183", "keyboard"), "uiposl183"),
    (("kernel183", "AA"), "kernel183"),
    (("signal183", "key"), "cmexej183"),
    (("signal183", "lemon"), "dmsbnw183"),
    (("signal183", "a"), "signal183"),
    (("signal183", "zz"), "rhfmzk183"),
    (("signal183", "AgentU"), "sokatf183"),
    (("signal183", "keyboard"), "cmeool183"),
    (("signal183", "AA"), "signal183"),
    (("packet183", "key"), "zeauir183"),
    (("packet183", "lemon"), "aeoyre183"),
    (("packet183", "a"), "packet183"),
    (("packet183", "zz"), "ozbjds183"),
    (("packet183", "AgentU"), "pggxxn183"),
    (("packet183", "keyboard"), "zealst183"),
    (("packet183", "AA"), "packet183"),
    (("router183", "key"), "bssdip183"),
    (("router183", "lemon"), "csghrc183"),
    (("router183", "a"), "router183"),
    (("router183", "zz"), "qntsdq183"),
    (("router183", "AgentU"), "ruygxl183"),
    (("router183", "keyboard"), "bssusr183"),
    (("router183", "AA"), "router183"),
    (("cluster183", "key"), "mpscxcb183"),
    (("cluster183", "lemon"), "npgggpv183"),
    (("cluster183", "a"), "cluster183"),
    (("cluster183", "zz"), "bktrsdq183"),
    (("cluster183", "AgentU"), "cryfmyr183"),
    (("cluster183", "keyboard"), "mpsthei183"),
    (("cluster183", "AA"), "cluster183"),
    (("mirror183", "key"), "wmpbsp183"),
    (("mirror183", "lemon"), "xmdfbc183"),
    (("mirror183", "a"), "mirror183"),
    (("mirror183", "zz"), "lhqqnq183"),
    (("mirror183", "AgentU"), "movehl183"),
    (("mirror183", "keyboard"), "wmpscr183"),
    (("mirror183", "AA"), "mirror183"),
    (("filter183", "key"), "pmjdip183"),
    (("filter183", "lemon"), "qmxhrc183"),
    (("filter183", "a"), "filter183"),
    (("filter183", "zz"), "ehksdq183"),
    (("filter183", "AgentU"), "fopgxl183"),
    (("filter183", "keyboard"), "pmjusr183"),
    (("filter183", "AA"), "filter183"),
    (("ranking183", "key"), "belumlq183"),
    (("ranking183", "lemon"), "cezyvyk183"),
    (("ranking183", "a"), "ranking183"),
    (("ranking183", "zz"), "qzmjhmf183"),
    (("ranking183", "AgentU"), "rgrxbhg183"),
    (("ranking183", "keyboard"), "bellwnx183"),
    (("ranking183", "AA"), "ranking183"),
    (("encoding183", "key"), "orayhgxk183"),
    (("encoding183", "lemon"), "procqtrs183"),
    (("encoding183", "a"), "encoding183"),
    (("encoding183", "zz"), "dmbnchmf183"),
    (("encoding183", "AgentU"), "etgbwcnm183"),
    (("encoding183", "keyboard"), "orapriej183"),
    (("encoding183", "AA"), "encoding183"),
    (("mapping183", "key"), "wenzmlq183"),
    (("mapping183", "lemon"), "xebdvyk183"),
    (("mapping183", "a"), "mapping183"),
    (("mapping183", "zz"), "lzoohmf183"),
    (("mapping183", "AgentU"), "mgtcbhg183"),
    (("mapping183", "keyboard"), "wenqwnx183"),
    (("mapping183", "AA"), "mapping183"),
    (("record183", "key"), "biayvb183"),
    (("record183", "lemon"), "cioceo183"),
    (("record183", "a"), "record183"),
    (("record183", "zz"), "qdbnqc183"),
    (("record183", "AgentU"), "rkgbkx183"),
    (("record183", "keyboard"), "biapfd183"),
    (("record183", "AA"), "record183"),
    (("candle183", "key"), "melnpc183"),
    (("candle183", "lemon"), "nezryp183"),
    (("candle183", "a"), "candle183"),
    (("candle183", "zz"), "bzmckd183"),
    (("candle183", "AgentU"), "cgrqey183"),
    (("candle183", "keyboard"), "meleze183"),
    (("candle183", "AA"), "candle183"),
    (("thread183", "key"), "dlpoeb183"),
    (("thread183", "lemon"), "eldsno183"),
    (("thread183", "a"), "thread183"),
    (("thread183", "zz"), "sgqdzc183"),
    (("thread183", "AgentU"), "tnvrtx183"),
    (("thread183", "keyboard"), "dlpfod183"),
    (("thread183", "AA"), "thread183"),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 183: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 183: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "a"),
        "round 183: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 183: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 183: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 183: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", "AA"),
        "round 183: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "key"),
        "bssxh 183: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 183: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "a"),
        "round 183: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 183: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 183: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 183: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", "AA"),
        "round 183: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 183: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 183: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "a"),
        "round 183: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 183: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 183: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 183: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", "AA"),
        "round 183: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 183: the processor reads the record then stops", "key"),
        "bssxh 183: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 183: the processor reads the record then stops", "lemon"),
        "csgbq 183: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 183: the processor reads the record then stops", "a"),
        "round 183: the processor reads the record then stops",
    ),
    (
        ("round 183: the processor reads the record then stops", "zz"),
        "qntmc 183: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 183: the processor reads the record then stops", "AgentU"),
        "ruyaw 183: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 183: the processor reads the record then stops", "keyboard"),
        "bssor 183: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 183: the processor reads the record then stops", "AA"),
        "round 183: the processor reads the record then stops",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "key"),
        "bssxh 183: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "lemon"),
        "csgbq 183: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "a"),
        "round 183: a worker pulls the next task from the queue",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "zz"),
        "qntmc 183: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 183: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "keyboard"),
        "bssor 183: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 183: a worker pulls the next task from the queue", "AA"),
        "round 183: a worker pulls the next task from the queue",
    ),
    (
        ("round 183: signals travel through the network layer", "key"),
        "bssxh 183: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 183: signals travel through the network layer", "lemon"),
        "csgbq 183: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 183: signals travel through the network layer", "a"),
        "round 183: signals travel through the network layer",
    ),
    (
        ("round 183: signals travel through the network layer", "zz"),
        "qntmc 183: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 183: signals travel through the network layer", "AgentU"),
        "ruyaw 183: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 183: signals travel through the network layer", "keyboard"),
        "bssor 183: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 183: signals travel through the network layer", "AA"),
        "round 183: signals travel through the network layer",
    ),
    (
        ("round 183: the gateway routes each request by policy", "key"),
        "bssxh 183: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 183: the gateway routes each request by policy", "lemon"),
        "csgbq 183: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 183: the gateway routes each request by policy", "a"),
        "round 183: the gateway routes each request by policy",
    ),
    (
        ("round 183: the gateway routes each request by policy", "zz"),
        "qntmc 183: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 183: the gateway routes each request by policy", "AgentU"),
        "ruyaw 183: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 183: the gateway routes each request by policy", "keyboard"),
        "bssor 183: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 183: the gateway routes each request by policy", "AA"),
        "round 183: the gateway routes each request by policy",
    ),
    (("round 183: memory grows until the buffer is full", "key"), "bssxh 183: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 183: memory grows until the buffer is full", "lemon"), "csgbq 183: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 183: memory grows until the buffer is full", "a"), "round 183: memory grows until the buffer is full"),
    (("round 183: memory grows until the buffer is full", "zz"), "qntmc 183: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 183: memory grows until the buffer is full", "AgentU"),
        "ruyaw 183: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 183: memory grows until the buffer is full", "keyboard"),
        "bssor 183: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 183: memory grows until the buffer is full", "AA"), "round 183: memory grows until the buffer is full"),
    (("round 183: the cluster mirrors every packet twice", "key"), "bssxh 183: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 183: the cluster mirrors every packet twice", "lemon"),
        "csgbq 183: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 183: the cluster mirrors every packet twice", "a"), "round 183: the cluster mirrors every packet twice"),
    (("round 183: the cluster mirrors every packet twice", "zz"), "qntmc 183: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 183: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 183: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 183: the cluster mirrors every packet twice", "keyboard"),
        "bssor 183: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 183: the cluster mirrors every packet twice", "AA"), "round 183: the cluster mirrors every packet twice"),
    (
        ("round 183: ranking uses tokens learned from the corpus", "key"),
        "bssxh 183: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 183: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", "a"),
        "round 183: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 183: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 183: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 183: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", "AA"),
        "round 183: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 183: a long session ends when the candle dies", "key"),
        "bssxh 183: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 183: a long session ends when the candle dies", "lemon"),
        "csgbq 183: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 183: a long session ends when the candle dies", "a"),
        "round 183: a long session ends when the candle dies",
    ),
    (
        ("round 183: a long session ends when the candle dies", "zz"),
        "qntmc 183: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 183: a long session ends when the candle dies", "AgentU"),
        "ruyaw 183: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 183: a long session ends when the candle dies", "keyboard"),
        "bssor 183: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 183: a long session ends when the candle dies", "AA"),
        "round 183: a long session ends when the candle dies",
    ),
    (("round 183: encode the prompt then map the result", "key"), "bssxh 183: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 183: encode the prompt then map the result", "lemon"), "csgbq 183: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 183: encode the prompt then map the result", "a"), "round 183: encode the prompt then map the result"),
    (("round 183: encode the prompt then map the result", "zz"), "qntmc 183: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 183: encode the prompt then map the result", "AgentU"),
        "ruyaw 183: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 183: encode the prompt then map the result", "keyboard"),
        "bssor 183: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 183: encode the prompt then map the result", "AA"), "round 183: encode the prompt then map the result"),
    (("round 183: the kernel wakes the worker at dawn", "key"), "bssxh 183: rri iovlop ukocc xfo ambocb er neux"),
    (("round 183: the kernel wakes the worker at dawn", "lemon"), "csgbq 183: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 183: the kernel wakes the worker at dawn", "a"), "round 183: the kernel wakes the worker at dawn"),
    (("round 183: the kernel wakes the worker at dawn", "zz"), "qntmc 183: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 183: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 183: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 183: the kernel wakes the worker at dawn", "keyboard"), "bssor 183: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 183: the kernel wakes the worker at dawn", "AA"), "round 183: the kernel wakes the worker at dawn"),
    (("round 183: service latency drops after the patch", "key"), "bssxh 183: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 183: service latency drops after the patch", "lemon"), "csgbq 183: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 183: service latency drops after the patch", "a"), "round 183: service latency drops after the patch"),
    (("round 183: service latency drops after the patch", "zz"), "qntmc 183: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 183: service latency drops after the patch", "AgentU"),
        "ruyaw 183: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 183: service latency drops after the patch", "keyboard"),
        "bssor 183: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 183: service latency drops after the patch", "AA"), "round 183: service latency drops after the patch"),
    (
        ("round 183: the library caches every vector it sees", "key"),
        "bssxh 183: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 183: the library caches every vector it sees", "lemon"),
        "csgbq 183: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 183: the library caches every vector it sees", "a"), "round 183: the library caches every vector it sees"),
    (
        ("round 183: the library caches every vector it sees", "zz"),
        "qntmc 183: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 183: the library caches every vector it sees", "AgentU"),
        "ruyaw 183: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 183: the library caches every vector it sees", "keyboard"),
        "bssor 183: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 183: the library caches every vector it sees", "AA"),
        "round 183: the library caches every vector it sees",
    ),
    (("round 183: agents argue then the debate resolves", "key"), "bssxh 183: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 183: agents argue then the debate resolves", "lemon"), "csgbq 183: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 183: agents argue then the debate resolves", "a"), "round 183: agents argue then the debate resolves"),
    (("round 183: agents argue then the debate resolves", "zz"), "qntmc 183: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 183: agents argue then the debate resolves", "AgentU"),
        "ruyaw 183: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 183: agents argue then the debate resolves", "keyboard"),
        "bssor 183: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 183: agents argue then the debate resolves", "AA"), "round 183: agents argue then the debate resolves"),
    (("round 183: the filter keeps only strong matches", "key"), "bssxh 183: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 183: the filter keeps only strong matches", "lemon"), "csgbq 183: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 183: the filter keeps only strong matches", "a"), "round 183: the filter keeps only strong matches"),
    (("round 183: the filter keeps only strong matches", "zz"), "qntmc 183: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 183: the filter keeps only strong matches", "AgentU"), "ruyaw 183: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 183: the filter keeps only strong matches", "keyboard"),
        "bssor 183: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 183: the filter keeps only strong matches", "AA"), "round 183: the filter keeps only strong matches"),
    (("round 183: the model answers with a short reply", "key"), "bssxh 183: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 183: the model answers with a short reply", "lemon"), "csgbq 183: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 183: the model answers with a short reply", "a"), "round 183: the model answers with a short reply"),
    (("round 183: the model answers with a short reply", "zz"), "qntmc 183: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 183: the model answers with a short reply", "AgentU"), "ruyaw 183: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 183: the model answers with a short reply", "keyboard"),
        "bssor 183: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 183: the model answers with a short reply", "AA"), "round 183: the model answers with a short reply"),
    (
        ("round 183: the recorder stores the reasoning trace", "key"),
        "bssxh 183: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 183: the recorder stores the reasoning trace", "lemon"),
        "csgbq 183: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 183: the recorder stores the reasoning trace", "a"), "round 183: the recorder stores the reasoning trace"),
    (
        ("round 183: the recorder stores the reasoning trace", "zz"),
        "qntmc 183: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 183: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 183: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 183: the recorder stores the reasoning trace", "keyboard"),
        "bssor 183: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 183: the recorder stores the reasoning trace", "AA"),
        "round 183: the recorder stores the reasoning trace",
    ),
    (("round 183: the angel watches the processor run", "key"), "bssxh 183: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 183: the angel watches the processor run", "lemon"), "csgbq 183: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 183: the angel watches the processor run", "a"), "round 183: the angel watches the processor run"),
    (("round 183: the angel watches the processor run", "zz"), "qntmc 183: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 183: the angel watches the processor run", "AgentU"), "ruyaw 183: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 183: the angel watches the processor run", "keyboard"), "bssor 183: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 183: the angel watches the processor run", "AA"), "round 183: the angel watches the processor run"),
    (("round 183: angle of the vector decides the match", "key"), "bssxh 183: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 183: angle of the vector decides the match", "lemon"), "csgbq 183: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 183: angle of the vector decides the match", "a"), "round 183: angle of the vector decides the match"),
    (("round 183: angle of the vector decides the match", "zz"), "qntmc 183: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 183: angle of the vector decides the match", "AgentU"),
        "ruyaw 183: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 183: angle of the vector decides the match", "keyboard"),
        "bssor 183: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 183: angle of the vector decides the match", "AA"), "round 183: angle of the vector decides the match"),
    (
        ("round 183: the candle burns twice as long at night", "key"),
        "bssxh 183: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 183: the candle burns twice as long at night", "lemon"),
        "csgbq 183: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 183: the candle burns twice as long at night", "a"), "round 183: the candle burns twice as long at night"),
    (
        ("round 183: the candle burns twice as long at night", "zz"),
        "qntmc 183: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 183: the candle burns twice as long at night", "AgentU"),
        "ruyaw 183: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 183: the candle burns twice as long at night", "keyboard"),
        "bssor 183: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 183: the candle burns twice as long at night", "AA"),
        "round 183: the candle burns twice as long at night",
    ),
    (("round 183: a mirror of the universe in one line", "key"), "bssxh 183: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 183: a mirror of the universe in one line", "lemon"), "csgbq 183: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 183: a mirror of the universe in one line", "a"), "round 183: a mirror of the universe in one line"),
    (("round 183: a mirror of the universe in one line", "zz"), "qntmc 183: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 183: a mirror of the universe in one line", "AgentU"), "ruyaw 183: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 183: a mirror of the universe in one line", "keyboard"),
        "bssor 183: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 183: a mirror of the universe in one line", "AA"), "round 183: a mirror of the universe in one line"),
    (("round 183: the queue drains before the storm", "key"), "bssxh 183: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 183: the queue drains before the storm", "lemon"), "csgbq 183: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 183: the queue drains before the storm", "a"), "round 183: the queue drains before the storm"),
    (("round 183: the queue drains before the storm", "zz"), "qntmc 183: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 183: the queue drains before the storm", "AgentU"), "ruyaw 183: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 183: the queue drains before the storm", "keyboard"), "bssor 183: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 183: the queue drains before the storm", "AA"), "round 183: the queue drains before the storm"),
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
