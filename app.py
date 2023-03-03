import streamlit as st
from pathlib import Path

from widgets import Widgets,STYLE
from structure import Structure
from function import parsestr2list,get_unique_items
from make_script_for_app import make_script,make_combine_script,make_animation_script

def _make_animation_kwargs(structure):
    unique_symbols = structure.get_unique_symbols()
    property_dict = {}
    property_dict["scale"] = st.session_state["scale"]
    property_dict["sizes"] = {symb:st.session_state[f"size_{symb}"] for symb in unique_symbols}
    property_dict["colors"] = {symb:st.session_state[f"color_{symb}"] for symb in unique_symbols}
    return property_dict

def make_animation_kwargs(structure,index_list=None,view_index=False,multi_structure=True):
    property_dict = _make_animation_kwargs(structure)
    return {"properties":property_dict,"index_list":index_list,"multi_structure":multi_structure,"view_index":view_index}

st.set_page_config(
    page_title="Blender用Pythonスクリプト作成",
    page_icon="./logo.png",
    menu_items={'About': 'https://shimi-lab.github.io/GRRMPY_document/src/blender_gallery.html'})
widgets = Widgets()
widgets.structure_file_upload_widgets()

if st.session_state["upload_file"] is not None:  
    widgets.structure_style_widgets()
    widgets.color_scale_widgets()
        
    file = st.session_state["upload_file"]
    format = None if st.session_state["format"]=="自動検出" else st.session_state["format"]
    
    if st.session_state["color_scale_selectbox"] == "import element.ini ...":
        widgets.user_color_scale_widgets()
    
    if st.session_state["style_radio"] == STYLE[5]: #"Animation":
        multi_structure = True
        structure = Structure(file,format,multi_structure=True)
        widgets.atoms_property_widgets(structure.atoms[0],space_filling=True)
        widgets.animations_property_widgets()
        # widgets.make_buttun_widgets(structure.atoms,True)
        widgets.animation_widgets()
    elif st.session_state["style_radio"] == STYLE[6]: # "Combine"
        widgets.combine_widgets()
        structure = Structure(file,format,multi_structure=False) # とりあえずmulti_structure=Falseで作成
        for style in st.session_state["multi_style_box"]:
            widgets.combine_property_widgets(style,structure.atoms,value=f"0-{structure.natoms()-1}")
        widgets.label_widgets()
        if "Animation" in st.session_state["multi_style_box"]:
            widgets.animation_widgets()
            radio_disabled = True
        else:
            radio_disabled = False
        # widgets.make_buttun_widgets(structure.atoms,radio_disabled)
    else:
        radio_disabled = False
        structure = Structure(file,format,multi_structure=False)
        if st.session_state["style_radio"] == STYLE[0]: # "Ball and Stick"
            widgets.atoms_property_widgets(structure.atoms)
            widgets.bond_propert_widgets(structure.atoms,bicolor=False)
        elif st.session_state["style_radio"] == STYLE[1]: # "Ball and Stick (bicolor)"
            widgets.atoms_property_widgets(structure.atoms)
            widgets.bond_propert_widgets(structure.atoms,bicolor=True)
        elif st.session_state["style_radio"] == STYLE[2]: # "Space Filling"
            widgets.atoms_property_widgets(structure.atoms,space_filling=True)
        elif st.session_state["style_radio"] == STYLE[3]: # "Stick"
            widgets.bond_propert_widgets(structure.atoms,bicolor=False)
        elif st.session_state["style_radio"] == STYLE[4]: # "Stick (bicilor)"
            widgets.bond_propert_widgets(structure.atoms,bicolor=True,stick_color=True)
        # widgets.make_buttun_widgets(structure.atoms,radio_disabled)
    widgets.render_widgets()
    
    ###### 構造の可視化 #######
    style = st.session_state["style_radio"]
    if style == "Animation":
        if st.session_state["one_structure"] == "1枚目の構造のみ表示":
            kwargs = make_animation_kwargs(structure,view_index=False,multi_structure=False)
        else:
            kwargs = make_animation_kwargs(structure,view_index=False,multi_structure=True)
        structure.view(style,**kwargs) 
    elif style == "Combine":
        apply_style_list = st.session_state["multi_style_box"]
        index_list = [list(set(parsestr2list(st.session_state[f"index_{style}"]))) for style in apply_style_list]
        index_list = get_unique_items(index_list)
        if "Animation" in apply_style_list and st.session_state["one_structure"] != "1枚目の構造のみ表示":
            # partial_atoms_dictの中身は{style:[images,index]}
            structure = Structure(file,format,multi_structure=True) #multi_structure=Trueに更新
            partial_atoms_dict = {
                style: [[atoms[idx] for atoms in structure.atoms] ,idx]
                        if style == "Animation" else 
                        [[structure.atoms[0][idx] for _ in structure.atoms],idx]
                        for style,idx in zip(apply_style_list,index_list) if not idx==[]}
        else:
            # partial_atoms_dictの中身は{style:[atoms,index]}
            partial_atoms_dict = {style:[structure.atoms[idx],idx] for style,idx in zip(apply_style_list,index_list) if not idx==[]}
        property_list = []
        for style,(atoms,index) in partial_atoms_dict.items():
            if "Animation" in apply_style_list and st.session_state["one_structure"] != "1枚目の構造のみ表示":
                unique_symbols = list(set(atoms[0].get_chemical_symbols()))
                animation = True
            else:
                unique_symbols = list(set(atoms.get_chemical_symbols()))
                animation = False
            property_dict = {}
            property_dict["style"] = style
            property_dict["index"] = index
            if style in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Animation"]:
                property_dict["scale"] = st.session_state[f"scale_{style}"]
                property_dict["sizes"] = {symb:st.session_state[f"size_{style}_{symb}"] for symb in unique_symbols}
            if style in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Stick (bicolor)","Animation"]:
                property_dict["colors"] = {symb:st.session_state[f"color_{style}_{symb}"] for symb in unique_symbols}
            if style in ["Ball and Stick","Stick"]:
                property_dict["bond_color"] = st.session_state[f"bond_color_{style}"]
            if style in ["Ball and Stick","Ball and Stick (bicolor)","Stick","Stick (bicolor)"]:
                property_dict["radius"] = st.session_state[f"radius_{style}"]
            property_list.append(property_dict)
        partial_atoms_list = [atoms for atoms,_ in partial_atoms_dict.values()]
        show_index = True if st.session_state["show_index"] else None
        structure.view_combine(partial_atoms_list,property_list,show_index=show_index,animation=animation)
    else:
        unique_symbols = structure.get_unique_symbols()
        property_dict = {}
        if style in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling"]:
            property_dict["scale"] = st.session_state["scale"]
            property_dict["sizes"] = {symb:st.session_state[f"size_{symb}"] for symb in unique_symbols}
        if style in ["Ball and Stick","Ball and Stick (bicolor)","Space Filling","Stick (bicolor)"]:
            property_dict["colors"] = {symb:st.session_state[f"color_{symb}"] for symb in unique_symbols}
        if style in ["Ball and Stick","Stick"]:
            property_dict["bond_color"] = st.session_state["bond_color"]
        if style in ["Ball and Stick","Ball and Stick (bicolor)","Stick","Stick (bicolor)"]:
            property_dict["radius"] = st.session_state["radius"]
        structure.view(style,property_dict) 
    ################################################### 
    
    if st.session_state["style_radio"] == STYLE[5]: #"Animation":
        file_name = str(Path(st.session_state["upload_file"].name).with_suffix(".zip"))
        zipbite = make_animation_script(structure)
        widgets.download_widgets(zipbite,file_name=file_name)
    elif st.session_state["style_radio"] == STYLE[6]: # "Combine":
        if "Animation" in st.session_state["multi_style_box"]:
            structure = Structure(file,format,multi_structure=True) #multi_structure=Trueに更新
            partial_atoms_list = [[atoms[idx] for atoms in structure.atoms]
                        if style == "Animation" else 
                        structure.atoms[0][idx]
                        for style,idx in zip(apply_style_list,index_list) if not idx==[]]
            zipbite = make_combine_script(partial_atoms_list,property_list)
            file_name = str(Path(st.session_state["upload_file"].name).with_suffix(".zip"))
            widgets.download_widgets(zipbite,file_name=file_name)
        else:
            make_combine_script(partial_atoms_list,property_list)
            widgets.script_widgets()
    else:
        make_script(structure.atoms)   
        widgets.script_widgets()
else:
    st.title("Blender用Pythonスクリプト作成")
    st.markdown(
        """
        ### はじめに
        左のサイドバーに構造ファイルをドラック＆ドロップ
        
        Belnder2.93.4で動作確認済み
        
        ### ギャラリー
        右上のメニューのAboutからBlenderのギャラリーを見ることができます
        
        ### 使い方
        """
    )
    st.write("構造ファイルをドラッグ&ドロップ")
    st.image("img/drag_and_drop.png") 
    st.write("Pythonスクリプトをコピー")
    st.image("img/copy.png") 
    st.write("Blenderを開き,テキストエディターを開く")
    st.image("img/text_editor.png") 
    st.write("新規をクリックし,コピーしたスクリプトを貼り付け,実行する")
    st.image("img/run.png") 
    st.write("3Dビューポートに戻る.シェダーに切り替えると色がついていることを確認できる")
    st.image("img/finish.png") 
    st.write("カメラとライトを設定し,レンダリングする")
    
    
    