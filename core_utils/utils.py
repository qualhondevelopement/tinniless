from .constants import *

def return_all_tinnitus_types():
    types=  [SUBJECTIVE_TINNITUS,OBJECTIVE_TINNITUS,TONAL_TINNITUS,PULSATILE_TINNITUS,MUSCULAR_TINNITUS,NEUROLOGICAL_TINNITUS,SOMATIC_TINNITUS,SENSORINEURAL_TINNITUS]
    for i in range(len(types)):
        types[i] = types[i].replace("_", " ")
        types[i] = types[i].capitalize()
    print(types)
        
    return types
        
        