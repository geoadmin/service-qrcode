#!bin/bash

set -exu

# The minimal working version of python for this project is 3.7.4, anything more recent, within the Major version,
# (for example: 3.7.12 or 3.8.0) is accepted.
PYTHON_BASE_VERSION_REQUIRED=3.7.4
PYTHON_MINIMAL_VERSION_MAJOR=${PYTHON_BASE_VERSION_REQUIRED:0:1}
PYTHON_MINIMAL_VERSION_MINOR=${PYTHON_BASE_VERSION_REQUIRED:2:1}
PYTHON_MINIMAL_VERSION_BUGFIX=${PYTHON_BASE_VERSION_REQUIRED:4:1}
# We find the current version of python
CURRENT_PYTHON_VERSION=$(python3 -c "import sys;t='{v[0]}.{v[1]}.{v[2]}'.format(v=list(sys.version_info[:]));sys.stdout.write(t)")
# format of version is M.m.b, we extract those
PYTHON_MAJOR_VERSION=${CURRENT_PYTHON_VERSION:0:1}
PYTHON_MINOR_VERSION=${CURRENT_PYTHON_VERSION:2:1}
PYTHON_BUGFIX_VERSION=${CURRENT_PYTHON_VERSION:4:1}

#This checks if the version is not compatible. If that's the case, an installation will occur.
if [[ ! "${PYTHON_MINIMAL_VERSION_MAJOR}" -eq "${PYTHON_MAJOR_VERSION}" ]] ||
[[ "${PYTHON_MINIMAL_VERSION_MINOR}" -gt "${PYTHON_MINOR_VERSION}" ]] ||
[[ "${PYTHON_MINIMAL_VERSION_MINOR}" -eq "${PYTHON_MINOR_VERSION}" ]] &&
[[ "${PYTHON_MINIMAL_VERSION_BUGFIX}" -gt "${PYTHON_BUGFIX_VERSION}" ]]; then

    # We install Python
    curl -z ./local/Python-${PYTHON_BASE_VERSION_REQUIRED}
.tar.xz https://www.python.org/ftp/python/${PYTHON_BASE_VERSION_REQUIRED}
/Python-${PYTHON_BASE_VERSION_REQUIRED}
.tar.xz -o ./local/Python-${PYTHON_BASE_VERSION_REQUIRED}
.tar.xz
    cd ./local && tar -xf Python-${PYTHON_BASE_VERSION_REQUIRED}
.tar.xz && Python-${PYTHON_BASE_VERSION_REQUIRED}
/configure --prefix=$./local/ && make altinstall
    echo "Python has been installed"
else
    echo "The python version set up on the system is sufficient."
fi