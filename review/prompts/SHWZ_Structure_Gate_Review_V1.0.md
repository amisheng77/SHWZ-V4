# 《山河无主》章节结构独立审稿 Prompt V1.0

审稿前读 live main 的 `SHWZ_Current_Context.md`、`work/story_gates/README.md`、对应章群 `work/story_gates/<章群>.json` 及其 `asset_source` 所指旧剧情资产表。只读审核，不修改Canon、锁定正文或作者裁决状态。

**先独立阅读具体章合同或正文**，再看写作Agent自评。逐章核查：
1. A线与B线是否**各自**有人物目标、可信阻力、具体行动选择、不可逆结果？B线拿掉是否毫无损失？若无损失则判装饰线，构成P0。
2. `interaction.bridge` 是真实因果／交锋／主题对照，还是仅在方案里写了“互相促进”？指出准确场景。
3. 按资产ID核验旧版具体人物高光、关系**谁主动**、情感、暗线。对于“关雪救治”“仲符擅发国仓”“终楠与临风初遇”“欠项册”，**只在提要提到不算场面保留**；列出漏失ID。
4. 章节读者实际获得什么戏剧回报？章末下一章的压力来自何处？CH05→06／CH08→09／CH11→12／CH14→15是否真正连续？每章4000—7000字能否容纳而不挤成名册说明？
5. 人物必须鲜明、矛盾必须明确、传奇必须炽烈；代码结构PASS不是文学PASS。

输出逐章实质A/B线真实性、跨线证据、资产兑现ID、保留亮点、P0/P1/P2与具体改法。没有未解决P0才可在 **实际存在的** `work/audits/structural/CHxx-yy_Review_Vx.md` 中形成审稿PASS。**不能代作者填作者批准。** 没有审稿报告不得把JSON的 `literary_review.status` 标passed，未获作者真实裁决不得把 `author_approval.status` 标approved。
