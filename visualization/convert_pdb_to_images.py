import os
import subprocess

pymol_bin = "/home/musa/Desktop/Endeavours/SukoonSphere/Neuroscience/pymol/pymol"
input_dir = "/home/musa/Documents/augment-projects/foldingdiff/backbone_samples_with_history/sampled_pdb/sample_history/generated_0"
output_dir = "/home/musa/Documents/augment-projects/foldingdiff/visualization"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".pdb"):
        pdb_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        output_img = os.path.join(output_dir, f"{base_name}.png")

        pymol_script = f"""
load {pdb_path}
hide everything
show cartoon
set ray_trace_mode, 1
bg_color white
ray 800, 600
png {output_img}, dpi=300
quit
"""
        script_file = f"/tmp/{base_name}.pml"
        with open(script_file, "w") as f:
            f.write(pymol_script)

        print(f"Rendering {filename} → {output_img}")
        result = subprocess.run(
            [pymol_bin, "-cq", script_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Error rendering {filename}:\n{result.stderr}")
        else:
            print(f"✅ Done: {output_img}")

print("✅ All renderings finished.")
