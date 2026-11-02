import sys
import argparse
import tkinter as tk
import ctypes

import modules.encrypt_save as encrypt_save
import modules.decrypt_save as decrypt_save
from modules.manager import TwilightSaveManager
from ui.twilight_dawn import TwilightDawnUI

def launch_gui_dashboard():
    manager = TwilightSaveManager()
    app = TwilightDawnUI(manager)
    app.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Twilight Dawn Suite")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--encrypt", action="store_true")
    group.add_argument("--decrypt", type=str)
    group.add_argument("--build-db", action="store_true")
    parser.add_argument("--path", type=str, default=None)
    parser.add_argument("--wts", default="war3map.txt")
    parser.add_argument("--w3t", default="war3map_w3t.txt")
    parser.add_argument("--w3u", default="war3map_w3u.txt")
    parser.add_argument("--w3a", default="war3map_w3a.txt")
    parser.add_argument("--arrays", default="arrays2engine.txt")
    args = parser.parse_args()

    if args.encrypt:
        encrypt_save.run_encryption(config_path=args.path); sys.exit(0)
    elif args.decrypt:
        target_save = args.path if args.path else args.decrypt
        utility = decrypt_save.SaveParserUtility()
        utility.export_to_json(file_path=target_save, output_dir=output_dir)
        sys.exit(0)
    elif args.build_db:
        import dumper.build_db as build_db
        build_db.execute_db_build(wts=args.wts, w3t=args.w3t, w3u=args.w3u, w3a=args.w3a, arrays=args.arrays);
        sys.exit(0)
    else:
        launch_gui_dashboard()


if __name__ == "__main__": main()