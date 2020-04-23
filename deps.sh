# git@branch or git@commit
DEPS=(
)

BUILDER_VER=1.2

mkdir -p deps && cd deps

if [ ! -d dep-builder-${BUILDER_VER} ]; then
    rm -f dep-builder*
    wget https://github.com/Yeolar/dep-builder/archive/v${BUILDER_VER}.tar.gz -O dep-builder.tar.gz
    tar xzf dep-builder.tar.gz
fi

python dep-builder-${BUILDER_VER}/dep-builder.py - ${DEPS[*]}
