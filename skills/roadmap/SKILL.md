---
name: roadmap
description: Create phased roadmap documents in docs/roadmap/ — a shared spec plus per-target roadmaps with checkboxes and known constraints
argument-hint: "<target-or-topic>"
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - glob
  - write
  - edit
permissions:
  allow:
    - Read(docs/roadmap/**)
    - Write(docs/roadmap/**)
---

Create roadmap documents in `docs/roadmap/` for multi-step work, comparisons,
PoCs, or feature rollouts.

## When to use

- The user asks for a roadmap / ロードマップ / plan for a feature, PoC, or
  multi-target comparison.
- Work spans multiple targets (stacks, modules, services) that share a spec.
- A task has clear phases (scaffold → implementation → verification → report).

Do NOT use for single-step tasks or ephemeral plans — a todo list is enough
there. Roadmaps are persistent documents, not session state.

## Critical rule: verification before check-off

**`[x]` には必ず検証を要する。** 実装コードを書いただけでは `[x]` にしない。

| 状態 | マーカー | 意味 |
|------|----------|------|
| 未着手 | `[ ]` | まだ書いていない |
| 実装済み（未検証） | `[/]` | コードはあるが、動作確認・テスト未実施 |
| 検証済み | `[x]` | テスト・ビルド・手動確認で動作を確認済み |

- 検証方法を各項目に明記する（例: `[x] xxx — `go test` 通過` / `[x] xxx — `wails3 build` 成功`）
- 検証していない項目は `[/]` に留める。後から検証して `[x]` に昇格させる
- 「実装したから動くはず」という根拠のない `[x]` は **禁止**

## Steps

1. **List existing roadmaps** with `glob docs/roadmap/*.md`.
2. **Create or update the shared spec** at `docs/roadmap/00-common-spec.md`
   when the work involves multiple targets or a unified requirement
   (unified UI items, shared mock data, common ports/conventions,
   comparison criteria). Single-target work can skip this file.
3. **Create one file per target** at `docs/roadmap/<kebab-target>.md`.
4. **Cross-link**: reference related ADRs (`docs/adr/`) and research notes
   (`docs/research/`). Roadmaps record *what and when*; ADRs record *why*.
5. **Keep them living**: mark `- [x]` only after verification. Update the
   shared spec first when requirements change, then sync the per-target files.

## Per-target template

```markdown
# ロードマップ — <target-name>

参照: `docs/roadmap/00-common-spec.md`（共通仕様・比較観点）
位置づけ: <このターゲットの役割 / 対応 ADR>

## 状態サマリー

- 検証済み: X 項目 / 全 N 項目
- 実装済み（未検証）: Y 項目
- 未着手: Z 項目
- ブロッカー: <あれば記載>

## Phase 0: スキャフォールド

- [x] 完了済み項目（検証方法: <コマンド or 手順>）
- [ ] 未着手項目

## Phase 1: <主実装>

- [ ] 項目（曖昧さを残さず、検証可能な粒度で）

## Phase N: 比較・レポート / 仕上げ

- [ ] 計測項目・記録先（`docs/research/<name>/notes.md` 等）

## 既知の制約

- 要件とトレードオフになる点、依存の注意点を正直に書く
```

## Guidelines

- **Phase 0 は完了状態から書き始める**: 既に済んでいる作業は `[x]` で
  記録し、現在地を一目で分かるようにする。**ただし検証済みのものだけ**。
- **各項目は検証可能な粒度に**: 「実装する」ではなく「〜を hx_get で
  部分更新する」程度まで落とす。
- **既知の制約セクションを必ず設ける**: 要件と衝突する点
  （例: デザイン統一 vs フレームワーク標準スタイル）を隠さない。
- **比較系では共通仕様を正とする**: モックデータ・画面項目・ポート等は
  `00-common-spec.md` に集約し、各ファイルから参照させる。変更時は
  共通仕様を先に更新する運用ルールを明記する。
- **検証は書きながら行う**: 実装してから後でまとめて検証するのではなく、
  各項目を検証してから次に進む。
- 言語はプロジェクトのドキュメント規約に従う（日本語プロジェクトなら
  日本語で書く）。
- **検証方法を必ず併記する**: `[x] xxx — `mise x -- go test ./...` 通過` のように、
  何を実行して確認したかを残す。

## 禁止事項

- 「実装したから動くはず」という根拠のない `[x]` マーク
- テスト・ビルド・動作確認をしていない項目を `[x]` にすること
- 検証せずに Phase を「完了」と見なすこと
- ロードマップだけ更新して実装や検証を後回しにすること
