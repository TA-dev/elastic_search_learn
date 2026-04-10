
import os
def merge_for_nominatim(target_dir="./osm_data"):
    # 2. Define paths
    output_file = os.path.join(target_dir, "middle_east_merged.osm.pbf")
    
    # Get all PBFs except the merged one itself
    files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) 
             if f.endswith('.pbf') and "merged" not in f]

    print(f"🛠️ Merging {len(files)} files into one...")
    
    # Run osmium merge. '--overwrite' is useful if you run this multiple times.
    cmd = ["osmium", "merge"] + files + ["-o", output_file, "--overwrite"]
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success! Merged file saved at: {output_file}")
        print(f"📦 Final Size: {os.path.getsize(output_file)/1024**3:.2f} GB")
    else:
        print(f"❌ Merge failed: {result.stderr}")



if __name__ == "__main__":    merge_for_nominatim()