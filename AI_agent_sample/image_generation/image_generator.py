"""
Image Generator with Database Integration
Generates images from reformatted prompts using black-forest-labs/flux-krea-dev model
and tracks everything in database

INPUT DIRECTORIES:
- PROMPT_FOLDER: Where reformatted prompts are read from (generator_prompts)

OUTPUT DIRECTORIES:
- SAVE_DIR: Where generated images are saved locally (generator_pics)

DATABASE INTEGRATION:
- Links generated images to reformatted prompts
- Tracks image generator API responses and generation status
- Stores image metadata and file information
"""

import time
import requests
import replicate as generator  # Generic wrapper for image generation API
from dotenv import load_dotenv
import os
from datetime import datetime
import argparse
from pathlib import Path
from PIL import Image
import sys

# Load environment variables - find .env in config folder
def find_and_load_env():
    """Find and load .env file from config folder using relative paths only"""
    possible_env_locations = [
        Path(__file__).parent.parent / "config" / ".env",  # Standard project structure
        Path("config") / ".env",  # Running from project root
    ]

    for env_path in possible_env_locations:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded .env from: {env_path}")
            return True

    print("WARNING: No .env file found. Please create config/.env from config/.env.example")
    return False


# Load environment
find_and_load_env()

# Import database modules
try:
    # Add database path
    sys.path.insert(0, str(Path(__file__).parent.parent / "database"))
    from database_utils import DatabaseManager

    print("Database module loaded")
except ImportError as e:
    print(f"Database module not found: {e}")
    DatabaseManager = None

# Configuration
GENERATOR_API_TOKEN = os.getenv("GENERATOR_API_TOKEN")

# Input/Output directories
PROMPT_FOLDER = r"generator_prompts"  # Relative path from where script is run
SAVE_DIR = r"generator_pics"  # Relative path from where script is run

# Sanity check
if not GENERATOR_API_TOKEN:
    raise ValueError("ERROR: GENERATOR_API_TOKEN not found in .env file")

# Set image generator API token
os.environ["REPLICATE_API_TOKEN"] = GENERATOR_API_TOKEN  # SDK still expects REPLICATE_API_TOKEN


def ensure_directories():
    """Ensure input and output directories exist"""
    # Convert to absolute paths from project root
    project_root = Path(__file__).parent.parent

    global PROMPT_FOLDER, SAVE_DIR
    PROMPT_FOLDER = project_root / PROMPT_FOLDER
    SAVE_DIR = project_root / SAVE_DIR

    if not PROMPT_FOLDER.exists():
        print(f"ERROR: Prompt folder not found: {PROMPT_FOLDER}")
        return False

    SAVE_DIR.mkdir(exist_ok=True)
    print(f"Input: {PROMPT_FOLDER}")
    print(f"Output: {SAVE_DIR}")
    return True


def get_reformatted_id_from_db(db_manager, session_id: str, filename: str):
    """Get reformatted_id and related IDs from database based on filename"""
    try:
        query = """
                SELECT rp.reformatted_id, rp.prompt_id, rp.evaluation_id
                FROM reformatted_prompts rp
                WHERE rp.session_id = ? 
                  AND rp.file_name = ?
                """
        db_manager.cursor.execute(query, (session_id, filename))
        result = db_manager.cursor.fetchone()

        if result:
            return result['reformatted_id'], result['prompt_id'], result['evaluation_id']
        return None, None, None
    except Exception as e:
        print(f"ERROR: Error getting reformatted_id: {e}")
        return None, None, None


def get_image_dimensions(image_path: Path) -> tuple:
    """Get image dimensions using PIL"""
    try:
        with Image.open(image_path) as img:
            return img.width, img.height
    except Exception as e:
        print(f"WARNING: Could not get image dimensions: {e}")
        return None, None


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes"""
    try:
        return file_path.stat().st_size
    except Exception as e:
        print(f"WARNING: Could not get file size: {e}")
        return None


def sanitize_prompt(text: str) -> str:
    """Clean up prompt text for filesystem-safe filenames"""
    import re

    # First handle Unicode quotes and dashes
    text = (
        text.replace(""", '"')
        .replace(""", '"')
        .replace("'", "'")
        .replace("'", "'")
        .replace("–", "-")
        .replace("—", "-")
        .replace("…", "...")
    )

    # Replace filesystem-unsafe characters
    # Forward and back slashes -> underscores (main fix for the error)
    text = text.replace("/", "_").replace("\\", "_")

    # Remove or replace other illegal filename characters
    illegal_chars = '<>:"|?*'
    for char in illegal_chars:
        text = text.replace(char, "_")

    # Remove control characters and excessive whitespace
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Remove control chars
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
    text = text.strip()  # Remove leading/trailing spaces

    # Limit length to prevent filesystem issues (Windows has ~255 char limit)
    if len(text) > 200:
        text = text[:200].rsplit(' ', 1)[0]  # Cut at word boundary

    # Ensure it's not empty
    if not text:
        text = "generated_image"

    return text


def generate_image(prompt: str, db_manager=None, image_id=None) -> str:
    """Generate image via image generation API with database tracking and return local file path"""

    print(f"[SENDING] Sending prompt to image generator: {prompt[:100]}...")

    try:
        # Ensure directories exist
        if not ensure_directories():
            raise Exception("Failed to set up directories")

        # Generate session_id if not provided
        session_id = f"carousel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generation_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create filename base from prompt
        prompt_filename_base = sanitize_prompt(prompt)[:50]  # Limit length

        # Run image generator API with enhanced parameters
        prediction = generator.run(
            "black-forest-labs/flux-krea-dev",
            input={
                "prompt": prompt,
                "guidance": 2,
                "aspect_ratio": "3:4",  # Image story format
                "output_format": "png",
                "output_quality": 100,
                "go_fast": False,  # Higher quality, slower generation
                "megapixels": "1",  # Full resolution
                "num_outputs": 1,  # Number of images to generate
                "num_inference_steps": 50,  # Maximum quality steps
                "disable_safety_checker": False  # Safety checker
            }
        )

        # Get prediction ID for tracking
        if hasattr(prediction, 'id'):
            task_id = prediction.id
        elif hasattr(prediction, 'url'):
            # FileOutput object - use URL as task_id
            task_id = str(prediction.url)[:50]
        else:
            task_id = str(type(prediction).__name__)  # Use type name as fallback

        print(f"[STARTED] Image generation started: {task_id}")

        # Update database with task_id and API response
        if db_manager and image_id:
            try:
                query = """
                        UPDATE generated_images
                        SET generator_task_id = ?,
                            api_response = ?
                        WHERE image_id = ?
                        """
                api_response = {"prediction_id": task_id, "model": "black-forest-labs/flux-krea-dev", "status": "started"}
                db_manager.cursor.execute(query, (task_id, str(api_response), image_id))
                db_manager.connection.commit()
                print(f"[DATABASE] Updated database with prediction_id: {task_id}")
            except Exception as e:
                print(f"WARNING: Failed to update database with task_id: {e}")

        # Return the prediction object for the caller to process
        return prediction

    except Exception as e:
        error_msg = f"Unexpected error during image generation: {e}"
        print(f"ERROR: {error_msg}")

        # Update database with error
        if db_manager and image_id:
            db_manager.update_image_generation_status(image_id, "failed", error_message=error_msg)

        raise


def process_generator_result(prediction_result) -> list:
    """Process image generator API prediction result and return list of URLs"""
    try:
        # Generator API typically returns the result directly as a URL or list of URLs
        if isinstance(prediction_result, str):
            # Single image URL
            if prediction_result.startswith(('http://', 'https://')):
                print(f"[SUCCESS] Generated 1 image successfully!")
                return [prediction_result]
            else:
                raise ValueError(f"Invalid URL (not http/https): {prediction_result}")

        elif isinstance(prediction_result, list):
            # Multiple image URLs - could be strings or FileOutput objects
            urls = []
            for item in prediction_result:
                if isinstance(item, str):
                    if item.startswith(('http://', 'https://')):
                        urls.append(item)
                    else:
                        print(f"WARNING: Skipping invalid URL: {item}")
                elif hasattr(item, 'url'):
                    # FileOutput object with url attribute
                    url = str(item.url)
                    if url.startswith(('http://', 'https://')):
                        urls.append(url)
                    else:
                        print(f"WARNING: FileOutput has invalid URL: {url}")
                else:
                    print(f"WARNING: Unknown item type, cannot extract URL: {type(item)}")

            if not urls:
                raise ValueError("No valid URLs found in prediction result")
            print(f"[SUCCESS] Generated {len(urls)} images successfully!")
            return urls
        else:
            # Handle FileOutput objects and other formats
            if hasattr(prediction_result, 'url'):
                # FileOutput object with url attribute
                url = str(prediction_result.url)
                if url.startswith(('http://', 'https://')):
                    print(f"[SUCCESS] Generated 1 image successfully!")
                    return [url]
                else:
                    raise ValueError(f"FileOutput has invalid URL (not http/https): {url}")
            else:
                raise ValueError(f"Cannot extract URL from prediction result type: {type(prediction_result)}")
    except Exception as e:
        print(f"ERROR: Error processing generator API result: {e}")
        print(f"Result type: {type(prediction_result)}")
        print(f"Result value: {prediction_result}")
        raise


def download_images(urls: list, base_save_dir: Path, prompt_filename_base: str, prompt_text: str,
                    session_id: str, generation_timestamp: str, db_manager=None, image_id=None, reformatted_id=None) -> list:
    """Download images with database tracking and content management"""
    log_path = base_save_dir / "prompt_log.txt"
    downloaded_files = []

    for i, url in enumerate(urls):
        try:
            print(f"[DOWNLOADING] Downloading image {i + 1}/{len(urls)}...")
            # Ensure url is a string (handle FileOutput objects)
            url_str = str(url.url) if hasattr(url, 'url') else str(url)

            # Validate URL before attempting download
            if not url_str.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL (must start with http/https): {url_str}")

            img_data = requests.get(url_str).content
            # Use the same timestamp as database record
            image_filename = f"{prompt_filename_base}_{generation_timestamp}_{i + 1}.png"
            filepath = base_save_dir / image_filename

            # Save the image file locally
            with open(filepath, "wb") as f:
                f.write(img_data)
            print(f"Saved locally: {filepath}")

            # Get image metadata
            file_size = get_file_size(filepath)
            width, height = get_image_dimensions(filepath)

            # Update database with successful generation
            if db_manager and image_id:
                db_manager.update_image_generation_status(
                    image_id=image_id,
                    status="completed",
                    image_url=url_str,  # Use the url_str we already created
                    file_size=file_size,
                    width=width,
                    height=height
                )
                print(f"Updated database: image_id {image_id} completed")

            # Log the generation
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"Image File: {image_filename}\n")
                log.write(f"Original Prompt File: {prompt_filename_base}.txt\n")
                log.write(f"Prompt: {prompt_text}\n")
                log.write(f"Download URL: {url}\n")
                if file_size:
                    log.write(f"File Size: {file_size} bytes\n")
                if width and height:
                    log.write(f"Dimensions: {width}x{height}\n")
                log.write(f"Generated: {datetime.now().isoformat()}\n")
                if db_manager and image_id:
                    log.write(f"Database image_id: {image_id}\n")
                if reformatted_id:
                    log.write(f"Database reformatted_id: {reformatted_id}\n")
                log.write("\n" + "=" * 50 + "\n\n")

            downloaded_files.append(filepath)
            time.sleep(1)  # Rate limiting

        except Exception as e:
            error_msg = f"Failed to download image {i + 1}: {e}"
            print(f"ERROR: {error_msg}")
            if db_manager and image_id:
                db_manager.update_image_generation_status(image_id, "failed", error_message=error_msg)

    return downloaded_files


def main():
    """Main function using image generation API"""
    parser = argparse.ArgumentParser(description='Image generator with database tracking')
    parser.add_argument('--session-id', type=str, help='Pipeline session ID for database tracking')
    parser.add_argument('--prompt-folder', type=str, help='Input folder containing reformatted prompts')
    parser.add_argument('--save-dir', type=str, help='Output directory for generated images')
    args = parser.parse_args()

    print("[IMAGE GENERATOR] IMAGE GENERATOR WITH DATABASE TRACKING")
    print("=" * 70)
    print("[MODEL] Model: black-forest-labs/flux-krea-dev")
    print("[FEATURES] Features: Database tracking + content management")

    # Ensure directories exist
    if not ensure_directories():
        return

    session_id = args.session_id or os.getenv('PIPELINE_SESSION_ID',
                                              f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # Override paths if provided
    if args.prompt_folder:
        global PROMPT_FOLDER
        PROMPT_FOLDER = Path(args.prompt_folder)
    if args.save_dir:
        global SAVE_DIR
        SAVE_DIR = Path(args.save_dir)
        SAVE_DIR.mkdir(exist_ok=True)

    print(f"[SESSION] Session ID: {session_id}")
    print(f"[INPUT] Input: {PROMPT_FOLDER}")
    print(f"[OUTPUT] Output: {SAVE_DIR}")

    # Initialize database connection
    db_manager = None
    try:
        if session_id and DatabaseManager:
            db_manager = DatabaseManager()
            print("[DATABASE] Database connected for image tracking")
    except Exception as e:
        print(f"WARNING: Database connection failed: {e}")
        print("[INFO] Will save images without database tracking")

    try:
        # Find all prompt files
        all_prompt_files = list(PROMPT_FOLDER.glob("*.txt"))

        if not all_prompt_files:
            print(f"ERROR: No .txt files found in {PROMPT_FOLDER}")
            return

        # Filter by session if session_id is provided
        if session_id and db_manager:
            print(f"[FILES] Found {len(all_prompt_files)} total prompt files, filtering by session...")
            # Get expected files for this session from database
            query = "SELECT file_name FROM reformatted_prompts WHERE session_id = ?"
            db_manager.cursor.execute(query, (session_id,))
            session_files = [row['file_name'] for row in db_manager.cursor.fetchall()]
            
            # The database already has the correct generator filenames - no conversion needed!
            expected_files = session_files
            print(f"  [DATABASE] Expected files from database: {expected_files}")
            
            # Filter prompt files to only session files
            prompt_files = [f for f in all_prompt_files if f.name in expected_files]
            print(f"[FILTERED] Filtered to {len(prompt_files)} files for session {session_id}")
        else:
            prompt_files = all_prompt_files
            print(f"[PROCESSING] Processing all {len(prompt_files)} prompt files (no session filter)")
        print("=" * 70)

        successful_generations = 0
        total_images_generated = 0

        for prompt_file in prompt_files:
            try:
                # Read the prompt
                with open(prompt_file, "r", encoding="utf-8") as f:
                    prompt = sanitize_prompt(f.read().strip())

                print(f"\n[GENERATING] Generating for: {prompt_file.name}")
                print(f"[PROMPT] Prompt: {prompt[:100]}...")

                # Create timestamp for this generation (needed for all files)
                prompt_file_basename = prompt_file.stem
                generation_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                # Get database IDs if available
                reformatted_id = None
                prompt_id = None
                evaluation_id = None
                image_id = None

                if db_manager and session_id:
                    reformatted_id, prompt_id, evaluation_id = get_reformatted_id_from_db(
                        db_manager, session_id, prompt_file.name
                    )

                    if reformatted_id:
                        print(f"[LINKED] Linked to database: reformatted_id {reformatted_id}")

                        # Create image record in database
                        image_filename = f"{prompt_file_basename}_{generation_timestamp}_1.png"
                        image_filepath = SAVE_DIR / image_filename

                        image_id = db_manager.insert_generated_image(
                            reformatted_id=reformatted_id,
                            prompt_id=prompt_id,
                            session_id=session_id,
                            generator_task_id="",  # Will be updated after API call
                            image_file_name=image_filename,
                            image_file_path=str(image_filepath),
                            generator_prompt=prompt
                        )

                        if image_id:
                            print(f"[DATABASE] Created database record: image_id {image_id}")

                # Generate image using image generator API
                prediction_result = generate_image(prompt, db_manager, image_id)
                print(f"[PREDICTION] Image generation completed")

                # Process the prediction result to get URLs
                urls = process_generator_result(prediction_result)

                # Download images to local storage
                downloaded_files = download_images(
                    urls, SAVE_DIR, prompt_file_basename, prompt,
                    session_id, generation_timestamp, db_manager, image_id, reformatted_id
                )

                successful_generations += 1
                total_images_generated += len(downloaded_files)

                print(f"[SUCCESS] Successfully generated {len(downloaded_files)} images for {prompt_file.name}")

            except Exception as e:
                print(f"ERROR: Error generating for {prompt_file.name}: {e}")
                continue

        # Update session statistics
        if db_manager and session_id:
            try:
                db_manager.update_pipeline_session_status(
                    session_id,
                    "running",
                    total_images_generated=total_images_generated
                )
                print(f"[DATABASE] Updated session statistics")
            except Exception as e:
                print(f"WARNING: Failed to update session statistics: {e}")

        # Final summary
        print(f"\n{'=' * 70}")
        print("[COMPLETE] IMAGE GENERATION COMPLETE!")
        print(f"{'=' * 70}")
        print(f"[MODEL] Model: black-forest-labs/flux-krea-dev")
        print(f"[SUCCESS] Successfully processed: {successful_generations}/{len(prompt_files)} prompts")
        print(f"[IMAGES] Total images generated: {total_images_generated}")
        print(f"[SAVED] Local images saved to: {SAVE_DIR}")
        if db_manager:
            print(f"[DATABASE] All generation data tracked in database")
            print(f"[CONTENT] Approved content created for content management")

    finally:
        if db_manager:
            db_manager.disconnect()


if __name__ == "__main__":
    main()