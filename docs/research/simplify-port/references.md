# simplify 移植 — 参照資料

## Claude Code 原典

- `/simplify` コマンド（v2.1.154+）
  - URL: https://code.claude.com/docs/en/commands.md
  - 挙動: 変更コードのクリーンアップ機会をレビューし修正を適用。
    4つのレビューエージェントが並列実行:
    1. 既存ヘルパーの再利用
    2. 単純化
    3. 効率化
    4. 適切な抽象レベルの検証
  - v2.1.154 以降、正確性バグは探索しない（`/code-review` に分離）。
  - 引数でパス/PR 参照を指定可能。

- `cdd-code-simplifier` サブエージェント
  - URL: https://github.com/aaddrick/claude-desktop-debian/blob/76a5a21725c3fa738cac061b80053b0745063321/.claude/skills/simplify/SKILL.md
  - Claude Desktop 同梱のスキル定義。
  - `subagent_type: "cdd-code-simplifier"` で Task ツール起動。
  - スコープ: 引数があればそれを、なければ `git diff --name-only main...HEAD` / `git status` で最近変更ファイルを特定。
  - 完了後: 変更をレビュー、変更があればコミット確認、要約を提示。

- Skills / Slash Commands 統合
  - URL: https://code.claude.com/docs/en/skills
  - `.claude/commands/deploy.md` と `.claude/skills/deploy/SKILL.md` は同等。
  - frontmatter: `name`, `description`, `argument-hint`, `disable-model-invocation`, `context: fork`, `agent` 等。
  - `context: fork` でスキルを forked subagent として実行（親履歴にアクセス不可）。

## batch（移植廃止の参考記録）

- URL: https://code.claude.com/docs/en/agents.md
- URL: https://github.com/chauncygu/collection-claude-code-source-code/blob/main/claude-code-source-code/src/skills/bundled/batch.ts
- 挙動: Plan Mode → 5-30 ユニットに分解 → 各ユニットを
  `isolation: "worktree"` + `run_in_background: true` で並列起動 →
  各ワーカーが simplify → テスト → e2e → PR 作成。
- **Devin CLI には `isolation: "worktree"` が存在しない**ことが移植廃止の決定的理由。
  `run_subagent` は `subagent_explore` / `subagent_general` / カスタムプロファイルのみで、
  ファイルシステム隔離オプションなし。

## Devin CLI 側の能力

- URL（ローカル）: `~/.local/share/devin/cli/_versions/2026.8.18/share/devin/docs/`
- `subagents.mdx`: サブエージェントは foreground / background。ネストはデフォルト禁止
  （`max-nesting` frontmatter で opt-in 可）。**サブエージェント内では `run_subagent`/
  `read_subagent` が無効化**され無限再帰を防ぐ。
- `extensibility/skills/creating-skills.mdx`: SKILL.md の frontmatter 仕様。
  - `subagent: true` でデフォルト `subagent_general` プロファイル実行。
  - `agent: <profile>` でカスタムプロファイル指定。
  - `allowed-tools`, `permissions`, `model`, `triggers` 等。
  - **サブエージェント実行スキル内から更にサブエージェント起動は不可**
    →「simplify を subagent 実行 + その中で4並列レビュアー」は不可能。
- `permissions`: `allow` / `deny` / `ask`。スキル permissions はセッション権限に加算。
- ツール名: `read`, `edit`, `grep`, `glob`, `exec`（+ MCP ツール）。

## 本 config の制約

- `config.json`: git push --force / git reset --hard / curl / wget / パッケージinstall 等を ask 指定。
- `rules/auto-mode.md`: allow の wildcard 化を明示的に警告。
  破壊的操作はユーザ明示的指示の時のみ許可。
- `AGENTS.md`: 既存 OSS / ライブラリ composition を推奨、再実装を避ける。
