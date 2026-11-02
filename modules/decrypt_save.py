import re
import json
import os
import sys
from modules.decoder import SaveDecoder
from modules.database import REVERSE_HERO_MAP, REVERSE_ITEM_MAP


class SaveParserUtility:
    def __init__(self):
        self.preload_regex = re.compile(
            r'(?:call Preload\(\s*"|call BlzSetAbilityTooltip\(\s*\d+\s*,\s*")([^"]+)'
        )
        self.color_strip_regex = re.compile(r'\|c[0-9a-fA-F]{8}|\|r', re.IGNORECASE)

    def clean_item_name(self, text):
        clean = self.color_strip_regex.sub('', text).strip()
        return clean if clean else "Empty"

    def export_to_json(self, file_path, output_dir=None):
        if not file_path or not os.path.exists(file_path):
            print(f"[-] Error: Target save text file string path invalid or missing -> {file_path}")
            sys.exit(1)

        if output_dir is None:
            output_json_path = os.path.join("configs", "config.json") if os.path.exists("configs") else "config.json"
        else:
            output_json_path = os.path.join(output_dir, "config.json")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        preload_lines = self.preload_regex.findall(content)
        save_code = None
        player_name_str = "UnknownPlayer"

        for line in preload_lines:
            trimmed_line = line.strip()
            if trimmed_line.startswith("-l "):
                save_code = trimmed_line.replace("-l ", "").strip()
            elif trimmed_line.startswith("-"):
                save_code = trimmed_line[1:].strip()
            elif trimmed_line.startswith("Player Name:"):
                player_name_str = trimmed_line.replace("Player Name:", "").strip()

        if not save_code:
            sys.exit(1)

        decoder_instance = SaveDecoder()
        raw = decoder_instance.decode_to_array(save_code)
        print(raw)

        profession_level = raw[0]
        profession_quest_complete = raw[1]
        profession_rank = raw[2]
        hero_class_id = raw[3]
        experience = raw[4]
        checkpoint_zone = raw[5]

        hero_class_str = REVERSE_HERO_MAP.get(hero_class_id, "Unknown")

        ability_count = raw[6]
        idx = 7

        from modules.database import HERO_ABILITY_IDS
        class_ability_ids = HERO_ABILITY_IDS.get(hero_class_str, [])

        engine_ordered_levels = [0] * len(class_ability_ids)
        for _ in range(ability_count):
            if idx + 1 < len(raw):
                stream_ability_id = raw[idx]
                stream_level_value = raw[idx + 1]
                if stream_ability_id in class_ability_ids:
                    engine_slot = class_ability_ids.index(stream_ability_id)
                    engine_ordered_levels[engine_slot] = stream_level_value
                idx += 2

        gold = raw[idx] if idx < len(raw) else 0
        power_shards = raw[idx + 1] if idx + 1 < len(raw) else 0
        prestige = raw[idx + 2] if idx + 2 < len(raw) else 0
        idx += 3

        inventory = []
        if idx < len(raw):
            inv_size = raw[idx]
            idx += 1
            for _ in range(inv_size):
                if idx < len(raw):
                    inventory.append(REVERSE_ITEM_MAP.get(raw[idx], "Empty"))
                    idx += 1
        while len(inventory) < 6:
            inventory.append("Empty")

        stashes = {}
        stash_1_items = []
        if idx < len(raw):
            s1_size = raw[idx]
            idx += 1
            for _ in range(s1_size):
                if idx < len(raw):
                    stash_1_items.append(REVERSE_ITEM_MAP.get(raw[idx], "Empty"))
                    idx += 1
        while len(stash_1_items) < 6:
            stash_1_items.append("Empty")
        stashes["stash_1"] = stash_1_items

        annihilator_bounty_level = 0
        if hero_class_str == "Annihilator":
            if idx < len(raw):
                annihilator_bounty_level = raw[idx]
                idx += 1

        for s_num in range(2, 6):
            stash_key = f"stash_{s_num}"
            stashes[stash_key] = []
            if idx < len(raw):
                stash_cnt = raw[idx]
                idx += 1
                for _ in range(stash_cnt):
                    if idx < len(raw):
                        stashes[stash_key].append(REVERSE_ITEM_MAP.get(raw[idx], "Empty"))
                        idx += 1
            while len(stashes[stash_key]) < 6:
                stashes[stash_key].append("Empty")

        ultimate_gear_harbinger_count = raw[idx] if idx < len(raw) else 0
        city_of_illusions_prestige = raw[idx + 2] if idx + 2 < len(raw) else 0
        dragon_fortress_prestige = raw[idx + 3] if idx + 3 < len(raw) else 0
        punishment_chamber_prestige = raw[idx + 4] if idx + 4 < len(raw) else 0
        cursed_heaven_prestige = raw[idx + 5] if idx + 5 < len(raw) else 0

        seed_i0111 = raw[idx + 6] if idx + 6 < len(raw) else 0
        idx += 7

        if idx < len(raw):
            stash_6_items = []
            stash_6_cnt = raw[idx]
            idx += 1
            for _ in range(stash_6_cnt):
                if idx < len(raw):
                    stash_6_items.append(REVERSE_ITEM_MAP.get(raw[idx], "Empty"))
                    idx += 1
            while len(stash_6_items) < 6:
                stash_6_items.append("Empty")
            stashes["stash_6"] = stash_6_items

        lucky_inspirit_player = raw[idx + 2] if idx + 2 < len(raw) else 0
        lucky_triforce_player = raw[idx + 3] if idx + 3 < len(raw) else 0
        souls = raw[idx + 4] if idx + 4 < len(raw) else 0
        mysterious_notes_read = raw[idx + 6] if idx + 6 < len(raw) else 0
        chiral_valley_prestige = raw[idx + 9] if idx + 9 < len(raw) else 0
        mysterious_sigils_collected = raw[idx + 10] if idx + 10 < len(raw) else 0
        tercessuinotlim_prestige = raw[idx + 12] if idx + 12 < len(raw) else 0
        mysterious_orbs_collected = raw[idx + 13] if idx + 13 < len(raw) else 0

        structured_json = {
            "player_name": player_name_str,
            "hero_class": hero_class_str,
            "experience": experience,
            "checkpoint_zone": checkpoint_zone,
            "profession_level": profession_level,
            "profession_quest_complete": profession_quest_complete,
            "profession_rank": profession_rank,
            "gold": gold,
            "power_shards": power_shards,
            "prestige": prestige,
            "souls": souls,
            "annihilator_bounty_level": annihilator_bounty_level,
            "ability_levels": engine_ordered_levels,
            "inventory": inventory,
            "stashes": stashes,
            "ultimate_gear_harbinger_count": ultimate_gear_harbinger_count,
            "lucky_inspirit_player": lucky_inspirit_player,
            "lucky_triforce_player": lucky_triforce_player,
            "mysterious_notes_read": mysterious_notes_read,
            "mysterious_sigils_collected": mysterious_sigils_collected,
            "mysterious_orbs_collected": mysterious_orbs_collected,
            "city_of_illusions_prestige": city_of_illusions_prestige,
            "dragon_fortress_prestige": dragon_fortress_prestige,
            "punishment_chamber_prestige": punishment_chamber_prestige,
            "cursed_heaven_prestige": cursed_heaven_prestige,
            "chiral_valley_prestige": chiral_valley_prestige,
            "tercessuinotlim_prestige": tercessuinotlim_prestige,
            "seed_i0111": seed_i0111
        }

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(structured_json, f, indent=2)
        print(f"[+] Decrypted profile file layout compiled straight to: {output_json_path}")