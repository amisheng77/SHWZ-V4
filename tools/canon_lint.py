#!/usr/bin/env python3
"""canon-lint：SHWZ V4 对齐自动检查（提交前跑：python3 tools/canon_lint.py）"""
import re, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
issues = []
warns = []

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

# ── 检查6：json 路径一致性（copilot.json 引用路径存在；chapters.json 各章 path 字段存在） ──
def _exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))

cfg = None
try:
    cfg = json.loads(read('copilot.json'))
except Exception as e:
    warns.append(f'[copilot.json] 解析失败: {e}')
cdb = None
try:
    cdb = json.loads(read('state/chapters.json'))
except Exception as e:
    warns.append(f'[chapters.json] 解析失败: {e}')

if cfg:
    _refs = [('docs_map.' + k, v) for k, v in cfg.get('docs_map', {}).items()]
    _refs += [('registry.' + k, v) for k, v in cfg.get('registry', {}).items()]
    if isinstance(cfg.get('open_threads'), str):
        _refs.append(('open_threads', cfg['open_threads']))
    for key, rel in _refs:
        if isinstance(rel, str) and not _exists(rel):
            issues.append(f'[copilot.json] {key} → 不存在: {rel}')

chs = {}
if cdb is not None:
    chs = {k: v for k, v in cdb.items() if re.match(r'^CH\d+$', k) and isinstance(v, dict)}

