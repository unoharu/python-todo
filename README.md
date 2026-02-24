# Nota — 大学生のための毎日の記録アプリ

> シンプルに、続けやすく。授業のこと、気づいたこと、なんでも書き留める個人日記 Web アプリ。

<img width="2940" height="1602" alt="top" src="https://github.com/user-attachments/assets/4512798d-d4c7-4170-acc8-03d217ab62be" />

---

## 概要

**Nota** は Flask ベースのシングルユーザー日記アプリです。
セットアップが最小限で、インストール後すぐにローカルで使いはじめられます。

- ノートの罫線・マージン線を模したデザイン
- タイトルと本文を書いて「書き留める」だけのシンプルな操作
- 日記の作成・編集・削除がページ遷移なし（AJAX）で完結

※コメントアウトが多いのはFlaskを学習するために作成したためです。

## 機能

| 機能 | 説明 |
|------|------|
| ユーザー登録 / ログイン | メールアドレス + パスワードで認証 |
| 日記の作成 | タイトル・本文を入力して投稿 |
| 日記の一覧表示 | 新しい順にリスト表示（AJAX） |
| 日記の編集 | モーダルから直接編集 |
| 日記の削除 | 確認ダイアログ付き削除 |
| アカウント削除 | アカウントと全データを一括削除 |

---

## スクリーンショット

### ダッシュボード
<img width="2940" height="1602" alt="login" src="https://github.com/user-attachments/assets/b02fe77a-de3e-4c6c-8e47-e00e38c37794" />

### ログイン画面

<img width="2940" height="1602" alt="edit-modal" src="https://github.com/user-attachments/assets/ae881736-5c18-4d7a-8efe-09f928677cdc" />

### 編集モーダル

<img width="2940" height="1602" alt="dashboard" src="https://github.com/user-attachments/assets/6aeebb8f-b087-4033-b8ea-65d87acd3235" />

---

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| バックエンド | Python 3.13 / Flask 3.x |
| データベース | SQLite 3（Python 標準ライブラリ） |
| ORM | SQLAlchemy 2.x / Flask-SQLAlchemy |
| テンプレート | Jinja2 |
| フロントエンド | カスタム CSS / jQuery 3.x |
| 認証 | Werkzeug（pbkdf2 + ソルト） |
| 環境変数 | python-dotenv |

---

## セットアップ

### 必要環境

- Python 3.10 以上
- pip

### インストール

```bash
# 1. リポジトリをクローン
git clone https://github.com/<your-username>/nota.git
cd nota

# 2. 仮想環境を作成して有効化
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 環境変数を設定
cp .env.example .env
# .env を開いて SECRET_KEY を任意の値に変更する
```

### 起動

```bash
python run.py
```

ブラウザで [http://localhost:5000](http://localhost:5000) を開いてください。
初回起動時にデータベース（`instance/diary.db`）が自動生成されます。

---

## ディレクトリ構成

```
nota/
├── run.py                    # エントリポイント
├── requirements.txt
├── .env.example              # 環境変数テンプレート
├── instance/
│   └── diary.db              # SQLite データベース（自動生成、.gitignore 済み）
├── app/
│   ├── __init__.py           # Flask アプリファクトリ
│   ├── config.py             # 環境別設定
│   ├── db.py                 # DB 接続・スキーマ管理
│   ├── models/               # User / DiaryEntry モデル
│   ├── routes/               # auth / diary ルート
│   └── services/             # 認証・日記 CRUD のビジネスロジック
├── static/css/
│   └── style.css             # カスタム CSS（変数・コンポーネント）
├── templates/                # Jinja2 テンプレート
└── tests/                    # pytest テストスイート
```

---

## テスト

```bash
pytest                          # テスト実行
pytest --cov=app tests/         # カバレッジ付き
```

---

## 環境変数

`.env.example` をコピーして `.env` を作成してください。

| 変数名 | 説明 | 例 |
|--------|------|----|
| `SECRET_KEY` | Flask セッション署名キー | `openssl rand -hex 32` の出力値 |
| `DATABASE_URL` | DB ファイルパス（省略可） | `sqlite:///diary.db` |

---

## 実装状況 / Roadmap

現在はローカル個人利用向けの MVP 段階です。
セキュリティ上の既知の未実装事項を含む、今後の課題を整理しています。

### 実装済み

| カテゴリ | 内容 |
|----------|------|
| 認証 | Werkzeug（pbkdf2:sha256 + ランダムソルト）によるパスワードハッシュ |
| 認証 | タイミング攻撃対策（存在しないユーザーでもハッシュ検証を実行） |
| 認証 | セッションに user_id のみ保存（ユーザー情報の過剰保存を排除） |
| バリデーション | タイトル・本文の空白チェック、最大文字数制限（title: 100字 / comment: 10,000字） |
| バリデーション | パスワード最低長チェック（8文字以上） |
| 認可 | `@login_required` デコレータによる未ログイン時のリダイレクト |
| 認可 | 日記の編集・削除で所有者チェック（他ユーザーの日記を操作不可） |
| DB | SQLite + SQLAlchemy（セットアップ不要） |
| テスト | pytest による service 層・route 層のユニット / 統合テスト |
| 設定 | `.env` による SECRET_KEY 管理 |

### 未実装（既知の課題）

セキュリティ関連は `[security]`、品質・UX 関連は `[quality]` で分類しています。

| 優先度 | カテゴリ | 内容 |
|--------|----------|------|
| 高 | `[security]` | **CSRF 保護** — 全 POST エンドポイントにトークン検証が未実装（Flask-WTF 等の導入が必要） |
| 高 | `[security]` | **メールアドレス形式のサーバーサイド検証** — 現在は `type="email"` のブラウザバリデーションのみ |
| 中 | `[security]` | **ユーザー名・メールアドレスの最大長制限** — サーバーサイドの上限チェックが未実装 |
| 中 | `[security]` | **レートリミット** — ブルートフォース攻撃への対策なし（ローカル利用前提のため現状は許容） |
| 中 | `[quality]` | **アカウント削除機能の未完成** — ルートとテンプレートが未実装（`delete_user.html` が存在しない） |
| 低 | `[quality]` | **ページネーション** — 日記が大量になっても全件取得している |
| 低 | `[quality]` | **エラーページ** — 404 / 500 のカスタムエラーページが未定義 |
| 低 | `[quality]` | **フロントエンドバリデーション** — タイトル・本文の文字数カウンターが未実装 |

> **注意:** このアプリはローカル個人利用を前提としています。外部に公開する場合は、少なくとも CSRF 保護とメールアドレス検証の実装が必要です。

---

## ライセンス

MIT
