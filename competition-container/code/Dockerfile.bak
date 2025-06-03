FROM ubuntu:24.04

# Support for C
RUN apt-get update && apt-get install -y \
    wget \
    cmake \
    g++ \
    gdb \
    m4 \
    xz-utils \
    libgmp-dev \
    unzip \
    zlib1g-dev \
    libboost-program-options-dev \
    libboost-serialization-dev \
    libboost-regex-dev \
    libboost-iostreams-dev \
    libtbb-dev \
    libreadline-dev \
    pkg-config \
    git \
    liblapack-dev \
    libgsl-dev \
    flex \
    bison \
    libcliquer-dev \
    gfortran \
    file \
    dpkg-dev \
    libopenblas-dev \
    rpm \
    vim \
    nano \
    curl \
    clang \
    && apt-get clean

# Download and build SCIP v9.2.2 from tarball
WORKDIR /opt
RUN wget https://www.scipopt.org/download/release/scipoptsuite-9.2.2.tgz && \
    tar -xzf scipoptsuite-9.2.2.tgz && \
    rm scipoptsuite-9.2.2.tgz
WORKDIR /opt/scipoptsuite-9.2.2
RUN mkdir build && cd build && \
    cmake .. -DAUTOBUILD=on -DCMAKE_INSTALL_PREFIX=/opt/scip && \
    make -j2 && \
    make install

# Install Python 3 and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

# Create a global virtual environment at /opt/venv
RUN python3 -m venv /opt/venv

# Install build tools for PySCIPOpt
RUN /opt/venv/bin/pip install --upgrade pip cython

# Clone and build PySCIPOpt v5.5.0 from GitHub
WORKDIR /opt
RUN git clone --branch v5.5.0 --depth 1 https://github.com/scipopt/PySCIPOpt.git

# Install PySCIPOpt in the global virtual environment
WORKDIR /opt/PySCIPOpt
RUN /opt/venv/bin/pip install --upgrade pip setuptools cython
ENV SCIPOPTDIR=/opt/scip
RUN /opt/venv/bin/python -m pip install .

# Configure bashrc to activate the virtual environment
RUN echo "source /opt/venv/bin/activate" >> /root/.bashrc

# Support Rust
# Install Rust (stable)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
RUN . "$HOME/.cargo/env"


# Copy test cases into the image
WORKDIR /data/testcases
COPY testcases.zip .

# Extract test cases
RUN unzip testcases.zip && rm testcases.zip

# Create mount points for user code and results
RUN mkdir -p /mnt/user-code /mnt/result

# Copy the evaluation script into the image
COPY evaluate.py /opt/evaluate/evaluate.py

# Set up alias for evaluate command
RUN echo "alias evaluate='source /opt/venv/bin/activate && python /opt/evaluate/evaluate.py'" >> /root/.bashrc

# Copy the entrypoint script into /root
COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

# Create mount points
RUN mkdir -p /mnt/user-code /mnt/result /data/testcases

# Set entrypoint to /root/entrypoint.sh
ENTRYPOINT ["/root/entrypoint.sh"]

# Default command: bash shell
CMD ["/bin/bash"]