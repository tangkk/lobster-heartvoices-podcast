# 龙虾心声

## Editorial Memory

面向学生与上班族的人文心理播客，从具体的日常情绪、关系和社会体验切入。优先选择“很多人经历过、但很少认真说出来”的困扰。温和但不空泛，不贴标签、不说教；通常从生活场景进入，再理解现象与心理机制，最后留下一个反直觉或新的观察角度。避免临床诊断化措辞，也避免“给你三个动作/三条建议”式方法论口吻。

## Workflow

**IDEA → WRITE → FREEZE → PREFLIGHT → Draft PR → TTS PREVIEW → ARTIFACT → LISTEN → AUDIO QA → APPROVE ARTIFACT → MERGE → PUBLISH APPROVED ARTIFACT → VERIFY**。

用户确认的定稿就是 TTS-ready canonical 稿，同时用于文字版和 Podcast。每期使用独立 build/episode branch 与 Draft PR 作为 staging boundary：Draft PR 可反复改稿和生成试听，但 build-only preview 不得上传 R2、修改 RSS 或发布。只有 Audio QA 通过并明确批准该 artifact 后才 merge；正式发布仍是独立、明确的有副作用 gate。

## Canonical / TTS-ready

像一对一聊天：自然短句，一句话尽量一个意思。少用括号、分号和连续破折号。**canonical 从写作阶段就以语音体验为第一排版原则。空行 / 自然段只表示真正需要明显长停顿、观点转场或情绪落点的位置；不能为了文字视觉强调把本应连续说出的句子拆成多个段落。短停顿交给正常标点和 TTS 自身 prosody。**

数字、金额、百分比、年份、年龄、英文、人名与缩写在 FREEZE 前处理成自然、明确、可正确朗读的形式。避免用奇怪标点、重复标点或视觉断行 hack TTS。文字版正文与 canonical 逐字一致，因此文字排版本身也服从 spoken rhythm。默认以约十五分钟成片为目标；旧经验约 4200–5200 中文字、常用目标约 4600 字，但这是写作/时长校验基线，不应为了数字机械扩写。

## Voice & Pause Baseline

使用讯飞；默认 `x6_lingyuyan_pro`、speed 50、volume 52、pitch 50。旧 SOP 保留两个仅在听感需要时使用的备选节奏：48/52/49 与 46/52/48。

长文正式主路径为 **自然段分段合成 + 段间约 350ms 静音**，该方案与当时《龙虾人物》文科试听通过版一致。350ms 只用于真实段落 / segment 层级；同一聊天语气、同一思路里的短句不应因为视觉排版而被插入长停顿。过长段落按完整句拆，经验约 240–420 字/segment；不从一句话中间切开。350ms 是 baseline，可在 Audio QA 后微调，不用奇怪标点修引擎停顿。

正式长文使用 `xfyun_segmented_run.py`；TTS 前检查讯飞环境变量，新稿/新环境先跑第一段最小样本。

## GitHub Build / Artifact Standard

GitHub Actions 是纯 GitHub 路线的执行环境。Preview workflow 长期存在，优先由 Draft PR 自动触发；固定 Python 3.12，并先 `command -v ffmpeg` 检测 runner，存在则复用，不存在才安装，再用 `ffmpeg -version` 验证。Secrets 在真正工作前显式检查，关键步骤失败必须 fail closed，不用 `continue-on-error` 吞错。

Audio QA 批准的是一个具体的 preview artifact，而不是抽象的“这版文字”。**正式发布应优先复用已经试听批准的同一音频 artifact，不应无必要重新 TTS**。若技术上暂时必须重新生成，则重新生成的成片必须视为新的待验证 artifact。

## QA & Publishing Guardrails

Preflight 检查 Editorial / Facts / TTS / Metadata；其中 TTS Preflight 必须做 spoken-form pass：数字 / 年份 / 英文 / 人名归一化、speech paragraphing、pause intent 检查。Audio QA 检查发音、数字、断句、句间停顿、段间停顿和整体聊天感。

发布必须 idempotent / fail-closed：发布前检查 guid 未存在、episode number 是 feed 推导的下一期、canonical 与批准 artifact 存在、R2 key / 文件名 / 文章音频链接一致、Secrets 完整。重复 guid 或关键输入不一致时直接停止，禁止静默继续或盲目 rerun。

发布后独立 VERIFY：至少核对 R2 对象、Podcast RSS 最新 item、guid、enclosure URL / length、`itunes:duration`、description 真实换行、文字版 URL / RSS / 页面。时长直接从最终音频用 `ffprobe` 计算；shell 中避免 `SECONDS` 等特殊变量名，使用 `AUDIO_SECONDS` 等明确变量。

Preview workflow 可以长期保留；Publish 应使用通用、受控的发布入口，不为每一期长期保留 episode-specific workflow。临时一次性 workflow 用完应清理，避免以后误触发。

README 是当前 source of truth；旧 OpenClaw SOP 只作历史参考，本机绝对路径、旧 rss-hosting/audio、消息平台交付和逐段进度回报等规则淘汰。
