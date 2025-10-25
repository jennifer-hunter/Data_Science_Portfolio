"""
Theme-Aware Creative Prompt Generator with Database Integration

INPUT DIRECTORIES:
- No direct input (generates from themes)

OUTPUT DIRECTORIES:
- Line 41: OUTPUT_DIR - Where prompt files are saved (generator_prompts_raw)

DATABASE INTEGRATION:
- Stores all generated prompts with metadata
- Tracks theme, approach type, variations
- Links to pipeline session for complete tracking
"""

import os
import sys
import random
import argparse
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
# Add path for database and theme loader
current_dir = Path(__file__).parent
database_dir = current_dir.parent / "database"
if str(database_dir) not in sys.path:
    sys.path.insert(0, str(database_dir))

from database_utils import DatabaseManager

# Import security utilities
try:
    from security_utils import sanitize_filename
except ImportError:
    print("[WARNING] Security utilities not available")
    sanitize_filename = lambda x: x.replace('/', '_').replace('\\', '_').replace('..', '_')

themes_dir = current_dir.parent / "evaluation" / "themes"
if str(themes_dir) not in sys.path:
    sys.path.insert(0, str(themes_dir))

# Import theme loader for mixed theme support
try:
    # Add evaluation path for proper imports
    eval_path = current_dir.parent / "evaluation"
    if str(eval_path) not in sys.path:
        sys.path.insert(0, str(eval_path))
    
    from themes.theme_loader import get_registry as get_theme_registry, theme_exists
    MIXED_THEMES_SUPPORTED = True
    print("[OK] Mixed theme support enabled")
except ImportError as e:
    print(f"[WARNING] Mixed theme support not available: {e}")
    MIXED_THEMES_SUPPORTED = False
    get_theme_registry = None
    theme_exists = None

# Load environment variables
config_env = Path(__file__).parent.parent / "config" / ".env"
if config_env.exists():
    load_dotenv(config_env)
else:
    load_dotenv()  # Try default locations
client = None

def get_openai_client():
    """Get OpenAI client, initializing if necessary"""
    global client
    if client is None:
        # Try different ways to get the API key
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            # Try loading from config directory
            config_dir = Path(__file__).parent.parent / "config"
            env_file = config_dir / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or add it to config/.env")
        
        client = OpenAI(api_key=api_key)
    
    return client

# === Enhanced Settings ===
OUTPUT_DIR = "generator_prompts_raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROMPT_CONFIG = {
    "base_prompts_per_theme": 1,
    "variations_per_base": 1,
    "bases_to_vary": 1
}


def ask_gpt(messages, model="gpt-4o"):
    # Add system message to enforce no-people rule
    enhanced_messages = [
        {"role": "system", "content": "IMPORTANT: Never include people, humans, children, kids, minors, babies, adults, or anyone in any generated prompts. Focus only on subjects without people - animals, landscapes, objects, nature, architecture, etc."}
    ] + messages
    
    response = get_openai_client().chat.completions.create(
        model=model,
        messages=enhanced_messages,
        temperature=1.1
    )
    return response.choices[0].message.content.strip()


