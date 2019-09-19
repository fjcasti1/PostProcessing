# PostProcessing

## Contents

<!--ts-->
   * [Flow Visualization](#flow-visualization)
      * [How to create Flow Field Movies](#How-to-create-flow-field-movies)
      * [How to create Surface Velocity Movies](#How-to-create-surface-velocity-movies)
<!--te-->

## Flow Visualization

### How to create Flow Field Movies

Different steps:
1. **Generate the Restarts:** 
* First we need to generate the job record file using the `zmeta_ReSWEEP_JOB_REC` code in the DNS repository. Pay special attention to the number of periods we want in the movie, *NT*, the number of time steps per period, *NtsT*, so the simulation doesn't crash and the number of restarts (future frames) to generate. Should use a number of time steps per period multiple of the number of frames we want to capture.
```
  bash src/DNS/zmeta_ReSWEEP_JOB_REC
```
* The file generated doesn't have the restars location yet. We add it using `createinputs.py`.
```python
  python src/PostProcessing/createInputs.py ADDRS path/to/masterFile path/to/datFile
  ```
* Run the DNS. NOTE that the mode has to be MOVIEDNS in order for many output restarts not to be erased.
```
  parallel bash src/DNS/SWEEP_JOB_REC.sh {} 'D-HH:MM' 'delayTime' 'MOVIEDNS' 'comment' ::: path/to/inputrecFile
```
2. **Create Probing File:**
* Generate the file `MOVIEPROBE_MASTER`
```python
  python src/PostProcessing/createInputs.py PROBEMODE path/to/masterFile path/to/datFile path/to/store/MOVIEPROBE_MASTER
```

3. **Probing**
* Split the `MOVIEPROBE_MASTER` file in the convenient subfiles *p**
* Run `driverFlowFieldMovie.sh` in PROBEMODE. It will generate the file `bounds.dat` in the same directory as `MOVIEPROBE_MASTER`.
```
  parallel bash src/PostProcessing/driverFlowFieldMovie.sh {} 'PROBEMODE' ::: path/to/p*
```
4. **Create Plotting File**
* Generate the file `MOVIELIST_MASTER`
```python
  python src/PostProcessing/createInputs.py MOVIEMODE path/to/bounds.dat path/to/store/MOVIELIST_MASTER
```
5. **Generate Movies**
* Split the `MOVIELIST_MASTER` file in the convenient subfiles *m**
* Run `driverFlowFieldMovie.sh` in MOVIEMODE. It will generate the frames in *.png* format and movies in *.mp4*.
```
  parallel bash src/PostProcessing/driverFlowFieldMovie.sh {} 'MOVIEMODE' ::: path/to/m*
```
<br>[⬆ Back to top](#PostProcessing)

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
