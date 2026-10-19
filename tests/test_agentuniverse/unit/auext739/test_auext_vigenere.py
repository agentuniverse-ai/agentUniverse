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
    (("kitten739", "key"), "umrdil739"),
    (("kitten739", "lemon"), "vmfhry739"),
    (("kitten739", "a"), "kitten739"),
    (("kitten739", "zz"), "jhssdm739"),
    (("kitten739", "AgentU"), "koxgxh739"),
    (("kitten739", "keyboard"), "umrusn739"),
    (("kitten739", "AA"), "kitten739"),
    (("sitting739", "key"), "cmrdmlq739"),
    (("sitting739", "lemon"), "dmfhvyk739"),
    (("sitting739", "a"), "sitting739"),
    (("sitting739", "zz"), "rhsshmf739"),
    (("sitting739", "AgentU"), "soxgbhg739"),
    (("sitting739", "keyboard"), "cmruwnx739"),
    (("sitting739", "AA"), "sitting739"),
    (("agent739", "key"), "kkcxx739"),
    (("agent739", "lemon"), "lkqbg739"),
    (("agent739", "a"), "agent739"),
    (("agent739", "zz"), "zfdms739"),
    (("agent739", "AgentU"), "amiam739"),
    (("agent739", "keyboard"), "kkcoh739"),
    (("agent739", "AA"), "agent739"),
    (("angle739", "key"), "krevi739"),
    (("angle739", "lemon"), "lrszr739"),
    (("angle739", "a"), "angle739"),
    (("angle739", "zz"), "zmfkd739"),
    (("angle739", "AgentU"), "atkyx739"),
    (("angle739", "keyboard"), "krems739"),
    (("angle739", "AA"), "angle739"),
    (("universe739", "key"), "ergfipci739"),
    (("universe739", "lemon"), "frujrcwq739"),
    (("universe739", "a"), "universe739"),
    (("universe739", "zz"), "tmhudqrd739"),
    (("universe739", "AgentU"), "utmixlsk739"),
    (("universe739", "keyboard"), "ergwsrjh739"),
    (("universe739", "AA"), "universe739"),
    (("memory739", "key"), "wikyvw739"),
    (("memory739", "lemon"), "xiycej739"),
    (("memory739", "a"), "memory739"),
    (("memory739", "zz"), "ldlnqx739"),
    (("memory739", "AgentU"), "mkqbks739"),
    (("memory739", "keyboard"), "wikpfy739"),
    (("memory739", "AA"), "memory739"),
    (("stream739", "key"), "cxpoek739"),
    (("stream739", "lemon"), "dxdsnx739"),
    (("stream739", "a"), "stream739"),
    (("stream739", "zz"), "rsqdzl739"),
    (("stream739", "AgentU"), "szvrtg739"),
    (("stream739", "keyboard"), "cxpfom739"),
    (("stream739", "AA"), "stream739"),
    (("context739", "key"), "msldivd739"),
    (("context739", "lemon"), "nszhrix739"),
    (("context739", "a"), "context739"),
    (("context739", "zz"), "bnmsdws739"),
    (("context739", "AgentU"), "curgxrt739"),
    (("context739", "keyboard"), "mslusxk739"),
    (("context739", "AA"), "context739"),
    (("knowledge739", "key"), "urmgpcnkc739"),
    (("knowledge739", "lemon"), "vrakyphss739"),
    (("knowledge739", "a"), "knowledge739"),
    (("knowledge739", "zz"), "jmnvkdcfd739"),
    (("knowledge739", "AgentU"), "ktsjeydmi739"),
    (("knowledge739", "keyboard"), "urmxzeujo739"),
    (("knowledge739", "AA"), "knowledge739"),
    (("vector739", "key"), "fiadsp739"),
    (("vector739", "lemon"), "giohbc739"),
    (("vector739", "a"), "vector739"),
    (("vector739", "zz"), "udbsnq739"),
    (("vector739", "AgentU"), "vkgghl739"),
    (("vector739", "keyboard"), "fiaucr739"),
    (("vector739", "AA"), "vector739"),
    (("processor739", "key"), "zvmmiqcsp739"),
    (("processor739", "lemon"), "avaqrdwaf739"),
    (("processor739", "a"), "processor739"),
    (("processor739", "zz"), "oqnbdrrnq739"),
    (("processor739", "AgentU"), "pxspxmsuv739"),
    (("processor739", "keyboard"), "zvmdssjrb739"),
    (("processor739", "AA"), "processor739"),
    (("reasoning739", "key"), "biycslsre739"),
    (("reasoning739", "lemon"), "cimgbymzu739"),
    (("reasoning739", "a"), "reasoning739"),
    (("reasoning739", "zz"), "qdzrnmhmf739"),
    (("reasoning739", "AgentU"), "rkefhhitk739"),
    (("reasoning739", "keyboard"), "biytcnzqq739"),
    (("reasoning739", "AA"), "reasoning739"),
    (("machine739", "key"), "wearmlo739"),
    (("machine739", "lemon"), "xeovvyi739"),
    (("machine739", "a"), "machine739"),
    (("machine739", "zz"), "lzbghmd739"),
    (("machine739", "AgentU"), "mggubhe739"),
    (("machine739", "keyboard"), "weaiwnv739"),
    (("machine739", "AA"), "machine739"),
    (("learning739", "key"), "viybrgxk739"),
    (("learning739", "lemon"), "wimfatrs739"),
    (("learning739", "a"), "learning739"),
    (("learning739", "zz"), "kdzqmhmf739"),
    (("learning739", "AgentU"), "lkeegcnm739"),
    (("learning739", "keyboard"), "viysbiej739"),
    (("learning739", "AA"), "learning739"),
    (("model739", "key"), "wsbop739"),
    (("model739", "lemon"), "xspsy739"),
    (("model739", "a"), "model739"),
    (("model739", "zz"), "lncdk739"),
    (("model739", "AgentU"), "muhre739"),
    (("model739", "keyboard"), "wsbfz739"),
    (("model739", "AA"), "model739"),
    (("token739", "key"), "dsior739"),
    (("token739", "lemon"), "eswsa739"),
    (("token739", "a"), "token739"),
    (("token739", "zz"), "snjdm739"),
    (("token739", "AgentU"), "tuorg739"),
    (("token739", "keyboard"), "dsifb739"),
    (("token739", "AA"), "token739"),
    (("prompt739", "key"), "zvmwtr739"),
    (("prompt739", "lemon"), "avaace739"),
    (("prompt739", "a"), "prompt739"),
    (("prompt739", "zz"), "oqnlos739"),
    (("prompt739", "AgentU"), "pxszin739"),
    (("prompt739", "keyboard"), "zvmndt739"),
    (("prompt739", "AA"), "prompt739"),
    (("session739", "key"), "ciqcmmx739"),
    (("session739", "lemon"), "diegvzr739"),
    (("session739", "a"), "session739"),
    (("session739", "zz"), "rdrrhnm739"),
    (("session739", "AgentU"), "skwfbin739"),
    (("session739", "keyboard"), "ciqtwoe739"),
    (("session739", "AA"), "session739"),
    (("library739", "key"), "vmzbepi739"),
    (("library739", "lemon"), "wmnfncc739"),
    (("library739", "a"), "library739"),
    (("library739", "zz"), "khaqzqx739"),
    (("library739", "AgentU"), "lofetly739"),
    (("library739", "keyboard"), "vmzsorp739"),
    (("library739", "AA"), "library739"),
    (("service739", "key"), "cipfmao739"),
    (("service739", "lemon"), "didjvni739"),
    (("service739", "a"), "service739"),
    (("service739", "zz"), "rdquhbd739"),
    (("service739", "AgentU"), "skvibwe739"),
    (("service739", "keyboard"), "cipwwcv739"),
    (("service739", "AA"), "service739"),
    (("gateway739", "key"), "qeroayi739"),
    (("gateway739", "lemon"), "refsjlc739"),
    (("gateway739", "a"), "gateway739"),
    (("gateway739", "zz"), "fzsdvzx739"),
    (("gateway739", "AgentU"), "ggxrpuy739"),
    (("gateway739", "keyboard"), "qerfkap739"),
    (("gateway739", "AA"), "gateway739"),
    (("storage739", "key"), "cxmbeeo739"),
    (("storage739", "lemon"), "dxafnri739"),
    (("storage739", "a"), "storage739"),
    (("storage739", "zz"), "rsnqzfd739"),
    (("storage739", "AgentU"), "szsetae739"),
    (("storage739", "keyboard"), "cxmsogv739"),
    (("storage739", "AA"), "storage739"),
    (("network739", "key"), "xirgspu739"),
    (("network739", "lemon"), "yifkbco739"),
    (("network739", "a"), "network739"),
    (("network739", "zz"), "mdsvnqj739"),
    (("network739", "AgentU"), "nkxjhlk739"),
    (("network739", "keyboard"), "xirxcrb739"),
    (("network739", "AA"), "network739"),
    (("latency739", "key"), "verorai739"),
    (("latency739", "lemon"), "wefsanc739"),
    (("latency739", "a"), "latency739"),
    (("latency739", "zz"), "kzsdmbx739"),
    (("latency739", "AgentU"), "lgxrgwy739"),
    (("latency739", "keyboard"), "verfbcp739"),
    (("latency739", "AA"), "latency739"),
    (("buffer739", "key"), "lydpip739"),
    (("buffer739", "lemon"), "myrtrc739"),
    (("buffer739", "a"), "buffer739"),
    (("buffer739", "zz"), "ateedq739"),
    (("buffer739", "AgentU"), "bajsxl739"),
    (("buffer739", "keyboard"), "lydgsr739"),
    (("buffer739", "AA"), "buffer739"),
    (("queue739", "key"), "aycei739"),
    (("queue739", "lemon"), "byqir739"),
    (("queue739", "a"), "queue739"),
    (("queue739", "zz"), "ptdtd739"),
    (("queue739", "AgentU"), "qaihx739"),
    (("queue739", "keyboard"), "aycvs739"),
    (("queue739", "AA"), "queue739"),
    (("worker739", "key"), "gspuip739"),
    (("worker739", "lemon"), "hsdyrc739"),
    (("worker739", "a"), "worker739"),
    (("worker739", "zz"), "vnqjdq739"),
    (("worker739", "AgentU"), "wuvxxl739"),
    (("worker739", "keyboard"), "gsplsr739"),
    (("worker739", "AA"), "worker739"),
    (("kernel739", "key"), "uipxij739"),
    (("kernel739", "lemon"), "vidbrw739"),
    (("kernel739", "a"), "kernel739"),
    (("kernel739", "zz"), "jdqmdk739"),
    (("kernel739", "AgentU"), "kkvaxf739"),
    (("kernel739", "keyboard"), "uiposl739"),
    (("kernel739", "AA"), "kernel739"),
    (("signal739", "key"), "cmexej739"),
    (("signal739", "lemon"), "dmsbnw739"),
    (("signal739", "a"), "signal739"),
    (("signal739", "zz"), "rhfmzk739"),
    (("signal739", "AgentU"), "sokatf739"),
    (("signal739", "keyboard"), "cmeool739"),
    (("signal739", "AA"), "signal739"),
    (("packet739", "key"), "zeauir739"),
    (("packet739", "lemon"), "aeoyre739"),
    (("packet739", "a"), "packet739"),
    (("packet739", "zz"), "ozbjds739"),
    (("packet739", "AgentU"), "pggxxn739"),
    (("packet739", "keyboard"), "zealst739"),
    (("packet739", "AA"), "packet739"),
    (("router739", "key"), "bssdip739"),
    (("router739", "lemon"), "csghrc739"),
    (("router739", "a"), "router739"),
    (("router739", "zz"), "qntsdq739"),
    (("router739", "AgentU"), "ruygxl739"),
    (("router739", "keyboard"), "bssusr739"),
    (("router739", "AA"), "router739"),
    (("cluster739", "key"), "mpscxcb739"),
    (("cluster739", "lemon"), "npgggpv739"),
    (("cluster739", "a"), "cluster739"),
    (("cluster739", "zz"), "bktrsdq739"),
    (("cluster739", "AgentU"), "cryfmyr739"),
    (("cluster739", "keyboard"), "mpsthei739"),
    (("cluster739", "AA"), "cluster739"),
    (("mirror739", "key"), "wmpbsp739"),
    (("mirror739", "lemon"), "xmdfbc739"),
    (("mirror739", "a"), "mirror739"),
    (("mirror739", "zz"), "lhqqnq739"),
    (("mirror739", "AgentU"), "movehl739"),
    (("mirror739", "keyboard"), "wmpscr739"),
    (("mirror739", "AA"), "mirror739"),
    (("filter739", "key"), "pmjdip739"),
    (("filter739", "lemon"), "qmxhrc739"),
    (("filter739", "a"), "filter739"),
    (("filter739", "zz"), "ehksdq739"),
    (("filter739", "AgentU"), "fopgxl739"),
    (("filter739", "keyboard"), "pmjusr739"),
    (("filter739", "AA"), "filter739"),
    (("ranking739", "key"), "belumlq739"),
    (("ranking739", "lemon"), "cezyvyk739"),
    (("ranking739", "a"), "ranking739"),
    (("ranking739", "zz"), "qzmjhmf739"),
    (("ranking739", "AgentU"), "rgrxbhg739"),
    (("ranking739", "keyboard"), "bellwnx739"),
    (("ranking739", "AA"), "ranking739"),
    (("encoding739", "key"), "orayhgxk739"),
    (("encoding739", "lemon"), "procqtrs739"),
    (("encoding739", "a"), "encoding739"),
    (("encoding739", "zz"), "dmbnchmf739"),
    (("encoding739", "AgentU"), "etgbwcnm739"),
    (("encoding739", "keyboard"), "orapriej739"),
    (("encoding739", "AA"), "encoding739"),
    (("mapping739", "key"), "wenzmlq739"),
    (("mapping739", "lemon"), "xebdvyk739"),
    (("mapping739", "a"), "mapping739"),
    (("mapping739", "zz"), "lzoohmf739"),
    (("mapping739", "AgentU"), "mgtcbhg739"),
    (("mapping739", "keyboard"), "wenqwnx739"),
    (("mapping739", "AA"), "mapping739"),
    (("record739", "key"), "biayvb739"),
    (("record739", "lemon"), "cioceo739"),
    (("record739", "a"), "record739"),
    (("record739", "zz"), "qdbnqc739"),
    (("record739", "AgentU"), "rkgbkx739"),
    (("record739", "keyboard"), "biapfd739"),
    (("record739", "AA"), "record739"),
    (("candle739", "key"), "melnpc739"),
    (("candle739", "lemon"), "nezryp739"),
    (("candle739", "a"), "candle739"),
    (("candle739", "zz"), "bzmckd739"),
    (("candle739", "AgentU"), "cgrqey739"),
    (("candle739", "keyboard"), "meleze739"),
    (("candle739", "AA"), "candle739"),
    (("thread739", "key"), "dlpoeb739"),
    (("thread739", "lemon"), "eldsno739"),
    (("thread739", "a"), "thread739"),
    (("thread739", "zz"), "sgqdzc739"),
    (("thread739", "AgentU"), "tnvrtx739"),
    (("thread739", "keyboard"), "dlpfod739"),
    (("thread739", "AA"), "thread739"),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 739: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 739: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "a"),
        "round 739: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 739: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 739: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 739: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", "AA"),
        "round 739: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "key"),
        "bssxh 739: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 739: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "a"),
        "round 739: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 739: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 739: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 739: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", "AA"),
        "round 739: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 739: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 739: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "a"),
        "round 739: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 739: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 739: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 739: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", "AA"),
        "round 739: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 739: the processor reads the record then stops", "key"),
        "bssxh 739: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 739: the processor reads the record then stops", "lemon"),
        "csgbq 739: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 739: the processor reads the record then stops", "a"),
        "round 739: the processor reads the record then stops",
    ),
    (
        ("round 739: the processor reads the record then stops", "zz"),
        "qntmc 739: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 739: the processor reads the record then stops", "AgentU"),
        "ruyaw 739: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 739: the processor reads the record then stops", "keyboard"),
        "bssor 739: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 739: the processor reads the record then stops", "AA"),
        "round 739: the processor reads the record then stops",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "key"),
        "bssxh 739: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "lemon"),
        "csgbq 739: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "a"),
        "round 739: a worker pulls the next task from the queue",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "zz"),
        "qntmc 739: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 739: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "keyboard"),
        "bssor 739: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 739: a worker pulls the next task from the queue", "AA"),
        "round 739: a worker pulls the next task from the queue",
    ),
    (
        ("round 739: signals travel through the network layer", "key"),
        "bssxh 739: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 739: signals travel through the network layer", "lemon"),
        "csgbq 739: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 739: signals travel through the network layer", "a"),
        "round 739: signals travel through the network layer",
    ),
    (
        ("round 739: signals travel through the network layer", "zz"),
        "qntmc 739: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 739: signals travel through the network layer", "AgentU"),
        "ruyaw 739: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 739: signals travel through the network layer", "keyboard"),
        "bssor 739: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 739: signals travel through the network layer", "AA"),
        "round 739: signals travel through the network layer",
    ),
    (
        ("round 739: the gateway routes each request by policy", "key"),
        "bssxh 739: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 739: the gateway routes each request by policy", "lemon"),
        "csgbq 739: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 739: the gateway routes each request by policy", "a"),
        "round 739: the gateway routes each request by policy",
    ),
    (
        ("round 739: the gateway routes each request by policy", "zz"),
        "qntmc 739: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 739: the gateway routes each request by policy", "AgentU"),
        "ruyaw 739: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 739: the gateway routes each request by policy", "keyboard"),
        "bssor 739: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 739: the gateway routes each request by policy", "AA"),
        "round 739: the gateway routes each request by policy",
    ),
    (("round 739: memory grows until the buffer is full", "key"), "bssxh 739: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 739: memory grows until the buffer is full", "lemon"), "csgbq 739: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 739: memory grows until the buffer is full", "a"), "round 739: memory grows until the buffer is full"),
    (("round 739: memory grows until the buffer is full", "zz"), "qntmc 739: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 739: memory grows until the buffer is full", "AgentU"),
        "ruyaw 739: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 739: memory grows until the buffer is full", "keyboard"),
        "bssor 739: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 739: memory grows until the buffer is full", "AA"), "round 739: memory grows until the buffer is full"),
    (("round 739: the cluster mirrors every packet twice", "key"), "bssxh 739: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 739: the cluster mirrors every packet twice", "lemon"),
        "csgbq 739: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 739: the cluster mirrors every packet twice", "a"), "round 739: the cluster mirrors every packet twice"),
    (("round 739: the cluster mirrors every packet twice", "zz"), "qntmc 739: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 739: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 739: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 739: the cluster mirrors every packet twice", "keyboard"),
        "bssor 739: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 739: the cluster mirrors every packet twice", "AA"), "round 739: the cluster mirrors every packet twice"),
    (
        ("round 739: ranking uses tokens learned from the corpus", "key"),
        "bssxh 739: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 739: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", "a"),
        "round 739: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 739: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 739: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 739: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", "AA"),
        "round 739: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 739: a long session ends when the candle dies", "key"),
        "bssxh 739: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 739: a long session ends when the candle dies", "lemon"),
        "csgbq 739: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 739: a long session ends when the candle dies", "a"),
        "round 739: a long session ends when the candle dies",
    ),
    (
        ("round 739: a long session ends when the candle dies", "zz"),
        "qntmc 739: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 739: a long session ends when the candle dies", "AgentU"),
        "ruyaw 739: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 739: a long session ends when the candle dies", "keyboard"),
        "bssor 739: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 739: a long session ends when the candle dies", "AA"),
        "round 739: a long session ends when the candle dies",
    ),
    (("round 739: encode the prompt then map the result", "key"), "bssxh 739: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 739: encode the prompt then map the result", "lemon"), "csgbq 739: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 739: encode the prompt then map the result", "a"), "round 739: encode the prompt then map the result"),
    (("round 739: encode the prompt then map the result", "zz"), "qntmc 739: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 739: encode the prompt then map the result", "AgentU"),
        "ruyaw 739: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 739: encode the prompt then map the result", "keyboard"),
        "bssor 739: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 739: encode the prompt then map the result", "AA"), "round 739: encode the prompt then map the result"),
    (("round 739: the kernel wakes the worker at dawn", "key"), "bssxh 739: rri iovlop ukocc xfo ambocb er neux"),
    (("round 739: the kernel wakes the worker at dawn", "lemon"), "csgbq 739: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 739: the kernel wakes the worker at dawn", "a"), "round 739: the kernel wakes the worker at dawn"),
    (("round 739: the kernel wakes the worker at dawn", "zz"), "qntmc 739: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 739: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 739: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 739: the kernel wakes the worker at dawn", "keyboard"), "bssor 739: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 739: the kernel wakes the worker at dawn", "AA"), "round 739: the kernel wakes the worker at dawn"),
    (("round 739: service latency drops after the patch", "key"), "bssxh 739: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 739: service latency drops after the patch", "lemon"), "csgbq 739: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 739: service latency drops after the patch", "a"), "round 739: service latency drops after the patch"),
    (("round 739: service latency drops after the patch", "zz"), "qntmc 739: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 739: service latency drops after the patch", "AgentU"),
        "ruyaw 739: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 739: service latency drops after the patch", "keyboard"),
        "bssor 739: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 739: service latency drops after the patch", "AA"), "round 739: service latency drops after the patch"),
    (
        ("round 739: the library caches every vector it sees", "key"),
        "bssxh 739: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 739: the library caches every vector it sees", "lemon"),
        "csgbq 739: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 739: the library caches every vector it sees", "a"), "round 739: the library caches every vector it sees"),
    (
        ("round 739: the library caches every vector it sees", "zz"),
        "qntmc 739: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 739: the library caches every vector it sees", "AgentU"),
        "ruyaw 739: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 739: the library caches every vector it sees", "keyboard"),
        "bssor 739: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 739: the library caches every vector it sees", "AA"),
        "round 739: the library caches every vector it sees",
    ),
    (("round 739: agents argue then the debate resolves", "key"), "bssxh 739: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 739: agents argue then the debate resolves", "lemon"), "csgbq 739: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 739: agents argue then the debate resolves", "a"), "round 739: agents argue then the debate resolves"),
    (("round 739: agents argue then the debate resolves", "zz"), "qntmc 739: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 739: agents argue then the debate resolves", "AgentU"),
        "ruyaw 739: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 739: agents argue then the debate resolves", "keyboard"),
        "bssor 739: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 739: agents argue then the debate resolves", "AA"), "round 739: agents argue then the debate resolves"),
    (("round 739: the filter keeps only strong matches", "key"), "bssxh 739: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 739: the filter keeps only strong matches", "lemon"), "csgbq 739: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 739: the filter keeps only strong matches", "a"), "round 739: the filter keeps only strong matches"),
    (("round 739: the filter keeps only strong matches", "zz"), "qntmc 739: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 739: the filter keeps only strong matches", "AgentU"), "ruyaw 739: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 739: the filter keeps only strong matches", "keyboard"),
        "bssor 739: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 739: the filter keeps only strong matches", "AA"), "round 739: the filter keeps only strong matches"),
    (("round 739: the model answers with a short reply", "key"), "bssxh 739: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 739: the model answers with a short reply", "lemon"), "csgbq 739: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 739: the model answers with a short reply", "a"), "round 739: the model answers with a short reply"),
    (("round 739: the model answers with a short reply", "zz"), "qntmc 739: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 739: the model answers with a short reply", "AgentU"), "ruyaw 739: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 739: the model answers with a short reply", "keyboard"),
        "bssor 739: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 739: the model answers with a short reply", "AA"), "round 739: the model answers with a short reply"),
    (
        ("round 739: the recorder stores the reasoning trace", "key"),
        "bssxh 739: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 739: the recorder stores the reasoning trace", "lemon"),
        "csgbq 739: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 739: the recorder stores the reasoning trace", "a"), "round 739: the recorder stores the reasoning trace"),
    (
        ("round 739: the recorder stores the reasoning trace", "zz"),
        "qntmc 739: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 739: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 739: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 739: the recorder stores the reasoning trace", "keyboard"),
        "bssor 739: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 739: the recorder stores the reasoning trace", "AA"),
        "round 739: the recorder stores the reasoning trace",
    ),
    (("round 739: the angel watches the processor run", "key"), "bssxh 739: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 739: the angel watches the processor run", "lemon"), "csgbq 739: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 739: the angel watches the processor run", "a"), "round 739: the angel watches the processor run"),
    (("round 739: the angel watches the processor run", "zz"), "qntmc 739: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 739: the angel watches the processor run", "AgentU"), "ruyaw 739: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 739: the angel watches the processor run", "keyboard"), "bssor 739: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 739: the angel watches the processor run", "AA"), "round 739: the angel watches the processor run"),
    (("round 739: angle of the vector decides the match", "key"), "bssxh 739: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 739: angle of the vector decides the match", "lemon"), "csgbq 739: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 739: angle of the vector decides the match", "a"), "round 739: angle of the vector decides the match"),
    (("round 739: angle of the vector decides the match", "zz"), "qntmc 739: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 739: angle of the vector decides the match", "AgentU"),
        "ruyaw 739: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 739: angle of the vector decides the match", "keyboard"),
        "bssor 739: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 739: angle of the vector decides the match", "AA"), "round 739: angle of the vector decides the match"),
    (
        ("round 739: the candle burns twice as long at night", "key"),
        "bssxh 739: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 739: the candle burns twice as long at night", "lemon"),
        "csgbq 739: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 739: the candle burns twice as long at night", "a"), "round 739: the candle burns twice as long at night"),
    (
        ("round 739: the candle burns twice as long at night", "zz"),
        "qntmc 739: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 739: the candle burns twice as long at night", "AgentU"),
        "ruyaw 739: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 739: the candle burns twice as long at night", "keyboard"),
        "bssor 739: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 739: the candle burns twice as long at night", "AA"),
        "round 739: the candle burns twice as long at night",
    ),
    (("round 739: a mirror of the universe in one line", "key"), "bssxh 739: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 739: a mirror of the universe in one line", "lemon"), "csgbq 739: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 739: a mirror of the universe in one line", "a"), "round 739: a mirror of the universe in one line"),
    (("round 739: a mirror of the universe in one line", "zz"), "qntmc 739: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 739: a mirror of the universe in one line", "AgentU"), "ruyaw 739: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 739: a mirror of the universe in one line", "keyboard"),
        "bssor 739: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 739: a mirror of the universe in one line", "AA"), "round 739: a mirror of the universe in one line"),
    (("round 739: the queue drains before the storm", "key"), "bssxh 739: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 739: the queue drains before the storm", "lemon"), "csgbq 739: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 739: the queue drains before the storm", "a"), "round 739: the queue drains before the storm"),
    (("round 739: the queue drains before the storm", "zz"), "qntmc 739: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 739: the queue drains before the storm", "AgentU"), "ruyaw 739: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 739: the queue drains before the storm", "keyboard"), "bssor 739: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 739: the queue drains before the storm", "AA"), "round 739: the queue drains before the storm"),
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
