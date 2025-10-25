"""
SQLite Database connection and utility functions for Pipeline
Handles all database operations for the content generation pipeline using SQLite
This version is for laptop use - data can be migrated to MySQL later
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, List

# Load environment variables
load_dotenv()


class DatabaseManager:
    """Manages all database operations for the pipeline using SQLite"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Create database in project root
            project_root = Path(__file__).parent.parent
            db_path = project_root / "image_pipeline.db"
        
        self.db_path = str(db_path)
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.migrate_schema()  # Apply schema migrations for existing databases

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Makes rows dict-like
            self.cursor = self.connection.cursor()
            print(f"[SUCCESS] SQLite database connected: {self.db_path}")
        except sqlite3.Error as e:
            print(f"[ERROR] Database connection failed: {e}")
            raise

    def create_tables(self):
        """Create all necessary tables"""
        try:
            # Pipeline Sessions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_sessions (
                    session_id TEXT PRIMARY KEY,
                    theme TEXT NOT NULL,
                    session_timestamp DATETIME NOT NULL,
                    base_output_dir TEXT,
                    status TEXT DEFAULT 'running',
                    total_prompts_generated INTEGER DEFAULT 0,
                    total_prompts_approved INTEGER DEFAULT 0,
                    total_images_generated INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Generated Prompts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_prompts (
                    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    prompt_text TEXT NOT NULL,
                    prompt_type TEXT,
                    approach_type TEXT,
                    variation_style TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    character_count INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES pipeline_sessions(session_id)
                )
            """)

            # Prompt Evaluations table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_evaluations (
                    evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    iteration_number INTEGER NOT NULL,
                    original_prompt TEXT NOT NULL,
                    refined_prompt TEXT NOT NULL,
                    evaluation_score TEXT NOT NULL,
                    feedback TEXT,
                    missing_elements TEXT,
                    strength_areas TEXT,
                    processing_time_seconds REAL,
                    approved BOOLEAN DEFAULT FALSE,
                    approved_file_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES generated_prompts(prompt_id),
                    FOREIGN KEY (session_id) REFERENCES pipeline_sessions(session_id)
                )
            """)

            # Reformatted Prompts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reformatted_prompts (
                    reformatted_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id INTEGER NOT NULL,
                    prompt_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    original_detailed_prompt TEXT NOT NULL,
                    generator_optimized_prompt TEXT NOT NULL,
                    character_count_before INTEGER,
                    character_count_after INTEGER,
                    compression_ratio REAL,
                    file_name TEXT,
                    file_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (evaluation_id) REFERENCES prompt_evaluations(evaluation_id),
                    FOREIGN KEY (prompt_id) REFERENCES generated_prompts(prompt_id),
                    FOREIGN KEY (session_id) REFERENCES pipeline_sessions(session_id)
                )
            """)

            # Generated Images table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_images (
                    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reformatted_id INTEGER NOT NULL,
                    prompt_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    generator_task_id TEXT,
                    image_file_name TEXT,
                    image_file_path TEXT,
                    generator_prompt_used TEXT,
                    api_response TEXT,
                    generation_status TEXT DEFAULT 'pending',
                    generation_timestamp DATETIME,
                    image_url TEXT,
                    file_size_bytes INTEGER,
                    image_width INTEGER,
                    image_height INTEGER,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reformatted_id) REFERENCES reformatted_prompts(reformatted_id),
                    FOREIGN KEY (prompt_id) REFERENCES generated_prompts(prompt_id),
                    FOREIGN KEY (session_id) REFERENCES pipeline_sessions(session_id)
                )
            """)

            self.connection.commit()
            print("[SUCCESS] Database tables created/verified")

        except sqlite3.Error as e:
            print(f"[ERROR] Failed to create tables: {e}")
            raise

    def migrate_schema(self):
        """Add missing columns to existing tables (for schema updates)"""
        try:
            # Check and add status column to generated_prompts if missing
            self.cursor.execute("PRAGMA table_info(generated_prompts)")
            columns = [row[1] for row in self.cursor.fetchall()]

            if 'status' not in columns:
                self.cursor.execute("""
                    ALTER TABLE generated_prompts ADD COLUMN status TEXT DEFAULT 'pending'
                """)
                print("[MIGRATION] Added 'status' column to generated_prompts table")

            if 'updated_at' not in columns:
                self.cursor.execute("""
                    ALTER TABLE generated_prompts ADD COLUMN updated_at DATETIME DEFAULT NULL
                """)
                print("[MIGRATION] Added 'updated_at' column to generated_prompts table")

            self.connection.commit()

        except sqlite3.Error as e:
            print(f"[WARNING] Schema migration failed: {e}")

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("[LIST] Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # =============================================================================
    # PIPELINE SESSION MANAGEMENT
    # =============================================================================

    def create_pipeline_session(self, session_id: str, theme: str, base_output_dir: str) -> bool:
        """Create a new pipeline session"""
        try:
            query = """
                INSERT INTO pipeline_sessions
                (session_id, theme, session_timestamp, base_output_dir, status)
                VALUES (?, ?, ?, ?, 'running')
            """
            self.cursor.execute(query, (session_id, theme, datetime.now(), base_output_dir))
            self.connection.commit()
            print(f"[SUCCESS] Created pipeline session: {session_id}")
            return True
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to create pipeline session: {e}")
            return False

    def update_pipeline_session_status(self, session_id: str, status: str, **kwargs) -> bool:
        """
        Update pipeline session status and statistics

        Security: Uses whitelist to prevent SQL injection via dynamic column names
        """
        try:
            # SECURITY: Whitelist of allowed column names to prevent SQL injection
            ALLOWED_COLUMNS = {
                'total_prompts_generated', 'total_prompts_approved',
                'total_images_generated',
                'base_output_dir', 'theme'
            }

            # Filter kwargs to only allowed columns
            safe_kwargs = {k: v for k, v in kwargs.items() if k in ALLOWED_COLUMNS}

            # Warn if any columns were rejected
            rejected = set(kwargs.keys()) - ALLOWED_COLUMNS
            if rejected:
                print(f"[SECURITY WARNING] Rejected unsafe column names: {rejected}")

            # Build query with validated column names
            update_fields = [f"{key} = ?" for key in safe_kwargs.keys()]
            update_fields.append("status = ?")
            update_fields.append("updated_at = ?")

            query = f"""
                UPDATE pipeline_sessions
                SET {', '.join(update_fields)}
                WHERE session_id = ?
            """

            values = list(safe_kwargs.values()) + [status, datetime.now(), session_id]
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"[SUCCESS] Updated session {session_id} status to: {status}")
            return True
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update session status: {e}")
            return False

    # =============================================================================
    # PROMPT MANAGEMENT
    # =============================================================================

    def insert_generated_prompt(self, session_id: str, theme: str, prompt_text: str,
                                prompt_type: str, approach_type: str, variation_style: str,
                                file_name: str, file_path: str) -> Optional[int]:
        """Insert a generated prompt into the database"""
        try:
            query = """
                INSERT INTO generated_prompts
                (session_id, theme, prompt_text, prompt_type, approach_type,
                 variation_style, file_name, file_path, character_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (session_id, theme, prompt_text, prompt_type, approach_type,
                      variation_style, file_name, file_path, len(prompt_text))

            self.cursor.execute(query, values)
            self.connection.commit()
            prompt_id = self.cursor.lastrowid
            print(f"[SUCCESS] Inserted prompt {prompt_id}: {file_name}")
            return prompt_id
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert prompt: {e}")
            return None

    def get_prompts_for_session(self, session_id: str) -> List[Dict]:
        """Get all prompts for a session"""
        try:
            query = """
                SELECT * FROM generated_prompts
                WHERE session_id = ?
                ORDER BY created_at
            """
            self.cursor.execute(query, (session_id,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to get prompts: {e}")
            return []

    def insert_prompt_evaluation(self, prompt_id: int, session_id: str, iteration_number: int,
                                 original_prompt: str, refined_prompt: str, evaluation_score: str,
                                 feedback: str, missing_elements: List[str], strength_areas: List[str],
                                 processing_time: float, approved: bool, approved_file_path: str = None) -> Optional[int]:
        """Insert prompt evaluation result"""
        try:
            query = """
                INSERT INTO prompt_evaluations
                (prompt_id, session_id, iteration_number, original_prompt, refined_prompt,
                 evaluation_score, feedback, missing_elements, strength_areas,
                 processing_time_seconds, approved, approved_file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (prompt_id, session_id, iteration_number, original_prompt, refined_prompt,
                      evaluation_score, feedback, json.dumps(missing_elements),
                      json.dumps(strength_areas), processing_time, approved, approved_file_path)

            self.cursor.execute(query, values)
            self.connection.commit()
            evaluation_id = self.cursor.lastrowid
            print(f"[SUCCESS] Inserted evaluation {evaluation_id} for prompt {prompt_id}")
            return evaluation_id
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert evaluation: {e}")
            return None

    # =============================================================================
    # REFORMATTED PROMPTS
    # =============================================================================

    def insert_reformatted_prompt(self, evaluation_id: int, prompt_id: int, session_id: str,
                                  original_detailed: str, generator_optimized: str,
                                  file_name: str, file_path: str) -> Optional[int]:
        """Insert reformatted prompt"""
        try:
            char_before = len(original_detailed)
            char_after = len(generator_optimized)
            compression_ratio = char_after / char_before if char_before > 0 else 0

            query = """
                INSERT INTO reformatted_prompts
                (evaluation_id, prompt_id, session_id, original_detailed_prompt,
                 generator_optimized_prompt, character_count_before, character_count_after,
                 compression_ratio, file_name, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (evaluation_id, prompt_id, session_id, original_detailed, generator_optimized,
                      char_before, char_after, compression_ratio, file_name, file_path)

            self.cursor.execute(query, values)
            self.connection.commit()
            reformatted_id = self.cursor.lastrowid
            print(f"[SUCCESS] Inserted reformatted prompt {reformatted_id}")
            return reformatted_id
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert reformatted prompt: {e}")
            return None

    # =============================================================================
    # IMAGE GENERATION
    # =============================================================================

    def insert_generated_image(self, reformatted_id: int, prompt_id: int, session_id: str,
                               generator_task_id: str, image_file_name: str, image_file_path: str,
                               generator_prompt: str, api_response: Dict = None) -> Optional[int]:
        """Insert generated image record"""
        try:
            query = """
                INSERT INTO generated_images
                (reformatted_id, prompt_id, session_id, generator_task_id, image_file_name,
                 image_file_path, generator_prompt_used, api_response, generation_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """
            values = (reformatted_id, prompt_id, session_id, generator_task_id, image_file_name,
                      image_file_path, generator_prompt, json.dumps(api_response) if api_response else None)

            self.cursor.execute(query, values)
            self.connection.commit()
            image_id = self.cursor.lastrowid
            print(f"[SUCCESS] Inserted image record {image_id}")
            return image_id
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert image record: {e}")
            return None

    def update_image_generation_status(self, image_id: int, status: str, image_url: str = None,
                                       file_size: int = None, width: int = None, height: int = None,
                                       error_message: str = None) -> bool:
        """Update image generation status"""
        try:
            query = """
                UPDATE generated_images
                SET generation_status = ?,
                    generation_timestamp = ?,
                    image_url = ?,
                    file_size_bytes = ?,
                    image_width = ?,
                    image_height = ?,
                    error_message = ?
                WHERE image_id = ?
            """
            values = (status, datetime.now(), image_url, file_size, width, height, error_message, image_id)
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"[SUCCESS] Updated image {image_id} status to: {status}")
            return True
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update image status: {e}")
            return False

    # =============================================================================
    # ANALYTICS AND REPORTING
    # =============================================================================

    def get_session_summary(self, session_id: str) -> Dict:
        """Get complete summary of a pipeline session"""
        try:
            # Get session info
            session_query = "SELECT * FROM pipeline_sessions WHERE session_id = ?"
            self.cursor.execute(session_query, (session_id,))
            session_row = self.cursor.fetchone()

            if not session_row:
                return {}

            session = dict(session_row)

            # Get pipeline flow data (image-only pipeline: prompts → judge → reformat → images)
            flow_query = """
                SELECT COUNT(DISTINCT gp.prompt_id) as total_prompts,
                       COUNT(DISTINCT CASE WHEN pe.approved = 1 THEN pe.prompt_id END) as approved_prompts,
                       COUNT(DISTINCT rp.reformatted_id) as reformatted_prompts,
                       COUNT(DISTINCT gi.image_id) as total_images,
                       COUNT(DISTINCT CASE WHEN gi.generation_status = 'completed' THEN gi.image_id END) as successful_images
                FROM pipeline_sessions ps
                LEFT JOIN generated_prompts gp ON ps.session_id = gp.session_id
                LEFT JOIN prompt_evaluations pe ON gp.prompt_id = pe.prompt_id
                LEFT JOIN reformatted_prompts rp ON pe.evaluation_id = rp.evaluation_id
                LEFT JOIN generated_images gi ON rp.reformatted_id = gi.reformatted_id
                WHERE ps.session_id = ?
            """
            self.cursor.execute(flow_query, (session_id,))
            stats_row = self.cursor.fetchone()
            stats = dict(stats_row) if stats_row else {}

            return {
                'session': session,
                'statistics': stats
            }

        except sqlite3.Error as e:
            print(f"[ERROR] Failed to get session summary: {e}")
            return {}