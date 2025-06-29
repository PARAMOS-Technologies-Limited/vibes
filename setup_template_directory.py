#!/usr/bin/env python3
"""
Setup script to copy the current app directory to an external template location.
This allows the Hovel system to use external templates instead of the local app directory.
"""

import os
import shutil
import sys
from pathlib import Path

def setup_template_directory():
    """Copy the current app directory to the external template location"""
    
    # Define paths
    current_app_dir = Path('app')
    template_base_dir = Path('/opt/hovel-templates')
    template_dir = template_base_dir / 'app-template'
    
    print(f"Setting up template directory at: {template_dir}")
    
    # Check if current app directory exists
    if not current_app_dir.exists():
        print(f"❌ Error: Current app directory '{current_app_dir}' not found!")
        print("Please make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Create template base directory if it doesn't exist
    template_base_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created template base directory: {template_base_dir}")
    
    # Remove existing template directory if it exists
    if template_dir.exists():
        print(f"🗑️  Removing existing template directory: {template_dir}")
        shutil.rmtree(template_dir)
    
    # Copy the app directory to the template location
    try:
        shutil.copytree(current_app_dir, template_dir)
        print(f"✅ Successfully copied app directory to: {template_dir}")
    except Exception as e:
        print(f"❌ Error copying app directory: {e}")
        sys.exit(1)
    
    # Verify the copy was successful
    if template_dir.exists():
        files = list(template_dir.rglob('*'))
        print(f"✅ Template directory created with {len(files)} files/directories")
        
        # List the files that were copied
        print("\n📁 Files in template directory:")
        for file_path in template_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(template_dir)
                print(f"  - {relative_path}")
    else:
        print("❌ Error: Template directory was not created successfully")
        sys.exit(1)
    
    # Set proper permissions
    try:
        os.chmod(template_dir, 0o755)
        for file_path in template_dir.rglob('*'):
            if file_path.is_file():
                os.chmod(file_path, 0o644)
        print("✅ Set appropriate permissions on template directory")
    except Exception as e:
        print(f"⚠️  Warning: Could not set permissions: {e}")
    
    print("\n🎉 Template directory setup complete!")
    print(f"\n📋 Next steps:")
    print(f"1. Restart your Docker container to pick up the new template path")
    print(f"2. Test creating a new branch to verify it works")
    print(f"3. Once confirmed working, you can remove the local 'app' directory")
    print(f"\n🔧 To test, run:")
    print(f"   curl -X POST http://localhost:8000/api/branch \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"branch_name\": \"test-template\"}}'")

def remove_local_app_directory():
    """Remove the local app directory after confirming template works"""
    
    current_app_dir = Path('app')
    
    if not current_app_dir.exists():
        print("❌ Local app directory doesn't exist")
        return
    
    print(f"🗑️  Removing local app directory: {current_app_dir}")
    
    try:
        shutil.rmtree(current_app_dir)
        print("✅ Local app directory removed successfully")
        print("\n📋 The system will now use the external template at:")
        print(f"   /opt/hovel-templates/app-template")
    except Exception as e:
        print(f"❌ Error removing local app directory: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--remove-local":
        remove_local_app_directory()
    else:
        setup_template_directory() 