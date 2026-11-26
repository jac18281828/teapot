#!/bin/bash
# Render one shot into the next free version: renders/<shot>/<shot>_vNNN.<format>.
# usage: tools/render.sh SHOT [RENDERER [FORMAT]]   (run from the project root; GMAN names the binary)
set -euo pipefail
shot=$1
renderer=${2:-gmanpathtracer}
format=${3:-png}
gman=${GMAN:-gman}
[ -f "shots/$shot/shot.rib" ] || { echo "no shot: shots/$shot/shot.rib" >&2; exit 1; }
info=$("$gman" --version)
banner=${info%%$'\n'*}
[[ $banner =~ ^gman\ ([0-9]+)\.([0-9]+)\.([0-9]+) ]] &&
  { major=$((10#${BASH_REMATCH[1]})); minor=$((10#${BASH_REMATCH[2]})); patch=$((10#${BASH_REMATCH[3]}))
    (( major > 1 || (major == 1 && (minor > 3 || (minor == 3 && patch >= 1))) )); } ||
  { echo "$gman reports \"$banner\"; Teapot needs gman 1.3.1 or later" >&2; exit 1; }
drivers=$(grep '^drivers:' <<< "$info" || true)
grep -qw "$format" <<< "${drivers#drivers:}" ||
  { echo "$gman has no $format driver ($drivers)" >&2; exit 1; }
mkdir -p "renders/$shot" build/frames
n=1
while compgen -G "$(printf 'renders/%s/%s_v%03d.*' "$shot" "$shot" "$n")" > /dev/null; do n=$((n + 1)); done
out=$(printf 'renders/%s/%s_v%03d.%s' "$shot" "$shot" "$n" "$format")
frame=$(printf 'build/frames/%s_v%03d.rib' "$shot" "$n")
printf 'Display "%s" "file" "rgba"\nReadArchive "../../shots/%s/shot.rib"\n' "$out" "$shot" > "$frame"
start=$(date +%s)
"$gman" -r "$renderer" "$frame"
echo "$out ($renderer, $(( $(date +%s) - start )) s)"
