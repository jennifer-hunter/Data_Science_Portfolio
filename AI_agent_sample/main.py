"""
AI Agent Automation Pipeline - Main Entry Point
Orchestrates the complete image generation pipeline from prompt creation to final images

PIPELINE STAGES:
1. Create Prompts: Generate raw creative prompts from themes
2. Prompt Judge: Evaluate and approve quality prompts
3. Reformatter: Convert prompts to generator-friendly format
4. Image Generator: Generate images from prompts

USAGE:
    # Interactive menu (recommended):
    python main.py

    # Command-line mode:
    python main.py --session-id my_session --theme christmas

    # Run specific stages only:
    python main.py --session-id my_session --stages judge,reformat

    # Skip stages (e.g., already have prompts):
    python main.py --session-id my_session --skip-judge --skip-reformat
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import os


class PipelineOrchestrator:
    """Orchestrates the complete AI image generation pipeline"""

    def __init__(self, session_id: str, theme: str = None):
        self.session_id = session_id
        self.theme = theme
        self.start_time = datetime.now()
        self.results = {
            'create': {'status': 'pending', 'error': None},
            'judge': {'status': 'pending', 'error': None},
            'reformat': {'status': 'pending', 'error': None},
            'generate': {'status': 'pending', 'error': None}
        }

    def print_banner(self):
        """Print welcome banner"""
        print("=" * 80)
        print("  AI AGENT AUTOMATION PIPELINE")
        print("=" * 80)
        print(f"  Session ID: {self.session_id}")
        if self.theme:
            print(f"  Theme: {self.theme}")
        print(f"  Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

    def print_stage_header(self, stage_num: int, stage_name: str, description: str):
        """Print stage header"""
        print("\n" + "=" * 80)
        print(f"  STAGE {stage_num}: {stage_name}")
        print("=" * 80)
        print(f"  {description}")
        print("=" * 80)
        print()

    def run_stage(self, stage_key: str, script_path: str, args: list) -> bool:
        """
        Run a pipeline stage

        Args:
            stage_key: Key for tracking in results dict
            script_path: Path to Python script
            args: Command-line arguments for the script

        Returns:
            True if successful, False if failed
        """
        try:
            # Build command
            command = [sys.executable, script_path] + args

            print(f"[COMMAND] Running: {' '.join(command)}")
            print()

            # Run the script
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=False  # Show output in real-time
            )

            self.results[stage_key]['status'] = 'success'
            print(f"\n[SUCCESS] Stage completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.results[stage_key]['status'] = 'failed'
            self.results[stage_key]['error'] = str(e)
            print(f"\n[ERROR] Stage failed with error: {e}")
            return False

        except FileNotFoundError:
            self.results[stage_key]['status'] = 'failed'
            self.results[stage_key]['error'] = f"Script not found: {script_path}"
            print(f"\n[ERROR] Script not found: {script_path}")
            return False

        except Exception as e:
            self.results[stage_key]['status'] = 'failed'
            self.results[stage_key]['error'] = str(e)
            print(f"\n[ERROR] Unexpected error: {e}")
            return False

    def run_create_prompts(self, output_folder: str = None) -> bool:
        """Run Stage 1: Create Prompts"""
        self.print_stage_header(
            1,
            "CREATE PROMPTS",
            "Generating raw creative prompts from theme"
        )

        script = "text_generation/create_prompts.py"
        args = ["--session-id", self.session_id]

        if self.theme:
            args.extend(["--theme", self.theme])
        if output_folder:
            args.extend(["--output-folder", output_folder])

        return self.run_stage('create', script, args)

    def run_prompt_judge(self, input_folder: str = None, output_folder: str = None) -> bool:
        """Run Stage 2: Prompt Judge"""
        self.print_stage_header(
            2,
            "PROMPT JUDGE",
            "Evaluating and approving quality prompts"
        )

        script = "evaluation/prompt_judge.py"
        args = ["--session-id", self.session_id]

        if self.theme:
            args.extend(["--theme", self.theme])
        if input_folder:
            args.extend(["--input-folder", input_folder])
        if output_folder:
            args.extend(["--output-folder", output_folder])

        return self.run_stage('judge', script, args)

    def run_reformatter(self, input_folder: str = None, output_folder: str = None) -> bool:
        """Run Stage 3: Reformatter"""
        self.print_stage_header(
            3,
            "REFORMATTER",
            "Converting prompts to generator-optimized format"
        )

        script = "evaluation/reformatter.py"
        args = ["--session-id", self.session_id]

        if input_folder:
            args.extend(["--input-folder", input_folder])
        if output_folder:
            args.extend(["--output-folder", output_folder])

        return self.run_stage('reformat', script, args)

    def run_image_generator(self, prompt_folder: str = None, save_dir: str = None) -> bool:
        """Run Stage 4: Image Generator"""
        self.print_stage_header(
            4,
            "IMAGE GENERATOR",
            "Generating images from optimized prompts"
        )

        script = "image_generation/image_generator.py"
        args = ["--session-id", self.session_id]

        if prompt_folder:
            args.extend(["--prompt-folder", prompt_folder])
        if save_dir:
            args.extend(["--save-dir", save_dir])

        return self.run_stage('generate', script, args)

    def print_summary(self):
        """Print pipeline execution summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print("\n\n" + "=" * 80)
        print("  PIPELINE EXECUTION SUMMARY")
        print("=" * 80)
        print(f"  Session ID: {self.session_id}")
        print(f"  Duration: {duration.total_seconds():.2f} seconds")
        print("=" * 80)

        # Stage results
        stage_names = {
            'create': 'Stage 1: Create Prompts',
            'judge': 'Stage 2: Prompt Judge',
            'reformat': 'Stage 3: Reformatter',
            'generate': 'Stage 4: Image Generator'
        }

        all_success = True
        for key, name in stage_names.items():
            status = self.results[key]['status']

            if status == 'success':
                print(f"  [SUCCESS] {name}: SUCCESS")
            elif status == 'failed':
                print(f"  [ERROR] {name}: FAILED")
                if self.results[key]['error']:
                    print(f"    Error: {self.results[key]['error']}")
                all_success = False
            elif status == 'skipped':
                print(f"  [SKIP] {name}: SKIPPED")
            else:
                print(f"  [PENDING] {name}: NOT RUN")

        print("=" * 80)

        if all_success:
            print("  [SUCCESS] PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            print("  [WARNING] PIPELINE COMPLETED WITH ERRORS")

        print("=" * 80)
        print()

        return all_success


def get_available_themes():
    """Get list of available theme files"""
    themes_dir = Path("evaluation/themes/definitions")
    if not themes_dir.exists():
        return []

    theme_files = list(themes_dir.glob("*.yaml")) + list(themes_dir.glob("*.yml"))
    themes = [f.stem for f in theme_files]
    return sorted(themes)


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu_header(title):
    """Print a styled menu header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def get_input(prompt, default=None, validation_func=None):
    """
    Get user input with optional default and validation

    Args:
        prompt: The prompt to display
        default: Default value if user presses Enter
        validation_func: Optional function to validate input

    Returns:
        User input string
    """
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()

        if not user_input and not default:
            print("  [WARNING] This field is required. Please enter a value.")
            continue

        if validation_func:
            is_valid, error_msg = validation_func(user_input or default)
            if not is_valid:
                print(f"  [WARNING] {error_msg}")
                continue

        return user_input or default


def get_yes_no(prompt, default=True):
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()

        if not response:
            return default

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("  [WARNING] Please enter 'y' or 'n'")


def get_choice(prompt, options, allow_none=False):
    """
    Get a choice from a list of options

    Args:
        prompt: The prompt to display
        options: List of options to choose from
        allow_none: If True, user can skip by pressing Enter

    Returns:
        Selected option or None
    """
    print(f"\n{prompt}")
    print("-" * 60)

    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    if allow_none:
        print(f"  0. Skip / None")

    print("-" * 60)

    while True:
        choice = input("Enter your choice (number): ").strip()

        if allow_none and (not choice or choice == '0'):
            return None

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
            else:
                print(f"  [WARNING] Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("  [WARNING] Please enter a valid number")


def interactive_menu():
    """Interactive menu for configuring pipeline"""
    clear_screen()

    print("=" * 80)
    print("  🎨 AI AGENT AUTOMATION PIPELINE - Interactive Setup")
    print("=" * 80)
    print("\n  Welcome! Let's configure your image generation pipeline.\n")

    config = {}

    # Auto-generate Session ID
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    config['session_id'] = session_id
    print(f"📝 Session ID: {session_id}\n")

    # Always run all stages
    config['run_create'] = True
    config['run_judge'] = True
    config['run_reformat'] = True
    config['run_generate'] = True

    # Theme Selection (required)
    print_menu_header("Select a Theme")

    themes = get_available_themes()

    if themes:
        print("Available themes:")
        for theme in themes:
            print(f"  • {theme}")
        print()

        theme_choice = get_choice("Select a theme:", themes, allow_none=False)
        config['theme'] = theme_choice
    else:
        print("[WARNING] No themes found in evaluation/themes/definitions/")
        print("[WARNING] Please add theme files before running the pipeline.")
        sys.exit(1)

    # Set default configuration (advanced options removed)
    config['judge_output'] = None
    config['reformat_output'] = None
    config['save_dir'] = None
    config['stop_on_error'] = False

    # Summary
    print_menu_header("Configuration Summary")

    print("📋 Your pipeline configuration:")
    print("-" * 60)
    print(f"  Session ID:       {config['session_id']}")
    print(f"  Theme:            {config['theme']}")
    print(f"  ")
    print(f"  Pipeline:         Full (All 4 stages)")
    print(f"    1. Create Prompts")
    print(f"    2. Prompt Judge")
    print(f"    3. Reformatter")
    print(f"    4. Image Generator")

    print("-" * 60)

    # Confirmation
    print()
    proceed = get_yes_no("🚀 Ready to start the pipeline?", default=True)

    if not proceed:
        print("\n❌ Pipeline cancelled by user.")
        sys.exit(0)

    return config


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='AI Agent Automation Pipeline - Complete workflow orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline:
  python main.py --session-id christmas_2025 --theme christmas

  # Run specific stages only:
  python main.py --session-id my_session --stages judge,reformat

  # Skip certain stages:
  python main.py --session-id my_session --skip-judge

  # Custom folders:
  python main.py --session-id my_session --prompt-folder my_prompts --save-dir my_images
        """
    )

    # Required arguments
    parser.add_argument(
        '--session-id',
        type=str,
        required=True,
        help='Unique session identifier for this pipeline run'
    )

    # Optional arguments
    parser.add_argument(
        '--theme',
        type=str,
        help='Theme for prompt generation (e.g. wildlife)'
    )

    # Stage control
    parser.add_argument(
        '--stages',
        type=str,
        help='Comma-separated list of stages to run (judge,reformat,generate). Default: all'
    )

    parser.add_argument(
        '--skip-judge',
        action='store_true',
        help='Skip the prompt judge stage'
    )

    parser.add_argument(
        '--skip-reformat',
        action='store_true',
        help='Skip the reformatter stage'
    )

    parser.add_argument(
        '--skip-generate',
        action='store_true',
        help='Skip the image generation stage'
    )

    # Folder customization
    parser.add_argument(
        '--judge-input',
        type=str,
        help='Input folder for prompt judge (default: auto-detect)'
    )

    parser.add_argument(
        '--judge-output',
        type=str,
        help='Output folder for approved prompts (default: approved_prompts)'
    )

    parser.add_argument(
        '--reformat-input',
        type=str,
        help='Input folder for reformatter (default: approved_prompts)'
    )

    parser.add_argument(
        '--reformat-output',
        type=str,
        help='Output folder for reformatted prompts (default: generator_prompts)'
    )

    parser.add_argument(
        '--prompt-folder',
        type=str,
        help='Folder containing prompts for image generation (default: generator_prompts)'
    )

    parser.add_argument(
        '--save-dir',
        type=str,
        help='Directory to save generated images (default: generator_pics)'
    )

    # Execution control
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop pipeline if any stage fails (default: continue to next stage)'
    )

    return parser.parse_args()


