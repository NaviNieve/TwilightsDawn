import json
import os
import sys
from modules.core_engine import SaveEngine
from modules.database import HERO_CLASSES, HERO_ABILITY_IDS, ITEM_DICTIONARY, ABILITY_MAX_LEVELS


def find_config(custom_path=None):
    if custom_path:
        if os.path.exists(custom_path):
            return custom_path
        print(f"[-] Explicit config path not found: {custom_path}")
        sys.exit(1)

    fallbacks = [
        os.path.join("configs", "config.json"),
        "config.json"
    ]
    for path in fallbacks:
        if os.path.exists(path):
            return path

    print("[-] Error: config.json missing.")
    sys.exit(1)


def run_encryption(config_path=None):
    target_config = find_config(config_path)
    print(f"[+] Using configuration file: {target_config}")

    with open(target_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    engine = SaveEngine()
    hero_class = config["hero_class"]
    raw_stream = []

    profession_level = max(0, min(config.get("profession_level", 0), 250))
    profession_quest_complete = max(0, min(config.get("profession_quest_complete", 0), 1))
    profession_rank = max(0, min(config.get("profession_rank", 0), 5))
    experience = max(0, min(config.get("experience", 0), 4529550))
    checkpoint_zone = max(0, min(config.get("checkpoint_zone", 0), 5))

    raw_stream.append(profession_level)
    raw_stream.append(profession_quest_complete)
    raw_stream.append(profession_rank)
    raw_stream.append(HERO_CLASSES.get(hero_class, 0))
    raw_stream.append(experience)
    raw_stream.append(checkpoint_zone)

    config_levels = config.get("ability_levels", [])
    ability_ids = HERO_ABILITY_IDS.get(hero_class, [])

    unsorted_pairs = []
    for i in range(len(config_levels)):
        engine_target_idx = i
        if engine_target_idx < len(ability_ids):
            ability_id = ability_ids[engine_target_idx]
            current_max_clamp = ABILITY_MAX_LEVELS.get(ability_id, 30)
            ability_level = max(0, min(config_levels[i], current_max_clamp))
            if ability_level > 0:
                unsorted_pairs.append((ability_id, ability_level))

    sorted_pairs = sorted(unsorted_pairs, key=lambda x: x[0])

    active_abilities_block = []
    for ability_id, ability_level in sorted_pairs:
        active_abilities_block.append(ability_id)
        active_abilities_block.append(ability_level)

    raw_stream.append(len(active_abilities_block) // 2)
    raw_stream.extend(active_abilities_block)

    raw_stream.append(max(0, min(config.get("gold", 0), 1000000)))
    raw_stream.append(max(0, min(config.get("power_shards", 0), 1000)))
    raw_stream.append(max(0, min(config.get("prestige", 0), 2147483647)))

    active_inventory = [item for item in config["inventory"] if item and item != "Empty"]
    raw_stream.append(len(active_inventory))
    for item_name in active_inventory:
        raw_stream.append(ITEM_DICTIONARY.get(item_name, 0))

    stash_1_items = config["stashes"].get("stash_1", [])
    active_stash_1 = [item for item in stash_1_items if item and item != "Empty"]
    raw_stream.append(len(active_stash_1))
    for item_name in active_stash_1:
        raw_stream.append(ITEM_DICTIONARY.get(item_name, 0))

    if hero_class == "Annihilator":
        raw_stream.append(max(0, min(config.get("annihilator_bounty_level", 0), 17)))

    for i in range(2, 6):
        stash_key = f"stash_{i}"
        items_list = config["stashes"].get(stash_key, [])
        active_items = [item for item in items_list if item and item != "Empty"]
        raw_stream.append(len(active_items))
        for item_name in active_items:
            raw_stream.append(ITEM_DICTIONARY.get(item_name, 0))

    raw_stream.append(max(0, config.get("ultimate_gear_harbinger_count", 0)))
    raw_stream.append(7400)
    raw_stream.append(max(0, config.get("city_of_illusions_prestige", 0)))
    raw_stream.append(max(0, config.get("dragon_fortress_prestige", 0)))
    raw_stream.append(max(0, config.get("punishment_chamber_prestige", 0)))
    raw_stream.append(max(0, config.get("cursed_heaven_prestige", 0)))

    saved_seed_i0111 = max(0, config.get("seed_i0111", 0))
    raw_stream.append(saved_seed_i0111)

    stash_6_items = config["stashes"].get("stash_6", [])
    active_stash_6 = [item for item in stash_6_items if item and item != "Empty"]
    raw_stream.append(len(active_stash_6))
    for item_name in active_stash_6:
        raw_stream.append(ITEM_DICTIONARY.get(item_name, 0))

    raw_stream.append(saved_seed_i0111)
    raw_stream.append(7)
    raw_stream.append(max(0, min(config.get("lucky_inspirit_player", 0), 1)))
    raw_stream.append(max(0, min(config.get("lucky_triforce_player", 0), 1)))
    raw_stream.append(max(0, min(config.get("souls", 0), 155)))
    raw_stream.append(saved_seed_i0111)
    raw_stream.append(max(0, config.get("mysterious_notes_read", 0)))
    raw_stream.append(0)
    raw_stream.append(saved_seed_i0111)
    raw_stream.append(max(0, config.get("chiral_valley_prestige", 0)))
    raw_stream.append(max(0, config.get("mysterious_sigils_collected", 0)))
    raw_stream.append(saved_seed_i0111)
    raw_stream.append(max(0, config.get("tercessuinotlim_prestige", 0)))
    raw_stream.append(max(0, config.get("mysterious_orbs_collected", 0)))

    generated_code = engine.generate_save_string(raw_stream, config["player_name"])

    print("\n" + "=" * 75)
    print("SERIALIZATION VECTOR ARRAY SEQUENCE COMPLETE:")
    print("=" * 75)
    print(f"Total elements length: {len(raw_stream)}")
    print(raw_stream)
    print("=" * 75)
    return generated_code