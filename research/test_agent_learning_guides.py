"""Regression guards for multi-agent installation documentation and skill parity."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GuideSetupTests(unittest.TestCase):
    def test_claude_and_portable_skill_copies_match(self):
        claude = (ROOT / ".claude/skills/verified-agent-learning/SKILL.md").read_text(encoding="utf-8")
        portable = (ROOT / ".agents/skills/verified-agent-learning/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(claude, portable)
        for phrase in ("independently", "retrieval", "plugin", "subagent", "two distinct"):
            self.assertIn(phrase, claude.lower())

    def test_harness_entrypoints_link_to_existing_guides(self):
        paths = ("CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md",
                 ".cursor/rules/verified-feedback.mdc")
        for filename in paths:
            with self.subTest(filename=filename):
                text = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn("AGENTS.md", text)
                self.assertIn("research/agent-learning-user-guide.md", text)

    def test_published_guide_has_all_agents_and_safety_boundary(self):
        guide = (ROOT / "research/agent-learning-user-guide.md").read_text(encoding="utf-8")
        for marker in ("Claude Code", "Codex", "ChatGPT", "Copilot", "Cursor",
                       "Gemini CLI", "OpenCode", "held-out", "independent",
                       "model-weight training", "branch protection"):
            with self.subTest(marker=marker):
                self.assertIn(marker, guide)


if __name__ == "__main__":
    unittest.main()
