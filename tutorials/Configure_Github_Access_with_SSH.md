# Configure GitHub Access with SSH
A very convinient way!

### 0) For Windows: Install Git Bash
	https://git-scm.com/downloads
	After installation, open Git-Bash by rightlicking somewhere on the explorer.
	On windows: If you need a command as root (if a command is shown with a '#'), then you need to open another Git Bash Window with Administrator rights!

### 1) Generate pair of ssh keys for your github account
	$ ssh-keygen -t rsa -f $HOME/.ssh/uniGithub.id -C <gitHubAccountName>

If asked for a password, it is just for your private key. It shouldn't be the same as your github account.
This password is used, if you "git pull/push". You may leave it blank, if you want to.
Just press enter, if no password is needed.

### 2) Create alias for accessing github with this special key.
	$ nano .ssh/config

And insert the following text:

	Host uniGithub
		HostName github.com
		Port 22
		User git
		IdentityFile ~/.ssh/uniGithub.id

Tabulators are important! First row has no tab. All other rows have 1 tab from the left.

The alias for the connection is defined in the "Host" row.
It has nothing to-do with the name  of the private key.
You may name the alias, as you wish!

### 3) Add public key to your github account

Copy the content of "~/.ssh/uniGithub.id.pub":
	$ cat ~/.ssh/uniGithub.id.pub

Open the following URL, which redirects to the settings of your github profile and opens the SSH pane:
https://github.com/settings/keys

Add "New SSH key" and just paste the copied public key content into the "Key" text-field.
You may ignore the "Title" text-field. It isn't needed.

### 4) Test the connection
If you enter the following command:
	$ ssh uniGithub
Optional: If something occurs like below, just answer with "yes":
	Are you sure you want to continue connecting (yes/no)?
You should see something like
	Hi FrieAT! You've successfully authenticated, but GitHub does not provide shell access.

### 5) Clone the repository
Below the command, which you dont have to modify. The reason why "FrieAT" is used, is because the repository was created with the account "FrieAT"
and you are just a collaborateur to this project.
	
Switch to the directory with "cd", you want to place the repository!

	$ git clone uniGithub:FrieAT/IP_WavletFV.git

### 6) Be happy and make a coffee
Just dont ready any further, you are done :P
