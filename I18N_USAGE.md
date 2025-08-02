# I18n Usage Guide

This document explains how to use the internationalization (i18n) system in the Telegram bot handlers.

## Overview

The i18n system automatically detects the user's language from their `ui_language_code` field in the database (cached in Redis). If the user is not found in cache, it falls back to the default language specified in settings.


## Usage in Handlers

### Basic Usage

```python
@telegram_router.message(F.text == "/start")
async def handle_start_command(message: Message, i18n) -> None:
    # Get translated message for the user (synchronous)
    welcome_message = i18n["WELCOME"].translate()
    await message.reply(welcome_message)
```

### With Parameters

```python
@telegram_router.message(F.text)
async def handle_language_selection(message: Message, i18n) -> None:
    # Get translated message with parameters (synchronous)
    confirmation = i18n["LETS_LEARN"].translate(language_name="Python")
    await message.reply(confirmation)
```

## Available Translation Keys

- `WELCOME` - Welcome message
- `WHAT_LANGUAGE_YOU_WANT_LEARN` - Language selection prompt
- `LETS_LEARN` - Confirmation message when language is selected (requires `language_name` parameter)
- `LANGUAGE_NOT_SUPPORTED` - Error message for unsupported languages

## Supported Languages

- English (`en`) - Default
- Russian (`ru`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)

## Architecture

The i18n system follows Domain-Driven Design principles:

1. **I18nService** - Core service that handles user language detection and translation
2. **I18nMiddleware** - Automatically injects synchronous i18n interface into handlers
3. **I18nManager** - Provides synchronous translation interface
4. **TranslatableKey** - Represents a translatable key with translation
5. **Translator** - Handles translation for a specific language

## Middleware Integration

The i18n system is automatically injected into handlers via middleware. No additional setup is required in handlers.

## Adding New Translations

To add new translations:

1. Add the translation key to all language dictionaries in `I18nService._create_translators()`
2. Use the key in your handlers with `i18n["YOUR_KEY"].translate()`

## Parameter Substitution

Use `${parameter_name}` in translation strings and pass parameters as keyword arguments:

```python
# Translation: "Hello ${name}, welcome to ${app}!"
i18n["GREETING"].translate(name="John", app="Lexi")
```