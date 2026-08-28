# One-Pass Production Checklist

这份清单是《龙虾头条》《龙虾心声》《龙虾故事》《龙虾人物》四档播客的共用生产 SOP。目标是下一期尽量一次走通，避免重复 TTS、半发布、RSS metadata 错误，以及文字版与 Podcast 发布阶段混淆。

## 1. Canonical 先天 TTS-ready
- 定稿就是 Podcast 与文字版共用 canonical，不再派生朗读版或文章改写版。
- 数字、金额、百分比、年份、人名、英文缩写在 FREEZE 前做 spoken-form pass；连续数字属于一个语义单元，禁止因排版或预处理拆开。
- 空行只表示真的需要明显长停顿/转场；普通短停顿靠标点和引擎 prosody。不要为了视觉强调多分段。
- 调长长停顿优先改 segmented synthesis 的 paragraph pause，不用重复/奇怪标点 hack。

## 2. Voice/profile 必须显式确定
- 每档以 repo voice profile 为 source of truth，不凭记忆猜参数。
- 多 profile 节目每期显式声明 profile；Preview 禁止硬编码 default。
- 新 voice/endpoint/授权异常先做极短 smoke test；11200 LiccCheck 优先检查 voice/private capability/APPID entitlement。

## 3. Draft PR 是唯一 staging boundary
- Preview 只由 PR 更新触发，不同时监听 build push + PR。
- `concurrency + cancel-in-progress: true`，连续改稿只保留最新 Preview。
- Preview 阶段只生成 TTS artifact，不写 Podcast 的 R2/RSS。
- Audio QA 批准具体 artifact；记录 run_id、artifact_name、audio_filename、SHA256。

## 4. 固定交付节奏：Preview 试听时发布文字版
标准流程固定为：

`开始制作 → canonical 定稿 → TTS Preview → 用户收到 Preview 完成通知 → 用户要求“发来听一下” → 发送试听 MP3 + 同步发布文字版 → 用户试听确认 → 发布 Podcast`

- **当用户在 TTS Preview 完成后说“发来听一下”时，必须在把 Preview MP3 发到对话里的同时，发布该期文字版。** 不再等最终 Podcast 批准后才发布文字版。
- 文字版使用当前 Preview 对应的 canonical 原文，正文必须逐字一致；禁止摘要、改写、二次生成或删节。
- 此阶段只发布文字站；**不得发布 Podcast，不得写正式 Podcast RSS/R2 音频。**
- 文字站发布后要完成 Pages VERIFY：source entry → Pages deployment success → article URL → 首页/列表 entry。
- 如果文字版发布失败，仍可把 Preview MP3 发给用户试听，但必须明确报告文字版尚未完成，并只修复文字版这一端。
- 用户试听 Preview 后明确说“发布”或等价确认，才进入正式 Podcast 发布。

## 5. “发布”默认指最终 Podcast 发布
- 在 Preview MP3 已交付且文字版已上线之后，用户说“发布”，默认语义是：批准当前试听 artifact，并发布正式 Podcast。
- 正式发布路径：approved artifact → merge/approval state → Podcast R2 → RSS → metadata VERIFY。
- 不重新 TTS；正式 Podcast 必须复用用户刚刚试听并批准的 artifact。
- 如果用户在 Preview 前直接说“发布”，仍不得跳过 Preview/试听批准，除非用户明确要求跳过试听。
- Podcast 发布完成后再次确认文字版仍在线且正文与 approved canonical 一致；若 Preview 后 canonical 有任何修改，必须重新 Preview，并同步更新文字版后再请求最终批准。

## 6. 发布只复用 approved artifact
- 新一期走常驻 `Publish Approved Artifact` + request JSON。
- request 锁定 run_id / artifact_name / audio_filename / SHA256 / slug / title / description / article_url / prefix。
- 发布前验证 Secrets、GUID、episode number、SHA256、MP3 非空、ffprobe 真时长、文件字节数。
- metadata validation 全通过后才允许 R2/RSS mutation；失败 fail closed。
- 禁用 `SECONDS` 特殊变量；使用 `AUDIO_SECONDS`。复杂逻辑放 Python，不在 YAML command substitution 中嵌 heredoc。

## 7. 新一期与重制是两条流程
- 已存在 GUID 禁止走 normal publish。
- 重制走 `replace-*.json` + `Replace Approved Episode Audio`；GUID/title/article/R2 URL 不变，只替换 approved MP3，并更新 length/duration。
- 覆盖 R2 前备份旧对象；RSS push 失败必须恢复旧 R2。

## 8. 文字版发布与 VERIFY
- 文字 repo source commit 不等于线上已发布；Pages 是发布链路的一部分，不只是可选验证。
- **文字版正文必须逐字使用当前 Preview 对应的 canonical 口播稿原文，禁止摘要、改写、二次生成或删节。** 网页只允许额外增加 front matter、音频播放器占位/后续正式音频链接等展示层内容。
- Preview 试听阶段文字版不依赖正式 Podcast enclosure 已存在；不得为了等待正式音频而延迟文字发布。
- 正式 Podcast 发布后，如文字页包含播放器或音频链接，再安全更新展示层，使其指向最终 approved R2 object；正文不得改变。
- 发布前必须验证 `web_article_body == preview_canonical_text`；不一致直接 fail closed。
- `draft: false`。
- Hugo front matter `date` 不得晚于实际 build 时间；建议实际当前时间或安全回拨 1–2 分钟，避免被 Hugo 当 future content 跳过。
- VERIFY：source entry → Pages deployment success → article URL → 首页/列表 entry。
- source 正确但 Pages 未更新时只安全 retrigger Pages，不重复文章/Podcast 发布。

## 9. 最终 VERIFY
Preview/文字交付阶段：
`canonical ✓ → preview artifact ✓ → Preview MP3 发给用户 ✓ → text source = canonical verbatim ✓ → Pages ✓ → online article/list ✓`

Podcast 最终发布阶段：
`audio QA/user approval ✓ → approved SHA ✓ → merge/approval ✓ → R2 ✓ → podcast RSS ✓ → duration/length ✓ → text still matches canonical ✓ → online article still available ✓`

**Podcast 最终链路全部打勾才允许报告“Podcast 发布完成”。** Workflow success 不是最终成功定义；生产端实际可见且 metadata 一致才算成功。

## 10. 操作纪律
- 每个有副作用步骤只走一条明确路径，不并行写同一资源。
- 不盲目 rerun；先判断失败发生在副作用前还是后。
- 临时排障 workflow 用完删除；长期只保留 Preview / Publish Approved Artifact / Replace Approved Episode Audio 三类通用入口。
