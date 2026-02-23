# Python Todo / Diary App

## 概要
Flask ベースの個人日記アプリ（シングルユーザー、ローカル利用）。
MySQL + JSON ファイルから SQLite への移行リファクタリング中。
フェーズ: MVP（プロトタイプ品質は許容。セキュリティ修正は必須スコープ）。

## スタック
- Python 3.x, Flask 3.x
- データベース: SQLite（MySQL からの移行中）
- テンプレート: Jinja2
- フロントエンドビルドステップなし

## 主要コマンド
venvにactivateしていることを確認してから実行
```bash
python run.py                         # 開発サーバー起動
pip install -r requirements.txt       # 依存インストール
pytest                                # テスト実行
pytest --cov=app tests/               # カバレッジ付きテスト
```

## 目標ファイル構成（リファクタリング後）

本番環境を意識し、テスト駆動開発がしやすいレイヤード構成に移行する。

```
app/
├── __init__.py          # Flask app factory (create_app())
├── config.py            # 環境別設定 (Development / Testing / Production)
├── models/
│   ├── __init__.py
│   ├── user.py          # User モデル
│   └── diary.py         # DiaryEntry モデル
├── routes/
│   ├── __init__.py
│   ├── auth.py          # /signin, /signup, /signout, /auth
│   └── diary.py         # /dashboard, /diary/create, /diary/delete など
├── services/
│   ├── __init__.py
│   ├── auth_service.py  # パスワードハッシュ・セッション管理（Flask 非依存）
│   └── diary_service.py # 日記 CRUD ロジック（Flask 非依存）
└── db.py                # SQLite 接続・スキーマ管理

tests/
├── conftest.py          # pytest fixtures（テスト用インメモリ DB、app factory）
├── test_auth.py         # 認証フローのテスト
└── test_diary.py        # 日記 CRUD のテスト

run.py                   # エントリポイント (create_app() を呼ぶだけ)
.env                     # SECRET_KEY, DATABASE_URL など（git 管理外）
.env.example             # 必要な環境変数の一覧（git 管理下）
```

**設計原則:**
- `routes/` は HTTP の関心事のみ（リクエスト受付・レスポンス返却）
- `services/` にビジネスロジックを集約（Flask に依存しない → pytest でそのままテスト可能）
- `models/` はデータ構造と DB アクセスのみ
- テストは `services/` を直接呼んで書く（HTTP レイヤーに引きずられない）

## 現在の技術的負債
- [ ] パスワードハッシュが SHA256 + ソルトなし → `werkzeug.security` に移行必須
- [ ] `SECRET_KEY` がハードコード → `.env` で管理
- [ ] DB 接続情報がハードコード → `.env` で管理
- [ ] CSRF 保護なし（全 POST エンドポイント）
- [ ] フォームフィールドの入力長バリデーションなし
- [ ] ユーザーデータと日記データが別ストレージ（MySQL vs JSON）

## 現フェーズのスコープ外
- マルチユーザー本番デプロイ
- レートリミット
