# The org profile page builds nothing, so it has one target.
# check: the vendored copies match their pinned sums, the context primers'
# figures match what tools/context_figures.py writes (packet cw1-context-primers),
# then the hygiene scan finds no hit outside .hygiene-allow (agentik-r1 7.3;
# packet ruling 1).
.PHONY: check
check:
	shasum -a 256 -c --status scripts/vendored.sha256
	tools/context_figures.py --check
	scripts/hygiene
