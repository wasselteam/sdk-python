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

wit:
