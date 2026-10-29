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
    (("kitten112", "key"), "umrdil112"),
    (("kitten112", "lemon"), "vmfhry112"),
    (("kitten112", "a"), "kitten112"),
    (("kitten112", "zz"), "jhssdm112"),
    (("kitten112", "AgentU"), "koxgxh112"),
    (("kitten112", "keyboard"), "umrusn112"),
    (("kitten112", "AA"), "kitten112"),
    (("sitting112", "key"), "cmrdmlq112"),
    (("sitting112", "lemon"), "dmfhvyk112"),
    (("sitting112", "a"), "sitting112"),
    (("sitting112", "zz"), "rhsshmf112"),
    (("sitting112", "AgentU"), "soxgbhg112"),
    (("sitting112", "keyboard"), "cmruwnx112"),
    (("sitting112", "AA"), "sitting112"),
    (("agent112", "key"), "kkcxx112"),
    (("agent112", "lemon"), "lkqbg112"),
    (("agent112", "a"), "agent112"),
    (("agent112", "zz"), "zfdms112"),
    (("agent112", "AgentU"), "amiam112"),
    (("agent112", "keyboard"), "kkcoh112"),
    (("agent112", "AA"), "agent112"),
    (("angle112", "key"), "krevi112"),
    (("angle112", "lemon"), "lrszr112"),
    (("angle112", "a"), "angle112"),
    (("angle112", "zz"), "zmfkd112"),
    (("angle112", "AgentU"), "atkyx112"),
    (("angle112", "keyboard"), "krems112"),
    (("angle112", "AA"), "angle112"),
    (("universe112", "key"), "ergfipci112"),
    (("universe112", "lemon"), "frujrcwq112"),
    (("universe112", "a"), "universe112"),
    (("universe112", "zz"), "tmhudqrd112"),
    (("universe112", "AgentU"), "utmixlsk112"),
    (("universe112", "keyboard"), "ergwsrjh112"),
    (("universe112", "AA"), "universe112"),
    (("memory112", "key"), "wikyvw112"),
    (("memory112", "lemon"), "xiycej112"),
    (("memory112", "a"), "memory112"),
    (("memory112", "zz"), "ldlnqx112"),
    (("memory112", "AgentU"), "mkqbks112"),
    (("memory112", "keyboard"), "wikpfy112"),
    (("memory112", "AA"), "memory112"),
    (("stream112", "key"), "cxpoek112"),
    (("stream112", "lemon"), "dxdsnx112"),
    (("stream112", "a"), "stream112"),
    (("stream112", "zz"), "rsqdzl112"),
    (("stream112", "AgentU"), "szvrtg112"),
    (("stream112", "keyboard"), "cxpfom112"),
    (("stream112", "AA"), "stream112"),
    (("context112", "key"), "msldivd112"),
    (("context112", "lemon"), "nszhrix112"),
    (("context112", "a"), "context112"),
    (("context112", "zz"), "bnmsdws112"),
    (("context112", "AgentU"), "curgxrt112"),
    (("context112", "keyboard"), "mslusxk112"),
    (("context112", "AA"), "context112"),
    (("knowledge112", "key"), "urmgpcnkc112"),
    (("knowledge112", "lemon"), "vrakyphss112"),
    (("knowledge112", "a"), "knowledge112"),
    (("knowledge112", "zz"), "jmnvkdcfd112"),
    (("knowledge112", "AgentU"), "ktsjeydmi112"),
    (("knowledge112", "keyboard"), "urmxzeujo112"),
    (("knowledge112", "AA"), "knowledge112"),
    (("vector112", "key"), "fiadsp112"),
    (("vector112", "lemon"), "giohbc112"),
    (("vector112", "a"), "vector112"),
    (("vector112", "zz"), "udbsnq112"),
    (("vector112", "AgentU"), "vkgghl112"),
    (("vector112", "keyboard"), "fiaucr112"),
    (("vector112", "AA"), "vector112"),
    (("processor112", "key"), "zvmmiqcsp112"),
    (("processor112", "lemon"), "avaqrdwaf112"),
    (("processor112", "a"), "processor112"),
    (("processor112", "zz"), "oqnbdrrnq112"),
    (("processor112", "AgentU"), "pxspxmsuv112"),
    (("processor112", "keyboard"), "zvmdssjrb112"),
    (("processor112", "AA"), "processor112"),
    (("reasoning112", "key"), "biycslsre112"),
    (("reasoning112", "lemon"), "cimgbymzu112"),
    (("reasoning112", "a"), "reasoning112"),
    (("reasoning112", "zz"), "qdzrnmhmf112"),
    (("reasoning112", "AgentU"), "rkefhhitk112"),
    (("reasoning112", "keyboard"), "biytcnzqq112"),
    (("reasoning112", "AA"), "reasoning112"),
    (("machine112", "key"), "wearmlo112"),
    (("machine112", "lemon"), "xeovvyi112"),
    (("machine112", "a"), "machine112"),
    (("machine112", "zz"), "lzbghmd112"),
    (("machine112", "AgentU"), "mggubhe112"),
    (("machine112", "keyboard"), "weaiwnv112"),
    (("machine112", "AA"), "machine112"),
    (("learning112", "key"), "viybrgxk112"),
    (("learning112", "lemon"), "wimfatrs112"),
    (("learning112", "a"), "learning112"),
    (("learning112", "zz"), "kdzqmhmf112"),
    (("learning112", "AgentU"), "lkeegcnm112"),
    (("learning112", "keyboard"), "viysbiej112"),
    (("learning112", "AA"), "learning112"),
    (("model112", "key"), "wsbop112"),
    (("model112", "lemon"), "xspsy112"),
    (("model112", "a"), "model112"),
    (("model112", "zz"), "lncdk112"),
    (("model112", "AgentU"), "muhre112"),
    (("model112", "keyboard"), "wsbfz112"),
    (("model112", "AA"), "model112"),
    (("token112", "key"), "dsior112"),
    (("token112", "lemon"), "eswsa112"),
    (("token112", "a"), "token112"),
    (("token112", "zz"), "snjdm112"),
    (("token112", "AgentU"), "tuorg112"),
    (("token112", "keyboard"), "dsifb112"),
    (("token112", "AA"), "token112"),
    (("prompt112", "key"), "zvmwtr112"),
    (("prompt112", "lemon"), "avaace112"),
    (("prompt112", "a"), "prompt112"),
    (("prompt112", "zz"), "oqnlos112"),
    (("prompt112", "AgentU"), "pxszin112"),
    (("prompt112", "keyboard"), "zvmndt112"),
    (("prompt112", "AA"), "prompt112"),
    (("session112", "key"), "ciqcmmx112"),
    (("session112", "lemon"), "diegvzr112"),
    (("session112", "a"), "session112"),
    (("session112", "zz"), "rdrrhnm112"),
    (("session112", "AgentU"), "skwfbin112"),
    (("session112", "keyboard"), "ciqtwoe112"),
    (("session112", "AA"), "session112"),
    (("library112", "key"), "vmzbepi112"),
    (("library112", "lemon"), "wmnfncc112"),
    (("library112", "a"), "library112"),
    (("library112", "zz"), "khaqzqx112"),
    (("library112", "AgentU"), "lofetly112"),
    (("library112", "keyboard"), "vmzsorp112"),
    (("library112", "AA"), "library112"),
    (("service112", "key"), "cipfmao112"),
    (("service112", "lemon"), "didjvni112"),
    (("service112", "a"), "service112"),
    (("service112", "zz"), "rdquhbd112"),
    (("service112", "AgentU"), "skvibwe112"),
    (("service112", "keyboard"), "cipwwcv112"),
    (("service112", "AA"), "service112"),
    (("gateway112", "key"), "qeroayi112"),
    (("gateway112", "lemon"), "refsjlc112"),
    (("gateway112", "a"), "gateway112"),
    (("gateway112", "zz"), "fzsdvzx112"),
    (("gateway112", "AgentU"), "ggxrpuy112"),
    (("gateway112", "keyboard"), "qerfkap112"),
    (("gateway112", "AA"), "gateway112"),
    (("storage112", "key"), "cxmbeeo112"),
    (("storage112", "lemon"), "dxafnri112"),
    (("storage112", "a"), "storage112"),
    (("storage112", "zz"), "rsnqzfd112"),
    (("storage112", "AgentU"), "szsetae112"),
    (("storage112", "keyboard"), "cxmsogv112"),
    (("storage112", "AA"), "storage112"),
    (("network112", "key"), "xirgspu112"),
    (("network112", "lemon"), "yifkbco112"),
    (("network112", "a"), "network112"),
    (("network112", "zz"), "mdsvnqj112"),
    (("network112", "AgentU"), "nkxjhlk112"),
    (("network112", "keyboard"), "xirxcrb112"),
    (("network112", "AA"), "network112"),
    (("latency112", "key"), "verorai112"),
    (("latency112", "lemon"), "wefsanc112"),
    (("latency112", "a"), "latency112"),
    (("latency112", "zz"), "kzsdmbx112"),
    (("latency112", "AgentU"), "lgxrgwy112"),
    (("latency112", "keyboard"), "verfbcp112"),
    (("latency112", "AA"), "latency112"),
    (("buffer112", "key"), "lydpip112"),
    (("buffer112", "lemon"), "myrtrc112"),
    (("buffer112", "a"), "buffer112"),
    (("buffer112", "zz"), "ateedq112"),
    (("buffer112", "AgentU"), "bajsxl112"),
    (("buffer112", "keyboard"), "lydgsr112"),
    (("buffer112", "AA"), "buffer112"),
    (("queue112", "key"), "aycei112"),
    (("queue112", "lemon"), "byqir112"),
    (("queue112", "a"), "queue112"),
    (("queue112", "zz"), "ptdtd112"),
    (("queue112", "AgentU"), "qaihx112"),
    (("queue112", "keyboard"), "aycvs112"),
    (("queue112", "AA"), "queue112"),
    (("worker112", "key"), "gspuip112"),
    (("worker112", "lemon"), "hsdyrc112"),
    (("worker112", "a"), "worker112"),
    (("worker112", "zz"), "vnqjdq112"),
    (("worker112", "AgentU"), "wuvxxl112"),
    (("worker112", "keyboard"), "gsplsr112"),
    (("worker112", "AA"), "worker112"),
    (("kernel112", "key"), "uipxij112"),
    (("kernel112", "lemon"), "vidbrw112"),
    (("kernel112", "a"), "kernel112"),
    (("kernel112", "zz"), "jdqmdk112"),
    (("kernel112", "AgentU"), "kkvaxf112"),
    (("kernel112", "keyboard"), "uiposl112"),
    (("kernel112", "AA"), "kernel112"),
    (("signal112", "key"), "cmexej112"),
    (("signal112", "lemon"), "dmsbnw112"),
    (("signal112", "a"), "signal112"),
    (("signal112", "zz"), "rhfmzk112"),
    (("signal112", "AgentU"), "sokatf112"),
    (("signal112", "keyboard"), "cmeool112"),
    (("signal112", "AA"), "signal112"),
    (("packet112", "key"), "zeauir112"),
    (("packet112", "lemon"), "aeoyre112"),
    (("packet112", "a"), "packet112"),
    (("packet112", "zz"), "ozbjds112"),
    (("packet112", "AgentU"), "pggxxn112"),
    (("packet112", "keyboard"), "zealst112"),
    (("packet112", "AA"), "packet112"),
    (("router112", "key"), "bssdip112"),
    (("router112", "lemon"), "csghrc112"),
    (("router112", "a"), "router112"),
    (("router112", "zz"), "qntsdq112"),
    (("router112", "AgentU"), "ruygxl112"),
    (("router112", "keyboard"), "bssusr112"),
    (("router112", "AA"), "router112"),
    (("cluster112", "key"), "mpscxcb112"),
    (("cluster112", "lemon"), "npgggpv112"),
    (("cluster112", "a"), "cluster112"),
    (("cluster112", "zz"), "bktrsdq112"),
    (("cluster112", "AgentU"), "cryfmyr112"),
    (("cluster112", "keyboard"), "mpsthei112"),
    (("cluster112", "AA"), "cluster112"),
    (("mirror112", "key"), "wmpbsp112"),
    (("mirror112", "lemon"), "xmdfbc112"),
    (("mirror112", "a"), "mirror112"),
    (("mirror112", "zz"), "lhqqnq112"),
    (("mirror112", "AgentU"), "movehl112"),
    (("mirror112", "keyboard"), "wmpscr112"),
    (("mirror112", "AA"), "mirror112"),
    (("filter112", "key"), "pmjdip112"),
    (("filter112", "lemon"), "qmxhrc112"),
    (("filter112", "a"), "filter112"),
    (("filter112", "zz"), "ehksdq112"),
    (("filter112", "AgentU"), "fopgxl112"),
    (("filter112", "keyboard"), "pmjusr112"),
    (("filter112", "AA"), "filter112"),
    (("ranking112", "key"), "belumlq112"),
    (("ranking112", "lemon"), "cezyvyk112"),
    (("ranking112", "a"), "ranking112"),
    (("ranking112", "zz"), "qzmjhmf112"),
    (("ranking112", "AgentU"), "rgrxbhg112"),
    (("ranking112", "keyboard"), "bellwnx112"),
    (("ranking112", "AA"), "ranking112"),
    (("encoding112", "key"), "orayhgxk112"),
    (("encoding112", "lemon"), "procqtrs112"),
    (("encoding112", "a"), "encoding112"),
    (("encoding112", "zz"), "dmbnchmf112"),
    (("encoding112", "AgentU"), "etgbwcnm112"),
    (("encoding112", "keyboard"), "orapriej112"),
    (("encoding112", "AA"), "encoding112"),
    (("mapping112", "key"), "wenzmlq112"),
    (("mapping112", "lemon"), "xebdvyk112"),
    (("mapping112", "a"), "mapping112"),
    (("mapping112", "zz"), "lzoohmf112"),
    (("mapping112", "AgentU"), "mgtcbhg112"),
    (("mapping112", "keyboard"), "wenqwnx112"),
    (("mapping112", "AA"), "mapping112"),
    (("record112", "key"), "biayvb112"),
    (("record112", "lemon"), "cioceo112"),
    (("record112", "a"), "record112"),
    (("record112", "zz"), "qdbnqc112"),
    (("record112", "AgentU"), "rkgbkx112"),
    (("record112", "keyboard"), "biapfd112"),
    (("record112", "AA"), "record112"),
    (("candle112", "key"), "melnpc112"),
    (("candle112", "lemon"), "nezryp112"),
    (("candle112", "a"), "candle112"),
    (("candle112", "zz"), "bzmckd112"),
    (("candle112", "AgentU"), "cgrqey112"),
    (("candle112", "keyboard"), "meleze112"),
    (("candle112", "AA"), "candle112"),
    (("thread112", "key"), "dlpoeb112"),
    (("thread112", "lemon"), "eldsno112"),
    (("thread112", "a"), "thread112"),
    (("thread112", "zz"), "sgqdzc112"),
    (("thread112", "AgentU"), "tnvrtx112"),
    (("thread112", "keyboard"), "dlpfod112"),
    (("thread112", "AA"), "thread112"),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 112: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 112: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "a"),
        "round 112: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 112: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 112: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 112: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", "AA"),
        "round 112: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "key"),
        "bssxh 112: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 112: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "a"),
        "round 112: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 112: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 112: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 112: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", "AA"),
        "round 112: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 112: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 112: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "a"),
        "round 112: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 112: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 112: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 112: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", "AA"),
        "round 112: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 112: the processor reads the record then stops", "key"),
        "bssxh 112: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 112: the processor reads the record then stops", "lemon"),
        "csgbq 112: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 112: the processor reads the record then stops", "a"),
        "round 112: the processor reads the record then stops",
    ),
    (
        ("round 112: the processor reads the record then stops", "zz"),
        "qntmc 112: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 112: the processor reads the record then stops", "AgentU"),
        "ruyaw 112: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 112: the processor reads the record then stops", "keyboard"),
        "bssor 112: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 112: the processor reads the record then stops", "AA"),
        "round 112: the processor reads the record then stops",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "key"),
        "bssxh 112: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "lemon"),
        "csgbq 112: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "a"),
        "round 112: a worker pulls the next task from the queue",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "zz"),
        "qntmc 112: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 112: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "keyboard"),
        "bssor 112: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 112: a worker pulls the next task from the queue", "AA"),
        "round 112: a worker pulls the next task from the queue",
    ),
    (
        ("round 112: signals travel through the network layer", "key"),
        "bssxh 112: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 112: signals travel through the network layer", "lemon"),
        "csgbq 112: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 112: signals travel through the network layer", "a"),
        "round 112: signals travel through the network layer",
    ),
    (
        ("round 112: signals travel through the network layer", "zz"),
        "qntmc 112: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 112: signals travel through the network layer", "AgentU"),
        "ruyaw 112: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 112: signals travel through the network layer", "keyboard"),
        "bssor 112: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 112: signals travel through the network layer", "AA"),
        "round 112: signals travel through the network layer",
    ),
    (
        ("round 112: the gateway routes each request by policy", "key"),
        "bssxh 112: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 112: the gateway routes each request by policy", "lemon"),
        "csgbq 112: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 112: the gateway routes each request by policy", "a"),
        "round 112: the gateway routes each request by policy",
    ),
    (
        ("round 112: the gateway routes each request by policy", "zz"),
        "qntmc 112: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 112: the gateway routes each request by policy", "AgentU"),
        "ruyaw 112: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 112: the gateway routes each request by policy", "keyboard"),
        "bssor 112: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 112: the gateway routes each request by policy", "AA"),
        "round 112: the gateway routes each request by policy",
    ),
    (("round 112: memory grows until the buffer is full", "key"), "bssxh 112: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 112: memory grows until the buffer is full", "lemon"), "csgbq 112: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 112: memory grows until the buffer is full", "a"), "round 112: memory grows until the buffer is full"),
    (("round 112: memory grows until the buffer is full", "zz"), "qntmc 112: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 112: memory grows until the buffer is full", "AgentU"),
        "ruyaw 112: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 112: memory grows until the buffer is full", "keyboard"),
        "bssor 112: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 112: memory grows until the buffer is full", "AA"), "round 112: memory grows until the buffer is full"),
    (("round 112: the cluster mirrors every packet twice", "key"), "bssxh 112: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 112: the cluster mirrors every packet twice", "lemon"),
        "csgbq 112: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 112: the cluster mirrors every packet twice", "a"), "round 112: the cluster mirrors every packet twice"),
    (("round 112: the cluster mirrors every packet twice", "zz"), "qntmc 112: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 112: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 112: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 112: the cluster mirrors every packet twice", "keyboard"),
        "bssor 112: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 112: the cluster mirrors every packet twice", "AA"), "round 112: the cluster mirrors every packet twice"),
    (
        ("round 112: ranking uses tokens learned from the corpus", "key"),
        "bssxh 112: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 112: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", "a"),
        "round 112: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 112: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 112: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 112: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", "AA"),
        "round 112: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 112: a long session ends when the candle dies", "key"),
        "bssxh 112: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 112: a long session ends when the candle dies", "lemon"),
        "csgbq 112: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 112: a long session ends when the candle dies", "a"),
        "round 112: a long session ends when the candle dies",
    ),
    (
        ("round 112: a long session ends when the candle dies", "zz"),
        "qntmc 112: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 112: a long session ends when the candle dies", "AgentU"),
        "ruyaw 112: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 112: a long session ends when the candle dies", "keyboard"),
        "bssor 112: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 112: a long session ends when the candle dies", "AA"),
        "round 112: a long session ends when the candle dies",
    ),
    (("round 112: encode the prompt then map the result", "key"), "bssxh 112: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 112: encode the prompt then map the result", "lemon"), "csgbq 112: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 112: encode the prompt then map the result", "a"), "round 112: encode the prompt then map the result"),
    (("round 112: encode the prompt then map the result", "zz"), "qntmc 112: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 112: encode the prompt then map the result", "AgentU"),
        "ruyaw 112: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 112: encode the prompt then map the result", "keyboard"),
        "bssor 112: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 112: encode the prompt then map the result", "AA"), "round 112: encode the prompt then map the result"),
    (("round 112: the kernel wakes the worker at dawn", "key"), "bssxh 112: rri iovlop ukocc xfo ambocb er neux"),
    (("round 112: the kernel wakes the worker at dawn", "lemon"), "csgbq 112: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 112: the kernel wakes the worker at dawn", "a"), "round 112: the kernel wakes the worker at dawn"),
    (("round 112: the kernel wakes the worker at dawn", "zz"), "qntmc 112: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 112: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 112: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 112: the kernel wakes the worker at dawn", "keyboard"), "bssor 112: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 112: the kernel wakes the worker at dawn", "AA"), "round 112: the kernel wakes the worker at dawn"),
    (("round 112: service latency drops after the patch", "key"), "bssxh 112: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 112: service latency drops after the patch", "lemon"), "csgbq 112: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 112: service latency drops after the patch", "a"), "round 112: service latency drops after the patch"),
    (("round 112: service latency drops after the patch", "zz"), "qntmc 112: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 112: service latency drops after the patch", "AgentU"),
        "ruyaw 112: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 112: service latency drops after the patch", "keyboard"),
        "bssor 112: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 112: service latency drops after the patch", "AA"), "round 112: service latency drops after the patch"),
    (
        ("round 112: the library caches every vector it sees", "key"),
        "bssxh 112: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 112: the library caches every vector it sees", "lemon"),
        "csgbq 112: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 112: the library caches every vector it sees", "a"), "round 112: the library caches every vector it sees"),
    (
        ("round 112: the library caches every vector it sees", "zz"),
        "qntmc 112: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 112: the library caches every vector it sees", "AgentU"),
        "ruyaw 112: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 112: the library caches every vector it sees", "keyboard"),
        "bssor 112: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 112: the library caches every vector it sees", "AA"),
        "round 112: the library caches every vector it sees",
    ),
    (("round 112: agents argue then the debate resolves", "key"), "bssxh 112: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 112: agents argue then the debate resolves", "lemon"), "csgbq 112: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 112: agents argue then the debate resolves", "a"), "round 112: agents argue then the debate resolves"),
    (("round 112: agents argue then the debate resolves", "zz"), "qntmc 112: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 112: agents argue then the debate resolves", "AgentU"),
        "ruyaw 112: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 112: agents argue then the debate resolves", "keyboard"),
        "bssor 112: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 112: agents argue then the debate resolves", "AA"), "round 112: agents argue then the debate resolves"),
    (("round 112: the filter keeps only strong matches", "key"), "bssxh 112: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 112: the filter keeps only strong matches", "lemon"), "csgbq 112: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 112: the filter keeps only strong matches", "a"), "round 112: the filter keeps only strong matches"),
    (("round 112: the filter keeps only strong matches", "zz"), "qntmc 112: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 112: the filter keeps only strong matches", "AgentU"), "ruyaw 112: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 112: the filter keeps only strong matches", "keyboard"),
        "bssor 112: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 112: the filter keeps only strong matches", "AA"), "round 112: the filter keeps only strong matches"),
    (("round 112: the model answers with a short reply", "key"), "bssxh 112: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 112: the model answers with a short reply", "lemon"), "csgbq 112: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 112: the model answers with a short reply", "a"), "round 112: the model answers with a short reply"),
    (("round 112: the model answers with a short reply", "zz"), "qntmc 112: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 112: the model answers with a short reply", "AgentU"), "ruyaw 112: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 112: the model answers with a short reply", "keyboard"),
        "bssor 112: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 112: the model answers with a short reply", "AA"), "round 112: the model answers with a short reply"),
    (
        ("round 112: the recorder stores the reasoning trace", "key"),
        "bssxh 112: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 112: the recorder stores the reasoning trace", "lemon"),
        "csgbq 112: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 112: the recorder stores the reasoning trace", "a"), "round 112: the recorder stores the reasoning trace"),
    (
        ("round 112: the recorder stores the reasoning trace", "zz"),
        "qntmc 112: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 112: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 112: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 112: the recorder stores the reasoning trace", "keyboard"),
        "bssor 112: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 112: the recorder stores the reasoning trace", "AA"),
        "round 112: the recorder stores the reasoning trace",
    ),
    (("round 112: the angel watches the processor run", "key"), "bssxh 112: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 112: the angel watches the processor run", "lemon"), "csgbq 112: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 112: the angel watches the processor run", "a"), "round 112: the angel watches the processor run"),
    (("round 112: the angel watches the processor run", "zz"), "qntmc 112: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 112: the angel watches the processor run", "AgentU"), "ruyaw 112: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 112: the angel watches the processor run", "keyboard"), "bssor 112: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 112: the angel watches the processor run", "AA"), "round 112: the angel watches the processor run"),
    (("round 112: angle of the vector decides the match", "key"), "bssxh 112: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 112: angle of the vector decides the match", "lemon"), "csgbq 112: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 112: angle of the vector decides the match", "a"), "round 112: angle of the vector decides the match"),
    (("round 112: angle of the vector decides the match", "zz"), "qntmc 112: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 112: angle of the vector decides the match", "AgentU"),
        "ruyaw 112: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 112: angle of the vector decides the match", "keyboard"),
        "bssor 112: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 112: angle of the vector decides the match", "AA"), "round 112: angle of the vector decides the match"),
    (
        ("round 112: the candle burns twice as long at night", "key"),
        "bssxh 112: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 112: the candle burns twice as long at night", "lemon"),
        "csgbq 112: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 112: the candle burns twice as long at night", "a"), "round 112: the candle burns twice as long at night"),
    (
        ("round 112: the candle burns twice as long at night", "zz"),
        "qntmc 112: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 112: the candle burns twice as long at night", "AgentU"),
        "ruyaw 112: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 112: the candle burns twice as long at night", "keyboard"),
        "bssor 112: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 112: the candle burns twice as long at night", "AA"),
        "round 112: the candle burns twice as long at night",
    ),
    (("round 112: a mirror of the universe in one line", "key"), "bssxh 112: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 112: a mirror of the universe in one line", "lemon"), "csgbq 112: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 112: a mirror of the universe in one line", "a"), "round 112: a mirror of the universe in one line"),
    (("round 112: a mirror of the universe in one line", "zz"), "qntmc 112: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 112: a mirror of the universe in one line", "AgentU"), "ruyaw 112: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 112: a mirror of the universe in one line", "keyboard"),
        "bssor 112: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 112: a mirror of the universe in one line", "AA"), "round 112: a mirror of the universe in one line"),
    (("round 112: the queue drains before the storm", "key"), "bssxh 112: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 112: the queue drains before the storm", "lemon"), "csgbq 112: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 112: the queue drains before the storm", "a"), "round 112: the queue drains before the storm"),
    (("round 112: the queue drains before the storm", "zz"), "qntmc 112: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 112: the queue drains before the storm", "AgentU"), "ruyaw 112: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 112: the queue drains before the storm", "keyboard"), "bssor 112: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 112: the queue drains before the storm", "AA"), "round 112: the queue drains before the storm"),
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
