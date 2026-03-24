import subprocess
import argparse
import re
import os
from datetime import datetime
try:
    import toytree
    import toyplot.png
    HAS_TOYTREE = True
except ImportError:
    HAS_TOYTREE = False

def run_evolver(evolver_path, num_species, num_trees, seed, birth_rate, death_rate, sampling_fraction, mutation_rate, visualize):
    # Construct the directory name with date and parameters
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    param_str = (
        f"species{num_species}_trees{num_trees}_seed{seed}_"
        f"birthrate{birth_rate}_deathrate{death_rate}_"
        f"samplingfraction{sampling_fraction}_mutationrate{mutation_rate}"
    )
    output_dir = os.path.join("data", f"date_{date_str}_{param_str}")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Construct the input string for evolver
    input_str = f"2\n{num_species}\n{num_trees} {seed}\n1\n{birth_rate} {death_rate} {sampling_fraction} {mutation_rate}\n0\n"
    
    # evolver needs to be run in a directory with MCbase.dat
    work_dir = "/Users/mrzi/Documents/software/paml4/paml/examples/"
    
    try:
        process = subprocess.Popen(
            [evolver_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=work_dir
        )
        print(f"Running evolver with input:\n{repr(input_str)}")
        stdout, _ = process.communicate(input=input_str)
        
        # Regex to find the Newick string
        tree_matches = re.findall(r'(\(.*\);)', stdout)
        
        if tree_matches:
            # Create a separate file for each tree
            for i, tree_str in enumerate(tree_matches):
                tree_index = i + 1
                tree_filename = f"tree_{tree_index}.nwk"
                tree_path = os.path.join(output_dir, tree_filename)
                with open(tree_path, 'w') as f:
                    f.write(tree_str + '\n')
            
            # Visualization
            if visualize and HAS_TOYTREE:
                try:
                    num_to_viz = min(len(tree_matches), 9)
                    
                    # Create a 3x3 grid (or smaller if fewer trees)
                    rows = (num_to_viz + 2) // 3
                    cols = min(num_to_viz, 3)
                    
                    canvas = toyplot.Canvas(width=cols*400, height=rows*400, style={"background-color": "white"})
                    
                    for i in range(num_to_viz):
                        # r, c = divmod(i, 3)
                        tree = toytree.tree(tree_matches[i])
                        axes = canvas.cartesian(grid=(rows, cols, i))
                        axes.show = False # Hide axes
                        tree.draw(
                            axes=axes,
                            node_labels=False,
                            node_sizes=5,
                            tip_labels_colors="black"
                        )
                    
                    # Save the grid as a single PNG
                    grid_png_path = os.path.join(output_dir, "trees_grid.png")
                    toyplot.png.render(canvas, grid_png_path, scale=2.0)
                    print(f"Generated  grid visualization (first {num_to_viz} trees): {grid_png_path}")
                    
                except Exception as vis_e:
                    print(f"Could not visualize trees grid: {vis_e}")
            
            print(f"Successfully extracted {len(tree_matches)} tree(s) as separate files in {output_dir}")
        else:
            print("Failed to find Newick tree in output.")
            print("Stdout:", stdout)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PAML evolver to generate a rooted tree.")
    parser.add_argument("--evolver", default="/Users/mrzi/Documents/software/paml4/paml/src/evolver", help="Path to evolver binary")
    parser.add_argument("--species", type=int, default=10, help="Number of species")
    parser.add_argument("--trees", type=int, default=1, help="Number of trees")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--birth", type=float, default=1.0, help="Birth rate")
    parser.add_argument("--death", type=float, default=2.0, help="Death rate")
    parser.add_argument("--sampling", type=float, default=0.5, help="Sampling fraction")
    parser.add_argument("--mutation", type=float, default=1.0, help="Mutation rate (tree height)")
    parser.add_argument("--visualize", action="store_true", help="Generate PNG/PDF visualizations of the trees")

    args = parser.parse_args()

    run_evolver(
        args.evolver, args.species, args.trees, args.seed, 
        args.birth, args.death, args.sampling, args.mutation,
        args.visualize
    )
