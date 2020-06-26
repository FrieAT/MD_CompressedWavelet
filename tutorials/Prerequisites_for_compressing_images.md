# Prerequisites for compressing images


	Legend:
	$ ... run command as the user
	# ... run command as root or with sudo privileges. (e.g. sudo <command>)

## 1) Install pre-compiled pre-requisites
For Debian / Ubuntu:
`
	# apt install ffmpeg yasm libjpeg-dev libpng-dev cmake imagemagick imagemagick-doc jxrlib-devel
`
For macOS:
`
	$ brew install ffmpeg jxrlib libbpg
`
	NOTICE: For macOS the bpg library is already pre-compiled available.

## 1b) Compile bpg-lib for non-macOS user's

### Download sources
`
	$ wget https://bellard.org/bpg/libbpg-0.9.8.tar.gz
`
### Extract archive
`
	$ tar -xf libbpg*.tar.gz
`
### Compile & Install
`
	$ cd libbpg*/ && make && sudo make install
`

## 2) Customizing delegate.xml from ImageMagick
Sadly libbpg isn't correctly delegat-ed by image magick within version 6, so we have to adjust the delegate.xml:

If you have installed ImageMagick 7 or later, you don't need to change that.

For Debian / Ubuntu:
`
	# nano /etc/ImageMagick-6/delegates.xml
`
For macOS:
`
	# nano /usr/local/Cellar/imagemagick/7.0.10-6_1/etc/ImageMagick-7/delegates.xml
`

Search for `bpgenc` and change the line to:
`
<delegate decode="png" encode="bpg" command="&quot;bpgenc&quot; -b 12 -q &quot;%~&quot; -o &quot;%o&quot; &quot;%i&quot;"/>
`