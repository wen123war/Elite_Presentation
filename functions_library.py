import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import subprocess
import time
from dataclasses import dataclass
import shutil
import ipywidgets
from ipywidgets import interact, fixed, interact_manual, widgets, Button, Layout, AppLayout, VBox
from ovito.io import import_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier
from ovito.vis import *
from ovito.pipeline import *
from ovito.data import DataCollection
from lammps import lammps
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Dataclass
@dataclass
class MD_system:
    Project_name: str = "Melting"
    element:str = "Al"
    lattice_constant: float = None
    box_length: int = 3
    timestep: float = 0.001
    start_temperature: int = None
    seed: int = 100
    end_temperature: int =None
    thermo_time :int = 200
    running_steps :int = 150000
    
    @property
    def potential_name(self):
        if self.element == "Al":
            potential_name = "Al03.eam.alloy"
        if self.element == "Cu":
            potential_name = "Cu01.eam.alloy"
        if self.element == "Ti":
            potential_name = "Farkas_Nb-Ti-Al_1996.eam.alloy"
        return potential_name
        
    @property
    def lattice(self):
        def atom_info(self):
            Al = {"a":[3.95, 6.00], "mass":26.982, "melting_point":933, "color":(0.837,0.837,0.837)}
            Cu = {"a":[3.62, 6.00], "mass":63.546, "melting_point":1360, "color":(0.885,0.421,0.177)}
            Ti = {"a":[2.85, 6.00], "mass":47.867, "Phasetransformation_temparature":1166, "color":(1,0.4,0.4)}
            atoms = vars()[self.element]
            return atoms

        self.atoms = atom_info(self)
        atom_mass = self.atoms["mass"]
        color = self.atoms["color"]
        alat_min, alat_max = self.atoms['a'][0], self.atoms['a'][1]
        if self.element == 'Ti':
            melting_point = self.atoms["Phasetransformation_temparature"]
        else:
            melting_point = self.atoms["melting_point"]
        return alat_min, alat_max, atom_mass, melting_point, color
    
    @property
    def random_number(self):
        seed = np.int64(self.seed)
        np.random.seed(seed)
        return int("".join([str(x) for x in np.random.randint(10, size=6)]))
    
    
### Function
## Common
def copy_file(source, target):
    """
    Copy a file from the source path to the target path
    """
    copy = f'cp {source} {target}'
    run = subprocess.Popen(copy, shell=True)
    run.wait()

    
def Checkdir(keyword):
    '''
    Check whether the file with corresponding key already existed.
    When the file existed, it will be removed
    '''
    root = os.getcwd()
    dir_list = os.listdir("./")
    for path in dir_list:
        if keyword in path:
            dir_path = f"{root}/{path}"
            if os.path.exists(dir_path):
                print(f"The dictionary {dir_path} will be removed!")
                shutil.rmtree(dir_path)
            else:
                pass
    
    
def showtime(func):
    """
    Show the running time of a function
    """
    def wrapper(System):
        start_time = time.time()
        func(System)
        end_time = time.time()
        print('Running time is {} s'.format(end_time - start_time))
    return wrapper


## Lammps simulation
def copy_potential(s:MD_system):
    copy_file(f"./potentials/{s.potential_name}", f"./{s.Project_name}/{s.potential_name}")

def copy_structure(s:MD_system):
    copy_file(f"./structures/initial_{s.element}", f"./{s.Project_name}/initial_{s.element}")

def write_input_melting(System):
    """
    Write input-file for running Lammps
    """
    with open(f"./{System.Project_name}/lammps_input", "w+") as fw:
        fw.write(f"""
dimension 3
units metal
atom_style atomic
boundary p p p

read_data ../structures/initial_{System.element}

pair_style eam/alloy
pair_coeff * * {System.potential_name} {System.element}

neighbor 3.0 bin

write_data original

change_box all x delta 0 3 
change_box all y delta 0 3 
change_box all z delta 0 3 boundary s s s

timestep {System.timestep}

thermo {System.thermo_time}

thermo_style custom step temp vol press

variable t equal step
variable m equal temp
fix thermo all print {System.thermo_time} '$t $m' file thermo_output.dat screen no

velocity all create {System.start_temperature} {System.random_number} mom yes rot yes dist gaussian

dump 1 all custom 200 melting id type xs ys zs

fix 2 all nvt temp {System.start_temperature} {System.end_temperature} 0.1

run {System.running_steps}
        """)
        
