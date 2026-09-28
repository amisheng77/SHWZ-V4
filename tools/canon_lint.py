#!/usr/bin/env python3
"""canon-lint：SHWZ V4 对齐自动检查（提交前跑：python3 tools/canon_lint.py）"""
import re, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
issues = []

def read(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()

# ── 检查1：D 表连续无重 ──
const = read('docs/00_创作宪法.md')
dnums = [int(m) for m in re.findall(r'^\| D(\d+) \|', const, re.M)]
if len(dnums) != len(set(dnums)):
    issues.append(f'[D表] 重复编号: {sorted({n for n in dnums if dnums.count(n)>1})}')
gaps = [n for n in range(min(dnums), max(dnums)+1) if n not in dnums] if dnums else ['空']
if gaps:
    issues.append(f'[D表] 断号: {gaps}')

# ── 检查2：版本头 D 范围与 D 表一致 ──
ctx = read('SHWZ_Current_Context.md')
declared = re.findall(r'D1—D(\d+)', ctx)
if declared and dnums:
    if int(declared[0]) != max(dnums):
        issues.append(f'[版本头] Current_Context 声明 D1—D{declared[0]}，宪法 D 表实至 D{max(dnums)}')

# ── 检查3：旧名白名单（改名史上的死名零出现） ──
DEAD = ['饕餮', '高离', '公子菖', '桑弧', '刺桑案', '公子关', '曾国', '淮国', '吴国', '执规（',
        'docs/01_世界观架构', 'docs/02_地理', 'docs/03_人物Bible', 'docs/04_POV',
        'docs/05_渤骥菖铎', 'docs/06_总时间线', 'docs/07_章节骨架', 'docs/08_饕餮',
        'docs/09_暗线', 'docs/10_叙事', 'docs/11_一致性', 'docs/12_创作', 'docs/13_开放',
        'docs/14_连续性', 'docs/15_礼制']
SCAN = []
for dp, _, fns in os.walk(DOCS):
    SCAN += [os.path.join(dp, f) for f in fns if f.endswith('.md')]
SCAN += [os.path.join(ROOT, f) for f in ['SHWZ_Current_Context.md', 'SHWZ_Story_State.md', 'HANDOFF.md']]
for path in SCAN:
    if 'registry/terms.md' in path:
        continue  # terms 改名记录合法提及死名
    t = read(os.path.relpath(path, ROOT))
    for ln in t.split('\n'):
        if any(k in ln for k in ['→', '原工作名', '避', '已废止', '原文', '改名', '本名', '换皮', '换名']):
            continue
        for w in DEAD:
            if w in ln:
                issues.append(f'[死名/旧路径] {os.path.relpath(path, ROOT)}: "{w}"')

# ── 检查4：owners.md 覆盖的 owner 文件存在 ──
own = read('docs/registry/owners.md')
for m in re.findall(r'`(docs/[^`]+|SHWZ_[^`]+)`', own):
    if not os.path.exists(os.path.join(ROOT, m)):
        issues.append(f'[owners] 指向不存在的文件: {m}')

# ── 检查5：跨文档引用路径存在 ──
for path in SCAN:
    t = read(os.path.relpath(path, ROOT))
    for m in re.findall(r'`(docs/(?:0[0-9]|registry|arcs)/[^`\s]+\.md)`', t):
        if not os.path.exists(os.path.join(ROOT, m)):
            issues.append(f'[引用] {os.path.relpath(path, ROOT)} → 不存在: {m}')

if issues:
    print(f'canon-lint：{len(issues)} 处违规')
    for i in issues:
        print(' ✗', i)
    sys.exit(1)
print(f'canon-lint：通过（D1—D{max(dnums)}，{len(SCAN)} 文件扫描）')
