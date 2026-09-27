import argparse
import os
import sys
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="ReelScope Local Analytics Engine")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--token", default="", help="Optional session token (preferred via REELSCOPE_TOKEN env var)")
    parser.add_argument("--data-dir", default="", help="Optional custom data directory")

    args = parser.parse_args()

    if args.token:
        os.environ["REELSCOPE_TOKEN"] = args.token
    if args.data_dir:
        os.environ["REELSCOPE_DATA_DIR"] = args.data_dir

    # Force 127.0.0.1 for desktop safety
    host = "127.0.0.1" if args.host != "127.0.0.1" else args.host

    print(f"Starting ReelScope Engine on http://{host}:{args.port}")
    uvicorn.run("reelscope_engine.main:app", host=host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
