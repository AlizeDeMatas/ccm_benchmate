FROM mambaorg/micromamba:1.5.10

USER root
WORKDIR /opt/benchmate

COPY environment.yaml /tmp/environment.yaml
COPY requirements.txt /tmp/requirements.txt
COPY . /opt/benchmate

RUN micromamba install -y -n base -c conda-forge -c bioconda python=3.10 pip git && \
    micromamba install -y -n base -f /tmp/environment.yaml && \
    micromamba clean --all --yes

# torch first
RUN micromamba run -n base pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1

# install everything else (remove/comment flash_attn + detectron2 in requirements.txt)
RUN micromamba run -n base pip install --no-cache-dir -r /tmp/requirements.txt

# then the two torch-coupled packages
RUN micromamba run -n base pip install --no-cache-dir --no-build-isolation flash_attn
RUN micromamba run -n base pip install --no-cache-dir --no-build-isolation \
    git+https://github.com/facebookresearch/detectron2.git@ff53992b1985b63bd3262b5a36167098e3dada02

RUN micromamba run -n base pip install --no-cache-dir --no-deps --no-build-isolation /opt/benchmate

RUN micromamba install -y -n base -c conda-forge -c bioconda \
    python=3.10 \
    pip \
    git \
    postgresql \
    rdkit-postgresql \
    compilers \
    make \
    cmake && \
    micromamba clean --all --yes

RUN micromamba run -n base bash -lc '\
    git clone https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    cd /tmp/pgvector && \
    make && \
    make install && \
    rm -rf /tmp/pgvector'

ENV PATH=/opt/conda/bin:$PATH
RUN echo 'export PATH=/opt/conda/bin:$PATH' >> /home/mambauser/.bashrc && \
    echo 'export PATH=/opt/conda/bin:$PATH' >> /home/mambauser/.bash_profile
USER mambauser

CMD ["python", "-c", "import benchmate; print('benchmate container ready')"]
