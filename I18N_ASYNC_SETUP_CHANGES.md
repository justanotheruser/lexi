# i18n Async Setup Implementation

## Overview

This implementation changes the i18n middleware approach to load phrases from the database during setup rather than in the middleware itself, making the setup process async and more efficient.

## Changes Made

### 1. Updated `app/telegram/i18n.py`

**Modified:**
- Made `_load_translators_from_db()` public as `load_translators_from_db()`
- Removed session parameter from `get_i18n()` method
- Simplified the method to only handle user language detection and translator selection

**Benefits:**
- Cleaner separation of concerns
- Phrases loaded once during setup
- No database calls in middleware execution

### 2. Updated `app/telegram/middleware/i18n_middleware.py`

**Simplified:**
- Removed session handling logic
- Removed fallback for missing session
- Direct call to `get_i18n()` without session parameter

**Benefits:**
- Simpler middleware logic
- Faster execution (no database calls)
- More predictable behavior

### 3. Updated `app/telegram/middlewares.py`

**Made async:**
- `setup_i18n_middleware()` is now async
- Added sessionmaker parameter
- Loads phrases from database during setup

**Implementation:**
```python
async def setup_i18n_middleware(router: Router, user_cache: UserCache, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    """Set up i18n middleware for all handlers"""
    i18n_service = I18nService(user_cache)
    
    # Load phrases from database during setup
    async with sessionmaker() as session:
        await i18n_service.load_translators_from_db(session)
    
    i18n_middleware = I18nMiddleware(i18n_service)
    router.message.middleware(i18n_middleware)
    router.callback_query.middleware(i18n_middleware)
```

### 4. Updated `app/telegram/bot.py`

**Modified:**
- Added `await` calls to `setup_i18n_middleware()`
- Passed sessionmaker parameter to setup function

**Implementation:**
```python
# Setup i18n middleware
user_cache = UserCache(cache)
await setup_i18n_middleware(telegram_router, user_cache, sessionmaker)
await setup_i18n_middleware(story_creation_router, user_cache, sessionmaker)
```

## Architecture Benefits

### 1. **Performance**
- Phrases loaded once during startup
- No database calls during message handling
- Faster middleware execution

### 2. **Reliability**
- Database connection issues handled during startup
- No runtime database dependencies in middleware
- Graceful fallback if database is unavailable during startup

### 3. **Maintainability**
- Clear separation between setup and runtime
- Easier to test and debug
- More predictable behavior

### 4. **Scalability**
- Phrases cached in memory after loading
- No repeated database queries
- Better resource utilization

## Flow Comparison

### Before (Runtime Loading)
```
Message → Middleware → Database Query → Load Phrases → Translate
```

### After (Setup Loading)
```
Startup → Load Phrases → Cache in Memory
Message → Middleware → Use Cached Phrases → Translate
```

## Error Handling

- **Startup failures:** Database connection issues handled during setup
- **Missing translations:** Fallback to phrase keys
- **Service unavailability:** Graceful degradation with empty translators

## Testing

All files compile successfully:
- ✅ `app/telegram/i18n.py`
- ✅ `app/telegram/middleware/i18n_middleware.py`
- ✅ `app/telegram/middlewares.py`
- ✅ `app/telegram/bot.py`

## Migration Notes

1. **Database must be available during startup**
2. **Phrases are loaded once and cached**
3. **No runtime database dependencies**
4. **Setup is now async and must be awaited**

## Future Enhancements

- **Hot reloading:** Ability to reload phrases without restart
- **Translation caching:** Redis-based phrase caching
- **Admin interface:** Real-time translation management
- **A/B testing:** Multiple translation versions 