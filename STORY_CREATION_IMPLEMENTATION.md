# Story Creation Dialog Implementation

## Overview

This implementation splits the original `start.py` file into two separate routers and implements a Finite State Machine (FSM) for the story creation dialog.

## Architecture

### 1. Router Split

- **`start.py`**: Handles only the `/start` command and initiates the story creation dialog
- **`story_creation.py`**: Handles the entire story creation dialog using FSM

### 2. FSM States

The story creation dialog follows these states:

1. **`selecting_language`**: User selects the target language for learning
2. **`defining_protagonist`**: User defines the main character of the story
3. **`defining_setting`**: User defines the setting/place of the story

### 3. Content Moderation

- Uses OpenAI Moderation API to check if protagonist and setting descriptions are appropriate for children
- Checks for violence, sexual content, hate, harassment, and self-harm
- If content is flagged, user is politely asked to try a different idea

### 4. Language Selection

- Supports fuzzy matching for language names
- Accepts both language names in English and user's native language
- Supports country flag emojis
- Requires 70% confidence threshold for language matching

## Files Created/Modified

### New Files
- `app/telegram/handlers/story_creation.py` - Story creation dialog router
- `app/features/content_moderation/service.py` - OpenAI moderation service
- `app/features/content_moderation/__init__.py` - Module init file

### Modified Files
- `app/telegram/handlers/start.py` - Simplified to only handle `/start` command
- `app/telegram/i18n.py` - Added new phrases for story creation dialog
- `app/telegram/bot.py` - Added story creation router and FSM setup

## New i18n Phrases

- `LANGUAGE_SELECTED` - Confirmation when language is selected
- `DEFINE_PROTAGONIST` - Prompt to define the main character
- `DEFINE_SETTING` - Prompt to define the story setting
- `CONTENT_INAPPROPRIATE` - Error message for inappropriate content
- `STORY_PARAMETERS_READY` - Confirmation when all parameters are ready

## FSM Storage

- Uses Redis as FSM storage backend
- Configured in `bot.py` with `RedisStorage.from_url(cfg.redis_url)`

## Story Parameters Output

At the end of the dialog, the bot outputs a JSON message with all story parameters:

```json
{
  "target_language_code": "en",
  "protagonist": "brave knight",
  "setting": "magical forest"
}
```

## Usage Flow

1. User sends `/start`
2. Bot asks for language selection
3. User selects language (e.g., "English", "Английский", "🇺🇸")
4. Bot confirms language and asks for protagonist
5. User defines protagonist (e.g., "brave knight")
6. Bot checks content moderation
7. If appropriate, bot asks for setting
8. User defines setting (e.g., "magical forest")
9. Bot checks content moderation
10. If appropriate, bot outputs JSON with all parameters
11. FSM state is cleared

## Error Handling

- Language not supported: User is asked to try again
- Inappropriate content: User is politely asked to try something more suitable for children
- API errors: Content is allowed to avoid blocking the flow 