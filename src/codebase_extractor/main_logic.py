import os
import sys
import time
import datetime
import uuid
import shutil
from pathlib import Path

import questionary
from halo import Halo
from termcolor import colored
from prompt_toolkit.styles import Style
from questionary import Validator, ValidationError

# Import from our modules
from . import config
from . import ui
from . import file_handler
from . import cli  # <-- New import

class NumberValidator(Validator):
    """Validates that the input is a positive integer."""
    def validate(self, document):
        try:
            value = int(document.text)
            if value <= 0:
                raise ValidationError(
                    message="Please enter a positive number.",
                    cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(
                message="Please enter a valid number.",
                cursor_position=len(document.text))

def main():
    """Main function to run the CLI application."""
    exit_message = colored("\nExtraction aborted by user. Closing Code Extractor. Goodbye.", "red")

    try:
        # The argparse logic is now neatly contained in the cli module.
        args = cli.parse_arguments()
        
        # Override config defaults with args if provided
        if args.output_dir:
            config.OUTPUT_DIR_NAME = args.output_dir
            # Also update the exclusion list to match
            config.EXCLUDED_DIRS.add(args.output_dir)

        ui.clear_screen()
        ui.print_banner(no_instructions=args.no_instructions)
        
        if not args.no_instructions:
            ui.show_instructions()
        else:
            input(colored("\nPress Enter to begin...", "green"))
            ui.clear_screen()

        # Use the path from args, which defaults to the current directory
        root_path = args.root.resolve()
        if not root_path.is_dir():
            print(colored(f"Error: The provided root path is not a valid directory: {root_path}", "red"))
            return

        select_style = Style([('qmark', 'fg:#FFA500'), ('pointer', 'fg:#FFA500'), ('highlighted', 'fg:black bg:#FFA500'), ('selected', 'fg:black bg:#FFA500')])
        checkbox_style = Style([('qmark', 'fg:#FFA500'), ('pointer', 'fg:#FFA500'), ('highlighted', 'fg:#FFA500'), ('selected', 'fg:#FFA500'), ('checkbox-selected', 'fg:#FFA500')])
        
        # --- Start collecting settings ---
        
        # Use args if provided, otherwise ask the user
        exclude_large = args.exclude_large_files if args.mode else questionary.select(
            "[1/2] -- Exclude files larger than 1MB?", 
            choices=["yes", "no"], 
            style=select_style, 
            instruction=" "
        ).ask()
        if exclude_large is None: raise KeyboardInterrupt
        exclude_large = exclude_large == "yes"
        print()

        selection_mode = args.mode if args.mode else questionary.select(
            "[2/2] -- What do you want to extract?", 
            choices=["everything", "specific"], 
            style=select_style, 
            instruction=" "
        ).ask()
        if selection_mode is None: raise KeyboardInterrupt

        folders_to_process = set()
        process_root_files = False
        
        run_ref = str(uuid.uuid4())
        run_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if selection_mode == "everything":
            folders_to_process.update([p for p in root_path.iterdir() if p.is_dir() and p.name not in config.EXCLUDED_DIRS])
            process_root_files = True
        else: # 'specific' mode
            scan_depth = args.depth
            if scan_depth is None:
                depth_str = questionary.text(
                    "-- How many levels deep should we scan for folders?",
                    default="3",
                    validate=NumberValidator,
                    style=select_style
                ).ask()
                if depth_str is None: raise KeyboardInterrupt
                scan_depth = int(depth_str)
            
            # Use args for folder selection if provided, otherwise show prompt
            if args.select_folders or args.select_root:
                if args.select_root:
                    process_root_files = True
                selected_paths_from_args = [root_path / p for p in args.select_folders]
                folders_to_process.update(selected_paths_from_args)
            else:
                folder_choices = file_handler.get_folder_choices(root_path, max_depth=scan_depth)
                selected_options = None
                confirm_exit = False
                checkbox_instruction = "(Arrows to move, Space to select, A to toggle, I to invert)"
                
                while not selected_options:
                    selection = questionary.checkbox(
                        "-- Select folders/sub-folders to extract (must select at least one):", 
                        choices=folder_choices, 
                        style=checkbox_style,
                        instruction=checkbox_instruction
                    ).ask()
                    if selection is None:
                        if confirm_exit: raise KeyboardInterrupt
                        confirm_exit = True
                        print(colored("\n[!] Press Ctrl+C again to exit.", "yellow"))
                        continue
                    confirm_exit = False
                    if not selection:
                        print(colored("[!] Error: You must make a selection.", "red"))
                        continue
                    selected_options = selection
                    break
                
                if "ROOT_SENTINEL" in selected_options:
                    process_root_files = True
                    selected_options.remove("ROOT_SENTINEL")
                
                selected_paths = [root_path / p for p in selected_options]
                sorted_paths = sorted(selected_paths, key=lambda p: len(p.parts))
                
                final_paths = set()
                for path in sorted_paths:
                    if not any(path.is_relative_to(parent) for parent in final_paths):
                        final_paths.add(path)
                folders_to_process.update(final_paths)

        print()
        total_files_extracted = 0

        for folder_path in sorted(list(folders_to_process)):
            with Halo(text=f"Extracting {folder_path.relative_to(root_path)}...", spinner="dots"):
                time.sleep(0.1)
                folder_md, folder_count = file_handler.extract_code_from_folder(folder_path, exclude_large)
            if folder_count > 0:
                metadata = {"run_ref": run_ref, "run_timestamp": run_timestamp, "folder_name": str(folder_path.relative_to(root_path)), "file_count": folder_count}
                file_handler.write_to_markdown_file(folder_md, metadata, root_path)
                total_files_extracted += folder_count
                print(f"✅ Extracted {folder_count} file(s) from: {folder_path.relative_to(root_path)}\n")
            else:
                print(f"[!] No extractable files in: {folder_path.relative_to(root_path)}\n")

        if process_root_files:
            root_display_name = f"root [{root_path.name}] (files in root folder only, excl. sub-folders)"
            with Halo(text=f"Extracting {root_display_name}...", spinner="dots"):
                time.sleep(0.1)
                root_md, root_count = file_handler.extract_code_from_root(root_path, exclude_large)
            if root_count > 0:
                metadata = {"run_ref": run_ref, "run_timestamp": run_timestamp, "folder_name": root_display_name, "file_count": root_count}
                file_handler.write_to_markdown_file(root_md, metadata, root_path)
                total_files_extracted += root_count
                print(f"✅ Extracted {root_count} file(s) from the root directory\n")
            else:
                print("[!] No extractable files in the root directory\n")
        
        try:
            width = shutil.get_terminal_size((80, 20)).columns
        except OSError:
            width = 80

        if total_files_extracted > 0:
            output_dir_path = Path(config.OUTPUT_DIR_NAME).resolve()
            print(colored(f"Success! A total of {total_files_extracted} file(s) have been extracted.", "grey", "on_green"))
            print(f"Files saved in: {colored(str(output_dir_path), 'cyan')}")
        else:
            print(colored("Extraction complete, but no files matched the criteria.", "yellow"))
        
        ui.print_footer()

    except KeyboardInterrupt:
        print(exit_message)
        sys.exit(0)