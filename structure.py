import streamlit as st
from ase.io import read,iread,Trajectory
from ase import Atoms
from pathlib import Path
from io import StringIO
import py3Dmol
from stmol import showmol

import default

class Structure():
    def __init__(self,uploaded_file,format,multi_structure=False):
        self.atoms = self.create_atoms(uploaded_file,format,multi_structure)
        self.multi_structure = multi_structure
    
    def create_atoms(self,uploaded_file,format,multi_structure):
        biteio = uploaded_file
        if format is None:
            if Path(uploaded_file.name).suffix == ".xyz":
                format = "xyz"
                file = StringIO(biteio.getvalue().decode("utf-8"))
            elif uploaded_file.name == "POSCAR" or uploaded_file.name == "CONTCAR":
                format = "vasp"
                file = StringIO(biteio.getvalue().decode("utf-8"))
            elif Path(uploaded_file.name).suffix == ".cif":
                format = "cif"
                file = StringIO(biteio.getvalue().decode("utf-8"))
            elif Path(uploaded_file.name).suffix == ".traj":
                format = "traj"
                file = biteio
        else:
            if format == "traj":
                file = biteio
            else:
                file = StringIO(biteio.getvalue().decode("utf-8"))
        try:
            if multi_structure:
                if format == "traj":
                    atoms = Trajectory(file)
                else:
                    atoms = list(iread(file,format=format))
            else:
                atoms = read(file,format=format)
        except Exception as e:
            st.error("自動検出できないのでformatを指定して下さい")
            st.stop()
        return atoms
    
    def natoms(self):
        if self.multi_structure:
            return len(self.atoms[0])
        else:
            return len(self.atoms)
    
    def view(self,style,properties,atoms=None,index_list=None,multi_structure=False,view_index=False,width=default.width,height=default.height):
        if atoms is None:
            atoms = self.atoms
            index_list = [i for i in range(self.natoms())]
        if not multi_structure and self.multi_structure:
            atoms = atoms[0]
        xyz_text = self.get_xyz(atoms)
        view = py3Dmol.view(width=width, height=height)
        if not multi_structure:
            view.addModel(xyz_text,'xyz')
            unique_symbols = self.get_unique_symbols()
            ball_dict = {symb:{} for symb in unique_symbols} # 空の辞書
            stick_dict = {symb:{} for symb in unique_symbols} # 空の辞書
            if style in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Animation"]:
                ball_dict = self.get_ball_dict(unique_symbols,properties["scale"],properties["sizes"],properties["colors"])
            if style in ["Ball and Stick (bicolor)","Stick (bicolor)"]:
                stick_dict = self.get_stick_dict(unique_symbols,properties["radius"],True,properties["colors"])
            if style in ["Ball and Stick","Stick"]:
                stick_dict = self.get_stick_dict(unique_symbols,properties["radius"],False,properties["bond_color"])
            style_dict = {symb:dict(ball_dict[symb], **stick_dict[symb]) for symb in unique_symbols} # マージ
            self.set_style(view,unique_symbols,style_dict)
        else: # animation
            view.addModelsAsFrames(xyz_text, "xyz")
            unique_symbols = self.get_unique_symbols()
            if view_index:
                self.add_index_label(view,atoms[0],index_list)
            view.animate({"loop": "forward","reps": 0})
            ball_dict = self.get_ball_dict(unique_symbols,properties["scale"],properties["sizes"],properties["colors"])
            self.set_style(view,unique_symbols,ball_dict)
        view.setBackgroundColor('0xF7F7F7')
        view.zoomTo()
        showmol(view,height=height,width=width)
        
    def view_combine(self,atoms_list,property_list,show_index=False,width=default.width,height=default.height,animation=False):
        view = py3Dmol.view(width=width, height=height)
        for i,(atoms,properties) in enumerate(zip(atoms_list,property_list)):
            xyz_text = self.get_xyz(atoms)
            if animation:
                view.addModelsAsFrames(xyz_text, "xyz")
                view.animate({"loop": "forward","reps": 0})
                atoms = atoms[0]
            else:
                view.addModel(xyz_text,'xyz')
            unique_symbols = list(set(atoms.get_chemical_symbols()))
            ball_dict = {symb:{} for symb in unique_symbols} 
            stick_dict = {symb:{} for symb in unique_symbols}
            if properties["style"] in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Animation"]:
                ball_dict = self.get_ball_dict(unique_symbols,properties["scale"],properties["sizes"],properties["colors"])
            if properties["style"] in ["Ball and Stick (bicolor)","Stick (bicolor)"]:
                stick_dict = self.get_stick_dict(unique_symbols,properties["radius"],True,properties["colors"])
            if properties["style"] in ["Ball and Stick","Stick"]:
                stick_dict = self.get_stick_dict(unique_symbols,properties["radius"],False,properties["bond_color"])
            style_dict = {symb:dict(ball_dict[symb], **stick_dict[symb]) for symb in unique_symbols} # マージ
            for symb in unique_symbols:
                view.setStyle({'model':i,"elem":symb},style_dict[symb])
            if show_index:
                self.add_index_label(view,atoms,properties["index"])
        view.setBackgroundColor('0xF7F7F7')
        view.zoomTo()
        showmol(view,height=height,width=width)
        
    def add_index_label(self,view,atoms,index_list):
        for (x,y,z),idx in zip(atoms.get_positions(),index_list):
            view.addLabel(
                f"{idx}",
                {"position":{"x":x,"y":y,"z":z},
                 "showBackground":True,
                 "backgroundColor":"white",
                 "backgroundOpacity": 0.3,
                 "fontSize":12,
                 "fontColor":"black",
                 "alignment":"center",
                 "frame":0})
            
    def get_ball_dict(self,unique_symb:list,scale:float,sizes:dict,colors:dict):
        return {symb:
            {"sphere":
                {"radius":sizes[symb],
                 "scale":scale,
                 "color":colors[symb]}}
            for symb in unique_symb}

    def get_stick_dict(self,unique_symb:list,radius:float,bicolor:bool,colors):
        if bicolor:
            return {symb:
                {"stick":
                    {"radius":radius,
                    "color":colors[symb]}}
                for symb in unique_symb}
        else:
            return {symb:
                {"stick":
                    {"radius":radius,
                     "color":colors}}
                for symb in unique_symb}
            
    def set_style(self,view,unique_symb,style_dict):
        for symb in unique_symb:
            view.setStyle({'elem':f'{symb}'},style_dict[symb])
        
    def get_xyz(self,images,fmt='%22.15f'):
        text = ""
        if type(images)==Atoms:
            images = [images]
        for atoms in images:
            natoms = len(atoms)
            text += '%d\n%s\n' % (natoms, "")
            for s, (x, y, z) in zip(atoms.symbols, atoms.positions):
                text += '%-2s %s %s %s\n' % (s, fmt % x, fmt % y, fmt % z)
        return text
    
    def get_unique_symbols(self):
        if self.multi_structure:
            return list(set(self.atoms[0].get_chemical_symbols()))
        else:
            return list(set(self.atoms.get_chemical_symbols()))
        
