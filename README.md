# PostProcessing

Table of contents
=================

<!--ts-->
   * [gh-md-toc](#gh-md-toc)
   * [Table of contents](#table-of-contents)
   * [Installation](#installation)
   * [Flow Visualization](#usage)
      * [How to create Flow Field Movies](#How-to-create-flow-field-movies)
      * [STDIN](#stdin)
      * [Local files](#local-files)
      * [Remote files](#remote-files)
      * [Multiple files](#multiple-files)
      * [Combo](#combo)
      * [Auto insert and update TOC](#auto-insert-and-update-toc)
      * [GitHub token](#github-token)
   * [Tests](#tests)
   * [Dependency](#dependency)
<!--te-->


### How to create Flow Field Movies

1. Create DNS input file with *TU* in the column of time units, not-specified.
2. Use python code **createInputs.py** to create the input file for the probe mode. This will substitute *TU* in the input file for the DNS for the corresponding time units for 2 periods, and will create the file **MOVIEPROBE_MASTER** where desired. The command is the following:
```python
  python src/PostProcessing/createInputs.py PROBEMODE path/to/movieDNS/masterFile path/to/datFile path/to/store/desired/inputFile
```
3. Divide DNS input in separate files, _z*_, appropriately.
4. Perform DNS with appropriate number of restarts, so far typically used 400
5. Divide the **MOVIEPROBE_MASTER** into appropriate number of files, _p*_
6. Generate file with the bounds **bounds.dat**, using the flag __PROBEMODE__:
```
  parallel bash src/DNS/PostProcessing/driverFlowFieldMovie.sh {} 'PROBEMODE' ::: path/to/p* 
```
7. The file **bounds.dat** has been created in the directory of **MOVIEPROBE_MASTER**. Now we need to create the input file with the bounds integrated, **MOVIELIST_MASTER**, to create the movies. 
```python
  python src/PostProcessing/createInputs.py MOVIEMODE path/to/datFile path/to/store/desired/inputFile
```
8. Divide the **MOVIELIST_MASTER** into appropriate number of files, _z*_
9. Finally, create the movies:
```
  parallel bash src/DNS/PostProcessing/driverFlowFieldMovie.sh {} 'MOVIEMODE' ::: path/to/z* 
```
## How to create Surface Velocity Movies 

###### Much Simpler
1. Create DNS input file with *TU* in the column of time units, not-specified.
2. Use python code **createInputs.py** to create the input file for the probe mode. This will substitute *TU* in the input file for the DNS for the corresponding time units for 2 periods, and will create the file **MOVIEPROBE_MASTER** where desired (for Flow Field Movies). The command is the following:
```python
  python src/PostProcessing/createInputs.py PROBEMODE path/to/movieDNS/masterFile path/to/datFile path/to/store/desired/inputFile
```
3. Divide DNS input in separate files appropriately.
4. Perform DNS with appropriate number of restarts, so far typically used 400
5. Finally, create the movies:
```
  parallel bash src/DNS/PostProcessing/driverSurfVelocMovie.sh {} 'MOVIEMODE' ::: path/to/DNS/z* 
```
