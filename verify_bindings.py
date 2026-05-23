import hymn_player_ext
player = hymn_player_ext.HymnPlayer()
print("Methods in HymnPlayer:", [m for m in dir(player) if not m.startswith("__")])
assert hasattr(player, "start_realtime")
assert hasattr(player, "stop_realtime")
print("Verification Success")