def generate_theme_prompts(theme="default", session_id=None, db_manager=None):
    """Generate prompts specifically tailored to the given theme with database integration"""

    print(f"[DEBUG] MIXED_THEMES_SUPPORTED: {MIXED_THEMES_SUPPORTED}")
    print(f"[DEBUG] theme_exists function available: {theme_exists is not None}")
    if theme_exists:
        theme_exists_result = theme_exists(theme)
        print(f"[DEBUG] theme_exists('{theme}'): {theme_exists_result}")

    if MIXED_THEMES_SUPPORTED and theme_exists and theme_exists(theme):
        try:
            # Try to load theme from YAML using theme loader
            theme_registry = get_theme_registry()
            print(f"[YAML] Loading theme from YAML: '{theme}'")
            yaml_theme_config = theme_registry.load_theme_config(theme)

            # Convert YAML theme config to old format for compatibility
            config = {
                "mood_pools": ["dynamic energy", "vibrant atmosphere", "authentic moment"],
                "lighting_scenarios": ["natural lighting", "ambient illumination", "documentary style"],
                "scene_elements": ["detailed objects", "environmental context", "realistic positioning"],
                "atmosphere_details": ["authentic arrangement", "natural physics", "discovered patterns"]
            }
            matched_theme = theme
            print(f"[YAML] Successfully loaded YAML theme: '{theme}'")
        except Exception as e:
            print(f"[ERROR] Failed to load theme from YAML: {e}")
            print(f"[ERROR] Theme '{theme}' not found. Please ensure the theme exists in evaluation/themes/definitions/")
            raise ValueError(f"Theme '{theme}' not found. YAML themes are required.")
    else:
        # Theme doesn't exist in YAML
        print(f"[ERROR] Theme '{theme}' not found in YAML theme system")
        print(f"[ERROR] Please ensure the theme exists in evaluation/themes/definitions/")
        raise ValueError(f"Theme '{theme}' not found. YAML themes are required.")

    print(f"[THEME] Using regular theme configuration: '{matched_theme}'")

    mood_pools = config["mood_pools"]
    lighting_scenarios = config["lighting_scenarios"]
    scene_elements = config["scene_elements"]
    atmosphere_details = config["atmosphere_details"]

    approaches = [
        "dynamic_action",
        "atmospheric_wide",
        "detail_focus",
        "cinematic_moment"
    ]

    prompts = []
    
    # Limit approaches based on base_prompts_per_theme config
    max_approaches = PROMPT_CONFIG["base_prompts_per_theme"]
    selected_approaches = approaches[:max_approaches]

    for approach in selected_approaches:
        if approach == "dynamic_action":
            mood = random.choice(mood_pools)
            scene = random.choice(scene_elements)
            lighting = random.choice(lighting_scenarios)

            messages = [
                {"role": "system",
                 "content": f"You are a professional photographer specializing in {theme} photography."},
                {"role": "user", "content": (
                    f"Create a hyperreal photographic scene for {theme} with {mood} mood. "
                    f"Scene focus: {scene}. Lighting: {lighting}. "
                    "Capture the essence and atmosphere of this theme. Show authentic moments and genuine emotion. "
                    "Professional photography style, rich colors, compelling composition. "
                    "Ultra-detailed, high resolution. No people. One perfect moment, one line."
                )}
            ]

        elif approach == "atmospheric_wide":
            atmosphere = random.choice(atmosphere_details)
            lighting = random.choice(lighting_scenarios)

            messages = [
                {"role": "system",
                 "content": f"You are a photographer capturing the full atmosphere of {theme} scenes."},
                {"role": "user", "content": (
                    f"Create a wide-angle photographic scene showing the full atmosphere of {theme}. "
                    f"Atmospheric details: {atmosphere}. Lighting: {lighting}. "
                    "Show the complete environment and context. Capture the mood and setting comprehensively. "
                    "Professional photography, rich atmosphere, immersive composition. "
                    "Ultra-detailed, wide perspective. No people. One encompassing scene, one line."
                )}
            ]

        elif approach == "detail_focus":
            detail = random.choice(atmosphere_details)
            mood = random.choice(mood_pools)

            messages = [
                {"role": "system",
                 "content": f"You are a photographer who finds meaning in the details of {theme} scenes."},
                {"role": "user", "content": (
                    f"Create a close-up photographic scene focusing on {theme} details. "
                    f"Detail focus: {detail}. Mood: {mood}. "
                    "Zoom in on the textures, objects, and small moments that define this theme. "
                    "Show the intimate details that tell the bigger story. "
                    "Macro photography style, sharp focus, rich textures. "
                    "Ultra-detailed, intimate perspective. No people. One revealing detail, one line."
                )}
            ]

        elif approach == "cinematic_moment":
            scene = random.choice(scene_elements)
            lighting = random.choice(lighting_scenarios)

            messages = [
                {"role": "system", "content": f"You are a cinematographer creating iconic {theme} imagery."},
                {"role": "user", "content": (
                    f"Create a cinematic photographic scene of {theme} that could be a movie poster. "
                    f"Scene: {scene}. Lighting: {lighting}. "
                    "Dramatic composition, perfect timing, iconic imagery that represents this theme. "
                    "Think commercial photography meets fine art. "
                    "Cinematic lighting, professional production value, striking visual impact. "
                    "Ultra-detailed, poster-worthy. No people. One iconic moment, one line."
                )}
            ]

        # Generate the prompt
        result = ask_gpt(messages)
        if result:
            prompts.append({
                'text': result,
                'approach': approach,
                'type': 'base'
            })

    return prompts, matched_theme


