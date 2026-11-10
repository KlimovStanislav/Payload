import applib, importlib
from base.folders import folder

components:dict[str, type] = {}
cmp_mdl = {}

def refresh(log:bool=True):
    for module in applib.Storage("components").list():
        if not module.endswith(".py"):
            continue
        name = module[:-3]

        if name in cmp_mdl:
            mod = importlib.reload(cmp_mdl[name])
        else:
            mod = importlib.import_module(f"components.{name}")
            cmp_mdl[name] = mod
        if not hasattr(mod, name):
            folder.log.write(f"The module <components/{module}> lacks a final class", type="ComponentsError", set_error=True)
            continue
        components[name] = getattr(mod, name)

    if log: folder.log.write("Components was refresed", type="Components")

refresh(False)