def write_sturcture_Ti(s:MD_system):
    """
    write the structure file of primivte cell of Ti
    """
    aLat = s.lattice_constant
    with open(f"./structures/hcp_Ti", "w+") as fw:
        fw.write(f"""Start File for LAMMPS
2 atoms
1 atom types

0.0 {1.00*aLat} xlo xhi
0.0 {0.866025*aLat} ylo yhi
0.0 {1.588*aLat} zlo zhi
{0.5*aLat} 0E-15 0E-15 xy xz yz

Masses

1 47.867000

Atoms

1 1 0.000000000000000 0.000000000000000 0.000000000000000
2 1 0.000000000000000 {0.577350269189626*aLat} {0.794000000000000*aLat}      
        """)


def write_input_PT(System):
    # PT:Phasetransformation
    """
    Write input-file for running Lammps
    """
    with open(f"./{System.Project_name}/lammps_input", "w+") as fw:
        fw.write(f"""
dimension 3
units metal
atom_style atomic
boundary p p p
box tilt large

read_data ../structures/initial_Ti

pair_style eam/alloy
pair_coeff * * {System.potential_name} {System.element}

write_data original

timestep {System.timestep}

fix ensemble all npt temp {System.start_temperature} {System.end_temperature} 0.1 x 10.0 10.0 1.0 y 10.0 10.0 1.0 z 10.0 10.0 1.0 xy 0.0 0.0 1.0 xz 0.0 0.0 1.0 yz 0.0 0.0 1.0

velocity all create {System.start_temperature} {System.random_number} dist gaussian

dump 1 all custom {System.thermo_time} phasetransfomation id type xsu ysu zsu fx fy fz vx vy vz
dump_modify 1 sort id format line "%d %d %20.15g %20.15g %20.15g %20.15g %20.15g %20.15g %20.15g %20.15g %20.15g"
thermo_style custom step temp pe etotal vol
# thermo_style custom step temp pe etotal pxx pxy pxz pyy pyz pzz vol
thermo_modify format float %20.15g
thermo {System.thermo_time}

variable t equal step
variable m equal temp
fix thermo all print {System.thermo_time} '$t $m' file thermo_output.dat screen no

run 60000
        """)
    

def run_lammps(input_file):
    lmp = lammps() #cmdargs=["-sc", "log"])
    lmp.file(f"./{input_file}")


