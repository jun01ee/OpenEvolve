import asyncio
import os
from openevolve import OpenEvolve

async def main():
    # Ensure files exist before running
    required_files = ["initial_program.py", "evaluator.py", "config.yaml"]
    for f in required_files:
        if not os.path.exists(f):
            print(f"Error: {f} not found in current directory.")
            return

    print("Initializing OpenEvolve...")
    evolve = OpenEvolve(
        initial_program_path="initial_program.py",
        evaluation_file="evaluator.py",
        config_path="config.yaml"
    )
    
    print("Starting evolution loop...")
    # Run the evolution (awaitable in recent versions)
    best_program = await evolve.run()
    
    print("\nEvolution Complete.")
    print("Best program found:")
    print(best_program)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ImportError:
        print("CRITICAL: 'openevolve' package not found.")
        print("Please run: pip install openevolve")
    except Exception as e:
        print(f"Runtime Error: {e}")
