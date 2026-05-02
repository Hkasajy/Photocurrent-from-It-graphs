**Scientific background: **

photodetectors are devices that generate an electrical response (current) once subjected to light signals. Several new materials and different device geometries are being proposed in the literature, thus requiring several figures of merit to measure devices’ performance. Such as the devices photocurrent defined as the difference between the current produced once the device is illuminated and the current produced by the same device under no illumination, defined by Eq.1 

I_ph=Ion-I_(off/Dark)                                                                                                     Eq.1

In addition, an analogy to the signal to noise ration in these devices is the so called on/off ratio defined by Eq.2  

on/off =I_ph/I_Dark                                                                                                      Eq. 2                                                                                                                               
These metrics can be found by measuring the devices current with time, where the device is subject to pulses of light, in other words a graph of current with time, such as the one shown in the figure below. By measuring the current at a specify point in time it is possible to extract the current at that point, but for more rigorous analysis it is recommended to calculate the median of a given time window. 

![An example of an It graph](Docs/images/It_graph.png)

The aim of this project is to introduce a simple software that facilitates these calculations. 

**Installation: **
 
To install the software, simply use these commands: 
git clone https://github.com/Hkasajy/Photocurrent-from-It-graphs.git
cd Photocurrent-from-It-graphs
pip install .
run-manual-picker

**Usage, input and output formats: 
**
The software currently takes .xlsx files, to prepare the input file simple add the time column, and the current values. The software supports multiple devices. Below is an example of an input file for It traces collected for 4 bar coated perovskite photodetector under increasing light power, this file is included in the package. 

![An example of an input file](Docs/images/Input_example.png) 


The user can name the columns as they wish, where the first cell of the column is assumed to be the device index which will be conserved in the output file.
Once the software is run, a popup will allow the user to select an input file as shown here,

![Input data selection](Docs/images/selection_window.png)

Once the user selects the input file in this example (Sample It data), another popup will ask the user to select where to save the resulting output data here called (Sample It data_Results)

![Output file selection](Docs/images/output_selection.png)

The package includes a folder to save the output, but the user is free to select any location on their device to save the data. The only limitation on naming is that the output cannot have the same name as the output file. 
Then one final popup will ask the user to select the time column, this provides the user with more freedom when preparing the input excel sheet, and to avoid any possible errors. 

![Time column selection](Docs/images/time_column_selection.png)

Once the user selects their files and time column, to assure propre data loading, a graph with all devices in the input file will be shown.

![Device overlay](Docs/images/device_overplot.png)

Once the user exits this window with the x button, the main part of the software starts, where a graph for each device in the input file will be shown one by one, such as device S1 shown here. 

![The selection window](Docs/images/Selection_window.png)

The basic commands are shown in the figure and are clear to the user, but are restated here.
Each click will register a horizontal line in the graph defining the start of a time window, as shown 

![Selection window showing the first click](Docs/images/Selection_window_with_first_click)

First click will register the start and the second will register the end of the window. 
First two clicks will define the on window (Red shading), and the last two clicks will define the off window (Blue shading), as shown

![first on off window](Docs/images/on_off_selected.png)

The user then can continue with defining windows, the end result could look like this 

![A completed on off windows defintion](Docs/images/on_off_selected_completed.png)

However, the user is free to select as many windows as required. 
The final output data will be saved in an excel file such as this one 


