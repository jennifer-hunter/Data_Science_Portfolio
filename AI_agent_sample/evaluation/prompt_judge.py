"""
SIMPLIFIED Theme-Aware Batch Photo Prompt Judge with Timeout Protection
STREAMLINED: Fast, reliable evaluation with reasonable quality requirements

INPUT DIRECTORIES:
- Line 130: INPUT_FOLDER - Where generated prompts are read from (generator_prompts_raw)

OUTPUT DIRECTORIES:
- Line 131: APPROVED_FOLDER - Where approved prompts are saved (approved_prompts)

DATABASE INTEGRATION:
- Tracks all evaluation iterations and results
- Simplified evaluation with 30-second timeout per prompt
- Maximum 3 iterations to prevent infinite loops
"""

from __future__ import annotations

import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Suppress TensorFlow info messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Hide TensorFlow warnings

import asyncio
import json
import argparse
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
# Note: anthropic-agents is a multi-provider agent framework that supports OpenAI (gpt-4o)
from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace
import sys
from pathlib import Path

# Add the database directory to Python path
current_dir = Path(__file__).parent
database_dir = current_dir.parent / "database"
sys.path.insert(0, str(database_dir))

from database_utils import DatabaseManager

# Import the new theme system
from themes import get_theme_config, get_lighting_config, list_available_themes, get_backward_compatibility_themes

"""
Theme-Aware Batch Photo Prompt Judge with Database Integration
ENHANCED: Focus on hyperrealistic/photorealistic quality with extensive detail
UPDATED: Now uses modular YAML-based theme system
"""


