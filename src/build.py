#!/usr/bin/env python3
"""
Simple PyInstaller build script
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_app(app_name, platform_override=None):
    """
    Build executable with PyInstaller
    
    Args:
        app_name: Name of your application
        platform_override: 'windows' or 'macos' (optional)
    """
    
    # Detect platform if not specified
    if platform_override:
        target_platform = platform_override.lower()
    else:
        import platform
        system = platform.system().lower()
        if system == 'darwin':
            target_platform = 'macos'
        else:
            target_platform = system  # 'windows' or 'linux'
    
    print(f"Building '{app_name}' for {target_platform}")
    print("-" * 40)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("ERROR: app.py not found in current directory!")
        return False
    
    # Prepare PyInstaller arguments
    args = [
        "pyinstaller",
        "--onefile",           # Single executable
        "--windowed",          # No console for GUI apps
        "--clean",            # Clean build cache
        "--name", app_name,
    ]
    
    # Platform-specific settings
    if target_platform == "windows":
        args.append("--noconsole")  # Hide console window
        # Optional: Add icon for Windows
        if Path("icon.ico").exists():
            args.extend(["--icon", "icon.ico"])
    
    elif target_platform == "macos":
        # Optional: Add icon for macOS
        if Path("icon.icns").exists():
            args.extend(["--icon", "icon.icns"])
    
    # Add the main script
    args.append("app.py")
    
    # Run PyInstaller
    print(f"Running: {' '.join(args)}")
    print("-" * 40)
    
    result = subprocess.run(args, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Build successful!")
        
        # Show output location
        if target_platform == "windows":
            output_path = Path("dist") / f"{app_name}.exe"
        elif target_platform == "macos":
            output_path = Path("dist") / f"{app_name}.app"
        else:
            output_path = Path("dist") / app_name
        
        if output_path.exists():
            print(f"\nOutput: {output_path}")
            
            # Show file size
            if output_path.is_file():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"Size: {size_mb:.1f} MB")
            
            print(f"\nTo run your app:")
            if target_platform == "windows":
                print(f"  Double-click: dist\\{app_name}.exe")
            elif target_platform == "macos":
                print(f"  Double-click: dist/{app_name}.app")
                print(f"  Or run: open dist/{app_name}.app")
        return True
    else:
        print("✗ Build failed!")
        print(result.stderr)
        return False

def cleanup():
    """Remove build artifacts"""
    print("\nCleaning up...")
    
    folders_to_remove = ["build", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    for folder in folders_to_remove:
        path = Path(folder)
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed: {folder}")
    
    import glob
    for spec in glob.glob("*.spec"):
        os.remove(spec)
        print(f"  Removed: {spec}")
    
    print("✓ Cleanup complete!")

def main():
    """Main function - parse arguments and run build"""
    
    # Simple argument parsing
    if len(sys.argv) < 2:
        print("Usage: python build.py APP_NAME [platform]")
        print("\nArguments:")
        print("  APP_NAME    Name of your application")
        print("  platform    Optional: 'windows' or 'macos' (default: auto-detect)")
        print("\nExamples:")
        print("  python build.py MyApp")
        print("  python build.py MyApp windows")
        print("  python build.py MyApp macos")
        return
    
    app_name = sys.argv[1]
    platform_override = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate platform
    if platform_override and platform_override.lower() not in ['windows', 'macos']:
        print(f"ERROR: Platform must be 'windows' or 'macos', not '{platform_override}'")
        return
    
    # Run build
    success = build_app(app_name, platform_override)
    
    # Always cleanup
    cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()