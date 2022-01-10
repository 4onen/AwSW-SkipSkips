import functools

import renpy
from renpy import ast

from modloader.modclass import Mod, loadable_mod
from modloader import modast
import jz_magmalink as ml

def menuize_skip(idx, node):
    skipmenu = ml.OtherNode(node).search_menu("Yes. I want to skip ahead.", depth=50)
    target = 'skipskip_four_target_' + str(idx)
    skipmenu.branch().search_say("As you wish.{cps=2}..{/cps}{w=1.0}{nw}").link_behind_from(target)
    cont = skipmenu.branch("No. Don't skip ahead.").search_say("As you wish.{cps=2}..{/cps}{w=1.0}{nw}").node.next

    def execute_skip(target, hook):
        renpy.ast.next_node(hook.next)
        renpy.exports.hide_screen('skipskip_four_screen')
        renpy.exports.show_screen('skipskip_four_screen', target)
        return True

    hook = modast.hook_opcode(node, functools.partial(execute_skip,target), tag='skipskip_four_hook_'+str(idx))
    hook.chain(cont)


@loadable_mod
class MyAwSWMod(Mod):
    name = "Skip Skips"
    version = "v1.0"
    author = "4onen"
    dependencies = ["MagmaLink"]

    @staticmethod
    def mod_load():
        [menuize_skip(idx,n) for (idx,n) in enumerate(renpy.game.script.all_stmts) if isinstance(n, ast.Call) and n.label == 'skiptut']

    @staticmethod
    def mod_complete():
        pass
