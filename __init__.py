import functools

import renpy
from renpy import ast

from modloader.modclass import Mod, loadable_mod
from modloader import modast
import jz_magmalink as ml

def is_skip_ahead_menu(node):
    return isinstance(node, ast.Menu) and ("Yes. I want to skip ahead." in (i[0] for i in node.items))

def is_asyouwish_say(node):
    return isinstance(node, ast.Say) and node.what == "As you wish.{cps=2}..{/cps}{w=1.0}{nw}"

def menuize_skip(idx, node):
    skipmenu_node = node.next
    for _ in range(50): # Set a hard cap of fifty nodes, or assume someone knotted up the tree and abort.
        if skipmenu_node is None:
            return # No skip menu found. Unsafe to link anything.
        if isinstance(skipmenu_node, modast.ASTHook):
            return # Mod already hooked this skip menu. Unsafe to link anything over it.
        if is_skip_ahead_menu(skipmenu_node):
            break
        skipmenu_node = skipmenu_node.next
    if not is_skip_ahead_menu(skipmenu_node):
        return # No skip menu found. Unsafe to link anything

    skipmenu = ml.MenuNode(skipmenu_node)

    linktarget_node = skipmenu.branch("Yes. I want to skip ahead.").first_node
    for _ in range(50):
        if linktarget_node is None or isinstance(linktarget_node, (ast.Jump, ast.Return)):
            return # No link target found. Unsafe to link anything.
        if isinstance(linktarget_node, modast.ASTHook):
            break # Mod already hooked this yes branch.
                  # What we can do is link to their link.
        if is_asyouwish_say(linktarget_node):
            break # Found the link target.
        linktarget_node = linktarget_node.next
    if not (isinstance(linktarget_node, modast.ASTHook) or is_asyouwish_say(linktarget_node)):
        return # No link target found. Unsafe to link anything.

    continue_node = skipmenu.branch("No. Don't skip ahead.").first_node
    for _ in range(50):
        if continue_node is None or isinstance(continue_node, (ast.Jump, ast.Return)):
            return # No continue node found. Unsafe to link anything.
        if isinstance(continue_node, modast.ASTHook):
            break # Mod already hooked this continue node.
                  # What we can do is link to their link.
        if is_asyouwish_say(continue_node):
            break # Found the continue node.
        continue_node = continue_node.next
    if not (isinstance(continue_node, modast.ASTHook) or is_asyouwish_say(continue_node)):
        return

    target = 'skipskip_four_target_' + str(idx)
    if isinstance(linktarget_node, modast.ASTHook):
        ml.node(linktarget_node).link_from(target)
    else:
        ml.node(linktarget_node).link_behind_from(target)

    def execute_skip(target, hook):
        ast.next_node(hook.next)
        renpy.exports.hide_screen('skipskip_four_screen')
        renpy.exports.show_screen('skipskip_four_screen', target)
        return True

    hook = modast.hook_opcode(node, functools.partial(execute_skip,target), tag='skipskip_four_hook_'+str(idx))
    if isinstance(continue_node, modast.ASTHook):
        hook.chain(continue_node)
    else:
        hook.chain(continue_node.next)


@loadable_mod
class MyAwSWMod(Mod):
    name = "Skip Skips"
    version = "v1.0"
    author = "4onen"
    dependencies = ["MagmaLink"]

    @staticmethod
    def mod_load():
        pass

    @staticmethod
    def mod_complete():
        [menuize_skip(idx,n) for (idx,n) in enumerate(renpy.game.script.all_stmts) if isinstance(n, ast.Call) and n.label == 'skiptut']
