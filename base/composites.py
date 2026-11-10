import applib, importlib
from base.folders import folder

composites:dict[str, type] = {}
cmp_mdl = {}

def refresh(log:bool=True):
    for module in applib.Storage("composites").list():
        if not module.endswith(".py"):
            continue
        name = module[:-3]
        if name in cmp_mdl:
            mod = importlib.reload(cmp_mdl[name])
        else:
            mod = importlib.import_module(f"composites.{name}")
            cmp_mdl[name] = mod
        if not hasattr(mod, name):
            folder.log.write(f"The module <composites/{module}> lacks a final class", type="CompositesError", set_error=True)
            continue
        composites[name] = getattr(mod, name)

    if log: folder.log.write("Composites was refresed", type="Composites")

refresh(False)