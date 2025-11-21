import asyncio
import os
import traceback

# Try importing OpenEvolve first to verify it exists
try:
    from openevolve import OpenEvolve
except ImportError:
    print("CRITICAL: 'openevolve' package not found.")
    print("Please run: pip install openevolve")
    exit(1)

async def main():
    # Ensure files exist before running
    required_files = ["initial_program.py", "evaluator.py", "config.yaml"]
    for f in required_files:
        if not os.path.exists(f):
            print(f"Error: {f} not found in current directory.")
            return

    print("Initializing OpenEvolve...")
    try:
        evolve = OpenEvolve(
            initial_program_path="initial_program.py",
            evaluation_file="evaluator.py",
            config_path="config.yaml"
        )
        
        print("Starting evolution loop...")
        best_program = await evolve.run()
        
        print("\nEvolution Complete.")
        print("Best program found:")
        print(best_program)
        
    except Exception as e:
        print(f"\nRuntime Error detected!")
        print(f"Details: {str(e)}")
        # Print full traceback for debugging imports
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())