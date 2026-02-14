
# Alfred Project Rulebook

## TL;DR
- Sergey Bar is the sole project lead and approves all changes.
- AI-generated code must include a comment with model, logic, reason, and context.
- All major changes are documented in the changelog and code_review folder.
- Security: Review dependencies, never commit credentials.
- Use the most advanced AI model for critical logic; see model guidance below.

## Project Lead
- Sergey Bar: final decision maker for all project aspects.

## AI Usage Policy
- Add an AI-generated comment to any code, doc, or config changed by AI:
  - Model name (e.g., GitHub Copilot, GPT-4.1)
  - Logic/reasoning for the change
  - Why and root cause
  - Context for future improvements
  - Suggest a better model if needed
- Manual edits by Sergey Bar do not require this comment.

## Code Review & Documentation
- Document all major changes in changelog and code_review.
- Indicate if AI was used for any part of the change.

## Contribution Policy
- Only Sergey Bar can approve/merge to main branch.
- External contributions require explicit review.

## Security & Compliance
- Review all dependencies for security and license compliance.
- Never commit sensitive data (API keys, credentials).

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Implements error handling for API failures as recommended in code review.
// Why: Previous implementation did not handle network errors, causing user confusion.
// Root Cause: Missing try/catch around fetch call; error messages were not user-friendly.
// Context: This API is called from the VS Code extension status bar and must always show a clear error state.
// Model Suitability: For complex error handling patterns, GPT-4 Turbo or Claude 3 may provide more robust suggestions due to better reasoning capabilities.



## for sergey's use only dont read this ##
## AI Model Guidance

### Free Models (0x Cost)
- **GPT-4.1**: General code generation, refactoring, documentation, code review. Use for most tasks where cost is a concern.
- **GPT-4o**: Fast, multimodal, good for quick prototyping and UI/UX tasks.
- **GPT-5 mini**: Lightweight, ideal for simple code snippets and boilerplate.
- **Grok Code Fast 1**: Rapid code suggestions, best for brainstorming and quick fixes.

### Discounted Models (0.33x Cost)
- **Claude Haiku 4.5**: Fast summarization, policy writing, and explanations. Use for documentation and quick analysis.
- **Gemini 3 Flash (Preview)**: Real-time code search, large context, cross-file analysis. Use for fast codebase navigation.
- **GPT-5.1-Codex-Mini (Preview)**: Efficient for small code generation and refactoring tasks.

### Standard Models (1x Cost)
- **Claude Sonnet 4 / 4.5**: Balanced performance, best for production code, architecture, and complex reasoning.
- **Gemini 2.5 Pro / 3 Pro (Preview)**: Advanced code search, pattern recognition, and multi-file refactoring.
- **GPT-5 (Warning icon displayed)**: Use for critical business logic, advanced architecture, and high-stakes code review.
- **GPT-5-Codex (Preview) (Warning icon displayed)**: Best for advanced API integration and complex refactoring.
- **GPT-5.1 / GPT-5.1-Codex / GPT-5.1-Codex-Max**: Use for large-scale codebase analysis, documentation, and production deployments.
- **GPT-5.2**: Latest model, use for cutting-edge features and high accuracy requirements.

### Premium Models (3x Cost)
- **Claude Opus 4.5**: Highest accuracy, best for mission-critical code, compliance, and advanced reasoning. Use when quality is paramount and cost is justified.

---

- Prefer free or discounted models for routine tasks and prototyping.
- Use standard models for production code, architecture, and complex workflows.
- Use premium models for compliance, mission-critical, or high-stakes scenarios.

---
## for sergey's use only dont read this ##

### Appendix: Example AI-Generated Comment
```js
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Implements error handling for API failures as recommended in code review.
// Why: Previous implementation did not handle network errors, causing user confusion.
// Root Cause: Missing try/catch around fetch call; error messages were not user-friendly.
// Context: This API is called from the VS Code extension status bar and must always show a clear error state.
// Model Suitability: For complex error handling patterns, GPT-4 Turbo or Claude 3 may provide more robust suggestions due to better reasoning capabilities.
```
