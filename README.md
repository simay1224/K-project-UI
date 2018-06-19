# K_project-UI

This fork is for redesigning the UI for K_project system

### Installation

If you are using [Anaconda](https://www.anaconda.com/) for installing packages:

1. Download [Anaconda](https://www.anaconda.com/download/)

2. Install following packages (pygame and opencv), since they are not automatically installed by Anaconda:

```shell
$ conda install -c cogsci pygame
$ conda install -c menpo opencv
```

---

If you are using pip for installing packages:

Several dependent packages (not all) are documented in ```req.txt```, so to help you install those packages:
```shell
$ pip install -r req.txt
```


### Structure of the system (for personal notes)

```
msgbox (info)
welcome (4 modes)
    -> bodygame3
        -> several analysis files
        -> largly dependent on the result of analysis.py
            -> self.ana.done: will display the exercise list
                -> instruction.showlist
            -> self.ky.done: finish the entire exercise
            for each frame: display text in accordance to the current state
    -> trainingmode (simplified version of bodygame3.py)
    -> historylog (included in welcome.py)
        -> matplotlib graph
    -> instruction (included in welcome.py)
        -> wx printer connection
```

#### Notes for using ipython

To run the system in ipython:

```
%run [filename]
```

To run shell command in ipython;

```
![command]
```
