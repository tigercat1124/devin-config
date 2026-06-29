# 移植計画書: Claude Code `simplify` → Devin CLI

- 作成日: 2026-06-29
- 決定記録: ADR-0002 (`docs/adr/0002-port-simplify-from-claude-code.md`)
- 調査記録: `docs/research/simplify-port/`

## 1. 背景

Claude Code 同梱の `simplify` / `batch` スキルを Devin CLI 設定
（`~/.config/devin/`）に移植したい、という要件から始まった。
dig スキルによる深掘りの結果、`batch` は Devin の能力外（worktree 隔離なし）
として廃止し、`simplify` のみを移植する方針に確定した。

## 2. 移植対象

| スキル | 移植 | 理由 |
|--------|------|------|
| `simplify` | **する** | Devin で忠実に再現可能 |
| `batch` | **しない** | `isolation: "worktree"` が Devin に存在せず、並列隔離が不可。順次退化は `dig` + 手動計画で代替可能 |

## 3. `simplify` 設計仕様

### 3.1 全体構造

```
/simplify [target]
    │
    ├─ (1) ルート: レビュー対象ファイル群を特定
    │      git diff --name-only main...HEAD（デフォルト）
    │      引数 <target> があればそちらを優先
    │
    ├─ (2) ルート: 4つの read-only バックグラウンドサブエージェントを
    │      1メッセージブロック内で並列起動（run_subagent x4）
    │      - reviewer-reuse:        既存ヘルパーの再利用機会
    │      - reviewer-simplify:     単純化機会
    │      - reviewer-efficiency:   効率化機会
    │      - reviewer-abstraction:  適切な抽象レベルの検証
    │      ※ 正確性バグは探索しない（Claude Code v2.1.154+ 準拠）
    │
    ├─ (3) ルート: 4レビュアーの指摘を統合・仲裁して1度だけ適用
    │      - 指摘対立はルートが仲裁して一方を採用
    │      - 同一ファイルの相反指摘は統合して安全側に倒す
    │
    ├─ (4) ルート: 適用後、ビルド/テストが壊れていないか軽量確認
    │      （プロジェクトの検証コマンドがあれば実行、なければ省略）
    │
    ├─ (5) ルート: 自動コミット
    │      メッセージ: "simplify: <要約>"
    │      push / PR は作成しない（ユーザ任せ）
    │
    └─ (6) ルート: 最終報告
           適用内容・コミットハッシュ・破壊の有無を提示
```

### 3.2 設計の根拠（ネスト制約対応）

Devin のサブエージェント内では `run_subagent` / `read_subagent` が無効化
される（無限再帰防止）。そのため「simplify を subagent 実行 + その中で
4並列レビュアー」は不可能。ルートインラインで起動し、4レビュアーを
バックグラウンドサブエージェントとして並列起動する構造が唯一の忠実再現経路。

### 3.3 失敗モード

| 状況 | 扱い | 設計意図 |
|------|------|----------|
| diff なし | 即時終了（「クリーンアップ対象なし」） | 無駄な作業を回避 |
| 4レビュアーの指摘対立 | ルートが仲裁して一方を採用 | 自動性優先 |
| 適用後にビルド/テスト破壊 | コミットを残置＋報告 | 成果を残す、ユーザが revert しやすい状態 |

### 3.4 権限と安全層

- レビュアー（4サブエージェント）: `subagent_explore` プロファイル（read-only）。
  `read` / `grep` / `glob` / `web_search` のみ。ファイル編集・exec なし。
- 適用・コミット: ルートエージェントが `edit` / `exec(git ...)` を使用。
  `git commit` は `config.json` で許可、`git push` は `ask` 指定のまま。
- **グローバル `config.json` の `allow` / `ask` / `deny` は一切変更しない。**
  `rules/auto-mode.md` の「allow wildcard 化回避」と整合。

## 4. 配置場所

```
~/.config/devin/
└── skills/
    └── simplify/
        └── SKILL.md      ← 新規作成
```

既存の `adr-create/` / `dig/` と並ぶ。グローバル配置により全プロジェクトで
`/simplify` を実行可能。

## 5. SKILL.md フロントマター（予定）

```yaml
---
name: simplify
description: Review changed code for cleanup opportunities and apply fixes. Four parallel reviewers cover reuse, simplification, efficiency, and abstraction-level. Does not hunt for correctness bugs.
argument-hint: "[target]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - edit
  - grep
  - glob
  - exec
  - run_subagent
  - read_subagent
  - todo_write
permissions:
  allow:
    - Exec(git diff)
    - Exec(git status)
    - Exec(git log)
    - Exec(git commit)
  ask:
    - Exec(git push)
---
```

※ `allowed-tools` に `run_subagent` / `read_subagent` を含めることで
ルートから4レビュアーを起動可能にする。`git push` は `ask` のまま維持。

## 6. 実装ステップ

1. **ADR-0002 確定** — 既に作成済み（`docs/adr/0002-...`）。
2. **`skills/simplify/SKILL.md` 作成** — 上記設計で書き下ろし。
   - プロンプト本文に (1)〜(6) の手順・4レビュアーの役割・仲裁ロジック・
     失敗モード処理を明記。
   - `// ADR-0002` 参照コメントを含める。
3. **README 更新** — スキル一覧に `simplify/` を追記。
   （`kiro-*` は既に削除済みのため、現在の `adr-create` / `dig` に並べる）
4. **実地検証** — 既存リポジトリで `/simplify` を実行:
   - 4レビュアーが並列起動するか
   - 指摘が統合・適用されるか
   - 自動コミットされるか
   - push が要求されないか
5. **外側ループ改善** — 運用しながら仲裁ロジックの精度を見て SKILL.md を改訂。

## 7. 検証計画

| 項目 | 方法 | 合否基準 |
|------|------|----------|
| スキル読み込み | Devin 起動後 `/simplify` が補完される | 補完候補に出る |
| 4レビュアー起動 | 変更のあるリポジトリで `/simplify` 実行 | 4つの bg サブエージェントが並列起動ログに現れる |
| 適用 | レビュアー指摘に基づく edit が実行される | ワーキングツリーに変更が入る |
| コミット | 自動コミットされる | `git log` に `simplify: ...` が追加される |
| push 非実行 | push が走らない | リモートに変更がない、`ask` プロンプトも出ない |
| diff なし | クリーンな状態で `/simplify` | 「クリーンアップ対象なし」で即終了 |
| ネスト安全 | `/simplify` 実行中に `/simplify` 再起 | サブエージェント内では inline 化され再帰しない |

## 8. 廃止したものと代替手段

| 廃止 | 代替 |
|------|------|
| `batch`（並列大規模変更） | `dig` で前提検証 → 手動でユニット分解 → 順次 `/simplify` 適用 |
| `decompose-execute`（縮退版） | 同上。独立スキルとしての保守対象を増やさない |

## 9. 残リスク

- 4レビュアーの指摘対立の仲裁がプロンプト依存。確定アルゴリズムでないため、
  運用しながら SKILL.md の仲裁ロジックを磨く必要がある（外側ループ）。
- 適用後ビルド破壊を残置する設計のため、ユーザが最終報告を見落とすと
  壊れた状態が残る。コミットメッセージの `simplify:` プレフィックスと
  最終報告での可視化で緩和する。

## 10. 関連文書

- ADR: `docs/adr/0002-port-simplify-from-claude-code.md`
- 調査: `docs/research/simplify-port/references.md`,
  `docs/research/simplify-port/investigation-log.md`
- 規約: `AGENTS.md`, `rules/auto-mode.md`, `rules/harness-engineering.md`
