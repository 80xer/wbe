echo �۾�����:%dt%

SET mypath=%~dp0

echo %mypath:~0,-1%

python %mypath:~0,-1%\run.py %*

pause