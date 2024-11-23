@echo off
cd /d "C:\proj\wpp"
git status
git add .
git commit -m "Atualizando"
git push origin master
pause
