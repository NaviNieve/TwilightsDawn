import os
import re
import json
from pathlib import Path
from modules.database import HERO_CLASSES, ITEM_DICTIONARY, HERO_ABILITY_IDS


class TwilightSaveManager:
    def __init__(self):
        self.base_save_dir = Path(
            os.path.expanduser("~")) / "Documents" / "Warcraft III" / "CustomMapData" / "Twilight's Eve Evo"
        self.preload_regex = re.compile(r'call Preload\(\s*"([^"]+)"\s*\)')
        self.color_strip_regex = re.compile(r'\|c[0-9a-fA-F]{8}|\|r', re.IGNORECASE)

    def calculate_level_from_exp(self, exp_val):
        try:
            target_exp = int(exp_val)
            if target_exp <= 0:
                return 1

            base_need_xp = 100
            formula_b = 100.0
            formula_c = 50.0
            max_level = 300

            current_level = 1
            remaining_xp = target_exp

            while remaining_xp > 0 and current_level < max_level:
                if current_level == 1:
                    current_cost = base_need_xp
                else:
                    current_cost = int(((current_level * formula_b) + formula_c) + base_need_xp)

                if remaining_xp >= current_cost:
                    current_level += 1
                    remaining_xp -= current_cost
                else:
                    break

            return current_level

        except (ValueError, TypeError):
            return 1

    def scan_game_save_directory(self):
        """
        Level 1-4 Folder Viewer Processor.
        Returns a structured dictionary map of all accounts, classes, and valid saves.
        """
        catalog = {}
        if not self.base_save_dir.exists():
            return catalog

        for acc_dir in self.base_save_dir.iterdir():
            if not acc_dir.is_dir():
                continue

            if acc_dir.name in ["Codeless", "Damage"]:
                continue

            account_name = acc_dir.name
            catalog[account_name] = {}

            for class_dir in acc_dir.iterdir():
                if not class_dir.is_dir():
                    continue

                class_name = class_dir.name
                catalog[account_name][class_name] = []

                for file_path in class_dir.glob("*.txt"):
                    file_title = file_path.stem
                    catalog[account_name][class_name].append({
                        "display_name": file_title,
                        "full_path": str(file_path)
                    })

        return catalog

    def extract_metadata_from_external_file(self, absolute_file_path):
        """
        Natively routes metadata parsing loops based on extension tracking,
        ensuring clean name and class loading for the 'Other' sidebar grid list.
        """
        if not os.path.isfile(absolute_file_path):
            return "UnknownPlayer", "Novice (Male)"

        if absolute_file_path.lower().endswith('.json'):
            try:
                print(
                    f"[📋 METADATA COMPILER] Reading external config data map directly: {os.path.basename(absolute_file_path)}")
                with open(absolute_file_path, "r", encoding="utf-8") as f:
                    config_payload = json.load(f)

                player_name = config_payload.get("player_name", "UnknownPlayer")
                hero_class = config_payload.get("hero_class", "Novice (Male)")
                return player_name, hero_class

            except Exception as e:
                print(f"[-] Error routing external JSON metadata lookup: {e}")
                return "UnknownPlayer", "Novice (Male)"

        else:
            player_name = "UnknownPlayer"
            hero_class = "Novice (Male)"

            try:
                with open(absolute_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "Player Name:" in line:
                            match = re.search(r'Player Name:\s*([^\"]+)', line)
                            if match:
                                player_name = match.group(1).strip()

                        elif "Hero:" in line:
                            match = re.search(r'Hero:\s*([^\"]+)', line)
                            if match:
                                hero_class = match.group(1).strip()

            except Exception as e:
                print(f"[-] Error compiling external text profile log metadata: {e}")

            return player_name, hero_class

    def rebuild_preload_file_content(self, data):
        from modules.database import ITEM_DICTIONARY, REVERSE_ITEM_DIRTY_MAP

        lines = [
            "function PreloadFiles takes nothing returns nothing\n",
            "\tcall PreloadStart()",
            '\tcall Preload( "MAP: Twilight\'s Eve Evo" )',
            f'\tcall Preload( "Player Name: {data.get("player_name", "")}" )',
            f'\tcall Preload( "Hero: {data.get("hero_class", "Novice (Male)")}" )',
            f'\tcall Preload( "Gold: {data.get("gold", 1500)}" )',
            f'\tcall Preload( "Power Shard: {data.get("power_shards", 0)}" )',
            '\tcall Preload( "        " )'
        ]

        inventory_items = data.get("inventory", ["Empty"] * 6)
        for idx in range(6):
            item_name = inventory_items[idx] if idx < len(inventory_items) else "Empty"
            item_idx = ITEM_DICTIONARY.get(item_name, 0)

            dirty_string = REVERSE_ITEM_DIRTY_MAP.get(item_idx, " ") if item_name != "Empty" else " "
            lines.append(f'\tcall Preload( "Item {idx + 1}: {dirty_string}" )')
        lines.append('\tcall Preload( "        " )')

        stashes = data.get("stashes", {})
        for s_idx in range(1, 7):
            stash_key = f"stash_{s_idx}"
            stash_items = stashes.get(stash_key, ["Empty"] * 6)
            prefix = "Stash " if s_idx == 1 else f"Stash{s_idx} "

            for idx in range(6):
                item_name = stash_items[idx] if idx < len(stash_items) else "Empty"
                item_idx = ITEM_DICTIONARY.get(item_name, 0)

                dirty_string = REVERSE_ITEM_DIRTY_MAP.get(item_idx, " ") if item_name != "Empty" else " "
                lines.append(f'\tcall Preload( "{prefix}Item {idx + 1}: {dirty_string}" )')
            lines.append('\tcall Preload( "        " )')

        lines.append(f'\tcall Preload( "-l {data.get("generated_code", "")}" )')
        lines.append('\tcall Preload( "        " )')
        lines.append("\tcall PreloadEnd( 0.0 )\n")
        lines.append("endfunction")

        return "\n".join(lines)

    def write_save_file_to_disk(self, data, target_directory_path=None):
        """
        Saves the reconstructed text save file directly inside the target nested directory tree structure.
        """
        player = data.get("player_name", "UnknownPlayer")
        h_class = data.get("hero_class", "Novice")
        calc_lvl = self.calculate_level_from_exp(data.get("experience", 0))
        filename = f"[Level {calc_lvl}].txt"

        if target_directory_path:
            dest_path = Path(target_directory_path)
            if dest_path.is_dir():
                dest_file = dest_path / filename
            else:
                dest_file = dest_path
        else:
            dest_file = self.base_save_dir / player / h_class / filename

        try:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            content = self.rebuild_preload_file_content(data)
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[+] Save file accurately exported straight to disk payload path: {dest_file}")
            return str(dest_file)
        except Exception as e:
            print(f"[-] Failed writing script template contents to target drive file: {e}")
            return None