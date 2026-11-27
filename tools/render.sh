#!/bin/bash
# usage: tools/render.sh SHOT [RENDERER [FORMAT]]
# Renders shots/SHOT into the next free renders/SHOT/SHOT_vNNN.FORMAT. Run from the project root.
set -euo pipefail

shot=$1
renderer=${2:-gmanpathtracer}
format=${3:-png}
gman=${GMAN:-gman}

if [ ! -f "shots/$shot/shot.rib" ]; then
    echo "no shot: shots/$shot/shot.rib" >&2
    exit 1
fi

if ! "$gman" --version | grep '^drivers:' | grep -qw "$format"; then
    echo "$gman has no $format driver" >&2
    exit 1
fi

mkdir -p "renders/$shot" build/frames

version=1
while compgen -G "renders/$shot/${shot}_v$(printf '%03d' "$version").*" > /dev/null; do
    version=$((version + 1))
done
name="${shot}_v$(printf '%03d' "$version")"
output="renders/$shot/$name.$format"
frame="build/frames/$name.rib"

cat > "$frame" <<RIB
Display "$output" "file" "rgba"
ReadArchive "../../shots/$shot/shot.rib"
RIB

start=$(date +%s)
"$gman" -r "$renderer" "$frame"
echo "$output ($renderer, $(($(date +%s) - start)) s)"
