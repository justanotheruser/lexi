-- Initialize the Lexi database
-- This script creates the database schema as described in the PRD

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    native_language_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create stories table
CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    target_language_code VARCHAR(10) NOT NULL,
    protagonist TEXT NOT NULL,
    setting TEXT NOT NULL,
    full_story_text TEXT,
    cover_image_url TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL
);

-- Create user_vocabulary_progress table
CREATE TABLE IF NOT EXISTS user_vocabulary_progress (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    word TEXT NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    times_seen INTEGER DEFAULT 0,
    times_quized INTEGER NULL,
    correct_answers INTEGER NULL,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, language_code, word)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stories_user_id ON stories(user_id);
CREATE INDEX IF NOT EXISTS idx_stories_finished_at ON stories(finished_at);
CREATE INDEX IF NOT EXISTS idx_vocabulary_user_language ON user_vocabulary_progress(user_id, language_code);
CREATE INDEX IF NOT EXISTS idx_vocabulary_word ON user_vocabulary_progress(word);

-- Insert some sample data for development
INSERT INTO users (id, native_language_code) VALUES 
    (123456789, 'es'),
    (987654321, 'en')
ON CONFLICT (id) DO NOTHING; 