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
    (("kitten146", "key"), "umrdil146"),
    (("kitten146", "lemon"), "vmfhry146"),
    (("kitten146", "a"), "kitten146"),
    (("kitten146", "zz"), "jhssdm146"),
    (("kitten146", "AgentU"), "koxgxh146"),
    (("kitten146", "keyboard"), "umrusn146"),
    (("kitten146", "AA"), "kitten146"),
    (("sitting146", "key"), "cmrdmlq146"),
    (("sitting146", "lemon"), "dmfhvyk146"),
    (("sitting146", "a"), "sitting146"),
    (("sitting146", "zz"), "rhsshmf146"),
    (("sitting146", "AgentU"), "soxgbhg146"),
    (("sitting146", "keyboard"), "cmruwnx146"),
    (("sitting146", "AA"), "sitting146"),
    (("agent146", "key"), "kkcxx146"),
    (("agent146", "lemon"), "lkqbg146"),
    (("agent146", "a"), "agent146"),
    (("agent146", "zz"), "zfdms146"),
    (("agent146", "AgentU"), "amiam146"),
    (("agent146", "keyboard"), "kkcoh146"),
    (("agent146", "AA"), "agent146"),
    (("angle146", "key"), "krevi146"),
    (("angle146", "lemon"), "lrszr146"),
    (("angle146", "a"), "angle146"),
    (("angle146", "zz"), "zmfkd146"),
    (("angle146", "AgentU"), "atkyx146"),
    (("angle146", "keyboard"), "krems146"),
    (("angle146", "AA"), "angle146"),
    (("universe146", "key"), "ergfipci146"),
    (("universe146", "lemon"), "frujrcwq146"),
    (("universe146", "a"), "universe146"),
    (("universe146", "zz"), "tmhudqrd146"),
    (("universe146", "AgentU"), "utmixlsk146"),
    (("universe146", "keyboard"), "ergwsrjh146"),
    (("universe146", "AA"), "universe146"),
    (("memory146", "key"), "wikyvw146"),
    (("memory146", "lemon"), "xiycej146"),
    (("memory146", "a"), "memory146"),
    (("memory146", "zz"), "ldlnqx146"),
    (("memory146", "AgentU"), "mkqbks146"),
    (("memory146", "keyboard"), "wikpfy146"),
    (("memory146", "AA"), "memory146"),
    (("stream146", "key"), "cxpoek146"),
    (("stream146", "lemon"), "dxdsnx146"),
    (("stream146", "a"), "stream146"),
    (("stream146", "zz"), "rsqdzl146"),
    (("stream146", "AgentU"), "szvrtg146"),
    (("stream146", "keyboard"), "cxpfom146"),
    (("stream146", "AA"), "stream146"),
    (("context146", "key"), "msldivd146"),
    (("context146", "lemon"), "nszhrix146"),
    (("context146", "a"), "context146"),
    (("context146", "zz"), "bnmsdws146"),
    (("context146", "AgentU"), "curgxrt146"),
    (("context146", "keyboard"), "mslusxk146"),
    (("context146", "AA"), "context146"),
    (("knowledge146", "key"), "urmgpcnkc146"),
    (("knowledge146", "lemon"), "vrakyphss146"),
    (("knowledge146", "a"), "knowledge146"),
    (("knowledge146", "zz"), "jmnvkdcfd146"),
    (("knowledge146", "AgentU"), "ktsjeydmi146"),
    (("knowledge146", "keyboard"), "urmxzeujo146"),
    (("knowledge146", "AA"), "knowledge146"),
    (("vector146", "key"), "fiadsp146"),
    (("vector146", "lemon"), "giohbc146"),
    (("vector146", "a"), "vector146"),
    (("vector146", "zz"), "udbsnq146"),
    (("vector146", "AgentU"), "vkgghl146"),
    (("vector146", "keyboard"), "fiaucr146"),
    (("vector146", "AA"), "vector146"),
    (("processor146", "key"), "zvmmiqcsp146"),
    (("processor146", "lemon"), "avaqrdwaf146"),
    (("processor146", "a"), "processor146"),
    (("processor146", "zz"), "oqnbdrrnq146"),
    (("processor146", "AgentU"), "pxspxmsuv146"),
    (("processor146", "keyboard"), "zvmdssjrb146"),
    (("processor146", "AA"), "processor146"),
    (("reasoning146", "key"), "biycslsre146"),
    (("reasoning146", "lemon"), "cimgbymzu146"),
    (("reasoning146", "a"), "reasoning146"),
    (("reasoning146", "zz"), "qdzrnmhmf146"),
    (("reasoning146", "AgentU"), "rkefhhitk146"),
    (("reasoning146", "keyboard"), "biytcnzqq146"),
    (("reasoning146", "AA"), "reasoning146"),
    (("machine146", "key"), "wearmlo146"),
    (("machine146", "lemon"), "xeovvyi146"),
    (("machine146", "a"), "machine146"),
    (("machine146", "zz"), "lzbghmd146"),
    (("machine146", "AgentU"), "mggubhe146"),
    (("machine146", "keyboard"), "weaiwnv146"),
    (("machine146", "AA"), "machine146"),
    (("learning146", "key"), "viybrgxk146"),
    (("learning146", "lemon"), "wimfatrs146"),
    (("learning146", "a"), "learning146"),
    (("learning146", "zz"), "kdzqmhmf146"),
    (("learning146", "AgentU"), "lkeegcnm146"),
    (("learning146", "keyboard"), "viysbiej146"),
    (("learning146", "AA"), "learning146"),
    (("model146", "key"), "wsbop146"),
    (("model146", "lemon"), "xspsy146"),
    (("model146", "a"), "model146"),
    (("model146", "zz"), "lncdk146"),
    (("model146", "AgentU"), "muhre146"),
    (("model146", "keyboard"), "wsbfz146"),
    (("model146", "AA"), "model146"),
    (("token146", "key"), "dsior146"),
    (("token146", "lemon"), "eswsa146"),
    (("token146", "a"), "token146"),
    (("token146", "zz"), "snjdm146"),
    (("token146", "AgentU"), "tuorg146"),
    (("token146", "keyboard"), "dsifb146"),
    (("token146", "AA"), "token146"),
    (("prompt146", "key"), "zvmwtr146"),
    (("prompt146", "lemon"), "avaace146"),
    (("prompt146", "a"), "prompt146"),
    (("prompt146", "zz"), "oqnlos146"),
    (("prompt146", "AgentU"), "pxszin146"),
    (("prompt146", "keyboard"), "zvmndt146"),
    (("prompt146", "AA"), "prompt146"),
    (("session146", "key"), "ciqcmmx146"),
    (("session146", "lemon"), "diegvzr146"),
    (("session146", "a"), "session146"),
    (("session146", "zz"), "rdrrhnm146"),
    (("session146", "AgentU"), "skwfbin146"),
    (("session146", "keyboard"), "ciqtwoe146"),
    (("session146", "AA"), "session146"),
    (("library146", "key"), "vmzbepi146"),
    (("library146", "lemon"), "wmnfncc146"),
    (("library146", "a"), "library146"),
    (("library146", "zz"), "khaqzqx146"),
    (("library146", "AgentU"), "lofetly146"),
    (("library146", "keyboard"), "vmzsorp146"),
    (("library146", "AA"), "library146"),
    (("service146", "key"), "cipfmao146"),
    (("service146", "lemon"), "didjvni146"),
    (("service146", "a"), "service146"),
    (("service146", "zz"), "rdquhbd146"),
    (("service146", "AgentU"), "skvibwe146"),
    (("service146", "keyboard"), "cipwwcv146"),
    (("service146", "AA"), "service146"),
    (("gateway146", "key"), "qeroayi146"),
    (("gateway146", "lemon"), "refsjlc146"),
    (("gateway146", "a"), "gateway146"),
    (("gateway146", "zz"), "fzsdvzx146"),
    (("gateway146", "AgentU"), "ggxrpuy146"),
    (("gateway146", "keyboard"), "qerfkap146"),
    (("gateway146", "AA"), "gateway146"),
    (("storage146", "key"), "cxmbeeo146"),
    (("storage146", "lemon"), "dxafnri146"),
    (("storage146", "a"), "storage146"),
    (("storage146", "zz"), "rsnqzfd146"),
    (("storage146", "AgentU"), "szsetae146"),
    (("storage146", "keyboard"), "cxmsogv146"),
    (("storage146", "AA"), "storage146"),
    (("network146", "key"), "xirgspu146"),
    (("network146", "lemon"), "yifkbco146"),
    (("network146", "a"), "network146"),
    (("network146", "zz"), "mdsvnqj146"),
    (("network146", "AgentU"), "nkxjhlk146"),
    (("network146", "keyboard"), "xirxcrb146"),
    (("network146", "AA"), "network146"),
    (("latency146", "key"), "verorai146"),
    (("latency146", "lemon"), "wefsanc146"),
    (("latency146", "a"), "latency146"),
    (("latency146", "zz"), "kzsdmbx146"),
    (("latency146", "AgentU"), "lgxrgwy146"),
    (("latency146", "keyboard"), "verfbcp146"),
    (("latency146", "AA"), "latency146"),
    (("buffer146", "key"), "lydpip146"),
    (("buffer146", "lemon"), "myrtrc146"),
    (("buffer146", "a"), "buffer146"),
    (("buffer146", "zz"), "ateedq146"),
    (("buffer146", "AgentU"), "bajsxl146"),
    (("buffer146", "keyboard"), "lydgsr146"),
    (("buffer146", "AA"), "buffer146"),
    (("queue146", "key"), "aycei146"),
    (("queue146", "lemon"), "byqir146"),
    (("queue146", "a"), "queue146"),
    (("queue146", "zz"), "ptdtd146"),
    (("queue146", "AgentU"), "qaihx146"),
    (("queue146", "keyboard"), "aycvs146"),
    (("queue146", "AA"), "queue146"),
    (("worker146", "key"), "gspuip146"),
    (("worker146", "lemon"), "hsdyrc146"),
    (("worker146", "a"), "worker146"),
    (("worker146", "zz"), "vnqjdq146"),
    (("worker146", "AgentU"), "wuvxxl146"),
    (("worker146", "keyboard"), "gsplsr146"),
    (("worker146", "AA"), "worker146"),
    (("kernel146", "key"), "uipxij146"),
    (("kernel146", "lemon"), "vidbrw146"),
    (("kernel146", "a"), "kernel146"),
    (("kernel146", "zz"), "jdqmdk146"),
    (("kernel146", "AgentU"), "kkvaxf146"),
    (("kernel146", "keyboard"), "uiposl146"),
    (("kernel146", "AA"), "kernel146"),
    (("signal146", "key"), "cmexej146"),
    (("signal146", "lemon"), "dmsbnw146"),
    (("signal146", "a"), "signal146"),
    (("signal146", "zz"), "rhfmzk146"),
    (("signal146", "AgentU"), "sokatf146"),
    (("signal146", "keyboard"), "cmeool146"),
    (("signal146", "AA"), "signal146"),
    (("packet146", "key"), "zeauir146"),
    (("packet146", "lemon"), "aeoyre146"),
    (("packet146", "a"), "packet146"),
    (("packet146", "zz"), "ozbjds146"),
    (("packet146", "AgentU"), "pggxxn146"),
    (("packet146", "keyboard"), "zealst146"),
    (("packet146", "AA"), "packet146"),
    (("router146", "key"), "bssdip146"),
    (("router146", "lemon"), "csghrc146"),
    (("router146", "a"), "router146"),
    (("router146", "zz"), "qntsdq146"),
    (("router146", "AgentU"), "ruygxl146"),
    (("router146", "keyboard"), "bssusr146"),
    (("router146", "AA"), "router146"),
    (("cluster146", "key"), "mpscxcb146"),
    (("cluster146", "lemon"), "npgggpv146"),
    (("cluster146", "a"), "cluster146"),
    (("cluster146", "zz"), "bktrsdq146"),
    (("cluster146", "AgentU"), "cryfmyr146"),
    (("cluster146", "keyboard"), "mpsthei146"),
    (("cluster146", "AA"), "cluster146"),
    (("mirror146", "key"), "wmpbsp146"),
    (("mirror146", "lemon"), "xmdfbc146"),
    (("mirror146", "a"), "mirror146"),
    (("mirror146", "zz"), "lhqqnq146"),
    (("mirror146", "AgentU"), "movehl146"),
    (("mirror146", "keyboard"), "wmpscr146"),
    (("mirror146", "AA"), "mirror146"),
    (("filter146", "key"), "pmjdip146"),
    (("filter146", "lemon"), "qmxhrc146"),
    (("filter146", "a"), "filter146"),
    (("filter146", "zz"), "ehksdq146"),
    (("filter146", "AgentU"), "fopgxl146"),
    (("filter146", "keyboard"), "pmjusr146"),
    (("filter146", "AA"), "filter146"),
    (("ranking146", "key"), "belumlq146"),
    (("ranking146", "lemon"), "cezyvyk146"),
    (("ranking146", "a"), "ranking146"),
    (("ranking146", "zz"), "qzmjhmf146"),
    (("ranking146", "AgentU"), "rgrxbhg146"),
    (("ranking146", "keyboard"), "bellwnx146"),
    (("ranking146", "AA"), "ranking146"),
    (("encoding146", "key"), "orayhgxk146"),
    (("encoding146", "lemon"), "procqtrs146"),
    (("encoding146", "a"), "encoding146"),
    (("encoding146", "zz"), "dmbnchmf146"),
    (("encoding146", "AgentU"), "etgbwcnm146"),
    (("encoding146", "keyboard"), "orapriej146"),
    (("encoding146", "AA"), "encoding146"),
    (("mapping146", "key"), "wenzmlq146"),
    (("mapping146", "lemon"), "xebdvyk146"),
    (("mapping146", "a"), "mapping146"),
    (("mapping146", "zz"), "lzoohmf146"),
    (("mapping146", "AgentU"), "mgtcbhg146"),
    (("mapping146", "keyboard"), "wenqwnx146"),
    (("mapping146", "AA"), "mapping146"),
    (("record146", "key"), "biayvb146"),
    (("record146", "lemon"), "cioceo146"),
    (("record146", "a"), "record146"),
    (("record146", "zz"), "qdbnqc146"),
    (("record146", "AgentU"), "rkgbkx146"),
    (("record146", "keyboard"), "biapfd146"),
    (("record146", "AA"), "record146"),
    (("candle146", "key"), "melnpc146"),
    (("candle146", "lemon"), "nezryp146"),
    (("candle146", "a"), "candle146"),
    (("candle146", "zz"), "bzmckd146"),
    (("candle146", "AgentU"), "cgrqey146"),
    (("candle146", "keyboard"), "meleze146"),
    (("candle146", "AA"), "candle146"),
    (("thread146", "key"), "dlpoeb146"),
    (("thread146", "lemon"), "eldsno146"),
    (("thread146", "a"), "thread146"),
    (("thread146", "zz"), "sgqdzc146"),
    (("thread146", "AgentU"), "tnvrtx146"),
    (("thread146", "keyboard"), "dlpfod146"),
    (("thread146", "AA"), "thread146"),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 146: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 146: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "a"),
        "round 146: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 146: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 146: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 146: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", "AA"),
        "round 146: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "key"),
        "bssxh 146: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 146: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "a"),
        "round 146: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 146: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 146: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 146: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", "AA"),
        "round 146: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 146: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 146: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "a"),
        "round 146: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 146: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 146: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 146: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", "AA"),
        "round 146: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 146: the processor reads the record then stops", "key"),
        "bssxh 146: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 146: the processor reads the record then stops", "lemon"),
        "csgbq 146: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 146: the processor reads the record then stops", "a"),
        "round 146: the processor reads the record then stops",
    ),
    (
        ("round 146: the processor reads the record then stops", "zz"),
        "qntmc 146: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 146: the processor reads the record then stops", "AgentU"),
        "ruyaw 146: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 146: the processor reads the record then stops", "keyboard"),
        "bssor 146: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 146: the processor reads the record then stops", "AA"),
        "round 146: the processor reads the record then stops",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "key"),
        "bssxh 146: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "lemon"),
        "csgbq 146: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "a"),
        "round 146: a worker pulls the next task from the queue",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "zz"),
        "qntmc 146: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 146: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "keyboard"),
        "bssor 146: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 146: a worker pulls the next task from the queue", "AA"),
        "round 146: a worker pulls the next task from the queue",
    ),
    (
        ("round 146: signals travel through the network layer", "key"),
        "bssxh 146: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 146: signals travel through the network layer", "lemon"),
        "csgbq 146: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 146: signals travel through the network layer", "a"),
        "round 146: signals travel through the network layer",
    ),
    (
        ("round 146: signals travel through the network layer", "zz"),
        "qntmc 146: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 146: signals travel through the network layer", "AgentU"),
        "ruyaw 146: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 146: signals travel through the network layer", "keyboard"),
        "bssor 146: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 146: signals travel through the network layer", "AA"),
        "round 146: signals travel through the network layer",
    ),
    (
        ("round 146: the gateway routes each request by policy", "key"),
        "bssxh 146: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 146: the gateway routes each request by policy", "lemon"),
        "csgbq 146: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 146: the gateway routes each request by policy", "a"),
        "round 146: the gateway routes each request by policy",
    ),
    (
        ("round 146: the gateway routes each request by policy", "zz"),
        "qntmc 146: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 146: the gateway routes each request by policy", "AgentU"),
        "ruyaw 146: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 146: the gateway routes each request by policy", "keyboard"),
        "bssor 146: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 146: the gateway routes each request by policy", "AA"),
        "round 146: the gateway routes each request by policy",
    ),
    (("round 146: memory grows until the buffer is full", "key"), "bssxh 146: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 146: memory grows until the buffer is full", "lemon"), "csgbq 146: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 146: memory grows until the buffer is full", "a"), "round 146: memory grows until the buffer is full"),
    (("round 146: memory grows until the buffer is full", "zz"), "qntmc 146: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 146: memory grows until the buffer is full", "AgentU"),
        "ruyaw 146: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 146: memory grows until the buffer is full", "keyboard"),
        "bssor 146: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 146: memory grows until the buffer is full", "AA"), "round 146: memory grows until the buffer is full"),
    (("round 146: the cluster mirrors every packet twice", "key"), "bssxh 146: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 146: the cluster mirrors every packet twice", "lemon"),
        "csgbq 146: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 146: the cluster mirrors every packet twice", "a"), "round 146: the cluster mirrors every packet twice"),
    (("round 146: the cluster mirrors every packet twice", "zz"), "qntmc 146: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 146: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 146: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 146: the cluster mirrors every packet twice", "keyboard"),
        "bssor 146: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 146: the cluster mirrors every packet twice", "AA"), "round 146: the cluster mirrors every packet twice"),
    (
        ("round 146: ranking uses tokens learned from the corpus", "key"),
        "bssxh 146: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 146: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", "a"),
        "round 146: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 146: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 146: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 146: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", "AA"),
        "round 146: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 146: a long session ends when the candle dies", "key"),
        "bssxh 146: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 146: a long session ends when the candle dies", "lemon"),
        "csgbq 146: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 146: a long session ends when the candle dies", "a"),
        "round 146: a long session ends when the candle dies",
    ),
    (
        ("round 146: a long session ends when the candle dies", "zz"),
        "qntmc 146: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 146: a long session ends when the candle dies", "AgentU"),
        "ruyaw 146: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 146: a long session ends when the candle dies", "keyboard"),
        "bssor 146: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 146: a long session ends when the candle dies", "AA"),
        "round 146: a long session ends when the candle dies",
    ),
    (("round 146: encode the prompt then map the result", "key"), "bssxh 146: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 146: encode the prompt then map the result", "lemon"), "csgbq 146: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 146: encode the prompt then map the result", "a"), "round 146: encode the prompt then map the result"),
    (("round 146: encode the prompt then map the result", "zz"), "qntmc 146: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 146: encode the prompt then map the result", "AgentU"),
        "ruyaw 146: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 146: encode the prompt then map the result", "keyboard"),
        "bssor 146: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 146: encode the prompt then map the result", "AA"), "round 146: encode the prompt then map the result"),
    (("round 146: the kernel wakes the worker at dawn", "key"), "bssxh 146: rri iovlop ukocc xfo ambocb er neux"),
    (("round 146: the kernel wakes the worker at dawn", "lemon"), "csgbq 146: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 146: the kernel wakes the worker at dawn", "a"), "round 146: the kernel wakes the worker at dawn"),
    (("round 146: the kernel wakes the worker at dawn", "zz"), "qntmc 146: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 146: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 146: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 146: the kernel wakes the worker at dawn", "keyboard"), "bssor 146: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 146: the kernel wakes the worker at dawn", "AA"), "round 146: the kernel wakes the worker at dawn"),
    (("round 146: service latency drops after the patch", "key"), "bssxh 146: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 146: service latency drops after the patch", "lemon"), "csgbq 146: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 146: service latency drops after the patch", "a"), "round 146: service latency drops after the patch"),
    (("round 146: service latency drops after the patch", "zz"), "qntmc 146: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 146: service latency drops after the patch", "AgentU"),
        "ruyaw 146: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 146: service latency drops after the patch", "keyboard"),
        "bssor 146: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 146: service latency drops after the patch", "AA"), "round 146: service latency drops after the patch"),
    (
        ("round 146: the library caches every vector it sees", "key"),
        "bssxh 146: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 146: the library caches every vector it sees", "lemon"),
        "csgbq 146: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 146: the library caches every vector it sees", "a"), "round 146: the library caches every vector it sees"),
    (
        ("round 146: the library caches every vector it sees", "zz"),
        "qntmc 146: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 146: the library caches every vector it sees", "AgentU"),
        "ruyaw 146: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 146: the library caches every vector it sees", "keyboard"),
        "bssor 146: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 146: the library caches every vector it sees", "AA"),
        "round 146: the library caches every vector it sees",
    ),
    (("round 146: agents argue then the debate resolves", "key"), "bssxh 146: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 146: agents argue then the debate resolves", "lemon"), "csgbq 146: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 146: agents argue then the debate resolves", "a"), "round 146: agents argue then the debate resolves"),
    (("round 146: agents argue then the debate resolves", "zz"), "qntmc 146: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 146: agents argue then the debate resolves", "AgentU"),
        "ruyaw 146: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 146: agents argue then the debate resolves", "keyboard"),
        "bssor 146: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 146: agents argue then the debate resolves", "AA"), "round 146: agents argue then the debate resolves"),
    (("round 146: the filter keeps only strong matches", "key"), "bssxh 146: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 146: the filter keeps only strong matches", "lemon"), "csgbq 146: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 146: the filter keeps only strong matches", "a"), "round 146: the filter keeps only strong matches"),
    (("round 146: the filter keeps only strong matches", "zz"), "qntmc 146: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 146: the filter keeps only strong matches", "AgentU"), "ruyaw 146: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 146: the filter keeps only strong matches", "keyboard"),
        "bssor 146: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 146: the filter keeps only strong matches", "AA"), "round 146: the filter keeps only strong matches"),
    (("round 146: the model answers with a short reply", "key"), "bssxh 146: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 146: the model answers with a short reply", "lemon"), "csgbq 146: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 146: the model answers with a short reply", "a"), "round 146: the model answers with a short reply"),
    (("round 146: the model answers with a short reply", "zz"), "qntmc 146: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 146: the model answers with a short reply", "AgentU"), "ruyaw 146: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 146: the model answers with a short reply", "keyboard"),
        "bssor 146: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 146: the model answers with a short reply", "AA"), "round 146: the model answers with a short reply"),
    (
        ("round 146: the recorder stores the reasoning trace", "key"),
        "bssxh 146: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 146: the recorder stores the reasoning trace", "lemon"),
        "csgbq 146: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 146: the recorder stores the reasoning trace", "a"), "round 146: the recorder stores the reasoning trace"),
    (
        ("round 146: the recorder stores the reasoning trace", "zz"),
        "qntmc 146: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 146: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 146: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 146: the recorder stores the reasoning trace", "keyboard"),
        "bssor 146: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 146: the recorder stores the reasoning trace", "AA"),
        "round 146: the recorder stores the reasoning trace",
    ),
    (("round 146: the angel watches the processor run", "key"), "bssxh 146: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 146: the angel watches the processor run", "lemon"), "csgbq 146: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 146: the angel watches the processor run", "a"), "round 146: the angel watches the processor run"),
    (("round 146: the angel watches the processor run", "zz"), "qntmc 146: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 146: the angel watches the processor run", "AgentU"), "ruyaw 146: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 146: the angel watches the processor run", "keyboard"), "bssor 146: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 146: the angel watches the processor run", "AA"), "round 146: the angel watches the processor run"),
    (("round 146: angle of the vector decides the match", "key"), "bssxh 146: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 146: angle of the vector decides the match", "lemon"), "csgbq 146: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 146: angle of the vector decides the match", "a"), "round 146: angle of the vector decides the match"),
    (("round 146: angle of the vector decides the match", "zz"), "qntmc 146: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 146: angle of the vector decides the match", "AgentU"),
        "ruyaw 146: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 146: angle of the vector decides the match", "keyboard"),
        "bssor 146: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 146: angle of the vector decides the match", "AA"), "round 146: angle of the vector decides the match"),
    (
        ("round 146: the candle burns twice as long at night", "key"),
        "bssxh 146: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 146: the candle burns twice as long at night", "lemon"),
        "csgbq 146: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 146: the candle burns twice as long at night", "a"), "round 146: the candle burns twice as long at night"),
    (
        ("round 146: the candle burns twice as long at night", "zz"),
        "qntmc 146: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 146: the candle burns twice as long at night", "AgentU"),
        "ruyaw 146: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 146: the candle burns twice as long at night", "keyboard"),
        "bssor 146: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 146: the candle burns twice as long at night", "AA"),
        "round 146: the candle burns twice as long at night",
    ),
    (("round 146: a mirror of the universe in one line", "key"), "bssxh 146: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 146: a mirror of the universe in one line", "lemon"), "csgbq 146: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 146: a mirror of the universe in one line", "a"), "round 146: a mirror of the universe in one line"),
    (("round 146: a mirror of the universe in one line", "zz"), "qntmc 146: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 146: a mirror of the universe in one line", "AgentU"), "ruyaw 146: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 146: a mirror of the universe in one line", "keyboard"),
        "bssor 146: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 146: a mirror of the universe in one line", "AA"), "round 146: a mirror of the universe in one line"),
    (("round 146: the queue drains before the storm", "key"), "bssxh 146: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 146: the queue drains before the storm", "lemon"), "csgbq 146: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 146: the queue drains before the storm", "a"), "round 146: the queue drains before the storm"),
    (("round 146: the queue drains before the storm", "zz"), "qntmc 146: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 146: the queue drains before the storm", "AgentU"), "ruyaw 146: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 146: the queue drains before the storm", "keyboard"), "bssor 146: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 146: the queue drains before the storm", "AA"), "round 146: the queue drains before the storm"),
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
