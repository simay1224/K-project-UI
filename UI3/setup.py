import cx_Freeze


#includefiles = []#,
                #(matplotlib.get_data_path(), "mpl-data")]
executables = [cx_Freeze.Executable("kinect_project.py")]



cx_Freeze.setup(
    name="Lymph_exer",
    version = "0.1",
    author = 'An-Ti Chaing and Qi Chen',
    options={"build_exe": {"includes":["matplotlib.backends.backend_tkagg"],
                           "packages":["pygame","matplotlib","numpy.core",
                           "numpy.lib","scipy.ndimage", "pandas",
                           "scipy.sparse.csgraph._validation"],
                           #"include_files":includefiles,
                           "excludes": ["collections.abc"]},  
                           },
    executables = executables

    )