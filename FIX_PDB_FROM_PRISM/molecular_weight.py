python
from pymol import cmd
# 1. Asegurar que PyMOL sabe qué elemento es cada átomo (para PDBs de PRISM)
cmd.alter("all", "elem=name[0]")
cmd.sort()

# 2. Extraer el modelo y sumar masas
model = cmd.get_model("all")
total_mass = sum(atom.get_mass() for atom in model.atom)

print(f"Peso Total: {total_mass/1000:.2f} kDa")
python end
