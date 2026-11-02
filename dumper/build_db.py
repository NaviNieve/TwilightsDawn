import re
import json
import os
import sys

def clean_warcraft_string(text):
    """Strips color codes and removes 'Forge ' prefixes from item names."""
    if not text: return ""
    clean = re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', text, flags=re.IGNORECASE)
    lines = clean.replace('\\n', '\n').split('\n')
    name = lines[0].strip() if lines else ""
    if name.startswith("Forge "):
        name = name.replace("Forge ", "")
    return name

def parse_wts_file_blocks(wts_path):
    wts_dict = {}
    if not os.path.exists(wts_path):
        print(f"[-] Error: String table path missing -> {wts_path}")
        return wts_dict
    try:
        with open(wts_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        matches = re.findall(r'STRING\s+(\d+)\s*\n\s*\{\s*\n?(.*?)\n?\s*\}', content, re.DOTALL)
        for num, text in matches:
            wts_dict[int(num)] = text.strip()
        print(f"[WTS SYSTEM] Successfully loaded {len(wts_dict)} raw strings from {wts_path}\n")
    except Exception as e:
        print(f"[-] Error parsing WTS file: {e}")
    return wts_dict

def extract_items_exclusively(file_path, wts_lookup):
    """Dedicated, state-isolated item harvester."""
    clean_item_mappings = {}
    dirty_item_mappings = {}
    if not os.path.exists(file_path):
        print(f"[-] Warning: Missing item metadata asset file -> {file_path}")
        return clean_item_mappings, dirty_item_mappings

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        raw_tokens = re.split(r"[\x00\t\n\r]+|\s{2,}", content)
        tokens = [t.strip() for t in raw_tokens if t.strip()]

        idx = 0
        while idx < len(tokens):
            element = tokens[idx]
            if len(element) == 8 and (element.startswith('rat9') or element.startswith('glsk')):
                item_fourcc = element[4:].upper()
                scan_idx = idx + 1
                while scan_idx < len(tokens):
                    sub_element = tokens[scan_idx]
                    if len(sub_element) == 8 and (sub_element.startswith('rat9') or sub_element.startswith('glsk')):
                        break
                    if sub_element[:4] == "unam" and scan_idx + 1 < len(tokens):
                        next_token = tokens[scan_idx + 1]
                        if "TRIGSTR_" in next_token:
                            try:
                                trig_num = int(next_token.split('_')[1])
                                if trig_num in wts_lookup:
                                    raw_dirty_payload = wts_lookup[trig_num]
                                    clean_name = clean_warcraft_string(raw_dirty_payload)
                                    clean_item_mappings[item_fourcc] = clean_name
                                    dirty_item_mappings[item_fourcc] = raw_dirty_payload
                            except (IndexError, ValueError):
                                pass
                            break
                    scan_idx += 1
            idx += 1
        print(f"[ITEM ENGINE] Successfully mapped {len(clean_item_mappings)} custom item profiles.")
    except Exception as e:
        print(f"[-] Error tracking item token streams: {e}")
    return clean_item_mappings, dirty_item_mappings
def extract_classes_exclusively(file_path, wts_lookup):
    """
    Dedicated, state-isolated hero classes harvester.
    Maintains your exact state loop steps and tracks raw comma-separated capability list streams.
    """
    fourcc_to_name = {}
    hero_raw_abilities = {}
    if not os.path.exists(file_path):
        print(f"[-] Warning: Missing metadata asset file -> {file_path}")
        return fourcc_to_name, hero_raw_abilities

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        raw_tokens = re.split(r"[\x00\t\n\r]+|\s{2,}", content)
        tokens = [t.strip() for t in raw_tokens if t.strip()]

        current_id = None
        idx = 0
        h_file_state = 0

        while idx < len(tokens):
            element = tokens[idx]

            if len(element) == 8 and element.startswith('H'):
                current_id = element[4:].upper()
                h_file_state = 1
                if current_id not in fourcc_to_name:
                    fourcc_to_name[current_id] = f"Unnamed_{current_id}"

            if h_file_state == 1 and current_id and idx + 1 < len(tokens):
                if element in ["uhab", "iabi"]:
                    raw_abilities_string = tokens[idx + 1].upper()
                    ab_list = [a.strip() for a in raw_abilities_string.split(',') if a.strip()]
                    hero_raw_abilities[current_id] = ab_list
                    h_file_state = 2

            if h_file_state == 2 and current_id and len(element) >= 4:
                if element[:4] == "unam" and idx + 1 < len(tokens):
                    next_element = tokens[idx + 1]
                    if "TRIGSTR_" in next_element:
                        try:
                            trig_num = int(next_element.split('_')[1])
                            if trig_num in wts_lookup:
                                fourcc_to_name[current_id] = wts_lookup[trig_num]
                                h_file_state = 0
                        except (IndexError, ValueError):
                            pass
            idx += 1
        print(f"[HERO ENGINE] Successfully mapped {len(fourcc_to_name)} hero class structures.")
    except Exception as e:
        print(f"[-] Error tracking hero tokens: {e}")
    return fourcc_to_name, hero_raw_abilities


def extract_abilities_exclusively(file_path, wts_lookup):
    """
    Dedicated, state-isolated ability harvester.
    Parses the file by tracing the exact start/stop boundaries of each child block
    in the array, capturing compressed names with zero cross-contamination.
    """
    fourcc_to_name = {}
    fourcc_to_maxlevel = {}

    if not os.path.exists(file_path):
        print(f"[-] Warning: Missing metadata asset file -> {file_path}")
        return fourcc_to_name, fourcc_to_maxlevel

    try:
        with open(file_path, "rb") as fb:
            raw_bytes = fb.read()

        content = raw_bytes.decode("utf-8", errors="ignore")
        raw_tokens = re.split(r"[\x00\t\n\r]+|\s{2,}", content)
        tokens = [t.strip() for t in raw_tokens if t.strip()]

        idx = 0
        while idx < len(tokens):
            element = tokens[idx]

            if len(element) == 8 and (element.startswith('A') or "A" in element[:4]):
                base_fourcc = element[:4].upper()
                custom_fourcc = element[4:].upper()

                if custom_fourcc not in fourcc_to_name:
                    fourcc_to_name[custom_fourcc] = f"Unnamed_{custom_fourcc}"
                if custom_fourcc not in fourcc_to_maxlevel:
                    fourcc_to_maxlevel[custom_fourcc] = 1

                scan_idx = idx + 1
                local_block_tokens = []

                while scan_idx < len(tokens):
                    next_el = tokens[scan_idx]
                    if len(next_el) == 8 and (next_el.startswith('A') or "A" in next_el[:4]):
                        break
                    local_block_tokens.append(next_el)
                    scan_idx += 1

                block_name = None
                block_tooltip = None

                p_idx = 0
                while p_idx < len(local_block_tokens):
                    prop = local_block_tokens[p_idx]
                    if len(prop) >= 4:
                        prefix = prop[:4]

                        if prefix == "anam" and p_idx + 1 < len(local_block_tokens):
                            val = local_block_tokens[p_idx + 1]
                            if "TRIGSTR_" in val:
                                try:
                                    t_num = int(val.split('_')[1])
                                    if t_num in wts_lookup:
                                        block_name = clean_warcraft_string(wts_lookup[t_num])
                                except (IndexError, ValueError):
                                    pass

                        elif prefix == "atp1" and p_idx + 1 < len(local_block_tokens):
                            val = local_block_tokens[p_idx + 1]
                            if "TRIGSTR_" in val:
                                try:
                                    t_num = int(val.split('_')[1])
                                    if t_num in wts_lookup:
                                        raw_tip = clean_warcraft_string(wts_lookup[t_num])
                                        clean_tip = raw_tip.split('(')[0].split('[')[0].split('-')[0].strip()
                                        if clean_tip and not clean_tip.startswith("TRIGSTR_"):
                                            block_tooltip = clean_tip
                                except (IndexError, ValueError):
                                    pass

                        elif prefix == "alev" and p_idx + 1 < len(local_block_tokens):
                            try:
                                fourcc_to_maxlevel[custom_fourcc] = int(local_block_tokens[p_idx + 1])
                            except (ValueError, TypeError):
                                pass

                    p_idx += 1

                if block_name:
                    fourcc_to_name[custom_fourcc] = block_name
                elif block_tooltip:
                    fourcc_to_name[custom_fourcc] = block_tooltip

                idx = scan_idx
                continue

            idx += 1

        overrides = {
            "A001": "Devotion Aura",
            "A003": "Critical Strike",
            "A00B": "Critical Strike",
            "A008": "Brilliance Aura",
            "A00F": "Evasion",
            "A00Y": "Thorns Aura",
            "A0VT": "Power Slam",
            "VT": "Power Slam",
            "AOWK": "Wind Walk",
            "OWK": "Wind Walk",
            "A1EE": "Psionic Energy",
            "1EE": "Psionic Energy"
        }

        for o_key, o_name in overrides.items():
            if o_key in fourcc_to_name:
                fourcc_to_name[o_key] = o_name

    except Exception as e:
        print(f"[-] Error parsing structural array entry blocks: {e}")

    return fourcc_to_name, fourcc_to_maxlevel


def compile_master_database(arrays_path, clean_mappings, dirty_item_mappings, hero_raw_abilities, fourcc_to_maxlevel):
    hero_classes = {}
    item_dictionary = {"Empty": 0}
    ability_dictionary = {}
    reverse_item_dirty_map = {0: ""}
    fourcc_to_ability_idx = {}
    name_to_fourcc = {}

    jass_pattern = re.compile(r'set\s+udg_int_array_([O0oIilL\d]+)\[(\d+)\]\s*=\s*[\'\"]?([A-Za-z0-9_]+)[\'\"]?')

    with open(arrays_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = jass_pattern.search(line)
            if not match: continue

            array_type = match.group(1)
            index_num = int(match.group(2))
            fourcc_code = match.group(3).upper()

            if fourcc_code == "AOWK":
                clean_name = "Wind Walk"
            else:
                clean_name = clean_mappings.get(fourcc_code, f"Unknown_{fourcc_code}")

            if "O" in array_type or "0" in array_type:
                hero_classes[clean_name] = index_num
                name_to_fourcc[clean_name] = fourcc_code
            elif "IIII" in line or array_type == "IIII":
                if clean_name != "Empty" and not clean_name.startswith("Unknown_"):
                    item_dictionary[clean_name] = index_num
                    if fourcc_code in dirty_item_mappings:
                        reverse_item_dirty_map[index_num] = dirty_item_mappings[fourcc_code]
            elif "IIlI" in line or array_type == "IIlI":
                ability_dictionary[clean_name] = index_num
                fourcc_to_ability_idx[fourcc_code] = index_num

    hero_ability_ids = {}
    for class_name, class_idx in hero_classes.items():
        hero_ability_ids[class_name] = []
        raw_hero_fourcc = name_to_fourcc.get(class_name)
        assigned_spells = hero_raw_abilities.get(raw_hero_fourcc, [])
        for spell_fourcc in assigned_spells:
            index_id = fourcc_to_ability_idx.get(spell_fourcc)
            if index_id is not None:
                hero_ability_ids[class_name].append(index_id)

    ability_max_level_clamps = {}
    for ab_fourcc, max_lvl in fourcc_to_maxlevel.items():
        if ab_fourcc in fourcc_to_ability_idx:
            ab_index_id = fourcc_to_ability_idx[ab_fourcc]
            ability_max_level_clamps[ab_index_id] = max_lvl

    ability_lines = []
    for k, v in sorted(hero_ability_ids.items()):
        ability_lines.append(f'    "{k}": {json.dumps(v)}')
    ability_ids_json_block = "{\n" + ",\n".join(ability_lines) + "\n}"

    dirty_map_lines = []
    for idx_key in sorted(reverse_item_dirty_map.keys()):
        escaped_val = reverse_item_dirty_map[idx_key].replace('"', '\\"')
        dirty_map_lines.append(f'    {idx_key}: "{escaped_val}"')
    dirty_map_string_block = "{\n" + ",\n".join(dirty_map_lines) + "\n}"

    clamp_lines = []
    for idx_key in sorted(ability_max_level_clamps.keys()):
        clamp_lines.append(f'    {idx_key}: {ability_max_level_clamps[idx_key]}')
    clamp_string_block = "{\n" + ",\n".join(clamp_lines) + "\n}"

    with open("database_new.py", "w", encoding="utf-8") as out:
        out.write("# Master Aligned Map Data Lookup Definitions\n\n")
        out.write("HERO_CLASSES = " + json.dumps(dict(sorted(hero_classes.items())), indent=4) + "\n\n")
        out.write("HERO_ABILITY_IDS = " + ability_ids_json_block + "\n\n")
        out.write("ITEM_DICTIONARY = " + json.dumps(dict(sorted(item_dictionary.items())), indent=4) + "\n\n")
        out.write("ABILITY_DICTIONARY = " + json.dumps(dict(sorted(ability_dictionary.items())), indent=4) + "\n\n")
        out.write("ABILITY_MAX_LEVELS = " + clamp_string_block + "\n\n")
        out.write("REVERSE_ITEM_DIRTY_MAP = " + dirty_map_string_block + "\n\n")
        out.write("REVERSE_HERO_MAP = {v: k for k, v in HERO_CLASSES.items()}\n")
        out.write("REVERSE_ITEM_MAP = {v: k for k, v in ITEM_DICTIONARY.items()}\n")
        out.write("REVERSE_ABILITY_MAP = {v: k for k, v in ABILITY_DICTIONARY.items()}\n")

    print("\n" + "=" * 75)
    print("SYSTEM COMPILER EXTRACTION COMPLETE:")
    print("=" * 75)
    print(f" -> Resulting Hero Classes:     {len(hero_classes)}")
    print(f" -> Mapped Index ID Level Caps: {len(ability_max_level_clamps)}")
    print(f" -> Resulting Custom Items:     {len(item_dictionary)}")
    print("Database built perfectly inside current directory: database_new.py")
    print("=" * 75)

def execute_db_build(wts, w3t, w3u, w3a, arrays):
    files = {
        "String Table (.txt)": wts, "Items Dump (.w3t)": w3t, "Heroes Dump (.w3u)": w3u, "Abilities Dump (.w3a)": w3a, "JASS Arrays (.txt)": arrays
    }
    validated_paths = {}
    for name, path in files.items():
        if path and os.path.exists(path): validated_paths[name] = path
        elif path and os.path.exists(os.path.basename(path)): validated_paths[name] = os.path.basename(path)

    wts_lookup = parse_wts_file_blocks(validated_paths["String Table (.txt)"])
    master_clean_mappings = {}

    clean_items, dirty_items = extract_items_exclusively(validated_paths["Items Dump (.w3t)"], wts_lookup)
    master_clean_mappings.update(clean_items)

    heroes_map, hero_raw_abilities = extract_classes_exclusively(validated_paths["Heroes Dump (.w3u)"], wts_lookup)
    master_clean_mappings.update(heroes_map)

    abilities_map, fourcc_to_maxlevel = extract_abilities_exclusively(validated_paths["Abilities Dump (.w3a)"], wts_lookup)
    master_clean_mappings.update(abilities_map)

    compile_master_database(validated_paths["JASS Arrays (.txt)"], master_clean_mappings, dirty_items, hero_raw_abilities, fourcc_to_maxlevel)

