"""
Generator-Optimized Prompt Converter with Database Integration
Converts detailed photography prompts to generator-friendly format while tracking in database

INPUT DIRECTORIES:
- Line 40: input_folder - Where approved prompts are read from (approved_prompts)

OUTPUT DIRECTORIES:
- Line 41: output_folder - Where generator-optimized prompts are saved (generator_prompts)

DATABASE INTEGRATION:
- Links reformatted prompts to original evaluations
- Tracks compression ratios and optimization metrics
- Stores both detailed and optimized versions
"""

import re
from pathlib import Path
import os
import argparse
import sys

# Add the database directory to Python path
current_dir = Path(__file__).parent
database_dir = current_dir.parent / "database"
sys.path.insert(0, str(database_dir))

from database_utils import DatabaseManager


def convert_to_generator_format(detailed_prompt):
    """
    Convert detailed photography prompt to clean generator-optimized format
    Extracts just the clean prompt text without any formatting or headers
    """

    # Extract the approved prompt text (the clean prompt without formatting)
    approved_match = re.search(r'APPROVED FINAL PROMPT:\s*(.+?)(?=\n\nRound:|$)', detailed_prompt, re.DOTALL)

    if approved_match:
        approved_text = approved_match.group(1).strip()

        # Remove any markdown formatting like **Photography Prompt:**
        approved_text = re.sub(r'\*\*[^*]+\*\*\s*', '', approved_text)

        # Remove any remaining headers or labels
        approved_text = re.sub(r'^[A-Z][^:]*:\s*', '', approved_text, flags=re.MULTILINE)

        # Remove section headers like "Technical Specifications:", "Lighting Setup:", etc.
        approved_text = re.sub(r'\n\n[A-Z][^:]*:\s*', '\n\n', approved_text, flags=re.MULTILINE)

        # Clean up extra whitespace and newlines
        approved_text = re.sub(r'\n+', ' ', approved_text)
        approved_text = re.sub(r'\s+', ' ', approved_text).strip()

        return approved_text
    
    # Try to extract just the improved prompt from the file content
    # Look for patterns like "Final prompt is X words" followed by content
    final_prompt_match = re.search(r'Final prompt[^\n]*\n(.+?)(?=\n\n|$)', detailed_prompt, re.DOTALL | re.IGNORECASE)
    if final_prompt_match:
        return final_prompt_match.group(1).strip()

    # Fallback: try to extract from original prompt if approved section not found
    original_match = re.search(r'Original Prompt:\s*(.+?)(?=\n\n|\n=|$)', detailed_prompt, re.DOTALL)
    if original_match:
        return original_match.group(1).strip()

    # Final fallback: return the whole text cleaned up
    cleaned = re.sub(r'Original Prompt:.*?={40,}', '', detailed_prompt, flags=re.DOTALL)
    cleaned = re.sub(r'Round:.*', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'Iterations:.*', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'Processing time:.*', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'\*\*[^*]+\*\*\s*', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def extract_metadata_from_approved_file(content):
    """Extract metadata from approved prompt file"""
    metadata = {}

    # Extract evaluation_id if present
    eval_match = re.search(r'Database evaluation_id:\s*(\d+)', content)
    if eval_match:
        metadata['evaluation_id'] = int(eval_match.group(1))

    # Extract prompt_id if present
    prompt_match = re.search(r'Database prompt_id:\s*(\d+)', content)
    if prompt_match:
        metadata['prompt_id'] = int(prompt_match.group(1))

    # Extract theme
    theme_match = re.search(r'Theme:\s*(.+)', content)
    if theme_match:
        metadata['theme'] = theme_match.group(1).strip()

    # Extract original prompt
    original_match = re.search(r'Original Prompt:\s*(.+?)(?=\n\n=|$)', content, re.DOTALL)
    if original_match:
        metadata['original_prompt'] = original_match.group(1).strip()

    return metadata


def get_evaluation_id_from_db(db_manager, session_id: str, filename: str):
    """Get evaluation_id from database based on approved filename"""
    try:
        # Remove 'approved_' prefix from filename to get original filename
        original_filename = filename.replace('approved_', '')
        
        # Try exact match first
        query = """
                SELECT pe.evaluation_id, pe.prompt_id
                FROM prompt_evaluations pe
                         JOIN generated_prompts gp ON pe.prompt_id = gp.prompt_id
                WHERE pe.session_id = ? 
                  AND gp.file_name = ? 
                  AND pe.approved = TRUE
                ORDER BY pe.created_at DESC LIMIT 1 
                """
        db_manager.cursor.execute(query, (session_id, original_filename))
        result = db_manager.cursor.fetchone()
        
        if result:
            return result['evaluation_id'], result['prompt_id']
            
        # If exact match fails, try pattern matching for timestamped files
        # Extract theme and number from filename (e.g., wildlife_20250811_130401_01.txt -> wildlife_%_01.txt)
        pattern_match = re.match(r'([^_]+)_\d{8}_\d{6}_(\d+)\.txt$', original_filename)
        if pattern_match:
            theme_part = pattern_match.group(1)
            number_part = pattern_match.group(2)
            
            # Try to find a matching pattern in database
            like_pattern = f"{theme_part}_%_{number_part}.txt"
            query = """
                    SELECT pe.evaluation_id, pe.prompt_id
                    FROM prompt_evaluations pe
                             JOIN generated_prompts gp ON pe.prompt_id = gp.prompt_id
                    WHERE pe.session_id = ? 
                      AND gp.file_name LIKE ? 
                      AND pe.approved = TRUE
                    ORDER BY pe.created_at DESC LIMIT 1 
                    """
            db_manager.cursor.execute(query, (session_id, like_pattern))
            result = db_manager.cursor.fetchone()
            
            if result:
                return result['evaluation_id'], result['prompt_id']
        
        return None, None
    except Exception as e:
        print(f"Error getting evaluation_id: {e}")
        return None, None


def process_approved_prompts_folder(input_folder="approved_prompts", output_folder="generator_prompts", session_id=None):
    """
    Process all approved prompt files and create generator-optimized versions with database integration
    """
    
    # If session_id provided, look for approved prompts in the root approved_prompts folder
    if session_id:
        try:
            # Always start with root approved_prompts folder (where prompt_judge.py saves)
            root_approved_dir = Path("approved_prompts")
            if root_approved_dir.exists():
                print(f"Found approved_prompts folder: {root_approved_dir}")
                input_path = root_approved_dir
            else:
                print(f"No approved_prompts folder found, trying database fallback...")
                # Try to find from database as fallback
                with DatabaseManager() as db:
                    prompts = db.get_prompts_for_session(session_id)
                    if prompts:
                        # Get the directory from the first prompt's file path
                        first_prompt_path = Path(prompts[0]['file_path'])
                        session_prompts_dir = first_prompt_path.parent
                        potential_approved_dir = session_prompts_dir / "approved_prompts"
                        
                        if potential_approved_dir.exists():
                            print(f"Found approved prompts via database: {potential_approved_dir}")
                            input_path = potential_approved_dir
                        else:
                            print(f"Session directory found but no approved_prompts: {session_prompts_dir}")
                            input_path = Path(input_folder)
                    else:
                        print(f"No prompts found in database for session {session_id}")
                        input_path = Path(input_folder)
        except Exception as e:
            print(f"Could not locate session prompts, using default: {e}")
            input_path = Path(input_folder)
    else:
        input_path = Path(input_folder)

    output_path = Path(output_folder)

    if not input_path.exists():
        print(f"Input folder not found: {input_path}")
        print(f"Searching for approved prompts...")
        
        # Try to find approved_prompts directories
        project_root = Path.cwd()
        potential_dirs = list(project_root.rglob("approved_prompts"))
        
        if potential_dirs:
            print(f"[SEARCH] Found potential directories:")
            for i, dir_path in enumerate(potential_dirs):
                files = list(dir_path.glob("approved_*.txt"))
                print(f"  {i+1}. {dir_path} ({len(files)} files)")

            if len(potential_dirs) == 1:
                input_path = potential_dirs[0]
                print(f"[OK] Auto-selected: {input_path}")
            else:
                # Use the most recent one or one with most files
                best_dir = max(potential_dirs, key=lambda d: len(list(d.glob("approved_*.txt"))))
                input_path = best_dir
                print(f"[OK] Auto-selected directory with most files: {input_path}")
        
        if not input_path.exists():
            return False

    # Create output folder
    output_path.mkdir(exist_ok=True)

    # Initialize database connection first (needed for session filtering)
    db_manager = None
    try:
        if session_id:
            db_manager = DatabaseManager()
            print("Database connected for reformatting tracking")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Will save to files only")

    # Find approved prompt files - filter by session if available
    all_prompt_files = list(input_path.glob("approved_*.txt"))
    print(f"DEBUG: Found {len(all_prompt_files)} total approved files")
    
    # Filter files to current session only
    prompt_files = []
    if session_id and db_manager:
        try:
            # Get original prompt files for this session from database
            cursor = db_manager.connection.cursor()
            cursor.execute("""
                SELECT file_name FROM generated_prompts 
                WHERE session_id = ?
                ORDER BY created_at
            """, (session_id,))
            db_results = cursor.fetchall()
            session_files_from_db = [f"approved_{row[0]}" for row in db_results]  # Add approved_ prefix
            print(f"DEBUG: Expected approved files for session {session_id}: {session_files_from_db}")
            
            # Filter actual files to match database records
            for file_path in all_prompt_files:
                if file_path.name in session_files_from_db:
                    prompt_files.append(file_path)
                    
        except Exception as e:
            print(f"WARNING: Could not filter files by session from database: {e}")
    
    # Fallback: Use timestamp-based filtering if database filtering failed
    if not prompt_files and session_id:
        import re
        # Extract date from session_id (e.g., session_2025-08-15_16-40-08 -> 20250815)
        session_date_match = re.search(r'session_(\d{4})-(\d{2})-(\d{2})', session_id)
        if session_date_match:
            year, month, day = session_date_match.groups()
            session_date = f"{year}{month}{day}"
            print(f"DEBUG: Filtering files by date: {session_date}")
            
            for file_path in all_prompt_files:
                if session_date in file_path.name:
                    prompt_files.append(file_path)
    
    # If no session filtering, use all files
    if not prompt_files:
        prompt_files = all_prompt_files

    if not prompt_files:
        print(f" No approved prompt files found in {input_path}")
        return False

    print(f"Processing {len(prompt_files)} prompts for generator optimization...")
    if len(prompt_files) != len(all_prompt_files):
        print(f"DEBUG: Filtered from {len(all_prompt_files)} total files to {len(prompt_files)} session files")
        skipped_files = [f.name for f in all_prompt_files if f not in prompt_files]
        print(f"DEBUG: Skipped files: {skipped_files}")
    print(f"DEBUG: Processing files: {[f.name for f in prompt_files]}")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    if session_id:
        print(f"Session ID: {session_id}")
    print(f"{'=' * 60}")

    successful = 0

    try:
        for file_path in prompt_files:
            try:
                # Read the detailed prompt
                with open(file_path, 'r', encoding='utf-8') as f:
                    detailed_prompt = f.read()

                # Extract metadata from the approved file
                metadata = extract_metadata_from_approved_file(detailed_prompt)

                # Get evaluation_id from database if not in file
                evaluation_id = metadata.get('evaluation_id')
                prompt_id = metadata.get('prompt_id')

                if not evaluation_id and db_manager and session_id:
                    evaluation_id, prompt_id = get_evaluation_id_from_db(db_manager, session_id, file_path.name)

                # Convert to generator format (extract clean prompt)
                generator_prompt = convert_to_generator_format(detailed_prompt)

                # Create output filename with unique identifier to prevent conflicts
                # Convert approved_christmas_20250811_130401_01.txt -> generator_christmas_20250811130401_01.txt
                base_name = file_path.name.replace("approved_", "")
                
                # Extract timestamp pattern but keep it for uniqueness
                import re
                timestamp_match = re.search(r'_(\d{8})_(\d{6})', base_name)
                if timestamp_match:
                    # Combine date and time into compact format: 20250811130401
                    date_part = timestamp_match.group(1)
                    time_part = timestamp_match.group(2) 
                    compact_timestamp = f"{date_part}{time_part}"
                    # Remove the original timestamp pattern and replace with compact version
                    clean_name = re.sub(r'_\d{8}_\d{6}', f'_{compact_timestamp}', base_name)
                else:
                    # Fallback: use original name if no timestamp found
                    clean_name = base_name
                
                generator_filename = f"generator_{clean_name}"
                generator_path = output_path / generator_filename

                # Save generator-optimized prompt
                with open(generator_path, 'w', encoding='utf-8') as f:
                    f.write(generator_prompt)

                print(f"Processing {file_path.name}")
                print(f"   Length: {len(detailed_prompt)} -> {len(generator_prompt)} chars")
                print(f"   Clean prompt: {generator_prompt}")
                print(f"   Saved as: {generator_filename}")

                # Save to database if connected
                if db_manager and session_id:
                    # Try to get prompt_id from database if missing
                    if not prompt_id:
                        original_filename = file_path.name.replace('approved_', '')
                        cursor = db_manager.connection.cursor()
                        cursor.execute("""
                            SELECT prompt_id FROM generated_prompts 
                            WHERE session_id = ? AND file_name = ?
                            ORDER BY created_at DESC LIMIT 1
                        """, (session_id, original_filename))
                        result = cursor.fetchone()
                        if result:
                            prompt_id = result[0]
                            print(f"   Found prompt_id from database: {prompt_id}")
                    
                    if prompt_id:
                        # Use evaluation_id if available, otherwise use 0 as placeholder
                        reformatted_id = db_manager.insert_reformatted_prompt(
                            evaluation_id=evaluation_id or 0,
                            prompt_id=prompt_id,
                            session_id=session_id,
                            original_detailed=detailed_prompt,
                            generator_optimized=generator_prompt,
                            file_name=generator_filename,
                            file_path=str(generator_path)
                        )

                        if reformatted_id:
                            print(f"   Saved to database: reformatted_id {reformatted_id}")
                        else:
                            print(f"   Database save failed")
                    else:
                        print(f"   Could not find prompt_id for database linking")

                print()
                successful += 1

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

        print(f"{'=' * 60}")
        print(f"Successfully processed {successful}/{len(prompt_files)} files")
        print(f"Clean prompts saved to: {output_path}")
        if db_manager:
            print(f"Reformatted prompts tracked in database")

        return successful > 0

    finally:
        if db_manager:
            db_manager.disconnect()


def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Generator prompt reformatter with database integration')
    parser.add_argument('--session-id', type=str, help='Pipeline session ID for database tracking')
    parser.add_argument('--input-folder', type=str, default='approved_prompts',
                        help='Input folder containing approved prompts')
    parser.add_argument('--output-folder', type=str, default='generator_prompts',
                        help='Output folder for generator-optimized prompts')
    args = parser.parse_args()

    print("GENERATOR PROMPT REFORMATTER WITH DATABASE INTEGRATION")
    print("=" * 60)

    if args.session_id:
        print(f"Session ID: {args.session_id}")
    else:
        print(" No session ID provided - database tracking disabled")

    # Process all approved prompts
    success = process_approved_prompts_folder(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        session_id=args.session_id
    )

    if success:
        print(" Reformatting completed successfully!")
    else:
        print(" Reformatting failed!")
        exit(1)


if __name__ == "__main__":
    # Run with command line arguments
    main()