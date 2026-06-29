# ADR-0002: Claude Code `simplify` スキルの Devin CLI 移植（`batch` は廃止）

## Status

Accepted

## Context

Claude Code に同梱される `simplify` と `batch` の2スキルを Devin CLI 設定
（`~/.config/devin/`）に移植したいという要件があった。

- `simplify`: 変更コードのクリーンアップ機会を4視点（既存ヘルパー再利用・
  単純化・効率化・抽象レベル）で並列レビューし、修正を適用する。
- `batch`: 大規模変更を5-30ユニットに分解し、各ユニットを独立 git worktree
  で並列実行、各々 PR を作成する。

dig スキルで深掘りした結果、以下の決定的制約を発見した。

1. **Devin CLI の `run_subagent` に `isolation: "worktree"` オプションがない**。
   Claude Code の `batch` は各ワーカーを worktree 隔離することが前提であり、
   Devin では並列ワーカーが同一チェックアウトを共有する。順次実行に退化
   すると並列高速化という `batch` の核心価値が失われる。
2. **Devin のサブエージェント内では `run_subagent` / `read_subagent` が無効化
   される**（無限再帰防止）。これは `simplify` をサブエージェント実行しつつ
   その中で4並列レビュアーを起動する設計を排除する。
3. **バックグラウンドサブエージェントは未承認ツールを自動拒否する**。
   `batch` ワーカーが git push / gh pr create / npm test 等を実行するには
   事前 allow が必要だが、`rules/auto-mode.md` は allow の wildcard 化を
   明示的に警告している。

詳細な調査経緯は `docs/research/simplify-port/investigation-log.md` および
`docs/research/simplify-port/references.md` を参照。

## Decision

1. **`simplify` のみを移植する。** `batch` は Devin CLI の能力外のため移植を廃止する。
2. **`simplify` の構造は「ルートインライン + 4バックグラウンドレビュアー」
   とする。** ルートエージェントがインラインで起動し、4つの read-only
   バックグラウンドサブエージェントを並列起動して4視点をレビュー、結果を
   ルートが統合して1度だけ適用する。ネスト禁止制約に抵触しない。
3. **レビュー対象は `git diff main...HEAD` をデフォルトとし、引数で上書き可能。**
   Claude Code 原典に忠実。
4. **適用後は自動的にローカルコミットする。** push / PR 作成はユーザに委ねる。
   `config.json` が git push を `ask` 指定しており、`rules/auto-mode.md` と整合する。
5. **失敗モードは自動性優先とする。** diff なしは即時終了、4レビュアーの
   指摘対立はルートが仲裁、適用後のビルド/テスト破壊はコミットを残置し報告する。
6. **配置場所は `~/.config/devin/skills/simplify/SKILL.md`（グローバル）。**
   既存の `adr-create` / `dig` と並ぶ。

## Rationale

- **`batch` 廃止**: worktree 隔離なしに並列実行すると git index 競合・コミット
  競合・独立マージ可能性の喪失が避けられない。順次実行に退化すると `dig` +
  手動計画で代替可能であり、独立スキルとして維持する価値が残らない。
  `AGENTS.md` の「既存 OSS / ライブラリ composition を推奨、再実装を避ける」
  原則にも合致する。
- **ルートインライン構造**: サブエージェント内で `run_subagent` が使えない
  ため、「simplify を subagent 実行 + 4並列レビュアー」は不可能。ルートで
  起動すれば4レビュアーを並列起動でき、適用を1箇所に集約して同時編集の
  衝突を防げる。
- **コミットのみ・push はユーザ任せ**: `rules/auto-mode.md` の
  「Bypass review / affect others」カテゴリと整合。git push は `ask` 指定の
  まま維持でき、安全層を後退させない。
- **自動性優先の失敗モード**: ユーザ承認を都度挟むと `simplify` の反復速度が
  落ちる。破壊を残置するリスクはコミットメッセージと報告で可視化し、
  ユーザが `git revert` しやすい状態を保つ。

## Alternatives Considered

- **`batch` を順次版 `decompose-execute` として縮退移植**: Round 2 で一時選択
  したが、並列高速化を失うと `dig` + 手動計画で代替可能であり、保守対象を
  増やすだけと判断して廃止。
- **`simplify` を単一サブエージェントで4視点順次レビュー**: 構造は単純だが
  Claude Code 原典の4並列レビューから逸脱し、コンテキスト分離の恩恵も
  ルートインライン+bg で得られるため却下。
- **`simplify` をルートインライン単一パスで実行**: 最単純だが4視点の並列
  コンテキスト分離を失い、Claude Code 設計から大きく逸脱するため却下。
- **適用のみ・コミットしない**: 最安全だが `simplify` を繰り返し呼ぶ際に
  ワーキングツリーが汚染しやすく、ユーザ管理負荷が増えるため却下。
- **グローバル allow に git push / gh 等を追加**: `rules/auto-mode.md` が
  明示的に警告する wildcard 化に該当し、全プロジェクト全セッションで
  破壊的操作が自動許可されるため却下。

## Consequences

**ポジティブ**
- `simplify` が全プロジェクトで利用可能になり、変更のクリーンアップが
  構造化・反復可能になる。
- `batch` 廃止により、Devin の能力外の複雑な協調ロジックを保守しなくて済む。
- 安全層（auto-mode / config.json）を一切後退させない。

**ネガティブ / リスク**
- 大規模並列変更の自動化手段が手元になくなる。必要時は `dig` + 手動で
  ユニット分解し、順次 `simplify` を適用する運用になる。
- 4レビュアーの指摘対立の仲裁がプロンプト依存であり、確定アルゴリズムで
  ない。運用しながら SKILL.md の仲裁ロジックを磨く必要がある。
- 適用後ビルド破壊を残置する設計のため、ユーザが報告を見落とすと壊れた
  状態が残る。コミットメッセージと最終報告での可視化で緩和する。

**フォローアップ**
- 実装後、既存リポジトリで `/simplify` を実行し4レビュアー起動〜自動
  コミットまでを検証する。
- 仲裁ロジックの精度を見て SKILL.md を改訂する（外側ループ改善）。

## Related

- 調査記録: `docs/research/simplify-port/references.md`,
  `docs/research/simplify-port/investigation-log.md`
- 移植計画書: `docs/plan/simplify-port.md`
- 実装: `skills/simplify/SKILL.md`
- 関連規約: `AGENTS.md`（Product & Implementation Stance, Pseudo Auto-Mode）,
  `rules/auto-mode.md`, `rules/harness-engineering.md`
