# simplify 移植 — 調査ログ

## 2026-06-29 — dig スキルによる深掘り

### Round 1: batch の前提検証
- worktree 隔離: Devin に `isolation: "worktree"` なし → 順次実行を選択。
- 権限モデル: グローバル allow 拡張を選んだが、順次なら不要と判明。
- 移植順序: simplify 先 → batch 後。

### Round 2: Round 1 の矛盾解消
- 順次実行の形: バックグラウンドSBを1つずつ。
- 権限: batch-worker プロファイル scoped allow に変更（グローバル拡張なし）。
- batch 存在意義: 並列を謳わない `decompose-execute` に縮退再設計を選択。

### Round 3: simplify 構造
- ネスト禁止制約（サブエージェント内で run_subagent 無効）を発見。
- 構造: ルートインライン + 4-bg レビュアー（read-only 並列）→ ルート統合適用。
- レビュー対象: `git diff main...HEAD` デフォルト + 引数上書き。
- 適用後: 自動コミット。

### Round 4: 方向転換後の simplify 残課題
- **方向転換**: batch/decompose-execute は廃止、simplify のみに縮小。
  - 理由: worktree 隔離が解決されず、batch の核心価値（並列高速化）が
    Devin で再現不能。順次版は dig/plan ワークフローで代替可能。
- 出力境界: コミットのみ・push はユーザ任せ（auto-mode と整合）。
- 失敗モード: 自動性優先（diff なし→即終了 / 対立→ルート仲裁 / 破壊→コミット残置＋報告）。
- 配置: グローバル `~/.config/devin/skills/simplify/SKILL.md`。

### 結論
simplify 単体は Devin で忠実に移植可能。batch は Devin の能力外のため移植廃止。
