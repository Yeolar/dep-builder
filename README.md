# dep-builder

A dependency builder.

Usage:

1. copy code below and save as deps.sh

    ```sh
    # git@branch or git@commit
    DEPS=(
    )

    mkdir -p deps && cd deps
    if [ ! -f dep-builder.py ]; then
        curl -L https://github.com/Yeolar/dep-builder/tarball/master | tar xz --strip 2 -C .
    fi

    python dep-builder.py - ${DEPS[*]}
    ```

2. add dependencies at DEPS array
3. run: `sh deps.sh`