def generate_variations(base_prompts, session_id=None, db_manager=None):
    """Generate variations of the base prompts with database integration"""
    variations = []

    variation_styles = ["perspective_shift", "time_variation", "intensity_change"]
    
    # Use PROMPT_CONFIG to determine how many bases to vary and variations per base
    bases_to_vary = min(PROMPT_CONFIG["bases_to_vary"], len(base_prompts))
    variations_per_base = PROMPT_CONFIG["variations_per_base"]

    for base_prompt in base_prompts[:bases_to_vary]:  # Use config value
        for style in variation_styles[:variations_per_base]:  # Use config value
            if style == "perspective_shift":
                messages = [
                    {"role": "system",
                     "content": "You are a photographer who finds fresh perspectives on familiar scenes."},
                    {"role": "user", "content": (
                        f"Original scene: '{base_prompt['text']}'. "
                        "Create a variation with a completely different camera angle or perspective. "
                        "If it was wide, go close-up. "
                        "If it was ground level, go aerial. Keep the energy but change the viewpoint. "
                        "Professional photography, same theme essence, new perspective. "
                        "Ultra-detailed, fresh angle. No people. One line."
                    )}
                ]
            elif style == "time_variation":
                messages = [
                    {"role": "system",
                     "content": "You are a photographer who captures the same energy at different moments."},
                    {"role": "user", "content": (
                        f"Original scene: '{base_prompt['text']}'. "
                        "Show this same energy and theme but at a different time of day or moment in the event. "
                        "If it was peak action, show the buildup or aftermath. "
                        "If it was day, make it night. Keep the core feeling but shift the timing. "
                        "Professional photography, temporal variation. "
                        "Ultra-detailed, different moment. No people. One line."
                    )}
                ]
            elif style == "intensity_change":
                messages = [
                    {"role": "system",
                     "content": "You are a photographer who explores different energy levels of the same theme."},
                    {"role": "user", "content": (
                        f"Original scene: '{base_prompt['text']}'. "
                        "Create a variation with different energy intensity - either more intimate/calm or more explosive/intense. "
                        "Keep the same theme but dial the energy up or down significantly. "
                        "Professional photography, intensity variation. "
                        "Ultra-detailed, different energy level. No people. One line."
                    )}
                ]

            result = ask_gpt(messages)
            if result:
                variations.append({
                    'text': result,
                    'approach': base_prompt['approach'],
                    'type': 'variation',
                    'variation_style': style
                })

    return variations


