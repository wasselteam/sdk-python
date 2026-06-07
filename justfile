@_default:
    just --list

bindings:
    mkdir -p build
    rm -rf ./build/bindings
    wkg wit fetch -d ./src/wassel_sdk/wit -t wit
    componentize-py \
        --wit-path ./src/wassel_sdk/wit \
        --world http-plugin \
        --world-module wassel_sdk.wit \
        bindings \
        ./build/bindings
    cp -r ./build/bindings/wassel_sdk/wit/* ./src/wassel_sdk/wit/

bindings-2:
    #!/bin/bash

    componentize-py \
        -d src/wassel_sdk/wit \
        -w "wassel:sdk/http-plugin" \
        --export-interface-name "wassel:foundation/http-handler=http-handler" \
        --world-module wassel_sdk.wit \
        --full-names \
        bindings \
        bindings
    rm -rf src/wassel_sdk/wit/imports src/wassel_sdk/wit/exports src/componentize_py_*
    mv bindings/wassel_sdk/wit/* src/wassel_sdk/wit/
    mv bindings/componentize_py_* src/
    # `pdoc3` needs to be able to load all modules in order to generate docs, so we
    # provide a stub version of `componentize_py_runtime` to make it happy:
    sed 's/\.\.\./raise NotImplementedError/' < src/componentize_py_runtime.pyi > src/componentize_py_runtime.py
    rm -r bindings
