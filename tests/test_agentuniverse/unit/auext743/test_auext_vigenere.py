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
    (("kitten743", "key"), "umrdil743"),
    (("kitten743", "lemon"), "vmfhry743"),
    (("kitten743", "a"), "kitten743"),
    (("kitten743", "zz"), "jhssdm743"),
    (("kitten743", "AgentU"), "koxgxh743"),
    (("kitten743", "keyboard"), "umrusn743"),
    (("kitten743", "AA"), "kitten743"),
    (("sitting743", "key"), "cmrdmlq743"),
    (("sitting743", "lemon"), "dmfhvyk743"),
    (("sitting743", "a"), "sitting743"),
    (("sitting743", "zz"), "rhsshmf743"),
    (("sitting743", "AgentU"), "soxgbhg743"),
    (("sitting743", "keyboard"), "cmruwnx743"),
    (("sitting743", "AA"), "sitting743"),
    (("agent743", "key"), "kkcxx743"),
    (("agent743", "lemon"), "lkqbg743"),
    (("agent743", "a"), "agent743"),
    (("agent743", "zz"), "zfdms743"),
    (("agent743", "AgentU"), "amiam743"),
    (("agent743", "keyboard"), "kkcoh743"),
    (("agent743", "AA"), "agent743"),
    (("angle743", "key"), "krevi743"),
    (("angle743", "lemon"), "lrszr743"),
    (("angle743", "a"), "angle743"),
    (("angle743", "zz"), "zmfkd743"),
    (("angle743", "AgentU"), "atkyx743"),
    (("angle743", "keyboard"), "krems743"),
    (("angle743", "AA"), "angle743"),
    (("universe743", "key"), "ergfipci743"),
    (("universe743", "lemon"), "frujrcwq743"),
    (("universe743", "a"), "universe743"),
    (("universe743", "zz"), "tmhudqrd743"),
    (("universe743", "AgentU"), "utmixlsk743"),
    (("universe743", "keyboard"), "ergwsrjh743"),
    (("universe743", "AA"), "universe743"),
    (("memory743", "key"), "wikyvw743"),
    (("memory743", "lemon"), "xiycej743"),
    (("memory743", "a"), "memory743"),
    (("memory743", "zz"), "ldlnqx743"),
    (("memory743", "AgentU"), "mkqbks743"),
    (("memory743", "keyboard"), "wikpfy743"),
    (("memory743", "AA"), "memory743"),
    (("stream743", "key"), "cxpoek743"),
    (("stream743", "lemon"), "dxdsnx743"),
    (("stream743", "a"), "stream743"),
    (("stream743", "zz"), "rsqdzl743"),
    (("stream743", "AgentU"), "szvrtg743"),
    (("stream743", "keyboard"), "cxpfom743"),
    (("stream743", "AA"), "stream743"),
    (("context743", "key"), "msldivd743"),
    (("context743", "lemon"), "nszhrix743"),
    (("context743", "a"), "context743"),
    (("context743", "zz"), "bnmsdws743"),
    (("context743", "AgentU"), "curgxrt743"),
    (("context743", "keyboard"), "mslusxk743"),
    (("context743", "AA"), "context743"),
    (("knowledge743", "key"), "urmgpcnkc743"),
    (("knowledge743", "lemon"), "vrakyphss743"),
    (("knowledge743", "a"), "knowledge743"),
    (("knowledge743", "zz"), "jmnvkdcfd743"),
    (("knowledge743", "AgentU"), "ktsjeydmi743"),
    (("knowledge743", "keyboard"), "urmxzeujo743"),
    (("knowledge743", "AA"), "knowledge743"),
    (("vector743", "key"), "fiadsp743"),
    (("vector743", "lemon"), "giohbc743"),
    (("vector743", "a"), "vector743"),
    (("vector743", "zz"), "udbsnq743"),
    (("vector743", "AgentU"), "vkgghl743"),
    (("vector743", "keyboard"), "fiaucr743"),
    (("vector743", "AA"), "vector743"),
    (("processor743", "key"), "zvmmiqcsp743"),
    (("processor743", "lemon"), "avaqrdwaf743"),
    (("processor743", "a"), "processor743"),
    (("processor743", "zz"), "oqnbdrrnq743"),
    (("processor743", "AgentU"), "pxspxmsuv743"),
    (("processor743", "keyboard"), "zvmdssjrb743"),
    (("processor743", "AA"), "processor743"),
    (("reasoning743", "key"), "biycslsre743"),
    (("reasoning743", "lemon"), "cimgbymzu743"),
    (("reasoning743", "a"), "reasoning743"),
    (("reasoning743", "zz"), "qdzrnmhmf743"),
    (("reasoning743", "AgentU"), "rkefhhitk743"),
    (("reasoning743", "keyboard"), "biytcnzqq743"),
    (("reasoning743", "AA"), "reasoning743"),
    (("machine743", "key"), "wearmlo743"),
    (("machine743", "lemon"), "xeovvyi743"),
    (("machine743", "a"), "machine743"),
    (("machine743", "zz"), "lzbghmd743"),
    (("machine743", "AgentU"), "mggubhe743"),
    (("machine743", "keyboard"), "weaiwnv743"),
    (("machine743", "AA"), "machine743"),
    (("learning743", "key"), "viybrgxk743"),
    (("learning743", "lemon"), "wimfatrs743"),
    (("learning743", "a"), "learning743"),
    (("learning743", "zz"), "kdzqmhmf743"),
    (("learning743", "AgentU"), "lkeegcnm743"),
    (("learning743", "keyboard"), "viysbiej743"),
    (("learning743", "AA"), "learning743"),
    (("model743", "key"), "wsbop743"),
    (("model743", "lemon"), "xspsy743"),
    (("model743", "a"), "model743"),
    (("model743", "zz"), "lncdk743"),
    (("model743", "AgentU"), "muhre743"),
    (("model743", "keyboard"), "wsbfz743"),
    (("model743", "AA"), "model743"),
    (("token743", "key"), "dsior743"),
    (("token743", "lemon"), "eswsa743"),
    (("token743", "a"), "token743"),
    (("token743", "zz"), "snjdm743"),
    (("token743", "AgentU"), "tuorg743"),
    (("token743", "keyboard"), "dsifb743"),
    (("token743", "AA"), "token743"),
    (("prompt743", "key"), "zvmwtr743"),
    (("prompt743", "lemon"), "avaace743"),
    (("prompt743", "a"), "prompt743"),
    (("prompt743", "zz"), "oqnlos743"),
    (("prompt743", "AgentU"), "pxszin743"),
    (("prompt743", "keyboard"), "zvmndt743"),
    (("prompt743", "AA"), "prompt743"),
    (("session743", "key"), "ciqcmmx743"),
    (("session743", "lemon"), "diegvzr743"),
    (("session743", "a"), "session743"),
    (("session743", "zz"), "rdrrhnm743"),
    (("session743", "AgentU"), "skwfbin743"),
    (("session743", "keyboard"), "ciqtwoe743"),
    (("session743", "AA"), "session743"),
    (("library743", "key"), "vmzbepi743"),
    (("library743", "lemon"), "wmnfncc743"),
    (("library743", "a"), "library743"),
    (("library743", "zz"), "khaqzqx743"),
    (("library743", "AgentU"), "lofetly743"),
    (("library743", "keyboard"), "vmzsorp743"),
    (("library743", "AA"), "library743"),
    (("service743", "key"), "cipfmao743"),
    (("service743", "lemon"), "didjvni743"),
    (("service743", "a"), "service743"),
    (("service743", "zz"), "rdquhbd743"),
    (("service743", "AgentU"), "skvibwe743"),
    (("service743", "keyboard"), "cipwwcv743"),
    (("service743", "AA"), "service743"),
    (("gateway743", "key"), "qeroayi743"),
    (("gateway743", "lemon"), "refsjlc743"),
    (("gateway743", "a"), "gateway743"),
    (("gateway743", "zz"), "fzsdvzx743"),
    (("gateway743", "AgentU"), "ggxrpuy743"),
    (("gateway743", "keyboard"), "qerfkap743"),
    (("gateway743", "AA"), "gateway743"),
    (("storage743", "key"), "cxmbeeo743"),
    (("storage743", "lemon"), "dxafnri743"),
    (("storage743", "a"), "storage743"),
    (("storage743", "zz"), "rsnqzfd743"),
    (("storage743", "AgentU"), "szsetae743"),
    (("storage743", "keyboard"), "cxmsogv743"),
    (("storage743", "AA"), "storage743"),
    (("network743", "key"), "xirgspu743"),
    (("network743", "lemon"), "yifkbco743"),
    (("network743", "a"), "network743"),
    (("network743", "zz"), "mdsvnqj743"),
    (("network743", "AgentU"), "nkxjhlk743"),
    (("network743", "keyboard"), "xirxcrb743"),
    (("network743", "AA"), "network743"),
    (("latency743", "key"), "verorai743"),
    (("latency743", "lemon"), "wefsanc743"),
    (("latency743", "a"), "latency743"),
    (("latency743", "zz"), "kzsdmbx743"),
    (("latency743", "AgentU"), "lgxrgwy743"),
    (("latency743", "keyboard"), "verfbcp743"),
    (("latency743", "AA"), "latency743"),
    (("buffer743", "key"), "lydpip743"),
    (("buffer743", "lemon"), "myrtrc743"),
    (("buffer743", "a"), "buffer743"),
    (("buffer743", "zz"), "ateedq743"),
    (("buffer743", "AgentU"), "bajsxl743"),
    (("buffer743", "keyboard"), "lydgsr743"),
    (("buffer743", "AA"), "buffer743"),
    (("queue743", "key"), "aycei743"),
    (("queue743", "lemon"), "byqir743"),
    (("queue743", "a"), "queue743"),
    (("queue743", "zz"), "ptdtd743"),
    (("queue743", "AgentU"), "qaihx743"),
    (("queue743", "keyboard"), "aycvs743"),
    (("queue743", "AA"), "queue743"),
    (("worker743", "key"), "gspuip743"),
    (("worker743", "lemon"), "hsdyrc743"),
    (("worker743", "a"), "worker743"),
    (("worker743", "zz"), "vnqjdq743"),
    (("worker743", "AgentU"), "wuvxxl743"),
    (("worker743", "keyboard"), "gsplsr743"),
    (("worker743", "AA"), "worker743"),
    (("kernel743", "key"), "uipxij743"),
    (("kernel743", "lemon"), "vidbrw743"),
    (("kernel743", "a"), "kernel743"),
    (("kernel743", "zz"), "jdqmdk743"),
    (("kernel743", "AgentU"), "kkvaxf743"),
    (("kernel743", "keyboard"), "uiposl743"),
    (("kernel743", "AA"), "kernel743"),
    (("signal743", "key"), "cmexej743"),
    (("signal743", "lemon"), "dmsbnw743"),
    (("signal743", "a"), "signal743"),
    (("signal743", "zz"), "rhfmzk743"),
    (("signal743", "AgentU"), "sokatf743"),
    (("signal743", "keyboard"), "cmeool743"),
    (("signal743", "AA"), "signal743"),
    (("packet743", "key"), "zeauir743"),
    (("packet743", "lemon"), "aeoyre743"),
    (("packet743", "a"), "packet743"),
    (("packet743", "zz"), "ozbjds743"),
    (("packet743", "AgentU"), "pggxxn743"),
    (("packet743", "keyboard"), "zealst743"),
    (("packet743", "AA"), "packet743"),
    (("router743", "key"), "bssdip743"),
    (("router743", "lemon"), "csghrc743"),
    (("router743", "a"), "router743"),
    (("router743", "zz"), "qntsdq743"),
    (("router743", "AgentU"), "ruygxl743"),
    (("router743", "keyboard"), "bssusr743"),
    (("router743", "AA"), "router743"),
    (("cluster743", "key"), "mpscxcb743"),
    (("cluster743", "lemon"), "npgggpv743"),
    (("cluster743", "a"), "cluster743"),
    (("cluster743", "zz"), "bktrsdq743"),
    (("cluster743", "AgentU"), "cryfmyr743"),
    (("cluster743", "keyboard"), "mpsthei743"),
    (("cluster743", "AA"), "cluster743"),
    (("mirror743", "key"), "wmpbsp743"),
    (("mirror743", "lemon"), "xmdfbc743"),
    (("mirror743", "a"), "mirror743"),
    (("mirror743", "zz"), "lhqqnq743"),
    (("mirror743", "AgentU"), "movehl743"),
    (("mirror743", "keyboard"), "wmpscr743"),
    (("mirror743", "AA"), "mirror743"),
    (("filter743", "key"), "pmjdip743"),
    (("filter743", "lemon"), "qmxhrc743"),
    (("filter743", "a"), "filter743"),
    (("filter743", "zz"), "ehksdq743"),
    (("filter743", "AgentU"), "fopgxl743"),
    (("filter743", "keyboard"), "pmjusr743"),
    (("filter743", "AA"), "filter743"),
    (("ranking743", "key"), "belumlq743"),
    (("ranking743", "lemon"), "cezyvyk743"),
    (("ranking743", "a"), "ranking743"),
    (("ranking743", "zz"), "qzmjhmf743"),
    (("ranking743", "AgentU"), "rgrxbhg743"),
    (("ranking743", "keyboard"), "bellwnx743"),
    (("ranking743", "AA"), "ranking743"),
    (("encoding743", "key"), "orayhgxk743"),
    (("encoding743", "lemon"), "procqtrs743"),
    (("encoding743", "a"), "encoding743"),
    (("encoding743", "zz"), "dmbnchmf743"),
    (("encoding743", "AgentU"), "etgbwcnm743"),
    (("encoding743", "keyboard"), "orapriej743"),
    (("encoding743", "AA"), "encoding743"),
    (("mapping743", "key"), "wenzmlq743"),
    (("mapping743", "lemon"), "xebdvyk743"),
    (("mapping743", "a"), "mapping743"),
    (("mapping743", "zz"), "lzoohmf743"),
    (("mapping743", "AgentU"), "mgtcbhg743"),
    (("mapping743", "keyboard"), "wenqwnx743"),
    (("mapping743", "AA"), "mapping743"),
    (("record743", "key"), "biayvb743"),
    (("record743", "lemon"), "cioceo743"),
    (("record743", "a"), "record743"),
    (("record743", "zz"), "qdbnqc743"),
    (("record743", "AgentU"), "rkgbkx743"),
    (("record743", "keyboard"), "biapfd743"),
    (("record743", "AA"), "record743"),
    (("candle743", "key"), "melnpc743"),
    (("candle743", "lemon"), "nezryp743"),
    (("candle743", "a"), "candle743"),
    (("candle743", "zz"), "bzmckd743"),
    (("candle743", "AgentU"), "cgrqey743"),
    (("candle743", "keyboard"), "meleze743"),
    (("candle743", "AA"), "candle743"),
    (("thread743", "key"), "dlpoeb743"),
    (("thread743", "lemon"), "eldsno743"),
    (("thread743", "a"), "thread743"),
    (("thread743", "zz"), "sgqdzc743"),
    (("thread743", "AgentU"), "tnvrtx743"),
    (("thread743", "keyboard"), "dlpfod743"),
    (("thread743", "AA"), "thread743"),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 743: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 743: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "a"),
        "round 743: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 743: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 743: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 743: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", "AA"),
        "round 743: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "key"),
        "bssxh 743: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 743: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "a"),
        "round 743: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 743: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 743: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 743: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", "AA"),
        "round 743: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 743: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 743: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "a"),
        "round 743: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 743: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 743: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 743: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", "AA"),
        "round 743: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 743: the processor reads the record then stops", "key"),
        "bssxh 743: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 743: the processor reads the record then stops", "lemon"),
        "csgbq 743: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 743: the processor reads the record then stops", "a"),
        "round 743: the processor reads the record then stops",
    ),
    (
        ("round 743: the processor reads the record then stops", "zz"),
        "qntmc 743: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 743: the processor reads the record then stops", "AgentU"),
        "ruyaw 743: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 743: the processor reads the record then stops", "keyboard"),
        "bssor 743: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 743: the processor reads the record then stops", "AA"),
        "round 743: the processor reads the record then stops",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "key"),
        "bssxh 743: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "lemon"),
        "csgbq 743: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "a"),
        "round 743: a worker pulls the next task from the queue",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "zz"),
        "qntmc 743: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 743: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "keyboard"),
        "bssor 743: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 743: a worker pulls the next task from the queue", "AA"),
        "round 743: a worker pulls the next task from the queue",
    ),
    (
        ("round 743: signals travel through the network layer", "key"),
        "bssxh 743: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 743: signals travel through the network layer", "lemon"),
        "csgbq 743: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 743: signals travel through the network layer", "a"),
        "round 743: signals travel through the network layer",
    ),
    (
        ("round 743: signals travel through the network layer", "zz"),
        "qntmc 743: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 743: signals travel through the network layer", "AgentU"),
        "ruyaw 743: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 743: signals travel through the network layer", "keyboard"),
        "bssor 743: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 743: signals travel through the network layer", "AA"),
        "round 743: signals travel through the network layer",
    ),
    (
        ("round 743: the gateway routes each request by policy", "key"),
        "bssxh 743: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 743: the gateway routes each request by policy", "lemon"),
        "csgbq 743: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 743: the gateway routes each request by policy", "a"),
        "round 743: the gateway routes each request by policy",
    ),
    (
        ("round 743: the gateway routes each request by policy", "zz"),
        "qntmc 743: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 743: the gateway routes each request by policy", "AgentU"),
        "ruyaw 743: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 743: the gateway routes each request by policy", "keyboard"),
        "bssor 743: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 743: the gateway routes each request by policy", "AA"),
        "round 743: the gateway routes each request by policy",
    ),
    (("round 743: memory grows until the buffer is full", "key"), "bssxh 743: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 743: memory grows until the buffer is full", "lemon"), "csgbq 743: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 743: memory grows until the buffer is full", "a"), "round 743: memory grows until the buffer is full"),
    (("round 743: memory grows until the buffer is full", "zz"), "qntmc 743: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 743: memory grows until the buffer is full", "AgentU"),
        "ruyaw 743: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 743: memory grows until the buffer is full", "keyboard"),
        "bssor 743: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 743: memory grows until the buffer is full", "AA"), "round 743: memory grows until the buffer is full"),
    (("round 743: the cluster mirrors every packet twice", "key"), "bssxh 743: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 743: the cluster mirrors every packet twice", "lemon"),
        "csgbq 743: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 743: the cluster mirrors every packet twice", "a"), "round 743: the cluster mirrors every packet twice"),
    (("round 743: the cluster mirrors every packet twice", "zz"), "qntmc 743: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 743: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 743: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 743: the cluster mirrors every packet twice", "keyboard"),
        "bssor 743: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 743: the cluster mirrors every packet twice", "AA"), "round 743: the cluster mirrors every packet twice"),
    (
        ("round 743: ranking uses tokens learned from the corpus", "key"),
        "bssxh 743: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 743: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", "a"),
        "round 743: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 743: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 743: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 743: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", "AA"),
        "round 743: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 743: a long session ends when the candle dies", "key"),
        "bssxh 743: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 743: a long session ends when the candle dies", "lemon"),
        "csgbq 743: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 743: a long session ends when the candle dies", "a"),
        "round 743: a long session ends when the candle dies",
    ),
    (
        ("round 743: a long session ends when the candle dies", "zz"),
        "qntmc 743: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 743: a long session ends when the candle dies", "AgentU"),
        "ruyaw 743: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 743: a long session ends when the candle dies", "keyboard"),
        "bssor 743: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 743: a long session ends when the candle dies", "AA"),
        "round 743: a long session ends when the candle dies",
    ),
    (("round 743: encode the prompt then map the result", "key"), "bssxh 743: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 743: encode the prompt then map the result", "lemon"), "csgbq 743: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 743: encode the prompt then map the result", "a"), "round 743: encode the prompt then map the result"),
    (("round 743: encode the prompt then map the result", "zz"), "qntmc 743: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 743: encode the prompt then map the result", "AgentU"),
        "ruyaw 743: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 743: encode the prompt then map the result", "keyboard"),
        "bssor 743: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 743: encode the prompt then map the result", "AA"), "round 743: encode the prompt then map the result"),
    (("round 743: the kernel wakes the worker at dawn", "key"), "bssxh 743: rri iovlop ukocc xfo ambocb er neux"),
    (("round 743: the kernel wakes the worker at dawn", "lemon"), "csgbq 743: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 743: the kernel wakes the worker at dawn", "a"), "round 743: the kernel wakes the worker at dawn"),
    (("round 743: the kernel wakes the worker at dawn", "zz"), "qntmc 743: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 743: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 743: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 743: the kernel wakes the worker at dawn", "keyboard"), "bssor 743: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 743: the kernel wakes the worker at dawn", "AA"), "round 743: the kernel wakes the worker at dawn"),
    (("round 743: service latency drops after the patch", "key"), "bssxh 743: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 743: service latency drops after the patch", "lemon"), "csgbq 743: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 743: service latency drops after the patch", "a"), "round 743: service latency drops after the patch"),
    (("round 743: service latency drops after the patch", "zz"), "qntmc 743: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 743: service latency drops after the patch", "AgentU"),
        "ruyaw 743: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 743: service latency drops after the patch", "keyboard"),
        "bssor 743: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 743: service latency drops after the patch", "AA"), "round 743: service latency drops after the patch"),
    (
        ("round 743: the library caches every vector it sees", "key"),
        "bssxh 743: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 743: the library caches every vector it sees", "lemon"),
        "csgbq 743: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 743: the library caches every vector it sees", "a"), "round 743: the library caches every vector it sees"),
    (
        ("round 743: the library caches every vector it sees", "zz"),
        "qntmc 743: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 743: the library caches every vector it sees", "AgentU"),
        "ruyaw 743: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 743: the library caches every vector it sees", "keyboard"),
        "bssor 743: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 743: the library caches every vector it sees", "AA"),
        "round 743: the library caches every vector it sees",
    ),
    (("round 743: agents argue then the debate resolves", "key"), "bssxh 743: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 743: agents argue then the debate resolves", "lemon"), "csgbq 743: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 743: agents argue then the debate resolves", "a"), "round 743: agents argue then the debate resolves"),
    (("round 743: agents argue then the debate resolves", "zz"), "qntmc 743: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 743: agents argue then the debate resolves", "AgentU"),
        "ruyaw 743: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 743: agents argue then the debate resolves", "keyboard"),
        "bssor 743: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 743: agents argue then the debate resolves", "AA"), "round 743: agents argue then the debate resolves"),
    (("round 743: the filter keeps only strong matches", "key"), "bssxh 743: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 743: the filter keeps only strong matches", "lemon"), "csgbq 743: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 743: the filter keeps only strong matches", "a"), "round 743: the filter keeps only strong matches"),
    (("round 743: the filter keeps only strong matches", "zz"), "qntmc 743: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 743: the filter keeps only strong matches", "AgentU"), "ruyaw 743: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 743: the filter keeps only strong matches", "keyboard"),
        "bssor 743: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 743: the filter keeps only strong matches", "AA"), "round 743: the filter keeps only strong matches"),
    (("round 743: the model answers with a short reply", "key"), "bssxh 743: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 743: the model answers with a short reply", "lemon"), "csgbq 743: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 743: the model answers with a short reply", "a"), "round 743: the model answers with a short reply"),
    (("round 743: the model answers with a short reply", "zz"), "qntmc 743: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 743: the model answers with a short reply", "AgentU"), "ruyaw 743: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 743: the model answers with a short reply", "keyboard"),
        "bssor 743: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 743: the model answers with a short reply", "AA"), "round 743: the model answers with a short reply"),
    (
        ("round 743: the recorder stores the reasoning trace", "key"),
        "bssxh 743: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 743: the recorder stores the reasoning trace", "lemon"),
        "csgbq 743: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 743: the recorder stores the reasoning trace", "a"), "round 743: the recorder stores the reasoning trace"),
    (
        ("round 743: the recorder stores the reasoning trace", "zz"),
        "qntmc 743: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 743: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 743: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 743: the recorder stores the reasoning trace", "keyboard"),
        "bssor 743: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 743: the recorder stores the reasoning trace", "AA"),
        "round 743: the recorder stores the reasoning trace",
    ),
    (("round 743: the angel watches the processor run", "key"), "bssxh 743: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 743: the angel watches the processor run", "lemon"), "csgbq 743: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 743: the angel watches the processor run", "a"), "round 743: the angel watches the processor run"),
    (("round 743: the angel watches the processor run", "zz"), "qntmc 743: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 743: the angel watches the processor run", "AgentU"), "ruyaw 743: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 743: the angel watches the processor run", "keyboard"), "bssor 743: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 743: the angel watches the processor run", "AA"), "round 743: the angel watches the processor run"),
    (("round 743: angle of the vector decides the match", "key"), "bssxh 743: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 743: angle of the vector decides the match", "lemon"), "csgbq 743: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 743: angle of the vector decides the match", "a"), "round 743: angle of the vector decides the match"),
    (("round 743: angle of the vector decides the match", "zz"), "qntmc 743: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 743: angle of the vector decides the match", "AgentU"),
        "ruyaw 743: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 743: angle of the vector decides the match", "keyboard"),
        "bssor 743: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 743: angle of the vector decides the match", "AA"), "round 743: angle of the vector decides the match"),
    (
        ("round 743: the candle burns twice as long at night", "key"),
        "bssxh 743: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 743: the candle burns twice as long at night", "lemon"),
        "csgbq 743: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 743: the candle burns twice as long at night", "a"), "round 743: the candle burns twice as long at night"),
    (
        ("round 743: the candle burns twice as long at night", "zz"),
        "qntmc 743: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 743: the candle burns twice as long at night", "AgentU"),
        "ruyaw 743: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 743: the candle burns twice as long at night", "keyboard"),
        "bssor 743: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 743: the candle burns twice as long at night", "AA"),
        "round 743: the candle burns twice as long at night",
    ),
    (("round 743: a mirror of the universe in one line", "key"), "bssxh 743: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 743: a mirror of the universe in one line", "lemon"), "csgbq 743: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 743: a mirror of the universe in one line", "a"), "round 743: a mirror of the universe in one line"),
    (("round 743: a mirror of the universe in one line", "zz"), "qntmc 743: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 743: a mirror of the universe in one line", "AgentU"), "ruyaw 743: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 743: a mirror of the universe in one line", "keyboard"),
        "bssor 743: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 743: a mirror of the universe in one line", "AA"), "round 743: a mirror of the universe in one line"),
    (("round 743: the queue drains before the storm", "key"), "bssxh 743: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 743: the queue drains before the storm", "lemon"), "csgbq 743: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 743: the queue drains before the storm", "a"), "round 743: the queue drains before the storm"),
    (("round 743: the queue drains before the storm", "zz"), "qntmc 743: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 743: the queue drains before the storm", "AgentU"), "ruyaw 743: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 743: the queue drains before the storm", "keyboard"), "bssor 743: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 743: the queue drains before the storm", "AA"), "round 743: the queue drains before the storm"),
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
