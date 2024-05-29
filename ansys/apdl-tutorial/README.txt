1) I use Notepad++ to view APDL code - install the *.xml as a user defined 
language in Notepad++, close and reopen Notepad++ so it adds the language
to the list and then finally open the ANSYS *.inp file. 

2) Always start ANSYS APDL using the launcher - this allows you to set the
working directory easily and specify high performance computing options. Go to
the High Performance Computing tab and select "Shared Memory Parallel" and 
specify the number of cores on your machine (8 on your UKAEA laptop).

3) Now work through the tutorial in the *.inp file.

UPDATE 2024: I now use vscode for viewing apdl files - use one of the in-built
highlighting extensions 