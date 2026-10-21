#!/usr/bin/env python3
"""SHWZ 章群结构门禁：覆盖旧剧情资产、保证双线合同完整性。

Stage structure verifies explicit, inspectable planning data, not literary quality.
Stage handoff additionally requires author approval + human/LLM literary review record.
Never reads or writes locked drafts and never edits Canon.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"keep", "rewrite", "defer", "propose_delete"}
INTERACTIONS = {"causal", "collision", "contrast", "braid"}
NOISE = re.compile(r"^(?:待定|TBD|TODO|placeholder|none|无|\[.*\]|\.\.\.|〔P〕)$", re.I)
ID_PATTERN = re.compile(r"^\|\s*((?:F\d+-A|Y\d+-A)\d+)\s*\|", re.M)


def meaning(value, *, min_len=8):
    if not isinstance(value, str):
        return False
    value = value.strip()
    return len(value) >= min_len and not NOISE.fullmatch(value)


def valid_chapter_id(value):
    return isinstance(value, str) and re.fullmatch(r"CH\d{2,3}", value) is not None


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def review_manifest(path: Path, stage: str = "structure", root: Path = ROOT):
    errors = []
    warnings = []
    def error(path, note):
        errors.append(f"{path}: {note}")
    if not path.exists():
        return [f"{path}: 清单不存在"], []
    try:
        data = load_json(path)
    except (ValueError, OSError) as exc:
        return [f"{path}: JSON 无效 ({exc})"], []
    if not isinstance(data, dict):
        return ["根节点必须是对象"], []
    if data.get("schema_version") != "1.0":
        error("schema_version", "必须为 1.0")
    asset_source = data.get("asset_source")
    asset_ids = set()
    if not meaning(asset_source, min_len=10) or not asset_source.startswith("docs/reports/") or not asset_source.endswith(".md"):
        error("asset_source", "必须是仓库内的剧情资产核对表路径 docs/reports/*.md")
    else:
        source_file = root / asset_source
        if not source_file.is_file():
            error("asset_source", f"源台账文件不存在：{asset_source}")
        else:
            asset_ids = set(ID_PATTERN.findall(source_file.read_text(encoding="utf-8")))
            if not asset_ids:
                error("asset_source", "源台账没有规范的 | F1-Axx | / | Y4-Axx | 行")
    arc = data.get("arc")
    if not meaning(arc, min_len=5):
        error("arc", "需填写被修改的章群范围")
    chapters = data.get("chapters")
    chapter_ids = set()
    chapter_asset_map = {}
    if not isinstance(chapters, list) or not chapters:
        error("chapters", "需列出逐章结构；不可只提交十章摘要")
        chapters = []
    for i, ch in enumerate(chapters):
        loc = f"chapters[{i}]"
        if not isinstance(ch, dict):
            error(loc, "章节必须是对象")
            continue
        cid = ch.get("id")
        if not valid_chapter_id(cid):
            error(f"{loc}.id", "章节ID须如 CH06")
            cid = f"unknown_{i}"
        elif cid in chapter_ids:
            error(f"{loc}.id", f"重复章号 {cid}")
        chapter_ids.add(cid)
        target = ch.get("word_target")
        if not isinstance(target, int) or isinstance(target, bool) or not 4000 <= target <= 7000:
            error(f"{cid}.word_target", "每章目标须在4000—7000字")
        if not meaning(ch.get("chapter_change"), min_len=12):
            error(f"{cid}.chapter_change", "必须写明本章新的不可逆局势/人物变化，不能只写主题")
        lines = ch.get("lines", [])
        if not isinstance(lines, list) or len(lines) < 2:
            error(f"{cid}.lines", "至少两条实质剧情线，只有一条必失败")
            lines = []
        seen_line = set()
        text_lines = []
        for k, line in enumerate(lines):
            lp = f"{cid}.lines[{k}]"
            if not isinstance(line, dict):
                error(lp, "需对象字段 goal, obstacle, choice, outcome, scene")
                continue
            lid = line.get("id")
            if not isinstance(lid, str) or not lid.strip() or lid in seen_line:
                error(f"{lp}.id", "剧情线ID必须唯一")
            seen_line.add(lid)
            for field in ("goal", "obstacle", "choice", "outcome", "scene"):
                if not meaning(line.get(field), min_len=10):
                    error(f"{lp}.{field}", "必须填写具体人物行动/阻力/选择/结果/场景，而非主题词")
            text_lines.append(tuple(line.get(x) for x in ("goal", "obstacle", "choice", "outcome")))
        if len(text_lines) != len(set(map(str, text_lines))):
            error(f"{cid}.lines", "A/B线内容重复，疑似同一事件拆成两行")
        link = ch.get("interaction")
        if not isinstance(link, dict) or link.get("type") not in INTERACTIONS:
            error(f"{cid}.interaction", "需明确 causal/collision/contrast/braid 类型")
        elif not meaning(link.get("bridge"), min_len=18):
            error(f"{cid}.interaction.bridge", "须具体写出两线因果/冲撞/对照的桥接事件")
        hook = ch.get("hook")
        if not isinstance(hook, dict):
            error(f"{cid}.hook", "须交代本章兑现与下章动力")
        else:
            for field in ("payoff", "next_pressure"):
                if not meaning(hook.get(field), min_len=10):
                    error(f"{cid}.hook.{field}", "兑现或新压力太笼统")
        aids = ch.get("asset_ids")
        if not isinstance(aids, list):
            error(f"{cid}.asset_ids", "须显式列出场面资产ID（允许空数组）")
            aids = []
        if len(aids) != len(set(aids)):
            error(f"{cid}.asset_ids", "资产ID本章重复")
        for a in aids:
            chapter_asset_map.setdefault(a, set()).add(cid)
            if asset_ids and a not in asset_ids:
                error(f"{cid}.asset_ids", f"未知资产编号 {a}")
    assets = data.get("asset_migrations")
    if not isinstance(assets, list):
        error("asset_migrations", "必须逐条列出原资产迁移核对")
        assets = []
    migrated = {}
    for i, record in enumerate(assets):
        key = f"asset_migrations[{i}]"
        if not isinstance(record, dict):
            error(key, "记录须为对象")
            continue
        aid = record.get("id")
        if not isinstance(aid, str):
            error(f"{key}.id", "必须登记资产ID")
            continue
        if aid in migrated:
            error(f"{key}.id", f"重复登记 {aid}")
        migrated[aid] = record
        if aid not in asset_ids:
            error(f"{key}.id", f"源台账中不存在 {aid}")
        action = record.get("disposition")
        if action not in ALLOWED:
            error(f"{key}.disposition", "须 keep/rewrite/defer/propose_delete")
            continue
        if action in {"keep", "rewrite"}:
            targets = record.get("chapters")
            if not isinstance(targets, list) or not targets or not all(t in chapter_ids for t in targets):
                error(f"{aid}.chapters", "保留/改写必须指向本章群实际章号")
            else:
                declared = chapter_asset_map.get(aid, set())
                if not set(targets).issubset(declared):
                    error(f"{aid}.chapters", f"资产在目标章场景未引用：{sorted(set(targets)-declared)}")
            if not meaning(record.get("scene_payoff"), min_len=12):
                error(f"{aid}.scene_payoff", "必须写原人物戏如何通过具体场面兑现，不可只说保留")
        elif action == "defer":
            if not meaning(record.get("later_target"), min_len=4) or not meaning(record.get("reason"), min_len=10):
                error(f"{aid}.defer", "必须填写后续章群位置及为什么现在不出现")
            if stage == "handoff" and not record.get("carry_forward_owner"):
                error(f"{aid}.carry_forward_owner", "进入写作前延期资产必须有下一阶段核销责任人/清单")
        elif action == "propose_delete":
            if not meaning(record.get("reason"), min_len=10):
                error(f"{aid}.reason", "拟删除必须说明原因")
            if stage == "handoff" and not meaning(record.get("author_decision_ref"), min_len=8):
                error(f"{aid}.author_decision_ref", "作者未明确批准删除，禁止交写作Agent")
    if asset_ids:
        missing = asset_ids-set(migrated)
        if missing:
            error("asset_migrations", "源台账漏迁移: "+", ".join(sorted(missing)))
    orphan = set(chapter_asset_map)-set(migrated)
    if orphan:
        error("chapters.asset_ids", "章节引用但未核销: "+", ".join(sorted(orphan)))
    if stage == "handoff":
        approval = data.get("author_approval", {})
        review = data.get("literary_review", {})
        if not isinstance(approval, dict) or approval.get("status") != "approved" or not meaning(approval.get("reference"), min_len=8):
            error("author_approval", "缺作者明确批准及可追踪裁决引用，不得交写作Agent")
        if not isinstance(review, dict) or review.get("status") != "passed":
            error("literary_review", "独立文学结构审稿未通过，不得交写作Agent")
        elif not meaning(review.get("report_path"), min_len=10) or not (root / review["report_path"]).is_file():
            error("literary_review.report_path", "须有真实审稿报告文件，非口头承诺")
    else:
        warnings.append("结构检查只验证显式字段与资产覆盖；不证明戏剧质量。交稿前执行 --stage handoff，并由独立审稿核实两线确实成立。")
    return errors, warnings


def main():
    p = argparse.ArgumentParser(description="SHWZ 章节多线及旧剧情迁移 Gate")
    p.add_argument("--file", type=Path, help="单份章群门禁清单 JSON")
    p.add_argument("--dir", type=Path, help="检查目录内所有 JSON 章群清单")
    p.add_argument("--stage", choices=("structure", "handoff"), default="structure")
    args = p.parse_args()
    if bool(args.file) == bool(args.dir):
        p.error("须且只须指定 --file 或 --dir")
    files = [args.file] if args.file else sorted(args.dir.glob("*.json"))
    if not files:
        p.error("未发现章群 JSON 清单")
    broken = 0
    for f in files:
        errors, warnings = review_manifest(f, stage=args.stage)
        for issue in warnings:
            print(f"⚠ {f}: {issue}")
        for issue in errors:
            print(f"✗ {f}: {issue}")
        if errors:
            broken += 1
        else:
            print(f"✓ {f} [{args.stage}] 通过（结构覆盖；非文学质量结论）")
    if broken:
        print(f"FAIL: {broken}/{len(files)} 份清单未通过")
        return 1
    print(f"PASS: {len(files)} 份结构/资产门禁清单通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
