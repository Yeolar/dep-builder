# git@branch or git@commit
DEPS=(
)

mkdir -p deps && cd deps

if [ ! -d dep-builder-master ]; then
    rm -rf dep-builder*
    wget https://github.com/Yeolar/dep-builder/archive/master.zip -O dep-builder.zip
    unzip dep-builder.zip
fi

python dep-builder-master/dep-builder.py - ${DEPS[*]}
