from setuptools import setup, find_packages

setup(
    name='benchmate',
    version='0.1.0',
    description="A data aggregation tool for omic data including literature search and accessing public databases",
    url='ccmbioinfo.github.io/benchmate',
    author='Alper Celik',
    author_email='alper.celik@sickkids.ca',
    packages=find_packages(),
    zip_safe=False,
    package_data={"": ["*.json"]},
    # scripts=["benchmate/scripts/run_mmseqs.sh"],
    include_package_data=True
)
