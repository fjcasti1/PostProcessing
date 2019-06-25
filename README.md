# PostProcessing

## How to create Flow Field Movies
1. Perform DNS with appropriate number of restarts, so far typically used 400
2. Use python code **createInputs.py** to create the input file for the probe mode:
```python
  python src/PostProcessing/createInputs.py PROBEMODE path/to/movieDNS/masterFile path/to/datFile path/to/store/desired/inputFile
```
3. Divide the **MOVIEPROBE_MASTER** into appropriate number of files, _p*_
4. Generate file with the bounds **bounds.dat**, using the flag __PROBEMODE__:
```
  parallel bash src/DNS/PostProcessing/driverFlowFieldMovie.sh {} 'PROBEMODE' ::: path/to/p* 
```
5. The file **bounds.dat** has been created in the directory of **MOVIEPROBE_MASTER**. Now we need to create the input file with the bounds integrated, **MOVIELIST_MASTER**, to create the movies. 
```python
  python src/PostProcessing/createInputs.py MOVIEMODE path/to/datFile path/to/store/desired/inputFile
```
6. Divide the **MOVIELIST_MASTER** into appropriate number of files, _z*_
7. Finally, create the movies:
```
  parallel bash src/DNS/PostProcessing/driverFlowFieldMovie.sh {} 'MOVIEMODE' ::: path/to/z* 
```
