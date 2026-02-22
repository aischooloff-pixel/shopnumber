from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    telegram_bot_token: 8596061120:AAEF7d2C8fZbLO6MfBWFFXDvr6y_US6cMyU

    tiger_api_key: str
    tiger_base_url: str = 'https://api.tigersms.org/stubs/handler_api.php'

    cryptobot_api_token: str
    cryptobot_base_url: str = 'https://pay.crypt.bot/api'
    payment_asset: str = 'USDT'

    default_country: str = 'ru'
    default_max_price: float = 35.0
    support_username: str = '@support'


settings = Settings()
