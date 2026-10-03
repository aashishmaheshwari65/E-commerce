import argparse
from .warehouse_builder import build_warehouse

def main():
    parser = argparse.ArgumentParser(description="Build Data Warehouse")
    args = parser.parse_args()
    
    print("Starting Data Warehouse Build...")
    try:
        manifest = build_warehouse()
        print("Build completed successfully.")
        print(manifest)
    except Exception as e:
        print(f"Error during build: {e}")

if __name__ == "__main__":
    main()
