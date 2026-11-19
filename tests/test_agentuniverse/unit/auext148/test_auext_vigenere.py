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
    (("kitten148", "key"), "umrdil148"),
    (("kitten148", "lemon"), "vmfhry148"),
    (("kitten148", "a"), "kitten148"),
    (("kitten148", "zz"), "jhssdm148"),
    (("kitten148", "AgentU"), "koxgxh148"),
    (("kitten148", "keyboard"), "umrusn148"),
    (("kitten148", "AA"), "kitten148"),
    (("sitting148", "key"), "cmrdmlq148"),
    (("sitting148", "lemon"), "dmfhvyk148"),
    (("sitting148", "a"), "sitting148"),
    (("sitting148", "zz"), "rhsshmf148"),
    (("sitting148", "AgentU"), "soxgbhg148"),
    (("sitting148", "keyboard"), "cmruwnx148"),
    (("sitting148", "AA"), "sitting148"),
    (("agent148", "key"), "kkcxx148"),
    (("agent148", "lemon"), "lkqbg148"),
    (("agent148", "a"), "agent148"),
    (("agent148", "zz"), "zfdms148"),
    (("agent148", "AgentU"), "amiam148"),
    (("agent148", "keyboard"), "kkcoh148"),
    (("agent148", "AA"), "agent148"),
    (("angle148", "key"), "krevi148"),
    (("angle148", "lemon"), "lrszr148"),
    (("angle148", "a"), "angle148"),
    (("angle148", "zz"), "zmfkd148"),
    (("angle148", "AgentU"), "atkyx148"),
    (("angle148", "keyboard"), "krems148"),
    (("angle148", "AA"), "angle148"),
    (("universe148", "key"), "ergfipci148"),
    (("universe148", "lemon"), "frujrcwq148"),
    (("universe148", "a"), "universe148"),
    (("universe148", "zz"), "tmhudqrd148"),
    (("universe148", "AgentU"), "utmixlsk148"),
    (("universe148", "keyboard"), "ergwsrjh148"),
    (("universe148", "AA"), "universe148"),
    (("memory148", "key"), "wikyvw148"),
    (("memory148", "lemon"), "xiycej148"),
    (("memory148", "a"), "memory148"),
    (("memory148", "zz"), "ldlnqx148"),
    (("memory148", "AgentU"), "mkqbks148"),
    (("memory148", "keyboard"), "wikpfy148"),
    (("memory148", "AA"), "memory148"),
    (("stream148", "key"), "cxpoek148"),
    (("stream148", "lemon"), "dxdsnx148"),
    (("stream148", "a"), "stream148"),
    (("stream148", "zz"), "rsqdzl148"),
    (("stream148", "AgentU"), "szvrtg148"),
    (("stream148", "keyboard"), "cxpfom148"),
    (("stream148", "AA"), "stream148"),
    (("context148", "key"), "msldivd148"),
    (("context148", "lemon"), "nszhrix148"),
    (("context148", "a"), "context148"),
    (("context148", "zz"), "bnmsdws148"),
    (("context148", "AgentU"), "curgxrt148"),
    (("context148", "keyboard"), "mslusxk148"),
    (("context148", "AA"), "context148"),
    (("knowledge148", "key"), "urmgpcnkc148"),
    (("knowledge148", "lemon"), "vrakyphss148"),
    (("knowledge148", "a"), "knowledge148"),
    (("knowledge148", "zz"), "jmnvkdcfd148"),
    (("knowledge148", "AgentU"), "ktsjeydmi148"),
    (("knowledge148", "keyboard"), "urmxzeujo148"),
    (("knowledge148", "AA"), "knowledge148"),
    (("vector148", "key"), "fiadsp148"),
    (("vector148", "lemon"), "giohbc148"),
    (("vector148", "a"), "vector148"),
    (("vector148", "zz"), "udbsnq148"),
    (("vector148", "AgentU"), "vkgghl148"),
    (("vector148", "keyboard"), "fiaucr148"),
    (("vector148", "AA"), "vector148"),
    (("processor148", "key"), "zvmmiqcsp148"),
    (("processor148", "lemon"), "avaqrdwaf148"),
    (("processor148", "a"), "processor148"),
    (("processor148", "zz"), "oqnbdrrnq148"),
    (("processor148", "AgentU"), "pxspxmsuv148"),
    (("processor148", "keyboard"), "zvmdssjrb148"),
    (("processor148", "AA"), "processor148"),
    (("reasoning148", "key"), "biycslsre148"),
    (("reasoning148", "lemon"), "cimgbymzu148"),
    (("reasoning148", "a"), "reasoning148"),
    (("reasoning148", "zz"), "qdzrnmhmf148"),
    (("reasoning148", "AgentU"), "rkefhhitk148"),
    (("reasoning148", "keyboard"), "biytcnzqq148"),
    (("reasoning148", "AA"), "reasoning148"),
    (("machine148", "key"), "wearmlo148"),
    (("machine148", "lemon"), "xeovvyi148"),
    (("machine148", "a"), "machine148"),
    (("machine148", "zz"), "lzbghmd148"),
    (("machine148", "AgentU"), "mggubhe148"),
    (("machine148", "keyboard"), "weaiwnv148"),
    (("machine148", "AA"), "machine148"),
    (("learning148", "key"), "viybrgxk148"),
    (("learning148", "lemon"), "wimfatrs148"),
    (("learning148", "a"), "learning148"),
    (("learning148", "zz"), "kdzqmhmf148"),
    (("learning148", "AgentU"), "lkeegcnm148"),
    (("learning148", "keyboard"), "viysbiej148"),
    (("learning148", "AA"), "learning148"),
    (("model148", "key"), "wsbop148"),
    (("model148", "lemon"), "xspsy148"),
    (("model148", "a"), "model148"),
    (("model148", "zz"), "lncdk148"),
    (("model148", "AgentU"), "muhre148"),
    (("model148", "keyboard"), "wsbfz148"),
    (("model148", "AA"), "model148"),
    (("token148", "key"), "dsior148"),
    (("token148", "lemon"), "eswsa148"),
    (("token148", "a"), "token148"),
    (("token148", "zz"), "snjdm148"),
    (("token148", "AgentU"), "tuorg148"),
    (("token148", "keyboard"), "dsifb148"),
    (("token148", "AA"), "token148"),
    (("prompt148", "key"), "zvmwtr148"),
    (("prompt148", "lemon"), "avaace148"),
    (("prompt148", "a"), "prompt148"),
    (("prompt148", "zz"), "oqnlos148"),
    (("prompt148", "AgentU"), "pxszin148"),
    (("prompt148", "keyboard"), "zvmndt148"),
    (("prompt148", "AA"), "prompt148"),
    (("session148", "key"), "ciqcmmx148"),
    (("session148", "lemon"), "diegvzr148"),
    (("session148", "a"), "session148"),
    (("session148", "zz"), "rdrrhnm148"),
    (("session148", "AgentU"), "skwfbin148"),
    (("session148", "keyboard"), "ciqtwoe148"),
    (("session148", "AA"), "session148"),
    (("library148", "key"), "vmzbepi148"),
    (("library148", "lemon"), "wmnfncc148"),
    (("library148", "a"), "library148"),
    (("library148", "zz"), "khaqzqx148"),
    (("library148", "AgentU"), "lofetly148"),
    (("library148", "keyboard"), "vmzsorp148"),
    (("library148", "AA"), "library148"),
    (("service148", "key"), "cipfmao148"),
    (("service148", "lemon"), "didjvni148"),
    (("service148", "a"), "service148"),
    (("service148", "zz"), "rdquhbd148"),
    (("service148", "AgentU"), "skvibwe148"),
    (("service148", "keyboard"), "cipwwcv148"),
    (("service148", "AA"), "service148"),
    (("gateway148", "key"), "qeroayi148"),
    (("gateway148", "lemon"), "refsjlc148"),
    (("gateway148", "a"), "gateway148"),
    (("gateway148", "zz"), "fzsdvzx148"),
    (("gateway148", "AgentU"), "ggxrpuy148"),
    (("gateway148", "keyboard"), "qerfkap148"),
    (("gateway148", "AA"), "gateway148"),
    (("storage148", "key"), "cxmbeeo148"),
    (("storage148", "lemon"), "dxafnri148"),
    (("storage148", "a"), "storage148"),
    (("storage148", "zz"), "rsnqzfd148"),
    (("storage148", "AgentU"), "szsetae148"),
    (("storage148", "keyboard"), "cxmsogv148"),
    (("storage148", "AA"), "storage148"),
    (("network148", "key"), "xirgspu148"),
    (("network148", "lemon"), "yifkbco148"),
    (("network148", "a"), "network148"),
    (("network148", "zz"), "mdsvnqj148"),
    (("network148", "AgentU"), "nkxjhlk148"),
    (("network148", "keyboard"), "xirxcrb148"),
    (("network148", "AA"), "network148"),
    (("latency148", "key"), "verorai148"),
    (("latency148", "lemon"), "wefsanc148"),
    (("latency148", "a"), "latency148"),
    (("latency148", "zz"), "kzsdmbx148"),
    (("latency148", "AgentU"), "lgxrgwy148"),
    (("latency148", "keyboard"), "verfbcp148"),
    (("latency148", "AA"), "latency148"),
    (("buffer148", "key"), "lydpip148"),
    (("buffer148", "lemon"), "myrtrc148"),
    (("buffer148", "a"), "buffer148"),
    (("buffer148", "zz"), "ateedq148"),
    (("buffer148", "AgentU"), "bajsxl148"),
    (("buffer148", "keyboard"), "lydgsr148"),
    (("buffer148", "AA"), "buffer148"),
    (("queue148", "key"), "aycei148"),
    (("queue148", "lemon"), "byqir148"),
    (("queue148", "a"), "queue148"),
    (("queue148", "zz"), "ptdtd148"),
    (("queue148", "AgentU"), "qaihx148"),
    (("queue148", "keyboard"), "aycvs148"),
    (("queue148", "AA"), "queue148"),
    (("worker148", "key"), "gspuip148"),
    (("worker148", "lemon"), "hsdyrc148"),
    (("worker148", "a"), "worker148"),
    (("worker148", "zz"), "vnqjdq148"),
    (("worker148", "AgentU"), "wuvxxl148"),
    (("worker148", "keyboard"), "gsplsr148"),
    (("worker148", "AA"), "worker148"),
    (("kernel148", "key"), "uipxij148"),
    (("kernel148", "lemon"), "vidbrw148"),
    (("kernel148", "a"), "kernel148"),
    (("kernel148", "zz"), "jdqmdk148"),
    (("kernel148", "AgentU"), "kkvaxf148"),
    (("kernel148", "keyboard"), "uiposl148"),
    (("kernel148", "AA"), "kernel148"),
    (("signal148", "key"), "cmexej148"),
    (("signal148", "lemon"), "dmsbnw148"),
    (("signal148", "a"), "signal148"),
    (("signal148", "zz"), "rhfmzk148"),
    (("signal148", "AgentU"), "sokatf148"),
    (("signal148", "keyboard"), "cmeool148"),
    (("signal148", "AA"), "signal148"),
    (("packet148", "key"), "zeauir148"),
    (("packet148", "lemon"), "aeoyre148"),
    (("packet148", "a"), "packet148"),
    (("packet148", "zz"), "ozbjds148"),
    (("packet148", "AgentU"), "pggxxn148"),
    (("packet148", "keyboard"), "zealst148"),
    (("packet148", "AA"), "packet148"),
    (("router148", "key"), "bssdip148"),
    (("router148", "lemon"), "csghrc148"),
    (("router148", "a"), "router148"),
    (("router148", "zz"), "qntsdq148"),
    (("router148", "AgentU"), "ruygxl148"),
    (("router148", "keyboard"), "bssusr148"),
    (("router148", "AA"), "router148"),
    (("cluster148", "key"), "mpscxcb148"),
    (("cluster148", "lemon"), "npgggpv148"),
    (("cluster148", "a"), "cluster148"),
    (("cluster148", "zz"), "bktrsdq148"),
    (("cluster148", "AgentU"), "cryfmyr148"),
    (("cluster148", "keyboard"), "mpsthei148"),
    (("cluster148", "AA"), "cluster148"),
    (("mirror148", "key"), "wmpbsp148"),
    (("mirror148", "lemon"), "xmdfbc148"),
    (("mirror148", "a"), "mirror148"),
    (("mirror148", "zz"), "lhqqnq148"),
    (("mirror148", "AgentU"), "movehl148"),
    (("mirror148", "keyboard"), "wmpscr148"),
    (("mirror148", "AA"), "mirror148"),
    (("filter148", "key"), "pmjdip148"),
    (("filter148", "lemon"), "qmxhrc148"),
    (("filter148", "a"), "filter148"),
    (("filter148", "zz"), "ehksdq148"),
    (("filter148", "AgentU"), "fopgxl148"),
    (("filter148", "keyboard"), "pmjusr148"),
    (("filter148", "AA"), "filter148"),
    (("ranking148", "key"), "belumlq148"),
    (("ranking148", "lemon"), "cezyvyk148"),
    (("ranking148", "a"), "ranking148"),
    (("ranking148", "zz"), "qzmjhmf148"),
    (("ranking148", "AgentU"), "rgrxbhg148"),
    (("ranking148", "keyboard"), "bellwnx148"),
    (("ranking148", "AA"), "ranking148"),
    (("encoding148", "key"), "orayhgxk148"),
    (("encoding148", "lemon"), "procqtrs148"),
    (("encoding148", "a"), "encoding148"),
    (("encoding148", "zz"), "dmbnchmf148"),
    (("encoding148", "AgentU"), "etgbwcnm148"),
    (("encoding148", "keyboard"), "orapriej148"),
    (("encoding148", "AA"), "encoding148"),
    (("mapping148", "key"), "wenzmlq148"),
    (("mapping148", "lemon"), "xebdvyk148"),
    (("mapping148", "a"), "mapping148"),
    (("mapping148", "zz"), "lzoohmf148"),
    (("mapping148", "AgentU"), "mgtcbhg148"),
    (("mapping148", "keyboard"), "wenqwnx148"),
    (("mapping148", "AA"), "mapping148"),
    (("record148", "key"), "biayvb148"),
    (("record148", "lemon"), "cioceo148"),
    (("record148", "a"), "record148"),
    (("record148", "zz"), "qdbnqc148"),
    (("record148", "AgentU"), "rkgbkx148"),
    (("record148", "keyboard"), "biapfd148"),
    (("record148", "AA"), "record148"),
    (("candle148", "key"), "melnpc148"),
    (("candle148", "lemon"), "nezryp148"),
    (("candle148", "a"), "candle148"),
    (("candle148", "zz"), "bzmckd148"),
    (("candle148", "AgentU"), "cgrqey148"),
    (("candle148", "keyboard"), "meleze148"),
    (("candle148", "AA"), "candle148"),
    (("thread148", "key"), "dlpoeb148"),
    (("thread148", "lemon"), "eldsno148"),
    (("thread148", "a"), "thread148"),
    (("thread148", "zz"), "sgqdzc148"),
    (("thread148", "AgentU"), "tnvrtx148"),
    (("thread148", "keyboard"), "dlpfod148"),
    (("thread148", "AA"), "thread148"),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 148: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 148: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "a"),
        "round 148: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 148: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 148: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 148: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", "AA"),
        "round 148: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "key"),
        "bssxh 148: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 148: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "a"),
        "round 148: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 148: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 148: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 148: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", "AA"),
        "round 148: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 148: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 148: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "a"),
        "round 148: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 148: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 148: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 148: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", "AA"),
        "round 148: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 148: the processor reads the record then stops", "key"),
        "bssxh 148: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 148: the processor reads the record then stops", "lemon"),
        "csgbq 148: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 148: the processor reads the record then stops", "a"),
        "round 148: the processor reads the record then stops",
    ),
    (
        ("round 148: the processor reads the record then stops", "zz"),
        "qntmc 148: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 148: the processor reads the record then stops", "AgentU"),
        "ruyaw 148: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 148: the processor reads the record then stops", "keyboard"),
        "bssor 148: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 148: the processor reads the record then stops", "AA"),
        "round 148: the processor reads the record then stops",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "key"),
        "bssxh 148: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "lemon"),
        "csgbq 148: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "a"),
        "round 148: a worker pulls the next task from the queue",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "zz"),
        "qntmc 148: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 148: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "keyboard"),
        "bssor 148: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 148: a worker pulls the next task from the queue", "AA"),
        "round 148: a worker pulls the next task from the queue",
    ),
    (
        ("round 148: signals travel through the network layer", "key"),
        "bssxh 148: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 148: signals travel through the network layer", "lemon"),
        "csgbq 148: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 148: signals travel through the network layer", "a"),
        "round 148: signals travel through the network layer",
    ),
    (
        ("round 148: signals travel through the network layer", "zz"),
        "qntmc 148: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 148: signals travel through the network layer", "AgentU"),
        "ruyaw 148: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 148: signals travel through the network layer", "keyboard"),
        "bssor 148: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 148: signals travel through the network layer", "AA"),
        "round 148: signals travel through the network layer",
    ),
    (
        ("round 148: the gateway routes each request by policy", "key"),
        "bssxh 148: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 148: the gateway routes each request by policy", "lemon"),
        "csgbq 148: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 148: the gateway routes each request by policy", "a"),
        "round 148: the gateway routes each request by policy",
    ),
    (
        ("round 148: the gateway routes each request by policy", "zz"),
        "qntmc 148: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 148: the gateway routes each request by policy", "AgentU"),
        "ruyaw 148: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 148: the gateway routes each request by policy", "keyboard"),
        "bssor 148: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 148: the gateway routes each request by policy", "AA"),
        "round 148: the gateway routes each request by policy",
    ),
    (("round 148: memory grows until the buffer is full", "key"), "bssxh 148: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 148: memory grows until the buffer is full", "lemon"), "csgbq 148: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 148: memory grows until the buffer is full", "a"), "round 148: memory grows until the buffer is full"),
    (("round 148: memory grows until the buffer is full", "zz"), "qntmc 148: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 148: memory grows until the buffer is full", "AgentU"),
        "ruyaw 148: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 148: memory grows until the buffer is full", "keyboard"),
        "bssor 148: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 148: memory grows until the buffer is full", "AA"), "round 148: memory grows until the buffer is full"),
    (("round 148: the cluster mirrors every packet twice", "key"), "bssxh 148: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 148: the cluster mirrors every packet twice", "lemon"),
        "csgbq 148: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 148: the cluster mirrors every packet twice", "a"), "round 148: the cluster mirrors every packet twice"),
    (("round 148: the cluster mirrors every packet twice", "zz"), "qntmc 148: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 148: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 148: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 148: the cluster mirrors every packet twice", "keyboard"),
        "bssor 148: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 148: the cluster mirrors every packet twice", "AA"), "round 148: the cluster mirrors every packet twice"),
    (
        ("round 148: ranking uses tokens learned from the corpus", "key"),
        "bssxh 148: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 148: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", "a"),
        "round 148: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 148: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 148: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 148: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", "AA"),
        "round 148: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 148: a long session ends when the candle dies", "key"),
        "bssxh 148: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 148: a long session ends when the candle dies", "lemon"),
        "csgbq 148: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 148: a long session ends when the candle dies", "a"),
        "round 148: a long session ends when the candle dies",
    ),
    (
        ("round 148: a long session ends when the candle dies", "zz"),
        "qntmc 148: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 148: a long session ends when the candle dies", "AgentU"),
        "ruyaw 148: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 148: a long session ends when the candle dies", "keyboard"),
        "bssor 148: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 148: a long session ends when the candle dies", "AA"),
        "round 148: a long session ends when the candle dies",
    ),
    (("round 148: encode the prompt then map the result", "key"), "bssxh 148: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 148: encode the prompt then map the result", "lemon"), "csgbq 148: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 148: encode the prompt then map the result", "a"), "round 148: encode the prompt then map the result"),
    (("round 148: encode the prompt then map the result", "zz"), "qntmc 148: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 148: encode the prompt then map the result", "AgentU"),
        "ruyaw 148: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 148: encode the prompt then map the result", "keyboard"),
        "bssor 148: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 148: encode the prompt then map the result", "AA"), "round 148: encode the prompt then map the result"),
    (("round 148: the kernel wakes the worker at dawn", "key"), "bssxh 148: rri iovlop ukocc xfo ambocb er neux"),
    (("round 148: the kernel wakes the worker at dawn", "lemon"), "csgbq 148: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 148: the kernel wakes the worker at dawn", "a"), "round 148: the kernel wakes the worker at dawn"),
    (("round 148: the kernel wakes the worker at dawn", "zz"), "qntmc 148: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 148: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 148: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 148: the kernel wakes the worker at dawn", "keyboard"), "bssor 148: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 148: the kernel wakes the worker at dawn", "AA"), "round 148: the kernel wakes the worker at dawn"),
    (("round 148: service latency drops after the patch", "key"), "bssxh 148: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 148: service latency drops after the patch", "lemon"), "csgbq 148: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 148: service latency drops after the patch", "a"), "round 148: service latency drops after the patch"),
    (("round 148: service latency drops after the patch", "zz"), "qntmc 148: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 148: service latency drops after the patch", "AgentU"),
        "ruyaw 148: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 148: service latency drops after the patch", "keyboard"),
        "bssor 148: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 148: service latency drops after the patch", "AA"), "round 148: service latency drops after the patch"),
    (
        ("round 148: the library caches every vector it sees", "key"),
        "bssxh 148: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 148: the library caches every vector it sees", "lemon"),
        "csgbq 148: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 148: the library caches every vector it sees", "a"), "round 148: the library caches every vector it sees"),
    (
        ("round 148: the library caches every vector it sees", "zz"),
        "qntmc 148: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 148: the library caches every vector it sees", "AgentU"),
        "ruyaw 148: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 148: the library caches every vector it sees", "keyboard"),
        "bssor 148: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 148: the library caches every vector it sees", "AA"),
        "round 148: the library caches every vector it sees",
    ),
    (("round 148: agents argue then the debate resolves", "key"), "bssxh 148: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 148: agents argue then the debate resolves", "lemon"), "csgbq 148: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 148: agents argue then the debate resolves", "a"), "round 148: agents argue then the debate resolves"),
    (("round 148: agents argue then the debate resolves", "zz"), "qntmc 148: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 148: agents argue then the debate resolves", "AgentU"),
        "ruyaw 148: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 148: agents argue then the debate resolves", "keyboard"),
        "bssor 148: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 148: agents argue then the debate resolves", "AA"), "round 148: agents argue then the debate resolves"),
    (("round 148: the filter keeps only strong matches", "key"), "bssxh 148: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 148: the filter keeps only strong matches", "lemon"), "csgbq 148: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 148: the filter keeps only strong matches", "a"), "round 148: the filter keeps only strong matches"),
    (("round 148: the filter keeps only strong matches", "zz"), "qntmc 148: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 148: the filter keeps only strong matches", "AgentU"), "ruyaw 148: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 148: the filter keeps only strong matches", "keyboard"),
        "bssor 148: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 148: the filter keeps only strong matches", "AA"), "round 148: the filter keeps only strong matches"),
    (("round 148: the model answers with a short reply", "key"), "bssxh 148: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 148: the model answers with a short reply", "lemon"), "csgbq 148: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 148: the model answers with a short reply", "a"), "round 148: the model answers with a short reply"),
    (("round 148: the model answers with a short reply", "zz"), "qntmc 148: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 148: the model answers with a short reply", "AgentU"), "ruyaw 148: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 148: the model answers with a short reply", "keyboard"),
        "bssor 148: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 148: the model answers with a short reply", "AA"), "round 148: the model answers with a short reply"),
    (
        ("round 148: the recorder stores the reasoning trace", "key"),
        "bssxh 148: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 148: the recorder stores the reasoning trace", "lemon"),
        "csgbq 148: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 148: the recorder stores the reasoning trace", "a"), "round 148: the recorder stores the reasoning trace"),
    (
        ("round 148: the recorder stores the reasoning trace", "zz"),
        "qntmc 148: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 148: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 148: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 148: the recorder stores the reasoning trace", "keyboard"),
        "bssor 148: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 148: the recorder stores the reasoning trace", "AA"),
        "round 148: the recorder stores the reasoning trace",
    ),
    (("round 148: the angel watches the processor run", "key"), "bssxh 148: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 148: the angel watches the processor run", "lemon"), "csgbq 148: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 148: the angel watches the processor run", "a"), "round 148: the angel watches the processor run"),
    (("round 148: the angel watches the processor run", "zz"), "qntmc 148: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 148: the angel watches the processor run", "AgentU"), "ruyaw 148: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 148: the angel watches the processor run", "keyboard"), "bssor 148: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 148: the angel watches the processor run", "AA"), "round 148: the angel watches the processor run"),
    (("round 148: angle of the vector decides the match", "key"), "bssxh 148: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 148: angle of the vector decides the match", "lemon"), "csgbq 148: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 148: angle of the vector decides the match", "a"), "round 148: angle of the vector decides the match"),
    (("round 148: angle of the vector decides the match", "zz"), "qntmc 148: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 148: angle of the vector decides the match", "AgentU"),
        "ruyaw 148: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 148: angle of the vector decides the match", "keyboard"),
        "bssor 148: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 148: angle of the vector decides the match", "AA"), "round 148: angle of the vector decides the match"),
    (
        ("round 148: the candle burns twice as long at night", "key"),
        "bssxh 148: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 148: the candle burns twice as long at night", "lemon"),
        "csgbq 148: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 148: the candle burns twice as long at night", "a"), "round 148: the candle burns twice as long at night"),
    (
        ("round 148: the candle burns twice as long at night", "zz"),
        "qntmc 148: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 148: the candle burns twice as long at night", "AgentU"),
        "ruyaw 148: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 148: the candle burns twice as long at night", "keyboard"),
        "bssor 148: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 148: the candle burns twice as long at night", "AA"),
        "round 148: the candle burns twice as long at night",
    ),
    (("round 148: a mirror of the universe in one line", "key"), "bssxh 148: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 148: a mirror of the universe in one line", "lemon"), "csgbq 148: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 148: a mirror of the universe in one line", "a"), "round 148: a mirror of the universe in one line"),
    (("round 148: a mirror of the universe in one line", "zz"), "qntmc 148: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 148: a mirror of the universe in one line", "AgentU"), "ruyaw 148: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 148: a mirror of the universe in one line", "keyboard"),
        "bssor 148: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 148: a mirror of the universe in one line", "AA"), "round 148: a mirror of the universe in one line"),
    (("round 148: the queue drains before the storm", "key"), "bssxh 148: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 148: the queue drains before the storm", "lemon"), "csgbq 148: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 148: the queue drains before the storm", "a"), "round 148: the queue drains before the storm"),
    (("round 148: the queue drains before the storm", "zz"), "qntmc 148: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 148: the queue drains before the storm", "AgentU"), "ruyaw 148: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 148: the queue drains before the storm", "keyboard"), "bssor 148: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 148: the queue drains before the storm", "AA"), "round 148: the queue drains before the storm"),
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
