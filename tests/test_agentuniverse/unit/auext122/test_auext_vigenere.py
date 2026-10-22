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
    (("kitten122", "key"), "umrdil122"),
    (("kitten122", "lemon"), "vmfhry122"),
    (("kitten122", "a"), "kitten122"),
    (("kitten122", "zz"), "jhssdm122"),
    (("kitten122", "AgentU"), "koxgxh122"),
    (("kitten122", "keyboard"), "umrusn122"),
    (("kitten122", "AA"), "kitten122"),
    (("sitting122", "key"), "cmrdmlq122"),
    (("sitting122", "lemon"), "dmfhvyk122"),
    (("sitting122", "a"), "sitting122"),
    (("sitting122", "zz"), "rhsshmf122"),
    (("sitting122", "AgentU"), "soxgbhg122"),
    (("sitting122", "keyboard"), "cmruwnx122"),
    (("sitting122", "AA"), "sitting122"),
    (("agent122", "key"), "kkcxx122"),
    (("agent122", "lemon"), "lkqbg122"),
    (("agent122", "a"), "agent122"),
    (("agent122", "zz"), "zfdms122"),
    (("agent122", "AgentU"), "amiam122"),
    (("agent122", "keyboard"), "kkcoh122"),
    (("agent122", "AA"), "agent122"),
    (("angle122", "key"), "krevi122"),
    (("angle122", "lemon"), "lrszr122"),
    (("angle122", "a"), "angle122"),
    (("angle122", "zz"), "zmfkd122"),
    (("angle122", "AgentU"), "atkyx122"),
    (("angle122", "keyboard"), "krems122"),
    (("angle122", "AA"), "angle122"),
    (("universe122", "key"), "ergfipci122"),
    (("universe122", "lemon"), "frujrcwq122"),
    (("universe122", "a"), "universe122"),
    (("universe122", "zz"), "tmhudqrd122"),
    (("universe122", "AgentU"), "utmixlsk122"),
    (("universe122", "keyboard"), "ergwsrjh122"),
    (("universe122", "AA"), "universe122"),
    (("memory122", "key"), "wikyvw122"),
    (("memory122", "lemon"), "xiycej122"),
    (("memory122", "a"), "memory122"),
    (("memory122", "zz"), "ldlnqx122"),
    (("memory122", "AgentU"), "mkqbks122"),
    (("memory122", "keyboard"), "wikpfy122"),
    (("memory122", "AA"), "memory122"),
    (("stream122", "key"), "cxpoek122"),
    (("stream122", "lemon"), "dxdsnx122"),
    (("stream122", "a"), "stream122"),
    (("stream122", "zz"), "rsqdzl122"),
    (("stream122", "AgentU"), "szvrtg122"),
    (("stream122", "keyboard"), "cxpfom122"),
    (("stream122", "AA"), "stream122"),
    (("context122", "key"), "msldivd122"),
    (("context122", "lemon"), "nszhrix122"),
    (("context122", "a"), "context122"),
    (("context122", "zz"), "bnmsdws122"),
    (("context122", "AgentU"), "curgxrt122"),
    (("context122", "keyboard"), "mslusxk122"),
    (("context122", "AA"), "context122"),
    (("knowledge122", "key"), "urmgpcnkc122"),
    (("knowledge122", "lemon"), "vrakyphss122"),
    (("knowledge122", "a"), "knowledge122"),
    (("knowledge122", "zz"), "jmnvkdcfd122"),
    (("knowledge122", "AgentU"), "ktsjeydmi122"),
    (("knowledge122", "keyboard"), "urmxzeujo122"),
    (("knowledge122", "AA"), "knowledge122"),
    (("vector122", "key"), "fiadsp122"),
    (("vector122", "lemon"), "giohbc122"),
    (("vector122", "a"), "vector122"),
    (("vector122", "zz"), "udbsnq122"),
    (("vector122", "AgentU"), "vkgghl122"),
    (("vector122", "keyboard"), "fiaucr122"),
    (("vector122", "AA"), "vector122"),
    (("processor122", "key"), "zvmmiqcsp122"),
    (("processor122", "lemon"), "avaqrdwaf122"),
    (("processor122", "a"), "processor122"),
    (("processor122", "zz"), "oqnbdrrnq122"),
    (("processor122", "AgentU"), "pxspxmsuv122"),
    (("processor122", "keyboard"), "zvmdssjrb122"),
    (("processor122", "AA"), "processor122"),
    (("reasoning122", "key"), "biycslsre122"),
    (("reasoning122", "lemon"), "cimgbymzu122"),
    (("reasoning122", "a"), "reasoning122"),
    (("reasoning122", "zz"), "qdzrnmhmf122"),
    (("reasoning122", "AgentU"), "rkefhhitk122"),
    (("reasoning122", "keyboard"), "biytcnzqq122"),
    (("reasoning122", "AA"), "reasoning122"),
    (("machine122", "key"), "wearmlo122"),
    (("machine122", "lemon"), "xeovvyi122"),
    (("machine122", "a"), "machine122"),
    (("machine122", "zz"), "lzbghmd122"),
    (("machine122", "AgentU"), "mggubhe122"),
    (("machine122", "keyboard"), "weaiwnv122"),
    (("machine122", "AA"), "machine122"),
    (("learning122", "key"), "viybrgxk122"),
    (("learning122", "lemon"), "wimfatrs122"),
    (("learning122", "a"), "learning122"),
    (("learning122", "zz"), "kdzqmhmf122"),
    (("learning122", "AgentU"), "lkeegcnm122"),
    (("learning122", "keyboard"), "viysbiej122"),
    (("learning122", "AA"), "learning122"),
    (("model122", "key"), "wsbop122"),
    (("model122", "lemon"), "xspsy122"),
    (("model122", "a"), "model122"),
    (("model122", "zz"), "lncdk122"),
    (("model122", "AgentU"), "muhre122"),
    (("model122", "keyboard"), "wsbfz122"),
    (("model122", "AA"), "model122"),
    (("token122", "key"), "dsior122"),
    (("token122", "lemon"), "eswsa122"),
    (("token122", "a"), "token122"),
    (("token122", "zz"), "snjdm122"),
    (("token122", "AgentU"), "tuorg122"),
    (("token122", "keyboard"), "dsifb122"),
    (("token122", "AA"), "token122"),
    (("prompt122", "key"), "zvmwtr122"),
    (("prompt122", "lemon"), "avaace122"),
    (("prompt122", "a"), "prompt122"),
    (("prompt122", "zz"), "oqnlos122"),
    (("prompt122", "AgentU"), "pxszin122"),
    (("prompt122", "keyboard"), "zvmndt122"),
    (("prompt122", "AA"), "prompt122"),
    (("session122", "key"), "ciqcmmx122"),
    (("session122", "lemon"), "diegvzr122"),
    (("session122", "a"), "session122"),
    (("session122", "zz"), "rdrrhnm122"),
    (("session122", "AgentU"), "skwfbin122"),
    (("session122", "keyboard"), "ciqtwoe122"),
    (("session122", "AA"), "session122"),
    (("library122", "key"), "vmzbepi122"),
    (("library122", "lemon"), "wmnfncc122"),
    (("library122", "a"), "library122"),
    (("library122", "zz"), "khaqzqx122"),
    (("library122", "AgentU"), "lofetly122"),
    (("library122", "keyboard"), "vmzsorp122"),
    (("library122", "AA"), "library122"),
    (("service122", "key"), "cipfmao122"),
    (("service122", "lemon"), "didjvni122"),
    (("service122", "a"), "service122"),
    (("service122", "zz"), "rdquhbd122"),
    (("service122", "AgentU"), "skvibwe122"),
    (("service122", "keyboard"), "cipwwcv122"),
    (("service122", "AA"), "service122"),
    (("gateway122", "key"), "qeroayi122"),
    (("gateway122", "lemon"), "refsjlc122"),
    (("gateway122", "a"), "gateway122"),
    (("gateway122", "zz"), "fzsdvzx122"),
    (("gateway122", "AgentU"), "ggxrpuy122"),
    (("gateway122", "keyboard"), "qerfkap122"),
    (("gateway122", "AA"), "gateway122"),
    (("storage122", "key"), "cxmbeeo122"),
    (("storage122", "lemon"), "dxafnri122"),
    (("storage122", "a"), "storage122"),
    (("storage122", "zz"), "rsnqzfd122"),
    (("storage122", "AgentU"), "szsetae122"),
    (("storage122", "keyboard"), "cxmsogv122"),
    (("storage122", "AA"), "storage122"),
    (("network122", "key"), "xirgspu122"),
    (("network122", "lemon"), "yifkbco122"),
    (("network122", "a"), "network122"),
    (("network122", "zz"), "mdsvnqj122"),
    (("network122", "AgentU"), "nkxjhlk122"),
    (("network122", "keyboard"), "xirxcrb122"),
    (("network122", "AA"), "network122"),
    (("latency122", "key"), "verorai122"),
    (("latency122", "lemon"), "wefsanc122"),
    (("latency122", "a"), "latency122"),
    (("latency122", "zz"), "kzsdmbx122"),
    (("latency122", "AgentU"), "lgxrgwy122"),
    (("latency122", "keyboard"), "verfbcp122"),
    (("latency122", "AA"), "latency122"),
    (("buffer122", "key"), "lydpip122"),
    (("buffer122", "lemon"), "myrtrc122"),
    (("buffer122", "a"), "buffer122"),
    (("buffer122", "zz"), "ateedq122"),
    (("buffer122", "AgentU"), "bajsxl122"),
    (("buffer122", "keyboard"), "lydgsr122"),
    (("buffer122", "AA"), "buffer122"),
    (("queue122", "key"), "aycei122"),
    (("queue122", "lemon"), "byqir122"),
    (("queue122", "a"), "queue122"),
    (("queue122", "zz"), "ptdtd122"),
    (("queue122", "AgentU"), "qaihx122"),
    (("queue122", "keyboard"), "aycvs122"),
    (("queue122", "AA"), "queue122"),
    (("worker122", "key"), "gspuip122"),
    (("worker122", "lemon"), "hsdyrc122"),
    (("worker122", "a"), "worker122"),
    (("worker122", "zz"), "vnqjdq122"),
    (("worker122", "AgentU"), "wuvxxl122"),
    (("worker122", "keyboard"), "gsplsr122"),
    (("worker122", "AA"), "worker122"),
    (("kernel122", "key"), "uipxij122"),
    (("kernel122", "lemon"), "vidbrw122"),
    (("kernel122", "a"), "kernel122"),
    (("kernel122", "zz"), "jdqmdk122"),
    (("kernel122", "AgentU"), "kkvaxf122"),
    (("kernel122", "keyboard"), "uiposl122"),
    (("kernel122", "AA"), "kernel122"),
    (("signal122", "key"), "cmexej122"),
    (("signal122", "lemon"), "dmsbnw122"),
    (("signal122", "a"), "signal122"),
    (("signal122", "zz"), "rhfmzk122"),
    (("signal122", "AgentU"), "sokatf122"),
    (("signal122", "keyboard"), "cmeool122"),
    (("signal122", "AA"), "signal122"),
    (("packet122", "key"), "zeauir122"),
    (("packet122", "lemon"), "aeoyre122"),
    (("packet122", "a"), "packet122"),
    (("packet122", "zz"), "ozbjds122"),
    (("packet122", "AgentU"), "pggxxn122"),
    (("packet122", "keyboard"), "zealst122"),
    (("packet122", "AA"), "packet122"),
    (("router122", "key"), "bssdip122"),
    (("router122", "lemon"), "csghrc122"),
    (("router122", "a"), "router122"),
    (("router122", "zz"), "qntsdq122"),
    (("router122", "AgentU"), "ruygxl122"),
    (("router122", "keyboard"), "bssusr122"),
    (("router122", "AA"), "router122"),
    (("cluster122", "key"), "mpscxcb122"),
    (("cluster122", "lemon"), "npgggpv122"),
    (("cluster122", "a"), "cluster122"),
    (("cluster122", "zz"), "bktrsdq122"),
    (("cluster122", "AgentU"), "cryfmyr122"),
    (("cluster122", "keyboard"), "mpsthei122"),
    (("cluster122", "AA"), "cluster122"),
    (("mirror122", "key"), "wmpbsp122"),
    (("mirror122", "lemon"), "xmdfbc122"),
    (("mirror122", "a"), "mirror122"),
    (("mirror122", "zz"), "lhqqnq122"),
    (("mirror122", "AgentU"), "movehl122"),
    (("mirror122", "keyboard"), "wmpscr122"),
    (("mirror122", "AA"), "mirror122"),
    (("filter122", "key"), "pmjdip122"),
    (("filter122", "lemon"), "qmxhrc122"),
    (("filter122", "a"), "filter122"),
    (("filter122", "zz"), "ehksdq122"),
    (("filter122", "AgentU"), "fopgxl122"),
    (("filter122", "keyboard"), "pmjusr122"),
    (("filter122", "AA"), "filter122"),
    (("ranking122", "key"), "belumlq122"),
    (("ranking122", "lemon"), "cezyvyk122"),
    (("ranking122", "a"), "ranking122"),
    (("ranking122", "zz"), "qzmjhmf122"),
    (("ranking122", "AgentU"), "rgrxbhg122"),
    (("ranking122", "keyboard"), "bellwnx122"),
    (("ranking122", "AA"), "ranking122"),
    (("encoding122", "key"), "orayhgxk122"),
    (("encoding122", "lemon"), "procqtrs122"),
    (("encoding122", "a"), "encoding122"),
    (("encoding122", "zz"), "dmbnchmf122"),
    (("encoding122", "AgentU"), "etgbwcnm122"),
    (("encoding122", "keyboard"), "orapriej122"),
    (("encoding122", "AA"), "encoding122"),
    (("mapping122", "key"), "wenzmlq122"),
    (("mapping122", "lemon"), "xebdvyk122"),
    (("mapping122", "a"), "mapping122"),
    (("mapping122", "zz"), "lzoohmf122"),
    (("mapping122", "AgentU"), "mgtcbhg122"),
    (("mapping122", "keyboard"), "wenqwnx122"),
    (("mapping122", "AA"), "mapping122"),
    (("record122", "key"), "biayvb122"),
    (("record122", "lemon"), "cioceo122"),
    (("record122", "a"), "record122"),
    (("record122", "zz"), "qdbnqc122"),
    (("record122", "AgentU"), "rkgbkx122"),
    (("record122", "keyboard"), "biapfd122"),
    (("record122", "AA"), "record122"),
    (("candle122", "key"), "melnpc122"),
    (("candle122", "lemon"), "nezryp122"),
    (("candle122", "a"), "candle122"),
    (("candle122", "zz"), "bzmckd122"),
    (("candle122", "AgentU"), "cgrqey122"),
    (("candle122", "keyboard"), "meleze122"),
    (("candle122", "AA"), "candle122"),
    (("thread122", "key"), "dlpoeb122"),
    (("thread122", "lemon"), "eldsno122"),
    (("thread122", "a"), "thread122"),
    (("thread122", "zz"), "sgqdzc122"),
    (("thread122", "AgentU"), "tnvrtx122"),
    (("thread122", "keyboard"), "dlpfod122"),
    (("thread122", "AA"), "thread122"),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 122: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 122: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "a"),
        "round 122: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 122: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 122: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 122: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", "AA"),
        "round 122: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "key"),
        "bssxh 122: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 122: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "a"),
        "round 122: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 122: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 122: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 122: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", "AA"),
        "round 122: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 122: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 122: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "a"),
        "round 122: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 122: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 122: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 122: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", "AA"),
        "round 122: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 122: the processor reads the record then stops", "key"),
        "bssxh 122: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 122: the processor reads the record then stops", "lemon"),
        "csgbq 122: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 122: the processor reads the record then stops", "a"),
        "round 122: the processor reads the record then stops",
    ),
    (
        ("round 122: the processor reads the record then stops", "zz"),
        "qntmc 122: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 122: the processor reads the record then stops", "AgentU"),
        "ruyaw 122: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 122: the processor reads the record then stops", "keyboard"),
        "bssor 122: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 122: the processor reads the record then stops", "AA"),
        "round 122: the processor reads the record then stops",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "key"),
        "bssxh 122: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "lemon"),
        "csgbq 122: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "a"),
        "round 122: a worker pulls the next task from the queue",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "zz"),
        "qntmc 122: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 122: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "keyboard"),
        "bssor 122: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 122: a worker pulls the next task from the queue", "AA"),
        "round 122: a worker pulls the next task from the queue",
    ),
    (
        ("round 122: signals travel through the network layer", "key"),
        "bssxh 122: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 122: signals travel through the network layer", "lemon"),
        "csgbq 122: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 122: signals travel through the network layer", "a"),
        "round 122: signals travel through the network layer",
    ),
    (
        ("round 122: signals travel through the network layer", "zz"),
        "qntmc 122: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 122: signals travel through the network layer", "AgentU"),
        "ruyaw 122: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 122: signals travel through the network layer", "keyboard"),
        "bssor 122: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 122: signals travel through the network layer", "AA"),
        "round 122: signals travel through the network layer",
    ),
    (
        ("round 122: the gateway routes each request by policy", "key"),
        "bssxh 122: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 122: the gateway routes each request by policy", "lemon"),
        "csgbq 122: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 122: the gateway routes each request by policy", "a"),
        "round 122: the gateway routes each request by policy",
    ),
    (
        ("round 122: the gateway routes each request by policy", "zz"),
        "qntmc 122: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 122: the gateway routes each request by policy", "AgentU"),
        "ruyaw 122: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 122: the gateway routes each request by policy", "keyboard"),
        "bssor 122: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 122: the gateway routes each request by policy", "AA"),
        "round 122: the gateway routes each request by policy",
    ),
    (("round 122: memory grows until the buffer is full", "key"), "bssxh 122: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 122: memory grows until the buffer is full", "lemon"), "csgbq 122: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 122: memory grows until the buffer is full", "a"), "round 122: memory grows until the buffer is full"),
    (("round 122: memory grows until the buffer is full", "zz"), "qntmc 122: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 122: memory grows until the buffer is full", "AgentU"),
        "ruyaw 122: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 122: memory grows until the buffer is full", "keyboard"),
        "bssor 122: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 122: memory grows until the buffer is full", "AA"), "round 122: memory grows until the buffer is full"),
    (("round 122: the cluster mirrors every packet twice", "key"), "bssxh 122: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 122: the cluster mirrors every packet twice", "lemon"),
        "csgbq 122: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 122: the cluster mirrors every packet twice", "a"), "round 122: the cluster mirrors every packet twice"),
    (("round 122: the cluster mirrors every packet twice", "zz"), "qntmc 122: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 122: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 122: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 122: the cluster mirrors every packet twice", "keyboard"),
        "bssor 122: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 122: the cluster mirrors every packet twice", "AA"), "round 122: the cluster mirrors every packet twice"),
    (
        ("round 122: ranking uses tokens learned from the corpus", "key"),
        "bssxh 122: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 122: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", "a"),
        "round 122: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 122: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 122: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 122: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", "AA"),
        "round 122: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 122: a long session ends when the candle dies", "key"),
        "bssxh 122: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 122: a long session ends when the candle dies", "lemon"),
        "csgbq 122: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 122: a long session ends when the candle dies", "a"),
        "round 122: a long session ends when the candle dies",
    ),
    (
        ("round 122: a long session ends when the candle dies", "zz"),
        "qntmc 122: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 122: a long session ends when the candle dies", "AgentU"),
        "ruyaw 122: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 122: a long session ends when the candle dies", "keyboard"),
        "bssor 122: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 122: a long session ends when the candle dies", "AA"),
        "round 122: a long session ends when the candle dies",
    ),
    (("round 122: encode the prompt then map the result", "key"), "bssxh 122: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 122: encode the prompt then map the result", "lemon"), "csgbq 122: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 122: encode the prompt then map the result", "a"), "round 122: encode the prompt then map the result"),
    (("round 122: encode the prompt then map the result", "zz"), "qntmc 122: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 122: encode the prompt then map the result", "AgentU"),
        "ruyaw 122: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 122: encode the prompt then map the result", "keyboard"),
        "bssor 122: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 122: encode the prompt then map the result", "AA"), "round 122: encode the prompt then map the result"),
    (("round 122: the kernel wakes the worker at dawn", "key"), "bssxh 122: rri iovlop ukocc xfo ambocb er neux"),
    (("round 122: the kernel wakes the worker at dawn", "lemon"), "csgbq 122: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 122: the kernel wakes the worker at dawn", "a"), "round 122: the kernel wakes the worker at dawn"),
    (("round 122: the kernel wakes the worker at dawn", "zz"), "qntmc 122: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 122: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 122: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 122: the kernel wakes the worker at dawn", "keyboard"), "bssor 122: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 122: the kernel wakes the worker at dawn", "AA"), "round 122: the kernel wakes the worker at dawn"),
    (("round 122: service latency drops after the patch", "key"), "bssxh 122: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 122: service latency drops after the patch", "lemon"), "csgbq 122: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 122: service latency drops after the patch", "a"), "round 122: service latency drops after the patch"),
    (("round 122: service latency drops after the patch", "zz"), "qntmc 122: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 122: service latency drops after the patch", "AgentU"),
        "ruyaw 122: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 122: service latency drops after the patch", "keyboard"),
        "bssor 122: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 122: service latency drops after the patch", "AA"), "round 122: service latency drops after the patch"),
    (
        ("round 122: the library caches every vector it sees", "key"),
        "bssxh 122: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 122: the library caches every vector it sees", "lemon"),
        "csgbq 122: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 122: the library caches every vector it sees", "a"), "round 122: the library caches every vector it sees"),
    (
        ("round 122: the library caches every vector it sees", "zz"),
        "qntmc 122: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 122: the library caches every vector it sees", "AgentU"),
        "ruyaw 122: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 122: the library caches every vector it sees", "keyboard"),
        "bssor 122: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 122: the library caches every vector it sees", "AA"),
        "round 122: the library caches every vector it sees",
    ),
    (("round 122: agents argue then the debate resolves", "key"), "bssxh 122: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 122: agents argue then the debate resolves", "lemon"), "csgbq 122: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 122: agents argue then the debate resolves", "a"), "round 122: agents argue then the debate resolves"),
    (("round 122: agents argue then the debate resolves", "zz"), "qntmc 122: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 122: agents argue then the debate resolves", "AgentU"),
        "ruyaw 122: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 122: agents argue then the debate resolves", "keyboard"),
        "bssor 122: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 122: agents argue then the debate resolves", "AA"), "round 122: agents argue then the debate resolves"),
    (("round 122: the filter keeps only strong matches", "key"), "bssxh 122: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 122: the filter keeps only strong matches", "lemon"), "csgbq 122: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 122: the filter keeps only strong matches", "a"), "round 122: the filter keeps only strong matches"),
    (("round 122: the filter keeps only strong matches", "zz"), "qntmc 122: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 122: the filter keeps only strong matches", "AgentU"), "ruyaw 122: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 122: the filter keeps only strong matches", "keyboard"),
        "bssor 122: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 122: the filter keeps only strong matches", "AA"), "round 122: the filter keeps only strong matches"),
    (("round 122: the model answers with a short reply", "key"), "bssxh 122: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 122: the model answers with a short reply", "lemon"), "csgbq 122: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 122: the model answers with a short reply", "a"), "round 122: the model answers with a short reply"),
    (("round 122: the model answers with a short reply", "zz"), "qntmc 122: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 122: the model answers with a short reply", "AgentU"), "ruyaw 122: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 122: the model answers with a short reply", "keyboard"),
        "bssor 122: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 122: the model answers with a short reply", "AA"), "round 122: the model answers with a short reply"),
    (
        ("round 122: the recorder stores the reasoning trace", "key"),
        "bssxh 122: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 122: the recorder stores the reasoning trace", "lemon"),
        "csgbq 122: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 122: the recorder stores the reasoning trace", "a"), "round 122: the recorder stores the reasoning trace"),
    (
        ("round 122: the recorder stores the reasoning trace", "zz"),
        "qntmc 122: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 122: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 122: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 122: the recorder stores the reasoning trace", "keyboard"),
        "bssor 122: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 122: the recorder stores the reasoning trace", "AA"),
        "round 122: the recorder stores the reasoning trace",
    ),
    (("round 122: the angel watches the processor run", "key"), "bssxh 122: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 122: the angel watches the processor run", "lemon"), "csgbq 122: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 122: the angel watches the processor run", "a"), "round 122: the angel watches the processor run"),
    (("round 122: the angel watches the processor run", "zz"), "qntmc 122: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 122: the angel watches the processor run", "AgentU"), "ruyaw 122: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 122: the angel watches the processor run", "keyboard"), "bssor 122: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 122: the angel watches the processor run", "AA"), "round 122: the angel watches the processor run"),
    (("round 122: angle of the vector decides the match", "key"), "bssxh 122: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 122: angle of the vector decides the match", "lemon"), "csgbq 122: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 122: angle of the vector decides the match", "a"), "round 122: angle of the vector decides the match"),
    (("round 122: angle of the vector decides the match", "zz"), "qntmc 122: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 122: angle of the vector decides the match", "AgentU"),
        "ruyaw 122: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 122: angle of the vector decides the match", "keyboard"),
        "bssor 122: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 122: angle of the vector decides the match", "AA"), "round 122: angle of the vector decides the match"),
    (
        ("round 122: the candle burns twice as long at night", "key"),
        "bssxh 122: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 122: the candle burns twice as long at night", "lemon"),
        "csgbq 122: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 122: the candle burns twice as long at night", "a"), "round 122: the candle burns twice as long at night"),
    (
        ("round 122: the candle burns twice as long at night", "zz"),
        "qntmc 122: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 122: the candle burns twice as long at night", "AgentU"),
        "ruyaw 122: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 122: the candle burns twice as long at night", "keyboard"),
        "bssor 122: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 122: the candle burns twice as long at night", "AA"),
        "round 122: the candle burns twice as long at night",
    ),
    (("round 122: a mirror of the universe in one line", "key"), "bssxh 122: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 122: a mirror of the universe in one line", "lemon"), "csgbq 122: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 122: a mirror of the universe in one line", "a"), "round 122: a mirror of the universe in one line"),
    (("round 122: a mirror of the universe in one line", "zz"), "qntmc 122: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 122: a mirror of the universe in one line", "AgentU"), "ruyaw 122: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 122: a mirror of the universe in one line", "keyboard"),
        "bssor 122: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 122: a mirror of the universe in one line", "AA"), "round 122: a mirror of the universe in one line"),
    (("round 122: the queue drains before the storm", "key"), "bssxh 122: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 122: the queue drains before the storm", "lemon"), "csgbq 122: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 122: the queue drains before the storm", "a"), "round 122: the queue drains before the storm"),
    (("round 122: the queue drains before the storm", "zz"), "qntmc 122: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 122: the queue drains before the storm", "AgentU"), "ruyaw 122: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 122: the queue drains before the storm", "keyboard"), "bssor 122: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 122: the queue drains before the storm", "AA"), "round 122: the queue drains before the storm"),
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
