import unittest

from app.services import ollama_service


class OllamaServiceTests(unittest.TestCase):
    def test_build_prompt_expands_korean_language_code(self) -> None:
        prompt = ollama_service._build_prompt(
            theme="late night memory",
            language="ko",
            style="ballad",
            instruction="short chorus",
            version_count=1,
        )

        self.assertIn("Target language: Korean only", prompt)
        self.assertIn("Write every lyric line in Korean", prompt)
        self.assertIn("Do not reuse or continue any previous draft", prompt)

    def test_build_prompt_expands_mixed_language_code(self) -> None:
        prompt = ollama_service._build_prompt(
            theme="late night memory",
            language="mixed",
            style="ballad",
            instruction="short chorus",
            version_count=1,
        )

        self.assertIn("Target language: Korean-English mixed", prompt)

    def test_build_messages_includes_system_and_user_instructions(self) -> None:
        messages = ollama_service._build_messages(
            theme="rainy night",
            language="ko",
            style="ballad",
            instruction="short chorus",
            version_count=1,
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Return only the lyric text", messages[0]["content"])
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("Do not reuse or continue any previous draft", messages[1]["content"])
        self.assertIn("Target language: Korean only", messages[1]["content"])

    def test_clean_model_content_removes_thinking_and_markdown_fence(self) -> None:
        content = """<think>
Internal reasoning that should not be shown.
</think>

```markdown
# 비가 내리는 밤

**[Chorus]**
비가 내리는 밤
```
"""

        cleaned = ollama_service._clean_model_content(content)

        self.assertNotIn("<think>", cleaned)
        self.assertNotIn("```", cleaned)
        self.assertEqual(cleaned, "# 비가 내리는 밤\n\n**[Chorus]**\n비가 내리는 밤")


if __name__ == "__main__":
    unittest.main()
