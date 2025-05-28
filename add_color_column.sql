-- Add color column to users table
ALTER TABLE users ADD COLUMN profile_color VARCHAR(7) DEFAULT '#008bb4';
