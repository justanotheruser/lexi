from __future__ import annotations

from typing import cast

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore

from lexi.config import AppConfig
from lexi.const import DEFAULT_LOCALE, MESSAGES_SOURCE_DIR
from lexi.utils.localization import UserManager


def create_i18n_core(config: AppConfig) -> FluentRuntimeCore:
    locales: list[str] = cast(list[str], config.telegram.locales)
    return FluentRuntimeCore(
        path=MESSAGES_SOURCE_DIR / "{locale}",
        raise_key_error=False,
        locales_map={locales[i]: locales[i + 1] for i in range(len(locales) - 1)},
    )


def create_i18n_middleware(config: AppConfig) -> I18nMiddleware:
    return I18nMiddleware(
        core=create_i18n_core(config=config),
        manager=UserManager(),
        default_locale=DEFAULT_LOCALE,
    )
