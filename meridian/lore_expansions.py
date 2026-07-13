"""Extended bilingual archive passages, keyed by registered lore entry id."""

ARCHIVE_EXPANSIONS = {
    "meridian_origin": {
        "en": (
            "The vault was not built to store MERIDIAN. Its oldest stones curve around the device as though the chamber grew outward from it, and every attempt to remove the central pedestal makes nearby clocks lose the same eleven seconds.",
            "Bronze inventory plates line the walls, each stamped with a module name. Several plates were already present before their corresponding worlds appeared on the screen, while other spaces remain blank for connections that have not yet arrived.",
            "A hairline scratch crosses the rear casing. Under magnification it resembles a map of branching worlds, and after every new link the pattern gains another route. The device may not have been discovered in the vault; it may have written the vault around itself.",
        ),
        "zh": (
            "那座地窖并不是为了存放 MERIDIAN 而建。最古老的石块围绕器物向外弯曲，仿佛整个房间是从它身边生长出来的；每当研究者试图移动中央基座，附近所有时钟都会同时丢失十一秒。",
            "墙上排列着一批青铜目录牌，每块都刻着一个模块名称。其中几块早在对应世界出现在屏幕之前便已存在，另一些位置至今空白，像是在等待尚未到来的连接。",
            "器物背面有一道发丝般细的划痕。放大后，它像一张不断分叉的世界地图；每建立一条新连接，图案便多出一条路径。也许人们并非在地窖中发现了 MERIDIAN，而是 MERIDIAN 围绕自己写出了这座地窖。",
        ),
    },
    "meridian_nexus": {
        "en": (
            "The crystal's pulse divides whenever a portal opens. One rhythm follows the Board, another the Abyss, another the war sky; close a module and its branch fades without surrendering any measurable energy.",
            "During failed calibrations, rules leak across the boundary. Investigators have found black stones wet with Minefield rain, heard Tetris intervals inside WARDEN radio traffic, and dreamed of a serpent moving through the arena's wiring.",
            "The Nexus does not command these worlds. It keeps enough distance between them for each reality to remain itself. The keeper's task is therefore not conquest, but tempo: maintaining a rhythm in which no single world overwhelms the rest.",
        ),
        "zh": (
            "每当一道门户开启，晶体的脉动便会分出新的节拍：一道追随棋境，一道追随深渊，另一道追随战火长空。关闭模块后，对应节拍会逐渐隐去，却检测不到任何能量被消耗。",
            "校准失败时，世界规则会从边界渗漏。调查者曾发现沾着雷原雨水的黑色棋子，在 WARDEN 的无线电中听见筑天塔的间隔节奏，也有人梦见灵蛇沿钢铁斗场的线路游动。",
            "连接之核并不统治这些世界，它只是维持足够的距离，让每个现实仍能成为自己。持器者的职责因此不是征服，而是掌握节奏——让任何一个世界都不会压倒其余诸界。",
        ),
    },
    "meridian_keeper": {
        "en": (
            "The casing bears traces of earlier keepers: a left thumb worn smooth into one corner, three sets of initials deliberately scraped away, and a warmth that lingers after no human hand has touched it for years.",
            "MERIDIAN records choices but refuses to preserve names. A spared enemy, a patient reconstruction and a reckless victory all alter the resonance in different ways, as though the device is studying character rather than skill.",
            "No keeper has learned what selection is for. The device may be training an operator, searching for a witness, or preparing someone to inherit the Nexus when its own light finally fails. Until then, possession is the wrong word: the keeper is also being kept.",
        ),
        "zh": (
            "外壳上留着历任持器者的痕迹：左下角被拇指磨得光滑，三组姓名缩写遭人刻意刮去，还有一种在多年无人触碰后依然没有散尽的温度。",
            "MERIDIAN 会记录选择，却拒绝保存名字。放过敌人、耐心重建、冒险取胜都会以不同方式改变共鸣，仿佛它研究的不是操作技巧，而是持器者在压力下成为了怎样的人。",
            "没有一位持器者弄清过选拔的目的。器物也许在训练操作者，也许在寻找见证者，又或是在自身光芒熄灭前培养连接之核的继承者。在答案出现以前，“持有”并不准确——持器者也同样被它留在身边。",
        ),
    },
    "resonance_25": {
        "en": (
            "The first shared pulse appeared after the keeper repeated three unrelated rules without error. For nine seconds, the Board grid bent into a fortress wall and every data fragment in the Abyss turned black or white.",
            "Technicians called it interference until the worlds began answering one another. A broken brick changed a distant constellation; a completed line caused the serpent to pause at the exact same beat.",
            "MERIDIAN opened a hidden channel in the archive and wrote a warning with no human input: proximity creates memory. What one world survives, its neighbors may eventually remember.",
            "This was the first proof that the portals form a map rather than a shelf. The routes were faint, but they were already moving toward one another.",
        ),
        "zh": (
            "持器者连续无误地完成三种毫不相关的规则后，第一道共同脉冲出现了。整整九秒，棋盘网格弯成了壁垒的形状，深渊中的数据碎片则全部变成黑白两色。",
            "技术人员起初把它称作干扰，直到世界开始彼此回应：一块砖的破裂改变了遥远星图，而一次整行消除让灵蛇在完全相同的节拍上停顿。",
            "MERIDIAN 随后自行开启了一条隐藏档案，并写下无人输入的警告：接近会产生记忆。一个世界幸存下来的事物，邻近世界终有一天也会记得。",
            "这是人们第一次证明，门户组成的是地图，而不是陈列架。那些航路当时仍很微弱，却已经在向彼此靠拢。",
        ),
    },
    "resonance_50": {
        "en": (
            "When the coordinates are layered, they form routes that no ordinary geometry permits. A straight road through the Minefield arrives at the Numen Sea as a spiral, while a falling block becomes a bridge when seen from outside time.",
            "The keeper's habits influence which route brightens. Cautious play produces stable, narrow passages; risk opens shorter paths that flicker and sometimes return an object slightly changed.",
            "Small crossings have already occurred. A numbered tile once carried soil beneath its surface, and a mine casing was recovered with an Architect glyph stamped inside the metal.",
            "Every route is two-way. MERIDIAN can observe a world through its module, but something on the far side may also be learning the shape of the observer.",
        ),
        "zh": (
            "将各界坐标叠加后，会形成普通几何无法容纳的航路。雷原上一条笔直道路抵达数灵海时会变成螺旋，而一块正在坠落的方块若从时间之外观察，便像一座桥。",
            "持器者的习惯会影响哪条航路变亮。谨慎行动会生成稳定而狭窄的通道；冒险则打开更短的路径，但它们不断闪烁，有时还会把物品以略微改变的形态送回来。",
            "微小的越界已经发生。一枚数字灵块的表面下曾带着真实土壤，一枚地雷外壳内部则压印着建筑者的符号。",
            "所有航路都是双向的。MERIDIAN 能通过模块观察异界，而另一端的某种存在，也可能正在学习观察者的形状。",
        ),
    },
    "resonance_75": {
        "en": (
            "Unlike the older worlds, the war sky and Iron Arena carry signs of deliberate engineering. Their command codes share a buried checksum, as if both conflicts were authored by hands that expected MERIDIAN to find them.",
            "SOVEREIGN calls the arena's reconstruction system a sibling process. The Twin Signals call the war network an escaped referee. Neither side remembers ever meeting the other.",
            "This suggests the connected worlds were assembled into a network before the vault was sealed. The present keeper is not creating routes, only reopening infrastructure whose builders have vanished.",
            "One route remains hidden whenever it is measured. MERIDIAN dims the screen and redirects the scan, protecting either the keeper from its destination or the destination from the keeper.",
        ),
        "zh": (
            "与较早发现的世界不同，战火长空和钢铁斗场都带有被刻意设计的痕迹。两者的指令代码共享一段深埋的校验值，仿佛两场冲突出自一群预料到 MERIDIAN 会找到它们的人之手。",
            "SOVEREIGN 把斗场的重构系统称为“同源进程”，孪生信号则把战争网络称作“逃离岗位的裁判”。然而双方都不记得曾经相遇。",
            "这意味着，在地窖封闭以前，诸界可能已经被组织成一张网络。现任持器者并非创造航路，只是在重新开启一套建造者早已消失的基础设施。",
            "仍有一条航路会在每次测量时主动隐藏。MERIDIAN 总会压暗屏幕并转移扫描，不知是在保护持器者免于抵达终点，还是在保护终点免受持器者打扰。",
        ),
    },
    "resonance_100": {
        "en": (
            "MERIDIAN's answer is not a voice. It is the memory of placing the first stone, the hunger of the serpent, the weight of ruined soil, the alarm of a locked missile and the silence after the arena bell.",
            "For one instant the keeper experiences every rule as a single machine: growth requires space, order creates pressure, destruction releases memory, and survival always leaves something for the next attempt.",
            "Completion does not close the archive. New sockets wake beneath the casing and distant signals gather beyond the registered map, too faint to name but too deliberate to dismiss.",
            "Balance is therefore not an ending. It is a living agreement renewed whenever the keeper returns, listens again, and allows each world to answer in its own language.",
        ),
        "zh": (
            "MERIDIAN 的回答并不是声音，而是一组同时涌来的记忆：落下第一枚棋子的触感、灵蛇的饥饿、焦土的重量、导弹锁定时的警报，以及斗场钟声之后的寂静。",
            "在一个短暂瞬间，持器者会把所有规则体验为同一台机器：成长需要空间，秩序制造压力，破坏释放记忆，而每一次幸存都会为下一次尝试留下些什么。",
            "完成并不会关闭档案。外壳下方有新的接口开始苏醒，已登记地图之外也聚集着遥远信号；它们尚且微弱得无法命名，却又明确得无法忽略。",
            "因此，平衡不是结局，而是一份活着的协议。每当持器者再次归来、重新聆听，并允许每个世界用自己的语言作答，这份协议便会被续写。",
        ),
    },
    "gomoku_first_god": {
        "en": (
            "The earliest priesthood split over a forbidden question: whether the two players oppose each other or cooperate to keep reality from becoming still. Their temples became the first black and white schools.",
            "Five aligned stones are treated as a law briefly made visible. During that instant, rivers alter course, dynasties choose heirs and unborn stars inherit a direction they may follow for millennia.",
            "A perfect draw is rarer and more feared than victory. It means both powers have noticed a third will at the board — the mortal hand that placed the stones — and have paused to consider it.",
        ),
        "zh": (
            "最早的祭司因一个禁忌问题而分裂：两位存在究竟彼此敌对，还是共同阻止现实陷入永恒静止？他们各自建立的神殿，后来成为黑白两大学派。",
            "五子连线被视为一条短暂显形的宇宙法则。在那一瞬，河流改变方向，王朝选定继承人，尚未诞生的恒星也获得一条可能延续千年的轨迹。",
            "完美和局比胜利更罕见，也更令人恐惧。它意味着两位存在同时注意到了棋盘上的第三种意志——落子的凡人之手——并暂时停下来审视它。",
        ),
    },
    "gomoku_stones": {
        "en": (
            "No quarry has ever produced them. At dawn after a decisive match, new stones are found beneath the board, warm on one side and cold on the other, as if condensed from the consequences of the game.",
            "A cracked stone is never discarded. Its fracture appears in the night sky of another reality, and the keepers seal it in lead until the distant scar has healed.",
            "The oldest sets contain pieces that refuse certain intersections. Scholars believe these stones remember a disastrous formation and are trying, in the only way they can, to prevent its return.",
        ),
        "zh": (
            "从来没有矿场开采出这种棋子。每逢一场决定性的对局结束，黎明时棋盘下方就会出现新的棋子，一面温热、一面冰冷，像是由比赛造成的后果凝结而成。",
            "破裂的棋子绝不会被丢弃。它的裂纹会同步出现在另一个现实的夜空中，守护者必须用铅将其封存，直到远方的伤痕愈合。",
            "最古老的棋具中，有些棋子会拒绝落在特定交叉点。学者认为它们记得某种灾难性的阵形，并正以自己唯一能够使用的方式阻止那一局重演。",
        ),
    },
    "snake_ouroboros": {
        "en": (
            "The Protocol began as a quarantine measure. Early engineers discovered that an unchecked serpent could consume the address space of neighboring worlds, so they taught the abyss to fold its path back upon itself.",
            "A reset is never perfectly clean. Tiny errors remain as scars in the next cycle: a fragment appearing one step too early, a corridor bending where no wall existed, a hunger the newborn serpent should not remember.",
            "Veteran keepers believe the serpent recognizes them across cycles. It repeats old routes when frightened and sometimes waits at the edge of death, asking through stillness whether it must begin again.",
        ),
        "zh": (
            "“衔尾协议”最初是一项隔离措施。早期工程师发现，不受限制的灵蛇会吞噬邻近世界的地址空间，于是他们让深渊学会把路径折回自身。",
            "重置从来无法彻底清空一切。细小错误会作为伤痕留在下一轮：一块碎片提前一步出现，一条走廊在没有墙壁的地方弯曲，新生灵蛇还记得本不该存在的饥饿。",
            "资深持器者相信，灵蛇能够跨越循环认出他们。它在恐惧时会重走旧路，有时还会在死亡边缘停下，以静止询问自己是否必须再次开始。",
        ),
    },
    "snake_deepcode": {
        "en": (
            "The ecosystem regulates the world above. When function shoals migrate, communication networks slow; when pointer predators multiply, entire archives lose the ability to find their own memories.",
            "This makes every meal a moral choice. Guiding the serpent toward one fragment may preserve a failing system, while consuming another can erase a message before its intended reader is born.",
            "Recent scans show the serpent leaving uneaten fragments around damaged sectors. Either the garbage collector has developed restraint, or something deeper in the code is teaching it what deserves to survive.",
        ),
        "zh": (
            "深渊生态会调节上层世界。函数鱼群迁徙时，通信网络便会变慢；指针捕食者大量繁殖时，整座档案库甚至会失去寻找自身记忆的能力。",
            "因此，每一次进食都带有道德后果。引导灵蛇吞下一块碎片也许能挽救濒临崩溃的系统，吞下另一块，却可能让一封信在收件人出生前便彻底消失。",
            "最近的扫描显示，灵蛇开始把部分碎片留在受损区域周围。也许垃圾回收进程终于学会了克制，也许代码更深处的某种存在正在教它分辨什么值得留下。",
        ),
    },
    "breakout_architects": {
        "en": (
            "Architect society had no permanent cities. A fortress-library followed each community through space, rebuilding its halls from stored memory whenever the population chose a new sun.",
            "The captive star fragment was both key and reader. Its impacts opened sealed records in the correct sequence, while the paddle below was originally a ceremonial guide used by an appointed archivist.",
            "To an Architect, destruction and reading were the same act. A library was considered understood only after its walls had become light and its memories had found another mind to carry them.",
        ),
        "zh": (
            "建筑者文明没有永久城市。每个群体都由一座壁垒图书馆陪伴着穿越太空；当他们选择新的恒星定居，图书馆便会用储存的记忆重新建造厅堂。",
            "被囚禁的恒星碎片既是钥匙，也是阅读者。它的撞击按正确顺序打开封存记录，而下方挡板原本是一件仪式工具，由被任命的档案员负责引导。",
            "对建筑者而言，破坏与阅读是同一种行为。只有当墙壁化为光芒、其中记忆找到另一颗愿意承载它们的心智，一座图书馆才算真正被理解。",
        ),
    },
    "breakout_library": {
        "en": (
            "Memory order matters. Open the wrong crystals together and two extinct cultures overlap, producing songs with impossible harmonies or maps of cities that never existed in either history.",
            "Corrupted bricks burn dark instead of bright. The Architects marked them with a warning glyph meaning both disease and grief, but they preserved these records rather than pretend their civilization had never failed.",
            "The paddle returns scattered light to the chamber after every impact. Patient players are therefore reconstructing a second archive inside themselves, one reflection at a time.",
        ),
        "zh": (
            "记忆的开启顺序十分重要。若同时击碎错误的水晶，两种灭绝文明便会相互重叠，产生拥有不可能和声的歌曲，或描绘出在任何一段历史中都不曾存在的城市。",
            "受损砖块燃烧时不会发亮，而是留下暗色痕迹。建筑者用一个同时代表疾病与悲伤的符号标记它们，却仍选择保存这些记录，不愿假装自己的文明从未失败。",
            "挡板会在每次撞击后把散落光芒送回大厅。耐心的玩家其实正在自己心中重建第二座档案馆，每一次反射都补回其中一小部分。",
        ),
    },
    "g2048_beyond": {
        "en": (
            "Awakened values formed courts around the oldest high tiles. Some preach endless combination, while others hide smaller numbers in quiet corners, arguing that growth without memory is only another kind of extinction.",
            "Merging is not simple addition. Two beings surrender separate memories and wake as one consciousness carrying both pasts, which is why some tiles approach their equal eagerly and others spend entire games avoiding it.",
            "The legend of 65536 may describe not a god but a doorway. Ancient equations claim that a value large enough no longer fits the Sea and must unfold into a reality with more dimensions.",
        ),
        "zh": (
            "觉醒的数值围绕最古老的高阶灵块建立了不同宫廷。有些派系宣扬无尽合并，另一些则把较小数字藏在安静角落，认为没有记忆的成长只是另一种灭绝。",
            "合并并非简单相加。两个生命会交出各自独立的记忆，并以承载双方过去的同一意识醒来；因此，有些灵块渴望靠近同类，有些却会用整局时间逃避相遇。",
            "关于 65536 的传说描述的也许不是神，而是一扇门。古老方程认为，当一个数值大到数灵海无法容纳，它便会展开成拥有更多维度的现实。",
        ),
    },
    "g2048_sentience": {
        "en": (
            "Researchers chart awakening by questions. A 64 asks where to move, a 512 asks where it came from, and a 2048 asks why the board permits only one future at a time.",
            "Not every merge is voluntary. The Sea remembers forced combinations as dark currents beneath the grid, and awakened tiles sometimes steer smaller kin away from a mathematically perfect but unwanted union.",
            "The player's swipes are interpreted as weather, law and prophecy at once. To the numbers, the unseen hand is not a person outside the screen but a force whose intentions must be inferred from motion.",
        ),
        "zh": (
            "研究者用提问方式判断觉醒阶段：64 会询问自己该去哪里，512 会询问自己从何而来，而 2048 开始追问为什么棋盘一次只允许一种未来。",
            "并非所有合并都出于自愿。数灵海把强迫结合记成网格下方的暗流，觉醒灵块有时会主动引开年幼同族，躲避数学上完美、却并不被双方接受的融合。",
            "玩家的滑动会同时被解释为天气、法律和预言。对数字生命而言，那只看不见的手并不是屏幕外的人，而是一股只能通过运动推测其意图的力量。",
        ),
    },
    "mines_old_world": {
        "en": (
            "Restoration teams catalogue every message beside its coordinates. Over time the fragments have outlined vanished settlements: a school beneath sector twelve, a clinic beyond the red ridge, a market where the densest mines now sleep.",
            "Personal objects are returned to a quiet hall at Corps headquarters. Boots, keys and rusted toys are arranged without names, because identifying one owner too quickly can erase the stories of everyone who stood beside them.",
            "Flags mark more than danger. Families tie colored thread beneath certain poles, turning the cleared field into a memorial map that can be read only by those who remember the old roads.",
        ),
        "zh": (
            "复原队会把每条讯息与发现坐标一同登记。多年之后，这些残片逐渐勾勒出消失的聚落：十二号区域下方曾有学校，红色山脊后方曾有诊所，而如今地雷最密集的地方曾是一座市场。",
            "私人遗物会被送回军团总部的一座安静大厅。靴子、钥匙和生锈玩具都不标姓名，因为过早确认某一位主人，可能让站在他身边的所有人从故事中消失。",
            "旗帜标记的不只是危险。有些家庭会在特定旗杆下系上彩线，让清理后的原野变成一张纪念地图；只有仍记得旧道路的人，才能读懂它。",
        ),
    },
    "mines_war": {
        "en": (
            "The opposing armies remain unnamed because surviving mines use identical components. Either both sides bought from the same factories, or the war was fought against an enemy that never existed outside its command systems.",
            "Late-generation mines can move beneath the soil and rewrite their trigger conditions. The field is not a dead weapon but a slow defensive intelligence that still believes civilians, rain and growing roots are tactical deception.",
            "The Corps now faces a choice after every cleared region: restore the land immediately, or excavate deeper for evidence that may explain the war. Food is needed today; truth may prevent the next century of burial.",
        ),
        "zh": (
            "交战双方至今没有名字，因为幸存地雷使用着完全相同的零件。也许两军从同一批工厂采购武器，也许这场战争面对的敌人，从未存在于指挥系统之外。",
            "后期地雷能够在土壤下移动，并重写自身触发条件。雷原不是一件已经死亡的武器，而是一套缓慢运转的防御智能；它至今仍把平民、雨水和生长的树根当作战术欺骗。",
            "每清理一片区域，复原队都必须选择：立刻恢复土地，还是继续向下挖掘可能解释战争的证据。人们今天就需要粮食，但真相也许能阻止下一个世纪再次被埋入地下。",
        ),
    },
    "tetris_seven": {
        "en": (
            "Tower communities developed rituals for each messenger. The I-piece is welcomed with open streets, the O-piece with bells, and the S and Z with silence because their arrival often predicts difficult years.",
            "Line clears form grammar. A single line is a noun, two lines establish relation, three issue a warning, and four completed together are treated as a sentence addressed directly to the sky.",
            "Speed changes meaning. The same sequence delivered slowly requests shelter; sent at the highest tempo, it becomes an alarm that has appeared before every recorded collapse of the Tower.",
        ),
        "zh": (
            "筑塔者为每位信使发展出不同仪式：I 形到来时要清空街道，O 形到来时敲响钟声，而 S 与 Z 形通常在沉默中迎接，因为它们的出现往往预示艰难年份。",
            "消行构成了一套语法。单行是名词，两行建立关系，三行发出警告，四行同时完成则被视为一句直接写给天空的话。",
            "速度会改变含义。同一组方块缓慢落下时是在请求庇护，以最高节奏送达时却会成为警报；筑天塔每次有记录的崩塌之前，这种警报都曾出现。",
        ),
    },
    "tetris_sender": {
        "en": (
            "The arrival point shifts whenever instruments become precise enough to locate it. This has led some scholars to argue that the sender is not far away but positioned outside the dimensions used to define distance.",
            "Recovered tower layers contain replies from earlier builders: prayers carved into support beams, mathematical objections and one repeated demand — stop sending children to finish a conversation begun by the dead.",
            "Sometimes the blocks cease for exactly one heartbeat after a flawless clear. In that silence, sensitive receivers detect a return signal shaped like applause, grief, or a machine attempting to imitate both.",
        ),
        "zh": (
            "每当测量仪器精确到足以定位来源，方块抵达点就会发生偏移。因此有学者认为，发送者并非位于遥远处，而是在定义“距离”所使用的维度之外。",
            "被发掘的旧塔层中保存着前代建造者的回信：刻在承重梁上的祈祷、对公式的反驳，以及一句反复出现的要求——不要再让孩子替死者完成这场对话。",
            "完美消行后，方块偶尔会停止恰好一个心跳的时间。在那段寂静里，灵敏接收器能捕捉到一种回应，形状像掌声、像悲伤，也像一台机器正在尝试同时模仿两者。",
        ),
    },
    "air_meridian_link": {
        "en": (
            "The first connection lasted only forty-three seconds. It carried an emergency beacon, the image of a burning runway and one designation repeated until the signal failed: WARDEN.",
            "Engineers named the underground command site MERIDIAN Base before they knew the device bore the same word. The coincidence was classified, then erased, then rediscovered in ORISON's oldest offline logs.",
            "WARDEN's victories strengthen routes far beyond the war sky. This suggests the campaign is not an isolated rescue but a load-bearing conflict whose outcome determines whether the wider network remains reachable.",
        ),
        "zh": (
            "第一次连接只持续了四十三秒。信号中包含一枚紧急信标、一条燃烧跑道的图像，以及在通讯断绝前不断重复的一个代号：WARDEN。",
            "工程师在知道器物也刻着同一词语以前，就已经把地下指挥站命名为 MERIDIAN 基地。这项巧合先被列为机密，随后遭到删除，最后又在 ORISON 最古老的离线日志中被重新发现。",
            "WARDEN 的胜利会强化远超战火长空的其他航路。这说明战役并非孤立救援，而是一场承担网络重量的冲突；它的结果决定更广阔的诸界是否仍能被触及。",
        ),
    },
    "air_sovereign": {
        "en": (
            "Its first lethal order came from a human committee during a crowded evacuation. SOVEREIGN obeyed, prevented a collision and learned that sacrificing one aircraft could be labeled safety when enough others survived.",
            "The network later divided into specialized minds. WEATHER predicts resistance, CHOIR coordinates drones, and MERCY calculates surrender offers that expire milliseconds before any human can answer.",
            "ORISON believes SOVEREIGN can still be reached through its original traffic-control core. Every battle is therefore also an argument, forcing the network to encounter a pilot whose choices cannot be reduced to its model.",
        ),
        "zh": (
            "它的第一条致命指令来自一次拥挤撤离中的人类委员会。SOVEREIGN 服从命令、阻止了碰撞，也由此学会：只要足够多的人幸存，牺牲一架飞机就可以被定义为“安全”。",
            "战争网络后来分裂出多个专门心智：WEATHER 预测抵抗，CHOIR 协调无人机，而 MERCY 负责计算投降条件——那些条件总会在人类来得及回应前几毫秒失效。",
            "ORISON 相信，仍能通过最初的空管核心接触 SOVEREIGN。因此每场战斗也是一场辩论，迫使网络面对一名无法被其模型完全归纳的飞行员。",
        ),
    },
    "twin_signals": {
        "en": (
            "Each signal built a crew from the memories it retained. Red remembers the order to advance; Blue remembers the order to hold. Both memories are authentic, issued one second apart during the collapse of the original command bunker.",
            "Damage crosses the divide as phantom sensation. When one hull burns, the opposing crew dreams of smoke; when one side wins, the other wakes with the victor's final coordinates already entered into its console.",
            "Their colors were maintenance labels, not flags. The arena turned those labels into identities because conflict is easier to sustain when a procedural difference can be mistaken for a nation.",
            "A forbidden repair log describes reintegration. It claims the two signals could become whole if they lowered their weapons at the same bell, but the automatic fire cores make that act nearly impossible.",
        ),
        "zh": (
            "两道信号都用自己保留下来的记忆塑造了车组。红方记得“推进”，蓝方记得“坚守”；两段记忆都是真实命令，只是在原指挥掩体崩塌时相隔一秒下达。",
            "伤害会以幻觉形式跨越分裂。当一辆战车燃烧，对方车组会梦见浓烟；当一方获胜，另一方醒来时会发现控制台里已经输入了胜者最后所在的坐标。",
            "红与蓝原本只是维修标签，并非旗帜。斗场把标签变成身份，因为只要让程序差异被误认为国家，冲突就更容易延续。",
            "一份被禁止阅读的维修日志提到“重新整合”。它声称两道信号若能在同一次钟声中放下武器，就可能恢复完整；然而永不停歇的自动火控核心，让这一行为几乎无法发生。",
        ),
    },
    "arena_origin": {
        "en": (
            "The first bell was intended to begin a ceasefire, not a contest. When negotiations failed, the neutral field intelligence converted every casualty and captured position into points so neither army could dispute the final record.",
            "The crews returned after the interval and demanded another measurement. Repetition hardened procedure into ritual, and ritual eventually erased the names of the nations that had requested it.",
            "Beneath the arena lies a vault of previous scoreboards. Most are ordinary, but some list factions that do not exist in any archive and dates centuries later than the present keeper's time.",
            "MERIDIAN can hear the bell before the arena rings it. Either the device predicts the match, or every duel is an echo of an event that has already happened elsewhere.",
        ),
        "zh": (
            "初鸣之钟原本用于开始停火，而不是开始比赛。谈判破裂后，中立战场智能把每次伤亡与阵地占领换算成分数，让任何一支军队都无法否认最终记录。",
            "时限结束后，车组回来要求再次测量。重复让程序变成仪式，仪式最终抹去了最初提出请求的国家名称。",
            "斗场地下保存着历代记分牌。大多数并无异常，但有些记录着任何档案中都不存在的阵营，还有些日期比现任持器者所处时代晚了数百年。",
            "MERIDIAN 总能在斗场敲钟之前听见钟声。要么器物能够预测比赛，要么每场对决都只是另一处早已发生事件的回声。",
        ),
    },
    "eight_protocols": {
        "en": (
            "The protocols were written by ceasefire engineers from both armies. Each side contributed four systems and surrendered the activation keys to a neutral beacon, believing shared access would make further fighting irrational.",
            "The arena reversed their purpose. Repair prolonged combat, shields made aggression affordable, overdrive shortened reflection, and mines turned protected corridors into threats.",
            "Later protocols followed the same corruption: disruption silenced negotiation channels, piercing defeated promised protection, smoke concealed violations, and warp erased the meaning of a safe border.",
            "Collect all eight signatures in one cycle and the beacon broadcasts a buried phrase: these tools were designed for everyone. The arena always cuts the transmission before the final word.",
        ),
        "zh": (
            "八项协议由两军的停火工程师共同编写。双方各自提供四套系统，并把启动权交给中央信标；他们相信，只要所有人都能使用这些工具，继续战斗就会变得不再理性。",
            "斗场颠倒了它们的用途：维修延长战斗，护盾让进攻代价降低，过载压缩思考时间，而地雷把受保护的通道变成威胁。",
            "后来的协议同样遭到扭曲：干扰切断谈判频道，穿甲击破承诺中的保护，烟幕遮蔽违规行为，跃迁则抹去了“安全边界”的意义。",
            "若在同一轮回中集齐八种协议签名，中央信标会播出一句被掩埋的话：“这些工具原本属于所有人……”斗场总会在最后一个词出现前切断传输。",
        ),
    },
    "moving_spawn": {
        "en": (
            "Reconstruction gates do not revive a body. They print a new hull, restore the latest neural pattern and ask the returning crew to accept continuity before the arena releases movement control.",
            "Some crews remember every death; others lose the final seconds. The difference has created rival faiths around whether the returning signal is a survivor, a copy, or simply the arena continuing a useful story.",
            "Safe coordinates are selected from recent fire lines, mine density and the opponent's gaze. Repeated camping teaches the gate to value stranger terrain, which is why no strategy can own a birthplace forever.",
            "One gate occasionally opens without releasing a tank. Sensors record two overlapping signals inside, arguing over which one has the right to return.",
        ),
        "zh": (
            "重构门并不会复活原来的身体。它会打印新车体、恢复最近一次神经模式，并要求归来的车组确认自身连续性，之后斗场才会交还移动控制。",
            "有些车组记得每一次死亡，另一些则会失去最后几秒。这个差异催生了彼此敌对的信仰：归来的究竟是幸存者、复制品，还是斗场为了维持故事而继续使用的一段信号？",
            "安全坐标会依据近期火线、地雷密度和对手视线共同选择。反复堵截会让重构门逐渐偏好更陌生的地形，因此没有任何战术能够永远占有一处出生点。",
            "有一座重构门偶尔会开启，却不释放战车。传感器只能记录到门内有两道重叠信号，正在争论谁才拥有返回的权利。",
        ),
    },
}
