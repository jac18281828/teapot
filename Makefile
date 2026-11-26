GMAN ?= gman
RENDERER ?= gmanpathtracer
FORMAT ?= png
SHOTS := $(notdir $(wildcard shots/*))

.PHONY: render all
render:
	@test -n "$(shot)" || { echo "usage: make shot=<$(SHOTS)>"; exit 1; }
	GMAN=$(GMAN) tools/render.sh $(shot) $(RENDERER) $(FORMAT)

all:
	@for s in $(SHOTS); do GMAN=$(GMAN) tools/render.sh $$s $(RENDERER) $(FORMAT) || exit 1; done
