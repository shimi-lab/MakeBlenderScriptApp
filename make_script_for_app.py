import streamlit as st
import pickle
import io
import zipfile

from make_script.make_pyscript import (make_py_script,
                                       BallAndStick,
                                       Stick,SpaceFilling,
                                       Animation,TEMP)
from default import sizes
from function import hex2rgba

ELEMENTS = list(sizes.keys())


def _get_cartoon_param():
    if st.session_state["cartoon"]:
        IOR = st.session_state["IOR"]
        color = hex2rgba(st.session_state["cartoon_color"])
        return {"apply":True,"IOR":IOR,"color":color}
    else:
        return {"apply":False,"IOR":0.8,"color":(0,0,0,1)}

def _get_color_param():
    kwargs = {}
    for symb in ELEMENTS:
        if f"color_{symb}" in st.session_state.keys():    
            kwargs[symb] = hex2rgba(st.session_state[f"color_{symb}"])
    return kwargs

def _get_sizes_param():
    kwargs = {}
    for symb in ELEMENTS:
        if f"size_{symb}" in st.session_state.keys():    
            kwargs[symb] = st.session_state[f"size_{symb}"]
    return kwargs

def _get_subdivision_surface_param():
    if st.session_state["subdivision_surface"]:
        level = st.session_state["level"]
        render_levels = st.session_state["render_levels"]
        return {"apply":True,"level":level,"render_levels":render_levels}
    else:
        return {"apply":False,"level":2,"render_levels":2}

def make_script(atoms):
    style = st.session_state["style_radio"]
    kwargs = {}
    if style == "Ball and Stick":
        style_obj = BallAndStick
        kwargs["bicolor"] = False
        kwargs["colors"] = _get_color_param()
        kwargs["radius"] = st.session_state["radius"]
        kwargs["scale"] = st.session_state["scale"]
        kwargs["sizes"] = _get_sizes_param()
        kwargs["bond_color"] = hex2rgba(st.session_state["bond_color"])
    elif style == "Ball and Stick (bicolor)":
        style_obj = BallAndStick
        kwargs["bicolor"] = True
        kwargs["colors"] = _get_color_param()
        kwargs["radius"] = st.session_state["radius"]
        kwargs["scale"] = st.session_state["scale"]
        kwargs["sizes"] = _get_sizes_param()
    elif style == "Space Filling":
        style_obj = SpaceFilling
        kwargs["bicolor"] = False
        kwargs["colors"] = _get_color_param()
        kwargs["scale"] = st.session_state["scale"]
        kwargs["sizes"] = _get_sizes_param()
    elif style == "Stick":
        style_obj = Stick
        kwargs["bicolor"] = False
        kwargs["radius"] = st.session_state["radius"]
        kwargs["bond_color"] = hex2rgba(st.session_state["bond_color"])
    elif style == "Stick (bicolor)":
        style_obj = Stick
        kwargs["bicolor"] = True
        kwargs["colors"] = _get_color_param()
        kwargs["radius"] = st.session_state["radius"]
    elif style == "Animation":
        style_obj = Animation
        kwargs["bicolor"] = False
        kwargs["colors"] = _get_color_param()
        kwargs["scale"] = st.session_state["scale"]
        kwargs["sizes"] = _get_sizes_param()
        kwargs["start"] = st.session_state["start"]
        kwargs["step"] = st.session_state["step"]
    kwargs["cartoon"] = _get_cartoon_param()
    kwargs["subdivision_surface"] = _get_subdivision_surface_param()
    pyscript = make_py_script("-",style_obj(atoms,**kwargs))
    st.session_state["script"] = pyscript
    
def make_combine_script(partial_atoms_list,property_list):
    style_list = []
    for atoms,kwargs in zip(partial_atoms_list,property_list):
        style = kwargs.pop("style")
        if style == "Ball and Stick": # ,"Animation"]
            style_cls = BallAndStick
            kwargs["bicolor"] = False
            kwargs["bond_color"] = hex2rgba(kwargs["bond_color"])
            kwargs["colors"] = {symb:hex2rgba(color) for symb,color in kwargs["colors"].items()}
        elif style == "Ball and Stick (bicolor)":
            style_cls = BallAndStick
            kwargs["bicolor"] = True
            kwargs["colors"] = {symb:hex2rgba(color) for symb,color in kwargs["colors"].items()}
        elif style ==  "Space Filling":
            style_cls = SpaceFilling
            kwargs["colors"] = {symb:hex2rgba(color) for symb,color in kwargs["colors"].items()}
        elif style == "Stick":
            style_cls = Stick
            kwargs["bicolor"] = False
            kwargs["bond_color"] = hex2rgba(kwargs["bond_color"])
        elif style == "Stick (bicolor)":
            style_cls = Stick
            kwargs["bicolor"] = True
            kwargs["colors"] = {symb:hex2rgba(color) for symb,color in kwargs["colors"].items()}
        elif style == "Animation":
            style_cls = Animation
            traj = atoms
            kwargs["colors"] = {symb:hex2rgba(color) for symb,color in kwargs["colors"].items()}
        kwargs["cartoon"] = _get_cartoon_param()
        kwargs["subdivision_surface"] = _get_subdivision_surface_param()
        style_obj = style_cls(atoms,**kwargs)
        style_list.append(style_obj)
        
    if not style == "Animation":
        pyscript = make_py_script("-",style_list)
        st.session_state["script"] = pyscript    
    else:
        st.session_state["script"] = None
        
        data_list = []
        for i,style in enumerate(style_list):
            d_dict = style.todict()
            if style.style == "animation":
                filename = "positions.pkl"
                d_dict["file"] = filename
            data_list.append(d_dict) 
        data = {
            "data_list":data_list,
        }
        pyscript = TEMP.render(data)
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            with zf.open("animation.py","w") as f:
                f.write(pyscript.encode())
            with zf.open("positions.pkl","w") as f:
                for atoms in traj:
                    positions = atoms.get_positions()
                    f.write(pickle.dumps(positions))
        return zip_stream.getvalue()
        
        
def make_animation_script(structure):
    property_dict = {}
    unique_symbols = structure.get_unique_symbols()
    property_dict["scale"] = st.session_state["scale"]
    property_dict["sizes"] = {symb:st.session_state[f"size_{symb}"] for symb in unique_symbols}
    property_dict["colors"] = {symb:hex2rgba(st.session_state[f"color_{symb}"]) for symb in unique_symbols}
    property_dict["cartoon"] = _get_cartoon_param()
    property_dict["subdivision_surface"] = _get_subdivision_surface_param()
    property_dict["start"] = st.session_state["start"]
    property_dict["step"] = st.session_state["step"]
    property_dict["style"] = "animation"
    property_dict["file"] = "positions.pkl"
    property_dict["chemical_symbols"] = structure.atoms[0].get_chemical_symbols()
    property_dict["unique_symbols"] = unique_symbols
    
    pyscript = TEMP.render({"data_list":[property_dict]})
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        with zf.open("animation.py","w") as f:
            f.write(pyscript.encode())
        with zf.open("positions.pkl","w") as f:
            for atoms in structure.atoms:
                positions = atoms.get_positions()
                f.write(pickle.dumps(positions))
    return zip_stream.getvalue()
        