from function import read_elementsini,read_csv,rgba2hex
# Animation
step=3
start=1
pyfile="animation.py"
pklfile="property.pkl"
# Bonds
bond_color = (0.5, 0.5, 0.5 ,1.0)
radius = 0.08
bicolor=False
# Viewer
width = 600
height = 600
# Atoms
scale = 0.4
space_filling_scale = 1.0
color = {element:rgba2hex(rgba) for element,rgba in read_elementsini("./default.ini").items()}
vesta_color = {element:rgba2hex(rgba) for element,rgba in read_elementsini("./vesta.ini").items()}
jmol_color = {symb:rgba2hex(color) for symb,color in read_csv("./jmol.csv").items()}
sizes={
    'Ac': 2.03,
    'Ag': 1.44,
    'Al': 1.43,
    'Am': 1.73,
    'Ar': 1.92,
    'As': 1.21,
    'At': 0.62,
    'Au': 1.44,
    'B': 0.81,
    'Ba': 2.24,
    'Be': 1.12,
    'Bi': 1.82,
    'Br': 1.14,
    'C': 0.77,
    'Ca': 1.97,
    'Cd': 1.52,
    'Ce': 1.82,
    'Cl': 0.99,
    'Co': 1.25,
    'Cr': 1.29,
    'Cs': 2.72,
    'Cu': 1.28,
    'D': 0.46,
    'Dy': 1.77,
    'Er': 1.75,
    'Eu': 2.06,
    'F': 0.72,
    'Fe': 1.26,
    'Fr': 1.0,
    'Ga': 1.53,
    'Gd': 1.79,
    'Ge': 1.22,
    'H': 0.46,
    'He': 1.22,
    'Hf': 1.59,
    'Hg': 1.55,
    'Ho': 1.76,
    'I': 1.33,
    'In': 1.67,
    'Ir': 1.36,
    'K': 2.35,
    'Kr': 1.98,
    'La': 1.88,
    'Li': 1.57,
    'Lu': 1.72,
    'Mg': 1.6,
    'Mn': 1.37,
    'Mo': 1.4,
    'N': 0.74,
    'Na': 1.91,
    'Nb': 1.47,
    'Nd': 1.82,
    'Ne': 1.6,
    'Ni': 1.25,
    'Np': 1.56,
    'O': 0.74,
    'Os': 1.35,
    'P': 1.1,
    'Pa': 1.63,
    'Pb': 1.75,
    'Pd': 1.37,
    'Pm': 1.81,
    'Po': 1.77,
    'Pr': 1.82,
    'Pt': 1.39,
    'Pu': 1.64,
    'Ra': 2.35,
    'Rb': 2.5,
    'Re': 1.37,
    'Rh': 1.34,
    'Rn': 0.8,
    'Ru': 1.34,
    'S': 1.04,
    'Sb': 1.41,
    'Sc': 1.64,
    'Se': 1.04,
    'Si': 1.18,
    'Sm': 1.81,
    'Sn': 1.58,
    'Sr': 2.15,
    'Ta': 1.47,
    'Tb': 1.77,
    'Tc': 1.35,
    'Te': 1.37,
    'Th': 1.8,
    'Ti': 1.47,
    'Tl': 1.71,
    'Tm': 1.0,
    'U': 1.56,
    'V': 1.35,
    'W': 1.41,
    'XX': 0.8,
    'Xe': 2.18,
    'Y': 1.82,
    'Yb': 1.94,
    'Zn': 1.37,
    'Zr': 1.6,
    }
# Render
subdivision_surface = {"apply":False,"level":3,"render_levels":3}
cartoon = {"apply":False,"IOR":0.85,"color":(0,0,0,1)}