def _walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            _walk(v, f'{path}.{k}' if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            _walk(v, f'{path}[{i}]')
    elif isinstance(o, str) and re.match(r'^(work|drafts|docs|state|research|archive)/.+\.(md|txt)$', o):
        if not _exists(o):
            issues.append(f'[chapters.json] {path} → 不存在: {o}')

_walk(cdb)
if cfg and cdb is not None:
    for pov, target in cfg.get('pov_anchors', {}).items():
        if isinstance(target, str) and target not in chs:
            issues.append(f'[pov_anchors] {pov} → {target} 不在 chapters.json')
if cfg or cdb is not None:
    print(f' ✓ [json] 路径扫描：docs_map/registry/open_threads + chapters.json {len(chs)} 章 path 字段')

# ── 检查7：占比锁（04 §0.5 爆点节拍表 vs 总章数/chapters.json 实际章号） ──
skel = read('docs/04_章节骨架.md')
m05 = re.search(r'## 0\.5[^\n]*\n(.*?)(?=\n## )', skel, re.S)
mtot = re.search(r'总章数[^\d]{0,8}(\d+)', skel)
N = int(mtot.group(1)) if mtot else max((int(m) for m in re.findall(r'CH(\d+)', skel)), default=0)
rows05 = []
if not m05:
    warns.append('[占比锁] §0.5 格式无法解析（找不到小节）')
else:
    for ln in m05.group(1).split('\n'):
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        nums = re.findall(r'CH(\d+)', cells[0]) if cells else []
        if len(cells) >= 4 and nums:
            rows05.append((int(nums[0]), cells[1],
                           [float(x) for x in re.findall(r'\d+(?:\.\d+)?', cells[3].replace('**', ''))]))
    if not rows05:
        warns.append('[占比锁] §0.5 格式无法解析（无节拍行）')
if rows05 and N:
    over = [k for k in chs if int(k[2:]) > N]
    if over:
        issues.append(f'[占比锁] chapters.json 章号超出骨架总章数 {N}: {sorted(over)}')
    bad = 0
    for start, ev, pct in rows05:
        comp = start / N * 100
        if len(pct) == 1 and comp > pct[0] + 1.0:
            issues.append(f'[占比锁] {ev}: CH{start}/{N}＝{comp:.1f}% 晚于表标 {pct[0]:g}%')
            bad += 1
        elif len(pct) >= 2 and not pct[0] - 1.0 <= comp <= pct[-1] + 1.0:
            issues.append(f'[占比锁] {ev}: CH{start}/{N}＝{comp:.1f}% 不在表标 {pct[0]:g}—{pct[-1]:g}%')
            bad += 1
    if not bad:
        fj = next((r for r in rows05 if '首捷' in r[1] and r[2]), None)
        extra = f'，首捷 CH{fj[0]}＝{fj[0]/N*100:.1f}% ≤ 表标 {fj[2][0]:g}%' if fj else ''
        print(f' ✓ [占比锁] 总章 {N}，{len(rows05)} 行节拍断言全过{extra}')

# ── 检查8：五牌干燥段（04 §0.6 分布图 vs 单元表；连续无魔单元 >5 告警） ──
m06 = re.search(r'## 0\.6[^\n]*\n(.*?)(?=\n## )', skel, re.S)
magic = set()
if not m06:
    warns.append('[五牌] §0.6 格式无法解析（找不到小节）')
else:
    for ln in m06.group(1).split('\n'):
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if len(cells) >= 2 and 'CH' in cells[1]:
            for a, b in re.findall(r'CH(\d+)(?:[—–\-](\d+))?', cells[1]):
                magic.update(range(int(a), int(b or a) + 1))
units = [(int(u[1:]), int(a), int(b or a))
         for u, a, b in re.findall(r'^## (U\d+)｜[^｜]+｜CH(\d+)(?:[—–\-](\d+))?｜', skel, re.M)]
if m06 and not units:
    warns.append('[五牌] 单元表格式无法解析（无 U 行）')
elif magic:
    runs = [[]]
    for u, a, b in sorted(units):
        if any(c in magic for c in range(a, b + 1)):
            runs.append([])
        else:
            runs[-1].append(f'U{u:02d}(CH{a}—{b})' if b != a else f'U{u:02d}(CH{a})')
    worst = max(runs, key=len)
    if len(worst) > 5:
        warns.append(f'[五牌] 连续无魔单元 {len(worst)} >5：{"、".join(worst)}')
    else:
        print(f' ✓ [五牌] {len(units)} 单元对照分布图，最长干燥段 {len(worst)} 单元 ≤5')

# ── 检查9：POV 序列（前 20 章连续同 POV ≤2）＋中心英雄首现 ≤CH4 ──
seq9 = sorted(((int(k[2:]), v.get('pov') or '') for k, v in chs.items()), key=lambda t: t[0])
pov20 = [(n, pv) for n, pv in seq9 if n <= 20]
runs9 = []
for n, pv in pov20:
    if runs9 and runs9[-1][0] == pv:
        runs9[-1][1].append(n)
    else:
        runs9.append((pv, [n]))
viol9 = [(pv, ns) for pv, ns in runs9 if pv and len(ns) > 2]
for pv, ns in viol9:
    issues.append(f'[POV] 前20章 {pv} 连续 {len(ns)} 章（CH{ns[0]:03d}—CH{ns[-1]:03d}）>2')
if pov20 and not viol9:
    print(f' ✓ [POV] 前20章连续同 POV ≤2（已登记 {len(pov20)} 章）')

hero = cfg.get('central_hero') if isinstance(cfg, dict) else None
if not hero:
    mh = None
    for src in ('docs/00_创作宪法.md', 'docs/04_章节骨架.md', 'SHWZ_Current_Context.md'):
        mh = re.search(r'中心英雄\*{0,2}\s*[：:＝]\s*\*{0,2}([^\s，。；、（）()｜|*]+)', read(src))
        if mh:
            break
    hero = mh.group(1) if mh else None
if not hero:
    warns.append('[中心英雄] 未配置（copilot.json central_hero 缺失且 canon 无「中心英雄＝X」标注），跳过首现检查')
else:
    unit_pov = [(int(a), b or a, p) for a, b, p in
                re.findall(r'^## U\d+｜[^｜]+｜CH(\d+)(?:[—–\-](\d+))?｜POV ([^｜]+)', skel, re.M)]
    first = next((n for n, pv in seq9 if pv and (hero in pv or pv in hero)), None)
    first_s = next((a for a, b, p in unit_pov if hero in p or p in hero), None)
    first = min([x for x in (first, first_s) if x is not None], default=None)
    if first is None:
        warns.append(f'[中心英雄] {hero} 在骨架与 chapters.json 均无 POV 首现记录')
    elif first > 4:
        issues.append(f'[中心英雄] {hero} 首现 CH{first:03d} 晚于 CH4')
    else:
        print(f' ✓ [中心英雄] {hero} 首现 CH{first:03d} ≤ CH4')

if warns:
    print(f'告警 {len(warns)} 处（不阻断）:')
    for w in warns:
        print(' ⚠', w)
if issues:
    print(f'canon-lint：{len(issues)} 处违规，{len(warns)} 处告警')
    for i in issues:
        print(' ✗', i)
    sys.exit(1)
print(f'canon-lint：通过（D1—D{max(dnums)}，{len(SCAN)} 文件扫描；json/占比锁/五牌/POV ✓）')
