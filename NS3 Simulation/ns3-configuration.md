# NS-3 Installation and Visualization Guide

This guide provides step-by-step instructions to install and configure **ns-3** (a discrete-event network simulator) on Ubuntu, including support for **NetAnim** and **PyViz** visualizations.

We use **ns-3.43** as the simulation framework for the cloud-integrated IoT environment.

------

## 📦 1. Prerequisites

Recommended environment:

- **Ubuntu 20.04** or **22.04** or **MacOS**
- **Python 3.8+**
- **g++ ≥ 9**

### Install Required Dependencies

```bash
sudo apt update
sudo apt install -y \
    g++ \
    python3 \
    python3-pip \
    python3-dev \
    qt5-default \
    mercurial \
    git \
    cmake \
    libc6-dev \
    libsqlite3-dev \
    libgtk-3-dev \
    vtun \
    lxc \
    libxml2-dev \
    libboost-all-dev \
    openmpi-bin \
    openmpi-common \
    openmpi-doc \
    libopenmpi-dev \
    libgsl-dev \
    libgtk2.0-dev \
    libxmu-dev \
    libxt-dev
```

------

## 🧱 2. Download and Build NS-3

### Clone the Official Repository

```bash
git clone https://gitlab.com/nsnam/ns-3-dev.git
cd ns-3-dev
```

### Configure and Build

```bash
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

After building, all components will be available under the `build/` directory.

------

## 🧪 3. Verify Installation

Run a simple test to check your installation:

```bash
./ns3 run hello-simulator
```

Expected output:

```bash
Hello Simulator
```

------

## 🖥️ 4. Visualization Tools

### 4.1 NetAnim (GUI Animator)

NetAnim is a GUI tool that visualizes ns-3 simulation events in real-time or offline.

#### Installation

```bash
git clone https://gitlab.com/nsnam/netanim.git
cd netanim
qmake NetAnim.pro
make -j4
```

This will generate a `NetAnim` binary:

```bash
./NetAnim
```

### 4.2 PyViz (Python-based Visualizer, optional)

Install additional packages:

```bash
sudo apt install python3-pygraphviz python3-pygoocanvas
```

Run a simulation with `--vis` enabled (e.g., WiFi ad-hoc example):

```bash
./ns3 run scratch/wifi-simple-adhoc-grid --vis
```

------

## 🧪 5. Run Example Scenarios

### 5.1 Run Built-in Example

```bash
./ns3 run dsdv-manet
```

### 5.2 Run Custom Scripts

Place your C++ file in the `scratch/` folder:

```bash
./ns3 run scratch/my_example
```

------

## 🧹 6. Clean Build Files

```bash
./ns3 clean
```

------

## ⚠️ 7. Common Issues

| Issue                      | Solution                                                     |
| :------------------------- | ------------------------------------------------------------ |
| Missing modules            | Use `--enable-examples --enable-tests` during configure <br>or use conda install <missing package> (if you have conda) |
| NetAnim doesn't show nodes | Ensure `AnimationInterface` is used and XML file is generated |
| PyViz fails                | Check that `pygraphviz` and `pygoocanvas` are installed correctly |

*Tips：'pip install <missing packages>' can't help you cope with missing modules problem.*

------

## 📚 8. References

- NS-3 Official Documentation (https://www.nsnam.org/documentation/)

------

Let me know if you'd like to customize this guide further (e.g., specific modules, integration with your scripts, automation tips).