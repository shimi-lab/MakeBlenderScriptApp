import streamlit as st
from ase.io.formats import ioformats

import default
from function import rgba2hex,hex2rgba,read_elementsini,read_csv
from make_script_for_app import make_script

FORMAT = ["自動検出"]+[key for key,val in ioformats.items() if val.can_read]
STYLE = ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Stick","Stick (bicolor)","Animation","Combine"]
COLOR_SCALE_LIST = ["Default","VESTA","Jmol","import element.ini ..."]

class Widgets():
    def __init__(self):
        pass
    
    def structure_file_upload_widgets(self):
        st.sidebar.selectbox(
            "format",
            FORMAT,
            index=0,
            key = "format",
            help="ase.io.readに準ずるformatを選択する")
        st.sidebar.file_uploader(
            "構造ファイルを選択",
            type=None,
            accept_multiple_files=False,
            key="upload_file",
            help=None,
            on_change=None,
            args=None)
        
    def structure_style_widgets(self):
        st.sidebar.radio(
            "Style",
            STYLE,
            index=0, 
            key="style_radio",
            on_change=self.change_style
            )
        
    def color_scale_widgets(self):
        st.sidebar.selectbox(
            "Color Scale",
            COLOR_SCALE_LIST,
            index = 0,
            key = "color_scale_selectbox",
            on_change=self.change_color_scale)
        
    def user_color_scale_widgets(self):
        st.sidebar.file_uploader(
            "element.ini ファイルを選択",
            type="ini",
            accept_multiple_files=False,
            key="color_file",
            help="element.iniファイルはVESTAの色を規定するテキストファイルです.",
            on_change=self.change_color_scale)
        
    def atoms_property_widgets(self,atoms,space_filling=False):
        with st.sidebar.expander("Atoms"):
            self._atoms_property_widgets(
                atoms=atoms,space_filling=space_filling,
                key_scale="scale",key_size="size_",key_color="color_",
                key_scalereset="reset_scale",key_sizereset="reset_size_")
    
    def _atoms_property_widgets(self,atoms,key_scale,key_size,key_color,key_scalereset,key_sizereset,space_filling=False,):
        unique_symb = list(set(atoms.get_chemical_symbols()))
        scale = default.space_filling_scale if space_filling else default.scale
        st.write("Scale")
        col1,col2 = st.columns([9,3])
        with col1:
            st.number_input(
                "Scale", 
                min_value=0.0, value=scale, step=0.1, 
                key=key_scale, on_change=None,
                label_visibility="collapsed")
        with col2:
            st.button("reset",key=f"{key_scalereset}",on_click=self.reset,args=(key_scale,scale))

        self.scale_list = []
        for symb in unique_symb:
            col1,col2,col3,col4 = st.columns([1.3,5,2,3])
            with col1:
                st.write(symb)
            with col2:
                size_obj = st.number_input(
                    f"size_{symb}",
                    min_value=0.0, value=default.sizes[symb], step=0.1, 
                    key=f"{key_size}{symb}", on_change=None,
                    label_visibility="collapsed")
                self.scale_list.append(size_obj)
            with col3:
                st.color_picker(
                    f"color_{symb}",
                    value=default.color[symb], key=f"{key_color}{symb}", 
                    on_change=None,label_visibility="collapsed") 
            with col4:
                st.button("reset",key=f"{key_sizereset}{symb}",on_click=self.reset,args=(f"{key_size}{symb}",default.sizes[symb]))

    def reset(self,key,value):
        st.session_state[key] = value               

            
    def bond_propert_widgets(self,atoms,bicolor=True,stick_color=False):
        with st.sidebar.expander("Bonds"):
            self._bond_propert_widgets(
                atoms=atoms,bicolor=bicolor,stick_color=stick_color,)
                        
    def _bond_propert_widgets(
        self,atoms,
        key_radius="radius",
        key_reset_radius="reset_radius",
        key_bond_color = "bond_color",
        key_color="color_",
        bicolor=True,stick_color=False):
        if bicolor:
            col1,col2,col3 = st.columns([2,5,3])
            with col1:
                st.write("Radius")
            with col2:
                st.number_input(
                    f"radius",
                    min_value=0.0, value=default.radius, step=0.05, 
                    key=key_radius, on_change=None,
                    label_visibility="collapsed")
            with col3:
                st.button("reset",key=key_reset_radius,on_click=self.reset,args=(key_radius,default.radius))
        else:
            col1,col2,col3 = st.columns([5,2,3])
            with col1:
                st.number_input(
                    f"radius",
                    min_value=0.0, value=default.radius, step=0.05, 
                    key=key_radius, on_change=None,
                    label_visibility="collapsed")
            with col2:
                st.color_picker(
                    f"bond_color",
                    value=rgba2hex(default.bond_color), key=key_bond_color, 
                    on_change=None,label_visibility="collapsed") 
            with col3:
                st.button("reset",key=key_reset_radius,on_click=self.reset,args=(key_radius,default.radius))
        if stick_color:
            unique_symb = list(set(atoms.get_chemical_symbols()))
            for symb in unique_symb:
                col1,col3 = st.columns([1.3,2])
                with col1:
                    st.write(symb)
                with col3:
                    st.color_picker(
                        f"color_{symb}",
                        value=default.color[symb], key=f"{key_color}{symb}", 
                        on_change=None,label_visibility="collapsed") 
                    
    def render_widgets(self):
        with st.sidebar.expander("Render"):
            cartoon = st.checkbox(
                "Cartoon", value=False, 
                help="漫画風にする",
                key="cartoon", on_change=None)
            if cartoon:
                st.number_input(
                    f"IOR",
                    min_value=0.0, value=default.cartoon["IOR"], step=0.1, 
                    key="IOR", on_change=None,
                    help="フレネルのIOR(枠線の太さに相当する.小さい程太くなる)",
                    label_visibility="visible")
                st.color_picker(
                    f"Color",
                    value=rgba2hex(default.cartoon["color"]), key="cartoon_color", 
                    help="ミックスのColor2(枠線の色に相当する)",
                    on_change=None,label_visibility="visible") 
            subdivision_surface = st.checkbox(
                "Subdivision Surface", value=False, 
                help="サブディビジョンサーフェイス(適用するとBlender上で実行に時間がかかるので注意)",
                key="subdivision_surface", on_change=None)
            if subdivision_surface:
                st.number_input(
                    f"Viewport Level",
                    min_value=0, value=default.subdivision_surface["level"], step=1, 
                    key="level", on_change=None,
                    label_visibility="visible")
                st.number_input(
                    f"Render Level",
                    min_value=0, value=default.subdivision_surface["render_levels"], step=1, 
                    key="render_levels", on_change=None,
                    label_visibility="visible")
            
    def animations_property_widgets(self):
        with st.sidebar.expander("Animation"):
            self._animations_property_widgets()
            
    def _animations_property_widgets(self): 
        st.number_input(
            "Start", 
            min_value=0, 
            max_value=None, 
            value=1, 
            step=1, 
            format="%d", 
            key="start",
            help="始めのキーフレームを打つ位置",
            on_change=None,) 
        st.number_input(
            "Step", 
            min_value=1, 
            max_value=None, 
            value=3, 
            step=1, 
            format="%d", 
            key="step",
            help="何フレーム毎にキーフレームを打つか",
            on_change=None,)  
            
    def combine_widgets(self):
        syle = STYLE.copy()
        syle.remove("Combine")
        st.multiselect(
            "Style", 
            syle, 
            default="Stick",
            key="multi_style_box",
            on_change=None,
            help="後から指定したStyleが優先される.")
        
    def combine_property_widgets(self,style,atoms,value=""):
        with st.expander(style):
            st.text_input(
                "index", 
                value=value,
                max_chars=100, 
                key=f"index_{style}", 
                help="適用する原子のindex番号を入力('1-10,20,24-30'のように指定可能)",  
                on_change=None,placeholder=None,label_visibility="visible")
            if style in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Animation"]:
                space_filling = True if style in ["Space Filling","Animation"] else False
                self._atoms_property_widgets(
                    atoms=atoms,
                    key_scale=f"scale_{style}",
                    key_size=f"size_{style}_",
                    key_color=f"color_{style}_",
                    key_scalereset=f"reset_scale_{style}",
                    key_sizereset=f"reset_size_{style}_",
                    space_filling=space_filling)
            if style == "Animation":
                self._animations_property_widgets()
            if style in ["Ball and Stick","Ball and Stick (bicolor)","Stick","Stick (bicolor)"]:
                bicolor = True if style in ["Ball and Stick (bicolor)","Stick (bicolor)"] else False
                stick_color = True if style == "Stick (bicolor)" else False
                self._bond_propert_widgets(
                    atoms=atoms,
                    key_radius=f"radius_{style}",
                    key_reset_radius=f"reset_radius_{style}",
                    key_bond_color=f"bond_color_{style}",
                    key_color=f"color_{style}_",
                    bicolor = bicolor,
                    stick_color = stick_color
                )
        
    def make_buttun_widgets(self,atoms,radio_disabled=True):
        st.button("Pythonスクリプト作成", key=None,
                  on_click=lambda:make_script(atoms),)
        
    def download_widgets(self,data,file_name=None):
        st.download_button("ファイルをダウンロード", data, file_name=file_name,on_click=None)
        
    def script_widgets(self):
        if "script" in st.session_state.keys():
            st.code(st.session_state["script"], language="python")
        
    def _index_label_widgets(self):
        st.checkbox("indexを表示", value=True, key="show_index", on_change=None)
            
    def label_widgets(self):
        self._index_label_widgets()
            
    def animation_widgets(self):
        st.radio(
            "label",
            ["1枚目の構造のみ表示","アニメーションで表示(時間がかかる場合があります)"],
            index=0,
            key="one_structure", 
            help=None, 
            on_change=None,
            horizontal=True, 
            label_visibility="collapsed")
        
    def change_color_scale(self):
        color_scale = st.session_state["color_scale_selectbox"]
        if not st.session_state["style_radio"] == "Combine":
            if color_scale == "Default":
                for symb,color in default.color.items():
                    if f"color_{symb}" in st.session_state.keys():
                        st.session_state[f"color_{symb}"]= default.color[symb]
            elif color_scale == "VESTA":
                for symb,color in default.color.items():
                    if f"color_{symb}" in st.session_state.keys():
                        st.session_state[f"color_{symb}"]= default.vesta_color[symb]
            elif color_scale == "Jmol":
                for symb,color in default.color.items():
                    if f"color_{symb}" in st.session_state.keys():
                        st.session_state[f"color_{symb}"]= default.jmol_color[symb]
            elif color_scale == "import element.ini ...":
                if "color_file" in st.session_state.keys():
                    if st.session_state["color_file"] is not None:
                        elements_ini_path = st.session_state["color_file"]
                        color_scale = {symb:rgba2hex(rgba) for symb,rgba in read_elementsini(elements_ini_path).items()}
                        for symb,color in color_scale.items():
                            if f"color_{symb}" in st.session_state.keys():
                                st.session_state[f"color_{symb}"]= color_scale[symb]
        else: #"Combine"
            if "multi_style_box" in st.session_state.keys():
                style_list = st.session_state["multi_style_box"]
                for style in style_list:
                    if color_scale == "Default":
                        for symb,color in default.color.items():
                            if f"color_{style}_{symb}" in st.session_state.keys():
                                st.session_state[f"color_{style}_{symb}"]= default.color[symb]
                    elif color_scale == "VESTA":
                        for symb,color in default.color.items():
                            if f"color_{style}_{symb}" in st.session_state.keys():
                                st.session_state[f"color_{style}_{symb}"]= default.vesta_color[symb]
                    elif color_scale == "Jmol":
                        for symb,color in default.color.items():
                            if f"color_{style}_{symb}" in st.session_state.keys():
                                st.session_state[f"color_{style}_{symb}"]= default.jmol_color[symb]
                    elif color_scale == "import element.ini ...":
                        if "color_file" in st.session_state.keys():
                            if st.session_state["color_file"] is not None:
                                elements_ini_path = st.session_state["color_file"]
                                color_scale = {symb:rgba2hex(rgba) for symb,rgba in read_elementsini(elements_ini_path).items()}
                                for symb,color in color_scale.items():
                                    if f"color_{style}_{symb}" in st.session_state.keys():
                                        st.session_state[f"color_{style}_{symb}"]= color_scale[symb]
                        
    def change_style(self):
        self.change_color_scale()
