# Compile & Install Python 3.x


	Legend:
	$ ... run command as the user
	# ... run command as root or with sudo privileges. (e.g. sudo <command>)


macOS 10.15 Users NOTE: Since 10.15 openssl isn´t used anymore. After installing/updating openssl, please also link missing crypto libraries to the openssl directory with

	# ln -s /usr/local/opt/openssl/lib/libssl.dylib libssl.dylib
	# ln -s /usr/local/opt/openssl/lib/libcrypto.dylib libcrypto.dylib

## 1) Gather latest Python version (now 3.8)
https://www.python.org/downloads/source/
### Direct Download link for macOS and Linux
	$ wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
### Direct Download link for windows10
	https://www.python.org/downloads/release/python-380/
a) Please download the "Windows x86-64 executeable installer". If you don't want to use the installer, you have to install python manually!
b) On the installation window ensure "Add Python 3.8 to PATH" is checked.
c) After the installation click on "Disable path length limit"

We won't cover building python3.8 on windows, because the libraries are always compiled for windows already.
So just download python3.8 from https://www.python.org/downloads/release/python-380/

If you have after the installation still a git bash window open. Close it! You need to reopen it to initialize the new PATH variable, which points now to the python binaries.

Skip now to STEP 6!

## 2) Extract Archive
	$ tar -xzvf Python*tgz # Subdirectory will be created :P

## 3) (Maybe optional) Install prerequesitites to compile
### Ubuntu / Debian
	$ apt install build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev

### macOS
	$ sudo xcode-select --install
	$ brew install cmake # if brew installed (if not see: http://www.brew.sh)
	$ brew install openssl; brew upgrade openssl

## 4) Create build folder and make
	$ cd Python*/; mkdir build; cd build

## 5) Configure, Make and Install
### Configure for platform ...
For Debian / Ubuntu:
	$ ../configure --enable-optimizations
For macOS:
	$ ../configure --with-openssl="/usr/local/Cellar/openssl/*/" --enable-optimizations

After configure please check in the last lines of the output if a "yes" for some of those lines appear:
	checking for openssl/ssl.h in /usr/local/Cellar/openssl/1.0.2t/... yes
	checking whether compiling and linking against OpenSSL works... yes

### For every platform towards:
	$ make -j8 build_all
	$ sudo make install # Statt install kann auch altinstall verwendet werden 'altinstall' würde nur bedeuten, vorherig installierte python3.x Versionen nich$


## 6) Freuen wenn der folgende Befehl ausgeführt wird :)
	$ python3.8 --version

## 7) Paketmanager für Python3.7 aktualisieren
	# pip3 install --upgrade pip

INFO: Bisher keine Probleme gesehen, wenn man das pip von einer früheren Python Version auch nutzt.

## 8) Virtuelles Pip (pipenv) installieren
	$ pip3 install pipenv

## 9) Pipenv Project Sync
!! Bitte per cd in das github Projektverzeichnis wechseln

	$ pipenv sync
