import tempfile, json, unittest
from pathlib import Path
from copy import deepcopy
from tools.story_gate import review_manifest

class TestStoryGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        s=self.root/"docs/reports/asset.md"
        s.parent.mkdir(parents=True)
        s.write_text("| F1-A01 | 戏份一 |\n| F1-A02 | 戏份二 |\n",encoding="utf8")
        self.file=self.root/"story.json"
        self.data={"schema_version":"1.0","arc":"CH06—07","asset_source":"docs/reports/asset.md",
          "chapters":[{"id":"CH06","word_target":5500,"chapter_change":"终楠和渤争取留证并付出相应代价",
            "lines":[
              {"id":"A","goal":"终楠争取保存真实的兽伤证据","obstacle":"尸体腐坏而王庭依法要求处置","choice":"向有司提供原始封记及图证","outcome":"获准暂时保存可检验的兽骨","scene":"终楠向城外验兽官展示保存证据"},
              {"id":"B","goal":"渤为朔国争取合法公验机会","obstacle":"王庭担忧疾疫而列国不愿垫钱","choice":"提出限制验兽时间的折中方案","outcome":"使各方同意有条件派员复验","scene":"渤与焦获君共同拜见王庭有司"}],
            "interaction":{"type":"collision","bridge":"终楠的证物保全措施决定渤能在朝廷提出的具体条件"},
            "hook":{"payoff":"两人取得有时间限制的合法留证成果","next_pressure":"北兽继续腐坏导致下一次验痕难度骤增"},
            "asset_ids":["F1-A01","F1-A02"]}],
          "asset_migrations":[
            {"id":"F1-A01","disposition":"keep","chapters":["CH06"],"scene_payoff":"终楠与有司争辩旧日误判造成的真实损失"},
            {"id":"F1-A02","disposition":"rewrite","chapters":["CH06"],"scene_payoff":"关雪在伤兵营实景救治终楠并令他反省"}],
          "author_approval":{"status":"pending","reference":""},
          "literary_review":{"status":"pending","report_path":""}}
    def audit(self,d,stage="structure"):
        self.file.write_text(json.dumps(d,ensure_ascii=False),encoding="utf8")
        return review_manifest(self.file,stage=stage,root=self.root)[0]
    def test_complete_structure(self): self.assertEqual([],self.audit(self.data))
    def test_single_line_fails(self):
        d=deepcopy(self.data);d["chapters"][0]["lines"]=d["chapters"][0]["lines"][:1]
        self.assertTrue(any("至少两条" in e for e in self.audit(d)))
    def test_missing_asset_fails(self):
        d=deepcopy(self.data);d["asset_migrations"].pop()
        self.assertTrue(any("漏迁移" in e for e in self.audit(d)))
    def test_dropped_scene_fails(self):
        d=deepcopy(self.data);d["asset_migrations"][0]["scene_payoff"]="保留"
        self.assertTrue(any("具体场面" in e for e in self.audit(d)))
    def test_no_bridge_fails(self):
        d=deepcopy(self.data);d["chapters"][0]["interaction"]["bridge"]="呼应"
        self.assertTrue(any("桥接" in e for e in self.audit(d)))
    def test_wrong_length_fails(self):
        d=deepcopy(self.data);d["chapters"][0]["word_target"]=3000
        self.assertTrue(any("4000" in e for e in self.audit(d)))
    def test_handoff_needs_signoff(self):
        self.assertTrue(any("作者" in e for e in self.audit(self.data,"handoff")))
        self.assertTrue(any("文学" in e for e in self.audit(self.data,"handoff")))
    def test_unapproved_deletion_fails_handoff(self):
        d=deepcopy(self.data);d["asset_migrations"][1]={"id":"F1-A02","disposition":"propose_delete","reason":"已提出删去旧人物场景但尚待作者裁决"}
        d["chapters"][0]["asset_ids"]=["F1-A01"]
        self.assertTrue(any("作者未明确批准删除" in e for e in self.audit(d,"handoff")))
if __name__=="__main__": unittest.main()