def animate(s:MD_system):
    if s.element in ['Al', 'Cu']:
        pipeline = import_file(f"./{s.Project_name}/melting", multiple_frames=True)
        data_in = np.loadtxt(f"./{s.Project_name}/thermo_output.dat")
        timestep = data_in[:,0]
        temperature = data_in[:,1]
        
    if s.element in ['Ti']:
        pipeline = import_file(f"./{s.Project_name}/phasetransfomation", multiple_frames=True)
        data_in = np.loadtxt(f"./{s.Project_name}/thermo_output.dat")
        timestep = data_in[:,0]
        temperature = data_in[:,1]
        ptm_modifier = PolyhedralTemplateMatchingModifier()
        ptm_modifier.rmsd_cutoff = 0.3
        ptm_modifier.structures[PolyhedralTemplateMatchingModifier.Type.FCC].enabled = False
        pipeline.modifiers.append(ptm_modifier)
        

    def modify_pipeline_input(frame: int, data: DataCollection):
        data.particles_.particle_types_.type_by_id_(1).color = s.lattice[4]
        data.particles_.particle_types_.type_by_id_(1).radius = 0.5
    
    pipeline.modifiers.append(modify_pipeline_input)

    title_show = widgets.HTML(value="<h1>Animation of Results</h1>", layout=Layout(height='10px', width='100%'))

    pipeline.add_to_scene()
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 2, -1))
    vp.zoom_all()

    max_frame = pipeline.source.num_frames
    play_image = widgets.Play(
        value=0,
        min=0,
        max=max_frame - 1,
        step=1,
        description="Press play",
        disabled=False,
        layout=Layout(width='auto', height='50px')
    )

    slider = widgets.FloatProgress(
        value=0,
        min=0,
        max=max_frame - 1,
        step=1,
        description='Progress:',
        bar_style='success',
        orientation='horizontal',
        layout=Layout(width='auto', height='50px')
    )

    control = widgets.IntSlider(
        value=0,
        min=0,
        max=max_frame - 1,
        description = 'Frame:',
        disabled = False,
        orientation = 'horizontal',
        layout=Layout(width='auto', height='50px')
    )

    time_show = widgets.HTML(
        value=f"Time: {timestep[vp.dataset.anim.current_frame]/1000:5.0f} ps",
        min=0,
        max=max_frame - 1,
        layout=Layout(width='auto', height='auto', fontsize=50),
        margin=('0px 0px 60px 0px')
    )

    temperature_show = widgets.HTML(
        value=f"<h3>Temperature: {temperature[vp.dataset.anim.current_frame]:4.0f} K</h3>",
        min=0,
        max=max_frame - 1,
        layout=Layout(width='auto', height='auto'),
        margin=('0px 0px 50px 0px')
    )

    widgets.jslink((play_image, 'value'), (slider, 'value'))
    widgets.jslink((play_image, 'value'), (control, 'value'))

    def on_frame_change(change):
      temperature_show.value = f"<h3>Temperature: {temperature[vp.dataset.anim.current_frame]:4.0f} K</h3>"
      time_show.value = f"Time: {timestep[vp.dataset.anim.current_frame]/1000:5.0f} ps"
    
    play_image.observe(on_frame_change, "value")

    def play(vp, x, w):
        vp.dataset.anim.current_frame = x
        w.refresh()

    window = vp.create_jupyter_widget()
    window.layout = ipywidgets.Layout(width='auto', height='auto')
    widgets.interactive(play, x=play_image, vp=fixed(vp), w=fixed(window))
    
    close_button = widgets.Button(
        description='Close',
        layout=Layout(width='auto', height='50px', margin='355px 0px 0px 0px'),
        button_style='success'
    )
    
    def close_click(sender):
        pipeline.remove_from_scene()
        window.scene.clear()
        close_button.button_style='danger'

    # connect the function with the button
    close_button.on_click(close_click)
    
    Box = AppLayout(header=title_show,
                      center=window,
                      left_sidebar=None,
                      right_sidebar=VBox([play_image, control, slider, time_show, temperature_show, close_button]),
                      footer=None,
                      pane_widths=['0px', '820px', '300px'],
                      pane_heights=['65px', '600px', '00px'],
                      width="100%",
                      grid_gap="10px")
    display(Box)
    

@showtime
def calculation(s:MD_system):
    # Prepare Input file
    Checkdir(s.Project_name)
    os.mkdir(f"./{s.Project_name}")
    copy_potential(s)
    
    print(s.element)
    if s.element in ['Al', 'Cu']:
        copy_structure(s)
        write_input_melting(s)
    if s.element in ['Ti']:
        copy_structure(s)
        write_input_PT(s)

    # Run Lammps
    os.chdir(f"./{s.Project_name}")
    run_lammps(f"./lammps_input")
    os.chdir("../")
    
    
