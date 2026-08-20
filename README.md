# 龙虾心声

## Editorial Memory

面向学生与上班族的人文心理播客，从具体的日常情绪、关系和社会体验切入。优先选择“很多人经历过、但很少认真说出来”的困扰。温和但不空泛，不贴标签、不说教；通常从生活场景进入，再理解现象与心理机制，最后留下一个反直觉或新的观察角度。避免临床诊断化措辞，也避免“给你三个动作/三条建议”式方法论口吻。

## Workflow

**IDEA → WRITE → FREEZE → PREFLIGHT → BUILD → LISTEN → PUBLISH → VERIFY**。用户确认的定稿就是 TTS-ready canonical 稿，同时用于文字版和 Podcast；定稿前不进入 GitHub 发布流程，正式发布前再次确认。

## Canonical / TTS-ready

像一对一聊天：自然短句，一句话尽量一个意思。少用括号、分号和连续破折号。**canonical 从写作阶段就以语音体验为第一排版原则。空行 / 自然段只表示真正需要明显长停顿、观点转场或情绪落点的位置；不能为了文字视觉强调把本应连续说出的句子拆成多个段落。短停顿交给正常标点和 TTS 自身 prosody。**

数字、金额、百分比、年份、年龄、英文、人名与缩写在 FREEZE 前处理成自然、明确、可正确朗读的形式。避免用奇怪标点、重复标点或视觉断行 hack TTS。文字版正文与 canonical 逐字一致，因此文字排版本身也服从 spoken rhythm。默认以约十五分钟成片为目标；旧经验约 4200–5200 中文字、常用目标约 4600 字，但这是写作/时长校验基线，不应为了数字机械扩写。

## Voice & Pause Baseline

使用讯飞；默认 `x6_lingyuyan_pro`、speed 50、volume 52、pitch 50。旧 SOP 保留两个仅在听感需要时使用的备选节奏：48/52/49 与 46/52/48。

长文正式主路径为 **自然段分段合成 + 段间约 350ms 静音**，该方案与当时《龙虾人物》文科试听通过版一致。350ms 只用于真实段落 / segment 层级；同一聊天语气、同一思路里的短句不应因为视觉排版而被插入长停顿。过长段落按完整句拆，经验约 240–420 字/segment；不从一句话中间切开。350ms 是 baseline，可在 Audio QA 后微调，不用奇怪标点修引擎停顿。

正式长文使用 `xfyun_segmented_run.py`；TTS 前检查讯飞环境变量，新稿/新环境先跑第一段最小样本。

## QA & Publishing Guardrails

Preflight 检查 Editorial / Facts / TTS / Metadata；其中 TTS Preflight 必须做 spoken-form pass：数字 / 年份 / 英文 / 人名归一化、speech paragraphing、pause intent 检查。Audio QA 检查发音、数字、断句、句间停顿、段间停顿和整体聊天感。episode number 从 feed 推导，guid、音频文件名、文章音频链接一致；RSS description 使用真实换行。发布后验证 R2、Podcast RSS、文字 RSS 和文章。

README 是当前 source of truth；旧 OpenClaw SOP 只作历史参考，本机绝对路径、旧 rss-hosting/audio、消息平台交付和逐段进度回报等规则淘汰。
