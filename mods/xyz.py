import xyz
import fcord
import util

def register():
    x = util.register_game("Test game", "xyz", [["a", "b", "c"], ["1", "2", "3"]], xyz.example_game, [0, 0, 0], lambda: "There are three sections a, b and c. You can increase any one by 1, 2 or 3 points. If a section reaches 10 points, the current player wins.\n!xyz cowsay (text) -> Just a simple echo.")
    util.register_game_subcommand(x, "cowsay", lambda e, game, coms: fcord.send("Cow: '" + " ".join(coms) + "'", e["d"]["channel_id"]))

def example_game(e, move, player, state, preview):
    if preview:
        fcord.send(" ".join([str(x) for x in state]), e["d"]["channel_id"])
        return
    state[ord(move[0]) - 97] += ord(move[1]) - 48
    
    fcord.send(" ".join([str(x) for x in state]), e["d"]["channel_id"])
    
    if state[0] >= 10 or state[1] >= 10 or state[2] >= 10:
        fcord.send("You have won!", e["d"]["channel_id"])
        return state, True
    return state, False