def input_melting(s:MD_system):
    System_melting = MD_system()

    title_show = widgets.HTML(value="<h1>Molecular Dynamics Simulation of Melting</h1>", layout=Layout(height='10px', width='100%'))
    title_show.style.text_align='center'

    pipeline = import_file(f"./structures/ghost_fcc", multiple_frames=True)
    pipeline.add_to_scene()
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 2, -1))
    vp.zoom_all()
    window_1 = vp.create_jupyter_widget()
    window_1.layout = Layout(width='auto', height='auto')
    window_1.refresh()
    pipeline.remove_from_scene()

    # define element list
    elements_show = widgets.ToggleButtons(
        options=['Al', 'Cu'],
        value = None,
        description='Element:',
        disabled=False,
        button_style='success',
        style={"button_width": "60px"},
        layout=Layout(width='auto', height='15%')
    )

    aLat_show = widgets.SelectionSlider(
        options=['Angstrom'],
        description = 'Lattice constant:',
        disabled = False,
        orientation = 'horizontal',
        readout_format='.1f',
        layout=Layout(width='auto', height='10%'),
        style={"description_width": "110px"}
    )

    melting_point_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))

    # Change the lattice constant and atom mass corresponding with the name of element
    def on_element_change(change):
        System_melting.element=elements_show.value
        with aLat_show.hold_trait_notifications():
            aLat_show.options = np.around(np.linspace(System_melting.lattice[0], System_melting.lattice[1], num=20), 4)
        melting_point_show.value = f"<h3>The melting point of {System_melting.element} is {System_melting.lattice[3]} K.</h3>"

    elements_show.observe(on_element_change, "value")

    # define Project name
    Project_name_show = widgets.Text(
        placeholder='Your Project name',
        description='Project:',
        layout=Layout(width='auto', height='10%'),
        disabled=False,
        style={"description_width": "50px"}
    )

    # define box_length 
    box_length_show = widgets.BoundedIntText(
        value=4,
        min=3,
        max=6,
        step=1,
        description='Size:',
        layout=Layout(width='auto', height='5%'),
        disabled=False
    )

    # Preview the structure
    preview_button = widgets.Button(
        description='Preview',
        layout=Layout(width='auto', height='5%', margin='0px 0px 35px 0px'),
        button_style='success'
    )


    def preview_click(sender):
        if Project_name_show.value == "":
           Project_name_show.style.danger = True
           submit_button.button_style='danger'
           MD_status_show.value = ""
           MD_finish_show.value = ""
           Error_status_show.value = f"<h2>You must name your project!</h2>"
        else:
           if submit_button.button_style=='danger':
              submit_button.button_style='success'
           Error_status_show.value = ""
        System_melting.box_length = box_length_show.value
        System_melting.lattice_constant = aLat_show.value
        lmp = lammps(cmdargs=["-sc", "log"])
        
        cmd = f"""
    dimension 3
    units metal
    atom_style atomic
    boundary p p p
    lattice fcc {System_melting.lattice_constant}
    region box block 0 {System_melting.box_length+0.1} 0 {System_melting.box_length+0.1} 0 {System_melting.box_length+0.1}
    create_box 1 box
    create_atoms 1 box
    mass 1 {System_melting.lattice[2]}
    write_data ./structures/initial_{System_melting.element}
        """
        
        lmp.commands_string(cmd)
        lmp.close()
        pipeline = import_file(f"./structures/initial_{System_melting.element}", multiple_frames=True)
        data = pipeline.compute()
        pipeline.add_to_scene()
        
        def modify_pipeline_input(frame: int, data: DataCollection):
            data.particles_.particle_types_.type_by_id_(1).color = System_melting.lattice[4]
            data.particles_.particle_types_.type_by_id_(1).radius = 0.6
        
        pipeline.modifiers.append(modify_pipeline_input)

        vp.zoom_all()
        window_tmp = vp.create_jupyter_widget()
        window_1.camera_params = window_tmp.camera_params
        window_1.orbit_center = vp.orbit_center
        window_1.refresh()
        pipeline.remove_from_scene()


    # connect the function with the button
    preview_button.on_click(preview_click)

    # set up the button for submission
    submit_button = widgets.Button(
        description='Submit',
        layout=Layout(width='auto', height='5%'),
        button_style='success'
    )


    start_T_show = widgets.Text(
        placeholder='Start Temperature (int)',
        description='Start T (K):',
        layout=Layout(width='auto', height='10%'),
        disabled=False
    )

    end_T_show = widgets.Text(
        placeholder='End Temperature (int)',
        description='End T (K):',
        layout=Layout(width='auto', height='10%'),
        disabled=False
    )

    seed_show = widgets.Text(
        placeholder='Seed (int)',
        description='Seed:',
        layout=Layout(width='auto', height='10%'),
        disabled=False
    )
    
    varibale_status_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))
    MD_status_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))
    MD_finish_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))
    Error_status_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=200))
    

    # define a function which can obtain the value form the interactive surface
    def button_click(sender):
        if Project_name_show.value == "" or start_T_show.value == "" or end_T_show.value == "" or seed_show.value == "":
           Project_name_show.style.danger = True
           submit_button.button_style='danger'
           MD_status_show.value = ""
           MD_finish_show.value = ""
           Error_status_show.value = f"<h2>You have not provided all input values!</h2>"
        else:
           if submit_button.button_style=='danger':
              submit_button.button_style='success'
           Error_status_show.value = ""
           System_melting.Project_name = Project_name_show.value
           System_melting.start_temperature = start_T_show.value
           System_melting.end_temperature = end_T_show.value
           System_melting.seed = seed_show.value
           submit_button.button_style='danger'
           MD_finish_show.value = ""
           MD_status_show.value = f"<h3>Molecular Dynamics is running ({System_melting.running_steps} steps)</h3>"
           calculation(System_melting)
           MD_finish_show.value = f"<h3>Molecular Dynamics is finished</h3>"
           submit_button.button_style='success'


    # connect the function with the button
    submit_button.on_click(button_click)

    # show the widgets
    show_windows = AppLayout(header=title_show,
                             center=window_1,
                             right_sidebar=VBox([Project_name_show,
                                                elements_show,
                                                box_length_show,
                                                aLat_show,
                                                preview_button,
                                                melting_point_show,
                                                start_T_show,
                                                end_T_show,
                                                seed_show,
                                                submit_button]),
                             left_sidebar=None,
                             footer=VBox([Error_status_show, MD_status_show, MD_finish_show]),
                             pane_widths=['0px', '820px', '300px'],
                             pane_heights=['65px', '600px', '140px'],
                             width="100%",
                             grid_gap="10px")
    display(show_windows)
    return System_melting


