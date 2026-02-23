import os


class Config:
    """全環境共通の設定基底クラス。"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-key-change-in-production")
    DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "diary.db")


class DevelopmentConfig(Config):
    """開発環境の設定。デバッグモードを有効にする。"""
    DEBUG = True


class TestingConfig(Config):
    """テスト環境の設定。インメモリ DB を使用する。"""
    TESTING = True
    DATABASE = ":memory:"


class ProductionConfig(Config):
    """本番環境の設定。デバッグ無効・SECRET_KEY 必須。"""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        if cls.SECRET_KEY == "dev-fallback-key-change-in-production":
            raise RuntimeError("SECRET_KEY must be set in production environment")


# 環境名と設定クラスの対応表
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
