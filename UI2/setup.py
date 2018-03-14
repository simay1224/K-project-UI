import cx_Freeze


includefiles = ['./video/ex1.mpg', './video/ex2.mpg', './video/ex3.mpg','./video/ex4.mpg',
                './video/ex5.mpg', './video/ex6.mpg', './video/ex7.mpg',
		'./data/GPR_cluster_800_meter_fix_ex4.pkl', './data/GPR_cluster_800_meter_fix_ex5.pkl',
		'./data/GPR_cluster_800_meter_fix_ex6.pkl', './data/GPR_cluster_800_meter_fix_ex7.pkl',	
                './data/GT_V_data_mod_EX1.h5', './data/GT_V_data_mod_EX2.h5', 
		'./data/GT_V_data_mod_EX3.h5', './data/GT_V_data_mod_EX4.h5',
		'./data/GT_kinect_EX4_40_40_40.h5', './data/model_CNN_0521_K2M_rel.h5']#,
                #(matplotlib.get_data_path(), "mpl-data")]
executables = [cx_Freeze.Executable("kinect_project.py")]



cx_Freeze.setup(
    name="Lymph_exer",
    version = "0.1",
    author = 'An-Ti Chaing and Qi Chen',
    options={"build_exe": {"includes":["matplotlib.backends.backend_tkagg"],
                           "packages":["pygame","matplotlib","numpy.core",
                           "numpy.lib","scipy.ndimage",
                           "scipy.sparse.csgraph._validation"],
                           "include_files":includefiles,
                           "excludes": ["collections.abc"]},
                           
                           },
    executables = executables

    )