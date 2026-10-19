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
    (("kitten750", "key"), "umrdil750"),
    (("kitten750", "lemon"), "vmfhry750"),
    (("kitten750", "a"), "kitten750"),
    (("kitten750", "zz"), "jhssdm750"),
    (("kitten750", "AgentU"), "koxgxh750"),
    (("kitten750", "keyboard"), "umrusn750"),
    (("kitten750", "AA"), "kitten750"),
    (("sitting750", "key"), "cmrdmlq750"),
    (("sitting750", "lemon"), "dmfhvyk750"),
    (("sitting750", "a"), "sitting750"),
    (("sitting750", "zz"), "rhsshmf750"),
    (("sitting750", "AgentU"), "soxgbhg750"),
    (("sitting750", "keyboard"), "cmruwnx750"),
    (("sitting750", "AA"), "sitting750"),
    (("agent750", "key"), "kkcxx750"),
    (("agent750", "lemon"), "lkqbg750"),
    (("agent750", "a"), "agent750"),
    (("agent750", "zz"), "zfdms750"),
    (("agent750", "AgentU"), "amiam750"),
    (("agent750", "keyboard"), "kkcoh750"),
    (("agent750", "AA"), "agent750"),
    (("angle750", "key"), "krevi750"),
    (("angle750", "lemon"), "lrszr750"),
    (("angle750", "a"), "angle750"),
    (("angle750", "zz"), "zmfkd750"),
    (("angle750", "AgentU"), "atkyx750"),
    (("angle750", "keyboard"), "krems750"),
    (("angle750", "AA"), "angle750"),
    (("universe750", "key"), "ergfipci750"),
    (("universe750", "lemon"), "frujrcwq750"),
    (("universe750", "a"), "universe750"),
    (("universe750", "zz"), "tmhudqrd750"),
    (("universe750", "AgentU"), "utmixlsk750"),
    (("universe750", "keyboard"), "ergwsrjh750"),
    (("universe750", "AA"), "universe750"),
    (("memory750", "key"), "wikyvw750"),
    (("memory750", "lemon"), "xiycej750"),
    (("memory750", "a"), "memory750"),
    (("memory750", "zz"), "ldlnqx750"),
    (("memory750", "AgentU"), "mkqbks750"),
    (("memory750", "keyboard"), "wikpfy750"),
    (("memory750", "AA"), "memory750"),
    (("stream750", "key"), "cxpoek750"),
    (("stream750", "lemon"), "dxdsnx750"),
    (("stream750", "a"), "stream750"),
    (("stream750", "zz"), "rsqdzl750"),
    (("stream750", "AgentU"), "szvrtg750"),
    (("stream750", "keyboard"), "cxpfom750"),
    (("stream750", "AA"), "stream750"),
    (("context750", "key"), "msldivd750"),
    (("context750", "lemon"), "nszhrix750"),
    (("context750", "a"), "context750"),
    (("context750", "zz"), "bnmsdws750"),
    (("context750", "AgentU"), "curgxrt750"),
    (("context750", "keyboard"), "mslusxk750"),
    (("context750", "AA"), "context750"),
    (("knowledge750", "key"), "urmgpcnkc750"),
    (("knowledge750", "lemon"), "vrakyphss750"),
    (("knowledge750", "a"), "knowledge750"),
    (("knowledge750", "zz"), "jmnvkdcfd750"),
    (("knowledge750", "AgentU"), "ktsjeydmi750"),
    (("knowledge750", "keyboard"), "urmxzeujo750"),
    (("knowledge750", "AA"), "knowledge750"),
    (("vector750", "key"), "fiadsp750"),
    (("vector750", "lemon"), "giohbc750"),
    (("vector750", "a"), "vector750"),
    (("vector750", "zz"), "udbsnq750"),
    (("vector750", "AgentU"), "vkgghl750"),
    (("vector750", "keyboard"), "fiaucr750"),
    (("vector750", "AA"), "vector750"),
    (("processor750", "key"), "zvmmiqcsp750"),
    (("processor750", "lemon"), "avaqrdwaf750"),
    (("processor750", "a"), "processor750"),
    (("processor750", "zz"), "oqnbdrrnq750"),
    (("processor750", "AgentU"), "pxspxmsuv750"),
    (("processor750", "keyboard"), "zvmdssjrb750"),
    (("processor750", "AA"), "processor750"),
    (("reasoning750", "key"), "biycslsre750"),
    (("reasoning750", "lemon"), "cimgbymzu750"),
    (("reasoning750", "a"), "reasoning750"),
    (("reasoning750", "zz"), "qdzrnmhmf750"),
    (("reasoning750", "AgentU"), "rkefhhitk750"),
    (("reasoning750", "keyboard"), "biytcnzqq750"),
    (("reasoning750", "AA"), "reasoning750"),
    (("machine750", "key"), "wearmlo750"),
    (("machine750", "lemon"), "xeovvyi750"),
    (("machine750", "a"), "machine750"),
    (("machine750", "zz"), "lzbghmd750"),
    (("machine750", "AgentU"), "mggubhe750"),
    (("machine750", "keyboard"), "weaiwnv750"),
    (("machine750", "AA"), "machine750"),
    (("learning750", "key"), "viybrgxk750"),
    (("learning750", "lemon"), "wimfatrs750"),
    (("learning750", "a"), "learning750"),
    (("learning750", "zz"), "kdzqmhmf750"),
    (("learning750", "AgentU"), "lkeegcnm750"),
    (("learning750", "keyboard"), "viysbiej750"),
    (("learning750", "AA"), "learning750"),
    (("model750", "key"), "wsbop750"),
    (("model750", "lemon"), "xspsy750"),
    (("model750", "a"), "model750"),
    (("model750", "zz"), "lncdk750"),
    (("model750", "AgentU"), "muhre750"),
    (("model750", "keyboard"), "wsbfz750"),
    (("model750", "AA"), "model750"),
    (("token750", "key"), "dsior750"),
    (("token750", "lemon"), "eswsa750"),
    (("token750", "a"), "token750"),
    (("token750", "zz"), "snjdm750"),
    (("token750", "AgentU"), "tuorg750"),
    (("token750", "keyboard"), "dsifb750"),
    (("token750", "AA"), "token750"),
    (("prompt750", "key"), "zvmwtr750"),
    (("prompt750", "lemon"), "avaace750"),
    (("prompt750", "a"), "prompt750"),
    (("prompt750", "zz"), "oqnlos750"),
    (("prompt750", "AgentU"), "pxszin750"),
    (("prompt750", "keyboard"), "zvmndt750"),
    (("prompt750", "AA"), "prompt750"),
    (("session750", "key"), "ciqcmmx750"),
    (("session750", "lemon"), "diegvzr750"),
    (("session750", "a"), "session750"),
    (("session750", "zz"), "rdrrhnm750"),
    (("session750", "AgentU"), "skwfbin750"),
    (("session750", "keyboard"), "ciqtwoe750"),
    (("session750", "AA"), "session750"),
    (("library750", "key"), "vmzbepi750"),
    (("library750", "lemon"), "wmnfncc750"),
    (("library750", "a"), "library750"),
    (("library750", "zz"), "khaqzqx750"),
    (("library750", "AgentU"), "lofetly750"),
    (("library750", "keyboard"), "vmzsorp750"),
    (("library750", "AA"), "library750"),
    (("service750", "key"), "cipfmao750"),
    (("service750", "lemon"), "didjvni750"),
    (("service750", "a"), "service750"),
    (("service750", "zz"), "rdquhbd750"),
    (("service750", "AgentU"), "skvibwe750"),
    (("service750", "keyboard"), "cipwwcv750"),
    (("service750", "AA"), "service750"),
    (("gateway750", "key"), "qeroayi750"),
    (("gateway750", "lemon"), "refsjlc750"),
    (("gateway750", "a"), "gateway750"),
    (("gateway750", "zz"), "fzsdvzx750"),
    (("gateway750", "AgentU"), "ggxrpuy750"),
    (("gateway750", "keyboard"), "qerfkap750"),
    (("gateway750", "AA"), "gateway750"),
    (("storage750", "key"), "cxmbeeo750"),
    (("storage750", "lemon"), "dxafnri750"),
    (("storage750", "a"), "storage750"),
    (("storage750", "zz"), "rsnqzfd750"),
    (("storage750", "AgentU"), "szsetae750"),
    (("storage750", "keyboard"), "cxmsogv750"),
    (("storage750", "AA"), "storage750"),
    (("network750", "key"), "xirgspu750"),
    (("network750", "lemon"), "yifkbco750"),
    (("network750", "a"), "network750"),
    (("network750", "zz"), "mdsvnqj750"),
    (("network750", "AgentU"), "nkxjhlk750"),
    (("network750", "keyboard"), "xirxcrb750"),
    (("network750", "AA"), "network750"),
    (("latency750", "key"), "verorai750"),
    (("latency750", "lemon"), "wefsanc750"),
    (("latency750", "a"), "latency750"),
    (("latency750", "zz"), "kzsdmbx750"),
    (("latency750", "AgentU"), "lgxrgwy750"),
    (("latency750", "keyboard"), "verfbcp750"),
    (("latency750", "AA"), "latency750"),
    (("buffer750", "key"), "lydpip750"),
    (("buffer750", "lemon"), "myrtrc750"),
    (("buffer750", "a"), "buffer750"),
    (("buffer750", "zz"), "ateedq750"),
    (("buffer750", "AgentU"), "bajsxl750"),
    (("buffer750", "keyboard"), "lydgsr750"),
    (("buffer750", "AA"), "buffer750"),
    (("queue750", "key"), "aycei750"),
    (("queue750", "lemon"), "byqir750"),
    (("queue750", "a"), "queue750"),
    (("queue750", "zz"), "ptdtd750"),
    (("queue750", "AgentU"), "qaihx750"),
    (("queue750", "keyboard"), "aycvs750"),
    (("queue750", "AA"), "queue750"),
    (("worker750", "key"), "gspuip750"),
    (("worker750", "lemon"), "hsdyrc750"),
    (("worker750", "a"), "worker750"),
    (("worker750", "zz"), "vnqjdq750"),
    (("worker750", "AgentU"), "wuvxxl750"),
    (("worker750", "keyboard"), "gsplsr750"),
    (("worker750", "AA"), "worker750"),
    (("kernel750", "key"), "uipxij750"),
    (("kernel750", "lemon"), "vidbrw750"),
    (("kernel750", "a"), "kernel750"),
    (("kernel750", "zz"), "jdqmdk750"),
    (("kernel750", "AgentU"), "kkvaxf750"),
    (("kernel750", "keyboard"), "uiposl750"),
    (("kernel750", "AA"), "kernel750"),
    (("signal750", "key"), "cmexej750"),
    (("signal750", "lemon"), "dmsbnw750"),
    (("signal750", "a"), "signal750"),
    (("signal750", "zz"), "rhfmzk750"),
    (("signal750", "AgentU"), "sokatf750"),
    (("signal750", "keyboard"), "cmeool750"),
    (("signal750", "AA"), "signal750"),
    (("packet750", "key"), "zeauir750"),
    (("packet750", "lemon"), "aeoyre750"),
    (("packet750", "a"), "packet750"),
    (("packet750", "zz"), "ozbjds750"),
    (("packet750", "AgentU"), "pggxxn750"),
    (("packet750", "keyboard"), "zealst750"),
    (("packet750", "AA"), "packet750"),
    (("router750", "key"), "bssdip750"),
    (("router750", "lemon"), "csghrc750"),
    (("router750", "a"), "router750"),
    (("router750", "zz"), "qntsdq750"),
    (("router750", "AgentU"), "ruygxl750"),
    (("router750", "keyboard"), "bssusr750"),
    (("router750", "AA"), "router750"),
    (("cluster750", "key"), "mpscxcb750"),
    (("cluster750", "lemon"), "npgggpv750"),
    (("cluster750", "a"), "cluster750"),
    (("cluster750", "zz"), "bktrsdq750"),
    (("cluster750", "AgentU"), "cryfmyr750"),
    (("cluster750", "keyboard"), "mpsthei750"),
    (("cluster750", "AA"), "cluster750"),
    (("mirror750", "key"), "wmpbsp750"),
    (("mirror750", "lemon"), "xmdfbc750"),
    (("mirror750", "a"), "mirror750"),
    (("mirror750", "zz"), "lhqqnq750"),
    (("mirror750", "AgentU"), "movehl750"),
    (("mirror750", "keyboard"), "wmpscr750"),
    (("mirror750", "AA"), "mirror750"),
    (("filter750", "key"), "pmjdip750"),
    (("filter750", "lemon"), "qmxhrc750"),
    (("filter750", "a"), "filter750"),
    (("filter750", "zz"), "ehksdq750"),
    (("filter750", "AgentU"), "fopgxl750"),
    (("filter750", "keyboard"), "pmjusr750"),
    (("filter750", "AA"), "filter750"),
    (("ranking750", "key"), "belumlq750"),
    (("ranking750", "lemon"), "cezyvyk750"),
    (("ranking750", "a"), "ranking750"),
    (("ranking750", "zz"), "qzmjhmf750"),
    (("ranking750", "AgentU"), "rgrxbhg750"),
    (("ranking750", "keyboard"), "bellwnx750"),
    (("ranking750", "AA"), "ranking750"),
    (("encoding750", "key"), "orayhgxk750"),
    (("encoding750", "lemon"), "procqtrs750"),
    (("encoding750", "a"), "encoding750"),
    (("encoding750", "zz"), "dmbnchmf750"),
    (("encoding750", "AgentU"), "etgbwcnm750"),
    (("encoding750", "keyboard"), "orapriej750"),
    (("encoding750", "AA"), "encoding750"),
    (("mapping750", "key"), "wenzmlq750"),
    (("mapping750", "lemon"), "xebdvyk750"),
    (("mapping750", "a"), "mapping750"),
    (("mapping750", "zz"), "lzoohmf750"),
    (("mapping750", "AgentU"), "mgtcbhg750"),
    (("mapping750", "keyboard"), "wenqwnx750"),
    (("mapping750", "AA"), "mapping750"),
    (("record750", "key"), "biayvb750"),
    (("record750", "lemon"), "cioceo750"),
    (("record750", "a"), "record750"),
    (("record750", "zz"), "qdbnqc750"),
    (("record750", "AgentU"), "rkgbkx750"),
    (("record750", "keyboard"), "biapfd750"),
    (("record750", "AA"), "record750"),
    (("candle750", "key"), "melnpc750"),
    (("candle750", "lemon"), "nezryp750"),
    (("candle750", "a"), "candle750"),
    (("candle750", "zz"), "bzmckd750"),
    (("candle750", "AgentU"), "cgrqey750"),
    (("candle750", "keyboard"), "meleze750"),
    (("candle750", "AA"), "candle750"),
    (("thread750", "key"), "dlpoeb750"),
    (("thread750", "lemon"), "eldsno750"),
    (("thread750", "a"), "thread750"),
    (("thread750", "zz"), "sgqdzc750"),
    (("thread750", "AgentU"), "tnvrtx750"),
    (("thread750", "keyboard"), "dlpfod750"),
    (("thread750", "AA"), "thread750"),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 750: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 750: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "a"),
        "round 750: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 750: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 750: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 750: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", "AA"),
        "round 750: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "key"),
        "bssxh 750: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 750: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "a"),
        "round 750: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 750: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 750: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 750: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", "AA"),
        "round 750: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 750: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 750: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "a"),
        "round 750: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 750: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 750: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 750: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", "AA"),
        "round 750: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 750: the processor reads the record then stops", "key"),
        "bssxh 750: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 750: the processor reads the record then stops", "lemon"),
        "csgbq 750: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 750: the processor reads the record then stops", "a"),
        "round 750: the processor reads the record then stops",
    ),
    (
        ("round 750: the processor reads the record then stops", "zz"),
        "qntmc 750: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 750: the processor reads the record then stops", "AgentU"),
        "ruyaw 750: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 750: the processor reads the record then stops", "keyboard"),
        "bssor 750: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 750: the processor reads the record then stops", "AA"),
        "round 750: the processor reads the record then stops",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "key"),
        "bssxh 750: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "lemon"),
        "csgbq 750: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "a"),
        "round 750: a worker pulls the next task from the queue",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "zz"),
        "qntmc 750: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 750: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "keyboard"),
        "bssor 750: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 750: a worker pulls the next task from the queue", "AA"),
        "round 750: a worker pulls the next task from the queue",
    ),
    (
        ("round 750: signals travel through the network layer", "key"),
        "bssxh 750: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 750: signals travel through the network layer", "lemon"),
        "csgbq 750: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 750: signals travel through the network layer", "a"),
        "round 750: signals travel through the network layer",
    ),
    (
        ("round 750: signals travel through the network layer", "zz"),
        "qntmc 750: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 750: signals travel through the network layer", "AgentU"),
        "ruyaw 750: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 750: signals travel through the network layer", "keyboard"),
        "bssor 750: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 750: signals travel through the network layer", "AA"),
        "round 750: signals travel through the network layer",
    ),
    (
        ("round 750: the gateway routes each request by policy", "key"),
        "bssxh 750: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 750: the gateway routes each request by policy", "lemon"),
        "csgbq 750: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 750: the gateway routes each request by policy", "a"),
        "round 750: the gateway routes each request by policy",
    ),
    (
        ("round 750: the gateway routes each request by policy", "zz"),
        "qntmc 750: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 750: the gateway routes each request by policy", "AgentU"),
        "ruyaw 750: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 750: the gateway routes each request by policy", "keyboard"),
        "bssor 750: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 750: the gateway routes each request by policy", "AA"),
        "round 750: the gateway routes each request by policy",
    ),
    (("round 750: memory grows until the buffer is full", "key"), "bssxh 750: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 750: memory grows until the buffer is full", "lemon"), "csgbq 750: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 750: memory grows until the buffer is full", "a"), "round 750: memory grows until the buffer is full"),
    (("round 750: memory grows until the buffer is full", "zz"), "qntmc 750: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 750: memory grows until the buffer is full", "AgentU"),
        "ruyaw 750: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 750: memory grows until the buffer is full", "keyboard"),
        "bssor 750: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 750: memory grows until the buffer is full", "AA"), "round 750: memory grows until the buffer is full"),
    (("round 750: the cluster mirrors every packet twice", "key"), "bssxh 750: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 750: the cluster mirrors every packet twice", "lemon"),
        "csgbq 750: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 750: the cluster mirrors every packet twice", "a"), "round 750: the cluster mirrors every packet twice"),
    (("round 750: the cluster mirrors every packet twice", "zz"), "qntmc 750: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 750: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 750: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 750: the cluster mirrors every packet twice", "keyboard"),
        "bssor 750: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 750: the cluster mirrors every packet twice", "AA"), "round 750: the cluster mirrors every packet twice"),
    (
        ("round 750: ranking uses tokens learned from the corpus", "key"),
        "bssxh 750: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 750: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", "a"),
        "round 750: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 750: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 750: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 750: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", "AA"),
        "round 750: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 750: a long session ends when the candle dies", "key"),
        "bssxh 750: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 750: a long session ends when the candle dies", "lemon"),
        "csgbq 750: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 750: a long session ends when the candle dies", "a"),
        "round 750: a long session ends when the candle dies",
    ),
    (
        ("round 750: a long session ends when the candle dies", "zz"),
        "qntmc 750: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 750: a long session ends when the candle dies", "AgentU"),
        "ruyaw 750: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 750: a long session ends when the candle dies", "keyboard"),
        "bssor 750: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 750: a long session ends when the candle dies", "AA"),
        "round 750: a long session ends when the candle dies",
    ),
    (("round 750: encode the prompt then map the result", "key"), "bssxh 750: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 750: encode the prompt then map the result", "lemon"), "csgbq 750: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 750: encode the prompt then map the result", "a"), "round 750: encode the prompt then map the result"),
    (("round 750: encode the prompt then map the result", "zz"), "qntmc 750: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 750: encode the prompt then map the result", "AgentU"),
        "ruyaw 750: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 750: encode the prompt then map the result", "keyboard"),
        "bssor 750: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 750: encode the prompt then map the result", "AA"), "round 750: encode the prompt then map the result"),
    (("round 750: the kernel wakes the worker at dawn", "key"), "bssxh 750: rri iovlop ukocc xfo ambocb er neux"),
    (("round 750: the kernel wakes the worker at dawn", "lemon"), "csgbq 750: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 750: the kernel wakes the worker at dawn", "a"), "round 750: the kernel wakes the worker at dawn"),
    (("round 750: the kernel wakes the worker at dawn", "zz"), "qntmc 750: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 750: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 750: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 750: the kernel wakes the worker at dawn", "keyboard"), "bssor 750: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 750: the kernel wakes the worker at dawn", "AA"), "round 750: the kernel wakes the worker at dawn"),
    (("round 750: service latency drops after the patch", "key"), "bssxh 750: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 750: service latency drops after the patch", "lemon"), "csgbq 750: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 750: service latency drops after the patch", "a"), "round 750: service latency drops after the patch"),
    (("round 750: service latency drops after the patch", "zz"), "qntmc 750: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 750: service latency drops after the patch", "AgentU"),
        "ruyaw 750: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 750: service latency drops after the patch", "keyboard"),
        "bssor 750: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 750: service latency drops after the patch", "AA"), "round 750: service latency drops after the patch"),
    (
        ("round 750: the library caches every vector it sees", "key"),
        "bssxh 750: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 750: the library caches every vector it sees", "lemon"),
        "csgbq 750: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 750: the library caches every vector it sees", "a"), "round 750: the library caches every vector it sees"),
    (
        ("round 750: the library caches every vector it sees", "zz"),
        "qntmc 750: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 750: the library caches every vector it sees", "AgentU"),
        "ruyaw 750: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 750: the library caches every vector it sees", "keyboard"),
        "bssor 750: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 750: the library caches every vector it sees", "AA"),
        "round 750: the library caches every vector it sees",
    ),
    (("round 750: agents argue then the debate resolves", "key"), "bssxh 750: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 750: agents argue then the debate resolves", "lemon"), "csgbq 750: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 750: agents argue then the debate resolves", "a"), "round 750: agents argue then the debate resolves"),
    (("round 750: agents argue then the debate resolves", "zz"), "qntmc 750: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 750: agents argue then the debate resolves", "AgentU"),
        "ruyaw 750: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 750: agents argue then the debate resolves", "keyboard"),
        "bssor 750: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 750: agents argue then the debate resolves", "AA"), "round 750: agents argue then the debate resolves"),
    (("round 750: the filter keeps only strong matches", "key"), "bssxh 750: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 750: the filter keeps only strong matches", "lemon"), "csgbq 750: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 750: the filter keeps only strong matches", "a"), "round 750: the filter keeps only strong matches"),
    (("round 750: the filter keeps only strong matches", "zz"), "qntmc 750: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 750: the filter keeps only strong matches", "AgentU"), "ruyaw 750: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 750: the filter keeps only strong matches", "keyboard"),
        "bssor 750: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 750: the filter keeps only strong matches", "AA"), "round 750: the filter keeps only strong matches"),
    (("round 750: the model answers with a short reply", "key"), "bssxh 750: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 750: the model answers with a short reply", "lemon"), "csgbq 750: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 750: the model answers with a short reply", "a"), "round 750: the model answers with a short reply"),
    (("round 750: the model answers with a short reply", "zz"), "qntmc 750: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 750: the model answers with a short reply", "AgentU"), "ruyaw 750: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 750: the model answers with a short reply", "keyboard"),
        "bssor 750: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 750: the model answers with a short reply", "AA"), "round 750: the model answers with a short reply"),
    (
        ("round 750: the recorder stores the reasoning trace", "key"),
        "bssxh 750: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 750: the recorder stores the reasoning trace", "lemon"),
        "csgbq 750: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 750: the recorder stores the reasoning trace", "a"), "round 750: the recorder stores the reasoning trace"),
    (
        ("round 750: the recorder stores the reasoning trace", "zz"),
        "qntmc 750: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 750: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 750: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 750: the recorder stores the reasoning trace", "keyboard"),
        "bssor 750: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 750: the recorder stores the reasoning trace", "AA"),
        "round 750: the recorder stores the reasoning trace",
    ),
    (("round 750: the angel watches the processor run", "key"), "bssxh 750: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 750: the angel watches the processor run", "lemon"), "csgbq 750: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 750: the angel watches the processor run", "a"), "round 750: the angel watches the processor run"),
    (("round 750: the angel watches the processor run", "zz"), "qntmc 750: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 750: the angel watches the processor run", "AgentU"), "ruyaw 750: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 750: the angel watches the processor run", "keyboard"), "bssor 750: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 750: the angel watches the processor run", "AA"), "round 750: the angel watches the processor run"),
    (("round 750: angle of the vector decides the match", "key"), "bssxh 750: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 750: angle of the vector decides the match", "lemon"), "csgbq 750: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 750: angle of the vector decides the match", "a"), "round 750: angle of the vector decides the match"),
    (("round 750: angle of the vector decides the match", "zz"), "qntmc 750: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 750: angle of the vector decides the match", "AgentU"),
        "ruyaw 750: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 750: angle of the vector decides the match", "keyboard"),
        "bssor 750: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 750: angle of the vector decides the match", "AA"), "round 750: angle of the vector decides the match"),
    (
        ("round 750: the candle burns twice as long at night", "key"),
        "bssxh 750: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 750: the candle burns twice as long at night", "lemon"),
        "csgbq 750: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 750: the candle burns twice as long at night", "a"), "round 750: the candle burns twice as long at night"),
    (
        ("round 750: the candle burns twice as long at night", "zz"),
        "qntmc 750: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 750: the candle burns twice as long at night", "AgentU"),
        "ruyaw 750: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 750: the candle burns twice as long at night", "keyboard"),
        "bssor 750: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 750: the candle burns twice as long at night", "AA"),
        "round 750: the candle burns twice as long at night",
    ),
    (("round 750: a mirror of the universe in one line", "key"), "bssxh 750: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 750: a mirror of the universe in one line", "lemon"), "csgbq 750: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 750: a mirror of the universe in one line", "a"), "round 750: a mirror of the universe in one line"),
    (("round 750: a mirror of the universe in one line", "zz"), "qntmc 750: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 750: a mirror of the universe in one line", "AgentU"), "ruyaw 750: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 750: a mirror of the universe in one line", "keyboard"),
        "bssor 750: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 750: a mirror of the universe in one line", "AA"), "round 750: a mirror of the universe in one line"),
    (("round 750: the queue drains before the storm", "key"), "bssxh 750: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 750: the queue drains before the storm", "lemon"), "csgbq 750: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 750: the queue drains before the storm", "a"), "round 750: the queue drains before the storm"),
    (("round 750: the queue drains before the storm", "zz"), "qntmc 750: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 750: the queue drains before the storm", "AgentU"), "ruyaw 750: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 750: the queue drains before the storm", "keyboard"), "bssor 750: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 750: the queue drains before the storm", "AA"), "round 750: the queue drains before the storm"),
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
