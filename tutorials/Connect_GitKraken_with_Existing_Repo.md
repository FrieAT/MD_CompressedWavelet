# Connect GitKraken with existing repository
You only need to do this, if you want to use a GUI for managing git.
If you have skills in another git-GUI or you are familiar with the git command line handling (e.g. branching, merging, conflicts, ...),
then you don't need to do this tutorial.

WARNING: This tutorial depends on "Configuring repository from github", so if you haven't done this, please make sure to configure your access to that repo.

## 1) Download and Install GitKraken "Git GUI"
https://www.gitkraken.com/

## 2) Login in GitKranken
You may use a alternative login, but you can also login with your GitHub Account information.

## 3) Next Window: "Set Up Your Profile"
Important fields are "Name" and "Email". Those informations are used for your commits.
You may use any Email you want.

## 4) Agree the EULA.
Yeaaah!

## 5) Add existing repository
Select in top the pane "New Tab" and then "Open a repo".
Choose the location of your git repository by "Browse".

## 6) Done!
Yeah, right. You don't have to configure the ssh keys for GitKraken, because we defined them already in "~/.ssh/config".
So no need to make more here.

One last thing:
Always create a branch from our master repository.
The naming convention for the branch is always "yyy-mm-dd-description".

So for example if you make a new class for kNN, then maybe something like:
"2019-11-06-knn-first-approach".

Never push to master, if you coded something! Use Pull requests, so everyone can see what you have done.

Thanks!
