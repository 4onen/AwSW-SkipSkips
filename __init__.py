import functools

import renpy
import renpy.exports
from renpy import ast
from renpy.game import script

from modloader.modclass import Mod, loadable_mod
from modloader import modast

def is_skip_ahead_menu(node):
    return isinstance(node, ast.Menu) and ("Yes. I want to skip ahead." in (i[0] for i in node.items))

def menu_branch_first_node(menu_node, choice):
    branch_first_node = next((i[2][0] for i in menu_node.items if i[0] == choice), None)
    if branch_first_node is None:
        raise ValueError("Cannot find branch " + choice + " in the menu"+str(menu_node))
    return branch_first_node

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

    linktarget_node = menu_branch_first_node(skipmenu_node,"Yes. I want to skip ahead.")
    for _ in range(50):
        if linktarget_node is None or isinstance(linktarget_node, (ast.Jump, ast.Return)):
            return # No link target found. Unsafe to link anything.
        if isinstance(linktarget_node, modast.ASTHook):
            break # Mod already hooked this yes branch.
                  # What we can do is link to their link.
        if is_asyouwish_say(linktarget_node):
            break # Found the link target.
        linktarget_node = linktarget_node.next
    if is_asyouwish_say(linktarget_node):
        # We need to find the end of the translation block,
        # because the link target is a say statement which is always in a translation block.
        linktarget_node = linktarget_node.next
        if not isinstance(linktarget_node, ast.EndTranslate):
            return # No link target found. Unsafe to link anything.
    elif isinstance(linktarget_node, modast.ASTHook):
        # Just hook to the ASTHook.
        pass
    else:
        return # No link target found. Unsafe to link anything.

    continue_node = menu_branch_first_node(skipmenu_node, "No. Don't skip ahead.")
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
    if script.has_label(target):
        raise ValueError("Name '" + target + "' exists. Did this mod run twice?")
    linktarget_label = ast.Label(("SkipSkips", idx), target, [], None)
    script.namemap[target] = linktarget_label
    if isinstance(linktarget_node, modast.ASTHook):
        linktarget_label.next = linktarget_node
    else:
        linktarget_label.next = linktarget_node.next

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
    version = "v1.1"
    author = "4onen"

    @staticmethod
    def mod_load():
        pass

    @staticmethod
    def mod_complete():
        [menuize_skip(idx,n) for (idx,n) in enumerate(script.all_stmts) if isinstance(n, ast.Call) and n.label == 'skiptut']
