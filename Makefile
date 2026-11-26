GMAN ?= gman
RENDERER ?= gmanpathtracer
FORMAT ?= png
SHOTS := $(notdir $(wildcard shots/*))
TIFS := $(wildcard assets/*/tex/*.tif)
TEXS := $(patsubst %.tif,build/tex/%.tex,$(notdir $(TIFS)))

vpath %.tif $(sort $(dir $(TIFS)))

.PHONY: render all tex
render: tex
	@test -n "$(shot)" || { echo "usage: make shot=<$(SHOTS)>"; exit 1; }
	GMAN=$(GMAN) tools/render.sh $(shot) $(RENDERER) $(FORMAT)

all: tex
	@for s in $(SHOTS); do GMAN=$(GMAN) tools/render.sh $$s $(RENDERER) $(FORMAT) || exit 1; done

tex: $(TEXS)

build/tex/%.tex: %.tif
	@mkdir -p build/tex
	printf 'MakeTexture "%s" "%s" "periodic" "periodic" "box" 1 1\n' $< $@ > build/tex/$*.rib
	$(GMAN) build/tex/$*.rib