def save_prompts_with_db(all_prompts, matched_theme, session_id, db_manager):
    """Save prompts to files and database with timestamps"""
    total_saved = 0

    # Use the original OUTPUT_DIR folder that your pipeline expects
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate timestamp for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for idx, prompt_data in enumerate(all_prompts, 1):
        # Create filename with theme prefix and timestamp
        # Security: sanitize theme name to prevent path traversal
        safe_theme = sanitize_filename(matched_theme.replace(' ', '_'))
        file_name = f"{safe_theme}_{timestamp}_{idx:02d}.txt"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        # Save to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(prompt_data['text'])

        # Save to database
        if db_manager and session_id:
            prompt_id = db_manager.insert_generated_prompt(
                session_id=session_id,
                theme=matched_theme,
                prompt_text=prompt_data['text'],
                prompt_type=prompt_data['type'],
                approach_type=prompt_data['approach'],
                variation_style=prompt_data.get('variation_style', ''),
                file_name=file_name,
                file_path=file_path
            )

            if prompt_id:
                print(f"Saved to DB: prompt_id {prompt_id}")

        total_saved += 1

    return total_saved


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate theme-specific prompts with database integration')
    parser.add_argument('--theme', type=str, default='default',
                        help='Theme for generating prompts (e.g., "aerial", "wildlife", "landscape", "architecture")')
    parser.add_argument('--session-id', type=str, required=True,
                        help='Pipeline session ID for database tracking')
    parser.add_argument('--base-prompts', type=int, default=None,
                        help='Number of base prompts to generate')
    parser.add_argument('--variations', type=int, default=None,
                        help='Number of variations per base prompt') 
    parser.add_argument('--bases-to-vary', type=int, default=None,
                        help='Number of base prompts to create variations for')
    args = parser.parse_args()

    theme = args.theme
    session_id = args.session_id
    
    # Override PROMPT_CONFIG if command-line arguments provided
    if args.base_prompts is not None:
        PROMPT_CONFIG["base_prompts_per_theme"] = args.base_prompts
    if args.variations is not None:
        PROMPT_CONFIG["variations_per_base"] = args.variations
    if args.bases_to_vary is not None:
        PROMPT_CONFIG["bases_to_vary"] = args.bases_to_vary

    print("[GENERATOR] THEME-AWARE CREATIVE PROMPT GENERATOR WITH DATABASE")
    print("=" * 60)
    print(f"[THEME] Theme: '{theme}'")
    print(f"[SESSION] Session ID: '{session_id}'")
    print(f"[INFO] Generating theme-specific prompts...")

    # Initialize database connection
    db_manager = None
    try:
        db_manager = DatabaseManager()
        print("[OK] Database connected for prompt tracking")
    except Exception as e:
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Will save to files only")

    try:
        # Generate theme-specific base prompts
        base_prompts, matched_theme = generate_theme_prompts(theme, session_id, db_manager)

        print(f"\n[GENERATED] Generated {len(base_prompts)} base prompts for '{matched_theme}':")
        for i, prompt in enumerate(base_prompts, 1):
            print(f"{i}. {prompt['text'][:100]}...")

        # Generate variations
        print(f"\n[VARIATIONS] Generating variations...")
        variations = generate_variations(base_prompts, session_id, db_manager)

        print(f"   Generated {len(variations)} variations")

        # Combine all prompts
        all_prompts = base_prompts + variations

        # Save all prompts to files and database
        total_saved = save_prompts_with_db(all_prompts, matched_theme, session_id, db_manager)

        # Update session statistics
        if db_manager and session_id:
            db_manager.update_pipeline_session_status(
                session_id,
                "running",
                total_prompts_generated=total_saved
            )

        print(f"\n[COMPLETE] GENERATION COMPLETE!")
        print(f"[SAVED] Saved {total_saved} unique '{matched_theme}' prompts to '{OUTPUT_DIR}/' folder")
        print(f"[DB] Tracked {total_saved} prompts in database")
        print(f"[STATS] {len(base_prompts)} base prompts + {len(variations)} variations")
        print(f"[APPROACHES] Theme-specific approaches used:")
        print(f"   - Dynamic action scenes")
        print(f"   - Atmospheric wide shots")
        print(f"   - Detail-focused captures")
        print(f"   - Cinematic compositions")
        print(f"   - Perspective variations")
        print(f"   - Time-based variations")
        print(f"   - Intensity variations")

    finally:
        if db_manager:
            db_manager.disconnect()


if __name__ == "__main__":
    main()