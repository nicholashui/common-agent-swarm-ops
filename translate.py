import argparse
import os

# Load environment variables from .env file

try:
    from opencc import OpenCC
except ImportError:
    print("Error: opencc-python-reimplemented is not installed")
    print("Please install it using: pip install opencc-python-reimplemented")
    exit(1)


def list_pattern_files_strict(directory: str, filename: str):
    if not directory:
        print(f"目錄 '{directory}' 不存在")
        return []
    if not os.path.isdir(directory):
        print(f"目錄 '{directory}' 不存在")
        return []

    matching_files = []
    for root, _, files in os.walk(directory):
        for current_file in files:
            if current_file == filename:
                matching_files.append((current_file, os.path.join(root, current_file)))

    return matching_files

def convert_to_traditional(test_first_one: bool = False):
    """
    Convert simplified Chinese to traditional Chinese for all text files
    in the current directory.
    """
    # Initialize OpenCC converter (simplified to traditional)
    cc = OpenCC('s2t')  # s2t = Simplified to Traditional
    
    temp_files = list_pattern_files_strict("business", "user_guide.script.hk.txt")
    if test_first_one:
        temp_files = temp_files[:1]

    for _, filename in temp_files:
        print(f"Processing: {filename}")
        
        try:
            # Read the file
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert simplified to traditional
            converted_content = cc.convert(content)
            
            # Check if any conversion happened
            if content == converted_content:
                print(f"  No changes (already traditional or no Chinese)")
            else:
                # Write back to the file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                print(f"  ✓ Converted successfully")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nCompleted processing files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-first-one",
        action="store_true",
        help="Process only the first matched file for testing",
    )
    args = parser.parse_args()

    convert_to_traditional(test_first_one=args.test_first_one)
