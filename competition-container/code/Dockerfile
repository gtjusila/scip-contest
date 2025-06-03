############################################
# BUILD IMAGE
############################################
FROM ubuntu:24.04 AS builder
# --- build stage – all the tools we need to build SCIP and PYSCIPOPT -----------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        cmake \
        g++ \
        gdb \
        m4 \
        xz-utils \
        libgmp-dev \
        libmpfr-dev\
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
        # add just what PySCIPOpt’s build needs:
        python3 \
        python3-venv \
        python3-dev \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# --- build & install SCIP -----------------------------------------------------
WORKDIR /tmp


RUN set -eux; \
    wget -O scip.tgz "https://www.scipopt.org/download/release/scipoptsuite-9.2.2.tgz"; \
    tar xf scip.tgz && rm scip.tgz; \
    cd scipoptsuite-9.2.2; \
    rm -rf scip; \
    rm -rf ug; \
    rm -rf zimpl; \
    rm -rf gcg; \
    git clone --depth 1 --branch master https://github.com/scipopt/scip; \
    mkdir scip_build && cd scip_build; \
    cmake .. \
          -DCMAKE_INSTALL_PREFIX=/opt/scip \
          -DUG=OFF\
          -DGCG=OFF \
          -DZIMPL=OFF\
          -DAUTOBUILD=on; \
    make -j"$(nproc)" install; \
    strip --strip-unneeded /opt/scip/bin/*  || true; \
    strip --strip-unneeded /opt/scip/lib/*.so || true; \
    find  /opt/scip/lib -name '*.a' -delete; \
    ############## 6. Clean up build detritus & git ########################
    cd /; \
    rm -rf /tmp/scip* 


# --- build PySCIPOpt -------------------------------------
ENV SCIPOPTDIR=/opt/scip

RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir cython pytest && \
    git clone --branch scip10 --depth 1 https://github.com/scipopt/PySCIPOpt.git && \
    cd PySCIPOpt && \
    pip install --no-cache-dir . && \
    cd .. && rm -rf PySCIPOpt



# --- OPTIONAL: build Rust tooling here and copy artefacts later --------------
# RUN curl -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
# RUN cargo build --release --workspace

############################################
# RUNTIME IMAGE 
############################################
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake pkg-config gdb valgrind \
    python3 python3-venv python3-pip \
    libgmp10 liblapack3 libgsl27 libcliquer-dev gfortran libopenblas0 \
    libtbb12 \
    libboost-program-options1.83.0 libboost-serialization1.83.0 \
    libboost-regex1.83.0 libboost-iostreams1.83.0 \
    libreadline8 zlib1g \
    libmpfr-dev\
    vim nano git zip unzip \
    && rm -rf /var/lib/apt/lists/*

# — pull in only what we need -------------------------------------------------
COPY --from=builder /opt/scip   /opt/scip
COPY --from=builder /opt/venv   /opt/venv
ENV SCIPOPTDIR=/opt/scip

# Minimalistic linrary for  scientific computing
RUN . /opt/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas scipy scikit-learn

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
RUN echo "alias evaluate='/opt/venv/bin/python /opt/evaluate/evaluate.py'" >> /root/.bashrc

# Configure bashrc to activate the virtual environment
RUN echo "source /opt/venv/bin/activate" >> /root/.bashrc

# Copy the entrypoint script into /root
COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

# Create mount points (redundant, but safe)
RUN mkdir -p /mnt/user-code /mnt/result /data/testcases

# Entrypoint and default command
ENTRYPOINT ["/root/entrypoint.sh"]

CMD ["/bin/bash"]