def input_solid_to_solid(s:MD_system):
    System_PT = MD_system()

    title_show = widgets.HTML(value="<h1>Molecular Dynamics Simulation of a solid-solid transformation</h1>", layout=Layout(width='100%', height='100px'))
    title_show.style.text_align='center'
    
    pipeline = import_file(f"./structures/ghost_hcp", multiple_frames=True)
    pipeline.add_to_scene()
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 2, -1))
    vp.zoom_all()
    window_1 = vp.create_jupyter_widget()
    window_1.layout = Layout(width='auto', height='auto')
    window_1.refresh()
    pipeline.remove_from_scene()
    
    # define element list
    elements_show = widgets.ToggleButtons(
        options=['Ti'],
        value = None,
        description='Element:',
        disabled=False,
        button_style='success',
        style={"button_width": "60px"},
        layout=Layout(width='auto', height='15%')
    )


    System_PT.element = 'Ti'
     
    aLat_show = widgets.SelectionSlider(
        options=np.linspace(System_PT.lattice[0], System_PT.lattice[1], num=20),
        description = 'Lattice constant:',
        disabled = False,
        orientation = 'horizontal',
        readout_format='.1f',
        layout=Layout(width='auto', height='10%'),
        style={"description_width": "110px"}
    )

    PT_tempeature_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))
    PT_tempeature_show.value = f"<h3>The transformation T of {System_PT.element} is {System_PT.lattice[3]} K.</h3>"

    # define Project name
    Project_name_show = widgets.Text(
        placeholder='Your Project name',
        description='Project:',
        layout=Layout(width='auto', height='10%'),
        disabled=False,
        style={"description_width": "50px"}
    )

    # define box_length 
    box_length_show = widgets.BoundedIntText(
        value=9,
        min=8,
        max=11,
        step=1,
        description='Size:',
        layout=Layout(width='auto', height='5%'),
        disabled=False
    )
    
    # Preview the structure
    preview_button = widgets.Button(
        description='Preview',
        layout=Layout(width='auto', height='5%', margin='0px 0px 35px 0px'),
        button_style='success'
    )

    def preview_click(sender):
        if Project_name_show.value == "":
           Project_name_show.style.danger = True
           submit_button.button_style='danger'
           MD_status_show.value = ""
           MD_finish_show.value = ""
           Error_status_show.value = f"<h2>You must name your project!</h2>"
        else:
           if submit_button.button_style=='danger':
              submit_button.button_style='success'
           Error_status_show.value = ""
        System_PT.box_length = box_length_show.value
        System_PT.lattice_constant = aLat_show.value
        write_sturcture_Ti(System_PT)
        lmp = lammps(cmdargs=["-sc", "log"])
        
        cmd = f"""
dimension 3
units metal
atom_style atomic
boundary p p p

read_data ./structures/hcp_Ti
replicate {System_PT.box_length} {System_PT.box_length} 6

write_data ./structures/initial_{System_PT.element}
        """
        
        lmp.commands_string(cmd)
        lmp.close()
        pipeline = import_file(f"./structures/initial_{System_PT.element}", multiple_frames=True)
        data = pipeline.compute()
        pipeline.add_to_scene()
        
        def modify_pipeline_input(frame: int, data: DataCollection):
            data.particles_.particle_types_.type_by_id_(1).color = System_PT.lattice[4]
            data.particles_.particle_types_.type_by_id_(1).radius = 0.6
        
        pipeline.modifiers.append(modify_pipeline_input)

        vp.zoom_all()
        window_tmp = vp.create_jupyter_widget()
        window_1.camera_params = window_tmp.camera_params
        window_1.orbit_center = vp.orbit_center
        window_1.refresh()
        pipeline.remove_from_scene()


    # connect the function with the button
    preview_button.on_click(preview_click)
    
    # set up the button for submission
    submit_button = widgets.Button(
        description='Submit',
        layout=Layout(width='auto', height='5%'),
        button_style='success'
    )

    start_T_show = widgets.Text(
        placeholder='Start Temperature (int)',
        description='Start T (K):',
        layout=Layout(width='auto', height='10%'),
        disabled=False
    )

    end_T_show = widgets.Text(
        placeholder='End Temperature (int)',
        description='End T (K):',
        layout=Layout(width='auto', height='10%'),
        disabled=False
    )

    seed_show = widgets.Text(
        placeholder='Seed (int)',
        description='Seed:',
        layout=Layout(width='auto', height='10%'),
        disabled=False
    )
 
    MD_status_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))
    MD_finish_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=50))
    Error_status_show = widgets.HTML(layout=Layout(width='auto', height='auto', fontsize=200))

    def button_click(sender):
        if Project_name_show.value == "" or start_T_show.value == "" or end_T_show.value == "" or seed_show.value == "":
           Project_name_show.style.danger = True
           submit_button.button_style='danger'
           MD_status_show.value = ""
           MD_finish_show.value = ""
           Error_status_show.value = f"<h2>You have not provided all input values!</h2>"
        else:
           if submit_button.button_style=='danger':
              submit_button.button_style='success'
           Error_status_show.value = ""
           System_PT.Project_name = Project_name_show.value
           System_PT.start_temperature = start_T_show.value
           System_PT.end_temperature = end_T_show.value
           System_PT.seed = seed_show.value
           submit_button.button_style='danger'
           MD_finish_show.value = ""
           MD_status_show.value = f"<h3>Molecular Dynamics is running (60000 steps)</h3>"
           calculation(System_PT)
           MD_finish_show.value = f"<h3>Molecular Dynamics is finished</h3>"
           submit_button.button_style='success'


    # connect the function with the button
    submit_button.on_click(button_click)

    # show the widgets
    show_windows = AppLayout(header=title_show,
                             center=window_1,
                             right_sidebar=VBox([Project_name_show,
                                                elements_show,
                                                box_length_show,
                                                aLat_show,
                                                preview_button,
                                                PT_tempeature_show,
                                                start_T_show,
                                                end_T_show,
                                                seed_show,
                                                submit_button]),
                             left_sidebar=None,
                             footer=VBox([Error_status_show, MD_status_show, MD_finish_show]),
                             pane_widths=['0px', '820px', '300px'],
                             pane_heights=['65px', '600px', '140px'],
                             width="100%",
                             grid_gap="10px")
    display(show_windows)
    return System_PT


if __name__ == '__main__':
    System_melting = input_melting(MD_system)
    # Show the animation
    animate(System_melting)
    
    System_PT = input_solid_to_solid(MD_system)
    # Show the animation
    animate(System_PT)
