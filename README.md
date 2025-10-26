# Jetson Nano Configuration Guide


**Prerequisites:**
- Run `sudo apt update && sudo apt upgrade` before installations to avoid issues.

## Changing the Graphical Environment for Optimization

To switch to a lighter desktop environment like LXDE for better performance:

1. At login or logout, select your profile.
2. Click the gear icon and choose "LXDE".
3. Once logged in, open a terminal and switch the display manager from GDM (GNOME Display Manager) to LightDM:

```bash
sudo dpkg-reconfigure lightdm
```

Select LightDM as the default and reboot.

## Changing the Keyboard Layout

If the software-configured keyboard doesn't match your hardware:

```bash
sudo dpkg-reconfigure keyboard-configuration
```

- Keep defaults for most options.
- In the second section (layout), select your preferred option (e.g., "Spanish - Latin American").

## Setting the Date and Time (Persistent)

To set and persist the timezone, time, and enable NTP synchronization:

```bash
# Set timezone (replace with your zone, e.g., America/Bogota)
sudo timedatectl set-timezone America/Bogota

# Manually set the time (format: YYYY-MM-DD HH:MM:SS)
sudo timedatectl set-time "2025-09-30 09:30:00"

# Enable NTP and restart the service
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
```

## SSH Connections

Connect to a remote Jetson Nano via SSH:

```bash
ssh username@ip_address
```

### Copying Folders via SCP

- Local to remote:

```bash
scp -r /home/youruser/project remoteuser@192.168.1.100:/var/www/
```

- Remote to local:

```bash
scp -r remoteuser@server:/path/to/remote/folder /path/to/local/destination
```

## Basic Installations

Install common tools:

```bash
sudo apt install nano v4l-utils git-all
```

For Conda, see the dedicated section below.

## Creating a Compressed Backup via Terminal

1. Check your SD card device name:

```bash
lsblk
```

(Typically `/dev/mmcblk0`.)

2. Unmount the SD card and all partitions (replace `mmcblk0` if different):

```bash
sudo umount /dev/mmcblk0p* 2>/dev/null
```

3. Create the backup:

```bash
sudo dd if=/dev/mmcblk0 bs=64K status=progress | gzip > "$HOME/jetson_nano_$(date +%Y-%m-%d_%H-%M%P).img.gz"
```

- `dd`: Data duplicator for copying.
- `if=`: Input device (SD card).
- `bs=64K`: Block size (standard value).
- `status=progress`: Shows real-time progress.
- `| gzip`: Compresses the output.
- `>`: Saves to the specified file in `$HOME`.

### Verification

```bash
gzip -t "$HOME/jetson_nano_YYYY-MM-DD_HH-MM.img.gz"
```

No output means success; otherwise, it shows an error.

## Installing Visual Studio Code (VS Code)

1. Navigate to your Downloads folder (use `ls` and `cd`).
2. Install curl if needed:

```bash
sudo apt install curl
```

3. Download the ARM64 deb package:

```bash
curl -L https://github.com/toolboc/vscode/releases/download/1.32.3/code-oss_1.32.3-arm64.deb -o code-oss_1.32.3-arm64.deb
```

4. Install:

```bash
sudo dpkg -i code-oss_1.32.3-arm64.deb
```

5. Run:

```bash
code-oss
```

### Installing a Newer Version of VS Code

Create a folder, download a specific version (e.g., 1.98) via curl, and make it executable:

1. Create a directory:

```bash
mkdir vscode-1.98 && cd vscode-1.98
```