def main():
    """Main pipeline orchestrator"""
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        # Interactive menu mode
        config = interactive_menu()

        # Create orchestrator
        orchestrator = PipelineOrchestrator(config['session_id'], config.get('theme'))
        orchestrator.print_banner()

        # Run stages based on interactive config
        run_create = config['run_create']
        run_judge = config['run_judge']
        run_reformat = config['run_reformat']
        run_generate = config['run_generate']
        stop_on_error = config.get('stop_on_error', False)

        # Folder config
        judge_output = config.get('judge_output')
        reformat_output = config.get('reformat_output')
        save_dir = config.get('save_dir')

    else:
        # Command-line mode
        args = parse_arguments()

        # Create orchestrator
        orchestrator = PipelineOrchestrator(args.session_id, args.theme)
        orchestrator.print_banner()

        # Determine which stages to run
        run_create = not args.skip_create if hasattr(args, 'skip_create') else True
        run_judge = not args.skip_judge
        run_reformat = not args.skip_reformat
        run_generate = not args.skip_generate

        # If --stages specified, override
        if args.stages:
            stages = [s.strip().lower() for s in args.stages.split(',')]
            run_create = 'create' in stages
            run_judge = 'judge' in stages
            run_reformat = 'reformat' in stages or 'reformatter' in stages
            run_generate = 'generate' in stages or 'generator' in stages

        stop_on_error = args.stop_on_error

        # Folder config
        judge_output = args.judge_output
        reformat_output = args.reformat_output
        save_dir = args.save_dir

    # Track overall success
    pipeline_success = True

    # STAGE 1: Create Prompts
    if run_create:
        success = orchestrator.run_create_prompts(
            output_folder=None  # Uses default: generator_prompts_raw
        )
        if not success:
            pipeline_success = False
            if stop_on_error:
                print("\n[STOPPED] Pipeline stopped due to error in Create Prompts stage")
                orchestrator.print_summary()
                sys.exit(1)
    else:
        orchestrator.results['create']['status'] = 'skipped'
        print("\n[SKIPPED] Stage 1: Create Prompts - Skipped per user request")

    # STAGE 2: Prompt Judge
    if run_judge:
        success = orchestrator.run_prompt_judge(
            input_folder=None,
            output_folder=judge_output
        )
        if not success:
            pipeline_success = False
            if stop_on_error:
                print("\n[STOPPED] Pipeline stopped due to error in Prompt Judge stage")
                orchestrator.print_summary()
                sys.exit(1)
    else:
        orchestrator.results['judge']['status'] = 'skipped'
        print("\n[SKIPPED] Stage 2: Prompt Judge - Skipped per user request")

    # STAGE 3: Reformatter
    if run_reformat:
        success = orchestrator.run_reformatter(
            input_folder=None,
            output_folder=reformat_output
        )
        if not success:
            pipeline_success = False
            if stop_on_error:
                print("\n[STOPPED] Pipeline stopped due to error in Reformatter stage")
                orchestrator.print_summary()
                sys.exit(1)
    else:
        orchestrator.results['reformat']['status'] = 'skipped'
        print("\n[SKIPPED] Stage 3: Reformatter - Skipped per user request")

    # STAGE 4: Image Generator
    if run_generate:
        success = orchestrator.run_image_generator(
            prompt_folder=None,
            save_dir=save_dir
        )
        if not success:
            pipeline_success = False
    else:
        orchestrator.results['generate']['status'] = 'skipped'
        print("\n[SKIPPED] Stage 4: Image Generator - Skipped per user request")

    # Print summary
    all_success = orchestrator.print_summary()

    # Exit with appropriate code
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[FATAL ERROR] Pipeline failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
