# SHWZ Story Gate V1.0：章节重构及旧剧情防丢失工作流

**优先级：工作流＋机器校验＋独立文学审稿；不是再写一段提示词。** 原Canon、既定历史事实由六份 owner 决定。讨论稿的机器结构通过不代表作者已批准，亦不代表文字精彩。

## 1. 每次章群重构必须走五关

| 环节 | 必须交付 | 放行条件 |
|---|---|---|
| G0 旧资产冻结 | 从现行及旧章纲列出**旧场面、人物高光、关系主动方向、联姻／情报及其后续因果**；每项有唯一编号及来源 | 没有旧剧情资产台账，不得直接重排新章位 |
| G1 多线章节合同 | 章群的 JSON 清单：每章4000—7000字目标，至少两条**有各自目标／阻力／主动选择／结果／具体场面**的实质线，记明两线因果／冲撞／对照关系及章末真实兑现 | 无实质B线或无跨线桥接，不得宣布章节结构完成 |
| G2 机器核销 | `python3 tools/story_gate.py --file work/story_gates/CH06-15_V0.1.json --stage structure` | 每项旧剧情资产有 **keep／rewrite／defer／propose_delete** 的显式去向；章节确实引用对应资产；缺一项即失败 |
| G3 GPT独立文学复核 | `review/prompts/SHWZ_Structure_Gate_Review_V1.0.md`，输出并保存结构审稿报告 | 审稿人逐章验证B线不是陪衬、旧精彩**场面**不是一句概述、场与场有真实因果，清除P0 |
| G4 作者裁决及交写作Agent | `--stage handoff`，记录作者明确批准引用及独立审稿报告路径 | 未有作者批准、报告未过 → **脚本FAIL，不能交写作Agent** |

## 2. 立即可运行的命令

在仓库根目录执行：

```bash
python3 -m unittest discover -s tests -p 'test_story_gate.py' -v
python3 tools/story_gate.py --file work/story_gates/CH06-15_V0.1.json --stage structure
python3 tools/story_gate.py --file work/story_gates/CH06-15_V0.1.json --stage handoff
```

**当前CH06—15的预期结果**：结构检查通过（10章、每章A/B实质线、40项旧剧情资产已映射）；handoff检查**失败**——尚无作者对新倒叙方式与章位的批准，也无独立文学审稿PASS，**绝不自动锁定Canon或启动正文创作**。

JSON字段：`chapter_change`（本章实际局势变化）；`lines[].goal/obstacle/choice/outcome/scene`；`interaction.type/bridge`；`hook.payoff/next_pressure`；`asset_ids`；`asset_migrations`。资产来源由 `asset_source` 指向仓库现有旧资产表，不靠模型自报“没有遗漏”。延后需指定下一章群及理由；删除需作者明确裁决。

## 3. 代码边界与落实

- `tools/story_gate.py` **只验证数据字段、字数目标范围及资产编号引用**。不能凭文字长度判断一条剧情是否真的吸引人，也不能验证正文已经写出旧场面。
- 所有重要资产的实际**戏剧质量、角色真实主动性、冲突升级、历史传奇强度**必须由GPT独立读正文／章合同后审核，作者拥有最终裁决权。
- GitHub Actions `.github/workflows/story-gate.yml` 在相关PR、push上自动执行**结构**检查与单元测试；精简、ubuntu-only、3分钟上限。**它不在无作者批准时强行让讨论稿的handoff测试变绿。**
- **重要现实限制**：Actions红灯默认不能阻止直接推送main。需由拥有仓库设置权限的人，在Ruleset/Branch protection将状态检查 `Story Gate` 设为合并所需条件，才是GitHub层面的真正强制；此外写作Agent必须先获得 `--stage handoff` PASS 的具体版本。
- **不能改旧锁稿**：原物理CH011/CH012、合同、PACK、SHA均保护。新CH06—15讨论只使用候选清单，不把尚未批准的Y4顺叙／闪回方案直接写为已定Canon。

## 4. 防止提示词循环

以后用户指出“B线丢失”“旧戏消失”时，**先交机器Gate失败的具体字段和资产ID，然后直接修JSON和对应场面合同并复审**；禁止再生成同类口号／对照表充当完成。提示词与Skill仅负责让不同Agent调用这条流程，不能替代Gate证据。
