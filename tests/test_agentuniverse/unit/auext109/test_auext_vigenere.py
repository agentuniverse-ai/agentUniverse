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
    (("kitten109", "key"), "umrdil109"),
    (("kitten109", "lemon"), "vmfhry109"),
    (("kitten109", "a"), "kitten109"),
    (("kitten109", "zz"), "jhssdm109"),
    (("kitten109", "AgentU"), "koxgxh109"),
    (("kitten109", "keyboard"), "umrusn109"),
    (("kitten109", "AA"), "kitten109"),
    (("sitting109", "key"), "cmrdmlq109"),
    (("sitting109", "lemon"), "dmfhvyk109"),
    (("sitting109", "a"), "sitting109"),
    (("sitting109", "zz"), "rhsshmf109"),
    (("sitting109", "AgentU"), "soxgbhg109"),
    (("sitting109", "keyboard"), "cmruwnx109"),
    (("sitting109", "AA"), "sitting109"),
    (("agent109", "key"), "kkcxx109"),
    (("agent109", "lemon"), "lkqbg109"),
    (("agent109", "a"), "agent109"),
    (("agent109", "zz"), "zfdms109"),
    (("agent109", "AgentU"), "amiam109"),
    (("agent109", "keyboard"), "kkcoh109"),
    (("agent109", "AA"), "agent109"),
    (("angle109", "key"), "krevi109"),
    (("angle109", "lemon"), "lrszr109"),
    (("angle109", "a"), "angle109"),
    (("angle109", "zz"), "zmfkd109"),
    (("angle109", "AgentU"), "atkyx109"),
    (("angle109", "keyboard"), "krems109"),
    (("angle109", "AA"), "angle109"),
    (("universe109", "key"), "ergfipci109"),
    (("universe109", "lemon"), "frujrcwq109"),
    (("universe109", "a"), "universe109"),
    (("universe109", "zz"), "tmhudqrd109"),
    (("universe109", "AgentU"), "utmixlsk109"),
    (("universe109", "keyboard"), "ergwsrjh109"),
    (("universe109", "AA"), "universe109"),
    (("memory109", "key"), "wikyvw109"),
    (("memory109", "lemon"), "xiycej109"),
    (("memory109", "a"), "memory109"),
    (("memory109", "zz"), "ldlnqx109"),
    (("memory109", "AgentU"), "mkqbks109"),
    (("memory109", "keyboard"), "wikpfy109"),
    (("memory109", "AA"), "memory109"),
    (("stream109", "key"), "cxpoek109"),
    (("stream109", "lemon"), "dxdsnx109"),
    (("stream109", "a"), "stream109"),
    (("stream109", "zz"), "rsqdzl109"),
    (("stream109", "AgentU"), "szvrtg109"),
    (("stream109", "keyboard"), "cxpfom109"),
    (("stream109", "AA"), "stream109"),
    (("context109", "key"), "msldivd109"),
    (("context109", "lemon"), "nszhrix109"),
    (("context109", "a"), "context109"),
    (("context109", "zz"), "bnmsdws109"),
    (("context109", "AgentU"), "curgxrt109"),
    (("context109", "keyboard"), "mslusxk109"),
    (("context109", "AA"), "context109"),
    (("knowledge109", "key"), "urmgpcnkc109"),
    (("knowledge109", "lemon"), "vrakyphss109"),
    (("knowledge109", "a"), "knowledge109"),
    (("knowledge109", "zz"), "jmnvkdcfd109"),
    (("knowledge109", "AgentU"), "ktsjeydmi109"),
    (("knowledge109", "keyboard"), "urmxzeujo109"),
    (("knowledge109", "AA"), "knowledge109"),
    (("vector109", "key"), "fiadsp109"),
    (("vector109", "lemon"), "giohbc109"),
    (("vector109", "a"), "vector109"),
    (("vector109", "zz"), "udbsnq109"),
    (("vector109", "AgentU"), "vkgghl109"),
    (("vector109", "keyboard"), "fiaucr109"),
    (("vector109", "AA"), "vector109"),
    (("processor109", "key"), "zvmmiqcsp109"),
    (("processor109", "lemon"), "avaqrdwaf109"),
    (("processor109", "a"), "processor109"),
    (("processor109", "zz"), "oqnbdrrnq109"),
    (("processor109", "AgentU"), "pxspxmsuv109"),
    (("processor109", "keyboard"), "zvmdssjrb109"),
    (("processor109", "AA"), "processor109"),
    (("reasoning109", "key"), "biycslsre109"),
    (("reasoning109", "lemon"), "cimgbymzu109"),
    (("reasoning109", "a"), "reasoning109"),
    (("reasoning109", "zz"), "qdzrnmhmf109"),
    (("reasoning109", "AgentU"), "rkefhhitk109"),
    (("reasoning109", "keyboard"), "biytcnzqq109"),
    (("reasoning109", "AA"), "reasoning109"),
    (("machine109", "key"), "wearmlo109"),
    (("machine109", "lemon"), "xeovvyi109"),
    (("machine109", "a"), "machine109"),
    (("machine109", "zz"), "lzbghmd109"),
    (("machine109", "AgentU"), "mggubhe109"),
    (("machine109", "keyboard"), "weaiwnv109"),
    (("machine109", "AA"), "machine109"),
    (("learning109", "key"), "viybrgxk109"),
    (("learning109", "lemon"), "wimfatrs109"),
    (("learning109", "a"), "learning109"),
    (("learning109", "zz"), "kdzqmhmf109"),
    (("learning109", "AgentU"), "lkeegcnm109"),
    (("learning109", "keyboard"), "viysbiej109"),
    (("learning109", "AA"), "learning109"),
    (("model109", "key"), "wsbop109"),
    (("model109", "lemon"), "xspsy109"),
    (("model109", "a"), "model109"),
    (("model109", "zz"), "lncdk109"),
    (("model109", "AgentU"), "muhre109"),
    (("model109", "keyboard"), "wsbfz109"),
    (("model109", "AA"), "model109"),
    (("token109", "key"), "dsior109"),
    (("token109", "lemon"), "eswsa109"),
    (("token109", "a"), "token109"),
    (("token109", "zz"), "snjdm109"),
    (("token109", "AgentU"), "tuorg109"),
    (("token109", "keyboard"), "dsifb109"),
    (("token109", "AA"), "token109"),
    (("prompt109", "key"), "zvmwtr109"),
    (("prompt109", "lemon"), "avaace109"),
    (("prompt109", "a"), "prompt109"),
    (("prompt109", "zz"), "oqnlos109"),
    (("prompt109", "AgentU"), "pxszin109"),
    (("prompt109", "keyboard"), "zvmndt109"),
    (("prompt109", "AA"), "prompt109"),
    (("session109", "key"), "ciqcmmx109"),
    (("session109", "lemon"), "diegvzr109"),
    (("session109", "a"), "session109"),
    (("session109", "zz"), "rdrrhnm109"),
    (("session109", "AgentU"), "skwfbin109"),
    (("session109", "keyboard"), "ciqtwoe109"),
    (("session109", "AA"), "session109"),
    (("library109", "key"), "vmzbepi109"),
    (("library109", "lemon"), "wmnfncc109"),
    (("library109", "a"), "library109"),
    (("library109", "zz"), "khaqzqx109"),
    (("library109", "AgentU"), "lofetly109"),
    (("library109", "keyboard"), "vmzsorp109"),
    (("library109", "AA"), "library109"),
    (("service109", "key"), "cipfmao109"),
    (("service109", "lemon"), "didjvni109"),
    (("service109", "a"), "service109"),
    (("service109", "zz"), "rdquhbd109"),
    (("service109", "AgentU"), "skvibwe109"),
    (("service109", "keyboard"), "cipwwcv109"),
    (("service109", "AA"), "service109"),
    (("gateway109", "key"), "qeroayi109"),
    (("gateway109", "lemon"), "refsjlc109"),
    (("gateway109", "a"), "gateway109"),
    (("gateway109", "zz"), "fzsdvzx109"),
    (("gateway109", "AgentU"), "ggxrpuy109"),
    (("gateway109", "keyboard"), "qerfkap109"),
    (("gateway109", "AA"), "gateway109"),
    (("storage109", "key"), "cxmbeeo109"),
    (("storage109", "lemon"), "dxafnri109"),
    (("storage109", "a"), "storage109"),
    (("storage109", "zz"), "rsnqzfd109"),
    (("storage109", "AgentU"), "szsetae109"),
    (("storage109", "keyboard"), "cxmsogv109"),
    (("storage109", "AA"), "storage109"),
    (("network109", "key"), "xirgspu109"),
    (("network109", "lemon"), "yifkbco109"),
    (("network109", "a"), "network109"),
    (("network109", "zz"), "mdsvnqj109"),
    (("network109", "AgentU"), "nkxjhlk109"),
    (("network109", "keyboard"), "xirxcrb109"),
    (("network109", "AA"), "network109"),
    (("latency109", "key"), "verorai109"),
    (("latency109", "lemon"), "wefsanc109"),
    (("latency109", "a"), "latency109"),
    (("latency109", "zz"), "kzsdmbx109"),
    (("latency109", "AgentU"), "lgxrgwy109"),
    (("latency109", "keyboard"), "verfbcp109"),
    (("latency109", "AA"), "latency109"),
    (("buffer109", "key"), "lydpip109"),
    (("buffer109", "lemon"), "myrtrc109"),
    (("buffer109", "a"), "buffer109"),
    (("buffer109", "zz"), "ateedq109"),
    (("buffer109", "AgentU"), "bajsxl109"),
    (("buffer109", "keyboard"), "lydgsr109"),
    (("buffer109", "AA"), "buffer109"),
    (("queue109", "key"), "aycei109"),
    (("queue109", "lemon"), "byqir109"),
    (("queue109", "a"), "queue109"),
    (("queue109", "zz"), "ptdtd109"),
    (("queue109", "AgentU"), "qaihx109"),
    (("queue109", "keyboard"), "aycvs109"),
    (("queue109", "AA"), "queue109"),
    (("worker109", "key"), "gspuip109"),
    (("worker109", "lemon"), "hsdyrc109"),
    (("worker109", "a"), "worker109"),
    (("worker109", "zz"), "vnqjdq109"),
    (("worker109", "AgentU"), "wuvxxl109"),
    (("worker109", "keyboard"), "gsplsr109"),
    (("worker109", "AA"), "worker109"),
    (("kernel109", "key"), "uipxij109"),
    (("kernel109", "lemon"), "vidbrw109"),
    (("kernel109", "a"), "kernel109"),
    (("kernel109", "zz"), "jdqmdk109"),
    (("kernel109", "AgentU"), "kkvaxf109"),
    (("kernel109", "keyboard"), "uiposl109"),
    (("kernel109", "AA"), "kernel109"),
    (("signal109", "key"), "cmexej109"),
    (("signal109", "lemon"), "dmsbnw109"),
    (("signal109", "a"), "signal109"),
    (("signal109", "zz"), "rhfmzk109"),
    (("signal109", "AgentU"), "sokatf109"),
    (("signal109", "keyboard"), "cmeool109"),
    (("signal109", "AA"), "signal109"),
    (("packet109", "key"), "zeauir109"),
    (("packet109", "lemon"), "aeoyre109"),
    (("packet109", "a"), "packet109"),
    (("packet109", "zz"), "ozbjds109"),
    (("packet109", "AgentU"), "pggxxn109"),
    (("packet109", "keyboard"), "zealst109"),
    (("packet109", "AA"), "packet109"),
    (("router109", "key"), "bssdip109"),
    (("router109", "lemon"), "csghrc109"),
    (("router109", "a"), "router109"),
    (("router109", "zz"), "qntsdq109"),
    (("router109", "AgentU"), "ruygxl109"),
    (("router109", "keyboard"), "bssusr109"),
    (("router109", "AA"), "router109"),
    (("cluster109", "key"), "mpscxcb109"),
    (("cluster109", "lemon"), "npgggpv109"),
    (("cluster109", "a"), "cluster109"),
    (("cluster109", "zz"), "bktrsdq109"),
    (("cluster109", "AgentU"), "cryfmyr109"),
    (("cluster109", "keyboard"), "mpsthei109"),
    (("cluster109", "AA"), "cluster109"),
    (("mirror109", "key"), "wmpbsp109"),
    (("mirror109", "lemon"), "xmdfbc109"),
    (("mirror109", "a"), "mirror109"),
    (("mirror109", "zz"), "lhqqnq109"),
    (("mirror109", "AgentU"), "movehl109"),
    (("mirror109", "keyboard"), "wmpscr109"),
    (("mirror109", "AA"), "mirror109"),
    (("filter109", "key"), "pmjdip109"),
    (("filter109", "lemon"), "qmxhrc109"),
    (("filter109", "a"), "filter109"),
    (("filter109", "zz"), "ehksdq109"),
    (("filter109", "AgentU"), "fopgxl109"),
    (("filter109", "keyboard"), "pmjusr109"),
    (("filter109", "AA"), "filter109"),
    (("ranking109", "key"), "belumlq109"),
    (("ranking109", "lemon"), "cezyvyk109"),
    (("ranking109", "a"), "ranking109"),
    (("ranking109", "zz"), "qzmjhmf109"),
    (("ranking109", "AgentU"), "rgrxbhg109"),
    (("ranking109", "keyboard"), "bellwnx109"),
    (("ranking109", "AA"), "ranking109"),
    (("encoding109", "key"), "orayhgxk109"),
    (("encoding109", "lemon"), "procqtrs109"),
    (("encoding109", "a"), "encoding109"),
    (("encoding109", "zz"), "dmbnchmf109"),
    (("encoding109", "AgentU"), "etgbwcnm109"),
    (("encoding109", "keyboard"), "orapriej109"),
    (("encoding109", "AA"), "encoding109"),
    (("mapping109", "key"), "wenzmlq109"),
    (("mapping109", "lemon"), "xebdvyk109"),
    (("mapping109", "a"), "mapping109"),
    (("mapping109", "zz"), "lzoohmf109"),
    (("mapping109", "AgentU"), "mgtcbhg109"),
    (("mapping109", "keyboard"), "wenqwnx109"),
    (("mapping109", "AA"), "mapping109"),
    (("record109", "key"), "biayvb109"),
    (("record109", "lemon"), "cioceo109"),
    (("record109", "a"), "record109"),
    (("record109", "zz"), "qdbnqc109"),
    (("record109", "AgentU"), "rkgbkx109"),
    (("record109", "keyboard"), "biapfd109"),
    (("record109", "AA"), "record109"),
    (("candle109", "key"), "melnpc109"),
    (("candle109", "lemon"), "nezryp109"),
    (("candle109", "a"), "candle109"),
    (("candle109", "zz"), "bzmckd109"),
    (("candle109", "AgentU"), "cgrqey109"),
    (("candle109", "keyboard"), "meleze109"),
    (("candle109", "AA"), "candle109"),
    (("thread109", "key"), "dlpoeb109"),
    (("thread109", "lemon"), "eldsno109"),
    (("thread109", "a"), "thread109"),
    (("thread109", "zz"), "sgqdzc109"),
    (("thread109", "AgentU"), "tnvrtx109"),
    (("thread109", "keyboard"), "dlpfod109"),
    (("thread109", "AA"), "thread109"),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 109: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 109: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "a"),
        "round 109: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 109: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 109: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 109: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", "AA"),
        "round 109: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "key"),
        "bssxh 109: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 109: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "a"),
        "round 109: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 109: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 109: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 109: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", "AA"),
        "round 109: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 109: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 109: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "a"),
        "round 109: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 109: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 109: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 109: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", "AA"),
        "round 109: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 109: the processor reads the record then stops", "key"),
        "bssxh 109: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 109: the processor reads the record then stops", "lemon"),
        "csgbq 109: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 109: the processor reads the record then stops", "a"),
        "round 109: the processor reads the record then stops",
    ),
    (
        ("round 109: the processor reads the record then stops", "zz"),
        "qntmc 109: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 109: the processor reads the record then stops", "AgentU"),
        "ruyaw 109: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 109: the processor reads the record then stops", "keyboard"),
        "bssor 109: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 109: the processor reads the record then stops", "AA"),
        "round 109: the processor reads the record then stops",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "key"),
        "bssxh 109: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "lemon"),
        "csgbq 109: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "a"),
        "round 109: a worker pulls the next task from the queue",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "zz"),
        "qntmc 109: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 109: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "keyboard"),
        "bssor 109: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 109: a worker pulls the next task from the queue", "AA"),
        "round 109: a worker pulls the next task from the queue",
    ),
    (
        ("round 109: signals travel through the network layer", "key"),
        "bssxh 109: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 109: signals travel through the network layer", "lemon"),
        "csgbq 109: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 109: signals travel through the network layer", "a"),
        "round 109: signals travel through the network layer",
    ),
    (
        ("round 109: signals travel through the network layer", "zz"),
        "qntmc 109: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 109: signals travel through the network layer", "AgentU"),
        "ruyaw 109: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 109: signals travel through the network layer", "keyboard"),
        "bssor 109: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 109: signals travel through the network layer", "AA"),
        "round 109: signals travel through the network layer",
    ),
    (
        ("round 109: the gateway routes each request by policy", "key"),
        "bssxh 109: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 109: the gateway routes each request by policy", "lemon"),
        "csgbq 109: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 109: the gateway routes each request by policy", "a"),
        "round 109: the gateway routes each request by policy",
    ),
    (
        ("round 109: the gateway routes each request by policy", "zz"),
        "qntmc 109: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 109: the gateway routes each request by policy", "AgentU"),
        "ruyaw 109: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 109: the gateway routes each request by policy", "keyboard"),
        "bssor 109: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 109: the gateway routes each request by policy", "AA"),
        "round 109: the gateway routes each request by policy",
    ),
    (("round 109: memory grows until the buffer is full", "key"), "bssxh 109: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 109: memory grows until the buffer is full", "lemon"), "csgbq 109: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 109: memory grows until the buffer is full", "a"), "round 109: memory grows until the buffer is full"),
    (("round 109: memory grows until the buffer is full", "zz"), "qntmc 109: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 109: memory grows until the buffer is full", "AgentU"),
        "ruyaw 109: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 109: memory grows until the buffer is full", "keyboard"),
        "bssor 109: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 109: memory grows until the buffer is full", "AA"), "round 109: memory grows until the buffer is full"),
    (("round 109: the cluster mirrors every packet twice", "key"), "bssxh 109: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 109: the cluster mirrors every packet twice", "lemon"),
        "csgbq 109: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 109: the cluster mirrors every packet twice", "a"), "round 109: the cluster mirrors every packet twice"),
    (("round 109: the cluster mirrors every packet twice", "zz"), "qntmc 109: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 109: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 109: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 109: the cluster mirrors every packet twice", "keyboard"),
        "bssor 109: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 109: the cluster mirrors every packet twice", "AA"), "round 109: the cluster mirrors every packet twice"),
    (
        ("round 109: ranking uses tokens learned from the corpus", "key"),
        "bssxh 109: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 109: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", "a"),
        "round 109: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 109: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 109: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 109: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", "AA"),
        "round 109: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 109: a long session ends when the candle dies", "key"),
        "bssxh 109: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 109: a long session ends when the candle dies", "lemon"),
        "csgbq 109: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 109: a long session ends when the candle dies", "a"),
        "round 109: a long session ends when the candle dies",
    ),
    (
        ("round 109: a long session ends when the candle dies", "zz"),
        "qntmc 109: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 109: a long session ends when the candle dies", "AgentU"),
        "ruyaw 109: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 109: a long session ends when the candle dies", "keyboard"),
        "bssor 109: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 109: a long session ends when the candle dies", "AA"),
        "round 109: a long session ends when the candle dies",
    ),
    (("round 109: encode the prompt then map the result", "key"), "bssxh 109: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 109: encode the prompt then map the result", "lemon"), "csgbq 109: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 109: encode the prompt then map the result", "a"), "round 109: encode the prompt then map the result"),
    (("round 109: encode the prompt then map the result", "zz"), "qntmc 109: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 109: encode the prompt then map the result", "AgentU"),
        "ruyaw 109: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 109: encode the prompt then map the result", "keyboard"),
        "bssor 109: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 109: encode the prompt then map the result", "AA"), "round 109: encode the prompt then map the result"),
    (("round 109: the kernel wakes the worker at dawn", "key"), "bssxh 109: rri iovlop ukocc xfo ambocb er neux"),
    (("round 109: the kernel wakes the worker at dawn", "lemon"), "csgbq 109: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 109: the kernel wakes the worker at dawn", "a"), "round 109: the kernel wakes the worker at dawn"),
    (("round 109: the kernel wakes the worker at dawn", "zz"), "qntmc 109: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 109: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 109: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 109: the kernel wakes the worker at dawn", "keyboard"), "bssor 109: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 109: the kernel wakes the worker at dawn", "AA"), "round 109: the kernel wakes the worker at dawn"),
    (("round 109: service latency drops after the patch", "key"), "bssxh 109: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 109: service latency drops after the patch", "lemon"), "csgbq 109: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 109: service latency drops after the patch", "a"), "round 109: service latency drops after the patch"),
    (("round 109: service latency drops after the patch", "zz"), "qntmc 109: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 109: service latency drops after the patch", "AgentU"),
        "ruyaw 109: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 109: service latency drops after the patch", "keyboard"),
        "bssor 109: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 109: service latency drops after the patch", "AA"), "round 109: service latency drops after the patch"),
    (
        ("round 109: the library caches every vector it sees", "key"),
        "bssxh 109: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 109: the library caches every vector it sees", "lemon"),
        "csgbq 109: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 109: the library caches every vector it sees", "a"), "round 109: the library caches every vector it sees"),
    (
        ("round 109: the library caches every vector it sees", "zz"),
        "qntmc 109: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 109: the library caches every vector it sees", "AgentU"),
        "ruyaw 109: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 109: the library caches every vector it sees", "keyboard"),
        "bssor 109: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 109: the library caches every vector it sees", "AA"),
        "round 109: the library caches every vector it sees",
    ),
    (("round 109: agents argue then the debate resolves", "key"), "bssxh 109: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 109: agents argue then the debate resolves", "lemon"), "csgbq 109: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 109: agents argue then the debate resolves", "a"), "round 109: agents argue then the debate resolves"),
    (("round 109: agents argue then the debate resolves", "zz"), "qntmc 109: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 109: agents argue then the debate resolves", "AgentU"),
        "ruyaw 109: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 109: agents argue then the debate resolves", "keyboard"),
        "bssor 109: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 109: agents argue then the debate resolves", "AA"), "round 109: agents argue then the debate resolves"),
    (("round 109: the filter keeps only strong matches", "key"), "bssxh 109: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 109: the filter keeps only strong matches", "lemon"), "csgbq 109: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 109: the filter keeps only strong matches", "a"), "round 109: the filter keeps only strong matches"),
    (("round 109: the filter keeps only strong matches", "zz"), "qntmc 109: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 109: the filter keeps only strong matches", "AgentU"), "ruyaw 109: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 109: the filter keeps only strong matches", "keyboard"),
        "bssor 109: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 109: the filter keeps only strong matches", "AA"), "round 109: the filter keeps only strong matches"),
    (("round 109: the model answers with a short reply", "key"), "bssxh 109: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 109: the model answers with a short reply", "lemon"), "csgbq 109: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 109: the model answers with a short reply", "a"), "round 109: the model answers with a short reply"),
    (("round 109: the model answers with a short reply", "zz"), "qntmc 109: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 109: the model answers with a short reply", "AgentU"), "ruyaw 109: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 109: the model answers with a short reply", "keyboard"),
        "bssor 109: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 109: the model answers with a short reply", "AA"), "round 109: the model answers with a short reply"),
    (
        ("round 109: the recorder stores the reasoning trace", "key"),
        "bssxh 109: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 109: the recorder stores the reasoning trace", "lemon"),
        "csgbq 109: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 109: the recorder stores the reasoning trace", "a"), "round 109: the recorder stores the reasoning trace"),
    (
        ("round 109: the recorder stores the reasoning trace", "zz"),
        "qntmc 109: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 109: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 109: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 109: the recorder stores the reasoning trace", "keyboard"),
        "bssor 109: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 109: the recorder stores the reasoning trace", "AA"),
        "round 109: the recorder stores the reasoning trace",
    ),
    (("round 109: the angel watches the processor run", "key"), "bssxh 109: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 109: the angel watches the processor run", "lemon"), "csgbq 109: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 109: the angel watches the processor run", "a"), "round 109: the angel watches the processor run"),
    (("round 109: the angel watches the processor run", "zz"), "qntmc 109: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 109: the angel watches the processor run", "AgentU"), "ruyaw 109: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 109: the angel watches the processor run", "keyboard"), "bssor 109: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 109: the angel watches the processor run", "AA"), "round 109: the angel watches the processor run"),
    (("round 109: angle of the vector decides the match", "key"), "bssxh 109: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 109: angle of the vector decides the match", "lemon"), "csgbq 109: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 109: angle of the vector decides the match", "a"), "round 109: angle of the vector decides the match"),
    (("round 109: angle of the vector decides the match", "zz"), "qntmc 109: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 109: angle of the vector decides the match", "AgentU"),
        "ruyaw 109: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 109: angle of the vector decides the match", "keyboard"),
        "bssor 109: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 109: angle of the vector decides the match", "AA"), "round 109: angle of the vector decides the match"),
    (
        ("round 109: the candle burns twice as long at night", "key"),
        "bssxh 109: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 109: the candle burns twice as long at night", "lemon"),
        "csgbq 109: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 109: the candle burns twice as long at night", "a"), "round 109: the candle burns twice as long at night"),
    (
        ("round 109: the candle burns twice as long at night", "zz"),
        "qntmc 109: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 109: the candle burns twice as long at night", "AgentU"),
        "ruyaw 109: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 109: the candle burns twice as long at night", "keyboard"),
        "bssor 109: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 109: the candle burns twice as long at night", "AA"),
        "round 109: the candle burns twice as long at night",
    ),
    (("round 109: a mirror of the universe in one line", "key"), "bssxh 109: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 109: a mirror of the universe in one line", "lemon"), "csgbq 109: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 109: a mirror of the universe in one line", "a"), "round 109: a mirror of the universe in one line"),
    (("round 109: a mirror of the universe in one line", "zz"), "qntmc 109: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 109: a mirror of the universe in one line", "AgentU"), "ruyaw 109: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 109: a mirror of the universe in one line", "keyboard"),
        "bssor 109: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 109: a mirror of the universe in one line", "AA"), "round 109: a mirror of the universe in one line"),
    (("round 109: the queue drains before the storm", "key"), "bssxh 109: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 109: the queue drains before the storm", "lemon"), "csgbq 109: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 109: the queue drains before the storm", "a"), "round 109: the queue drains before the storm"),
    (("round 109: the queue drains before the storm", "zz"), "qntmc 109: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 109: the queue drains before the storm", "AgentU"), "ruyaw 109: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 109: the queue drains before the storm", "keyboard"), "bssor 109: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 109: the queue drains before the storm", "AA"), "round 109: the queue drains before the storm"),
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
