# 《山河无主》Legacy Canon Cleanup 审计与执行记录

> 执行日：2026-10-19；仓库：`amisheng77/SHWZ-V4` live `main`。性质：**防旧设定回流的文档及来源治理**，不是新的 Canon 决策。原物理 CH011／CH012 正文、合同、PACK 和 `state/chapters.json` 的锁定状态/SHA 均不触碰。

## 1. 核对发现

- 清理前 `state/baseline_manifest.json` 登记 **104** 个旧路径，其中 **96** 个在清理前 `main` 中已不存在；该文件不具备现行权威源索引资格。
- 原 `work/contracts/Y4_Chapter11_Contract_V0.1.md` 的 **9 条 `canon_refs`** 指向的旧文档在当前 main 已不存在。旧 `work/packs/CH011_pack.md` 亦把 V3 人物档案、旧四公子关系档及旧大会盟档标成 `type: canon`。这些是**历史生产快照**，不能直接用于新章装配。
- 00 的历史 D13、D23、D91 保留旧“决裂”“王族四公子/旧青年名单”“青公”原案文字。最新事实须分别执行 D110、D66、D105；𬩽史因另依 D94。
- V1.0—V1.3 政治经济提案仍保留历史稿的书名与版本信息；V1.3 的子易角色标签有旧“游学士人”用词，不能盖过 D112 文国使团身份。

## 2. 已执行修改

| 对象 | 执行结果 |
|---|---|
| `state/baseline_manifest.json` | 重建为 **20 项**当前有效 owner、文档与生产入口的源索引；不再是过时的全仓库文件清单。 |
| `state/legacy_quarantine.json`（新建） | **9 项**旧锁稿、合同和 PACK 进入 `NON_CANON_EXECUTION_QUARANTINE`；保留本体、文件名、历史 SHA 和旧版上下文。 |
| `tools/canon_lint.py` | 新增 Legacy Gate：检查源索引有效路径、六 owner 是否完整、隔离资产是否混入当前来源；对非隔离新合同/PACK 的失效 `docs/` 引用报错。历史提案/报告/归档不再当 Canon 执行死名扫描。 |
| `docs/00_创作宪法.md` | 对 D13、D23、D91 加明确 `REPLACED`／`PARTIALLY REPLACED` 标识，保留决策沿革原文。 |
| `docs/03_人物设定.md` | 将含混的“四公子与养望”史料标题明确为“战国四君子原型”，避免当作本书四位王族公子。 |
| `docs/05_生产工作流.md`、Context、HANDOFF、README | 增设生成前的 source index → owner → 新合同/新 PACK 隔离规则；明确旧物理锁稿不可擅改。 |
| `docs/proposals/README.md` 与政经 V1.0—V1.3 | 加 `HISTORICAL / NON-CANON` 标签；V1.3 旧书名只作为历史原题，子易以 D112 文国正式使团名辩身份标注。 |

## 3. 验证与限制

- 已回读 GitHub live `main` 做**结构性验证通过**：有效源清单 **20/20** 路径存在、六 owner 全部列入、隔离旧资产 **9/9** 路径存在且 **0** 项混入现行 source index；D1—D112 决策编号仍为 **112** 项不重复；D13/D23/D91 失效标注、03 人物标题、05 Gate、V1.3 子易现行身份和历史标签均存在。
- 旧 CH011 合同在读回时仍包含原历史 Canon 来源，用于证明未私自改写锁定合同；其旧 `type: canon` 权限**被隔离登记否决**，不是把路径修复成现行事实。
- **本轮未能实际执行 `python3 tools/canon_lint.py`**：运行环境访问 GitHub 的 DNS 失败，无法克隆当前仓库作本地 Python 执行。因此上述验证仅为 GitHub API 回读与结构性规则检查，**不得宣称整体 Python lint 已通过**。下次具备仓库执行环境时，须运行 `python3 -m py_compile tools/canon_lint.py && python3 tools/canon_lint.py` 并修复发现的问题。

## 4. 不改变的 Canon 与后续工作

- Canon **V4.25／D1—D112**；V5.3 **89逻辑章**；D104 食人兽开篇与三处三条黑蟒终镜；D103 传奇三律；**不恢复已废弃审美口号**。
- D112：北海君外交财经养士而无实控封地，安澜君实控浥州港，焦获君实控朔北边州；子易文国使团辩士非学宫旧生；骥同龄将领刺骥案护骥重伤幸存；杜若/舟月/子菖/临风支持链不变。
- 尚未完成的任务：**旧物理 CH011/CH012 到 V5.3 逻辑 CH03/04 的非破坏性映射、重建新合同及 PACK、实际执行引擎与 quarantine 清单的直接对接测试**。本次防回流校验不能代替后续生产工具全链路验证。

**操作原则**：历史材料可以保留，**失效 Canon 权限不能保留**。新一轮写作先查 `state/baseline_manifest.json` 与 owner；如发现旧 `type: canon`，必须检查 `state/legacy_quarantine.json`，禁止把历史事实反向升级。
