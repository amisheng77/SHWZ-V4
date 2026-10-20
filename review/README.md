# 《山河无主》正文独立审稿工具包 V1.0

> **性质**：非 Canon 的审稿操作资料。现行世界观权威仍为 live main 的六份 owner 与 D112；本目录不新增 D 编号，不修改旧 CH011/CH012 锁稿或状态。

## 最省事的使用方式

**短样稿**：在 ChatGPT 对话中直接粘贴全文并说“按 SHWZ Literary Review Protocol V1.0 审稿”。

**推荐长期方式**：写作 Agent 把每次完整正文提交到 GitHub 的独立写作分支，使用清晰的路径与文件版本（如 `drafts/v5_3/CH01_夜哭_V0.1.md`；仅举例，**不要覆盖旧版 CH011/CH012 路径**），把 commit SHA 与路径发给 GPT：

> 按《山河无主》独立文学审稿规范 V1.0 审核：仓库 amisheng77/SHWZ-V4；正文 [精确路径]；commit [完整 SHA]；逻辑章 CH01。请先评文学、再评 Canon，给我 P0/P1/P2 和写作 Agent 可直接执行的修订任务。只读审核，不直接改正文。

**提交建议**：提供正文全文或 GitHub URL／`路径@commit`；有 Chapter Contract 更好，但没有也可先进行文学初审，缺失事实证据须标“待验证”而不是假定错误。审稿人如在聊天中先读正文，再读合同与 Canon，能够减少把设计意图自动脑补进正文的偏差——**但这不等于真正完全不知道背景的盲读者**。

**出报告**：默认在对话中展示审稿结果。要留 Git 版本记录，可明确要求将报告另存 `work/audits/literary/CH01_Literary_Review_V0.1.md`；不覆盖正文，不自动调整 lock／Canon／Story State。

## 工具包的三个部分

- [正式审稿协议](SHWZ_Literary_Review_Protocol_V1.0.md)：审核顺序、文学六维、Canon Gate、P0/P1/P2、五章整体审查。
- [一段式审稿 Prompt](prompts/SHWZ_Independent_Review_Prompt_V1.0.md)：给 GPT 或其他审稿模型复制使用。
- [审稿报告模板](templates/Chapter_Review_Report_Template_V1.0.md)：统一版本标识、证据、修订任务和复审状态。
- [可移植 Skill](../.agents/skills/shwz-literary-review/SKILL.md)：面向支持读取项目 `SKILL.md` 的 Agent；**在 GitHub 中创建文件不代表它已经自动安装或注册到 ChatGPT 插件系统**。在这里给正文链接即可由 GPT 按协议执行。

## 分工底线

写作 Agent 负责完整小说正文；GPT 负责独立的文学初读、Canon 审计和修订复核；作者拥有最终艺术裁决权。**代码只做可验证的事实校验，无法替代文学判断。**原有 `tools/canon_lint.py` 继续负责客观一致性，勿为审稿重复搭一套复杂引擎。