2. Download (replace URL with the latest ARM64 tarball from https://code.visualstudio.com/):

```bash
curl -L https://update.code.visualstudio.com/1.98.0/linux-arm64/stable -o vscode.tar.gz
```

3. Extract and make executable:

```bash
tar -xzf vscode.tar.gz
cd VSCode-linux-arm64
chmod +x code
./code
```

## Installing Git and Using Repositories

Install Git:

```bash
sudo apt install git
```

To clone and use a repository:

```bash
git clone https://github.com/example/repo.git
cd repo
# Make changes, commit, push as needed
git add .
git commit -m "Your message"
git push origin main
```

## Installing Python Libraries

General installation:

```bash
sudo apt install python3-matplotlib
```

### Special Case: OpenCV

Due to version conflicts between Python 2 and 3:

1. Install the Python 3 version:

```bash
sudo apt install python3-opencv
```

2. Remove the Python 2 version (if installed) to resolve conflicts:

```bash
sudo apt remove python-opencv
```

For a lighter OpenCV in a Conda environment (see Conda section):

```bash
conda install -c conda-forge opencv
# Or via pip
pip install opencv-python
```

## Working with Docker (jetson-inference)

Enter the Docker container (assuming jetson-inference repo is cloned and set up):

```bash
cd jetson-inference
./docker/run.sh
```

- `run.sh` is typically created during jetson-inference setup (e.g., via build scripts).
- `./` executes it from the current directory (as it's not in PATH).

### Testing Jetson Models

1. Enter the Docker container (above).
2. Navigate to models:

```bash
cd /build/aarch64/bin
```

3. Run a model (e.g., ImageNet on an image):

```bash
./imagenet.py images/orange_0.jpg images/test/output_0.jpg  # Default network: googlenet
```

4. To open the output directory:

```bash
xdg-open ~/jetson-inference/data/images/test/
```

## Checking and Running Cameras

Install v4l-utils if not present (check with `v4l2-ctl --version`):

```bash
sudo apt install v4l-utils
```

List devices:

```bash
v4l2-ctl --list-devices
```

Run capture:

```bash
nvgstcapture-1.0
```

If window issues occur:

```bash
sudo systemctl restart nvargus-daemon
nvgstcapture-1.0
```

### Checking Camera Capture Support

- Output stream details appear in `nvgstcapture-1.0`.
- List formats:

```bash
v4l2-ctl --list-formats-ext -d /dev/video0
```

For GStreamer pipelines, parameters, and responses: Refer to example code or documentation (e.g., Jetson Nano camera pipelines like `nvarguscamerasrc` for CSI cameras).

## Drawing a Rectangle with OpenCV

Example loop to capture frames and draw a rectangle:

```python
import cv2

cap = cv2.VideoCapture(0)  # Open camera

while True:
    ret, frame = cap.read()  # Read frame
    if not ret:
        break
    
    # Draw rectangle (start_point, end_point, color, thickness)
    cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 2)
    
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### What is ROI and How to Use It

ROI (Region of Interest) in OpenCV is a subset of an image for focused processing (e.g., cropping).

Example:

```python
import cv2

img = cv2.imread('image.jpg')
roi = img[100:200, 100:200]  # Crop rows 100-200, cols 100-200
cv2.imshow('ROI', roi)
cv2.waitKey(0)
```

## Conda Setup and Management

### Downloading Miniconda

- On a standard computer (x86_64):

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

- On Jetson Nano (aarch64):

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
```

If certificate issues:

```bash
wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
```

### Installing Miniconda

```bash
bash ~/Miniconda3-latest-Linux-aarch64.sh
```

After installation:

```bash
source ~/.bashrc
```

You should see `(base)` in your prompt.

### Creating an Environment

```bash
conda create --name my_env python=3.12
# Or with packages and versions
conda create --name my_env python=3.12 matplotlib=3.8
```

Environments are saved in `~/miniconda3/envs/`.

### Managing Environments

- List environments:

```bash
conda env list
# Or
conda info --envs
```

- Activate:

```bash
conda activate my_env
```

- Deactivate:

```bash
conda deactivate
```

- Switch: Activate the new one directly.
- Remove:

```bash
conda remove --name my_env --all
```

- Clone:

```bash
conda create --name new_env --clone old_env
```

### Locking and Sharing Environments

1. Install conda-project:

```bash
conda install conda-project
```

2. Initialize project (creates `conda-project.yml`):

```bash
conda-project init
```

3. Lock:

```bash
conda-project lock
```

(Produces `conda-lock.default.yml` for sharing.)

Export environment:

```bash
conda env export > environment.yml
```

View YAML:

```bash
less environment.yml
```

Create from YAML:

```bash
conda env create --file environment.yml
```

### Version Specifiers

- Exact: `python=3.12.1`
- Greater/equal: `python>=3.11`
- Less/equal: `python<=3.12`
- Range (exclusive): `python>3.10,<3.12`
- Range (inclusive): `python>=3.10,<=3.12`
- Prefix: `python[version='3.12.*']`

### Installing Packages

```bash
conda install matplotlib
# In a specific env (from base)
conda install matplotlib --name my_env
```

Search:

```bash
conda search matplotlib=3.8
```

Download only:

```bash
conda install matplotlib --download-only
```

Update:

```bash
conda update matplotlib
# All packages
conda update --all
```

## Adafruit and GPIO Setup

Install Adafruit Blinka:

```bash
pip3 install adafruit-blinka
```

Install Jetson GPIO:

```bash
pip install Jetson.GPIO
```

Add permissions:

```bash
sudo usermod -aG gpio,i2c $USER
# Optionally for SPI and dialout
sudo usermod -aG spi,dialout $USER
```

Verify rules file: `/etc/udev/rules.d/99-gpio.rules`

If missing or permissions issues:

```bash
sudo groupadd -f gpio
printf 'KERNEL=="gpiochip*", MODE="0660", GROUP="gpio", SYMLINK+="gpiochip%%n"\n' | sudo tee /etc/udev/rules.d/99-gpio.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reboot after changes.

Check installation: Run `BlinkaTest.py` (from Adafruit examples).

**Note:** The backup from early 2025-10-02 does not include this setup.

## Working with I2C and PCA9685

In the environment with Adafruit:

```bash
pip3 install adafruit-circuitpython-pca9685
pip3 install adafruit-circuitpython-servokit
```

Use for servo control or PWM (refer to Adafruit docs for examples).

## Troubleshooting OpenCV Issues

Check version and build info:

```python
import cv2
print(cv2.__version__)  # Should be 4.x.x
print(cv2.getBuildInformation())  # Check for GStreamer: YES
```

If fails (e.g., no GStreamer support):

1. Purge existing OpenCV:

```bash
sudo apt purge python3-opencv python-opencv -y
sudo apt purge *libopencv* -y
sudo apt autoremove -y
```

2. Clone and build from JetsonHacksNano repo:

```bash
git clone https://github.com/JetsonHacksNano/buildOpenCV.git
cd buildOpenCV
./buildOpenCV.sh
```

### Linking OpenCV with Symlink in Conda Env

1. Find native cv2 path:

```bash
find /usr/local/lib -name "cv2*.so" 2>/dev/null | grep python
```

2. Activate env and clean:

```bash
conda activate my_env
pip uninstall opencv-python opencv-contrib-python -y
conda uninstall opencv opencv-python opencv-contrib-python -y
```

3. Find env site-packages:

```python
python -c "import site; print(site.getsitepackages())"
```

4. Create symlink (replace paths):

```bash
ln -s /usr/local/lib/python3.x/site-packages/cv2.so /path/to/conda/env/site-packages/cv2.so
```

Deactivate/activate the env and test.