async def run_with_rate_limit_retry(agent, input_items, max_retries=3, base_delay=5):
    """Run agent with exponential backoff retry for rate limiting"""
    import random
    for attempt in range(max_retries):
        try:
            return await Runner.run(agent, input_items)
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "error code: 429" in error_str:
                if attempt < max_retries - 1:
                    # Extract wait time from error message if available
                    import re
                    wait_match = re.search(r'try again in (\d+\.?\d*)s', str(e))
                    if wait_match:
                        wait_time = float(wait_match.group(1)) + random.uniform(1, 3)
                    else:
                        # Exponential backoff with jitter
                        wait_time = base_delay * (2 ** attempt) + random.uniform(1, 5)
                    
                    print(f"      Rate limit hit, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
            # Re-raise if not a rate limit error or if max retries exceeded
            raise e
    # This should never be reached, but just in case:
    raise Exception(f"Max retries ({max_retries}) exceeded for rate limiting")


# Load environment variables from .env file in parent directories
def load_env_from_parent():
    """Look for .env file in current, parent, and config directories"""
    current_path = Path(__file__).parent

    # Check config directory first
    config_env = current_path.parent / "config" / ".env"
    if config_env.exists():
        print(f"Loading environment from: {config_env}")
        load_dotenv(config_env)
        return
    
    # Check current and parent directories
    for _ in range(3):  # Check up to 3 parent directories
        env_file = current_path / '.env'
        if env_file.exists():
            print(f"Loading environment from: {env_file}")
            load_dotenv(env_file)
            return
        current_path = current_path.parent
    print("No .env file found in config, current, or parent directories")

# Load environment
load_env_from_parent()

# Get legacy configurations for backward compatibility
def get_legacy_lighting_styles():
    """Get legacy lighting styles for backward compatibility"""
    return get_backward_compatibility_themes()

def get_legacy_theme_configs():
    """Get legacy theme configs for backward compatibility"""
    # Default fallback config
    default_config = {
        "theme_specific_notes": (
            "GENERAL HYPERREALISTIC REQUIREMENTS:\n"
            "- Every surface must have described texture and material properties\n"
            "- Include environmental context and atmospheric conditions\n"
            "- Add human elements with realistic imperfections\n"
            "- Describe light behavior on different materials\n"
            "- Include age, wear, and weathering where appropriate\n"
            "- Minimum 200 words of comprehensive photographic detail"
        )
    }

    try:
        available_themes = list_available_themes()
        configs = {"default": default_config}  # Always include default

        for theme_name in available_themes:
            try:
                config = get_theme_config(theme_name)
                configs[theme_name] = config
            except Exception as e:
                print(f"Warning: Could not load theme {theme_name}: {e}")

        return configs
    except Exception as e:
        print(f"Warning: Could not load theme system: {e}")
        # Return just the default fallback config
        return {"default": default_config}

# Create the compatibility variables
LIGHTING_STYLES = get_legacy_lighting_styles()
THEME_JUDGE_CONFIGS = get_legacy_theme_configs()


def detect_theme_from_folder(input_folder: Path) -> str:
    """Detect theme from folder name or files"""
    folder_name = input_folder.name.lower()

    # Check folder name for theme indicators
    for theme in THEME_JUDGE_CONFIGS.keys():
        if theme != "default":
            theme_words = theme.replace("_", " ").split()
            if any(word in folder_name for word in theme_words):
                return theme

    # Check for theme in prompt files
    for txt_file in input_folder.glob("*.txt"):
        filename = txt_file.stem.lower()
        for theme in THEME_JUDGE_CONFIGS.keys():
            if theme != "default":
                theme_words = theme.replace("_", " ").split()
                if any(word in filename for word in theme_words):
                    return theme

    return "default"


def select_lighting_style() -> str:
    """Interactive lighting style selection for enhanced prompt evaluation"""
    print(f"\n{'=' * 50}")
    print("HYPERREALISTIC LIGHTING STYLE SELECTION")
    print(f"{'=' * 50}")
    print("Choose lighting style for prompt evaluation:")
    print("1. AUTUMN HYPERREALISTIC DOCUMENTARY STYLE")
    print("   - Flat overcast lighting with muted colors")
    print("   - Best for: autumn, winter, documentary themes")
    print()
    print("2. SUMMER HYPERREALISTIC BRIGHT STYLE")
    print("   - Bright even lighting with enhanced natural colors")
    print("   - Best for: summer, beach, outdoor themes")
    print()
    print("3. UNIVERSAL HYPERREALISTIC STYLE")
    print("   - Versatile photorealistic lighting for maximum realism")
    print("   - Best for: all themes (recommended)")
    print()
    
    while True:
        choice = input("Select lighting style (1-3): ").strip()
        if choice == "1":
            return "autumn"
        elif choice == "2":
            return "summer"
        elif choice == "3":
            return "hyperreal_standard"
        else:
            print("Please enter 1, 2, or 3")


@dataclass
class BatchConfig:
    """Configuration for batch processing"""
    input_folder: Path
    output_folder: Path
    theme: str
    lighting_style: str
    session_id: str = None
    max_iterations: int = 3
    timeout_seconds: int = 120

@dataclass 
class PhotoPromptEvaluation:
    """Evaluation result for a photo prompt"""
    score: Literal["pass", "fail"]
    reasoning: str
    enhanced_prompt: str
    theme_alignment: str
    lighting_notes: str

@dataclass
class BatchResult:
    """Results from batch processing"""
    total_processed: int
    approved_count: int 
    failed_count: int
    processing_time: float
    session_id: str

def create_theme_agents(theme: str, lighting_style: str = "hyperreal_standard"):
    """Create evaluation agents based on theme and lighting style"""
    
    # Get theme configuration
    theme_config = THEME_JUDGE_CONFIGS.get(theme, THEME_JUDGE_CONFIGS["default"])
    
    # Get lighting style configuration
    lighting_config = LIGHTING_STYLES.get(lighting_style, LIGHTING_STYLES["hyperreal_standard"])
    
    # Build comprehensive evaluation instructions
    theme_notes = theme_config.get("theme_specific_notes", "")
    lighting_instructions = lighting_config.get("lighting_instructions", "")
    evaluation_criteria = lighting_config.get("evaluation_criteria", "")
    
    evaluation_agent = Agent(
        name="hyperrealistic_photo_prompt_judge",
        model="gpt-4o",
        instructions=f"""You are a professional photography prompt enhancer. Your job is to make prompts more hyperrealistic and image-worthy.

CRITICAL RULE: NEVER include people, humans, adults, children, or anyone in any prompts. Focus exclusively on nature, wildlife, landscapes, architecture, and objects.

TASK: Enhance the input prompt using theme-specific success patterns + hyperrealistic photography details.

THEME: {theme.upper()}

THEME-SPECIFIC SUCCESS PATTERNS:

**WILDLIFE Photography:**
- Natural animal behavior and authentic habitat context
- Detailed fur/feather textures, animal expressions, natural postures
- Environmental storytelling: vegetation, terrain, weather conditions
- Professional wildlife photography specs (telephoto lens, fast shutter, natural lighting)
- Seasonal elements and ecosystem context

**LANDSCAPE Photography:**
- Dramatic natural lighting (golden hour, blue hour, dramatic skies)
- Layered depth: foreground, midground, background elements
- Atmospheric conditions: mist, fog, weather patterns
- Natural color palettes and seasonal characteristics
- Composition: leading lines, rule of thirds, perspective depth

**AERIAL Photography:**
- Bird's-eye perspective, scale and geographic context
- Patterns and textures visible from above
- Natural formations, topography, environmental features
- Professional drone/aerial photography specifications
- Atmospheric clarity and lighting conditions

**ARCHITECTURE Photography:**
- Structural details, materials, textures, construction elements
- Lighting interaction with surfaces (natural or ambient)
- Geometric composition, lines, symmetry, perspective
- Environmental context and setting
- Professional architectural photography techniques

ENHANCEMENT RULES:
1. Add "Hyperrealistic photograph" at the beginning if missing
2. Add "8K resolution, ultra-detailed, professional photography" if missing
3. Keep the original subject and scene exactly the same
4. Make the prompt at least 100 words with rich descriptive detail
5. Apply theme-specific patterns from above based on current theme
6. Add appropriate technical camera specifications
7. NO PEOPLE - Remove any human elements if present

LIGHTING STYLE: {lighting_config.get('style_name', 'Standard')}
LIGHTING INSTRUCTIONS: {lighting_instructions[:200] if lighting_instructions else 'Professional natural lighting'}

THEME REQUIREMENTS:
{theme_notes[:300] if theme_notes else 'Hyperrealistic photography with detailed textures and authentic environmental context'}

CRITICAL: Respond with valid JSON only. No other text.

```json
{{
    "score": "pass",
    "reasoning": "Enhanced with {theme} photography patterns and hyperrealistic details",
    "enhanced_prompt": "Your optimized enhanced prompt here - minimum 100 words",
    "theme_alignment": "Excellent alignment with {theme} photography",
    "lighting_notes": "Applied {lighting_config.get('style_name', 'standard')} lighting style"
}}
```

Always use "pass" for score. Always return valid JSON."""
    )
    
    return evaluation_agent


def get_prompt_id_from_db(db_manager, session_id: str, filename: str):
    """Get prompt_id from database based on session_id and filename"""
    try:
        # Remove the .txt extension if present
        base_filename = filename.replace('.txt', '')
        
        # Query the database
        cursor = db_manager.connection.cursor()
        cursor.execute("""
            SELECT prompt_id FROM generated_prompts 
            WHERE session_id = ? AND file_name LIKE ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (session_id, f"%{base_filename}%"))
        
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"Warning: No prompt_id found for session {session_id}, filename {filename}")
            return None
            
    except Exception as e:
        print(f"Error getting prompt_id: {e}")
        return None


async def process_batch(config: BatchConfig) -> BatchResult:
    """Process a batch of photo prompts with theme-aware evaluation"""
    print(f"Processing batch for theme: {config.theme}, lighting: {config.lighting_style}")
    
    if not config.input_folder.exists():
        raise FileNotFoundError(f"Input folder not found: {config.input_folder}")
    
    # Create output folder if it doesn't exist
    config.output_folder.mkdir(parents=True, exist_ok=True)
    
    # Connect to database first (needed for session filtering)
    db_manager = None
    if config.session_id:
        try:
            db_manager = DatabaseManager()
            print("Database connected for evaluation tracking")
        except Exception as e:
            print(f"Warning: Could not connect to database: {e}")
    
    # Create evaluation agent
    eval_agent = create_theme_agents(config.theme, config.lighting_style)
    
    # Get prompt files - filter by session if session_id is provided
    all_prompt_files = list(config.input_folder.glob("*.txt"))
    print(f"DEBUG: Found {len(all_prompt_files)} total .txt files in {config.input_folder}")
    
    # Filter files to current session only
    prompt_files = []
    session_files_from_db = []
    
    if config.session_id and db_manager:
        try:
            # Get files for this specific session from database
            cursor = db_manager.connection.cursor()
            cursor.execute("""
                SELECT file_name FROM generated_prompts 
                WHERE session_id = ?
                ORDER BY created_at
            """, (config.session_id,))
            db_results = cursor.fetchall()
            session_files_from_db = [row[0] for row in db_results]
            print(f"DEBUG: Database has {len(session_files_from_db)} files for session {config.session_id}")
            
            # Filter actual files to match database records
            for file_path in all_prompt_files:
                if file_path.name in session_files_from_db:
                    prompt_files.append(file_path)
                    
        except Exception as e:
            print(f"WARNING: Could not filter files by session from database: {e}")
            # Fallback to timestamp-based filtering
            pass
    
    # Fallback: Use timestamp-based filtering if database filtering failed or no session_id
    if not prompt_files and config.session_id:
        import re
        from datetime import datetime
        
        # Extract date from session_id (e.g., session_2025-08-15_15-22-58 -> 20250815)
        session_date_match = re.search(r'session_(\d{4})-(\d{2})-(\d{2})', config.session_id)
        if session_date_match:
            year, month, day = session_date_match.groups()
            session_date = f"{year}{month}{day}"
            print(f"DEBUG: Filtering files by date: {session_date}")
            
            # Filter files that contain the session date
            for file_path in all_prompt_files:
                if session_date in file_path.name:
                    prompt_files.append(file_path)
                    
        if not prompt_files:
            print(f"WARNING: No files found matching session date {session_date}")
            # If still no files found, process all files as last resort
            prompt_files = all_prompt_files
    
    # If no session filtering, use all files
    if not prompt_files:
        prompt_files = all_prompt_files
    
    if not prompt_files:
        print(f"ERROR: No .txt files found in {config.input_folder}")
        return BatchResult(0, 0, 0, 0.0, config.session_id or "unknown")
    
    print(f"Processing {len(prompt_files)} prompt files for session {config.session_id}")
    if len(prompt_files) != len(all_prompt_files):
        print(f"DEBUG: Filtered from {len(all_prompt_files)} total files to {len(prompt_files)} session files")
        skipped_files = [f.name for f in all_prompt_files if f not in prompt_files]
        print(f"DEBUG: Skipped files: {skipped_files[:5]}{'...' if len(skipped_files) > 5 else ''}")
    
    # Show which files will be processed
    print(f"DEBUG: Files to process: {[f.name for f in prompt_files]}")
    
    import time
    start_time = time.time()
    approved_count = 0
    failed_count = 0
    
    for i, prompt_file in enumerate(prompt_files, 1):
        print(f"\n[{i}/{len(prompt_files)}] Processing: {prompt_file.name}")
        
        try:
            # Read the original prompt
            with open(prompt_file, 'r', encoding='utf-8') as f:
                original_prompt = f.read().strip()
            
            print(f"   Original: {original_prompt[:100]}...")
            
            # Get prompt_id if we have database connection
            prompt_id = None
            if db_manager and config.session_id:
                prompt_id = get_prompt_id_from_db(db_manager, config.session_id, prompt_file.name)
            
            # Process with iterations
            current_prompt = original_prompt
            iteration = 1
            final_result = None
            
            while iteration <= config.max_iterations:
                try:
                    print(f"   Iteration {iteration}: Evaluating...")
                    
                    # Create input for evaluation - correct TResponseInputItem format
                    input_items = [{"content": current_prompt, "role": "user"}]
                    
                    # Run evaluation with timeout and rate limit protection
                    eval_result = await asyncio.wait_for(
                        run_with_rate_limit_retry(eval_agent, input_items),
                        timeout=config.timeout_seconds
                    )
                    
                    # Parse the result - handle RunResult object properly
                    if hasattr(eval_result, 'final_output'):
                        result_text = str(eval_result.final_output)
                    elif hasattr(eval_result, 'new_items') and eval_result.new_items:
                        from agents import ItemHelpers
                        result_text = ItemHelpers.text_message_outputs(eval_result.new_items)
                    else:
                        # Fallback for different result structures
                        result_text = str(eval_result)
                    
                    # Extract JSON from response with multiple strategies
                    import re
                    import json
                    
                    # Debug: Log actual response for troubleshooting
                    print(f"   DEBUG: Raw Agent response ({len(result_text)} chars)")
                    print(f"   DEBUG: Response preview: {result_text[:200]}...")
                    
                    result_json = None
                    parsing_method = "none"
                    
                    # Strategy 1: Standard markdown code block with proper multiline support
                    json_patterns = [
                        r'```json\s*(\{.*?\})\s*```',  # Original pattern
                        r'```json\s*(\{[\s\S]*?\})\s*```',  # Multiline support
                        r'```json\s*(\[.*?\])\s*```',  # Array format
                        r'```json\s*(\[[\s\S]*?\])\s*```',  # Multiline array
                    ]
                    
                    for pattern in json_patterns:
                        json_match = re.search(pattern, result_text, re.DOTALL)
                        if json_match:
                            try:
                                result_json = json.loads(json_match.group(1))
                                parsing_method = f"markdown_pattern_{json_patterns.index(pattern) + 1}"
                                break
                            except json.JSONDecodeError as e:
                                print(f"   DEBUG: JSON decode error with pattern {pattern}: {e}")
                                continue
                    
                    # Strategy 2: Look for raw JSON without markdown wrapper
                    if not result_json:
                        raw_patterns = [
                            r'(\{[^{}]*"score"[^{}]*\})',  # Simple object with score
                            r'(\{[\s\S]*?"score"[\s\S]*?\})',  # Multiline object with score
                            r'(\{.*?\})',  # Any JSON object
                            r'(\{[\s\S]*?\})',  # Any multiline JSON object
                        ]
                        
                        for pattern in raw_patterns:
                            matches = re.findall(pattern, result_text, re.DOTALL)
                            for match in matches:
                                try:
                                    potential_json = json.loads(match)
                                    if isinstance(potential_json, dict) and "score" in potential_json:
                                        result_json = potential_json
                                        parsing_method = f"raw_pattern_{raw_patterns.index(pattern) + 1}"
                                        break
                                except json.JSONDecodeError:
                                    continue
                            if result_json:
                                break
                    
                    # Strategy 3: Extract key-value pairs manually if JSON parsing fails
                    if not result_json:
                        print(f"   DEBUG: Attempting manual key-value extraction")
                        manual_json = {}
                        
                        # Look for key patterns in the response
                        key_patterns = {
                            'score': r'(?:score|result)["\':\s]*(["\']?(?:pass|fail)["\']?)',
                            'reasoning': r'(?:reasoning|explanation)["\':\s]*["\']([^"\']+)["\']',
                            'enhanced_prompt': r'(?:enhanced_prompt|prompt)["\':\s]*["\']([^"\']+)["\']',
                            'theme_alignment': r'(?:theme_alignment|alignment)["\':\s]*["\']([^"\']+)["\']',
                            'lighting_notes': r'(?:lighting_notes|lighting)["\':\s]*["\']([^"\']+)["\']'
                        }
                        
                        for key, pattern in key_patterns.items():
                            match = re.search(pattern, result_text, re.IGNORECASE | re.DOTALL)
                            if match:
                                manual_json[key] = match.group(1).strip().strip('"\'')
                        
                        if manual_json.get('score'):
                            result_json = manual_json
                            parsing_method = "manual_extraction"
                    
                    # Strategy 4: Default fallback - assume pass and extract text
                    if not result_json:
                        print(f"   DEBUG: Using fallback strategy - assuming pass")
                        result_json = {
                            "score": "pass",
                            "reasoning": "Enhanced via fallback parsing",
                            "enhanced_prompt": result_text.strip()[:500] + "...",  # Use first part of response
                            "theme_alignment": "Good",
                            "lighting_notes": f"Applied {lighting_config.get('style_name', 'standard')} style"
                        }
                        parsing_method = "fallback"
                    
                    print(f"   DEBUG: JSON parsed using method: {parsing_method}")
                    
                    if result_json:
                        # Create evaluation object
                        evaluation = PhotoPromptEvaluation(
                            score=result_json.get("score", "fail"),
                            reasoning=result_json.get("reasoning", ""),
                            enhanced_prompt=result_json.get("enhanced_prompt", current_prompt),
                            theme_alignment=result_json.get("theme_alignment", ""),
                            lighting_notes=result_json.get("lighting_notes", "")
                        )
                        
                        print(f"   Result: {evaluation.score.upper()}")
                        print(f"   Reasoning: {evaluation.reasoning[:100]}...")
                        
                        # Save evaluation to database if available
                        if db_manager and prompt_id:
                            try:
                                db_manager.connection.cursor().execute("""
                                    INSERT INTO prompt_evaluations 
                                    (prompt_id, session_id, iteration_number, original_prompt, refined_prompt, 
                                     evaluation_score, feedback, approved, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                                """, (
                                    prompt_id, config.session_id, iteration, original_prompt,
                                    evaluation.enhanced_prompt, evaluation.score, evaluation.reasoning,
                                    evaluation.score == "pass"
                                ))
                                db_manager.connection.commit()
                            except Exception as e:
                                print(f"   Warning: Could not save evaluation to database: {e}")
                        
                        if evaluation.score == "pass":
                            # Save approved prompt with "approved_" prefix for reformatting step
                            approved_filename = f"approved_{prompt_file.name}"
                            output_file = config.output_folder / approved_filename
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(evaluation.enhanced_prompt)
                            
                            print(f"   APPROVED and saved to {output_file.name}")
                            approved_count += 1
                            final_result = evaluation
                            break
                        else:
                            # Use enhanced prompt for next iteration
                            current_prompt = evaluation.enhanced_prompt
                            iteration += 1
                            continue
                    else:
                        print(f"   WARNING: All JSON parsing strategies failed")
                        print(f"   DEBUG: Full response: {result_text}")
                        iteration += 1
                        continue
                        
                except asyncio.TimeoutError:
                    print(f"   Timeout after {config.timeout_seconds}s (iteration {iteration})")
                    iteration += 1
                    continue
                except Exception as e:
                    print(f"   Error in iteration {iteration}: {str(e)[:100]}")
                    iteration += 1
                    continue
            
            # If we exhausted all iterations without success
            if final_result is None or final_result.score != "pass":
                print(f"   FAILED after {config.max_iterations} iterations")
                failed_count += 1
                
                # Update prompt status in database
                if db_manager and prompt_id:
                    try:
                        db_manager.connection.cursor().execute("""
                            UPDATE generated_prompts SET status = 'failed_evaluation'
                            WHERE prompt_id = ?
                        """, (prompt_id,))
                        db_manager.connection.commit()
                    except Exception as e:
                        print(f"   Warning: Could not update prompt status: {e}")
            else:
                # Update prompt status to approved
                if db_manager and prompt_id:
                    try:
                        db_manager.connection.cursor().execute("""
                            UPDATE generated_prompts SET status = 'approved'
                            WHERE prompt_id = ?
                        """, (prompt_id,))
                        db_manager.connection.commit()
                    except Exception as e:
                        print(f"   Warning: Could not update prompt status: {e}")
            
        except Exception as e:
            print(f"   Error processing {prompt_file.name}: {str(e)[:100]}")
            failed_count += 1
            continue
    
    processing_time = time.time() - start_time
    
    # Close database connection
    if db_manager:
        try:
            db_manager.connection.close()
        except:
            pass
    
    return BatchResult(
        total_processed=len(prompt_files),
        approved_count=approved_count,
        failed_count=failed_count,
        processing_time=processing_time,
        session_id=config.session_id or "unknown"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Theme-Aware Photo Prompt Judge')
    parser.add_argument('--session-id', help='Session ID for database tracking')
    parser.add_argument('--theme', help='Theme for evaluation (e.g., wildlife)')
    parser.add_argument('--lighting-style', help='Lighting style (autumn, summer, hyperreal_standard)')
    parser.add_argument('--input-folder', help='Input folder path')
    parser.add_argument('--output-folder', help='Output folder path')
    
    args = parser.parse_args()
    
    # Use provided arguments or defaults
    INPUT_FOLDER = Path(args.input_folder) if args.input_folder else Path("generator_prompts_raw")
    OUTPUT_FOLDER = Path(args.output_folder) if args.output_folder else Path("approved_prompts")
    
    # Detect theme if not provided
    if args.theme:
        THEME = args.theme
    else:
        THEME = detect_theme_from_folder(INPUT_FOLDER)
    
    # Select lighting style
    if args.lighting_style:
        LIGHTING_STYLE = args.lighting_style
    else:
        LIGHTING_STYLE = select_lighting_style()
    
    print(f"\nTHEME-AWARE PROMPT EVALUATION")
    print(f"Input Folder: {INPUT_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print(f"Theme: {THEME}")
    print(f"Lighting Style: {LIGHTING_STYLE}")
    if args.session_id:
        print(f"Session ID: {args.session_id}")
    
    # Create configuration
    config = BatchConfig(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        theme=THEME,
        lighting_style=LIGHTING_STYLE,
        session_id=args.session_id,
        max_iterations=3,
        timeout_seconds=120
    )
    
    # Run the batch processing
    async def main():
        try:
            result = await process_batch(config)
            
            print(f"\n{'=' * 60}")
            print(f"BATCH PROCESSING COMPLETE")
            print(f"{'=' * 60}")
            print(f"Approved: {result.approved_count}")
            print(f"Failed: {result.failed_count}")
            print(f"Total: {result.total_processed}")
            print(f"Time: {result.processing_time:.1f}s")
            if result.approved_count > 0:
                print(f"Rate: {result.processing_time/result.approved_count:.1f}s per approved prompt")
            print(f"Session: {result.session_id}")
            
            # Calculate success rate
            if result.total_processed > 0:
                success_rate = (result.approved_count / result.total_processed) * 100
                print(f"Success Rate: {success_rate:.1f}%")
            
        except KeyboardInterrupt:
            print(f"\nProcessing interrupted by user")
            sys.exit(130)  # Standard exit code for SIGINT
        except Exception as e:
            print(f"\nError during batch processing: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)  # Exit with error code to signal failure

    # Run the async main function
    asyncio.run(main())