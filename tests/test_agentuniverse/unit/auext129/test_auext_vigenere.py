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
    (("kitten129", "key"), "umrdil129"),
    (("kitten129", "lemon"), "vmfhry129"),
    (("kitten129", "a"), "kitten129"),
    (("kitten129", "zz"), "jhssdm129"),
    (("kitten129", "AgentU"), "koxgxh129"),
    (("kitten129", "keyboard"), "umrusn129"),
    (("kitten129", "AA"), "kitten129"),
    (("sitting129", "key"), "cmrdmlq129"),
    (("sitting129", "lemon"), "dmfhvyk129"),
    (("sitting129", "a"), "sitting129"),
    (("sitting129", "zz"), "rhsshmf129"),
    (("sitting129", "AgentU"), "soxgbhg129"),
    (("sitting129", "keyboard"), "cmruwnx129"),
    (("sitting129", "AA"), "sitting129"),
    (("agent129", "key"), "kkcxx129"),
    (("agent129", "lemon"), "lkqbg129"),
    (("agent129", "a"), "agent129"),
    (("agent129", "zz"), "zfdms129"),
    (("agent129", "AgentU"), "amiam129"),
    (("agent129", "keyboard"), "kkcoh129"),
    (("agent129", "AA"), "agent129"),
    (("angle129", "key"), "krevi129"),
    (("angle129", "lemon"), "lrszr129"),
    (("angle129", "a"), "angle129"),
    (("angle129", "zz"), "zmfkd129"),
    (("angle129", "AgentU"), "atkyx129"),
    (("angle129", "keyboard"), "krems129"),
    (("angle129", "AA"), "angle129"),
    (("universe129", "key"), "ergfipci129"),
    (("universe129", "lemon"), "frujrcwq129"),
    (("universe129", "a"), "universe129"),
    (("universe129", "zz"), "tmhudqrd129"),
    (("universe129", "AgentU"), "utmixlsk129"),
    (("universe129", "keyboard"), "ergwsrjh129"),
    (("universe129", "AA"), "universe129"),
    (("memory129", "key"), "wikyvw129"),
    (("memory129", "lemon"), "xiycej129"),
    (("memory129", "a"), "memory129"),
    (("memory129", "zz"), "ldlnqx129"),
    (("memory129", "AgentU"), "mkqbks129"),
    (("memory129", "keyboard"), "wikpfy129"),
    (("memory129", "AA"), "memory129"),
    (("stream129", "key"), "cxpoek129"),
    (("stream129", "lemon"), "dxdsnx129"),
    (("stream129", "a"), "stream129"),
    (("stream129", "zz"), "rsqdzl129"),
    (("stream129", "AgentU"), "szvrtg129"),
    (("stream129", "keyboard"), "cxpfom129"),
    (("stream129", "AA"), "stream129"),
    (("context129", "key"), "msldivd129"),
    (("context129", "lemon"), "nszhrix129"),
    (("context129", "a"), "context129"),
    (("context129", "zz"), "bnmsdws129"),
    (("context129", "AgentU"), "curgxrt129"),
    (("context129", "keyboard"), "mslusxk129"),
    (("context129", "AA"), "context129"),
    (("knowledge129", "key"), "urmgpcnkc129"),
    (("knowledge129", "lemon"), "vrakyphss129"),
    (("knowledge129", "a"), "knowledge129"),
    (("knowledge129", "zz"), "jmnvkdcfd129"),
    (("knowledge129", "AgentU"), "ktsjeydmi129"),
    (("knowledge129", "keyboard"), "urmxzeujo129"),
    (("knowledge129", "AA"), "knowledge129"),
    (("vector129", "key"), "fiadsp129"),
    (("vector129", "lemon"), "giohbc129"),
    (("vector129", "a"), "vector129"),
    (("vector129", "zz"), "udbsnq129"),
    (("vector129", "AgentU"), "vkgghl129"),
    (("vector129", "keyboard"), "fiaucr129"),
    (("vector129", "AA"), "vector129"),
    (("processor129", "key"), "zvmmiqcsp129"),
    (("processor129", "lemon"), "avaqrdwaf129"),
    (("processor129", "a"), "processor129"),
    (("processor129", "zz"), "oqnbdrrnq129"),
    (("processor129", "AgentU"), "pxspxmsuv129"),
    (("processor129", "keyboard"), "zvmdssjrb129"),
    (("processor129", "AA"), "processor129"),
    (("reasoning129", "key"), "biycslsre129"),
    (("reasoning129", "lemon"), "cimgbymzu129"),
    (("reasoning129", "a"), "reasoning129"),
    (("reasoning129", "zz"), "qdzrnmhmf129"),
    (("reasoning129", "AgentU"), "rkefhhitk129"),
    (("reasoning129", "keyboard"), "biytcnzqq129"),
    (("reasoning129", "AA"), "reasoning129"),
    (("machine129", "key"), "wearmlo129"),
    (("machine129", "lemon"), "xeovvyi129"),
    (("machine129", "a"), "machine129"),
    (("machine129", "zz"), "lzbghmd129"),
    (("machine129", "AgentU"), "mggubhe129"),
    (("machine129", "keyboard"), "weaiwnv129"),
    (("machine129", "AA"), "machine129"),
    (("learning129", "key"), "viybrgxk129"),
    (("learning129", "lemon"), "wimfatrs129"),
    (("learning129", "a"), "learning129"),
    (("learning129", "zz"), "kdzqmhmf129"),
    (("learning129", "AgentU"), "lkeegcnm129"),
    (("learning129", "keyboard"), "viysbiej129"),
    (("learning129", "AA"), "learning129"),
    (("model129", "key"), "wsbop129"),
    (("model129", "lemon"), "xspsy129"),
    (("model129", "a"), "model129"),
    (("model129", "zz"), "lncdk129"),
    (("model129", "AgentU"), "muhre129"),
    (("model129", "keyboard"), "wsbfz129"),
    (("model129", "AA"), "model129"),
    (("token129", "key"), "dsior129"),
    (("token129", "lemon"), "eswsa129"),
    (("token129", "a"), "token129"),
    (("token129", "zz"), "snjdm129"),
    (("token129", "AgentU"), "tuorg129"),
    (("token129", "keyboard"), "dsifb129"),
    (("token129", "AA"), "token129"),
    (("prompt129", "key"), "zvmwtr129"),
    (("prompt129", "lemon"), "avaace129"),
    (("prompt129", "a"), "prompt129"),
    (("prompt129", "zz"), "oqnlos129"),
    (("prompt129", "AgentU"), "pxszin129"),
    (("prompt129", "keyboard"), "zvmndt129"),
    (("prompt129", "AA"), "prompt129"),
    (("session129", "key"), "ciqcmmx129"),
    (("session129", "lemon"), "diegvzr129"),
    (("session129", "a"), "session129"),
    (("session129", "zz"), "rdrrhnm129"),
    (("session129", "AgentU"), "skwfbin129"),
    (("session129", "keyboard"), "ciqtwoe129"),
    (("session129", "AA"), "session129"),
    (("library129", "key"), "vmzbepi129"),
    (("library129", "lemon"), "wmnfncc129"),
    (("library129", "a"), "library129"),
    (("library129", "zz"), "khaqzqx129"),
    (("library129", "AgentU"), "lofetly129"),
    (("library129", "keyboard"), "vmzsorp129"),
    (("library129", "AA"), "library129"),
    (("service129", "key"), "cipfmao129"),
    (("service129", "lemon"), "didjvni129"),
    (("service129", "a"), "service129"),
    (("service129", "zz"), "rdquhbd129"),
    (("service129", "AgentU"), "skvibwe129"),
    (("service129", "keyboard"), "cipwwcv129"),
    (("service129", "AA"), "service129"),
    (("gateway129", "key"), "qeroayi129"),
    (("gateway129", "lemon"), "refsjlc129"),
    (("gateway129", "a"), "gateway129"),
    (("gateway129", "zz"), "fzsdvzx129"),
    (("gateway129", "AgentU"), "ggxrpuy129"),
    (("gateway129", "keyboard"), "qerfkap129"),
    (("gateway129", "AA"), "gateway129"),
    (("storage129", "key"), "cxmbeeo129"),
    (("storage129", "lemon"), "dxafnri129"),
    (("storage129", "a"), "storage129"),
    (("storage129", "zz"), "rsnqzfd129"),
    (("storage129", "AgentU"), "szsetae129"),
    (("storage129", "keyboard"), "cxmsogv129"),
    (("storage129", "AA"), "storage129"),
    (("network129", "key"), "xirgspu129"),
    (("network129", "lemon"), "yifkbco129"),
    (("network129", "a"), "network129"),
    (("network129", "zz"), "mdsvnqj129"),
    (("network129", "AgentU"), "nkxjhlk129"),
    (("network129", "keyboard"), "xirxcrb129"),
    (("network129", "AA"), "network129"),
    (("latency129", "key"), "verorai129"),
    (("latency129", "lemon"), "wefsanc129"),
    (("latency129", "a"), "latency129"),
    (("latency129", "zz"), "kzsdmbx129"),
    (("latency129", "AgentU"), "lgxrgwy129"),
    (("latency129", "keyboard"), "verfbcp129"),
    (("latency129", "AA"), "latency129"),
    (("buffer129", "key"), "lydpip129"),
    (("buffer129", "lemon"), "myrtrc129"),
    (("buffer129", "a"), "buffer129"),
    (("buffer129", "zz"), "ateedq129"),
    (("buffer129", "AgentU"), "bajsxl129"),
    (("buffer129", "keyboard"), "lydgsr129"),
    (("buffer129", "AA"), "buffer129"),
    (("queue129", "key"), "aycei129"),
    (("queue129", "lemon"), "byqir129"),
    (("queue129", "a"), "queue129"),
    (("queue129", "zz"), "ptdtd129"),
    (("queue129", "AgentU"), "qaihx129"),
    (("queue129", "keyboard"), "aycvs129"),
    (("queue129", "AA"), "queue129"),
    (("worker129", "key"), "gspuip129"),
    (("worker129", "lemon"), "hsdyrc129"),
    (("worker129", "a"), "worker129"),
    (("worker129", "zz"), "vnqjdq129"),
    (("worker129", "AgentU"), "wuvxxl129"),
    (("worker129", "keyboard"), "gsplsr129"),
    (("worker129", "AA"), "worker129"),
    (("kernel129", "key"), "uipxij129"),
    (("kernel129", "lemon"), "vidbrw129"),
    (("kernel129", "a"), "kernel129"),
    (("kernel129", "zz"), "jdqmdk129"),
    (("kernel129", "AgentU"), "kkvaxf129"),
    (("kernel129", "keyboard"), "uiposl129"),
    (("kernel129", "AA"), "kernel129"),
    (("signal129", "key"), "cmexej129"),
    (("signal129", "lemon"), "dmsbnw129"),
    (("signal129", "a"), "signal129"),
    (("signal129", "zz"), "rhfmzk129"),
    (("signal129", "AgentU"), "sokatf129"),
    (("signal129", "keyboard"), "cmeool129"),
    (("signal129", "AA"), "signal129"),
    (("packet129", "key"), "zeauir129"),
    (("packet129", "lemon"), "aeoyre129"),
    (("packet129", "a"), "packet129"),
    (("packet129", "zz"), "ozbjds129"),
    (("packet129", "AgentU"), "pggxxn129"),
    (("packet129", "keyboard"), "zealst129"),
    (("packet129", "AA"), "packet129"),
    (("router129", "key"), "bssdip129"),
    (("router129", "lemon"), "csghrc129"),
    (("router129", "a"), "router129"),
    (("router129", "zz"), "qntsdq129"),
    (("router129", "AgentU"), "ruygxl129"),
    (("router129", "keyboard"), "bssusr129"),
    (("router129", "AA"), "router129"),
    (("cluster129", "key"), "mpscxcb129"),
    (("cluster129", "lemon"), "npgggpv129"),
    (("cluster129", "a"), "cluster129"),
    (("cluster129", "zz"), "bktrsdq129"),
    (("cluster129", "AgentU"), "cryfmyr129"),
    (("cluster129", "keyboard"), "mpsthei129"),
    (("cluster129", "AA"), "cluster129"),
    (("mirror129", "key"), "wmpbsp129"),
    (("mirror129", "lemon"), "xmdfbc129"),
    (("mirror129", "a"), "mirror129"),
    (("mirror129", "zz"), "lhqqnq129"),
    (("mirror129", "AgentU"), "movehl129"),
    (("mirror129", "keyboard"), "wmpscr129"),
    (("mirror129", "AA"), "mirror129"),
    (("filter129", "key"), "pmjdip129"),
    (("filter129", "lemon"), "qmxhrc129"),
    (("filter129", "a"), "filter129"),
    (("filter129", "zz"), "ehksdq129"),
    (("filter129", "AgentU"), "fopgxl129"),
    (("filter129", "keyboard"), "pmjusr129"),
    (("filter129", "AA"), "filter129"),
    (("ranking129", "key"), "belumlq129"),
    (("ranking129", "lemon"), "cezyvyk129"),
    (("ranking129", "a"), "ranking129"),
    (("ranking129", "zz"), "qzmjhmf129"),
    (("ranking129", "AgentU"), "rgrxbhg129"),
    (("ranking129", "keyboard"), "bellwnx129"),
    (("ranking129", "AA"), "ranking129"),
    (("encoding129", "key"), "orayhgxk129"),
    (("encoding129", "lemon"), "procqtrs129"),
    (("encoding129", "a"), "encoding129"),
    (("encoding129", "zz"), "dmbnchmf129"),
    (("encoding129", "AgentU"), "etgbwcnm129"),
    (("encoding129", "keyboard"), "orapriej129"),
    (("encoding129", "AA"), "encoding129"),
    (("mapping129", "key"), "wenzmlq129"),
    (("mapping129", "lemon"), "xebdvyk129"),
    (("mapping129", "a"), "mapping129"),
    (("mapping129", "zz"), "lzoohmf129"),
    (("mapping129", "AgentU"), "mgtcbhg129"),
    (("mapping129", "keyboard"), "wenqwnx129"),
    (("mapping129", "AA"), "mapping129"),
    (("record129", "key"), "biayvb129"),
    (("record129", "lemon"), "cioceo129"),
    (("record129", "a"), "record129"),
    (("record129", "zz"), "qdbnqc129"),
    (("record129", "AgentU"), "rkgbkx129"),
    (("record129", "keyboard"), "biapfd129"),
    (("record129", "AA"), "record129"),
    (("candle129", "key"), "melnpc129"),
    (("candle129", "lemon"), "nezryp129"),
    (("candle129", "a"), "candle129"),
    (("candle129", "zz"), "bzmckd129"),
    (("candle129", "AgentU"), "cgrqey129"),
    (("candle129", "keyboard"), "meleze129"),
    (("candle129", "AA"), "candle129"),
    (("thread129", "key"), "dlpoeb129"),
    (("thread129", "lemon"), "eldsno129"),
    (("thread129", "a"), "thread129"),
    (("thread129", "zz"), "sgqdzc129"),
    (("thread129", "AgentU"), "tnvrtx129"),
    (("thread129", "keyboard"), "dlpfod129"),
    (("thread129", "AA"), "thread129"),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 129: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 129: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "a"),
        "round 129: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 129: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 129: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 129: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", "AA"),
        "round 129: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "key"),
        "bssxh 129: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 129: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "a"),
        "round 129: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 129: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 129: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 129: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", "AA"),
        "round 129: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 129: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 129: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "a"),
        "round 129: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 129: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 129: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 129: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", "AA"),
        "round 129: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 129: the processor reads the record then stops", "key"),
        "bssxh 129: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 129: the processor reads the record then stops", "lemon"),
        "csgbq 129: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 129: the processor reads the record then stops", "a"),
        "round 129: the processor reads the record then stops",
    ),
    (
        ("round 129: the processor reads the record then stops", "zz"),
        "qntmc 129: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 129: the processor reads the record then stops", "AgentU"),
        "ruyaw 129: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 129: the processor reads the record then stops", "keyboard"),
        "bssor 129: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 129: the processor reads the record then stops", "AA"),
        "round 129: the processor reads the record then stops",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "key"),
        "bssxh 129: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "lemon"),
        "csgbq 129: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "a"),
        "round 129: a worker pulls the next task from the queue",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "zz"),
        "qntmc 129: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 129: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "keyboard"),
        "bssor 129: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 129: a worker pulls the next task from the queue", "AA"),
        "round 129: a worker pulls the next task from the queue",
    ),
    (
        ("round 129: signals travel through the network layer", "key"),
        "bssxh 129: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 129: signals travel through the network layer", "lemon"),
        "csgbq 129: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 129: signals travel through the network layer", "a"),
        "round 129: signals travel through the network layer",
    ),
    (
        ("round 129: signals travel through the network layer", "zz"),
        "qntmc 129: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 129: signals travel through the network layer", "AgentU"),
        "ruyaw 129: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 129: signals travel through the network layer", "keyboard"),
        "bssor 129: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 129: signals travel through the network layer", "AA"),
        "round 129: signals travel through the network layer",
    ),
    (
        ("round 129: the gateway routes each request by policy", "key"),
        "bssxh 129: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 129: the gateway routes each request by policy", "lemon"),
        "csgbq 129: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 129: the gateway routes each request by policy", "a"),
        "round 129: the gateway routes each request by policy",
    ),
    (
        ("round 129: the gateway routes each request by policy", "zz"),
        "qntmc 129: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 129: the gateway routes each request by policy", "AgentU"),
        "ruyaw 129: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 129: the gateway routes each request by policy", "keyboard"),
        "bssor 129: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 129: the gateway routes each request by policy", "AA"),
        "round 129: the gateway routes each request by policy",
    ),
    (("round 129: memory grows until the buffer is full", "key"), "bssxh 129: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 129: memory grows until the buffer is full", "lemon"), "csgbq 129: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 129: memory grows until the buffer is full", "a"), "round 129: memory grows until the buffer is full"),
    (("round 129: memory grows until the buffer is full", "zz"), "qntmc 129: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 129: memory grows until the buffer is full", "AgentU"),
        "ruyaw 129: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 129: memory grows until the buffer is full", "keyboard"),
        "bssor 129: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 129: memory grows until the buffer is full", "AA"), "round 129: memory grows until the buffer is full"),
    (("round 129: the cluster mirrors every packet twice", "key"), "bssxh 129: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 129: the cluster mirrors every packet twice", "lemon"),
        "csgbq 129: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 129: the cluster mirrors every packet twice", "a"), "round 129: the cluster mirrors every packet twice"),
    (("round 129: the cluster mirrors every packet twice", "zz"), "qntmc 129: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 129: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 129: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 129: the cluster mirrors every packet twice", "keyboard"),
        "bssor 129: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 129: the cluster mirrors every packet twice", "AA"), "round 129: the cluster mirrors every packet twice"),
    (
        ("round 129: ranking uses tokens learned from the corpus", "key"),
        "bssxh 129: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 129: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", "a"),
        "round 129: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 129: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 129: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 129: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", "AA"),
        "round 129: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 129: a long session ends when the candle dies", "key"),
        "bssxh 129: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 129: a long session ends when the candle dies", "lemon"),
        "csgbq 129: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 129: a long session ends when the candle dies", "a"),
        "round 129: a long session ends when the candle dies",
    ),
    (
        ("round 129: a long session ends when the candle dies", "zz"),
        "qntmc 129: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 129: a long session ends when the candle dies", "AgentU"),
        "ruyaw 129: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 129: a long session ends when the candle dies", "keyboard"),
        "bssor 129: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 129: a long session ends when the candle dies", "AA"),
        "round 129: a long session ends when the candle dies",
    ),
    (("round 129: encode the prompt then map the result", "key"), "bssxh 129: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 129: encode the prompt then map the result", "lemon"), "csgbq 129: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 129: encode the prompt then map the result", "a"), "round 129: encode the prompt then map the result"),
    (("round 129: encode the prompt then map the result", "zz"), "qntmc 129: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 129: encode the prompt then map the result", "AgentU"),
        "ruyaw 129: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 129: encode the prompt then map the result", "keyboard"),
        "bssor 129: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 129: encode the prompt then map the result", "AA"), "round 129: encode the prompt then map the result"),
    (("round 129: the kernel wakes the worker at dawn", "key"), "bssxh 129: rri iovlop ukocc xfo ambocb er neux"),
    (("round 129: the kernel wakes the worker at dawn", "lemon"), "csgbq 129: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 129: the kernel wakes the worker at dawn", "a"), "round 129: the kernel wakes the worker at dawn"),
    (("round 129: the kernel wakes the worker at dawn", "zz"), "qntmc 129: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 129: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 129: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 129: the kernel wakes the worker at dawn", "keyboard"), "bssor 129: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 129: the kernel wakes the worker at dawn", "AA"), "round 129: the kernel wakes the worker at dawn"),
    (("round 129: service latency drops after the patch", "key"), "bssxh 129: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 129: service latency drops after the patch", "lemon"), "csgbq 129: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 129: service latency drops after the patch", "a"), "round 129: service latency drops after the patch"),
    (("round 129: service latency drops after the patch", "zz"), "qntmc 129: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 129: service latency drops after the patch", "AgentU"),
        "ruyaw 129: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 129: service latency drops after the patch", "keyboard"),
        "bssor 129: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 129: service latency drops after the patch", "AA"), "round 129: service latency drops after the patch"),
    (
        ("round 129: the library caches every vector it sees", "key"),
        "bssxh 129: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 129: the library caches every vector it sees", "lemon"),
        "csgbq 129: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 129: the library caches every vector it sees", "a"), "round 129: the library caches every vector it sees"),
    (
        ("round 129: the library caches every vector it sees", "zz"),
        "qntmc 129: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 129: the library caches every vector it sees", "AgentU"),
        "ruyaw 129: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 129: the library caches every vector it sees", "keyboard"),
        "bssor 129: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 129: the library caches every vector it sees", "AA"),
        "round 129: the library caches every vector it sees",
    ),
    (("round 129: agents argue then the debate resolves", "key"), "bssxh 129: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 129: agents argue then the debate resolves", "lemon"), "csgbq 129: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 129: agents argue then the debate resolves", "a"), "round 129: agents argue then the debate resolves"),
    (("round 129: agents argue then the debate resolves", "zz"), "qntmc 129: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 129: agents argue then the debate resolves", "AgentU"),
        "ruyaw 129: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 129: agents argue then the debate resolves", "keyboard"),
        "bssor 129: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 129: agents argue then the debate resolves", "AA"), "round 129: agents argue then the debate resolves"),
    (("round 129: the filter keeps only strong matches", "key"), "bssxh 129: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 129: the filter keeps only strong matches", "lemon"), "csgbq 129: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 129: the filter keeps only strong matches", "a"), "round 129: the filter keeps only strong matches"),
    (("round 129: the filter keeps only strong matches", "zz"), "qntmc 129: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 129: the filter keeps only strong matches", "AgentU"), "ruyaw 129: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 129: the filter keeps only strong matches", "keyboard"),
        "bssor 129: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 129: the filter keeps only strong matches", "AA"), "round 129: the filter keeps only strong matches"),
    (("round 129: the model answers with a short reply", "key"), "bssxh 129: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 129: the model answers with a short reply", "lemon"), "csgbq 129: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 129: the model answers with a short reply", "a"), "round 129: the model answers with a short reply"),
    (("round 129: the model answers with a short reply", "zz"), "qntmc 129: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 129: the model answers with a short reply", "AgentU"), "ruyaw 129: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 129: the model answers with a short reply", "keyboard"),
        "bssor 129: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 129: the model answers with a short reply", "AA"), "round 129: the model answers with a short reply"),
    (
        ("round 129: the recorder stores the reasoning trace", "key"),
        "bssxh 129: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 129: the recorder stores the reasoning trace", "lemon"),
        "csgbq 129: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 129: the recorder stores the reasoning trace", "a"), "round 129: the recorder stores the reasoning trace"),
    (
        ("round 129: the recorder stores the reasoning trace", "zz"),
        "qntmc 129: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 129: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 129: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 129: the recorder stores the reasoning trace", "keyboard"),
        "bssor 129: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 129: the recorder stores the reasoning trace", "AA"),
        "round 129: the recorder stores the reasoning trace",
    ),
    (("round 129: the angel watches the processor run", "key"), "bssxh 129: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 129: the angel watches the processor run", "lemon"), "csgbq 129: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 129: the angel watches the processor run", "a"), "round 129: the angel watches the processor run"),
    (("round 129: the angel watches the processor run", "zz"), "qntmc 129: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 129: the angel watches the processor run", "AgentU"), "ruyaw 129: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 129: the angel watches the processor run", "keyboard"), "bssor 129: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 129: the angel watches the processor run", "AA"), "round 129: the angel watches the processor run"),
    (("round 129: angle of the vector decides the match", "key"), "bssxh 129: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 129: angle of the vector decides the match", "lemon"), "csgbq 129: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 129: angle of the vector decides the match", "a"), "round 129: angle of the vector decides the match"),
    (("round 129: angle of the vector decides the match", "zz"), "qntmc 129: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 129: angle of the vector decides the match", "AgentU"),
        "ruyaw 129: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 129: angle of the vector decides the match", "keyboard"),
        "bssor 129: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 129: angle of the vector decides the match", "AA"), "round 129: angle of the vector decides the match"),
    (
        ("round 129: the candle burns twice as long at night", "key"),
        "bssxh 129: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 129: the candle burns twice as long at night", "lemon"),
        "csgbq 129: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 129: the candle burns twice as long at night", "a"), "round 129: the candle burns twice as long at night"),
    (
        ("round 129: the candle burns twice as long at night", "zz"),
        "qntmc 129: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 129: the candle burns twice as long at night", "AgentU"),
        "ruyaw 129: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 129: the candle burns twice as long at night", "keyboard"),
        "bssor 129: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 129: the candle burns twice as long at night", "AA"),
        "round 129: the candle burns twice as long at night",
    ),
    (("round 129: a mirror of the universe in one line", "key"), "bssxh 129: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 129: a mirror of the universe in one line", "lemon"), "csgbq 129: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 129: a mirror of the universe in one line", "a"), "round 129: a mirror of the universe in one line"),
    (("round 129: a mirror of the universe in one line", "zz"), "qntmc 129: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 129: a mirror of the universe in one line", "AgentU"), "ruyaw 129: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 129: a mirror of the universe in one line", "keyboard"),
        "bssor 129: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 129: a mirror of the universe in one line", "AA"), "round 129: a mirror of the universe in one line"),
    (("round 129: the queue drains before the storm", "key"), "bssxh 129: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 129: the queue drains before the storm", "lemon"), "csgbq 129: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 129: the queue drains before the storm", "a"), "round 129: the queue drains before the storm"),
    (("round 129: the queue drains before the storm", "zz"), "qntmc 129: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 129: the queue drains before the storm", "AgentU"), "ruyaw 129: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 129: the queue drains before the storm", "keyboard"), "bssor 129: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 129: the queue drains before the storm", "AA"), "round 129: the queue drains before the storm"),
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
