# CSFW RPG デモ

[English version here](README.md)

**C-S Framework (CSFW)** の実証用プロジェクトです。

CSFW は、Concept（コンセプト）とSynchronization（同期ルール）によるイベント駆動アーキテクチャを提供するPythonフレームワークです。このリポジトリでは、CSFWを使用してレトロスタイルのRPGゲームを構築しています。

👉 **CSFW本体**: [https://github.com/shuntacurosu/cs-framework](https://github.com/shuntacurosu/cs-framework)

## スクリーンショット

| フィールド | バトル |
|:---:|:---:|
| ![Village](refs/village.png) | ![Battle](refs/battle.png) |

## 技術スタック

- **フレームワーク**: [C-S Framework (CSFW)](https://github.com/shuntacurosu/cs-framework)
- **グラフィック**: [Pyxel](https://github.com/kitao/pyxel) (レトロゲームエンジン)
- **言語**: Python 3.10+

## アーキテクチャ

このプロジェクトはCSFWのConcept-Synchronizationパターンに従っています:

- **Concepts** (`src/concepts/`): ゲームロジックをカプセル化
  - `GameLoop`: メインループ・描画管理
  - `Player`: プレイヤー状態・移動
  - `MapSystem`: マップ読み込み・衝突判定・エンカウント
  - `BattleSystem`: ターン制バトル
  - `NpcSystem`: NPC管理・AI移動
  - `MenuSystem`: メニューUI
  - など

- **Synchronizations** (`src/sync/rules.yaml`): Concept間の連携ルール
  - イベント駆動で疎結合を実現
  - YAMLで宣言的に定義

## セットアップ

```bash
# 依存関係インストール
pip install cs-framework pyxel pyyaml pydantic

# 実行
python src/main.py
```

## 操作方法

| キー | アクション |
|------|--------|
| 矢印キー | 移動 |
| Z | 決定 / 話しかける |
| X | キャンセル / メニュー |

## ライセンス

MIT License
