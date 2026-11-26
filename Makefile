GMAN ?= gman
RENDERER ?= gmanpathtracer
FORMAT ?= png
TEXRES ?= 8192
SHOTS := $(notdir $(wildcard shots/*))
TIFS := $(filter-out assets/teapot/tex/tendrils.tif,$(wildcard assets/*/tex/*.tif))
TEXS := $(patsubst %.tif,build/tex/%.tex,$(notdir $(TIFS))) build/tex/tendrils.tex

vpath %.tif $(sort $(dir $(TIFS)))

.PHONY: render all tex
render: tex
	@test -n "$(shot)" || { echo "usage: make shot=<$(SHOTS)>"; exit 1; }
	GMAN=$(GMAN) tools/render.sh $(shot) $(RENDERER) $(FORMAT)

all: tex
	@for s in $(SHOTS); do GMAN=$(GMAN) tools/render.sh $$s $(RENDERER) $(FORMAT) || exit 1; done

tex: $(TEXS)

PAINTED := $(wildcard assets/teapot/tex/tendrils.tif)
ifeq ($(PAINTED),)
build/tex/tendrils.tif: tools/tendrils.py
	@mkdir -p build/tex
	python3 -I tools/tendrils.py $(TEXRES) $@
else
build/tex/tendrils.tif: $(PAINTED)
	@mkdir -p build/tex
	cp $< $@
endif

build/tex/%.tex: build/tex/%.tif
	printf 'MakeTexture "%s" "%s" "periodic" "clamp" "box" 1 1\n' $< $@ > build/tex/$*.rib
	$(GMAN) build/tex/$*.rib

build/tex/%.tex: %.tif
	@mkdir -p build/tex
	printf 'MakeTexture "%s" "%s" "periodic" "periodic" "box" 1 1\n' $< $@ > build/tex/$*.rib
	$(GMAN) build/tex/$*.rib
