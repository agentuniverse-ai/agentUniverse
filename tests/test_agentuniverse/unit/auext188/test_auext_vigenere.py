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
    (("kitten188", "key"), "umrdil188"),
    (("kitten188", "lemon"), "vmfhry188"),
    (("kitten188", "a"), "kitten188"),
    (("kitten188", "zz"), "jhssdm188"),
    (("kitten188", "AgentU"), "koxgxh188"),
    (("kitten188", "keyboard"), "umrusn188"),
    (("kitten188", "AA"), "kitten188"),
    (("sitting188", "key"), "cmrdmlq188"),
    (("sitting188", "lemon"), "dmfhvyk188"),
    (("sitting188", "a"), "sitting188"),
    (("sitting188", "zz"), "rhsshmf188"),
    (("sitting188", "AgentU"), "soxgbhg188"),
    (("sitting188", "keyboard"), "cmruwnx188"),
    (("sitting188", "AA"), "sitting188"),
    (("agent188", "key"), "kkcxx188"),
    (("agent188", "lemon"), "lkqbg188"),
    (("agent188", "a"), "agent188"),
    (("agent188", "zz"), "zfdms188"),
    (("agent188", "AgentU"), "amiam188"),
    (("agent188", "keyboard"), "kkcoh188"),
    (("agent188", "AA"), "agent188"),
    (("angle188", "key"), "krevi188"),
    (("angle188", "lemon"), "lrszr188"),
    (("angle188", "a"), "angle188"),
    (("angle188", "zz"), "zmfkd188"),
    (("angle188", "AgentU"), "atkyx188"),
    (("angle188", "keyboard"), "krems188"),
    (("angle188", "AA"), "angle188"),
    (("universe188", "key"), "ergfipci188"),
    (("universe188", "lemon"), "frujrcwq188"),
    (("universe188", "a"), "universe188"),
    (("universe188", "zz"), "tmhudqrd188"),
    (("universe188", "AgentU"), "utmixlsk188"),
    (("universe188", "keyboard"), "ergwsrjh188"),
    (("universe188", "AA"), "universe188"),
    (("memory188", "key"), "wikyvw188"),
    (("memory188", "lemon"), "xiycej188"),
    (("memory188", "a"), "memory188"),
    (("memory188", "zz"), "ldlnqx188"),
    (("memory188", "AgentU"), "mkqbks188"),
    (("memory188", "keyboard"), "wikpfy188"),
    (("memory188", "AA"), "memory188"),
    (("stream188", "key"), "cxpoek188"),
    (("stream188", "lemon"), "dxdsnx188"),
    (("stream188", "a"), "stream188"),
    (("stream188", "zz"), "rsqdzl188"),
    (("stream188", "AgentU"), "szvrtg188"),
    (("stream188", "keyboard"), "cxpfom188"),
    (("stream188", "AA"), "stream188"),
    (("context188", "key"), "msldivd188"),
    (("context188", "lemon"), "nszhrix188"),
    (("context188", "a"), "context188"),
    (("context188", "zz"), "bnmsdws188"),
    (("context188", "AgentU"), "curgxrt188"),
    (("context188", "keyboard"), "mslusxk188"),
    (("context188", "AA"), "context188"),
    (("knowledge188", "key"), "urmgpcnkc188"),
    (("knowledge188", "lemon"), "vrakyphss188"),
    (("knowledge188", "a"), "knowledge188"),
    (("knowledge188", "zz"), "jmnvkdcfd188"),
    (("knowledge188", "AgentU"), "ktsjeydmi188"),
    (("knowledge188", "keyboard"), "urmxzeujo188"),
    (("knowledge188", "AA"), "knowledge188"),
    (("vector188", "key"), "fiadsp188"),
    (("vector188", "lemon"), "giohbc188"),
    (("vector188", "a"), "vector188"),
    (("vector188", "zz"), "udbsnq188"),
    (("vector188", "AgentU"), "vkgghl188"),
    (("vector188", "keyboard"), "fiaucr188"),
    (("vector188", "AA"), "vector188"),
    (("processor188", "key"), "zvmmiqcsp188"),
    (("processor188", "lemon"), "avaqrdwaf188"),
    (("processor188", "a"), "processor188"),
    (("processor188", "zz"), "oqnbdrrnq188"),
    (("processor188", "AgentU"), "pxspxmsuv188"),
    (("processor188", "keyboard"), "zvmdssjrb188"),
    (("processor188", "AA"), "processor188"),
    (("reasoning188", "key"), "biycslsre188"),
    (("reasoning188", "lemon"), "cimgbymzu188"),
    (("reasoning188", "a"), "reasoning188"),
    (("reasoning188", "zz"), "qdzrnmhmf188"),
    (("reasoning188", "AgentU"), "rkefhhitk188"),
    (("reasoning188", "keyboard"), "biytcnzqq188"),
    (("reasoning188", "AA"), "reasoning188"),
    (("machine188", "key"), "wearmlo188"),
    (("machine188", "lemon"), "xeovvyi188"),
    (("machine188", "a"), "machine188"),
    (("machine188", "zz"), "lzbghmd188"),
    (("machine188", "AgentU"), "mggubhe188"),
    (("machine188", "keyboard"), "weaiwnv188"),
    (("machine188", "AA"), "machine188"),
    (("learning188", "key"), "viybrgxk188"),
    (("learning188", "lemon"), "wimfatrs188"),
    (("learning188", "a"), "learning188"),
    (("learning188", "zz"), "kdzqmhmf188"),
    (("learning188", "AgentU"), "lkeegcnm188"),
    (("learning188", "keyboard"), "viysbiej188"),
    (("learning188", "AA"), "learning188"),
    (("model188", "key"), "wsbop188"),
    (("model188", "lemon"), "xspsy188"),
    (("model188", "a"), "model188"),
    (("model188", "zz"), "lncdk188"),
    (("model188", "AgentU"), "muhre188"),
    (("model188", "keyboard"), "wsbfz188"),
    (("model188", "AA"), "model188"),
    (("token188", "key"), "dsior188"),
    (("token188", "lemon"), "eswsa188"),
    (("token188", "a"), "token188"),
    (("token188", "zz"), "snjdm188"),
    (("token188", "AgentU"), "tuorg188"),
    (("token188", "keyboard"), "dsifb188"),
    (("token188", "AA"), "token188"),
    (("prompt188", "key"), "zvmwtr188"),
    (("prompt188", "lemon"), "avaace188"),
    (("prompt188", "a"), "prompt188"),
    (("prompt188", "zz"), "oqnlos188"),
    (("prompt188", "AgentU"), "pxszin188"),
    (("prompt188", "keyboard"), "zvmndt188"),
    (("prompt188", "AA"), "prompt188"),
    (("session188", "key"), "ciqcmmx188"),
    (("session188", "lemon"), "diegvzr188"),
    (("session188", "a"), "session188"),
    (("session188", "zz"), "rdrrhnm188"),
    (("session188", "AgentU"), "skwfbin188"),
    (("session188", "keyboard"), "ciqtwoe188"),
    (("session188", "AA"), "session188"),
    (("library188", "key"), "vmzbepi188"),
    (("library188", "lemon"), "wmnfncc188"),
    (("library188", "a"), "library188"),
    (("library188", "zz"), "khaqzqx188"),
    (("library188", "AgentU"), "lofetly188"),
    (("library188", "keyboard"), "vmzsorp188"),
    (("library188", "AA"), "library188"),
    (("service188", "key"), "cipfmao188"),
    (("service188", "lemon"), "didjvni188"),
    (("service188", "a"), "service188"),
    (("service188", "zz"), "rdquhbd188"),
    (("service188", "AgentU"), "skvibwe188"),
    (("service188", "keyboard"), "cipwwcv188"),
    (("service188", "AA"), "service188"),
    (("gateway188", "key"), "qeroayi188"),
    (("gateway188", "lemon"), "refsjlc188"),
    (("gateway188", "a"), "gateway188"),
    (("gateway188", "zz"), "fzsdvzx188"),
    (("gateway188", "AgentU"), "ggxrpuy188"),
    (("gateway188", "keyboard"), "qerfkap188"),
    (("gateway188", "AA"), "gateway188"),
    (("storage188", "key"), "cxmbeeo188"),
    (("storage188", "lemon"), "dxafnri188"),
    (("storage188", "a"), "storage188"),
    (("storage188", "zz"), "rsnqzfd188"),
    (("storage188", "AgentU"), "szsetae188"),
    (("storage188", "keyboard"), "cxmsogv188"),
    (("storage188", "AA"), "storage188"),
    (("network188", "key"), "xirgspu188"),
    (("network188", "lemon"), "yifkbco188"),
    (("network188", "a"), "network188"),
    (("network188", "zz"), "mdsvnqj188"),
    (("network188", "AgentU"), "nkxjhlk188"),
    (("network188", "keyboard"), "xirxcrb188"),
    (("network188", "AA"), "network188"),
    (("latency188", "key"), "verorai188"),
    (("latency188", "lemon"), "wefsanc188"),
    (("latency188", "a"), "latency188"),
    (("latency188", "zz"), "kzsdmbx188"),
    (("latency188", "AgentU"), "lgxrgwy188"),
    (("latency188", "keyboard"), "verfbcp188"),
    (("latency188", "AA"), "latency188"),
    (("buffer188", "key"), "lydpip188"),
    (("buffer188", "lemon"), "myrtrc188"),
    (("buffer188", "a"), "buffer188"),
    (("buffer188", "zz"), "ateedq188"),
    (("buffer188", "AgentU"), "bajsxl188"),
    (("buffer188", "keyboard"), "lydgsr188"),
    (("buffer188", "AA"), "buffer188"),
    (("queue188", "key"), "aycei188"),
    (("queue188", "lemon"), "byqir188"),
    (("queue188", "a"), "queue188"),
    (("queue188", "zz"), "ptdtd188"),
    (("queue188", "AgentU"), "qaihx188"),
    (("queue188", "keyboard"), "aycvs188"),
    (("queue188", "AA"), "queue188"),
    (("worker188", "key"), "gspuip188"),
    (("worker188", "lemon"), "hsdyrc188"),
    (("worker188", "a"), "worker188"),
    (("worker188", "zz"), "vnqjdq188"),
    (("worker188", "AgentU"), "wuvxxl188"),
    (("worker188", "keyboard"), "gsplsr188"),
    (("worker188", "AA"), "worker188"),
    (("kernel188", "key"), "uipxij188"),
    (("kernel188", "lemon"), "vidbrw188"),
    (("kernel188", "a"), "kernel188"),
    (("kernel188", "zz"), "jdqmdk188"),
    (("kernel188", "AgentU"), "kkvaxf188"),
    (("kernel188", "keyboard"), "uiposl188"),
    (("kernel188", "AA"), "kernel188"),
    (("signal188", "key"), "cmexej188"),
    (("signal188", "lemon"), "dmsbnw188"),
    (("signal188", "a"), "signal188"),
    (("signal188", "zz"), "rhfmzk188"),
    (("signal188", "AgentU"), "sokatf188"),
    (("signal188", "keyboard"), "cmeool188"),
    (("signal188", "AA"), "signal188"),
    (("packet188", "key"), "zeauir188"),
    (("packet188", "lemon"), "aeoyre188"),
    (("packet188", "a"), "packet188"),
    (("packet188", "zz"), "ozbjds188"),
    (("packet188", "AgentU"), "pggxxn188"),
    (("packet188", "keyboard"), "zealst188"),
    (("packet188", "AA"), "packet188"),
    (("router188", "key"), "bssdip188"),
    (("router188", "lemon"), "csghrc188"),
    (("router188", "a"), "router188"),
    (("router188", "zz"), "qntsdq188"),
    (("router188", "AgentU"), "ruygxl188"),
    (("router188", "keyboard"), "bssusr188"),
    (("router188", "AA"), "router188"),
    (("cluster188", "key"), "mpscxcb188"),
    (("cluster188", "lemon"), "npgggpv188"),
    (("cluster188", "a"), "cluster188"),
    (("cluster188", "zz"), "bktrsdq188"),
    (("cluster188", "AgentU"), "cryfmyr188"),
    (("cluster188", "keyboard"), "mpsthei188"),
    (("cluster188", "AA"), "cluster188"),
    (("mirror188", "key"), "wmpbsp188"),
    (("mirror188", "lemon"), "xmdfbc188"),
    (("mirror188", "a"), "mirror188"),
    (("mirror188", "zz"), "lhqqnq188"),
    (("mirror188", "AgentU"), "movehl188"),
    (("mirror188", "keyboard"), "wmpscr188"),
    (("mirror188", "AA"), "mirror188"),
    (("filter188", "key"), "pmjdip188"),
    (("filter188", "lemon"), "qmxhrc188"),
    (("filter188", "a"), "filter188"),
    (("filter188", "zz"), "ehksdq188"),
    (("filter188", "AgentU"), "fopgxl188"),
    (("filter188", "keyboard"), "pmjusr188"),
    (("filter188", "AA"), "filter188"),
    (("ranking188", "key"), "belumlq188"),
    (("ranking188", "lemon"), "cezyvyk188"),
    (("ranking188", "a"), "ranking188"),
    (("ranking188", "zz"), "qzmjhmf188"),
    (("ranking188", "AgentU"), "rgrxbhg188"),
    (("ranking188", "keyboard"), "bellwnx188"),
    (("ranking188", "AA"), "ranking188"),
    (("encoding188", "key"), "orayhgxk188"),
    (("encoding188", "lemon"), "procqtrs188"),
    (("encoding188", "a"), "encoding188"),
    (("encoding188", "zz"), "dmbnchmf188"),
    (("encoding188", "AgentU"), "etgbwcnm188"),
    (("encoding188", "keyboard"), "orapriej188"),
    (("encoding188", "AA"), "encoding188"),
    (("mapping188", "key"), "wenzmlq188"),
    (("mapping188", "lemon"), "xebdvyk188"),
    (("mapping188", "a"), "mapping188"),
    (("mapping188", "zz"), "lzoohmf188"),
    (("mapping188", "AgentU"), "mgtcbhg188"),
    (("mapping188", "keyboard"), "wenqwnx188"),
    (("mapping188", "AA"), "mapping188"),
    (("record188", "key"), "biayvb188"),
    (("record188", "lemon"), "cioceo188"),
    (("record188", "a"), "record188"),
    (("record188", "zz"), "qdbnqc188"),
    (("record188", "AgentU"), "rkgbkx188"),
    (("record188", "keyboard"), "biapfd188"),
    (("record188", "AA"), "record188"),
    (("candle188", "key"), "melnpc188"),
    (("candle188", "lemon"), "nezryp188"),
    (("candle188", "a"), "candle188"),
    (("candle188", "zz"), "bzmckd188"),
    (("candle188", "AgentU"), "cgrqey188"),
    (("candle188", "keyboard"), "meleze188"),
    (("candle188", "AA"), "candle188"),
    (("thread188", "key"), "dlpoeb188"),
    (("thread188", "lemon"), "eldsno188"),
    (("thread188", "a"), "thread188"),
    (("thread188", "zz"), "sgqdzc188"),
    (("thread188", "AgentU"), "tnvrtx188"),
    (("thread188", "keyboard"), "dlpfod188"),
    (("thread188", "AA"), "thread188"),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "key"),
        "bssxh 188: rri oemau fpyal psv tykzw mfip dlc vexi hmq",
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "lemon"),
        "csgbq 188: elq ehtgw pezaz tbi ngacd shse elq znkc pct",
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "a"),
        "round 188: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "zz"),
        "qntmc 188: sgd pthbj aqnvm enw itlor nudq sgd kzyx cnf",
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "AgentU"),
        "ruyaw 188: nhk uhbwk hvbph fub wngpy sixl tni ytty jst",
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "keyboard"),
        "bssor 188: tyh aygdy birgr dpl jlpzw mwsr kko pyam dfj",
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", "AA"),
        "round 188: the quick brown fox jumps over the lazy dog",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "key"),
        "bssxh 188: yqildylszcbwc sw y pvywiuyvi psp wyjdm yqildw",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "lemon"),
        "csgbq 188: lkqbgfrujrcwq wf l jdozpaafx qsd ahwxu otprfg",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "a"),
        "round 188: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "zz"),
        "qntmc 188: zfdmstmhudqrd hr z eqzldvnqj enq ltksh zfdmsr",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "AgentU"),
        "ruyaw 188: ugkrgnhibiely iy e skumkabke fuv znfto etxhty",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "keyboard"),
        "bssor 188: axhxxsowvvuci gt o fidwiupfk wrb qsmhi rjorrt",
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", "AA"),
        "round 188: agentuniverse is a framework for multi agents",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "key"),
        "bssxh 188: ixsuvibqi qdspoh yc zcmxmbw cxezviq birbmcfej",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "lemon"),
        "csgbq 188: vrakyphss fesdsq lw hspesdg ryenzrd vqhetihoy",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "a"),
        "round 188: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "zz"),
        "qntmc 188: jmnvkdcfd rsnqdc zr udbsnqr dmzakdr qdsqhduzk",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "AgentU"),
        "ruyaw 188: enuayxxgk wghlej ef oyczsel yngfyxm rkxebyvgp",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "keyboard"),
        "bssor 188: kergpceue jwyvce os mhmxmsg eedlpct fekusitbz",
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", "AA"),
        "round 188: knowledge stored as vectors enables retrieval",
    ),
    (
        ("round 188: the processor reads the record then stops", "key"),
        "bssxh 188: rri nbsaowqyv poebc xfo vcmspn xfor qdsnc",
    ),
    (
        ("round 188: the processor reads the record then stops", "lemon"),
        "csgbq 188: elq dezgqgfzv dsnow fvr cioceo xtsa dxadf",
    ),
    (
        ("round 188: the processor reads the record then stops", "a"),
        "round 188: the processor reads the record then stops",
    ),
    (
        ("round 188: the processor reads the record then stops", "zz"),
        "qntmc 188: sgd oqnbdrrnq qdzcr sgd qdbnqc sgdm rsnor",
    ),
    (
        ("round 188: the processor reads the record then stops", "AgentU"),
        "ruyaw 188: nhk tehweywbk leghf mbe xiphld zlrg mtutf",
    ),
    (
        ("round 188: the processor reads the record then stops", "keyboard"),
        "bssor 188: tyh zvmdssjrb vcbrs kko vcdcru wril thogv",
    ),
    (
        ("round 188: the processor reads the record then stops", "AA"),
        "round 188: the processor reads the record then stops",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "key"),
        "bssxh 188: y gspuip zyjvw rri lobr dequ jpyq rri oeiso",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "lemon"),
        "csgbq 188: l aafxpv biyww fvr yijh glww tezq fvr byqir",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "a"),
        "round 188: a worker pulls the next task from the queue",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "zz"),
        "qntmc 188: z vnqjdq otkkr sgd mdws szrj eqnl sgd ptdtd",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "AgentU"),
        "ruyaw 188: u wuvxxl papyl nhk rrqn tgwx ylos xux kukyr",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "keyboard"),
        "bssor 188: a nrbocs ducoc xff beow deql trfp dlc rielh",
    ),
    (
        ("round 188: a worker pulls the next task from the queue", "AA"),
        "round 188: a worker pulls the next task from the queue",
    ),
    (
        ("round 188: signals travel through the network layer", "key"),
        "bssxh 188: qsklkpq dvyfij dlpyyer xfo rcdambo jkccb",
    ),
    (
        ("round 188: signals travel through the network layer", "lemon"),
        "csgbq 188: dmsbnww ffngix hucsguu elq breaafx wekse",
    ),
    (
        ("round 188: signals travel through the network layer", "a"),
        "round 188: signals travel through the network layer",
    ),
    (
        ("round 188: signals travel through the network layer", "zz"),
        "qntmc 188: rhfmzkr sqzudk sgqntfg sgd mdsvnqj kzxdq",
    ),
    (
        ("round 188: signals travel through the network layer", "AgentU"),
        "ruyaw 188: mimrnem txeixf tnvbnah zlr gytcsed faeie",
    ),
    (
        ("round 188: signals travel through the network layer", "keyboard"),
        "bssor 188: szjxejt hrryop rifoljr xff bekzyvi moyvu",
    ),
    (
        ("round 188: signals travel through the network layer", "AA"),
        "round 188: signals travel through the network layer",
    ),
    (
        ("round 188: the gateway routes each request by policy", "key"),
        "bssxh 188: rri ekxcgew bssdiq oear vcayccx zi tmvmai",
    ),
    (
        ("round 188: the gateway routes each request by policy", "lemon"),
        "csgbq 188: elq uneiiol csghrd imqu cicirdx nm czpuql",
    ),
    (
        ("round 188: the gateway routes each request by policy", "a"),
        "round 188: the gateway routes each request by policy",
    ),
    (
        ("round 188: the gateway routes each request by policy", "zz"),
        "qntmc 188: sgd fzsdvzx qntsdr dzbg qdptdrs ax onkhbx",
    ),
    (
        ("round 188: the gateway routes each request by policy", "AgentU"),
        "ruyaw 188: nhk knmywgc ehotkw rtwh xidnysz fl iilogl",
    ),
    (
        ("round 188: the gateway routes each request by policy", "keyboard"),
        "bssor 188: tyh qerfkap uyyrfg erfr vcriejw lc npzitb",
    ),
    (
        ("round 188: the gateway routes each request by policy", "AA"),
        "round 188: the gateway routes each request by policy",
    ),
    (("round 188: memory grows until the buffer is full", "key"), "bssxh 188: koqmbc ebsuc yldmj dlc lydpip sw depj"),
    (("round 188: memory grows until the buffer is full", "lemon"), "csgbq 188: xiycej kdcjd yzhvw xts ofjrse tw riyw"),
    (("round 188: memory grows until the buffer is full", "a"), "round 188: memory grows until the buffer is full"),
    (("round 188: memory grows until the buffer is full", "zz"), "qntmc 188: ldlnqx fqnvr tmshk sgd ateedq hr etkk"),
    (
        ("round 188: memory grows until the buffer is full", "AgentU"),
        "ruyaw 188: gesser aruaf nhtop gay bajsxl iy jhef",
    ),
    (
        ("round 188: memory grows until the buffer is full", "keyboard"),
        "bssor 188: mvpyvw hfonv errjz tyh lydgsr zv pyjm",
    ),
    (("round 188: memory grows until the buffer is full", "AA"), "round 188: memory grows until the buffer is full"),
    (("round 188: the cluster mirrors every packet twice", "key"), "bssxh 188: rri avyqdip wmpbspc itovw zeauir dagmi"),
    (
        ("round 188: the cluster mirrors every packet twice", "lemon"),
        "csgbq 188: elq qyfwfse xmdfbcw qjrcc bopvif hjtgq",
    ),
    (("round 188: the cluster mirrors every packet twice", "a"), "round 188: the cluster mirrors every packet twice"),
    (("round 188: the cluster mirrors every packet twice", "zz"), "qntmc 188: sgd bktrsdq lhqqnqr dudqx ozbjds svhbd"),
    (
        ("round 188: the cluster mirrors every packet twice", "AgentU"),
        "ruyaw 188: nhk gynmtkv zblruvf xpexc ctwkkx gpcck",
    ),
    (
        ("round 188: the cluster mirrors every packet twice", "keyboard"),
        "bssor 188: tyh mpsthei psvppfs vyovw qocbhd xujqe",
    ),
    (("round 188: the cluster mirrors every packet twice", "AA"), "round 188: the cluster mirrors every packet twice"),
    (
        ("round 188: ranking uses tokens learned from the corpus", "key"),
        "bssxh 188: pkrisre ewcc xmuilc pckvloh dbsk dlc mspzyq",
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", "lemon"),
        "csgbq 188: cezyvyk ggrd xayryw xsncrqr scsy hup gafcfw",
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", "a"),
        "round 188: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", "zz"),
        "qntmc 188: qzmjhmf trdr snjdmr kdzqmdc eqnl sgd bnqotr",
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", "AgentU"),
        "ruyaw 188: latovga uyif mikkrf eyaxrrw zruq gay cuvcnm",
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", "keyboard"),
        "bssor 188: rrqumlh isvv dsifbs chkvlfr firw xff qoisew",
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", "AA"),
        "round 188: ranking uses tokens learned from the corpus",
    ),
    (
        ("round 188: a long session ends when the candle dies", "key"),
        "bssxh 188: y vslq wccwgyr cxhq glcx xfo gyxhjo hgow",
    ),
    (
        ("round 188: a long session ends when the candle dies", "lemon"),
        "csgbq 188: l pabt diegvzr qbqd atsa elq qnyhxs qtie",
    ),
    (
        ("round 188: a long session ends when the candle dies", "a"),
        "round 188: a long session ends when the candle dies",
    ),
    (
        ("round 188: a long session ends when the candle dies", "zz"),
        "qntmc 188: z knmf rdrrhnm dmcr vgdm sgd bzmckd chdr",
    ),
    (
        ("round 188: a long session ends when the candle dies", "AgentU"),
        "ruyaw 188: u lurt lysymbg ynjw jayn zlr vunjpr wcey",
    ),
    (
        ("round 188: a long session ends when the candle dies", "keyboard"),
        "bssor 188: a crxk qfgszrx ileg wyhx xff qaegvi bjss",
    ),
    (
        ("round 188: a long session ends when the candle dies", "AA"),
        "round 188: a long session ends when the candle dies",
    ),
    (("round 188: encode the prompt then map the result", "key"), "bssxh 188: cxgmni rri nbskzx rril wen dlc biqepr"),
    (("round 188: encode the prompt then map the result", "lemon"), "csgbq 188: procqp xts ccsydg elqb zlt fvr cieiye"),
    (("round 188: encode the prompt then map the result", "a"), "round 188: encode the prompt then map the result"),
    (("round 188: encode the prompt then map the result", "zz"), "qntmc 188: dmbncd sgd oqnlos sgdm lzo sgd qdrtks"),
    (
        ("round 188: encode the prompt then map the result", "AgentU"),
        "ruyaw 188: ynisqx nhk tehgpz xuxh mgt gay rkwhen",
    ),
    (
        ("round 188: encode the prompt then map the result", "keyboard"),
        "bssor 188: eefyhc uve guyqnu hhvq wen uve ihcyju",
    ),
    (("round 188: encode the prompt then map the result", "AA"), "round 188: encode the prompt then map the result"),
    (("round 188: the kernel wakes the worker at dawn", "key"), "bssxh 188: rri iovlop ukocc xfo ambocb er neux"),
    (("round 188: the kernel wakes the worker at dawn", "lemon"), "csgbq 188: elq yrcrqz jloqg gsi icevid og oeib"),
    (("round 188: the kernel wakes the worker at dawn", "a"), "round 188: the kernel wakes the worker at dawn"),
    (("round 188: the kernel wakes the worker at dawn", "zz"), "qntmc 188: sgd jdqmdk vzjdr sgd vnqjdq zs czvm"),
    (("round 188: the kernel wakes the worker at dawn", "AgentU"), "ruyaw 188: nhk orkher andys zlr pirqie tn dgaa"),
    (("round 188: the kernel wakes the worker at dawn", "keyboard"), "bssor 188: tyh uiposl nduiq uve nrbocs ot udgr"),
    (("round 188: the kernel wakes the worker at dawn", "AA"), "round 188: the kernel wakes the worker at dawn"),
    (("round 188: service latency drops after the patch", "key"), "bssxh 188: qovtsgc verorai hpytq kjrov rri nkxar"),
    (("round 188: service latency drops after the patch", "lemon"), "csgbq 188: didjvni xogprom qcsbg nqxqf gsi bognl"),
    (("round 188: service latency drops after the patch", "a"), "round 188: service latency drops after the patch"),
    (("round 188: service latency drops after the patch", "zz"), "qntmc 188: rdquhbd kzsdmbx cqnor zesdq sgd ozsbg"),
    (
        ("round 188: service latency drops after the patch", "AgentU"),
        "ruyaw 188: mexzvvy lgxrgwy jvbim alxrk nhk tnmwh",
    ),
    (
        ("round 188: service latency drops after the patch", "keyboard"),
        "bssor 188: svufmaf zakhxgw efogv kjrff tyh zerdv",
    ),
    (("round 188: service latency drops after the patch", "AA"), "round 188: service latency drops after the patch"),
    (
        ("round 188: the library caches every vector it sees", "key"),
        "bssxh 188: rri jsfpkvw meariq ozcbc togryv gd wcow",
    ),
    (
        ("round 188: the library caches every vector it sees", "lemon"),
        "csgbq 188: elq zvmvmfl neovrd ihsej zqqgzv uh fpie",
    ),
    (("round 188: the library caches every vector it sees", "a"), "round 188: the library caches every vector it sees"),
    (
        ("round 188: the library caches every vector it sees", "zz"),
        "qntmc 188: sgd khaqzqx bzbgdr dudqx udbsnq hs rddr",
    ),
    (
        ("round 188: the library caches every vector it sees", "AgentU"),
        "ruyaw 188: nhk pvulaxc ptwhkw royre zrvnox mg lyey",
    ),
    (
        ("round 188: the library caches every vector it sees", "keyboard"),
        "bssor 188: tyh vmzsorp fkgffg emhbc tfqtfu sx qfss",
    ),
    (
        ("round 188: the library caches every vector it sees", "AA"),
        "round 188: the library caches every vector it sees",
    ),
    (("round 188: agents argue then the debate resolves", "key"), "bssxh 188: yqildw ybkso xfor rri bofydi powmvzcc"),
    (("round 188: agents argue then the debate resolves", "lemon"), "csgbq 188: lkqbgd eduhp xtsa elq rrmefs epwazipw"),
    (("round 188: agents argue then the debate resolves", "a"), "round 188: agents argue then the debate resolves"),
    (("round 188: agents argue then the debate resolves", "zz"), "qntmc 188: zfdmsr zqftd sgdm sgd cdazsd qdrnkudr"),
    (
        ("round 188: agents argue then the debate resolves", "AgentU"),
        "ruyaw 188: ugkrgl urmyr mbet xux xehegx leysyoys",
    ),
    (
        ("round 188: agents argue then the debate resolves", "keyboard"),
        "bssor 188: axhxxq bfglh dlco hhv gofyus rvvyptfg",
    ),
    (("round 188: agents argue then the debate resolves", "AA"), "round 188: agents argue then the debate resolves"),
    (("round 188: the filter keeps only strong matches", "key"), "bssxh 188: rri dsprov ioinc slvc qdvmxk kkxariq"),
    (("round 188: the filter keeps only strong matches", "lemon"), "csgbq 188: elq tvwxqf xpibg bypk ggcszu zlxovrd"),
    (("round 188: the filter keeps only strong matches", "a"), "round 188: the filter keeps only strong matches"),
    (("round 188: the filter keeps only strong matches", "zz"), "qntmc 188: sgd ehksdq jddor nmkx rsqnmf lzsbgdr"),
    (("round 188: the filter keeps only strong matches", "AgentU"), "ruyaw 188: nhk jvenex orxjs uryr mtxsaz gazguxm"),
    (
        ("round 188: the filter keeps only strong matches", "keyboard"),
        "bssor 188: tyh pmjusr bhotq pblp vdvmou mrwmlct",
    ),
    (("round 188: the filter keeps only strong matches", "AA"), "round 188: the filter keeps only strong matches"),
    (("round 188: the model answers with a short reply", "key"), "bssxh 188: rri kyhcv elcacbw usxf k wfyvr binvc"),
    (("round 188: the model answers with a short reply", "lemon"), "csgbq 188: elq aboix oadaqff hmfv n dlafg cibzl"),
    (("round 188: the model answers with a short reply", "a"), "round 188: the model answers with a short reply"),
    (("round 188: the model answers with a short reply", "zz"), "qntmc 188: sgd lncdk zmrvdqr vhsg z rgnqs qdokx"),
    (("round 188: the model answers with a short reply", "AgentU"), "ruyaw 188: nhk qbwyl grfpyry avmb a ylbkn rktyr"),
    (
        ("round 188: the model answers with a short reply", "keyboard"),
        "bssor 188: tyh wsbfz aevgipt kikk k wfpft ihzpw",
    ),
    (("round 188: the model answers with a short reply", "AA"), "round 188: the model answers with a short reply"),
    (
        ("round 188: the recorder stores the reasoning trace", "key"),
        "bssxh 188: rri pogmbhcb wryvcc xfo vckwmxmlq xpkgc",
    ),
    (
        ("round 188: the recorder stores the reasoning trace", "lemon"),
        "csgbq 188: elq frnsdrrc wfcepw fvr cimgbymzu gceos",
    ),
    (("round 188: the recorder stores the reasoning trace", "a"), "round 188: the recorder stores the reasoning trace"),
    (
        ("round 188: the recorder stores the reasoning trace", "zz"),
        "qntmc 188: sgd qdbnqcdq rsnqdr sgd qdzrnmhmf sqzbd",
    ),
    (
        ("round 188: the recorder stores the reasoning trace", "AgentU"),
        "ruyaw 188: nhk vrvirjie lnoxif mbe xinlinort mlaii",
    ),
    (
        ("round 188: the recorder stores the reasoning trace", "keyboard"),
        "bssor 188: tyh biapfdvu cxmsss kko vcbgoelxk rsocv",
    ),
    (
        ("round 188: the recorder stores the reasoning trace", "AA"),
        "round 188: the recorder stores the reasoning trace",
    ),
    (("round 188: the angel watches the processor run", "key"), "bssxh 188: rri yxkcv aydgfow rri nbsaowqyv per"),
    (("round 188: the angel watches the processor run", "lemon"), "csgbq 188: elq oarix knegtsf elq dezgqgfzv dia"),
    (("round 188: the angel watches the processor run", "a"), "round 188: the angel watches the processor run"),
    (("round 188: the angel watches the processor run", "zz"), "qntmc 188: sgd zmfdk vzsbgdr sgd oqnbdrrnq qtm"),
    (("round 188: the angel watches the processor run", "AgentU"), "ruyaw 188: nhk eazyl cegvbey xux jrugrlmox vhg"),
    (("round 188: the angel watches the processor run", "keyboard"), "bssor 188: tyh krefz wrwmlct hhv sbsafgsfu byl"),
    (("round 188: the angel watches the processor run", "AA"), "round 188: the angel watches the processor run"),
    (("round 188: angle of the vector decides the match", "key"), "bssxh 188: yxkjo sd dlc fiadsp niashcc xfo qydgf"),
    (("round 188: angle of the vector decides the match", "lemon"), "csgbq 188: lrszr zj fvr giohbc hqqvoie hup qmhps"),
    (("round 188: angle of the vector decides the match", "a"), "round 188: angle of the vector decides the match"),
    (("round 188: angle of the vector decides the match", "zz"), "qntmc 188: zmfkd ne sgd udbsnq cdbhcdr sgd lzsbg"),
    (
        ("round 188: angle of the vector decides the match", "AgentU"),
        "ruyaw 188: unmpr hz tni ixwtuv qxwijif mbe segvb",
    ),
    (
        ("round 188: angle of the vector decides the match", "keyboard"),
        "bssor 188: aejvi mg hhv yogrpf dvfshct hhv pkxai",
    ),
    (("round 188: angle of the vector decides the match", "AA"), "round 188: angle of the vector decides the match"),
    (
        ("round 188: the candle burns twice as long at night", "key"),
        "bssxh 188: rri akrbvi zevlc xusgc kw jyre kx lskfd",
    ),
    (
        ("round 188: the candle burns twice as long at night", "lemon"),
        "csgbq 188: elq qnyhxs ofvzg ghmos nd pabt lx zwtsx",
    ),
    (("round 188: the candle burns twice as long at night", "a"), "round 188: the candle burns twice as long at night"),
    (
        ("round 188: the candle burns twice as long at night", "zz"),
        "qntmc 188: sgd bzmckd atqmr svhbd zr knmf zs mhfgs",
    ),
    (
        ("round 188: the candle burns twice as long at night", "AgentU"),
        "ruyaw 188: nhk gngxlk fhkhs zavvy ay pbga az rvzbt",
    ),
    (
        ("round 188: the candle burns twice as long at night", "keyboard"),
        "bssor 188: tyh meleze sxbrq ukith kw jpbg rw xmeih",
    ),
    (
        ("round 188: the candle burns twice as long at night", "AA"),
        "round 188: the candle burns twice as long at night",
    ),
    (("round 188: a mirror of the universe in one line", "key"), "bssxh 188: y wmpbsp yj rri sxmtovqo ml yrc vmlo"),
    (("round 188: a mirror of the universe in one line", "lemon"), "csgbq 188: l qufezv at gsi gbvgidgr tr abr wmzs"),
    (("round 188: a mirror of the universe in one line", "a"), "round 188: a mirror of the universe in one line"),
    (("round 188: a mirror of the universe in one line", "zz"), "qntmc 188: z lhqqnq ne sgd tmhudqrd hm nmd khmd"),
    (("round 188: a mirror of the universe in one line", "AgentU"), "ruyaw 188: u movehl ol xux onozrkme or bgy lorr"),
    (
        ("round 188: a mirror of the universe in one line", "keyboard"),
        "bssor 188: a dlbvms cf kko yljjeivo ml pbe clxi",
    ),
    (("round 188: a mirror of the universe in one line", "AA"), "round 188: a mirror of the universe in one line"),
    (("round 188: the queue drains before the storm", "key"), "bssxh 188: rri oeiso hpkmlc fcpspo xfo wryvk"),
    (("round 188: the queue drains before the storm", "lemon"), "csgbq 188: elq ehpyq relmzg opjafr elq ggzvy"),
    (("round 188: the queue drains before the storm", "a"), "round 188: the queue drains before the storm"),
    (("round 188: the queue drains before the storm", "zz"), "qntmc 188: sgd ptdtd cqzhmr adenqd sgd rsnql"),
    (("round 188: the queue drains before the storm", "AgentU"), "ruyaw 188: nhk uhxoe jvnbhs hishle zlr lnoxq"),
    (("round 188: the queue drains before the storm", "keyboard"), "bssor 188: tyh aycvs didsrq csffuo xff gtfuw"),
    (("round 188: the queue drains before the storm", "AA"), "round 188: the queue drains before the storm"),
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
