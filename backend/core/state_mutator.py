def apply_effects(world_data: dict, events: list) -> None:
    """
    Aplica todos los effects de los eventos al world_data.
    Modifica world_data in-place.
    """
    locations_by_id = {loc["id"]: loc for loc in world_data.get("locations", [])}
    kingdoms_by_id = {k["id"]: k for k in world_data.get("kingdoms", [])}

    for event in events:
        for effect in event.get("effects", []):
            apply_single_effect(effect, locations_by_id, kingdoms_by_id, world_data)


def apply_single_effect(effect: dict, locations_by_id: dict, kingdoms_by_id: dict, world_data: dict) -> None:
    """
    Aplica un efecto individual al mundo.
    """
    target_type = effect.get("target_type")
    target_id = effect.get("target_id")
    field = effect.get("field")
    delta = effect.get("delta", 0)

    if target_type == "location":
        location = locations_by_id.get(target_id)
        if not location:
            return

        if field in location:
            # Campo simple: numerico
            current = location.get(field, 0)
            new_value = current + delta
            # Clampar entre 0 y 100 para propiedades estandar
            if field in ["tension", "unrest", "wealth"]:
                new_value = max(0, min(100, new_value))
            location[field] = new_value

    elif target_type == "kingdom":
        kingdom = kingdoms_by_id.get(target_id)
        if not kingdom:
            return

        # Manejar tracks.X
        if field.startswith("tracks."):
            track_name = field.split(".")[1]
            tracks = kingdom.get("tracks", {})
            if track_name in tracks:
                current = tracks[track_name]
                new_value = current + delta
                new_value = max(0, min(100, new_value))
                tracks[track_name] = new_value

    elif target_type == "relationship":
        kingdoms_list = effect.get("kingdoms", [])
        if len(kingdoms_list) != 2:
            return

        k1_id, k2_id = kingdoms_list[0], kingdoms_list[1]
        kingdom1 = kingdoms_by_id.get(k1_id)
        kingdom2 = kingdoms_by_id.get(k2_id)

        if not kingdom1 or not kingdom2:
            return

        # Actualizar relaciones bilaterales
        rels1 = kingdom1.get("relationships", {})
        rels2 = kingdom2.get("relationships", {})

        if k2_id in rels1:
            rels1[k2_id] += delta
        if k1_id in rels2:
            rels2[k1_id] += delta
